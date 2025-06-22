# Contains functionality for icons that follow the mouse pointer

import pygame
from modules.constructs.images import free_image
from modules.constants import constants, status, flags


class mouse_follower_template(free_image):
    """
    Free image that follows the mouse pointer and appears in certain situations, such as when choosing on a movement destination
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
        Output:
            None
        """
        input_dict["image_id"] = "misc/targeting_mouse.png"
        input_dict["coordinates"] = pygame.mouse.get_pos()
        input_dict["width"] = 50
        input_dict["height"] = 50
        input_dict["modes"] = [constants.STRATEGIC_MODE, constants.EARTH_MODE]
        super().__init__(input_dict)

    def update(self):
        """'
        Moves this image to follow the mouse pointer
        """
        self.x, self.y = pygame.mouse.get_pos()
        self.x -= self.width // 2
        self.y += self.height // 2

    def draw(self):
        """
        Draws this image if the player is currently choosing a movement destination
        """
        if (
            flags.choosing_destination
            or flags.choosing_advertised_item
            or flags.drawing_automatic_route
        ):
            self.update()
            super().draw()
