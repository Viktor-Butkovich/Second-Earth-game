# Contains dedicated callback and utility functions

from typing import List, Any
from modules.util import utility
from modules.constants import constants, status, flags


def uncrewed_vehicle_reorganization_tooltip_factory(target_label: Any) -> List[str]:
    """
    Makes a tooltip for the uncrewed vehicle input slot in the vehicle reorganization interface
    """
    if target_label.actor:
        return target_label.actor.tooltip_text
    elif status.vehicle_reorganization_collection.autofill_actors[
        constants.CREW_VEHICLE_PERMISSION
    ].get_permission(constants.ASTRONAUTS_PERMISSION):
        return [
            "Find an uncrewed spaceship to fill this slot",
            "If astronauts and an uncrewed spaceship share a location, the spaceship can be crewed",
        ]
    else:
        return [
            "Find an uncrewed vehicle to fill this slot",
            "If an uncrewed vehicle and a valid crew share a location, the vehicle can be crewed",
        ]


def crew_reorganization_tooltip_factory(target_label: Any) -> List[str]:
    """
    Makes a tooltip for the crew input slot in the vehicle reorganization interface
    """
    if target_label.actor:
        return target_label.actor.tooltip_text
    elif status.vehicle_reorganization_collection.autofill_actors[
        constants.INACTIVE_VEHICLE_PERMISSION
    ].get_permission(constants.SPACESHIP_PERMISSION):
        return [
            "Find astronauts (astronaut commander + colonists) to fill this slot",
            "If astronauts and a spaceship share a location, the spaceship can be crewed",
        ]
    else:
        return [
            "Find a valid crew to fill this slot",
            "If an uncrewed vehicle and a valid crew share a location, the vehicle can be crewed",
        ]


def active_vehicle_reorganization_tooltip_factory(target_label: Any) -> List[str]:
    """
    Makes a tooltip for the crewed vehicle output slot in the vehicle reorganization interface
    """
    if target_label.actor:
        return target_label.actor.tooltip_text
    elif status.vehicle_reorganization_collection.autofill_actors[
        constants.CREW_VEHICLE_PERMISSION
    ]:
        if status.vehicle_reorganization_collection.autofill_actors[
            constants.CREW_VEHICLE_PERMISSION
        ].get_permission(
            constants.ASTRONAUTS_PERMISSION
        ):  # If astronaut crew
            return [
                "Find an uncrewed spaceship to fill this slot with a crewed spaceship",
                "If astronauts and an uncrewed spaceship share a location, the spaceship can be crewed",
            ]
        else:  # If non-astronaut crew
            return [
                "Find an uncrewed vehicle to fill this slot with a crewed vehicle",
                "If an uncrewed vehicle and a valid crew share a location, the vehicle can be crewed",
            ]
    else:  # If just a vehicle is available
        if status.vehicle_reorganization_collection.autofill_actors[
            constants.INACTIVE_VEHICLE_PERMISSION
        ].get_permission(
            constants.SPACESHIP_PERMISSION
        ):  # If spaceship vehicle
            return [
                "Find astronauts (astronaut commander + colonists) to fill this slot with a crewed spaceship",
                "If astronauts and an uncrewed spaceship share a location, the spaceship can be crewed",
            ]
        else:  # If non-spaceship vehicle
            return [
                "Find a valid crew to fill this slot with a crewed vehicle",
                "If an uncrewed vehicle and a valid crew share a location, the vehicle can be crewed",
            ]


def worker_reorganization_tooltip_factory(target_label: Any) -> List[str]:
    """
    Makes a tooltip for the worker input slot in the group reorganization interface
    """
    if target_label.actor:
        return target_label.actor.tooltip_text
    elif status.group_reorganization_collection.autofill_actors[
        constants.OFFICER_PERMISSION
    ]:
        officer_type = status.group_reorganization_collection.autofill_actors[
            constants.OFFICER_PERMISSION
        ].unit_type
        group_type = officer_type.group_type
        return [
            f"Find colonists to fill this slot",
            f"If colonists and {utility.generate_article(officer_type.name)} {officer_type.name} share a location, they can be merged into a {group_type.name}",
        ]
    else:
        return [
            "Find colonists to fill this slot",
            "If colonists and an officer share a location, they can be merged into a group",
        ]


def officer_reorganization_tooltip_factory(target_label: Any) -> List[str]:
    """
    Makes a tooltip for the officer input slot in the group reorganization interface
    """
    if target_label.actor:
        return target_label.actor.tooltip_text
    else:
        return [
            "Find colonists to fill this slot",
            "If a worker and colonists share a location, they can be merged into a group",
        ]


def group_reorganization_tooltip_factory(target_label: Any) -> List[str]:
    """
    Makes a tooltip for the group output slot in the group reorganization interface
    """
    if target_label.actor:
        return target_label.actor.tooltip_text
    elif status.group_reorganization_collection.autofill_actors[
        constants.OFFICER_PERMISSION
    ]:
        officer_type = status.group_reorganization_collection.autofill_actors[
            constants.OFFICER_PERMISSION
        ].unit_type
        group_type = officer_type.group_type
        return [
            f"Find colonists and {utility.generate_article(officer_type.name)} {officer_type.name} to fill this slot with a {group_type.name}",
            f"If colonists and {utility.generate_article(officer_type.name)} {officer_type.name} share a location, they can be merged into a {group_type.name}",
        ]

    else:
        return [
            "Find colonists and an officer to fill this slot with their combined group",
            "If colonists and an officer share a location, they can be merged into a group",
        ]
