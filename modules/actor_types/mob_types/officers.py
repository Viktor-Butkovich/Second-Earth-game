# Contains functionality for officer units

from .pmobs import pmob
from ...util import actor_utility
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
                'officer_type': string value - Type of officer that this is, like 'explorer', or 'engineer'
                'end_turn_destination': string or int tuple - Required if from save, 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string - Required if end_turn_destination is not 'none', matches the status key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'max_movement_points': int value - Required if from save, maximum number of movement points this mob can have
                'veteran': boolean value - Required if from save, whether this officer is a veteran
        Output:
            None
        """
        super().__init__(from_save, input_dict, original_constructor=False)
        self.is_officer = True
        self.officer_type = input_dict.get("officer_type", type(self).__name__)
        self.set_controlling_minister_type(
            constants.officer_minister_dict[self.officer_type]
        )
        if not from_save:
            self.veteran = False
            self.selection_sound()
        else:
            self.veteran = input_dict["veteran"]
            if self.veteran:
                self.load_veteran()
        self.finish_init(original_constructor, from_save, input_dict)

    def replace(self, attached_group="none"):
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
            constants.recruitment_costs[self.default_name] * -1,
            "attrition_replacements",
        )
        if not attached_group == "none":
            attached_group.set_name(attached_group.default_name)
            attached_group.veteran = False

    def to_save_dict(self):
        """
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                Along with superclass outputs, also saves the following values:
                'officer_type': Type of officer that this is, like 'explorer' or 'engineer'
                'veteran': Whether this officer is a veteran
        """
        save_dict = super().to_save_dict()
        save_dict["officer_type"] = self.officer_type
        save_dict["veteran"] = self.veteran
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
        self.veteran = True
        self.set_name("veteran " + self.name)
        self.update_image_bundle()
        if status.displayed_mob == self:
            actor_utility.calibrate_actor_info_display(
                status.mob_info_display, self
            )  # updates actor info display with veteran icon

    def load_veteran(self):
        """
        Description:
            Promotes this officer to a veteran while loading, changing the name as needed to prevent the word veteran from being added multiple times
        Input:
            None
        Output:
            None
        """
        self.promote()
        if status.displayed_mob == self:
            actor_utility.calibrate_actor_info_display(status.mob_info_display, self)

    def can_show_tooltip(self):
        """
        Description:
            Returns whether this officer's tooltip can be shown. Along with the superclass' requirements, officer tooltips cannot be shown when attached to another actor, such as when part of a group
        Input:
            None
        Output:
            None
        """
        if not (self.in_group or self.in_vehicle):
            return super().can_show_tooltip()
        else:
            return False

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
        self.go_to_grid(self.images[0].current_cell.grid, (self.x, self.y))
        self.select()
        if self.movement_points > 0:
            self.add_to_turn_queue()
