# Contains functionality for building type templates

from typing import Dict, List, Tuple, Any
from modules.constants import constants, status, flags


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
                'display_coordinates': Tuple[int, int] value - Coordinates to display this building type at (within 3 x 3 matrix in location)
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
        self.display_coordinates: Tuple[int, int] = input_dict.get(
            "display_coordinates", (0, 0)
        )
        self.link_to_adjacent: bool = input_dict.get("link_to_adjacent", False)
        self.image_id_list: List[Any] = input_dict.get(
            "image_id", [{"image_id": f"buildings/{self.key}.png"}]
        )
        self.button_image_id_list: List[Any] = input_dict.get(
            "button_image_id_list", [{"image_id": f"buildings/buttons/{self.key}.png"}]
        )
        self.attached_settlement: bool = input_dict.get("attached_settlement", False)
        self.cost: int = input_dict.get("cost", 0)
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
