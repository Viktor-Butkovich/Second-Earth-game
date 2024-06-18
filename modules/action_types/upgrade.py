# Contains all functionality for building upgrades

import pygame
from . import action
from ..util import actor_utility, action_utility
import modules.constants.constants as constants
import modules.constants.status as status


class upgrade(action.action):
    """
    Action for construction gang to upgrade a particular aspect of a building
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
        self.building_type = kwargs.get("building_type", "none")
        del status.actions[self.action_type]
        status.actions[self.building_type] = self
        self.building_name = self.building_type.replace("_", " ")
        self.requirement = "can_construct"
        self.current_building = "none"
        self.upgraded_building_type = {
            "scale": "resource",
            "efficiency": "resource",
            "warehouse_level": "warehouses",
        }[self.building_type]
        self.name = "upgrade"
        self.allow_critical_failures = False

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
        initial_input_dict["image_id"] = (
            "buttons/actions/upgrade_" + self.building_type + "_button.png"
        )
        initial_input_dict["keybind_id"] = {
            "scale": "none",
            "efficiency": "none",
            "warehouse_level": pygame.K_k,
        }.get(self.building_type, "none")
        return initial_input_dict

    def update_tooltip(self):
        """
        Description:
            Sets this tooltip of a button linked to this action
        Input:
            None
        Output:
            None
        """
        message = []
        unit = status.displayed_mob
        if unit != None:
            self.current_building = unit.images[0].current_cell.get_intact_building(
                self.upgraded_building_type
            )
            actor_utility.update_descriptions(self.building_type)
            if self.building_type == "warehouse_level":
                noun = "tile"
            elif self.building_type in ["efficiency", "scale"]:
                noun = self.current_building.name
            value = getattr(self.current_building, self.building_type)
            message.append(
                f"Attempts to increase this {noun}'s {self.building_name} from {value} to {value + 1} for {self.get_price()} money"
            )
            message += constants.list_descriptions[self.building_type]
            message.append(
                "Unlike new buildings, the cost of building upgrades is not impacted by local terrain"
            )
            message.append(
                "An upgrade's cost is doubled for each previous upgrade to that " + noun
            )
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

        if self.building_type == "warehouse_level":
            noun = "tile"
        elif self.building_type in ["efficiency", "scale"]:
            noun = self.current_building.name

        if subject == "confirmation":
            value = getattr(self.current_building, self.building_type)
            text += f"Are you sure you want to start upgrading this {noun}'s {self.building_name}? /n /n"
            text += f"The planning and materials will cost {self.get_price()} money. Each upgrade to a building doubles the cost of all future upgrades to that building.\n\n"
            text += f"If successful, this {noun}'s {self.building_name} will increase from {value} to {value + 1}. /n /n"
            text += constants.string_descriptions[self.building_type]
        elif subject == "initial":
            text += f"The {self.current_unit.name} attempts to upgrade the {noun}'s {self.building_name}. /n /n"
        elif subject == "success":
            text += f"The {self.current_unit.name} successfully upgraded the {noun}'s {self.building_name}. /n /n"
        elif subject == "failure":
            text += f"Little progress was made and the {self.current_unit.officer.name} requests more time and funds to complete the upgrade. /n /n"
        elif subject == "critical_success":
            text += self.generate_notification_text("success")
            text += f"The {self.current_unit.officer.name} managed the upgrade well enough to become a veteran. /n /n"
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
        if building == "none":
            building = status.displayed_mob.images[0].current_cell.get_intact_building(
                self.upgraded_building_type
            )
        return building.get_upgrade_cost()

    def can_show(self):
        """
        Description:
            Returns whether a button linked to this action should be drawn - if correct type of unit selected and building not yet present in tile
        Input:
            None
        Output:
            boolean: Returns whether a button linked to this action should be drawn
        """
        unit = status.displayed_mob
        building = unit.images[0].current_cell.get_intact_building(
            self.upgraded_building_type
        )
        can_show = (
            super().can_show()
            and unit.is_group
            and getattr(unit, self.requirement)
            and building != "none"
            and building.can_upgrade(self.building_type)
        )
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
            none
        """
        super().pre_start(unit)
        self.current_building = unit.images[0].current_cell.get_intact_building(
            self.upgraded_building_type
        )

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
        if self.roll_result >= self.current_min_success:
            self.current_building.upgrade(self.building_type)
            actor_utility.calibrate_actor_info_display(
                status.tile_info_display, self.current_unit.images[0].current_cell.tile
            )  # update tile display to show building upgrade
            status.minimap_grid.calibrate(self.current_unit.x, self.current_unit.y)
        super().complete()
