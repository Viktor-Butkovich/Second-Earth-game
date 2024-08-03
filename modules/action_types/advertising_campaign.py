# Contains all functionality for advertising campaigns

import pygame
import random
from . import action
from ..util import (
    action_utility,
    text_utility,
    market_utility,
    scaling,
    game_transitions,
)
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags


class advertising_campaign(action.campaign):
    """
    Action for merchant on Earth to increase the price of a particular commodity while lowering a random other
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
        constants.transaction_descriptions[self.action_type] = "advertising"
        self.name = "advertising campaign"
        self.target_commodity = "none"
        self.requirements += [
            constants.OFFICER_PERMISSION,
            constants.MERCHANT_PERMISSION,
        ]

    def pre_start(self, unit):
        """
        Description:
            Prepares for starting an action starting with roll modifiers, setting ongoing action, etc.
        Input:
            pmob unit: Unit selected when the linked button is clicked
        Output:
            none
        """
        super().pre_start(unit)
        self.current_min_success = 5  # alternative to subtracting a roll modifier, which would change the max crit fail

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
            f"Attempts to advertise a chosen commodity and increase its price for {self.get_price()} money",
            f"Can only be done on Earth",
            f"If successful, increases the price of a chosen commodity while randomly decreasing the price of another",
            f"Costs all remaining movement points, at least 1",
            f"Each {self.name} attempted doubles the cost of other advertising campaigns in the same turn",
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
            text += f"Are you sure you want to start an advertising campaign for {self.target_commodity}? If successful, the price of {self.target_commodity} will increase, decreasing the price of another random commodity. /n /n"
            text += f"The campaign will cost {self.get_price()} money. /n /n "
        elif subject == "initial":
            text += f"The merchant attempts to increase public demand for {self.target_commodity}. /n /n"
            (
                advertising_message,
                index,
            ) = constants.flavor_text_manager.generate_substituted_indexed_flavor_text(
                "advertising_campaign", "_", self.target_commodity
            )
            self.success_audio = [
                {
                    "sound_id": f"voices/advertising/messages/{index}",
                    "dampen_music": True,
                    "dampen_time_interval": 0.75,
                    "volume": 1.0,
                },
                {
                    "sound_id": f"voices/advertising/commodities/{self.target_commodity}",
                    "in_sequence": True,
                },
            ]
            text += f"{advertising_message} /n /n"
        elif subject == "success":
            increase = 1
            if self.roll_result >= 6:
                increase += 1
            advertised_original_price = constants.item_prices[self.target_commodity]
            unadvertised_original_price = constants.item_prices[
                self.target_unadvertised_commodity
            ]
            unadvertised_final_price = unadvertised_original_price - increase
            if unadvertised_final_price < 1:
                unadvertised_final_price = 1
            text += f"The merchant successfully advertised for {self.target_commodity}, increasing its price from {advertised_original_price} to "
            text += f"{advertised_original_price + increase}. The price of {self.target_unadvertised_commodity} decreased from {unadvertised_original_price} to {unadvertised_final_price}. /n /n"
            if self.roll_result >= 6:
                text += f"The advertising campaign was so popular that the value of {self.target_commodity} increased by 2 instead of 1. /n /n"
        elif subject == "critical_success":
            text += self.generate_notification_text("success")
            text += "This merchant is now a veteran. /n /n"
        elif subject == "failure":
            text += f"The merchant failed to increase the popularity of {self.target_commodity}. /n /n"
        elif subject == "critical_failure":
            text += self.generate_notification_text("failure")
            text += "Embarassed by this utter failure, the merchant quits your company. /n /n"
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
        if subject in ["success", "critical_success"]:
            return_list.append(
                action_utility.generate_free_image_input_dict(
                    [
                        {"image_id": "misc/green_circle.png", "size": 0.75},
                        {
                            "image_id": "items/"
                            + self.target_unadvertised_commodity
                            + ".png",
                            "size": 0.75,
                        },
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
            return_list.append(
                action_utility.generate_free_image_input_dict(
                    [
                        {"image_id": "misc/green_circle.png", "size": 0.75},
                        {
                            "image_id": "items/" + self.target_commodity + ".png",
                            "size": 0.75,
                        },
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
        audio = super().generate_audio(subject)
        if subject == "roll_finished":
            if self.roll_result >= self.current_min_success:
                audio += self.success_audio
        return audio

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
                if not constants.current_game_mode == "earth":
                    game_transitions.set_game_mode("earth")
                    unit.select()
                text_utility.print_to_screen(
                    "Select a commodity to advertise, or click elsewhere to cancel: "
                )
                flags.choosing_advertised_commodity = True
            else:
                text_utility.print_to_screen(
                    self.name.capitalize() + "s are only possible on Earth"
                )

    def start(self, unit, commodity):
        """
        Description:
            Used when the player clicks on the start action button, displays a choice notification that allows the player to start or not
        Input:
            pmob unit: Unit selected when the linked button is clicked
        Output:
            None
        """
        flags.choosing_advertised_commodity = False
        self.target_commodity = commodity
        self.target_unadvertised_commodity = random.choice(constants.commodity_types)
        while (
            (not self.target_unadvertised_commodity in constants.collectable_resources)
            or self.target_unadvertised_commodity == self.target_commodity
            or constants.item_prices[self.target_unadvertised_commodity] == 1
        ):
            self.target_unadvertised_commodity = random.choice(
                constants.commodity_types
            )

        if super().start(unit):
            constants.notification_manager.display_notification(
                {
                    "message": action_utility.generate_risk_message(self, unit)
                    + self.generate_notification_text("confirmation"),
                    "choices": [
                        {
                            "on_click": (self.middle, []),
                            "tooltip": [
                                "Starts an "
                                + self.name
                                + " for "
                                + self.target_commodity
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
            increase = 1
            if self.roll_result >= self.current_min_crit_success:
                increase += 1
            market_utility.change_price(self.target_commodity, increase)
            market_utility.change_price(
                self.target_unadvertised_commodity, -1 * increase
            )
        elif self.roll_result <= self.current_max_crit_fail:
            self.current_unit.die("quit")
        super().complete()
