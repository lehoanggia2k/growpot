from __future__ import annotations

import tkinter as tk
from tkinter import Toplevel
from growpot.state import GameState
from growpot.game_config import GameConfig
from growpot.ui_config import UIConfig


class WarehouseManager:
    """Manages the warehouse system for storing and selling harvested items"""
    
    def __init__(self, config: GameConfig, ui_config: UIConfig):
        self.cfg = config
        self.ui = ui_config
    
    def show_warehouse(self, root: tk.Tk, state: GameState, sell_callback: callable, update_money_callback: callable):
        """Create and show the warehouse dialog"""
        # Create warehouse dialog
        warehouse_win = Toplevel(root)
        warehouse_win.title(self.ui.warehouse_title)
        warehouse_win.geometry("350x300")
        warehouse_win.resizable(False, False)
        
        # Main frame
        main_frame = tk.Frame(warehouse_win, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text=self.ui.warehouse_inventory_title, font=("Segoe UI", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Inventory list frame
        inventory_frame = tk.Frame(main_frame)
        inventory_frame.pack(fill="both", expand=True)
        
        # Display each inventory item
        has_items = False
        for plant_type, quantity in state.inventory.items():
            if quantity > 0:
                has_items = True
                self._create_inventory_item(inventory_frame, plant_type, quantity, warehouse_win, sell_callback)
        
        # If no items
        if not has_items:
            empty_label = tk.Label(
                inventory_frame,
                text=self.ui.warehouse_empty_message,
                font=("Segoe UI", 10),
                fg="gray"
            )
            empty_label.pack(pady=20)
        
        # Close button
        close_btn = tk.Button(
            main_frame,
            text=self.ui.warehouse_close_button,
            command=warehouse_win.destroy,
            font=("Segoe UI", 10),
            relief="raised"
        )
        close_btn.pack(pady=(20, 0))
    
    def _create_inventory_item(self, parent: tk.Frame, plant_type: str, quantity: int, 
                              warehouse_win: Toplevel, sell_callback: callable):
        """Create an inventory item widget"""
        item_frame = tk.Frame(parent)
        item_frame.pack(fill="x", pady=2)
        
        # Handle bugs specially
        if plant_type == "bug":
            plant_name = "Bug"
            sell_price = self.cfg.bug_sell_price
        else:
            # Get plant stats
            plant_stats = self.cfg.PLANT_STATS.get(plant_type)
            if not plant_stats:
                return

            plant_name = plant_type.capitalize()
            sell_price = plant_stats.harvest_price_per_item
        total_value = quantity * sell_price
        
        info_label = tk.Label(
            item_frame,
            text=f"{plant_name}: {quantity} items (💰{sell_price} each = 💰{total_value})",
            font=("Segoe UI", 10),
            anchor="w"
        )
        info_label.pack(side="left", fill="x", expand=True)
        
        # Sell button
        sell_btn = tk.Button(
            item_frame,
            text=self.ui.warehouse_sell_button,
            command=lambda: self._sell_items(plant_type, quantity, sell_price, warehouse_win, sell_callback),
            font=("Segoe UI", 9),
            relief="raised"
        )
        sell_btn.pack(side="right", padx=(10, 0))
    
    def _sell_items(self, plant_type: str, quantity: int, price_per_item: int, 
                   warehouse_win: Toplevel, sell_callback: callable):
        """Sell items and update state"""
        # Input validation
        if quantity <= 0:
            return  # Cannot sell zero or negative items
        if price_per_item < 0:
            return  # Cannot sell with negative price
        
        # Call the sell callback to handle the transaction
        success = sell_callback(plant_type, quantity, price_per_item)
        
        if success:
            # Close and reopen warehouse to refresh
            warehouse_win.destroy()
            # Note: The callback should trigger showing warehouse again if needed
    
    def sell_items_transaction(self, state: GameState, plant_type: str, quantity: int, price_per_item: int) -> bool:
        """Perform the sell transaction atomically"""
        # Input validation
        if quantity <= 0:
            return False
        if price_per_item < 0:
            return False
        if plant_type not in state.inventory:
            return False
        
        current_quantity = state.inventory[plant_type]
        if current_quantity < quantity:
            return False  # Not enough items to sell
        
        # Calculate total earnings
        total_earned = quantity * price_per_item
        
        # Atomic transaction: remove items first
        state.inventory[plant_type] = current_quantity - quantity
        if state.inventory[plant_type] == 0:
            del state.inventory[plant_type]
        
        # Then add money
        state.money += total_earned
        
        # Update harvested_count for backward compatibility
        state.harvested_count += quantity
        
        return True
    
    def has_inventory_items(self, state: GameState) -> bool:
        """Check if there are any items in inventory"""
        return any(quantity > 0 for quantity in state.inventory.values())
    
    def get_total_inventory_value(self, state: GameState) -> int:
        """Calculate total value of all items in inventory"""
        total_value = 0
        for plant_type, quantity in state.inventory.items():
            if quantity > 0:
                if plant_type == "bug":
                    total_value += quantity * self.cfg.bug_sell_price
                else:
                    plant_stats = self.cfg.PLANT_STATS.get(plant_type)
                    if plant_stats:
                        total_value += quantity * plant_stats.harvest_price_per_item
        return total_value
