from __future__ import annotations

import tkinter as tk
from pathlib import Path
from typing import Optional

try:
    import winsound
except Exception:  # pragma: no cover
    winsound = None

from growpot.state import GameState, save_state, now_ts
from growpot.ui_config import UIConfig


class EventHandler:
    """Handles all user interface events and interactions"""
    
    def __init__(self, root: tk.Tk, assets_dir: Path, ui_config: UIConfig):
        self.root = root
        self.assets_dir = assets_dir
        self.ui = ui_config
        self._drag_start: Optional[tuple[int, int]] = None
        
        # Store callbacks for various actions
        self._callbacks: dict[str, callable] = {}
    
    def register_callback(self, event_name: str, callback: callable):
        """Register a callback for a specific event"""
        self._callbacks[event_name] = callback
    
    def on_drag_start(self, event: tk.Event):
        """Handle drag start event"""
        self._drag_start = (event.x_root, event.y_root)
    
    def on_drag_move(self, event: tk.Event):
        """Handle drag move event"""
        if not self._drag_start:
            return
        
        sx, sy = self._drag_start
        dx = event.x_root - sx
        dy = event.y_root - sy
        
        x = self.root.winfo_x() + dx
        y = self.root.winfo_y() + dy
        
        self.root.geometry(f"+{x}+{y}")
        self._drag_start = (event.x_root, event.y_root)
    
    def on_drag_end(self, event: tk.Event):
        """Handle drag end event"""
        self._drag_start = None
        self._store_window_pos()
        if 'save_state' in self._callbacks:
            self._callbacks['save_state']()
    
    def on_close(self):
        """Handle application close event"""
        self._store_window_pos()
        if 'update_last_time' in self._callbacks:
            self._callbacks['update_last_time']()
        if 'save_state' in self._callbacks:
            self._callbacks['save_state']()
        self.root.destroy()
    
    def on_settings_click(self):
        """Handle settings button click"""
        if 'show_settings_menu' in self._callbacks:
            self._callbacks['show_settings_menu']()
    
    def on_water(self):
        """Handle water button click"""
        if 'water_plant' in self._callbacks:
            self._callbacks['water_plant']()
        self._play_sound(self.assets_dir / "sounds" / "water.wav")
    
    def on_harvest(self):
        """Handle harvest button click"""
        if 'harvest_plant' in self._callbacks:
            self._callbacks['harvest_plant']()
    
    def on_reset(self):
        """Handle reset button click"""
        if 'reset_plant' in self._callbacks:
            self._callbacks['reset_plant']()
    
    def on_show_warehouse(self):
        """Handle warehouse menu click"""
        if 'show_warehouse' in self._callbacks:
            self._callbacks['show_warehouse']()
    
    def on_show_pet_status(self):
        """Handle pet status menu click"""
        if 'show_pet_status' in self._callbacks:
            self._callbacks['show_pet_status']()
    
    def on_show_shop(self):
        """Handle shop menu click"""
        if 'show_shop' in self._callbacks:
            self._callbacks['show_shop']()

    def on_show_quests(self):
        """Handle quests menu click"""
        if 'show_quests' in self._callbacks:
            self._callbacks['show_quests']()

    def on_show_profile(self):
        """Handle profile menu click"""
        if 'show_profile' in self._callbacks:
            self._callbacks['show_profile']()
    
    def on_show_seed_menu(self):
        """Handle seed menu click"""
        if 'show_seed_menu' in self._callbacks:
            self._callbacks['show_seed_menu']()
    
    def on_plant_seed(self, plant_type: str):
        """Handle seed planting"""
        if 'plant_seed' in self._callbacks:
            self._callbacks['plant_seed'](plant_type)
    
    def on_change_pot(self, pot_type: str):
        """Handle pot change"""
        if 'change_pot' in self._callbacks:
            self._callbacks['change_pot'](pot_type)
    
    def on_unlock_pot(self, pot_type: str, cost: int):
        """Handle pot unlock"""
        if 'unlock_pot' in self._callbacks:
            self._callbacks['unlock_pot'](pot_type, cost)
    
    def _store_window_pos(self):
        """Store current window position in state"""
        try:
            if 'get_state' in self._callbacks:
                state = self._callbacks['get_state']()
                state.x = self.root.winfo_x()
                state.y = self.root.winfo_y()
        except Exception:
            pass
    
    def _play_sound(self, wav_path: Path):
        """Play a sound file"""
        if winsound is None:
            return
        if not wav_path.exists():
            return
        try:
            winsound.PlaySound(str(wav_path), winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception:
            pass
    
    def create_seed_menu(self, root: tk.Tk, state: GameState, plant_seed_callback: callable):
        """Create and show seed planting menu"""
        from tkinter import Menu
        
        # Create seed planting submenu
        seed_menu = Menu(root, tearoff=0)
        
        # Get all available plant types from config
        if 'get_game_config' in self._callbacks:
            cfg = self._callbacks['get_game_config']()
            available_plants = list(cfg.PLANT_STATS.keys())
        else:
            available_plants = []
        
        for plant_type in available_plants:
            if 'get_game_config' in self._callbacks:
                cfg = self._callbacks['get_game_config']()
                stats = cfg.PLANT_STATS[plant_type]
                plant_name = plant_type.capitalize()
                current_stock = state.seed_inventory.get(plant_type, 0)

                if current_stock > 0:
                    if state.level >= stats.unlock_level:
                        label = f"{plant_name} ({self.ui.shop_seed_stock_label.format(current_stock)})"
                    else:
                        label = f"{plant_name} (Level {stats.unlock_level} cần thiết)"
                else:
                    cost = stats.seed_price
                    if cost == 0:
                        if state.level >= stats.unlock_level:
                            label = self.ui.seed_free_label.format(plant_name)
                        else:
                            label = f"{plant_name} (Level {stats.unlock_level} cần thiết)"
                    else:
                        if state.level >= stats.unlock_level:
                            label = self.ui.seed_cost_label.format(plant_name, cost)
                        else:
                            label = f"{plant_name} (Level {stats.unlock_level} cần thiết)"

                # Only add command if player has stock or meets level requirement
                if current_stock > 0 or state.level >= stats.unlock_level:
                    seed_menu.add_command(
                        label=label,
                        command=lambda pt=plant_type: plant_seed_callback(pt)
                    )
                else:
                    # Add disabled item for plants that require higher level
                    seed_menu.add_command(
                        label=label + " - Chưa đủ level",
                        command=lambda: None,  # Disabled
                        state="disabled"
                    )
        
        # Position menu below settings button
        if 'get_settings_button' in self._callbacks:
            btn = self._callbacks['get_settings_button']()
            x = btn.winfo_rootx()
            y = btn.winfo_rooty() + btn.winfo_height()
            seed_menu.post(x, y)
        
        return seed_menu
    
    def create_pot_menu(self, root: tk.Tk, state: GameState, change_pot_callback: callable, 
                       unlock_pot_callback: callable):
        """Create pot selection submenu"""
        from tkinter import Menu
        
        pot_menu = Menu(root, tearoff=0)
        
        if 'get_game_config' in self._callbacks:
            cfg = self._callbacks['get_game_config']()
            for pot_type, pot_stats in cfg.POT_STATS.items():
                pot_name = pot_type.capitalize()
                if pot_type in state.unlocked_pots:
                    pot_menu.add_command(
                        label=pot_name, 
                        command=lambda pt=pot_type: change_pot_callback(pt)
                    )
                else:
                    cost = pot_stats.price
                    pot_menu.add_command(
                        label=self.ui.pot_cost_label.format(pot_name, cost),
                        command=lambda pt=pot_type, c=cost: unlock_pot_callback(pt, c)
                    )
        
        return pot_menu
    
    def rebuild_pot_menu(self, pot_menu, state: GameState, change_pot_callback: callable, 
                        unlock_pot_callback: callable):
        """Rebuild the pot menu to reflect current unlock status"""
        # Clear existing pot menu
        pot_menu.delete(0, "end")
        
        if 'get_game_config' in self._callbacks:
            cfg = self._callbacks['get_game_config']()
            # Rebuild pot menu with current unlock status
            for pot_type, pot_stats in cfg.POT_STATS.items():
                pot_name = pot_type.capitalize()
                if pot_type in state.unlocked_pots:
                    pot_menu.add_command(
                        label=pot_name, 
                        command=lambda pt=pot_type: change_pot_callback(pt)
                    )
                else:
                    cost = pot_stats.price
                    pot_menu.add_command(
                        label=self.ui.pot_cost_label.format(pot_name, cost),
                        command=lambda pt=pot_type, c=cost: unlock_pot_callback(pt, c)
                    )
