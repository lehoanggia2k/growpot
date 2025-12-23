from __future__ import annotations

import tkinter as tk
from tkinter import Menu, ttk
from pathlib import Path
from typing import Callable

from growpot.ui_config import UIConfig
from growpot.state import GameState


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

        # Bug display
        self.bug_item = None  # Canvas item for bug display

        # Store callbacks
        self._callbacks: dict[str, Callable] = {}
    
    def setup_settings_menu(self, state: GameState, water_callback: Callable, harvest_callback: Callable,
                           seed_menu_callback: Callable, reset_callback: Callable, warehouse_callback: Callable,
                           pet_status_callback: Callable, shop_callback: Callable, quests_callback: Callable,
                           profile_callback: Callable, pot_menu: Menu, close_callback: Callable):
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
        self.settings_menu.add_command(label=self.ui.menu_quests, command=quests_callback)
        self.settings_menu.add_command(label=self.ui.menu_profile, command=profile_callback)
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

    def show_bug(self, x: int, y: int, click_callback: Callable = None):
        """Show bug on canvas at specified position"""
        if self.bug_item is None:
            # Create bug as red circle
            self.bug_item = self.canvas.create_oval(
                x - 8, y - 8, x + 8, y + 8,
                fill="red",
                outline="darkred",
                width=2
            )
            # Bind click handler to the new bug item
            if click_callback:
                self.canvas.tag_bind(self.bug_item, "<Button-1>", click_callback)
        else:
            # Update existing bug position
            self.canvas.coords(self.bug_item, x - 8, y - 8, x + 8, y + 8)
            self.canvas.itemconfigure(self.bug_item, state="normal")

    def hide_bug(self):
        """Hide bug from canvas"""
        if self.bug_item:
            self.canvas.itemconfigure(self.bug_item, state="hidden")

    def delete_bug(self):
        """Delete bug from canvas"""
        if self.bug_item:
            self.canvas.delete(self.bug_item)
            self.bug_item = None



    def get_bug_position(self) -> tuple[int, int]:
        """Get current bug position"""
        if self.bug_item:
            coords = self.canvas.coords(self.bug_item)
            if len(coords) >= 4:
                x = (coords[0] + coords[2]) // 2
                y = (coords[1] + coords[3]) // 2
                return int(x), int(y)
        return 0, 0

    def show_quests(self, quests: list[dict], claim_callback: Callable, close_callback: Callable):
        """Show daily quests window"""
        # Create quest window
        quest_window = tk.Toplevel(self.root)
        quest_window.title(self.ui.quest_title)
        quest_window.geometry(f"{self.ui.default_popup_width}x{self.ui.default_popup_height}")
        quest_window.resizable(self.ui.default_popup_resizable, self.ui.default_popup_resizable)
        quest_window.attributes("-topmost", True)

        # Title
        title_label = tk.Label(
            quest_window,
            text=self.ui.quest_title,
            font=("Segoe UI", 16, "bold"),
            pady=10
        )
        title_label.pack()

        # Quest list frame
        quest_frame = tk.Frame(quest_window)
        quest_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        if not quests:
            # No quests message
            no_quests_label = tk.Label(
                quest_frame,
                text=self.ui.quest_no_quests,
                font=("Segoe UI", 12),
                justify="center"
            )
            no_quests_label.pack(expand=True)
        else:
            # Create scrollable frame for quests
            canvas = tk.Canvas(quest_frame, height=300)
            scrollbar = tk.Scrollbar(quest_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas)

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # Display each quest
            for quest in quests:
                self._create_quest_item(scrollable_frame, quest, claim_callback)

        # Close button
        close_button = tk.Button(
            quest_window,
            text=self.ui.quest_close_button,
            command=lambda: [quest_window.destroy(), close_callback()],
            font=("Segoe UI", 12),
            width=10
        )
        close_button.pack(pady=(0, 20))

    def _create_quest_item(self, parent: tk.Frame, quest: dict, claim_callback: Callable):
        """Create a quest item widget"""
        # Quest frame
        quest_frame = tk.Frame(parent, relief="solid", borderwidth=1, padx=10, pady=10)
        quest_frame.pack(fill="x", pady=(0, 10))

        # Quest name
        name_label = tk.Label(
            quest_frame,
            text=quest["name"],
            font=("Segoe UI", 12, "bold"),
            anchor="w"
        )
        name_label.pack(fill="x")

        # Quest description
        desc_label = tk.Label(
            quest_frame,
            text=quest["description"],
            font=("Segoe UI", 10),
            anchor="w",
            fg="gray"
        )
        desc_label.pack(fill="x")

        # Progress
        progress_text = self.ui.quest_progress_label.format(
            quest["current_progress"], quest["requirement_count"]
        )
        progress_label = tk.Label(
            quest_frame,
            text=progress_text,
            font=("Segoe UI", 10),
            anchor="w"
        )
        progress_label.pack(fill="x")

        # Progress bar
        progress_bar = ttk.Progressbar(
            quest_frame,
            orient="horizontal",
            length=200,
            mode="determinate",
            maximum=quest["requirement_count"],
            value=quest["current_progress"]
        )
        progress_bar.pack(fill="x", pady=(5, 5))

        # Reward
        reward_text = self.ui.quest_reward_label.format(quest["reward_money"])
        reward_label = tk.Label(
            quest_frame,
            text=reward_text,
            font=("Segoe UI", 10, "bold"),
            anchor="w",
            fg="green"
        )
        reward_label.pack(fill="x")

        # Status and claim button
        bottom_frame = tk.Frame(quest_frame)
        bottom_frame.pack(fill="x", pady=(5, 0))

        if quest["completed"] and not quest.get("claimed", False):
            # Completed, show claim button
            claim_button = tk.Button(
                bottom_frame,
                text=self.ui.quest_claim_button,
                command=lambda q=quest: [claim_callback(q["id"]), self._refresh_quests(parent)],
                font=("Segoe UI", 10),
                bg="green",
                fg="white"
            )
            claim_button.pack(side="right")
        elif quest.get("claimed", False):
            # Already claimed
            claimed_label = tk.Label(
                bottom_frame,
                text="Đã nhận",
                font=("Segoe UI", 10, "bold"),
                fg="green"
            )
            claimed_label.pack(side="right")
        elif quest["completed"]:
            # Completed but not claimed
            status_label = tk.Label(
                bottom_frame,
                text=self.ui.quest_completed_label,
                font=("Segoe UI", 10, "bold"),
                fg="green"
            )
            status_label.pack(side="right")

    def _refresh_quests(self, parent: tk.Frame):
        """Refresh the quests display after claiming"""
        # This would need to be implemented to refresh the quest list
        # For now, we'll just close and reopen, but ideally we'd update in place
        pass
