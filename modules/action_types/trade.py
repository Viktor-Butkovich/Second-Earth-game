# Contains all functionality for transactions with villages

import random
from . import action
from ..util import action_utility, utility, actor_utility, market_utility, scaling
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags


class trade(action.action):
    """
    Action for caravan at a village to conduct a transaction after a successful willing to trade action - may occur multiple times, once per
        transaction
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
        constants.transaction_descriptions[self.action_type] = "trade"
        self.name = "transaction"
        self.trades_remaining = 0
        self.commodity = None
        self.attracted_worker = False
        self.current_village = None
        self.allow_critical_failures = False
        self.allow_critical_successes = False

    def get_default_price(self):
        """
        Description:
            Returns the unmodified price of this action
        Input:
            None
        Output:
            int: Returns the unmodified price of this action
        """
        return 0

    def process_payment(self):
        """
        Description:
            Finds the price of this action and processes the payment - while a trade does not cost any money, the cost of its consumer goods are used
                for minister stealing
        Input:
            None
        Output:
            float: Returns the amount paid
        """
        return constants.item_prices["consumer goods"]

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
        return None

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
            self.current_village = status.displayed_tile.cell.get_building("village")
            text += (
                "The villagers can conduct up to "
                + str(self.trades_remaining)
                + " more transaction"
                + utility.generate_plural(self.trades_remaining)
                + " this turn. /n /n"
            )
            text += (
                "The caravan has "
                + str(self.current_unit.get_inventory("consumer goods"))
                + " consumer goods to sell. /n /n"
            )
            text += "Would you like to trade a unit of consumer goods for items that may or may not be valuable?"
        elif subject == "initial":
            text += "The merchant attempts to find valuable commodities in return for consumer goods. /n /n"
        elif subject in ["success", "failure"]:
            text += "/n"
            if subject == "success":
                self.commodity = random.choice(constants.collectable_resources)
                text += (
                    "The merchant managed to buy a unit of "
                    + self.commodity
                    + " (currently worth "
                    + str(constants.item_prices[self.commodity])
                    + " money). /n /n"
                )
            else:
                text += (
                    "The merchant bought items that turned out to be worthless. /n /n"
                )
            if (
                self.current_village.population
                != self.current_village.available_workers
            ) and random.randrange(
                1, 7
            ) >= 4:  # half chance of getting worker
                self.attracted_worker = True
                text += "Drawn to the Western lifestyle by consumer goods, some of the villagers are now available to be hired by your company. /n /n"
            else:
                self.attracted_worker = False
            if self.trades_remaining >= 1:
                text += (
                    "The villagers are willing to trade "
                    + str(self.trades_remaining - 1)
                    + " more time"
                    + utility.generate_plural(self.trades_remaining - 1)
                    + " with this caravan. /n /n"
                )
                text += (
                    "The merchant has "
                    + str(self.current_unit.get_inventory("consumer goods") - 1)
                    + " more consumer goods to sell /n /n"
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
        return_list = super().generate_attached_interface_elements(subject)
        if subject in ["success", "critical_success", "failure", "critical_failure"]:
            return_list.append(
                action_utility.generate_free_image_input_dict(
                    [
                        {"image_id": "misc/green_circle.png", "size": 0.75},
                        {"image_id": "items/consumer goods.png", "size": 0.75},
                        {
                            "image_id": "misc/minus.png",
                            "size": 0.5,
                            "x_offset": 0.3,
                            "y_offset": 0.2,
                        },
                    ],
                    200,
                    override_input_dict={
                        "member_config": {
                            "order_x_offset": scaling.scale_width(-75),
                            "second_dimension_alignment": "left",
                            "centered": True,
                        }
                    },
                )
            )
        if subject in ["success", "critical_success"]:
            return_list.append(
                action_utility.generate_free_image_input_dict(
                    [
                        {"image_id": "misc/green_circle.png", "size": 0.75},
                        {"image_id": "items/" + self.commodity + ".png", "size": 0.75},
                        {
                            "image_id": "misc/plus.png",
                            "size": 0.5,
                            "x_offset": 0.3,
                            "y_offset": 0.2,
                        },
                    ],
                    200,
                    override_input_dict={
                        "member_config": {
                            "order_x_offset": scaling.scale_width(-75),
                            "second_dimension_alignment": "leftmost",
                            "centered": True,
                        }
                    },
                )
            )
        if (
            subject in ["success", "critical_success", "failure", "critical_failure"]
            and self.attracted_worker
        ):
            return_list.append(
                action_utility.generate_free_image_input_dict(
                    [
                        "buttons/default_button_alt.png",
                        actor_utility.generate_unit_component_image_id(
                            "mobs/African workers/default.png", "left", to_front=True
                        ),
                        actor_utility.generate_unit_component_image_id(
                            "mobs/African workers/default.png", "right", to_front=True
                        ),
                    ],
                    150,
                    override_input_dict={
                        "member_config": {
                            "order_x_offset": scaling.scale_width(-75),
                            "second_dimension_alignment": "leftmost",
                            "centered": True,
                        }
                    },
                )
            )
        return return_list

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
                            "tooltip": ["Start " + self.name],
                            "message": "Start " + self.name,
                        },
                        {
                            "tooltip": ["Stop " + self.name],
                            "message": "Stop " + self.name,
                        },
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
        super().complete()
        if self.roll_result >= self.current_min_success:
            self.current_unit.change_inventory(self.commodity, 1)
        self.current_unit.change_inventory("consumer goods", -1)
        if self.attracted_worker:
            self.current_village.change_available_workers(1)
            market_utility.attempt_worker_upkeep_change("decrease", "African")
        self.trades_remaining -= 1
        if self.trades_remaining == 0:
            constants.notification_manager.display_notification(
                {
                    "message": "The villagers are not willing to trade any more with this caravan this turn. /n /n"
                }
            )
        elif self.current_unit.get_inventory("consumer goods") == 0:
            constants.notification_manager.display_notification(
                {
                    "message": "The caravan does not have any more consumer goods to sell. /n /n"
                }
            )
        else:
            self.start(self.current_unit)
