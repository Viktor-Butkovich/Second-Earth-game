# Contains functionality for instructions pages

from modules.interface_types.labels import label
from modules.interface_types.buttons import button
from modules.util import scaling, text_utility
from modules.constants import constants, status, flags


class instructions_button(button):
    """
    Button that displays the first page of game instructions when clicked
    """

    def on_click(self):
        """
        Description:
            Controls this button's behavior when clicked. This type of button displays the first page of game instructions when clicked
        Input:
            None
        Output:
            None
        """
        if status.current_instructions_page == None:
            display_instructions_page(0)
        else:
            status.current_instructions_page.remove_complete()
            status.current_instructions_page = None
            constants.current_instructions_page_index = 0


class instructions_page(label):
    """
    Label shown when the instructions button is pressed that goes to the next instructions page when clicked, or stops showing instructions if it is the last one. Unlike other labels, can have multiple lines
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'message': string value - Default text for this label
        Output:
            None
        """
        self.minimum_height = scaling.scale_height(
            constants.default_display_height - 120
        )
        self.ideal_width = scaling.scale_width(constants.default_display_width - 120)
        input_dict["coordinates"] = scaling.scale_coordinates(60, 60)
        input_dict["minimum_width"] = self.ideal_width
        input_dict["height"] = self.minimum_height
        input_dict["modes"] = [constants.STRATEGIC_MODE, constants.EARTH_MODE]
        input_dict["image_id"] = "misc/default_notification.png"
        super().__init__(input_dict)

    def on_click(self):
        """
        Description:
            Controls this button's behavior when clicked. This type of button displays the next page of game instructions when clicked, or closes the instructions if there are no more pages
        Input:
            None
        Output:
            None
        """
        if (
            constants.current_instructions_page_index
            != len(status.instructions_list) - 1
        ):
            constants.current_instructions_page_index += 1
            constants.current_instructions_page_text = status.instructions_list[
                constants.current_instructions_page_index
            ]
            status.current_instructions_page = instructions_page(
                constants.current_instructions_page_text
            )
            self.remove_complete()
        else:
            status.current_instructions_page = None
            self.remove_complete()

    def set_label(self, new_message):
        """
        Description:
            Sets this page's text to the corresponding item in the inputted string, adjusting width and height as needed
        Input:
            string instruction_text: New text for this instructions page
        Output:
            None
        """
        self.message = new_message
        self.format_message()
        for text_line in self.message:
            self.width = max(
                self.minimum_width,
                self.font.calculate_size(text_line) + scaling.scale_width(10),
            )

    def draw(self):
        """
        Description:
            Draws this page and draws its text on top of it
        Input:
            None
        Output:
            None
        """
        if self.showing:
            self.image.draw()
            for text_line_index in range(len(self.message)):
                text_line = self.message[text_line_index]
                constants.game_display.blit(
                    text_utility.text(text_line, self.font),
                    (
                        self.x + 10,
                        constants.display_height
                        - (self.y + self.height - (text_line_index * self.font.size)),
                    ),
                )

    def format_message(self):
        """
        Description:
            Converts this page's string message to a list of strings, with each string representing a line of text. Each line of text ends when its width exceeds the ideal_width. Also describes how to close the instructions or go to
                the next page
        Input:
            None
        Output:
            None
        """
        new_message = []
        next_line = ""
        next_word = ""
        for index in range(len(self.message)):
            next_word += self.message[index]
            if self.message[index] == " ":
                if self.font.calculate_size(next_line + next_word) > self.ideal_width:
                    new_message.append(next_line)
                    next_line = ""
                next_line += next_word
                next_word = ""
        next_line += next_word
        new_message.append(next_line)
        new_message.append("Click to go to the next instructions page.")
        new_message.append(
            "Press the display instructions button on the right side of the screen again to close the instructions."
        )
        new_message.append("Page " + str(constants.current_instructions_page_index + 1))

        self.message = new_message

    def update_tooltip(self):
        """
        Description:
            Sets this page's tooltip to what it should be. By default, instructions pages describe how to close the instructions or go to the next page
        Input:
            None
        Output:
            None
        """
        self.set_tooltip(
            [
                "Click to go to the next instructions page.",
                "Press the display instructions button on the right side of the screen again to close the instructions.",
            ]
        )


def display_instructions_page(page_number):
    """
    Description:
        Displays a new instructions page with text corresponding to the inputted page number
    Input:
        int page_number: Page number of instructions to display,
    Output:
        None
    """
    constants.current_instructions_page_index = page_number
    constants.current_instructions_page_text = status.instructions_list[page_number]
    status.current_instructions_page = instructions_page(
        constants.current_instructions_page_text
    )
