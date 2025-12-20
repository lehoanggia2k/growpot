from dataclasses import dataclass


@dataclass(frozen=True)
class UIConfig:
    # Menu labels
    menu_water: str = "Water"
    menu_harvest: str = "Harvest"
    menu_plant_seed: str = "Plant Seed"
    menu_reset: str = "Reset"
    menu_warehouse: str = "Warehouse"
    menu_change_pot: str = "Change Pot"
    menu_quit: str = "Quit"

    # Warehouse window
    warehouse_title: str = "Warehouse - Stored Harvest"
    warehouse_inventory_title: str = "🌾 Warehouse Inventory"
    warehouse_empty_message: str = "No harvested items in storage.\nHarvest some plants to see them here!"
    warehouse_close_button: str = "Close"
    warehouse_sell_button: str = "Sell All"

    # Money display
    money_format: str = "💰 {}"

    # Settings button
    settings_button_text: str = "⚙"

    # Seed menu labels
    seed_free_label: str = "{} (Free)"
    seed_cost_label: str = "{} (💰{})"

    # Pot menu labels
    pot_cost_label: str = "{} (💰{})"

    # Progress bar styles
    water_progress_style: str = "Water.Horizontal.TProgressbar"

    # Pet system
    menu_pet: str = "Pet"
    pet_status_title: str = "🐾 Pet Status"
    pet_active_label: str = "Active Pet: {}"
    pet_no_active: str = "No active pet"
    pet_time_until_hungry: str = "Time until hungry: {}"
    pet_feed_button: str = "Feed Pet"
    pet_activate_button: str = "Activate"
    pet_deactivate_button: str = "Deactivate"
    pet_unlock_label: str = "{} (💰{})"
    pet_close_button: str = "Close"

    # Shop system
    menu_shop: str = "Cửa hàng"
    shop_title: str = "🛒 Cửa hàng"
    shop_close_button: str = "Đóng"
    shop_buy_button: str = "Mua"
    shop_not_enough_money: str = "Không đủ tiền!"
    shop_purchase_success: str = "Mua hàng thành công!"

    # Daily quest system
    menu_quests: str = "Nhiệm vụ"
    quest_title: str = "📋 Nhiệm vụ hàng ngày"
    quest_close_button: str = "Đóng"
    quest_claim_button: str = "Nhận thưởng"
    quest_progress_label: str = "Tiến độ: {}/{}"
    quest_reward_label: str = "Phần thưởng: 💰{}"
    quest_completed_label: str = "Hoàn thành"
    quest_no_quests: str = "Không có nhiệm vụ nào hôm nay.\nHãy quay lại vào ngày mai!"
    
    # Shop tabs
    shop_tab_pet_food: str = "Thức ăn"
    shop_tab_seeds: str = "Hạt giống"
    shop_tab_pots: str = "Chậu"
    shop_tab_pets: str = "Thú cưng"  
    
    # Shop item descriptions
    shop_pet_food_desc: str = "Cho thú cưng ăn để chúng làm việc"
    shop_seed_stock_label: str = "Trong kho: {}"
    shop_price_label: str = "Giá: 💰{}"
    shop_pot_owned: str = "Đã sở hữu"
