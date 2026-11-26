# Contains functionality for building type templates

from __future__ import annotations
import math
from typing import Dict, List, Tuple, Any
from modules.constants import constants, status, flags, dataclasses


class building_type:
    """
    Building type template that tracks the features of a particular building type
    """

    def __init__(self, input_dict: Dict) -> None:
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'key': str value - Constant key for this building type
                'name': str value - Name of this building type
                'description': List[str] value - Description of this building type
                'can_construct': bool value - Whether this building type can be constructed, or is automatically generated in certain circumstances
                'can_damage': bool value - Whether this building type can be damaged/can be repaired
                'upgrade_fields': Dict[Dict[str, Any]] value - Fields for upgrading this building type
                    key: Constant key for this upgrade type
                    'cost' - int value - Base cost for this upgrade type
                    'max' - int value - Maximum level for this upgrade type, default of None (unlimited)
                    'name' - str value - Name of this upgrade type
                    'keybind' - pygame.key value - Keybind to attempt this upgrade type
                'warehouse_level': int value - Level of warehouse automatically created with this building
                'display_coordinates': Tuple[int, int] value - Coordinates to display this building type at (within 3 x 3 matrix in location). Deprecated
                'link_to_adjacent': bool value - Whether this building type can be linked to adjacent buildings, like roads
                'image_id': List[Any] value - List of image ids for this building type
                'button_image_id_list': List[Any] value - List of image ids for this building type's construction button
                'attached_settlement': bool value - Whether this building type automatically creates a settlement, if none already exists
                'cost': int value - Base cost for this building type
                'build_requirements': List[str] value - List of permissions to build this building type
                'build_keybind': pygame.key value - Keybind to attempt constructing this building type
                'grammar': Dict[str, str] value - Grammatical keywords used in this building type's construction descriptions
        Output:
            None
        """
        self.key: str = input_dict["key"]
        self.name: str = input_dict["name"]
        self.description: List[str] = input_dict.get("description", [])
        self.can_construct: bool = input_dict["can_construct"]
        self.can_damage: bool = input_dict["can_damage"]
        self.upgrade_fields: Dict[Dict[str, Any]] = input_dict.get("upgrade_fields", {})
        self.warehouse_level: int = input_dict.get("warehouse_level", 0)
        assert (
            "display_coordinates" not in input_dict
        )  # Non-origin building coordinates are no longer applicable with the zone building system
        # self.display_coordinates: Tuple[int, int] = input_dict.get(
        #    "display_coordinates", (0, 0)
        # )
        self.link_to_adjacent: bool = input_dict.get("link_to_adjacent", False)
        # self.image_id_list: List[Any] = input_dict.get(
        #    "image_id", [{"image_id": f"items/equipment/buildings/{self.key}.png"}]
        # )
        self.background_image_id: str = (
            f"items/equipment/buildings/{self.key}_background.png"
        )
        self.icon_image_id: str = f"items/equipment/buildings/{self.key}_icon.png"
        self.button_image_id_list: List[Any] = input_dict.get(
            "button_image_id_list",
            [{"image_id": f"items/equipment/buildings/buttons/{self.key}.png"}],
        )
        self.attached_settlement: bool = input_dict.get("attached_settlement", False)
        self.build_requirements = input_dict.get(
            "build_requirements",
            [constants.GROUP_PERMISSION, constants.CONSTRUCTION_PERMISSION],
        )
        self.build_keybind: int = input_dict.get("build_keybind", None)
        self.grammar: Dict[str, str] = input_dict.get(
            "grammar",
            {
                "verb": "construct",
                "preterit_verb": "constructed",
                "noun": "construction",
            },
        )
        self.cost_per_attempt: dataclasses.material_cost = input_dict[
            "cost_per_attempt"
        ]
        self.required_successes: int = input_dict["required_successes"]

        status.building_types[self.key] = self

    def get_string_description(self) -> str:
        """
        Description:
            Converts and returns this building type's description as a string
        Input:
            None
        Output:
            str: The string version of this building type's description
        """
        return " /n /n".join(self.description) + " /n /n"

    def get_image_id_list(self, build_progress: float = None) -> List[Any]:
        build_progress = 1.0 if build_progress is None else round(build_progress, 2)
        if build_progress >= 1.0:
            return [
                {"image_id": self.background_image_id},
                {"image_id": self.icon_image_id},
            ]
        else:
            assert build_progress >= 0 and build_progress < 1
            incomplete_opacity = 50
            image_id = [
                {
                    "image_id": f"items/equipment/buildings/plan_fill.png",
                    "clip_to_image": self.background_image_id,
                    "opacity": incomplete_opacity,
                },  # Semi-transparent, incomplete, upper component of background
                {
                    "image_id": self.background_image_id,
                    "clip_to_vertical_range": (
                        100 - math.floor(build_progress * 100),
                        100,
                    ),
                },  # Opaque, completed, lower component of background
                {
                    "image_id": self.icon_image_id,
                    "clip_to_vertical_range": (
                        0,
                        100 - math.floor(build_progress * 100),
                    ),
                    "opacity": incomplete_opacity,
                },  # Semi-transparent, incomplete, upper component of icon
                {
                    "image_id": self.icon_image_id,
                    "clip_to_vertical_range": (
                        100 - math.floor(build_progress * 100),
                        100,
                    ),
                },  # Opaque, completed, lower component of icon
            ]
            return image_id
