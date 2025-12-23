from __future__ import annotations

import time
import tkinter as tk
from pathlib import Path

from growpot.state import GameState, load_state, now_ts, save_state
from growpot.game_config import GameConfig
from growpot.ui_config import UIConfig
from growpot.ui_components import UIManager
from growpot.game_logic import GameEngine
from growpot.animation_system import AnimationManager
from growpot.warehouse_system import WarehouseManager
from growpot.pet_system import PetManager
from growpot.shop_system import ShopManager
from growpot.profile_system import ProfileManager
from growpot.event_handlers import EventHandler


class GrowPlotApp:
    """Main application coordinator that manages all subsystems"""
    
    def __init__(self, root: tk.Tk, assets_dir: Path) -> None:
        self.root = root
        self.assets_dir = assets_dir
        
        # Initialize configurations
        self.cfg = GameConfig()
        self.ui = UIConfig()
        
        # Load game state
        self.state = load_state()
        
        # Initialize subsystems
        self.game_engine = GameEngine(self.cfg)
        self.animation_manager = AnimationManager(self.cfg)
        self.ui_manager = UIManager(root, 140, 100, self.ui)  # Initial size, will be updated
        self.warehouse_manager = WarehouseManager(self.cfg, self.ui)
        self.pet_manager = PetManager(self.cfg, self.ui)
        self.shop_manager = ShopManager(self.cfg, self.ui)
        self.profile_manager = ProfileManager(self.ui)
        self.event_handler = EventHandler(root, assets_dir, self.ui)
        
        # Setup window
        self._setup_window()
        
        # Load assets and calculate canvas size
        self._load_assets()
        self._update_canvas_size()
        
        # Initialize UI with callbacks
        self._setup_ui_callbacks()
        
        # Apply offline progress and initialize shop inventory
        self.game_engine.apply_offline_progress(self.state)
        self._initialize_shop_inventory()

        # Check for daily quest reset
        self.game_engine.check_daily_quest_reset(self.state)
        
        # Start game loop
        self._last_tick_perf = time.perf_counter()
        self._last_save_perf = time.perf_counter()
        self._tick()
    
    def _setup_window(self):
        """Setup the main window properties"""
        self.root.overrideredirect(True)  # no window borders
        self.root.attributes("-topmost", True)
        self.root.configure(bg="magenta")
        
        # Make background transparent-ish (Windows supports transparentcolor)
        try:
            self.root.wm_attributes("-transparentcolor", "magenta")
        except tk.TclError:
            pass
        
        # Set window protocol
        self.root.protocol("WM_DELETE_WINDOW", self.event_handler.on_close)
    
    def _load_assets(self):
        """Load all game assets"""
        # Load pot frames
        if not self.animation_manager.load_pot_frames(self.assets_dir, self.state.pot_type):
            raise FileNotFoundError(f"Pot frames not found for type: {self.state.pot_type}")
        
        # Load plant frames
        if not self.animation_manager.load_plant_frames(self.assets_dir, self.state.plant_type):
            raise FileNotFoundError(f"Plant frames not found for type: {self.state.plant_type}")
        
        # Load pet frames
        self.animation_manager.load_pet_frames(self.assets_dir, self.state.active_pet)
    
    def _update_canvas_size(self):
        """Update canvas size based on loaded assets"""
        max_width, max_height = self.animation_manager.calculate_max_canvas_size()
        self.ui_manager.resize_canvas(max_width, max_height)
    
    def _setup_ui_callbacks(self):
        """Setup all UI callbacks and event handlers"""
        # Register callbacks with event handler
        self.event_handler.register_callback('get_state', lambda: self.state)
        self.event_handler.register_callback('get_game_config', lambda: self.cfg)
        self.event_handler.register_callback('save_state', lambda: save_state(self.state))
        self.event_handler.register_callback('update_last_time', lambda: setattr(self.state, 'last_update_ts', now_ts()))
        self.event_handler.register_callback('get_settings_button', lambda: self.ui_manager.btn_settings)
        
        # Game action callbacks
        self.event_handler.register_callback('water_plant', self._handle_water)
        self.event_handler.register_callback('harvest_plant', self._handle_harvest)
        self.event_handler.register_callback('reset_plant', self._handle_reset)
        self.event_handler.register_callback('plant_seed', self._handle_plant_seed)
        self.event_handler.register_callback('change_pot', self._handle_change_pot)
        self.event_handler.register_callback('unlock_pot', self._handle_unlock_pot)
        
        # UI callbacks
        self.event_handler.register_callback('show_settings_menu', self._handle_show_settings_menu)
        self.event_handler.register_callback('show_warehouse', self._handle_show_warehouse)
        self.event_handler.register_callback('show_pet_status', self._handle_show_pet_status)
        self.event_handler.register_callback('show_shop', self._handle_show_shop)
        self.event_handler.register_callback('show_quests', self._handle_show_quests)
        self.event_handler.register_callback('show_profile', self._handle_show_profile)
        self.event_handler.register_callback('show_seed_menu', self._handle_show_seed_menu)
        
        # Setup drag handlers
        self.ui_manager.setup_drag_handlers(
            self.event_handler.on_drag_start,
            self.event_handler.on_drag_move,
            self.event_handler.on_drag_end
        )
        
        # Setup settings button
        self.ui_manager.btn_settings.config(command=self.event_handler.on_settings_click)
        
        # Create pot menu
        pot_menu = self.event_handler.create_pot_menu(
            self.root, self.state,
            self.event_handler.on_change_pot,
            self.event_handler.on_unlock_pot
        )
        
        # Setup settings menu with all callbacks
        self.ui_manager.setup_settings_menu(
            self.state,
            self.event_handler.on_water,
            self.event_handler.on_harvest,
            self.event_handler.on_show_seed_menu,
            self.event_handler.on_reset,
            self.event_handler.on_show_warehouse,
            self.event_handler.on_show_pet_status,
            self.event_handler.on_show_shop,
            self.event_handler.on_show_quests,
            self.event_handler.on_show_profile,
            pot_menu,
            self.event_handler.on_close
        )
        
        # Initialize money display
        self.ui_manager.update_money_display(self.state.money)
    
    def _initialize_shop_inventory(self):
        """Initialize seed inventory and pet food for new games"""
        from growpot.game_config import ShopConfig
        shop_cfg = ShopConfig()
        
        # Only initialize if inventories are empty (new game)
        if not self.state.seed_inventory and self.state.pet_food == 0:
            self.state.seed_inventory = shop_cfg.initial_seed_stock.copy()
            self.state.pet_food = shop_cfg.initial_pet_food
            save_state(self.state)
    
    def _tick(self):
        """Main game loop tick"""
        # Calculate delta time
        now = time.perf_counter()
        dt = max(0.0, now - self._last_tick_perf)
        self._last_tick_perf = now
        
        # Update game simulation
        self.game_engine.advance_simulation(self.state, dt)
        self.game_engine.check_pet_auto_watering(self.state)
        
        # Update harvest menu state if changed
        if self.game_engine.get_harvest_menu_state_changed(self.state):
            self.ui_manager.update_harvest_menu_state(
                self.game_engine.get_current_harvest_menu_state(self.state) == "normal"
            )
        
        # Update animations
        plant_image = self.animation_manager.update_plant_animation(
            dt, self.state.growth, 
            self.ui_manager.max_canvas_width, 
            self.ui_manager.max_canvas_height
        )
        if plant_image:
            self.ui_manager.update_canvas_image(plant_image)
        
        # Update pet animation
        pet_image = self.animation_manager.update_pet_animation(
            dt, self.ui_manager.max_canvas_width, self.ui_manager.max_canvas_height
        )
        if pet_image and not self.animation_manager.pet_img_item:
            self.animation_manager.pet_img_item = self.ui_manager.create_pet_image_item()
        
        if pet_image and self.animation_manager.pet_img_item:
            pet_x, pet_y = self.animation_manager.get_pet_position(
                self.ui_manager.max_canvas_width, self.ui_manager.max_canvas_height
            )
            self.ui_manager.update_pet_image(
                self.animation_manager.pet_img_item, pet_image, pet_x, pet_y
            )
        
        # Update bug display
        if self.state.bug_active:
            # Show bug above the pot
            bug_x = self.ui_manager.max_canvas_width // 2
            bug_y = self.ui_manager.max_canvas_height // 2 - 30  # Above the plant
            self.ui_manager.show_bug(bug_x, bug_y, self._handle_bug_click)
        else:
            self.ui_manager.hide_bug()

        # Save state periodically
        if (now - self._last_save_perf) * 1000.0 >= self.cfg.save_every_ms:
            self._last_save_perf = now
            self.state.last_update_ts = now_ts()
            save_state(self.state)
        
        # Schedule next tick
        self.root.after(self.cfg.tick_ms, self._tick)
    
    # Event handlers
    def _handle_water(self):
        """Handle water action"""
        self.game_engine.water_plant(self.state)
    
    def _handle_harvest(self):
        """Handle harvest action"""
        yield_amount, quality = self.game_engine.harvest_plant(self.state)
        if yield_amount > 0:
            # Add to inventory
            if self.state.plant_type not in self.state.inventory:
                self.state.inventory[self.state.plant_type] = 0
            self.state.inventory[self.state.plant_type] += yield_amount

            # Update harvested_count for backward compatibility
            self.state.harvested_count += yield_amount

            # Award EXP for harvesting
            plant_stats = self.cfg.PLANT_STATS[self.state.plant_type]
            self.profile_manager.add_exp(self.state, plant_stats.harvest_exp_reward)

            # Reset animation
            self.animation_manager.reset_animation_index()
            save_state(self.state)
    
    def _handle_reset(self):
        """Handle reset action"""
        self.game_engine.reset_plant(self.state)
        self.animation_manager.reset_animation_index()
        save_state(self.state)
    
    def _handle_plant_seed(self, plant_type: str):
        """Handle seed planting"""
        # Check if planting is allowed (pot must be empty)
        if not self.game_engine.can_plant_seed(self.state):
            return  # Cannot plant on occupied pot

        # Check if player has seeds in inventory
        current_stock = self.state.seed_inventory.get(plant_type, 0)
        if current_stock <= 0:
            return  # No seeds available, cannot plant

        # Check if player level meets unlock requirement
        plant_stats = self.cfg.PLANT_STATS[plant_type]
        if self.state.level < plant_stats.unlock_level:
            return  # Player level too low, cannot plant

        # Use existing seeds (these get consumed)
        self.state.seed_inventory[plant_type] -= 1
        if self.state.seed_inventory[plant_type] == 0:
            del self.state.seed_inventory[plant_type]

        # Plant the seed
        if self.game_engine.plant_seed(self.state, plant_type):
            # Load new plant frames
            self.animation_manager.load_plant_frames(self.assets_dir, plant_type)
            self._update_canvas_size()
            self.animation_manager.reset_animation_index()
            save_state(self.state)
    
    def _handle_change_pot(self, pot_type: str):
        """Handle pot change"""
        if self.game_engine.change_pot(self.state, pot_type):
            # Load new pot frames
            if self.animation_manager.load_pot_frames(self.assets_dir, pot_type):
                self._update_canvas_size()
                save_state(self.state)
    
    def _handle_unlock_pot(self, pot_type: str, cost: int):
        """Handle pot unlock"""
        if self.game_engine.unlock_pot(self.state, pot_type, cost):
            self.ui_manager.update_money_display(self.state.money)
            # Switch to the newly unlocked pot
            self._handle_change_pot(pot_type)
            save_state(self.state)
            
            # Rebuild pot menu
            self._handle_show_settings_menu()  # Refresh settings menu
    
    def _handle_show_settings_menu(self):
        """Handle settings menu display"""
        self.ui_manager.show_settings_menu()
    
    def _handle_show_warehouse(self):
        """Handle warehouse display"""
        self.warehouse_manager.show_warehouse(
            self.root, self.state,
            self._handle_warehouse_sell,
            lambda: self.ui_manager.update_money_display(self.state.money)
        )
    
    def _handle_warehouse_sell(self, plant_type: str, quantity: int, price_per_item: int):
        """Handle warehouse selling"""
        success = self.warehouse_manager.sell_items_transaction(
            self.state, plant_type, quantity, price_per_item
        )
        if success:
            self.ui_manager.update_money_display(self.state.money)
            save_state(self.state)
            # Refresh warehouse to show updated inventory
            self._handle_show_warehouse()
        return success
    
    def _handle_show_pet_status(self):
        """Handle status display"""
        # Callback to get current state values for live updates
        def get_current_state():
            return self.state.growth, self.state.water, self.cfg.plant_at

        self.pet_manager.show_pet_status(
            self.root, self.state, self.state.growth, self.state.water, self.cfg.plant_at,
            self._handle_pet_feed,
            self._handle_pet_activate,
            self._handle_pet_deactivate,
            self._handle_pet_unlock,
            get_current_state
        )
    
    def _handle_pet_feed(self):
        """Handle pet feeding"""
        success = self.pet_manager.feed_pet_transaction(self.state)
        if success:
            save_state(self.state)
            # Refresh pet status
            self._handle_show_pet_status()
        return success
    
    def _handle_pet_activate(self, pet_type: str):
        """Handle pet activation"""
        success = self.pet_manager.activate_pet_transaction(self.state, pet_type)
        if success:
            # Load pet frames
            self.animation_manager.load_pet_frames(self.assets_dir, pet_type)
            save_state(self.state)
            # Refresh pet status
            self._handle_show_pet_status()
        return success
    
    def _handle_pet_deactivate(self):
        """Handle pet deactivation"""
        success = self.pet_manager.deactivate_pet_transaction(self.state)
        if success:
            # Clear pet frames
            if self.animation_manager.pet_img_item:
                self.ui_manager.delete_pet_image(self.animation_manager.pet_img_item)
                self.animation_manager.pet_img_item = None
            self.animation_manager.load_pet_frames(self.assets_dir, None)
            save_state(self.state)
            # Refresh pet status
            self._handle_show_pet_status()
        return success
    
    def _handle_pet_unlock(self, pet_type: str, cost: int):
        """Handle pet unlocking"""
        success = self.pet_manager.unlock_pet_transaction(self.state, pet_type, cost)
        if success:
            self.ui_manager.update_money_display(self.state.money)
            save_state(self.state)
            # Refresh pet status
            self._handle_show_pet_status()
        return success
    
    def _handle_show_shop(self):
        """Handle shop display"""
        self.shop_manager.show_shop(
            self.root, self.state,
            self._handle_shop_buy_pet_food,
            self._handle_shop_buy_net,
            self._handle_shop_buy_seeds,
            self._handle_shop_buy_pot,
            self._handle_shop_buy_pet,
            self._handle_shop_switch_pot,
            self._handle_shop_activate_pet,
            lambda: self.ui_manager.update_money_display(self.state.money)
        )
    
    def _handle_shop_buy_pet_food(self, quantity: int, cost: int):
        """Handle pet food purchase from shop"""
        success = self.shop_manager.buy_pet_food_transaction(self.state, quantity, cost)
        if success:
            self.ui_manager.update_money_display(self.state.money)
            save_state(self.state)
        return success

    def _handle_shop_buy_net(self, quantity: int, cost: int):
        """Handle net purchase from shop"""
        success = self.shop_manager.buy_net_transaction(self.state, quantity, cost)
        if success:
            self.ui_manager.update_money_display(self.state.money)
            save_state(self.state)
        return success
    
    def _handle_shop_buy_seeds(self, plant_type: str, quantity: int, cost: int):
        """Handle seeds purchase from shop"""
        success = self.shop_manager.buy_seeds_transaction(self.state, plant_type, quantity, cost)
        if success:
            self.ui_manager.update_money_display(self.state.money)
            save_state(self.state)
        return success
    
    def _handle_shop_buy_pot(self, pot_type: str, cost: int):
        """Handle pot purchase from shop"""
        success = self.shop_manager.buy_pot_transaction(self.state, pot_type, cost)
        if success:
            self.ui_manager.update_money_display(self.state.money)
            save_state(self.state)
        return success
    
    def _handle_shop_buy_pet(self, pet_type: str, cost: int):
        """Handle pet purchase from shop"""
        success = self.shop_manager.buy_pet_transaction(self.state, pet_type, cost)
        if success:
            self.ui_manager.update_money_display(self.state.money)
            save_state(self.state)
        return success
    
    def _handle_shop_switch_pot(self, pot_type: str):
        """Handle pot switching from shop"""
        return self._handle_change_pot(pot_type)
    
    def _handle_shop_activate_pet(self, pet_type: str):
        """Handle pet activation from shop"""
        return self._handle_pet_activate(pet_type)

    def _handle_show_quests(self):
        """Handle quests display"""
        active_quests = self.game_engine.get_active_quests(self.state)
        self.ui_manager.show_quests(
            active_quests,
            self._handle_claim_quest,
            self._handle_close_quests
        )

    def _handle_claim_quest(self, quest_id: str):
        """Handle quest reward claiming"""
        success = self.game_engine.complete_quest(self.state, quest_id)
        if success:
            self.ui_manager.update_money_display(self.state.money)
            save_state(self.state)

    def _handle_close_quests(self):
        """Handle quests window closing"""
        # Refresh settings menu to update any changes
        self._handle_show_settings_menu()
    
    def _handle_show_profile(self):
        """Handle profile display"""
        self.profile_manager.show_profile(
            self.root, self.state, lambda: save_state(self.state)
        )

    def _handle_show_seed_menu(self):
        """Handle seed menu display"""
        self.event_handler.create_seed_menu(
            self.root, self.state, self.event_handler.on_plant_seed
        )

    def _handle_bug_click(self, event):
        """Handle bug click for catching"""
        success = self.game_engine.catch_bug(self.state)
        if success:
            save_state(self.state)
    
    def _place_initial_position(self):
        """Place window at initial position"""
        self.root.update_idletasks()
        
        if self.state.x is not None and self.state.y is not None:
            self.root.geometry(f"+{self.state.x}+{self.state.y}")
            return
        
        # bottom-right corner
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        w = self.root.winfo_reqwidth()
        h = self.root.winfo_reqheight()
        
        x = max(0, sw - w - 20)
        y = max(0, sh - h - 60)
        self.root.geometry(f"+{x}+{y}")
