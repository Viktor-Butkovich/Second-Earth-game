# Contains functionality for choice notifications

from . import buttons, action_notifications
from ..util import text_utility, scaling, market_utility, utility
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags


class choice_notification(action_notifications.action_notification):
    """
    Notification that presents 2 choices and is removed when one is chosen rather than when the notification itself is clicked, causing a different outcome depending on the chosen option
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
                'button_types': string list value - List of string corresponding to the button types of this notification's choice buttons, like ['end turn', None
                    - Each button type could also be a dictionary value, in which case the created button will be an anonymous button with
                        functionality decided by the dictionary's contents
                'choice_info_dict': dictionary value - Dictionary containing any case-specific information for choice buttons to function as intended
        Output:
            None
        """
        button_height = scaling.scale_height(50)
        super().__init__(input_dict)
        self.choice_buttons = []
        self.choice_info_dict = input_dict["choice_info_dict"]
        button_types = input_dict["button_types"]
        for current_button_type_index in range(len(button_types)):
            if type(button_types[current_button_type_index]) == dict:
                init_type = constants.ANONYMOUS_BUTTON
            elif (
                button_types[current_button_type_index]
                == constants.RECRUITMENT_CHOICE_BUTTON
            ):
                init_type = constants.RECRUITMENT_CHOICE_BUTTON
            else:
                init_type = constants.CHOICE_BUTTON
            self.choice_buttons.append(
                constants.actor_creation_manager.create_interface_element(
                    {
                        "coordinates": (
                            self.x
                            + (
                                current_button_type_index
                                * round(self.width / len(button_types))
                            ),
                            self.y - button_height,
                        ),
                        "width": round(self.width / len(button_types)),
                        "height": button_height,
                        "modes": self.modes,
                        "button_type": button_types[current_button_type_index],
                        "image_id": "misc/paper_label.png",
                        "notification": self,
                        "init_type": init_type,
                    }
                )
            )

    def on_click(self, choice_button_override=False):
        """
        Description:
            Controls this notification's behavior when clicked. Choice notifications do nothing when clicked, instead acting when their choice buttons are clicked
        Input:
            None
        Output:
            None
        """
        if choice_button_override:
            super().on_click()
        return  # does not remove self when clicked

    def update_tooltip(self):
        """
        Description:
            Sets this notification's tooltip to what it should be. Choice notifications prompt the user to click on one of its choice buttons to close it
        Input:
            None
        Output:
            None
        """
        self.set_tooltip(["Choose an option to close this notification"])

    def remove(self):
        """
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. When a notification is removed, the next notification is shown, if there is one. Choice notifications are removed
                when one of their choice buttons is clicked
        Input:
            None
        Output:
            None
        """
        super().remove()
        for current_choice_button in self.choice_buttons:
            current_choice_button.remove_complete()


class choice_button(buttons.button):
    """
    Button with no keybind that is attached to a choice notification and removes its notification when clicked
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'button_type': string value - Determines the function of this button, like 'end turn'
                'keybind_id' = None: pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'notification': choice_notification value: notification to which this choice button is attached
        Output:
            None
        """
        self.button_type = input_dict.get("button_type", input_dict["init_type"])
        self.notification = input_dict["notification"]
        match self.button_type:
            case constants.RECRUITMENT_CHOICE_BUTTON:
                self.recruitment_type = self.notification.choice_info_dict[
                    "recruitment_type"
                ]
                self.recruitment_name = self.notification.choice_info_dict[
                    "recruitment_name"
                ]
                if self.recruitment_type in [constants.SHIP]:
                    self.message = "Purchase"
                    self.verb = "purchase"
                else:
                    self.message = "Hire"
                    self.verb = "hire"
                self.cost = self.notification.choice_info_dict["cost"]
                self.mob_image_id = self.notification.choice_info_dict.get(
                    "mob_image_id"
                )  # Image ID provided for most units, but generated on creation for workers

            case constants.CHOICE_CONFIRM_MAIN_MENU_BUTTON:
                self.message = "Main menu"

            case constants.CHOICE_CONFIRM_REMOVE_MINISTER:
                self.message = "Confirm"

            case constants.CHOICE_QUIT_BUTTON:
                self.message = "Exit game"

            case constants.CHOICE_END_TURN_BUTTON:
                self.message = "End turn"

            case constants.CHOICE_FIRE_BUTTON:
                self.message = "Fire"

            case None:
                self.message = "Cancel"

            case _:
                self.message = input_dict["button_type"].capitalize()
        super().__init__(input_dict)
        self.font = constants.fonts["default_notification"]
        self.in_notification = True

    def on_click(self):
        """
        Description:
            Controls this button's behavior when clicked. Choice buttons remove their notifications when clicked, along with the normal behaviors associated with their button_type
        Input:
            None
        Output:
            None
        """
        super().on_click()
        self.notification.on_click(choice_button_override=True)

    def draw(self):
        """
        Description:
            Draws this button below its choice notification and draws a description of what it does on top of it
        Input:
            None
        Output:
            None
        """
        super().draw()
        if self.showing:
            constants.game_display.blit(
                text_utility.text(self.message, self.font),
                (
                    self.x + scaling.scale_width(10),
                    constants.display_height - (self.y + self.height),
                ),
            )

    def update_tooltip(self):
        """
        Description:
            Sets this image's tooltip to what it should be, depending on its button_type
        Input:
            None
        Output:
            None
        """
        if self.button_type == constants.RECRUITMENT_CHOICE_BUTTON:
            if self.recruitment_type.endswith("workers"):
                self.set_tooltip(
                    [
                        f"{utility.capitalize(self.verb)} a unit of {self.recruitment_name} for {str(self.cost)} money"
                    ]
                )
            else:
                self.set_tooltip(
                    [
                        f"{utility.capitalize(self.verb)} a {self.recruitment_name} for {str(self.cost)} money"
                    ]
                )

        elif self.button_type == constants.CHOICE_END_TURN_BUTTON:
            self.set_tooltip(["End the current turn"])

        elif self.button_type == constants.CHOICE_CONFIRM_MAIN_MENU_BUTTON:
            self.set_tooltip(["Exits to the main menu without saving"])

        elif self.button_type == constants.CHOICE_QUIT_BUTTON:
            self.set_tooltip(["Exits the game without saving"])

        elif self.button_type == None:
            self.set_tooltip(["Cancel"])

        else:
            self.set_tooltip(
                [self.button_type.capitalize()]
            )  # stop trading -> ['Stop trading']


class recruitment_choice_button(choice_button):
    """
    Choice_button that recruits a unit when clicked
    """

    def on_click(self):
        """
        Description:
            Controls this button's behavior when clicked. Recruitment choice buttons recruit a unit, pay for the unit's cost, and remove their attached notification when clicked
        Input:
            None
        Output:
            None
        """
        input_dict = {"select_on_creation": True, "coordinates": (0, 0)}
        if (
            status.displayed_tile
        ):  # When recruiting in abstract grid, the correct tile will be selected - use that tile's grids
            input_dict["grids"] = status.displayed_tile.grids
        else:  # If no tile selected, assume recruiting on Earth
            input_dict["grids"] = [status.earth_grid]
        if self.mob_image_id:
            input_dict["image"] = self.mob_image_id
        input_dict["modes"] = input_dict["grids"][0].modes
        constants.money_tracker.change(-1 * self.cost, "unit_recruitment")
        if self.recruitment_type in constants.officer_types:
            name = ""
            for character in self.recruitment_type:
                if not character == "_":
                    name += character
                else:
                    name += " "
            input_dict["name"] = name
            input_dict["init_type"] = self.recruitment_type
            input_dict["officer_type"] = self.recruitment_type

        elif self.recruitment_type in [
            constants.EUROPEAN_WORKERS,
            constants.CHURCH_VOLUNTEERS,
        ]:
            input_dict.update(
                status.worker_types[self.recruitment_type].generate_input_dict()
            )

        elif self.recruitment_type == constants.SHIP:
            image_dict = {
                "default": self.mob_image_id,
                "uncrewed": "mobs/ship/uncrewed.png",
            }
            input_dict["image_dict"] = image_dict
            input_dict["name"] = "ship"
            input_dict["crew"] = None
            input_dict["init_type"] = constants.SHIP
        constants.actor_creation_manager.create(False, input_dict)
        super().on_click()
