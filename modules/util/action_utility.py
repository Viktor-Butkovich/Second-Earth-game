# Contains miscellaneous functions relating to action functionality

from modules.util import scaling
from modules.constants import constants, status, flags


def generate_die_input_dict(
    coordinates, final_result, action, override_input_dict=None
):
    """
    Description:
        Creates and returns the input dict of a die created at the inputted coordinates with the inputted final result for the inputted action
    Input:
        int tuple coordinates: Two values representing x and y coordinates for the pixel location of the element
        int final_result: Predetermined final result of roll for die to end on
        action action: Action for which die is being rolled
    Output:
        dictionary: Returns the created input dict
    """
    result_outcome_dict = {
        "min_success": action.current_min_success,
        "min_crit_success": action.current_min_crit_success,
        "max_crit_fail": action.current_max_crit_fail,
    }
    outcome_color_dict = {
        "success": constants.COLOR_DARK_GREEN,
        "fail": constants.COLOR_DARK_RED,
        "crit_success": constants.COLOR_BRIGHT_GREEN,
        "crit_fail": constants.COLOR_BRIGHT_RED,
        "default": constants.COLOR_BLACK,
    }

    return_dict = {
        "coordinates": scaling.scale_coordinates(coordinates[0], coordinates[1]),
        "width": scaling.scale_width(100),
        "height": scaling.scale_height(100),
        "modes": [constants.current_game_mode],
        "num_sides": 6,
        "result_outcome_dict": result_outcome_dict,
        "outcome_color_dict": outcome_color_dict,
        "final_result": final_result,
        "init_type": constants.DIE_ELEMENT,
    }
    if override_input_dict:
        for value in override_input_dict:
            return_dict[value] = override_input_dict[value]
    return return_dict


def generate_action_ordered_collection_input_dict(
    coordinates, override_input_dict=None
):
    """
    Description:
        Creates and returns the input dict of an ordered collection created at the inputted coordinates with any extra overrides
    Input:
        int tuple coordinates: Two values representing x and y coordinates for the pixel location of the element
        dictionary override_input_dict=None: Optional dictionary to override attributes of created input_dict
    Output:
        dictionary: Returns the created input dict
    """
    return_dict = {
        "coordinates": coordinates,
        "width": scaling.scale_width(10),
        "height": scaling.scale_height(30),
        "modes": [constants.current_game_mode],
        "init_type": constants.ORDERED_COLLECTION,
        "initial_members": [],
        "reversed": True,
    }
    if override_input_dict:
        for value in override_input_dict:
            return_dict[value] = override_input_dict[value]
    return return_dict


def generate_free_image_input_dict(image_id, default_size, override_input_dict=None):
    """
    Description:
        Creates and returns the input dict of a free image with the inputted image id and inputted size
    Input:
        string/list/dict image_id: Image id of image to create
        default_size: Non-scaled width and height of image to create
        dictionary override_input_dict=None: Optional dictionary to override attributes of created input_dict
    Output:
        dictionary: Returns the created input dict
    """
    return_dict = {
        "image_id": image_id,
        "coordinates": (0, 0),
        "width": scaling.scale_width(default_size),
        "height": scaling.scale_height(default_size),
        "modes": [constants.current_game_mode],
        "to_front": True,
        "init_type": constants.FREE_IMAGE,
    }
    if override_input_dict:
        for value in override_input_dict:
            return_dict[value] = override_input_dict[value]
    return return_dict


def generate_background_image_id_list(actor=None) -> list:
    """
    Description:
        Creates and returns the image id list of a unit background image
    Input:
        None
    Output:
        list: Returns the created image id list
    """
    image_id_list = []
    if not actor:
        image_id_list.append(
            {
                "image_id": "misc/actor_backgrounds/mob_background.png",
                "level": constants.BACKGROUND_LEVEL,
            }
        )
    elif actor.actor_type == constants.MINISTER_ACTOR_TYPE:
        if not actor.current_position:
            image_id_list.append("misc/actor_backgrounds/mob_background.png")
        else:
            image_id_list.append(
                f"ministers/icons/{actor.current_position.skill_type}.png"
            )
        if actor.just_removed and not actor.current_position:
            image_id_list.append(
                {"image_id": "misc/warning_icon.png", "x_offset": 0.75}
            )
    elif actor.actor_type == constants.MOB_ACTOR_TYPE:
        if actor.get_permission(constants.SPACESHIP_PERMISSION):
            image_id_list.append(
                {
                    "image_id": "misc/actor_backgrounds/space_background.png",
                    "level": constants.BACKGROUND_LEVEL,
                }
            )
        else:
            image_id_list.append(
                {
                    "image_id": "misc/actor_backgrounds/mob_background.png",
                    "level": constants.BACKGROUND_LEVEL,
                }
            )
    elif actor.actor_type == constants.TILE_ACTOR_TYPE:
        pass
    return image_id_list


def generate_tile_image_id_list(cell, force_visibility=False):
    """
    Description:
        Creates and returns an image id list to display an image of the inputted cell's tile
    Input:
        cell cell: Cell to make a tile image for
        boolean force_visibility=False: Whether to ignore the tile's explored/unexplored status in the image created
    Output:
        string/dict list: Generated image id list
    """
    return (
        generate_background_image_id_list()
        + cell.tile.get_image_id_list(force_visibility=force_visibility)
        + ["misc/tile_outline.png"]
    )


def generate_risk_message(action, unit):
    """
    Description:
        Creates and returns the risk message for the inputted unit conducting the inputted action, based on veteran status and modifiers
    Input:
        action action: Action being conducted
        pmob unit: Unit conducting action
    Output:
        dictionary list: Returns the created input dicts
    """
    risk_value = (
        -1 * action.current_roll_modifier
    )  # modifier of -1 means risk value of 1
    if unit.get_permission(constants.VETERAN_PERMISSION):  # reduce risk if veteran
        risk_value -= 1

    if action.current_max_crit_fail <= 0:  # if action can never have risk
        message = ""
    elif risk_value < 0:  # 0/6 = no risk
        message = "RISK: LOW /n /n"
    elif risk_value == 0:  # 1/6 death = moderate risk
        message = "RISK: MODERATE /n /n"  # puts risk message at beginning
    elif risk_value == 1:  # 2/6 = high risk
        message = "RISK: HIGH /n /n"
    elif risk_value > 1:  # 3/6 or higher = extremely high risk
        message = "RISK: DEADLY /n /n"
    return message
