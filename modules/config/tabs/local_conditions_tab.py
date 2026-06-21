from __future__ import annotations
import pygame
from modules.constants import constants, status, flags
from modules.util import scaling


def config_local_conditions_tab():
    """
    Initializes the local conditions tab as part of the location tabbed collection
    """
    status.local_conditions_collection = (
        constants.ActorCreationManager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(0, 0),
                "width": scaling.scale_width(0),
                "height": scaling.scale_height(0),
                "init_type": constants.ORDERED_COLLECTION,
                "parent_collection": status.location_tabbed_collection,
                "member_config": {
                    "tabbed": True,
                    "button_image_id": "misc/empty.png",
                    "identifier": constants.LOCAL_CONDITIONS_PANEL,
                    "tab_name": "local conditions",
                },
            }
        )
    )

    for current_actor_label_type in [
        constants.KNOWLEDGE_LABEL,
        constants.TERRAIN_LABEL,
        constants.BANNER_LABEL,
        constants.WATER_LABEL,
        constants.TEMPERATURE_LABEL,
        constants.LOCAL_AVERAGE_TEMPERATURE_LABEL,
        constants.VEGETATION_LABEL,
        constants.ROUGHNESS_LABEL,
        constants.SOIL_LABEL,
        constants.ALTITUDE_LABEL,
        constants.HABITABILITY_LABEL,
    ]:
        if current_actor_label_type in [
            constants.KNOWLEDGE_LABEL,
            constants.HABITABILITY_LABEL,
        ]:
            x_displacement = 0
        elif current_actor_label_type == constants.LOCAL_AVERAGE_TEMPERATURE_LABEL:
            x_displacement = 50
        else:
            x_displacement = 25
        input_dict = {
            "minimum_width": scaling.scale_width(10),
            "height": scaling.scale_height(
                constants.default_notification_font_size + 5
            ),
            "image_id": "misc/default_label.png",
            "init_type": current_actor_label_type,
            "actor_type": constants.LOCATION_ACTOR_TYPE,
            "parent_collection": status.local_conditions_collection,
            "member_config": {"order_x_offset": scaling.scale_width(x_displacement)},
        }
        if current_actor_label_type == constants.BANNER_LABEL:
            input_dict["banner_type"] = constants.TERRAIN_DETAILS_BANNER
            input_dict["banner_text"] = "Details unknown"
        constants.ActorCreationManager.create_interface_element(input_dict)

        status.albedo_free_image = (
            constants.ActorCreationManager.create_interface_element(
                {
                    "coordinates": (0, 200),
                    "image_id": "misc/empty.png",
                    "modes": [],
                    "width": 2,
                    "height": 2,
                    "init_type": constants.FREE_IMAGE,
                }
            )
        )
