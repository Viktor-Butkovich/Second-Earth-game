# Contains utility functions for setting up reorganization interface with correct dummy units for merge/split procedures

from . import actor_utility
import modules.constants.constants as constants
import modules.constants.status as status


def generate_autofill_actors(search_start_index=0):
    """
    Description:
        Based on the currently displayed mob and the other mobs in its tile, determine a possible merge/split procedure and find/create dummy versions of the other mobs
            involved
    Input:
        None
    Output:
        dict: Generates and returns dictionary with 'worker', 'officer', 'group', and 'procedure' entries corresponding to 'none' or a dummy/actual unit of that type that
        would be involved in the determined merge/split procedure
    """
    return_dict = {
        "worker": "none",
        "officer": "none",
        "group": "none",
        "procedure": "none",
    }
    displayed_mob = status.displayed_mob
    if displayed_mob and displayed_mob.is_pmob:

        required_dummy_attributes = [
            "name",
            "is_group",
            "default_permissions",
            "override_permissions",
            "is_pmob",
            "is_npmob",
            "has_infinite_movement",
            "crew",
            "movement_points",
            "max_movement_points",
            "inventory_capacity",
            "inventory",
            "equipment",
            "contained_mobs",
            "temp_movement_disabled",
            "disorganized",
            "veteran",
            "sentry_mode",
            "base_automatic_route",
            "end_turn_destination",
            "officer",
            "worker",
            "group_type",
            "battalion_type",
        ]

        dummy_input_dict = {
            "actor_type": "mob",
            "in_vehicle": False,
            "in_group": False,
            "in_building": False,
            "images": [
                constants.actor_creation_manager.create_dummy({"image_id": None})
            ],
        }

        if displayed_mob.any_permissions(
            constants.WORKER_PERMISSION,
            constants.OFFICER_PERMISSION,
            constants.INACTIVE_VEHICLE_PERMISSION,
        ):
            if displayed_mob.get_permission(constants.WORKER_PERMISSION):
                return_dict["worker"] = displayed_mob
                return_dict["officer"] = displayed_mob.images[
                    0
                ].current_cell.get_officer(start_index=search_start_index)
            else:
                return_dict["officer"] = displayed_mob
                return_dict["worker"] = displayed_mob.get_cell().get_worker(
                    start_index=search_start_index
                )

            if return_dict["worker"] != "none" and return_dict["officer"] != "none":
                if return_dict["officer"].get_permission(constants.OFFICER_PERMISSION):
                    return_dict["group"] = simulate_merge(
                        return_dict["officer"],
                        return_dict["worker"],
                        required_dummy_attributes,
                        dummy_input_dict,
                    )
                    return_dict["procedure"] = "merge"
                elif return_dict["officer"].get_permission(
                    constants.VEHICLE_PERMISSION
                ):
                    return_dict["group"] = simulate_crew(
                        return_dict["officer"],
                        return_dict["worker"],
                        required_dummy_attributes,
                        dummy_input_dict,
                    )
                    return_dict["procedure"] = "crew"

        elif displayed_mob.is_group or displayed_mob.all_permissions(
            constants.VEHICLE_PERMISSION, constants.ACTIVE_PERMISSION
        ):
            return_dict["group"] = displayed_mob

            if return_dict["group"].is_group:
                return_dict["officer"], return_dict["worker"] = simulate_split(
                    return_dict["group"], required_dummy_attributes, dummy_input_dict
                )
                return_dict["procedure"] = "split"
            elif return_dict["group"].get_permission(constants.VEHICLE_PERMISSION):
                return_dict["officer"], return_dict["worker"] = simulate_uncrew(
                    return_dict["group"], required_dummy_attributes, dummy_input_dict
                )
                return_dict["procedure"] = "uncrew"

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
    dummy_input_dict["image_id_list"] = unit.get_image_id_list(
        override_values={"override_permissions": override_permissions}
    )
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
    return_value = "none"
    if officer != "none" and worker != "none":
        for attribute in required_dummy_attributes:
            if hasattr(officer, attribute):
                if type(getattr(officer, attribute)) in [list, dict]:
                    dummy_input_dict[attribute] = getattr(officer, attribute).copy()
                else:
                    dummy_input_dict[attribute] = getattr(officer, attribute)
        dummy_input_dict["officer"] = officer
        dummy_input_dict["worker"] = worker
        dummy_input_dict["group_type"] = constants.officer_group_type_dict[
            officer.officer_type
        ]
        dummy_input_dict["disorganized"] = worker.disorganized
        dummy_input_dict["veteran"] = officer.veteran
        if dummy_input_dict["group_type"] == "battalion":
            dummy_input_dict["disorganized"] = True
            if worker.worker_type == "European":
                dummy_input_dict["battalion_type"] = "imperial"
            else:
                dummy_input_dict["battalion_type"] = "colonial"
        dummy_input_dict["name"] = actor_utility.generate_group_name(
            worker, officer, add_veteran=True
        )
        dummy_input_dict[
            "movement_points"
        ] = actor_utility.generate_group_movement_points(worker, officer)
        dummy_input_dict[
            "max_movement_points"
        ] = actor_utility.generate_group_movement_points(
            worker, officer, generate_max=True
        )
        dummy_input_dict["default_permissions"].update(
            {
                constants.OFFICER_PERMISSION: False,
            }
        )
        dummy_input_dict["is_group"] = True
        image_id_list = []
        dummy_input_dict[
            "image_id_list"
        ] = image_id_list + actor_utility.generate_group_image_id_list(worker, officer)
        if dummy_input_dict.get("disorganized", False):
            dummy_input_dict["image_id_list"].append("misc/disorganized_icon.png")
        if dummy_input_dict.get("veteran", False):
            dummy_input_dict["image_id_list"].append("misc/veteran_icon.png")

        return_value = constants.actor_creation_manager.create_dummy(dummy_input_dict)
    return return_value


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
    unit.worker.disorganized = unit.disorganized
    dummy_officer_dict = dummy_input_dict.copy()
    dummy_worker = create_dummy_copy(
        unit.worker, dummy_worker_dict, required_dummy_attributes
    )
    dummy_officer = create_dummy_copy(
        unit.officer, dummy_officer_dict, required_dummy_attributes
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
        unit.crew, dummy_input_dict.copy(), required_dummy_attributes
    )
    dummy_vehicle = create_dummy_copy(
        unit,
        dummy_input_dict,
        required_dummy_attributes,
        override_permissions={constants.ACTIVE_PERMISSION: False},
    )
    return (dummy_vehicle, dummy_worker)
