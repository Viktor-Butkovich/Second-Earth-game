from __future__ import annotations
import pygame
from modules.constants import constants, status, flags
from modules.constructs.actor_types import locations
from modules.constructs import buildings
from modules.util import drawing_utility, utility
from typing import Tuple, List, Any, Dict


class zone:
    """
    Represents an individual area within a location
    """

    def __init__(
        self, coordinates: Tuple[int, int], parent_location: locations.location
    ) -> None:
        """
        Description:
            Initializes this object
        Input:
            Tuple[int, int] coordinates: Coordinates of this zone within its parent location
            location parent_location: The location this zone lies within
        Output:
            None
        """
        self.x: int = coordinates[0]
        self.y: int = coordinates[1]
        self.parent_location: locations.location = parent_location
        self.actor_type: str = constants.ZONE_ACTOR_TYPE
        self.zone_buildings: List[buildings.building] = []

    def get_image_id_list(self) -> List[Dict[str, Any]]:
        """
        Description:
            Generates and returns a list of this zone's image IDs. Zones use a subsection of their parent location's rendered
                high-resolution image surface
        Input:
            None
        Output:
            Image ID list: List of image IDs for this zone (just a single pre-rendered surface for zones)
        """
        if self.parent_location == status.location_mode_focus:
            image_id_list = [
                {
                    "image_id": drawing_utility.get_subsurface(
                        status.focused_location_surface,
                        constants.zone_grid_coordinate_size,
                        (self.x, self.y),
                    )
                }
            ]
            if self.has_zone_surface():
                image_id_list.append({"image_id": self.get_zone_surface()})
            return image_id_list
        else:
            return [{"image_id": "misc/empty.png"}]

    def has_zone_surface(self) -> bool:
        return bool(self.zone_buildings)

    def get_zone_surface(self) -> pygame.Surface:
        return drawing_utility.image_id_to_surface(
            utility.combine(
                *[building.get_image_id_list() for building in self.zone_buildings]
            )
        )

    @property
    def batch_tooltip_list(self) -> List[List[str]]:
        """
        Gets a 2D list of strings to use as this object's tooltip
            Each string is displayed on a separate line, while each sublist is displayed in a separate box
        """
        return [self.tooltip_text]

    @property
    def tooltip_text(self) -> List[str]:
        """
        Provides the tooltip for this object
        """
        tooltip_message = [f"Placeholder Zone Tooltip ({self.x}, {self.y})"]
        return tooltip_message

    def add_building(self, building: buildings.building) -> None:
        self.zone_buildings.append(building)
        self.parent_location.zones_with_surfaces.add(self)
        if not building.building_type.key in self.parent_location.contained_buildings:
            self.parent_location.contained_buildings[building.building_type.key] = []
        self.parent_location.contained_buildings[building.building_type.key].append(
            building
        )
        constants.EventBus.subscribe(
            self.parent_location.update_image_bundle,
            building.uuid,
            constants.BUILDING_SET_DAMAGED_ROUTE,
        )  # Update location image bundle when building's damaged status changes
        self.parent_location.publish_events(constants.LOCATION_ADD_BUILDING_ROUTE)
