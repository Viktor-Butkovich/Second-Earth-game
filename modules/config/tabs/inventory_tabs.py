from __future__ import annotations
from modules.constants import constants, status, flags
from modules.util import scaling, actor_utility

inventory_cell_height = scaling.scale_height(29)
inventory_cell_width = scaling.scale_width(29)


def config_inventory_tabs() -> None:
    mob_inventory_tab()
    location_inventory_tab()


def mob_inventory_tab() -> None:
    """
    Initializes the mob tabbed collection and inventory interface
    """
    status.mob_inventory_collection = (
        constants.ActorCreationManager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(-40, -5),
                "width": scaling.scale_width(0),
                "height": scaling.scale_height(0),
                "init_type": constants.ORDERED_COLLECTION,
                "parent_collection": status.mob_tabbed_collection,
                "member_config": {
                    "tabbed": True,
                    "button_image_id": [
                        "buttons/default_button_alt2.png",
                        {
                            "image_id": "misc/circle.png",
                            "green_screen": status.item_types[
                                constants.RESOURCE_CONSUMER_GOODS
                            ].background_color,
                            "size": 0.75,
                        },
                        {
                            "image_id": status.item_types[
                                constants.RESOURCE_CONSUMER_GOODS
                            ].item_image,
                            "size": 0.75,
                        },
                    ],
                    "identifier": constants.INVENTORY_PANEL,
                    "tab_name": "cargo",
                },
            }
        )
    )

    input_dict = {
        "minimum_width": scaling.scale_width(10),
        "height": scaling.scale_height(constants.default_notification_font_size + 5),
        "image_id": "misc/default_label.png",
        "init_type": constants.MOB_INVENTORY_CAPACITY_LABEL,
        "actor_type": constants.MOB_ACTOR_TYPE,
        "parent_collection": status.mob_inventory_collection,
    }
    mob_inventory_capacity_label = (
        constants.ActorCreationManager.create_interface_element(input_dict)
    )

    status.mob_inventory_grid = constants.ActorCreationManager.create_interface_element(
        {
            "width": (inventory_cell_width + scaling.scale_width(2)) * 9,
            "height": (inventory_cell_height + scaling.scale_height(2)) * 3,
            "separation": scaling.scale_height(2),
            "init_type": constants.INVENTORY_GRID,
            "parent_collection": status.mob_inventory_collection,
            "second_dimension_increment": inventory_cell_width
            + scaling.scale_height(2),
        }
    )
    for current_index in range(27):
        constants.ActorCreationManager.create_interface_element(
            {
                "width": inventory_cell_width,
                "height": inventory_cell_height,
                "image_id": "buttons/default_button.png",
                "init_type": constants.ITEM_ICON,
                "parent_collection": status.mob_inventory_grid,
                "icon_index": current_index,
                "actor_type": constants.MOB_INVENTORY_ACTOR_TYPE,
                "member_config": {
                    "second_dimension_coordinate": current_index % 9,
                    "order_y_offset": status.mob_inventory_grid.height,
                },
            }
        )

    mob_scroll_up_button = constants.ActorCreationManager.create_interface_element(
        {
            "width": scaling.scale_width(35),
            "height": scaling.scale_width(35),
            "parent_collection": status.mob_inventory_grid,
            "image_id": "buttons/cycle_ministers_up_button.png",
            "value_name": "inventory_page",
            "increment": -1,
            "member_config": {
                "order_exempt": True,
                "x_offset": scaling.scale_width(-40),
                "y_offset": 0,
            },
            "init_type": constants.SCROLL_BUTTON,
        }
    )

    mob_scroll_down_button = constants.ActorCreationManager.create_interface_element(
        {
            "width": scaling.scale_width(35),
            "height": scaling.scale_width(35),
            "parent_collection": status.mob_inventory_grid,
            "image_id": "buttons/cycle_ministers_down_button.png",
            "value_name": "inventory_page",
            "increment": 1,
            "member_config": {
                "order_exempt": True,
                "x_offset": scaling.scale_width(-40),
                "y_offset": status.mob_inventory_grid.height - scaling.scale_height(35),
            },
            "init_type": constants.SCROLL_BUTTON,
        }
    )


def location_inventory_tab() -> None:
    """
    Initializes the location tabbed collection and inventory interface
    """
    status.location_inventory_collection = (
        constants.ActorCreationManager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(-40, -5),
                "width": scaling.scale_width(0),
                "height": scaling.scale_height(0),
                "init_type": constants.ORDERED_COLLECTION,
                "parent_collection": status.location_tabbed_collection,
                "member_config": {
                    "tabbed": True,
                    "button_image_id": [
                        "buttons/default_button_alt2.png",
                        {
                            "image_id": "misc/circle.png",
                            "green_screen": status.item_types[
                                constants.RESOURCE_CONSUMER_GOODS
                            ].background_color,
                            "size": 0.75,
                        },
                        {
                            "image_id": status.item_types[
                                constants.RESOURCE_CONSUMER_GOODS
                            ].item_image,
                            "size": 0.75,
                        },
                    ],
                    "identifier": constants.INVENTORY_PANEL,
                    "tab_name": "supply chain",
                },
            }
        )
    )

    location_inventory_capacity_label = (
        constants.ActorCreationManager.create_interface_element(
            {
                "minimum_width": scaling.scale_width(10),
                "height": scaling.scale_height(
                    constants.default_notification_font_size + 5
                ),
                "image_id": "misc/default_label.png",
                "init_type": constants.LOCATION_INVENTORY_CAPACITY_LABEL,
                "actor_type": constants.LOCATION_ACTOR_TYPE,
                "parent_collection": status.location_inventory_collection,
            }
        )
    )

    status.location_inventory_grid = (
        constants.ActorCreationManager.create_interface_element(
            {
                "width": (inventory_cell_width + scaling.scale_width(2)) * 9,
                "height": (inventory_cell_height + scaling.scale_height(2)) * 3,
                "separation": scaling.scale_height(2),
                "init_type": constants.INVENTORY_GRID,
                "parent_collection": status.location_inventory_collection,
                "second_dimension_increment": inventory_cell_width
                + scaling.scale_height(2),
            }
        )
    )

    location_scroll_up_button = constants.ActorCreationManager.create_interface_element(
        {
            "width": scaling.scale_width(35),
            "height": scaling.scale_height(35),
            "parent_collection": status.location_inventory_grid,
            "image_id": "buttons/cycle_ministers_up_button.png",
            "value_name": "inventory_page",
            "increment": -1,
            "member_config": {
                "order_exempt": True,
                "x_offset": scaling.scale_width(-40),
                "y_offset": status.location_inventory_grid.height
                - scaling.scale_height(35),
            },
            "init_type": constants.SCROLL_BUTTON,
        }
    )

    location_scroll_down_button = (
        constants.ActorCreationManager.create_interface_element(
            {
                "width": scaling.scale_width(35),
                "height": scaling.scale_height(35),
                "parent_collection": status.location_inventory_grid,
                "image_id": "buttons/cycle_ministers_down_button.png",
                "value_name": "inventory_page",
                "increment": 1,
                "member_config": {
                    "order_exempt": True,
                    "x_offset": scaling.scale_width(-40),
                    "y_offset": 0,
                },
                "init_type": constants.SCROLL_BUTTON,
            }
        )
    )

    for current_index in range(27):
        constants.ActorCreationManager.create_interface_element(
            {
                "width": inventory_cell_width,
                "height": inventory_cell_height,
                "image_id": "buttons/default_button.png",
                "init_type": constants.ITEM_ICON,
                "parent_collection": status.location_inventory_grid,
                "icon_index": current_index,
                "actor_type": constants.LOCATION_INVENTORY_ACTOR_TYPE,
                "member_config": {
                    "second_dimension_coordinate": current_index % 9,
                    "order_y_offset": status.location_inventory_grid.height,
                },
            }
        )

    inventory_info_display_interface()

    supply_chain_table_coordinate_height = 6
    status.supply_chain_table = constants.ActorCreationManager.create_interface_element(
        input_dict={
            "init_type": constants.TABLE_GRID,
            "subject": constants.SUPPLY_CHAIN_TABLE_SUBJECT,
            "width": scaling.scale_width(560),
            "height": scaling.scale_height(supply_chain_table_coordinate_height * 30),
            "coordinate_width": 5,
            "coordinate_height": supply_chain_table_coordinate_height,
            "parent_collection": status.location_inventory_collection,
            "internal_line_color": constants.COLOR_BLACK,
            "external_line_color": constants.COLOR_BLACK,
            "member_config": {
                "order_x_offset": scaling.scale_width(-90),
                "order_y_offset": scaling.scale_height(-5),
            },
        }
    )


def inventory_info_display_interface() -> None:
    """
    Displays the item sub-display interface for item-specific information
    """
    for inventory_collection in [
        status.location_inventory_collection,
        status.mob_inventory_collection,
    ]:
        item_agnostic_buttons = constants.ActorCreationManager.create_interface_element(
            {
                "coordinates": (
                    (
                        status.location_inventory_grid.width + scaling.scale_width(5)
                        if status.location_inventory_grid
                        else status.mob_inventory_grid.width + scaling.scale_width(5)
                    ),
                    (
                        -1
                        * (
                            status.location_inventory_grid.height
                            + scaling.scale_height(30)
                        )
                        if status.location_inventory_grid
                        else -1
                        * (status.mob_inventory_grid.height + scaling.scale_height(30))
                    ),
                ),
                "width": scaling.scale_width(0),
                "height": scaling.scale_height(0),
                "init_type": constants.ORDERED_COLLECTION,
                "parent_collection": inventory_collection,
                "direction": "vertical",
                "reversed": True,
                "separation": scaling.scale_height(5),
                "member_config": {
                    "order_exempt": True,
                },
            }
        )  # Collection of buttons that shows regardless of item selection
        if inventory_collection == status.location_inventory_collection:
            button_definitions = [
                (
                    constants.USE_EACH_EQUIPMENT_BUTTON,
                    "buttons/use_equipment_button.png",
                ),
                (
                    constants.PICK_UP_EACH_ITEM_BUTTON,
                    "buttons/item_drop_each_button.png",
                ),
                (constants.SELL_EACH_ITEM_BUTTON, "buttons/item_sell_each_button.png"),
            ]
        elif inventory_collection == status.mob_inventory_collection:
            button_definitions = [
                (
                    constants.DROP_EACH_ITEM_BUTTON,
                    "buttons/item_pick_up_each_button.png",
                ),
            ]
        for init_type, image_id in button_definitions:
            constants.ActorCreationManager.create_interface_element(
                {
                    "init_type": init_type,
                    "image_id": image_id,
                    "parent_collection": item_agnostic_buttons,
                    "width": scaling.scale_width(35),
                    "height": scaling.scale_height(35),
                }
            )

    base_inventory_info_display_input_dict = {
        "coordinates": scaling.scale_coordinates(320, 5),
        "width": scaling.scale_width(0),
        "height": scaling.scale_height(constants.default_notification_font_size + 10)
        * 2,
        "init_type": constants.ORDERED_COLLECTION,
        "is_info_display": True,
        "member_config": {
            "calibrate_exempt": True,
            "order_exempt": True,
        },
    }
    status.mob_inventory_info_display = (
        constants.ActorCreationManager.create_interface_element(
            {
                "actor_type": constants.MOB_INVENTORY_ACTOR_TYPE,
                "description": "mob inventory panel",
                "parent_collection": status.mob_inventory_collection,
                **base_inventory_info_display_input_dict,
            }
        )
    )
    status.location_inventory_info_display = (
        constants.ActorCreationManager.create_interface_element(
            {
                "actor_type": constants.LOCATION_INVENTORY_ACTOR_TYPE,
                "description": "location inventory panel",
                "parent_collection": status.location_inventory_collection,
                **base_inventory_info_display_input_dict,
            }
        )
    )

    for inventory_info_display in [
        status.location_inventory_info_display,
        status.mob_inventory_info_display,
    ]:
        inventory_icon = constants.ActorCreationManager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(0, 0),
                "actor_type": inventory_info_display.actor_type,
                "width": scaling.scale_width(constants.inventory_icon_dimensions),
                "height": scaling.scale_height(constants.inventory_icon_dimensions),
                "init_type": constants.ACTOR_ICON,
                "parent_collection": inventory_info_display,
            }
        )

        for current_actor_label_type in [
            constants.INVENTORY_NAME_LABEL,
            constants.INVENTORY_QUANTITY_LABEL,
        ]:
            x_displacement = 0
            input_dict = {
                "minimum_width": scaling.scale_width(10),
                "height": scaling.scale_height(
                    constants.default_notification_font_size + 5
                ),
                "image_id": "misc/default_label.png",
                "init_type": current_actor_label_type,
                "actor_type": inventory_info_display.actor_type,
                "parent_collection": inventory_info_display,
                "member_config": {
                    "order_x_offset": scaling.scale_width(x_displacement)
                },
            }
            constants.ActorCreationManager.create_interface_element(input_dict)

        button_grid = constants.ActorCreationManager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(75, 0),
                "width": scaling.scale_width(0),
                "height": scaling.scale_height(0),
                "init_type": constants.ORDERED_COLLECTION,
                "parent_collection": inventory_info_display,
                "direction": "vertical",
                "separation": scaling.scale_height(5),
                "second_dimension_increment": scaling.scale_width(
                    40
                ),  # Space between columns
                "member_config": {
                    "order_exempt": True,
                },
            }
        )
        index = 0
        if inventory_info_display.actor_type == constants.LOCATION_INVENTORY_ACTOR_TYPE:
            button_definitions = [
                (
                    constants.ANONYMOUS_BUTTON,
                    {
                        "on_click": [
                            (
                                actor_utility.callback,
                                ["displayed_location_inventory", "transfer", 1],
                            ),  # item_icon.transfer(
                        ],
                        "tooltip": ["Orders the selected unit to pick up this item"],
                    },
                    "buttons/item_drop_button.png",
                ),
                (
                    constants.ANONYMOUS_BUTTON,
                    {
                        "on_click": [
                            (
                                actor_utility.callback,
                                ["displayed_location_inventory", "transfer", None],
                            ),  # item_icon.transfer(
                        ],
                        "tooltip": [
                            "Orders the selected unit to pick up all of this item"
                        ],
                    },
                    "buttons/item_drop_all_button.png",
                ),
                (
                    constants.SELL_ITEM_BUTTON,
                    constants.SELL_ITEM_BUTTON,
                    "buttons/item_sell_button.png",
                ),
                (
                    constants.SELL_ALL_ITEM_BUTTON,
                    constants.SELL_ALL_ITEM_BUTTON,
                    "buttons/item_sell_all_button.png",
                ),
                (
                    constants.USE_EQUIPMENT_BUTTON,
                    constants.USE_EQUIPMENT_BUTTON,
                    "buttons/use_equipment_button.png",
                ),
            ]
        elif inventory_info_display.actor_type == constants.MOB_INVENTORY_ACTOR_TYPE:
            button_definitions = [
                (
                    constants.ANONYMOUS_BUTTON,
                    {
                        "on_click": [
                            (
                                actor_utility.callback,
                                ["displayed_mob_inventory", "transfer", 1],
                            ),  # item_icon.transfer(
                        ],
                        "tooltip": ["Orders the selected unit to drop this item"],
                    },
                    "buttons/item_pick_up_button.png",
                ),
                (
                    constants.ANONYMOUS_BUTTON,
                    {
                        "on_click": [
                            (
                                actor_utility.callback,
                                ["displayed_mob_inventory", "transfer", None],
                            ),  # item_icon.transfer(
                        ],
                        "tooltip": [
                            "Orders the selected unit to drop up all of this item"
                        ],
                    },
                    "buttons/item_pick_up_all_button.png",
                ),
                (
                    constants.USE_EQUIPMENT_BUTTON,
                    constants.USE_EQUIPMENT_BUTTON,
                    "buttons/use_equipment_button.png",
                ),
            ]

        for init_type, button_type, image_id in button_definitions:
            constants.ActorCreationManager.create_interface_element(
                {
                    "init_type": init_type,
                    "image_id": image_id,
                    "button_type": button_type,
                    "parent_collection": button_grid,
                    "width": scaling.scale_width(35),
                    "height": scaling.scale_height(35),
                    "member_config": {
                        "second_dimension_coordinate": index % 2,  # 2 columns
                    },
                }
            )
            index += 1
