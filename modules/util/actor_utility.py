# Contains miscellaneous functions relating to actor functionality

import random
import os
import pygame
import math
from typing import List, Tuple
from . import utility, text_utility
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags


def reset_action_prices():
    """
    Description:
        Resets the costs of any actions that were increased during the previous turn
    Input:
        None
    Output:
        None
    """
    for current_action_type in constants.action_types:
        constants.action_prices[current_action_type] = constants.base_action_prices[
            current_action_type
        ]


def double_action_price(action_type):
    """
    Description:
        Doubles the price of a certain action type each time it is done, usually for ones that do not require workers
    Input:
        string action_type: Type of action to double the price of
    Output:
        None
    """
    constants.action_prices[action_type] *= 2


def get_building_cost(constructor, building_type, building_name="n/a"):
    """
    Description:
        Returns the cost of the inputted unit attempting to construct the inputted building
    Input:
        pmob/string constructor: Unit attempting to construct the building, or None if no location/unit type is needed
        string building_type: Type of building to build, like 'infrastructure'
        string building_name = 'n/a': Name of building being built, used to differentiate roads from railroads
    Output:
        int: Returns the cost of the inputted unit attempting to construct the inputted building
    """
    if building_type == constants.INFRASTRUCTURE:
        building_type = building_name.replace(
            " ", "_"
        )  # road, railroad, road_bridge, or railroad_bridge
    if building_type == constants.WAREHOUSES:
        if constructor:
            base_price = constructor.get_cell().get_warehouses_cost()
        else:
            base_price = 5
    else:
        base_price = constants.building_prices[building_type]

    if building_type in [constants.TRAIN]:
        cost_multiplier = 1
    elif (not constructor) or not status.strategic_map_grid in constructor.grids:
        cost_multiplier = 1
    else:
        cost_multiplier = constants.terrain_build_cost_multiplier_dict.get(
            constructor.get_cell().terrain_handler.terrain, 1
        )

    return base_price * cost_multiplier


def update_descriptions(target="all"):
    """
    Description:
        Updates the descriptions of recruitable units for use in various parts of the program. Updates all units during setup and can target a certain unit to update prices, etc. when the information is needed later in the game.
            Creates list versions for tooltips and string versions for notifications
    Input:
        string target = 'all': Targets a certain unit type, or 'all' by default, to update while minimizing unnecessary calculations
    Output:
        None
    """
    if target == "all":
        targets_to_update = constants.building_types + [
            constants.ROAD,
            constants.RAILROAD,
            constants.FERRY,
            constants.ROAD_BRIDGE,
            constants.RAILROAD_BRIDGE,
        ]
        targets_to_update += constants.upgrade_types
    else:
        targets_to_update = [target]

    for current_target in targets_to_update:
        list_descriptions = constants.list_descriptions
        string_descriptions = constants.string_descriptions
        text_list = []

        if current_target == constants.RESOURCE:
            if current_target in status.actions:
                building_name = status.actions[current_target].building_name
                if not building_name:
                    building_name = "resource production facility"
            else:
                building_name = "resource production facility"
            text_list.append(
                f"A {building_name} expands the tile's warehouse capacity, and each work crew attached to it attempts to produce resources each turn."
            )
            text_list.append(
                "Upgrades to the facility can increase the maximum number of attached work crews and the number of production attempts each work crew can make. "
            )

        elif current_target == constants.ROAD:
            text_list.append(
                "A road halves movement cost when moving to another tile that has a road or railroad and can later be upgraded to a railroad."
            )

        elif current_target == constants.RAILROAD:
            text_list.append(
                "A railroad, like a road, halves movement cost when moving to another tile that has a road or railroad."
            )
            text_list.append(
                "It is also required for trains to move and for a train station to be built."
            )

        elif current_target == constants.FERRY:
            text_list.append(
                "A ferry built on a water tile between 2 land tiles allows movement across the water."
            )
            text_list.append(
                "A ferry allows moving to the ferry tile for 2 movement points, and can later be upgraded to a road bridge."
            )

        elif current_target == constants.ROAD_BRIDGE:
            text_list.append(
                "A bridge built on a water tile between 2 land tiles allows movement across the water."
            )
            text_list.append(
                "A road bridge acts as a road between the tiles it connects and can later be upgraded to a railroad bridge."
            )

        elif current_target == constants.RAILROAD_BRIDGE:
            text_list.append(
                "A bridge built on a water tile between 2 land tiles allows movement across the water."
            )
            text_list.append(
                "A railroad bridge acts as a railroad between the tiles it connects."
            )

        elif current_target == constants.PORT:
            text_list.append(
                "A port allows steamships to enter the tile and expands the tile's warehouse capacity."
            )
            text_list.append("A port adjacent to the water allows entry by steamships.")

        elif current_target == constants.TRAIN_STATION:
            text_list.append(
                "A train station is required for a train to exchange cargo and passengers, expands the tile's warehouse capacity, and allows assembly of trains."
            )

        elif current_target == constants.FORT:
            text_list.append(
                "A fort increases the combat effectiveness of your units standing in this tile."
            )

        elif current_target == constants.RESOURCE_SCALE:
            text_list.append(
                "A resource production facility can have a number of attached work crews equal to its scale"
            )

        elif current_target == constants.RESOURCE_EFFICIENCY:
            text_list.append(
                "A resource production facility's attached work crews each make a number of production attempts per turn equal to its efficiency."
            )

        elif current_target == constants.WAREHOUSES_LEVEL:
            text_list.append(
                "Each of a tile's warehouse levels corresponds to 9 inventory capacity."
            )

        list_descriptions[current_target] = text_list

        text = " /n /n".join(list_descriptions[current_target])
        string_descriptions[current_target] = text


def create_image_dict(stem):
    """
    Description:
        Creates a dictionary of image file paths for an actor to store and set its image to in different situations
    Input:
        string stem: Path to an actor's image folder
    Output:
        string/string dictionary: String image description keys and string file path values, like 'left': 'explorer/left.png'
    """
    stem = "mobs/" + stem
    stem += "/"
    image_dict = {}
    image_dict["default"] = stem + "default.png"
    image_dict["right"] = stem + "right.png"
    image_dict["left"] = stem + "left.png"
    return image_dict


def update_roads():
    """
    Description:
        Updates the road/railroad connections between tiles when a new one is built
    Input:
        None
    Output:
        None
    """
    for current_building in status.building_list:
        if current_building.building_type == constants.INFRASTRUCTURE:
            current_building.cell.tile.update_image_bundle()


def get_random_ocean_coordinates():
    """
    Description:
        Returns a random set of coordinates from the ocean section of the strategic map
    Input:
        None
    Output:
        int tuple: Two values representing x and y coordinates
    """
    start_x = random.randrange(0, status.strategic_map_grid.coordinate_width)
    start_y = 0
    return (start_x, start_y)


def calibrate_actor_info_display(info_display, new_actor, override_exempt=False):
    """
    Description:
        Updates all relevant objects to display a certain mob or tile
    Input:
        interface_collection info_display: Collection of interface elements to calibrate to the inputted actor
        actor new_actor: The new mob or tile that is displayed
        boolean override_exempt=False: Whether to calibrate interface elements that are normally exempt, such as the reorganization interface
    Output:
        None
    """
    if info_display == status.tile_info_display:
        for current_same_tile_icon in status.same_tile_icon_list:
            current_same_tile_icon.reset()
        if new_actor != status.displayed_tile:
            calibrate_actor_info_display(status.tile_inventory_info_display, None)
        status.displayed_tile = new_actor
        if new_actor:
            new_actor.select()  # plays correct music based on tile selected - main menu/earth music
        if (
            not flags.choosing_destination
        ):  # Don't change tabs while choosing destination
            select_default_tab(status.tile_tabbed_collection, status.displayed_tile)

    elif info_display == status.mob_info_display:
        if new_actor != status.displayed_mob:
            calibrate_actor_info_display(status.mob_inventory_info_display, None)
        status.displayed_mob = new_actor
        if new_actor and new_actor.get_cell().tile == status.displayed_tile:
            for current_same_tile_icon in status.same_tile_icon_list:
                current_same_tile_icon.reset()
        if (
            not flags.choosing_destination
        ):  # Don't change tabs while choosing destination
            select_default_tab(status.mob_tabbed_collection, status.displayed_mob)

    target = None
    if new_actor:
        target = new_actor
    info_display.calibrate(target, override_exempt)


def select_default_tab(tabbed_collection, displayed_actor) -> None:
    """
    Description:
        Selects the default tab for the inputted tabbed collection based on the inputted displayed actor
    Input:
        interface_collection tabbed_collection: Tabbed collection to select tab of
        actor displayed_actor: Mob or tile to select tab for
    Output:
        None
    """
    target_tab = None
    if displayed_actor:
        if tabbed_collection == status.tile_tabbed_collection:
            if status.displayed_tile.inventory:
                target_tab = status.tile_inventory_collection
            elif status.displayed_tile.cell.settlement:
                target_tab = status.settlement_collection
            else:
                target_tab = status.terrain_collection
        elif tabbed_collection == status.mob_tabbed_collection:
            if status.displayed_mob.get_permission(constants.PMOB_PERMISSION):
                if status.displayed_mob.inventory or status.displayed_mob.equipment:
                    target_tab = status.mob_inventory_collection
                else:
                    target_tab = status.mob_reorganization_collection
    if target_tab:
        select_interface_tab(tabbed_collection, target_tab)


def generate_resource_icon(tile):
    """
    Description:
        Generates and returns the correct string image file path based on the resource and buildings built in the inputted tile
    Input:
        tile tile: Tile to generate a resource icon for
    Output:
        string/list: Returns string or list image id for tile's resource icon
    """
    image_id = [
        {"image_id": "misc/green_circle.png", "size": 0.75},
        {
            "image_id": "items/" + tile.cell.terrain_handler.resource + ".png",
            "size": 0.75,
        },
    ]

    if bool(tile.cell.get_buildings()):  # Make small icon if tile has any buildings
        for (
            current_image
        ) in (
            image_id
        ):  # To make small icon, make each component of image smaller and shift to bottom left corner
            current_image.update({"x_offset": -0.33, "y_offset": -0.33})
            current_image["size"] = current_image.get("size", 1.0) * 0.45
    return image_id


def get_image_variants(base_path, keyword="default"):
    """
    Description:
        Finds and returns a list of all images with the same name format in the same folder, like 'folder/default.png' and 'folder/default1.png'
    Input:
        string base_path: File path of base image, like 'folder/default.png'
        string keyword = 'default': Name format to look for
    Output:
        string list: Returns list of all images with the same name format in the same folder
    """
    variants = []
    if base_path.endswith("default.png"):
        folder_path = base_path.removesuffix("default.png")
        for file_name in os.listdir("graphics/" + folder_path):
            if file_name.startswith(keyword):
                variants.append(folder_path + file_name)
                continue
            else:
                continue
    else:
        variants.append(base_path)
    return variants


def extract_folder_colors(folder_path: str) -> List[Tuple[int, int, int]]:
    """
    Description:
        Iterates through a folder's files and finds the first color in each image, returning that color's RGB values
    Input:
        string folder_path: Folder path to search through, like 'ministers/portraits/hair/colors'
    Output:
        int tuple list: Returns list of (red, green, blue) items, with red, green, and blue being the RGB values of the first color in each respective file
    """
    colors = []
    for file_name in os.listdir("graphics/" + folder_path):
        current_image = pygame.image.load("graphics/" + folder_path + file_name)
        red, green, blue, alpha = current_image.get_at((0, 0))
        colors.append((red, green, blue))
    return colors


def generate_unit_component_image_id(
    base_image, component: str, to_front: bool = False
):
    """
    Description:
        Generates and returns an image id dict for the inputted base_image moved to the inputted section of the frame, like 'group left' for a group's left worker
    Input:
        string base_image: Base image file path to display
        string component: Section of the frame to display base image in, like 'group left'
        boolean to_front=False: Whether image level/layer should be a positive or negative
    Output:
        dict: Returns generated image id dict
    """
    return_dict = {}
    if component in ["group left", "group right"]:
        return_dict = {
            "image_id": base_image,
            "size": 0.8,
            "x_offset": -0.28,
            "y_offset": 0.05,
            "level": -2,
        }
    elif component in ["left", "right"]:
        return_dict = {
            "image_id": base_image,
            "size": 0.85,
            "x_offset": -0.25,
            "y_offset": 0,
            "level": -1,
        }
    elif component == "center":
        return_dict = {
            "image_id": base_image,
            "size": 0.85,
            "x_offset": 0,
            "y_offset": -0.05,
            "level": -1,
        }
    if component.endswith("right"):
        return_dict["x_offset"] *= -1
    if to_front:
        return_dict["level"] *= -1
    return return_dict


def generate_unit_component_portrait(
    base_image, component: str, to_front: bool = False
):
    """
    Description:
        Generates and returns an image id dict for the inputted base_image moved to the inputted section of the frame, like 'center portrait' for a group's officer's portrait
            As portraits are image id lists, they are handled differently than normal unit component images
    Input:
        image_id list base_image: Image id list of portrait to display
        string component: Section of the frame to display base image in, like 'group left'
        boolean to_front=False: Whether image level/layer should be a positive or negative
    Output:
        list: Returns generated image id list
    """
    return_list = []
    for section in base_image:
        edited_section = {
            "image_id": section["image_id"],
            "x_size": 0.85 * section.get("size", 1.0) * section.get("x_size", 1.0),
            "y_size": 0.85 * section.get("size", 1.0) * section.get("y_size", 1.0),
            "x_offset": section.get("x_offset", 0) - 0.01,
            "y_offset": section.get("y_offset", 0) - 0.1,
            "level": section.get("level", 0) - 1,
            "green_screen": section.get("green_screen", []),
            "metadata": section.get("metadata", {}),
        }
        if component.endswith("left"):
            edited_section["x_offset"] -= 0.245
            edited_section["y_offset"] += 0.043
            if component == "group left":
                edited_section["x_offset"] -= 0.025
                edited_section["y_offset"] += 0.043
                edited_section["x_size"] *= 0.94
                edited_section["y_size"] *= 0.94
            if section["metadata"]["portrait_section"] == "full_body":
                edited_section["x_offset"] += 0.008
                edited_section["y_offset"] += 0.055
        elif component.endswith("right"):
            edited_section["x_offset"] += 0.245
            edited_section["y_offset"] += 0.043
            if component == "group right":
                edited_section["x_offset"] += 0.035
                edited_section["y_offset"] += 0.043
                edited_section["x_size"] *= 0.94
                edited_section["y_size"] *= 0.94
            if section["metadata"]["portrait_section"] == "full_body":
                edited_section["x_offset"] += 0.018
                edited_section["y_offset"] += 0.055
        elif section["metadata"]["portrait_section"] == "full_body":
            edited_section["x_offset"] += 0.015
            edited_section["y_offset"] += 0.05
        return_list.append(edited_section)

    return return_list


def generate_group_image_id_list(worker, officer):
    """
    Description:
        Generates and returns an image id list that a group formed from the inputted worker and officer would have
    Input:
        worker worker: Worker to use for group image
        officer officer: Officer to use for group image
    Output:
        list: Returns image id list of dictionaries for each part of the group image
    """
    return (
        generate_unit_component_portrait(
            worker.image_dict["left portrait"], "group left"
        )
        + generate_unit_component_portrait(
            worker.image_dict["right portrait"], "group right"
        )
        + generate_unit_component_portrait(officer.image_dict["portrait"], "center")
    )


def generate_group_name(worker, officer, add_veteran=False):
    """
    Description:
        Generates and returns the name that a group formed from the inputted worker and officer would have
    Input:
        worker worker: Worker to use for group name
        officer officer: Officer to use for group name
        boolean add_veteran=False: Whether veteran should be added to the start of the name if the officer is a veteran - while a mock group needs veteran to be added, a
            group actually being created will add veteran to its name automatically when it promotes
    Output:
        list: Returns image id list of dictionaries for each part of the group image
    """
    if not officer.get_permission(constants.MAJOR_PERMISSION):
        name = ""
        for character in officer.unit_type.group_type.name:
            if not character == "_":
                name += character
            else:
                name += " "
    else:  # battalions have special naming convention based on worker type
        if worker.get_permission(constants.EUROPEAN_WORKERS_PERMISSION):
            name = "imperial battalion"
        else:
            name = "colonial battalion"
    if add_veteran and officer.get_permission(constants.VETERAN_PERMISSION):
        name = "veteran " + name
    return name


def generate_group_movement_points(worker, officer, generate_max=False):
    """
    Description:
        Generates and returns either the current or maximum movement points that a group created from the inputted worker and officer would have
    Input:
        worker worker: Worker to use for group
        officer officer: Officer to use for group
        boolean generate_max=False: Whether to return the group's current or maximum number of movement points
    Output:
        list: Returns image id list of dictionaries for each part of the group image
    """
    if generate_max:
        max_movement_points = officer.max_movement_points
        if officer.all_permissions(
            constants.DRIVER_PERMISSION, constants.VETERAN_PERMISSION
        ):
            max_movement_points = 6
        return max_movement_points
    else:
        max_movement_points = generate_group_movement_points(
            worker, officer, generate_max=True
        )
        worker_movement_ratio_remaining = (
            worker.movement_points / worker.max_movement_points
        )
        officer_movement_ratio_remaining = (
            officer.movement_points / officer.max_movement_points
        )
        if worker_movement_ratio_remaining > officer_movement_ratio_remaining:
            return math.floor(max_movement_points * officer_movement_ratio_remaining)
        else:
            return math.floor(max_movement_points * worker_movement_ratio_remaining)


def select_interface_tab(tabbed_collection, target_tab):
    """
    Description:
        Selects the inputted interface tab from the inputted tabbed collection, such as selecting the inventory tab from the mob tabbed collection
    Input:
        interface_collection tabbed_collection: Tabbed collection to select from
        interface_collection target_tab: Tab to select
    Output:
        None
    """
    if not target_tab.showing:
        for tab_button in tabbed_collection.tabs_collection.members:
            if tab_button.linked_element == target_tab:
                tab_button.on_click()
                continue


def generate_label_image_id(text: str, y_offset=0):
    """
    Description:
        Generates and returns an image ID list for a label containing the inputted text at the inputted y offset
            Used for "labels" that are part of images, not independent label objects
    Input:
        str text: Text for label to contain
        float y_offset: -1.0 through 0.0, determines how far down image to offset the label, with 0 being at the top of the image
    """
    x_size = min(
        0.96, 0.10 * len(text)
    )  # Try to use a particular font size, decreasing if surpassing the maximum of 93% of the image width
    if x_size < 0.93:
        x_offset = 0.5 - (x_size / 2)
    else:
        x_offset = 0.02
    y_size = (
        x_size / len(text)
    ) * 2.3  # Decrease vertical font size proportionally if x_size was bounded by maximum
    return [
        {
            "image_id": "misc/paper_label.png",
            "x_offset": x_offset - 0.01,
            "y_offset": y_offset,
            "free": True,
            "level": constants.LABEL_LEVEL,
            "x_size": x_size + 0.02,
            "y_size": y_size,
        },
        text_utility.prepare_render(
            text,
            font=constants.fonts["max_detail_black"],
            override_input_dict={
                "x_offset": x_offset,
                "y_offset": y_offset,
                "free": True,
                "level": constants.LABEL_LEVEL,
                "override_height": None,
                "override_width": None,
                "x_size": x_size,
                "y_size": y_size,
            },
        ),
    ]


def callback(target, function, *args):
    """
    Description:
        Orders the inputted target to call the inputted function with the inputted arguments
    Input:
        str target: Status object to call function of
        str function: Name of function to call
        *args: Any number of arguments to pass to function call
    """
    getattr(getattr(status, target), function)(*args)


def generate_frame(
    image_id: any,
    frame: str = "buttons/default_button.png",
    size: float = 0.75,
    y_offset: float = -0.02,
    x_offset: float = 0.02,
):
    """
    Description:
        Generates and returns a version of the inputted image ID with a frame added
    Input:
        image_id image_id: Image ID for button, either in string, dict, or list format
        str frame: Frame to place button in, using "buttons/default_button.png" as default
    Output:
        None
    """
    frame = {
        "image_id": frame,
        "level": constants.BACKGROUND_LEVEL,
    }

    if type(image_id) == str:
        return utility.combine(
            frame,
            {
                "image_id": image_id,
                "x_size": size,
                "y_size": size,
                "x_offset": x_offset,
                "y_offset": y_offset,
                "level": constants.BACKGROUND_LEVEL + 1,
            },
        )

    elif type(image_id) == list:
        for image in image_id:
            image["x_size"] = image.get("x_size", 1) * size
            image["y_size"] = image.get("y_size", 1) * size
            image["x_offset"] = image.get("x_offset", 0) + x_offset
            image["y_offset"] = image.get("y_offset", 0) + y_offset
        return utility.combine(frame, image_id)
