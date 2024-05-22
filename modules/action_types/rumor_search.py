# Contains all functionality for finding artifact rumors

import pygame
from . import action
from ..util import action_utility, text_utility
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags


class rumor_search(action.action):
    """
    Action for expedition at a village to find possible location of an artifact
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
        constants.transaction_descriptions[self.action_type] = "artifact rumor searches"
        self.name = "rumor search"
        self.aggressiveness_modifier = 0

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
        if status.current_lore_mission:
            description = "the location of the " + status.current_lore_mission.name
        else:
            description = "a lore mission artifact's location"
        return [
            "Attempts to search this village for rumors of "
            + description
            + " for "
            + str(constants.action_prices[self.action_type])
            + " money",
            "Can only be done in a village",
            "If successful, reveals the coordinates of a possible location for the current lore mission's artifact",
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
                "Are you sure you want to attempt to search for artifact rumors? If successful, the coordinates of a possible location for the "
                + status.current_lore_mission.name
                + " will be revealed. /n /n"
            )
            text += (
                "The "
                + self.name
                + " will cost "
                + str(constants.action_prices[self.action_type])
                + " money. /n /n"
            )
            if self.aggressiveness_modifier < 0:
                text += "The villagers are hostile and unlikely to cooperate. /n /n"
            elif self.aggressiveness_modifier > 0:
                text += "The villagers are friendly and likely to provide useful information. /n /n"
            else:
                text += "The villagers are wary but may cooperate with sufficient persuasion. /n /n"
        elif subject == "initial":
            text += (
                "The expedition tries to find information regarding the location of the "
                + status.current_lore_mission.name
                + ". /n /n"
            )
        elif subject == "success":
            if status.current_lore_mission.get_num_revealed_possible_artifact_locations() == len(
                status.current_lore_mission.possible_artifact_locations
            ):
                self.current_unit.images[0].current_cell.get_building(
                    "village"
                ).found_rumors = True
                status.current_lore_mission.confirmed_all_locations_revealed = True
                text += (
                    "While the villagers have proven cooperative, the expedition has concluded that all rumors about the "
                    + status.current_lore_mission.name
                    + " have been found. /n /n"
                )
            else:
                text += (
                    "The villagers have proven cooperative, and the expedition found valuable new rumors regarding the location of the "
                    + status.current_lore_mission.name
                    + ". /n /n"
                )
        elif subject == "failure":
            text += "The expedition failed to find any useful information from the natives. /n /n"
        elif subject == "critical_failure":
            text += self.generate_notification_text("failure")
            text += "Angered by the expedition's intrusive attempts to extract information, the natives attack the expedition. /n /n"
        elif subject == "critical_success":
            text += self.generate_notification_text("success")
            text += "The explorer is now a veteran and will be more successful in future ventures. /n /n"
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
            village = unit.images[0].current_cell.get_building("village")
            if not status.current_lore_mission:
                text_utility.print_to_screen(
                    "There are no ongoing lore missions for which to find rumors."
                )
            elif village == "none":
                text_utility.print_to_screen(
                    "Searching for rumors is only possible in a village."
                )
            elif village.population <= 0:
                text_utility.print_to_screen(
                    "This village has no population, so no rumors can be found."
                )
            elif status.current_lore_mission.confirmed_all_locations_revealed:
                text_utility.print_to_screen(
                    "All possible locations of the "
                    + status.current_lore_mission.name
                    + " have already been revealed."
                )
            elif village.found_rumors:
                text_utility.print_to_screen(
                    "This village's rumors regarding the location of the "
                    + status.current_lore_mission.name
                    + " have already been found."
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
                            "tooltip": ["Start rumor search"],
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
        village = self.current_unit.images[0].current_cell.get_building("village")
        location = (
            status.current_lore_mission.get_random_unrevealed_possible_artifact_location()
        )
        if self.roll_result >= self.current_min_success:
            if location != "none":
                coordinates = (location.x, location.y)
                location.set_revealed(True)
                village.found_rumors = True
                text = (
                    "The villagers tell rumors that the "
                    + status.current_lore_mission.name
                    + " may be located at ("
                    + str(coordinates[0])
                    + ", "
                    + str(coordinates[1])
                    + "). /n /n"
                )
                constants.notification_manager.display_notification(
                    {
                        "message": text + "Click to remove this notification. /n /n",
                        "notification_type": "off_tile_exploration",
                        "extra_parameters": {
                            "cell": status.strategic_map_grid.find_cell(
                                coordinates[0], coordinates[1]
                            ),
                            "reveal_cell": False,
                        },
                    }
                )
        elif self.roll_result <= self.current_max_crit_fail:
            warrior = village.spawn_warrior()
            warrior.show_images()
            warrior.attack_on_spawn()
