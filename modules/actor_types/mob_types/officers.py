# Contains functionality for officer units

import random
from .pmobs import pmob
import modules.constants.constants as constants
import modules.constants.status as status


class officer(pmob):
    """
    pmob that is considered an officer and can join groups and become a veteran
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
                'end_turn_destination': string or int tuple - Required if from save, None if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string - Required if end_turn_destination is not None, matches the status key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'max_movement_points': int value - Required if from save, maximum number of movement points this mob can have
                'veteran': boolean value - Required if from save, whether this officer is a veteran
        Output:
            None
        """
        if not from_save:
            self.character_info = {}
            self.character_info[
                "ethnicity"
            ] = constants.character_manager.generate_ethnicity()
            self.character_info["masculine"] = random.choice([True, False])
            self.character_info["name"] = " ".join(
                constants.character_manager.generate_name(
                    self.character_info["ethnicity"], self.character_info["masculine"]
                )
            )
        else:
            self.character_info = input_dict["character_info"]
        super().__init__(from_save, input_dict, original_constructor=False)
        if not from_save:
            self.selection_sound()
        else:
            if input_dict["veteran"]:
                self.promote()
        self.finish_init(original_constructor, from_save, input_dict)

    def replace(self, attached_group=None):
        """
        Description:
            Replaces this unit for a new version of itself when it dies from attrition, removing all experience and name modifications. Also charges the usual officer recruitment cost
        Input:
            None
        Output:
            None
        """
        super().replace()
        constants.money_tracker.change(
            self.unit_type.recruitment_cost * -1,
            "attrition_replacements",
        )
        if attached_group:
            attached_group.set_name(attached_group.default_name)
            attached_group.set_permission(constants.VETERAN_PERMISSION, False)

    def to_save_dict(self):
        """
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                Along with superclass outputs, also saves the following values:
                'veteran': Whether this officer is a veteran
        """
        save_dict = super().to_save_dict()
        save_dict["veteran"] = self.get_permission(constants.VETERAN_PERMISSION)
        save_dict["character_info"] = self.character_info
        return save_dict

    def promote(self):
        """
        Description:
            Promotes this officer to a veteran after performing various actions particularly well, improving the officer's future capabilities. Creates a veteran star icon that follows this officer
        Input:
            None
        Output:
            None
        """
        if not self.get_permission(constants.VETERAN_PERMISSION):
            self.set_name("veteran " + self.name)
            self.set_permission(constants.VETERAN_PERMISSION, True)

    def join_group(self):
        """
        Description:
            Hides this officer when joining a group, preventing it from being directly interacted with until the group is disbanded
        Input:
            None
        Output:
            None
        """
        self.in_group = True
        self.hide_images()
        self.remove_from_turn_queue()

    def leave_group(self, group):
        """
        Description:
            Reveals this officer when its group is disbanded, allowing it to be directly interacted with. Also selects this officer, rather than the group's worker
        Input:
            group group: group from which this officer is leaving
        Output:
            None
        """
        self.in_group = False
        self.x = group.x
        self.y = group.y
        self.show_images()
        self.go_to_grid(self.get_cell().grid, (self.x, self.y))
        self.select()
        if self.movement_points > 0:
            self.add_to_turn_queue()
