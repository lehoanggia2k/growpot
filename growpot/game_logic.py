from __future__ import annotations

import math
import random
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

        # Track if water ever reached zero (simple quality system)
        if state.water <= 0.01 and not state.water_ever_depleted:
            state.water_ever_depleted = True
        
        # Calculate effective growth rate based on plant and pot
        plant_stats = self.cfg.PLANT_STATS[state.plant_type]
        
        base_growth_rate = self.cfg.plant_at / plant_stats.growth_time_sec  # e.g., 3.0 / 10.0 = 0.3
        pot_multiplier = 1 + pot_stats.growth_time_reduction_percent  # e.g., 1.1 for 10% reduction
        effective_growth_rate = base_growth_rate * pot_multiplier
        
        water_factor = 1.0 - math.exp(-state.water)
        growth_rate = effective_growth_rate + water_factor * self.cfg.water_boost_growth_per_sec
        prev_growth = state.growth
        state.growth += growth_rate * dt

        # Check for bug generation (only if no bug is currently active)
        if not state.bug_active and prev_growth < self.cfg.bug_growth_end and state.growth >= self.cfg.bug_growth_start:
            # Check if growth crossed into bug spawn range
            growth_in_range = min(state.growth, self.cfg.bug_growth_end) - max(prev_growth, self.cfg.bug_growth_start)
            if growth_in_range > 0:
                # Calculate spawn probability based on growth traversed in spawn range
                spawn_chance = self.cfg.bug_appearance_chance * (growth_in_range / (self.cfg.bug_growth_end - self.cfg.bug_growth_start))
                if random.random() < spawn_chance:
                    state.bug_active = True
                    state.bug_appearance_time = now_ts()
    
    def can_harvest(self, state: GameState) -> bool:
        """Check if plant is ready for harvest"""
        return state.growth >= self.cfg.plant_at
    
    def harvest_plant(self, state: GameState) -> tuple[int, str]:
        """Harvest the plant and return the yield amount and quality"""
        if state.growth < self.cfg.plant_at:
            return 0, "normal"  # Not ready to harvest

        # Calculate base yield
        plant_stats = self.cfg.PLANT_STATS[state.plant_type]
        base_yield = plant_stats.yield_amount

        # Determine quality based on water and harvest timing
        quality = self._calculate_harvest_quality(state, plant_stats)

        # Apply quality modifiers (simple system)
        if quality == "poor":
            # Poor quality: 50% reduction for ever running out of water
            effective_yield = max(1, int(base_yield * 0.5))
        elif quality == "normal":
            # Normal quality: standard yield
            effective_yield = base_yield
        elif quality == "excellent":
            # Excellent quality: 25% bonus
            effective_yield = int(base_yield * 1.25)

        # Handle bug penalty: reduce quality by 1 level if bug wasn't caught
        if state.bug_active:
            quality = self._apply_bug_penalty(quality)
            state.bug_active = False  # Bug is gone after harvest
            state.bug_appearance_time = 0.0

        # Harvest: make pot empty, add to inventory
        state.growth = -1.0  # Empty pot
        state.growth_water_deficit = 0.0  # Reset deficit
        state.water_ever_depleted = False  # Reset depletion flag
        state.last_harvest_ts = now_ts()

        return effective_yield, quality
    
    def water_plant(self, state: GameState):
        """Add water to the plant"""
        state.water += self.cfg.water_per_click
    
    def reset_plant(self, state: GameState):
        """Reset the plant to initial state"""
        state.growth = 0.0
        state.water = 0.0
        state.growth_water_deficit = 0.0
        state.water_ever_depleted = False  # Reset depletion flag
        # Reset bug state
        state.bug_active = False
        state.bug_appearance_time = 0.0
    
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
        state.water_ever_depleted = False  # Reset depletion flag
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
        if state.growth >= 0:
            return False  # Cannot change pot when plant is growing

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

    def _calculate_harvest_quality(self, state: GameState, plant_stats) -> str:
        """Calculate harvest quality based on water and timing"""
        # Check if water ever depleted (simple system: never ran out of water)
        water_sufficient = not state.water_ever_depleted

        # Check harvest timing for excellent quality
        # Excellent: harvest within 20% growth time after ripening
        time_since_ripening = now_ts() - state.last_harvest_ts if state.last_harvest_ts > 0 else 0
        max_bonus_time = plant_stats.growth_time_sec * self.cfg.bug_harvest_bonus_time_percent
        timely_harvest = time_since_ripening <= max_bonus_time

        if water_sufficient and timely_harvest:
            return "excellent"
        elif water_sufficient:
            return "normal"
        else:
            return "poor"

    def _apply_bug_penalty(self, quality: str) -> str:
        """Apply bug penalty by reducing quality by one level"""
        if quality == "excellent":
            return "normal"
        elif quality == "normal":
            return "poor"
        else:
            return "poor"  # Already poor, stays poor

    def catch_bug(self, state: GameState) -> bool:
        """Attempt to catch the active bug"""
        if not state.bug_active or state.net_quantity <= 0:
            return False

        # Consume one net
        state.net_quantity -= 1

        # Add bug to inventory
        if "bug" not in state.inventory:
            state.inventory["bug"] = 0
        state.inventory["bug"] += 1

        # Remove bug
        state.bug_active = False
        state.bug_appearance_time = 0.0

        return True

    def can_catch_bug(self, state: GameState) -> bool:
        """Check if bug can be caught"""
        return state.bug_active and state.net_quantity > 0
