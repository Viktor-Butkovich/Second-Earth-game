# Contains all functionality for finding an artifact at a rumored location

import random
import pygame
from . import action
from ..util import action_utility, text_utility, actor_utility
import modules.constants.constants as constants
import modules.constants.status as status


class artifact_search(action.action):
    """
    Action for expedition at a possible artifact location to search for the artifact
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
        constants.transaction_descriptions[self.action_type] = "artifact searches"
        self.name = "artifact search"
        self.prize_money = 0
        self.public_opinion_increase = 0
        self.lore_type = ""

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
        initial_input_dict["keybind_id"] = pygame.K_t
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
        if status.current_lore_mission:
            description = "the " + status.current_lore_mission.name
        else:
            description = "a lore mission's artifact"
        return [
            "Attempts to search for "
            + description
            + " at a rumored location for "
            + str(constants.action_prices[self.action_type])
            + " money",
            "Can only be done on a possible location revealed by a rumor",
            "If successful, either finds the artifact and completes the mission, or verifies that it is located elsewhere",
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
            text = (
                "Are you sure you want to attempt to search for the "
                + status.current_lore_mission.name
                + "? "
            )
            text += (
                "If successful, finds the "
                + status.current_lore_mission.name
                + " and completes the mission, or verifies that it is located elsewhere. /n /n"
            )
            text += (
                "The "
                + self.name
                + " will cost "
                + str(constants.action_prices[self.action_type])
                + " money. /n /n"
            )
        elif subject == "initial":
            text += (
                "The expedition tries to locate the "
                + status.current_lore_mission.name
                + ". /n /n"
            )
        elif subject == "success":
            location = status.current_lore_mission.get_possible_artifact_location(
                self.current_unit.x, self.current_unit.y
            )
            if location == status.current_lore_mission.artifact_location:
                text += (
                    "The expedition successfully found the "
                    + status.current_lore_mission.name
                    + "! /n /n"
                )
                text += (
                    "These findings will be reported to the "
                    + status.current_country.government_type_adjective.capitalize()
                    + " Geographical Society as soon as possible. /n /n"
                )
            else:
                text += (
                    "The expedition successfully verified that the "
                    + status.current_lore_mission.name
                    + " is not at this location. /n /n"
                )
        elif subject == "failure":
            text += (
                "The expedition failed to find whether the "
                + status.current_lore_mission.name
                + " is at this location. /n /n"
            )
        elif subject == "critical_failure":
            text += self.generate_notification_text("failure")
            text += "With neither trace nor logical explanation, the entire expedition seems to have vanished. /n /n"
        elif subject == "critical_success":
            text += self.generate_notification_text("success")
            text += "The explorer is now a veteran and will be more successful in future ventures. /n /n"
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
        return (
            super().can_show()
            and status.displayed_mob.is_group
            and status.displayed_mob.group_type == "expedition"
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
            if not status.current_lore_mission:
                text_utility.print_to_screen(
                    "There are no ongoing lore missions for which to find artifacts."
                )
            elif (
                not status.current_lore_mission.has_revealed_possible_artifact_location(
                    unit.x, unit.y
                )
            ):
                text_utility.print_to_screen(
                    "You have not found any rumors indicating that the "
                    + status.current_lore_mission.name
                    + " may be at this location."
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
                            "tooltip": ["Start artifact search"],
                            "message": "Start search",
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
        super().complete()
        if self.roll_result >= self.current_min_success:
            location = status.current_lore_mission.get_possible_artifact_location(
                self.current_unit.x, self.current_unit.y
            )
            if location == status.current_lore_mission.artifact_location:
                self.prize_money = random.randrange(25, 51) * 10
                self.public_opinion_increase = random.randrange(30, 61)
                text = (
                    "The "
                    + status.current_country.government_type_adjective.capitalize()
                    + " Geographical Society awarded "
                    + str(self.prize_money)
                    + " money for finding the "
                    + status.current_lore_mission.name
                    + ". /n /n"
                )
                text += (
                    "Additionally, public opinion has increased by "
                    + str(self.public_opinion_increase)
                    + ". /n /n"
                )
                self.lore_type = status.current_lore_mission.lore_type
                if not self.lore_type in constants.completed_lore_mission_types:
                    text += (
                        "Completing a mission in the "
                        + self.lore_type
                        + " category has given your company a permanent "
                        + constants.lore_types_effect_descriptions_dict[self.lore_type]
                        + ". /n /n"
                    )
                constants.notification_manager.display_notification(
                    {"message": text, "on_reveal": self.complete_lore_mission}
                )
            else:
                location.set_proven_false(True)
            actor_utility.calibrate_actor_info_display(
                status.tile_info_display, status.displayed_tile
            )  # updates tile display without question mark
        elif self.roll_result <= self.current_max_crit_fail:
            self.current_unit.die()

    def complete_lore_mission(self):
        """
        Description:
            Callback function to put into effect the changes from completing a lore mission when the reward notification is revealed
        Input:
            None
        Output:
            None
        """
        if not self.lore_type in constants.completed_lore_mission_types:
            constants.completed_lore_mission_types.append(self.lore_type)
            status.lore_types_effects_dict[self.lore_type].apply()
        constants.completed_lore_missions[
            status.current_lore_mission.name
        ] = self.lore_type
        constants.achievement_manager.check_achievements("It Belongs in a Museum")
        constants.money_tracker.change(self.prize_money, "subsidies")
        constants.public_opinion_tracker.change(self.public_opinion_increase)
        status.current_lore_mission.remove_complete()
