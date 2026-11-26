from __future__ import annotations
from modules.constants import constants, status, flags
from modules.util import scaling


def config_info_displays_collection() -> None:
    """
    Initializes info displays collection (must be run after new game setup is created for correct layering)
    """
    status.info_displays_collection = (
        constants.ActorCreationManager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(
                    5, constants.default_display_height - 205 + 125 - 5
                ),
                "width": scaling.scale_width(10),
                "height": scaling.scale_height(10),
                "modes": [
                    constants.STRATEGIC_MODE,
                    constants.EARTH_MODE,
                    constants.MINISTERS_MODE,
                    constants.NEW_GAME_SETUP_MODE,
                    constants.LOCATION_MODE,
                ],
                "init_type": constants.ORDERED_COLLECTION,
                "description": "general information panel",
            }
        )
    )
