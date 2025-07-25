# Contains functionality for labels

import pygame
from typing import List
from modules.interface_components.buttons import button
from modules.util import scaling, text_utility, utility, market_utility
from modules.constructs import item_types
from modules.constants import constants, status, flags


class label(button):
    """
    A button that shares most of a button's behaviors but displays a message and does nothing when clicked
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'minimum_width': int value - Minimum pixel width of this label. Its width will increase if the contained text would extend past the edge of the label
                'message': string value - Default text for this label
        Output:
            None
        """
        self.font = input_dict.get("font", constants.fonts["default_notification"])
        self.current_character = None
        self.message = input_dict["message"]
        self.minimum_width = input_dict["minimum_width"]
        input_dict["width"] = self.minimum_width
        input_dict["button_type"] = "label"
        super().__init__(input_dict)
        self.set_label(self.message)

    def set_label(self, new_message):
        """
        Description:
            Sets this label's text to the inputted string, adjusting width as needed
        Input:
            string new_message: New text for this label
        Output:
            None
        """
        self.message = new_message
        self.width = max(
            self.minimum_width,
            self.font.calculate_size(self.message) + scaling.scale_width(10),
        )
        self.image.width = self.width
        self.Rect.width = self.width
        self.image.set_image(self.image.image_id)
        self.image.Rect = self.Rect

    @property
    def tooltip_text(self) -> List[List[str]]:
        """
        Provides the tooltip for this object
        """
        return [self.message]

    def on_click(self):
        """
        Controls this label's behavior when clicked. By default, labels do nothing when clicked, though label subclasses like notifications may still need on_click functionality
        """
        return

    def draw(self):
        """
        Draws this label and draws its text on top of it, ignoring outlines from the label being clicked
        """
        if self.showing:
            super().draw(allow_show_outline=False)
            constants.game_display.blit(
                text_utility.text(self.message, self.font),
                (
                    self.x + scaling.scale_width(10),
                    constants.display_height - (self.y + self.height),
                ),
            )


class value_label(label):
    """
    Label that tracks the value of a certain variable and is attached to a value_tracker object. Whenever the value of the value_tracker changes, this label is automatically changed
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'minimum_width': int value - Minimum pixel width of this label. Its width will increase if the contained text would extend past the edge of the label
                'value_name': string value - Type of value tracked by this label, like 'turn' for turn number label
        Output:
            None
        """
        self.value_name = input_dict["value_name"]
        input_dict["message"] = "none"
        super().__init__(input_dict)
        self.display_name = text_utility.remove_underscores(
            self.value_name
        )  # public_opinion to public opinion
        camel_case_name = self.display_name.title().replace(" ", "")
        self.tracker = getattr(constants, f"{camel_case_name}Tracker")
        self.tracker.value_label = self
        self.update_label(self.tracker.get())

    def update_label(self, new_value):
        """
        Description:
            Updates the value shown by this label when to match the value of its value_tracker
        Input:
            int new_value: New value of this label's value_tracker
        Output:
            None
        """
        self.set_label(utility.capitalize(self.display_name + ": " + str(new_value)))

    @property
    def tooltip_text(self) -> List[List[str]]:
        """
        Provides the tooltip for this object
        """
        tooltip_text = [self.message]
        if self.value_name == "public_opinion":
            tooltip_text.append(
                "Public opinion represents your company's reputation and expectations for its success and is used to calculate government subsidies"
            )
            tooltip_text.append(
                "Public opinion tends to approach the netural value of 50 over time"
            )
        return tooltip_text


class money_label(value_label):
    """
    Special type of value label that tracks money
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'button_type': string value - Determines the function of this button, like 'end turn'
                'keybind_id' = None: pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'minimum_width': int value - Minimum pixel width of this label. Its width will increase if the contained text would extend past the edge of the label
        Output:
            None
        """
        input_dict["value_name"] = "money"
        super().__init__(input_dict)

    def update_label(self, new_value):
        """
        Description:
            Updates the value shown by this label when to match the value of its value tracker. Money labels additionally show the projected income for the next turn
        Input:
            int new_value: New value of this label's value_tracker
        Output:
            None
        """
        end_turn_money_change = market_utility.calculate_end_turn_money_change()
        if end_turn_money_change >= 0:
            sign = "+"
        else:
            sign = ""
        self.set_label(
            utility.capitalize(
                self.display_name
                + ": "
                + str(new_value)
                + " ("
                + sign
                + str(end_turn_money_change)
                + ")"
            )
        )

    def check_for_updates(self):
        """
        Updates the projected income shown by this label when the income would change for any reason, such as when a worker is hired
        """
        self.update_label(getattr(constants, self.tracker.value_key))

    @property
    def tooltip_text(self) -> List[List[str]]:
        """
        Provides the tooltip for this object
        """
        tooltip_text = [self.message]

        total_upkeep = 0.0
        total_num_instances = 0
        worker_type_info_dicts = {}
        for key, worker_type in status.worker_types.items():
            current_dict = {}
            current_dict["upkeep"] = worker_type.upkeep
            current_dict["total_upkeep"] = worker_type.get_total_upkeep()
            current_dict["num_instances"] = worker_type.num_instances
            current_dict["name"] = worker_type.name
            total_upkeep += current_dict["total_upkeep"]
            total_num_instances += current_dict["num_instances"]
            worker_type_info_dicts[key] = current_dict
        total_upkeep = round(total_upkeep, 2)

        tooltip_text.append("")
        tooltip_text.append(
            f"At the end of the turn, your {total_num_instances} worker{utility.generate_plural(total_num_instances)} will cost a total of {total_upkeep} money in upkeep."
        )
        for key, current_dict in worker_type_info_dicts.items():
            if current_dict["upkeep"] > 0:
                if current_dict["num_instances"] > 0:
                    tooltip_text.append(
                        f"    Your {current_dict['num_instances']} {current_dict['name']} will be paid {current_dict['upkeep']} money, totaling to {current_dict['total_upkeep']} money."
                    )
                else:
                    tooltip_text.append(
                        f"    Any {current_dict['name']} would each be paid {current_dict['upkeep']} money."
                    )
            else:
                if current_dict["num_instances"] > 0:
                    tooltip_text.append(
                        f"    Your {current_dict['num_instances']} {current_dict['name']} will not need to be paid."
                    )
                else:
                    tooltip_text.append(
                        f"    Any {current_dict['name']} would not need to be paid."
                    )
        tooltip_text.append("")

        if len(status.loan_list) > 0:
            tooltip_text.append("")
            tooltip_text.append("Loans: ")
            for current_loan in status.loan_list:
                tooltip_text.append("    " + current_loan.get_description())

        tooltip_text.append("")
        tooltip_text.append(
            f"While public opinion and government subsidies are not entirely predictable, your company is estimated to receive {market_utility.calculate_subsidies(True)} money in subsidies this turn"
        )

        total_sale_revenue = market_utility.calculate_total_sale_revenue()
        if total_sale_revenue > 0:
            tooltip_text.append("")
            tooltip_text.append(
                f"Your {status.minister_types[constants.TERRAN_AFFAIRS_MINISTER].name} has been ordered to sell items at the end of the turn for an estimated total of {total_sale_revenue} money"
            )

        tooltip_text.append("")
        estimated_money_change = market_utility.calculate_end_turn_money_change()
        if estimated_money_change > 0:
            tooltip_text.append(
                f"Between these revenues and expenses, your company is expected to gain about {estimated_money_change} money at the end of the turn."
            )
        elif estimated_money_change < 0:
            tooltip_text.append(
                f"Between these revenues and expenses, your company is expected to lose about {-1 * estimated_money_change} money at the end of the turn."
            )
        else:
            tooltip_text.append(
                "Between these revenues and expenses, your company is expected to neither gain nor lose money at the end of the turn."
            )

        return tooltip_text


class item_prices_label_template(label):
    """
    Label that shows the price of each item. Unlike most labels, its message is a list of strings rather than a string, allowing it to have a line for each item
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'minimum_width': int value - Minimum pixel width of this label. Its width will increase if the contained text would extend past the edge of the label
        Output:
            None
        """
        self.ideal_width = input_dict["minimum_width"]
        self.minimum_height = input_dict["height"]
        input_dict["message"] = "none"
        super().__init__(input_dict)
        self.font = constants.fonts["large_notification"]
        self.update_label()

    def update_label(self):
        """
        Updates the values shown by this label when item prices change
        """
        message = ["Prices: "]
        market_items: List[item_types.item_type] = [
            current_item_type
            for current_item_type in status.item_types.values()
            if current_item_type.can_sell or current_item_type.can_purchase
        ]
        widest_name_width = max(
            [self.font.calculate_size(item_type.name) for item_type in market_items]
        )
        for current_item_type in market_items:
            current_line = ""
            while (
                self.font.calculate_size(f"{current_line}{current_item_type.name}")
                < widest_name_width
            ):
                current_line += " "
            current_line += f"{current_item_type.name}: {current_item_type.price}"
            message.append(current_line)
        self.set_label(message)

    def set_label(self, new_message):
        """
        Description:
            Sets each line of this label's text to the corresponding item in the inputted list, adjusting width as needed
        Input:
            string list new_message: New text for this label, with each item corresponding to a line of text
        Output:
            None
        """
        self.message = new_message
        for text_line in self.message:
            message_size = self.font.calculate_size(text_line)
            if (
                message_size > self.ideal_width - scaling.scale_width(10)
                and message_size + scaling.scale_width(10) > self.width
            ):
                self.width = message_size + scaling.scale_width(20)
                self.image.width = self.width
                self.Rect.width = self.width
                self.image.set_image(self.image.image_id)  # update width scaling
                self.image.Rect = self.Rect

    def draw(self):
        """
        Draws this label and draws its text on top of it
        """
        if constants.current_game_mode in self.modes:
            self.image.draw()
            for text_line_index in range(len(self.message)):
                text_line = self.message[text_line_index]
                constants.game_display.blit(
                    text_utility.text(text_line, self.font),
                    (
                        self.x + scaling.scale_width(10),
                        constants.display_height
                        - (self.y + self.height - (text_line_index * self.font.size)),
                    ),
                )

    @property
    def tooltip_text(self) -> List[List[str]]:
        """
        Provides the tooltip for this object
        """
        return self.message


class multi_line_label(label):
    """
    Label that has multiple lines and moves to the next line when a line of text exceeds its width
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
        Output:
            None
        """
        self.ideal_width = input_dict["ideal_width"]
        self.minimum_height = input_dict["minimum_height"]
        self.original_y = input_dict["coordinates"][1]
        self.center_lines = input_dict.get("center_lines", False)
        input_dict["minimum_width"] = input_dict["ideal_width"]
        input_dict["height"] = self.minimum_height
        super().__init__(input_dict)

    def draw(self):
        """
        Draws this label and draws each line of its text on top of it
        """
        if self.showing:
            self.image.draw()
            for text_line_index in range(len(self.message)):
                text_line = self.message[text_line_index]
                if self.center_lines:
                    x = (
                        self.x
                        + scaling.scale_width(10)
                        + self.width / 2
                        - self.font.pygame_font.size(text_line)[0] / 2
                    )
                else:
                    x = self.x + scaling.scale_width(10)
                constants.game_display.blit(
                    text_utility.text(text_line, self.font),
                    (
                        x,
                        constants.display_height
                        - (self.y + self.height - (text_line_index * self.font.size)),
                    ),
                )

    @property
    def tooltip_text(self) -> List[List[str]]:
        """
        Provides the tooltip for this object
        """
        return self.message

    def format_message(self):
        """
        Converts this label's string message to a list of strings, with each string representing a line of text. Each line of text ends when its width exceeds the ideal_width or when a '/n' is encountered in the text
        """
        new_message = []
        next_line = ""
        next_word = ""
        for index in range(len(self.message)):
            if not (
                (
                    not (index + 2) > len(self.message)
                    and self.message[index] + self.message[index + 1]
                )
                == "/n"
            ):  # don't add if /n
                if not (
                    index > 0 and self.message[index - 1] + self.message[index] == "/n"
                ):  # if on n after /, skip
                    next_word += self.message[index]
            if self.message[index] == " ":
                if self.font.calculate_size(next_line + next_word) > self.ideal_width:
                    new_message.append(next_line)
                    next_line = ""
                next_line += next_word
                next_word = ""
            elif (
                not (index + 2) > len(self.message)
                and self.message[index] + self.message[index + 1]
            ) == "/n":  # don't check for /n if at last index
                new_message.append(next_line)
                next_line = ""
                next_line += next_word
                next_word = ""
        if self.font.calculate_size(next_line + next_word) > self.ideal_width:
            new_message.append(next_line)
            next_line = ""
        next_line += next_word
        new_message.append(next_line)
        self.message = new_message
        self.height = max(self.minimum_height, (len(new_message) + 2) * self.font.size)

    def set_label(self, new_message):
        """
        Description:
            Sets each line of this label's text to the corresponding item in the inputted list, adjusting width and height as needed
        Input:
            string list new_message: New text for this label, with each item corresponding to a line of text
        Output:
            None
        """
        self.message = new_message
        self.format_message()
        for text_line in self.message:
            self.width = max(self.ideal_width, self.font.calculate_size(text_line))
        self.width += scaling.scale_width(5)
        self.Rect = pygame.Rect(
            self.x,
            constants.display_height - self.y - self.height,
            self.width,
            self.height,
        )
        self.image.update_state(self.x, self.y, self.width, self.height)
