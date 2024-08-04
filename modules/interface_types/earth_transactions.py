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
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'recruitment_type': string value - Type of unit recruited by this button, like 'explorer'
        Output:
            None
        """
        self.recruitment_type = input_dict["recruitment_type"]
        if self.recruitment_type in constants.recruitment_types:
            self.mob_image_id = "mobs/" + self.recruitment_type + "/default.png"
        else:
            self.mob_image_id = "mobs/default/default.png"
        self.recruitment_name = ""
        for character in self.recruitment_type:
            if not character == "_":
                self.recruitment_name += character
            else:
                self.recruitment_name += " "
        status.recruitment_button_list.append(self)
        dummy_recruited_unit = constants.actor_creation_manager.create_dummy({})
        dummy_recruited_unit.set_permission(constants.PMOB_PERMISSION, True)

        if self.recruitment_name.endswith(" workers"):
            dummy_recruited_unit.set_permission(constants.WORKER_PERMISSION, True)
        elif self.recruitment_name == "steamship":
            dummy_recruited_unit.set_permission(constants.VEHICLE_PERMISSION, True)
            dummy_recruited_unit.set_permission(constants.ACTIVE_PERMISSION, True)
        else:
            dummy_recruited_unit.set_permission(constants.OFFICER_PERMISSION, True)

        if self.recruitment_name.endswith(" workers"):
            image_id = utility.combine(actor_utility.generate_unit_component_portrait(
                constants.character_manager.generate_unit_portrait(
                dummy_recruited_unit, metadata={"body_image": self.mob_image_id}
            ), "left"
            ),
            actor_utility.generate_unit_component_portrait(
                constants.character_manager.generate_unit_portrait(
                dummy_recruited_unit, metadata={"body_image": self.mob_image_id}
            ), "right"
            ))
            for image in image_id:
                if type(image) == dict and image.get("metadata", {}).get("portrait_section", "") != "full_body":
                    image["y_offset"] = image.get("y_offset", 0) - 0.02

        elif self.recruitment_name == "steamship":
            image_id = self.mob_image_id
        else:
            image_id = constants.character_manager.generate_unit_portrait(
                dummy_recruited_unit, metadata={"body_image": self.mob_image_id}
            )
            for image in image_id:
                if type(image) == dict and image.get("metadata", {}).get("portrait_section", "") != "full_body":
                    image["x_offset"] = image.get("x_offset", 0) - 0.01
                    image["y_offset"] = image.get("y_offset", 0) - 0.01

        image_id = actor_utility.generate_frame(image_id, frame="buttons/default_button_alt.png", size=0.9, y_offset = 0.02)            
        input_dict["image_id"] = image_id
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
        cost = constants.recruitment_costs[self.recruitment_type]
        if main_loop_utility.action_possible():
            if constants.money_tracker.get() >= cost:
                choice_info_dict = {
                    "recruitment_type": self.recruitment_type,
                    "cost": cost,
                    "mob_image_id": self.mob_image_id,
                    "type": "recruitment",
                }
                constants.actor_creation_manager.display_recruitment_choice_notification(
                    choice_info_dict, self.recruitment_name
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
        actor_utility.update_descriptions(self.recruitment_type)
        cost = constants.recruitment_costs[self.recruitment_type]
        if self.recruitment_type.endswith(" workers"):
            self.set_tooltip([f"Recruits a unit of {self.recruitment_name} for {cost} money."] + constants.list_descriptions[self.recruitment_type])
        else:
            self.set_tooltip([f"Recruits an {self.recruitment_name} for {cost} money."] + constants.list_descriptions[self.recruitment_type])

    def remove(self):
        """
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        Input:
            None
        Output:
            None
        """
        super().remove()
        status.recruitment_button_list = utility.remove_from_list(
            status.recruitment_button_list, self
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
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'button_type': string value - Determines the function of this button, like 'end turn'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'commodity_type': string value - Type of commodity that this button buys, like 'consumer goods'
        Output:
            None
        """
        self.item_type = input_dict["item_type"]
        input_dict["image_id"] = [
            "buttons/default_button_alt.png",
            {"image_id": "misc/green_circle.png", "size": 0.75},
            {"image_id": "items/" + self.item_type + ".png", "size": 0.75},
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
                            "You spent "
                            + str(cost)
                            + " money to buy 1 unit of "
                            + self.item_type
                            + "."
                        )
                    else:
                        text_utility.print_to_screen(
                            "You spent "
                            + str(cost)
                            + " money to buy 1 "
                            + self.item_type
                            + "."
                        )
                    if (
                        random.randrange(1, 7) == 1
                        and self.item_type in constants.commodity_types
                    ):  # 1/6 chance
                        market_utility.change_price(self.item_type, 1)
                        text_utility.print_to_screen(
                            "The price of "
                            + self.item_type
                            + " has increased from "
                            + str(cost)
                            + " to "
                            + str(cost + 1)
                            + "."
                        )
                    actor_utility.calibrate_actor_info_display(
                        status.tile_inventory_info_display,
                        status.displayed_tile_inventory,
                    )
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
                "Purchases 1 unit of "
                + self.item_type
                + " for "
                + str(constants.item_prices[self.item_type])
                + " money."
            )
        else:
            new_tooltip.append(
                "Purchases 1 "
                + self.item_type
                + " for "
                + str(constants.item_prices[self.item_type])
                + " money."
            )
        if self.item_type in status.equipment_types:
            new_tooltip += status.equipment_types[self.item_type].description
        self.set_tooltip(new_tooltip)
