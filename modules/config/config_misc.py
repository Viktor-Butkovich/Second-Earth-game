from __future__ import annotations
from modules.constants import constants, status, flags
from modules.util import scaling, game_transitions, actor_utility
from modules.constructs import fonts
from modules.managers import (
    achievement_manager,
    actor_creation_manager,
    character_manager,
    help_manager,
    terrain_manager,
    notification_manager,
    supply_chain_request_engine,
)


def config_info_displays() -> None:
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


def config_misc() -> None:
    """
    Initializes object lists, current object variables, current status booleans, and other misc. values
    """
    constants.ActorCreationManager = actor_creation_manager.actor_creation_manager()
    constants.TerrainManager = terrain_manager.terrain_manager()

    constants.font_size = scaling.scale_height(constants.default_font_size)
    constants.notification_font_size = scaling.scale_height(
        constants.default_notification_font_size
    )

    constants.myfont = fonts.font(
        {
            "descriptor": constants.DEFAULT_FONT,
            "name": constants.small_font_name,
            "size": constants.font_size,
            "color": constants.COLOR_BLACK,
        }
    )
    fonts.font(
        {
            "descriptor": constants.WHITE_FONT,
            "name": constants.small_font_name,
            "size": constants.font_size,
            "color": constants.COLOR_WHITE,
        }
    )
    fonts.font(
        {
            "descriptor": constants.DEFAULT_NOTIFICATION_FONT,
            "name": constants.font_name,
            "size": constants.notification_font_size,
            "color": constants.COLOR_BLACK,
        }
    )
    fonts.font(
        {
            "descriptor": constants.WHITE_NOTIFICATION_FONT,
            "name": constants.font_name,
            "size": constants.notification_font_size,
            "color": constants.COLOR_WHITE,
        }
    )
    fonts.font(
        {
            "descriptor": constants.RED_FONT,
            "name": constants.font_name,
            "size": constants.font_size,
            "color": constants.COLOR_RED,
        }
    )
    fonts.font(
        {
            "descriptor": constants.BLUE_FONT,
            "name": constants.font_name,
            "size": constants.font_size,
            "color": constants.COLOR_ELECTRIC_BLUE,
        }
    )
    fonts.font(
        {
            "descriptor": constants.LARGE_NOTIFICATION_FONT,
            "name": constants.font_name,
            "size": scaling.scale_height(30),
            "color": constants.COLOR_BLACK,
        }
    )
    fonts.font(
        {
            "descriptor": constants.LARGE_WHITE_NOTIFICATION_FONT,
            "name": constants.font_name,
            "size": scaling.scale_height(30),
            "color": constants.COLOR_WHITE,
        }
    )
    fonts.font(
        {
            "descriptor": constants.MAX_DETAIL_WHITE_FONT,
            "name": "helvetica",
            "size": scaling.scale_height(100),
            "color": constants.COLOR_WHITE,
        }
    )
    fonts.font(
        {
            "descriptor": constants.MAX_DETAIL_BLACK_FONT,
            "name": "helvetica",
            "size": scaling.scale_height(100),
            "color": constants.COLOR_BLACK,
        }
    )

    # page 1
    instructions_message = "Placeholder instructions, use += to add"
    status.instructions_list.append(instructions_message)

    status.loading_image = constants.ActorCreationManager.create_interface_element(
        {
            "image_id": [
                {"image_id": "misc/screen_backgrounds/title.png", "detail_level": 1.0},
                {
                    "image_id": "misc/screen_backgrounds/loading.png",
                    "detail_level": 1.0,
                },
            ],
            "init_type": constants.LOADING_IMAGE_TEMPLATE_IMAGE,
        }
    )
    loading_screen_banner_width = 1400
    status.loading_screen_quote_banner = (
        constants.ActorCreationManager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(
                    constants.default_display_width / 2
                    - (loading_screen_banner_width // 2),
                    constants.default_display_height / 2 - 500,
                ),
                "ideal_width": scaling.scale_width(loading_screen_banner_width),
                "minimum_height": 50,
                "image_id": "misc/empty.png",
                "init_type": constants.MULTI_LINE_LABEL,
                "message": "Loading screen quote",
                "font": constants.fonts[constants.LARGE_WHITE_NOTIFICATION_FONT],
                "modes": [],
                "center_lines": True,
            }
        )
    )
    loading_screen_continue_message = "Press ENTER to continue"
    loading_screen_continue_message_width = constants.fonts[
        constants.LARGE_WHITE_NOTIFICATION_FONT
    ].pygame_font.size(loading_screen_continue_message)[0]
    status.loading_screen_continue_banner = (
        constants.ActorCreationManager.create_interface_element(
            {
                "coordinates": (
                    scaling.scale_width(constants.default_display_width / 2)
                    - loading_screen_continue_message_width / 2,
                    scaling.scale_height(constants.default_display_height / 2 - 500),
                ),
                "minimum_width": loading_screen_continue_message_width,
                "height": 50,
                "image_id": "misc/empty.png",
                "init_type": constants.LABEL,
                "message": loading_screen_continue_message,
                "font": constants.fonts[constants.LARGE_WHITE_NOTIFICATION_FONT],
                "modes": [],
            }
        )
    )

    strategic_background_image = (
        constants.ActorCreationManager.create_interface_element(
            {
                "modes": [
                    constants.STRATEGIC_MODE,
                    constants.EARTH_MODE,
                    constants.TRIAL_MODE,
                    constants.NEW_GAME_SETUP_MODE,
                ],
                "init_type": constants.BACKGROUND_IMAGE,
            }
        )
    )

    ministers_background_image = (
        constants.ActorCreationManager.create_interface_element(
            {
                "modes": [
                    constants.MINISTERS_MODE,
                ],
                "image_id": {
                    "image_id": "misc/screen_backgrounds/ministers_background.png",
                    "detail_level": 1.0,
                },
                "init_type": constants.BACKGROUND_IMAGE,
            }
        )
    )

    title_background_image = constants.ActorCreationManager.create_interface_element(
        {
            "modes": [
                constants.MAIN_MENU_MODE,
            ],
            "image_id": {
                "image_id": "misc/screen_backgrounds/title.png",
                "detail_level": 1.0,
            },
            "init_type": constants.BACKGROUND_IMAGE,
        }
    )

    status.safe_click_area = constants.ActorCreationManager.create_interface_element(
        {
            "width": constants.display_width / 2 + 25,
            "height": constants.display_height,
            "modes": [
                constants.STRATEGIC_MODE,
                constants.EARTH_MODE,
                constants.MINISTERS_MODE,
                constants.NEW_GAME_SETUP_MODE,
                # constants.LOCATION_MODE,
            ],
            "image_id": "misc/empty.png",
            "init_type": constants.SAFE_CLICK_PANEL_ELEMENT,
        }
    )

    for relative_coordinates in [
        (-1, -1),
        (0, -1),
        (1, -1),
        (-1, 0),
        (1, 0),
        (-1, 1),
        (0, 1),
        (1, 1),
    ]:
        status.focused_location_adjacent_images[relative_coordinates[0] + 1][
            relative_coordinates[1] + 1
        ] = constants.ActorCreationManager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(
                    constants.zone_grid_x
                    + ((constants.zone_grid_pixel_width - 1) * relative_coordinates[0]),
                    constants.zone_grid_y
                    + (
                        (constants.zone_grid_pixel_height - 1) * relative_coordinates[1]
                    ),
                ),
                "image_id": "misc/empty.png",
                "modes": [constants.LOCATION_MODE],
                "width": scaling.scale_width(constants.zone_grid_pixel_width),
                "height": scaling.scale_height(constants.zone_grid_pixel_height),
                "init_type": constants.FREE_IMAGE,
            }
        )
    location_mode_safe_click_area = (
        constants.ActorCreationManager.create_interface_element(
            {
                "width": constants.display_width / 2 + 25,
                "height": constants.display_height,
                "modes": [
                    constants.LOCATION_MODE,
                ],
                "image_id": "misc/safe_click_area.png",
                "init_type": constants.SAFE_CLICK_PANEL_ELEMENT,
            }
        )
    )
    # safe click area has empty image but is managed with panel to create correct behavior - its intended image is in the background image's bundle to blit more efficiently

    game_transitions.set_game_mode(constants.MAIN_MENU_MODE)

    constants.mouse_follower = constants.ActorCreationManager.create_interface_element(
        {"init_type": constants.MOUSE_FOLLOWER_IMAGE}
    )

    constants.SupplyChainRequestEngine = (
        supply_chain_request_engine.supply_chain_request_engine()
    )

    constants.NotificationManager = notification_manager.notification_manager()

    constants.AchievementManager = achievement_manager.achievement_manager()

    constants.CharacterManager = character_manager.character_manager()

    constants.HelpManager = help_manager.help_manager()

    status.grids_collection = constants.ActorCreationManager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(
                constants.grids_collection_x, constants.grids_collection_y
            ),
            "width": scaling.scale_width(0),
            "height": scaling.scale_height(0),
            "modes": [constants.STRATEGIC_MODE, constants.EARTH_MODE],
            "init_type": constants.INTERFACE_COLLECTION,
        }
    )

    north_indicator_image = constants.ActorCreationManager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, 0),
            "modes": [constants.STRATEGIC_MODE],
            "image_id": [
                {
                    "image_id": "misc/north_indicator.png",
                    "detail_level": 1.0,
                }
            ],
            "init_type": constants.DIRECTIONAL_INDICATOR_IMAGE,
            "anchor_key": "north_pole",
            "width": scaling.scale_width(25),
            "height": scaling.scale_height(25),
        }
    )

    south_indicator_image = constants.ActorCreationManager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, 0),
            "modes": [constants.STRATEGIC_MODE],
            "image_id": [
                {
                    "image_id": "misc/south_indicator.png",
                    "detail_level": 1.0,
                }
            ],
            "init_type": constants.DIRECTIONAL_INDICATOR_IMAGE,
            "anchor_key": "south_pole",
            "width": scaling.scale_width(25),
            "height": scaling.scale_height(25),
        }
    )
    # anchor = constants.ActorCreationManager.create_interface_element(
    #    {'width': 1, 'height': 1, 'init_type': 'interface element', 'parent_collection': status.info_displays_collection}
    # ) # rect at original location prevents collection from moving unintentionally when resizing
    actor_utility.reset_action_prices()
