from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class GameState:
    # Growth is continuous, but we map it to stages for visuals.
    growth: float = 0.0  # -1.0 means empty pot, no plant
    # "water" acts like a temporary boost that decays.
    water: float = 0.0
    # Accumulated water deficit during growth (affects yield)
    growth_water_deficit: float = 0.0

    # window position
    x: int | None = None
    y: int | None = None

    # unix epoch seconds
    last_update_ts: float = 0.0

    # Customization
    pot_type: str = "default"
    plant_type: str = "basic"

    # Progress
    harvested_count: int = 0
    last_harvest_ts: float = 0.0

    # Economy
    money: int = 0
    inventory: dict[str, int] = None  # Harvested items
    seed_inventory: dict[str, int] = None  # Seeds for planting
    unlocked_pots: set[str] = None

    # Pet system
    active_pet: str | None = None
    pet_last_fed_ts: float = 0.0
    pet_last_worked_ts: float = 0.0
    pet_food: int = 0  # Amount of pet food owned
    unlocked_pets: set[str] = None

    def __post_init__(self):
        if self.inventory is None:
            self.inventory = {}
        if self.seed_inventory is None:
            self.seed_inventory = {}
        if self.unlocked_pots is None:
            self.unlocked_pots = {"default"}  # Basic pot is unlocked by default
        if self.unlocked_pets is None:
            self.unlocked_pets = set()  # No pets unlocked by default


DEFAULT_STATE_FILE = Path("state.json")


def now_ts() -> float:
    return time.time()


def load_state(path: Path = DEFAULT_STATE_FILE) -> GameState:
    if not path.exists():
        return GameState(last_update_ts=now_ts())

    try:
        data = json.loads(path.read_text(encoding="utf-8"))

        # Load inventory, migrating old harvested_count if needed
        inventory = data.get("inventory", {})
        harvested_count = int(data.get("harvested_count", 0))

        # Migrate existing harvested_count to inventory if not already done
        # We'll assume they were "basic" plants for migration purposes
        if harvested_count > 0 and not inventory:
            inventory["basic"] = harvested_count

        return GameState(
            growth=float(data.get("growth", 0.0)),
            water=float(data.get("water", 0.0)),
            growth_water_deficit=float(data.get("growth_water_deficit", 0.0)),
            x=data.get("x"),
            y=data.get("y"),
            last_update_ts=float(data.get("last_update_ts", now_ts())),
            pot_type=data.get("pot_type", "default"),
            plant_type=data.get("plant_type", "basic"),
            harvested_count=harvested_count,  # Keep for backward compatibility
            last_harvest_ts=float(data.get("last_harvest_ts", 0.0)),
            money=int(data.get("money", 0)),
            inventory=inventory,
            seed_inventory=data.get("seed_inventory", {}),
            unlocked_pots=set(data.get("unlocked_pots", ["default"])),
            active_pet=data.get("active_pet"),
            pet_last_fed_ts=float(data.get("pet_last_fed_ts", 0.0)),
            pet_last_worked_ts=float(data.get("pet_last_worked_ts", 0.0)),
            pet_food=int(data.get("pet_food", 0)),
            unlocked_pets=set(data.get("unlocked_pets", [])),
        )
    except Exception:
        # If state is corrupt, start fresh.
        return GameState(last_update_ts=now_ts())


def save_state(state: GameState, path: Path = DEFAULT_STATE_FILE) -> None:
    data = asdict(state)
    # Convert sets to list for JSON serialization
    if "unlocked_pots" in data and isinstance(data["unlocked_pots"], set):
        data["unlocked_pots"] = list(data["unlocked_pots"])
    if "unlocked_pets" in data and isinstance(data["unlocked_pets"], set):
        data["unlocked_pets"] = list(data["unlocked_pets"])
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
