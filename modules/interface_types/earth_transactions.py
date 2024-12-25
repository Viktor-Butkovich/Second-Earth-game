# Contains functionality for buttons relating to the Earth headquarters screen

import random
from .buttons import button
from ..util import (
    main_loop_utility,
    text_utility,
    market_utility,
    utility,
    actor_utility,
    minister_utility,
    dummy_utility,
)
from ..constructs import unit_types
import modules.constants.constants as constants
import modules.constants.status as status


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
        input_dict[
            "image_id"
        ] = self.recruitment_type.generate_framed_recruitment_image()
        input_dict["button_type"] = "recruitment"
        super().__init__(input_dict)

    def on_click(self):
        """
        Description:
            Controls this button's behavior when clicked. This type of button creates a new unit with a type depending on recruitment_type and places it on Earth
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            if constants.money_tracker.get() >= self.recruitment_type.recruitment_cost:
                constants.actor_creation_manager.display_recruitment_choice_notification(
                    self.recruitment_type
                )
            else:
                text_utility.print_to_screen(
                    "You do not have enough money to recruit this unit"
                )
        else:
            text_utility.print_to_screen("You are busy and cannot recruit a unit")

    def update_tooltip(self):
        """
        Description:
            Sets this image's tooltip to what it should be, depending on its button_type. This type of button has a tooltip describing the type of unit it recruits
        Input:
            None
        Output:
            None
        """
        if self.recruitment_type.number >= 2:
            self.set_tooltip(
                [
                    f"Recruits a unit of {self.recruitment_type.name} for {self.recruitment_type.recruitment_cost} money."
                ]
                + self.recruitment_type.get_list_description()
            )
        else:
            self.set_tooltip(
                [
                    f"Recruits a {self.recruitment_type.name} for {self.recruitment_type.recruitment_cost} money."
                ]
                + self.recruitment_type.get_list_description()
            )


class buy_item_button(button):
    """
    Button that buys a unit of commodity_type when clicked and has an image matching that of its commodity
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
                'commodity_type': string value - Type of commodity that this button buys, like 'consumer goods'
        Output:
            None
        """
        self.item_type = input_dict["item_type"]
        input_dict["image_id"] = [
            {
                "image_id": "buttons/default_button_alt.png",
                "detail_level": constants.BUTTON_DETAIL_LEVEL,
            },
            {
                "image_id": "misc/green_circle.png",
                "size": 0.75,
                "detail_level": constants.BUTTON_DETAIL_LEVEL,
            },
            {
                "image_id": f"items/{self.item_type}.png",
                "size": 0.75,
                "detail_level": constants.BUTTON_DETAIL_LEVEL,
            },
        ]
        input_dict["button_type"] = "buy item"
        super().__init__(input_dict)

    def on_click(self):
        """
        Description:
            Controls this button's behavior when clicked. This type of button buys a unit of the item_type commodity
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            cost = constants.item_prices[self.item_type]
            if constants.money_tracker.get() >= cost:
                if minister_utility.positions_filled():
                    actor_utility.calibrate_actor_info_display(
                        status.tile_info_display,
                        status.earth_grid.cell_list[0][0].tile,
                    )
                    status.earth_grid.cell_list[0][0].tile.change_inventory(
                        self.item_type, 1
                    )  # adds 1 of commodity type to
                    constants.money_tracker.change(-1 * cost, "items")
                    if self.item_type.endswith("s"):
                        text_utility.print_to_screen(
                            f"You spent {cost} money to buy 1 unit of {self.item_type}."
                        )
                    else:
                        text_utility.print_to_screen(
                            f"You spent {cost} money to buy 1 {self.item_type}."
                        )
                    if (
                        random.randrange(1, 7) == 1
                        and self.item_type in constants.commodity_types
                    ):  # 1/6 chance
                        market_utility.change_price(self.item_type, 1)
                        text_utility.print_to_screen(
                            f"The price of {self.item_type} has increased from {cost} to {cost + 1}."
                        )
                    for linked_tab in status.tile_tabbed_collection.tabbed_members:
                        linked_tab_button = linked_tab.linked_tab_button
                        if linked_tab_button.identifier == constants.INVENTORY_PANEL:
                            linked_tab_button.on_click()
                            pass
            else:
                text_utility.print_to_screen(
                    "You do not have enough money to purchase this commodity"
                )
        else:
            text_utility.print_to_screen(
                "You are busy and cannot purchase " + self.item_type + "."
            )

    def update_tooltip(self):
        """
        Description:
            Sets this image's tooltip to what it should be, depending on its button_type. This type of button has a tooltip describing the commodity that it buys and its price
        Input:
            None
        Output:
            None
        """
        new_tooltip = []
        if self.item_type.endswith("s"):
            new_tooltip.append(
                f"Purchases 1 unit of {self.item_type} for {constants.item_prices[self.item_type]} money."
            )
        else:
            new_tooltip.append(
                f"Purchases 1 {self.item_type} for {constants.item_prices[self.item_type]} money."
            )
        if self.item_type in status.equipment_types:
            new_tooltip += status.equipment_types[self.item_type].description
        self.set_tooltip(new_tooltip)
