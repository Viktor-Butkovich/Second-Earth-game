def print_terrains(global_manager):
    for current_terrain in global_manager.get("terrain_list"):
        print(current_terrain)


def get_terrain(terrain_dict, global_manager):
    """
    Takes terrain_dict as input with parametername: parametervalue for each parameter
    """
    for current_terrain in global_manager.get("terrain_list"):
        if current_terrain.in_bounds(terrain_dict):
            return current_terrain
    return "none"


def get_all_terrains(terrain_dict, global_manager):
    return_list = []
    for current_terrain in global_manager.get("terrain_list"):
        if current_terrain.in_bounds(terrain_dict):
            return_list.append(current_terrain)
    return return_list


def terrain_exists(terrain_dict):
    if get_terrain(terrain_dict) != "none":
        return True
    return False


def get_terrain_by_name(terrain_name, global_manager):
    for current_terrain in global_manager.get("terrain_list"):
        if current_terrain.name == terrain_name:
            return current_terrain
    return "none"


def remove_from_list(received_list, item_to_remove):
    """
    Description:
        Returns a version of the inputted list with all instances of the inputted item removed
    Input:
        any type list received list: list to remove items from
        any type item_to_remove: Item to remove from the list
    Output:
        any type list: Returns a version of the inputted list with all instances of the inputted item removed
    """
    output_list = []
    for item in received_list:
        if not item == item_to_remove:
            output_list.append(item)
    return output_list


def create_terrain(global_manager, parameter_dict={}):
    input_dict = {"init_type": "terrain"}
    counter = 1
    while get_terrain_by_name(f"default{counter}", global_manager) != "none":
        counter += 1
    input_dict["name"] = f"default{counter}"
    for current_parameter_type in global_manager.get("parameter_types"):
        if len(parameter_dict) == 0:
            input_dict["min_" + current_parameter_type] = 1
            input_dict["max_" + current_parameter_type] = 6
        else:  # can take point parameter_dict as input and set min and max values to the point values
            input_dict["min_" + current_parameter_type] = parameter_dict[
                current_parameter_type
            ]
            input_dict["max_" + current_parameter_type] = parameter_dict[
                current_parameter_type
            ]
    return global_manager.get("actor_creation_manager").create(
        input_dict, global_manager
    )


def create_point(global_manager, parameter_dict={}):
    input_dict = {"init_type": "point"}
    for current_parameter_type in global_manager.get("parameter_types"):
        if len(parameter_dict) == 0:
            input_dict[current_parameter_type] = 1
        else:  # can take point parameter_dict as input and set min and max values to the point values
            input_dict[current_parameter_type] = parameter_dict[current_parameter_type]
    return global_manager.get("actor_creation_manager").create(
        input_dict, global_manager
    )


def extract_arguments(input_str):
    """
    Takes a string with words separated by spaces and returns a list with each word as an item
    """
    return_value = []
    current_argument = ""
    for current_char in input_str:
        if current_char == " ":
            return_value.append(current_argument)
            current_argument = ""
        else:
            current_argument += current_char
    if current_argument != "" and current_argument != " ":
        return_value.append(current_argument)
    return return_value


def comma_list(input_list):
    """
    Takes a list of strings and returns a string of them separated by commmas
    """
    return_value = ""
    for i in range(0, len(input_list)):
        return_value += input_list[i]
        if i != len(input_list) - 1:
            return_value += ", "
    return return_value
