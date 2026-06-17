from __future__ import annotations
import pygame
from modules.constants import constants, status, flags
from modules.util import scaling, actor_utility


def config_temperature_breakdown_tab():
    """
    Initializes the temperature breakdown tab as part of the location tabbed collection
    """
    status.temperature_breakdown_collection = (
        constants.ActorCreationManager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(0, 0),
                "width": scaling.scale_width(0),
                "height": scaling.scale_height(0),
                "init_type": constants.ORDERED_COLLECTION,
                "parent_collection": status.location_tabbed_collection,
                "member_config": {
                    "tabbed": True,
                    "button_image_id": actor_utility.generate_frame(
                        "misc/map_modes/temperature.png"
                    ),
                    "identifier": constants.TEMPERATURE_BREAKDOWN_PANEL,
                    "tab_name": "temperature breakdown",
                },
            }
        )
    )

    for current_actor_label_type in [
        constants.BANNER_LABEL,
        constants.TOTAL_HEAT_LABEL,
        constants.INSOLATION_LABEL,
        constants.STAR_DISTANCE_LABEL,
        constants.GHG_EFFECT_LABEL,
        constants.WATER_VAPOR_EFFECT_LABEL,
        constants.ALBEDO_EFFECT_LABEL,
        constants.AVERAGE_TEMPERATURE_LABEL,
    ]:
        if current_actor_label_type in [
            constants.AVERAGE_TEMPERATURE_LABEL,
            constants.BANNER_LABEL,
            constants.TOTAL_HEAT_LABEL,
        ]:
            x_displacement = 0
        elif current_actor_label_type in [constants.STAR_DISTANCE_LABEL]:
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
            "parent_collection": status.temperature_breakdown_collection,
            "member_config": {"order_x_offset": scaling.scale_width(x_displacement)},
        }
        if current_actor_label_type == constants.BANNER_LABEL:
            input_dict["banner_type"] = constants.ABSOLUTE_ZERO_BANNER
            input_dict["banner_text"] = f"Absolute zero: {constants.ABSOLUTE_ZERO} °F"
        constants.ActorCreationManager.create_interface_element(input_dict)
