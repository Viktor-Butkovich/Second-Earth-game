from __future__ import annotations
import pygame
from modules.constants import constants, status, flags
from modules.util import scaling


def config_mob_info_display() -> None:
    """
    Initializes mob selection interface
    """
    actor_display_top_y = constants.default_display_height - 205 + 125 + 10
    actor_display_current_y = actor_display_top_y
    constants.mob_ordered_list_start_y = actor_display_current_y

    status.mob_info_display = constants.ActorCreationManager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, -400),
            "width": scaling.scale_width(400),
            "height": scaling.scale_height(430),
            "modes": [
                constants.STRATEGIC_MODE,
                constants.EARTH_MODE,
                constants.LOCATION_MODE,
            ],
            "init_type": constants.ORDERED_COLLECTION,
            "is_info_display": True,
            "actor_type": constants.MOB_ACTOR_TYPE,
            "description": "unit information panel",
            "parent_collection": status.info_displays_collection,
            "member_config": {
                "order_exempt": True,
            },
        }
    )

    tab_collection_relative_coordinates = (420, -30)
    status.mob_tabbed_collection = (
        constants.ActorCreationManager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(
                    tab_collection_relative_coordinates[0],
                    tab_collection_relative_coordinates[1],
                ),
                "width": scaling.scale_width(0),
                "height": scaling.scale_height(0),
                "init_type": constants.TABBED_COLLECTION,
                "parent_collection": status.mob_info_display,
                "member_config": {"order_exempt": True},
                "description": "unit information tabs",
            }
        )
    )
    mob_icon = constants.ActorCreationManager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, 0),
            "actor_type": constants.MOB_ACTOR_TYPE,
            "width": scaling.scale_width(constants.actor_icon_dimensions),
            "height": scaling.scale_height(constants.actor_icon_dimensions),
            "init_type": constants.ACTOR_ICON,
            "parent_collection": status.mob_info_display,
        }
    )

    fire_unit_button = constants.ActorCreationManager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(
                constants.actor_icon_dimensions + 5,
                -1 * constants.actor_icon_dimensions,
            ),
            "width": scaling.scale_width(35),
            "height": scaling.scale_height(35),
            "image_id": "buttons/fire_minister_button.png",
            "init_type": constants.FIRE_UNIT_BUTTON,
            "parent_collection": status.mob_info_display,
            "member_config": {"order_exempt": True},
        }
    )

    for parameters in [
        {
            "coordinates": scaling.scale_coordinates(200, -105),
            "keybind_id": pygame.K_a,
            "image_id": "buttons/left_button.png",
            "init_type": constants.MOVE_LEFT_BUTTON,
        },
        {
            "coordinates": scaling.scale_coordinates(245, -105),
            "keybind_id": pygame.K_s,
            "image_id": "buttons/down_button.png",
            "init_type": constants.MOVE_DOWN_BUTTON,
        },
        {
            "coordinates": scaling.scale_coordinates(245, -60),
            "keybind_id": pygame.K_w,
            "image_id": "buttons/up_button.png",
            "init_type": constants.MOVE_UP_BUTTON,
        },
        {
            "coordinates": scaling.scale_coordinates(290, -105),
            "keybind_id": pygame.K_d,
            "image_id": "buttons/right_button.png",
            "init_type": constants.MOVE_RIGHT_BUTTON,
        },
    ]:
        constants.ActorCreationManager.create_interface_element(
            {
                "width": scaling.scale_width(40),
                "height": scaling.scale_height(40),
                "parent_collection": status.mob_info_display,
                "modes": [constants.STRATEGIC_MODE],
                "member_config": {"order_exempt": True},
                **parameters,
            }
        )

    # mob info labels setup
    for current_actor_label_type in [
        constants.UNIT_TYPE_LABEL,
        constants.OFFICER_NAME_LABEL,
        constants.MINISTER_LABEL,
        constants.OFFICER_LABEL,
        constants.GROUP_NAME_LABEL,
        constants.WORKERS_LABEL,
        constants.MOVEMENT_LABEL,
        constants.EQUIPMENT_LABEL,
        constants.BANNER_LABEL,
        constants.ATTITUDE_LABEL,
        constants.CONTROLLABLE_LABEL,
        constants.CREW_LABEL,
        constants.PASSENGERS_LABEL,
        constants.CURRENT_PASSENGER_LABEL,
    ]:
        if (
            current_actor_label_type == constants.MINISTER_LABEL
        ):  # how far from edge of screen
            x_displacement = 40
        elif current_actor_label_type in [
            constants.CURRENT_PASSENGER_LABEL,
            constants.GROUP_NAME_LABEL,
        ]:
            x_displacement = 30
        else:
            x_displacement = 0
        input_dict = {  # should declare here to reinitialize dict and prevent extra parameters from being incorrectly retained between iterations
            "minimum_width": scaling.scale_width(10),
            "height": scaling.scale_height(
                constants.default_notification_font_size + 5
            ),
            "image_id": [{"image_id": "misc/default_label.png"}],
            "init_type": current_actor_label_type,
            "actor_type": constants.MOB_ACTOR_TYPE,
            "parent_collection": status.mob_info_display,
            "member_config": {"order_x_offset": x_displacement},
        }
        if current_actor_label_type == constants.BANNER_LABEL:
            input_dict["banner_type"] = constants.DEADLY_CONDITIONS_BANNER
            input_dict["banner_text"] = "Deadly conditions - will die at end of turn"

        if current_actor_label_type == constants.CURRENT_PASSENGER_LABEL:
            input_dict["list_type"] = constants.SPACESHIP_PERMISSION
            for i in range(0, 3):  # 0, 1, 2
                # label for each passenger
                input_dict["list_index"] = i
                constants.ActorCreationManager.create_interface_element(input_dict)
        else:
            constants.ActorCreationManager.create_interface_element(input_dict)
