# Contains all functionality for public relations campaigns

import pygame
import random
from . import action
from ..util import action_utility, text_utility
import modules.constants.constants as constants
import modules.constants.status as status


class public_relations_campaign(action.campaign):
    """
    Action for evangelist on Earth to increase public opinion
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
        constants.transaction_descriptions[
            self.action_type
        ] = "public relations campaigning"
        self.name = "public relations campaign"
        self.requirements += [
            constants.OFFICER_PERMISSION,
            constants.EVANGELIST_PERMISSION,
        ]

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
            f"Attempts to spread word of your company's benevolent goals and righteous deeds in Africa for {self.get_price()} money",
            "Can only be done on Earth",
            f"If successful, increases your company's public opinion",
            "Costs all remaining movement points, at least 1",
            f"Each {self.name} attempted doubles the cost of other {self.name}s in the same turn",
        ]

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
            text += "Are you sure you want to start a public relations campaign? /n /nIf successful, your company's public opinion will increase by between 1 and 6 /n /n"
            text += f"The campaign will cost {self.get_price()} money. /n /n"
        elif subject == "initial":
            text += "The evangelist campaigns to increase your company's public opinion with word of your company's benevolent goals and righteous deeds in Africa. /n /n"
        elif subject == "success":
            self.public_relations_change = random.randrange(1, 7)
            text += f"Met with gullible and enthusiastic audiences, the evangelist successfully improves your company's public opinion by {self.public_relations_change}. /n /n"
        elif subject == "failure":
            text += "Whether by a lack of charisma, a reluctant audience, or a doomed cause, the evangelist fails to improve your company's public opinion. /n /n"
        elif subject == "critical_failure":
            text += self.generate_notification_text("failure")
            text += "The evangelist is deeply embarassed by this public failure and decides to abandon your company. /n /n"
        elif subject == "critical_success":
            text += self.generate_notification_text("success")
            text += "With fiery word and true belief in his cause, the evangelist becomes a veteran and will be more successful in future ventures. /n /n"
        return text

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
            if status.earth_grid in unit.grids:
                self.start(unit)
            else:
                text_utility.print_to_screen(
                    self.name.capitalize() + "s are only possible on Earth"
                )

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
                                "Starts a "
                                + self.name
                                + ", possibly improving your company's public opinion"
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
        if self.roll_result >= self.current_min_success:
            constants.public_opinion_tracker.change(self.public_relations_change)
        elif self.roll_result <= self.current_max_crit_fail:
            self.current_unit.die("quit")
        super().complete()
