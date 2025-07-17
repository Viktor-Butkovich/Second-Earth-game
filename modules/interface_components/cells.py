# Contains functionality for grid cells

import pygame
from modules.interface_components import interface_elements
from modules.constructs import images
from modules.constants import constants, status, flags


class cell(interface_elements.interface_element):
    """
    Object representing one cell of a grid corresponding to one of its coordinates, which can subscribe to a location to render its contents
    """

    def __init__(self, input_dict) -> None:
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this cell's bottom left corner
                'width': int value - Pixel width of this cell
                'height': int value - Pixel height of this cell
                'grid_coordinates': tuple[int, int] - Coordinates of this cell in the grid, e.g (0, 0) for the origin cell
                'grid': grid value - Grid this cell belongs to
        Output:
            None
        """
        super().__init__(input_dict)
        self.grid = input_dict["grid"]
        self.grid_x, self.grid_y = input_dict["grid_coordinates"]
        self.subscribed_source = None
        # A cell can calibrate to a source, an object that must support batch tooltips
        #   Sources are responsible for handling the cell's image updates
        #   Source calibration is handled externally
        self.image: images.cell_image = images.cell_image(self)
        self.set_image([{"image_id": "misc/empty.png"}])

    def set_origin(self, new_x, new_y):
        """
        Description:
            Sets this interface element's location at the inputted coordinates
        Input:
            int new_x: New x coordinate for this element's origin
            int new_y: New y coordinate for this element's origin
        Output:
            None
        """
        super().set_origin(new_x, new_y)
        if self.image:
            self.image.update_state()

    @property
    def batch_tooltip_list(self):
        """
        Gets a 2D list of strings to use as this object's tooltip
            Each string is displayed on a separate line, while each sublist is displayed in a separate box
        """
        if self.subscribed_source:
            return self.subscribed_source.batch_tooltip_list
        else:
            return []

    def set_image(self, *args, **kwargs):
        """
        Description:
            Changes the image reflected by this cell, used when re-calibrating to a subscribed location
        Input:
            image ID list image_id_list: Image ID(s) for this image
        Output:
            None
        """
        self.image.set_image(*args, **kwargs)

    def set_text(self, *args, **kwargs):
        """
        Description:
            Changes the image reflected by this cell - wrapper over set-image to set an inputted text argument
        Input:
            string text: Text to display in this cell
        Output:
            None
        """
        self.image.set_text(*args, **kwargs)

    @property
    def source(self):
        """
        Gets the subscribed source of this cell
        """
        return self.subscribed_source

    def can_show_tooltip(self):
        """
        Returns whether this cell's tooltip can currently be shown
        """
        return self.grid.can_show() and self.touching_mouse()

    def draw(self):
        """
        Draws this cell as a rectangle with a certain color on its grid, depending on this cell's color value, along with actors this cell contains
        """
        self.image.draw()
        if self.source and self.source.actor_type == constants.LOCATION_ACTOR_TYPE:
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
