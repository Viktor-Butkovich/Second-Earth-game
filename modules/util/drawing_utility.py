# Contains functions that control the display of images

import pygame
from modules.constants import constants, status, flags


def rect_to_surface(rect):
    """
    Description:
        Converts the inputted Rect to a Surface and returns it, allowing an image or text to be drawn on it
    Input:
        pygame.Rect rect: Rect to convert to a Surface
    Output:
        pygame.Surface: Returns a version of the inputted Rect converted to a Surface
    """
    return pygame.Surface(
        (rect.width, rect.height), pygame.HWSURFACE | pygame.DOUBLEBUF
    )


def display_image(image, x, y):
    """
    Description:
        Draws the inputted image at the inputted coordinates
    Input:
        pygame.image image: Image to be displayed
        int x: Pixel x coordinate at which to display the image
        int y: Pixel y coordinate at which to display the image
    Output:
        None
    """
    constants.game_display.blit(image, (x, y))


def display_image_angle(image, x, y, angle):
    """
    Description:
        Draws the inputted image at the inputted coordinates tilted at the inputted angle
    Input:
        pygame.image image: Image to be displayed
        int x: Pixel x coordinate at which to display the image
        int y: Pixel y coordinate at which to display the image
        int angle: Angle in degrees at which to display the image
    Output:
        None
    """
    topleft = (x, y)
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft=topleft).center)
    constants.game_display.blit(rotated_image, new_rect.topleft)
