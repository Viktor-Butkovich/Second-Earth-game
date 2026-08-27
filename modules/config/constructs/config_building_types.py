from __future__ import annotations
import pygame
from modules.constants import constants, status, flags, dataclasses
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
            "attached_settlement": True,
            "build_keybind": pygame.K_p,
            "cost_per_attempt": dataclasses.material_cost(
                base_metals=0.2,
                building_materials=1.2,
                advanced_metals=0.05,
                chemicals=0.05,
            ),
            "required_successes": 3,
        }
    )
