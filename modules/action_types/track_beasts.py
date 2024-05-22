# Contains all functionality for beast tracking

import pygame
import random
from . import action
from ..util import action_utility, text_utility, utility
import modules.constants.constants as constants
import modules.constants.status as status


class track_beasts(action.action):
    """
    Action for safari to track hidden beasts
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
        constants.transaction_descriptions[self.action_type] = "beast tracking"
        self.name = "track beasts"

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

    def generate_attached_interface_elements(self, subject):
        """
        Description:
            Returns list of input dicts of interface elements to attach to a notification regarding a particular subject for this action
        Input:
            string subject: Determines input dicts
        Output:
            dictionary list: Returns list of input dicts for inputted subject
        """
        return_list = []
        if subject == "completion":
            return_list = (
                self.current_unit.controlling_minister.generate_icon_input_dicts(
                    alignment="left"
                )
            )
        return return_list

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
            "Attempts to reveal beasts in this tile and adjacent tiles",
            "If successful, beasts in the area will be visible until the end of the turn, allowing them to be targeted by attacks",
            "Cannot reveal beasts in unexplored tiles",
            "Costs 1 movement point",
        ]

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
            and status.displayed_mob.group_type == "safari"
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
            if not status.strategic_map_grid in unit.grids:
                text_utility.print_to_screen("Beasts can only be tracked in Africa.")
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
            self.current_unit = unit
            result = unit.controlling_minister.no_corruption_roll(6)
            if unit.veteran:
                second_result = unit.controlling_minister.no_corruption_roll(6)
                if second_result > result:
                    result = second_result
            beasts_found = []
            ambush_list = []
            if result >= 4:
                for current_beast in status.beast_list:
                    if current_beast.hidden:
                        if (
                            utility.find_grid_distance(unit, current_beast) <= 1
                        ):  # if different by 1 in x or y or at same coordinates
                            beast_cell = unit.grids[0].find_cell(
                                current_beast.x, current_beast.y
                            )
                            if (
                                beast_cell.visible
                            ):  # if beasts's cell has been discovered
                                current_beast.set_hidden(False)
                                beasts_found.append(current_beast)
            text = ""
            if len(beasts_found) == 0:
                text += "Though beasts may still be hiding nearby, the safari was not able to successfully track any beasts. /n /n"
            else:
                for current_beast in beasts_found:
                    if current_beast.x == unit.x and current_beast.y == unit.y:
                        text += (
                            "As the safari starts searching for their quarry, they soon realize that the "
                            + current_beast.name
                            + " had been stalking them the whole time. They have only moments to prepare for the ambush. /n /n"
                        )
                        ambush_list.append(current_beast)
                    elif current_beast.x > unit.x:
                        text += (
                            "The safari finds signs of "
                            + utility.generate_article(current_beast.name)
                            + " "
                            + current_beast.name
                            + " to the east. /n /n"
                        )
                    elif current_beast.x < unit.x:
                        text += (
                            "The safari finds signs of "
                            + utility.generate_article(current_beast.name)
                            + " "
                            + current_beast.name
                            + " to the west. /n /n"
                        )
                    elif current_beast.y > unit.y:
                        text += (
                            "The safari finds signs of "
                            + utility.generate_article(current_beast.name)
                            + " "
                            + current_beast.name
                            + " to the north. /n /n"
                        )
                    elif current_beast.y < unit.y:
                        text += (
                            "The safari finds signs of "
                            + utility.generate_article(current_beast.name)
                            + " "
                            + current_beast.name
                            + " to the south. /n /n"
                        )
                    current_beast.set_hidden(False)
                    current_beast.just_revealed = True
                if result == 6 and not unit.veteran:
                    text += (
                        "This safari's hunter tracked the "
                        + random.choice(beasts_found).name
                        + " well enough to become a veteran. /n /n"
                    )
                    unit.promote()
            constants.notification_manager.display_notification(
                {
                    "message": text,
                    "notification_type": "action",
                    "attached_interface_elements": self.generate_attached_interface_elements(
                        "completion"
                    ),
                }
            )
            unit.change_movement_points(-1)
            for current_beast in ambush_list:
                current_beast.attempt_local_combat()
