# Contains functions that manage the text box and other miscellaneous text display utility

from __future__ import annotations
import pygame
from modules.util import scaling
from modules.constants import constants, status, flags


def text(message, font):
    """
    Description:
        Returns a rendered pygame.Surface of the inputted text
    Input:
        string message: Text to be rendered
        font font: Constructs font with which the text is rendered
    Output:
        pygame.Surface: Rendered pygame.Surface of the inputted text
    """
    try:
        text_surface = font.pygame_font.render(message, False, font.color)
    except:
        text_surface = pygame.Surface(
            (1, 1), pygame.HWSURFACE | pygame.DOUBLEBUF
        )  # prevents error when trying to render very small text (of width 0) on very low resolutions
    return text_surface


def manage_text_list(text_list, max_length):
    """
    Description:
        Removes any text lines in the inputted list past the inputted length
    Input:
        string list text_list: List of text lines contained in the text box
        int max_length: Maximum number of text lines that the text box should be able to have
    Output:
        string list: Inputted list shortened to the inputted length
    """
    if len(text_list) > max_length:
        while not len(text_list) == max_length:
            text_list.pop(0)
    return text_list


def print_to_screen(input_message: str):
    """
    Description:
        Adds the inputted message to the bottom of the text box
    Input:
        string input_message: Message to be added to the text box
    Output:
        None
    """
    font = constants.fonts[constants.DEFAULT_FONT]
    current_word = ""
    current_line = ""
    for index in range(len(input_message)):
        current_word += input_message[index]
        if input_message[index] == " " or index == len(input_message) - 1:
            if font.calculate_size(current_line + current_word) > scaling.scale_width(
                constants.DEFAULT_TEXT_BOX_WIDTH
            ):
                status.text_list.append(current_line)
                current_line = f"    "
            current_line += current_word
            current_word = ""
    status.text_list.append(current_line)


def print_to_previous_message(message):
    """
    Description:
        Adds the inputted message to the most recently displayed message of the text box
    Input:
        string message: Message to be added to the text box
    Output:
        None
    """
    status.text_list[-1] = status.text_list[-1] + message


def remove_underscores(message):
    """
    Description:
        Replaces underscores in the inputted message with spaces
    Input:
        string message: a message with underscores
    Output:
        string: the inputted message but with spaces
    """
    return message.replace("_", " ")


def prepare_render(
    message, font=None, override_input_dict=None, target_width=None, alignment="center"
):
    """
    Description:
        Prepares a dictionary that can be passed to as an image id to render the inputted message in the desired font
    Input:
        string message: Text to render
        font font: Constructs font to render text in - myfont by default
    Output:
        dictionary: Returns image id dictionary of inputted message in inputted font
    """
    if not font:
        font = constants.myfont
    width, height = font.pygame_font.size(message)
    return_dict = {
        "image_id": message,
        "override_width": width,
        "override_height": height,
        "font": font,
    }
    if alignment == "center":
        pass
    elif alignment == "left":
        if target_width:
            return_dict["abs_x_offset"] = -target_width / 2 + width / 2
        else:
            return_dict["abs_x_offset"] = -width / 2
    elif alignment == "right":
        if target_width:
            return_dict["abs_x_offset"] = target_width / 2 - width / 2
        else:
            return_dict["abs_x_offset"] = width / 2
    if override_input_dict:
        for value in override_input_dict:
            return_dict[value] = override_input_dict[value]
    return return_dict


def generate_table_text_image_id(
    input_text: str, scale_width: bool = False, width_bound: int = 0
) -> None:
    """
    Description:
        Sets this image to be a text image with the inputted text
    Input:
        str text: Text to display in this image
    Output:
        None
    """
    if not input_text:
        return [{"image_id": "misc/empty.png"}]
    font = constants.fonts[constants.DEFAULT_NOTIFICATION_FONT]
    width, height = font.pygame_font.size(input_text)
    if scale_width:
        width = min(width, width_bound - scaling.scale_width(5))
        # Forces smaller text to fit within cell's width - use for non-flex width cells
    return [
        {
            "image_id": text(input_text, font),
            "override_width": width,
            "override_height": height,
            "level": constants.TABLE_TEXT_LEVEL,
        }
    ]
