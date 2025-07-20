from __future__ import annotations
import os

class terrain_type:
    def __init__(self, key: str, range_dict):
        self.key: str = key
        self.name = key.replace("_", " ")
        self.range_dict = range_dict
        self.build_cost_multiplier: int = 1
        self.movement_cost: int = 1
        current_variant = 0
        while os.path.exists(f"graphics/terrains/{self.key}_{current_variant}.png"):
            current_variant += 1
        current_variant -= 1  # back up from index that didn't work
        self.num_variants = (
            current_variant + 1
        )  # number of variants, variants in format 'mountains_0', 'mountains_1', etc.
