# Contains wrapper for pygame font

import pygame
from modules.constants import constants, status, flags


class font:
    """
    Wrapper for pygame font that contains additional information, like font color
    """

    def __init__(self, input_dict=None):
        """
        Description:
            Initializes this object - all inputs are optional
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'descriptor': Key in constants.fonts corresponding to the new font
                'name': Name of font, defaults to constants.font_name
                'size': Size of font, defaults to constants.font_size
                'color': Color dict entry of font, default to 'black'
        Output:
            None
        """
        if not input_dict:
            input_dict = {}
        if input_dict.get("descriptor", None):
            constants.fonts[input_dict["descriptor"]] = self
        self.pygame_font = pygame.font.SysFont(
            input_dict.get("name", constants.font_name),
            input_dict.get("size", constants.font_size),
        )
        self.color = input_dict.get("color", "black")
        self.size = input_dict.get("size", constants.font_size)

    def calculate_size(self, message):
        """
        Description:
            Wrapper for pygame.font.size, calculates and returns the pixel width of the inputted string in this font
        Input:
            string message: Message for which to calculate length
        Output:
            int: Returns pixel width of resulting message
        """
        return self.pygame_font.size(message)[0]
