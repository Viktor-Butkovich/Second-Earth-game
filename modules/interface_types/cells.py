# Contains functionality for grid cells

import pygame
import random
from typing import Dict, List, Any
from modules.util import actor_utility
from modules.constructs import locations
from modules.constants import constants, status, flags


class cell:
    """
    Object representing one cell of a grid corresponding to one of its coordinates, able to contain terrain, resources, mobs, and tiles
    """

    def __init__(self, x, y, width, height, grid, color):
        """
        Description:
            Initializes this object
        Input:
            int x: the x coordinate of this cell in its grid
            int y: the y coordinate of this cell in its grid
            int width: Pixel width of this button
            int height: Pixel height of this button
            grid grid: The grid that this cell is attached to
            string color: Color in the color_dict dictionary for this cell when nothing is covering it
        Output:
            None
        """
        self.x: int = x
        self.y: int = y
        self.width: int = width
        self.height: int = height
        self.grid = grid
        self.color: tuple[int, int, int] = color
        self.pixel_x, self.pixel_y = self.grid.convert_coordinates((self.x, self.y))
        self.Rect: pygame.Rect = pygame.Rect(
            self.pixel_x, self.pixel_y - self.height, self.width, self.height
        )  # (left, top, width, height)
        self.tile: status.tile = None
        self.settlement = None
        self.location: locations.location = None
        self.grid.world_handler.find_location(self.x, self.y).add_cell(self)

    def get_location(self) -> locations.location:
        return self.location

    def draw(self):
        """
        Description:
            Draws this cell as a rectangle with a certain color on its grid, depending on this cell's color value, along with actors this cell contains
        Input:
            None
        Output:
            None
        """
        current_color = self.color
        red = current_color[0]
        green = current_color[1]
        blue = current_color[2]
        if not self.get_location().visible:
            red, green, blue = constants.color_dict[constants.COLOR_BLONDE]
        pygame.draw.rect(constants.game_display, (red, green, blue), self.Rect)
        if self.tile:
            for current_image in self.tile.images:
                current_image.draw()
            if self.get_location().visible and self.contained_mobs:
                for current_image in self.contained_mobs[0].images:
                    current_image.draw()
                self.show_num_mobs()

    def show_num_mobs(self):
        """
        Description:
            Draws a number showing how many mobs are in this cell if it contains multiple mobs, otherwise does nothing
        Input:
            None
        Output:
            None
        """
        length = len(self.contained_mobs)
        if length >= 2:
            message = str(length)
            font = constants.fonts["max_detail_white"]
            font_width = self.width * 0.13 * 1.3
            font_height = self.width * 0.3 * 1.3
            textsurface = font.pygame_font.render(message, False, font.color)
            textsurface = pygame.transform.scale(
                textsurface, (font_width * len(message), font_height)
            )
            text_x = self.pixel_x + self.width - (font_width * (len(message) + 0.3))
            text_y = self.pixel_y + (-0.8 * self.height) - (0.5 * font_height)
            constants.game_display.blit(textsurface, (text_x, text_y))

    def touching_mouse(self):
        """
        Description:
            Returns True if this cell is colliding with the mouse, otherwise returns False
        Input:
            None
        Output:
            boolean: Returns True if this cell is colliding with the mouse, otherwise returns False
        """
        if self.Rect.collidepoint(pygame.mouse.get_pos()):
            return True
        else:
            return False
