# Contains functions that scale coordinates and lengths/widths to different resolutions

from __future__ import annotations
from modules.constants import constants, status, flags
from typing import Tuple


def scale_coordinates(x: int, y: int) -> Tuple[int, int]:
    """
    Description:
        Returns a version of the inputted coordinates scaled to the player's screen resolution. For example, if the inputted coordinates are at the center of the program's default screen, the returned coordinates will be in the center
            of the player's screen
    Input:
        int x: Unscaled pixel x coordinate
        int y: Unscaled pixel y coordinate
    Output:
        int: Scaled pixel x coordinate
        int: Scaled pixel y coordinate
    """
    x_ratio = constants.display_width / constants.default_display_width
    y_ratio = constants.display_height / constants.default_display_height
    scaled_x = round(x * x_ratio)
    scaled_y = round(y * y_ratio)
    return (scaled_x, scaled_y)


def scale_width(width: int) -> int:
    """
    Description:
        Returns a version of the inputted width scaled to the player's screen resolution. For example, if the inputted width is as wide as the program's default screen, the returned width will be as wide as the player's screen
    Input:
        int width: Unscaled pixel width
    Output:
        int: Scaled pixel width
    """
    ratio = constants.display_width / constants.default_display_width
    scaled_width = round(width * ratio)
    return scaled_width


def scale_height(height: int) -> int:
    """
    Description:
        Returns a version of the inputted height scaled to the player's screen resolution. For example, if the inputted height is as tall as the program's default screen, the returned height will be as tall as the player's screen
    Input:
        int height: Unscaled pixel height
    Output:
        int: Scaled pixel height
    """
    ratio = constants.display_height / constants.default_display_height
    scaled_height = round(height * ratio)
    return scaled_height


def unscale_width(scaled_width: int) -> int:
    """
    Description:
        Returns a version of the inputted width reverse-scaled from the player's screen resolution, such that x = unscale_width(scale_width(x))
    Input:
        int scaled_width: Scaled pixel width
    Output:
        int: Unscaled pixel width
    """
    ratio = constants.default_display_width / constants.display_width
    unscaled_width = round(scaled_width * ratio)
    return unscaled_width


def unscale_height(scaled_height: int) -> int:
    """
    Description:
        Returns a version of the inputted height reverse-scaled from the player's screen resolution, such that x = unscale_height(scale_height(x))
    Input:
        int scaled_height: Scaled pixel height
    Output:
        int: Unscaled pixel height
    """
    ratio = constants.default_display_height / constants.display_height
    unscaled_height = round(scaled_height * ratio)
    return unscaled_height


def scaled_coordinates_percentage(
    x_percentage: float, y_percentage: float
) -> Tuple[int, int]:
    """
    Description:
        Returns coordinates corresponding to the x_percentage, y_percentage location of the screen
    Input:
        float x_percentage: X coordinate percentage w.r.t. screen width
        float y_percentage: Y coordinate percentage w.r.t. screen height
    Output:
        int: Scaled pixel x coordinate
        int: Scaled pixel y coordinate
    """
    scaled_x = round(constants.display_width * x_percentage)
    scaled_y = round(constants.display_height * y_percentage)
    return (scaled_x, scaled_y)


def scale_width_percentage(width_percentage: float) -> int:
    """
    Description:
        Returns a width corresponding to width_percentage of the screen
    Input:
        float width_percentage: Screen width percentage
    Output:
        int: Scaled pixel width
    """
    scaled_width = round(constants.display_width * width_percentage)
    return scaled_width


def scale_height_percentage(height_percentage: float) -> int:
    """
    Description:
        Returns a height corresponding to height_percentage of the screen
    Input:
        float height_percentage: Screen height percentage
    Output:
        int: Scaled pixel height
    """
    scaled_height = round(constants.display_height * height_percentage)
    return scaled_height
