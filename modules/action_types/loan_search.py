# Contains all functionality for loan searches

import pygame
from . import action
from ..util import action_utility, text_utility, market_utility
import modules.constants.constants as constants
import modules.constants.status as status


class loan_search(action.campaign):
    """
    Action for merchant on Earth to search for a loan offer
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
        constants.transaction_descriptions[self.action_type] = "loan searches"
        self.name = "loan search"
        self.current_proposed_loan = {}
        self.requirements += [
            constants.OFFICER_PERMISSION,
            constants.MERCHANT_PERMISSION,
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
        initial_input_dict["keybind_id"] = pygame.K_l
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
            f"Attempts to find a 100 money loan offer with a favorable interest rate for {self.get_price()} money",
            "Can only be done on Earth",
            "While automatically successful, the offered interest rate may vary",
            f"Costs all remaining movement points, at least 1",
            f"Each {self.name} attempted doubles the cost of other loan searches in the same turn",
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
            text += "Are you sure you want to search for a 100 money loan? A loan will always be available, but the merchant's success will determine the interest rate found. /n /n"
            text += f"The search will cost {self.get_price()} money. /n /n "
        elif subject == "success":
            text += "Loan offer: /n /n"
            text += f"The company will be provided an immediate sum of {self.current_proposed_loan['principal']} money. /n /n"
            text += f"In return, the company will be obligated to pay back {self.current_proposed_loan['interest']} money per turn for 10 turns, for a total of {self.current_proposed_loan['total_paid']} money. /n /n"
            text += "Do you accept this exchange? /n /n"
        elif subject == "critical_success":
            text += self.generate_notification_text("success")
            text += "The merchant negotiated the loan offer well enough to become a veteran. /n /n"
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
        if subject == "dice":
            return_list = (
                self.current_unit.controlling_minister.generate_icon_input_dicts(
                    alignment="left"
                )
            )
        return return_list

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
                text_utility.print_to_screen("Loan searches are only possible on Earth")

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
                    "attached_interface_elements": self.generate_attached_interface_elements(
                        "dice"
                    ),
                    "transfer_interface_elements": True,
                    "choices": [
                        {
                            "on_click": (self.middle, []),
                            "tooltip": [
                                "Starts a search for a low-interest loan offer"
                            ],
                            "message": "Find loan",
                        },
                        {"tooltip": ["Stop search"], "message": "Stop search"},
                    ],
                }
            )

    def middle(self):
        """
        Description:
            Controls the campaign process, determining and displaying its result through a series of notifications
        Input:
            None
        Output:
            None
        """
        self.roll_result = 0
        self.current_unit.set_movement_points(0)

        self.process_payment()

        if self.current_unit.get_permission(constants.VETERAN_PERMISSION):
            num_dice = 2
        else:
            num_dice = 1

        num_attempts = 0
        result = 0
        self.current_proposed_loan["principal"] = 100
        self.current_proposed_loan["interest"] = 10
        while result < 5:
            result = 0
            for i in range(num_dice):
                result = max(
                    self.current_unit.controlling_minister.no_corruption_roll(
                        6, self.action_type
                    ),
                    result,
                )
            num_attempts += 1
            self.current_proposed_loan["interest"] += 1

        if (
            self.current_unit.controlling_minister.check_corruption()
        ):  # no money stolen immediately, but may pay bribe to prosecutor if caught giving false interest amount
            self.current_proposed_loan["interest"] += 2
            self.current_unit.controlling_minister.steal_money(0, self.action_type)
            self.current_proposed_loan["corrupt"] = True
        else:
            self.current_proposed_loan["corrupt"] = False

        self.current_proposed_loan["total_paid"] = (
            self.current_proposed_loan["interest"] * 10
        )  # 12 interest -> 120 paid
        self.current_proposed_loan["interest_percent"] = (
            self.current_proposed_loan["interest"] - 10
        ) * 10  # 12 interest -> 20%

        if (
            (not self.current_unit.get_permission(constants.VETERAN_PERMISSION))
            and result == 6
            and num_attempts == 1
        ):  # promote if rolled 6 on first attempt and not yet veteran
            result = "critical_success"
            self.roll_result = 6
        else:
            result = "success"
            self.roll_result = 5

        constants.notification_manager.display_notification(
            {
                "message": self.generate_notification_text(result),
                "choices": [
                    {
                        "on_click": (self.accept_loan, []),
                        "tooltip": ["Accept"],
                        "message": "Accept",
                    },
                    {"tooltip": ["Decline"], "message": "Decline"},
                ],
                "on_remove": self.complete,
            }
        )

    def accept_loan(self):
        """
        Description:
            Accepts the most recently proposed loan
        Input:
            None
        Output:
            None
        """
        if self.current_proposed_loan["corrupt"]:
            self.current_unit.controlling_minister.steal_money(
                20, "loan_interest", allow_prosecutor_detection=False
            )
        new_loan = market_utility.loan(
            False,
            {
                "principal": self.current_proposed_loan["principal"],
                "interest": self.current_proposed_loan["interest"],
                "remaining_duration": 10,
            },
        )
