# Contains all functionality for slave trade suppression

import pygame
import random
from . import action
from ..util import action_utility, text_utility, actor_utility, market_utility
import modules.constants.constants as constants
import modules.constants.status as status


class suppress_slave_trade(action.action):
    """
    Action for battalion in slave traders grid to decrease slave traders strength, eradicating slave trade on reaching 0
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
        constants.transaction_descriptions[self.action_type] = "slave trade suppression"
        self.name = "suppress slave trade"
        self.allow_critical_failures = False

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
        initial_input_dict["keybind_id"] = pygame.K_r
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
        return [
            "Attempts to suppress the slave trade for "
            + str(self.get_price())
            + " money",
            "Can only be done in the slave traders tile",
            "If successful, decreases the strength of the slave traders and increases public opinion",
            "Success chance and risk influenced by the current strength of the slave traders",
            "Costs all remaining movement points, at least 1",
        ]

    def generate_audio(self, subject):
        """
        Description:
            Returns list of audio dicts of sounds to play when notification appears, based on the inputted subject and other current circumstances
        Input:
            string subject: Determines sound dicts
        Output:
            dictionary list: Returns list of sound dicts for inputted subject
        """
        audio = super().generate_audio(subject)
        if subject == "roll_started":
            audio.append("effects/gunfire")
        return audio

    def generate_current_roll_modifier(self):
        """
        Description:
            Calculates and returns the current flat roll modifier for this action - this is always applied, while many modifiers are applied only half the time.
                A positive modifier increases the action's success chance and vice versa
        Input:
            None
        Output:
            int: Returns the current flat roll modifier for this action
        """
        return (
            super().generate_current_roll_modifier()
            + actor_utility.get_slave_traders_strength_modifier()
        )

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
            text += "Are you sure you want to attempt to suppress the slave trade? If successful, your company's public opinion will increase and the strength of the slave traders will decrease, ending the slave trade once strength reaches 0. /n /n"
            text += (
                "The suppression will cost " + str(self.get_price()) + " money. /n /n"
            )
            strength_modifier = actor_utility.get_slave_traders_strength_modifier()
            if strength_modifier < 0:
                text += "The slave traders are flourishing and will provide strong resistance. /n /n"
            elif strength_modifier > 0:
                text += "The slave traders are approaching collapse and will provide weak resistance. /n /n"
            else:
                text += "The slave traders are relatively intact and will provide moderate resistance. /n /n"
        elif subject == "initial":
            text += "The battalion tries to suppress the slave trade. /n /n"
        elif subject == "success":
            self.strength_decrease = random.randrange(1, 4)
            self.public_opinion_increase = random.randrange(1, 4)
            text += (
                "The battalion successfully disrupt certain slave trader operations, decreasing the strength of the slave traders by "
                + str(self.strength_decrease)
                + ". /n /n"
            )
            text += (
                "Word of your company's suppression of the slave trade reaches Europe, increasing public opinion by "
                + str(self.public_opinion_increase)
                + ". /n /n"
            )
        elif subject == "failure":
            text += "The battalion failed to significantly disrupt the operations of the slave traders. /n /n"
        elif subject == "critical_failure":
            text += self.generate_notification_text("failure")
            text += "Across a series of suboptimal engagements, the slave traders manage to destroy the battalion. /n /n"  # critical failures are currently impossible for this action
        elif subject == "critical_success":
            text += self.generate_notification_text("success")
            text += "The major has gained insights into the optimal strategies to intimidating and suppressing slave traders. /n /n"
            text += "The major is now a veteran and will be more successful in future ventures. /n /n"
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
        return super().can_show() and status.displayed_mob.is_battalion

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
            if unit.images[0].current_cell.grid != status.slave_traders_grid:
                text_utility.print_to_screen(
                    "Suppressing the slave trade is only possible in the slave traders tile."
                )
            elif constants.slave_traders_strength <= 0:
                text_utility.print_to_screen(
                    "The slave trade has already been eradicated."
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
                    "message": action_utility.generate_risk_message(self, unit)
                    + self.generate_notification_text("confirmation"),
                    "choices": [
                        {
                            "on_click": (self.middle, []),
                            "tooltip": [
                                "Starts attempting to suppress the slave trade"
                            ],
                            "message": "Start campaign",
                        },
                        {"tooltip": ["Stop " + self.name], "message": "Stop campaign"},
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
        if self.roll_result >= self.current_min_success:  # if campaign succeeded
            actor_utility.set_slave_traders_strength(
                constants.slave_traders_strength - self.strength_decrease
            )
            if constants.slave_traders_strength <= 0:
                constants.slave_traders_strength = 0
                num_freed_slaves = random.randrange(1, 7) + random.randrange(1, 7)
                initial_public_opinion_increase = self.public_opinion_increase
                for i in range(num_freed_slaves):
                    self.public_opinion_increase += 4 + random.randrange(
                        -3, 4
                    )  # 1-7 each
                    market_utility.attempt_worker_upkeep_change("decrease", "African")
                    constants.evil_tracker.change(-2)
                    constants.num_wandering_workers += 1
                text = "The slave trade has been eradicated. /n /n"
                text += (
                    str(num_freed_slaves)
                    + " freed slaves have entered the labor pool, increasing public opinion by "
                    + str(
                        self.public_opinion_increase - initial_public_opinion_increase
                    )
                    + ". /n /n"
                )
                text += "Slaves are no longer able to be purchased, and existing slave units will no longer be automatically replaced. /n /n"
                for current_pmob in status.pmob_list:
                    if current_pmob.is_worker and current_pmob.worker_type == "slave":
                        current_pmob.set_automatically_replace(False)
                constants.notification_manager.display_notification(
                    {
                        "message": text,
                    }
                )
                constants.achievement_manager.achieve("Abolitionist")
            constants.public_opinion_tracker.change(self.public_opinion_increase)
        elif self.roll_result <= self.current_max_crit_fail:
            self.current_unit.die()

        super().complete()

        if constants.slave_traders_strength <= 0:
            status.displayed_tile.select()  # sets music to switch from slave traders music
