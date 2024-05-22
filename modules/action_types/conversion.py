# Contains all functionality for village conversion

import pygame
import random
from . import action
from ..util import action_utility, text_utility
import modules.constants.constants as constants
import modules.constants.status as status


class conversion(action.action):
    """
    Action for missionaries to decrease village aggressiveness
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
        constants.transaction_descriptions[self.action_type] = "religious conversion"
        self.name = "religious conversion"
        self.current_village = None
        self.aggressiveness_modifier = 0
        self.population_modifier = 0

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
        return [
            "Attempts to convert some of this village's inhabitants to Christianity for "
            + str(self.get_price())
            + " money",
            "Can only be done in a village",
            "If successful, reduces the aggressiveness of the village and increases public opinion",
            "Has higher success chance and lower risk when a mission is present",
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
            text += "Are you sure you want to attempt to convert the natives? If successful, the natives will be less aggressive and easier to cooperate with. /n /n"
            text += (
                "The conversion will cost " + str(self.get_price()) + " money. /n /n"
            )
            if not self.current_village.cell.has_intact_building("mission"):
                text += "Without an established mission, the missionaries will have difficulty converting the villagers. /n /n"
            if self.aggressiveness_modifier < 0:
                text += "The villagers are hostile and are unlikely to listen to the teachings of the missionaries. /n /n"
            elif self.aggressiveness_modifier > 0:
                text += "The villagers are friendly and are likely to listen to the teachings of the missionaries. /n /n"
            else:
                text += "The villagers are wary of the missionaries but may be willing to listen to their teachings. /n /n"
            if self.population_modifier < 0:
                text += "The high population of this village will require more effort to convert. /n /n"
            elif self.population_modifier > 0:
                text += "The low population of this village will require less effort to convert. /n /n"
        elif subject == "initial":
            text += "The missionaries try to convert the natives to reduce their aggressiveness. /n /n"
        elif subject == "success":
            if self.current_village.aggressiveness > 1:
                text += "The missionaries have made progress in converting the natives and have reduced their aggressiveness from "
                text += (
                    str(self.current_village.aggressiveness)
                    + " to "
                    + str(self.current_village.aggressiveness - 1)
                    + ". /n /n"
                )
            if (
                self.current_village.aggressiveness <= 7
                and self.current_village.has_cannibals()
            ):
                text += "The villagers have been persuaded to abandon their cannibalistic traditions. /n /n"
            self.public_relations_change = random.randrange(0, 2)
            if self.public_relations_change > 0:
                text += "Working to fulfill your company's proclaimed mission of enlightening the heathens of Africa has increased your public opinion by "
                text += str(self.public_relations_change) + ". /n /n"
        elif subject == "failure":
            text += (
                "The missionaries made little progress in converting the natives. /n /n"
            )
        elif subject == "critical_failure":
            text += self.generate_notification_text("failure")
            text += "Angered by your company's attempts to destroy their spiritual traditions, the natives attack the missionaries. /n /n"
        elif subject == "critical_success":
            text += self.generate_notification_text("success")
            text += "The evangelist has gained insights into converting natives and demonstrating connections between their beliefs and Christianity - this evangelist is now a veteran. /n /n"
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
        if not self.current_village.cell.has_intact_building("mission"):
            roll_modifier -= 1
        self.aggressiveness_modifier = (
            self.current_village.get_aggressiveness_modifier()
        )
        roll_modifier += self.aggressiveness_modifier
        self.population_modifier = self.current_village.get_population_modifier()
        roll_modifier += self.population_modifier
        return roll_modifier

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
                if status.current_country.religion == "protestant":
                    sound_id = "effects/onward_christian_soldiers"
                elif status.current_country.religion == "catholic":
                    sound_id = "effects/ave_maria"
                audio.append({"sound_id": sound_id, "dampen_music": True})
        return audio

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
            and status.displayed_mob.group_type == "missionaries"
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
            current_cell = unit.images[0].current_cell
            self.current_village = current_cell.get_building("village")
            if self.current_village == "none":
                text_utility.print_to_screen(
                    "Converting is only possible in a village."
                )
            elif (
                self.current_village.aggressiveness <= 1
                and not self.current_village.has_cannibals()
            ):
                text_utility.print_to_screen(
                    "This village already has the minimum aggressiveness and cannot be converted."
                )
            elif self.current_village.population <= 0:
                text_utility.print_to_screen(
                    "This village has no population and cannot be converted."
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
                                "Starts converting natives, possibly reducing their aggressiveness"
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
            self.current_village.change_aggressiveness(-1)
            constants.public_opinion_tracker.change(self.public_relations_change)
            if self.current_village.aggressiveness <= 6:
                self.current_village.remove_cannibals()
        super().complete()
        if self.roll_result <= self.current_max_crit_fail:
            warrior = self.current_village.spawn_warrior()
            warrior.show_images()
            warrior.attack_on_spawn()
