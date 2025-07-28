from __future__ import annotations
import os


class terrain_type:
    """
    Construct to represent a terrain type, like cold desert
        Note that terrain_manager handles the actual classification/range dict logic
    """

    def __init__(self, key: str):
        """
        Description:
            Initializes this object
        Input:
            string key: The key for this terrain type, like 'cold_desert'
                Used in terrain_manager's terrain_type_dict
        """
        self.key: str = key
        self.name = key.replace("_", " ")
        self.build_cost_multiplier: int = 1
        self.movement_cost: int = 1
        current_variant = 0
        while os.path.exists(f"graphics/terrains/{self.key}_{current_variant}.png"):
            current_variant += 1
        current_variant -= 1  # back up from index that didn't work
        self.num_variants = (
            current_variant + 1
        )  # number of variants, variants in format 'mountains_0', 'mountains_1', etc.
