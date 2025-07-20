# Contains functionality for buttons relating to the Earth headquarters screen

from __future__ import annotations
import random
from typing import List
from modules.interface_components.buttons import button
from modules.util import (
    main_loop_utility,
    text_utility,
    market_utility,
    actor_utility,
    minister_utility,
)
from modules.constructs import unit_types, item_types
from modules.constants import constants, status, flags


class recruitment_button(button):
    """
    Button that creates a new unit with a type depending on recruitment_type and places it on Earth
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = None: pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'recruitment_type': string value - Type of unit recruited by this button, like 'explorer'
        Output:
            None
        """
        self.recruitment_type: unit_types.unit_type = input_dict["recruitment_type"]
        input_dict["image_id"] = (
            self.recruitment_type.generate_framed_recruitment_image()
        )
        input_dict["button_type"] = "recruitment"
        super().__init__(input_dict)

    def on_click(self):
        """
        Controls this button's behavior when clicked. This type of button creates a new unit with a type depending on recruitment_type and places it on Earth
        """
        if main_loop_utility.action_possible():
            if constants.MoneyTracker.get() >= self.recruitment_type.recruitment_cost:
                constants.ActorCreationManager.display_recruitment_choice_notification(
                    self.recruitment_type
                )
            else:
                text_utility.print_to_screen(
                    "You do not have enough money to recruit this unit"
                )
        else:
            text_utility.print_to_screen("You are busy and cannot recruit a unit")

    @property
    def tooltip_text(self) -> List[List[str]]:
        """
        Provides the tooltip for this object
        """
        if self.recruitment_type.number >= 2:
            return [
                f"Recruits a unit of {self.recruitment_type.name} for {self.recruitment_type.recruitment_cost} money."
            ] + self.recruitment_type.get_list_description()
        else:
            return [
                f"Recruits a {self.recruitment_type.name} for {self.recruitment_type.recruitment_cost} money."
            ] + self.recruitment_type.get_list_description()


class buy_item_button(button):
    """
    Button that buys a unit of item when clicked and has an image matching that of its item
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'button_type': string value - Determines the function of this button, like 'end turn'
                'keybind_id' = None: pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'item_type': string value - Key for the item type that this button buys, like "consumer_goods"
        Output:
            None
        """
        self.item_type: item_types.item_type = input_dict["item_type"]
        input_dict["image_id"] = [
            {
                "image_id": "buttons/default_button_alt.png",
                "detail_level": constants.BUTTON_DETAIL_LEVEL,
            },
            {
                "image_id": "misc/circle.png",
                "green_screen": self.item_type.background_color,
                "size": 0.75,
                "detail_level": constants.BUTTON_DETAIL_LEVEL,
            },
            {
                "image_id": self.item_type.item_image,
                "size": 0.75,
                "detail_level": constants.BUTTON_DETAIL_LEVEL,
            },
        ]
        input_dict["button_type"] = "buy item"
        super().__init__(input_dict)

    def on_click(self):
        """
        Controls this button's behavior when clicked. This type of button buys a unit of the item
        """
        if main_loop_utility.action_possible():
            if constants.MoneyTracker.get() >= self.item_type.price:
                if minister_utility.positions_filled():
                    actor_utility.calibrate_actor_info_display(
                        status.location_info_display,
                        status.earth_world.find_location(0, 0),
                    )
                    status.earth_world.find_location(0, 0).change_inventory(
                        self.item_type, 1
                    )  # Adds 1 of item bought to Earth location

                    actor_utility.calibrate_actor_info_display(
                        status.location_inventory_info_display,
                        status.displayed_location_inventory,
                    )
                    # Update currently selected item icon with new contents and item quantity

                    constants.MoneyTracker.change(-1 * self.item_type.price, "items")
                    if self.item_type.name.endswith("s"):
                        text_utility.print_to_screen(
                            f"You spent {self.item_type.price} money to buy 1 unit of {self.item_type.name}."
                        )
                    else:
                        text_utility.print_to_screen(
                            f"You spent {self.item_type.price} money to buy 1 {self.item_type.name}."
                        )
                    if (
                        random.randrange(1, 7) == 1
                        and self.item_type.allow_price_variation
                    ):  # 1/6 chance
                        text_utility.print_to_screen(
                            f"The price of {self.item_type.name} has increased from {self.item_type.price} to {self.item_type.price + 1}."
                        )
                        market_utility.change_price(self.item_type, 1)
                    actor_utility.select_interface_tab(
                        status.location_tabbed_collection,
                        status.location_inventory_collection,
                    )
            else:
                text_utility.print_to_screen(
                    "You do not have enough money to purchase this item"
                )
        else:
            text_utility.print_to_screen(
                f"You are busy and cannot purchase {self.item_type.name}."
            )

    @property
    def tooltip_text(self) -> List[List[str]]:
        """
        Provides the tooltip for this object
        """
        return [
            f"Purchases 1 unit of {self.item_type.name} for {self.item_type.price} money."
        ] + self.item_type.description
