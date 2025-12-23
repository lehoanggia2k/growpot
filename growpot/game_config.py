from dataclasses import dataclass, field


@dataclass(frozen=True)
class PlantStats:
    growth_time_sec: float  # Time to reach full growth
    yield_amount: int  # Number of items harvested
    seed_price: int  # Cost to buy seed
    harvest_price_per_item: int  # Sell price per harvested item
    harvest_exp_reward: int  # EXP gained when harvesting this plant
    unlock_level: int  # Player level required to unlock this plant


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
class QuestTemplate:
    id: str  # Unique identifier
    name: str  # Display name
    description: str  # Quest description
    requirement_type: str  # Type of requirement (e.g., "harvest")
    plant_type: str  # Specific plant type required (for harvest quests)
    requirement_count: int  # How many to complete
    reward_money: int  # Money reward


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
        "net": ShopItem(
            name="Net",
            price=20,
            category="pet_food",
            item_type="net",
            description="Catch bugs that appear on plants"
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

    # Bug system
    bug_appearance_chance: float = 0.34  # 34% chance to appear
    bug_growth_start: float = 1.8  # Start appearing at 60% growth (1.8/3.0)
    bug_growth_end: float = 2.4  # Stop appearing at 80% growth (2.4/3.0)
    bug_catch_time_percent: float = 0.1  # Must catch within 10% of total growth time
    bug_harvest_bonus_time_percent: float = 0.2  # Harvest within 20% after ripening for bonus
    bug_sell_price: int = 10  # Price per bug when sold

    # Plant stats
    PLANT_STATS: dict[str, PlantStats] = field(default_factory=lambda: {
        "basic": PlantStats(growth_time_sec=10.0, yield_amount=1, seed_price=0, harvest_price_per_item=20, harvest_exp_reward=10, unlock_level=1),
        "rose": PlantStats(growth_time_sec=15.0, yield_amount=1, seed_price=20, harvest_price_per_item=30, harvest_exp_reward=15, unlock_level=3),
        "daisy": PlantStats(growth_time_sec=20.0, yield_amount=2, seed_price=30, harvest_price_per_item=30, harvest_exp_reward=20, unlock_level=5),
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

    # Daily quest templates (base templates that will be modified with specific plant types)
    QUEST_TEMPLATES: dict[str, QuestTemplate] = field(default_factory=lambda: {
        "harvest_bronze_basic": QuestTemplate(
            id="harvest_bronze_basic",
            name="Thu hoạch cơ bản",
            description="Thu hoạch 4 cây basic",
            requirement_type="harvest",
            plant_type="basic",
            requirement_count=4,
            reward_money=50
        ),
        "harvest_bronze_rose": QuestTemplate(
            id="harvest_bronze_rose",
            name="Thu hoạch cơ bản",
            description="Thu hoạch 2 cây rose",
            requirement_type="harvest",
            plant_type="rose",
            requirement_count=2,
            reward_money=50
        ),
        "harvest_bronze_daisy": QuestTemplate(
            id="harvest_bronze_daisy",
            name="Thu hoạch cơ bản",
            description="Thu hoạch 1 cây daisy",
            requirement_type="harvest",
            plant_type="daisy",
            requirement_count=1,
            reward_money=50
        ),
        "harvest_silver_basic": QuestTemplate(
            id="harvest_silver_basic",
            name="Thu hoạch nâng cao",
            description="Thu hoạch 6 cây basic",
            requirement_type="harvest",
            plant_type="basic",
            requirement_count=6,
            reward_money=75
        ),
        "harvest_silver_rose": QuestTemplate(
            id="harvest_silver_rose",
            name="Thu hoạch nâng cao",
            description="Thu hoạch 3 cây rose",
            requirement_type="harvest",
            plant_type="rose",
            requirement_count=3,
            reward_money=75
        ),
        "harvest_silver_daisy": QuestTemplate(
            id="harvest_silver_daisy",
            name="Thu hoạch nâng cao",
            description="Thu hoạch 2 cây daisy",
            requirement_type="harvest",
            plant_type="daisy",
            requirement_count=2,
            reward_money=75
        ),
        "harvest_gold_basic": QuestTemplate(
            id="harvest_gold_basic",
            name="Thu hoạch chuyên nghiệp",
            description="Thu hoạch 8 cây basic",
            requirement_type="harvest",
            plant_type="basic",
            requirement_count=8,
            reward_money=100
        ),
        "harvest_gold_rose": QuestTemplate(
            id="harvest_gold_rose",
            name="Thu hoạch chuyên nghiệp",
            description="Thu hoạch 4 cây rose",
            requirement_type="harvest",
            plant_type="rose",
            requirement_count=4,
            reward_money=100
        ),
        "harvest_gold_daisy": QuestTemplate(
            id="harvest_gold_daisy",
            name="Thu hoạch chuyên nghiệp",
            description="Thu hoạch 3 cây daisy",
            requirement_type="harvest",
            plant_type="daisy",
            requirement_count=3,
            reward_money=100
        ),
    })

    # Daily quest settings
    daily_quest_count_min: int = 2  # Minimum quests per day
    daily_quest_count_max: int = 3  # Maximum quests per day
