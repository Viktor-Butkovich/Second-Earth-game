from __future__ import annotations
import pygame
from modules.constants import constants, status, flags
from modules.util import scaling, actor_utility


def config_ministers_screen() -> None:
    """
    Initializes static interface of ministers screen
    """
    # Minister table setup
    table_width = 400
    table_height = 750
    constants.ActorCreationManager.create_interface_element(
        {
            "image_id": "misc/minister_table.png",
            "coordinates": scaling.scale_coordinates(
                (constants.default_display_width / 2) - (table_width / 2), 55
            ),
            "width": scaling.scale_width(table_width),
            "height": scaling.scale_height(table_height),
            "modes": [constants.MINISTERS_MODE],
            "init_type": constants.FREE_IMAGE,
        }
    )

    position_icon_width = 75
    portrait_icon_width = 125
    input_dict = {
        "width": scaling.scale_width(portrait_icon_width),
        "height": scaling.scale_height(portrait_icon_width),
        "modes": [constants.MINISTERS_MODE],
        "init_type": constants.MINISTER_TABLE_ICON,
    }
    for current_index, minister_type_tuple in enumerate(status.minister_types.items()):
        # Creates an office icon and a portrait at a section of the table for each minister
        key, minister_type = minister_type_tuple
        if current_index <= 3:  # left side
            constants.ActorCreationManager.create_interface_element(
                {
                    "coordinates": scaling.scale_coordinates(
                        (constants.default_display_width / 2) - (table_width / 2) + 10,
                        current_index * 180
                        + 95
                        + (portrait_icon_width / 2 - position_icon_width / 2),
                    ),
                    "width": scaling.scale_width(position_icon_width),
                    "height": scaling.scale_height(position_icon_width),
                    "modes": [constants.MINISTERS_MODE],
                    "init_type": constants.TOOLTIP_FREE_IMAGE,
                    "image_id": [
                        {"image_id": f"ministers/icons/{minister_type.skill_type}.png"}
                    ],
                    "preset_tooltip_text": minister_type.get_description(),
                }
            )
            constants.ActorCreationManager.create_interface_element(
                {
                    **input_dict,
                    "coordinates": scaling.scale_coordinates(
                        (constants.default_display_width / 2)
                        - (table_width / 2)
                        - portrait_icon_width
                        - 10,
                        current_index * 180 + 95,
                    ),
                    "minister_type": minister_type,
                    "actor_type": constants.MINISTER_ACTOR_TYPE,
                    "image_id": [
                        {
                            "image_id": "ministers/portraits/frame/frame.png",
                            "level": constants.BACKGROUND_LEVEL,
                        },
                        {
                            "image_id": "misc/warning_icon.png",
                            "level": constants.DEFAULT_PORTRAIT_LEVEL,
                        },
                    ],
                }
            )

        else:
            constants.ActorCreationManager.create_interface_element(
                {
                    "coordinates": scaling.scale_coordinates(
                        (constants.default_display_width / 2)
                        + (table_width / 2)
                        - position_icon_width
                        - 10,
                        (current_index - 4) * 180
                        + 95
                        + (portrait_icon_width / 2 - position_icon_width / 2),
                    ),
                    "width": scaling.scale_width(position_icon_width),
                    "height": scaling.scale_height(position_icon_width),
                    "modes": [constants.MINISTERS_MODE],
                    "init_type": constants.TOOLTIP_FREE_IMAGE,
                    "image_id": [
                        {"image_id": f"ministers/icons/{minister_type.skill_type}.png"}
                    ],
                    "preset_tooltip_text": minister_type.get_description(),
                }
            )
            constants.ActorCreationManager.create_interface_element(
                {
                    **input_dict,
                    "coordinates": scaling.scale_coordinates(
                        (constants.default_display_width / 2) + (table_width / 2) + 10,
                        (current_index - 4) * 180 + 95,
                    ),
                    "minister_type": minister_type,
                    "actor_type": constants.MINISTER_ACTOR_TYPE,
                    "image_id": [
                        {
                            "image_id": "ministers/portraits/frame/frame.png",
                            "level": constants.BACKGROUND_LEVEL,
                        },
                        {
                            "image_id": "misc/warning_icon.png",
                            "level": constants.DEFAULT_PORTRAIT_LEVEL,
                        },
                    ],
                }
            )

    available_minister_display_x = constants.default_display_width - 205
    available_minister_display_y = 770
    cycle_input_dict = {
        "coordinates": scaling.scale_coordinates(
            available_minister_display_x - (position_icon_width / 2) - 50,
            available_minister_display_y,
        ),
        "width": scaling.scale_width(50),
        "height": scaling.scale_height(50),
        "keybind_id": pygame.K_w,
        "modes": [constants.MINISTERS_MODE],
        "image_id": actor_utility.generate_frame("buttons/cycle_ministers_up_button.png", background="buttons/default_button_frameless.png"),
        "init_type": constants.CYCLE_AVAILABLE_MINISTERS_BUTTON,
        "direction": "left",
    }
    cycle_left_button = constants.ActorCreationManager.create_interface_element(
        cycle_input_dict
    )

    for i in range(0, 5):
        available_minister_display_y -= portrait_icon_width + 10
        current_portrait = constants.ActorCreationManager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(
                    available_minister_display_x - portrait_icon_width,
                    available_minister_display_y,
                ),
                "width": scaling.scale_width(portrait_icon_width),
                "height": scaling.scale_height(portrait_icon_width),
                "modes": [constants.MINISTERS_MODE],
                "init_type": constants.AVAILABLE_MINISTER_ICON,
                "actor_type": constants.MINISTER_ACTOR_TYPE,
                "image_id": [
                    {
                        "image_id": "misc/actor_backgrounds/minister_background.png",
                        "level": constants.BACKGROUND_LEVEL,
                    },
                    {
                        "image_id": "ministers/portraits/frame/frame.png",
                        "level": constants.BACKGROUND_LEVEL,
                    },
                ],
                "minister_type": "none",
                "enable_shader": i
                == 2,  # Only enable shader for middle portrait (when minister just appointed)
            }
        )

    available_minister_display_y -= 60
    cycle_right_button = constants.ActorCreationManager.create_interface_element(
        {
            **cycle_input_dict,
            "coordinates": (
                cycle_input_dict["coordinates"][0],
                scaling.scale_height(available_minister_display_y),
            ),
            "keybind_id": pygame.K_s,
            "image_id": actor_utility.generate_frame("buttons/cycle_ministers_down_button.png", background="buttons/default_button_frameless.png"),
            "direction": "right",
        }
    )

    status.minister_loading_image = constants.ActorCreationManager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, 0),
            "width": scaling.scale_width(portrait_icon_width),
            "height": scaling.scale_height(portrait_icon_width),
            "modes": [],
            "actor_type": constants.MINISTER_ACTOR_TYPE,
            "init_type": constants.ACTOR_ICON,
        }
    )  # Dummy image to calibrate all ministers to, ensuring portrait images are rendered and cached at creation time
