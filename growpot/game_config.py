from dataclasses import dataclass, field


@dataclass(frozen=True)
class PlantStats:
    growth_time_sec: float  # Time to reach full growth
    yield_amount: int  # Number of items harvested
    seed_price: int  # Cost to buy seed
    harvest_price_per_item: int  # Sell price per harvested item


@dataclass(frozen=True)
class PotStats:
    growth_time_reduction_percent: float  # Reduction in growth time (0-1)
    water_decay_reduction_percent: float  # Reduction in water decay rate (0-1)
    price: int  # Cost to buy pot


@dataclass(frozen=True)
class PetStats:
    unlock_cost: int  # Cost to unlock pet
    work_duration_sec: float  # How long pet can work before feeding (seconds)
    auto_water_threshold: float  # Water level percentage to trigger auto-watering (0-1)
    auto_water_amount: float  # Amount of water to add when auto-watering


@dataclass(frozen=True)
class ShopItem:
    name: str  # Display name
    price: int  # Purchase price
    category: str  # Shop category (pet_food, seeds, pots)
    item_type: str  # Specific item type identifier
    description: str = ""  # Optional description


@dataclass(frozen=True)
class ShopConfig:
    items: dict[str, ShopItem] = field(default_factory=lambda: {
        "pet_food": ShopItem(
            name="Pet Food",
            price=50,
            category="pet_food",
            item_type="pet_food",
            description="Feed your pet to keep it working"
        ),
    })
    # Initial seed stock for each plant type
    initial_seed_stock: dict[str, int] = field(default_factory=lambda: {
        "basic": 10,  # Start with 10 basic seeds
        "rose": 5,   # Start with 5 rose seeds
        "daisy": 3,  # Start with 3 daisy seeds
    })
    # Initial pet food stock
    initial_pet_food: int = 5
    
    # Pet descriptions
    pet_descriptions: dict[str, str] = field(default_factory=lambda: {
        "cat": "Auto-waters your plants when water level is low. Works for 2 hours before needing food."
    })
    
    # Plant descriptions
    plant_descriptions: dict[str, str] = field(default_factory=lambda: {
        "basic": "Fast growing plant (10s). Basic yield. Good for beginners.",
        "rose": "Beautiful flower (15s growth). Sells for good price.",
        "daisy": "Quick growing (20s). Double yield compared to basic."
    })
    
    # Pot descriptions
    pot_descriptions: dict[str, str] = field(default_factory=lambda: {
        "default": "Basic pot with no bonuses. Free to use.",
        "wood": "Premium pot. 10% faster growth and 30% better water retention."
    })


@dataclass(frozen=True)
class GameConfig:
    tick_ms: int = 100
    anim_fps: int = 10
    save_every_ms: int = 1500

    # growth values
    base_growth_per_sec: float = 0.3  # Adjusted for 10s growth time
    water_boost_growth_per_sec: float = 0.03
    water_decay_per_sec: float = 0.12

    # Growth thresholds for stage changes
    sprout_at: float = 1.0
    plant_at: float = 3.0

    # Watering
    water_per_click: float = 5.0  # Fill to 100% per click

    # Plant stats
    PLANT_STATS: dict[str, PlantStats] = field(default_factory=lambda: {
        "basic": PlantStats(growth_time_sec=10.0, yield_amount=1, seed_price=0, harvest_price_per_item=20),
        "rose": PlantStats(growth_time_sec=15.0, yield_amount=1, seed_price=20, harvest_price_per_item=30),
        "daisy": PlantStats(growth_time_sec=20.0, yield_amount=2, seed_price=30, harvest_price_per_item=30),
    })

    # Pot stats
    POT_STATS: dict[str, PotStats] = field(default_factory=lambda: {
        "default": PotStats(growth_time_reduction_percent=0.0, water_decay_reduction_percent=0.0, price=0),  # Free default
        "wood": PotStats(growth_time_reduction_percent=0.1, water_decay_reduction_percent=0.3, price=200),  # 10% growth reduction, 30% water retention, costs 200
    })

    # Pet stats
    PET_STATS: dict[str, PetStats] = field(default_factory=lambda: {
        "cat": PetStats(unlock_cost=200, work_duration_sec=7200.0, auto_water_threshold=0.1, auto_water_amount=3.0),  # 2 hours work, auto-water at 10%, adds 3.0 water
    })
