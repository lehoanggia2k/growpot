from __future__ import annotations

import tkinter as tk
from tkinter import Toplevel, messagebox
from growpot.state import GameState
from growpot.ui_config import UIConfig


class ProfileManager:
    """Manages the player profile system including name, level, exp, and avatar"""

    def __init__(self, ui_config: UIConfig):
        self.ui = ui_config
        # Available avatars (emoji-based for now)
        self.available_avatars = [
            "👤", "👨", "👩", "🧑", "👦", "👧", "🧔", "👱", "👨‍🦱", "👩‍🦱",
            "👨‍🦰", "👩‍🦰", "👨‍🦳", "👩‍🦳", "👨‍🦲", "👩‍🦲"
        ]

    def show_profile(self, root: tk.Tk, state: GameState, save_callback: callable):
        """Create and show the profile dialog"""
        # Create profile dialog
        profile_win = Toplevel(root)
        profile_win.title(self.ui.profile_title)
        profile_win.geometry("350x400")
        profile_win.resizable(True, True)

        # Main frame
        main_frame = tk.Frame(profile_win, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        # Title
        title_label = tk.Label(main_frame, text=self.ui.profile_title, font=("Segoe UI", 16, "bold"))
        title_label.pack(pady=(0, 20))

        # Avatar section
        avatar_frame = tk.Frame(main_frame)
        avatar_frame.pack(pady=10)

        avatar_label = tk.Label(avatar_frame, text=self.ui.profile_avatar_label, font=("Segoe UI", 11, "bold"))
        avatar_label.pack()

        # Current avatar display
        current_avatar_label = tk.Label(avatar_frame, text=state.avatar, font=("Segoe UI", 48))
        current_avatar_label.pack(pady=10)

        # Avatar selection
        avatar_selection_frame = tk.Frame(avatar_frame)
        avatar_selection_frame.pack()

        # Create avatar buttons (show 8 at a time for better layout)
        avatar_buttons = []
        for i, avatar in enumerate(self.available_avatars[:8]):
            btn = tk.Button(
                avatar_selection_frame,
                text=avatar,
                font=("Segoe UI", 16),
                width=3,
                command=lambda a=avatar: self._select_avatar(a, current_avatar_label, state)
            )
            btn.grid(row=i//4, column=i%4, padx=2, pady=2)
            avatar_buttons.append(btn)

        # Name section
        name_frame = tk.Frame(main_frame)
        name_frame.pack(fill="x", pady=10)

        name_label = tk.Label(name_frame, text=self.ui.profile_name_label, font=("Segoe UI", 11, "bold"))
        name_label.pack(anchor="w")

        name_entry = tk.Entry(name_frame, font=("Segoe UI", 10), width=30)
        name_entry.insert(0, state.player_name)
        name_entry.pack(pady=5)

        # Level and EXP section
        stats_frame = tk.Frame(main_frame)
        stats_frame.pack(fill="x", pady=10)

        # Calculate EXP needed for current level
        exp_needed = self.get_exp_needed_for_level(state.level)

        level_label = tk.Label(
            stats_frame,
            text=self.ui.profile_level_label.format(state.level),
            font=("Segoe UI", 11, "bold"),
            fg="blue"
        )
        level_label.pack(anchor="w", pady=2)

        exp_label = tk.Label(
            stats_frame,
            text=self.ui.profile_exp_label.format(state.exp, exp_needed),
            font=("Segoe UI", 10),
            fg="green"
        )
        exp_label.pack(anchor="w", pady=2)

        # EXP Progress bar
        exp_progress = tk.ttk.Progressbar(
            stats_frame,
            orient="horizontal",
            length=250,
            mode="determinate",
            maximum=exp_needed,
            value=min(state.exp, exp_needed)
        )
        exp_progress.pack(pady=5)

        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=(20, 0))

        save_btn = tk.Button(
            button_frame,
            text=self.ui.profile_save_button,
            command=lambda: self._save_profile(
                profile_win, name_entry.get(), current_avatar_label.cget("text"), state, save_callback
            ),
            font=("Segoe UI", 10),
            relief="raised",
            bg="lightgreen"
        )
        save_btn.pack(side="left", padx=10)

        close_btn = tk.Button(
            button_frame,
            text=self.ui.profile_close_button,
            command=profile_win.destroy,
            font=("Segoe UI", 10),
            relief="raised"
        )
        close_btn.pack(side="right", padx=10)

    def get_exp_needed_for_level(self, level: int) -> int:
        """Calculate EXP needed for a given level"""
        return level * 100

    def add_exp(self, state: GameState, exp_amount: int) -> bool:
        """Add EXP to player and handle level ups. Returns True if leveled up."""
        old_level = state.level
        state.exp += exp_amount

        # Check for level ups
        while state.exp >= self.get_exp_needed_for_level(state.level):
            state.exp -= self.get_exp_needed_for_level(state.level)
            state.level += 1

        return state.level > old_level

    def get_exp_progress(self, state: GameState) -> tuple[int, int]:
        """Get current EXP and EXP needed for next level"""
        exp_needed = self.get_exp_needed_for_level(state.level)
        return state.exp, exp_needed

    def _select_avatar(self, avatar: str, display_label: tk.Label, state: GameState):
        """Handle avatar selection"""
        display_label.config(text=avatar)

    def _save_profile(self, profile_win: Toplevel, new_name: str, new_avatar: str,
                     state: GameState, save_callback: callable):
        """Handle profile save"""
        # Validate name
        if not new_name.strip():
            messagebox.showerror("Lỗi", "Tên không được để trống!")
            return

        if len(new_name.strip()) > 20:
            messagebox.showerror("Lỗi", "Tên không được quá 20 ký tự!")
            return

        # Update state
        state.player_name = new_name.strip()
        state.avatar = new_avatar

        # Save state
        success = save_callback()
        if success:
            messagebox.showinfo("Thành công", "Profile đã được cập nhật!")
            profile_win.destroy()
        else:
            messagebox.showerror("Lỗi", "Không thể lưu profile!")
