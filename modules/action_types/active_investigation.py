# Contains all functionality for minister investigations

import random
from typing import Tuple, Dict
from modules.util import text_utility, minister_utility
from modules.action_types import action
from modules.constants import constants, status, flags


class active_investigation(action.campaign):
    """
    Action for prosecutor to investigate another minister for information
    """

    def initial_setup(self):
        """
        Description:
            Completes any configuration required for this action during setup - automatically called during action_setup
        Input:
            None
        Output:
            None
        """
        super().initial_setup()
        constants.transaction_descriptions[self.action_type] = "investigations"
        self.name = "active investigation"
        self.actor_type = constants.PROSECUTION_ACTOR_TYPE
        self.allow_critical_failures = False
        self.allow_critical_successes = False
        self.skip_result_notification = True

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
        initial_input_dict["modes"] = [constants.MINISTERS_MODE]
        return super().button_setup(initial_input_dict)

    def update_tooltip(self):
        """
        Description:
            Sets this tooltip of a button linked to this action
        Input:
            None
        Output:
            None
        """
        if status.displayed_minister:
            return [
                f"Orders your Prosecutor to conduct an active investigation against {status.displayed_minister.name} for {str(self.get_price())} money",
                f"If successful, information may be uncovered regarding this minister's loyalty, skills, or past crimes",
                f"Each {self.name} attempted doubles the cost of other active investigations in the same turn",
            ]
        else:
            return []

    def generate_notification_text(self, subject):
        """
        Description:
            Returns text regarding a particular subject for this action
        Input:
            string subject: Determines type of text to return
        Output:
            string: Returns text for the inputted subject
        """
        text = super().generate_notification_text(subject)
        if subject == "confirmation":
            text += f"Are you sure you want to conduct an active investigation against {status.displayed_minister.name}"
            if status.displayed_minister.current_position:
                text += f", your {status.displayed_minister.current_position.name}"
            text += "? /n /n"
            text += f"This may uncover information regarding {status.displayed_minister.name}'s loyalty, skills, or past crimes. /n /n"
            text += f"The investigation will cost {str(self.get_price())} money. /n /n "
        elif subject == "initial":
            text += f"Minister of Security {minister_utility.get_minister(constants.SECURITY_MINISTER).name} launches an investigation against "
            if status.displayed_minister.current_position:
                text += f"{status.displayed_minister.current_position.name} {status.displayed_minister.name}. /n /n"
            else:
                text += f"{status.displayed_minister.name}. /n /n"
        return text

    def can_show(self):
        """
        Description:
            Returns whether a button linked to this action should be drawn
        Input:
            None
        Output:
            boolean: Returns whether a button linked to this action should be drawn
        """
        return status.displayed_minister and (
            (not status.displayed_minister.current_position)
            or (
                status.displayed_minister.current_position
                and status.displayed_minister.current_position.key
                != constants.SECURITY_MINISTER
            )
        )

    def on_click(self, unit):
        """
        Description:
            Used when the player clicks a linked action button - checks if the unit can do the action, proceeding with 'start' if applicable
        Input:
            pmob unit: Unit selected when the linked button is clicked
        Output:
            None
        """
        if super().on_click(unit):
            if not minister_utility.get_minister(constants.SECURITY_MINISTER):
                text_utility.print_to_screen(
                    "An active investigation requires a Minister of Security to be appointed."
                )
            else:
                self.start(unit)

    def start(self, unit):
        """
        Description:
            Used when the player clicks on the start action button, displays a choice notification that allows the player to start or not
        Input:
            pmob unit: Unit selected when the linked button is clicked
        Output:
            None
        """
        if super().start(unit):
            constants.notification_manager.display_notification(
                {
                    "message": self.generate_notification_text("confirmation"),
                    "transfer_interface_elements": True,
                    "choices": [
                        {
                            "on_click": (self.middle, []),
                            "tooltip": ["Starts an active investigation"],
                            "message": "Start investigation",
                        },
                        {"tooltip": ["Cancel"], "message": "Cancel"},
                    ],
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
        prosecutor = self.current_unit
        target = status.displayed_minister
        previous_values: Dict = {}
        new_values: Dict = {}
        corruption_event: Tuple[float, str] = None
        if self.roll_result >= self.current_min_success:
            categories = [
                minister_type.skill_type
                for key, minister_type in status.minister_types.items()
            ] + ["loyalty", "evidence"]
            for category in categories:
                if (
                    target.current_position
                    and category == target.current_position.skill_type
                ):
                    difficulty = 4
                elif category in ["loyalty", "evidence"]:
                    difficulty = 5
                else:
                    difficulty = 6
                if (
                    random.randrange(1, 7) >= difficulty
                ):  # More common to find rumors for current position or for loyalty than for random skill
                    if category == "evidence":
                        if len(target.undetected_corruption_events) > 0:
                            random_index = random.randrange(
                                0, len(target.undetected_corruption_events)
                            )
                            corruption_event = target.undetected_corruption_events[
                                random_index
                            ]  # random.choice(target.undetected_corruption_events)
                            if (
                                target.check_corruption() or target.check_corruption()
                            ) and (
                                prosecutor.check_corruption()
                                or prosecutor.check_corruption()
                            ):  # conspiracy check with advantage
                                bribe_cost = 5
                                if (
                                    target.personal_savings + target.stolen_money
                                    >= bribe_cost
                                ):
                                    target.personal_savings -= bribe_cost
                                    if (
                                        target.personal_savings < 0
                                    ):  # spend from personal savings, transfer stolen to personal savings if not enough
                                        target.stolen_money += target.personal_savings
                                        target.personal_savings = 0
                                    prosecutor.steal_money(bribe_cost, "bribery")
                                    corruption_event = None
                            else:
                                target.corruption_evidence += 1
                                target.undetected_corruption_events.pop(random_index)
                                minister_utility.calibrate_minister_info_display(target)
                    else:
                        if category == "loyalty":
                            previous_values[
                                category
                            ] = target.apparent_corruption_description
                        else:
                            previous_values[
                                category
                            ] = target.apparent_skill_descriptions[category]
                        target.attempt_rumor(category, prosecutor)
                        if category == "loyalty":
                            if (
                                target.apparent_corruption_description
                                != previous_values[category]
                            ):
                                new_values[
                                    category
                                ] = target.apparent_corruption_description
                        else:
                            if (
                                target.apparent_skill_descriptions[category]
                                != previous_values[category]
                            ):
                                new_values[
                                    category
                                ] = target.apparent_skill_descriptions[category]
        message = ""
        audio = None
        if new_values or corruption_event:
            message = "The investigation resulted in the following discoveries: /n /n"
            for category in new_values:
                message += f"    {category.capitalize()}: {new_values[category]}"
                if previous_values[category] == "unknown":  # if unknown
                    message += " /n"
                else:
                    message += f" (formerly {previous_values[category]}) /n"
            if corruption_event:
                theft_amount, theft_type = corruption_event
                message += f"    Evidence of a previous theft of {theft_amount} money relating to {constants.transaction_descriptions[theft_type]}. /n"
                audio = prosecutor.get_voice_line("evidence")
        else:
            message = "The investigation failed to make any significant discoveries. /n"
        message += " /n"
        constants.notification_manager.display_notification(
            {
                "message": message,
                "notification_type": constants.ACTION_NOTIFICATION,
                "audio": {
                    "sound_id": audio,
                    "radio_effect": prosecutor.get_radio_effect(),
                },
            }
        )
        super().complete()
