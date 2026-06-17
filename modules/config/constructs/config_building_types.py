from __future__ import annotations
import pygame
from modules.constants import constants, status, flags
from modules.constructs import building_types


def config_building_types() -> None:
    """
    Defines building type templates
    """
    building_types.building_type(
        {
            "key": constants.SPACEPORT,
            "name": "spaceport",
            "description": [
                "A spaceport allows spaceships to land and launch, and expands the location's warehouse capacity."
            ],
            "warehouse_level": 1,
            "can_construct": True,
            "can_damage": True,
            "cost": 15,
            "attached_settlement": True,
            "build_keybind": pygame.K_p,
        }
    )
    # Add attrition modifiers
    # add upgrade types
