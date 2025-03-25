# Contains functionality for unit type templates, such as workers, engineers, spaceships, etc.

import random
from typing import Dict, List
from modules.util import market_utility, text_utility, utility, actor_utility
from modules.constructs import minister_types, building_types
from modules.constants import constants, status, flags


class unit_type:
    """
    Template for a conceptual type of unit with standard images, permissions, etc., not including actual instances of the unit
    """

    def __init__(self, from_save: bool, input_dict: Dict) -> None:
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'key': string value - Constant uniquely identifying this type of worker across the program
                'permissions': boolean dictionary value - Dictionary of this unit type's default permissions, with True/False permissions
                'can_recruit': boolean value - Whether this unit type can be recruited
                    'recruitment_verb': string value - Verb to use when recruiting this unit, default of 'recruit'
                    'recruitment_cost': int value - Cost of recruiting this unit, default of 0.0
                    'description': string list value - Description text to display when recruiting this unit
                'inventory_capacity': int value - Maximum number of items this unit can carry, default of 0
                'controlling_minister_type': minister_type value - Minister type that controls this unit type
                'number': int value - Number of entities referenced by this unit's name, used in plural declension
                'name': string value - Default name of this unit type
                'movement_points': int value - Maximum number of movement points this unit starts with, default of 4
                'required_infrastructure': building_type value - Building type required for this unit to move (like railroad), default of None
        Output:
            None
        """
        self.save_changes: bool = input_dict.get("save_changes", False)
        self.key: str = input_dict["key"]
        if (
            from_save and self.save_changes
        ):  # If from save, rather than creating full unit type template, just edit existing one
            copy_to: unit_type = status.unit_types[self.key]
            copy_to.recruitment_cost = input_dict["recruitment_cost"]
        else:
            self.permissions: Dict[str, bool] = input_dict.get("permissions", [])
            self.can_recruit: bool = input_dict["can_recruit"]

            if self.can_recruit:
                self.recruitment_verb: str = input_dict.get(
                    "recruitment_verb", "recruit"
                )
                self.recruitment_cost: int = input_dict["recruitment_cost"]
                self.initial_recruitment_cost: int = self.recruitment_cost
                self.min_recruitment_cost: int = min(2, self.recruitment_cost)
                self.description: List[str] = input_dict.get("description", [])
                status.recruitment_types.append(self)

            self.inventory_capacity: int = input_dict.get("inventory_capacity", 0)
            self.controlling_minister_type: minister_types.minister_type = input_dict[
                "controlling_minister_type"
            ]
            self.number: int = input_dict.get("number", 1)
            self.num_instances: int = 0
            self.image_id = f"mobs/{self.key}/default.png"
            self.name: str = input_dict.get("name", "default")
            self.movement_points: int = input_dict.get("movement_points", 4)
            self.required_infrastructure: building_types.building_type = input_dict.get(
                "required_infrastructure", None
            )
            self.item_upkeep: Dict[str, float] = input_dict.get("item_upkeep", {})
            self.missing_upkeep_penalties: Dict[str, float] = input_dict.get(
                "missing_upkeep_penalties", {}
            )

            status.unit_types[self.key] = self
        return

    def generate_center_recruitment_image(self, dummy_recruited_unit):
        """
        Description:
            Generates the image for the center of a recruitment button for this unit type
        Input:
            actor dummy_recruited_unit: Dummy actor of this type to use for generating the image
        Output
            image_id list: List of image IDs for the recruitment button center image
        """
        image_id = constants.character_manager.generate_unit_portrait(
            dummy_recruited_unit, metadata={"body_image": self.image_id}
        )
        for image in image_id:
            if (
                type(image) == dict
                and image.get("metadata", {}).get("portrait_section", "")
                != constants.FULL_BODY_PORTRAIT_SECTION
            ):
                image["x_offset"] = image.get("x_offset", 0) - 0.01
                image["y_offset"] = image.get("y_offset", 0) - 0.01
        return image_id

    def generate_framed_recruitment_image(self):
        """
        Description:
            Deterministically generates the image for a framed recruitment button for this unit type
        Input:
            None
        Output
            image_id list: List of image IDs for the recruitment button image
        """
        dummy_recruited_unit = constants.actor_creation_manager.create_dummy(
            {"unit_type": self}
        )
        for permission, value in self.permissions.items():
            dummy_recruited_unit.set_permission(permission, value)

        original_random_state = random.getstate()
        random.seed(
            self.key + "random #7"
        )  # Consistently generate the same random portrait for the same interface elements - modify concatenated text to try different versions

        image_id = self.generate_center_recruitment_image(dummy_recruited_unit)

        random.setstate(original_random_state)

        return actor_utility.generate_frame(
            image_id, frame="buttons/default_button_alt.png", size=0.9, y_offset=0.02
        )

    def get_list_description(self) -> List[str]:
        """
        Description:
            Gets the description of this unit type as a list of strings
        Input:
            None
        Output:
            string list: List of strings describing this unit type
        """
        return self.description

    def get_string_description(self) -> str:
        """
        Description:
            Gets the description of this unit type as a list of strings
        Input:
            None
        Output:
            string: /n /n separated string describing this unit type
        """
        return " /n /n".join(self.description) + " /n /n"

    def to_save_dict(self) -> Dict:
        """
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                'key': string value - Constant uniquely identifying this type of worker across the program
                'recruitment_cost': float value - Cost of recruiting this unit
        """
        return {
            "key": self.key,
            "recruitment_cost": self.recruitment_cost,
            "save_changes": self.save_changes,
        }

    def get_total_upkeep(self) -> float:
        """
        Description:
            Calculates and returns the total upkeep of this worker type's units
        Input:
            None
        Output:
            float: Returns the total upkeep of this worker type's units
        """
        return self.num_instances * self.upkeep

    def generate_input_dict(self) -> Dict:
        """
        Description:
            Generates an input dict to create a worker of this type
        Input:
            None
        Output:
            dictionary: Returns dictionary with standard entries for this worker type
        """
        input_dict = {
            "image": self.image_id,
            "name": self.name,
            "init_type": self.key,
            "unit_type": self,
        }
        return input_dict

    def on_recruit(self) -> None:
        """
        Description:
            Called when an instance of this unit is newly hired (not reconstructed from save)
        Input:
            None
        Output:
            None
        """
        return

    def on_remove(self) -> None:
        """
        Description:
            Called whenever an instance of this unit is removed, tracking how many instances remain
        Input:
            None
        Output:
            None
        """
        self.num_instances -= 1

    def reset(self) -> None:
        """
        Description:
            Resets this unit types value's when a new game is created, preventing any mutable values from carrying over
        Input:
            None
        Output:
            None
        """
        self.num_instances = 0
        if self.can_recruit:
            self.recruitment_cost = self.initial_recruitment_cost


class officer_type(unit_type):
    """
    Unit type template representing an officer, which can combine with workers to form a certain type of group
    """

    def link_group_type(self, group_type) -> None:
        """
        Description:
            Links this officer type to a group type, and vice versa. Must be used after initialization of both types, so not part of the constructor
        Input:
            group_type group_type: Type of group to link this officer type to
        Output:
            None
        """
        self.group_type: unit_type = group_type
        group_type.officer_type = self


class group_type(unit_type):
    """
    Unit type template representing a group, which is a combination of workers and a certain type of officer
    """

    def __init__(self, from_save: bool, input_dict: Dict) -> None:
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'key': string value - Constant uniquely identifying this type of worker across the program
                'permissions': boolean dictionary value - Dictionary of this unit type's default permissions, with True/False permissions
                'can_recruit': boolean value - Whether this unit type can be recruited
                    'recruitment_verb': string value - Verb to use when recruiting this unit, default of 'recruit'
                    'recruitment_cost': int value - Cost of recruiting this unit, default of 0.0
                    'description': string list value - Description text to display when recruiting this unit
                'inventory_capacity': int value - Maximum number of items this unit can carry, default of 0
                'controlling_minister_type': minister_type value - Minister type that controls this unit type
                'number': int value - Number of entities referenced by this unit's name, used in plural declension
                'name': string value - Default name of this unit type
        Output:
            None
        """
        super().__init__(from_save, input_dict)
        self.officer_type: officer_type = None


class vehicle_type(unit_type):
    """
    Unit type template representing a vehicle, which requires a crew to be operational
    """

    def __init__(self, from_save: bool, input_dict: Dict) -> None:
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'key': string value - Constant uniquely identifying this type of worker across the program
                'permissions': boolean dictionary value - Dictionary of this unit type's default permissions, with True/False permissions
                'can_recruit': boolean value - Whether this unit type can be recruited
                    'recruitment_verb': string value - Verb to use when recruiting this unit, default of 'recruit'
                    'recruitment_cost': int value - Cost of recruiting this unit, default of 0.0
                    'description': string list value - Description text to display when recruiting this unit
                'inventory_capacity': int value - Maximum number of items this unit can carry, default of 0
                'controlling_minister_type': minister_type value - Minister type that controls this unit type
                'number': int value - Number of entities referenced by this unit's name, used in plural declension
                'name': string value - Default name of this unit type
        Output:
            None
        """
        super().__init__(from_save, input_dict)
        self.uncrewed_image_id = f"mobs/{self.key}/uncrewed.png"
        self.moving_image_id = f"mobs/{self.key}/moving.png"

    def generate_input_dict(self) -> Dict:
        """
        Description:
            Generates an input dict to create a unit of this type
        Input:
            None
        Output:
            dictionary: Returns dictionary with standard entries for this unit type
        """
        input_dict = super().generate_input_dict()
        input_dict["image_dict"] = {
            "default": self.image_id,
            "uncrewed": self.uncrewed_image_id,
            "moving": self.moving_image_id,
        }
        input_dict["crew"] = None
        return input_dict

    def generate_center_recruitment_image(self, dummy_recruited_unit) -> List[Dict]:
        """
        Description:
            Generates the image for the center of a recruitment button for this unit type. Rather than generating a character image, a vehicle can just use a pre-set image
        Input:
            actor dummy_recruited_unit: Dummy actor of this type to use for generating the image
        Output
            image_id list: List of image IDs for the recruitment button center image
        """
        return self.uncrewed_image_id


class worker_type(unit_type):
    """
    Unit type template representing a worker, which has upkeep and can combine with officers to form a group
    """

    def __init__(self, from_save: bool, input_dict: Dict) -> None:
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'key': string value - Constant uniquely identifying this type of worker across the program
                'name': string value - Name of the corresponding unit
                'upkeep': float value - Cost of this unit each turn, default of 0.0
                'recruitment_cost': float value - Cost of recruiting this unit, default of 0.0
                'fired_description': string list value - Description text to confirm firing of this unit
                'upkeep_variance': bool value - Whether this worker type's upkeep can randomly fluctuate each turn
                'init_type': string value - Actor creation init type to use for this unit, default of 'workers'
        Output:
            None
        """
        super().__init__(from_save, input_dict)
        self.save_changes: bool = input_dict.get("save_changes", False)
        if (
            from_save and self.save_changes
        ):  # If from save, rather than creating full worker type template, just edit existing one
            copy_to: worker_type = status.worker_types[self.key]
            copy_to.upkeep = input_dict["upkeep"]
        else:
            status.worker_types[self.key] = self

            self.upkeep: float = input_dict.get("upkeep", 0.0)
            self.initial_upkeep: float = self.upkeep
            self.min_upkeep: float = min(0.5, self.initial_upkeep)
            self.fired_description: List[str] = input_dict.get("fired_description", [])
            self.upkeep_variance: bool = input_dict.get("upkeep_variance", False)

    def generate_center_recruitment_image(self, dummy_recruited_unit):
        """
        Description:
            Generates the image for the center of a recruitment button for this unit type
        Input:
            actor dummy_recruited_unit: Dummy actor of this type to use for generating the image
        Output
            image_id list: List of image IDs for the recruitment button center image
        """
        worker_images = random.choices(
            actor_utility.get_image_variants(self.image_id), k=2
        )
        image_id = utility.combine(
            actor_utility.generate_unit_component_portrait(
                constants.character_manager.generate_unit_portrait(
                    dummy_recruited_unit,
                    metadata={"body_image": worker_images[0]},
                ),
                "left",
            ),
            actor_utility.generate_unit_component_portrait(
                constants.character_manager.generate_unit_portrait(
                    dummy_recruited_unit,
                    metadata={"body_image": worker_images[1]},
                ),
                "right",
            ),
        )
        for image in image_id:
            if (
                type(image) == dict
                and image.get("metadata", {}).get("portrait_section", "")
                != constants.FULL_BODY_PORTRAIT_SECTION
            ):
                image["y_offset"] = image.get("y_offset", 0) - 0.02
        return image_id

    def to_save_dict(self) -> Dict:
        """
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                'key': string value - Constant uniquely identifying this type of worker across the program
                'recruitment_cost': float value - Cost of recruiting this unit
                'upkeep': float value - Cost of this unit each turn
        """
        save_dict = super().to_save_dict()
        save_dict["upkeep"] = self.upkeep
        return save_dict

    def reset(self) -> None:
        """
        Description:
            Resets this unit types value's when a new game is created, preventing any mutable values from carrying over
        Input:
            None
        Output:
            None
        """
        super().reset()
        self.upkeep = self.initial_upkeep

    def get_total_upkeep(self) -> float:
        """
        Description:
            Calculates and returns the total upkeep of this worker type's units
        Input:
            None
        Output:
            float: Returns the total upkeep of this worker type's units
        """
        return self.num_instances * self.upkeep

    def generate_input_dict(self) -> Dict:
        """
        Description:
            Generates an input dict to create a worker of this type
        Input:
            None
        Output:
            dictionary: Returns dictionary with standard entries for this worker type
        """
        input_dict = super().generate_input_dict()
        input_dict["worker_type"] = self
        return input_dict

    def on_recruit(self) -> None:
        """
        Description:
            Makes any updates required when worker first recruited (not on load)
        Input:
            None
        Output:
            None
        """
        super().on_recruit()
        if self.upkeep > 0:
            market_utility.attempt_worker_upkeep_change("increase", self)

    def on_remove(self):
        """
        Description:
            Called whenever an instance of this unit is removed, tracking how many instances remain
        Input:
            None
        Output:
            None
        """
        super().on_remove()
        constants.money_label.check_for_updates()

    def on_fire(self, wander=False):
        """
        Description:
            Makes any updates required when worker fired
        Input:
            boolean wander=False: Whether this worker will wander after being fired
        Output:
            None
        """
        if self.upkeep > 0:
            market_utility.attempt_worker_upkeep_change("decrease", self)

        if self.key in [constants.COLONISTS]:
            current_public_opinion = constants.public_opinion
            constants.public_opinion_tracker.change(-1)
            resulting_public_opinion = constants.public_opinion
            if not current_public_opinion == resulting_public_opinion:
                text_utility.print_to_screen(
                    f"Firing {self.name} reflected poorly on your company and reduced your public opinion from {current_public_opinion} to {resulting_public_opinion}."
                )
