from __future__ import annotations
import pygame
from modules.constants import constants, status, flags
from modules.util import scaling, actor_utility, world_utility, text_utility


def config_buttons() -> None:
    """
    Initializes static buttons
    """
    status.planet_view_mask = constants.ActorCreationManager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(
                constants.strategic_map_x_offset, constants.strategic_map_y_offset
            ),
            "width": scaling.scale_width(constants.strategic_map_pixel_width),
            "height": scaling.scale_height(constants.strategic_map_pixel_height),
            "parent_collection": status.grids_collection,
            "modes": [
                constants.STRATEGIC_MODE
            ],  # Manually drawn by scrolling strategic grid
            "init_type": constants.FREE_IMAGE,
            "color_key": (255, 255, 255),
            "image_id": "misc/planet_view_mask.png",
        }
    )

    if constants.EffectManager.effect_active("map_customization"):
        north_pole_centered_earth = (
            constants.ActorCreationManager.create_interface_element(
                {
                    "coordinates": scaling.scale_coordinates(
                        constants.strategic_map_x_offset,
                        constants.strategic_map_y_offset,
                    ),
                    "width": scaling.scale_width(constants.strategic_map_pixel_width),
                    "height": scaling.scale_height(
                        constants.strategic_map_pixel_height
                    ),
                    "parent_collection": status.grids_collection,
                    "modes": [constants.STRATEGIC_MODE],
                    "init_type": constants.FREE_IMAGE,
                    "image_id": "locations/north_pole_centered_earth_grid.png",
                }
            )
        )
        constants.globe_projection_grid_x_offset += constants.strategic_map_pixel_width
        constants.strategic_map_x_offset += constants.strategic_map_pixel_width

    globe_projection_x = scaling.scale_width(
        constants.strategic_map_x_offset
        + constants.grids_collection_x
        + constants.strategic_map_pixel_width
        + 15
    )
    globe_projection_y = (
        scaling.scale_height(constants.earth_grid_y_offset) + status.grids_collection.y
    )
    globe_projection_size = constants.earth_grid_width * 0.85
    status.dummy_surface_image = constants.ActorCreationManager.create_interface_element(
        {
            "coordinates": (globe_projection_x, globe_projection_y),
            "init_type": constants.FREE_IMAGE,
            "modes": [],
            "width": scaling.scale_width(1000),
            "height": scaling.scale_height(
                1000
            ),  # Sufficient to retain surface detail - does not seem to have a performance impact
            "image_id": "misc/empty.png",
            "pixellate_image": True,
        }
    )
    status.dummy_surface_image_high_res = (
        constants.ActorCreationManager.create_interface_element(
            {
                "coordinates": (globe_projection_x, globe_projection_y),
                "init_type": constants.FREE_IMAGE,
                "modes": [],
                "width": scaling.scale_width(200),
                "height": scaling.scale_height(200),
                "image_id": "misc/empty.png",
                "pixellate_image": False,
            }
        )
    )
    compass_overlay_size = 15
    north_overlay = constants.ActorCreationManager.create_interface_element(
        {
            "coordinates": (
                status.grids_collection.x
                + scaling.scale_width(
                    constants.globe_projection_grid_x_offset
                    + constants.globe_projection_grid_width / 2
                    - compass_overlay_size / 2
                ),
                status.grids_collection.y
                + scaling.scale_height(
                    constants.globe_projection_grid_y_offset
                    + constants.globe_projection_grid_height
                    - (compass_overlay_size * 0.25)
                ),
            ),
            "init_type": constants.FREE_IMAGE,
            "modes": [constants.STRATEGIC_MODE],
            "width": scaling.scale_width(compass_overlay_size),
            "height": scaling.scale_width(compass_overlay_size),
            "image_id": "misc/north_indicator.png",
            "to_front": True,
        }
    )
    south_overlay = constants.ActorCreationManager.create_interface_element(
        {
            "coordinates": (
                status.grids_collection.x
                + scaling.scale_width(
                    constants.globe_projection_grid_x_offset
                    + constants.globe_projection_grid_width / 2
                    - compass_overlay_size / 2
                ),
                status.grids_collection.y
                + scaling.scale_height(
                    constants.globe_projection_grid_y_offset
                    + compass_overlay_size * -0.75
                ),
            ),
            "init_type": constants.FREE_IMAGE,
            "modes": north_overlay.modes,
            "width": scaling.scale_width(compass_overlay_size),
            "height": scaling.scale_width(compass_overlay_size),
            "image_id": "misc/south_indicator.png",
        }
    )

    switch_game_mode_buttons_x = (
        constants.strategic_map_x_offset
        + constants.grids_collection_x
        + constants.strategic_map_pixel_width
        + 15
        + globe_projection_size
        + 15
    )
    game_mode_navigation_collection = constants.ActorCreationManager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(
                switch_game_mode_buttons_x, constants.default_display_height - 55
            ),
            "width": 10,
            "height": 10,
            "modes": [
                constants.STRATEGIC_MODE,
                constants.EARTH_MODE,
                constants.MINISTERS_MODE,
                constants.TRIAL_MODE,
                constants.LOCATION_MODE,
            ],
            "init_type": constants.ORDERED_COLLECTION,
            "member_config": {"order_exempt": True},
            "separation": 10,
            "direction": "horizontal",
            "outline_color": constants.space_background_outline_color,
        }
    )
    status.to_strategic_button = constants.ActorCreationManager.create_interface_element(
        {
            "height": scaling.scale_height(50),
            "width": scaling.scale_width(50),
            "keybind_id": pygame.K_1,
            "image_id": "misc/empty.png", # Matches the planet
            "to_mode": constants.STRATEGIC_MODE,
            "init_type": constants.SWITCH_GAME_MODE_BUTTON,
            "parent_collection": game_mode_navigation_collection,
        }
    )
    status.to_earth_button = constants.ActorCreationManager.create_interface_element(
        {
            "height": scaling.scale_height(50),
            "width": scaling.scale_width(50),
            "keybind_id": pygame.K_2,
            "image_id": actor_utility.generate_frame(world_utility.generate_abstract_world_image(planet=constants.EARTH_WORLD, size=0.6)),
            "to_mode": constants.EARTH_MODE,
            "init_type": constants.SWITCH_GAME_MODE_BUTTON,
            "parent_collection": game_mode_navigation_collection,
        }
    )

    to_ministers_button = constants.ActorCreationManager.create_interface_element(
        {
            "height": scaling.scale_height(50),
            "width": scaling.scale_width(50),
            "keybind_id": pygame.K_3,
            "image_id": actor_utility.generate_frame("buttons/hq_button.png"),
            "to_mode": constants.MINISTERS_MODE,
            "init_type": constants.SWITCH_GAME_MODE_BUTTON,
            "parent_collection": game_mode_navigation_collection,
        }
    )

    rhs_menu_collection = constants.ActorCreationManager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(
                constants.default_display_width - 55,
                constants.default_display_height - 5,
            ),
            "width": 10,
            "height": 10,
            "modes": [
                constants.STRATEGIC_MODE,
                constants.EARTH_MODE,
                constants.MINISTERS_MODE,
                constants.TRIAL_MODE,
                constants.NEW_GAME_SETUP_MODE,
                constants.LOCATION_MODE,
            ],
            "init_type": constants.ORDERED_COLLECTION,
            "member_config": {"order_exempt": True},
            "separation": 10,
            "outline_color": constants.space_background_outline_color,
        }
    )

    status.lhs_menu_collection = (
        constants.ActorCreationManager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(
                    5, constants.default_display_height - 55
                ),
                "width": 10,
                "height": 10,
                "modes": [
                    constants.STRATEGIC_MODE,
                    constants.EARTH_MODE,
                    constants.MINISTERS_MODE,
                    constants.NEW_GAME_SETUP_MODE,
                    constants.LOCATION_MODE,
                    constants.MAIN_MENU_MODE,
                ],
                "init_type": constants.ORDERED_COLLECTION,
                "member_config": {"order_exempt": True},
                "separation": 5,
                "direction": "horizontal",
            }
        )
    )

    to_main_menu_button = constants.ActorCreationManager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(
                constants.default_display_width - 50, constants.default_display_height - 50
            ),
            "width": scaling.scale_width(50),
            "height": scaling.scale_height(50),
            "keybind_id": pygame.K_ESCAPE,
            "image_id": actor_utility.generate_frame("buttons/exit_earth_screen_button.png", background="buttons/default_button_frameless.png"),
            "to_mode": constants.MAIN_MENU_MODE,
            "init_type": constants.SWITCH_GAME_MODE_BUTTON,
            "modes": [
                constants.STRATEGIC_MODE,
                constants.EARTH_MODE,
                constants.MINISTERS_MODE,
                constants.TRIAL_MODE,
                constants.LOCATION_MODE,
            ],
            "parent_collection": rhs_menu_collection,
        }
    )
    new_game_setup_to_main_menu_button = constants.ActorCreationManager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(
                0, constants.default_display_height - 50
            ),
            "width": scaling.scale_width(50),
            "height": scaling.scale_height(50),
            "keybind_id": pygame.K_ESCAPE,
            "image_id": actor_utility.generate_frame("buttons/exit_earth_screen_button.png", background="buttons/default_button_frameless.png"),
            "to_mode": constants.MAIN_MENU_MODE,
            "init_type": constants.SWITCH_GAME_MODE_BUTTON,
            "modes": [
                constants.NEW_GAME_SETUP_MODE,
            ],
            "parent_collection": status.lhs_menu_collection,
            "outline_color": constants.space_background_outline_color,
        }
    )

    wide_button_defaults = {
        "width": scaling.scale_width(round(constants.default_display_width * 0.2)),
        "height": scaling.scale_height(50),
        "outline_color": constants.space_background_outline_color,
    }
    end_turn_button = constants.ActorCreationManager.create_interface_element(
        {
            **wide_button_defaults,
            "coordinates": scaling.scale_coordinates(
                round(constants.default_display_width * 0.4) - 15,
                constants.default_display_height - 55,
            ),
            "modes": [
                constants.STRATEGIC_MODE,
                constants.EARTH_MODE,
                constants.MINISTERS_MODE,
                constants.TRIAL_MODE,
                constants.LOCATION_MODE,
            ],
            "keybind_id": pygame.K_SPACE,
            "image_id": [
                "buttons/default_wide_button.png",
                text_utility.prepare_render("End Turn", constants.fonts[constants.LARGE_NOTIFICATION_FONT]),
            ],
            "init_type": constants.END_TURN_BUTTON,
        }
    )
    main_menu_new_game_button = constants.ActorCreationManager.create_interface_element(
        {
            **wide_button_defaults,
            "coordinates": scaling.scale_coordinates(
                round(constants.default_display_width * 0.4) - 15,
                scaling.scale_height(constants.default_display_height / 2 - 150),
            ),
            "modes": [constants.MAIN_MENU_MODE],
            "keybind_id": pygame.K_n,
            "image_id": [
                "buttons/default_wide_button.png",
                text_utility.prepare_render("New Game", constants.fonts[constants.LARGE_NOTIFICATION_FONT]),
            ],
            "init_type": constants.NEW_GAME_BUTTON,
        }
    )
    setup_new_game_button = constants.ActorCreationManager.create_interface_element(
        {
            **wide_button_defaults,
            "coordinates": scaling.scale_coordinates(
                round(constants.default_display_width * 0.4) - 15,
                scaling.scale_height(constants.default_display_height / 2 - 400),
            ),
            "modes": [constants.NEW_GAME_SETUP_MODE],
            "keybind_id": pygame.K_n,
            "image_id": [
                "buttons/default_wide_button.png",
                text_utility.prepare_render("New Game", constants.fonts[constants.LARGE_NOTIFICATION_FONT]),
            ],
            "init_type": constants.NEW_GAME_BUTTON,
        }
    )
    load_game_button = constants.ActorCreationManager.create_interface_element(
        {
            **wide_button_defaults,
            "coordinates": scaling.scale_coordinates(
                round(constants.default_display_width * 0.4) - 15,
                scaling.scale_height(constants.default_display_height / 2 - 225),
            ),
            "modes": [constants.MAIN_MENU_MODE],
            "keybind_id": pygame.K_l,
            "image_id": [
                "buttons/default_wide_button.png",
                text_utility.prepare_render("Load Game", constants.fonts[constants.LARGE_NOTIFICATION_FONT]),
            ],
            "init_type": constants.LOAD_GAME_BUTTON,
        }
    )

    rhs_button_defaults = {
        "width": scaling.scale_width(50),
        "height": scaling.scale_height(50),
        "outline_color": constants.space_background_outline_color,
        "parent_collection": rhs_menu_collection,
    }
    save_game_button = constants.ActorCreationManager.create_interface_element(
        {
            **rhs_button_defaults,
            "modes": [
                constants.STRATEGIC_MODE,
                constants.EARTH_MODE,
                constants.MINISTERS_MODE,
                constants.TRIAL_MODE,
                constants.LOCATION_MODE,
            ],
            "image_id": actor_utility.generate_frame(
                "buttons/save_game_button.png", background="buttons/default_button_frameless.png"
            ),
            "init_type": constants.SAVE_GAME_BUTTON,
        }
    )

    expand_text_box_button = constants.ActorCreationManager.create_interface_element(
        {
            **rhs_button_defaults,
            "modes": [
                constants.STRATEGIC_MODE,
                constants.EARTH_MODE,
                constants.MINISTERS_MODE,
                constants.TRIAL_MODE,
                constants.LOCATION_MODE,
            ],
            "image_id": actor_utility.generate_frame("buttons/text_box_size_button.png", background="buttons/default_button_frameless.png"),
            "init_type": constants.TOGGLE_BUTTON,
            "toggle_variable": "expand_text_box",
            "attached_to_actor": False,
        }
    )

    toggle_grid_lines_button = constants.ActorCreationManager.create_interface_element(
        {
            **rhs_button_defaults,
            "modes": [constants.STRATEGIC_MODE],
            "image_id": actor_utility.generate_frame("buttons/grid_line_button.png"),
            "init_type": constants.TOGGLE_BUTTON,
            "toggle_variable": "show_grid_lines",
            "attached_to_actor": False,
        }
    )

    if constants.EffectManager.effect_active("allow_planet_mask"):
        toggle_planet_mask_button = constants.ActorCreationManager.create_interface_element(
            {
                **rhs_button_defaults,
                "modes": [constants.STRATEGIC_MODE],
                "image_id": "buttons/toggle_planet_mask_button.png",
                "init_type": constants.TOGGLE_BUTTON,
                "toggle_variable": "show_planet_mask",
                "attached_to_actor": False,
            }
        )

    if constants.EffectManager.effect_active("allow_toggle_fog_of_war"):
        toggle_fog_of_war_button = constants.ActorCreationManager.create_interface_element(
            {
                **rhs_button_defaults,
                "modes": [constants.STRATEGIC_MODE],
                "image_id": actor_utility.generate_frame(
                    "buttons/toggle_fog_of_war_button.png"
                ),
                "init_type": constants.TOGGLE_BUTTON,
                "toggle_variable": "remove_fog_of_war",
                "attached_to_actor": False,
            }
        )
    if constants.EffectManager.effect_active("allow_toggle_clouds"):
        toggle_clouds_button = constants.ActorCreationManager.create_interface_element(
            {
                **rhs_button_defaults,
                "modes": [constants.STRATEGIC_MODE],
                "image_id": actor_utility.generate_frame(
                    "buttons/toggle_clouds_button.png"
                ),
                "init_type": constants.TOGGLE_BUTTON,
                "toggle_variable": "show_clouds",
                "attached_to_actor": False,
            }
        )

    if constants.EffectManager.effect_active("allow_toggle_god_mode"):
        toggle_god_mode_button = constants.ActorCreationManager.create_interface_element(
            {
                **rhs_button_defaults,
                "modes": [constants.STRATEGIC_MODE],
                "image_id": actor_utility.generate_frame("buttons/toggle_god_mode_button.png"),
                "init_type": constants.TOGGLE_BUTTON,
                "toggle_variable": "god_mode",
                "attached_to_actor": False,
            }
        )
    if constants.EffectManager.effect_active("map_modes"):
        for map_mode in constants.map_modes:
            constants.ActorCreationManager.create_interface_element(
                {
                    **rhs_button_defaults,
                    "modes": [constants.STRATEGIC_MODE, constants.EARTH_MODE, constants.LOCATION_MODE],
                    "image_id": actor_utility.generate_frame(
                        f"misc/map_modes/{map_mode}.png"
                    ),
                    "init_type": constants.MAP_MODE_BUTTON,
                    "map_mode": map_mode,
                }
            )

    lhs_button_defaults = {
        "width": scaling.scale_width(50),
        "height": scaling.scale_height(50),
        "parent_collection": status.lhs_menu_collection,
    }
    cycle_units_button = constants.ActorCreationManager.create_interface_element(
        {
            **lhs_button_defaults,
            "modes": [
                constants.STRATEGIC_MODE,
                constants.EARTH_MODE,
                constants.MINISTERS_MODE,
                constants.LOCATION_MODE,
            ],
            "keybind_id": pygame.K_TAB,
            "image_id": actor_utility.generate_frame("buttons/cycle_units_button.png", background="buttons/default_button_frameless.png"),
            "init_type": constants.CYCLE_UNITS_BUTTON,
        }
    )

    generate_crash_button = constants.ActorCreationManager.create_interface_element(
        {
            **lhs_button_defaults,
            "modes": [constants.MAIN_MENU_MODE],
            "image_id": actor_utility.generate_frame("buttons/exit_earth_screen_button.png", background="buttons/default_button_frameless.png"),
            "init_type": constants.GENERATE_CRASH_BUTTON,
        }
    )

    if constants.EffectManager.effect_active("allow_presets"):
        planet_preset_defaults = {
            "width": scaling.scale_width(100),
            "height": scaling.scale_height(100),
            "parent_collection": rhs_menu_collection,
            "member_config": {"order_x_offset": scaling.scale_width(-50)}
        }
        mars_preset_button = constants.ActorCreationManager.create_interface_element(
            {
                **planet_preset_defaults,
                "modes": [constants.NEW_GAME_SETUP_MODE],
                "image_id": actor_utility.generate_frame(
                    world_utility.generate_abstract_world_image(
                        size=0.8, planet=constants.MARS_WORLD
                    )
                ),
                "init_type": constants.TOGGLE_BUTTON,
                "toggle_variable": "mars_preset",
                "attached_to_actor": False,
            }
        )
        earth_preset_button = constants.ActorCreationManager.create_interface_element(
            {
                **planet_preset_defaults,
                "modes": [constants.NEW_GAME_SETUP_MODE],
                "image_id": actor_utility.generate_frame(
                    world_utility.generate_abstract_world_image(
                        size=0.8, planet=constants.EARTH_WORLD
                    )
                ),
                "init_type": constants.TOGGLE_BUTTON,
                "toggle_variable": "earth_preset",
                "attached_to_actor": False,
            }
        )
        venus_preset_button = constants.ActorCreationManager.create_interface_element(
            {
                **planet_preset_defaults,
                "modes": [constants.NEW_GAME_SETUP_MODE],
                "image_id": actor_utility.generate_frame(
                    world_utility.generate_abstract_world_image(
                        size=0.8, planet=constants.VENUS_WORLD
                    )
                ),
                "init_type": constants.TOGGLE_BUTTON,
                "toggle_variable": "venus_preset",
                "attached_to_actor": False,
            }
        )
