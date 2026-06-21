from __future__ import annotations
from modules.constants import constants, status, flags
from modules.util import scaling, actor_utility


def config_location_info_display() -> None:
    """
    Initializes location selection interface
    """
    status.location_info_display = (
        constants.ActorCreationManager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(0, 0),  # (0, -400),
                "width": scaling.scale_width(775),
                "height": scaling.scale_height(10),
                "modes": [
                    constants.STRATEGIC_MODE,
                    constants.EARTH_MODE,
                    constants.LOCATION_MODE,
                ],
                "init_type": constants.ORDERED_COLLECTION,
                "is_info_display": True,
                "actor_type": constants.LOCATION_ACTOR_TYPE,
                "description": "location information panel",
                "parent_collection": status.info_displays_collection,
            }
        )
    )

    separation = scaling.scale_height(3)
    same_location_ordered_collection = (
        constants.ActorCreationManager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(
                    constants.actor_icon_dimensions + 5, 0
                ),
                "width": 10,
                "height": 10,
                "init_type": constants.ORDERED_COLLECTION,
                "parent_collection": status.location_info_display,
                "member_config": {"order_exempt": True},
                "separation": separation,
            }
        )
    )

    for i in range(0, 4):  # Add button to cycle through
        constants.ActorCreationManager.create_interface_element(
            {
                "coordinates": (0, 0),
                "width": scaling.scale_width(25),
                "height": scaling.scale_height(25),
                "init_type": constants.SAME_LOCATION_ICON,
                "image_id": "buttons/default_button.png",
                "is_last": False,
                "parent_collection": same_location_ordered_collection,
                "index": i,
                "is_last": i == 3,
            }
        )

    cycle_same_location_button = (
        constants.ActorCreationManager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(0, separation),
                "width": scaling.scale_width(25),
                "height": scaling.scale_height(15),
                "image_id": actor_utility.generate_frame("buttons/cycle_passengers_down_button.png", background="buttons/default_button_frameless.png"),
                "init_type": constants.CYCLE_SAME_LOCATION_BUTTON,
                "parent_collection": same_location_ordered_collection,
            }
        )
    )

    location_icon = constants.ActorCreationManager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, 0),
            "actor_type": constants.LOCATION_ACTOR_TYPE,
            "width": scaling.scale_width(constants.actor_icon_dimensions),
            "height": scaling.scale_height(constants.actor_icon_dimensions),
            "init_type": constants.ACTOR_ICON,
            "parent_collection": status.location_info_display,
        }
    )

    location_actor_label_input_dict = {
        "minimum_width": scaling.scale_width(10),
        "height": scaling.scale_height(constants.default_notification_font_size + 5),
        "image_id": "misc/default_label.png",
        "actor_type": constants.LOCATION_ACTOR_TYPE,
        "parent_collection": status.location_info_display,
    }
    # location info labels setup
    for current_actor_label_type in [
        constants.COORDINATES_LABEL,
        constants.TERRAIN_LABEL,
        constants.PLANET_NAME_LABEL,
        constants.RESOURCE_LABEL,
        constants.TERRAIN_FEATURE_LABEL,
        constants.HABITABILITY_LABEL,
    ]:
        x_displacement = 0

        if current_actor_label_type == constants.TERRAIN_FEATURE_LABEL:
            for key, terrain_feature_type in status.terrain_feature_types.items():
                if terrain_feature_type.visible:
                    constants.ActorCreationManager.create_interface_element(
                        {
                            **location_actor_label_input_dict,
                            "init_type": constants.TERRAIN_FEATURE_LABEL,
                            "terrain_feature_type": key,
                            "member_config": {
                                "order_x_offset": scaling.scale_width(x_displacement)
                            },
                        }
                    )
        else:
            constants.ActorCreationManager.create_interface_element(
                {
                    **location_actor_label_input_dict,
                    "init_type": current_actor_label_type,
                    "member_config": {
                        "order_x_offset": scaling.scale_width(x_displacement)
                    },
                }
            )

    tab_collection_relative_coordinates = (420, -30)

    status.location_tabbed_collection = (
        constants.ActorCreationManager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(
                    tab_collection_relative_coordinates[0],
                    tab_collection_relative_coordinates[1],
                ),
                "width": scaling.scale_width(0),
                "height": scaling.scale_height(0),
                "init_type": constants.TABBED_COLLECTION,
                "parent_collection": status.location_info_display,
                "member_config": {"order_exempt": True},
                "description": "location information tabs",
            }
        )
    )
