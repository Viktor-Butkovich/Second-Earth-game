# Contains functionality for multi-step notifications

from modules.interface_types.notifications import notification
from modules.util import scaling, action_utility
from modules.constants import constants, status, flags


class action_notification(notification):
    """
    Notification that supports attached interface elements
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'message': string value - Default text for this label, with lines separated by /n
                'ideal_width': int value - Pixel width that this label will try to retain. Each time a word is added to the label, if the word extends past the ideal width, the next line
                    will be started
                'minimum_height': int value - Minimum pixel height of this label. Its height will increase if the contained text would extend past the bottom of the label
                'attached_interface_elements' = None: list value - Interface elements, either in initialized or input_dict form, to add to this notification's
                    sibling ordered collection
                'transfer_interface_elements' = False: boolean value - Whether this notification's sibling ordered collection's member should be transferred
                    to that of the next action notification on removal
                'on_remove' = []: List value - Functions to run after this notification is removed, in format [(function, [args]), ...]
        Output:
            None
        """
        super().__init__(input_dict)
        self.attached_interface_elements = input_dict.get(
            "attached_interface_elements", None
        )
        if self.attached_interface_elements:
            if self.attached_interface_elements:
                self.insert_collection_above(
                    override_input_dict={"coordinates": (self.x, 0)}
                )
                self.parent_collection.can_show_override = self
                self.set_origin(
                    input_dict["coordinates"][0], input_dict["coordinates"][1]
                )

                notification_manager = constants.notification_manager
                column_increment = 120
                collection_y = notification_manager.default_notification_y - (
                    notification_manager.default_notification_height / 2
                )
                self.notification_ordered_collection = (
                    constants.actor_creation_manager.create_interface_element(
                        action_utility.generate_action_ordered_collection_input_dict(
                            scaling.scale_coordinates(
                                -1 * column_increment + (column_increment / 2),
                                collection_y,
                            ),
                            override_input_dict={
                                "parent_collection": self.parent_collection,
                                "second_dimension_increment": scaling.scale_width(
                                    column_increment
                                ),
                                "anchor_coordinate": scaling.scale_height(
                                    notification_manager.default_notification_height / 2
                                ),
                            },
                        )
                    )
                )

                index = 0
                for element_input_dict in self.attached_interface_elements:
                    if type(element_input_dict) == dict:
                        element_input_dict["parent_collection"] = (
                            self.notification_ordered_collection
                        )  # self.parent_collection
                        self.attached_interface_elements[index] = (
                            constants.actor_creation_manager.create_interface_element(
                                element_input_dict
                            )
                        )  # if given input dict, create it and add it to notification
                    else:
                        self.notification_ordered_collection.add_member(
                            element_input_dict,
                            member_config=element_input_dict.transfer_info_dict,
                        )
                    index += 1

        self.transfer_interface_elements = input_dict.get(
            "transfer_interface_elements", False
        )

    def on_click(self):
        """
        Description:
            Controls this notification's behavior when clicked - action notifications recursively remove their automatically generated parent collections and
                transfer sibling ordered collection's interface elements, if applicable
        Input:
            None
        Output:
            None
        """
        transferred_interface_elements = []
        if self.attached_interface_elements and self.transfer_interface_elements:
            transferred_interface_elements = []
            for (
                interface_element
            ) in self.notification_ordered_collection.members.copy():
                for (
                    key
                ) in self.notification_ordered_collection.second_dimension_coordinates:
                    if (
                        interface_element
                        in self.notification_ordered_collection.second_dimension_coordinates[
                            key
                        ]
                    ):
                        second_dimension_coordinate = int(key)
                interface_element.transfer_info_dict = {
                    "x_offset": interface_element.x_offset,
                    "y_offset": interface_element.y_offset,
                    "order_x_offset": interface_element.order_x_offset,
                    "order_y_offset": interface_element.order_y_offset,
                    "second_dimension_coordinate": second_dimension_coordinate,
                    "order_overlap": interface_element
                    in self.notification_ordered_collection.order_overlap_list,
                    "order_exempt": interface_element
                    in self.notification_ordered_collection.order_exempt_list,
                }

                self.notification_ordered_collection.remove_member(interface_element)
                transferred_interface_elements.append(interface_element)

        if self.has_parent_collection:
            self.parent_collection.remove_recursive(complete=False)
        else:
            self.remove()

        constants.notification_manager.handle_next_notification(
            transferred_interface_elements=transferred_interface_elements
        )

    def format_message(self):
        """
        Description:
            Converts this notification's string message to a list of strings, with each string representing a line of text. Each line of text ends when its width exceeds the ideal_width or when a '/n' is encountered in the text. Unlike s
                uperclass, this version removes the automatic prompt to close the notification, as action notifications often require more specific messages not add a prompt to close the notification.
        Input:
            None
        Output:
            None
        """
        super().format_message()
        self.message.pop(-1)


class dice_rolling_notification(action_notification):
    """
    Notification that is removed when a dice roll is completed rather than when clicked
    """

    def update_tooltip(self):
        """
        Description:
            Sets this notification's tooltip to what it should be. Dice rolling notifications tell the user to wait for the dice to finish rolling
        Input:
            None
        Output:
            None
        """
        self.set_tooltip(["Wait for the dice to finish rolling"])

    def on_click(self, die_override=False):
        """
        Description:
            Controls this notification's behavior when clicked. Unlike superclass, dice rolling notifications are not removed when clicked
        Input:
            None
        Output:
            None
        """
        if die_override:
            super().on_click()
        else:
            return

    def remove(self):
        """
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. When a notification is removed, the next notification is shown, if there is one. Dice rolling notifications are
                removed when all dice finish rolling rather than when clicked. Upon removal, dice rolling notifications highlight the chosen die with a color corresponding to the roll's outcome
        Input:
            None
        Output:
            None
        """
        super().remove()
        num_dice = len(status.dice_list)
        if (
            num_dice > 1
        ):  # if there are multiple dice, check if any player-controlled dice are critical successes for promotion
            max_roll = 0
            max_die = 0
            for current_die in status.dice_list:
                if not (
                    not current_die.normal_die
                    and current_die.special_die_type == constants.COLOR_RED
                ):  # do not include enemy dice in this calculation
                    if current_die.roll_result > max_roll:
                        max_roll = current_die.roll_result
                        max_die = current_die
                if (
                    not current_die.normal_die
                ):  # change highlight color of special dice to show that roll is complete
                    if current_die.special_die_type == constants.COLOR_GREEN:
                        current_die.outline_color = current_die.outcome_color_dict[
                            "crit_success"
                        ]
                    elif current_die.special_die_type == constants.COLOR_RED:
                        current_die.outline_color = current_die.outcome_color_dict[
                            "crit_fail"
                        ]

            for current_die in status.dice_list:
                if not (
                    not current_die.normal_die
                    and current_die.special_die_type == constants.COLOR_RED
                ):
                    if not current_die == max_die:
                        current_die.normal_die = True
            max_die.highlighted = True
        elif num_dice:  # if only 1 die, check if it is a crtiical success for promotion
            status.dice_list[0].highlighted = True


class off_tile_exploration_notification(action_notification):
    """
    Notification that shows a tile explored by an expedition in an adjacent tile, focusing on the new tile and returning minimap to original position upon removal
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'message': string value - Default text for this label, with lines separated by /n
                'ideal_width': int value - Pixel width that this label will try to retain. Each time a word is added to the label, if the word extends past the ideal width, the next line
                    will be started
                'minimum_height': int value - Minimum pixel height of this label. Its height will increase if the contained text would extend past the bottom of the label
                'notification_dice': int value - Number of dice allowed to be shown during this notification, allowign the correct set of dice to be shown when multiple notifications queued
        Output:
            None
        """
        cell = input_dict["extra_parameters"]["cell"]
        reveal_cell = input_dict["extra_parameters"].get("reveal_cell", True)
        public_opinion_increase = input_dict["extra_parameters"].get(
            "public_opinion_increase", 0
        )
        money_increase = input_dict["extra_parameters"].get("money_increase", 0)

        if (not "attached_interface_elements" in input_dict) or not input_dict[
            "attached_interface_elements"
        ]:
            input_dict["attached_interface_elements"] = []
        input_dict["attached_interface_elements"].append(
            action_utility.generate_free_image_input_dict(
                action_utility.generate_tile_image_id_list(
                    cell, force_visibility=(reveal_cell or cell.get_location().visible)
                ),
                250,
                override_input_dict={
                    "member_config": {
                        "second_dimension_coordinate": -1,
                        "centered": True,
                    }
                },
            )
        )

        if reveal_cell:
            cell.get_location().set_visibility(True)
        status.minimap_grid.calibrate(cell.x, cell.y)
        super().__init__(input_dict)
        constants.public_opinion_tracker.change(public_opinion_increase)
        constants.money_tracker.change(money_increase)

    def remove(self):
        """
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. When a notification is removed, the next notification is shown, if there is one
        Input:
            None
        Output:
            None
        """
        status.minimap_grid.calibrate(status.displayed_mob.x, status.displayed_mob.y)
        super().remove()
