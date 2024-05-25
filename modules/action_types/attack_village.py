# Contains all functionality for village attacks

import pygame
import random
from . import action
from ..util import action_utility, text_utility, actor_utility
import modules.constants.constants as constants
import modules.constants.status as status


class attack_village(action.action):
    """
    Action for battalion to directly attack village
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
        constants.transaction_descriptions[self.action_type] = "village attacks"
        self.name = "attack village"
        self.current_village = None
        self.aggressiveness_modifier = 0
        self.aggressiveness_increase = 0
        self.public_relations_change = 0

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
        initial_input_dict["keybind_id"] = pygame.K_k
        return super().button_setup(initial_input_dict)

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
        self.current_max_crit_fail += 1  # more critical failures than usual

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
            "Attempts to attack a village's population for "
            + str(self.get_price())
            + " money",
            "Can only be done in a village",
            "If successful, kills 1-3 of the village's population",
            "This may decrease public opinion and/or drastically change the village's aggressiveness in either direction"
            "Has higher success chance and lower risk when aggressiveness is low",
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
            text = "Are you sure you want to attempt to attack this village? If successful, 1-3 of the village's population will be killed. /n /n"
            text += "Regardless of success, this may increase the village's aggressiveness and/or decrease public opinion. /n /n"
            text += "The attack will cost " + str(self.get_price()) + " money. /n /n"
            if self.aggressiveness_modifier < 0:
                text += "The villagers are hostile and prepared to resist. /n /n"
            elif self.aggressiveness_modifier > 0:
                text += "The villagers are friendly and may not suspect your harmful intentions. /n /n"
            else:
                text += "The villagers are wary of the battalion and may resist. /n /n"
        elif subject == "initial":
            text += "The battalion tries to kill the natives. /n /n"

        elif subject in ["success", "failure"]:
            self.aggressiveness_increase = 0
            if subject == "success":
                constants.evil_tracker.change(10)
                self.population_decrease = min(
                    random.randrange(1, 4), self.current_village.population
                )
                text += (
                    "The battalion successfully killed "
                    + str(self.population_decrease)
                    + " of the village's population. /n /n"
                )

                if self.current_village.population > self.population_decrease:
                    if random.randrange(1, 7) >= 4:
                        self.aggressiveness_increase = min(
                            9 - self.current_village.aggressiveness,
                            random.randrange(2, 5),
                        )
                        if self.aggressiveness_increase != 0:
                            text += (
                                "The natives of this village have grown vengeful torwards the invaders, increasing their aggressiveness by "
                                + str(self.aggressiveness_increase)
                                + ". /n /n"
                            )
                    else:
                        self.aggressiveness_increase = -1 * min(
                            self.current_village.aggressiveness - 1,
                            random.randrange(2, 5),
                        )
                        if self.aggressiveness_increase != 0:
                            text += (
                                "Targeting subversive elements while sparing collaborators has left the remaining population most agreeable, decreasing their aggressiveness by "
                                + str(-1 * self.aggressiveness_increase)
                                + ". /n /n"
                            )
            else:
                self.population_decrease = 0
                text += "The battalion failed to kill a substantial portion of the village's inhabitants. /n /n"

            self.public_relations_change = -1 * random.randrange(0, 3)
            if (
                abs(self.public_relations_change) > 0
            ):  # reports could be based on the orders even be given - can occur even if corruption occurred
                text += (
                    "Rumors of your company's brutal treatment of the natives reaches Earth, decreasing public opinion by "
                    + str(-1 * self.public_relations_change)
                    + ". /n /n"
                )
        elif subject == "critical_failure":
            text += self.generate_notification_text("failure")
            text += "Angered by your company's brutal attempts at extermination, the natives attack the battalion. /n /n"
        elif subject == "critical_success":
            text += self.generate_notification_text("success")
            text += "With insights into the optimal strategies to intimidate and defeat the African natives, the major is now a veteran and will be more successful in future venture. /n /n"
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
        self.aggressiveness_modifier = (
            self.current_village.get_aggressiveness_modifier()
        )
        roll_modifier += self.aggressiveness_modifier
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
        if subject == "roll_started":
            audio.append("effects/gunfire")
        elif subject == "initial":
            audio.append("effects/bolt_action_1")
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
            and status.displayed_mob.group_type == "battalion"
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
                text_utility.print_to_screen("There is no village to attack.")
            elif self.current_village.population <= 0:
                text_utility.print_to_screen(
                    "This village has no remaining population to be attacked."
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
                            "tooltip": ["Start attempt to attack village"],
                            "message": "Attack village",
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
        new_unit = None
        if self.roll_result >= self.current_min_success:
            self.current_village.change_population(-1 * self.population_decrease)
            if self.current_village.population <= 0:
                constants.achievement_manager.achieve("Naught but Ashes")
        elif self.roll_result <= self.current_max_crit_fail:
            warrior = self.current_village.spawn_warrior()
            warrior.show_images()
            warrior.attack_on_spawn()
        self.current_village.change_aggressiveness(self.aggressiveness_increase)
        constants.public_opinion_tracker.change(self.public_relations_change)
        super().complete()
        if new_unit:
            actor_utility.calibrate_actor_info_display(
                status.mob_info_display, new_unit
            )
