# Contains all functionality for starting trades with villages

import pygame
import math
from . import action
from ..util import action_utility, text_utility, utility, actor_utility
import modules.constants.constants as constants
import modules.constants.status as status


class willing_to_trade(action.action):
    """
    Action for caravan at a village to attempt to start a trade action
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
        constants.transaction_descriptions[self.action_type] = "willing to trade"
        self.name = "trade"
        self.aggressiveness_modifier = 0
        self.trades_remaining = 0
        self.current_village = None
        # don't allow corruption on roll

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
            "Attempts to trade with natives, which allows paying consumer goods to gain random commodities and attract workers",
            "The willingness of a a village to start a trade depends on the village's aggressiveness and the presence of a trading post",
            "Once a trade has begun, a series of transactions will exchange consumer goods to attempt to gain random commodities and/or attract workers",
            "The number of transactions possible depends on the village's population",
            "Can only be done in a village",
            "Costs all remaining movement points, at least 1",
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
            self.current_village = status.displayed_tile.cell.get_building("village")
            text = (
                "Are you sure you want to attempt to trade with the village of "
                + self.current_village.name
                + "? /n /n"
            )
            if not status.displayed_tile.cell.has_intact_building("trading_post"):
                text += "Without an established trading post, the merchant will have difficulty convincing villagers to trade. /n /n"

            if self.aggressiveness_modifier < 0:
                text += "The villagers are hostile and are unlikely to be willing to trade. /n /n"
            elif self.aggressiveness_modifier > 0:
                text += "The villagers are friendly and are likely to be willing to trade. /n /n"
            else:
                text += "The villagers are wary of the merchant but may be willing to trade. /n /n"

            text += (
                "If a trade is started, each transaction will trade 1 of the caravan's "
                + str(self.current_unit.get_inventory("consumer goods"))
                + " consumer goods for items that may or may not be valuable. /n /n"
            )
            text += "Each transaction may also convince villagers to become available for hire as workers. /n /n"

        elif subject == "initial":
            text += "The merchant attempts to convince the villagers to trade. /n /n"
        elif subject == "success":
            self.trades_remaining = math.ceil(self.current_village.population / 3)
            text += (
                "The villagers are willing to trade "
                + str(self.trades_remaining)
                + " time"
                + utility.generate_plural(self.trades_remaining)
            )
            text += " with this caravan. /n /n"
            text += (
                "The caravan has "
                + str(self.current_unit.get_inventory("consumer goods"))
                + " consumer goods available to sell. /n /n"
            )
            # text += 'Click to start trading. /n /n'
        elif subject == "failure":
            text += "The villagers are not willing to trade with the caravan. /n /n"
        elif subject == "critical_failure":
            text += self.generate_notification_text("failure")
            text += "Believing that the merchant seeks to trick them out of their valuables, the villagers attack the caravan. /n /n"
        elif subject == "critical_success":
            text += self.generate_notification_text("success")
            text += "The merchant is now a veteran and will be more successful in future ventures. /n /n"
        return text

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
        roll_modifier = super().generate_current_roll_modifier()
        if not status.displayed_tile.cell.has_intact_building("trading_post"):
            roll_modifier -= 1
        self.aggressiveness_modifier = (
            status.displayed_mob.images[0]
            .current_cell.get_building("village")
            .get_aggressiveness_modifier()
        )
        roll_modifier += self.aggressiveness_modifier
        return roll_modifier

    def can_show(self):
        """
        Description:
            Returns whether a button linked to this action should be drawn
        Input:
            None
        Output:
            boolean: Returns whether a button linked to this action should be drawn
        """
        return (
            super().can_show()
            and status.displayed_mob.is_group
            and status.displayed_mob.group_type == "caravan"
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
            village = unit.images[0].current_cell.get_building("village")
            if village == "none":
                text_utility.print_to_screen("Trading is only possible in a village.")
            elif village.population <= 0:
                text_utility.print_to_screen(
                    "Trading is only possible in a village with population above 0."
                )
            elif unit.get_inventory("consumer goods") == 0:
                text_utility.print_to_screen(
                    "Trading requires at least 1 unit of consumer goods."
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
            actor_utility.select_interface_tab(
                status.mob_tabbed_collection, status.mob_inventory_collection
            )
            status.actions["trade"].trades_remaining = self.trades_remaining
            status.actions["trade"].start(self.current_unit)
        elif self.roll_result <= self.current_max_crit_fail:
            warrior = self.current_village.spawn_warrior()
            warrior.show_images()
            warrior.attack_on_spawn()
        self.current_village = None
