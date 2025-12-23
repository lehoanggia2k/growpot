from __future__ import annotations

import tkinter as tk
from tkinter import Toplevel, Menu
from growpot.state import GameState, now_ts
from growpot.game_config import GameConfig
from growpot.ui_config import UIConfig


class PetManager:
    """Manages the pet system including status, feeding, and activation"""
    
    def __init__(self, config: GameConfig, ui_config: UIConfig):
        self.cfg = config
        self.ui = ui_config
    
    def show_pet_status(self, root: tk.Tk, state: GameState,
                       feed_callback: callable, activate_callback: callable,
                       deactivate_callback: callable, unlock_callback: callable):
        """Create and show the pet status dialog"""
        # Create pet status dialog
        pet_win = Toplevel(root)
        pet_win.title(self.ui.pet_status_title)
        pet_win.geometry(f"{self.ui.default_popup_width}x{self.ui.default_popup_height}")
        pet_win.resizable(self.ui.default_popup_resizable, self.ui.default_popup_resizable)
        
        # Main frame
        main_frame = tk.Frame(pet_win, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text=self.ui.pet_status_title, font=("Segoe UI", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Pet status frame
        status_frame = tk.Frame(main_frame)
        status_frame.pack(fill="x", pady=10)
        
        # Current active pet
        if state.active_pet:
            self._create_active_pet_section(status_frame, state, pet_win, feed_callback, deactivate_callback)
        else:
            self._create_no_pet_section(status_frame)
        
        # Available pets section
        available_frame = tk.Frame(main_frame)
        available_frame.pack(fill="x", pady=10)
        
        available_label = tk.Label(
            available_frame,
            text="Available Pets:",
            font=("Segoe UI", 11, "bold")
        )
        available_label.pack(anchor="w", pady=5)
        
        # List available pets
        for pet_type, pet_stats in self.cfg.PET_STATS.items():
            self._create_pet_option(available_frame, pet_type, pet_stats, state, pet_win, activate_callback, unlock_callback)
        
        # Close button
        close_btn = tk.Button(
            main_frame,
            text=self.ui.pet_close_button,
            command=pet_win.destroy,
            font=("Segoe UI", 10),
            relief="raised"
        )
        close_btn.pack(pady=(20, 0))
    
    def _create_active_pet_section(self, parent: tk.Frame, state: GameState, pet_win: Toplevel,
                                   feed_callback: callable, deactivate_callback: callable):
        """Create section for active pet"""
        active_label = tk.Label(
            parent,
            text=self.ui.pet_active_label.format(state.active_pet.capitalize()),
            font=("Segoe UI", 11),
            fg="green"
        )
        active_label.pack(anchor="w", pady=2)
        
        # Pet food stock
        food_label = tk.Label(
            parent,
            text=f"Pet Food: {state.pet_food}",
            font=("Segoe UI", 10),
            fg="purple"
        )
        food_label.pack(anchor="w", pady=2)
        
        # Time until hungry
        time_remaining = self.get_pet_time_remaining(state)
        time_label = tk.Label(
            parent,
            text=self.ui.pet_time_until_hungry.format(time_remaining),
            font=("Segoe UI", 10),
            fg="blue"
        )
        time_label.pack(anchor="w", pady=2)
        
        # Feed button (only if has pet food)
        if state.pet_food > 0:
            feed_btn = tk.Button(
                parent,
                text=self.ui.pet_feed_button,
                command=lambda: self._feed_pet(pet_win, feed_callback),
                font=("Segoe UI", 10),
                relief="raised",
                bg="lightgreen"
            )
            feed_btn.pack(pady=10)
        else:
            no_food_label = tk.Label(
                parent,
                text="No pet food available! Buy from shop.",
                font=("Segoe UI", 10),
                fg="red"
            )
            no_food_label.pack(pady=10)
        
        # Deactivate button
        deactivate_btn = tk.Button(
            parent,
            text=self.ui.pet_deactivate_button,
            command=lambda: self._deactivate_pet(pet_win, deactivate_callback),
            font=("Segoe UI", 10),
            relief="raised",
            bg="lightcoral"
        )
        deactivate_btn.pack(pady=5)
    
    def _create_no_pet_section(self, parent: tk.Frame):
        """Create section when no active pet"""
        no_pet_label = tk.Label(
            parent,
            text=self.ui.pet_no_active,
            font=("Segoe UI", 11),
            fg="gray"
        )
        no_pet_label.pack(anchor="w", pady=10)
    
    def _create_pet_option(self, parent: tk.Frame, pet_type: str, pet_stats, state: GameState,
                           pet_win: Toplevel, activate_callback: callable, unlock_callback: callable):
        """Create pet option widget"""
        pet_name = pet_type.capitalize()
        
        if pet_type in state.unlocked_pets:
            # Pet is unlocked, show activate button if not active
            if state.active_pet != pet_type:
                activate_btn = tk.Button(
                    parent,
                    text=f"{pet_name} - {self.ui.pet_activate_button}",
                    command=lambda: self._activate_pet(pet_type, pet_win, activate_callback),
                    font=("Segoe UI", 9),
                    relief="raised",
                    bg="lightblue"
                )
                activate_btn.pack(fill="x", pady=2)
        else:
            # Pet is locked, show unlock option
            cost = pet_stats.unlock_cost
            unlock_label = self.ui.pet_unlock_label.format(pet_name, cost)
            unlock_btn = tk.Button(
                parent,
                text=unlock_label,
                command=lambda: self._unlock_pet(pet_type, cost, pet_win, unlock_callback),
                font=("Segoe UI", 9),
                relief="raised",
                bg="lightyellow"
            )
            unlock_btn.pack(fill="x", pady=2)
    
    def get_pet_time_remaining(self, state: GameState) -> str:
        """Get time remaining until pet is hungry"""
        if not state.active_pet:
            return "N/A"
        
        pet_stats = self.cfg.PET_STATS[state.active_pet]
        work_duration = pet_stats.work_duration_sec
        time_fed = state.pet_last_fed_ts
        time_remaining = work_duration - (now_ts() - time_fed)
        
        if time_remaining <= 0:
            return "Hungry now!"
        
        hours = int(time_remaining // 3600)
        minutes = int((time_remaining % 3600) // 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def unlock_pet_transaction(self, state: GameState, pet_type: str, cost: int) -> bool:
        """Perform pet unlock transaction"""
        # Check if already unlocked
        if pet_type in state.unlocked_pets:
            return False
        
        # Check if player has enough money
        if state.money < cost:
            return False
        
        # Deduct cost and unlock pet
        state.money -= cost
        state.unlocked_pets.add(pet_type)
        return True
    
    def activate_pet_transaction(self, state: GameState, pet_type: str) -> bool:
        """Activate a pet"""
        # Check if pet is unlocked
        if pet_type not in state.unlocked_pets:
            return False
        
        # Activate the pet
        state.active_pet = pet_type
        state.pet_last_fed_ts = now_ts()
        state.pet_last_worked_ts = now_ts()
        return True
    
    def deactivate_pet_transaction(self, state: GameState) -> bool:
        """Deactivate the current pet"""
        if not state.active_pet:
            return False
        
        state.active_pet = None
        return True
    
    def feed_pet_transaction(self, state: GameState) -> bool:
        """Feed the active pet"""
        if not state.active_pet:
            return False
        
        # Check if player has pet food
        if state.pet_food <= 0:
            return False  # No pet food available
        
        # Feed the pet (consume pet food and reset working time)
        state.pet_food -= 1
        state.pet_last_fed_ts = now_ts()
        state.pet_last_worked_ts = now_ts()
        return True
    
    def _feed_pet(self, pet_win: Toplevel, feed_callback: callable):
        """Handle pet feed button click"""
        success = feed_callback()
        if success:
            pet_win.destroy()
            # Note: The callback should trigger showing pet status again if needed
    
    def _activate_pet(self, pet_type: str, pet_win: Toplevel, activate_callback: callable):
        """Handle pet activate button click"""
        success = activate_callback(pet_type)
        if success:
            pet_win.destroy()
            # Note: The callback should trigger showing pet status again if needed
    
    def _deactivate_pet(self, pet_win: Toplevel, deactivate_callback: callable):
        """Handle pet deactivate button click"""
        success = deactivate_callback()
        if success:
            pet_win.destroy()
            # Note: The callback should trigger showing pet status again if needed
    
    def _unlock_pet(self, pet_type: str, cost: int, pet_win: Toplevel, unlock_callback: callable):
        """Handle pet unlock button click"""
        success = unlock_callback(pet_type, cost)
        if success:
            pet_win.destroy()
            # Note: The callback should trigger showing pet status again if needed
    
    def is_pet_hungry(self, state: GameState) -> bool:
        """Check if the active pet is hungry"""
        if not state.active_pet:
            return False
        
        pet_stats = self.cfg.PET_STATS[state.active_pet]
        time_since_fed = now_ts() - state.pet_last_fed_ts
        return time_since_fed >= pet_stats.work_duration_sec
    
    def can_pet_work(self, state: GameState) -> bool:
        """Check if the active pet can work (not hungry)"""
        if not state.active_pet:
            return False
        return not self.is_pet_hungry(state)
