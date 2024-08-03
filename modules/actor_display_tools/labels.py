# Contains functionality for actor display labels

import pygame

from ..interface_types.labels import label
from ..util import utility, scaling, actor_utility
import modules.constants.constants as constants
import modules.constants.status as status


class actor_display_label(label):
    """
    Label that changes its text to match the information of selected mobs or tiles
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'minimum_width': int value - Minimum pixel width of this label. Its width will increase if the contained text would extend past the edge of the label
                'actor_label_type': string value - Type of actor information shown
                'actor_type': string value - Type of actor to display the information of, like 'mob', 'tile', or 'minister'
        Output:
            None
        """
        self.attached_buttons = []
        self.has_label_collection = False
        self.actor = "none"
        self.actor_label_type = input_dict[
            "actor_label_type"
        ]  # name, terrain, resource, etc
        self.actor_type = input_dict[
            "actor_type"
        ]  # mob or tile, none if does not scale with shown labels, like tooltip labels
        self.image_y_displacement = 0
        input_dict["message"] = ""
        super().__init__(input_dict)
        # all labels in a certain ordered label list will be placed in order on the side of the screen when the correct type of actor/minister is selected
        s_increment = scaling.scale_width(6)
        m_increment = scaling.scale_width(9)
        l_increment = scaling.scale_width(30)

        s_size = self.height + s_increment
        m_size = self.height + m_increment
        l_size = self.height + l_increment
        input_dict = {
            "coordinates": (self.x, self.y),
            "width": m_size,
            "height": m_size,
            "modes": self.modes,
            "attached_label": self,
        }
        if self.actor_label_type == "name":
            self.message_start = "Name: "

            input_dict["init_type"] = "embark vehicle button"
            input_dict["image_id"] = "buttons/embark_ship_button.png"
            input_dict["keybind_id"] = pygame.K_b
            input_dict["vehicle_type"] = "ship"
            self.add_attached_button(input_dict)

            input_dict["init_type"] = "embark vehicle button"
            input_dict["image_id"] = "buttons/embark_train_button.png"
            input_dict["keybind_id"] = pygame.K_b
            input_dict["vehicle_type"] = "train"
            self.add_attached_button(input_dict)

            input_dict["init_type"] = "work crew to building button"
            input_dict["image_id"] = "buttons/work_crew_to_building_button.png"
            input_dict["keybind_id"] = pygame.K_g
            input_dict["building_type"] = "resource"
            self.add_attached_button(input_dict)

            input_dict["init_type"] = "switch theatre button"
            input_dict["image_id"] = "buttons/switch_theatre_button.png"
            input_dict["keybind_id"] = pygame.K_g
            input_dict["width"], input_dict["height"] = (m_size, m_size)
            self.add_attached_button(input_dict)

            del input_dict["keybind_id"]
            input_dict["image_id"] = [
                "buttons/default_button_alt2.png",
                {"image_id": "misc/green_circle.png", "size": 0.75},
                {"image_id": "items/consumer goods.png", "size": 0.75},
            ]
            input_dict["init_type"] = "toggle button"
            input_dict["toggle_variable"] = "wait_until_full"
            self.add_attached_button(input_dict)

            input_dict = {
                "coordinates": (self.x, self.y),
                "width": m_size,
                "height": m_size,
                "modes": self.modes,
                "attached_label": self,
            }
            input_dict["init_type"] = "automatic route button"
            input_dict["image_id"] = "buttons/clear_automatic_route_button.png"
            input_dict["button_type"] = "clear automatic route"
            self.add_attached_button(input_dict)

            input_dict["image_id"] = "buttons/draw_automatic_route_button.png"
            input_dict["button_type"] = "draw automatic route"
            self.add_attached_button(input_dict)

            input_dict["image_id"] = "buttons/execute_single_movement_route_button.png"
            input_dict["button_type"] = "execute automatic route"
            self.add_attached_button(input_dict)

            for action_type in status.actions:
                if (
                    status.actions[action_type].actor_type in ["mob", "tile"]
                    and status.actions[action_type].placement_type == "label"
                ):
                    button_input_dict = status.actions[action_type].button_setup(
                        input_dict.copy()
                    )
                    if button_input_dict:
                        self.add_attached_button(button_input_dict)

        elif self.actor_label_type == "movement":
            self.message_start = "Movement points: "

            input_dict["init_type"] = "enable automatic replacement button"
            input_dict["target_type"] = "unit"
            input_dict[
                "image_id"
            ] = "buttons/enable_automatic_replacement_officer_button.png"
            self.add_attached_button(input_dict)

            input_dict["init_type"] = "disable automatic replacement button"
            input_dict[
                "image_id"
            ] = "buttons/disable_automatic_replacement_officer_button.png"
            self.add_attached_button(input_dict)

            input_dict["init_type"] = "enable automatic replacement button"
            input_dict[
                "image_id"
            ] = "buttons/enable_automatic_replacement_worker_button.png"
            input_dict["target_type"] = "worker"
            self.add_attached_button(input_dict)

            input_dict["init_type"] = "disable automatic replacement button"
            input_dict[
                "image_id"
            ] = "buttons/disable_automatic_replacement_worker_button.png"
            self.add_attached_button(input_dict)

            input_dict["init_type"] = "enable automatic replacement button"
            input_dict[
                "image_id"
            ] = "buttons/enable_automatic_replacement_officer_button.png"
            input_dict["target_type"] = "officer"
            self.add_attached_button(input_dict)

            input_dict["init_type"] = "disable automatic replacement button"
            input_dict[
                "image_id"
            ] = "buttons/disable_automatic_replacement_officer_button.png"
            self.add_attached_button(input_dict)

            del input_dict["target_type"]

            input_dict["init_type"] = "enable sentry mode button"
            input_dict["image_id"] = "buttons/enable_sentry_mode_button.png"
            self.add_attached_button(input_dict)

            input_dict["init_type"] = "disable sentry mode button"
            input_dict["image_id"] = "buttons/disable_sentry_mode_button.png"
            self.add_attached_button(input_dict)

            input_dict["init_type"] = "end unit turn button"
            input_dict["image_id"] = "buttons/end_unit_turn_button.png"
            input_dict["keybind_id"] = pygame.K_f
            self.add_attached_button(input_dict)
            del input_dict["keybind_id"]

        elif self.actor_label_type == "building work crews":
            self.message_start = "Work crews: "
            input_dict["init_type"] = "cycle work crews button"
            input_dict["image_id"] = "buttons/cycle_passengers_down_button.png"
            self.add_attached_button(input_dict)

        elif self.actor_label_type == "current building work crew":
            self.message_start = ""
            self.attached_building = "none"
            input_dict["init_type"] = "remove work crew button"
            input_dict["image_id"] = "buttons/remove_work_crew_button.png"
            input_dict["building_type"] = "resource"
            self.add_attached_button(input_dict)

        elif self.actor_label_type == "passengers":
            self.message_start = "Passengers: "
            input_dict["init_type"] = "cycle passengers button"
            input_dict["image_id"] = "buttons/cycle_passengers_down_button.png"
            input_dict["keybind_id"] = pygame.K_4
            self.add_attached_button(input_dict)

            input_dict["init_type"] = "embark all passengers button"
            input_dict["image_id"] = "buttons/embark_ship_button.png"
            input_dict["keybind_id"] = pygame.K_z
            self.add_attached_button(input_dict)

            input_dict["init_type"] = "disembark all passengers button"
            input_dict["image_id"] = "buttons/disembark_ship_button.png"
            input_dict["keybind_id"] = pygame.K_x
            self.add_attached_button(input_dict)

        elif self.actor_label_type == "current passenger":
            self.message_start = ""
            input_dict["keybind_id"] = "none"
            if self.list_index == 0:
                input_dict["keybind_id"] = pygame.K_F1
            elif self.list_index == 1:
                input_dict["keybind_id"] = pygame.K_F2
            elif self.list_index == 2:
                input_dict["keybind_id"] = pygame.K_F3
            input_dict["init_type"] = "disembark vehicle button"
            input_dict["image_id"] = "buttons/disembark_ship_button.png"
            self.add_attached_button(input_dict)

        elif self.actor_label_type == "tooltip":
            self.message_start = ""

        elif self.actor_label_type in [
            "mob inventory capacity",
            "tile inventory capacity",
        ]:
            self.message_start = "Inventory: "
            input_dict["width"], input_dict["height"] = (m_size, m_size)
            if self.actor_label_type == "tile inventory capacity":
                input_dict["init_type"] = "pick up each commodity button"
                input_dict["image_id"] = "buttons/commodity_pick_up_each_button.png"
                self.add_attached_button(input_dict)

                input_dict["init_type"] = "sell each commodity button"
                input_dict["image_id"] = "buttons/commodity_sell_each_button.png"
                self.add_attached_button(input_dict)

            else:
                input_dict["init_type"] = "drop each commodity button"
                input_dict["image_id"] = "buttons/commodity_drop_each_button.png"
                self.add_attached_button(input_dict)

            if self.actor_label_type == "mob inventory capacity":
                input_dict["init_type"] = "remove equipment button"
                for equipment_type in status.equipment_types:
                    input_dict["equipment_type"] = equipment_type
                    input_dict["image_id"] = [
                        "buttons/default_button.png",
                        "misc/green_circle.png",
                        "items/" + equipment_type + ".png",
                    ]
                    self.add_attached_button(input_dict)

        elif self.actor_label_type == "terrain":
            self.message_start = "Terrain: "

        elif self.actor_label_type == "minister":
            self.message_start = "Minister: "
            input_dict["width"], input_dict["height"] = (m_size, m_size)

            attached_minister_position_image = (
                constants.actor_creation_manager.create_interface_element(
                    {
                        "coordinates": (self.x - self.height - m_increment, self.y),
                        "width": self.height + m_increment,
                        "height": self.height + m_increment,
                        "modes": self.modes,
                        "minister_type": "none",
                        "attached_label": self,
                        "init_type": "minister type image",
                        "minister_image_type": "portrait",
                        "parent_collection": self.insert_collection_above(),
                        "member_config": {
                            "x_offset": -1 * (self.height + m_increment),
                            "y_offset": -0.5 * m_increment,
                        },
                    }
                )
            )
            attached_minister_portrait_image = constants.actor_creation_manager.create_interface_element(
                {
                    "width": self.height + m_increment,
                    "height": self.height + m_increment,
                    "init_type": "minister portrait image",
                    "minister_type": "none",
                    "parent_collection": attached_minister_position_image.parent_collection,
                    "member_config": {
                        "x_offset": -1 * (self.height + m_increment),
                        "y_offset": -0.5 * m_increment,
                    },
                }
            )

            self.parent_collection.can_show_override = self  # parent collection is considered showing when this label can show, allowing ordered collection to work correctly
            self.image_y_displacement = 5

        elif self.actor_label_type in ["minister_name"]:
            self.message_start = "Name: "
            if self.actor_label_type == "minister_name":
                input_dict["width"], input_dict["height"] = (s_size, s_size)
                for action_type in status.actions:
                    if (
                        status.actions[action_type].actor_type
                        in ["minister", "prosecutor"]
                        and status.actions[action_type].placement_type == "label"
                    ):
                        button_input_dict = status.actions[action_type].button_setup(
                            input_dict.copy()
                        )
                        if button_input_dict:
                            self.add_attached_button(button_input_dict)

        elif self.actor_label_type == "minister_office":
            self.message_start = "Office: "
            input_dict["init_type"] = "remove minister button"
            self.add_attached_button(input_dict)
            input_dict["init_type"] = "appoint minister button"
            input_dict["width"], input_dict["height"] = (s_size, s_size)
            for current_position in constants.minister_types:
                input_dict["appoint_type"] = current_position
                self.add_attached_button(input_dict)

        elif self.actor_label_type == "evidence":
            self.message_start = "Evidence: "
            if "ministers" in self.modes:
                input_dict["init_type"] = "to trial button"
                input_dict["width"], input_dict["height"] = (m_size, m_size)
                self.add_attached_button(input_dict)
            if "trial" in self.modes:
                input_dict["init_type"] = "fabricate evidence button"
                input_dict["width"], input_dict["height"] = (m_size, m_size)
                self.add_attached_button(input_dict)

                input_dict["init_type"] = "bribe judge button"
                self.add_attached_button(input_dict)

        elif self.actor_label_type == "slums":
            self.message_start = "Slums population: "

        elif (
            self.actor_label_type in constants.building_types
            and self.actor_label_type != "resource"
        ):
            self.message_start = ""

        elif self.actor_label_type == "combat_strength":
            self.message_start = "Combat strength: "

        elif self.actor_label_type == "building work crews":
            self.message_start = "Work crews: "

        elif self.actor_label_type == "inventory_name":
            self.message_start = ""

        elif self.actor_label_type == "inventory_quantity":
            self.message_start = "Quantity: "
            if self.actor_type == "mob":
                input_dict["init_type"] = "anonymous button"
                input_dict["image_id"] = "buttons/commodity_drop_button.png"
                input_dict["button_type"] = {
                    "on_click": (
                        actor_utility.callback,
                        ["displayed_mob_inventory", "transfer", 1],
                    ),
                    "tooltip": ["Orders the selected unit to drop this item"],
                }
                self.add_attached_button(input_dict)

                input_dict["image_id"] = "buttons/commodity_drop_all_button.png"
                input_dict["button_type"] = {
                    "on_click": (
                        actor_utility.callback,
                        ["displayed_mob_inventory", "transfer", "all"],
                    ),
                    "tooltip": ["Orders the selected unit to drop all of this item"],
                }
                self.add_attached_button(input_dict)

            elif self.actor_type == "tile":
                original_input_dict = input_dict.copy()
                input_dict["init_type"] = "anonymous button"
                input_dict["image_id"] = "buttons/commodity_pick_up_button.png"
                input_dict["button_type"] = {
                    "on_click": (
                        actor_utility.callback,
                        ["displayed_tile_inventory", "transfer", 1],
                    ),
                    "tooltip": ["Orders the selected unit to pick up this item"],
                }
                self.add_attached_button(input_dict)

                input_dict["image_id"] = "buttons/commodity_pick_up_all_button.png"
                input_dict["button_type"] = {
                    "on_click": (
                        actor_utility.callback,
                        ["displayed_tile_inventory", "transfer", "all"],
                    ),
                    "tooltip": ["Orders the selected unit to pick up all of this item"],
                }
                self.add_attached_button(input_dict)

                # Add pick up each button to inventory capacity label - if has at least 1 inventory capacity, show button that drops/picks up each type of item at once

                input_dict = original_input_dict
                input_dict["init_type"] = "sell commodity button"
                input_dict["image_id"] = "buttons/commodity_sell_button.png"
                self.add_attached_button(input_dict)

                input_dict["init_type"] = "sell all commodity button"
                input_dict["image_id"] = "buttons/commodity_sell_all_button.png"
                self.add_attached_button(input_dict)

                input_dict["init_type"] = "use equipment button"
                input_dict["image_id"] = "buttons/use_equipment_button.png"
                self.add_attached_button(input_dict)

        elif self.actor_label_type == "settlement":
            self.message_start = "Settlement: "
            input_dict["init_type"] = "rename settlement button"
            input_dict["image_id"] = "buttons/rename.png"
            self.add_attached_button(input_dict)

        elif self.actor_label_type in constants.terrain_parameters:
            self.message_start = utility.capitalize(self.actor_label_type) + ": "
            if constants.effect_manager.effect_active("god_mode"):
                input_dict["init_type"] = "change parameter button"
                input_dict["width"], input_dict["height"] = (s_size, s_size)

                input_dict["change"] = -1
                input_dict["image_id"] = "buttons/cycle_ministers_down_button.png"
                self.add_attached_button(input_dict)

                input_dict["change"] = 1
                input_dict["image_id"] = "buttons/cycle_ministers_up_button.png"
                self.add_attached_button(input_dict)

        elif self.actor_label_type == "banner":
            self.message_start = self.banner_text

        else:
            self.message_start = (
                utility.capitalize(self.actor_label_type) + ": "
            )  #'worker' -> 'Worker: '
        self.calibrate("none")

    def add_attached_button(self, input_dict, member_config=None):
        """
        Description:
            Adds a button created by the inputted input_dict to this label's interface collection, creating the collection if it does not already exist
        Input:
            dictionary input_dict: Input dict of button to create
            dictionary member_config=None: Optional member config of button to create
        Output:
            None
        """
        if not self.has_label_collection:
            self.has_label_collection = True
            self.insert_collection_above(
                override_input_dict={
                    "init_type": "ordered collection",
                    "direction": "horizontal",
                }
            )
            self.parent_collection.can_show_override = self  # uses this label's can_show as the collection's can_show, so any members require this label to be showing
        if (
            not member_config
        ):  # avoids issue with same default {} being used across multiple calls
            member_config = {}
        if not "order_y_offset" in member_config:
            member_config["order_y_offset"] = (
                abs(input_dict["height"] - self.height) / -2
            )
        self.parent_collection.add_member(
            constants.actor_creation_manager.create_interface_element(input_dict),
            member_config,
        )

    def update_tooltip(self):
        """
        Description:
            Sets this label's tooltip based on the label's type and the information of the actor it is attached to
        Input:
            None
        Output:
            None
        """
        if self.actor_label_type in ["current building work crew", "current passenger"]:
            if len(self.attached_list) > self.list_index:
                self.attached_list[self.list_index].update_tooltip()
                tooltip_text = self.attached_list[self.list_index].tooltip_text
                self.set_tooltip(tooltip_text)
            else:
                super().update_tooltip()

        elif self.actor_label_type == "passengers":
            if self.actor != "none":
                if self.actor.get_permission(constants.ACTIVE_PERMISSION):
                    name_list = [self.message_start]
                    for current_passenger in self.actor.contained_mobs:
                        name_list.append(
                            "    " + utility.capitalize(current_passenger.name)
                        )
                    if len(name_list) == 1:
                        name_list[0] = self.message_start + " none"
                    self.set_tooltip(name_list)
                else:
                    super().update_tooltip()

        elif self.actor_label_type == "crew":
            if self.actor != "none" and self.actor.crew != "none":
                self.actor.crew.update_tooltip()
                tooltip_text = self.actor.crew.tooltip_text
                self.set_tooltip(tooltip_text)
            else:
                super().update_tooltip()

        elif self.actor_label_type == "tooltip":
            if not self.actor == "none":
                self.actor.update_tooltip()
                tooltip_text = self.actor.tooltip_text
                if (
                    self.actor.actor_type == "tile"
                ):  # show tooltips of buildings in tile
                    for current_building in self.actor.cell.get_buildings():
                        current_building.update_tooltip()
                        tooltip_text.append("")
                        tooltip_text += current_building.tooltip_text
                self.set_tooltip(tooltip_text)

        elif self.actor_label_type in [
            "mob inventory capacity",
            "tile inventory capacity",
        ]:
            tooltip_text = [self.message]
            if self.actor_label_type == "mob inventory capacity":
                if not self.actor == "none":
                    tooltip_text.append(
                        f"This unit is currently holding {self.actor.get_inventory_used()} commodities"
                    )
                    tooltip_text.append(
                        f"This unit can hold a maximum of {self.actor.inventory_capacity} commodities"
                    )
            elif self.actor_label_type == "tile inventory capacity":
                if not self.actor == "none":
                    if not self.actor.cell.terrain_handler.visible:
                        tooltip_text.append("This tile has not been explored")
                    elif self.actor.infinite_inventory_capacity:
                        tooltip_text.append("This tile can hold infinite commodities")
                    else:
                        tooltip_text.append(
                            f"This tile currently contains {self.actor.get_inventory_used()} commodities"
                        )
                        tooltip_text.append(
                            f"This tile can retain a maximum of {self.actor.inventory_capacity} commodities"
                        )
                        tooltip_text.append(
                            "If this tile is holding commodities exceeding its capacity before resource production at the end of the turn, extra commodities will be lost"
                        )
            self.set_tooltip(tooltip_text)

        elif self.actor_label_type == "minister":
            tooltip_text = []
            if not self.actor == "none":
                self.actor.update_tooltip()
                if not self.actor.controlling_minister == "none":
                    tooltip_text = self.actor.controlling_minister.tooltip_text
                else:
                    tooltip_text = [
                        f"The {self.actor.controlling_minister_type} is responsible for controlling this unit",
                        f"As there is currently no {self.actor.controlling_minister_type}, this unit will not be able to complete most actions until one is appointed",
                    ]
            self.set_tooltip(tooltip_text)

        elif self.actor_label_type == "evidence":
            tooltip_text = []
            if not self.actor == "none":
                if constants.current_game_mode == "trial":
                    real_evidence = (
                        self.actor.corruption_evidence - self.actor.fabricated_evidence
                    )
                    tooltip_text.append(
                        f"Your prosecutor has found {real_evidence} piece{utility.generate_plural(real_evidence)} of evidence of corruption against this minister."
                    )
                    if self.actor.fabricated_evidence > 0:
                        tooltip_text.append(
                            f"Additionally, your prosecutor has fabricated {self.actor.fabricated_evidence} piece{utility.generate_plural(self.actor.corruption_evidence)} of fake evidence against this minister."
                        )
                    tooltip_text.append(
                        "Each piece of evidence, real or fabricated, increases the chance of a trial's success. After a trial, all fabricated evidence and about half of the real evidence are rendered unusable"
                    )
                else:
                    tooltip_text.append(
                        f"Your prosecutor has found {self.actor.corruption_evidence} piece{utility.generate_plural(self.actor.corruption_evidence)} of evidence of corruption against this minister."
                    )
                    tooltip_text.append(
                        "A corrupt minister may let goods go missing, steal the money given for a task and report a failure, or otherwise benefit themselves at the expense of your company"
                    )
                    tooltip_text.append(
                        "When a corrupt act is done, a skilled and loyal prosecutor may find evidence of the crime."
                    )
                    tooltip_text.append(
                        "If you believe a minister is corrupt, evidence against them can be used in a criminal trial to justify appointing a new minister in their position"
                    )
            self.set_tooltip(tooltip_text)

        elif self.actor_label_type == "background":
            tooltip_text = [self.message]
            tooltip_text.append(
                "A minister's personal background determines their social status and may give them additional expertise in certain areas"
            )
            self.set_tooltip(tooltip_text)

        elif self.actor_label_type == "social status":
            tooltip_text = [self.message]
            tooltip_text.append(
                "A minister's social status determines their power independent of your company."
            )
            tooltip_text.append(
                "A minister of higher social status has a much greater ability to either help your company when your goals align, or fight back should they ever diverge"
            )
            self.set_tooltip(tooltip_text)

        elif self.actor_label_type == "interests":
            tooltip_text = [self.message]
            tooltip_text.append(
                "While some interests are derived from a minister's legitimate talent or experience in a particular field, others are mere fancies"
            )
            self.set_tooltip(tooltip_text)

        elif self.actor_label_type == "ability":
            tooltip_text = [self.message]
            rank = 0
            if not self.actor == "none":
                for skill_value in range(6, 0, -1):  # iterates backwards from 6 to 1
                    for skill_type in self.actor.apparent_skills:
                        if self.actor.apparent_skills[skill_type] == skill_value:
                            rank += 1
                            skill_name = constants.minister_type_dict[
                                skill_type
                            ]  # like General to military
                            tooltip_text.append(
                                f"    {rank}. {skill_name.capitalize()}: {self.actor.apparent_skill_descriptions[skill_type]}"
                            )
            self.set_tooltip(tooltip_text)

        elif self.actor_label_type == "loyalty":
            tooltip_text = [self.message]
            self.set_tooltip(tooltip_text)

        elif self.actor_label_type == "building work crews":
            tooltip_text = []
            tooltip_text.append(
                "Increase work crew capacity by upgrading the building's scale with a construction gang"
            )
            if not self.attached_building == "none":
                tooltip_text.append(
                    f"Work crews: {len(self.attached_building.contained_work_crews)}/{self.attached_building.scale}"
                )
                for current_work_crew in self.attached_building.contained_work_crews:
                    tooltip_text.append(
                        "    " + utility.capitalize(current_work_crew.name)
                    )
            self.set_tooltip(tooltip_text)

        elif self.actor_label_type == "building efficiency":
            tooltip_text = [self.message]
            tooltip_text.append(
                "Each work crew attached to this building can produce up to the building efficiency in commodities each turn"
            )
            tooltip_text.append(
                "Increase work crew efficiency by upgrading the building's efficiency with a construction gang"
            )
            self.set_tooltip(tooltip_text)

        elif self.actor_label_type == "terrain feature":
            self.set_tooltip(
                status.terrain_feature_types[self.terrain_feature_type].description
            )

        elif self.actor_label_type == "slums":
            tooltip_text = [self.message]
            tooltip_text.append(
                "Slums can form around ports, train stations, and resource production facilities"
            )
            self.set_tooltip(tooltip_text)

        elif (
            self.actor_label_type in constants.building_types + ["resource building"]
            and self.actor_label_type != "resource"
        ):
            if self.actor != "none":
                label_type = self.actor_label_type
                if label_type == "resource building":
                    label_type = "resource"
                current_building = self.actor.cell.get_building(label_type)
                current_building.update_tooltip()
                self.set_tooltip(current_building.tooltip_text)

        elif self.actor_label_type == "combat_strength":
            tooltip_text = [self.message]
            tooltip_text.append(
                "Combat strength is an estimation of a unit's likelihood to win combat based on its experience and unit type"
            )
            tooltip_text.append(
                "When attacked, the defending side will automatically choose its strongest unit to fight"
            )
            if self.actor != "none":
                modifier = self.actor.get_combat_modifier()
                if modifier >= 0:
                    sign = "+"
                else:
                    sign = ""
                if self.actor.get_combat_strength() == 0:
                    tooltip_text.append(
                        "A unit with 0 combat strength will die automatically if forced to fight or if all other defenders are defeated"
                    )
                else:
                    if self.actor.get_permission(constants.VETERAN_PERMISSION):
                        tooltip_text.append(
                            f"In combat, this unit would roll 2 dice with a {sign}{modifier} modifier, taking the higher of the 2 results"
                        )
                    else:
                        tooltip_text.append(
                            f"In combat, this unit would roll 1 die with a {sign}{modifier} modifier"
                        )
            self.set_tooltip(tooltip_text)

        elif self.actor_label_type in constants.terrain_parameters:
            tooltip_text = [self.message]
            if self.actor != "none":
                if self.actor_label_type == "water":
                    tooltip_text.append(
                        "Represents the amount of water in this tile, including both standing water and average precipitation"
                    )
                elif self.actor_label_type == "temperature":
                    tooltip_text.append(
                        "Represents the average temperature in this tile, on a scale from -5 to 12"
                    )
                    if self.actor.cell.terrain_handler.knowledge_available(
                        constants.TERRAIN_PARAMETER_KNOWLEDGE
                    ):
                        tooltip_text.append(
                            f"Approximately {utility.fahrenheit(self.actor.cell.get_parameter('temperature'))} degrees Fahrenheit"
                        )
            self.set_tooltip(tooltip_text)

        else:
            super().update_tooltip()

    def calibrate(self, new_actor):
        """
        Description:
            Attaches this label to the inputted actor and updates this label's information based on the inputted actor
        Input:
            string/actor new_actor: The displayed actor whose information is matched by this label. If this equals 'none', the label does not match any actors.
        Output:
            None
        """
        self.actor = new_actor
        if new_actor != "none":
            if self.actor_label_type == "name":
                self.set_label(self.message_start + utility.capitalize(new_actor.name))

            elif self.actor_label_type == "coordinates":
                self.set_label(f"{self.message_start}({new_actor.x}, {new_actor.y})")

            elif self.actor_label_type == "terrain":
                if new_actor.grid.is_abstract_grid:
                    self.set_label(utility.capitalize(new_actor.grid.name))
                elif (
                    self.actor.cell.terrain_handler.visible
                    and self.actor.cell.terrain_handler.knowledge_available(
                        constants.TERRAIN_KNOWLEDGE
                    )
                ):
                    self.set_label(
                        f"{self.message_start}{new_actor.cell.terrain_handler.terrain.replace('_', ' ')}"
                    )
                else:
                    self.set_label(self.message_start + "unknown")

            elif self.actor_label_type == "resource":
                if new_actor.grid.is_abstract_grid:
                    self.set_label(self.message_start + "n/a")
                elif new_actor.cell.terrain_handler.visible:
                    self.set_label(
                        self.message_start + new_actor.cell.terrain_handler.resource
                    )
                else:
                    self.set_label(self.message_start + "unknown")

            elif self.actor_label_type == "terrain feature":
                self.set_label(self.terrain_feature_type.capitalize())

            elif self.actor_label_type == "resource building":
                if (
                    (not new_actor.grid.is_abstract_grid)
                    and new_actor.cell.terrain_handler.visible
                    and new_actor.cell.has_building("resource")
                ):
                    self.set_label(
                        new_actor.cell.get_building("resource").name.capitalize()
                    )

            elif self.actor_label_type == "movement":
                if self.actor.get_permission(constants.PMOB_PERMISSION):
                    if new_actor.get_permission(constants.ACTIVE_PERMISSION) and not (
                        new_actor.has_infinite_movement
                        or new_actor.temp_movement_disabled
                    ):
                        # If train with crew or normal unit
                        self.set_label(
                            f"{self.message_start}{new_actor.movement_points}/{new_actor.max_movement_points}"
                        )
                    else:  # If ship or train without crew
                        if not new_actor.has_infinite_movement:
                            if (
                                new_actor.movement_points == 0
                                or new_actor.temp_movement_disabled
                                or not new_actor.get_permission(
                                    constants.ACTIVE_PERMISSION
                                )
                            ):
                                self.set_label("No movement")
                        else:
                            if (
                                new_actor.movement_points == 0
                                or new_actor.temp_movement_disabled
                                or not new_actor.get_permission(
                                    constants.ACTIVE_PERMISSION
                                )
                            ):
                                self.set_label("No movement")
                            else:
                                self.set_label("Infinite movement")
                else:
                    self.set_label(self.message_start + "???")

            elif self.actor_label_type == "attitude":
                if not self.actor.get_permission(constants.PMOB_PERMISSION):
                    if self.actor.hostile:
                        self.set_label(self.message_start + "hostile")
                    else:
                        self.set_label(self.message_start + "neutral")

            elif self.actor_label_type == "combat_strength":
                self.set_label(
                    f"{self.message_start}{str(self.actor.get_combat_strength())}"
                )

            elif self.actor_label_type == "controllable":
                if not self.actor.get_permission(constants.PMOB_PERMISSION):
                    self.set_label("You do not control this unit")

            elif self.actor_label_type == "current building work crew":
                if self.list_type == "resource building":
                    if new_actor.cell.has_building("resource"):
                        self.attached_building = new_actor.cell.get_building("resource")
                        self.attached_list = self.attached_building.contained_work_crews
                        if len(self.attached_list) > self.list_index:
                            self.set_label(
                                self.message_start
                                + utility.capitalize(
                                    self.attached_list[self.list_index].name
                                )
                            )
                    else:
                        self.attached_building = "none"
                        self.attached_list = []

            elif self.actor_label_type == "crew":
                if self.actor.all_permissions(
                    constants.VEHICLE_PERMISSION, constants.ACTIVE_PERMISSION
                ):
                    self.set_label(
                        self.message_start + utility.capitalize(self.actor.crew.name)
                    )
                else:
                    self.set_label(self.message_start + "none")

            elif self.actor_label_type == "passengers":
                if not self.actor.get_permission(constants.ACTIVE_PERMISSION):
                    self.set_label("Requires a worker crew to function")
                elif self.actor.get_permission(constants.VEHICLE_PERMISSION):
                    if len(self.actor.contained_mobs) == 0:
                        self.set_label(self.message_start + "none")
                    else:
                        self.set_label(self.message_start)

            elif self.actor_label_type == "current passenger":
                if self.actor.get_permission(constants.VEHICLE_PERMISSION):
                    if len(self.actor.contained_mobs) > 0:
                        self.attached_list = new_actor.contained_mobs
                        if len(self.attached_list) > self.list_index:
                            self.set_label(
                                self.message_start
                                + utility.capitalize(
                                    self.attached_list[self.list_index].name
                                )
                            )

            elif self.actor_label_type in ["workers", "officer"]:
                if self.actor.get_permission(constants.GROUP_PERMISSION):
                    if self.actor_label_type == "workers":
                        self.set_label(
                            f"{self.message_start}{str(utility.capitalize(self.actor.worker.name))}"
                        )
                    else:
                        self.set_label(
                            f"{self.message_start}{str(utility.capitalize(self.actor.officer.name))}"
                        )

            elif self.actor_label_type in [
                "mob inventory capacity",
                "tile inventory capacity",
            ]:
                inventory_used = self.actor.get_inventory_used()
                if (
                    self.actor_label_type == "tile inventory capacity"
                    and not self.actor.cell.terrain_handler.visible
                ):
                    text = self.message_start + "n/a"
                elif self.actor.infinite_inventory_capacity:
                    text = self.message_start + "unlimited"
                else:
                    text = f"{self.message_start}{inventory_used}/{self.actor.inventory_capacity}"
                inventory_grid = getattr(status, self.actor_type + "_inventory_grid")
                if inventory_grid.inventory_page > 0:
                    minimum = (inventory_grid.inventory_page * 27) + 1
                    functional_capacity = max(
                        inventory_used, self.actor.inventory_capacity
                    )
                    maximum = min(minimum + 26, functional_capacity)
                    if maximum >= minimum:
                        text += f" ({minimum}-{maximum})"
                self.set_label(text)

            elif self.actor_label_type == "minister":
                if (
                    self.actor.get_permission(constants.PMOB_PERMISSION)
                    and self.actor.controlling_minister != "none"
                ):
                    self.set_label(
                        self.message_start + self.actor.controlling_minister.name
                    )
                else:
                    self.set_label(f"{self.message_start}n/a")

            elif self.actor_label_type == "evidence":
                if new_actor.fabricated_evidence == 0:
                    self.set_label(
                        f"{self.message_start}{str(new_actor.corruption_evidence)}"
                    )
                else:
                    self.set_label(
                        f"{self.message_start}{new_actor.corruption_evidence} ({new_actor.fabricated_evidence})"
                    )

            elif self.actor_label_type == "background":
                self.set_label(self.message_start + new_actor.background)

            elif self.actor_label_type == "social status":
                self.set_label(self.message_start + new_actor.status)

            elif self.actor_label_type == "interests":
                self.set_label(
                    f"{self.message_start} {new_actor.interests[0]} and {new_actor.interests[1]}"
                )

            elif self.actor_label_type == "ability":
                message = ""
                if new_actor.current_position == "none":
                    displayed_skill = new_actor.get_max_apparent_skill()
                    message += "Highest ability: "
                else:
                    displayed_skill = new_actor.current_position
                    message += "Current ability: "
                if displayed_skill != "unknown":
                    displayed_skill_name = constants.minister_type_dict[
                        displayed_skill
                    ]  # like General to military
                    message += f"{new_actor.apparent_skill_descriptions[displayed_skill]} ({displayed_skill_name})"
                else:
                    message += displayed_skill
                self.set_label(message)

            elif self.actor_label_type == "loyalty":
                self.set_label(
                    self.message_start + new_actor.apparent_corruption_description
                )

            elif self.actor_label_type in constants.skill_types:
                self.set_label(
                    self.actor_label_type.capitalize()
                    + ": "
                    + self.actor.apparent_skill_descriptions[
                        constants.type_minister_dict[self.actor_label_type]
                    ]
                )

            elif self.actor_label_type == "minister_name":
                self.set_label(self.message_start + new_actor.name)

            elif self.actor_label_type == "minister_office":
                self.set_label(self.message_start + new_actor.current_position)

            elif self.actor_label_type == "slums":
                if self.actor.cell.has_building("slums"):
                    self.set_label(
                        f"{self.message_start}{str(self.actor.cell.get_building('slums').available_workers)}"
                    )

            elif self.actor_label_type in constants.building_types:
                if self.actor.cell.has_building(self.actor_label_type):
                    self.set_label(
                        f"{self.message_start}{self.actor.cell.get_building(self.actor_label_type).name.capitalize()}"
                    )

            elif self.actor_label_type == "inventory_name":
                self.set_label(
                    f"{self.message_start}{utility.capitalize(new_actor.current_item)}"
                )

            elif self.actor_label_type == "inventory_quantity":
                self.set_label(
                    f"{self.message_start}{str(new_actor.actor.get_inventory(new_actor.current_item))}"
                )

            elif self.actor_label_type == "settlement":
                if new_actor.cell.settlement:
                    self.set_label(
                        f"{self.message_start}{str(new_actor.cell.settlement.name)}"
                    )
                else:
                    self.set_label(f"{self.message_start} n/a")

            elif self.actor_label_type in constants.terrain_parameters:
                if (
                    new_actor.cell.terrain_handler.knowledge_available(
                        constants.TERRAIN_PARAMETER_KNOWLEDGE
                    )
                    or self.actor_label_type == "knowledge"
                ):
                    value = new_actor.cell.get_parameter(self.actor_label_type)
                    self.set_label(
                        f"{self.message_start}{constants.terrain_manager.terrain_parameter_keywords[self.actor_label_type][value]} ({value}/{new_actor.cell.terrain_handler.maxima.get(self.actor_label_type, 6)})"
                    )
                else:
                    self.set_label(f"{self.message_start}unknown")

        elif self.actor_label_type == "tooltip":
            return  # do not set text for tooltip label
        elif self.actor_label_type == "banner":
            self.set_label(self.message_start)
        else:
            self.set_label(f"{self.message_start}n/a")

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this label should be drawn
        Input:
            None
        Output:
            boolean: False if no actor displayed or if various conditions are present depending on label type, otherwise returns same value as superclass
        """
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if not result:
            return False
        elif self.actor == "none":
            return False
        elif self.actor_label_type == "resource" and (
            self.actor.cell.terrain_handler.resource == "none"
            or (not self.actor.cell.terrain_handler.visible)
            or self.actor.grid.is_abstract_grid
        ):
            return False
        elif self.actor_label_type == "resource building" and (
            (not self.actor.cell.terrain_handler.visible)
            or (not self.actor.cell.has_building("resource"))
        ):
            return False
        elif self.actor_label_type in [
            "crew",
            "passengers",
        ] and not self.actor.get_permission(
            constants.VEHICLE_PERMISSION
        ):  # do not show passenger or crew labels for non-vehicle mobs
            return False
        elif self.actor_label_type in [
            "workers",
            "officer",
        ] and not self.actor.get_permission(constants.GROUP_PERMISSION):
            return False
        elif self.actor.actor_type == "mob" and (
            self.actor.in_vehicle or self.actor.in_group or self.actor.in_building
        ):  # Do not show mobs that are attached to another unit/building
            return False
        elif (
            self.actor_label_type in constants.building_types
            and self.actor_label_type != "resource"
            and not self.actor.cell.has_building(self.actor_label_type)
        ):
            return False
        elif self.actor_label_type == "settlement" and not self.actor.cell.settlement:
            return False
        elif self.actor_label_type == "minister" and not self.actor.get_permission(
            constants.PMOB_PERMISSION
        ):
            return False
        elif self.actor_label_type in [
            "attitude",
            "controllable",
        ] and self.actor.get_permission(constants.PMOB_PERMISSION):
            return False
        elif (
            self.actor_label_type == "loyalty"
            and self.actor.apparent_corruption_description == "unknown"
        ):
            return False
        elif self.actor_label_type == "ability":
            empty = True
            for skill_type in self.actor.apparent_skills:
                if self.actor.apparent_skill_descriptions[skill_type] != "unknown":
                    empty = False
            if empty:
                return False
            else:
                return result
        elif self.actor_label_type in constants.skill_types:
            return (
                self.actor.apparent_skill_descriptions[
                    constants.type_minister_dict[self.actor_label_type]
                ]
                != "unknown"
            )
        elif (
            self.actor_label_type in constants.terrain_parameters
            and self.actor_label_type != "knowledge"
        ):
            return self.actor.cell.terrain_handler.knowledge_available(
                constants.TERRAIN_PARAMETER_KNOWLEDGE
            )
        else:
            return result


class banner(actor_display_label):
    """
    Banner with predefined text that is displayed under certain conditions
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'minimum_width': int value - Minimum pixel width of this label. Its width will increase if the contained text would extend past the edge of the label
                'actor_label_type': string value - Type of actor information shown
                'actor_type': string value - Type of actor to display the information of, like 'mob' or 'tile'
                'banner_type': Type of banner to display, like 'terrain details' - determines behavior
                'banner_text': string value - Text to display on the banner
        Output:
            None
        """
        self.banner_type = input_dict["banner_type"]
        self.banner_text = input_dict["banner_text"]
        input_dict["actor_label_type"] = "banner"
        super().__init__(input_dict)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this label should be drawn
        Input:
            None
        Output:
            boolean: Returns whether this label should be drawn
        """
        if self.banner_type == "terrain details":
            return (
                super().can_show(skip_parent_collection=skip_parent_collection)
                and self.actor.cell.terrain_handler.knowledge_available(
                    constants.TERRAIN_KNOWLEDGE
                )
                and not self.actor.cell.terrain_handler.knowledge_available(
                    constants.TERRAIN_PARAMETER_KNOWLEDGE
                )
            )
        else:
            return super().can_show(skip_parent_collection=skip_parent_collection)


class list_item_label(actor_display_label):
    """
    Label that shows the information of a certain item in a list, like a train passenger among a list of passengers
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'minimum_width': int value - Minimum pixel width of this label. Its width will increase if the contained text would extend past the edge of the label
                'actor_label_type': string value - Type of actor information shown
                'actor_type': string value - Type of actor to display the information of, like 'mob' or 'tile'
                'list_index': int value - Index to determine item of list reflected
                'list_type': string value - Type of list associated with, like 'resource building' along with label type of 'current building work crew' to show work crews attached to a resource
                    building
        Output:
            None
        """
        self.list_index = input_dict["list_index"]
        self.list_type = input_dict["list_type"]
        self.attached_list = []
        super().__init__(input_dict)

    def calibrate(self, new_actor):
        """
        Description:
            Attaches this label to the inputted actor and updates this label's information based on one of the inputted actor's lists
        Input:
            string/actor new_actor: The displayed actor that whose information is matched by this label. If this equals 'none', the label does not match any actors
        Output:
            None
        """
        self.attached_list = []
        super().calibrate(new_actor)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this label should be drawn
        Input:
            None
        Output:
            boolean: Returns same value as superclass as long as this label's list is long enough to contain this label's index, otherwise returns False
        """
        if len(self.attached_list) > self.list_index:
            return super().can_show(skip_parent_collection=skip_parent_collection)
        return False


class actor_tooltip_label(actor_display_label):
    """
    Label used for actor tooltips that can calibrate to actors and select them when clicked
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'minimum_width': int value - Minimum pixel width of this label. Its width will increase if the contained text would extend past the edge of the label
                'actor_type': string value - Type of actor to display the information of, like 'mob', 'tile', or 'minister'
        Output:
            None
        """
        input_dict["actor_label_type"] = "tooltip"
        super().__init__(input_dict)

    def on_click(self):
        """
        Description:
            Selects the calibrated unit when clicked - used to allow selecting units from reorganization interface
        Input:
            None
        Output:
            None
        """
        if self.actor_type == "tile":
            actor_utility.calibrate_actor_info_display(
                status.tile_info_display, self.actor
            )
            actor_utility.calibrate_actor_info_display(status.mob_info_display, None)
        elif self.actor.get_permission(constants.DUMMY_PERMISSION):
            if self.actor.get_permission(
                constants.GROUP_PERMISSION
            ) or self.actor.all_permissions(
                constants.VEHICLE_PERMISSION, constants.ACTIVE_PERMISSION
            ):
                status.reorganize_unit_right_button.on_click()
            else:
                status.reorganize_unit_left_button.on_click()
                if not self.actor.get_permission(
                    constants.DUMMY_PERMISSION
                ):  # Only select if dummy unit successfully became real
                    self.actor.cycle_select()
        else:
            self.actor.cycle_select()


class building_work_crews_label(actor_display_label):
    """
    Label at the top of the list of work crews in a building that shows how many work crews are in it
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'minimum_width': int value - Minimum pixel width of this label. Its width will increase if the contained text would extend past the edge of the label
                'actor_type': string value - Type of actor to display the information of, like 'mob' or 'tile'
                'building_type': string value - Type of building associated with, like 'resource building'
        Output:
            None
        """
        self.remove_work_crew_button = "none"
        self.show_label = False
        self.attached_building = "none"
        input_dict["actor_label_type"] = "building work crews"
        super().__init__(input_dict)
        self.building_type = input_dict["building_type"]

    def calibrate(self, new_actor):
        """
        Description:
            Attaches this label to the inputted actor and updates this label's information based on the inputted actor
        Input:
            string/actor new_actor: The displayed actor that whose information is matched by this label. If this equals 'none', the label does not match any actors.
        Output:
            None
        """
        self.actor = new_actor
        self.show_label = False
        if new_actor != "none":
            self.attached_building = new_actor.cell.get_building(self.building_type)
            if not self.attached_building == "none":
                self.set_label(
                    f"{self.message_start}{len(self.attached_building.contained_work_crews)}/{self.attached_building.scale}"
                )
                self.show_label = True

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this label should be drawn
        Input:
            None
        Output:
            boolean: Returns same value as superclass as long as the displayed tile has a building of this label's building_type, otherwise returns False
        """
        if self.show_label:
            return super().can_show(skip_parent_collection=skip_parent_collection)
        else:
            return False


class building_efficiency_label(actor_display_label):
    """
    Label that shows a production building's efficiency, which is the number of attempts work crews at the building have to produce commodities
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'minimum_width': int value - Minimum pixel width of this label. Its width will increase if the contained text would extend past the edge of the label
                'actor_type': string value - Type of actor to display the information of, like 'mob' or 'tile'
                'building_type': string value - Type of building associated with, like 'resource building'
        Output:
            None
        """
        self.remove_work_crew_button = "none"
        self.show_label = False
        input_dict["actor_label_type"] = "building efficiency"
        super().__init__(input_dict)
        self.building_type = input_dict["building_type"]
        self.attached_building = "none"

    def calibrate(self, new_actor):
        """
        Description:
            Attaches this label to the inputted actor and updates this label's information based on the inputted actor
        Input:
            string/actor new_actor: The displayed actor that whose information is matched by this label. If this equals 'none', the label does not match any actors.
        Output:
            None
        """
        self.actor = new_actor
        self.show_label = False
        if new_actor != "none":
            self.attached_building = new_actor.cell.get_building(self.building_type)
            if not self.attached_building == "none":
                self.set_label(f"Efficiency: {self.attached_building.efficiency}")
                self.show_label = True

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this label should be drawn
        Input:
            None
        Output:
            boolean: Returns same value as superclass as long as the displayed tile has a building of this label's building_type, otherwise returns False
        """
        if self.show_label:
            return super().can_show(skip_parent_collection=skip_parent_collection)
        else:
            return False


class terrain_feature_label(actor_display_label):
    """
    Label that shows a particular type of terrain feature, if present
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'minimum_width': int value - Minimum pixel width of this label. Its width will increase if the contained text would extend past the edge of the label
                'actor_type': string value - Type of actor to display the information of, like 'mob' or 'tile'
                'terrain_feature_type': string value - Type of terrain feature associated with, like 'equator'
        Output:
            None
        """
        self.terrain_feature_type = input_dict["terrain_feature_type"]
        input_dict["actor_label_type"] = "terrain feature"
        super().__init__(input_dict)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this label should be drawn
        Input:
            None
        Output:
            boolean: Returns same value as superclass as long as the associated terrain feature is present
        """
        return super().can_show(
            skip_parent_collection=skip_parent_collection
        ) and self.actor.cell.terrain_handler.terrain_features.get(
            self.terrain_feature_type, False
        )
