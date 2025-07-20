# Contains miscellaneous functions relating to actor functionality

from __future__ import annotations
import os
import pygame
import math
from typing import List, Tuple, Dict, Any
from modules.util import utility, text_utility
from modules.constants import constants, status, flags
from modules.constructs.actor_types import actors, locations, mobs
from modules.interface_components import interface_elements


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


def reset_action_prices() -> None:
    """
    Resets the costs of any actions that were increased during the previous turn
    """
    for current_action_type in constants.action_types:
        constants.action_prices[current_action_type] = constants.base_action_prices[
            current_action_type
        ]


def double_action_price(action_type: str):
    """
    Description:
        Doubles the price of a certain action type each time it is done, usually for ones that do not require workers
    Input:
        string action_type: Type of action to double the price of
    Output:
        None
    """
    constants.action_prices[action_type] *= 2


def get_building_cost(builder: mobs.mob, building_type, building_name="n/a") -> int:
    """
    Description:
        Returns the cost of the inputted unit attempting to construct the inputted building
    Input:
        pmob/None builder: Unit attempting to construct the building, or None if no location/unit type is needed
        string building_type: Key of type of building to build, like 'infrastructure'
        string building_name = 'n/a': Name of building being built, used to differentiate roads from railroads
    Output:
        int: Returns the cost of the inputted unit attempting to construct the inputted building
    """
    if building_type == constants.INFRASTRUCTURE:
        building_type = building_name.replace(
            " ", "_"
        )  # Road, railroad, road_bridge, or railroad_bridge
    if building_type == constants.WAREHOUSES:
        if builder:
            base_price = builder.location.get_warehouses_cost()
        else:
            base_price = 5
    else:
        base_price = status.building_types[building_type].cost

    if building_type in [constants.TRAIN]:
        cost_multiplier = 1
    elif builder and builder.location.terrain_type:
        cost_multiplier = builder.location.terrain_type.build_cost_multiplier
    else:  # Abstract world has no terrain for multiplier
        cost_multiplier = 1
    return base_price * cost_multiplier


def update_roads():
    """
    Description:
        Updates the road/railroad connections between locations when a new one is built
    Input:
        None
    Output:
        None
    """
    for current_building in status.building_list:
        if current_building.building_type == constants.INFRASTRUCTURE:
            current_building.location.update_image_bundle()


def calibrate_actor_info_display(
    info_display: interface_elements.interface_element,
    new_actor: actors.actor,
    override_exempt=False,
):
    """
    Description:
        Updates all relevant objects to display a certain mob or location
    Input:
        interface_collection info_display: Collection of interface elements to calibrate to the inputted actor
        actor new_actor: The new mob or location that is displayed
        boolean override_exempt=False: Whether to calibrate interface elements that are normally exempt, such as the reorganization interface
    Output:
        None
    """
    if flags.loading:
        return
    if info_display == status.location_info_display:
        for current_same_location_icon in status.same_location_icon_list:
            current_same_location_icon.reset()
        calibrate_actor_info_display(status.location_inventory_info_display, None)
        status.displayed_location = new_actor
        if new_actor:
            new_actor.select()  # Plays correct music based on location selected - main menu/earth music

    elif info_display == status.mob_info_display:
        changed_displayed_mob = new_actor != status.displayed_mob
        if changed_displayed_mob:
            if status.displayed_mob:
                status.displayed_mob.stop_ambient_sound()
        calibrate_actor_info_display(status.mob_inventory_info_display, None)
        status.displayed_mob = new_actor
        if changed_displayed_mob and new_actor:
            new_actor.start_ambient_sound()
        if new_actor and new_actor.location == status.displayed_location:
            for current_same_location_icon in status.same_location_icon_list:
                current_same_location_icon.reset()

    target = None
    if new_actor:
        target = new_actor
    info_display.calibrate(target, override_exempt)

    if not flags.choosing_destination:  # Don't change tabs while choosing destination
        if info_display == status.mob_info_display:
            select_default_tab(status.mob_tabbed_collection, status.displayed_mob)
        elif info_display == status.location_info_display:
            select_default_tab(
                status.location_tabbed_collection, status.displayed_location
            )


def select_default_tab(
    tabbed_collection: interface_elements.tabbed_collection,
    displayed_actor: actors.actor,
) -> None:
    """
    Description:
        Selects the default tab for the inputted tabbed collection based on the inputted displayed actor
    Input:
        interface_collection tabbed_collection: Tabbed collection to select tab of
        actor displayed_actor: Mob or location to select tab for
    Output:
        None
    """
    target_tab = None
    if displayed_actor:
        for current_tab in tabbed_collection.mru_tab_queue:
            if current_tab.tab_button.tab_enabled():
                target_tab = current_tab
                break
            # Use the most recently used tab that is still showing
        if target_tab and constants.EffectManager.effect_active("debug_tab_selection"):
            print("Fetching MRU tab:", target_tab.tab_button.tab_name)
        if not target_tab:
            # If no previously used tabs are showing, use game rules to determine initial tab
            if tabbed_collection == status.location_tabbed_collection:
                if (
                    (
                        status.location_tabbed_collection.current_tabbed_member == None
                        or status.location_tabbed_collection.current_tabbed_member.tab_button.tab_enabled()
                    )
                    and status.location_tabbed_collection.current_tabbed_member
                    != status.local_conditions_collection
                ):
                    target_tab = status.location_tabbed_collection.current_tabbed_member
                elif (
                    constants.EffectManager.effect_active("link_inventory_tabs")
                    and status.mob_tabbed_collection.current_tabbed_member
                    == status.mob_inventory_collection
                ):
                    target_tab = status.mob_inventory_collection
                elif status.displayed_location.settlement:
                    target_tab = status.settlement_collection
                elif status.local_conditions_collection.tab_button.tab_enabled():
                    target_tab = status.local_conditions_collection
                else:
                    target_tab = status.global_conditions_collection
                # Except for local conditions, try to keep the current tab selected
                # If mob inventory tab, select inventory tab
                # If can't keep current location selected, select settlement, if any
                # Otherwise, default to local or global conditions, based on location type

            elif tabbed_collection == status.mob_tabbed_collection:
                if status.displayed_mob.get_permission(constants.PMOB_PERMISSION):
                    if status.displayed_mob.inventory:
                        target_tab = status.mob_inventory_collection
                    elif (
                        constants.EffectManager.effect_active("link_inventory_tabs")
                        and status.location_tabbed_collection.current_tabbed_member
                        == status.location_inventory_collection
                    ):
                        target_tab = status.mob_inventory_collection
                    else:
                        target_tab = status.mob_reorganization_collection
                # If unit has inventory and at least 1 item held, select inventory tab
                # If location inventory tab is selected, select inventory tab
                # Otherwise, select reorganization tab
            if constants.EffectManager.effect_active("debug_tab_selection"):
                print("Defaulting to tab:", target_tab.tab_button.tab_name)
    if target_tab and target_tab.tab_button.tab_enabled():
        select_interface_tab(tabbed_collection, target_tab)


def generate_resource_icon(location: locations.location):
    """
    Description:
        Generates and returns the correct string image file path based on the resource and buildings built in the inputted location
    Input:
        location location: Location to generate a resource icon for
    Output:
        string/list: Returns string or list image id for location's resource icon
    """
    image_id = [
        {
            "image_id": "misc/circle.png",
            "green_screen": location.resource.background_color,
            "size": 0.75,
        },
        {"image_id": location.resource.item_image, "size": 0.75},
    ]

    if bool(
        location.get_buildings()
    ):  # Switch to small icon if location has any buildings
        for (
            current_image
        ) in (
            image_id
        ):  # To make small icon, make each component of image smaller and shift to bottom left corner
            current_image.update({"x_offset": -0.33, "y_offset": -0.33})
            current_image["size"] = current_image.get("size", 1.0) * 0.45
    return image_id


def get_image_variants(base_path: str, keyword: str = "default") -> List[str]:
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
    base_image: str, component: str, to_front: bool = False
) -> Dict[str, Any]:
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
    base_image: List[Dict[str, Any]], component: str
) -> List[Dict[str, Any]]:
    """
    Description:
        Generates and returns an image id dict for the inputted base_image moved to the inputted section of the frame, like 'center portrait' for a group's officer's portrait
            As portraits are image id lists, they are handled differently than normal unit component images
    Input:
        image_id list base_image: Image id list of portrait to display
        string component: Section of the frame to display base image in, like 'group left'
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


def generate_group_image_id_list(
    worker: mobs.mob, officer: mobs.mob
) -> List[Dict[str, Any]]:
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
            worker.insert_equipment(
                worker.image_dict[constants.IMAGE_ID_LIST_LEFT_PORTRAIT]
            ),
            "group left",
        )
        + generate_unit_component_portrait(
            worker.insert_equipment(
                worker.image_dict[constants.IMAGE_ID_LIST_RIGHT_PORTRAIT]
            ),
            "group right",
        )
        + generate_unit_component_portrait(
            officer.insert_equipment(
                officer.image_dict[constants.IMAGE_ID_LIST_PORTRAIT]
            ),
            "center",
        )
    )


def generate_group_name(
    worker: mobs.mob, officer: mobs.mob, add_veteran: bool = False
) -> str:
    """
    Description:
        Generates and returns the name that a group formed from the inputted worker and officer would have
    Input:
        worker worker: Worker to use for group name
        officer officer: Officer to use for group name
        boolean add_veteran=False: Whether veteran should be added to the start of the name if the officer is a veteran - while a mock group needs veteran to be added, a
            group actually being created will add veteran to its name automatically when it promotes
    Output:
        str: Returns name of group formed from the inputted worker and officer
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


def generate_group_movement_points(
    worker: mobs.mob, officer: mobs.mob, generate_max: bool = False
) -> int:
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


def select_interface_tab(
    tabbed_collection: interface_elements.tabbed_collection,
    target_tab: interface_elements.interface_collection,
) -> None:
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
        in [status.location_inventory_collection, status.mob_inventory_collection]
        or not target_tab.showing
    ):
        for tab_button in tabbed_collection.tabs_collection.members:
            if (
                hasattr(tab_button, "linked_element")
                and tab_button.linked_element == target_tab
            ):
                tab_button.on_click()
                continue


def generate_label_image_id(text: str, y_offset: int = 0) -> List[Dict[str, Any]]:
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
            "level": constants.OVERLAY_ICON_LEVEL,
            "x_size": x_size + 0.02,
            "y_size": y_size,
        },
        text_utility.prepare_render(
            text,
            font=constants.fonts[constants.MAX_DETAIL_BLACK_FONT],
            override_input_dict={
                "x_offset": x_offset,
                "y_offset": y_offset,
                "free": True,
                "level": constants.OVERLAY_ICON_LEVEL,
                "override_height": None,
                "override_width": None,
                "x_size": x_size,
                "y_size": y_size,
            },
        ),
    ]


def callback(target: str, function: str, *args: Any) -> None:
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
    image_id: List[Dict[str, Any]] | str,
    frame: str = "buttons/default_button_frame.png",
    background: str = None,
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
    frame = [
        {
            "image_id": frame,
            "level": constants.FRONT_LEVEL,
            "detail_level": 1.0,
        }
    ]
    if background:
        frame.append(
            {
                "image_id": background,
                "level": constants.BACKGROUND_LEVEL,
                "detail_level": 1.0,
            }
        )

    if type(image_id) == str:
        return utility.combine(
            frame,
            {
                "image_id": image_id,
                "x_size": size,
                "y_size": size,
                "x_offset": x_offset,
                "y_offset": y_offset,
                "level": constants.FRONT_LEVEL - 1,
                "detail_level": constants.BUTTON_DETAIL_LEVEL,
            },
        )

    elif type(image_id) == list:
        framed_image = []
        for image in image_id:
            next_image = image.copy()
            if "x_size" in image and "y_size" in image:
                next_image["x_size"] = image.get("x_size", 1) * size
                next_image["y_size"] = image.get("y_size", 1) * size
            else:
                next_image["size"] = image.get("size", 1) * size
            next_image["x_offset"] = image.get("x_offset", 0) + x_offset
            next_image["y_offset"] = image.get("y_offset", 0) + y_offset
            framed_image.append(next_image)
        return utility.combine(frame, framed_image)


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


def summarize_amount_dict(item_dict: Dict[str, float]) -> str:
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


def line_item_amount_dict(item_dict: Dict[str, float]) -> str:
    """
    Description:
        Convert a dictionary of item keys and amounts to a line item-formatted string summary
    Input:
        Dict[str, float] item_dict: Dictionary of item keys and amounts, in the format
            {
                constants.CONSUMER_GOODS_ITEM_TYPE: 2,
                constants.FOOD_ITEM_TYPE: 1
            }
    Output:
        str: String summary, in the format "/n    Consumer goods: 2 /n    Food: 1"
    """
    lines = []
    for item_type_key, amount in item_dict.items():
        item_name = status.item_types[item_type_key].name.capitalize()
        lines.append(f"    {item_name}: {amount}")
    return " /n".join(lines)


def calibrate_minimap_grids(world_handler: Any, x: int, y: int) -> None:
    for current_grid in world_handler.subscribed_grids:
        current_grid.calibrate(x, y)


def focus_minimap_grids(location: locations.location) -> None:
    calibrate_minimap_grids(location.world_handler, location.x, location.y)


def add_logistics_incident_to_report(subject: str, explanation: str) -> None:
    if subject.actor_type == constants.LOCATION_ACTOR_TYPE:
        status.logistics_incident_list.append(
            {
                "unit": None,
                "location": subject,
                "explanation": explanation,
            }
        )
    else:
        status.logistics_incident_list.append(
            {
                "unit": subject,
                "location": subject.location,  # Note that if unit dies before report is created, location cannot be derived
                "explanation": explanation,
            }
        )
