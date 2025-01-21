# Contains functionality for equipment type templates

import random
from typing import Dict, List
from modules.util import (
    actor_utility,
    text_utility,
    main_loop_utility,
    minister_utility,
)
from modules.constants import constants, status, flags


class equipment_type:
    """
    Equipment template that tracks the effects, descriptions, and requirements of a particular equipment type
        Equipment inclues any item that provides an optional enhancement to a unit's capabilities
    """

    def __init__(self, input_dict: Dict) -> None:
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'key': string value - Key of this equipment type
                'description': string list value - Description tooltip for this equipment type
                'effects': string list value - List of types of actions this equipment provides a positive modifier on
                'price': float value - Purchase price of this equipment type
                'requirement': str value - Name of boolean attribute that must be True for units to equip this
        Output:
            None
        """
        self.key: str = input_dict["equipment_type"]
        self.description: List[str] = input_dict.get("description", [])
        self.effects: Dict[str, any] = input_dict.get("effects", {})
        status.equipment_types[self.key] = self
        self.can_purchase: bool = input_dict.get("can_purchase", False)
        self.price: float = input_dict.get("price", 5.0)
        requirements_type, requirements = input_dict.get("requirements", [None])
        self.requirements_type: str = requirements_type
        self.requirements: List[str] = requirements
        self.equipment_image: dict = input_dict.get("equipment_image", None)

    def apply_modifier(self, action_type: str) -> int:
        """
        Description:
            Returns the modifier this equipment applies to the inputted action type, if any
        Input:
            string action_type: Type of action to apply to, like 'combat'
        Output:
            int: Returns modifier this equipment applies to the inputted action type
        """
        modifier = 0
        if action_type in self.effects.get("positive_modifiers", []):
            modifier = random.randrange(0, 2)
        elif action_type in self.effects.get("negative_modifiers", []):
            modifier = -1 * random.randrange(0, 2)

        if modifier != 0 and constants.effect_manager.effect_active("show_modifiers"):
            if modifier > 0:
                print(f"{self.key} gave modifier of +{modifier} to {action_type} roll")
            else:
                print(f"{self.key} gave modifier of {modifier} to {action_type} roll")
        return modifier

    def can_show_portrait_section(self, unit, key: str) -> bool:
        """
        Description:
            Returns whether the inputted unit can show the inputted section of this equipment in its portrait
        Input:
            pmob unit: Unit to check conditions for
            string key: Key of equipment type to check for, like constants.SPACESUIT_EQUIPMENT
        Output:
            bool: Returns whether the inputted unit can show the inputted section of this equipment in its portrait
        """
        if self.key == constants.SPACESUITS_EQUIPMENT:
            if unit.get_cell():
                habitability = unit.get_cell().terrain_handler.get_unit_habitability(
                    unit=None
                )
            else:
                habitability = constants.HABITABILITY_DEADLY
            toggled_sections = [
                constants.HAT_PORTRAIT_SECTION,
                constants.HAIR_PORTRAIT_SECTION,
                constants.FACIAL_HAIR_PORTAIT_SECTION,
            ]
            return not (
                key in toggled_sections
                and habitability != constants.HABITABILITY_DEADLY
            )
            # Take off spacesuit helmet if in non-deadly conditions
        else:
            return True

    def equip(self, unit) -> None:
        """
        Description:
            Orders the inputted unit to equip this type of item
        Input:
            pmob unit: Unit to equip item to
        Output:
            None
        """
        if not unit.equipment.get(self.key, False):
            unit.equipment[self.key] = True
            if self.effects.get("max_movement_points", 0) != 0:
                unit.set_max_movement_points(
                    4 + self.effects["max_movement_points"],
                    initial_setup=False,
                    allow_increase=False,
                )
            for permission in self.effects.get("permissions", []):
                unit.set_permission(permission, True, override=True, update_image=False)
            if unit.get_permission(constants.GROUP_PERMISSION):
                if self.check_requirement(unit.officer):
                    self.equip(unit.officer)
                if self.check_requirement(unit.worker):
                    self.equip(unit.worker)
            unit.update_image_bundle()

    def unequip(self, unit) -> None:
        """
        Description:
            Orders the inputted unit to unequip this type of item
        Input:
            pmob unit: Unit to unequip item from
        Output:
            None
        """
        if unit.equipment.get(self.key, False):
            del unit.equipment[self.key]
            if self.effects.get("max_movement_points", 0) != 0:
                unit.set_max_movement_points(
                    unit.unit_type.movement_points,
                    initial_setup=False,
                    allow_increase=False,
                )
            for permission in self.effects.get("permissions", []):
                unit.set_permission(permission, False, override=True)
            if unit.get_permission(constants.GROUP_PERMISSION):
                self.unequip(unit.officer)
                self.unequip(unit.worker)
            unit.update_image_bundle()

    def check_requirement(self, unit) -> bool:
        """
        Description:
            Returns whether the inputted unit fulfills the requirements to equip this item - must have the requirement boolean attribute and it must be True
        Input:
            pmob unit: Unit to check requirement for
        Output:
            bool: Returns whether the inputted unit fulfills the requirements to equip this item
        """
        if self.requirements_type:
            if self.requirements_type == "any":
                return unit.any_permissions(*self.requirements)
            elif self.requirements_type == "all":
                return unit.all_permissions(*self.requirements)
        return False


def transfer(item_type: str, amount, source_type: str) -> None:
    """
    Description:
        Transfers amount of item type from the source inventory to the other (tile to mob and vice versa, if picking up or dropping)
    Input:
        string item_type: Type of item to transfer, like 'diamond' or 'rifles'
        int/str amount: Amount of item to transfer, or 'all' if transferring all
        string source_type: Item origin, like 'tile_inventory' or 'mob_inventory'
    Output:
        None
    """
    if main_loop_utility.action_possible():
        if minister_utility.positions_filled():
            displayed_mob = status.displayed_mob
            displayed_tile = status.displayed_tile
            if (
                displayed_mob
                and displayed_tile
                and displayed_mob.get_permission(constants.PMOB_PERMISSION)
                and displayed_mob.get_cell().tile == displayed_tile
            ):
                if amount == "all":
                    if source_type == "tile_inventory":
                        amount = displayed_tile.get_inventory(item_type)
                    elif source_type == "mob_inventory":
                        amount = displayed_mob.get_inventory(item_type)
                elif (
                    source_type == "mob_inventory"
                    and amount > displayed_mob.get_inventory(item_type)
                ):
                    text_utility.print_to_screen(
                        f"This unit does not have enough {item_type} to transfer."
                    )
                    return
                elif (
                    source_type == "tile_inventory"
                    and amount > displayed_tile.get_inventory(item_type)
                ):
                    text_utility.print_to_screen(
                        f"This tile does not have enough {item_type} to transfer."
                    )
                    return

                if displayed_mob.all_permissions(
                    constants.VEHICLE_PERMISSION, constants.TRAIN_PERMISSION
                ) and not displayed_tile.cell.has_intact_building(
                    constants.TRAIN_STATION
                ):
                    text_utility.print_to_screen(
                        "A train can only transfer cargo at a train station."
                    )
                    return

                if source_type == "tile_inventory":
                    if displayed_mob.get_inventory_remaining(amount) < 0:
                        amount = displayed_mob.get_inventory_remaining()
                        if amount == 0:
                            if item_type == "each":
                                text_utility.print_to_screen(
                                    "This unit can not pick up any items."
                                )
                            else:
                                text_utility.print_to_screen(
                                    f"This unit can not pick up {item_type}."
                                )
                            return

                if displayed_mob.sentry_mode:
                    displayed_mob.set_sentry_mode(False)

                if source_type == "tile_inventory":
                    source = status.displayed_tile
                    destination = status.displayed_mob
                elif source_type == "mob_inventory":
                    source = status.displayed_mob
                    destination = status.displayed_tile
                if item_type == "each":
                    for item in source.inventory.copy():
                        amount = source.inventory[item]
                        if (
                            destination.get_inventory_remaining(amount) < 0
                            and destination == status.displayed_mob
                        ):
                            amount = destination.get_inventory_remaining()
                        destination.change_inventory(item, amount)
                        source.change_inventory(item, amount * -1)
                else:
                    destination.change_inventory(item_type, amount)
                    source.change_inventory(item_type, amount * -1)

                if source_type == "tile_inventory":  # Pick up item(s)
                    actor_utility.select_interface_tab(
                        status.mob_tabbed_collection, status.mob_inventory_collection
                    )
                    actor_utility.calibrate_actor_info_display(
                        status.tile_info_display, displayed_tile
                    )

                elif source_type == "mob_inventory":  # Drop item(s)
                    actor_utility.select_interface_tab(
                        status.tile_tabbed_collection, status.tile_inventory_collection
                    )
                    if not status.displayed_mob.inventory:
                        actor_utility.select_default_tab(
                            status.mob_tabbed_collection, status.displayed_mob
                        )
                    actor_utility.calibrate_actor_info_display(
                        status.mob_info_display, displayed_mob
                    )

            elif source_type == "mob_inventory":
                text_utility.print_to_screen(
                    "There is no tile to transfer this commodity to."
                )
            elif source_type == "tile_inventory":
                text_utility.print_to_screen(
                    "There is no unit to transfer this commodity to."
                )
    else:
        text_utility.print_to_screen("You are busy and cannot transfer commodities.")
