# Contains functionality for terrain feature types - points of interest at a location

import random
from typing import Dict, List, Tuple
from modules.constants import constants, status, flags


class terrain_feature_type:
    """
    Equipment template that tracks the effects, descriptions, and requirements of a particular equipment type
        Equipment inclues any item that provides an optional enhancement to a unit's capabilities
    """

    def __init__(self, input_dict: Dict) -> None:
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'equipment_type': string value - Name of this equipment type
                'description': string list value - Description tooltip for this equipment type
                'effects': string list value - List of types of actions this equipment provides a positive modifier on
                'price': float value - Purchase price of this equipment type
                'requirements': string dictionary value - Optional series of restrictions on terrain feature placement, varying by feature type
                "tracking_type": string value - Optional string equal to UNIQUE_FEATURE_TRACKING or LIST_FEATURE_TRACKING, indicating to track each instance of this feature in a status variable
                "visible": boolean value - Optional boolean indicating whether to display this feature - True by default
                    Hidden features like equator can still be placed but are only for internal calculations
        Output:
            None
        """
        self.terrain_feature_type = input_dict["terrain_feature_type"]
        self.description: List[str] = input_dict.get("description", [])
        self.tracking_type: str = input_dict.get("tracking_type", None)
        self.display_type: str = input_dict.get("display_type", "icon")
        self.visible: bool = input_dict.get("visible", True)
        self.image_id = input_dict.get(
            "image_id",
            {
                "image_id": f"terrains/features/{self.terrain_feature_type}.png",
                "level": -1,
            },
        )
        self.requirements: Dict[str, any] = input_dict.get("requirements", {})
        self.frequency: Tuple[int, int] = input_dict.get("frequency", None)
        status.terrain_feature_types[self.terrain_feature_type] = self

    def clear_tracking(self) -> None:
        """
        Clears all status tracking of this feature type
        """
        if self.tracking_type == constants.UNIQUE_FEATURE_TRACKING:
            setattr(status, self.terrain_feature_type.replace(" ", "_"), None)
        elif self.tracking_type == constants.LIST_FEATURE_TRACKING:
            setattr(status, self.terrain_feature_type.replace(" ", "_") + "_list", [])

    def allow_place(self, location) -> bool:
        """
        Description:
            Calculates and returns whether to place one of this particular feature in the inputted location during map generation, based on the feature's frequency and
                requirements
        Input:
            location location: Location to place feature in
        Output:
            boolean: Returns whether to place one of this particular featuer in the inputted location
        """
        if self.frequency:
            if (
                random.randrange(1, self.frequency[1] + 1) <= self.frequency[0]
            ):  # For (1, 10), appear if random.randrange(1, 11) <= 1
                for requirement in self.requirements:
                    if requirement == "terrain":
                        if self.requirements[requirement] != location.terrain:
                            return False
                    elif requirement == "min_y":
                        if location.y < self.requirements[requirement]:
                            return False
                    elif requirement == "resource":
                        if location.resource != self.requirements[requirement]:
                            return False
                return True
        return False
