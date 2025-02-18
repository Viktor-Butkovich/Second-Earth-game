# Manages initial game setup in a semi-modular order

import pygame
import logging
from modules.constants import constants, status, flags
from modules.util import scaling, actor_utility, game_transitions
from modules.constructs import (
    fonts,
    unit_types,
    minister_types,
    building_types,
    equipment_types,
    terrain_feature_types,
    item_types,
)
from modules.tools.data_managers import (
    notification_manager_template,
    value_tracker_template,
    achievement_manager_template,
    character_manager_template,
    actor_creation_manager_template,
    terrain_manager_template,
    help_manager_template,
)
from modules.action_types import (
    public_relations_campaign,
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
                "modes": [
                    constants.STRATEGIC_MODE,
                    constants.EARTH_MODE,
                    constants.MINISTERS_MODE,
                    constants.NEW_GAME_SETUP_MODE,
                ],
                "init_type": constants.ORDERED_COLLECTION,
                "description": "general information panel",
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
    constants.terrain_manager = terrain_manager_template.terrain_manager_template()

    constants.font_size = scaling.scale_height(constants.default_font_size)
    constants.notification_font_size = scaling.scale_height(
        constants.default_notification_font_size
    )

    constants.myfont = fonts.font(
        {
            "descriptor": "default",
            "name": constants.small_font_name,
            "size": constants.font_size,
            "color": "black",
        }
    )
    fonts.font(
        {
            "descriptor": "white",
            "name": constants.small_font_name,
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
        constants.actor_creation_manager.create_interface_element(
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
                "font": constants.fonts["large_white_notification"],
                "modes": [],
                "center_lines": True,
            }
        )
    )
    loading_screen_continue_message = "Press ENTER to continue"
    loading_screen_continue_message_width = constants.fonts[
        "large_white_notification"
    ].pygame_font.size(loading_screen_continue_message)[0]
    status.loading_screen_continue_banner = (
        constants.actor_creation_manager.create_interface_element(
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
                "font": constants.fonts["large_white_notification"],
                "modes": [],
            }
        )
    )

    strategic_background_image = (
        constants.actor_creation_manager.create_interface_element(
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
        constants.actor_creation_manager.create_interface_element(
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

    title_background_image = constants.actor_creation_manager.create_interface_element(
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

    status.safe_click_area = constants.actor_creation_manager.create_interface_element(
        {
            "width": constants.display_width / 2 + 25,
            "height": constants.display_height,
            "modes": [
                constants.STRATEGIC_MODE,
                constants.EARTH_MODE,
                constants.MINISTERS_MODE,
                constants.NEW_GAME_SETUP_MODE,
            ],
            "image_id": "misc/empty.png",  # make a good image for this
            "init_type": constants.SAFE_CLICK_PANEL_ELEMENT,
        }
    )
    # safe click area has empty image but is managed with panel to create correct behavior - its intended image is in the background image's bundle to blit more efficiently

    game_transitions.set_game_mode(constants.MAIN_MENU_MODE)

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

    constants.help_manager = help_manager_template.help_manager_template()

    status.grids_collection = constants.actor_creation_manager.create_interface_element(
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

    north_indicator_image = constants.actor_creation_manager.create_interface_element(
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

    south_indicator_image = constants.actor_creation_manager.create_interface_element(
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
    # anchor = constants.actor_creation_manager.create_interface_element(
    #    {'width': 1, 'height': 1, 'init_type': 'interface element', 'parent_collection': status.info_displays_collection}
    # ) # rect at original location prevents collection from moving unintentionally when resizing


def item_types_config():
    """
    Description:
        Defines item type templates
    Input:
        None
    Output:
        None
    """
    item_types.item_type(
        {
            "equipment_type": constants.CONSUMER_GOODS_ITEM,
            "can_purchase": True,
            "price": constants.consumer_goods_starting_price,
            "can_sell": True,
            "price": constants.consumer_goods_starting_price,
            "description": ["Placeholder consumer goods description"],
            "item_image": "items/consumer_goods.png",
            "allow_price_variation": True,
        }
    )

    item_types.item_type(
        {
            "equipment_type": "iron",
            "can_purchase": True,
            "price": constants.consumer_goods_starting_price,
            "can_sell": True,
            "price": 5,
            "description": ["Placeholder idk description"],
            "item_image": "items/consumer_goods.png",
            "allow_price_variation": True,
        }
    )

    item_types.item_type(
        {
            "equipment_type": "gold",
            "can_purchase": True,
            "price": constants.consumer_goods_starting_price,
            "can_sell": True,
            "price": 5,
            "description": ["Placeholder idk description"],
            "item_image": "items/consumer_goods.png",
            "allow_price_variation": True,
        }
    )

    equipment_types.equipment_type(
        {
            "equipment_type": constants.SPACESUITS_EQUIPMENT,
            "can_purchase": True,
            "price": 5,
            "requirements": (
                "any",
                [
                    constants.GROUP_PERMISSION,
                    constants.WORKER_PERMISSION,
                    constants.OFFICER_PERMISSION,
                ],
            ),
            "effects": {
                "permissions": [constants.SPACESUITS_PERMISSION],
            },
            "description": [
                "Spacesuits are required for humans to survive in deadly conditions",
                "Human units without spacesuits in deadly conditions cannot perform actions and will die at the end of the turn",
                # "By default, solitary officers are assumed to be wearing personal spacesuits",
            ],
            "item_image": {
                constants.FULL_BODY_PORTRAIT_SECTION: "mobs/spacesuits/spacesuit_body.png",
                constants.HAT_PORTRAIT_SECTION: "ministers/portraits/hat/spacesuit/spacesuit_helmet.png",
                constants.HAIR_PORTRAIT_SECTION: "misc/empty.png",
                constants.FACIAL_HAIR_PORTAIT_SECTION: "misc/empty.png",
                constants.BACKPACK_PORTRAIT_SECTION: "mobs/spacesuits/spacesuit_backpack.png",
            },
        }
    )


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
    for building_type in status.building_types.values():
        if building_type.can_construct:
            construction.construction(building_type=building_type)
        if building_type.can_damage:
            repair.repair(building_type=building_type)
        for upgrade_type in building_type.upgrade_fields.keys():
            upgrade.upgrade(building_type=building_type, upgrade_type=upgrade_type)
    public_relations_campaign.public_relations_campaign()
    advertising_campaign.advertising_campaign()
    combat.combat()
    exploration.exploration()
    loan_search.loan_search()
    active_investigation.active_investigation()
    trial.trial()

    for key, action_type in status.actions.items():
        if action_type.placement_type == "free":
            button_input_dict = action_type.button_setup({})
            if button_input_dict:
                action_type.button = (
                    constants.actor_creation_manager.create_interface_element(
                        button_input_dict
                    )
                )
    # action imports hardcoded here, alternative to needing to keep module files in .exe version


def minister_types_config():
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
            "key": constants.SPACE_MINISTER,
            "name": "Minister of Space",
            "skill_type": constants.SPACE_SKILL,
            "description": [
                "Space-oriented units include astronauts, navigators, and space vehicles.",
                "The Minister of Space also controls outer colonies and space logistics.",
            ],
        }
    )
    minister_types.minister_type(
        {
            "key": constants.ECOLOGY_MINISTER,
            "name": "Minister of Ecology",
            "skill_type": constants.ECOLOGY_SKILL,
            "description": ["Ecology-oriented units include terraformers and doctors."],
        }
    )
    minister_types.minister_type(
        {
            "key": constants.TERRAN_AFFAIRS_MINISTER,
            "name": "Minister of Terran Affairs",
            "skill_type": constants.TERRAN_AFFAIRS_SKILL,
            "description": [
                "Terran Affairs-oriented units include lobbyists, executives, and influencers.",
                "The Minister of Terran Affairs also controls the purchase and sale of goods on Earth",
            ],
        }
    )
    minister_types.minister_type(
        {
            "key": constants.SCIENCE_MINISTER,
            "name": "Minister of Science",
            "skill_type": constants.SCIENCE_SKILL,
            "description": [
                "Science-oriented units include researchers and surveyors."
            ],
        }
    )

    minister_types.minister_type(
        {
            "key": constants.INDUSTRY_MINISTER,
            "name": "Minister of Industry",
            "skill_type": constants.INDUSTRY_SKILL,
            "description": [
                "Industry-oriented units include construction crews and work crews."
            ],
        }
    )

    minister_types.minister_type(
        {
            "key": constants.ENERGY_MINISTER,
            "name": "Minister of Energy",
            "skill_type": constants.ENERGY_SKILL,
            "description": ["Energy-oriented units include technicians."],
        }
    )

    minister_types.minister_type(
        {
            "key": constants.TRANSPORTATION_MINISTER,
            "name": "Minister of Transportation",
            "skill_type": constants.TRANSPORTATION_SKILL,
            "description": [
                "Transportation-oriented units include planetary vehicles and their crews.",
                "The Minister of Transportation also manages planetary logistics and warehouses.",
            ],
        }
    )
    minister_types.minister_type(
        {
            "key": constants.SECURITY_MINISTER,
            "name": "Minister of Security",
            "skill_type": constants.SECURITY_SKILL,
            "controls_units": False,
            "description": [
                "Security-oriented units include marines and investigators."
                "The Minister of Security also controls the process of investigating and removing corrupt ministers."
            ],
        }
    )


def building_types_config():
    """
    Description:
        Defines building type templates
    Input:
        None
    Output:
        None
    """
    building_types.building_type(
        {
            "key": constants.SPACEPORT,
            "name": "spaceport",
            "description": [
                "A spaceport allows spaceships to land and launch, and expands the tile's warehouse capacity."
            ],
            "warehouse_level": 1,
            "can_construct": True,
            "can_damage": True,
            "cost": 15,
            "display_coordinates": (1, -1),
            "attached_settlement": True,
            "build_keybind": pygame.K_p,
        }
    )
    building_types.building_type(
        {
            "key": constants.TRAIN_STATION,
            "name": "train station",
            "description": [
                "A train station allows trains to pick up or drop off cargo, and expands the tile's warehouse capacity.",
            ],
            "warehouse_level": 1,
            "can_construct": True,
            "can_damage": True,
            "cost": 10,
            "display_coordinates": (0, -1),
            "attached_settlement": True,
            "image_id_list": [
                {"image_id": "buildings/train_station.png"},
                {"image_id": "buildings/infrastructure/down_railroad.png"},
            ],
            "build_keybind": pygame.K_t,
        }
    )
    # building_types.building_type(
    #    {
    #        "key": constants.RESOURCE,
    #        "name": "resource production facility",
    #        "warehouse_level": 1,
    #        "can_construct": True,
    #        "can_damage": True,
    #        "cost": 10,
    #        "description": [
    #            "A resource production facility allows attaching work crews to attempt to produce resources each turn, and expands the tile's warehouse capacity.",
    #            "Upgrades can increase the maximum number of attached work crews and the number of production attempts each work crew can make.",
    #        ],
    #        "upgrade_fields": {
    #            constants.RESOURCE_SCALE: {
    #                "cost": constants.base_upgrade_price,
    #                "max": 6,
    #                "name": "scale",
    #                "description": [
    #                   "Each increase to scale allows another work crew to work here."
    #                ]"
    #            },
    #            constants.RESOURCE_EFFICIENCY: {
    #                "cost": constants.base_upgrade_price,
    #                "max": 6,
    #                "name": "efficiency",
    #                "description": [
    #                    "Each increase to efficiency allows each work crew to make an additional production attempt each turn."
    #                ],
    #            },
    #        },
    #        "attached_settlement": True,
    #        "build_keybind": pygame.K_g,
    #    }
    # )
    building_types.building_type(
        {
            "key": constants.FORT,
            "name": "fort",
            "description": [
                "A fort grants a +1 combat modifier to your units fighting in this tile."
            ],
            "can_construct": True,
            "can_damage": True,
            "cost": 5,
            "display_coordinates": (-1, 1),
            "attached_settlement": True,
            "build_requirements": [
                constants.GROUP_PERMISSION,
                constants.BATTALION_PERMISSION,
            ],
            "build_keybind": pygame.K_v,
        }
    )
    building_types.building_type(
        {
            "key": constants.TRAIN,
            "name": "train",
            "description": [
                "A train can be built as a vehicle with 27 inventory capacity and 16 movement points that is restricted to moving on railroads and loading/unloading on train stations."
            ],
            "can_construct": True,
            "can_damage": False,
            "cost": 10,
            "build_keybind": pygame.K_y,
            "image_id_list": [{"image_id": "mobs/train/default.png"}],
            "button_image_id_list": [
                "buttons/default_button_alt.png",
                {
                    "image_id": "mobs/train/default.png",
                    "size": 0.95,
                    "x_offset": 0,
                    "y_offset": 0,
                    "level": 1,
                },
            ],
        }
    )

    building_types.building_type(
        {
            "key": constants.WAREHOUSES,
            "name": "warehouses",
            "can_construct": False,
            "can_damage": False,
            "cost": 5,
            "upgrade_fields": {
                constants.WAREHOUSE_LEVEL: {
                    "name": "warehouse capacity",
                    "cost": constants.base_upgrade_price,
                    "keybind": pygame.K_k,
                    "description": [
                        "Each increase to warehouse capacity increases this tile's inventory capacity by 9."
                    ],
                },
            },
        }
    )
    building_types.building_type(
        {
            "key": constants.SLUMS,
            "name": "slums",
            "can_construct": False,
            "can_damage": False,
        }
    )
    # building_types.building_type(
    #     {
    #         "key": constants.INFRASTRUCTURE,
    #         "name": "infrastructure",
    #         "can_construct": True,
    #         "can_damage": False,
    #         "cost": 5, # 15 for railroad, 50 for ferry, 100 for road bridge, 300 for railroad bridge?
    #         "build_keybind": pygame.K_r,
    #     }
    # )

    # Add attrition modifiers
    # add upgrade types


def unit_types_config():
    """
    Description:
        Defines unit type templates
    Input:
        None
    Output:
        None
    """
    if not constants.effect_manager.effect_active("hide_old_units"):
        unit_types.group_type(
            False,
            {
                "key": constants.EXPEDITION,
                "name": "expedition",
                "controlling_minister_type": status.minister_types[
                    constants.SCIENCE_MINISTER
                ],
                "permissions": {
                    constants.PMOB_PERMISSION: True,
                    constants.GROUP_PERMISSION: True,
                    constants.EXPEDITION_PERMISSION: True,
                },
                "can_recruit": False,
            },
        )
        unit_types.officer_type(
            False,
            {
                "key": constants.EXPLORER,
                "name": "explorer",
                "controlling_minister_type": status.minister_types[
                    constants.SCIENCE_MINISTER
                ],
                "permissions": {
                    constants.PMOB_PERMISSION: True,
                    constants.OFFICER_PERMISSION: True,
                    constants.EXPLORER_PERMISSION: True,
                },
                "can_recruit": True,
                "recruitment_verb": "hire",
                "recruitment_cost": 5,
                "description": [
                    f"Explorers are controlled by the {status.minister_types[constants.SCIENCE_MINISTER].name}.",
                    "An explorer combines with colonists to form an expedition, which can explore new tiles.",
                ],
            },
        ).link_group_type(status.unit_types[constants.EXPEDITION])

        unit_types.group_type(
            False,
            {
                "key": constants.MISSIONARIES,
                "name": "missionaries",
                "controlling_minister_type": status.minister_types[
                    constants.TERRAN_AFFAIRS_MINISTER
                ],
                "permissions": {
                    constants.PMOB_PERMISSION: True,
                    constants.GROUP_PERMISSION: True,
                    constants.MISSIONARIES_PERMISSION: True,
                },
                "can_recruit": False,
            },
        )
        unit_types.officer_type(
            False,
            {
                "key": constants.EVANGELIST,
                "name": "evangelist",
                "controlling_minister_type": status.minister_types[
                    constants.TERRAN_AFFAIRS_MINISTER
                ],
                "permissions": {
                    constants.PMOB_PERMISSION: True,
                    constants.OFFICER_PERMISSION: True,
                    constants.EVANGELIST_PERMISSION: True,
                },
                "can_recruit": True,
                "recruitment_verb": "hire",
                "recruitment_cost": 5,
                "description": [
                    f"Evangelists are controlled by the {status.minister_types[constants.TERRAN_AFFAIRS_MINISTER].name}, and can personally conduct religious campaigns and public relations campaigns on Earth.",
                    "An evangelist combines with church volunteers to form missionaries, which can build missions.",
                ],
            },
        ).link_group_type(status.unit_types[constants.MISSIONARIES])

        unit_types.group_type(
            False,
            {
                "key": constants.BATTALION,
                "name": "battalion",
                "controlling_minister_type": status.minister_types[
                    constants.SPACE_MINISTER
                ],
                "permissions": {
                    constants.PMOB_PERMISSION: True,
                    constants.GROUP_PERMISSION: True,
                    constants.BATTALION_PERMISSION: True,
                },
                "can_recruit": False,
            },
        )
        unit_types.officer_type(
            False,
            {
                "key": constants.MAJOR,
                "name": "major",
                "controlling_minister_type": status.minister_types[
                    constants.SPACE_MINISTER
                ],
                "permissions": {
                    constants.PMOB_PERMISSION: True,
                    constants.OFFICER_PERMISSION: True,
                    constants.MAJOR_PERMISSION: True,
                },
                "can_recruit": True,
                "recruitment_verb": "hire",
                "recruitment_cost": 5,
                "description": [
                    f"Majors are controlled by the {status.minister_types[constants.SPACE_MINISTER].name}.",
                    "A major combines with colonists to form a battalion, which has a very high combat strength, and can build forts and attack enemies.",
                ],
            },
        ).link_group_type(status.unit_types[constants.BATTALION])

        unit_types.group_type(
            False,
            {
                "key": constants.PORTERS,
                "name": "porters",
                "controlling_minister_type": status.minister_types[
                    constants.TRANSPORTATION_MINISTER
                ],
                "permissions": {
                    constants.PMOB_PERMISSION: True,
                    constants.GROUP_PERMISSION: True,
                    constants.PORTERS_PERMISSION: True,
                },
                "can_recruit": False,
                "inventory_capacity": 9,
                "number": 2,
            },
        )
        unit_types.officer_type(
            False,
            {
                "key": constants.DRIVER,
                "name": "driver",
                "controlling_minister_type": status.minister_types[
                    constants.TRANSPORTATION_MINISTER
                ],
                "permissions": {
                    constants.PMOB_PERMISSION: True,
                    constants.OFFICER_PERMISSION: True,
                    constants.DRIVER_PERMISSION: True,
                },
                "can_recruit": True,
                "recruitment_verb": "hire",
                "recruitment_cost": 5,
                "description": [
                    f"Drivers are controlled by the {status.minister_types[constants.TRANSPORTATION_MINISTER].name}.",
                    "A driver combines with colonists to form porters, which can transport items and move quickly.",
                ],
            },
        ).link_group_type(status.unit_types[constants.PORTERS])

        unit_types.group_type(
            False,
            {
                "key": constants.WORK_CREW,
                "name": "work crew",
                "controlling_minister_type": status.minister_types[
                    constants.INDUSTRY_MINISTER
                ],
                "permissions": {
                    constants.PMOB_PERMISSION: True,
                    constants.GROUP_PERMISSION: True,
                    constants.WORK_CREW_PERMISSION: True,
                },
                "can_recruit": False,
            },
        )
        unit_types.officer_type(
            False,
            {
                "key": constants.FOREMAN,
                "name": "foreman",
                "controlling_minister_type": status.minister_types[
                    constants.INDUSTRY_MINISTER
                ],
                "permissions": {
                    constants.PMOB_PERMISSION: True,
                    constants.OFFICER_PERMISSION: True,
                    constants.FOREMAN_PERMISSION: True,
                },
                "can_recruit": True,
                "recruitment_verb": "hire",
                "recruitment_cost": 5,
                "description": [
                    f"Foremen are controlled by the {status.minister_types[constants.INDUSTRY_MINISTER].name}.",
                    "A foreman combines with colonists to form a work crew, which can produce resources when attached to a production facility.",
                ],
            },
        ).link_group_type(status.unit_types[constants.WORK_CREW])

    unit_types.group_type(
        False,
        {
            "key": constants.ASTRONAUTS,
            "name": "astronauts",
            "controlling_minister_type": status.minister_types[
                constants.SPACE_MINISTER
            ],
            "permissions": {
                constants.PMOB_PERMISSION: True,
                constants.GROUP_PERMISSION: True,
                constants.ASTRONAUTS_PERMISSION: True,
                constants.CREW_VEHICLE_PERMISSION: True,
                constants.CREW_SPACESHIP_PERMISSION: True,
            },
            "can_recruit": False,
        },
    )
    unit_types.officer_type(
        False,
        {
            "key": constants.ASTRONAUT_COMMANDER,
            "name": "astronaut commander",
            "controlling_minister_type": status.minister_types[
                constants.SPACE_MINISTER
            ],
            "permissions": {
                constants.PMOB_PERMISSION: True,
                constants.OFFICER_PERMISSION: True,
                constants.ASTRONAUT_COMMANDER_PERMISSION: True,
            },
            "can_recruit": True,
            "recruitment_verb": "hire",
            "recruitment_cost": 5,
            "description": [
                f"Astronaut commanders are controlled by the {status.minister_types[constants.SPACE_MINISTER].name}.",
                "An astronaut commander combines with colonists to form astronauts, which can crew spaceships and space stations, and perform actions in orbit.",
            ],
        },
    ).link_group_type(status.unit_types[constants.ASTRONAUTS])

    unit_types.group_type(
        False,
        {
            "key": constants.CONSTRUCTION_CREW,
            "name": "construction crew",
            "controlling_minister_type": status.minister_types[
                constants.INDUSTRY_MINISTER
            ],
            "permissions": {
                constants.PMOB_PERMISSION: True,
                constants.GROUP_PERMISSION: True,
                constants.CONSTRUCTION_PERMISSION: True,
            },
            "can_recruit": False,
        },
    )
    unit_types.officer_type(
        False,
        {
            "key": constants.ENGINEER,
            "name": "engineer",
            "controlling_minister_type": status.minister_types[
                constants.INDUSTRY_MINISTER
            ],
            "permissions": {
                constants.PMOB_PERMISSION: True,
                constants.OFFICER_PERMISSION: True,
                constants.ENGINEER_PERMISSION: True,
            },
            "can_recruit": True,
            "recruitment_verb": "hire",
            "recruitment_cost": 5,
            "description": [
                f"Engineers are controlled by the {status.minister_types[constants.INDUSTRY_MINISTER].name}.",
                "An engineer combines with colonists to form a construction crew, which can build buildings, roads, railroads, and trains.",
            ],
        },
    ).link_group_type(status.unit_types[constants.CONSTRUCTION_CREW])

    merchant_officer_type = unit_types.officer_type(
        False,
        {
            "key": constants.MERCHANT,
            "name": "merchant",
            "controlling_minister_type": status.minister_types[
                constants.TERRAN_AFFAIRS_MINISTER
            ],
            "permissions": {
                constants.PMOB_PERMISSION: True,
                constants.OFFICER_PERMISSION: True,
                constants.MERCHANT_PERMISSION: True,
            },
            "can_recruit": True,
            "recruitment_verb": "hire",
            "recruitment_cost": 5,
            "description": [
                f"Merchants are controlled by the {status.minister_types[constants.TERRAN_AFFAIRS_MINISTER].name}, and can personally search for loans and conduct advertising campaigns on Earth.",
                "A merchant combines with colonists to form a caravan, which can trade and build trading posts.",
            ],
        },
    )
    if not constants.effect_manager.effect_active("hide_old_units"):
        caravan_group_type = unit_types.group_type(
            False,
            {
                "key": constants.CARAVAN,
                "name": "caravan",
                "controlling_minister_type": status.minister_types[
                    constants.TERRAN_AFFAIRS_MINISTER
                ],
                "permissions": {
                    constants.PMOB_PERMISSION: True,
                    constants.GROUP_PERMISSION: True,
                    constants.CARAVAN_PERMISSION: True,
                },
                "can_recruit": False,
                "inventory_capacity": 9,
            },
        )
        merchant_officer_type.link_group_type(caravan_group_type)

    unit_types.worker_type(
        False,
        {
            "key": constants.COLONISTS,
            "name": "colonists",
            "controlling_minister_type": status.minister_types[
                constants.TERRAN_AFFAIRS_MINISTER
            ],
            "permissions": {
                constants.PMOB_PERMISSION: True,
                constants.WORKER_PERMISSION: True,
                constants.CREW_SPACESHIP_PERMISSION: True,
                constants.CREW_TRAIN_PERMISSION: True,
            },
            "upkeep": 6.0,
            "upkeep_variance": True,
            "save_changes": True,
            "can_recruit": True,
            "recruitment_cost": 0,
            "recruitment_verb": "hire",
            "fired_description": ["Fired description."],
            "description": [
                "Colonists represent a large group of workers, and are required for most tasks. ",
                "Colonists must work near their housing, and require upkeep each turn in food, air, water, and goods. ",
                "Officers can be attached to colonists to form groups, which can perform actions. ",
                "For example, an engineer combined with colonists forms a construction crew, which can construct buildings. ",
            ],
            "number": 2,
        },
    )

    unit_types.vehicle_type(
        False,
        {
            "key": constants.COLONY_SHIP,
            "name": "colony ship",
            "controlling_minister_type": status.minister_types[
                constants.SPACE_MINISTER
            ],
            "permissions": {
                constants.PMOB_PERMISSION: True,
                constants.INACTIVE_VEHICLE_PERMISSION: True,
                constants.VEHICLE_PERMISSION: True,
                constants.ACTIVE_PERMISSION: False,
                constants.SPACESHIP_PERMISSION: True,
                constants.INFINITE_MOVEMENT_PERMISSION: True,
                constants.TRAVEL_PERMISSION: True,
                constants.CONSTANT_MOVEMENT_COST_PERMISSION: True,
            },
            "inventory_capacity": 81,
            "can_recruit": True,
            "recruitment_verb": "purchase",
            "recruitment_cost": 500,
            "description": [
                "This ship is equipped for interstellar travel, with a massive cargo hold and advanced life support systems to serve as an initial base of operations on another planet.",
                "A colony ship contains enough space for a small city of crew and passengers, as well as modules, equipment, and supplies (not included).",
                "Suitable for a 1-way trip.",
            ],
        },
    )

    unit_types.vehicle_type(
        False,
        {
            "key": constants.TRAIN,
            "name": "train",
            "controlling_minister_type": status.minister_types[
                constants.TRANSPORTATION_MINISTER
            ],
            "permissions": {
                constants.PMOB_PERMISSION: True,
                constants.INACTIVE_VEHICLE_PERMISSION: True,
                constants.VEHICLE_PERMISSION: True,
                constants.ACTIVE_PERMISSION: False,
                constants.TRAIN_PERMISSION: True,
                constants.CONSTANT_MOVEMENT_COST_PERMISSION: True,
            },
            "can_recruit": False,
            "movement_points": 16,
            # "required_infrastructure": status.building_types[constants.RAILROAD],
            #   Re-introduce once infrastructure is re-implemented
            "description": [
                "While useless by itself, a train crewed by workers can quickly transport units and cargo through railroads between train stations.",
            ],
        },
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
                "width": scaling.scale_width(0),
                "height": scaling.scale_height(0),
                "modes": [
                    constants.STRATEGIC_MODE,
                    constants.EARTH_MODE,
                    constants.MINISTERS_MODE,
                    constants.TRIAL_MODE,
                    constants.MAIN_MENU_MODE,
                    constants.NEW_GAME_SETUP_MODE,
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
            "height": scaling.scale_height(
                constants.default_notification_font_size + 5
            ),
            "modes": [
                constants.STRATEGIC_MODE,
                constants.EARTH_MODE,
                constants.MINISTERS_MODE,
            ],
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
            "height": scaling.scale_height(
                constants.default_notification_font_size + 5
            ),
            "modes": [
                constants.STRATEGIC_MODE,
                constants.EARTH_MODE,
                constants.MINISTERS_MODE,
                constants.TRIAL_MODE,
            ],
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
            "height": scaling.scale_height(
                constants.default_notification_font_size + 5
            ),
            "modes": [
                constants.STRATEGIC_MODE,
                constants.EARTH_MODE,
                constants.MINISTERS_MODE,
                constants.TRIAL_MODE,
            ],
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
                "height": scaling.scale_height(
                    constants.default_notification_font_size + 5
                ),
                "modes": [
                    constants.STRATEGIC_MODE,
                    constants.EARTH_MODE,
                    constants.MINISTERS_MODE,
                    constants.TRIAL_MODE,
                    constants.MAIN_MENU_MODE,
                    constants.NEW_GAME_SETUP_MODE,
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
            "modes": [
                constants.STRATEGIC_MODE,
                constants.EARTH_MODE,
                constants.MINISTERS_MODE,
                constants.TRIAL_MODE,
            ],
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

    if constants.effect_manager.effect_active("map_customization"):
        north_pole_centered_earth = (
            constants.actor_creation_manager.create_interface_element(
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
        # globe_projection_x += constants.strategic_map_pixel_width

    input_dict = {
        "coordinates": scaling.scale_coordinates(0, 10),
        "width": scaling.scale_width(150),
        "height": scaling.scale_height(100),
        "image_id": "misc/empty.png",
        "modes": [constants.STRATEGIC_MODE, constants.EARTH_MODE],
        "to_mode": constants.EARTH_MODE,
        "init_type": constants.FREE_IMAGE,
        "parent_collection": status.grids_collection,
    }
    strategic_flag_icon = constants.actor_creation_manager.create_interface_element(
        input_dict
    )

    input_dict["modes"] = [constants.MINISTERS_MODE]
    input_dict["coordinates"] = scaling.scale_coordinates(
        constants.default_display_width / 2 - 75, constants.default_display_height - 160
    )
    input_dict["parent_collection"] = None
    ministers_flag_icon = constants.actor_creation_manager.create_interface_element(
        input_dict
    )
    globe_projection_x = scaling.scale_width(
        constants.strategic_map_x_offset
        + constants.grids_collection_x
        + constants.strategic_map_pixel_width
        + 15
    )
    # if constants.effect_manager.effect_active("map_customization"):
    #    globe_projection_x += constants.strategic_map_pixel_width
    globe_projection_y = (
        scaling.scale_height(constants.earth_grid_y_offset) + status.grids_collection.y
    )
    globe_projection_size = constants.earth_grid_width * 0.85
    status.globe_projection_image = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": (globe_projection_x, globe_projection_y),
                "init_type": constants.FREE_IMAGE,
                "modes": [],
                "width": scaling.scale_width(globe_projection_size),
                "height": scaling.scale_height(globe_projection_size),
                "image_id": "misc/empty.png",
                "pixellate_image": True,
            }
        )
    )
    compass_overlay_size = 15
    north_overlay = constants.actor_creation_manager.create_interface_element(
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
            "modes": [constants.STRATEGIC_MODE],  # status.globe_projection_image.modes,
            "width": scaling.scale_width(compass_overlay_size),
            "height": scaling.scale_width(compass_overlay_size),
            "image_id": "misc/north_indicator.png",
            "to_front": True,
        }
    )
    south_overlay = constants.actor_creation_manager.create_interface_element(
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
    input_dict = {
        "coordinates": scaling.scale_coordinates(
            switch_game_mode_buttons_x, constants.default_display_height - 55
        ),
        "height": scaling.scale_height(50),
        "width": scaling.scale_width(50),
        "keybind_id": pygame.K_1,
        "image_id": actor_utility.generate_frame("locations/africa.png"),
        "modes": [
            constants.MINISTERS_MODE,
            constants.STRATEGIC_MODE,
            constants.EARTH_MODE,
            constants.TRIAL_MODE,
        ],
        "to_mode": constants.STRATEGIC_MODE,
        "init_type": constants.SWITCH_GAME_MODE_BUTTON,
    }
    status.to_strategic_button = (
        constants.actor_creation_manager.create_interface_element(input_dict)
    )

    input_dict.update(
        {
            "coordinates": scaling.scale_coordinates(
                switch_game_mode_buttons_x + 60, constants.default_display_height - 55
            ),
            "image_id": actor_utility.generate_frame(
                "misc/space.png",
            )
            + [
                {
                    "image_id": "locations/earth.png",
                    "size": 0.6,
                }
            ],
            "to_mode": constants.EARTH_MODE,
            "keybind_id": pygame.K_2,
        }
    )
    status.to_earth_button = constants.actor_creation_manager.create_interface_element(
        input_dict
    )

    input_dict.update(
        {
            "coordinates": scaling.scale_coordinates(
                switch_game_mode_buttons_x + 120, constants.default_display_height - 55
            ),
            "width": scaling.scale_width(50),
            "to_mode": constants.MINISTERS_MODE,
            "image_id": "buttons/hq_button.png",
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
            "modes": [
                constants.STRATEGIC_MODE,
                constants.EARTH_MODE,
                constants.MINISTERS_MODE,
                constants.TRIAL_MODE,
                constants.NEW_GAME_SETUP_MODE,
            ],
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
            "modes": [
                constants.STRATEGIC_MODE,
                constants.EARTH_MODE,
                constants.MINISTERS_MODE,
                constants.NEW_GAME_SETUP_MODE,
            ],
            "init_type": constants.ORDERED_COLLECTION,
            "member_config": {"order_exempt": True},
            "separation": 5,
            "direction": "horizontal",
        }
    )

    input_dict["coordinates"] = scaling.scale_coordinates(
        constants.default_display_width - 50, constants.default_display_height - 50
    )
    input_dict["image_id"] = "buttons/exit_earth_screen_button.png"
    input_dict["init_type"] = constants.SWITCH_GAME_MODE_BUTTON
    input_dict["width"] = scaling.scale_width(50)
    input_dict["height"] = scaling.scale_height(50)
    input_dict["modes"] = [
        constants.STRATEGIC_MODE,
        constants.EARTH_MODE,
        constants.MINISTERS_MODE,
        constants.TRIAL_MODE,
    ]
    input_dict["keybind_id"] = pygame.K_ESCAPE
    input_dict["to_mode"] = constants.MAIN_MENU_MODE
    to_main_menu_button = constants.actor_creation_manager.create_interface_element(
        input_dict
    )
    rhs_menu_collection.add_member(to_main_menu_button)

    input_dict["coordinates"] = scaling.scale_coordinates(
        0, constants.default_display_height - 50
    )
    input_dict["modes"] = [constants.NEW_GAME_SETUP_MODE]
    input_dict["keybind_id"] = pygame.K_ESCAPE
    new_game_setup_to_main_menu_button = (
        constants.actor_creation_manager.create_interface_element(input_dict)
    )
    lhs_menu_collection.add_member(new_game_setup_to_main_menu_button)

    input_dict = {
        "coordinates": scaling.scale_coordinates(
            round(constants.default_display_width * 0.4) - 15,
            constants.default_display_height - 55,
        ),
        "width": scaling.scale_width(round(constants.default_display_width * 0.2)),
        "height": scaling.scale_height(50),
        "modes": [
            constants.STRATEGIC_MODE,
            constants.EARTH_MODE,
            constants.MINISTERS_MODE,
            constants.TRIAL_MODE,
        ],
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
    input_dict["modes"] = [constants.MAIN_MENU_MODE]
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
    input_dict["modes"] = [constants.NEW_GAME_SETUP_MODE]
    input_dict["keybind_id"] = pygame.K_n
    setup_new_game_button = constants.actor_creation_manager.create_interface_element(
        input_dict
    )

    input_dict["coordinates"] = (
        input_dict["coordinates"][0],
        scaling.scale_height(constants.default_display_height / 2 - 225),
    )
    input_dict["modes"] = [constants.MAIN_MENU_MODE]
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
        "modes": [
            constants.STRATEGIC_MODE,
            constants.EARTH_MODE,
            constants.MINISTERS_MODE,
            constants.TRIAL_MODE,
        ],
        "image_id": "buttons/save_game_button.png",
        "init_type": constants.SAVE_GAME_BUTTON,
    }
    save_game_button = constants.actor_creation_manager.create_interface_element(
        input_dict
    )
    rhs_menu_collection.add_member(save_game_button)

    input_dict["modes"] = [
        constants.STRATEGIC_MODE,
        constants.EARTH_MODE,
        constants.MINISTERS_MODE,
        constants.TRIAL_MODE,
    ]
    input_dict["image_id"] = "buttons/text_box_size_button.png"
    input_dict["init_type"] = constants.TOGGLE_BUTTON
    input_dict["toggle_variable"] = "expand_text_box"
    input_dict["attached_to_actor"] = False
    expand_text_box_button = constants.actor_creation_manager.create_interface_element(
        input_dict
    )
    rhs_menu_collection.add_member(expand_text_box_button)

    input_dict["modes"] = [constants.STRATEGIC_MODE]
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
        input_dict["modes"] = [constants.STRATEGIC_MODE]
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
        input_dict["modes"] = [constants.STRATEGIC_MODE]
        input_dict["image_id"] = actor_utility.generate_frame(
            "buttons/toggle_fog_of_war_button.png"
        )
        rhs_menu_collection.add_member(
            constants.actor_creation_manager.create_interface_element(input_dict)
        )
    if constants.effect_manager.effect_active("allow_toggle_clouds"):
        input_dict["init_type"] = constants.TOGGLE_BUTTON
        input_dict["toggle_variable"] = "show_clouds"
        input_dict["attached_to_actor"] = False
        input_dict["modes"] = [constants.STRATEGIC_MODE]
        input_dict["image_id"] = actor_utility.generate_frame(
            "buttons/toggle_clouds_button.png"
        )
        rhs_menu_collection.add_member(
            constants.actor_creation_manager.create_interface_element(input_dict)
        )

    if constants.effect_manager.effect_active("allow_toggle_god_mode"):
        input_dict["init_type"] = constants.TOGGLE_BUTTON
        input_dict["toggle_variable"] = "god_mode"
        input_dict["attached_to_actor"] = False
        input_dict["modes"] = [constants.STRATEGIC_MODE]
        input_dict["image_id"] = "buttons/toggle_god_mode_button.png"
        rhs_menu_collection.add_member(
            constants.actor_creation_manager.create_interface_element(input_dict)
        )

    input_dict["coordinates"] = scaling.scale_coordinates(
        110, constants.default_display_height - 50
    )
    input_dict["modes"] = [
        constants.STRATEGIC_MODE,
        constants.EARTH_MODE,
        constants.MINISTERS_MODE,
    ]
    input_dict["keybind_id"] = pygame.K_TAB
    input_dict["image_id"] = "buttons/cycle_units_button.png"
    input_dict["init_type"] = constants.CYCLE_UNITS_BUTTON
    cycle_units_button = constants.actor_creation_manager.create_interface_element(
        input_dict
    )
    lhs_menu_collection.add_member(cycle_units_button)
    del input_dict["keybind_id"]

    if not constants.effect_manager.effect_active("hide_old_buttons"):
        input_dict["coordinates"] = (
            scaling.scale_width(165),
            input_dict["coordinates"][1],
        )
        input_dict["modes"] = [constants.STRATEGIC_MODE, constants.EARTH_MODE]
        input_dict["image_id"] = "buttons/disable_sentry_mode_button.png"
        input_dict["init_type"] = constants.WAKE_UP_ALL_BUTTON
        wake_up_all_button = constants.actor_creation_manager.create_interface_element(
            input_dict
        )
        lhs_menu_collection.add_member(wake_up_all_button)

        input_dict["coordinates"] = (
            scaling.scale_width(220),
            input_dict["coordinates"][1],
        )
        input_dict["image_id"] = "buttons/execute_movement_routes_button.png"
        input_dict["init_type"] = constants.EXECUTE_MOVEMENT_ROUTES_BUTTON
        execute_movement_routes_button = (
            constants.actor_creation_manager.create_interface_element(input_dict)
        )
        lhs_menu_collection.add_member(execute_movement_routes_button)

    input_dict["coordinates"] = scaling.scale_coordinates(
        constants.default_display_width - 55, constants.default_display_height - 55
    )
    input_dict["modes"] = [constants.MAIN_MENU_MODE]
    input_dict["image_id"] = ["buttons/exit_earth_screen_button.png"]
    input_dict["init_type"] = constants.GENERATE_CRASH_BUTTON
    generate_crash_button = constants.actor_creation_manager.create_interface_element(
        input_dict
    )

    if constants.effect_manager.effect_active("map_modes"):
        input_dict["init_type"] = constants.MAP_MODE_BUTTON
        input_dict["parent_collection"] = rhs_menu_collection
        input_dict["modes"] = [constants.STRATEGIC_MODE, constants.EARTH_MODE]
        for map_mode in constants.map_modes:
            input_dict["map_mode"] = map_mode
            input_dict["image_id"] = actor_utility.generate_frame(
                f"misc/map_modes/{map_mode}.png"
            )
            constants.actor_creation_manager.create_interface_element(input_dict)

    if constants.effect_manager.effect_active("allow_presets"):
        input_dict["init_type"] = constants.TOGGLE_BUTTON
        input_dict["toggle_variable"] = "mars_preset"
        input_dict["attached_to_actor"] = False
        input_dict["modes"] = [constants.NEW_GAME_SETUP_MODE]
        input_dict["image_id"] = actor_utility.generate_frame("misc/space.png") + [
            {
                "image_id": "locations/mars.png",
                "size": 0.6,
                "detail_level": 1.0,
            }
        ]
        input_dict["width"] = scaling.scale_width(100)
        input_dict["height"] = scaling.scale_height(100)
        input_dict["parent_collection"] = rhs_menu_collection
        input_dict["member_config"] = {"order_x_offset": scaling.scale_width(-50)}
        constants.actor_creation_manager.create_interface_element(input_dict)

        input_dict["toggle_variable"] = "earth_preset"
        input_dict["image_id"] = actor_utility.generate_frame("misc/space.png") + [
            {
                "image_id": "locations/earth.png",
                "size": 0.6,
                "detail_level": 1.0,
            }
        ]
        constants.actor_creation_manager.create_interface_element(input_dict)

        input_dict["toggle_variable"] = "venus_preset"
        input_dict["image_id"] = actor_utility.generate_frame("misc/space.png") + [
            {
                "image_id": "locations/venus.png",
                "size": 0.6,
                "detail_level": 1.0,
            }
        ]
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
            "modes": [constants.EARTH_MODE],
            "init_type": constants.ORDERED_COLLECTION,
            "separation": scaling.scale_height(20),
            "reversed": True,
            "second_dimension_increment": scaling.scale_width(125),
            "direction": "vertical",
        }
    )
    purchase_button_grid_height = 7

    for recruitment_type in status.recruitment_types:
        constants.actor_creation_manager.create_interface_element(
            {
                "width": scaling.scale_width(100),
                "height": scaling.scale_height(100),
                "init_type": constants.RECRUITMENT_BUTTON,
                "parent_collection": earth_purchase_buttons,
                "recruitment_type": recruitment_type,
                "member_config": {
                    "second_dimension_coordinate": 0  # -1 * (len(earth_purchase_buttons.members) // purchase_button_grid_height)
                },
            }
        )
    for (
        purchase_item_type
    ) in status.item_types.values():  # Creates purchase button for items from earth
        constants.actor_creation_manager.create_interface_element(
            {
                "width": scaling.scale_width(100),
                "height": scaling.scale_height(100),
                "init_type": constants.BUY_ITEM_BUTTON,
                "parent_collection": earth_purchase_buttons,
                "item_type": purchase_item_type,
                "member_config": {
                    "second_dimension_coordinate": -1  # -1 * (len(earth_purchase_buttons.members) // purchase_button_grid_height)
                },  # Re-uses recruitment index from previous loop
            }
        )


def ministers_screen():
    """
    Description:
        Initializes static interface of ministers screen
    Input:
        None
    Output:
        None
    """
    # Minister table setup
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
                    "modes": [constants.MINISTERS_MODE],
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
                    "modes": [constants.MINISTERS_MODE],
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
        "modes": [constants.MINISTERS_MODE],
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
                "modes": [constants.MINISTERS_MODE],
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

    status.minister_loading_image = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(0, 0),
                "width": scaling.scale_width(portrait_icon_width),
                "height": scaling.scale_height(portrait_icon_width),
                "modes": [],
                "init_type": constants.MINISTER_PORTRAIT_IMAGE,
                "color": "gray",
                "minister_type": None,
            }
        )
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
                "modes": [constants.TRIAL_MODE],
                "init_type": constants.ORDERED_COLLECTION,
                "is_info_display": True,
                "actor_type": constants.DEFENSE_ACTOR_TYPE,
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
            "modes": [constants.TRIAL_MODE],
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
        "height": scaling.scale_height(constants.default_notification_font_size + 5),
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
    for current_actor_label_type in [
        constants.MINISTER_NAME_LABEL,
        constants.MINISTER_OFFICE_LABEL,
        constants.EVIDENCE_LABEL,
    ]:
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
                "modes": [constants.TRIAL_MODE],
                "init_type": constants.ORDERED_COLLECTION,
                "is_info_display": True,
                "actor_type": constants.PROSECUTION_ACTOR_TYPE,
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
            "modes": [constants.TRIAL_MODE],
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
        "height": scaling.scale_height(constants.default_notification_font_size + 5),
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
    for current_actor_label_type in [
        constants.MINISTER_NAME_LABEL,
        constants.MINISTER_OFFICE_LABEL,
    ]:
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
            "modes": [constants.TRIAL_MODE],
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
                "modes": [constants.TRIAL_MODE],
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
    #     "modes": [constants.NEW_GAME_SETUP_MODE],
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
            "coordinates": scaling.scale_coordinates(0, -400),
            "width": scaling.scale_width(400),
            "height": scaling.scale_height(430),
            "modes": [constants.STRATEGIC_MODE, constants.EARTH_MODE],
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
        constants.actor_creation_manager.create_interface_element(
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


def mob_sub_interface():
    """
    Description:
        Initializes elements of mob interface, some of which are dependent on initalization of tabbed panels
    Input:
        None
    Output:
        None
    """
    # mob background image's tooltip
    mob_free_image_background_tooltip = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(0, 0),
                "minimum_width": scaling.scale_width(115),
                "height": scaling.scale_height(115),
                "image_id": "misc/empty.png",
                "actor_type": constants.MOB_ACTOR_TYPE,
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
            "modes": [constants.STRATEGIC_MODE, constants.EARTH_MODE],
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
        "modes": [constants.STRATEGIC_MODE, constants.EARTH_MODE],
        "image_id": "buttons/fire_minister_button.png",
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
            "modes": [constants.STRATEGIC_MODE, constants.EARTH_MODE],
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
            "modes": [constants.STRATEGIC_MODE, constants.EARTH_MODE],
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
            "modes": [constants.STRATEGIC_MODE, constants.EARTH_MODE],
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
            "modes": [constants.STRATEGIC_MODE, constants.EARTH_MODE],
            "keybind_id": pygame.K_d,
            "image_id": "buttons/right_button.png",
            "init_type": constants.MOVE_RIGHT_BUTTON,
            "parent_collection": status.mob_info_display,
            "member_config": {"order_exempt": True},
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
            "image_id": "misc/default_label.png",
            "init_type": current_actor_label_type,
            "actor_type": constants.MOB_ACTOR_TYPE,
            "parent_collection": status.mob_info_display,
            "member_config": {"order_x_offset": x_displacement},
        }
        if current_actor_label_type == constants.BANNER_LABEL:
            input_dict["banner_type"] = "deadly conditions"
            input_dict["banner_text"] = "Deadly conditions - will die at end of turn"

        if current_actor_label_type != constants.CURRENT_PASSENGER_LABEL:
            constants.actor_creation_manager.create_interface_element(input_dict)
        else:
            input_dict["list_type"] = constants.SPACESHIP_PERMISSION
            for i in range(0, 3):  # 0, 1, 2
                # label for each passenger
                input_dict["list_index"] = i
                constants.actor_creation_manager.create_interface_element(input_dict)


def tile_interface():
    """
    Description:
        Initializes tile selection interface
    Input:
        None
    Output:
        None
    """
    status.tile_info_display = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, 0),  # (0, -400),
            "width": scaling.scale_width(775),
            "height": scaling.scale_height(10),
            "modes": [constants.STRATEGIC_MODE, constants.EARTH_MODE],
            "init_type": constants.ORDERED_COLLECTION,
            "is_info_display": True,
            "actor_type": constants.TILE_ACTOR_TYPE,
            "description": "tile information panel",
            "parent_collection": status.info_displays_collection,
            # "member_config": {
            #     "order_exempt": True,
            # },
        }
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
        "modes": [constants.STRATEGIC_MODE, constants.EARTH_MODE],
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
            "modes": [constants.STRATEGIC_MODE, constants.EARTH_MODE],
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
            "modes": [constants.STRATEGIC_MODE, constants.EARTH_MODE],
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
                "actor_type": constants.TILE_ACTOR_TYPE,
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
            "modes": [constants.STRATEGIC_MODE, constants.EARTH_MODE],
            "actor_image_type": "default",
            "init_type": constants.ACTOR_DISPLAY_FREE_IMAGE,
            "parent_collection": status.tile_info_display,
            "member_config": {"order_overlap": False},
        }
    )

    # tile info labels setup
    for current_actor_label_type in [
        constants.COORDINATES_LABEL,
        constants.TERRAIN_LABEL,
        constants.PLANET_NAME_LABEL,
        constants.RESOURCE_LABEL,
        constants.TERRAIN_FEATURE_LABEL,
        constants.HABITABILITY_LABEL,
    ]:
        x_displacement = 0
        input_dict = {
            "minimum_width": scaling.scale_width(10),
            "height": scaling.scale_height(
                constants.default_notification_font_size + 5
            ),
            "image_id": "misc/default_label.png",
            "init_type": current_actor_label_type,
            "actor_type": constants.TILE_ACTOR_TYPE,
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
        else:
            constants.actor_creation_manager.create_interface_element(input_dict)

    tab_collection_relative_coordinates = (420, -30)

    status.tile_tabbed_collection = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(
                    tab_collection_relative_coordinates[0],
                    tab_collection_relative_coordinates[1],
                ),
                "width": scaling.scale_width(0),
                "height": scaling.scale_height(0),
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
        Initializes the item prices display and both mob/tile tabbed collections and inventory interfaces
    Input:
        None
    Output:
        None
    """
    item_prices_x, item_prices_y = (1000, 100)
    item_prices_height = 35 + (
        30
        * len(
            [
                current_item_type
                for current_item_type in status.item_types.values()
                if current_item_type.can_sell
            ]
        )
    )
    item_prices_width = 200

    status.item_prices_label = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(item_prices_x, item_prices_y),
                "minimum_width": scaling.scale_width(item_prices_width),
                "height": scaling.scale_height(item_prices_height),
                "modes": [constants.EARTH_MODE],
                "image_id": "misc/item_prices_label.png",
                "init_type": constants.ITEM_PRICES_LABEL,
            }
        )
    )

    input_dict = {
        "width": scaling.scale_width(30),
        "height": scaling.scale_height(30),
        "modes": [constants.EARTH_MODE],
        "init_type": constants.SELLABLE_ITEM_BUTTON,
    }
    current_index = 0
    for current_item_type in status.item_types.values():
        if current_item_type.can_sell:
            input_dict["coordinates"] = scaling.scale_coordinates(
                item_prices_x - 35,
                item_prices_y + item_prices_height - 65 - (30 * current_index),
            )
            input_dict["image_id"] = [
                "misc/green_circle.png",
                f"items/{current_item_type.key}.png",
            ]
            input_dict["item_type"] = current_item_type
            new_sellable_item_button = (
                constants.actor_creation_manager.create_interface_element(input_dict)
            )
            current_index += 1

    status.mob_inventory_collection = (
        constants.actor_creation_manager.create_interface_element(
            {
                "width": scaling.scale_width(0),
                "height": scaling.scale_height(0),
                "init_type": constants.ORDERED_COLLECTION,
                "parent_collection": status.mob_tabbed_collection,
                "member_config": {
                    "tabbed": True,
                    "button_image_id": [
                        "buttons/default_button_alt2.png",
                        {"image_id": "misc/green_circle.png", "size": 0.75},
                        {"image_id": "items/consumer_goods.png", "size": 0.75},
                    ],
                    "identifier": constants.INVENTORY_PANEL,
                    "tab_name": "cargo",
                },
            }
        )
    )

    input_dict = {
        "minimum_width": scaling.scale_width(10),
        "height": scaling.scale_height(constants.default_notification_font_size + 5),
        "image_id": "misc/default_label.png",
        "init_type": constants.MOB_INVENTORY_CAPACITY_LABEL,
        "actor_type": constants.MOB_ACTOR_TYPE,
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
                "actor_type": constants.MOB_INVENTORY_ACTOR_TYPE,
                "member_config": {
                    "second_dimension_coordinate": current_index % 9,
                    "order_y_offset": status.mob_inventory_grid.height,
                },
            }
        )

    status.mob_inventory_info_display = (
        constants.actor_creation_manager.create_interface_element(
            {
                "width": scaling.scale_width(0),
                "height": scaling.scale_height(0),
                "init_type": constants.ORDERED_COLLECTION,
                "is_info_display": True,
                "actor_type": constants.MOB_INVENTORY_ACTOR_TYPE,
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
                "actor_type": constants.TILE_ACTOR_TYPE,
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
            "modes": [constants.STRATEGIC_MODE, constants.EARTH_MODE],
            "actor_image_type": "inventory_default",
            "init_type": constants.ACTOR_DISPLAY_FREE_IMAGE,
            "parent_collection": status.mob_inventory_info_display,
            "member_config": {"order_overlap": False},
        }
    )

    tile_scroll_up_button = constants.actor_creation_manager.create_interface_element(
        {
            "width": inventory_cell_width,
            "height": inventory_cell_height,
            "parent_collection": status.mob_inventory_grid,
            "image_id": "buttons/cycle_ministers_up_button.png",
            "value_name": "inventory_page",
            "increment": -1,
            "member_config": {
                "order_exempt": True,
                "x_offset": scaling.scale_width(-1.3 * inventory_cell_width),
                "y_offset": status.mob_inventory_grid.height
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
            "parent_collection": status.mob_inventory_grid,
            "image_id": "buttons/cycle_ministers_down_button.png",
            "value_name": "inventory_page",
            "increment": 1,
            "member_config": {
                "order_exempt": True,
                "x_offset": scaling.scale_width(-1.3 * inventory_cell_width),
                "y_offset": status.mob_inventory_grid.height - (inventory_cell_height),
            },
            "init_type": constants.SCROLL_BUTTON,
        }
    )

    for current_actor_label_type in [
        constants.INVENTORY_NAME_LABEL,
        constants.INVENTORY_QUANTITY_LABEL,
    ]:
        x_displacement = 0
        input_dict = {
            "minimum_width": scaling.scale_width(10),
            "height": scaling.scale_height(
                constants.default_notification_font_size + 5
            ),
            "image_id": "misc/default_label.png",
            "init_type": current_actor_label_type,
            "actor_type": constants.MOB_ACTOR_TYPE,
            "parent_collection": status.mob_inventory_info_display,
            "member_config": {"order_x_offset": scaling.scale_width(x_displacement)},
        }
        constants.actor_creation_manager.create_interface_element(input_dict)

    status.tile_inventory_collection = (
        constants.actor_creation_manager.create_interface_element(
            {
                "width": scaling.scale_width(0),
                "height": scaling.scale_height(0),
                "init_type": constants.ORDERED_COLLECTION,
                "parent_collection": status.tile_tabbed_collection,
                "member_config": {
                    "tabbed": True,
                    "button_image_id": [
                        "buttons/default_button_alt2.png",
                        {"image_id": "misc/green_circle.png", "size": 0.75},
                        {"image_id": "items/consumer_goods.png", "size": 0.75},
                    ],
                    "identifier": constants.INVENTORY_PANEL,
                    "tab_name": "warehouses",
                },
            }
        )
    )

    input_dict = {
        "minimum_width": scaling.scale_width(10),
        "height": scaling.scale_height(constants.default_notification_font_size + 5),
        "image_id": "misc/default_label.png",
        "init_type": constants.TILE_INVENTORY_CAPACITY_LABEL,
        "actor_type": constants.TILE_ACTOR_TYPE,
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
                "actor_type": constants.TILE_INVENTORY_ACTOR_TYPE,
                "member_config": {
                    "second_dimension_coordinate": current_index % 9,
                    "order_y_offset": status.tile_inventory_grid.height,
                },
            }
        )

    status.tile_inventory_info_display = (
        constants.actor_creation_manager.create_interface_element(
            {
                "width": scaling.scale_width(0),
                "height": scaling.scale_height(0),
                "init_type": constants.ORDERED_COLLECTION,
                "is_info_display": True,
                "actor_type": constants.TILE_INVENTORY_ACTOR_TYPE,
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
                "actor_type": constants.TILE_ACTOR_TYPE,
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
            "modes": [constants.STRATEGIC_MODE, constants.EARTH_MODE],
            "actor_image_type": "inventory_default",
            "init_type": constants.ACTOR_DISPLAY_FREE_IMAGE,
            "parent_collection": status.tile_inventory_info_display,
            "member_config": {"order_overlap": False},
        }
    )

    for current_actor_label_type in [
        constants.INVENTORY_NAME_LABEL,
        constants.INVENTORY_QUANTITY_LABEL,
    ]:
        x_displacement = 0
        input_dict = {
            "minimum_width": scaling.scale_width(10),
            "height": scaling.scale_height(
                constants.default_notification_font_size + 5
            ),
            "image_id": "misc/default_label.png",
            "init_type": current_actor_label_type,
            "actor_type": constants.TILE_ACTOR_TYPE,
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
                "width": scaling.scale_width(0),
                "height": scaling.scale_height(0),
                "init_type": constants.ORDERED_COLLECTION,
                "parent_collection": status.tile_tabbed_collection,
                "member_config": {
                    "tabbed": True,
                    "button_image_id": "buttons/crew_train_button.png",
                    "identifier": constants.SETTLEMENT_PANEL,
                    "tab_name": "settlement",
                },
            }
        )
    )
    for current_actor_label_type in [
        constants.SETTLEMENT,
        constants.SPACEPORT,
        constants.TRAIN_STATION,
        constants.RESOURCE,
        constants.BUILDING_EFFICIENCY_LABEL,
        constants.BUILDING_WORK_CREWS_LABEL,
        constants.CURRENT_BUILDING_WORK_CREW_LABEL,
        constants.FORT,
        constants.SLUMS,
        # constants.INFRASTRUCTURE,
    ]:
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
            "height": scaling.scale_height(
                constants.default_notification_font_size + 5
            ),
            "image_id": "misc/default_label.png",
            "actor_type": constants.TILE_ACTOR_TYPE,
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
            input_dict["init_type"] = current_actor_label_type
            constants.actor_creation_manager.create_interface_element(input_dict)


def terrain_interface():
    """
    Description:
        Initializes the terrain interface as part of the tile tabbed collection
    Input:
        None
    Output:
        None
    """
    status.global_conditions_collection = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(0, 0),
                "width": scaling.scale_width(0),
                "height": scaling.scale_height(0),
                "init_type": constants.ORDERED_COLLECTION,
                "parent_collection": status.tile_tabbed_collection,
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
            "actor_type": constants.TILE_ACTOR_TYPE,
            "parent_collection": status.global_conditions_collection,
            "member_config": {"order_x_offset": scaling.scale_width(x_displacement)},
        }
        constants.actor_creation_manager.create_interface_element(input_dict)

    status.temperature_breakdown_collection = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(0, 0),
                "width": scaling.scale_width(0),
                "height": scaling.scale_height(0),
                "init_type": constants.ORDERED_COLLECTION,
                "parent_collection": status.tile_tabbed_collection,
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
            "actor_type": constants.TILE_ACTOR_TYPE,
            "parent_collection": status.temperature_breakdown_collection,
            "member_config": {"order_x_offset": scaling.scale_width(x_displacement)},
        }
        if current_actor_label_type == constants.BANNER_LABEL:
            input_dict["banner_type"] = "absolute zero"
            input_dict["banner_text"] = f"Absolute zero: {constants.ABSOLUTE_ZERO} °F"
        constants.actor_creation_manager.create_interface_element(input_dict)

    status.local_conditions_collection = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(0, 0),
                "width": scaling.scale_width(0),
                "height": scaling.scale_height(0),
                "init_type": constants.ORDERED_COLLECTION,
                "parent_collection": status.tile_tabbed_collection,
                "member_config": {
                    "tabbed": True,
                    "button_image_id": "buttons/crew_train_button.png",
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
            "actor_type": constants.TILE_ACTOR_TYPE,
            "parent_collection": status.local_conditions_collection,
            "member_config": {"order_x_offset": scaling.scale_width(x_displacement)},
        }
        if current_actor_label_type == constants.BANNER_LABEL:
            input_dict["banner_type"] = "terrain details"
            input_dict["banner_text"] = "Details unknown"
        constants.actor_creation_manager.create_interface_element(input_dict)

        status.albedo_free_image = (
            constants.actor_creation_manager.create_interface_element(
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


def organization_interface():
    """
    Description:
        Initializes the unit organization interface as part of the mob tabbed collection
    Input:
        None
    Output:
        None
    """
    image_height = 75
    status.mob_reorganization_collection = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(0, -1 * image_height),
                "width": scaling.scale_width(0),
                "height": scaling.scale_height(0),
                "init_type": constants.ORDERED_COLLECTION,
                "parent_collection": status.mob_tabbed_collection,
                "member_config": {
                    "tabbed": True,
                    "button_image_id": "buttons/merge_button.png",
                    "identifier": constants.REORGANIZATION_PANEL,
                    "tab_name": "reorganization",
                },
                "description": "unit organization panel",
                "direction": "vertical",
            }
        )
    )


def unit_organization_interface():
    """
    Description:
        Initializes the group organization interface as a subsection of the mob reorganization collection
    Input:
        None
    Output:
        None
    """
    image_height = 75
    lhs_x_offset = 95
    rhs_x_offset = image_height + 80

    status.group_reorganization_collection = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(0, 0),
                "width": scaling.scale_width(10),
                "height": scaling.scale_height(2 * image_height),
                "init_type": constants.AUTOFILL_COLLECTION,
                "parent_collection": status.mob_reorganization_collection,
                "direction": "horizontal",
                "block_height_offset": True,
                "member_config": {"order_x_offset": lhs_x_offset},
                "allowed_procedures": [
                    constants.MERGE_PROCEDURE,
                    constants.SPLIT_PROCEDURE,
                ],
                "autofill_targets": {
                    constants.OFFICER_PERMISSION: [],
                    constants.WORKER_PERMISSION: [],
                    constants.GROUP_PERMISSION: [],
                },
            }
        )
    )

    # mob background image's tooltip
    lhs_top_tooltip = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, 0),
            "minimum_width": scaling.scale_width(image_height - 10),
            "height": scaling.scale_height(image_height - 10),
            "image_id": "misc/empty.png",
            "actor_type": constants.MOB_ACTOR_TYPE,
            "init_type": constants.ACTOR_TOOLTIP_LABEL,
            "parent_collection": status.group_reorganization_collection,
            "member_config": {"calibrate_exempt": True},
            "default_tooltip_text": [
                "Select an officer to fill this slot",
                "If a worker and an officer are selected, they can be merged into a group",
            ],
        }
    )
    status.group_reorganization_collection.autofill_targets[
        constants.OFFICER_PERMISSION
    ].append(lhs_top_tooltip)

    # mob image
    lhs_top_mob_free_image = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, 0),
            "width": scaling.scale_width(image_height - 10),
            "height": scaling.scale_height(image_height - 10),
            "modes": [constants.STRATEGIC_MODE, constants.EARTH_MODE],
            "actor_image_type": "default",
            "default_image_id": "mobs/default/mock_officer.png",
            "init_type": constants.ACTOR_DISPLAY_FREE_IMAGE,
            "parent_collection": status.group_reorganization_collection,
            "member_config": {
                "calibrate_exempt": True,
                "x_offset": scaling.scale_width(0),
            },
        }
    )
    status.group_reorganization_collection.autofill_targets[
        constants.OFFICER_PERMISSION
    ].append(lhs_top_mob_free_image)

    # mob background image's tooltip
    lhs_bottom_tooltip = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, -1 * (image_height - 5)),
            "minimum_width": scaling.scale_width(image_height - 10),
            "height": scaling.scale_height(image_height - 10),
            "image_id": "misc/empty.png",
            "actor_type": constants.MOB_ACTOR_TYPE,
            "init_type": constants.ACTOR_TOOLTIP_LABEL,
            "parent_collection": status.group_reorganization_collection,
            "member_config": {"calibrate_exempt": True},
            "default_tooltip_text": [
                "Select a worker to fill this slot",
                "If a worker and an officer are selected, they can be merged into a group",
            ],
        }
    )
    status.group_reorganization_collection.autofill_targets[
        constants.WORKER_PERMISSION
    ].append(lhs_bottom_tooltip)

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
                "modes": [constants.STRATEGIC_MODE, constants.EARTH_MODE],
                "actor_image_type": "default",
                "default_image_id": default_image_id,
                "init_type": constants.ACTOR_DISPLAY_FREE_IMAGE,
                "parent_collection": status.group_reorganization_collection,
                "member_config": {
                    "calibrate_exempt": True,
                    "y_offset": scaling.scale_height(-1 * (image_height - 5)),
                },
            }
        )
    )
    status.group_reorganization_collection.autofill_targets[
        constants.WORKER_PERMISSION
    ].append(lhs_bottom_mob_free_image)

    # right side
    # mob background image's tooltip
    rhs_top_tooltip = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, 0),
            "minimum_width": scaling.scale_width(image_height - 10),
            "height": scaling.scale_height(image_height - 10),
            "image_id": "misc/empty.png",
            "actor_type": constants.MOB_ACTOR_TYPE,
            "init_type": constants.ACTOR_TOOLTIP_LABEL,
            "parent_collection": status.group_reorganization_collection,
            "member_config": {
                "calibrate_exempt": True,
                "x_offset": scaling.scale_width(rhs_x_offset),
                "y_offset": scaling.scale_height(-0.5 * (image_height)),
            },
            "default_tooltip_text": [
                "Select a worker and officer to fill this slot with their combined group",
            ],
        }
    )
    status.group_reorganization_collection.autofill_targets[
        constants.GROUP_PERMISSION
    ].append(rhs_top_tooltip)

    # mob image
    default_image_id = [
        actor_utility.generate_unit_component_image_id(
            "mobs/default/mock_worker.png", "group left", to_front=True
        ),
        actor_utility.generate_unit_component_image_id(
            "mobs/default/mock_worker.png", "group right", to_front=True
        ),
        actor_utility.generate_unit_component_image_id(
            "mobs/default/mock_officer.png", "center", to_front=True
        ),
    ]
    rhs_top_mob_free_image = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, 0),
            "width": scaling.scale_width(image_height - 10),
            "height": scaling.scale_height(image_height - 10),
            "modes": [constants.STRATEGIC_MODE, constants.EARTH_MODE],
            "actor_image_type": "default",
            "default_image_id": default_image_id,
            "init_type": constants.ACTOR_DISPLAY_FREE_IMAGE,
            "parent_collection": status.group_reorganization_collection,
            "member_config": {
                "calibrate_exempt": True,
                "x_offset": scaling.scale_width(rhs_x_offset),
                "y_offset": scaling.scale_height(-0.5 * (image_height)),
            },
        }
    )
    status.group_reorganization_collection.autofill_targets[
        constants.GROUP_PERMISSION
    ].append(rhs_top_mob_free_image)

    # reorganize unit to right button
    status.reorganize_group_right_button = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(
                    rhs_x_offset - 60 - 15,
                    -1 * (image_height - 15) + 40 - 15 + 30 + 5,
                ),
                "width": scaling.scale_width(60),
                "height": scaling.scale_height(25),
                "init_type": constants.REORGANIZE_UNIT_BUTTON,
                "parent_collection": status.group_reorganization_collection,
                "image_id": "buttons/cycle_units_button.png",
                "allowed_procedures": [
                    constants.MERGE_PROCEDURE,
                ],
                "keybind_id": pygame.K_m,
                "enable_shader": True,
            }
        )
    )

    # reorganize unit to left button
    status.reorganize_group_left_button = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(
                    rhs_x_offset - 60 - 15,
                    -1 * (image_height - 15) + 40 - 15 + 5,
                ),
                "width": scaling.scale_width(60),
                "height": scaling.scale_height(25),
                "init_type": constants.REORGANIZE_UNIT_BUTTON,
                "parent_collection": status.group_reorganization_collection,
                "image_id": "buttons/cycle_units_reverse_button.png",
                "allowed_procedures": [
                    constants.SPLIT_PROCEDURE,
                ],
                "keybind_id": pygame.K_n,
                "enable_shader": True,
            }
        )
    )

    input_dict = {
        "coordinates": scaling.scale_coordinates(
            35 - image_height, -1 * (image_height - 15) + 95 - 35 / 2
        ),
        "width": scaling.scale_width(30),
        "height": scaling.scale_height(30),
        "init_type": constants.CYCLE_AUTOFILL_BUTTON,
        "parent_collection": status.group_reorganization_collection,
        "image_id": "buttons/reset_button.png",
        "autofill_target_type": constants.OFFICER_PERMISSION,
    }
    cycle_autofill_officer_button = (
        constants.actor_creation_manager.create_interface_element(input_dict)
    )

    input_dict = {
        "coordinates": scaling.scale_coordinates(
            35 - image_height, -1 * (image_height - 15) + 25 - 35 / 2
        ),
        "width": input_dict["width"],  # copies most attributes from previous button
        "height": input_dict["height"],
        "init_type": input_dict["init_type"],
        "parent_collection": input_dict["parent_collection"],
        "image_id": input_dict["image_id"],
        "autofill_target_type": constants.WORKER_PERMISSION,
    }
    cycle_autofill_worker_button = (
        constants.actor_creation_manager.create_interface_element(input_dict)
    )


def vehicle_organization_interface():
    """
    Description:
        Initializes the vehicle organization interface as a subsection of the mob reorganization collection
    Input:
        None
    Output:
        None
    """
    image_height = 75
    lhs_x_offset = 95
    rhs_x_offset = image_height + 80
    status.vehicle_reorganization_collection = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(0, 0),
                "width": scaling.scale_width(0),
                "height": scaling.scale_height(2 * image_height),
                "init_type": constants.AUTOFILL_COLLECTION,
                "parent_collection": status.mob_reorganization_collection,
                "direction": "horizontal",
                "block_height_offset": True,
                "member_config": {"order_x_offset": lhs_x_offset},
                "allowed_procedures": [
                    constants.CREW_PROCEDURE,
                    constants.UNCREW_PROCEDURE,
                ],
                "autofill_targets": {
                    constants.INACTIVE_VEHICLE_PERMISSION: [],
                    constants.CREW_VEHICLE_PERMISSION: [],
                    constants.ACTIVE_VEHICLE_PERMISSION: [],
                },
            }
        )
    )

    # mob background image's tooltip
    lhs_top_tooltip = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, 0),
            "minimum_width": scaling.scale_width(image_height - 10),
            "height": scaling.scale_height(image_height - 10),
            "image_id": "misc/empty.png",
            "actor_type": constants.MOB_ACTOR_TYPE,
            "init_type": constants.ACTOR_TOOLTIP_LABEL,
            "parent_collection": status.vehicle_reorganization_collection,
            "member_config": {"calibrate_exempt": True},
            "default_tooltip_text": [
                "Select an uncrewed vehicle to fill this slot",
                "If an uncrewed vehicle and a valid crew are selected, the vehicle can be crewed",
            ],
        }
    )
    status.vehicle_reorganization_collection.autofill_targets[
        constants.INACTIVE_VEHICLE_PERMISSION
    ].append(lhs_top_tooltip)

    # mob image
    lhs_top_mob_free_image = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, 0),
            "width": scaling.scale_width(image_height - 10),
            "height": scaling.scale_height(image_height - 10),
            "modes": [constants.STRATEGIC_MODE, constants.EARTH_MODE],
            "actor_image_type": "default",
            "default_image_id": "mobs/default/mock_uncrewed_vehicle.png",
            "init_type": constants.ACTOR_DISPLAY_FREE_IMAGE,
            "parent_collection": status.vehicle_reorganization_collection,
            "member_config": {
                "calibrate_exempt": True,
                "x_offset": scaling.scale_width(0),
            },
        }
    )
    status.vehicle_reorganization_collection.autofill_targets[
        constants.INACTIVE_VEHICLE_PERMISSION
    ].append(lhs_top_mob_free_image)

    # mob background image's tooltip
    lhs_bottom_tooltip = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, -1 * (image_height - 5)),
            "minimum_width": scaling.scale_width(image_height - 10),
            "height": scaling.scale_height(image_height - 10),
            "image_id": "misc/empty.png",
            "actor_type": constants.MOB_ACTOR_TYPE,
            "init_type": constants.ACTOR_TOOLTIP_LABEL,
            "parent_collection": status.vehicle_reorganization_collection,
            "member_config": {"calibrate_exempt": True},
            "default_tooltip_text": [
                "Select a valid crew to fill this slot",
                "If an uncrewed vehicle and a valid crew are selected, the vehicle can be crewed",
            ],
        }
    )
    status.vehicle_reorganization_collection.autofill_targets[
        constants.CREW_VEHICLE_PERMISSION
    ].append(lhs_bottom_tooltip)

    # mob image
    default_image_id = [
        actor_utility.generate_unit_component_image_id(
            "mobs/default/mock_worker.png", "group left", to_front=True
        ),
        actor_utility.generate_unit_component_image_id(
            "mobs/default/mock_worker.png", "group right", to_front=True
        ),
        actor_utility.generate_unit_component_image_id(
            "mobs/default/mock_officer.png", "center", to_front=True
        ),
    ]
    lhs_bottom_mob_free_image = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(0, 0),
                "width": scaling.scale_width(image_height - 10),
                "height": scaling.scale_height(image_height - 10),
                "modes": [constants.STRATEGIC_MODE, constants.EARTH_MODE],
                "actor_image_type": "default",
                "default_image_id": default_image_id,
                "init_type": constants.ACTOR_DISPLAY_FREE_IMAGE,
                "parent_collection": status.vehicle_reorganization_collection,
                "member_config": {
                    "calibrate_exempt": True,
                    "y_offset": scaling.scale_height(-1 * (image_height - 5)),
                },
            }
        )
    )
    status.vehicle_reorganization_collection.autofill_targets[
        constants.CREW_VEHICLE_PERMISSION
    ].append(lhs_bottom_mob_free_image)

    # right side
    # mob background image's tooltip
    rhs_top_tooltip = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, 0),
            "minimum_width": scaling.scale_width(image_height - 10),
            "height": scaling.scale_height(image_height - 10),
            "image_id": "misc/empty.png",
            "actor_type": constants.MOB_ACTOR_TYPE,
            "init_type": constants.ACTOR_TOOLTIP_LABEL,
            "parent_collection": status.vehicle_reorganization_collection,
            "member_config": {
                "calibrate_exempt": True,
                "x_offset": scaling.scale_width(rhs_x_offset),
                "y_offset": scaling.scale_height(-0.5 * (image_height)),
            },
            "default_tooltip_text": [
                "Select an uncrewed vehicle and a crew to fill this slot with a crewed vehicle",
            ],
        }
    )
    status.vehicle_reorganization_collection.autofill_targets[
        constants.ACTIVE_VEHICLE_PERMISSION
    ].append(rhs_top_tooltip)

    # mob image
    rhs_top_mob_free_image = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, 0),
            "width": scaling.scale_width(image_height - 10),
            "height": scaling.scale_height(image_height - 10),
            "modes": [constants.STRATEGIC_MODE, constants.EARTH_MODE],
            "actor_image_type": "default",
            "default_image_id": "mobs/default/mock_crewed_vehicle.png",
            "init_type": constants.ACTOR_DISPLAY_FREE_IMAGE,
            "parent_collection": status.vehicle_reorganization_collection,
            "member_config": {
                "calibrate_exempt": True,
                "x_offset": scaling.scale_width(rhs_x_offset),
                "y_offset": scaling.scale_height(-0.5 * (image_height)),
            },
        }
    )
    status.vehicle_reorganization_collection.autofill_targets[
        constants.ACTIVE_VEHICLE_PERMISSION
    ].append(rhs_top_mob_free_image)

    # reorganize unit to right button
    status.reorganize_vehicle_right_button = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(
                    rhs_x_offset - 60 - 15,
                    -1 * (image_height - 15) + 40 - 15 + 30 + 5,
                ),
                "width": scaling.scale_width(60),
                "height": scaling.scale_height(25),
                "init_type": constants.REORGANIZE_UNIT_BUTTON,
                "parent_collection": status.vehicle_reorganization_collection,
                "image_id": "buttons/cycle_units_button.png",
                "allowed_procedures": [
                    constants.CREW_PROCEDURE,
                ],
                "keybind_id": pygame.K_m,
                "enable_shader": True,
            }
        )
    )

    # reorganize unit to left button
    status.reorganize_vehicle_left_button = (
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(
                    rhs_x_offset - 60 - 15,
                    -1 * (image_height - 15) + 40 - 15 + 5,
                ),
                "width": scaling.scale_width(60),
                "height": scaling.scale_height(25),
                "init_type": constants.REORGANIZE_UNIT_BUTTON,
                "parent_collection": status.vehicle_reorganization_collection,
                "image_id": "buttons/cycle_units_reverse_button.png",
                "allowed_procedures": [
                    constants.UNCREW_PROCEDURE,
                ],
                "keybind_id": pygame.K_n,
                "enable_shader": True,
            }
        )
    )

    input_dict = {
        "coordinates": scaling.scale_coordinates(
            35 - image_height, -1 * (image_height - 15) + 95 - 35 / 2
        ),
        "width": scaling.scale_width(30),
        "height": scaling.scale_height(30),
        "init_type": constants.CYCLE_AUTOFILL_BUTTON,
        "parent_collection": status.vehicle_reorganization_collection,
        "image_id": "buttons/reset_button.png",
        "autofill_target_type": constants.INACTIVE_VEHICLE_PERMISSION,
    }
    cycle_autofill_vehicle_button = (
        constants.actor_creation_manager.create_interface_element(input_dict)
    )

    input_dict = {
        "coordinates": scaling.scale_coordinates(
            35 - image_height, -1 * (image_height - 15) + 25 - 35 / 2
        ),
        "width": input_dict["width"],  # Copies most attributes from previous button
        "height": input_dict["height"],
        "init_type": input_dict["init_type"],
        "parent_collection": input_dict["parent_collection"],
        "image_id": input_dict["image_id"],
        "autofill_target_type": constants.CREW_VEHICLE_PERMISSION,
    }
    cycle_autofill_crew_button = (
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
                "modes": [constants.MINISTERS_MODE],
                "init_type": constants.ORDERED_COLLECTION,
                "is_info_display": True,
                "actor_type": constants.MINISTER_ACTOR_TYPE,
                "allow_minimize": False,
                "allow_move": False,
                "description": "minister information panel",
                "parent_collection": status.info_displays_collection,
            }
        )
    )

    # minister background image
    # minister_free_image_background = (
    #     constants.actor_creation_manager.create_interface_element(
    #         {
    #             "image_id": "misc/actor_backgrounds/minister_background.png",
    #             "coordinates": scaling.scale_coordinates(0, 0),
    #             "width": scaling.scale_width(125),
    #             "height": scaling.scale_height(125),
    #             "modes": [constants.MINISTERS_MODE],
    #             "init_type": constants.ACTOR_DISPLAY_FREE_IMAGE,
    #             "parent_collection": status.minister_info_display,
    #             "member_config": {"order_overlap": True},
    #         }
    #     )
    # )

    # minister image
    minister_free_image = constants.actor_creation_manager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, 0),
            "width": scaling.scale_width(115),
            "height": scaling.scale_height(115),
            "modes": [constants.MINISTERS_MODE],
            "actor_image_type": "default",
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
                "actor_type": constants.MINISTER_ACTOR_TYPE,
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
        "height": scaling.scale_height(constants.default_notification_font_size + 5),
        "image_id": "misc/default_label.png",
        "actor_type": constants.MINISTER_ACTOR_TYPE,
        "init_type": constants.ACTOR_DISPLAY_LABEL,
        "parent_collection": status.minister_info_display,
    }

    # minister info labels setup
    for current_actor_label_type in [
        constants.MINISTER_OFFICE_LABEL,
        constants.MINISTER_NAME_LABEL,
        constants.MINISTER_ETHNICITY_LABEL,
        constants.MINISTER_BACKGROUND_LABEL,
        constants.MINISTER_SOCIAL_STATUS_LABEL,
        constants.MINISTER_INTERESTS_LABEL,
        constants.MINISTER_LOYALTY_LABEL,
        constants.MINISTER_ABILITY_LABEL,
        constants.SPACE_SKILL_LABEL,
        constants.ECOLOGY_SKILL_LABEL,
        constants.TERRAN_AFFAIRS_SKILL_LABEL,
        constants.SCIENCE_SKILL_LABEL,
        constants.INDUSTRY_SKILL_LABEL,
        constants.ENERGY_SKILL_LABEL,
        constants.TRANSPORTATION_SKILL_LABEL,
        constants.SECURITY_SKILL_LABEL,
        constants.EVIDENCE_LABEL,
    ]:
        if current_actor_label_type in [
            constants.SPACE_SKILL_LABEL,
            constants.ECOLOGY_SKILL_LABEL,
            constants.TERRAN_AFFAIRS_SKILL_LABEL,
            constants.SCIENCE_SKILL_LABEL,
            constants.ENERGY_SKILL_LABEL,
            constants.INDUSTRY_SKILL_LABEL,
            constants.TRANSPORTATION_SKILL_LABEL,
            constants.SECURITY_SKILL_LABEL,
            constants.MINISTER_SOCIAL_STATUS_LABEL,
        ]:
            # try displacing everything except office?
            x_displacement = 50
        elif current_actor_label_type != constants.MINISTER_OFFICE_LABEL:
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
