# Contains functions that manage the text box and other miscellaneous text display utility

import pygame
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


def print_to_screen(input_message):
    """
    Description:
        Adds the inputted message to the bottom of the text box
    Input:
        string input_message: Message to be added to the text box
    Output:
        None
    """
    status.text_list.append(input_message)


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


def prepare_render(message, font=None, override_input_dict=None):
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
    if override_input_dict:
        for value in override_input_dict:
            return_dict[value] = override_input_dict[value]
    return return_dict
