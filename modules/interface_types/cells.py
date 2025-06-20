# Contains functionality for grid cells

import pygame
from typing import Dict, List, Any
from modules.constructs import images
from modules.util import scaling
from modules.constants import constants, status, flags


class cell:
    """
    Object representing one cell of a grid corresponding to one of its coordinates, which can subscribe to a location to render its contents
    """

    def __init__(self, x, y, width, height, grid, color):
        """
        Description:
            Initializes this object
        Input:
            int width: Pixel width of this cell
            int height: Pixel height of this cell
            grid grid: The grid that this cell is attached to
            string color: Color in the color_dict dictionary for this cell when nothing is covering it
        Output:
            None
        """
        self.x: int = x
        self.y: int = y
        self.supports_batch_tooltip: bool = True
        self.width: int = width
        self.height: int = height
        self.grid = grid
        self.color: tuple[int, int, int] = color
        self.pixel_x, self.pixel_y = self.grid.convert_coordinates((self.x, self.y))
        self.Rect: pygame.Rect = pygame.Rect(
            self.pixel_x, self.pixel_y - self.height, self.width, self.height
        )  # (left, top, width, height)
        self.location = None
        self.image: images.cell_image = images.cell_image(self)
        self.grid.world_handler.find_location(self.x, self.y).subscribe_cell(self)

    @property
    def batch_tooltip_list(self):
        return self.get_location().batch_tooltip_list

    def set_image(self, *args, **kwargs):
        self.image.set_image(*args, **kwargs)

    def get_location(self):
        return self.location

    def can_show_tooltip(self):
        return self.grid.can_show() and self.touching_mouse()

    def draw(self):
        """
        Description:
            Draws this cell as a rectangle with a certain color on its grid, depending on this cell's color value, along with actors this cell contains
        Input:
            None
        Output:
            None
        """
        pygame.draw.rect(
            constants.game_display,
            (self.color[0], self.color[1], self.color[2]),
            self.Rect,
        )
        self.image.draw()
        self.image.show_num_mobs()

    def draw_outline(self, color: str) -> None:
        pygame.draw.rect(
            constants.game_display,
            constants.color_dict[color],
            self.Rect,
            self.image.outline_width,
        )

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
