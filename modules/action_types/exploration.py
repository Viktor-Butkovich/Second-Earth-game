# Contains all functionality for exploration

import random
from typing import List
from modules.action_types import action
from modules.util import action_utility, actor_utility
from modules.constants import constants, status, flags


class exploration(action.action):
    """
    Action for expedition to explore a location
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
        constants.transaction_descriptions[self.action_type] = "exploration"
        self.requirements += [
            constants.OFFICER_PERMISSION,
            constants.EXPEDITION_PERMISSION,
        ]
        self.name = "exploration"
        self.x_change = None
        self.y_change = None
        self.direction = None
        self.target_location = None

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
        return

    def pre_start(self, unit):
        """
        Description:
            Prepares for starting an action starting with roll modifiers, setting ongoing action, etc.
        Input:
            pmob unit: Unit selected when the linked button is clicked
        Output:
            None
        """
        super().pre_start(unit)
        self.public_relations_change = 0
        self.initial_movement_points = unit.movement_points

    @property
    def tooltip_text(self) -> List[List[str]]:
        """
        Provides the tooltip for this object
        """
        message = []
        if status.displayed_mob.get_permission(constants.EXPEDITION_PERMISSION):
            # message.append(
            #    "Press to attempt to explore in the " + tooltip_info_dict["direction"]
            # )
            message.append(
                f"Attempting to explore would cost {self.get_price()} money and all remaining movement points, at least 1"
            )
        else:
            # message.append(
            #    f"This unit cannot currently move to the {tooltip_info_dict['direction']}"
            # )
            message.append("This unit cannot move into unexplored areas")
        return message

    def generate_notification_text(self, subject):
        """
        Description:
            Returns text regarding a particular subject for this action
        Input:
            string subject: Determines type of text to return
        Output:
            string: Returns text for the inputted subject
        """
        return ""
        text = super().generate_notification_text(subject)
        if subject == "confirmation":
            text += f"Are you sure you want to spend {self.get_price()} money to attempt an exploration to the {self.direction}?"
        elif subject == "initial":
            current_location = self.current_unit.location
            self.target_location = current_location.world_handler.find_location(
                current_location.x + self.x_change,
                current_location.y + self.y_change,
            )
            text += "The expedition heads towards the " + self.direction + ". /n /n"
            text += f"{constants.FlavorTextManager.generate_flavor_text(self.action_type)} /n /n"
        elif subject == "success":
            text += "/n"
            self.public_relations_change = random.randrange(0, 3)
            if self.target_location.resource:
                text += f"The expedition has discovered a {self.target_location.terrain.replace('_', ' ').upper()} location with a {self.target_location.resource.upper()} resource (currently worth {constants.item_prices[self.target_location.resource]} money each). /n /n"
                self.public_relations_change += 3
            else:
                text += f"The expedition has discovered a {self.target_location.terrain.replace('_', ' ').upper()} location. /n /n"
            if self.public_relations_change > 0:  # Royal/National/Imperial
                text += f"The Geographical Society is pleased with these findings, increasing your public opinion by {self.public_relations_change}. /n /n"
        elif subject == "failure":
            text += "The expedition was not able to explore the location. /n /n"
        elif subject == "critical_failure":
            text += self.generate_notification_text("failure")
            text += "Everyone in the expedition has died. /n /n"
        elif subject == "critical_success":
            text += self.generate_notification_text("success")
            text += "This explorer is now a veteran. /n /n"
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
                    action_utility.generate_location_image_id_list(
                        self.target_location
                    ),
                    250,
                    override_input_dict={
                        "member_config": {
                            "second_dimension_coordinate": -2,
                            "centered": True,
                        }
                    },
                )
            )
        return return_list

    def on_click(self, unit, on_click_info_dict=None):
        """
        Description:
            Used when the player clicks a linked action button - checks if the unit can do the action, proceeding with 'start' if applicable
        Input:
            pmob unit: Unit selected when the linked button is clicked
        Output:
            None
        """
        if super().on_click(unit):
            self.x_change = on_click_info_dict["x_change"]
            self.y_change = on_click_info_dict["y_change"]
            self.direction = on_click_info_dict["direction"]
            self.start(unit)
            current_location = unit.location
            future_location = current_location.world_handler.find_location(
                current_location.x + self.x_change,
                current_location.y + self.y_change,
            )
            constants.ActorCreationManager.create_interface_element(
                input_dict={
                    "init_type": constants.HOSTED_ICON,
                    "location": future_location,
                    "image_id": [
                        {"image_id": f"misc/exploration_x/{self.direction}.png"}
                    ],
                },
            )  # Track this icon and remove it when it should disappear
            return True
        return False

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
            constants.NotificationManager.display_notification(
                {
                    "message": f"{action_utility.generate_risk_message(self, unit)}{self.generate_notification_text('confirmation')}",
                    "choices": [
                        {
                            "on_click": (self.middle, []),
                            "tooltip": [
                                f"Attempt an exploration for {self.get_price()} money"
                            ],
                            "message": "Explore",
                        },
                        {
                            # "on_click": (
                            #    self.current_unit.clear_attached_cell_icons,
                            #    [],
                            # ),
                            "tooltip": ["Cancel"],
                            "message": "Cancel",
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
        if self.roll_result >= self.current_min_success:
            constants.PublicOpinionTracker.change(self.public_relations_change)
            # Modify location's knowledge level
            if self.initial_movement_points >= self.current_unit.get_movement_cost(
                self.x_change, self.y_change
            ):
                self.current_unit.set_movement_points(self.initial_movement_points)
                if self.current_unit.can_move(
                    self.x_change, self.y_change
                ):  # checks for npmobs in explored location
                    self.current_unit.move(self.x_change, self.y_change)
                else:
                    actor_utility.focus_minimap_grids(self.current_unit.location)
                    # Changes minimap to show unexplored location without moving
            else:
                constants.NotificationManager.display_notification(
                    {
                        "message": f"This unit's {self.initial_movement_points} remaining movement points are not enough to move into the newly explored location. /n /n",
                    }
                )
                actor_utility.focus_minimap_grids(self.current_unit.location)
        self.current_unit.set_movement_points(0)
        # self.current_unit.clear_attached_cell_icons()
        super().complete()
        if self.roll_result <= self.current_max_crit_fail:
            self.current_unit.die()
