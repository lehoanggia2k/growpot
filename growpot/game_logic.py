from __future__ import annotations

import math
from growpot.state import GameState, now_ts
from growpot.game_config import GameConfig


class GameEngine:
    """Handles core game simulation and logic"""
    
    def __init__(self, config: GameConfig):
        self.cfg = config
        self._last_harvest_state = "disabled"
    
    def advance_simulation(self, state: GameState, dt: float):
        """Advance game simulation by dt seconds"""
        # Don't simulate if pot is empty
        if state.growth < 0:
            return
        
        # Get pot stats for water decay reduction
        pot_stats = self.cfg.POT_STATS[state.pot_type]
        effective_water_decay = self.cfg.water_decay_per_sec * (1.0 - pot_stats.water_decay_reduction_percent)
        
        # Water decays
        if state.water > 0:
            state.water = max(0.0, state.water - effective_water_decay * dt)
        
        # Track water deficit for yield reduction
        water_threshold = 0.5
        if state.water < water_threshold:
            deficit = (water_threshold - state.water) * dt
            state.growth_water_deficit += deficit
        
        # Calculate effective growth rate based on plant and pot
        plant_stats = self.cfg.PLANT_STATS[state.plant_type]
        
        base_growth_rate = self.cfg.plant_at / plant_stats.growth_time_sec  # e.g., 3.0 / 10.0 = 0.3
        pot_multiplier = 1 + pot_stats.growth_time_reduction_percent  # e.g., 1.1 for 10% reduction
        effective_growth_rate = base_growth_rate * pot_multiplier
        
        water_factor = 1.0 - math.exp(-state.water)
        growth_rate = effective_growth_rate + water_factor * self.cfg.water_boost_growth_per_sec
        state.growth += growth_rate * dt
    
    def can_harvest(self, state: GameState) -> bool:
        """Check if plant is ready for harvest"""
        return state.growth >= self.cfg.plant_at
    
    def harvest_plant(self, state: GameState) -> int:
        """Harvest the plant and return the yield amount"""
        if state.growth < self.cfg.plant_at:
            return 0  # Not ready to harvest
        
        # Calculate yield reduction based on water deficit
        plant_stats = self.cfg.PLANT_STATS[state.plant_type]
        base_yield = plant_stats.yield_amount
        
        # Total possible deficit over full growth time (rough estimate)
        full_growth_time = plant_stats.growth_time_sec
        max_deficit = 0.5 * full_growth_time  # Assuming threshold 0.5
        
        # Yield reduction: up to 50% reduction if deficit >= max_deficit
        deficit_ratio = min(1.0, state.growth_water_deficit / max_deficit)
        yield_reduction = 0.5 * deficit_ratio  # Max 50% reduction
        effective_yield = max(1, int(base_yield * (1.0 - yield_reduction)))
        
        # Harvest: make pot empty, add to inventory
        state.growth = -1.0  # Empty pot
        state.growth_water_deficit = 0.0  # Reset deficit
        state.last_harvest_ts = now_ts()
        
        return effective_yield
    
    def water_plant(self, state: GameState):
        """Add water to the plant"""
        state.water += self.cfg.water_per_click
    
    def reset_plant(self, state: GameState):
        """Reset the plant to initial state"""
        state.growth = 0.0
        state.water = 0.0
        state.growth_water_deficit = 0.0
    
    def can_plant_seed(self, state: GameState) -> bool:
        """Check if a seed can be planted"""
        return state.growth < 0  # Pot must be empty
    
    def plant_seed(self, state: GameState, plant_type: str):
        """Plant a seed of the specified type"""
        if not self.can_plant_seed(state):
            return False
        
        state.plant_type = plant_type
        state.growth = 0.0
        state.water = 0.0
        state.growth_water_deficit = 0.0
        return True
    
    def check_pet_auto_watering(self, state: GameState):
        """Check and perform pet auto-watering if needed"""
        # Don't auto-water if no active pet or pot is empty
        if not state.active_pet or state.growth < 0:
            return
        
        pet_stats = self.cfg.PET_STATS[state.active_pet]
        
        # Check if pet is still working (not hungry)
        time_since_fed = now_ts() - state.pet_last_fed_ts
        if time_since_fed >= pet_stats.work_duration_sec:
            return  # Pet is hungry, won't work
        
        # Check if water level is below threshold (convert percentage to actual water level)
        max_water = 5.0  # Same as in progress bars
        water_threshold = pet_stats.auto_water_threshold * max_water
        
        if state.water <= water_threshold:
            # Auto-water the plant
            state.water += pet_stats.auto_water_amount
            state.pet_last_worked_ts = now_ts()
    
    def get_harvest_menu_state_changed(self, state: GameState) -> bool:
        """Check if harvest menu state needs to be updated"""
        harvest_state = "normal" if self.can_harvest(state) else "disabled"
        changed = harvest_state != self._last_harvest_state
        if changed:
            self._last_harvest_state = harvest_state
        return changed
    
    def get_current_harvest_menu_state(self, state: GameState) -> str:
        """Get current harvest menu state ('normal' or 'disabled')"""
        return "normal" if self.can_harvest(state) else "disabled"
    
    def apply_offline_progress(self, state: GameState):
        """Apply offline progress when app starts"""
        now = now_ts()
        dt = max(0.0, now - float(state.last_update_ts or now))
        self.advance_simulation(state, dt)
        state.last_update_ts = now
    
    def change_pot(self, state: GameState, pot_type: str) -> bool:
        """Change the pot type"""
        if pot_type == state.pot_type:
            return False  # No change
        if pot_type not in state.unlocked_pots:
            return False  # Pot not unlocked
        
        state.pot_type = pot_type
        return True
    
    def unlock_pot(self, state: GameState, pot_type: str, cost: int) -> bool:
        """Unlock a new pot type"""
        # Check if already unlocked
        if pot_type in state.unlocked_pots:
            return False
        
        # Check if player has enough money
        if state.money < cost:
            return False
        
        # Deduct cost and unlock pot
        state.money -= cost
        state.unlocked_pots.add(pot_type)
        return True
