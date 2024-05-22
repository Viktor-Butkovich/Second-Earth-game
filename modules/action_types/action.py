# Contains functionality for generic actions

from ..util import (
    main_loop_utility,
    text_utility,
    actor_utility,
    dice_utility,
    action_utility,
    utility,
    minister_utility,
)
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags


class action:
    """
    Generic action class with automatic setup, button creation/functionality, and start/middle/complete logical flow
    """

    def __init__(self, **kwargs):
        """
        Description:
            Initializes this object
        Input:
            None
        Output:
            None
        """
        self.action_type = self.generate_action_type()  # class name
        self.button = None
        self.initial_setup(**kwargs)

    def generate_action_type(self):
        """
        Description:
            Determines this action's action type, usually based on the class name
        Input:
            None
        Output:
            None
        """
        return type(self).__name__

    def initial_setup(self, **kwargs):
        """
        Description:
            Completes any configuration required for this action during setup - automatically called during action_setup
        Input:
            None
        Output:
            None
        """
        status.actions[self.action_type] = self
        self.current_unit = "none"
        self.actor_type = "mob"
        self.placement_type = "label"
        if not self.action_type in constants.action_types:
            constants.action_types.append(self.action_type)
            constants.transaction_types.append(self.action_type)
        constants.action_prices[self.action_type] = self.get_default_price()
        constants.base_action_prices[self.action_type] = self.get_default_price()
        self.roll_lists = []
        self.allow_critical_failures = True
        self.allow_critical_successes = True
        self.skip_result_notification = False

    def button_setup(self, initial_input_dict):
        """
        Description:
            Completes the inputted input_dict with any values required to create a button linked to this action - automatically called during actor display label
                setup
        Input:
            None
        Output:
            None
        """
        initial_input_dict["init_type"] = "action button"
        initial_input_dict["corresponding_action"] = self
        initial_input_dict["image_id"] = (
            "buttons/actions/" + self.action_type + "_button.png"
        )
        return initial_input_dict

    def can_show(self):
        """
        Description:
            Returns whether a button linked to this action should be drawn
        Input:
            None
        Output:
            boolean: Returns whether a button linked to this action should be drawn
        """
        return True

    def on_click(self, unit):
        """
        Description:
            Returns whether the subclass on_click can continue with its logic, printing the relevant explanation if it cannot
        Input:
            pmob unit: Unit selected when the linked button is clicked
        Output:
            boolean: Returns whether the subclass on_click can continue with its logic
        """
        self.current_unit = unit
        if not main_loop_utility.action_possible():
            text_utility.print_to_screen(
                "You are busy and cannot start a " + self.name + "."
            )
            return False
        elif self.actor_type == "mob" and not (unit.movement_points >= 1):
            text_utility.print_to_screen(
                utility.generate_article(self.name).capitalize()
                + " "
                + self.name
                + " requires all remaining movement points, at least 1."
            )
            return False
        elif constants.money < self.get_price():
            text_utility.print_to_screen(
                "You do not have the "
                + str(self.get_price())
                + " money needed for a "
                + self.name
                + "."
            )
            return False
        elif self.actor_type == "mob" and not minister_utility.positions_filled():
            return False
        if self.actor_type == "mob" and unit.sentry_mode:
            unit.set_sentry_mode(False)
        return True

    def get_default_price(self):
        """
        Description:
            Returns the unmodified price of this action
        Input:
            None
        Output:
            int: Returns the unmodified price of this action
        """
        return 5

    def get_price(self):
        """
        Description:
            Calculates and returns the price of this action
        Input:
            None
        Output:
            float: Returns price of this action
        """
        return constants.action_prices[self.action_type]

    def generate_notification_text(self, subject):
        """
        Description:
            Returns text regarding a particular subject for this action
        Input:
            string subject: Determines type of text to return
        Output:
            string: Returns text for the inputted subject
        """
        text = ""
        if subject == "roll_message":
            base_roll_message = "Click to roll. "
            full_roll_message = (
                base_roll_message + str(self.current_min_success) + "+ required "
            )
            officer_name = self.current_unit.name
            if self.actor_type == "mob" and self.current_unit.veteran:
                text += (
                    "The "
                    + officer_name
                    + " can roll twice and pick the higher result. /n /n"
                )
                full_roll_message += "on at least 1 die to succeed."
            else:
                full_roll_message += "to succeed."
            if self.current_min_success >= 1 and self.current_min_success <= 6:
                text += full_roll_message
            else:
                text += base_roll_message
        elif subject == "impossible":
            text += (
                "As a "
                + str(self.current_min_success)
                + "+ would be required to succeed this roll, it is impossible and may not be attempted. /n /n"
            )
        return text

    def generate_attached_interface_elements(self, subject):
        """
        Description:
            Returns list of input dicts of interface elements to attach to a notification regarding a particular subject for this action
        Input:
            string subject: Determines input dicts
        Output:
            dictionary list: Returns list of input dicts for inputted subject
        """
        return_list = []
        if subject == "dice" or subject == "die":
            if subject == "dice":
                return_list += [
                    action_utility.generate_die_input_dict(
                        (0, 0),
                        roll_list[0],
                        self,
                        override_input_dict={"member_config": {"centered": True}},
                    )
                    for roll_list in self.roll_lists
                ]
            else:
                return_list.append(
                    action_utility.generate_die_input_dict(
                        (0, 0),
                        self.roll_lists[0][0],
                        self,
                        override_input_dict={"member_config": {"centered": True}},
                    )
                )
            if self.actor_type == "mob":
                return_list += (
                    self.current_unit.controlling_minister.generate_icon_input_dicts(
                        alignment="leftmost"
                    )
                )
            elif self.actor_type == "minister":
                return_list += self.current_unit.generate_icon_input_dicts(
                    alignment="leftmost"
                )
            elif self.actor_type == "prosecutor":
                return_list += status.displayed_minister.generate_icon_input_dicts(
                    alignment="leftmost"
                )
                return_list += self.current_unit.generate_icon_input_dicts(
                    alignment="left"
                )
        return return_list

    def generate_audio(self, subject):
        """
        Description:
            Returns list of audio dicts of sounds to play when notification appears, based on the inputted subject and other current circumstances
        Input:
            string subject: Determines sound dicts
        Output:
            dictionary list: Returns list of sound dicts for inputted subject
        """
        audio = []
        if subject == "roll_finished":
            if (
                self.roll_result >= self.current_min_crit_success
                and not self.current_unit.veteran
            ):
                audio.append("effects/trumpet")
        return audio

    def generate_current_roll_modifier(self):
        """
        Description:
            Calculates and returns the current flat roll modifier for this action - this is always applied, while many modifiers are applied only half the time
                A positive modifier increases the action's success chance and vice versa
        Input:
            None
        Output:
            int: Returns the current flat roll modifier for this action
        """
        return 0

    def random_unit_modifier(self):
        """
        Description:
            Calculates and returns the current secret roll modifier for this action - each of these is only applied half the time, and as rolls occur
        Input:
            None
        Output:
            int: Returns the current roll modifier
        """
        total_modifier = 0
        if self.actor_type != "prosecutor":
            for equipment_type in self.current_unit.equipment:
                total_modifier += status.equipment_types[equipment_type].apply_modifier(
                    self.action_type
                )
        return total_modifier

    def pre_start(self, unit):
        """
        Description:
            Prepares for starting an action starting with roll modifiers, setting ongoing action, etc.
        Input:
            pmob unit: Unit selected when the linked button is clicked
        Output:
            none
        """
        if self.actor_type == "prosecutor":
            self.current_unit = status.current_ministers["Prosecutor"]
        else:
            self.current_unit = unit
        self.current_roll_modifier = self.generate_current_roll_modifier()
        self.current_min_success = 4  # default_min_success
        self.current_max_crit_fail = 1  # default_max_crit_fail
        self.current_min_crit_success = 6  # default_min_crit_success

        self.current_min_success -= (
            self.current_roll_modifier
        )  # positive modifier reduces number required for succcess, reduces maximum that can be crit fail
        self.current_max_crit_fail -= self.current_roll_modifier
        if self.current_min_success > self.current_min_crit_success:
            self.current_min_crit_success = (
                self.current_min_success
            )  # if 6 is a failure, should not be critical success. However, if 6 is a success, it will always be a critical success
        if not self.allow_critical_failures:
            self.current_max_crit_fail = 0
        if not self.allow_critical_successes:
            self.current_min_crit_success = 7

    def start(self, unit):
        """
        Description:
            Used when the player clicks on the start action button, displays a choice notification that allows the player to start or not
        Input:
            pmob unit: Unit selected when the linked button is clicked
        Output:
            None
        """
        self.pre_start(unit)
        if self.current_min_success > 6:
            constants.notification_manager.display_notification(
                {
                    "message": self.generate_notification_text("confirmation")
                    + self.generate_notification_text("impossible"),
                }
            )
            return False
        else:
            return True

    def process_payment(self):
        """
        Description:
            Finds the price of this action and processes the payment
        Input:
            None
        Output:
            float: Returns the amount paid
        """
        price = self.get_price()
        constants.money_tracker.change(price * -1, self.action_type)
        return price

    def generate_roll_lists(self, results):
        """
        Description:
            Creates and returns a list of roll descriptions for the inputted roll results
        Input:
            int list: List of dice roll results to describe
        Output:
            int/string list list: List of roll result lists containing each roll result and a corresponding description
        """
        return_list = []
        roll_type = self.name.capitalize() + " roll"
        for index in range(len(results)):
            result = results[index]
            return_list.append(
                dice_utility.roll_to_list(
                    6,
                    roll_type,
                    self.current_min_success,
                    self.current_min_crit_success,
                    self.current_max_crit_fail,
                    result,
                )
            )
            roll_type = "second"
        return return_list

    def middle(self):
        """
        Description:
            Controls the campaign process, determining and displaying its result through a series of notifications
        Input:
            None
        Output:
            None
        """
        constants.notification_manager.set_lock(True)
        self.roll_result = 0
        if self.actor_type == "mob":
            self.current_unit.set_movement_points(0)

        price = self.process_payment()

        if self.actor_type == "mob" and self.current_unit.veteran:
            num_dice = 2
        else:
            num_dice = 1

        if self.actor_type == "mob":
            results = self.current_unit.controlling_minister.roll_to_list(
                6,
                self.current_min_success,
                self.current_max_crit_fail,
                price,
                self.action_type,
                num_dice,
            )
        else:
            results = self.current_unit.roll_to_list(
                6,
                self.current_min_success,
                self.current_max_crit_fail,
                price,
                self.action_type,
                num_dice,
            )
        results = [
            max(min(current_result + self.random_unit_modifier(), 6), 1)
            for current_result in results
        ]  # Adds unit-specific modifiers

        self.roll_lists = self.generate_roll_lists(results)

        self.roll_result = 0
        for roll_list in self.roll_lists:
            self.roll_result = max(roll_list[0], self.roll_result)

        text = self.generate_notification_text("initial")
        roll_message = self.generate_notification_text("roll_message")

        constants.notification_manager.display_notification(
            {
                "message": text + roll_message,
                "notification_type": "action",
                "attached_interface_elements": self.generate_attached_interface_elements(
                    "dice"
                ),
                "transfer_interface_elements": True,
                "audio": self.generate_audio("initial"),
            },
            insert_index=0,
        )

        constants.notification_manager.display_notification(
            {
                "message": text + "Rolling... ",
                "notification_type": "roll",
                "transfer_interface_elements": True,
                "audio": self.generate_audio("roll_started"),
            },
            insert_index=1,
        )

        constants.notification_manager.set_lock(
            False
        )  # locks notifications so that corruption messages will occur after the roll notification

        for roll_list in self.roll_lists:
            text += roll_list[1]

        if len(self.roll_lists) > 1:
            result_outcome_dict = {}
            for i in range(1, 7):
                if i <= self.current_max_crit_fail:
                    word = "CRITICAL FAILURE"
                elif i >= self.current_min_crit_success:
                    word = "CRITICAL SUCCESS"
                elif i >= self.current_min_success:
                    word = "SUCCESS"
                else:
                    word = "FAILURE"
                result_outcome_dict[i] = word
            text += (
                "The higher result, "
                + str(self.roll_result)
                + ": "
                + result_outcome_dict[self.roll_result]
                + ", was used. /n /n"
            )
        else:
            text += "/n"
        constants.notification_manager.display_notification(
            {
                "message": text + "Click to remove this notification. /n /n",
                "notification_type": "action",
                "transfer_interface_elements": True,
                "on_remove": self.complete,
                "audio": self.generate_audio("roll_finished"),
            }
        )

        if not self.skip_result_notification:
            if self.roll_result <= self.current_max_crit_fail:
                result = "critical_failure"
            elif (
                self.actor_type == "mob" and not self.current_unit.veteran
            ) and self.roll_result >= self.current_min_crit_success:
                result = "critical_success"
            elif self.roll_result >= self.current_min_success:
                result = "success"
            else:
                result = "failure"

            text += self.generate_notification_text(result)

            constants.notification_manager.display_notification(
                {
                    "message": text + "Click to remove this notification. /n /n",
                    "notification_type": "action",
                    "attached_interface_elements": self.generate_attached_interface_elements(
                        result
                    ),
                }
            )

    def complete(self):
        """
        Description:
            Used when the player finishes rolling, shows the action's results and makes any changes caused by the result
        Input:
            None
        Output:
            None
        """
        if (
            self.actor_type == "mob"
            and self.roll_result >= self.current_min_crit_success
            and not self.current_unit.veteran
        ):
            self.current_unit.promote()
            status.displayed_mob.select()


class campaign(action):
    """
    Action conducted without workers that doubles in price each time it is completed within a turn, resetting at the start of the next turn
    """

    def process_payment(self):
        """
        Description:
            Finds the price of this action and processes the payment, also doubling the campaign cost
        Input:
            None
        Output:
            float: Returns the amount paid
        """
        price = super().process_payment()
        actor_utility.double_action_price(self.action_type)
        return price
