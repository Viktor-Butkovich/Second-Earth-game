from __future__ import annotations
import pygame
from modules.constants import constants, status, flags
from modules.constructs import unit_types


def config_unit_types() -> None:
    """
    Defines unit type templates
    """
    standard_officer_upkeep = {}
    standard_officer_required = {
        constants.RESOURCE_AIR: True,
        constants.RESOURCE_WATER: True,
        constants.RESOURCE_FOOD: True,
        constants.RESOURCE_CONSUMER_GOODS: True,
        # constants.RESOURCE_ENERGY: True,
    }
    standard_colonist_upkeep = {
        constants.RESOURCE_AIR: 0.1,
        constants.RESOURCE_WATER: 0.1,
        constants.RESOURCE_FOOD: 0.1,
        constants.RESOURCE_CONSUMER_GOODS: 0.1,
        # constants.RESOURCE_ENERGY: 0.1,
    }
    standard_missing_upkeep_penalties = {
        constants.RESOURCE_AIR: constants.UPKEEP_MISSING_PENALTY_DEATH,
        constants.RESOURCE_WATER: constants.UPKEEP_MISSING_PENALTY_DEHYDRATION,
        constants.RESOURCE_FOOD: constants.UPKEEP_MISSING_PENALTY_STARVATION,
        constants.RESOURCE_CONSUMER_GOODS: constants.UPKEEP_MISSING_PENALTY_MORALE,
        # constants.RESOURCE_ENERGY: constants.UPKEEP_MISSING_PENALTY_MORALE,
    }
    if not constants.EffectManager.effect_active("hide_old_units"):
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
                "item_upkeep": standard_officer_upkeep,
                "required_item_upkeep": standard_officer_required,
                "missing_upkeep_penalties": standard_missing_upkeep_penalties,
                "can_recruit": True,
                "recruitment_verb": "hire",
                "recruitment_cost": 5,
                "description": [
                    f"Explorers are controlled by the {status.minister_types[constants.SCIENCE_MINISTER].name}.",
                    "An explorer combines with colonists to form an expedition, which can explore new locations.",
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
                "item_upkeep": standard_officer_upkeep,
                "required_item_upkeep": standard_officer_required,
                "missing_upkeep_penalties": standard_missing_upkeep_penalties,
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
                "item_upkeep": standard_officer_upkeep,
                "required_item_upkeep": standard_officer_required,
                "missing_upkeep_penalties": standard_missing_upkeep_penalties,
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
                "base_inventory_capacity": 9,
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
                "item_upkeep": standard_officer_upkeep,
                "required_item_upkeep": standard_officer_required,
                "missing_upkeep_penalties": standard_missing_upkeep_penalties,
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
                "item_upkeep": standard_officer_upkeep,
                "required_item_upkeep": standard_officer_required,
                "missing_upkeep_penalties": standard_missing_upkeep_penalties,
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
            "item_upkeep": standard_officer_upkeep,
            "required_item_upkeep": standard_officer_required,
            "missing_upkeep_penalties": standard_missing_upkeep_penalties,
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
            "item_upkeep": standard_officer_upkeep,
            "required_item_upkeep": standard_officer_required,
            "missing_upkeep_penalties": standard_missing_upkeep_penalties,
            "can_recruit": True,
            "recruitment_verb": "hire",
            "recruitment_cost": 5,
            "description": [
                f"Engineers are controlled by the {status.minister_types[constants.INDUSTRY_MINISTER].name}.",
                "An engineer combines with colonists to form a construction crew, which can build buildings, roads, railroads, and trains.",
            ],
        },
    ).link_group_type(status.unit_types[constants.CONSTRUCTION_CREW])

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
            "base_inventory_capacity": 9,
        },
    )
    unit_types.officer_type(
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
            "item_upkeep": standard_officer_upkeep,
            "missing_upkeep_penalties": standard_missing_upkeep_penalties,
            "required_item_upkeep": standard_officer_required,
            "can_recruit": True,
            "recruitment_verb": "hire",
            "recruitment_cost": 5,
            "description": [
                f"Merchants are controlled by the {status.minister_types[constants.TERRAN_AFFAIRS_MINISTER].name}, and can personally search for loans and conduct advertising campaigns on Earth.",
                "A merchant combines with colonists to form a caravan, which can trade and build trading posts.",
            ],
        },
    ).link_group_type(caravan_group_type)

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
            "item_upkeep": standard_colonist_upkeep,
            "missing_upkeep_penalties": standard_missing_upkeep_penalties,
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
            "base_inventory_capacity": 81,
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
