# Contains functions that manage the display of images

from __future__ import annotations
import pygame
from typing import Tuple, Dict, Any, List
from modules.constants import constants, status, flags


def rect_to_surface(rect: pygame.Rect) -> pygame.Surface:
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


def display_image(image: pygame.Surface, x: int, y: int) -> None:
    """
    Description:
        Draws the inputted image at the inputted coordinates
    Input:
        pygame.Surface image: Image to be displayed
        int x: Pixel x coordinate at which to display the image
        int y: Pixel y coordinate at which to display the image
    Output:
        None
    """
    constants.game_display.blit(image, (x, y))


def display_image_angle(image: pygame.Surface, x: int, y: int, angle: int) -> None:
    """
    Description:
        Draws the inputted image at the inputted coordinates tilted at the inputted angle
    Input:
        pygame.Surface image: Image to be displayed
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


def cached_surfaces_memory() -> float:
    """
    Calculates and returns the total memory size of cached images in MB
    """
    total_bytes = 0
    for surface in status.cached_images.values():
        width, height = surface.get_size()
        bytes_per_pixel = surface.get_bytesize()
        total_bytes += width * height * bytes_per_pixel
    return total_bytes / (1024 * 1024)


def get_subsurface(
    surface: pygame.Surface, grid_size: int, target_coords: Tuple[int, int]
) -> pygame.Surface:
    """
    Description:
        Extracts a sub-rect from the input surface as if it were divided into a grid.
    Inputs:
        pygame.Surface surface: The source surface.
        int grid_size: width and height of the grid.
        Tuple[int, int] target_coords: (target_x, target_y) coordinates in the grid.
    Outputs:
        pygame.Surface: The subsurface corresponding to the grid cell.
    """
    pixel_width = surface.get_size()[0] // grid_size
    pixel_height = surface.get_size()[1] // grid_size
    return surface.subsurface(
        pygame.Rect(
            target_coords[0] * pixel_width,
            (grid_size - 1 - target_coords[1]) * pixel_height,
            pixel_width,
            pixel_height,
        )
    )


def compose_surface(
    grid_size: int, pixel_size: Tuple[int, int], *args
) -> pygame.Surface:

    # Create the blank output surface
    out_surface = pygame.Surface(
        pixel_size, pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SRCALPHA
    )
    out_surface.fill((0, 0, 0, 0))  # Fill with transparent color

    cell_width = pixel_size[0] // grid_size
    cell_height = pixel_size[1] // grid_size

    idx = 0
    for item in args:
        surf = pygame.transform.scale(item["surface"], ((cell_width, cell_height)))
        pygame.image.save(surf, f"debug_surface_{idx}.png")
        idx += 1
        x, y = item["coords"]

        draw_x = x * cell_width
        draw_y = (grid_size - 1 - y) * cell_height

        # Blit the small surface into the correct cell
        out_surface.blit(surf, (draw_x, draw_y))
    pygame.image.save(out_surface, "debug_composed_surface.png")
    return out_surface


def image_id_to_surface(image_id: List[Dict[str, Any]]) -> pygame.Surface:
    """
    Description:
        Converts an image ID list to a pygame Surface
    Input:
        List[Dict[str, Any]] image_id: Image ID list to convert
    Output:
        pygame.Surface: Corresponding pygame Surface
    """
    status.dummy_surface_image.set_image(image_id)
    return status.dummy_surface_image.image
