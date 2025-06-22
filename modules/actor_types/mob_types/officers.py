# Contains functionality for officer units

import random
from modules.util import utility
from modules.actor_types.mob_types.pmobs import pmob
from modules.constants import constants, status, flags


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
                'end_turn_destination_coordinates': int tuple value - None if no saved destination, destination coordinates if saved destination
                'end_turn_destination_world_index': int value - Index of the world of the end turn destination, if any
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'max_movement_points': int value - Required if from save, maximum number of movement points this mob can have
                'veteran': boolean value - Required if from save, whether this officer is a veteran
        Output:
            None
        """
        if not from_save:
            self.character_info = {}
            self.character_info["ethnicity"] = (
                constants.character_manager.generate_ethnicity()
            )
            self.character_info["masculine"] = random.choice([True, False])
            name = constants.character_manager.generate_name(
                self.character_info["ethnicity"], self.character_info["masculine"]
            )
            while (
                constants.effect_manager.effect_active("omit_default_names")
                and "default" in name
            ):  # Prevent any default first or last names
                self.character_info["ethnicity"] = (
                    constants.character_manager.generate_ethnicity()
                )
                name = constants.character_manager.generate_name(
                    self.character_info["ethnicity"], self.character_info["masculine"]
                )
            self.character_info["name"] = " ".join(name)
        else:
            self.character_info = input_dict["character_info"]
        self.voice_set, self.voice_lines = utility.extract_voice_set(
            self.character_info["masculine"],
            voice_set=self.character_info.get("voice_set", None),
        )
        self.last_voice_line: str = None
        self.character_info["voice_set"] = self.voice_set
        self.group = None
        super().__init__(from_save, input_dict, original_constructor=False)
        if not from_save:
            self.selection_sound()
        else:
            if input_dict["veteran"]:
                self.promote()
        self.finish_init(original_constructor, from_save, input_dict)

    def replace(self, attached_group=None):
        """
        Replaces this unit for a new version of itself when it dies from attrition, removing all experience and name modifications. Also charges the usual officer recruitment cost
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
        Promotes this officer to a veteran after performing various actions particularly well, improving the officer's future capabilities. Creates a veteran star icon that follows this officer
        """
        if not self.get_permission(constants.VETERAN_PERMISSION):
            self.set_name("veteran " + self.name)
            self.set_permission(constants.VETERAN_PERMISSION, True)
