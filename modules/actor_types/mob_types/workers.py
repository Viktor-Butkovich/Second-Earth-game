# Contains functionality for worker units
import random

from .pmobs import pmob
from ...util import actor_utility
from ...util import text_utility
from ...constructs import unit_types
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags
from typing import Dict


class worker(pmob):
    """
    pmob that is required for resource buildings to produce commodities, officers to form group, and vehicles to function
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
                'end_turn_destination': string or int tuple value - Required if from save, None if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not None, matches the status key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'max_movement_points': int value - Required if from save, maximum number of movement points this mob can have
                'worker_type': worker_type value - Type of worker this is, like 'Colonist'. Each type of worker has a separate upkeep, labor pool, and abilities
        Output:
            None
        """
        self.worker_type: unit_types.worker_type = input_dict.get(
            "worker_type", status.worker_types.get(input_dict.get("init_type"))
        )  # Colonist, etc. worker_type object
        super().__init__(from_save, input_dict, original_constructor=False)

        if not from_save:
            self.second_image_variant = random.randrange(0, len(self.image_variants))
        constants.money_label.check_for_updates()
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
                self.image_dict[
                    "left portrait"
                ] = constants.character_manager.generate_unit_portrait(
                    self, metadata={"body_image": self.image_dict["default"]}
                )
                self.image_dict[
                    "right portrait"
                ] = constants.character_manager.generate_unit_portrait(
                    self,
                    metadata={
                        "body_image": self.image_variants[self.second_image_variant]
                    },
                )
            else:
                self.image_dict["left portrait"] = input_dict.get("left portrait", [])
                self.image_dict["right portrait"] = input_dict.get("right portrait", [])
            super().finish_init(
                original_constructor, from_save, input_dict, create_portrait=False
            )

    def replace(self, attached_group=None):
        """
        Description:
            Replaces this unit for a new version of itself when it dies from attrition, removing all experience and name modifications
        Input:
            None
        Output:
            None
        """
        super().replace()
        if attached_group:
            destination = attached_group
        else:
            destination = self
        destination_message = (
            f" for the {destination.name} at ({destination.x}, {destination.y})"
        )
        self.worker_type.on_recruit(purchased=True)
        text_utility.print_to_screen(
            f"Replacement {self.worker_type.name} have been automatically hired{destination_message}."
        )

    def fire(self, wander=True):
        """
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. Additionally has a chance to decrease the upkeep of other workers of this worker's type by increasing the size of
                the labor pool
        Input:
            None
        Output:
            None
        """
        super().fire()
        self.worker_type.on_fire(wander=wander)

    def join_group(self):
        """
        Description:
            Hides this worker when joining a group, preventing it from being directly interacted with until the group is disbanded
        Input:
            None
        Output:
            None
        """
        self.set_permission(constants.IN_GROUP_PERMISSION, True)
        self.hide_images()
        self.remove_from_turn_queue()

    def leave_group(self, group):
        """
        Description:
            Reveals this worker when its group is disbanded, allowing it to be directly interacted with. Does not select this worker, meaning that the officer will be selected rather than the worker when a group is disbanded
        Input:
            group group: group from which this worker is leaving
        Output:
            None
        """
        self.x = group.x
        self.y = group.y
        self.show_images()
        self.set_permission(constants.IN_GROUP_PERMISSION, False)
        self.set_permission(
            constants.DISORGANIZED_PERMISSION,
            group.get_permission(constants.DISORGANIZED_PERMISSION),
        )
        self.go_to_grid(self.get_cell().grid, (self.x, self.y))
        if self.movement_points > 0:
            self.add_to_turn_queue()
        self.update_image_bundle()

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
