# Contains all functionality for building repairs

from __future__ import annotations
from typing import List
from modules.action_types import action
from modules.util import actor_utility, action_utility
from modules.constructs import building_types
from modules.constants import constants, status, flags


class repair(action.action):
    """
    Action for unit to repair a damaged building
    """

    def initial_setup(self, **kwargs):
        """
        Description:
            Completes any configuration required for this action during setup - automatically called during action_setup
        Input:
            None
        Output:
            None
        """
        super().initial_setup(**kwargs)
        self.building_type: building_types.building_type = kwargs.get(
            "building_type", None
        )
        self.requirements: List[str] = status.actions[
            self.building_type.key
        ].requirements
        del status.actions[self.action_type]
        status.actions["repair_" + self.building_type.key] = self
        self.current_building = None

        constants.transaction_descriptions[self.action_type] = "repairs"
        self.name = "repair"
        self.allow_critical_failures = False

    def generate_current_roll_modifier(self):
        """
        Description:
            Calculates and returns the current flat roll modifier for this action - this is always applied, while many modifiers are applied only half the time.
                A positive modifier increases the action's success chance and vice versa
        Input:
            None
        Output:
            int: Returns the current flat roll modifier for this action
        """
        return super().generate_current_roll_modifier() + 1

    def generate_action_type(self):
        """
        Description:
            Determines this action's action type, usually based on the class name
        Input:
            None
        Output:
            None
        """
        return "construction"

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
        initial_input_dict = super().button_setup(initial_input_dict)
        if self.building_type.key != constants.RESOURCE:
            initial_input_dict["image_id"] = [
                f"buildings/buttons/{self.building_type.key}.png",
                "buildings/repair_hammer.png",
            ]
        else:
            initial_input_dict["image_id"] = "buildings/buttons/repair_resource.png"
        initial_input_dict["keybind_id"] = status.actions[
            self.building_type.key
        ].button.keybind_id
        return initial_input_dict

    @property
    def tooltip_text(self) -> List[List[str]]:
        """
        Provides the tooltip for this object
        """
        message = []
        unit = status.displayed_mob
        if unit != None:
            self.current_building = unit.location.get_building(self.building_type.key)
            message.append(
                f"Attempts to repair this location's {self.current_building.name} for {str(self.get_price())} money"
            )
            if self.building_type.key in [
                constants.SPACEPORT,
                constants.TRAIN_STATION,
                constants.RESOURCE,
            ]:
                message.append("If successful, also repairs this location's warehouses")
            message.append("Costs all remaining movement points, at least 1")
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
        text = super().generate_notification_text(subject)
        if subject == "confirmation":
            text += f"Are you sure you want to start repairing this {self.current_building.name}? /n /n"
            text += f"The planning and materials will cost {str(self.get_price())} money (half of the building's initial cost). /n /n"
            text += f"If successful, the {self.current_building.name} will be restored to full functionality. /n /n"
        elif subject == "initial":
            text += f"The {self.current_unit.name} attempts to repair the {self.current_building.name}. /n /n"
        elif subject == "success":
            text += f"The {self.current_unit.name} successfully repaired the {self.current_building.name}. /n /n"
        elif subject == "failure":
            text += f"Little progress was made and the {self.current_unit.officer.name} requests more time and funds to complete the repair. /n /n"
        elif subject == "critical_success":
            text += self.generate_notification_text("success")
            text += f"The {self.current_unit.officer.name} managed the repair well enough to become a veteran. /n /n"
        return text

    def get_price(self):
        """
        Description:
            Calculates and returns the price of this action
        Input:
            None
        Output:
            float: Returns price of this action
        """
        building = self.current_building
        if not building:
            building = status.displayed_mob.location.get_building(
                self.building_type.key
            )
        return building.get_repair_cost()

    def can_show(self):
        """
        Description:
            Returns whether a button linked to this action should be drawn - if correct type of unit selected and building not yet present in location
        Input:
            None
        Output:
            boolean: Returns whether a button linked to this action should be drawn
        """
        building = status.displayed_mob.location.get_building(self.building_type.key)
        can_show = super().can_show() and building and building.damaged
        return can_show

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
            self.start(unit)

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
        self.current_building = unit.location.get_building(self.building_type.key)

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
                    "message": action_utility.generate_risk_message(self, unit)
                    + self.generate_notification_text("confirmation"),
                    "choices": [
                        {
                            "on_click": [(self.middle, [])],
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
        if self.roll_result >= self.current_min_success:
            self.current_building.set_damaged(False)
            actor_utility.calibrate_actor_info_display(
                status.location_info_display, self.current_unit.location
            )  # Update location display to show building repair
        super().complete()
