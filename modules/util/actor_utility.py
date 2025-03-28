# Contains miscellaneous functions relating to actor functionality

import random
import os
import pygame
import math
from typing import List, Tuple, Dict
from modules.util import utility, text_utility
from modules.constants import constants, status, flags


def press_button(button_type: str) -> None:
    """
    Description:
        Presses the first button of the inputted type
    Input:
        string button_type: Type of button to press
    Output:
        None
    """
    for current_button in status.button_list:
        if current_button.button_type == button_type:
            current_button.on_click(override_action_possible=True)
            break


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
        string building_type: Key of type of building to build, like 'infrastructure'
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
        base_price = status.building_types[building_type].cost

    if building_type in [constants.TRAIN]:
        cost_multiplier = 1
    elif (not constructor) or not status.strategic_map_grid in constructor.grids:
        cost_multiplier = 1
    else:
        cost_multiplier = constants.terrain_build_cost_multiplier_dict.get(
            constructor.get_cell().terrain_handler.terrain, 1
        )
    return base_price * cost_multiplier


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
    if flags.loading:
        return
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
        changed_displayed_mob = new_actor != status.displayed_mob
        if changed_displayed_mob:
            if status.displayed_mob:
                status.displayed_mob.stop_ambient_sound()
            calibrate_actor_info_display(status.mob_inventory_info_display, None)
        status.displayed_mob = new_actor
        if changed_displayed_mob and new_actor:
            new_actor.start_ambient_sound()
        select_default_tab(status.mob_tabbed_collection, new_actor)
        if new_actor and new_actor.get_cell().tile == status.displayed_tile:
            for current_same_tile_icon in status.same_tile_icon_list:
                current_same_tile_icon.reset()

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
            if (
                (
                    status.tile_tabbed_collection.current_tabbed_member == None
                    or status.tile_tabbed_collection.current_tabbed_member.tab_button.can_show()
                )
                and status.tile_tabbed_collection.current_tabbed_member
                != status.local_conditions_collection
            ):
                target_tab = status.tile_tabbed_collection.current_tabbed_member
            elif (
                constants.effect_manager.effect_active("link_inventory_tabs")
                and status.mob_tabbed_collection.current_tabbed_member
                == status.mob_inventory_collection
            ):
                target_tab = status.mob_inventory_collection
            elif status.displayed_tile.cell.settlement:
                target_tab = status.settlement_collection
            elif status.local_conditions_collection.tab_button.can_show():
                target_tab = status.local_conditions_collection
            else:
                target_tab = status.global_conditions_collection
            # Except for local conditions, try to keep the current tab selected
            # If mob inventory tab, select inventory tab
            # If can't keep local tile selected, select settlement, if present
            # Otherwise, default to local or global conditions, based on tile type

        elif tabbed_collection == status.mob_tabbed_collection:
            if status.displayed_mob.get_permission(constants.PMOB_PERMISSION):
                if status.displayed_mob.inventory:
                    target_tab = status.mob_inventory_collection
                elif (
                    constants.effect_manager.effect_active("link_inventory_tabs")
                    and status.tile_tabbed_collection.current_tabbed_member
                    == status.tile_inventory_collection
                ):
                    target_tab = status.mob_inventory_collection
                else:
                    target_tab = status.mob_reorganization_collection
            # If unit has inventory and at least 1 item held, select inventory tab
            # If tile inventory tab is selected, select inventory tab
            # Otherwise, select reorganization tab
    if target_tab and (
        target_tab == status.tile_inventory_collection or not target_tab.showing
    ):
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
        {
            "image_id": "misc/circle.png",
            "green_screen": tile.cell.terrain_handler.resource.background_color,
            "size": 0.75,
        },
        {"image_id": tile.cell.terrain_handler.resource.item_image, "size": 0.75},
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
        edited_section = section.copy()
        edited_section.update(
            {
                "image_id": section["image_id"],
                "x_size": 0.85 * section.get("size", 1.0) * section.get("x_size", 1.0),
                "y_size": 0.85 * section.get("size", 1.0) * section.get("y_size", 1.0),
                "x_offset": section.get("x_offset", 0) - 0.01,
                "y_offset": section.get("y_offset", 0) - 0.1,
                "level": section.get("level", 0) - 1,
                "green_screen": section.get("green_screen", []),
                "metadata": section.get("metadata", {}),
            }
        )
        if component.endswith("left"):
            edited_section["x_offset"] -= 0.245
            edited_section["y_offset"] += 0.043
            if component == "group left":
                edited_section["x_offset"] -= 0.025
                edited_section["y_offset"] += 0.043
                edited_section["x_size"] *= 0.94
                edited_section["y_size"] *= 0.94
            if section["metadata"]["portrait_section"] in [
                constants.FULL_BODY_PORTRAIT_SECTION,
                constants.BACKPACK_PORTRAIT_SECTION,
            ]:
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
            if section["metadata"]["portrait_section"] in [
                constants.FULL_BODY_PORTRAIT_SECTION,
                constants.BACKPACK_PORTRAIT_SECTION,
            ]:
                edited_section["x_offset"] += 0.018
                edited_section["y_offset"] += 0.055
        elif section["metadata"]["portrait_section"] in [
            constants.FULL_BODY_PORTRAIT_SECTION,
            constants.BACKPACK_PORTRAIT_SECTION,
        ]:
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
            worker.insert_equipment(worker.image_dict["left portrait"]), "group left"
        )
        + generate_unit_component_portrait(
            worker.insert_equipment(worker.image_dict["right portrait"]), "group right"
        )
        + generate_unit_component_portrait(
            officer.insert_equipment(officer.image_dict["portrait"]), "center"
        )
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
    else:
        name = "battalion"
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
    if (
        tabbed_collection
        in [status.tile_inventory_collection, status.mob_inventory_collection]
        or not target_tab.showing
    ):
        for tab_button in tabbed_collection.tabs_collection.members:
            if (
                hasattr(tab_button, "linked_element")
                and tab_button.linked_element == target_tab
            ):
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
            "detail_level": 1.0,
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
        "detail_level": 1.0,
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
                "detail_level": constants.BUTTON_DETAIL_LEVEL,
            },
        )

    elif type(image_id) == list:
        for image in image_id:
            image["x_size"] = image.get("x_size", 1) * size
            image["y_size"] = image.get("y_size", 1) * size
            image["x_offset"] = image.get("x_offset", 0) + x_offset
            image["y_offset"] = image.get("y_offset", 0) + y_offset
        return utility.combine(frame, image_id)


def get_temperature_habitability(temperature: int) -> int:
    """
    Description:
        Calculates and returns the habitability effect of a particular temperature value
    Input:
        int temperature: Temperature value to calculate habitability for
    Output:
        int: Returns the habitability effect of the inputted temperature, from 0 to 5 (5 is perfect, 0 is deadly)
    """
    if temperature >= 6:
        return constants.HABITABILITY_DEADLY
    elif temperature >= 5:
        return constants.HABITABILITY_DANGEROUS
    elif temperature >= 4:
        return constants.HABITABILITY_UNPLEASANT
    elif temperature >= 1:
        return constants.HABITABILITY_PERFECT
    elif temperature >= 0:
        return constants.HABITABILITY_UNPLEASANT
    elif temperature >= -1:
        return constants.HABITABILITY_HOSTILE
    elif temperature >= -2:
        return constants.HABITABILITY_DANGEROUS
    else:
        return constants.HABITABILITY_DEADLY


def summarize_amount_dict(item_dict: Dict[str, float]):
    """
    Description:
        Convert a dictionary of item keys and amounts to a string summary
    Input:
        Dict[str, float] item_dict: Dictionary of item keys and amounts, in the format
            {
                constants.CONSUMER_GOODS_ITEM_TYPE: 2,
                constants.FOOD_ITEM_TYPE: 1
            }
    Output:
        str: String summary, in the format "2 units of consumer goods and 1 unit of food"
    """
    text = ""
    for item_type_key, amount in item_dict.items():
        line = f"{amount} unit{utility.generate_plural(sum(item_dict.values()))} of {status.item_types[item_type_key].name}"
        if len(item_dict.keys()) == 1:
            pass
        elif len(item_dict.keys()) == 2 and item_type_key == list(item_dict.keys())[0]:
            line += " "
        elif item_type_key != list(item_dict.keys())[-1]:
            line += ", "
        else:
            line = f"and {line}"
        text += line
    return text
