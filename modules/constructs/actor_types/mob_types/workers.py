# Contains functionality for worker units

from __future__ import annotations
import random
from typing import Dict
from modules.constructs.actor_types.mob_types.pmobs import pmob
from modules.util import actor_utility, text_utility
from modules.constructs import unit_types
from modules.constants import constants, status, flags


class worker(pmob):
    """
    pmob that is required for officers to form groups
    """

    def __init__(self, from_save, input_dict, original_constructor: bool = True):
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'grids': grid list value - grids in which this mob's images can appear
                'image': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'name': string value - Required if from save, this mob's name
                'modes': string list value - Game modes during which this mob's images can appear
                'end_turn_destination_coordinates': int tuple value - None if no saved destination, destination coordinates if saved destination
                'end_turn_destination_world_index': int value - Index of the world of the end turn destination, if any
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'max_movement_points': int value - Required if from save, maximum number of movement points this mob can have
                'worker_type': worker_type value - Type of worker this is, like 'Colonist'. Each type of worker has a separate upkeep, labor pool, and abilities
        Output:
            None
        """
        self.worker_type: unit_types.worker_type = input_dict.get(
            "worker_type", status.worker_types.get(input_dict.get("init_type"))
        )  # Colonist, etc. worker_type object
        self.group = None
        super().__init__(from_save, input_dict, original_constructor=False)

        if not from_save:
            self.second_image_variant = random.randrange(0, len(self.image_variants))
        constants.MoneyLabel.check_for_updates()
        self.finish_init(original_constructor, from_save, input_dict)

    def finish_init(
        self, original_constructor: bool, from_save: bool, input_dict: Dict[str, any]
    ):
        """
        Description:
            Finishes initialization of this actor, called after the original is finished
        Input:
            boolean original_constructor: Whether this is the original constructor call for this object
        Output:
            None
        """
        if original_constructor:
            if not from_save:
                self.image_dict[constants.IMAGE_ID_LIST_LEFT_PORTRAIT] = (
                    constants.CharacterManager.generate_unit_portrait(
                        self,
                        metadata={
                            "body_image": self.image_dict[
                                constants.IMAGE_ID_LIST_DEFAULT
                            ][0]["image_id"]
                        },
                    )
                )
                self.image_dict[constants.IMAGE_ID_LIST_RIGHT_PORTRAIT] = (
                    constants.CharacterManager.generate_unit_portrait(
                        self,
                        metadata={
                            "body_image": self.image_variants[self.second_image_variant]
                        },
                    )
                )
            super().finish_init(
                original_constructor, from_save, input_dict, create_portrait=False
            )

    def replace(self, attached_group=None):
        """
        Replaces this unit for a new version of itself when it dies from attrition, removing all experience and name modifications
        """
        super().replace()
        if attached_group:
            recipient = attached_group
        else:
            recipient = self
        recipient_location = recipient.location
        self.worker_type.on_recruit()
        text_utility.print_to_screen(
            f"Replacement {self.worker_type.name} have been automatically hired for the {recipient.name} at ({recipient_location.x}, {recipient_location.y})."
        )

    def fire(self, wander=True):
        """
        Removes this object from relevant lists and prevents it from further appearing in or affecting the program. Additionally has a chance to decrease the upkeep of other workers of this worker's type by increasing the size of
            the labor pool
        """
        super().fire()
        self.worker_type.on_fire(wander=wander)

    def image_variants_setup(self, from_save, input_dict):
        """
        Description:
            Sets up this unit's image variants
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
        Output:
            None
        """
        super().image_variants_setup(from_save, input_dict)
        return
        for variant_type in [
            "soldier",
            "porter",
        ]:  # adds image_dict['soldier']: '.../soldier.png' and image_dict['porter']: '.../porter.png' if any are present in folders
            variants = actor_utility.get_image_variants(
                self.image_dict["default"], keyword=variant_type
            )
            if len(variants) > 0:
                self.image_dict[variant_type] = random.choice(variants)
        super().image_variants_setup(from_save, input_dict)

    def get_worker(self) -> "pmob":
        """
        Description:
            Returns the worker associated with this unit, if any (self if worker, crew if vehicle, worker component if group)
        Input:
            None
        Output:
            worker: Returns the worker associated with this unit, if any
        """
        return self
