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
        self.selection_outline_color = constants.COLOR_YELLOW
        self.actor_match_outline_color = constants.COLOR_WHITE
        self.pixel_x, self.pixel_y = self.grid.convert_coordinates((self.x, self.y))
        self.Rect: pygame.Rect = pygame.Rect(
            self.pixel_x, self.pixel_y - self.height, self.width, self.height
        )  # (left, top, width, height)
        self.location = None
        self.image: images.cell_image = images.cell_image(self)
        self.batch_tooltip_box_list: List[pygame.Rect] = []
        self.grid.world_handler.find_location(self.x, self.y).add_cell(self)

    @property
    def batch_tooltip_list(self):
        batch_tooltip_list: List[Dict[str, Any]] = []
        batch_tooltip_text_list = self.get_location().generate_batch_tooltip_text_list()
        self.batch_tooltip_box_list = []
        font = constants.fonts["default"]
        tooltip_outline_width = 1
        tooltip_width = 0
        for tooltip_text in batch_tooltip_text_list:
            for text_line in tooltip_text:
                tooltip_width = max(
                    tooltip_width,
                    font.calculate_size(text_line) + scaling.scale_width(10),
                )
            tooltip_height = (len(tooltip_text) * font.size) + scaling.scale_height(5)

            batch_tooltip_list.append(
                {
                    "text": tooltip_text,
                    "box": pygame.Rect(
                        self.pixel_x, self.pixel_y, tooltip_width, tooltip_height
                    ),
                    "outline": pygame.Rect(
                        self.pixel_x - tooltip_outline_width,
                        self.pixel_y + tooltip_outline_width,
                        tooltip_width + (2 * tooltip_outline_width),
                        tooltip_height + (tooltip_outline_width * 2),
                    ),
                    "outline_width": tooltip_outline_width,
                }
            )
        return batch_tooltip_list

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

        # Instead, have some stored pygame surface corresponding to the rendered version of the location and all its contents
        #   From the location, fetch an image ID list of all desired images to render
        #   Cell should have a single image object that takes this image ID list and renders it into a surface
        #   When the cell draws, it should instruct its image to draw at the cell's pixel location
        """
        if self.location:
            for current_image in self.location.images:
                current_image.draw()
            if self.get_location().visible and self.contained_mobs:
                for current_image in self.contained_mobs[0].images:
                    current_image.draw()
                self.show_num_mobs()
        """

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

    def draw_actor_match_outline(self):
        """
        Description:
            Draws an outline around the displayed cell
        Input:
            None
        Output:
            None
        """
        if self.grid.can_show():
            pygame.draw.rect(
                constants.game_display,
                constants.color_dict[self.actor_match_outline_color],
                self.Rect,
                self.image.outline_width,
            )
