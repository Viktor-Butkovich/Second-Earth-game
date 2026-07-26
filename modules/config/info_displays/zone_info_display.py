from __future__ import annotations
from modules.constants import constants, status, flags
from modules.util import scaling, actor_utility


def config_zone_info_display() -> None:
    """
    Initializes zone selection interface for zones within a location
    """
    status.zone_info_display = constants.ActorCreationManager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, -400),
            "width": scaling.scale_width(775),
            "height": scaling.scale_height(10),
            "modes": [
                constants.LOCATION_MODE,
            ],
            "init_type": constants.ORDERED_COLLECTION,
            "is_info_display": True,
            "actor_type": constants.ZONE_ACTOR_TYPE,
            "description": "zone information panel",
            "parent_collection": status.info_displays_collection,
            "member_config": {
                "order_exempt": True,
            },
        }
    )
    free_unfocus_location_button = (
        constants.ActorCreationManager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(
                    750 - (5 + constants.earth_grid_width), 10
                ),
                "width": scaling.scale_width(constants.earth_grid_width),
                "height": scaling.scale_height(constants.earth_grid_width),
                "image_id": actor_utility.generate_frame(
                    "buttons/unmagnify_button.png",
                    background="buttons/default_button_frameless.png",
                ),
                "init_type": constants.UNFOCUS_LOCATION_BUTTON,
                "modes": [constants.LOCATION_MODE],
            }
        )
    )

    zone_icon = constants.ActorCreationManager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, 0),
            "actor_type": constants.ZONE_ACTOR_TYPE,
            "width": scaling.scale_width(constants.actor_icon_dimensions),
            "height": scaling.scale_height(constants.actor_icon_dimensions),
            "init_type": constants.ACTOR_ICON,
            "parent_collection": status.zone_info_display,
        }
    )
    zone_actor_label_input_dict = {
        "minimum_width": scaling.scale_width(10),
        "height": scaling.scale_height(constants.default_notification_font_size + 5),
        "image_id": "misc/default_label.png",
        "actor_type": constants.ZONE_ACTOR_TYPE,
        "parent_collection": status.zone_info_display,
    }
    # location info labels setup
    for current_actor_label_type in [
        constants.ZONE_COORDINATES_LABEL,
    ]:
        x_displacement = 0
        constants.ActorCreationManager.create_interface_element(
            {
                **zone_actor_label_input_dict,
                "init_type": current_actor_label_type,
                "member_config": {
                    "order_x_offset": scaling.scale_width(x_displacement)
                },
            }
        )
