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
    # True if water ever reached zero during growth
    water_ever_depleted: bool = False

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

    # Bug system
    bug_active: bool = False
    bug_appearance_time: float = 0.0
    net_quantity: int = 0  # Amount of nets owned

    # Daily quest system
    daily_quests: list[dict] = None  # List of active daily quests
    quest_last_reset_ts: float = 0.0  # Last time quests were reset
    completed_quests_today: int = 0  # Number of quests completed today

    # Profile system
    player_name: str = "Player"  # Player's name
    level: int = 1  # Player level
    exp: int = 0  # Current experience points
    avatar: str = "👤"  # Player avatar (emoji for now)

    def __post_init__(self):
        if self.inventory is None:
            self.inventory = {}
        if self.seed_inventory is None:
            self.seed_inventory = {}
        if self.unlocked_pots is None:
            self.unlocked_pots = {"default"}  # Basic pot is unlocked by default
        if self.unlocked_pets is None:
            self.unlocked_pets = set()  # No pets unlocked by default
        if self.daily_quests is None:
            self.daily_quests = []  # No quests by default


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
            water_ever_depleted=bool(data.get("water_ever_depleted", False)),
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
            bug_active=bool(data.get("bug_active", False)),
            bug_appearance_time=float(data.get("bug_appearance_time", 0.0)),
            net_quantity=int(data.get("net_quantity", 0)),
            daily_quests=data.get("daily_quests", []),
            quest_last_reset_ts=float(data.get("quest_last_reset_ts", 0.0)),
            completed_quests_today=int(data.get("completed_quests_today", 0)),
            player_name=data.get("player_name", "Player"),
            level=int(data.get("level", 1)),
            exp=int(data.get("exp", 0)),
            avatar=data.get("avatar", "👤"),
        )
    except Exception:
        # If state is corrupt, start fresh.
        return GameState(last_update_ts=now_ts())


def save_state(state: GameState, path: Path = DEFAULT_STATE_FILE) -> bool:
    try:
        data = asdict(state)
        # Convert sets to list for JSON serialization
        if "unlocked_pots" in data and isinstance(data["unlocked_pots"], set):
            data["unlocked_pots"] = list(data["unlocked_pots"])
        if "unlocked_pets" in data and isinstance(data["unlocked_pets"], set):
            data["unlocked_pets"] = list(data["unlocked_pets"])
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return True
    except Exception:
        return False
