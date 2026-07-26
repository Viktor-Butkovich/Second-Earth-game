from __future__ import annotations
import pygame
from modules.constants import constants, status, flags
from modules.util import scaling, actor_utility, action_utility, callback_utility


def config_unit_organization_tab() -> None:
    """
    Initializes the unit organization interface as part of the mob tabbed collection
    """
    image_height = 75
    status.mob_reorganization_collection = (
        constants.ActorCreationManager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(0, -1 * image_height),
                "width": scaling.scale_width(0),
                "height": scaling.scale_height(0),
                "init_type": constants.ORDERED_COLLECTION,
                "parent_collection": status.mob_tabbed_collection,
                "member_config": {
                    "tabbed": True,
                    "button_image_id": actor_utility.generate_frame(
                        "buttons/merge_button.png",
                        background="buttons/default_button_frameless.png",
                    ),
                    "identifier": constants.REORGANIZATION_PANEL,
                    "tab_name": "reorganization",
                },
                "description": "unit organization panel",
                "direction": "vertical",
            }
        )
    )
    unit_organization_interface()
    vehicle_organization_interface()


def unit_organization_interface() -> None:
    """
    Initializes the group organization interface as a subsection of the mob reorganization collection
    """
    image_height = 75
    lhs_x_offset = 95
    rhs_x_offset = image_height + 80

    status.group_reorganization_collection = (
        constants.ActorCreationManager.create_interface_element(
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

    lhs_top_mob_icon_default_image = (
        action_utility.generate_background_image_id_list()
        + [
            {"image_id": "mobs/default/mock_officer.png"},
            {"image_id": "misc/dark_shader.png", "level": constants.FRONT_LEVEL - 1},
            {
                "image_id": "misc/actor_backgrounds/pmob_outline.png",  # Behind outline
                "detail_level": 1.0,
                "level": constants.FRONT_LEVEL,
            },
        ]
    )

    lhs_top_mob_icon = constants.ActorCreationManager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, 0),
            "actor_type": constants.MOB_ACTOR_TYPE,
            "width": scaling.scale_width(image_height - 10),
            "height": scaling.scale_height(image_height - 10),
            "init_type": constants.ACTOR_ICON,
            "parent_collection": status.group_reorganization_collection,
            "image_id": lhs_top_mob_icon_default_image,
            "member_config": {
                "calibrate_exempt": True,
            },
            "dynamic_tooltip_factory": callback_utility.officer_reorganization_tooltip_factory,
        }
    )
    status.group_reorganization_collection.autofill_targets[
        constants.OFFICER_PERMISSION
    ].append(lhs_top_mob_icon)

    lhs_bottom_mob_icon_default_image = (
        action_utility.generate_background_image_id_list()
        + [
            actor_utility.generate_unit_component_image_id(
                "mobs/default/mock_worker.png", "left", to_front=True
            ),
            actor_utility.generate_unit_component_image_id(
                "mobs/default/mock_worker.png", "right", to_front=True
            ),
            {"image_id": "misc/dark_shader.png", "level": constants.FRONT_LEVEL - 1},
            {
                "image_id": "misc/actor_backgrounds/pmob_outline.png",  # Behind outline
                "detail_level": 1.0,
                "level": constants.FRONT_LEVEL,
            },
        ]
    )

    lhs_bottom_mob_icon = constants.ActorCreationManager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, -1 * (image_height - 5)),
            "actor_type": constants.MOB_ACTOR_TYPE,
            "width": scaling.scale_width(image_height - 10),
            "height": scaling.scale_height(image_height - 10),
            "init_type": constants.ACTOR_ICON,
            "parent_collection": status.group_reorganization_collection,
            "image_id": lhs_bottom_mob_icon_default_image,
            "member_config": {
                "calibrate_exempt": True,
            },
            "dynamic_tooltip_factory": callback_utility.worker_reorganization_tooltip_factory,
        }
    )
    status.group_reorganization_collection.autofill_targets[
        constants.WORKER_PERMISSION
    ].append(lhs_bottom_mob_icon)

    rhs_mob_icon_default_image = action_utility.generate_background_image_id_list() + [
        actor_utility.generate_unit_component_image_id(
            "mobs/default/mock_worker.png", "group left", to_front=True
        ),
        actor_utility.generate_unit_component_image_id(
            "mobs/default/mock_worker.png", "group right", to_front=True
        ),
        actor_utility.generate_unit_component_image_id(
            "mobs/default/mock_officer.png", "center", to_front=True
        ),
        {"image_id": "misc/dark_shader.png", "level": constants.FRONT_LEVEL - 1},
        {
            "image_id": "misc/actor_backgrounds/pmob_outline.png",  # Behind outline
            "detail_level": 1.0,
            "level": constants.FRONT_LEVEL,
        },
    ]
    rhs_mob_icon = constants.ActorCreationManager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, 0),
            "actor_type": constants.MOB_ACTOR_TYPE,
            "width": scaling.scale_width(image_height - 10),
            "height": scaling.scale_height(image_height - 10),
            "init_type": constants.ACTOR_ICON,
            "parent_collection": status.group_reorganization_collection,
            "image_id": rhs_mob_icon_default_image,
            "member_config": {
                "calibrate_exempt": True,
                "x_offset": scaling.scale_width(rhs_x_offset),
                "y_offset": scaling.scale_height(-0.5 * (image_height)),
            },
            "dynamic_tooltip_factory": callback_utility.group_reorganization_tooltip_factory,
        }
    )
    status.group_reorganization_collection.autofill_targets[
        constants.GROUP_PERMISSION
    ].append(rhs_mob_icon)

    # reorganize unit to right button
    status.reorganize_group_right_button = (
        constants.ActorCreationManager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(
                    rhs_x_offset - 60 - 15,
                    -1 * (image_height - 15) + 40 - 15 + 30 + 5,
                ),
                "width": scaling.scale_width(60),
                "height": scaling.scale_height(25),
                "init_type": constants.REORGANIZE_UNIT_BUTTON,
                "parent_collection": status.group_reorganization_collection,
                "image_id": actor_utility.generate_frame(
                    "buttons/cycle_units_button.png",
                    background="buttons/default_button_frameless.png",
                ),
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
        constants.ActorCreationManager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(
                    rhs_x_offset - 60 - 15,
                    -1 * (image_height - 15) + 40 - 15 + 5,
                ),
                "width": scaling.scale_width(60),
                "height": scaling.scale_height(25),
                "init_type": constants.REORGANIZE_UNIT_BUTTON,
                "parent_collection": status.group_reorganization_collection,
                "image_id": actor_utility.generate_frame(
                    "buttons/cycle_units_reverse_button.png",
                    background="buttons/default_button_frameless.png",
                ),
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
        constants.ActorCreationManager.create_interface_element(input_dict)
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
        constants.ActorCreationManager.create_interface_element(input_dict)
    )


def vehicle_organization_interface() -> None:
    """
    Initializes the vehicle organization interface as a subsection of the mob reorganization collection
    """
    image_height = 75
    lhs_x_offset = 95
    rhs_x_offset = image_height + 80
    status.vehicle_reorganization_collection = (
        constants.ActorCreationManager.create_interface_element(
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

    lhs_top_mob_icon_default_image = (
        action_utility.generate_background_image_id_list()
        + [
            {
                "image_id": "mobs/default/mock_uncrewed_vehicle.png",
            },
            {"image_id": "misc/dark_shader.png", "level": constants.FRONT_LEVEL - 1},
            {
                "image_id": "misc/actor_backgrounds/pmob_outline.png",  # Behind outline
                "detail_level": 1.0,
                "level": constants.FRONT_LEVEL,
            },
        ]
    )

    lhs_top_mob_icon = constants.ActorCreationManager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, 0),
            "actor_type": constants.MOB_ACTOR_TYPE,
            "width": scaling.scale_width(image_height - 10),
            "height": scaling.scale_height(image_height - 10),
            "init_type": constants.ACTOR_ICON,
            "parent_collection": status.vehicle_reorganization_collection,
            "image_id": lhs_top_mob_icon_default_image,
            "member_config": {
                "calibrate_exempt": True,
            },
            "dynamic_tooltip_factory": callback_utility.uncrewed_vehicle_reorganization_tooltip_factory,
        }
    )
    status.vehicle_reorganization_collection.autofill_targets[
        constants.INACTIVE_VEHICLE_PERMISSION
    ].append(lhs_top_mob_icon)

    lhs_bottom_mob_icon_default_image = (
        action_utility.generate_background_image_id_list()
        + [
            actor_utility.generate_unit_component_image_id(
                "mobs/default/mock_worker.png", "group left", to_front=True
            ),
            actor_utility.generate_unit_component_image_id(
                "mobs/default/mock_worker.png", "group right", to_front=True
            ),
            actor_utility.generate_unit_component_image_id(
                "mobs/default/mock_officer.png", "center", to_front=True
            ),
            {"image_id": "misc/dark_shader.png", "level": constants.FRONT_LEVEL - 1},
            {
                "image_id": "misc/actor_backgrounds/pmob_outline.png",  # Behind outline
                "detail_level": 1.0,
                "level": constants.FRONT_LEVEL,
            },
        ]
    )

    lhs_bottom_mob_icon = constants.ActorCreationManager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, -1 * (image_height - 5)),
            "actor_type": constants.MOB_ACTOR_TYPE,
            "width": scaling.scale_width(image_height - 10),
            "height": scaling.scale_height(image_height - 10),
            "init_type": constants.ACTOR_ICON,
            "parent_collection": status.vehicle_reorganization_collection,
            "image_id": lhs_bottom_mob_icon_default_image,
            "member_config": {
                "calibrate_exempt": True,
            },
            "dynamic_tooltip_factory": callback_utility.crew_reorganization_tooltip_factory,
        }
    )
    status.vehicle_reorganization_collection.autofill_targets[
        constants.CREW_VEHICLE_PERMISSION
    ].append(lhs_bottom_mob_icon)

    rhs_mob_icon_default_image = action_utility.generate_background_image_id_list() + [
        {
            "image_id": "mobs/default/mock_crewed_vehicle.png",
        },
        {"image_id": "misc/dark_shader.png", "level": constants.FRONT_LEVEL - 1},
        {
            "image_id": "misc/actor_backgrounds/pmob_outline.png",  # Behind outline
            "detail_level": 1.0,
            "level": constants.FRONT_LEVEL,
        },
    ]
    rhs_mob_icon = constants.ActorCreationManager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, 0),
            "actor_type": constants.MOB_ACTOR_TYPE,
            "width": scaling.scale_width(image_height - 10),
            "height": scaling.scale_height(image_height - 10),
            "init_type": constants.ACTOR_ICON,
            "parent_collection": status.vehicle_reorganization_collection,
            "image_id": rhs_mob_icon_default_image,
            "member_config": {
                "calibrate_exempt": True,
                "x_offset": scaling.scale_width(rhs_x_offset),
                "y_offset": scaling.scale_height(-0.5 * (image_height)),
            },
            "dynamic_tooltip_factory": callback_utility.active_vehicle_reorganization_tooltip_factory,
        }
    )
    status.vehicle_reorganization_collection.autofill_targets[
        constants.ACTIVE_VEHICLE_PERMISSION
    ].append(rhs_mob_icon)

    # reorganize unit to right button
    status.reorganize_vehicle_right_button = (
        constants.ActorCreationManager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(
                    rhs_x_offset - 60 - 15,
                    -1 * (image_height - 15) + 40 - 15 + 30 + 5,
                ),
                "width": scaling.scale_width(60),
                "height": scaling.scale_height(25),
                "init_type": constants.REORGANIZE_UNIT_BUTTON,
                "parent_collection": status.vehicle_reorganization_collection,
                "image_id": actor_utility.generate_frame(
                    "buttons/cycle_units_button.png",
                    background="buttons/default_button_frameless.png",
                ),
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
        constants.ActorCreationManager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(
                    rhs_x_offset - 60 - 15,
                    -1 * (image_height - 15) + 40 - 15 + 5,
                ),
                "width": scaling.scale_width(60),
                "height": scaling.scale_height(25),
                "init_type": constants.REORGANIZE_UNIT_BUTTON,
                "parent_collection": status.vehicle_reorganization_collection,
                "image_id": actor_utility.generate_frame(
                    "buttons/cycle_units_reverse_button.png",
                    background="buttons/default_button_frameless.png",
                ),
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
        constants.ActorCreationManager.create_interface_element(input_dict)
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
        constants.ActorCreationManager.create_interface_element(input_dict)
    )
