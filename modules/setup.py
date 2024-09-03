# Manages initial game setup in a semi-modular order

import pygame
import os
import logging
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags
import modules.util.scaling as scaling
import modules.util.actor_utility as actor_utility
import modules.util.game_transitions as game_transitions
import modules.constructs.fonts as fonts
import modules.constructs.worker_types as worker_types
import modules.constructs.minister_types as minister_types
import modules.constructs.equipment_types as equipment_types
import modules.constructs.terrain_feature_types as terrain_feature_types
from modules.tools.data_managers import (
    notification_manager_template,
    value_tracker_template,
    achievement_manager_template,
    character_manager_template,
    actor_creation_manager_template,
)
from modules.action_types import (
    public_relations_campaign,
    religious_campaign,
    advertising_campaign,
    combat,
    exploration,
    construction,
    upgrade,
    repair,
    loan_search,
    active_investigation,
    trial,
)


def setup(*args):
    """
    Description:
        Runs the inputted setup functions in order
    Input:
        function list args: List of setup functions to run
    Output:
        None
    """
    flags.startup_complete = False
    for setup_function in args:
        setup_function()
    flags.startup_complete = True
    flags.creating_new_game = False


def info_displays():
    """
    Description:
        Initializes info displays collection (must be run after new game setup is created for correct layering)
    Input:
        None
    Output:
        None
    """
    status.info_displays_collection = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(
                    5, constants.default_display_height - 205 + 125 - 5
                ),
                "width": scaling.scale_width(10),
                "height": scaling.scale_height(10),
                "modes": ["strategic", "earth", "ministers", "new_game_setup"],
                "init_type": constants.ORDERED_COLLECTION,
                "description": "general information panel",
                "resize_with_contents": True,
            }
        )
    )


def misc():
    """
    Description:
        Initializes object lists, current object variables, current status booleans, and other misc. values
    Input:
        None
    Output:
        None
    """
    constants.actor_creation_manager = (
        actor_creation_manager_template.actor_creation_manager_template()
    )

    constants.font_size = scaling.scale_height(constants.default_font_size)
    constants.notification_font_size = scaling.scale_height(
        constants.default_notification_font_size
    )

    constants.myfont = fonts.font(
        {
            "descriptor": "default",
            "name": constants.font_name,
            "size": constants.font_size,
            "color": "black",
        }
    )
    fonts.font(
        {
            "descriptor": "white",
            "name": constants.font_name,
            "size": constants.font_size,
            "color": "white",
        }
    )
    fonts.font(
        {
            "descriptor": "default_notification",
            "name": constants.font_name,
            "size": constants.notification_font_size,
            "color": "black",
        }
    )
    fonts.font(
        {
            "descriptor": "white_notification",
            "name": constants.font_name,
            "size": constants.notification_font_size,
            "color": "white",
        }
    )
    fonts.font(
        {
            "descriptor": "large_notification",
            "name": constants.font_name,
            "size": scaling.scale_height(30),
            "color": "black",
        }
    )
    fonts.font(
        {
            "descriptor": "large_white_notification",
            "name": constants.font_name,
            "size": scaling.scale_height(30),
            "color": "white",
        }
    )
    fonts.font(
        {
            "descriptor": "max_detail_white",
            "name": "helvetica",
            "size": scaling.scale_height(100),
            "color": "white",
        }
    )
    fonts.font(
        {
            "descriptor": "max_detail_black",
            "name": "helvetica",
            "size": scaling.scale_height(100),
            "color": "black",
        }
    )

    # page 1
    instructions_message = "Placeholder instructions, use += to add"
    status.instructions_list.append(instructions_message)

    status.loading_image = constants.actor_creation_manager.create_interface_element(
        {
            "image_id": ["misc/title.png", "misc/loading.png"],
            "init_type": constants.LOADING_IMAGE_TEMPLATE_IMAGE,
        }
    )

    strategic_background_image = (
        constants.actor_creation_manager.create_interface_element(
            {
                "modes": [
                    "strategic",
                    "earth",
                    "trial",
                    "new_game_setup",
                ],
                "image_id": "misc/background.png",
                "init_type": constants.BACKGROUND_IMAGE,
            }
        )
    )

    ministers_background_image = (
        constants.actor_creation_manager.create_interface_element(
            {
                "modes": [
                    "ministers",
                ],
                "image_id": "misc/ministers_background.png",
                "init_type": constants.BACKGROUND_IMAGE,
            }
        )
    )

    title_background_image = constants.actor_creation_manager.create_interface_element(
        {
            "modes": [
                "main_menu",
            ],
            "image_id": "misc/title.png",
            "init_type": constants.BACKGROUND_IMAGE,
        }
    )

    status.safe_click_area = constants.actor_creation_manager.create_interface_element(
        {
            "width": constants.display_width / 2 - scaling.scale_width(35),
            "height": constants.display_height,
            "modes": ["strategic", "earth", "ministers", "new_game_setup"],
            "image_id": "misc/empty.png",  # make a good image for this
            "init_type": constants.SAFE_CLICK_PANEL_ELEMENT,
        }
    )
    # safe click area has empty image but is managed with panel to create correct behavior - its intended image is in the background image's bundle to blit more efficiently

    game_transitions.set_game_mode("main_menu")

    constants.mouse_follower = (
        constants.actor_creation_manager.create_interface_element(
            {"init_type": constants.MOUSE_FOLLOWER_IMAGE}
        )
    )

    constants.notification_manager = (
        notification_manager_template.notification_manager_template()
    )

    constants.achievement_manager = (
        achievement_manager_template.achievement_manager_template()
    )

    constants.character_manager = (
        character_manager_template.character_manager_template()
    )

    status.grids_collection = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(
                constants.grids_collection_x, constants.grids_collection_y
            ),
            "width": scaling.scale_width(10),
            "height": scaling.scale_height(30),
            "modes": ["strategic", "earth"],
            "init_type": constants.INTERFACE_COLLECTION,
        }
    )

    north_indicator_image = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, 0),
            "modes": ["strategic"],
            "image_id": "misc/north_indicator.png",
            "init_type": constants.DIRECTIONAL_INDICATOR_IMAGE,
            "anchor_key": "north_pole",
            "width": scaling.scale_width(25),
            "height": scaling.scale_height(25),
        }
    )

    south_indicator_image = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, 0),
            "modes": ["strategic"],
            "image_id": "misc/south_indicator.png",
            "init_type": constants.DIRECTIONAL_INDICATOR_IMAGE,
            "anchor_key": "south_pole",
            "width": scaling.scale_width(25),
            "height": scaling.scale_height(25),
        }
    )
    # anchor = constants.actor_creation_manager.create_interface_element(
    #    {'width': 1, 'height': 1, 'init_type': 'interface element', 'parent_collection': status.info_displays_collection}
    # ) #rect at original location prevents collection from moving unintentionally when resizing


def worker_types_config():
    """
    Description:
        Defines worker type templates
    Input:
        None
    Output:
        None
    """
    worker_types.worker_type(
        False,
        {
            "key": constants.EUROPEAN_WORKERS,
            "adjective": "European",
            "permissions": [
                constants.WORKER_PERMISSION,
                constants.EUROPEAN_WORKERS_PERMISSION,
            ],
            "upkeep": 6.0,
            "can_crew": [constants.SHIP, constants.TRAIN],
            "upkeep_variance": True,
            "fired_description": "Fired description. /n /n",
        },
    )
    worker_types.worker_type(
        False,
        {
            "key": constants.CHURCH_VOLUNTEERS,
            "adjective": "religious",
            "permissions": [
                constants.WORKER_PERMISSION,
                constants.CHURCH_VOLUNTEERS_PERMISSION,
            ],
            "name": "church volunteers",
            "upkeep": 0.0,
            "fired_description": "Fired church volunteers will never settle in slums and will instead return to Europe. /n /n"
            + "Firing church volunteers reflects poorly on your company and will incur a public opinion penalty of 1. /n /n",
        },
    )


def equipment_types_config():
    """
    Description:
        Defines equipment type templates
    Input:
        None
    Output:
        None
    """
    return


def terrain_feature_types_config():
    """
    Description:
        Defines terrain feature type templates
    Input:
        None
    Output:
        None
    """
    terrain_feature_types.terrain_feature_type(
        {
            "terrain_feature_type": "north pole",
            "image_id": "misc/empty.png",
            "description": ["North pole of the planet"],
            "tracking_type": constants.UNIQUE_FEATURE_TRACKING,
        }
    )

    terrain_feature_types.terrain_feature_type(
        {
            "terrain_feature_type": "south pole",
            "image_id": "misc/empty.png",
            "description": ["South pole of the planet"],
            "tracking_type": constants.UNIQUE_FEATURE_TRACKING,
        }
    )

    terrain_feature_types.terrain_feature_type(
        {
            "terrain_feature_type": "equator",
            "image_id": "misc/empty.png",
            "description": ["Lies along the equator of the planet"],
            "tracking_type": constants.LIST_FEATURE_TRACKING,
            "visible": False,
        }
    )
    terrain_feature_types.terrain_feature_type(
        {
            "terrain_feature_type": "northern tropic",
            "image_id": "Northern Tropic",
            "description": ["Lies along the northern edge of the equatorial zone"],
        }
    )
    terrain_feature_types.terrain_feature_type(
        {
            "terrain_feature_type": "southern tropic",
            "image_id": "Southern Tropic",
            "description": ["Lies along the southern edge of the equatorial zone"],
        }
    )


def actions():
    """
    Description:
        Configures any actions in the action_types folder, preparing them to be automatically implemented
    Input:
        None
    Output:
        None
    """
    for building_type in constants.building_types + [constants.TRAIN]:
        if not building_type in [constants.WAREHOUSES, constants.SLUMS]:
            construction.construction(building_type=building_type)
            if not building_type in [constants.TRAIN, constants.INFRASTRUCTURE]:
                repair.repair(building_type=building_type)
    for upgrade_type in constants.upgrade_types:
        upgrade.upgrade(building_type=upgrade_type)
    public_relations_campaign.public_relations_campaign()
    religious_campaign.religious_campaign()
    advertising_campaign.advertising_campaign()
    combat.combat()
    exploration.exploration()
    loan_search.loan_search()
    active_investigation.active_investigation()
    trial.trial()

    for action_type in status.actions:
        if status.actions[action_type].placement_type == "free":
            button_input_dict = status.actions[action_type].button_setup({})
            if button_input_dict:
                constants.actor_creation_manager.create_interface_element(
                    button_input_dict
                )
    # action imports hardcoded here, alternative to needing to keep module files in .exe version


def commodities():
    """
    Description:
        Defines commodities with associated buildings and icons, along with buildings
    Input:
        None
    Output:
        None
    """
    for current_commodity in constants.commodity_types:
        constants.item_prices[current_commodity] = 0
        constants.sold_commodities[current_commodity] = 0

    for current_commodity in constants.collectable_resources:
        constants.commodities_produced[current_commodity] = 0

    for current_equipment in status.equipment_types:
        constants.item_prices[current_equipment] = status.equipment_types[
            current_equipment
        ].price


def def_ministers():
    """
    Description:
        Defines minister positions, backgrounds, and associated units
    Input:
        None
    Output:
        None
    """
    minister_types.minister_type(
        {
            "key": constants.MILITARY_MINISTER,
            "name": "General",
            "skill_type": "military",
            "description": ["Military-oriented units include majors and battalions."],
        }
    )
    minister_types.minister_type(
        {
            "key": constants.RELIGION_MINISTER,
            "name": "Bishop",
            "skill_type": "religion",
            "description": [
                "Religion-oriented units include evangelists, church volunteers, and missionaries."
            ],
        }
    )
    minister_types.minister_type(
        {
            "key": constants.TRADE_MINISTER,
            "name": "Minister of Trade",
            "skill_type": "trade",
            "description": [
                "Trade-oriented units include merchants and caravans.",
                "The Minister of Trade also controls the purchase and sale of goods on Earth",
            ],
        }
    )
    minister_types.minister_type(
        {
            "key": constants.EXPLORATION_MINISTER,
            "name": "Minister of Geography",
            "skill_type": "exploration",
            "description": [
                "Exploration-oriented units include explorers and expeditions."
            ],
        }
    )
    minister_types.minister_type(
        {
            "key": constants.CONSTRUCTION_MINISTER,
            "name": "Minister of Construction",
            "skill_type": "construction",
            "description": [
                "Construction-oriented units include engineers and construction gangs."
            ],
        }
    )
    minister_types.minister_type(
        {
            "key": constants.PRODUCTION_MINISTER,
            "name": "Minister of Production",
            "skill_type": "production",
            "description": [
                "Production-oriented units include work crews and foremen."
            ],
        }
    )
    minister_types.minister_type(
        {
            "key": constants.TRANSPORTATION_MINISTER,
            "name": "Minister of Transportation",
            "skill_type": "transportation",
            "description": [
                "Transportation-oriented units include ships, trains, drivers, and porters.",
                "The Minister of Transportation also ensures that goods are not lost in transport or storage",
            ],
        }
    )
    minister_types.minister_type(
        {
            "key": constants.PROSECUTION_MINISTER,
            "name": "Prosecutor",
            "skill_type": "prosecution",
            "controls_units": False,
            "description": [
                "Rather than controlling units, a prosecutor controls the process of investigating and removing ministers suspected to be corrupt."
            ],
        }
    )


def transactions():
    """
    Description:
        Defines recruitment, upkeep, building, and action costs, along with action and financial transaction types
    Input:
        None
    Output:
        None
    """
    for current_officer in constants.officer_types:
        constants.recruitment_costs[current_officer] = constants.recruitment_costs[
            "officer"
        ]
    actor_utility.update_descriptions()
    actor_utility.reset_action_prices()


def value_trackers():
    """
    Description:
        Defines important global values and initializes associated tracker labels
    Input:
        None
    Output:
        None
    """
    value_trackers_ordered_collection = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(
                    250, constants.default_display_height - 5
                ),
                "width": scaling.scale_width(10),
                "height": scaling.scale_height(30),
                "modes": [
                    "strategic",
                    "earth",
                    "ministers",
                    "trial",
                    "main_menu",
                    "new_game_setup",
                ],
                "init_type": constants.ORDERED_COLLECTION,
            }
        )
    )

    constants.turn_tracker = value_tracker_template.value_tracker_template(
        value_key="turn", initial_value=0, min_value=None, max_value=None
    )
    constants.actor_creation_manager.create_interface_element(
        {
            "minimum_width": scaling.scale_width(10),
            "height": scaling.scale_height(30),
            "modes": ["strategic", "earth", "ministers"],
            "image_id": "misc/default_label.png",
            "value_name": "turn",
            "init_type": constants.VALUE_LABEL,
            "parent_collection": value_trackers_ordered_collection,
            "member_config": {
                "order_x_offset": scaling.scale_width(315),
                "order_overlap": True,
            },
        }
    )

    constants.money_tracker = value_tracker_template.money_tracker_template(100)
    constants.money_label = constants.actor_creation_manager.create_interface_element(
        {
            "minimum_width": scaling.scale_width(10),
            "height": scaling.scale_height(30),
            "modes": ["strategic", "earth", "ministers", "trial"],
            "image_id": "misc/default_label.png",
            "init_type": constants.MONEY_LABEL,
            "parent_collection": value_trackers_ordered_collection,
            "member_config": {
                "index": 1
            },  # should appear before public opinion in collection but relies on public opinion existing
        }
    )

    constants.public_opinion_tracker = (
        value_tracker_template.public_opinion_tracker_template(
            value_key="public_opinion", initial_value=0, min_value=0, max_value=100
        )
    )
    constants.actor_creation_manager.create_interface_element(
        {
            "minimum_width": scaling.scale_width(10),
            "height": scaling.scale_height(30),
            "modes": ["strategic", "earth", "ministers", "trial"],
            "image_id": "misc/default_label.png",
            "value_name": "public_opinion",
            "init_type": constants.VALUE_LABEL,
            "parent_collection": value_trackers_ordered_collection,
        }
    )

    if constants.effect_manager.effect_active("track_fps"):
        constants.fps_tracker = value_tracker_template.value_tracker_template(
            value_key="fps", initial_value=0, min_value=0, max_value=None
        )
        constants.actor_creation_manager.create_interface_element(
            {
                "minimum_width": scaling.scale_width(10),
                "height": scaling.scale_height(30),
                "modes": [
                    "strategic",
                    "earth",
                    "ministers",
                    "trial",
                    "main_menu",
                    "new_game_setup",
                ],
                "image_id": "misc/default_label.png",
                "value_name": "fps",
                "init_type": constants.VALUE_LABEL,
                "parent_collection": value_trackers_ordered_collection,
            }
        )

    constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(
                225, constants.default_display_height - 35
            ),
            "width": scaling.scale_width(30),
            "height": scaling.scale_height(30),
            "modes": ["strategic", "earth", "ministers", "trial"],
            "image_id": "buttons/instructions.png",
            "init_type": constants.SHOW_PREVIOUS_REPORTS_BUTTON,
        }
    )

    constants.evil_tracker = value_tracker_template.value_tracker_template(
        "evil", 0, 0, 100
    )

    constants.fear_tracker = value_tracker_template.value_tracker_template(
        "fear", 1, 1, 6
    )


def buttons():
    """
    Description:
        Initializes static buttons
    Input:
        None
    Output:
        None
    """
    status.planet_view_mask = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(320, 0),
            "width": scaling.scale_width(constants.strategic_map_pixel_width),
            "height": scaling.scale_height(constants.strategic_map_pixel_height),
            "parent_collection": status.grids_collection,
            "modes": ["strategic"],  # Manually drawn by scrolling strategic grid
            "init_type": constants.FREE_IMAGE,
            "color_key": (255, 255, 255),
            "image_id": "misc/planet_view_mask.png",
        }
    )

    input_dict = {
        "coordinates": scaling.scale_coordinates(0, 10),
        "width": scaling.scale_width(150),
        "height": scaling.scale_height(100),
        "image_id": "misc/empty.png",
        "modes": ["strategic", "earth"],
        "to_mode": "earth",
        "init_type": constants.FREE_IMAGE,
        "parent_collection": status.grids_collection,
    }
    strategic_flag_icon = constants.actor_creation_manager.create_interface_element(
        input_dict
    )

    input_dict["modes"] = ["ministers"]
    input_dict["coordinates"] = scaling.scale_coordinates(
        constants.default_display_width / 2 - 75, constants.default_display_height - 160
    )
    input_dict["parent_collection"] = None
    ministers_flag_icon = constants.actor_creation_manager.create_interface_element(
        input_dict
    )
    # status.flag_icon_list.append(ministers_flag_icon)

    input_dict = {
        "coordinates": scaling.scale_coordinates(
            1065, constants.default_display_height - 55
        ),
        "height": scaling.scale_height(50),
        "width": scaling.scale_width(50),
        "keybind_id": pygame.K_1,
        "image_id": "locations/africa_button.png",
        "modes": ["ministers", "strategic", "earth", "trial"],
        "to_mode": "strategic",
        "init_type": constants.SWITCH_GAME_MODE_BUTTON,
    }
    to_strategic_button = constants.actor_creation_manager.create_interface_element(
        input_dict
    )

    input_dict.update(
        {
            "coordinates": scaling.scale_coordinates(
                1125, constants.default_display_height - 55
            ),
            "image_id": "locations/europe_button.png",
            "to_mode": "earth",
            "keybind_id": pygame.K_2,
        }
    )
    to_europe_button = constants.actor_creation_manager.create_interface_element(
        input_dict
    )

    input_dict.update(
        {
            "coordinates": scaling.scale_coordinates(
                1185, constants.default_display_height - 55
            ),
            "width": scaling.scale_width(50),
            "to_mode": "ministers",
            "image_id": "buttons/european_hq_button.png",
            "keybind_id": pygame.K_3,
        }
    )
    to_ministers_button = constants.actor_creation_manager.create_interface_element(
        input_dict
    )

    rhs_menu_collection = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(
                constants.default_display_width - 55,
                constants.default_display_height - 5,
            ),
            "width": 10,
            "height": 10,
            "modes": ["strategic", "earth", "ministers", "trial", "new_game_setup"],
            "init_type": constants.ORDERED_COLLECTION,
            "member_config": {"order_exempt": True},
            "separation": 5,
        }
    )

    lhs_menu_collection = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(
                5, constants.default_display_height - 55
            ),
            "width": 10,
            "height": 10,
            "modes": ["strategic", "earth", "ministers", "new_game_setup"],
            "init_type": constants.ORDERED_COLLECTION,
            "member_config": {"order_exempt": True},
            "separation": 5,
            "direction": "horizontal",
        }
    )

    input_dict["coordinates"] = scaling.scale_coordinates(
        constants.default_display_width - 50, constants.default_display_height - 50
    )
    input_dict["image_id"] = "buttons/exit_european_hq_button.png"
    input_dict["init_type"] = constants.SWITCH_GAME_MODE_BUTTON
    input_dict["width"] = scaling.scale_width(50)
    input_dict["height"] = scaling.scale_height(50)
    input_dict["modes"] = ["strategic", "earth", "ministers", "trial"]
    input_dict["keybind_id"] = pygame.K_ESCAPE
    input_dict["to_mode"] = "main_menu"
    to_main_menu_button = constants.actor_creation_manager.create_interface_element(
        input_dict
    )
    rhs_menu_collection.add_member(to_main_menu_button)

    input_dict["coordinates"] = scaling.scale_coordinates(
        0, constants.default_display_height - 50
    )
    input_dict["modes"] = ["new_game_setup"]
    input_dict["keybind_id"] = pygame.K_ESCAPE
    new_game_setup_to_main_menu_button = (
        constants.actor_creation_manager.create_interface_element(input_dict)
    )
    lhs_menu_collection.add_member(new_game_setup_to_main_menu_button)

    input_dict = {
        "coordinates": scaling.scale_coordinates(
            round(constants.default_display_width * 0.4),
            constants.default_display_height - 55,
        ),
        "width": scaling.scale_width(round(constants.default_display_width * 0.2)),
        "height": scaling.scale_height(50),
        "modes": ["strategic", "earth", "ministers", "trial"],
        "keybind_id": pygame.K_SPACE,
        "image_id": "buttons/end_turn_button.png",
        "init_type": constants.END_TURN_BUTTON,
    }
    end_turn_button = constants.actor_creation_manager.create_interface_element(
        input_dict
    )

    input_dict["coordinates"] = (
        input_dict["coordinates"][0],
        scaling.scale_height(constants.default_display_height / 2 - 150),
    )
    input_dict["modes"] = ["main_menu"]
    input_dict["keybind_id"] = pygame.K_n
    input_dict["image_id"] = "buttons/new_game_button.png"
    input_dict["init_type"] = constants.NEW_GAME_BUTTON
    main_menu_new_game_button = (
        constants.actor_creation_manager.create_interface_element(input_dict)
    )

    input_dict["coordinates"] = (
        input_dict["coordinates"][0],
        scaling.scale_height(constants.default_display_height / 2 - 400),
    )
    input_dict["modes"] = ["new_game_setup"]
    input_dict["keybind_id"] = pygame.K_n
    setup_new_game_button = constants.actor_creation_manager.create_interface_element(
        input_dict
    )

    input_dict["coordinates"] = (
        input_dict["coordinates"][0],
        scaling.scale_height(constants.default_display_height / 2 - 225),
    )
    input_dict["modes"] = ["main_menu"]
    input_dict["keybind_id"] = pygame.K_l
    input_dict["image_id"] = "buttons/load_game_button.png"
    input_dict["init_type"] = constants.LOAD_GAME_BUTTON
    load_game_button = constants.actor_creation_manager.create_interface_element(
        input_dict
    )

    input_dict = {
        "coordinates": scaling.scale_coordinates(
            constants.default_display_width - 50, constants.default_display_height - 125
        ),
        "width": scaling.scale_width(50),
        "height": scaling.scale_height(50),
        "modes": ["strategic", "earth", "ministers", "trial"],
        "image_id": "buttons/save_game_button.png",
        "init_type": constants.SAVE_GAME_BUTTON,
    }
    save_game_button = constants.actor_creation_manager.create_interface_element(
        input_dict
    )
    rhs_menu_collection.add_member(save_game_button)

    input_dict["modes"] = ["strategic", "earth", "ministers", "trial"]
    input_dict["image_id"] = "buttons/text_box_size_button.png"
    input_dict["init_type"] = constants.TOGGLE_BUTTON
    input_dict["toggle_variable"] = "expand_text_box"
    input_dict["attached_to_actor"] = False
    expand_text_box_button = constants.actor_creation_manager.create_interface_element(
        input_dict
    )
    rhs_menu_collection.add_member(expand_text_box_button)

    input_dict["modes"] = ["strategic"]
    input_dict["image_id"] = "buttons/grid_line_button.png"

    input_dict["init_type"] = constants.TOGGLE_BUTTON
    input_dict["attached_to_actor"] = False
    input_dict["toggle_variable"] = "show_grid_lines"
    toggle_grid_lines_button = (
        constants.actor_creation_manager.create_interface_element(input_dict)
    )
    rhs_menu_collection.add_member(toggle_grid_lines_button)

    if constants.effect_manager.effect_active("allow_planet_mask"):
        input_dict["init_type"] = constants.TOGGLE_BUTTON
        input_dict["toggle_variable"] = "show_planet_mask"
        input_dict["attached_to_actor"] = False
        input_dict["modes"] = ["strategic"]
        input_dict["image_id"] = actor_utility.generate_frame(
            "buttons/toggle_planet_mask_button.png"
        )
        rhs_menu_collection.add_member(
            constants.actor_creation_manager.create_interface_element(input_dict)
        )

    if constants.effect_manager.effect_active("allow_toggle_fog_of_war"):
        input_dict["init_type"] = constants.TOGGLE_BUTTON
        input_dict["toggle_variable"] = "remove_fog_of_war"
        input_dict["attached_to_actor"] = False
        input_dict["modes"] = ["strategic"]
        input_dict["image_id"] = actor_utility.generate_frame(
            "buttons/toggle_fog_of_war_button.png"
        )
        rhs_menu_collection.add_member(
            constants.actor_creation_manager.create_interface_element(input_dict)
        )

    input_dict["coordinates"] = scaling.scale_coordinates(
        110, constants.default_display_height - 50
    )
    input_dict["modes"] = ["strategic", "earth", "ministers"]
    input_dict["keybind_id"] = pygame.K_TAB
    input_dict["image_id"] = "buttons/cycle_units_button.png"
    input_dict["init_type"] = constants.CYCLE_UNITS_BUTTON
    cycle_units_button = constants.actor_creation_manager.create_interface_element(
        input_dict
    )
    lhs_menu_collection.add_member(cycle_units_button)
    del input_dict["keybind_id"]

    input_dict["coordinates"] = (scaling.scale_width(165), input_dict["coordinates"][1])
    input_dict["modes"] = ["strategic", "earth"]
    input_dict["image_id"] = "buttons/disable_sentry_mode_button.png"
    input_dict["init_type"] = constants.WAKE_UP_ALL_BUTTON
    wake_up_all_button = constants.actor_creation_manager.create_interface_element(
        input_dict
    )
    lhs_menu_collection.add_member(wake_up_all_button)

    input_dict["coordinates"] = (scaling.scale_width(220), input_dict["coordinates"][1])
    input_dict["image_id"] = "buttons/execute_movement_routes_button.png"
    input_dict["init_type"] = constants.EXECUTE_MOVEMENT_ROUTES_BUTTON
    execute_movement_routes_button = (
        constants.actor_creation_manager.create_interface_element(input_dict)
    )
    lhs_menu_collection.add_member(execute_movement_routes_button)

    input_dict["coordinates"] = scaling.scale_coordinates(
        constants.default_display_width - 55, constants.default_display_height - 55
    )
    input_dict["modes"] = ["main_menu"]
    input_dict["image_id"] = ["buttons/exit_european_hq_button.png"]
    input_dict["init_type"] = constants.GENERATE_CRASH_BUTTON
    generate_crash_button = constants.actor_creation_manager.create_interface_element(
        input_dict
    )

    if constants.effect_manager.effect_active("map_modes"):
        input_dict["init_type"] = constants.MAP_MODE_BUTTON
        input_dict["parent_collection"] = rhs_menu_collection
        input_dict["modes"] = ["strategic", "earth"]
        for map_mode in constants.map_modes:
            input_dict["map_mode"] = map_mode
            input_dict["image_id"] = actor_utility.generate_frame(
                f"misc/map_modes/{map_mode}.png"
            )
            constants.actor_creation_manager.create_interface_element(input_dict)


def earth_screen():
    """
    Description:
        Initializes static interface of Earth screen - purchase buttons for units and items, 8 per column
    Input:
        None
    Output:
        None
    """
    earth_purchase_buttons = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(1500, 20),
            "width": 10,
            "height": 10,
            "modes": ["earth"],
            "init_type": constants.ORDERED_COLLECTION,
            "separation": scaling.scale_height(20),
            "reversed": True,
            "second_dimension_increment": scaling.scale_width(125),
            "direction": "vertical",
        }
    )

    for recruitment_index, recruitment_type in enumerate(
        constants.recruitment_types
    ):  # Creates recruitment button for each officer type, workers, and steamship
        constants.actor_creation_manager.create_interface_element(
            {
                "width": scaling.scale_width(100),
                "height": scaling.scale_height(100),
                "init_type": constants.RECRUITMENT_BUTTON,
                "parent_collection": earth_purchase_buttons,
                "recruitment_type": recruitment_type,
                "member_config": {
                    "second_dimension_coordinate": -1 * (recruitment_index // 8)
                },
            }
        )

    for item_type in ["consumer goods"]:  # Creates purchase button for items from earth
        constants.actor_creation_manager.create_interface_element(
            {
                "width": scaling.scale_width(100),
                "height": scaling.scale_height(100),
                "init_type": constants.BUY_ITEM_BUTTON,
                "parent_collection": earth_purchase_buttons,
                "item_type": item_type,
                "member_config": {
                    "second_dimension_coordinate": -1 * (recruitment_index // 8)
                },  # Re-uses recruitment index from previous loop
            }
        )
        recruitment_index += 1


def ministers_screen():
    """
    Description:
        Initializes static interface of ministers screen
    Input:
        None
    Output:
        None
    """
    # minister table setup
    table_width = 400
    table_height = 750
    constants.actor_creation_manager.create_interface_element(
        {
            "image_id": "misc/minister_table.png",
            "coordinates": scaling.scale_coordinates(
                (constants.default_display_width / 2) - (table_width / 2), 55
            ),
            "width": scaling.scale_width(table_width),
            "height": scaling.scale_height(table_height),
            "modes": ["ministers"],
            "init_type": constants.FREE_IMAGE,
        }
    )
    status.table_map_image = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(
                (constants.default_display_width / 2) - 100, 400
            ),
            "init_type": constants.FREE_IMAGE,
            "modes": ["ministers"],
            "width": scaling.scale_width(200),
            "height": scaling.scale_height(200),
            "image_id": "misc/empty.png",
        }
    )
    position_icon_width = 75
    portrait_icon_width = 125
    input_dict = {
        "width": scaling.scale_width(portrait_icon_width),
        "height": scaling.scale_height(portrait_icon_width),
        "modes": ["ministers"],
        "color": "gray",
        "init_type": constants.MINISTER_PORTRAIT_IMAGE,
    }
    for current_index, minister_type_tuple in enumerate(status.minister_types.items()):
        # Creates an office icon and a portrait at a section of the table for each minister
        key, minister_type = minister_type_tuple
        if current_index <= 3:  # left side
            constants.actor_creation_manager.create_interface_element(
                {
                    "coordinates": scaling.scale_coordinates(
                        (constants.default_display_width / 2) - (table_width / 2) + 10,
                        current_index * 180
                        + 95
                        + (portrait_icon_width / 2 - position_icon_width / 2),
                    ),
                    "width": scaling.scale_width(position_icon_width),
                    "height": scaling.scale_height(position_icon_width),
                    "modes": ["ministers"],
                    "minister_type": minister_type,
                    "attached_label": None,
                    "init_type": constants.MINISTER_TYPE_IMAGE,
                }
            )

            input_dict["coordinates"] = scaling.scale_coordinates(
                (constants.default_display_width / 2)
                - (table_width / 2)
                - portrait_icon_width
                - 10,
                current_index * 180 + 95,
            )
            input_dict["minister_type"] = minister_type
            constants.actor_creation_manager.create_interface_element(input_dict)

        else:
            constants.actor_creation_manager.create_interface_element(
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
                    "modes": ["ministers"],
                    "minister_type": minister_type,
                    "attached_label": None,
                    "init_type": constants.MINISTER_TYPE_IMAGE,
                }
            )

            input_dict["coordinates"] = scaling.scale_coordinates(
                (constants.default_display_width / 2) + (table_width / 2) + 10,
                (current_index - 4) * 180 + 95,
            )
            input_dict["minister_type"] = minister_type
            constants.actor_creation_manager.create_interface_element(input_dict)

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
        "modes": ["ministers"],
        "image_id": "buttons/cycle_ministers_up_button.png",
        "init_type": constants.CYCLE_AVAILABLE_MINISTERS_BUTTON,
        "direction": "left",
    }
    cycle_left_button = constants.actor_creation_manager.create_interface_element(
        cycle_input_dict
    )

    for i in range(0, 5):
        available_minister_display_y -= portrait_icon_width + 10
        current_portrait = constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(
                    available_minister_display_x - portrait_icon_width,
                    available_minister_display_y,
                ),
                "width": scaling.scale_width(portrait_icon_width),
                "height": scaling.scale_height(portrait_icon_width),
                "modes": ["ministers"],
                "init_type": constants.MINISTER_PORTRAIT_IMAGE,
                "color": "gray",
                "minister_type": None,
            }
        )

    available_minister_display_y -= 60
    cycle_input_dict["coordinates"] = (
        cycle_input_dict["coordinates"][0],
        scaling.scale_height(available_minister_display_y),
    )
    cycle_input_dict["keybind_id"] = pygame.K_s
    cycle_input_dict["image_id"] = "buttons/cycle_ministers_down_button.png"
    cycle_input_dict["direction"] = "right"
    cycle_right_button = constants.actor_creation_manager.create_interface_element(
        cycle_input_dict
    )


def trial_screen():
    """
    Description:
        Initializes static interface of trial screen
    Input:
        None
    Output:
        None
    """
    trial_display_default_y = 700
    button_separation = 100
    distance_to_center = 300
    distance_to_notification = 100

    defense_y = trial_display_default_y
    defense_x = (
        (constants.default_display_width / 2)
        + (distance_to_center - button_separation)
        + distance_to_notification
    )
    defense_current_y = 0
    status.defense_info_display = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": (defense_x, defense_y),
                "width": 10,
                "height": 10,
                "modes": ["trial"],
                "init_type": constants.ORDERED_COLLECTION,
                "is_info_display": True,
                "actor_type": "defense",
                "allow_minimize": False,
                "allow_move": False,
                "description": "defense information panel",
            }
        )
    )

    defense_type_image = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, defense_current_y),
            "width": scaling.scale_width(button_separation * 2 - 5),
            "height": scaling.scale_height(button_separation * 2 - 5),
            "modes": ["trial"],
            "minister_type": None,
            "attached_label": None,
            "init_type": constants.MINISTER_TYPE_IMAGE,
            "parent_collection": status.defense_info_display,
        }
    )

    defense_current_y -= button_separation * 2
    defense_portrait_image = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, defense_current_y),
            "width": scaling.scale_width(button_separation * 2 - 5),
            "height": scaling.scale_height(button_separation * 2 - 5),
            "init_type": constants.MINISTER_PORTRAIT_IMAGE,
            "minister_type": None,
            "color": "gray",
            "parent_collection": status.defense_info_display,
        }
    )

    defense_current_y -= 35
    input_dict = {
        "coordinates": scaling.scale_coordinates(0, defense_current_y),
        "minimum_width": scaling.scale_width(10),
        "height": scaling.scale_height(30),
        "image_id": "misc/default_label.png",
        "message": "Defense",
        "init_type": constants.LABEL,
        "parent_collection": status.defense_info_display,
    }
    defense_label = constants.actor_creation_manager.create_interface_element(
        input_dict
    )

    input_dict["actor_type"] = "minister"
    del input_dict["message"]
    defense_info_display_labels = [
        constants.MINISTER_NAME_LABEL,
        constants.MINISTER_OFFICE_LABEL,
        constants.EVIDENCE_LABEL,
    ]
    for current_actor_label_type in defense_info_display_labels:
        defense_current_y -= 35
        input_dict["coordinates"] = scaling.scale_coordinates(0, defense_current_y)
        input_dict["init_type"] = current_actor_label_type
        constants.actor_creation_manager.create_interface_element(input_dict)

    prosecution_y = trial_display_default_y
    prosecution_x = (
        (constants.default_display_width / 2)
        - (distance_to_center + button_separation)
        - distance_to_notification
    )
    prosecution_current_y = 0

    status.prosecution_info_display = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": (prosecution_x, prosecution_y),
                "width": 10,
                "height": 10,
                "modes": ["trial"],
                "init_type": constants.ORDERED_COLLECTION,
                "is_info_display": True,
                "actor_type": "prosecution",
                "allow_minimize": False,
                "allow_move": False,
                "description": "prosecution information panel",
            }
        )
    )

    prosecution_type_image = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, prosecution_current_y),
            "width": scaling.scale_width(button_separation * 2 - 5),
            "height": scaling.scale_height(button_separation * 2 - 5),
            "modes": ["trial"],
            "minister_type": None,
            "attached_label": None,
            "init_type": constants.MINISTER_TYPE_IMAGE,
            "parent_collection": status.prosecution_info_display,
        }
    )

    prosecution_current_y -= button_separation * 2
    prosecution_portrait_image = (
        constants.actor_creation_manager.create_interface_element(
            {
                "width": scaling.scale_width(button_separation * 2 - 5),
                "height": scaling.scale_height(button_separation * 2 - 5),
                "init_type": constants.MINISTER_PORTRAIT_IMAGE,
                "minister_type": None,
                "color": "gray",
                "parent_collection": status.prosecution_info_display,
            }
        )
    )

    prosecution_current_y -= 35
    input_dict = {
        "minimum_width": scaling.scale_width(10),
        "height": scaling.scale_height(30),
        "image_id": "misc/default_label.png",
        "message": "Prosecution",
        "init_type": constants.LABEL,
        "parent_collection": status.prosecution_info_display,
    }
    prosecution_label = constants.actor_creation_manager.create_interface_element(
        input_dict
    )

    input_dict["actor_type"] = "minister"
    del input_dict["message"]
    input_dict["parent_collection"] = status.prosecution_info_display
    prosecution_info_display_labels = [
        constants.MINISTER_NAME_LABEL,
        constants.MINISTER_OFFICE_LABEL,
    ]
    for current_actor_label_type in prosecution_info_display_labels:
        prosecution_current_y -= 35
        input_dict["coordinates"] = scaling.scale_coordinates(0, prosecution_current_y)
        input_dict["init_type"] = current_actor_label_type
        constants.actor_creation_manager.create_interface_element(input_dict)

    bribed_judge_indicator = constants.actor_creation_manager.create_interface_element(
        {
            "image_id": "misc/bribed_judge.png",
            "coordinates": scaling.scale_coordinates(
                (constants.default_display_width / 2)
                - ((button_separation * 2 - 5) / 2),
                trial_display_default_y,
            ),
            "width": scaling.scale_width(button_separation * 2 - 5),
            "height": scaling.scale_height(button_separation * 2 - 5),
            "modes": ["trial"],
            "indicator_type": "prosecution_bribed_judge",
            "init_type": constants.INDICATOR_IMAGE,
        }
    )

    non_bribed_judge_indicator = (
        constants.actor_creation_manager.create_interface_element(
            {
                "image_id": "misc/non_bribed_judge.png",
                "coordinates": scaling.scale_coordinates(
                    (constants.default_display_width / 2)
                    - ((button_separation * 2 - 5) / 2),
                    trial_display_default_y,
                ),
                "width": scaling.scale_width(button_separation * 2 - 5),
                "height": scaling.scale_height(button_separation * 2 - 5),
                "modes": ["trial"],
                "indicator_type": "not prosecution_bribed_judge",
                "init_type": constants.INDICATOR_IMAGE,
            }
        )
    )


def new_game_setup_screen():
    """
    Description:
        Initializes new game setup screen interface
    Input:
        None
    Output:
        None
    """
    current_index = 0
    image_width = 300
    image_height = 200
    separation = 50
    per_row = 3
    # input_dict = {
    #     "width": scaling.scale_width(image_width),
    #     "height": scaling.scale_height(image_height),
    #     "modes": ["new_game_setup"],
    #     "init_type": "___ selection image",
    # }
    """
        input_dict["coordinates"] = scaling.scale_coordinates(
            (constants.default_display_width / 2)
            - (countries_per_row * (image_width + separation) / 2)
            + (image_width + separation)
            * (current_index % countries_per_row)
            + separation / 2,
            constants.default_display_height / 2
            + 50
            - (
                (image_height + separation)
                * (index // countries_per_row)
            ),
        )
        constants.actor_creation_manager.create_interface_element(input_dict)
        current_index += 1
    """


def mob_interface():
    """
    Description:
        Initializes mob selection interface
    Input:
        None
    Output:
        None
    """
    actor_display_top_y = constants.default_display_height - 205 + 125 + 10
    actor_display_current_y = actor_display_top_y
    constants.mob_ordered_list_start_y = actor_display_current_y

    status.mob_info_display = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, 0),
            "width": scaling.scale_width(400),
            "height": scaling.scale_height(430),
            "modes": ["strategic", "earth"],
            "init_type": constants.ORDERED_COLLECTION,
            "is_info_display": True,
            "actor_type": "mob",
            "description": "unit information panel",
            "parent_collection": status.info_displays_collection,
            #'resize_with_contents': True, #need to get resize to work with info displays - would prevent invisible things from taking space
            # - collection with 5 width/height should still take space because of its member rects - the fact that this is not happening means something about resizing is not working
        }
    )

    # mob background image's tooltip
    mob_free_image_background_tooltip = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(0, 0),
                "minimum_width": scaling.scale_width(115),
                "height": scaling.scale_height(115),
                "image_id": "misc/empty.png",
                "actor_type": "mob",
                "init_type": constants.ACTOR_TOOLTIP_LABEL,
                "parent_collection": status.mob_info_display,
                "member_config": {"order_overlap": True},
            }
        )
    )

    # mob image
    mob_free_image = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, 0),
            "width": scaling.scale_width(115),
            "height": scaling.scale_height(115),
            "modes": ["strategic", "earth"],
            "actor_image_type": "default",
            "init_type": constants.ACTOR_DISPLAY_FREE_IMAGE,
            "parent_collection": status.mob_info_display,
            "member_config": {"order_overlap": False},
        }
    )

    input_dict = {
        "coordinates": scaling.scale_coordinates(125, -115),
        "width": scaling.scale_width(35),
        "height": scaling.scale_height(35),
        "modes": ["strategic", "earth"],
        "image_id": "buttons/remove_minister_button.png",
        "init_type": constants.FIRE_UNIT_BUTTON,
        "parent_collection": status.mob_info_display,
        "member_config": {"order_exempt": True},
    }
    fire_unit_button = constants.actor_creation_manager.create_interface_element(
        input_dict
    )

    left_arrow_button = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(200, -105),
            "width": scaling.scale_width(40),
            "height": scaling.scale_height(40),
            "modes": ["strategic", "earth"],
            "keybind_id": pygame.K_a,
            "image_id": "buttons/left_button.png",
            "init_type": constants.MOVE_LEFT_BUTTON,
            "parent_collection": status.mob_info_display,
            "member_config": {"order_exempt": True},
        }
    )
    down_arrow_button = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(245, -105),
            "width": scaling.scale_width(40),
            "height": scaling.scale_height(40),
            "modes": ["strategic", "earth"],
            "keybind_id": pygame.K_s,
            "image_id": "buttons/down_button.png",
            "init_type": constants.MOVE_DOWN_BUTTON,
            "parent_collection": status.mob_info_display,
            "member_config": {"order_exempt": True},
        }
    )

    up_arrow_button = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(245, -60),
            "width": scaling.scale_width(40),
            "height": scaling.scale_height(40),
            "modes": ["strategic", "earth"],
            "keybind_id": pygame.K_w,
            "image_id": "buttons/up_button.png",
            "init_type": constants.MOVE_UP_BUTTON,
            "parent_collection": status.mob_info_display,
            "member_config": {"order_exempt": True},
        }
    )

    right_arrow_button = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(290, -105),
            "width": scaling.scale_width(40),
            "height": scaling.scale_height(40),
            "modes": ["strategic", "earth"],
            "keybind_id": pygame.K_d,
            "image_id": "buttons/right_button.png",
            "init_type": constants.MOVE_RIGHT_BUTTON,
            "parent_collection": status.mob_info_display,
            "member_config": {"order_exempt": True},
        }
    )

    # mob info labels setup
    for current_actor_label_type in [
        constants.NAME_LABEL,
        constants.MINISTER_LABEL,
        constants.OFFICER_LABEL,
        constants.WORKERS_LABEL,
        constants.MOVEMENT_LABEL,
        constants.COMBAT_STRENGTH_LABEL,
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
        elif current_actor_label_type == constants.CURRENT_PASSENGER_LABEL:
            x_displacement = 30
        else:
            x_displacement = 0
        input_dict = {  # should declare here to reinitialize dict and prevent extra parameters from being incorrectly retained between iterations
            "coordinates": scaling.scale_coordinates(0, 0),
            "minimum_width": scaling.scale_width(10),
            "height": scaling.scale_height(30),
            "image_id": "misc/default_label.png",
            "init_type": current_actor_label_type,
            "actor_type": "mob",
            "parent_collection": status.mob_info_display,
            "member_config": {"order_x_offset": x_displacement},
        }
        if current_actor_label_type != constants.CURRENT_PASSENGER_LABEL:
            constants.actor_creation_manager.create_interface_element(input_dict)
        else:
            input_dict["list_type"] = constants.SHIP
            for i in range(0, 3):  # 0, 1, 2
                # label for each passenger
                input_dict["list_index"] = i
                constants.actor_creation_manager.create_interface_element(input_dict)

    tab_collection_relative_coordinates = (450, -30)
    status.mob_tabbed_collection = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(
                    tab_collection_relative_coordinates[0],
                    tab_collection_relative_coordinates[1],
                ),
                "width": scaling.scale_width(10),
                "height": scaling.scale_height(30),
                "init_type": constants.TABBED_COLLECTION,
                "parent_collection": status.mob_info_display,
                "member_config": {"order_exempt": True},
                "description": "unit information tabs",
            }
        )
    )


def tile_interface():
    """
    Description:
        Initializes tile selection interface
    Input:
        None
    Output:
        None
    """
    status.tile_info_display = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(0, 0),
                "width": scaling.scale_width(775),
                "height": scaling.scale_height(10),
                "modes": ["strategic", "earth"],
                "init_type": constants.ORDERED_COLLECTION,
                "is_info_display": True,
                "actor_type": "tile",
                "description": "tile information panel",
                "parent_collection": status.info_displays_collection,
            }
        )
    )

    separation = scaling.scale_height(3)
    same_tile_ordered_collection = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(120, 0),
                "width": 10,
                "height": 10,
                "init_type": constants.ORDERED_COLLECTION,
                "parent_collection": status.tile_info_display,
                "member_config": {"order_exempt": True},
                "separation": separation,
            }
        )
    )

    input_dict = {
        "coordinates": (0, 0),
        "width": scaling.scale_width(25),
        "height": scaling.scale_height(25),
        "modes": ["strategic", "earth"],
        "init_type": constants.SAME_TILE_ICON,
        "image_id": "buttons/default_button.png",
        "is_last": False,
        "color": "gray",
        "parent_collection": same_tile_ordered_collection,
    }

    for i in range(0, 3):  # add button to cycle through
        input_dict["index"] = i
        same_tile_icon = constants.actor_creation_manager.create_interface_element(
            input_dict
        )

    same_tile_icon = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": (0, 0),
            "width": scaling.scale_width(25),
            "height": scaling.scale_height(15),
            "modes": ["strategic", "earth"],
            "init_type": constants.SAME_TILE_ICON,
            "image_id": "buttons/default_button.png",
            "index": 3,
            "is_last": True,
            "color": "gray",
            "parent_collection": same_tile_ordered_collection,
        }
    )

    cycle_same_tile_button = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, separation),
            "width": scaling.scale_width(25),
            "height": scaling.scale_height(15),
            "modes": ["strategic", "earth"],
            "image_id": "buttons/cycle_passengers_down_button.png",
            "init_type": constants.CYCLE_SAME_TILE_BUTTON,
            "parent_collection": same_tile_ordered_collection,
        }
    )

    # tile background image's tooltip
    tile_free_image_background_tooltip = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(0, 0),
                "minimum_width": scaling.scale_width(115),
                "height": scaling.scale_height(115),
                "image_id": "misc/empty.png",
                "actor_type": "tile",
                "init_type": constants.ACTOR_TOOLTIP_LABEL,
                "parent_collection": status.tile_info_display,
                "member_config": {"order_overlap": True},
            }
        )
    )

    tile_image = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(5, 5),
            "width": scaling.scale_width(115),
            "height": scaling.scale_height(115),
            "modes": ["strategic", "earth"],
            "actor_image_type": "default",
            "init_type": constants.ACTOR_DISPLAY_FREE_IMAGE,
            "parent_collection": status.tile_info_display,
            "member_config": {"order_overlap": False},
        }
    )

    # tile info labels setup
    tile_info_display_labels = [
        constants.COORDINATES_LABEL,
        constants.KNOWLEDGE_LABEL,
        constants.TERRAIN_LABEL,
        constants.BANNER_LABEL,
        constants.WATER_LABEL,
        constants.TEMPERATURE_LABEL,
        constants.VEGETATION_LABEL,
        constants.ROUGHNESS_LABEL,
        constants.SOIL_LABEL,
        constants.ALTITUDE_LABEL,
        constants.RESOURCE_LABEL,
        constants.TERRAIN_FEATURE_LABEL,
    ]
    for current_actor_label_type in tile_info_display_labels:
        if (
            current_actor_label_type
            in [
                constants.TERRAIN_FEATURE_LABEL,
                constants.TERRAIN_LABEL,
                constants.BANNER_LABEL,
            ]
            + constants.terrain_parameters
            and current_actor_label_type != constants.KNOWLEDGE_LABEL
        ):
            x_displacement = 25
        else:
            x_displacement = 0
        input_dict = {
            "minimum_width": scaling.scale_width(10),
            "height": scaling.scale_height(30),
            "image_id": "misc/default_label.png",
            "init_type": current_actor_label_type,
            "actor_type": "tile",
            "parent_collection": status.tile_info_display,
            "member_config": {"order_x_offset": scaling.scale_width(x_displacement)},
        }
        if current_actor_label_type == constants.TERRAIN_FEATURE_LABEL:
            for key, terrain_feature_type in status.terrain_feature_types.items():
                if terrain_feature_type.visible:
                    input_dict["terrain_feature_type"] = key
                    constants.actor_creation_manager.create_interface_element(
                        input_dict
                    )
        elif current_actor_label_type == constants.BANNER_LABEL:
            input_dict["banner_type"] = "terrain details"
            input_dict["banner_text"] = "Details unknown"
            constants.actor_creation_manager.create_interface_element(input_dict)
        else:
            constants.actor_creation_manager.create_interface_element(input_dict)

    tab_collection_relative_coordinates = (450, -30)

    status.tile_tabbed_collection = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(
                    tab_collection_relative_coordinates[0],
                    tab_collection_relative_coordinates[1],
                ),
                "width": scaling.scale_width(10),
                "height": scaling.scale_height(30),
                "init_type": constants.TABBED_COLLECTION,
                "parent_collection": status.tile_info_display,
                "member_config": {"order_exempt": True},
                "description": "tile information tabs",
            }
        )
    )


def inventory_interface():
    """
    Description:
        Initializes the commodity prices display and both mob/tile tabbed collections and inventory interfaces
    Input:
        None
    Output:
        None
    """
    commodity_prices_x, commodity_prices_y = (900, 100)
    commodity_prices_height = 35 + (30 * len(constants.commodity_types))
    commodity_prices_width = 200

    status.commodity_prices_label = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(
                    commodity_prices_x, commodity_prices_y
                ),
                "minimum_width": scaling.scale_width(commodity_prices_width),
                "height": scaling.scale_height(commodity_prices_height),
                "modes": ["earth"],
                "image_id": "misc/commodity_prices_label.png",
                "init_type": constants.COMMODITY_PRICES_LABEL,
            }
        )
    )

    input_dict = {
        "width": scaling.scale_width(30),
        "height": scaling.scale_height(30),
        "modes": ["earth"],
        "init_type": constants.COMMODITY_BUTTON,
    }
    for current_index in range(
        len(constants.commodity_types)
    ):  # commodity prices on Earth
        input_dict["coordinates"] = scaling.scale_coordinates(
            commodity_prices_x - 35,
            commodity_prices_y + commodity_prices_height - 65 - (30 * current_index),
        )
        input_dict["image_id"] = [
            "misc/green_circle.png",
            "items/" + constants.commodity_types[current_index] + ".png",
        ]
        input_dict["commodity"] = constants.commodity_types[current_index]
        new_commodity_button = (
            constants.actor_creation_manager.create_interface_element(input_dict)
        )

    status.mob_inventory_collection = (
        constants.actor_creation_manager.create_interface_element(
            {
                "width": scaling.scale_width(10),
                "height": scaling.scale_height(30),
                "init_type": constants.ORDERED_COLLECTION,
                "parent_collection": status.mob_tabbed_collection,
                "member_config": {
                    "tabbed": True,
                    "button_image_id": [
                        "buttons/default_button_alt2.png",
                        {"image_id": "misc/green_circle.png", "size": 0.75},
                        {"image_id": "items/consumer goods.png", "size": 0.75},
                    ],
                    "identifier": constants.INVENTORY_PANEL,
                },
                "description": "unit inventory panel",
            }
        )
    )

    input_dict = {
        "minimum_width": scaling.scale_width(10),
        "height": scaling.scale_height(30),
        "image_id": "misc/default_label.png",
        "init_type": constants.MOB_INVENTORY_CAPACITY_LABEL,
        "actor_type": "mob",
        "parent_collection": status.mob_inventory_collection,
    }
    mob_inventory_capacity_label = (
        constants.actor_creation_manager.create_interface_element(input_dict)
    )

    inventory_cell_height = scaling.scale_height(34)
    inventory_cell_width = scaling.scale_width(34)

    status.mob_inventory_grid = (
        constants.actor_creation_manager.create_interface_element(
            {
                "width": scaling.scale_width(10),
                "height": (inventory_cell_height + scaling.scale_height(5)) * 3,
                "init_type": constants.INVENTORY_GRID,
                "parent_collection": status.mob_inventory_collection,
                "second_dimension_increment": inventory_cell_width
                + scaling.scale_height(5),
            }
        )
    )
    for current_index in range(27):
        constants.actor_creation_manager.create_interface_element(
            {
                "width": inventory_cell_width,
                "height": inventory_cell_height,
                "image_id": "buttons/default_button.png",
                "init_type": constants.ITEM_ICON,
                "parent_collection": status.mob_inventory_grid,
                "icon_index": current_index,
                "actor_type": "mob_inventory",
                "member_config": {
                    "second_dimension_coordinate": current_index % 9,
                    "order_y_offset": status.mob_inventory_grid.height,
                },
            }
        )

    status.mob_inventory_info_display = (
        constants.actor_creation_manager.create_interface_element(
            {
                "width": scaling.scale_width(10),
                "height": scaling.scale_height(30),
                "init_type": constants.ORDERED_COLLECTION,
                "is_info_display": True,
                "actor_type": "mob_inventory",
                "description": "mob inventory panel",
                "parent_collection": status.mob_inventory_collection,
                "member_config": {"calibrate_exempt": True},
            }
        )
    )

    # mob inventory background image's tooltip
    mob_inventory_free_image_background_tooltip = (
        constants.actor_creation_manager.create_interface_element(
            {
                "minimum_width": scaling.scale_width(90),
                "height": scaling.scale_height(90),
                "image_id": "misc/empty.png",
                "init_type": constants.ACTOR_TOOLTIP_LABEL,
                "actor_type": "tile",
                "parent_collection": status.mob_inventory_info_display,
                "member_config": {"order_overlap": True},
            }
        )
    )

    mob_inventory_image = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(5, 5),
            "width": scaling.scale_width(90),
            "height": scaling.scale_height(90),
            "modes": ["strategic", "earth"],
            "actor_image_type": "inventory_default",
            "init_type": constants.ACTOR_DISPLAY_FREE_IMAGE,
            "parent_collection": status.mob_inventory_info_display,
            "member_config": {"order_overlap": False},
        }
    )

    mob_info_display_labels = [
        constants.INVENTORY_NAME_LABEL,
        constants.INVENTORY_QUANTITY_LABEL,
    ]
    for current_actor_label_type in mob_info_display_labels:
        x_displacement = 0
        input_dict = {
            "minimum_width": scaling.scale_width(10),
            "height": scaling.scale_height(30),
            "image_id": "misc/default_label.png",
            "init_type": current_actor_label_type,
            "actor_type": "mob",
            "parent_collection": status.mob_inventory_info_display,
            "member_config": {"order_x_offset": scaling.scale_width(x_displacement)},
        }
        constants.actor_creation_manager.create_interface_element(input_dict)

    status.tile_inventory_collection = (
        constants.actor_creation_manager.create_interface_element(
            {
                "width": scaling.scale_width(10),
                "height": scaling.scale_height(30),
                "init_type": constants.ORDERED_COLLECTION,
                "parent_collection": status.tile_tabbed_collection,
                "member_config": {
                    "tabbed": True,
                    "button_image_id": [
                        "buttons/default_button_alt2.png",
                        {"image_id": "misc/green_circle.png", "size": 0.75},
                        {"image_id": "items/consumer goods.png", "size": 0.75},
                    ],
                    "identifier": constants.INVENTORY_PANEL,
                },
                "description": "tile inventory panel",
            }
        )
    )

    input_dict = {
        "minimum_width": scaling.scale_width(10),
        "height": scaling.scale_height(30),
        "image_id": "misc/default_label.png",
        "init_type": constants.TILE_INVENTORY_CAPACITY_LABEL,
        "actor_type": "tile",
        "parent_collection": status.tile_inventory_collection,
    }
    tile_inventory_capacity_label = (
        constants.actor_creation_manager.create_interface_element(input_dict)
    )

    status.tile_inventory_grid = (
        constants.actor_creation_manager.create_interface_element(
            {
                "width": scaling.scale_width(10),
                "height": (inventory_cell_height + scaling.scale_height(5)) * 3,
                "init_type": constants.INVENTORY_GRID,
                "parent_collection": status.tile_inventory_collection,
                "second_dimension_increment": inventory_cell_width
                + scaling.scale_height(5),
            }
        )
    )

    tile_scroll_up_button = constants.actor_creation_manager.create_interface_element(
        {
            "width": inventory_cell_width,
            "height": inventory_cell_height,
            "parent_collection": status.tile_inventory_grid,
            "image_id": "buttons/cycle_ministers_up_button.png",
            "value_name": "inventory_page",
            "increment": -1,
            "member_config": {
                "order_exempt": True,
                "x_offset": scaling.scale_width(-1.3 * inventory_cell_width),
                "y_offset": status.tile_inventory_grid.height
                - ((inventory_cell_height + scaling.scale_height(5)) * 3)
                + scaling.scale_height(5),
            },
            "init_type": constants.SCROLL_BUTTON,
        }
    )

    tile_scroll_down_button = constants.actor_creation_manager.create_interface_element(
        {
            "width": inventory_cell_width,
            "height": inventory_cell_height,
            "parent_collection": status.tile_inventory_grid,
            "image_id": "buttons/cycle_ministers_down_button.png",
            "value_name": "inventory_page",
            "increment": 1,
            "member_config": {
                "order_exempt": True,
                "x_offset": scaling.scale_width(-1.3 * inventory_cell_width),
                "y_offset": status.tile_inventory_grid.height - (inventory_cell_height),
            },
            "init_type": constants.SCROLL_BUTTON,
        }
    )

    for current_index in range(27):
        constants.actor_creation_manager.create_interface_element(
            {
                "width": inventory_cell_width,
                "height": inventory_cell_height,
                "image_id": "buttons/default_button.png",
                "init_type": constants.ITEM_ICON,
                "parent_collection": status.tile_inventory_grid,
                "icon_index": current_index,
                "actor_type": "tile_inventory",
                "member_config": {
                    "second_dimension_coordinate": current_index % 9,
                    "order_y_offset": status.tile_inventory_grid.height,
                },
            }
        )

    status.tile_inventory_info_display = (
        constants.actor_creation_manager.create_interface_element(
            {
                "width": scaling.scale_width(10),
                "height": scaling.scale_height(30),
                "init_type": constants.ORDERED_COLLECTION,
                "is_info_display": True,
                "actor_type": "tile_inventory",
                "description": "tile inventory panel",
                "parent_collection": status.tile_inventory_collection,
                "member_config": {"calibrate_exempt": True},
            }
        )
    )

    # tile inventory background image's tooltip
    tile_inventory_free_image_background_tooltip = (
        constants.actor_creation_manager.create_interface_element(
            {
                "minimum_width": scaling.scale_width(90),
                "height": scaling.scale_height(90),
                "image_id": "misc/empty.png",
                "actor_type": "tile",
                "init_type": constants.ACTOR_TOOLTIP_LABEL,
                "parent_collection": status.tile_inventory_info_display,
                "member_config": {"order_overlap": True},
            }
        )
    )

    tile_inventory_image = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(5, 5),
            "width": scaling.scale_width(90),
            "height": scaling.scale_height(90),
            "modes": ["strategic", "earth"],
            "actor_image_type": "inventory_default",
            "init_type": constants.ACTOR_DISPLAY_FREE_IMAGE,
            "parent_collection": status.tile_inventory_info_display,
            "member_config": {"order_overlap": False},
        }
    )

    tile_info_display_labels = [
        constants.INVENTORY_NAME_LABEL,
        constants.INVENTORY_QUANTITY_LABEL,
    ]
    for current_actor_label_type in tile_info_display_labels:
        x_displacement = 0
        input_dict = {
            "minimum_width": scaling.scale_width(10),
            "height": scaling.scale_height(30),
            "image_id": "misc/default_label.png",
            "init_type": current_actor_label_type,
            "actor_type": "tile",
            "parent_collection": status.tile_inventory_info_display,
            "member_config": {"order_x_offset": scaling.scale_width(x_displacement)},
        }
        constants.actor_creation_manager.create_interface_element(input_dict)


def settlement_interface():
    """
    Description:
        Initializes the settlement interface as part of the tile tabbed collection
    Input:
        None
    Output:
        None
    """
    status.settlement_collection = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(0, 0),
                "width": scaling.scale_width(10),
                "height": scaling.scale_height(30),
                "init_type": constants.ORDERED_COLLECTION,
                "parent_collection": status.tile_tabbed_collection,
                "member_config": {
                    "tabbed": True,
                    "button_image_id": "buttons/crew_train_button.png",
                    "identifier": constants.SETTLEMENT_PANEL,
                },
                "description": "settlement panel",
            }
        )
    )
    settlement_info_display_labels = [
        constants.SETTLEMENT,
        constants.PORT,
        constants.TRAIN_STATION,
        constants.RESOURCE,
        constants.BUILDING_EFFICIENCY_LABEL,
        constants.BUILDING_WORK_CREWS_LABEL,
        constants.CURRENT_BUILDING_WORK_CREW_LABEL,
        constants.FORT,
        constants.SLUMS,
        constants.INFRASTRUCTURE,
    ]
    for current_actor_label_type in settlement_info_display_labels:
        if current_actor_label_type in [
            constants.SETTLEMENT,
            constants.INFRASTRUCTURE,
        ]:  # Left align any top-level buildings
            x_displacement = 0
        elif current_actor_label_type == constants.CURRENT_BUILDING_WORK_CREW_LABEL:
            x_displacement = 75
        elif current_actor_label_type in [
            constants.BUILDING_EFFICIENCY_LABEL,
            constants.BUILDING_WORK_CREWS_LABEL,
        ]:
            x_displacement = 50
        else:
            x_displacement = 25
        input_dict = {
            "minimum_width": scaling.scale_width(10),
            "height": scaling.scale_height(30),
            "image_id": "misc/default_label.png",
            "actor_label_type": current_actor_label_type,
            "actor_type": "tile",
            "parent_collection": status.settlement_collection,
            "member_config": {"order_x_offset": scaling.scale_width(x_displacement)},
        }

        if current_actor_label_type == constants.BUILDING_EFFICIENCY_LABEL:
            input_dict["init_type"] = constants.BUILDING_EFFICIENCY_LABEL
            input_dict["building_type"] = constants.RESOURCE
            constants.actor_creation_manager.create_interface_element(input_dict)
        elif current_actor_label_type == constants.BUILDING_WORK_CREWS_LABEL:
            input_dict["init_type"] = constants.BUILDING_WORK_CREWS_LABEL
            input_dict["building_type"] = constants.RESOURCE
            constants.actor_creation_manager.create_interface_element(input_dict)
        elif current_actor_label_type == constants.CURRENT_BUILDING_WORK_CREW_LABEL:
            input_dict["init_type"] = constants.LIST_ITEM_LABEL
            input_dict["list_type"] = constants.RESOURCE
            for i in range(0, 3):
                input_dict["list_index"] = i
                constants.actor_creation_manager.create_interface_element(input_dict)
        else:
            input_dict["init_type"] = constants.ACTOR_DISPLAY_LABEL
            constants.actor_creation_manager.create_interface_element(input_dict)


def unit_organization_interface():
    """
    Description:
        Initializes the unit organization interface as part of the mob tabbed collection
    Input:
        None
    Output:
        None
    """
    image_height = 75
    lhs_x_offset = 35
    rhs_x_offset = image_height + 80

    status.mob_reorganization_collection = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(-30, -1 * image_height - 115),
                "width": scaling.scale_width(10),
                "height": scaling.scale_height(30),
                "init_type": constants.AUTOFILL_COLLECTION,
                "parent_collection": status.mob_tabbed_collection,
                "member_config": {
                    "tabbed": True,
                    "button_image_id": "buttons/merge_button.png",
                    "identifier": constants.REORGANIZATION_PANEL,
                },
                "description": "unit organization panel",
                "direction": "horizontal",
                "autofill_targets": {"officer": [], "worker": [], "group": []},
            }
        )
    )

    # mob background image's tooltip
    lhs_top_tooltip = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(lhs_x_offset, 0),
            "minimum_width": scaling.scale_width(image_height - 10),
            "height": scaling.scale_height(image_height - 10),
            "image_id": "misc/empty.png",
            "actor_type": "mob",
            "init_type": constants.ACTOR_TOOLTIP_LABEL,
            "parent_collection": status.mob_reorganization_collection,
            "member_config": {"calibrate_exempt": True},
        }
    )
    status.mob_reorganization_collection.autofill_targets["officer"].append(
        lhs_top_tooltip
    )

    # mob image
    lhs_top_mob_free_image = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, 0),
            "width": scaling.scale_width(image_height - 10),
            "height": scaling.scale_height(image_height - 10),
            "modes": ["strategic", "earth"],
            "actor_image_type": "default",
            "default_image_id": "mobs/default/mock_officer.png",
            "init_type": constants.ACTOR_DISPLAY_FREE_IMAGE,
            "parent_collection": status.mob_reorganization_collection,
            "member_config": {
                "calibrate_exempt": True,
                "x_offset": scaling.scale_width(lhs_x_offset),
            },
        }
    )
    status.mob_reorganization_collection.autofill_targets["officer"].append(
        lhs_top_mob_free_image
    )

    # mob background image's tooltip
    lhs_bottom_tooltip = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(
                lhs_x_offset, -1 * (image_height - 5)
            ),
            "minimum_width": scaling.scale_width(image_height - 10),
            "height": scaling.scale_height(image_height - 10),
            "image_id": "misc/empty.png",
            "actor_type": "mob",
            "init_type": constants.ACTOR_TOOLTIP_LABEL,
            "parent_collection": status.mob_reorganization_collection,
            "member_config": {"calibrate_exempt": True},
        }
    )
    status.mob_reorganization_collection.autofill_targets["worker"].append(
        lhs_bottom_tooltip
    )

    # mob image
    default_image_id = [
        actor_utility.generate_unit_component_image_id(
            "mobs/default/mock_worker.png", "left", to_front=True
        ),
        actor_utility.generate_unit_component_image_id(
            "mobs/default/mock_worker.png", "right", to_front=True
        ),
    ]
    lhs_bottom_mob_free_image = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(0, 0),
                "width": scaling.scale_width(image_height - 10),
                "height": scaling.scale_height(image_height - 10),
                "modes": ["strategic", "earth"],
                "actor_image_type": "default",
                "default_image_id": default_image_id,
                "init_type": constants.ACTOR_DISPLAY_FREE_IMAGE,
                "parent_collection": status.mob_reorganization_collection,
                "member_config": {
                    "calibrate_exempt": True,
                    "x_offset": scaling.scale_width(lhs_x_offset),
                    "y_offset": scaling.scale_height(-1 * (image_height - 5)),
                },
            }
        )
    )
    status.mob_reorganization_collection.autofill_targets["worker"].append(
        lhs_bottom_mob_free_image
    )

    # right side
    # mob background image's tooltip
    rhs_top_tooltip = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, 0),
            "minimum_width": scaling.scale_width(image_height - 10),
            "height": scaling.scale_height(image_height - 10),
            "image_id": "misc/empty.png",
            "actor_type": "mob",
            "init_type": constants.ACTOR_TOOLTIP_LABEL,
            "parent_collection": status.mob_reorganization_collection,
            "member_config": {
                "calibrate_exempt": True,
                "x_offset": scaling.scale_width(lhs_x_offset + rhs_x_offset),
                "y_offset": scaling.scale_height(-0.5 * (image_height)),
            },
        }
    )
    status.mob_reorganization_collection.autofill_targets["group"].append(
        rhs_top_tooltip
    )

    # mob image
    default_image_id = [
        actor_utility.generate_unit_component_image_id(
            "mobs/default/mock_worker.png", "group left", to_front=True
        )
    ]
    default_image_id.append(
        actor_utility.generate_unit_component_image_id(
            "mobs/default/mock_worker.png", "group right", to_front=True
        )
    )
    default_image_id.append(
        actor_utility.generate_unit_component_image_id(
            "mobs/default/mock_officer.png", "center", to_front=True
        )
    )
    rhs_top_mob_free_image = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, 0),
            "width": scaling.scale_width(image_height - 10),
            "height": scaling.scale_height(image_height - 10),
            "modes": ["strategic", "earth"],
            "actor_image_type": "default",
            "default_image_id": default_image_id,
            "init_type": constants.ACTOR_DISPLAY_FREE_IMAGE,
            "parent_collection": status.mob_reorganization_collection,
            "member_config": {
                "calibrate_exempt": True,
                "x_offset": scaling.scale_width(lhs_x_offset + rhs_x_offset),
                "y_offset": scaling.scale_height(-0.5 * (image_height)),
            },
        }
    )
    status.mob_reorganization_collection.autofill_targets["group"].append(
        rhs_top_mob_free_image
    )

    # reorganize unit to right button
    status.reorganize_unit_right_button = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(
                    lhs_x_offset + rhs_x_offset - 60 - 15,
                    -1 * (image_height - 15) + 40 - 15 + 30 + 5,
                ),
                "width": scaling.scale_width(60),
                "height": scaling.scale_height(25),
                "init_type": constants.REORGANIZE_UNIT_BUTTON,
                "parent_collection": status.mob_reorganization_collection,
                "image_id": "buttons/cycle_units_button.png",
                "allowed_procedures": [
                    constants.MERGE_PROCEDURE,
                    constants.CREW_PROCEDURE,
                ],
                "keybind_id": pygame.K_m,
                "enable_shader": True,
            }
        )
    )

    # reorganize unit to left button
    status.reorganize_unit_left_button = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(
                    lhs_x_offset + rhs_x_offset - 60 - 15,
                    -1 * (image_height - 15) + 40 - 15 + 5,
                ),
                "width": scaling.scale_width(60),
                "height": scaling.scale_height(25),
                "init_type": constants.REORGANIZE_UNIT_BUTTON,
                "parent_collection": status.mob_reorganization_collection,
                "image_id": "buttons/cycle_units_reverse_button.png",
                "allowed_procedures": [
                    constants.SPLIT_PROCEDURE,
                    constants.UNCREW_PROCEDURE,
                ],
                "keybind_id": pygame.K_n,
                "enable_shader": True,
            }
        )
    )

    input_dict = {
        "coordinates": scaling.scale_coordinates(
            lhs_x_offset - 35, -1 * (image_height - 15) + 95 - 35 / 2
        ),
        "width": scaling.scale_width(30),
        "height": scaling.scale_height(30),
        "init_type": constants.CYCLE_AUTOFILL_BUTTON,
        "parent_collection": status.mob_reorganization_collection,
        "image_id": "buttons/reset_button.png",
        "autofill_target_type": "officer",
    }
    cycle_autofill_officer_button = (
        constants.actor_creation_manager.create_interface_element(input_dict)
    )

    input_dict = {
        "coordinates": scaling.scale_coordinates(
            lhs_x_offset - 35, -1 * (image_height - 15) + 25 - 35 / 2
        ),
        "width": input_dict["width"],  # copies most attributes from previous button
        "height": input_dict["height"],
        "init_type": input_dict["init_type"],
        "parent_collection": input_dict["parent_collection"],
        "image_id": input_dict["image_id"],
        "autofill_target_type": "worker",
    }
    cycle_autofill_worker_button = (
        constants.actor_creation_manager.create_interface_element(input_dict)
    )


def minister_interface():
    """
    Description:
        Initializes minister selection interface
    Input:
        None
    Output:
        int actor_display_current_y: Value that tracks the location of interface as it is created, used by other setup functions
    """
    # minister info images setup
    minister_display_top_y = constants.mob_ordered_list_start_y
    minister_display_current_y = 0

    status.minister_info_display = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": (5, -5),
                "width": 10,
                "height": 10,
                "modes": ["ministers"],
                "init_type": constants.ORDERED_COLLECTION,
                "is_info_display": True,
                "actor_type": "minister",
                "allow_minimize": False,
                "allow_move": False,
                "description": "minister information panel",
                "parent_collection": status.info_displays_collection,
            }
        )
    )

    # minister background image
    minister_free_image_background = (
        constants.actor_creation_manager.create_interface_element(
            {
                "image_id": "misc/mob_background.png",
                "coordinates": scaling.scale_coordinates(0, 0),
                "width": scaling.scale_width(125),
                "height": scaling.scale_height(125),
                "modes": ["ministers"],
                "init_type": constants.MINISTER_BACKGROUND_IMAGE,
                "parent_collection": status.minister_info_display,
                "member_config": {"order_overlap": True},
            }
        )
    )

    # minister image
    minister_free_image = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, 0),
            "width": scaling.scale_width(115),
            "height": scaling.scale_height(115),
            "modes": ["ministers"],
            "actor_image_type": "minister_default",
            "init_type": constants.ACTOR_DISPLAY_FREE_IMAGE,
            "parent_collection": status.minister_info_display,
            "member_config": {
                "order_overlap": True,
                "order_x_offset": 5,
                "order_y_offset": -5,
            },
        }
    )

    # minister background image's tooltip
    minister_free_image_background_tooltip = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(0, minister_display_current_y),
                "minimum_width": scaling.scale_width(125),
                "height": scaling.scale_height(125),
                "image_id": "misc/empty.png",
                "actor_type": "minister",
                "init_type": constants.ACTOR_TOOLTIP_LABEL,
                "parent_collection": status.minister_info_display,
                "member_config": {"order_overlap": False},
            }
        )
    )

    minister_display_current_y -= 35
    # minister info images setup

    input_dict = {
        "coordinates": scaling.scale_coordinates(0, 0),
        "minimum_width": scaling.scale_width(10),
        "height": scaling.scale_height(30),
        "image_id": "misc/default_label.png",
        "actor_type": "minister",
        "init_type": constants.ACTOR_DISPLAY_LABEL,
        "parent_collection": status.minister_info_display,
    }

    # minister info labels setup
    for current_actor_label_type in [
        constants.MINISTER_NAME_LABEL,
        constants.MINISTER_OFFICE_LABEL,
        constants.MINISTER_BACKGROUND_LABEL,
        constants.MINISTER_SOCIAL_STATUS_LABEL,
        constants.MINISTER_INTERESTS_LABEL,
        constants.MINISTER_LOYALTY_LABEL,
        constants.MINISTER_ABILITY_LABEL,
        constants.MILITARY_SKILL_LABEL,
        constants.RELIGION_SKILL_LABEL,
        constants.TRADE_SKILL_LABEL,
        constants.EXPLORATION_SKILL_LABEL,
        constants.CONSTRUCTION_SKILL_LABEL,
        constants.PRODUCTION_SKILL_LABEL,
        constants.TRANSPORTATION_SKILL_LABEL,
        constants.PROSECUTION_SKILL_LABEL,
        constants.EVIDENCE_LABEL,
    ]:
        if current_actor_label_type in [
            constants.MILITARY_SKILL_LABEL,
            constants.RELIGION_SKILL_LABEL,
            constants.TRADE_SKILL_LABEL,
            constants.EXPLORATION_SKILL_LABEL,
            constants.CONSTRUCTION_SKILL_LABEL,
            constants.PRODUCTION_SKILL_LABEL,
            constants.TRANSPORTATION_SKILL_LABEL,
            constants.PROSECUTION_SKILL_LABEL,
        ]:
            x_displacement = 25
        else:
            x_displacement = 0
        input_dict["member_config"] = {"order_x_offset": x_displacement}
        input_dict["init_type"] = current_actor_label_type
        constants.actor_creation_manager.create_interface_element(input_dict)
    # minister info labels setup


def manage_crash(exception):
    """
    Description:
        Uses an exception to write a crash log and exit the game
    Input:
        Exception exception: Exception that caused the crash
    Output:
        None
    """
    crash_log_file = open("notes/Crash Log.txt", "w")
    crash_log_file.write("")  # clears crash report file
    console = (
        logging.StreamHandler()
    )  # sets logger to go to both console and crash log file
    logging.basicConfig(filename="notes/Crash Log.txt")
    logging.getLogger("").addHandler(console)

    logging.error(
        exception, exc_info=True
    )  # sends error message to console and crash log file

    crash_log_file.close()
    pygame.quit()
