from __future__ import annotations

import tkinter as tk
from tkinter import Toplevel, ttk
from growpot.state import GameState
from growpot.game_config import GameConfig
from growpot.ui_config import UIConfig


class ShopManager:
    """Manages the shop system for buying items, seeds, pots, and pets"""
    
    def __init__(self, config: GameConfig, ui_config: UIConfig):
        from growpot.game_config import ShopConfig
        self.cfg = config
        self.ui = ui_config
        self.shop_cfg = ShopConfig()
    
    def show_shop(self, root: tk.Tk, state: GameState, 
                  buy_pet_food_callback: callable, buy_seeds_callback: callable,
                  buy_pot_callback: callable, buy_pet_callback: callable,
                  switch_pot_callback: callable, activate_pet_callback: callable,
                  update_money_callback: callable):
        """Create and show the shop dialog with tabbed interface"""
        shop_win = Toplevel(root)
        shop_win.title(self.ui.shop_title)
        shop_win.geometry("400x350")
        shop_win.resizable(True, True)
        
        # Main frame
        main_frame = tk.Frame(shop_win, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text=self.ui.shop_title, font=("Segoe UI", 14, "bold"))
        title_label.pack(pady=(0, 15))
        
        # Money display
        money_label = tk.Label(
            main_frame,
            text=self.ui.money_format.format(state.money),
            font=("Segoe UI", 12, "bold"),
            fg="green"
        )
        money_label.pack(pady=(0, 10))
        
        # Notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True, pady=(0, 10))
        
        # Create tabs
        pet_food_frame = tk.Frame(notebook)
        seeds_frame = tk.Frame(notebook)
        pots_frame = tk.Frame(notebook)
        pets_frame = tk.Frame(notebook)
        
        notebook.add(pet_food_frame, text=self.ui.shop_tab_pet_food)
        notebook.add(seeds_frame, text=self.ui.shop_tab_seeds)
        notebook.add(pots_frame, text=self.ui.shop_tab_pots)
        notebook.add(pets_frame, text=self.ui.shop_tab_pets)
        
        # Populate tabs
        self._populate_pet_food_tab(pet_food_frame, shop_win, state, buy_pet_food_callback)
        self._populate_seeds_tab(seeds_frame, shop_win, state, buy_seeds_callback)
        self._populate_pots_tab(pots_frame, shop_win, state, buy_pot_callback, switch_pot_callback)
        self._populate_pets_tab(pets_frame, shop_win, state, buy_pet_callback, activate_pet_callback)
        
        # Close button
        close_btn = tk.Button(
            main_frame,
            text=self.ui.shop_close_button,
            command=shop_win.destroy,
            font=("Segoe UI", 10),
            relief="raised"
        )
        close_btn.pack(pady=(10, 0))
    
    def _create_scrollable_tab_frame(self, parent: tk.Frame):
        """Create a scrollable frame setup with improved UX"""
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Bind mouse wheel events for scrolling on the entire parent frame
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        def _on_mousewheel_linux(event):
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")

        parent.bind("<Enter>", lambda e: parent.focus_set())
        parent.bind("<MouseWheel>", _on_mousewheel)  # Windows
        parent.bind("<Button-4>", _on_mousewheel_linux)  # Linux scroll up
        parent.bind("<Button-5>", _on_mousewheel_linux)  # Linux scroll down

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        return canvas, scrollable_frame, scrollbar

    def _populate_pet_food_tab(self, parent: tk.Frame, shop_win: Toplevel, state: GameState, buy_callback: callable):
        """Populate the pet food tab"""
        # Scrollable frame for pet food
        canvas, scrollable_frame, scrollbar = self._create_scrollable_tab_frame(parent)

        # Pet Food item
        item_frame = tk.Frame(scrollable_frame, padx=20, pady=20)
        item_frame.pack(fill="both", expand=True)

        # Item info
        name_label = tk.Label(
            item_frame,
            text="Pet Food",
            font=("Segoe UI", 12, "bold")
        )
        name_label.pack(anchor="w", pady=(0, 5))

        desc_label = tk.Label(
            item_frame,
            text=self.ui.shop_pet_food_desc,
            font=("Segoe UI", 10),
            fg="gray"
        )
        desc_label.pack(anchor="w", pady=(0, 10))

        # Quantity selector
        quantity_frame = tk.Frame(item_frame)
        quantity_frame.pack(anchor="w", pady=(0, 10))

        quantity_label = tk.Label(
            quantity_frame,
            text="Số lượng:",
            font=("Segoe UI", 10)
        )
        quantity_label.pack(side="left", padx=(0, 10))

        quantity_var = tk.IntVar(value=1)
        quantity_spinbox = tk.Spinbox(
            quantity_frame,
            from_=1,
            to=99,
            textvariable=quantity_var,
            width=5,
            font=("Segoe UI", 10)
        )
        quantity_spinbox.pack(side="left")

        # Dynamic price display
        price_var = tk.StringVar()
        price_var.set(self.ui.shop_price_label.format(50))

        def update_price(*args):
            quantity = quantity_var.get()
            total_cost = 50 * quantity
            price_var.set(self.ui.shop_price_label.format(total_cost))

        quantity_var.trace_add("write", update_price)

        price_label = tk.Label(
            item_frame,
            textvariable=price_var,
            font=("Segoe UI", 11, "bold"),
            fg="blue"
        )
        price_label.pack(anchor="w", pady=(0, 10))

        # Buy button
        buy_btn = tk.Button(
            item_frame,
            text=self.ui.shop_buy_button,
            command=lambda: self._buy_pet_food(quantity_var.get(), shop_win, state, buy_callback),
            font=("Segoe UI", 14, "bold"),
            relief="raised",
            bg="lightgreen",
            padx=20,
            pady=10
        )
        buy_btn.pack(pady=(15, 0))
    
    def _populate_seeds_tab(self, parent: tk.Frame, shop_win: Toplevel, state: GameState, buy_callback: callable):
        """Populate the seeds tab"""
        # Scrollable frame for seeds
        canvas, scrollable_frame, scrollbar = self._create_scrollable_tab_frame(parent)

        # Populate seeds
        for plant_type, stats in self.cfg.PLANT_STATS.items():
            self._create_seed_item(scrollable_frame, plant_type, stats, state, shop_win, buy_callback)
    
    def _create_seed_item(self, parent: tk.Frame, plant_type: str, stats, state: GameState,
                          shop_win: Toplevel, buy_callback: callable):
        """Create a seed item widget"""
        seed_frame = tk.Frame(parent, padx=20, pady=10)
        seed_frame.pack(fill="x", padx=10, pady=5)
        
        plant_name = plant_type.capitalize()
        
        # Plant name
        name_label = tk.Label(
            seed_frame,
            text=plant_name,
            font=("Segoe UI", 11, "bold")
        )
        name_label.pack(anchor="w", pady=(0, 5))
        
        # Plant description
        plant_desc = self.shop_cfg.plant_descriptions.get(plant_type, "")
        if plant_desc:
            desc_label = tk.Label(
                seed_frame,
                text=plant_desc,
                font=("Segoe UI", 9),
                fg="gray"
            )
            desc_label.pack(anchor="w", pady=(0, 5))
        
        # Stock or price info
        current_stock = state.seed_inventory.get(plant_type, 0)
        if current_stock > 0:
            stock_label = tk.Label(
                seed_frame,
                text=self.ui.shop_seed_stock_label.format(current_stock),
                font=("Segoe UI", 10),
                fg="green"
            )
            stock_label.pack(anchor="w", pady=(0, 5))
        else:
            price_label = tk.Label(
                seed_frame,
                text=self.ui.shop_price_label.format(stats.seed_price),
                font=("Segoe UI", 10),
                fg="blue"
            )
            price_label.pack(anchor="w", pady=(0, 5))
        
        # Buy button (only if no stock)
        if current_stock == 0 and stats.seed_price > 0:
            buy_btn = tk.Button(
                seed_frame,
                text=self.ui.shop_buy_button,
                command=lambda: self._buy_seeds(plant_type, 1, stats.seed_price, shop_win, state, buy_callback),
                font=("Segoe UI", 9),
                relief="raised",
                bg="lightblue"
            )
            buy_btn.pack(pady=(5, 0))
    
    def _populate_pots_tab(self, parent: tk.Frame, shop_win: Toplevel, state: GameState,
                          buy_callback: callable, switch_callback: callable):
        """Populate the pots tab with owned and available pots"""
        # Scrollable frame for pots
        canvas, scrollable_frame, scrollbar = self._create_scrollable_tab_frame(parent)

        # Owned pots section
        owned_frame = tk.Frame(scrollable_frame, padx=20, pady=20)
        owned_frame.pack(fill="both", expand=True)

        title_label = tk.Label(
            owned_frame,
            text="Owned Pots:",
            font=("Segoe UI", 12, "bold")
        )
        title_label.pack(anchor="w", pady=(0, 15))

        # List owned pots
        for pot_type in state.unlocked_pots:
            self._create_owned_pot_item(owned_frame, pot_type, state, shop_win, switch_callback)

        # Available pots for purchase section
        available_frame = tk.Frame(scrollable_frame, padx=20, pady=20)
        available_frame.pack(fill="x")

        available_label = tk.Label(
            available_frame,
            text="Available for Purchase:",
            font=("Segoe UI", 12, "bold")
        )
        available_label.pack(anchor="w", pady=(0, 10))

        # List available pots
        for pot_type, pot_stats in self.cfg.POT_STATS.items():
            if pot_type not in state.unlocked_pots and pot_stats.price > 0:
                self._create_pot_purchase_item(available_frame, pot_type, pot_stats, shop_win, state, buy_callback)
    
    def _create_owned_pot_item(self, parent: tk.Frame, pot_type: str, state: GameState,
                               shop_win: Toplevel, switch_callback: callable):
        """Create owned pot item widget"""
        pot_frame = tk.Frame(parent)
        pot_frame.pack(fill="x", pady=5)
        
        pot_name = pot_type.capitalize()
        
        # Pot name and status
        name_label = tk.Label(
            pot_frame,
            text=pot_name,
            font=("Segoe UI", 11)
        )
        name_label.pack(side="left", anchor="w")
        
        # Status label or switch button
        if pot_type == state.pot_type:
            status_label = tk.Label(
                pot_frame,
                text=" (Current)",
                font=("Segoe UI", 10, "italic"),
                fg="green"
            )
            status_label.pack(side="left", padx=(10, 0))
        else:
            switch_btn = tk.Button(
                pot_frame,
                text="Switch",
                command=lambda: self._switch_pot(pot_type, shop_win, switch_callback),
                font=("Segoe UI", 9),
                relief="raised",
                bg="lightyellow"
            )
            switch_btn.pack(side="right", padx=(10, 0))
    
    def _create_pot_purchase_item(self, parent: tk.Frame, pot_type: str, pot_stats, shop_win: Toplevel,
                                  state: GameState, buy_callback: callable):
        """Create pot purchase item widget"""
        pot_frame = tk.Frame(parent)
        pot_frame.pack(fill="x", pady=5)
        
        pot_name = pot_type.capitalize()
        
        # Pot name and price
        name_label = tk.Label(
            pot_frame,
            text=pot_name,
            font=("Segoe UI", 11)
        )
        name_label.pack(side="left", anchor="w")
        
        price_label = tk.Label(
            pot_frame,
            text=self.ui.shop_price_label.format(pot_stats.price),
            font=("Segoe UI", 10),
            fg="blue"
        )
        price_label.pack(side="left", padx=(20, 0))
        
        # Buy button
        buy_btn = tk.Button(
            pot_frame,
            text=self.ui.shop_buy_button,
            command=lambda: self._buy_pot(pot_type, pot_stats.price, shop_win, state, buy_callback),
            font=("Segoe UI", 9),
            relief="raised",
            bg="lightgreen"
        )
        buy_btn.pack(side="right", padx=(10, 0))
    
    def _populate_pets_tab(self, parent: tk.Frame, shop_win: Toplevel, state: GameState,
                          buy_callback: callable, activate_callback: callable):
        """Populate the pets tab for purchasing pets"""
        # Scrollable frame for pets
        canvas, scrollable_frame, scrollbar = self._create_scrollable_tab_frame(parent)

        # Populate pets
        for pet_type, pet_stats in self.cfg.PET_STATS.items():
            self._create_pet_item(scrollable_frame, pet_type, pet_stats, state, shop_win, buy_callback, activate_callback)
    
    def _create_pet_item(self, parent: tk.Frame, pet_type: str, pet_stats, state: GameState,
                         shop_win: Toplevel, buy_callback: callable, activate_callback: callable):
        """Create a pet item widget"""
        pet_frame = tk.Frame(parent, padx=20, pady=10)
        pet_frame.pack(fill="x", padx=10, pady=5)
        
        pet_name = pet_type.capitalize()
        
        # Pet name
        name_label = tk.Label(
            pet_frame,
            text=pet_name,
            font=("Segoe UI", 11, "bold")
        )
        name_label.pack(anchor="w", pady=(0, 5))
        
        # Pet description
        desc = self.shop_cfg.pet_descriptions.get(pet_type, "")
        if desc:
            desc_label = tk.Label(
                pet_frame,
                text=desc,
                font=("Segoe UI", 9),
                fg="gray"
            )
            desc_label.pack(anchor="w", pady=(0, 5))
        
        # Status or price info
        if pet_type in state.unlocked_pets:
            if state.active_pet == pet_type:
                status_label = tk.Label(
                    pet_frame,
                    text="(Đang kích hoạt)",
                    font=("Segoe UI", 10),
                    fg="green"
                )
                status_label.pack(anchor="w", pady=(0, 5))
            else:
                activate_btn = tk.Button(
                    pet_frame,
                    text="Kích hoạt",
                    command=lambda: self._activate_pet(pet_type, shop_win, activate_callback),
                    font=("Segoe UI", 9),
                    relief="raised",
                    bg="lightblue"
                )
                activate_btn.pack(pady=(5, 0))
        else:
            cost = pet_stats.unlock_cost
            price_label = tk.Label(
                pet_frame,
                text=self.ui.shop_price_label.format(cost),
                font=("Segoe UI", 10),
                fg="blue"
            )
            price_label.pack(anchor="w", pady=(0, 5))
            
            # Buy button
            buy_btn = tk.Button(
                pet_frame,
                text=self.ui.shop_buy_button,
                command=lambda: self._buy_pet(pet_type, cost, shop_win, state, buy_callback),
                font=("Segoe UI", 9),
                relief="raised",
                bg="lightgreen"
            )
            buy_btn.pack(pady=(5, 0))
    
    def _buy_pet_food(self, quantity: int, shop_win: Toplevel, state: GameState, buy_callback: callable):
        """Handle pet food purchase"""
        cost = 50 * quantity
        success = buy_callback(quantity, cost)
        if success:
            shop_win.destroy()
        else:
            self._show_purchase_error(shop_win)
    
    def _buy_seeds(self, plant_type: str, quantity: int, cost: int, shop_win: Toplevel,
                   state: GameState, buy_callback: callable):
        """Handle seeds purchase"""
        success = buy_callback(plant_type, quantity, cost)
        if success:
            shop_win.destroy()
        else:
            self._show_purchase_error(shop_win)
    
    def _buy_pot(self, pot_type: str, cost: int, shop_win: Toplevel, state: GameState, buy_callback: callable):
        """Handle pot purchase"""
        success = buy_callback(pot_type, cost)
        if success:
            shop_win.destroy()
        else:
            self._show_purchase_error(shop_win)
    
    def _buy_pet(self, pet_type: str, cost: int, shop_win: Toplevel, state: GameState, buy_callback: callable):
        """Handle pet purchase"""
        success = buy_callback(pet_type, cost)
        if success:
            shop_win.destroy()
        else:
            self._show_purchase_error(shop_win)
    
    def _switch_pot(self, pot_type: str, shop_win: Toplevel, switch_callback: callable):
        """Handle pot switching"""
        success = switch_callback(pot_type)
        if success:
            shop_win.destroy()
    
    def _activate_pet(self, pet_type: str, shop_win: Toplevel, activate_callback: callable):
        """Handle pet activation"""
        success = activate_callback(pet_type)
        if success:
            shop_win.destroy()
    
    def _show_purchase_error(self, parent_window: Toplevel):
        """Show not enough money error"""
        error_win = Toplevel(parent_window)
        error_win.title("Lỗi")
        error_win.geometry("250x100")
        error_win.resizable(False, False)
        
        # Center the error window
        error_win.transient(parent_window)
        error_win.grab_set()
        
        error_label = tk.Label(
            error_win,
            text=self.ui.shop_not_enough_money,
            font=("Segoe UI", 11),
            fg="red"
        )
        error_label.pack(pady=20)
        
        ok_btn = tk.Button(
            error_win,
            text="OK",
            command=error_win.destroy,
            font=("Segoe UI", 10),
            relief="raised"
        )
        ok_btn.pack(pady=(0, 20))
    
    # Transaction methods
    def buy_pet_food_transaction(self, state: GameState, quantity: int, cost: int) -> bool:
        """Perform pet food purchase transaction"""
        if quantity <= 0 or cost < 0 or state.money < cost:
            return False

        state.money -= cost
        state.pet_food += quantity
        return True
    
    def buy_seeds_transaction(self, state: GameState, plant_type: str, quantity: int, cost: int) -> bool:
        """Perform seeds purchase transaction"""
        if quantity <= 0 or cost < 0 or state.money < cost:
            return False
        
        state.money -= cost
        if plant_type not in state.seed_inventory:
            state.seed_inventory[plant_type] = 0
        state.seed_inventory[plant_type] += quantity
        return True
    
    def buy_pot_transaction(self, state: GameState, pot_type: str, cost: int) -> bool:
        """Perform pot purchase transaction"""
        if state.money < cost:
            return False
        
        state.money -= cost
        state.unlocked_pots.add(pot_type)
        return True
    
    def buy_pet_transaction(self, state: GameState, pet_type: str, cost: int) -> bool:
        """Perform pet purchase transaction"""
        if state.money < cost:
            return False
        
        state.money -= cost
        state.unlocked_pets.add(pet_type)
        return True
