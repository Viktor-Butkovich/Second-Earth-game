# Contains all functionality for construction

import pygame
from . import action
from ..util import action_utility, utility, actor_utility, text_utility
import modules.constants.constants as constants
import modules.constants.status as status


class construction(action.action):
    """
    Action for construction gang to construct a certain type of building
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
        if self.building_type == "infrastructure":
            self.building_name = "road"  # deal with infrastructure exceptions later
        constants.transaction_descriptions["construction"] = "construction"
        if self.building_type == "trading_post":
            self.requirement = "can_trade"
        elif self.building_type == "mission":
            self.requirement = "can_convert"
        elif self.building_type == "fort":
            self.requirement = "is_battalion"
        else:
            self.requirement = "can_construct"
        if self.building_type == "resource":
            self.attached_resource = "none"
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
        if self.building_type == "resource":
            displayed_resource = self.attached_resource
            if displayed_resource == "none":
                displayed_resource = "consumer goods"
            initial_input_dict["image_id"] = [
                "buttons/default_button_alt2.png",
                {"image_id": "items/" + displayed_resource + ".png"},
                {
                    "image_id": "misc/plus.png",
                    "size": 0.5,
                    "x_offset": 0.3,
                    "y_offset": 0.2,
                },
            ]
        elif self.building_type == "infrastructure":
            initial_input_dict["image_id"] = "buildings/buttons/road.png"
        elif self.building_type == "train":
            initial_input_dict["image_id"] = [
                "buttons/default_button_alt.png",
                {
                    "image_id": "mobs/train/default.png",
                    "size": 0.95,
                    "x_offset": 0,
                    "y_offset": 0,
                    "level": 1,
                },
            ]
        elif self.building_type == "steamboat":
            initial_input_dict["image_id"] = [
                "buttons/default_button_alt.png",
                {
                    "image_id": "mobs/steamboat/default.png",
                    "size": 0.95,
                    "x_offset": 0,
                    "y_offset": 0,
                    "level": 1,
                },
            ]
        else:
            initial_input_dict["image_id"] = (
                "buildings/buttons/" + self.building_type + ".png"
            )
        initial_input_dict["keybind_id"] = {
            "resource": pygame.K_g,
            "port": pygame.K_p,
            "infrastructure": pygame.K_r,
            "train_station": pygame.K_t,
            "trading_post": pygame.K_y,
            "mission": pygame.K_y,
            "fort": pygame.K_v,
            "train": pygame.K_y,
            "steamboat": pygame.K_u,
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
        actor_utility.update_descriptions(self.building_type)
        message.append("Attempts to build a " + self.building_name + " in this tile")
        if self.building_type != "infrastructure":
            message += constants.list_descriptions[self.building_type]
        else:
            message += constants.list_descriptions[self.building_name.replace(" ", "_")]
            if self.building_name == "railroad":
                message += [
                    "Upgrades this tile's road into a railroad, retaining the benefits of a road"
                ]
            elif self.building_name == "railroad bridge":
                message += [
                    "Upgrades this tile's road bridge into a railroad bridge, retaining the benefits of a road bridge"
                ]
            elif self.building_name == "road bridge":
                message += ["Upgrades this tile's ferry into a road bridge"]

        if self.building_type == "trading_post":
            message.append("Can only be built in a village")
        elif self.building_type == "mission":
            message.append("Can only be built in a village")
        elif self.building_type == "train":
            message.append("Can only be assembled at a train station")
        elif self.building_type == "steamboat":
            message.append("Can only be assembled at a river port")

        if self.building_type in ["train_station", "port", "resource"]:
            message.append(
                "Also upgrades this tile's warehouses by 9 inventory capacity, or creates new warehouses if none are present"
            )

        base_cost = actor_utility.get_building_cost(
            None, self.building_type, self.building_name
        )
        cost = actor_utility.get_building_cost(
            status.displayed_mob, self.building_type, self.building_name
        )

        message.append(
            "Attempting to build costs "
            + str(cost)
            + " money and all remaining movement points, at least 1"
        )
        if self.building_type in ["train", "steamboat"]:
            message.append(
                "Unlike buildings, the cost of vehicle assembly is not impacted by local terrain"
            )

        if (
            status.displayed_mob
            and status.strategic_map_grid in status.displayed_mob.grids
        ):
            terrain = status.displayed_mob.images[
                0
            ].current_cell.terrain_handler.terrain
            if not self.building_type in ["train", "steamboat"]:
                message.append(
                    f"{utility.generate_capitalized_article(self.building_name)}{self.building_name} {utility.conjugate('cost', 1, self.building_name)} {base_cost} money by default, which is multiplied by {constants.terrain_build_cost_multiplier_dict[terrain]} when built in {terrain} terrain"
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
        if self.building_name in ["train", "steamboat"]:
            verb = "assemble"
            preterit_verb = "assembled"
            noun = "assembly"
        else:
            verb = "construct"
            preterit_verb = "constructed"
            noun = "construction"

        if subject == "confirmation":
            text += (
                "Are you sure you want to start building a "
                + self.building_name
                + "? /n /n"
            )
            text += (
                "The planning and materials will cost "
                + str(self.get_price())
                + " money. /n /n"
            )
            text += "If successful, a " + self.building_name + " will be built. "
            text += constants.string_descriptions[self.building_type]
        elif subject == "initial":
            text += (
                "The "
                + self.current_unit.name
                + " attempts to "
                + verb
                + " a "
                + self.building_name
                + ". /n /n"
            )
        elif subject == "success":
            text += (
                "The "
                + self.current_unit.name
                + " successfully "
                + preterit_verb
                + " the "
                + self.building_name
                + ". /n /n"
            )
        elif subject == "failure":
            text += (
                "Little progress was made and the "
                + self.current_unit.officer.name
                + " requests more time and funds to complete the "
                + noun
                + " of the "
                + self.building_name
                + ". /n /n"
            )
        elif subject == "critical_success":
            text += self.generate_notification_text("success")
            text += (
                "The "
                + self.current_unit.officer.name
                + " managed the "
                + noun
                + " well enough to become a veteran. /n /n"
            )
        return text

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
                if self.building_type == "mission":
                    if status.current_country.religion == "protestant":
                        sound_id = "effects/onward_christian_soldiers"
                    elif status.current_country.religion == "catholic":
                        sound_id = "effects/ave_maria"
                    audio.append({"sound_id": sound_id, "dampen_music": True})
        return audio

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
            self.current_unit, self.building_type, self.building_name
        )

    def can_show(self):
        """
        Description:
            Returns whether a button linked to this action should be drawn - if correct type of unit selected and building not yet present in tile
        Input:
            None
        Output:
            boolean: Returns whether a button linked to this action should be drawn
        """
        can_show = (
            super().can_show()
            and status.displayed_mob.is_group
            and getattr(status.displayed_mob, self.requirement)
        )
        if can_show and not self.building_type in ["train", "steamboat"]:
            can_show = (self.building_type == "infrastructure") or (
                not status.displayed_mob.images[0].current_cell.has_building(
                    self.building_type
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
        if self.building_type == "resource":
            cell = status.displayed_mob.images[0].current_cell
            if cell.terrain_handler.resource != self.attached_resource:
                if (
                    cell.terrain_handler.resource in constants.collectable_resources
                ):  # if not natives or none
                    self.attached_resource = (
                        cell.terrain_handler.terrain_handler.resource
                    )
                    if self.attached_resource in ["gold", "iron", "copper", "diamond"]:
                        self.building_name = self.attached_resource + " mine"
                    elif self.attached_resource in [
                        "exotic wood",
                        "fruit",
                        "rubber",
                        "coffee",
                    ]:
                        self.building_name = self.attached_resource + " plantation"
                    elif self.attached_resource == "ivory":
                        self.building_name = "ivory camp"
                else:
                    self.attached_resource = "none"
                    self.building_name = "resource production facility"
                displayed_resource = self.attached_resource
                if displayed_resource == "none":
                    displayed_resource = "consumer goods"
                self.button.image.set_image(
                    [
                        "buttons/default_button_alt2.png",
                        {"image_id": "items/" + displayed_resource + ".png"},
                        {
                            "image_id": "misc/plus.png",
                            "size": 0.5,
                            "x_offset": 0.3,
                            "y_offset": 0.2,
                        },
                    ]
                )

        elif self.building_type == "infrastructure":
            cell = status.displayed_mob.images[0].current_cell
            if not cell.has_building("infrastructure"):
                if cell.terrain_handler.terrain == "water" and cell.y > 0:
                    new_name = "ferry"
                    new_image = "buildings/buttons/ferry.png"
                else:
                    new_name = "road"
                    new_image = "buildings/buttons/road.png"
            else:
                if cell.terrain_handler.terrain == "water" and cell.y > 0:
                    if cell.get_building("infrastructure") == "none":
                        new_name = "ferry"
                        new_image = "buildings/buttons/ferry.png"
                    elif (
                        cell.get_building("infrastructure").infrastructure_type
                        == "ferry"
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
            Calculates and returns the result of any building-specific logic to allow building in the current tile
        Input:
            None
        Output:
            boolean: Returns the result of any building-specific logic to allow building in the current tile
        """
        return_value = False
        if self.building_type == "resource":
            if self.attached_resource != "none":
                return_value = True
            else:
                text_utility.print_to_screen(
                    "This building can only be built in tiles with resources."
                )
        elif self.building_type == "port":
            if (
                unit.adjacent_to_water()
                and unit.images[0].current_cell.terrain_handler.terrain != "water"
            ):
                return_value = True
            else:
                text_utility.print_to_screen(
                    "This building can only be built in land tiles adjacent to water."
                )
        elif self.building_type == "train_station":
            if unit.images[0].current_cell.has_intact_building("railroad"):
                return_value = True
            else:
                text_utility.print_to_screen(
                    "This building can only be built on railroads."
                )
        elif self.building_type in ["trading_post", "mission"]:
            if unit.images[0].current_cell.has_building("village"):
                return_value = True
            else:
                text_utility.print_to_screen(
                    "This building can only be built in villages."
                )
        elif self.building_type == "infrastructure":
            if self.building_name in ["road bridge", "railroad bridge", "ferry"]:
                current_cell = unit.images[0].current_cell
                if (
                    current_cell.terrain_handler.terrain == "water"
                    and current_cell.y > 0
                ):  # if in river tile
                    up_cell = current_cell.grid.find_cell(
                        current_cell.x, current_cell.y + 1
                    )
                    down_cell = current_cell.grid.find_cell(
                        current_cell.x, current_cell.y - 1
                    )
                    left_cell = current_cell.grid.find_cell(
                        current_cell.x - 1, current_cell.y
                    )
                    right_cell = current_cell.grid.find_cell(
                        current_cell.x + 1, current_cell.y
                    )
                    if (not (up_cell == None or down_cell == None)) and (
                        not (
                            up_cell.terrain_handler.terrain == "water"
                            or down_cell.terrain_handler.terrain == "water"
                        )
                    ):  # if vertical bridge
                        if (
                            up_cell.terrain_handler.visible
                            and down_cell.terrain_handler.visible
                        ):
                            return_value = True
                    elif (not (left_cell == None or right_cell == None)) and (
                        not (
                            left_cell.terrain_handler.terrain == "water"
                            or right_cell.terrain_handler.terrain == "water"
                        )
                    ):  # if horizontal bridge
                        if (
                            left_cell.terrain_handler.visible
                            and right_cell.terrain_handler.visible
                        ):
                            return_value = True
                if not return_value:
                    text_utility.print_to_screen(
                        "A bridge can only be built on a river tile between 2 discovered land tiles"
                    )
            else:
                return_value = True
        elif self.building_type == "train":
            if unit.images[0].current_cell.has_intact_building("train_station"):
                return_value = True
            else:
                text_utility.print_to_screen(
                    "This building can only be built on train stations"
                )
        elif self.building_type == "steamboat":
            if (
                unit.images[0].current_cell.has_intact_building("port")
                and unit.adjacent_to_river()
            ):
                return_value = True
            else:
                text_utility.print_to_screen(
                    "This building can only be built on river ports"
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
            current_cell = unit.images[0].current_cell
            current_building = current_cell.get_building(self.building_type)
            if not (
                current_building == "none"
                or (
                    self.building_name in ["railroad", "railroad bridge"]
                    and current_building.is_road
                )
                or (
                    self.building_name == "road bridge"
                    and not (current_building.is_road or current_building.is_railroad)
                )
            ):
                if self.building_type == "infrastructure":  # if railroad
                    text_utility.print_to_screen(
                        "This tile already contains a railroad."
                    )
                else:
                    text_utility.print_to_screen(
                        "This tile already contains a "
                        + self.building_type
                        + " building."
                    )
            elif not status.strategic_map_grid in unit.grids:
                text_utility.print_to_screen(
                    "This building can only be built in Africa."
                )
            elif not (
                current_cell.terrain_handler.terrain != "water"
                or self.building_name in ["road bridge", "railroad bridge", "ferry"]
            ):
                text_utility.print_to_screen("This building cannot be built in water.")
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
            input_dict = {
                "coordinates": (self.current_unit.x, self.current_unit.y),
                "grids": self.current_unit.grids,
                "name": self.building_name,
                "modes": self.current_unit.grids[0].modes,
                "init_type": self.building_type,
            }

            if not self.building_type in ["train", "steamboat"]:
                if self.current_unit.images[0].current_cell.has_building(
                    self.building_type
                ):  # if building of same type exists, remove it and replace with new one
                    self.current_unit.images[0].current_cell.get_building(
                        self.building_type
                    ).remove_complete()
            if self.building_type == "resource":
                input_dict["image"] = "buildings/resource_building.png"
                input_dict["resource_type"] = self.attached_resource
            elif self.building_type == "infrastructure":
                building_image_id = "none"
                if self.building_name == "road":
                    building_image_id = "buildings/infrastructure/road.png"
                elif self.building_name == "railroad":
                    building_image_id = "buildings/infrastructure/railroad.png"
                else:  # bridge image handled in infrastructure initialization to use correct horizontal/vertical version
                    building_image_id = "buildings/infrastructure/road.png"
                input_dict["image"] = building_image_id
                input_dict["infrastructure_type"] = self.building_name.replace(" ", "_")
            elif self.building_type == "port":
                input_dict["image"] = "buildings/port.png"
            elif self.building_type == "train_station":
                input_dict["image"] = "buildings/train_station.png"
            elif self.building_type == "trading_post":
                input_dict["image"] = "buildings/trading_post.png"
            elif self.building_type == "mission":
                input_dict["image"] = "buildings/mission.png"
            elif self.building_type == "fort":
                input_dict["image"] = "buildings/fort.png"
            elif self.building_type == "train":
                image_dict = {
                    "default": "mobs/train/default.png",
                    "crewed": "mobs/train/default.png",
                    "uncrewed": "mobs/train/uncrewed.png",
                }
                input_dict["image_dict"] = image_dict
                input_dict["crew"] = "none"
            elif self.building_type == "steamboat":
                image_dict = {
                    "default": "mobs/steamboat/default.png",
                    "crewed": "mobs/steamboat/default.png",
                    "uncrewed": "mobs/steamboat/uncrewed.png",
                }
                input_dict["image_dict"] = image_dict
                input_dict["crew"] = "none"
                input_dict["init_type"] = "boat"
            else:
                input_dict["image"] = "buildings/" + self.building_type + ".png"
            new_building = constants.actor_creation_manager.create(False, input_dict)

            if self.building_type in ["port", "train_station", "resource"]:
                warehouses = self.current_unit.images[0].current_cell.get_building(
                    "warehouses"
                )
                if warehouses != "none":
                    if warehouses.damaged:
                        warehouses.set_damaged(False)
                    warehouses.upgrade()
                else:
                    input_dict["image"] = "misc/empty.png"
                    input_dict["name"] = "warehouses"
                    input_dict["init_type"] = "warehouses"
                    constants.actor_creation_manager.create(False, input_dict)

            actor_utility.calibrate_actor_info_display(
                status.tile_info_display, self.current_unit.images[0].current_cell.tile
            )  # update tile display to show new building
            if self.building_type in ["steamboat", "train"]:
                new_building.select()
            else:
                actor_utility.calibrate_actor_info_display(
                    status.mob_info_display, self.current_unit
                )  # update mob display to show new upgrade possibilities
        super().complete()
