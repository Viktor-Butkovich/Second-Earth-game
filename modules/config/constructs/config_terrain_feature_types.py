from __future__ import annotations
from modules.constants import constants, status, flags
from modules.constructs import terrain_feature_types
from modules.util import actor_utility


def config_terrain_feature_types() -> None:
    """
    Defines terrain feature type templates
    """
    terrain_feature_types.terrain_feature_type(
        {
            "terrain_feature_type": "north pole",
            "image_id": {
                "image_id": "misc/north_indicator.png",
                "size": 25
                / (
                    constants.minimap_grid_pixel_width
                    / constants.minimap_grid_coordinate_size
                ),
                "level": constants.OVERLAY_ICON_LEVEL,
            },  # Scales to 25x25 pixels in the minimap grid - minimap cells are 750 pixels total / 7 cells = 107.14 pixels
            "display_type": constants.MINIMAP_OVERLAY_TERRAIN_FEATURE,
            "description": ["North pole of the planet"],
            "tracking_type": constants.UNIQUE_FEATURE_TRACKING,
        }
    )

    terrain_feature_types.terrain_feature_type(
        {
            "terrain_feature_type": "south pole",
            "image_id": {
                "image_id": "misc/south_indicator.png",
                "size": 25
                / (
                    constants.minimap_grid_pixel_width
                    / constants.minimap_grid_coordinate_size
                ),
                "level": constants.OVERLAY_ICON_LEVEL,
            },  # Scales to 25x25 pixels in the minimap grid - minimap cells are 750 pixels total / 7 cells = 107.14 pixels
            "display_type": constants.MINIMAP_OVERLAY_TERRAIN_FEATURE,
            "description": ["South pole of the planet"],
            "tracking_type": constants.UNIQUE_FEATURE_TRACKING,
        }
    )

    terrain_feature_types.terrain_feature_type(
        {
            "terrain_feature_type": "equator",
            "image_id": "misc/empty.png",
            "description": ["Lies along the equator of the planet"],
            "tracking_type": constants.LIST_FEATURE_TRACKING,
            "visible": False,
        }
    )
    terrain_feature_types.terrain_feature_type(
        {
            "terrain_feature_type": "northern tropic",
            "image_id": actor_utility.generate_label_image_id(
                "Northern Tropic",
                y_offset=-0.75,
            ),
            "display_type": constants.MINIMAP_OVERLAY_TERRAIN_FEATURE,
            "description": ["Lies along the northern edge of the equatorial zone"],
        }
    )
    terrain_feature_types.terrain_feature_type(
        {
            "terrain_feature_type": "southern tropic",
            "image_id": actor_utility.generate_label_image_id(
                "Southern Tropic",
                y_offset=-0.75,
            ),
            "display_type": constants.MINIMAP_OVERLAY_TERRAIN_FEATURE,
            "description": ["Lies along the southern edge of the equatorial zone"],
        }
    )
