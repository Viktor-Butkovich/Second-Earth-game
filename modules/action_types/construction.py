# Contains all functionality for construction

from modules.action_types import action
from modules.util import action_utility, utility, actor_utility, text_utility
from modules.constructs import building_types, item_types
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
        if self.building_type.key == constants.RESOURCE:
            self.attached_resource: item_types.item_type = None
            self.building_name = "resource production facility"
        self.name = "construction"
        self.allow_critical_failures = False

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
        if self.building_type.key == constants.RESOURCE:
            displayed_resource = self.attached_resource
            if not displayed_resource:
                displayed_resource = "consumer goods"
            initial_input_dict["image_id"] = [
                "buttons/default_button_alt2.png",
                {"image_id": f"items/{displayed_resource}.png"},
                {
                    "image_id": "misc/plus.png",
                    "size": 0.5,
                    "x_offset": 0.3,
                    "y_offset": 0.2,
                },
            ]
        elif self.building_type.key == constants.INFRASTRUCTURE:
            initial_input_dict["image_id"] = "buildings/buttons/road.png"
        else:
            initial_input_dict["image_id"] = self.building_type.button_image_id_list
        initial_input_dict["keybind_id"] = self.building_type.build_keybind
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

        if (
            status.displayed_mob
            and not status.displayed_mob.get_location().get_world_handler().is_earth
        ):
            terrain = status.displayed_mob.get_location().terrain
            if not self.building_type.key in [constants.TRAIN]:
                message.append(
                    f"{utility.generate_capitalized_article(self.building_name)}{self.building_name} {utility.conjugate('cost', 1, self.building_name)} {base_cost} money by default, which is multiplied by {constants.terrain_build_cost_multiplier_dict.get(terrain, 1)} when built in {terrain.replace('_', ' ')} terrain"
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

    def can_show(self):
        """
        Description:
            Returns whether a button linked to this action should be drawn - if correct type of unit selected and building not yet present in location
        Input:
            None
        Output:
            boolean: Returns whether a button linked to this action should be drawn
        """
        can_show = super().can_show()
        if can_show and not self.building_type.key in [constants.TRAIN]:
            can_show = (self.building_type.key == constants.INFRASTRUCTURE) or (
                not status.displayed_mob.get_location().has_building(
                    self.building_type.key
                )
            )
        if can_show:
            self.update_info()
        return can_show

    def update_info(self):
        """
        Description:
            Updates this action based on any local circumstances, such as changing resource building built depending on local resource
        Input:
            None
        Output:
            None
        """
        if self.building_type.key == constants.RESOURCE:
            if status.displayed_mob.get_location().resource != self.attached_resource:
                self.attached_resource = None
                self.building_name = "resource production facility"

                displayed_resource = self.attached_resource
                if not displayed_resource:
                    displayed_resource = "consumer goods"
                self.button.image.set_image(
                    [
                        "buttons/default_button_alt2.png",
                        {"image_id": f"items/{displayed_resource}.png"},
                        {
                            "image_id": "misc/plus.png",
                            "size": 0.5,
                            "x_offset": 0.3,
                            "y_offset": 0.2,
                        },
                    ]
                )

        elif self.building_type.key == constants.INFRASTRUCTURE:
            if not status.displayed_mob.get_location().has_building(
                constants.INFRASTRUCTURE
            ):
                if status.displayed_mob.get_location().terrain == "water":
                    new_name = "ferry"
                    new_image = "buildings/buttons/ferry.png"
                else:
                    new_name = "road"
                    new_image = "buildings/buttons/road.png"
            else:
                if status.displayed_mob.get_location().terrain == "water":
                    if not status.displayed_mob.get_location().has_building(
                        constants.INFRASTRUCTURE
                    ):
                        new_name = "ferry"
                        new_image = "buildings/buttons/ferry.png"
                    elif (
                        status.displayed_mob.get_location()
                        .get_building(constants.INFRASTRUCTURE)
                        .infrastructure_type
                        == constants.FERRY
                    ):
                        new_name = "road bridge"
                        new_image = "buildings/buttons/road_bridge.png"
                    else:
                        new_name = "railroad bridge"
                        new_image = "buildings/buttons/railroad_bridge.png"
                else:
                    new_name = "railroad"
                    new_image = "buildings/buttons/railroad.png"
            if new_name != self.building_name:
                self.building_name = new_name
                self.button.image.set_image(new_image)

    def can_build(self, unit):
        """
        Description:
            Calculates and returns the result of any building-specific logic to allow building in the current location
        Input:
            None
        Output:
            boolean: Returns the result of any building-specific logic to allow building in the current location
        """
        return_value = False
        if self.building_type.key == constants.RESOURCE:
            if self.attached_resource:
                return_value = True
            else:
                text_utility.print_to_screen(
                    "This building can only be built in locations with resources."
                )
        elif self.building_type.key == constants.TRAIN_STATION:
            if unit.get_location().has_intact_building(constants.RAILROAD):
                return_value = True
            else:
                text_utility.print_to_screen(
                    "This building can only be built on railroads."
                )
        elif self.building_type.key == constants.TRAIN:
            if unit.get_location().has_intact_building(constants.TRAIN_STATION):
                return_value = True
            else:
                text_utility.print_to_screen(
                    "This building can only be built on train stations"
                )
        else:
            return_value = True
        return return_value

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
            current_building = unit.get_location().get_building(self.building_type.key)
            if not (
                current_building == None
                or (
                    self.building_name in ["railroad", "railroad bridge"]
                    and current_building.is_road
                )
                or (
                    self.building_name == "road bridge"
                    and not (current_building.is_road or current_building.is_railroad)
                )
            ):
                if self.building_type.key == constants.INFRASTRUCTURE:
                    text_utility.print_to_screen(
                        "This location already contains a railroad."
                    )
                else:
                    text_utility.print_to_screen(
                        f"This location already contains a {self.building_name} building."
                    )
            elif unit.get_location().get_world_handler().is_earth:
                text_utility.print_to_screen(
                    "This building can only be built on the planet."
                )
            elif self.can_build(unit):
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
            input_dict = {
                "init_type": self.building_type.key,
                "location": self.current_unit.get_location(),
                "name": self.building_name,
            }

            if not self.building_type.key in [constants.TRAIN]:
                if self.current_unit.get_location().has_building(
                    self.building_type.key
                ):  # if building of same type exists, remove it and replace with new one
                    self.current_unit.get_location().get_building(
                        self.building_type.key
                    ).remove_complete()
            if self.building_type.key == constants.RESOURCE:
                input_dict["image"] = "buildings/resource_building.png"
                input_dict["resource_type"] = self.attached_resource
            elif self.building_type.key == constants.INFRASTRUCTURE:
                building_image_id = None
                if self.building_name == "road":
                    building_image_id = "buildings/infrastructure/road.png"
                elif self.building_name == "railroad":
                    building_image_id = "buildings/infrastructure/railroad.png"
                else:  # bridge image handled in infrastructure initialization to use correct horizontal/vertical version
                    building_image_id = "buildings/infrastructure/road.png"
                input_dict["image"] = building_image_id
                input_dict["infrastructure_type"] = self.building_name.replace(" ", "_")
            elif self.building_type.key == constants.TRAIN:
                image_dict = {
                    "default": "mobs/train/default.png",
                    "crewed": "mobs/train/default.png",
                    "uncrewed": "mobs/train/uncrewed.png",
                }
                input_dict["image_dict"] = image_dict
                input_dict["crew"] = None
            else:
                input_dict["image"] = f"buildings/{self.building_type.key}.png"
            new_building = constants.actor_creation_manager.create(False, input_dict)

            if self.building_type.warehouse_level > 0:
                warehouses = self.current_unit.get_location().get_building(
                    constants.WAREHOUSES
                )  # Create warehouses here
                if warehouses:
                    if warehouses.damaged:
                        warehouses.set_damaged(False)
                    warehouses.upgrade()
                else:
                    input_dict["image"] = "misc/empty.png"
                    input_dict["name"] = "warehouses"
                    input_dict["init_type"] = constants.WAREHOUSES
                    constants.actor_creation_manager.create(False, input_dict)

            actor_utility.calibrate_actor_info_display(
                status.location_info_display, self.current_unit.get_location()
            )  # Update location display to show new building
            if self.building_type.key in [constants.TRAIN]:
                new_building.select()
            else:
                actor_utility.calibrate_actor_info_display(
                    status.mob_info_display, self.current_unit
                )  # Update mob display to show new upgrade possibilities
        super().complete()
