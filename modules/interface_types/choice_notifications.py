# Contains functionality for choice notifications

from typing import List
from modules.interface_types import buttons, action_notifications
from modules.util import utility, text_utility, scaling
from modules.constructs import unit_types
from modules.constants import constants, status, flags


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
        Controls this notification's behavior when clicked. Choice notifications do nothing when clicked, instead acting when their choice buttons are clicked
        """
        if choice_button_override:
            super().on_click()
        return  # does not remove self when clicked

    @property
    def tooltip_text(self) -> List[List[str]]:
        """
        Provides the tooltip for this object
        """
        return ["Choose an option to close this notification"]

    def remove(self):
        """
        Removes this object from relevant lists and prevents it from further appearing in or affecting the program. When a notification is removed, the next notification is shown, if there is one. Choice notifications are removed
            when one of their choice buttons is clicked
        """
        super().remove()
        for current_choice_button in self.choice_buttons:
            current_choice_button.remove()


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
                self.recruitment_type: unit_types.unit_type = (
                    self.notification.choice_info_dict["recruitment_type"]
                )
                self.message = self.recruitment_type.recruitment_verb.capitalize()

            case constants.CHOICE_CONFIRM_MAIN_MENU_BUTTON:
                self.message = "Main menu"

            case constants.CHOICE_QUIT_BUTTON:
                self.message = "Exit game"

            case constants.CHOICE_END_TURN_BUTTON:
                self.message = "End turn"

            case constants.CHOICE_FIRE_BUTTON:
                self.message = "Fire"

            case constants.CHOICE_CONFIRM_FIRE_MINISTER_BUTTON:
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
        Controls this button's behavior when clicked. Choice buttons remove their notifications when clicked, along with the normal behaviors associated with their button_type
        """
        super().on_click()
        self.notification.on_click(choice_button_override=True)

    def draw(self):
        """
        Draws this button below its choice notification and draws a description of what it does on top of it
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

    @property
    def tooltip_text(self) -> List[List[str]]:
        """
        Provides the tooltip for this object
        """
        if self.button_type == constants.RECRUITMENT_CHOICE_BUTTON:
            if self.recruitment_type.number >= 2:
                return [
                    f"{utility.capitalize(self.recruitment_type.recruitment_verb)} a unit of {self.recruitment_type.name} for {self.recruitment_type.recruitment_cost} money"
                ]
            else:
                return [
                    f"{utility.capitalize(self.recruitment_type.recruitment_verb)} a {self.recruitment_type.name} for {self.recruitment_type.recruitment_cost} money"
                ]

        elif self.button_type == constants.CHOICE_END_TURN_BUTTON:
            return ["End the current turn"]

        elif self.button_type == constants.CHOICE_CONFIRM_MAIN_MENU_BUTTON:
            return ["Exits to the main menu without saving"]

        elif self.button_type == constants.CHOICE_QUIT_BUTTON:
            return ["Exits the game without saving"]

        elif self.button_type == None:
            return ["Cancel"]

        else:
            return [self.message]


class recruitment_choice_button(choice_button):
    """
    Choice_button that recruits a unit when clicked
    """

    def on_click(self):
        """
        Controls this button's behavior when clicked. Recruitment choice buttons recruit a unit, pay for the unit's cost, and remove their attached notification when clicked
        """
        input_dict = {
            "select_on_creation": True,
            "location": status.earth_world.find_location(0, 0),
        }
        constants.money_tracker.change(
            -1 * self.recruitment_type.recruitment_cost, "unit_recruitment"
        )
        input_dict.update(self.recruitment_type.generate_input_dict())
        constants.actor_creation_manager.create(False, input_dict)
        super().on_click()
