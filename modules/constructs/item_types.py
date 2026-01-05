from __future__ import annotations
from typing import Dict, List, Any
from modules.util import (
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
        status.item_types[self.key] = self
        self.description: List[str] = input_dict.get("description", [])

        self.can_purchase: bool = input_dict.get("can_purchase", False)
        self.can_sell: bool = input_dict.get("can_sell", False)
        self.price: float = input_dict.get("price", 5.0)

        self.amount_sold_this_turn: int = input_dict.get("amount_sold_this_turn", 0)
        self.production_attempted_this_turn: bool = False
        self.amount_produced_this_turn: int = input_dict.get(
            "amount_produced_this_turn", 0
        )

        self.allow_price_variation: bool = input_dict.get(
            "allow_price_variation", False
        )
        self.item_image: str = input_dict.get(
            "item_image", "items/consumer_goods.png"
        )  # Basic image that can be used in icons
        self.background_color: tuple = input_dict.get(
            "background_color", constants.color_dict[constants.COLOR_GREEN_ICON]
        )
        self.name: str = input_dict.get("name", self.key).replace("_", " ")

    def apply_save_dict(self, save_dict: Dict[str, Any]) -> None:
        """
        Description:
            Uses a save dict to set this object's values
        Input:
            dictionary save_dict: Dictionary containing the values to set
        Output:
            None
        """
        # Key used to choose which item type to apply save dict to
        self.amount_sold_this_turn = save_dict["amount_sold_this_turn"]
        self.amount_produced_this_turn = save_dict["amount_produced_this_turn"]
        self.production_attempted_this_turn = save_dict[
            "production_attempted_this_turn"
        ]
        self.price = save_dict["price"]

    def to_save_dict(self) -> Dict[str, Any]:
        """
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
        """
        return {
            "key": self.key,
            "amount_sold_this_turn": self.amount_sold_this_turn,
            "amount_produced_this_turn": self.amount_produced_this_turn,
            "production_attempted_this_turn": self.production_attempted_this_turn,
            "price": self.price,
        }


def transfer(
    source_type: str, transferred_item: item_type = None, amount: int = None
) -> None:
    """
    Description:
        Transfers amount of item type from the source inventory to the other (location to mob and vice versa, if picking up or dropping)
    Input:
        item_type transferred_item: Type of item to transfer, like diamond or spacesuits, or None if transferring each type
        int/str amount: Amount of item to transfer, or None if transferring all of the type
        string source_type: Item origin, like 'location_inventory' or 'mob_inventory'
    Output:
        None
    """
    if main_loop_utility.action_possible():
        if minister_utility.positions_filled():
            displayed_mob = status.displayed_mob
            displayed_location = status.displayed_location
            if (
                displayed_mob
                and displayed_location
                and displayed_mob.get_permission(constants.PMOB_PERMISSION)
                and displayed_mob.location == displayed_location
            ):
                if amount == None:
                    if transferred_item == None:  # If transferring all items
                        if source_type == "location_inventory":
                            amount = displayed_location.get_inventory_used()
                        elif source_type == "mob_inventory":
                            amount = displayed_mob.get_inventory_used()
                    else:  # If transferring all of a specific item type
                        if source_type == "location_inventory":
                            amount = displayed_location.get_inventory(transferred_item)
                        elif source_type == "mob_inventory":
                            amount = displayed_mob.get_inventory(transferred_item)

                if displayed_mob.all_permissions(
                    constants.VEHICLE_PERMISSION, constants.TRAIN_PERMISSION
                ) and not displayed_location.has_intact_building(
                    constants.TRAIN_STATION
                ):
                    text_utility.print_to_screen(
                        "A train can only transfer cargo at a train station."
                    )
                    return

                if source_type == "location_inventory":
                    if displayed_mob.get_inventory_remaining() == 0:
                        if transferred_item == None:  # If transferring all types
                            text_utility.print_to_screen(
                                "This unit can not pick up any items."
                            )
                        else:
                            text_utility.print_to_screen(
                                f"This unit can not pick up {transferred_item.name}."
                            )
                        return
                    elif amount > displayed_mob.get_inventory_remaining():
                        if transferred_item == None:  # If transferring all types
                            text_utility.print_to_screen(
                                "This unit can not pick up all the items."
                            )
                        else:
                            text_utility.print_to_screen(
                                f"This unit can not pick up all the {transferred_item.name}."
                            )
                        return

                displayed_mob.set_permission(constants.SENTRY_MODE_PERMISSION, False)

                if source_type == "location_inventory":
                    source = status.displayed_location
                    destination = status.displayed_mob
                elif source_type == "mob_inventory":
                    source = status.displayed_mob
                    destination = status.displayed_location
                if transferred_item == None:  # If transferring all types
                    for item in source.get_held_items():
                        amount = source.get_inventory(item)
                        if (
                            destination.get_inventory_remaining(amount) < 0
                            and destination == status.displayed_mob
                        ):
                            amount = destination.get_inventory_remaining()
                        destination.change_inventory(item, amount)
                        source.change_inventory(item, amount * -1)
                else:
                    amount_transferred = min(
                        source.get_inventory(transferred_item), amount
                    )
                    # In some cases, a button to transfer x amount of an item may be clicked when less than x is available
                    destination.change_inventory(transferred_item, amount_transferred)
                    source.change_inventory(transferred_item, amount_transferred * -1)

            elif source_type == "mob_inventory":
                text_utility.print_to_screen(
                    "There is no location to transfer this item to."
                )
            elif source_type == "location_inventory":
                text_utility.print_to_screen(
                    "There is no unit to transfer this item to."
                )
    else:
        text_utility.print_to_screen("You are busy and cannot transfer items.")
