from __future__ import annotations

import tkinter as tk
from tkinter import Menu, ttk
from pathlib import Path
from typing import Callable

from growplot.ui_config import UIConfig
from growplot.state import GameState


class UIManager:
    """Manages all UI components for the GrowPlot application"""
    
    def __init__(self, root: tk.Tk, max_canvas_width: int, max_canvas_height: int, ui_config: UIConfig):
        self.root = root
        self.ui = ui_config
        self.max_canvas_width = max_canvas_width
        self.max_canvas_height = max_canvas_height
        
        # Style for progress bars
        self.style = ttk.Style()
        self.style.configure("Water.Horizontal.TProgressbar", troughcolor="lightgray", background="blue")
        
        # Setup main container
        self.container = tk.Frame(self.root, bg="magenta")
        self.container.pack(fill="both", expand=True)
        
        # Setup canvas
        self.canvas = tk.Canvas(
            self.container,
            width=self.max_canvas_width,
            height=self.max_canvas_height,
            bg="magenta",
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(side="top", fill="both", expand=True)
        
        # Create image item for plant/pot display
        self.img_item = self.canvas.create_image(
            self.max_canvas_width // 2, 
            self.max_canvas_height // 2, 
            anchor="center"
        )
        
        # Setup progress bars frame (hidden by default)
        self.progress_frame = tk.Frame(self.container, bg="magenta")
        self.progress_frame.pack_forget()
        
        # Harvest progress bar
        self.harvest_progress = ttk.Progressbar(
            self.progress_frame,
            orient="horizontal",
            length=160,
            mode="determinate",
            maximum=100,
            value=0,
            style="TProgressbar"
        )
        self.harvest_progress.pack(side="top", pady=(2, 1))
        
        # Water progress bar
        self.water_progress = ttk.Progressbar(
            self.progress_frame,
            orient="horizontal",
            length=160,
            mode="determinate",
            maximum=100,
            value=0,
            style="Water.Horizontal.TProgressbar"
        )
        self.water_progress.pack(side="top", pady=(1, 2))
        
        # Setup controls frame
        self.controls = tk.Frame(self.container, bg="magenta")
        self.controls.pack(side="bottom", fill="x")
        
        # Money display
        self.money_label = tk.Label(
            self.controls,
            text="",  # Will be set by update_money_display
            bg="magenta",
            fg="white",
            font=("Segoe UI", 10),
        )
        self.money_label.pack(side="left", padx=(6, 4), pady=6)
        
        # Settings button
        self.btn_settings = tk.Button(
            self.controls,
            text=self.ui.settings_button_text,
            command=None,  # Will be set by main app
            relief="raised",
            font=("Segoe UI", 12),
            width=2,
        )
        self.btn_settings.pack(side="right", padx=(4, 6), pady=6)
        
        # Setup settings menu
        self.settings_menu = Menu(self.root, tearoff=0)
        
        # Bind hover events
        self.canvas.bind("<Enter>", self._show_progress_bars)
        self.canvas.bind("<Leave>", self._hide_progress_bars)
        
        # Drag state
        self._drag_start: tuple[int, int] | None = None
        
        # Store callbacks
        self._callbacks: dict[str, Callable] = {}
    
    def setup_settings_menu(self, state: GameState, water_callback: Callable, harvest_callback: Callable, 
                           seed_menu_callback: Callable, reset_callback: Callable, warehouse_callback: Callable,
                           pet_status_callback: Callable, shop_callback: Callable, pot_menu: Menu,
                           close_callback: Callable):
        """Setup the settings menu with all callbacks"""
        
        # Clear existing menu items
        self.settings_menu.delete(0, "end")
        
        # Add menu items
        self.settings_menu.add_command(label=self.ui.menu_water, command=water_callback)
        self.settings_menu.add_command(label=self.ui.menu_harvest, command=harvest_callback, state="disabled")
        self.settings_menu.add_command(label=self.ui.menu_plant_seed, command=seed_menu_callback)
        self.settings_menu.add_command(label=self.ui.menu_reset, command=reset_callback)
        self.settings_menu.add_command(label=self.ui.menu_warehouse, command=warehouse_callback)
        self.settings_menu.add_command(label=self.ui.menu_pet, command=pet_status_callback)
        self.settings_menu.add_command(label=self.ui.menu_shop, command=shop_callback)
        self.settings_menu.add_separator()
        self.settings_menu.add_cascade(label=self.ui.menu_change_pot, menu=pot_menu)
        self.settings_menu.add_separator()
        self.settings_menu.add_command(label=self.ui.menu_quit, command=close_callback)
        
        # Store harvest callback for enabling/disabling
        self._callbacks['harvest'] = harvest_callback
    
    def update_money_display(self, money: int):
        """Update the money display label"""
        self.money_label.config(text=self.ui.money_format.format(money))
    
    def update_harvest_menu_state(self, enabled: bool):
        """Enable or disable harvest menu item"""
        state = "normal" if enabled else "disabled"
        try:
            self.settings_menu.entryconfig(self.ui.menu_harvest, state=state)
        except tk.TclError:
            pass  # Menu item might not exist yet
    
    def update_progress_bars(self, growth: float, water: float, plant_at: float):
        """Update the progress bars with current values"""
        # Harvest progress: 0-100% based on growth / plant_at
        harvest_percent = min(100.0, (growth / plant_at) * 100.0) if growth >= 0 else 0.0
        self.harvest_progress.config(value=harvest_percent)
        
        # Water progress: 0-100% based on water level (assuming max ~5.0)
        max_water = 5.0
        water_percent = min(100.0, (water / max_water) * 100.0)
        self.water_progress.config(value=water_percent)
    
    def update_canvas_image(self, image: tk.PhotoImage):
        """Update the canvas image"""
        self.canvas.itemconfigure(self.img_item, image=image)
    
    def resize_canvas(self, new_width: int, new_height: int):
        """Resize the canvas and update image position"""
        self.max_canvas_width = new_width
        self.max_canvas_height = new_height
        self.canvas.config(width=new_width, height=new_height)
        self.canvas.coords(self.img_item, new_width // 2, new_height // 2)
    
    def setup_drag_handlers(self, drag_start_callback: Callable, drag_move_callback: Callable, 
                           drag_end_callback: Callable):
        """Setup drag event handlers"""
        self.canvas.bind("<ButtonPress-1>", drag_start_callback)
        self.canvas.bind("<B1-Motion>", drag_move_callback)
        self.canvas.bind("<ButtonRelease-1>", drag_end_callback)
    
    def show_settings_menu(self):
        """Show the settings menu below the settings button"""
        x = self.btn_settings.winfo_rootx()
        y = self.btn_settings.winfo_rooty() + self.btn_settings.winfo_height()
        self.settings_menu.post(x, y)
    
    def _show_progress_bars(self, event: tk.Event):
        """Show progress bars on hover"""
        self.progress_frame.pack(side="top", after=self.canvas)
    
    def _hide_progress_bars(self, event: tk.Event):
        """Hide progress bars when mouse leaves"""
        self.progress_frame.pack_forget()
    
    def create_pet_image_item(self) -> int:
        """Create pet image item on canvas"""
        return self.canvas.create_image(0, 0, anchor="center")
    
    def update_pet_image(self, pet_img_item: int, image, x: int, y: int):
        """Update pet image and position"""
        if pet_img_item and image:
            self.canvas.coords(pet_img_item, x, y)
            self.canvas.itemconfigure(pet_img_item, image=image)
    
    def delete_pet_image(self, pet_img_item: int):
        """Delete pet image from canvas"""
        if pet_img_item:
            self.canvas.delete(pet_img_item)
