# Contains utility functions for setting up reorganization interface with correct dummy units for merge/split procedures

from typing import List
from copy import deepcopy
from modules.util import actor_utility
from modules.constants import constants, status, flags


required_dummy_attributes = [
    "name",
    "default_permissions",
    "override_permissions",
    "crew",
    "movement_points",
    "max_movement_points",
    "inventory_capacity",
    "inventory",
    "equipment",
    "subscribed_passengers",
    "sentry_mode",
    "base_automatic_route",
    "end_turn_destination",
    "officer",
    "worker",
    "character_info",
    "image_dict",
]


def generate_autofill_actors(
    allowed_procedures: List[str] = None,
    targets: List[str] = None,
    search_start_index=0,
) -> dict:
    """
    Description:
        Based on the currently displayed mob and the other mobs in its location, determine a possible merge/split procedure and find/create dummy versions of the other mobs
            involved
    Input:
        None
    Output:
        dict: Generates and returns dictionary with 'worker', 'officer', 'group', and 'procedure' entries corresponding to None or a dummy/actual unit of that type that
        would be involved in the determined merge/split procedure
    """
    return_dict = {constants.AUTOFILL_PROCEDURE: None}
    if status.displayed_mob and status.displayed_mob.get_permission(
        constants.PMOB_PERMISSION
    ):
        dummy_input_dict = {}
        for target in targets:
            if status.displayed_mob.get_permission(target):
                if constants.MERGE_PROCEDURE in allowed_procedures and target in [
                    constants.WORKER_PERMISSION,
                    constants.OFFICER_PERMISSION,
                ]:
                    return_dict[target] = status.displayed_mob
                    if target == constants.WORKER_PERMISSION:
                        # If a worker selected, find an officer if present and make a dummy group
                        return_dict[constants.OFFICER_PERMISSION] = (
                            status.displayed_mob.location.get_unit_by_filter(
                                [constants.OFFICER_PERMISSION],
                                start_index=search_start_index,
                            )
                        )
                    elif target == constants.OFFICER_PERMISSION:
                        # If an officer selected, find a worker if present and make a dummy group
                        return_dict[constants.WORKER_PERMISSION] = (
                            status.displayed_mob.location.get_unit_by_filter(
                                [constants.WORKER_PERMISSION],
                                start_index=search_start_index,
                            )
                        )
                    if (
                        return_dict[constants.WORKER_PERMISSION]
                        and return_dict[constants.OFFICER_PERMISSION]
                    ):
                        # If officer and worker present
                        return_dict[constants.GROUP_PERMISSION] = simulate_merge(
                            return_dict[constants.OFFICER_PERMISSION],
                            return_dict[constants.WORKER_PERMISSION],
                            required_dummy_attributes,
                            dummy_input_dict,
                        )
                    return_dict[constants.AUTOFILL_PROCEDURE] = (
                        constants.MERGE_PROCEDURE
                    )

                elif (
                    constants.SPLIT_PROCEDURE in allowed_procedures
                    and target == constants.GROUP_PERMISSION
                ):
                    return_dict[target] = status.displayed_mob
                    # If a group selected, split into dummy officer and worker
                    (
                        return_dict[constants.OFFICER_PERMISSION],
                        return_dict[constants.WORKER_PERMISSION],
                    ) = simulate_split(
                        status.displayed_mob,
                        required_dummy_attributes,
                        dummy_input_dict,
                    )
                    return_dict[constants.AUTOFILL_PROCEDURE] = (
                        constants.SPLIT_PROCEDURE
                    )

                elif constants.CREW_PROCEDURE in allowed_procedures and target in [
                    constants.CREW_VEHICLE_PERMISSION,
                    constants.INACTIVE_VEHICLE_PERMISSION,
                ]:
                    return_dict[target] = status.displayed_mob
                    if target == constants.CREW_VEHICLE_PERMISSION:
                        # If a crew selected, find an uncrewed vehicle if present and make a dummy crewed vehicle
                        return_dict[constants.INACTIVE_VEHICLE_PERMISSION] = (
                            status.displayed_mob.location.get_unit_by_filter(
                                [constants.INACTIVE_VEHICLE_PERMISSION],
                                start_index=search_start_index,
                            )
                        )
                    elif target == constants.INACTIVE_VEHICLE_PERMISSION:
                        # If a vehicle selected, find a crew if present and make a dummy crewed vehicle
                        return_dict[constants.CREW_VEHICLE_PERMISSION] = (
                            status.displayed_mob.location.get_unit_by_filter(
                                [constants.CREW_VEHICLE_PERMISSION],
                                start_index=search_start_index,
                            )
                        )
                    if (
                        return_dict[constants.CREW_VEHICLE_PERMISSION]
                        and return_dict[constants.INACTIVE_VEHICLE_PERMISSION]
                    ):
                        # If a crew and uncrewed vehicle present
                        return_dict[constants.ACTIVE_VEHICLE_PERMISSION] = (
                            simulate_crew(
                                return_dict[constants.INACTIVE_VEHICLE_PERMISSION],
                                return_dict[constants.CREW_VEHICLE_PERMISSION],
                                required_dummy_attributes,
                                dummy_input_dict,
                            )
                        )
                    return_dict[constants.AUTOFILL_PROCEDURE] = constants.CREW_PROCEDURE

                elif (
                    constants.UNCREW_PROCEDURE in allowed_procedures
                    and target == constants.ACTIVE_VEHICLE_PERMISSION
                ):
                    return_dict[target] = status.displayed_mob
                    # If a crewed vehicle selected, uncrew into dummy vehicle and worker
                    (
                        return_dict[constants.INACTIVE_VEHICLE_PERMISSION],
                        return_dict[constants.CREW_VEHICLE_PERMISSION],
                    ) = simulate_uncrew(
                        status.displayed_mob,
                        required_dummy_attributes,
                        dummy_input_dict,
                    )
                    return_dict[constants.AUTOFILL_PROCEDURE] = (
                        constants.UNCREW_PROCEDURE
                    )

            if return_dict[
                constants.AUTOFILL_PROCEDURE
            ]:  # If procedure chosen, no need to check for others
                break
            else:
                return_dict = {constants.AUTOFILL_PROCEDURE: None}
    return return_dict


def create_dummy_copy(
    unit, dummy_input_dict, required_dummy_attributes, override_permissions={}
):
    """
    Description:
        Creates a dummy object with the same attributes (shallow copied) as the inputted unit
    Input:
        mob unit: Mob being copied
        string list required_dummy_attributes: List of attributes required for dummies to have working tooltips/images to copy over from unit
        dictionary dummy_input_dict: Input dict for mock units with initial values - any values also contained in required attributes will be overridden by the unit
            values
        dictionary override_permissions = {}: Overridden values for copy - any permissions contained will be prioritize of unit's defaults
    Output:
        dummy: Returns dummy object copied from inputted unit
    """
    dummy_input_dict["unit_type"] = unit.unit_type
    for attribute in required_dummy_attributes:
        if hasattr(unit, attribute):
            if type(getattr(unit, attribute)) in [list, dict]:
                dummy_input_dict[attribute] = getattr(unit, attribute).copy()
            else:
                dummy_input_dict[attribute] = getattr(unit, attribute)
    dummy_input_dict["override_permissions"].update(override_permissions)
    return constants.actor_creation_manager.create_dummy(dummy_input_dict)


def simulate_merge(officer, worker, required_dummy_attributes, dummy_input_dict):
    """
    Description:
        Generates the mock output for the merge procedure based on the inputted information
    Input:
        officer officer: Officer being merged - used to base mock output unit off of
        worker worker: Worker being merged - used to base mock output unit off of
        string list required_dummy_attributes: List of attributes required for dummies to have working tooltips/images to copy over from unit
        dictionary dummy_input_dict: Input dict for mock units with initial values - any values also contained in required attributes will be overridden by the unit
            values
    Output:
        dummy: Returns dummy object representing group that would be created from merging inputted officer and worker
    """
    if officer and worker:
        for attribute in required_dummy_attributes:
            if hasattr(officer, attribute):
                if type(getattr(officer, attribute)) in [list, dict]:
                    dummy_input_dict[attribute] = getattr(officer, attribute).copy()
                else:
                    dummy_input_dict[attribute] = getattr(officer, attribute)

        dummy_officer = create_dummy_copy(officer, {}, required_dummy_attributes)
        dummy_input_dict["officer"] = dummy_officer
        dummy_worker = create_dummy_copy(worker, {}, required_dummy_attributes)
        dummy_input_dict["worker"] = dummy_worker
        dummy_input_dict["unit_type"] = officer.unit_type.group_type

        dummy_input_dict["equipment"] = {}
        dummy_officer.image_dict = deepcopy(officer.image_dict)
        dummy_worker.image_dict = deepcopy(worker.image_dict)
        for (
            equipment_type,
            equipped,
        ) in (
            dummy_worker.equipment.items()
        ):  # Attempt to share worker equipment with officer
            if equipped:
                if status.equipment_types[equipment_type].check_requirement(
                    dummy_officer
                ) and not dummy_officer.equipment.get(equipment_type, False):
                    status.equipment_types[equipment_type].equip(dummy_officer)

        for (
            equipment_type,
            equipped,
        ) in (
            dummy_officer.equipment.items()
        ):  # Attempt to share officer equipment with worker
            if equipped:
                if status.equipment_types[equipment_type].check_requirement(
                    dummy_worker
                ) and not dummy_worker.equipment.get(equipment_type, False):
                    status.equipment_types[equipment_type].equip(dummy_worker)

        dummy_input_dict[constants.DISORGANIZED_PERMISSION] = worker.get_permission(
            constants.DISORGANIZED_PERMISSION
        )
        dummy_input_dict[constants.DEHYDRATION_PERMISSION] = worker.get_permission(
            constants.DEHYDRATION_PERMISSION
        ) or officer.get_permission(constants.DEHYDRATION_PERMISSION)
        dummy_input_dict[constants.STARVATION_PERMISSION] = worker.get_permission(
            constants.STARVATION_PERMISSION
        ) or officer.get_permission(constants.STARVATION_PERMISSION)
        dummy_input_dict[constants.VETERAN_PERMISSION] = officer.get_permission(
            constants.VETERAN_PERMISSION
        )
        if dummy_input_dict["unit_type"].key == constants.BATTALION:
            dummy_input_dict[constants.DISORGANIZED_PERMISSION] = True
        dummy_input_dict["name"] = actor_utility.generate_group_name(
            worker, officer, add_veteran=True
        )
        dummy_input_dict["movement_points"] = (
            actor_utility.generate_group_movement_points(worker, officer)
        )
        dummy_input_dict["max_movement_points"] = (
            actor_utility.generate_group_movement_points(
                worker, officer, generate_max=True
            )
        )
        dummy_input_dict["default_permissions"].update(
            {
                constants.OFFICER_PERMISSION: False,
                constants.GROUP_PERMISSION: True,
                constants.DISORGANIZED_PERMISSION: dummy_input_dict[
                    constants.DISORGANIZED_PERMISSION
                ],
                constants.DEHYDRATION_PERMISSION: dummy_input_dict[
                    constants.DEHYDRATION_PERMISSION
                ],
                constants.STARVATION_PERMISSION: dummy_input_dict[
                    constants.STARVATION_PERMISSION
                ],
                constants.VETERAN_PERMISSION: dummy_input_dict[
                    constants.VETERAN_PERMISSION
                ],
            }
        )
        dummy_group = constants.actor_creation_manager.create_dummy(dummy_input_dict)
        for (
            equipment_type,
            equipped,
        ) in (
            worker.equipment.items()
        ):  # Equip any equipment of the worker that the group can use
            if equipped and status.equipment_types[equipment_type].check_requirement(
                dummy_group
            ):
                status.equipment_types[equipment_type].equip(dummy_group)
        for (
            equipment_type,
            equipped,
        ) in (
            officer.equipment.items()
        ):  # Equip any equipment of the officer that the group can use
            if (
                equipped
                and status.equipment_types[equipment_type].check_requirement(
                    dummy_group
                )
                and not dummy_group.equipment.get(equipment_type, False)
            ):
                status.equipment_types[equipment_type].equip(dummy_group)
    dummy_group.set_permission(
        constants.SURVIVABLE_PERMISSION,
        officer.location.get_unit_habitability(dummy_group),
    )
    return dummy_group


def simulate_crew(vehicle, worker, required_dummy_attributes, dummy_input_dict):
    """
    Description:
        Generates the mock output for the crew procedure based on the inputted information
    Input:
        vehicle vehicle: Vehicle being crewed - used to base mock output unit off of
        worker worker: New crew - used to base mock output unit off of
        string list required_dummy_attributes: List of attributes required for dummies to have working tooltips/images to copy over from unit
        dictionary dummy_input_dict: Input dict for mock units with initial values - any values also contained in required attributes will be overridden by the unit
            values
    Output:
        dummy: Returns dummy object representing inputted vehicle once crewed by inputted worker
    """
    dummy_vehicle = create_dummy_copy(
        vehicle,
        dummy_input_dict,
        required_dummy_attributes,
        override_permissions={
            constants.ACTIVE_VEHICLE_PERMISSION: True,
            constants.ACTIVE_PERMISSION: True,
        },
    )
    dummy_vehicle.crew = worker
    return dummy_vehicle


def simulate_split(unit, required_dummy_attributes, dummy_input_dict):
    """
    Description:
        Generates the mock output for the split procedure based on the inputted information
    Input:
        group unit: Group being split - component officer and worker used to base mock output units off of
        string list required_dummy_attributes: List of attributes required for dummies to have working tooltips/images to copy over from unit
        dictionary dummy_input_dict: Input dict for mock units with initial values - any values also contained in required attributes will be overridden by the unit
            values
    Output:
        dummy, dummy tuple: Returns tuple of dummy objects representing output officer and worker resulting from split
    """
    dummy_worker_dict = dummy_input_dict
    unit.worker.set_permission(
        constants.DISORGANIZED_PERMISSION,
        unit.get_permission(constants.DISORGANIZED_PERMISSION),
    )
    dummy_officer_dict = dummy_input_dict.copy()
    dummy_worker = create_dummy_copy(
        unit.worker, dummy_worker_dict, required_dummy_attributes
    )
    dummy_officer = create_dummy_copy(
        unit.officer, dummy_officer_dict, required_dummy_attributes
    )

    for (
        equipment_type,
        equipped,
    ) in unit.equipment.items():  # Attempt to inherit equipment
        if equipped:
            if status.equipment_types[equipment_type].check_requirement(dummy_worker):
                status.equipment_types[equipment_type].equip(dummy_worker)
                status.equipment_types[equipment_type].unequip(dummy_officer)
            elif status.equipment_types[equipment_type].check_requirement(
                dummy_officer
            ):
                status.equipment_types[equipment_type].equip(dummy_officer)
                status.equipment_types[equipment_type].unequip(dummy_worker)
    dummy_officer.set_permission(
        constants.SURVIVABLE_PERMISSION,
        unit.location.get_unit_habitability(dummy_officer),
    )
    dummy_worker.set_permission(
        constants.SURVIVABLE_PERMISSION,
        unit.location.get_unit_habitability(dummy_worker),
    )
    return (dummy_officer, dummy_worker)


def simulate_uncrew(unit, required_dummy_attributes, dummy_input_dict):
    """
    Description:
        Generates the mock output for the uncrew procedure based on the inputted information
    Input:
        vehicle unit: Vehicle being uncrewed - vehicle and crew worker used to base mock output units off of
        string list required_dummy_attributes: List of attributes required for dummies to have working tooltips/images to copy over from unit
        dictionary dummy_input_dict: Input dict for mock units with initial values - any values also contained in required attributes will be overridden by the unit
            values
    Output:
        dummy, dummy tuple: Returns tuple of dummy objects representing output vehicle and worker resulting from split
    """
    dummy_worker = create_dummy_copy(
        unit.crew,
        dummy_input_dict.copy(),
        required_dummy_attributes,
        override_permissions={
            constants.IN_VEHICLE_PERMISSION: False,
        },
    )
    dummy_worker.set_permission(
        constants.SURVIVABLE_PERMISSION,
        unit.location.get_unit_habitability(dummy_worker),
    )
    dummy_vehicle = create_dummy_copy(
        unit,
        dummy_input_dict,
        required_dummy_attributes,
        override_permissions={
            constants.ACTIVE_PERMISSION: False,
            constants.ACTIVE_VEHICLE_PERMISSION: False,
        },
    )
    return (dummy_vehicle, dummy_worker)
