# Contains functionality for notifications

from modules.interface_types.labels import multi_line_label
from modules.util import actor_utility
from modules.constants import constants, status, flags


class notification(multi_line_label):
    """
    Multi-line label that prompts the user to click on it, and disappears when clicked
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'message': string value - Default text for this label, with lines separated by /n
                'ideal_width': int value - Pixel width that this label will try to retain. Each time a word is added to the label, if the word extends past the ideal width, the next line
                    will be started
                'minimum_height': int value - Minimum pixel height of this label. Its height will increase if the contained text would extend past the bottom of the label
                'on_remove' = []: List value - Functions to run after this notification is removed, in format [(function, [args]), ...]
        Output:
            None
        """
        status.displayed_notification = self
        self.can_remove = True
        if input_dict.get("extra_parameters", False):
            self.can_remove = input_dict["extra_parameters"].get("can_remove", True)
        super().__init__(input_dict)
        self.in_notification = True
        self.is_action_notification = False
        self.notification_dice = (
            0  # by default, do not show any dice when notification shown
        )
        constants.sound_manager.play_sound("effects/receiving_message")
        self.notification_type = input_dict.get(
            "notification_type", input_dict["init_type"]
        )
        if input_dict.get("on_reveal", None):
            if (
                type(input_dict["on_reveal"]) == tuple
            ):  # If given tuple, call function in 1st index with list of arguments in 2nd index
                input_dict["on_reveal"][0](*input_dict["on_reveal"][1])
            else:
                input_dict["on_reveal"]()
        self.on_remove = input_dict.get("on_remove", [])
        if self.on_remove == None:
            self.on_remove = []

        if input_dict.get("zoom_destination", None):
            target = input_dict["zoom_destination"]
            if target.actor_type == constants.BUILDING_ACTOR_TYPE:
                target = target.cell.tile

            if target.actor_type == constants.TILE_ACTOR_TYPE:
                actor_utility.calibrate_actor_info_display(
                    status.mob_info_display, None
                )
                actor_utility.calibrate_actor_info_display(
                    status.tile_info_display, target
                )
                for mini_grid in target.cell.grid.mini_grids:
                    mini_grid.calibrate(target.x, target.y)
            elif target.actor_type == constants.MOB_ACTOR_TYPE:
                if (
                    target.get_cell()
                ):  # If non-hidden mob, move to front of tile and select
                    target.select()
                else:  # If hidden mob, move to location and select tile
                    for mini_grid in target.grids[0].mini_grids:
                        mini_grid.calibrate(target.x, target.y)
                    actor_utility.calibrate_actor_info_display(
                        status.tile_info_display,
                        target.grids[0].find_cell(target.x, target.y).tile,
                    )

    def format_message(self):
        """
        Description:
            Converts this notification's string message to a list of strings, with each string representing a line of text. Each line of text ends when its width exceeds the ideal_width or when a '/n' is encountered in the text
        Input:
            None
        Output:
            None
        """
        super().format_message()
        if self.can_remove:
            self.message.append("Click to remove this notification.")

    def update_tooltip(self):
        """
        Description:
            Sets this notification's tooltip to what it should be. By default, notifications prompt the player to close them
        Input:
            None
        Output:
            None
        """
        if self.can_remove:
            self.set_tooltip(["Click to remove this notification"])
        else:
            self.set_tooltip(self.message)

    def on_click(self, override_can_remove=False):
        """
        Description:
            Controls this notification's behavior when clicked. By default, notifications are removed when clicked
        Input:
            None
        Output:
            None
        """
        if self.can_remove or override_can_remove:
            if self.has_parent_collection:
                self.parent_collection.remove_recursive(complete=False)
            else:
                self.remove()
            constants.notification_manager.handle_next_notification()

    def remove(self):
        """
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. By default, notifications are removed when clicked. When a notification is removed, the next notification is shown,
                if there is one
        Input:
            None
        Output:
            None
        """
        for current_on_remove in self.on_remove:
            current_on_remove[0](*current_on_remove[1])
        super().remove()
        status.displayed_notification = None
