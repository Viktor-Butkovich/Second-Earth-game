# Contains utilities for rendering synthetic surfaces

from __future__ import annotations
import pygame
from typing import Tuple
from modules.constants import constants, status, flags


def render_outline(
    width: int, height: int, color: Tuple[int, int, int], outline_width: int
) -> pygame.Surface:
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(surface, color, surface.get_rect(), outline_width)
    return surface
