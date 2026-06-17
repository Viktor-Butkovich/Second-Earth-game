from __future__ import annotations
from modules.constants import constants, status, flags
from modules.util import scaling


def config_earth_screen():
    item_prices_x, item_prices_y = (950, 100)
    item_prices_height = 35 + (
        30
        * len(
            [
                current_item_type
                for current_item_type in status.item_types.values()
                if current_item_type.can_purchase
            ]
        )
    )
    item_prices_width = 250

    status.item_prices_label = constants.ActorCreationManager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(item_prices_x, item_prices_y),
            "minimum_width": scaling.scale_width(item_prices_width),
            "height": scaling.scale_height(item_prices_height),
            "modes": [constants.EARTH_MODE],
            "image_id": "misc/item_prices_label.png",
            "init_type": constants.ITEM_PRICES_LABEL,
        }
    )

    input_dict = {
        "width": scaling.scale_width(30),
        "height": scaling.scale_height(30),
        "modes": [constants.EARTH_MODE],
        "init_type": constants.SELLABLE_ITEM_BUTTON,
    }
    current_index = 0
    for current_item_type in status.item_types.values():
        if current_item_type.can_sell or current_item_type.can_purchase:
            input_dict["coordinates"] = scaling.scale_coordinates(
                item_prices_x - 35,
                item_prices_y + item_prices_height - 65 - (30 * current_index),
            )
            input_dict["image_id"] = [
                {
                    "image_id": "misc/circle.png",
                    "green_screen": current_item_type.background_color,
                },
                f"items/{current_item_type.item_category}/{current_item_type.key}.png",
            ]
            input_dict["item_type"] = current_item_type
            new_sellable_item_button = (
                constants.ActorCreationManager.create_interface_element(input_dict)
            )
            current_index += 1

    earth_purchase_buttons = constants.ActorCreationManager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(1500, 20),
            "width": 10,
            "height": 10,
            "modes": [constants.EARTH_MODE],
            "init_type": constants.ORDERED_COLLECTION,
            "separation": scaling.scale_height(20),
            "reversed": True,
            "second_dimension_increment": scaling.scale_width(125),
            "direction": "vertical",
        }
    )
    purchase_button_grid_height = 7

    for (
        purchase_item_type
    ) in status.item_types.values():  # Creates purchase button for items from Earth
        if purchase_item_type.can_purchase:
            constants.ActorCreationManager.create_interface_element(
                {
                    "width": scaling.scale_width(100),
                    "height": scaling.scale_height(100),
                    "init_type": constants.BUY_ITEM_BUTTON,
                    "parent_collection": earth_purchase_buttons,
                    "item_type": purchase_item_type,
                    "member_config": {
                        "second_dimension_coordinate": -1
                        * (
                            len(earth_purchase_buttons.members)
                            // purchase_button_grid_height
                        )
                    },  # Re-use recruitment index for both loops
                }
            )
    for recruitment_type in status.recruitment_types:
        constants.ActorCreationManager.create_interface_element(
            {
                "width": scaling.scale_width(100),
                "height": scaling.scale_height(100),
                "init_type": constants.RECRUITMENT_BUTTON,
                "parent_collection": earth_purchase_buttons,
                "recruitment_type": recruitment_type,
                "member_config": {
                    "second_dimension_coordinate": -1
                    * (
                        len(earth_purchase_buttons.members)
                        // purchase_button_grid_height
                    )
                },  # Re-use recruitment index for both loops
            }
        )
