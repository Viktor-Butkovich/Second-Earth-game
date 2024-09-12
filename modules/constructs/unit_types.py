# Contains functionality for worker type templates, such as European, religious workers

import random
from typing import Dict, List
import modules.constants.status as status
import modules.constants.constants as constants
import modules.util.market_utility as market_utility
import modules.util.text_utility as text_utility
import modules.util.utility as utility
import modules.util.actor_utility as actor_utility
import modules.constructs.minister_types as minister_types


class unit_type:
    def __init__(self, from_save: bool, input_dict: Dict) -> None:
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
                self.initial_recruitment_cost: float = self.recruitment_cost
                self.min_recruitment_cost: float = min(2.0, self.recruitment_cost)
                self.description: List[str] = input_dict.get("description", [])

            self.inventory_capacity: int = input_dict.get("inventory_capacity", 0)
            self.controlling_minister_type: minister_types.minister_type = input_dict[
                "controlling_minister_type"
            ]
            self.number: int = input_dict.get("number", 1)
            self.num_instances: int = 0
            self.image_id = f"mobs/{self.key}/default.png"
            self.name: str = input_dict.get("name", "default")

            status.unit_types[self.key] = self
        return

    def generate_recruitment_permissions(self):
        return self.permissions

    def generate_center_recruitment_image(self, dummy_recruited_unit):
        image_id = constants.character_manager.generate_unit_portrait(
            dummy_recruited_unit, metadata={"body_image": self.mob_image_id}
        )
        for image in image_id:
            if (
                type(image) == dict
                and image.get("metadata", {}).get("portrait_section", "") != "full_body"
            ):
                image["x_offset"] = image.get("x_offset", 0) - 0.01
                image["y_offset"] = image.get("y_offset", 0) - 0.01
        return image_id

    def generate_framed_recruitment_image(self):
        dummy_recruited_unit = constants.actor_creation_manager.create_dummy(
            {"unit_type": self}
        )
        for permission, value in self.generate_recruitment_permissions().items():
            dummy_recruited_unit.set_permission(permission, value)

        original_random_state = random.getstate()
        random.seed(
            self.key
        )  # Consistently generate the same random portrait for the same interface elements

        image_id = self.generate_center_recruitment_image(dummy_recruited_unit)

        random.setstate(original_random_state)

        return actor_utility.generate_frame(
            image_id, frame="buttons/default_button_alt.png", size=0.9, y_offset=0.02
        )

    def get_list_description(self) -> List[str]:
        return self.description

    def get_string_description(self) -> str:
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
        return self.number * self.upkeep

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

    def on_remove(self):
        self.num_instances -= 1


class officer_type(unit_type):
    def link_group_type(self, group_type):
        self.group_type: unit_type = group_type
        group_type.officer_type = self


class group_type(unit_type):
    def __init__(self, from_save: bool, input_dict: Dict) -> None:
        super().__init__(from_save, input_dict)
        self.officer_type: officer_type = None


class vehicle_type(unit_type):
    def __init__(self, from_save: bool, input_dict: Dict) -> None:
        super().__init__(from_save, input_dict)
        self.uncrewed_image_id = input_dict.get("uncrewed_image_id", self.image_id)

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
        input_dict["image_dict"] = {
            "default": self.image_id,
            "uncrewed": self.uncrewed_image_id,
        }
        input_dict["crew"] = None
        return input_dict

    def generate_recruitment_permissions(self):
        permissions = super().generate_recruitment_permissions()
        del permissions[constants.INACTIVE_VEHICLE_PERMISSION]
        permissions[constants.ACTIVE_VEHICLE_PERMISSION] = True
        return permissions

    def generate_center_recruitment_image(self, dummy_recruited_unit):
        return self.image_id


class worker_type(unit_type):
    """
    Worker template that tracks the current number, upkeep, and recruitment cost of a particular worker type
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
        image_id = utility.combine(
            actor_utility.generate_unit_component_portrait(
                constants.character_manager.generate_unit_portrait(
                    dummy_recruited_unit,
                    metadata={"body_image": self.recruitment_type.image_id},
                ),
                "left",
            ),
            actor_utility.generate_unit_component_portrait(
                constants.character_manager.generate_unit_portrait(
                    dummy_recruited_unit,
                    metadata={"body_image": self.recruitment_type.image_id},
                ),
                "right",
            ),
        )
        for image in image_id:
            if (
                type(image) == dict
                and image.get("metadata", {}).get("portrait_section", "") != "full_body"
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
            Resets this worker type's values when a new game is created
        Input:
            None
        Output:
            None
        """
        self.number = 0
        self.upkeep = self.initial_upkeep
        if self.can_recruit:
            self.recruitment_cost = self.initial_recruitment_cost

    def get_total_upkeep(self) -> float:
        """
        Description:
            Calculates and returns the total upkeep of this worker type's units
        Input:
            None
        Output:
            float: Returns the total upkeep of this worker type's units
        """
        return self.number * self.upkeep

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
        if self.key != constants.CHURCH_VOLUNTEERS:
            market_utility.attempt_worker_upkeep_change("increase", self)

    def on_remove(self):
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
        if self.key != constants.CHURCH_VOLUNTEERS:
            market_utility.attempt_worker_upkeep_change("decrease", self)

        if self.key in [constants.CHURCH_VOLUNTEERS, constants.EUROPEAN_WORKERS]:
            current_public_opinion = constants.public_opinion
            constants.public_opinion_tracker.change(-1)
            resulting_public_opinion = constants.public_opinion
            if not current_public_opinion == resulting_public_opinion:
                text_utility.print_to_screen(
                    f"Firing {self.name} reflected poorly on your company and reduced your public opinion from {current_public_opinion} to {resulting_public_opinion}."
                )
