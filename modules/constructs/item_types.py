from typing import Dict, List
from modules.util import (
    actor_utility,
    text_utility,
    main_loop_utility,
    minister_utility,
)
from modules.constants import constants, status, flags


class item_type:
    """
    Item template that tracks a particular item type
        An item is any object that can be carried in an inventory slot
    """

    def __init__(self, input_dict: Dict) -> None:
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'key': string value - Key of this equipment type
                'description': string list value - Description tooltip for this equipment type
                'price': float value - Purchase price of this equipment type
        Output:
            None
        """
        self.key: str = input_dict["equipment_type"]
        self.description: List[str] = input_dict.get("description", [])
        self.can_purchase: bool = input_dict.get("can_purchase", False)
        self.price: float = input_dict.get("price", 5.0)
        self.item_image: dict = input_dict.get("item_image", None)


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
