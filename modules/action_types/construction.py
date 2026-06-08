# Contains all functionality for construction

from __future__ import annotations
from typing import List
from modules.action_types import action
from modules.util import (
    action_utility,
    utility,
    actor_utility,
    text_utility,
)
from modules.constructs import building_types, item_types, zones
from modules.constructs.actor_types.mob_types import pmobs
from modules.constants import constants, status, flags


class construction(action.action):
    """
    Action for construction crew to construct a certain type of building
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
        del status.actions[self.action_type]
        status.actions[self.building_type.key] = self
        self.building_name = self.building_type.name
        if self.building_type.key == constants.INFRASTRUCTURE:
            self.building_name = constants.ROAD
        constants.transaction_descriptions["construction"] = "construction"
        self.requirements += self.building_type.build_requirements
        self.name = "construction"
        self.allow_critical_failures = False
        self.target_zone: zones.zone = None

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
        initial_input_dict["image_id"] = self.building_type.button_image_id_list
        initial_input_dict["keybind_id"] = self.building_type.build_keybind
        return initial_input_dict

    @property
    def tooltip_text(self) -> List[List[str]]:
        """
        Provides the tooltip for this object
        """
        message = []
        message.append(f"Attempts to build a {self.building_name} in this location")
        message += self.building_type.description
        if self.building_type.key == constants.INFRASTRUCTURE:
            if self.building_name == constants.RAILROAD:
                message += [
                    "Upgrades this location's road into a railroad, retaining the benefits of a road"
                ]
            elif self.building_name == "railroad bridge":
                message += [
                    "Upgrades this location's road bridge into a railroad bridge, retaining the benefits of a road bridge"
                ]
            elif self.building_name == "road bridge":
                message += ["Upgrades this location's ferry into a road bridge"]

        if self.building_type.key == constants.TRAIN:
            message.append("Can only be assembled at a train station")

        if self.building_type.warehouse_level > 0:
            message.append(
                f"Also increases this location's warehouse capacity by {9 * self.building_type.warehouse_level} slots"
            )

        base_cost = actor_utility.get_building_cost(
            None, self.building_type.key, self.building_name
        )
        cost = actor_utility.get_building_cost(
            status.displayed_mob, self.building_type.key, self.building_name
        )

        message.append(
            f"Attempting to build costs {cost} money and all remaining movement points, at least 1"
        )
        if self.building_type.key in [constants.TRAIN]:
            message.append(
                "Unlike buildings, the cost of vehicle assembly is not impacted by local terrain"
            )

        if status.displayed_mob and not status.displayed_mob.location.is_earth_location:
            terrain_type = status.displayed_mob.location.terrain_type
            if not self.building_type.key in [constants.TRAIN]:
                message.append(
                    f"{utility.generate_capitalized_article(self.building_name)}{self.building_name} {utility.conjugate('cost', 1, self.building_name)} {base_cost} money by default, which is multiplied by {terrain_type.build_cost_multiplier} when built in {terrain_type.name} terrain"
                )
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
        verb = self.building_type.grammar["verb"]
        preterit_verb = self.building_type.grammar["preterit_verb"]
        noun = self.building_type.grammar["noun"]

        if subject == "confirmation":
            text += (
                f"Are you sure you want to start building a {self.building_name}? /n /n"
            )
            text += (
                f"The planning and materials will cost {self.get_price()} money. /n /n"
            )
            text += "If successful, a " + self.building_name + " will be built. "
            text += self.building_type.get_string_description()
        elif subject == "initial":
            text += f"The {self.current_unit.name} attempts to {verb} a {self.building_name}. /n /n"
        elif subject == "success":
            text += f"The {self.current_unit.name} successfully {preterit_verb} the {self.building_name}. /n /n"
        elif subject == "failure":
            text += f"Little progress was made and the {self.current_unit.officer.name} requests more time and funds to complete the {noun} of the {self.building_name}. /n /n"
        elif subject == "critical_success":
            text += self.generate_notification_text("success")
            text += f"The {self.current_unit.officer.name} managed the {noun} well enough to become a veteran. /n /n"
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
        return actor_utility.get_building_cost(
            self.current_unit, self.building_type.key, self.building_name
        )

    def can_build(self, unit):
        """
        Description:
            Calculates and returns the result of any building-specific logic to allow building in the current location
        Input:
            None
        Output:
            boolean: Returns the result of any building-specific logic to allow building in the current location
        """
        if unit.location.is_abstract_location:
            text_utility.print_to_screen(
                "This building can only be built on the planet."
            )
            return False
        else:
            return True

    def on_click(self, unit: pmobs.pmob) -> None:
        """
        Description:
            Used when the player clicks a linked action button - checks if the unit can do the action, proceeding with 'start' if applicable
        Input:
            pmob unit: Unit selected when the linked button is clicked
        Output:
            None
        """
        if super().on_click(unit) and self.can_build(unit):
            if constants.current_game_mode != constants.LOCATION_MODE:
                status.displayed_location.focus_location()
            constants.SelectorManager.start(
                constants.CONSTRUCTION_SELECTOR,
                config={
                    constants.SELECTOR_CONFIG_CONSTRUCTION_ACTION: self,
                },
            )

    def start(self, unit: pmobs.pmob, target_zone: zones.zone) -> None:
        """
        Description:
            Used when the player clicks on the start action button, displays a choice notification that allows the player to start or not
        Input:
            pmob unit: Unit selected when the linked button is clicked
        Output:
            None
        """
        if super().start(unit):
            self.target_zone = target_zone
            actor_utility.calibrate_actor_info_display(
                status.zone_info_display, self.target_zone
            )
            constants.NotificationManager.display_notification(
                {
                    "message": action_utility.generate_risk_message(self, unit)
                    + self.generate_notification_text("confirmation"),
                    "choices": [
                        {
                            "on_click": [(self.middle, [])],
                            "tooltip": [f"Start {self.name}"],
                            "message": f"Start {self.name}",
                        },
                        {
                            "tooltip": [f"Stop {self.name}"],
                            "message": f"Stop {self.name}",
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
            constants.ActorCreationManager.create(
                from_save=False,
                input_dict={
                    "init_type": self.building_type.key,
                    "zone": self.target_zone,
                    "name": self.building_name,
                },
            )
            status.location_mode_focus.focus_location(force_refresh=True)
            actor_utility.calibrate_actor_info_display(
                status.zone_info_display, self.target_zone
            )
        super().complete()
