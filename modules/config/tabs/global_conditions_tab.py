from __future__ import annotations
import pygame
from modules.constants import constants, status, flags
from modules.util import scaling


def config_global_conditions_tab() -> None:
    """
    Initializes the global conditions tab as part of the location tabbed collection
    """
    status.global_conditions_collection = (
        constants.ActorCreationManager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(0, 0),
                "width": scaling.scale_width(0),
                "height": scaling.scale_height(0),
                "init_type": constants.ORDERED_COLLECTION,
                "parent_collection": status.location_tabbed_collection,
                "member_config": {
                    "tabbed": True,
                    "button_image_id": "misc/empty.png",  # Filled by other functions
                    "identifier": constants.GLOBAL_CONDITIONS_PANEL,
                    "tab_name": "global conditions",
                },
            }
        )
    )

    for current_actor_label_type in [
        constants.PRESSURE_LABEL,
        constants.OXYGEN_LABEL,
        constants.GHG_LABEL,
        constants.INERT_GASES_LABEL,
        constants.TOXIC_GASES_LABEL,
        constants.AVERAGE_WATER_LABEL,
        constants.AVERAGE_TEMPERATURE_LABEL,
        constants.GRAVITY_LABEL,
        constants.RADIATION_LABEL,
        constants.MAGNETIC_FIELD_LABEL,
    ]:
        if current_actor_label_type in [
            constants.OXYGEN_LABEL,
            constants.GHG_LABEL,
            constants.INERT_GASES_LABEL,
            constants.TOXIC_GASES_LABEL,
        ]:
            x_displacement = 25
        else:
            x_displacement = 0
        input_dict = {
            "minimum_width": scaling.scale_width(10),
            "height": scaling.scale_height(
                constants.default_notification_font_size + 5
            ),
            "image_id": "misc/default_label.png",
            "init_type": current_actor_label_type,
            "actor_type": constants.LOCATION_ACTOR_TYPE,
            "parent_collection": status.global_conditions_collection,
            "member_config": {"order_x_offset": scaling.scale_width(x_displacement)},
        }
        constants.ActorCreationManager.create_interface_element(input_dict)
