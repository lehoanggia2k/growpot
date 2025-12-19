from __future__ import annotations

import time
import tkinter as tk
from pathlib import Path
from typing import Optional

from growplot.anim import FrameSet, load_frames
from PIL import ImageTk
from growplot.game_config import GameConfig


class AnimationManager:
    """Handles all animation logic for plants and pets"""
    
    def __init__(self, config: GameConfig):
        self.cfg = config
        self._anim_index = 0
        self._anim_accum = 0.0
        self._pet_anim_index = 0
        self._pet_anim_accum = 0.0
        
        # Animation frames
        self.pot_frames: FrameSet | None = None
        self.plant_frames_seed: FrameSet | None = None
        self.plant_frames_sprout: FrameSet | None = None
        self.plant_frames_plant: FrameSet | None = None
        self.pet_frames: FrameSet | None = None
        
        # Current composite image
        self.current_image: tk.PhotoImage | None = None
        self.pet_img_item: Optional[int] = None
    
    def load_plant_frames(self, assets_dir: Path, plant_type: str) -> bool:
        """Load plant frames for the specified plant type"""
        try:
            self.plant_frames_seed = load_frames(assets_dir / "plants" / plant_type / "seed")
        except FileNotFoundError:
            # Fallback to old structure
            try:
                self.plant_frames_seed = load_frames(assets_dir / "seed")
            except FileNotFoundError:
                return False
        
        try:
            self.plant_frames_sprout = load_frames(assets_dir / "plants" / plant_type / "sprout")
        except FileNotFoundError:
            try:
                self.plant_frames_sprout = load_frames(assets_dir / "sprout")
            except FileNotFoundError:
                return False
        
        try:
            self.plant_frames_plant = load_frames(assets_dir / "plants" / plant_type / "plant")
        except FileNotFoundError:
            try:
                self.plant_frames_plant = load_frames(assets_dir / "plant")
            except FileNotFoundError:
                return False
        
        return True
    
    def load_pot_frames(self, assets_dir: Path, pot_type: str) -> bool:
        """Load pot frames for the specified pot type"""
        try:
            self.pot_frames = load_frames(assets_dir / "pots" / pot_type)
            return True
        except FileNotFoundError:
            return False
    
    def load_pet_frames(self, assets_dir: Path, pet_type: Optional[str]) -> bool:
        """Load pet frames for the specified pet type"""
        if pet_type:
            try:
                self.pet_frames = load_frames(assets_dir / "pets" / pet_type)
                return True
            except FileNotFoundError:
                self.pet_frames = None
                return False
        else:
            self.pet_frames = None
            return True
    
    def get_current_plant_frames(self, growth: float) -> FrameSet:
        """Get the appropriate plant frames based on growth stage"""
        if growth < 0:
            # Empty pot - return empty frameset that shows just the pot
            return FrameSet([], 0, 0)
        if growth >= self.cfg.plant_at:
            return self.plant_frames_plant or FrameSet([], 0, 0)
        if growth >= self.cfg.sprout_at:
            return self.plant_frames_sprout or FrameSet([], 0, 0)
        return self.plant_frames_seed or FrameSet([], 0, 0)
    
    def update_plant_animation(self, dt: float, growth: float, max_canvas_width: int, max_canvas_height: int) -> Optional[tk.PhotoImage]:
        """Update plant animation and return the composite image"""
        if not self.pot_frames:
            return None
        
        plant_frameset = self.get_current_plant_frames(growth)
        
        # Update animation
        self._anim_accum += dt
        frame_period = 1.0 / max(1, self.cfg.anim_fps)
        while self._anim_accum >= frame_period:
            self._anim_accum -= frame_period
            if plant_frameset.frames:  # Only animate if there are frames
                self._anim_index = (self._anim_index + 1) % len(plant_frameset.frames)
        
        # Create composite image
        self.current_image = self.pot_frames.composite_with(
            plant_frameset, 
            self._anim_index, 
            max_canvas_width, 
            max_canvas_height
        )
        
        return self.current_image
    
    def update_pet_animation(self, dt: float, max_canvas_width: int, max_canvas_height: int) -> Optional[tk.PhotoImage]:
        """Update pet animation and return the current pet frame"""
        if not self.pet_frames or not self.pet_frames.frames:
            return None
        
        # Animate pet
        self._pet_anim_accum += dt
        frame_period = 1.0 / max(1, self.cfg.anim_fps)
        while self._pet_anim_accum >= frame_period:
            self._pet_anim_accum -= frame_period
            self._pet_anim_index = (self._pet_anim_index + 1) % len(self.pet_frames.frames)
        
        # Convert PIL Image to PhotoImage
        pil_frame = self.pet_frames.frames[self._pet_anim_index]
        return ImageTk.PhotoImage(pil_frame)
    
    def get_pet_position(self, max_canvas_width: int, max_canvas_height: int) -> tuple[int, int]:
        """Get the position where pet should be displayed"""
        pet_x = max_canvas_width // 2
        pet_y = max_canvas_height - 20  # Near bottom
        return pet_x, pet_y
    
    def calculate_max_canvas_size(self) -> tuple[int, int]:
        """Calculate the maximum canvas size needed for current frames"""
        if not self.pot_frames:
            return 140, 100  # Default size
        
        plant_frames = [self.plant_frames_seed, self.plant_frames_sprout, self.plant_frames_plant]
        max_width = max(
            self.pot_frames.width,
            max((f.width for f in plant_frames if f and f.frames), default=0),
            140
        )
        max_height = max(
            self.pot_frames.height,
            max((f.height for f in plant_frames if f and f.frames), default=0)
        )
        
        return max_width, max_height
    
    def reset_animation_index(self):
        """Reset animation index to 0"""
        self._anim_index = 0
        self._pet_anim_index = 0
        self._anim_accum = 0.0
        self._pet_anim_accum = 0.0
