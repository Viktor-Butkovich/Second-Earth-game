# Contains functionality for buttons

import pygame
from typing import List
from modules.util import (
    text_utility,
    scaling,
    main_loop_utility,
    actor_utility,
    utility,
    turn_management_utility,
    market_utility,
    game_transitions,
    minister_utility,
)
from modules.constructs import item_types, minister_types, equipment_types
from modules.interface_components import interface_elements
from modules.constants import constants, status, flags


class button(interface_elements.interface_element):
    """
    An object does something when clicked or when the corresponding key is pressed
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'button_type': string value - Determines the function of this button, like 'end turn'
                'keybind_id' = None: pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'attached_label': label value - Label that this button is attached to, optional except for label-specific buttons, like disembarking a particular passenger
                    based on which passenger label the button is attached to
        Output:
            None
        """
        self.outline_width = 2
        self.outline = pygame.Rect(
            0,
            0,
            input_dict["width"] + (2 * self.outline_width),
            input_dict["height"] + (self.outline_width * 2),
        )
        if "attached_label" in input_dict:
            self.attached_label = input_dict["attached_label"]
        if "attached_collection" in input_dict:
            self.attached_collection = input_dict["attached_collection"]
        super().__init__(input_dict)
        self.has_released = True
        self.button_type = input_dict.get("button_type", input_dict["init_type"])
        status.button_list.append(self)
        self.keybind_id = input_dict.get("keybind_id", None)
        self.has_keybind = self.keybind_id != None
        if self.has_keybind:
            self.set_keybind(self.keybind_id)
        if "color" in input_dict:
            self.color = constants.color_dict[input_dict["color"]]
        self.has_button_press_override = False
        self.enable_shader = input_dict.get("enable_shader", False)
        self.showing_outline = False
        self.showing_background = True
        self.confirming = False
        self.being_pressed = False
        self.in_notification = (
            False  # used to prioritize notification buttons in drawing and tooltips
        )

    def calibrate(self, new_actor, override_exempt=False):
        """
        Description:
            Attaches this button to the inputted actor and updates this button's image to that of the actor. May also display a shader over this button, if its particular
                requirements are fulfilled
        Input:
            string/actor new_actor: The minister whose information is matched by this button. If this equals None, this button is detached from any ministers
            bool override_exempt: Optional parameter that may be given to calibrate functions, does nothing for buttons
        Output:
            None
        """
        super().calibrate(new_actor, override_exempt)
        if self.enable_shader:
            shader_image_id = "misc/shader.png"
            if self.enable_shader_condition():
                if type(self.image.image_id) == str:
                    self.image.set_image([self.image.image_id, shader_image_id])
                elif not shader_image_id in self.image.image_id:
                    self.image.set_image(self.image.image_id + shader_image_id)
            else:
                if not type(self.image.image_id) == str:
                    if shader_image_id in self.image.image_id:
                        image_id = utility.remove_from_list(
                            self.image.image_id, shader_image_id
                        )
                        if len(image_id) == 1:
                            image_id = image_id[0]
                        self.image.set_image(image_id)

    def enable_shader_condition(self):
        """
        Description:
            Calculates and returns whether this button should display its shader, given that it has shader enabled - open to be redefined by subclasses w/ specific criteria
        Input:
            None
        Output:
            boolean: Returns whether this button should display its shader, given that it has shader enabled
        """
        return True

    def set_origin(self, new_x, new_y):
        """
        Description:
            Sets this interface element's location at the inputted coordinates
        Input:
            int new_x: New x coordinate for this element's origin
            int new_y: New y coordinate for this element's origin
        Output:
            None
        """
        super().set_origin(new_x, new_y)
        self.outline.y = self.Rect.y - self.outline_width
        self.outline.x = self.Rect.x - self.outline_width

    @property
    def tooltip_text(self) -> List[List[str]]:
        """
        Provides the tooltip for this object
        """
        if self.button_type in [
            constants.MOVE_UP_BUTTON,
            constants.MOVE_DOWN_BUTTON,
            constants.MOVE_LEFT_BUTTON,
            constants.MOVE_RIGHT_BUTTON,
        ]:
            direction = None
            x_change = 0
            y_change = 0
            if self.button_type == constants.MOVE_UP_BUTTON:
                direction = "north"
                non_cardinal_direction = "up"
                y_change = 1
            elif self.button_type == constants.MOVE_DOWN_BUTTON:
                direction = "south"
                non_cardinal_direction = "down"
                y_change = -1
            elif self.button_type == constants.MOVE_LEFT_BUTTON:
                direction = "west"
                non_cardinal_direction = "left"
                x_change = -1
            elif self.button_type == constants.MOVE_RIGHT_BUTTON:
                direction = "east"
                non_cardinal_direction = "right"
                x_change = 1

            tooltip_text = []

            if status.displayed_mob:
                movement_cost = status.displayed_mob.get_movement_cost(
                    x_change, y_change
                )
                adjacent_location = status.displayed_mob.location.adjacent_locations[
                    non_cardinal_direction
                ]
                local_infrastructure = (
                    status.displayed_mob.location.get_intact_building(
                        constants.INFRASTRUCTURE
                    )
                )
                if True:  # adjacent_location.visible:
                    tooltip_text.append(f"Press to move to the {direction}")
                    adjacent_infrastructure = adjacent_location.get_intact_building(
                        constants.INFRASTRUCTURE
                    )
                    connecting_roads = False
                    if (
                        status.displayed_mob.get_permission(
                            constants.BATTALION_PERMISSION
                        )
                        and adjacent_location.get_best_combatant("npmob") != None
                    ):
                        tooltip_text += status.actions["combat"].tooltip_text
                        # (
                        #    tooltip_info_dict={
                        #        "adjacent_infrastructure": adjacent_infrastructure,
                        #        "local_infrastructure": local_infrastructure,
                        #        "x_change": x_change,
                        #        "y_change": y_change,
                        #        "adjacent_location": adjacent_location,
                        #    }
                        # )
                    else:
                        message = ""
                        if status.displayed_mob.all_permissions(
                            constants.VEHICLE_PERMISSION, constants.TRAIN_PERMISSION
                        ):
                            if (
                                adjacent_infrastructure
                                and adjacent_infrastructure.is_railroad
                                and local_infrastructure
                                and local_infrastructure.is_railroad
                            ):
                                message = f"Costs {movement_cost} movement point{utility.generate_plural(movement_cost)} because the adjacent location has connecting railroads"
                            else:
                                message = "Not possible because the adjacent location does not have connecting railroads"
                            tooltip_text.append(message)
                            tooltip_text.append("A train can only move along railroads")
                        else:
                            message = f"Costs {movement_cost} movement point{utility.generate_plural(movement_cost)} because the adjacent location has {adjacent_location.terrain.replace('_', ' ')} terrain"
                            if (
                                local_infrastructure and adjacent_infrastructure
                            ):  # if both have infrastructure
                                connecting_roads = True
                                message += " and connecting roads"
                            elif (
                                local_infrastructure == None and adjacent_infrastructure
                            ):  # if local has no infrastructure but adjacent does
                                message += " and no connecting roads"
                            elif (
                                local_infrastructure
                            ):  # if local has infrastructure but not adjacent
                                message += " and no connecting roads"  # + local_infrastructure.infrastructure_type
                            else:
                                message += " and no connecting roads"

                            tooltip_text.append(message)
                            tooltip_text.append(
                                f"Moving into a {adjacent_location.terrain.replace('_', ' ')} location costs {constants.terrain_movement_cost_dict.get(adjacent_location.terrain, 1)} movement points"
                            )
                    if connecting_roads:
                        tooltip_text.append(
                            "Moving between 2 locations with roads or railroads costs half as many movement points."
                        )
                else:
                    tooltip_text += status.actions["exploration"].tooltip_text
                    # (
                    #    tooltip_info_dict={"direction": direction}
                    # )

            return tooltip_text

        elif self.button_type == constants.EXECUTE_MOVEMENT_ROUTES_BUTTON:
            return [
                "Press to move all valid units along their designated movement routes"
            ]

        elif self.button_type == constants.INSTRUCTIONS_BUTTON:
            return [
                "Shows the game's instructions",
                "Press this when instructions are not opened to open them",
                "Press this when instructions are opened to close them",
            ]

        elif self.button_type == constants.MERGE_PROCEDURE:
            if status.displayed_mob and status.displayed_mob.all_permissions(
                constants.OFFICER_PERMISSION, constants.EVANGELIST_PERMISSION
            ):
                return [
                    "Merges this evangelist with church volunteers in the same location to form a group of missionaries",
                    "Requires that an evangelist is selected in the same location as church volunteers",
                ]
            else:
                return [
                    "Merges this officer with a worker in the same location to form a group with a type based on that of the officer",
                    "Requires that an officer is selected in the same location as a worker",
                ]

        elif self.button_type == constants.SPLIT_PROCEDURE:
            return ["Splits a group into its worker and officer"]

        elif self.button_type == constants.CREW_PROCEDURE:  # clicked on vehicle side
            return [
                f"Merges this vehicle with a worker in the same location to form a crewed vehicle",
                f"Requires that an uncrewed vehicle is selected in the same location as a worker",
            ]

        elif self.button_type == constants.UNCREW_PROCEDURE:
            return [f"Orders this vehicle's crew to abandon the vehicle."]

        elif self.button_type == constants.EMBARK_VEHICLE_BUTTON:
            return [
                f"Orders this unit to embark a vehicle in the same location",
            ]

        elif self.button_type == constants.DISEMBARK_VEHICLE_BUTTON:
            return ["Orders this unit to disembark the vehicle"]

        elif self.button_type == constants.EMBARK_ALL_PASSENGERS_BUTTON:
            return [
                f"Orders this vehicle to take all non-vehicle units in this location as passengers"
            ]

        elif self.button_type == constants.DISEMBARK_ALL_PASSENGERS_BUTTON:
            return [f"Orders this vehicle to disembark all passengers"]

        elif self.button_type == constants.REMOVE_WORK_CREW_BUTTON:
            if self.attached_label.attached_building:
                return [
                    "Detaches this work crew from the "
                    + self.attached_label.attached_building.name
                ]
            else:
                return ["none"]

        elif (
            self.button_type == constants.END_TURN_BUTTON
        ):  # different from end turn from choice buttons - start end turn brings up a choice notification
            return ["Ends the current turn"]

        elif self.button_type in [
            constants.SELL_ITEM_BUTTON,
            constants.SELL_ALL_ITEM_BUTTON,
            constants.SELL_EACH_ITEM_BUTTON,
        ]:
            if status.displayed_location:
                if self.button_type == constants.SELL_ITEM_BUTTON:
                    return [
                        f"Orders your {status.minister_types[constants.TERRAN_AFFAIRS_MINISTER].name} to sell 1 unit of {self.attached_label.actor.current_item.name} for about {self.attached_label.actor.current_item.price} money at the end of the turn",
                        "The amount each item was sold for is reported at the beginning of your next turn",
                        f"Each unit of {self.attached_label.actor.current_item.name} sold has a chance of reducing its sale price",
                    ]
                elif self.button_type == constants.SELL_ALL_ITEM_BUTTON:
                    num_present = status.displayed_location.get_inventory(
                        self.attached_label.actor.current_item
                    )
                    return [
                        f"Orders your {status.minister_types[constants.TERRAN_AFFAIRS_MINISTER].name} to sell your entire stockpile of {self.attached_label.actor.current_item.name} for about {self.attached_label.actor.current_item.price} money each at the end of the turn, for a total of about {self.attached_label.actor.current_item.price * num_present} money",
                        "The amount each item was sold for is reported at the beginning of your next turn",
                        f"Each unit of {self.attached_label.actor.current_item.name} sold has a chance of reducing its sale price",
                    ]
                else:
                    return [
                        f"Orders your {status.minister_types[constants.TERRAN_AFFAIRS_MINISTER].name} to sell all items at the end of the turn, "
                        f"The amount each item was sold for is reported at the beginning of your next turn",
                        "Each item sold has a chance of reducing its sale price",
                    ]
            else:
                return ["none"]

        elif self.button_type == constants.PICK_UP_EACH_ITEM_BUTTON:
            return ["Orders the selected unit to pick up all items"]

        elif self.button_type == constants.DROP_EACH_ITEM_BUTTON:
            return ["Orders the selected unit to drop all items"]

        elif self.button_type == constants.USE_EQUIPMENT_BUTTON:
            if status.displayed_location:
                return [
                    f"Orders the selected unit to equip {self.attached_label.actor.current_item.name}"
                ]

        elif self.button_type == constants.REMOVE_EQUIPMENT_BUTTON:
            if status.displayed_mob:
                return [
                    f"Click to unequip {self.equipment_type.name}"
                ] + self.equipment_type.description

        elif self.button_type == constants.USE_EACH_EQUIPMENT_BUTTON:
            return ["Orders the selected unit to equip all eligible items"]

        elif self.button_type == constants.SWITCH_THEATRE_BUTTON:
            return [
                "Moves this ship across space to another theatre at the end of the turn",
                "Once clicked, the mouse pointer can be used to click on the destination",
                "The destination, once chosen, will having a flashing yellow outline",
                "Requires that this spaceship is able to move",
            ]

        elif self.button_type == constants.CYCLE_PASSENGERS_BUTTON:
            if self.vehicle_type:
                tooltip_text = [f"Cycles through this vehicle's passengers"]
                tooltip_text.append("Passengers: ")
                if self.showing:
                    for current_passenger in status.displayed_mob.subscribed_passengers:
                        tooltip_text.append(f"    {current_passenger.name}")
                return tooltip_text

        elif self.button_type == constants.CYCLE_WORK_CREWS_BUTTON:
            tooltip_text = ["Cycles through this  building's work crews"]
            tooltip_text.append("Work crews: ")
            if self.showing:
                for current_work_crew in status.displayed_location.get_building(
                    constants.RESOURCE
                ).subscribed_work_crews:
                    tooltip_text.append(f"    {current_work_crew.name}")
            return tooltip_text

        elif self.button_type == constants.CYCLE_SAME_LOCATION_BUTTON:
            tooltip_text = ["Cycles through this location's units"]
            tooltip_text.append("Units: ")
            if self.showing:
                tooltip_text += [
                    f"    {current_mob.name}"
                    for current_mob in status.displayed_location.subscribed_mobs
                ]
            return tooltip_text

        elif self.button_type == constants.BUILD_TRAIN_BUTTON:
            cost = actor_utility.get_building_cost(
                status.displayed_mob, status.building_types[constants.TRAIN]
            )
            return [
                f"Orders parts for and attempts to assemble a train in this unit's location for {cost} money",
                "Can only be assembled on a train station",
                "Costs all remaining movement points, at least 1",
                "Unlike buildings, the cost of vehicle assembly is not impacted by local terrain",
            ]

        elif self.button_type == constants.CYCLE_UNITS_BUTTON:
            tooltip_text = ["Selects the next unit in the turn order"]
            turn_queue = status.player_turn_queue
            if len(turn_queue) > 0:
                for current_pmob in turn_queue:
                    tooltip_text.append(f"    {utility.capitalize(current_pmob.name)}")
            return tooltip_text

        elif self.button_type == constants.NEW_GAME_BUTTON:
            return ["Starts a new game"]

        elif self.button_type == constants.SAVE_GAME_BUTTON:
            return ["Saves this game"]

        elif self.button_type == constants.LOAD_GAME_BUTTON:
            return ["Loads a saved game"]

        elif self.button_type == constants.CYCLE_AVAILABLE_MINISTERS_BUTTON:
            return ["Cycles through the candidates available to be appointed"]

        elif self.button_type == constants.APPOINT_MINISTER_BUTTON:
            return ["Appoints this candidate as " + self.appoint_type.name]

        elif self.button_type == constants.FIRE_MINISTER_BUTTON:
            return [
                "Fires this minister, incurring a public opinion penalty based on their social status",
            ]

        elif self.button_type == constants.REAPPOINT_MINISTER_BUTTON:
            return [
                "Removes this minister from their current office, allowing them to be reappointed",
                "If this minister is not reappointed by the end of the turn, they will be automatically fired",
            ]

        elif self.button_type == constants.TO_TRIAL_BUTTON:
            return [
                "Opens the trial planning screen to attempt to imprison this minister for corruption",
                "A trial has a higher success chance as more evidence of that minister's corruption is found",
                f"While entering this screen is free, a trial costs {constants.action_prices['trial']} money once started",
                "Each trial attempted doubles the cost of other trials in the same turn",
            ]

        elif self.button_type == constants.FABRICATE_EVIDENCE_BUTTON:
            if constants.current_game_mode == constants.TRIAL_MODE:
                return [
                    f"Creates a unit of fake evidence against this minister to improve the trial's success chance for {self.get_cost()} money",
                    "Each piece of evidence fabricated in a trial becomes increasingly expensive.",
                    "Unlike real evidence, fabricated evidence disappears at the end of the turn and is never preserved after a failed trial",
                ]
            else:
                return ["placeholder"]

        elif self.button_type == constants.BRIBE_JUDGE_BUTTON:
            return [
                f"Bribes the judge of the next trial this turn for {self.get_cost()} money",
                "While having unpredictable results, bribing the judge may swing the trial in your favor or blunt the defense's efforts to do the same",
            ]

        elif self.button_type == constants.RENAME_SETTLEMENT_BUTTON:
            return ["Renames this settlement"]

        elif self.button_type == constants.RENAME_PLANET_BUTTON:
            return ["Renames this planet"]

        elif self.button_type == constants.SHOW_PREVIOUS_REPORTS_BUTTON:
            return [
                "Displays the previous turn's production, sales, and financial reports"
            ]

        elif self.button_type in [
            constants.ENABLE_SENTRY_MODE_BUTTON,
            constants.DISABLE_SENTRY_MODE_BUTTON,
        ]:
            if self.button_type == constants.ENABLE_SENTRY_MODE_BUTTON:
                verb = "enable"
            elif self.button_type == constants.DISABLE_SENTRY_MODE_BUTTON:
                verb = "disable"
            return [
                utility.capitalize(verb) + "s sentry mode for this unit",
                "A unit in sentry mode is removed from the turn order and will be skipped when cycling through unmoved units",
            ]

        elif self.button_type in [
            constants.ENABLE_AUTOMATIC_REPLACEMENT_BUTTON,
            constants.DISABLE_AUTOMATIC_REPLACEMENT_BUTTON,
        ]:
            if self.button_type == constants.ENABLE_AUTOMATIC_REPLACEMENT_BUTTON:
                verb = "enable"
                operator = "not "
            elif self.button_type == constants.DISABLE_AUTOMATIC_REPLACEMENT_BUTTON:
                verb = "disable"
                operator = ""
            if self.target_type == "unit":
                target = "unit"
            else:
                target = "unit's " + self.target_type  # worker or officer
            return [
                f"{utility.capitalize(verb)}s automatic replacement for this {target}",
                "A unit with automatic replacement will be automatically replaced if it dies from attrition",
                f"This {target} is currently set to {operator}be automatically replaced",
            ]

        elif self.button_type == constants.WAKE_UP_ALL_BUTTON:
            return [
                "Disables sentry mode for all units",
                "A unit in sentry mode is removed from the turn order and will be skipped when cycling through unmoved units",
            ]

        elif self.button_type == constants.END_UNIT_TURN_BUTTON:
            return [
                "Ends this unit's turn, skipping it when cycling through unmoved units for the rest of the turn"
            ]

        elif self.button_type == constants.CLEAR_AUTOMATIC_ROUTE_BUTTON:
            return ["Removes this unit's currently designated movement route"]

        elif self.button_type == constants.DRAW_AUTOMATIC_ROUTE_BUTTON:
            return [
                "Starts customizing a new movement route for this unit",
                "Add to the route by clicking on valid locations adjacent to the current destination",
                "The start is outlined in purple, the destination is outlined in yellow, and the path is outlined in blue",
                "When moving along its route, a unit will pick up as many items as possible at the start and drop them at the destination",
                "A unit may not be able to move along its route because of enemy units, a lack of movement points, or not having any items to pick up at the start",
            ]

        elif self.button_type == constants.EXECUTE_AUTOMATIC_ROUTE_BUTTON:
            return ["Moves this unit along its currently designated movement route"]

        elif self.button_type == constants.GENERATE_CRASH_BUTTON:
            return ["Exits the game"]

        elif self.button_type == constants.MINIMIZE_INTERFACE_COLLECTION_BUTTON:
            if self.parent_collection.minimized:
                verb = "Opens"
            else:
                verb = "Minimizes"
            return [f"{verb} the {self.parent_collection.description}"]

        elif self.button_type == constants.MOVE_INTERFACE_COLLECTION_BUTTON:
            if self.parent_collection.move_with_mouse_config["moving"]:
                verb = "Stops moving"
            else:
                verb = "Moves"
            return [f"{verb} the {self.parent_collection.description}"]

        elif self.button_type == constants.RESET_INTERFACE_COLLECTION_BUTTON:
            return [
                f"Resets the {self.parent_collection.description} to its original location"
            ]

        elif self.button_type == constants.TAB_BUTTON:
            if hasattr(self.linked_element, "description"):
                description = f"{self.linked_element.tab_button.tab_name} panel"
            else:
                description = "attached panel"
            return ["Displays the " + description]

        elif self.button_type == constants.CYCLE_AUTOFILL_BUTTON:
            if self.parent_collection.autofill_actors.get(
                self.autofill_target_type, None
            ):
                amount = 1
                if self.autofill_target_type == constants.WORKER_PERMISSION:
                    amount = 2
                verb = utility.conjugate("be", amount, "preterite")  # was or were
                return [
                    f"The {self.parent_collection.autofill_actors[self.autofill_target_type].name} here {verb} automatically selected for the {self.parent_collection.autofill_actors[constants.AUTOFILL_PROCEDURE]} procedure",
                    f"Press to cycle to the next available choice",
                ]
        elif self.button_type == constants.CHANGE_PARAMETER_BUTTON:
            return [
                f"Changes this location's {self.attached_label.actor_label_type.removesuffix('_label').replace('_', ' ')} by {self.change}"
            ]
        else:
            return ["placeholder"]

    def set_keybind(self, new_keybind):
        """
        Description:
            Records a string version of the inputted pygame key object, allowing in-game descriptions of keybind to be shown
        Input:
            pygame key object new_keybind: The keybind id that activates this button, like pygame.K_n
        Output:
            None
        """
        keybind_name_dict = {
            pygame.K_a: "a",
            pygame.K_b: "b",
            pygame.K_c: "c",
            pygame.K_d: "d",
            pygame.K_e: "e",
            pygame.K_f: "f",
            pygame.K_g: "g",
            pygame.K_h: "h",
            pygame.K_i: "i",
            pygame.K_j: "j",
            pygame.K_k: "k",
            pygame.K_l: "l",
            pygame.K_m: "m",
            pygame.K_n: "n",
            pygame.K_o: "o",
            pygame.K_p: "p",
            pygame.K_q: "q",
            pygame.K_r: "r",
            pygame.K_s: "s",
            pygame.K_t: "t",
            pygame.K_u: "u",
            pygame.K_v: "v",
            pygame.K_w: "w",
            pygame.K_x: "x",
            pygame.K_y: "y",
            pygame.K_z: "z",
            pygame.K_DOWN: "down arrow",
            pygame.K_UP: "up arrow",
            pygame.K_LEFT: "left arrow",
            pygame.K_RIGHT: "right arrow",
            pygame.K_1: "1",
            pygame.K_2: "2",
            pygame.K_3: "3",
            pygame.K_4: "4",
            pygame.K_5: "5",
            pygame.K_6: "6",
            pygame.K_7: "7",
            pygame.K_8: "8",
            pygame.K_9: "9",
            pygame.K_0: "0",
            pygame.K_SPACE: "space",
            pygame.K_RETURN: "enter",
            pygame.K_TAB: "tab",
            pygame.K_ESCAPE: "escape",
            pygame.K_F1: "f1",
            pygame.K_F2: "f2",
            pygame.K_F3: "f3",
        }
        self.keybind_name = keybind_name_dict[new_keybind]

    @property
    def batch_tooltip_list(self):
        """
        Gets a 2D list of strings to use as this object's tooltip
            Each string is displayed on a separate line, while each sublist is displayed in a separate box
        """
        if self.has_keybind:
            return [self.tooltip_text + [f"Press {self.keybind_name} to use."]]
        else:
            return [self.tooltip_text]

    def touching_mouse(self):
        """
        Description:
            Returns whether this button is colliding with the mouse
        Input:
            None
        Output:
            boolean: Returns True if this button is colliding with the mouse, otherwise returns False
        """
        if self.Rect.collidepoint(pygame.mouse.get_pos()):  # if mouse is in button
            return True
        else:
            return False

    def can_show_tooltip(self):
        """
        Returns whether this button's tooltip can be shown. By default, its tooltip can be shown when it is visible and colliding with the mouse
        """
        if self.touching_mouse() and self.showing:
            return True
        else:
            return False

    def draw(self, allow_show_outline=True):
        """
        Draws this button with a description of its keybind if it has one, along with an outline if its keybind is being pressed
        """
        if self.showing:
            if self.showing_outline and allow_show_outline:
                pygame.draw.rect(
                    constants.game_display,
                    constants.color_dict[constants.COLOR_WHITE],
                    self.outline,
                    width=2,
                )
            if self.showing_background and hasattr(self, "color"):
                pygame.draw.rect(constants.game_display, self.color, self.Rect)
            self.image.draw()
            if (
                self.has_keybind
            ):  # The key to which a button is bound will appear on the button's image
                message = self.keybind_name
                color = constants.COLOR_WHITE
                textsurface = constants.myfont.pygame_font.render(
                    message, False, constants.color_dict[color]
                )
                constants.game_display.blit(
                    textsurface,
                    (
                        self.x + scaling.scale_width(10),
                        (
                            constants.display_height
                            - (self.y + self.height - scaling.scale_height(5))
                        ),
                    ),
                )

    def on_rmb_click(self):
        """
        Controls this button's behavior when right clicked. By default, the button's right click behavior is the same as its left click behavior.
        """
        self.on_click()

    def on_click(self, override_action_possible: bool = False):
        """
        Description:
            Controls this button's behavior when left clicked. This behavior depends on the button's button_type
        Input:
            boolean override_action_possible: Whether to ignore the action_possible check, used in special on_click calls
        Output:
            None
        """
        if self.button_type in [
            constants.MOVE_UP_BUTTON,
            constants.MOVE_LEFT_BUTTON,
            constants.MOVE_DOWN_BUTTON,
            constants.MOVE_RIGHT_BUTTON,
        ]:
            x_change = 0
            y_change = 0
            if self.button_type == constants.MOVE_LEFT_BUTTON:
                x_change = -1
            elif self.button_type == constants.MOVE_RIGHT_BUTTON:
                x_change = 1
            elif self.button_type == constants.MOVE_UP_BUTTON:
                y_change = 1
            elif self.button_type == constants.MOVE_DOWN_BUTTON:
                y_change = -1
            if main_loop_utility.action_possible():
                if status.displayed_mob.check_action_survivability(notify=True):
                    if minister_utility.positions_filled():
                        current_mob = status.displayed_mob
                        if current_mob:
                            if constants.current_game_mode == constants.STRATEGIC_MODE:
                                if current_mob.can_move(
                                    x_change, y_change, can_print=False
                                ):
                                    current_mob.move(x_change, y_change)
                                    flags.show_selection_outlines = True
                                    constants.last_selection_outline_switch = (
                                        constants.current_time
                                    )
                                    current_mob.set_permission(
                                        constants.SENTRY_MODE_PERMISSION, False
                                    )
                                    current_mob.clear_automatic_route()

                                elif current_mob.get_permission(
                                    constants.VEHICLE_PERMISSION
                                ):  # If moving into unreachable land, have each passenger attempt to move
                                    if current_mob.subscribed_passengers:
                                        passengers = (
                                            current_mob.subscribed_passengers.copy()
                                        )
                                        current_mob.eject_passengers()
                                        last_moved = None
                                        for current_passenger in passengers:
                                            if (
                                                not status.displayed_notification
                                            ) and current_passenger.can_move(
                                                x_change, y_change, can_print=True
                                            ):
                                                current_passenger.move(
                                                    x_change, y_change
                                                )
                                                last_moved = current_passenger
                                        if (
                                            not status.displayed_notification
                                        ):  # If attacking, don't reembark
                                            for current_passenger in passengers:
                                                if (
                                                    current_passenger.location
                                                    == current_mob.location
                                                ):
                                                    current_passenger.embark_vehicle(
                                                        current_mob
                                                    )
                                        if (
                                            last_moved
                                            and not last_moved.get_permission(
                                                constants.IN_VEHICLE_PERMISSION
                                            )
                                        ):
                                            last_moved.select()
                                        flags.show_selection_outlines = True
                                        constants.last_selection_outline_switch = (
                                            constants.current_time
                                        )
                                    else:
                                        text_utility.print_to_screen(
                                            "This vehicle has no passengers to send onto land"
                                        )

                                else:
                                    current_mob.can_move(
                                        x_change, y_change, can_print=True
                                    )
                            else:
                                text_utility.print_to_screen(
                                    "You cannot move while in the Earth HQ screen."
                                )
                        else:
                            text_utility.print_to_screen(
                                "There are no selected units to move."
                            )
            else:
                text_utility.print_to_screen("You are busy and cannot move.")

        elif self.button_type == constants.EXECUTE_MOVEMENT_ROUTES_BUTTON:
            if main_loop_utility.action_possible():
                if minister_utility.positions_filled():
                    if not constants.current_game_mode == constants.STRATEGIC_MODE:
                        game_transitions.set_game_mode(constants.STRATEGIC_MODE)

                    unit_types = [
                        constants.PORTERS,
                        constants.SPACESHIP,
                        constants.TRAIN,
                    ]
                    moved_units = {}
                    attempted_units = {}
                    for current_unit_type in unit_types:
                        moved_units[current_unit_type] = 0
                        attempted_units[current_unit_type] = 0
                    last_moved = None
                    for current_pmob in status.pmob_list:
                        if len(current_pmob.base_automatic_route) > 0:
                            unit_type = current_pmob.unit_type.key
                            attempted_units[unit_type] += 1

                            progressed = current_pmob.follow_automatic_route()
                            if progressed:
                                moved_units[unit_type] += 1
                                last_moved = current_pmob
                            current_pmob.remove_from_turn_queue()
                    if last_moved:
                        last_moved.select()  # updates mob info display if automatic route changed anything
                    types_moved = 0
                    text = ""
                    for current_unit_type in unit_types:
                        if attempted_units[current_unit_type] > 0:

                            if current_unit_type == constants.PORTERS:
                                singular = "unit of porters"
                                plural = "units of porters"
                            else:
                                singular = current_unit_type
                                plural = singular + "s"
                            types_moved += 1
                            num_attempted = attempted_units[current_unit_type]
                            num_progressed = moved_units[current_unit_type]
                            if num_attempted == num_progressed:
                                if num_attempted == 1:
                                    text += f"The {singular} made progress on its designated movement route. /n /n"
                                else:
                                    text += f"All {num_attempted} of the {plural} made progress on their designated movement routes. /n /n"
                            else:
                                if num_progressed == 0:
                                    if num_attempted == 1:
                                        text += f"The {singular} made no progress on its designated movement route. /n /n"
                                    else:
                                        text += f"None of the {plural} made progress on their designated movement routes. /n /n"
                                else:
                                    text += f"Only {num_progressed} of the {num_attempted} {plural} made progress on their designated movement routes. /n /n"
                    transportation_minister = minister_utility.get_minister(
                        constants.TRANSPORTATION_MINISTER
                    )
                    if types_moved > 0:
                        transportation_minister.display_message(text)
                    else:
                        transportation_minister.display_message(
                            "There were no units with designated movement routes. /n /n"
                        )
            else:
                text_utility.print_to_screen("You are busy and cannot move units.")

        elif self.button_type == constants.REMOVE_WORK_CREW_BUTTON:
            if self.attached_label.attached_building:
                if (
                    not len(self.attached_label.attached_building.contained_workers)
                    == 0
                ):
                    self.attached_label.attached_building.contained_workers[
                        0
                    ].leave_building(self.attached_label.attached_building)
                else:
                    text_utility.print_to_screen(
                        "There are no workers to remove from this building."
                    )

        elif self.button_type == constants.END_TURN_BUTTON:
            if main_loop_utility.action_possible():
                if minister_utility.positions_filled():
                    if not constants.current_game_mode == constants.STRATEGIC_MODE:
                        game_transitions.set_game_mode(constants.STRATEGIC_MODE)
                    turn_management_utility.end_turn_warnings()

                    choice_info_dict = {"type": "end turn"}

                    constants.NotificationManager.display_notification(
                        {
                            "message": "Are you sure you want to end your turn? ",
                            "choices": [constants.CHOICE_END_TURN_BUTTON, None],
                            "extra_parameters": choice_info_dict,
                        }
                    )

            else:
                text_utility.print_to_screen("You are busy and cannot end your turn.")

        elif self.button_type == constants.CHOICE_END_TURN_BUTTON:
            turn_management_utility.end_turn()

        elif self.button_type in [
            constants.PICK_UP_EACH_ITEM_BUTTON,
            constants.DROP_EACH_ITEM_BUTTON,
        ]:
            if self.button_type == constants.PICK_UP_EACH_ITEM_BUTTON:
                source_type = "location_inventory"
            else:
                source_type = "mob_inventory"
            item_types.transfer(
                source_type, transferred_item=None, amount=None
            )  # Transfer all of each type
            if status.displayed_location_inventory:
                status.displayed_location_inventory.on_click()
            if status.displayed_mob_inventory:
                status.displayed_mob_inventory.on_click()

        elif self.button_type in [
            constants.SELL_ITEM_BUTTON,
            constants.SELL_ALL_ITEM_BUTTON,
            constants.SELL_EACH_ITEM_BUTTON,
        ]:
            if self.button_type == constants.SELL_EACH_ITEM_BUTTON:
                sold_item_types = [
                    current_item_type
                    for current_item_type in status.item_types.values()
                    if current_item_type.can_sell
                ]
            elif self.button_type in [
                constants.SELL_ITEM_BUTTON,
                constants.SELL_ALL_ITEM_BUTTON,
            ]:
                sold_item_types = [self.attached_label.actor.current_item]
            if minister_utility.positions_filled():
                for current_item_type in sold_item_types:
                    num_present: int = status.displayed_location.get_inventory(
                        current_item_type
                    )
                    if num_present > 0:
                        num_sold: int
                        if self.button_type == constants.SELL_ITEM_BUTTON:
                            num_sold = 1
                        else:
                            num_sold = num_present
                        market_utility.sell(
                            status.displayed_location, current_item_type, num_sold
                        )

                actor_utility.calibrate_actor_info_display(
                    status.location_info_display, status.displayed_location
                )
                if (
                    status.displayed_location_inventory
                    and status.displayed_location_inventory.current_item
                ):
                    actor_utility.calibrate_actor_info_display(
                        status.location_inventory_info_display,
                        status.displayed_location_inventory,
                    )
                else:
                    actor_utility.calibrate_actor_info_display(
                        status.location_inventory_info_display, None
                    )

        elif self.button_type == constants.USE_EACH_EQUIPMENT_BUTTON:
            if main_loop_utility.action_possible():
                if status.displayed_mob and status.displayed_mob.get_permission(
                    constants.PMOB_PERMISSION
                ):
                    for equipment_type in status.equipment_types.values():
                        if status.displayed_location.get_inventory(equipment_type) > 0:
                            if equipment_type.check_requirement(status.displayed_mob):
                                if not status.displayed_mob.equipment.get(
                                    equipment_type.key, False
                                ):
                                    # If equipment in location, equippable by this unit, and not already equipped, equip it
                                    radio_effect = (
                                        status.displayed_mob.get_radio_effect()
                                    )
                                    equipment_type.equip(status.displayed_mob)
                                    if (
                                        radio_effect
                                        != status.displayed_mob.get_radio_effect()
                                    ):  # If radio effect changed, play new voice line
                                        status.displayed_mob.selection_sound()
                                    status.displayed_location.change_inventory(
                                        equipment_type, -1
                                    )
                                    actor_utility.calibrate_actor_info_display(
                                        status.location_info_display,
                                        status.displayed_location,
                                    )
                                    actor_utility.calibrate_actor_info_display(
                                        status.mob_info_display, status.displayed_mob
                                    )
                                    actor_utility.select_interface_tab(
                                        status.mob_tabbed_collection,
                                        status.mob_inventory_collection,
                                    )
                                    if (
                                        status.displayed_location_inventory
                                        and status.displayed_location_inventory.current_item
                                    ):
                                        actor_utility.calibrate_actor_info_display(
                                            status.location_inventory_info_display,
                                            status.displayed_location_inventory,
                                        )
                                    else:
                                        actor_utility.calibrate_actor_info_display(
                                            status.location_inventory_info_display, None
                                        )

        elif self.button_type == constants.USE_EQUIPMENT_BUTTON:
            if main_loop_utility.action_possible():
                if status.displayed_mob and status.displayed_mob.get_permission(
                    constants.PMOB_PERMISSION
                ):
                    equipment = self.attached_label.actor.current_item
                    if equipment.check_requirement(status.displayed_mob):
                        if not status.displayed_mob.equipment.get(equipment.key, False):
                            radio_effect = status.displayed_mob.get_radio_effect()
                            equipment.equip(status.displayed_mob)
                            if (
                                radio_effect != status.displayed_mob.get_radio_effect()
                            ):  # If radio effect changed, play new voice line
                                status.displayed_mob.selection_sound()
                            status.displayed_location.change_inventory(equipment, -1)
                            actor_utility.calibrate_actor_info_display(
                                status.location_info_display, status.displayed_location
                            )
                            actor_utility.calibrate_actor_info_display(
                                status.mob_info_display, status.displayed_mob
                            )
                            actor_utility.select_interface_tab(
                                status.mob_tabbed_collection,
                                status.mob_inventory_collection,
                            )
                            if (
                                status.displayed_location_inventory
                                and status.displayed_location_inventory.current_item
                            ):
                                actor_utility.calibrate_actor_info_display(
                                    status.location_inventory_info_display,
                                    status.displayed_location_inventory,
                                )
                            else:
                                actor_utility.calibrate_actor_info_display(
                                    status.location_inventory_info_display, None
                                )
                        else:
                            text_utility.print_to_screen(
                                f"This unit already has {equipment.key} equipped."
                            )
                    else:
                        text_utility.print_to_screen(
                            f"This type of unit can not equip {equipment.key}."
                        )
                else:
                    text_utility.print_to_screen(
                        "There is no unit to use this equipment."
                    )
            else:
                text_utility.print_to_screen(
                    "You are busy and cannot transfer equipment."
                )

        elif self.button_type == constants.REMOVE_EQUIPMENT_BUTTON:
            if main_loop_utility.action_possible():
                radio_effect = status.displayed_mob.get_radio_effect()
                self.equipment_type.unequip(status.displayed_mob)
                if (
                    radio_effect != status.displayed_mob.get_radio_effect()
                ):  # If radio effect changed, play new voice line
                    status.displayed_mob.selection_sound()
                status.displayed_location.change_inventory(self.equipment_type, 1)
                actor_utility.calibrate_actor_info_display(
                    status.mob_info_display, status.displayed_mob
                )
            else:
                text_utility.print_to_screen(
                    "You are busy and cannot transfer equipment."
                )

        elif self.button_type == constants.CYCLE_UNITS_BUTTON:
            if main_loop_utility.action_possible():
                game_transitions.cycle_player_turn()
            else:
                text_utility.print_to_screen(
                    "You are busy and cannot cycle through units."
                )

        elif self.button_type == constants.NEW_GAME_BUTTON:
            if constants.current_game_mode == constants.NEW_GAME_SETUP_MODE:
                constants.SaveLoadManager.new_game()
            else:
                game_transitions.set_game_mode(constants.NEW_GAME_SETUP_MODE)

        elif self.button_type == constants.SAVE_GAME_BUTTON:
            if main_loop_utility.action_possible():
                constants.SaveLoadManager.save_game("save1.pickle")
                constants.NotificationManager.display_notification(
                    {
                        "message": "Game successfully saved to save1.pickle /n /n",
                    }
                )
            else:
                text_utility.print_to_screen("You are busy and cannot save the game")

        elif self.button_type == constants.LOAD_GAME_BUTTON:
            constants.SaveLoadManager.load_game("save1.pickle")

        elif self.button_type == constants.CHOICE_FIRE_BUTTON:
            fired_unit = status.displayed_mob
            fired_unit.fire()

        elif self.button_type == constants.CHOICE_CONFIRM_MAIN_MENU_BUTTON:
            game_transitions.to_main_menu()

        elif self.button_type == constants.CHOICE_QUIT_BUTTON:
            flags.crashed = True

        elif self.button_type == constants.WAKE_UP_ALL_BUTTON:
            if main_loop_utility.action_possible():
                for current_pmob in status.pmob_list:
                    current_pmob.set_permission(constants.SENTRY_MODE_PERMISSION, False)
                actor_utility.calibrate_actor_info_display(
                    status.mob_info_display, status.displayed_mob
                )
            else:
                text_utility.print_to_screen(
                    "You are busy and cannot disable sentry mode."
                )

        elif self.button_type == constants.CHOICE_CONFIRM_FIRE_MINISTER_BUTTON:
            status.displayed_minister.respond("fired")
            status.displayed_minister.appoint(None, update_display=False)
            status.displayed_minister.remove()
            minister_utility.calibrate_minister_info_display(None)

        elif self.button_type == constants.GENERATE_CRASH_BUTTON:
            if constants.EffectManager.effect_active("enable_crash_button"):
                print(1 / 0)
            else:
                flags.crashed = True

        elif self.button_type == constants.MINIMIZE_INTERFACE_COLLECTION_BUTTON:
            self.attached_collection.minimized = not self.attached_collection.minimized
            if not self.attached_collection.minimized:
                # If any movement within the collection occurred while minimized, makes sure all newly shown elements are at their correct locations
                self.attached_collection.set_origin(
                    self.parent_collection.x, self.parent_collection.y
                )

        elif self.button_type == constants.MOVE_INTERFACE_COLLECTION_BUTTON:
            if self.parent_collection.move_with_mouse_config["moving"]:
                self.parent_collection.move_with_mouse_config = {"moving": False}
            else:
                x, y = pygame.mouse.get_pos()
                y = constants.display_height - y
                self.parent_collection.move_with_mouse_config = {
                    "moving": True,
                    "mouse_x_offset": self.parent_collection.x - x,
                    "mouse_y_offset": self.parent_collection.y - y,
                }

        elif self.button_type == constants.RESET_INTERFACE_COLLECTION_BUTTON:
            if not self.parent_collection.has_parent_collection:
                self.parent_collection.set_origin(
                    self.parent_collection.original_coordinates[0],
                    self.parent_collection.original_coordinates[1],
                )
            else:
                self.parent_collection.set_origin(
                    self.parent_collection.parent_collection.x
                    + self.parent_collection.original_offsets[0],
                    self.parent_collection.parent_collection.y
                    + self.parent_collection.original_offsets[1],
                )
            for (
                member
            ) in (
                self.parent_collection.members
            ):  # only goes down 1 layer - should modify to recursively iterate through each item below parent in hierarchy
                if hasattr(member, "original_offsets"):
                    member.set_origin(
                        member.parent_collection.x + member.original_offsets[0],
                        member.parent_collection.y + member.original_offsets[1],
                    )

        elif self.button_type == constants.TAB_BUTTON:
            tabbed_collection = self.parent_collection.parent_collection
            tabbed_collection.current_tabbed_member = self.linked_element
            if (
                self.identifier == constants.INVENTORY_PANEL
                and constants.EffectManager.effect_active("link_inventory_tabs")
            ):
                if tabbed_collection == status.mob_tabbed_collection:
                    alternate_collection = status.location_tabbed_collection
                else:
                    alternate_collection = status.mob_tabbed_collection
                for linked_tab in alternate_collection.tabbed_members:
                    linked_tab_button = linked_tab.linked_tab_button
                    if linked_tab_button.identifier == constants.INVENTORY_PANEL:
                        linked_tab_button.parent_collection.parent_collection.current_tabbed_member = (
                            linked_tab_button.linked_element
                        )
                if (
                    alternate_collection == status.mob_tabbed_collection
                ):  # Manually calibrate tab name banner label to new tab name
                    alternate_collection.tabs_collection.members[-1].calibrate(
                        status.displayed_mob
                    )
                elif alternate_collection == status.location_tabbed_collection:
                    alternate_collection.tabs_collection.members[-1].calibrate(
                        status.displayed_location
                    )
            if (
                tabbed_collection == status.mob_tabbed_collection
            ):  # Manually calibrate tab name banner label to new tab name
                tabbed_collection.tabs_collection.members[-1].calibrate(
                    status.displayed_mob
                )
            elif tabbed_collection == status.location_tabbed_collection:
                tabbed_collection.tabs_collection.members[-1].calibrate(
                    status.displayed_location
                )

        elif self.button_type == constants.RENAME_SETTLEMENT_BUTTON:
            if override_action_possible or main_loop_utility.action_possible():
                constants.message = status.displayed_location.settlement.name
                constants.InputManager.start_receiving_input(
                    status.displayed_location.settlement.rename,
                    prompt="Type a new name for your settlement: ",
                )
            else:
                text_utility.print_to_screen(
                    "You are busy and cannot rename this settlement."
                )

        elif self.button_type == constants.RENAME_PLANET_BUTTON:
            if override_action_possible or main_loop_utility.action_possible():
                constants.message = status.displayed_location.true_world_handler.name
                constants.InputManager.start_receiving_input(
                    status.displayed_location.true_world_handler.rename,
                    prompt="Type a new name for this planet: ",
                )
            else:
                text_utility.print_to_screen(
                    "You are busy and cannot rename this planet."
                )

    def on_rmb_release(self):
        """
        Controls what this button does when right clicked and released. By default, buttons will stop showing their outlines when released.
        """
        self.on_release()

    def on_release(self):
        """
        Controls what this button does when left clicked and released. By default, buttons will stop showing their outlines when released.
        """
        self.showing_outline = False
        self.has_released = True
        self.being_pressed = False

    def remove(self):
        """
        Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        """
        super().remove()
        status.button_list = utility.remove_from_list(status.button_list, self)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button can be shown. By default, it can be shown during game modes in which this button can appear
        Input:
            None
        Output:
            boolean: Returns True if this button can appear during the current game mode, otherwise returns False
        """
        # Currently, these buttons are not being used anywhere. For these to be functional, they will need to be changed to modify x_offset and y_offset rather than just origin, since all actor display collections are now in a parent collection
        if (
            self.button_type == constants.MOVE_INTERFACE_COLLECTION_BUTTON
            and self.parent_collection.move_with_mouse_config["moving"]
        ):
            x, y = pygame.mouse.get_pos()
            y = constants.display_height - y
            destination_x, destination_y = (
                x + self.parent_collection.move_with_mouse_config["mouse_x_offset"],
                y + self.parent_collection.move_with_mouse_config["mouse_y_offset"],
            )
            self.parent_collection.set_origin(destination_x, destination_y)

        if super().can_show(skip_parent_collection=skip_parent_collection):
            if self.button_type in [
                constants.MOVE_UP_BUTTON,
                constants.MOVE_DOWN_BUTTON,
                constants.MOVE_LEFT_BUTTON,
                constants.MOVE_RIGHT_BUTTON,
            ]:
                if (
                    status.displayed_mob == None
                    or (
                        not status.displayed_mob.get_permission(
                            constants.PMOB_PERMISSION
                        )
                    )
                    or status.displayed_mob.location.is_abstract_location
                ):
                    return False
            elif self.button_type in [
                constants.SELL_ITEM_BUTTON,
                constants.SELL_ALL_ITEM_BUTTON,
            ]:
                return (
                    status.displayed_location
                    and status.displayed_location.is_earth_location
                    and self.attached_label.actor.current_item.can_sell
                )
            elif self.button_type == constants.SELL_EACH_ITEM_BUTTON:
                if (
                    status.displayed_location
                    and status.displayed_location.is_earth_location
                ):
                    for current_item_type in status.displayed_location.get_held_items():
                        if current_item_type.can_sell:
                            return True
                return False
            elif self.button_type in [
                constants.PICK_UP_EACH_ITEM_BUTTON,
                constants.DROP_EACH_ITEM_BUTTON,
            ]:
                return self.attached_label.actor.get_inventory_used() > 0
            elif self.button_type == constants.USE_EQUIPMENT_BUTTON:
                return (
                    self.attached_label.actor.current_item.key in status.equipment_types
                )
            elif self.button_type == constants.USE_EACH_EQUIPMENT_BUTTON:
                if status.displayed_mob:
                    held_items = status.displayed_location.get_held_items()
                    return any(
                        [
                            equipment_type in held_items
                            and equipment_type.check_requirement(status.displayed_mob)
                            for equipment_type in status.equipment_types.values()
                        ]
                    )
                return False
            elif self.button_type == constants.RENAME_PLANET_BUTTON:
                if (
                    status.displayed_location
                    and status.displayed_location.is_abstract_location
                    and (not status.displayed_location.is_earth_location)
                ):
                    return True
                return False
            return True
        return False


class remove_equipment_button(button):
    """
    Button linked to a particular equipment type that can unequip it when equipped, and shows that is is equipped
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = None: pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'equipment_type': string value - Type of equipment, like 'rifles'
        Output:
            None
        """
        self.equipment_type: equipment_types.equipment_type = input_dict[
            "equipment_type"
        ]
        super().__init__(input_dict)

    def can_show(self):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: If superclass would show, returns True if the selected unit has this button's equipment type equipped
        """
        return (
            super().can_show()
            and self.attached_label.actor.get_permission(constants.PMOB_PERMISSION)
            and self.attached_label.actor.equipment.get(self.equipment_type.key, False)
        )


class end_turn_button(button):
    """
    Button that ends the turn when pressed and changes appearance based on the current turn
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = None: pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
        Output:
            None
        """
        super().__init__(input_dict)
        image_input_dict = {
            "attached_image": self,
            "init_type": constants.WARNING_IMAGE,
        }
        if self.parent_collection:
            image_input_dict["parent_collection"] = self.parent_collection
            image_input_dict["member_config"] = {
                "order_exempt": True,
                "order_x_offset": 100,
            }
        self.warning_image = constants.ActorCreationManager.create_interface_element(
            image_input_dict
        )

        self.warning_image.set_image("misc/time_passing.png")
        self.warning_image.to_front = True

    def set_origin(self, new_x, new_y):
        """
        Description:
            Sets this interface element's location and those of its members to the inputted coordinates
        Input:
            int new_x: New x coordinate for this element's origin
            int new_y: New y coordinate for this element's origin
        Output:
            None
        """
        super().set_origin(new_x, new_y)
        if hasattr(self, "warning_image"):
            self.warning_image.set_origin(
                new_x + self.warning_image.order_x_offset,
                new_y + self.warning_image.order_y_offset,
            )

    def can_show_warning(
        self,
    ):  # Show warning if enemy movements or combat are still occurring
        """
        Description:
            Whether this button can show its enemy turn version using the 'warning' system, returning True if is the enemy's turn or if it is the enemy combat phase (not technically during enemy turn)
        Input:
            None
        Output:
            boolean: Returns whether this button's enemy turn version should be shown
        """
        if flags.player_turn and not flags.enemy_combat_phase:
            return False
        return True


class cycle_same_location_button(button):
    """
    Button that appears near the displayed location and cycles the order of mobs displayed in a location
    """

    def on_click(self):
        """
        Controls this button's behavior when clicked. This type of button cycles the order of mobs displayed in a location, moving the first one shown to the bottom and moving others up
        """
        if main_loop_utility.action_possible():
            cycled_location = status.displayed_location
            cycled_location.subscribed_mobs.append(
                cycled_location.subscribed_mobs.pop(0)
            )
            cycled_location.subscribed_mobs[0].cycle_select()
        else:
            text_utility.print_to_screen("You are busy and cannot cycle units.")

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the currently displayed location contains 3 or less mobs. Otherwise, returns same as superclass
        """
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_location = status.displayed_location
            if displayed_location and len(displayed_location.subscribed_mobs) >= 4:
                return True
        return False


class same_location_icon(button):
    """
    Button that appears near the displayed location and selects mobs that are not currently at the top of the location
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = None: pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'index': int value - Index to determine which item of the displayed location's cell's list of contained mobs is selected by this button
                'is_last': boolean value - Whether this is the last of the displayed location's selection icons. If it is last, it will show all mobs are not being shown rather than being
                        attached to a specific mob
        Output:
            None
        """
        self.attached_mob = None
        super().__init__(input_dict)
        self.previous_subscribed_mobs = []
        self.default_image_id = input_dict["image_id"]
        self.index = input_dict["index"]
        self.is_last = input_dict["is_last"]
        if self.is_last:
            self.name_list = []
        status.same_location_icon_list.append(self)

    def reset(self):
        """
        Resets this icon when a new location is selected, forcing it to re-calibrate with any new units
        """
        self.resetting = True

    def on_click(self):
        """
        Controls this button's behavior when clicked. This type of button selects the mob that it is currently attached to when clicked
        """
        if (not self.is_last) and self.attached_mob:
            self.attached_mob.cycle_select()

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if there is no location selected, otherwise returns same as superclass
        """
        self.update()
        return (
            status.displayed_location
            and len(self.previous_subscribed_mobs) > self.index
            and super().can_show()
        )

    def can_show_tooltip(self):
        """
        Returns whether this button's tooltip can be shown. A same location icon has the the normal requirements for a tooltip to be shown, along with requiring that it is attached to a unit
        """
        return self.attached_mob and super().can_show_tooltip()

    def update(self):
        """
        Updates this icon's appearance based on the corresponding unit in the displayed location, if any
        """
        if super().can_show():
            displayed_location = status.displayed_location
            if displayed_location:
                new_subscribed_mobs = displayed_location.subscribed_mobs
                if (
                    new_subscribed_mobs != self.previous_subscribed_mobs
                ) or self.resetting:
                    self.resetting = False
                    self.previous_subscribed_mobs = []
                    for current_item in new_subscribed_mobs:
                        self.previous_subscribed_mobs.append(current_item)
                    if self.is_last and len(new_subscribed_mobs) > self.index:
                        self.attached_mob = "last"
                        self.image.set_image("buttons/extra_selected_button.png")
                        name_list = []
                        for current_mob_index in range(
                            len(self.previous_subscribed_mobs)
                        ):
                            if current_mob_index > self.index - 1:
                                name_list.append(
                                    self.previous_subscribed_mobs[
                                        current_mob_index
                                    ].name
                                )
                        self.name_list = name_list

                    elif len(self.previous_subscribed_mobs) > self.index:
                        self.attached_mob = self.previous_subscribed_mobs[self.index]
                        self.image.set_image(
                            self.attached_mob.image_dict[
                                constants.IMAGE_ID_LIST_FULL_MOB
                            ]
                        )
            else:
                self.attached_mob = None

    def draw(self):
        """
        Draws this button and draws a copy of the this button's attached mob's image on top of it
        """
        if self.showing:
            if self.index == 0 and status.displayed_location:
                if status.displayed_location.subscribed_mobs[0] == status.displayed_mob:
                    pygame.draw.rect(
                        constants.game_display,
                        constants.color_dict[constants.COLOR_BRIGHT_GREEN],
                        self.outline,
                    )
                else:
                    pygame.draw.rect(
                        constants.game_display,
                        constants.color_dict[constants.COLOR_WHITE],
                        self.outline,
                    )
            super().draw()

    @property
    def tooltip_text(self) -> List[List[str]]:
        """
        Provides the tooltip for this object
        """
        if not self.showing:
            return []
        else:
            if self.is_last:
                return ["More: "] + self.name_list
            else:
                return self.attached_mob.tooltip_text + ["Click to select this unit"]


class fire_unit_button(button):
    """
    Button that fires the selected unit, removing it from the game as if it died
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = None: pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
        Output:
            None
        """
        self.attached_mob = None
        super().__init__(input_dict)

    def on_click(self):
        """
        Controls this button's behavior when clicked. This type of button fires the selected unit
        """
        if (
            main_loop_utility.action_possible()
        ):  # When clicked, calibrate minimap to attached mob and move it to the front of each stack
            if self.attached_mob.check_action_survivability(notify=True):
                message = "Are you sure you want to fire this unit? Firing this unit would remove it, any units attached to it, and any associated upkeep from the game. /n /n"
                worker = self.attached_mob.get_worker()
                if worker:
                    if worker.get_permission(constants.GROUP_PERMISSION):
                        worker = worker.worker
                    message += (
                        " /n /n".join(worker.worker_type.fired_description) + " /n /n"
                    )
                constants.NotificationManager.display_notification(
                    {
                        "message": message,
                        "choices": [constants.CHOICE_FIRE_BUTTON, "cancel"],
                    }
                )
        else:
            text_utility.print_to_screen("You are busy and cannot fire a unit")

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if there is a selected unit, otherwise returns False
        """
        if super().can_show(skip_parent_collection=skip_parent_collection):
            if self.attached_mob != status.displayed_mob:
                self.attached_mob = status.displayed_mob
            if self.attached_mob and self.attached_mob.get_permission(
                constants.PMOB_PERMISSION
            ):
                return True
        return False

    @property
    def tooltip_text(self) -> List[List[str]]:
        """
        Provides the tooltip for this object
        """
        if not self.showing:
            return []
        else:
            tooltip_text = ["Click to fire this unit"]
            if self.attached_mob.any_permissions(
                constants.GROUP_PERMISSION, constants.WORKER_PERMISSION
            ):
                tooltip_text.append(
                    "Once fired, this unit will cost no longer cost upkeep"
                )
            elif self.attached_mob.get_permission(constants.VEHICLE_PERMISSION):
                tooltip_text.append(
                    "Firing this unit will also fire all of its passengers."
                )
            return tooltip_text


class switch_game_mode_button(button):
    """
    Button that switches between game modes, like from the strategic map to the minister conference room
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = None: pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'to_mode': string value - Game mode that this button switches to. If this equals 'previous', it switches to the previous game mode rather than a preset one
        Output:
            None
        """
        self.to_mode = input_dict["to_mode"]
        self.to_mode_tooltip_dict = {}
        self.to_mode_tooltip_dict[constants.MAIN_MENU_MODE] = [
            "Exits to the main menu",
            "Does not automatically save the game",
        ]
        self.to_mode_tooltip_dict[constants.STRATEGIC_MODE] = [
            "Enters the strategic map screen"
        ]
        self.to_mode_tooltip_dict[constants.EARTH_MODE] = [
            "Enters the Earth headquarters screen"
        ]
        self.to_mode_tooltip_dict[constants.MINISTERS_MODE] = [
            "Enters the minister conference room screen"
        ]
        super().__init__(input_dict)

    def on_click(self):
        """
        Controls this button's behavior when clicked. This type of button transtions from the current game mode to either the previous game mode or one specified on button initialization
        """
        if main_loop_utility.action_possible():
            if self.to_mode == constants.MAIN_MENU_MODE:
                constants.NotificationManager.display_notification(
                    {
                        "message": "Are you sure you want to exit to the main menu without saving? /n /n",
                        "choices": [constants.CHOICE_CONFIRM_MAIN_MENU_BUTTON, None],
                    }
                )
            if self.to_mode != constants.MAIN_MENU_MODE:
                game_transitions.set_game_mode(self.to_mode)
        else:
            text_utility.print_to_screen("You are busy and cannot switch screens.")

    @property
    def tooltip_text(self) -> List[List[str]]:
        """
        Provides the tooltip for this object
        """
        return utility.copy_list(self.to_mode_tooltip_dict[self.to_mode])

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns whether this button should be drawn
        """
        if self.to_mode != constants.MAIN_MENU_MODE:
            self.showing_outline = constants.current_game_mode == self.to_mode
        return super().can_show(skip_parent_collection=skip_parent_collection)


class minister_portrait_image(button):
    """
    Button that can be calibrated to a minister to show that minister's portrait and selects the minister when clicked
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = None: pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'minister_type': string value - Minister office that this button is linked to, causing this button to always be connected to the minister in that office. If equals None,
                    can be calibrated to an available minister candidate
        Output:
            None
        """
        self.background_image_id = []
        self.empty_image_id = []
        self.current_minister = None
        input_dict["image_id"] = self.empty_image_id
        super().__init__(input_dict)
        self.insert_collection_above()
        self.minister_type: minister_types.minister_type = input_dict[
            "minister_type"
        ]  # Position, like Minister of Space minister_type object
        if self.minister_type:
            self.background_image_id.append("misc/empty.png")
            self.empty_image_id.append("ministers/empty_portrait.png")
            warning_x_offset = 0
        else:  # If available minister portrait
            self.background_image_id.append("misc/empty.png")
            self.empty_image_id.append("ministers/empty_portrait.png")
            if constants.MINISTERS_MODE in self.modes:
                status.available_minister_portrait_list.append(self)
            warning_x_offset = scaling.scale_width(-100)
        status.minister_image_list.append(self)

        self.warning_image = constants.ActorCreationManager.create_interface_element(
            {
                "attached_image": self,
                "init_type": constants.WARNING_IMAGE,
                "parent_collection": self.parent_collection,
                "member_config": {"x_offset": warning_x_offset, "y_offset": 0},
            }
        )
        self.parent_collection.can_show_override = self  # Parent collection is considered showing when this label can show, allowing ordered collection to work correctly

        self.calibrate(None)

    def can_show_warning(self):
        """
        Description:
            Returns whether this image should display its warning image. It should be shown when this image is visible and its attached minister is about to be fired at the end of the turn
        Input:
            None
        Output:
            Returns whether this image should display its warning image
        """
        if self.current_minister:
            if (
                self.current_minister.just_removed
                and not self.current_minister.current_position
            ):
                return True
        elif (
            self.minister_type
        ):  # If portrait in minister table and no minister assigned for office
            return True
        return False

    def draw(self):
        """
        Draws this button's image along with a white background and, if its minister is currently selected, a flashing green outline
        """
        showing = False
        if (
            self.showing and constants.current_game_mode == constants.MINISTERS_MODE
        ):  # Draw outline around portrait if minister selected
            showing = True
            if (
                status.displayed_minister
                and status.displayed_minister == self.current_minister
                and flags.show_selection_outlines
            ):
                pygame.draw.rect(
                    constants.game_display,
                    constants.color_dict[constants.COLOR_BRIGHT_GREEN],
                    self.outline,
                )
        super().draw(
            allow_show_outline=(constants.current_game_mode == constants.MINISTERS_MODE)
        )  # Show outline for selection icons on ministers mode but not the overlapping ones on strategic mode
        if showing and self.warning_image.showing:
            self.warning_image.draw()

    def on_click(self):
        """
        Controls this button's behavior when clicked. This type of button selects its attached minister when clicked
        """
        if main_loop_utility.action_possible():
            if (
                constants.current_game_mode == constants.MINISTERS_MODE
                and self.current_minister
            ):
                self.current_minister.play_voice_line("acknowledgement")
                if (
                    self in status.available_minister_portrait_list
                ):  # if available minister portrait
                    own_index = status.available_minister_list.index(
                        self.current_minister
                    )
                    constants.available_minister_left_index = own_index - 2
                    minister_utility.update_available_minister_display()
                else:  # if cabinet portrait
                    minister_utility.calibrate_minister_info_display(
                        self.current_minister
                    )
            elif (
                constants.current_game_mode != constants.MINISTERS_MODE
            ):  # If clicked while not on ministers screen, go to ministers screen and select that minister
                old_minister = self.current_minister
                game_transitions.set_game_mode(constants.MINISTERS_MODE)
                self.current_minister = old_minister
                if self.current_minister:
                    self.on_click()
        else:
            text_utility.print_to_screen(
                "You are busy and cannot select other ministers."
            )

    def calibrate(self, new_minister):
        """
        Description:
            Attaches this button to the inputted minister and updates this button's image to that of the minister
        Input:
            string/minister new_minister: The minister whose information is matched by this button. If this equals None, this button is detached from any ministers
        Output:
            None
        """
        if (
            new_minister and new_minister.actor_type != constants.MINISTER_ACTOR_TYPE
        ):  # If calibrated to non-minister, attempt to calibrate to that unit's controlling minister
            if hasattr(new_minister, "controlling_minister"):
                new_minister = new_minister.controlling_minister
            else:
                new_minister = None

        if new_minister:
            if constants.MINISTERS_MODE in self.modes:
                self.image.set_image(
                    self.background_image_id
                    + new_minister.image_id
                    + actor_utility.generate_label_image_id(
                        new_minister.get_f_lname(use_prefix=True)
                    )
                )
            else:
                self.image.set_image(new_minister.image_id)
        elif (
            constants.MINISTERS_MODE in self.modes
        ):  # Show empty minister if minister screen icon
            self.image.set_image(self.empty_image_id)
        else:  # If minister icon on strategic mode, no need to show empty minister
            self.image.set_image("misc/empty.png")
        self.current_minister = new_minister

    @property
    def tooltip_text(self) -> List[List[str]]:
        """
        Provides the tooltip for this object
        """
        if self.current_minister:
            return self.current_minister.tooltip_text
        elif self.minister_type:  # If available minister portrait
            return [
                f"No {self.minister_type.name} is currently appointed.",
                f"Without a {self.minister_type.name}, {self.minister_type.skill_type.replace('_', ' ')}-oriented actions are not possible",
            ]
        else:  # If appointed minister portrait
            return ["There is no available candidate in this slot."]


class cycle_available_ministers_button(button):
    """
    Button that cycles through the ministers available to be appointed
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = None: pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'direction': string value - If equals 'right', this button cycles forward in the list of available ministers. If equals 'left', this button cycles backwards in the list of
                    available ministers
        Output:
            None
        """
        self.direction = input_dict["direction"]
        super().__init__(input_dict)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if clicking this button would move more than 1 past the edge of the list of available ministers, otherwise returns same as superclass
        """
        if self.direction == "left":
            if constants.available_minister_left_index > -2:
                return super().can_show(skip_parent_collection=skip_parent_collection)
            else:
                return False
        elif (
            self.direction == "right"
        ):  # left index = 0, left index + 4 = 4 which is greater than the length of a 3-minister list, so can't move right farther
            if not constants.available_minister_left_index + 4 > len(
                status.available_minister_list
            ):
                return super().can_show(skip_parent_collection=skip_parent_collection)
            else:
                return False

    def on_click(self):
        """
        Controls this button's behavior when clicked. This type of button changes the range of available ministers that are displayed depending on its direction
        """
        if main_loop_utility.action_possible():
            if self.direction == "left":
                constants.available_minister_left_index -= 1
            if self.direction == "right":
                constants.available_minister_left_index += 1
            minister_utility.update_available_minister_display()
            status.available_minister_portrait_list[
                2
            ].on_click()  # select new middle portrait
        else:
            text_utility.print_to_screen(
                "You are busy and cannot select other ministers."
            )


class scroll_button(button):
    """
    Button that increments or decrements a particular value of its parent collection
    """

    def __init__(self, input_dict) -> None:
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = None: pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'value_name': str value - Variable name of value being scrolled
                'increment': int value - Amount to change attached value each time button is pressed
        Output:
            None
        """
        self.value_name: str = input_dict["value_name"]
        self.increment: int = input_dict["increment"]
        input_dict["button_type"] = "scroll"
        super().__init__(input_dict)
        if self.increment > 0:
            self.parent_collection.scroll_down_button = self
        elif self.increment < 0:
            self.parent_collection.scroll_up_button = self

    def on_click(self) -> None:
        """
        When this button is clicked, increment/decrement the corresponding value of the parent collection and update its display
        """
        if main_loop_utility.action_possible():
            setattr(
                self.parent_collection,
                self.value_name,
                getattr(self.parent_collection, self.value_name) + self.increment,
            )
            self.parent_collection.scroll_update()

    def can_show(self, skip_parent_collection=False) -> bool:
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns True if this button's attached collection needs to show a scroll button and would otherwise be shown
        """
        return super().can_show(
            skip_parent_collection=skip_parent_collection
        ) and self.parent_collection.show_scroll_button(self)

    @property
    def tooltip_text(self) -> List[List[str]]:
        """
        Provides the tooltip for this object
        """
        if self.increment > 0:
            descriptor = "down"
        elif self.increment < 0:
            descriptor = "up"
        return [
            f"Click to scroll {descriptor} {abs(self.increment)} {self.value_name.replace('_', ' ')}"
        ]


class sellable_item_button(button):
    """
    Button appearing near item sell prices label that can be clicked as a target for advertising campaigns
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = None: pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'item_type': item_type value - Sellable item type that this button corresponds to
        Output:
            None
        """
        self.item_type: item_types.item_type = input_dict["item_type"]
        super().__init__(input_dict)
        self.showing_background = False
        self.outline.width = 0
        self.outline.height = 0
        self.outline.x = 0
        self.outline.y = 0

    def on_click(self):
        """
        Controls this button's behavior when clicked. When the player is choosing a target for an advertising campaign, clicking on this button starts an advertising campaign for this button's item
        """
        if flags.choosing_advertised_item:
            if self.item_type.key == constants.CONSUMER_GOODS_ITEM:
                text_utility.print_to_screen("You cannot advertise consumer goods.")
            else:
                if any(
                    [
                        current_item_type.can_sell
                        and current_item_type.price > 1
                        and current_item_type != self.item_type
                        for current_item_type in status.item_types.values()
                    ]
                ):
                    status.actions["advertising_campaign"].start(
                        status.displayed_mob, self.item_type
                    )
                else:
                    text_utility.print_to_screen(
                        f"You cannot advertise {self.item_type.name} because all other items are already at the minimum price."
                    )

    def can_show_tooltip(self):
        """
        Returns whether this button's tooltip can be shown. A sellable item button never shows a tooltip
        """
        return False


class show_previous_reports_button(button):
    """
    Button appearing near money label that can be clicked to display the previous turn's production, sales, and financial reports again
    """

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False during the first turn when there is no previous financial report to show, otherwise returns same as superclass
        """
        return super().can_show(skip_parent_collection=skip_parent_collection) and (
            status.previous_financial_report
            or status.previous_production_report
            or status.previous_sales_report
        )

    def on_click(self):
        """
        Controls this button's behavior when clicked. This type of button displays the previous turn's financial report again
        """
        if main_loop_utility.action_possible():
            for report in [
                status.previous_production_report,
                status.previous_sales_report,
                status.previous_financial_report,
            ]:
                if report:
                    constants.NotificationManager.display_notification(
                        {
                            "message": report,
                        }
                    )
        else:
            text_utility.print_to_screen(
                "You are busy and cannot view the last turn's reports"
            )


class tab_button(button):
    """
    Button representing an interface tab that is a member of a tabbed collection and is attached to one of its member collections, setting whether it is active
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = None: pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'linked_element': Member collection of tabbed collection that this button is associated with
                'identifier': Key of linked panel, like constants.SETTLEMENT_PANEL or constants.INVENTORY_PANEL
        Output:
            None
        """
        self.linked_element = input_dict["linked_element"]
        self.linked_element.linked_tab_button = self
        self.identifier = input_dict["identifier"]
        self.tab_name = input_dict["tab_name"]
        super().__init__(input_dict)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button can be shown - uses usual can_show logic, but shows outline iff tab is active
        Input:
            None
        Output:
            boolean: Returns True if this button can appear during the current game mode, otherwise returns False
        """
        return_value = super().can_show(skip_parent_collection=skip_parent_collection)
        if return_value:
            if self.identifier == constants.SETTLEMENT_PANEL:
                return_value = bool(
                    status.displayed_location.settlement
                    or status.displayed_location.has_building(constants.INFRASTRUCTURE)
                )

            elif self.identifier == constants.INVENTORY_PANEL:
                if self.linked_element == status.location_inventory_collection:
                    return_value = (
                        status.displayed_location.inventory
                        or status.displayed_location.inventory_capacity > 0
                        or status.displayed_location.infinite_inventory_capacity
                    )
                else:
                    return_value = status.displayed_mob.inventory_capacity > 0 or (
                        flags.enable_equipment_panel
                        and status.displayed_mob.get_permission(
                            constants.PMOB_PERMISSION
                        )
                        and status.displayed_mob.equipment
                    )

            elif self.identifier == constants.REORGANIZATION_PANEL:
                return_value = status.displayed_mob.get_permission(
                    constants.PMOB_PERMISSION
                )
            elif self.identifier == constants.LOCAL_CONDITIONS_PANEL:
                return_value = not status.displayed_location.is_abstract_location
            elif self.identifier in [
                constants.GLOBAL_CONDITIONS_PANEL,
                constants.TEMPERATURE_BREAKDOWN_PANEL,
            ]:
                return_value = status.displayed_location.is_abstract_location

        if (
            self.linked_element
            == self.parent_collection.parent_collection.current_tabbed_member
        ):
            if return_value:
                self.showing_outline = True
            else:
                self.showing_outline = False
                self.parent_collection.parent_collection.current_tabbed_member = None
                for (
                    tabbed_member
                ) in self.parent_collection.parent_collection.tabbed_members:
                    if (
                        tabbed_member != self.linked_element
                        and tabbed_member.linked_tab_button.can_show()
                    ):
                        self.parent_collection.parent_collection.current_tabbed_member = (
                            tabbed_member
                        )
        elif (
            return_value
            and self.parent_collection.parent_collection.current_tabbed_member == None
        ):
            self.on_click()
            self.showing_outline = True
        else:
            self.showing_outline = False

        return return_value


class reorganize_unit_button(button):
    """
    Button that reorganizes 1 or more units into 1 or more other units, based on which are present - such as combining a officer and worker into a group, or crew and vehicle
        into a crewed vehicle
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = None: pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'input_sources': string list value - List of interface elements to use to determine the pmobs to use as formula input
                'output_destinations': string list value - List of interface elements to send formula results to
                'allowed_procedures': string list value - Types of merge/split procedure this button can execute
        Output:
            None
        """
        self.allowed_procedures = input_dict["allowed_procedures"]
        super().__init__(input_dict)
        self.has_button_press_override = True
        self.default_keybind_id = self.keybind_id

    def button_press_override(self):
        """
        Description:
            Allows this button to be pressed via keybind when it is not currently showing, under particular circumstances. Requires the
                has_button_press_override flag to be enabled
        Input:
            None
        Output
        """
        if status.mob_tabbed_collection.showing:
            actor_utility.select_interface_tab(
                status.mob_tabbed_collection, status.mob_reorganization_collection
            )
            return True
        return False

    def enable_shader_condition(self):
        """
        Description:
            Calculates and returns whether this button should display its shader, given that it has shader enabled - reorganize button displays shader when current
                procedure is not in this button's allowed procedures
        Input:
            None
        Output:
            boolean: Returns whether this button should display its shader, given that it has shader enabled
        """
        result = (
            super().enable_shader_condition()
            and not self.parent_collection.autofill_actors[constants.AUTOFILL_PROCEDURE]
            in self.allowed_procedures
        )
        if result:
            self.keybind_id = None
            self.on_release()
        else:
            self.keybind_id = self.default_keybind_id
        return result

    @property
    def tooltip_text(self) -> List[List[str]]:
        """
        Provides the tooltip for this object
        """
        if (
            constants.MERGE_PROCEDURE in self.allowed_procedures
            or constants.CREW_PROCEDURE in self.allowed_procedures
        ):
            tooltip_text = [
                "Combines the units on the left to form the unit on the right"
            ]
        elif (
            constants.SPLIT_PROCEDURE in self.allowed_procedures
            or constants.UNCREW_PROCEDURE in self.allowed_procedures
        ):
            tooltip_text = [
                "Separates the unit on the right to form the units on the left"
            ]
        if (
            self.parent_collection.autofill_actors[constants.AUTOFILL_PROCEDURE]
            in self.allowed_procedures
        ):
            if (
                self.parent_collection.autofill_actors[constants.AUTOFILL_PROCEDURE]
                == constants.MERGE_PROCEDURE
            ):
                if (
                    self.parent_collection.autofill_actors[constants.OFFICER_PERMISSION]
                    and self.parent_collection.autofill_actors[
                        constants.WORKER_PERMISSION
                    ]
                ):
                    tooltip_text.append(
                        f"Press to combine the {self.parent_collection.autofill_actors[constants.OFFICER_PERMISSION].name} and the {self.parent_collection.autofill_actors[constants.WORKER_PERMISSION].name} into a {self.parent_collection.autofill_actors[constants.GROUP_PERMISSION].name}"
                    )
                else:
                    tooltip_text += [
                        "Merging requires both a worker and an officer to be present",
                        "The current combination of units has no valid reorganization procedure",
                    ]
            elif (
                self.parent_collection.autofill_actors[constants.AUTOFILL_PROCEDURE]
                == constants.SPLIT_PROCEDURE
            ):
                tooltip_text.append(
                    f"Press to separate the {self.parent_collection.autofill_actors[constants.GROUP_PERMISSION].name} into a {self.parent_collection.autofill_actors[constants.OFFICER_PERMISSION].name} and {self.parent_collection.autofill_actors[constants.WORKER_PERMISSION].name}"
                )
            elif (
                self.parent_collection.autofill_actors[constants.AUTOFILL_PROCEDURE]
                == constants.CREW_PROCEDURE
            ):
                if (
                    self.parent_collection.autofill_actors[
                        constants.INACTIVE_VEHICLE_PERMISSION
                    ]
                    and self.parent_collection.autofill_actors[
                        constants.CREW_VEHICLE_PERMISSION
                    ]
                ):
                    tooltip_text.append(
                        f"Press to combine the {self.parent_collection.autofill_actors[constants.INACTIVE_VEHICLE_PERMISSION].name} and the {self.parent_collection.autofill_actors[constants.CREW_VEHICLE_PERMISSION].name} into a crewed {self.parent_collection.autofill_actors[constants.ACTIVE_VEHICLE_PERMISSION].name}"
                    )
                else:
                    tooltip_text += [
                        "Crewing a vehicle requires both an uncrewed vehicle and a crew to be present",
                        "The current combination of units has no valid reorganization procedure",
                    ]
            elif (
                self.parent_collection.autofill_actors[constants.AUTOFILL_PROCEDURE]
                == constants.UNCREW_PROCEDURE
            ):
                tooltip_text.append(
                    f"Press to separate the {self.parent_collection.autofill_actors[constants.ACTIVE_VEHICLE_PERMISSION].name} into {self.parent_collection.autofill_actors[constants.CREW_VEHICLE_PERMISSION].name} and a non-crewed {self.parent_collection.autofill_actors[constants.INACTIVE_VEHICLE_PERMISSION].name}"
                )
        elif self.parent_collection.autofill_actors[constants.AUTOFILL_PROCEDURE]:
            tooltip_text.append(
                f"The {self.parent_collection.autofill_actors[constants.AUTOFILL_PROCEDURE]} procedure is controlled by the other button"
            )
        else:
            tooltip_text.append(
                "The current combination of units has no valid reorganization procedure"
            )

        return tooltip_text

    def on_click(self, allow_sound: bool = True):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button completes the determined procedure based
            on the current input cell contents
        Input:
            bool allow_sound = False: Whether the reorganized unit will be allowed to play a selection sound
        Output:
            None
        """
        if main_loop_utility.action_possible():
            procedure_actors = self.parent_collection.autofill_actors
            attempted_procedure_type = procedure_actors[constants.AUTOFILL_PROCEDURE]
            procedure_type = constants.INVALID_PROCEDURE
            if attempted_procedure_type in self.allowed_procedures:
                dummy_autofill_target_to_procedure_dict = {
                    constants.OFFICER_PERMISSION: constants.SPLIT_PROCEDURE,
                    constants.WORKER_PERMISSION: constants.SPLIT_PROCEDURE,
                    constants.GROUP_PERMISSION: constants.MERGE_PROCEDURE,
                    constants.ACTIVE_VEHICLE_PERMISSION: constants.CREW_PROCEDURE,
                    constants.INACTIVE_VEHICLE_PERMISSION: constants.UNCREW_PROCEDURE,
                }
                # Type of procedure to execute if dummy version of corresponding unit found - if a dummy officer is found, the procedure must be a split
                procedure_type = constants.INVALID_PROCEDURE
                for autofill_target_type in dummy_autofill_target_to_procedure_dict:
                    if procedure_actors.get(autofill_target_type, None):
                        if procedure_actors[autofill_target_type].get_permission(
                            constants.DUMMY_PERMISSION
                        ):
                            procedure_type = dummy_autofill_target_to_procedure_dict[
                                autofill_target_type
                            ]
                            break
                if procedure_type == constants.MERGE_PROCEDURE:
                    constants.ActorCreationManager.create_group(
                        procedure_actors[constants.WORKER_PERMISSION],
                        procedure_actors[constants.OFFICER_PERMISSION],
                    ).select()
                    if allow_sound:
                        status.displayed_mob.selection_sound()

                elif procedure_type == constants.CREW_PROCEDURE:
                    if procedure_actors[
                        constants.CREW_VEHICLE_PERMISSION
                    ].get_permission(
                        constants.CREW_PERMISSIONS[
                            procedure_actors[
                                constants.INACTIVE_VEHICLE_PERMISSION
                            ].unit_type.key
                        ]
                    ):
                        procedure_actors[
                            constants.CREW_VEHICLE_PERMISSION
                        ].crew_vehicle(
                            procedure_actors[constants.INACTIVE_VEHICLE_PERMISSION]
                        )
                        if allow_sound:
                            status.displayed_mob.selection_sound()
                    else:
                        text_utility.print_to_screen(
                            f"{procedure_actors[constants.CREW_VEHICLE_PERMISSION].worker_type.name.capitalize()} cannot crew {procedure_actors[constants.INACTIVE_VEHICLE_PERMISSION].unit_type.name}s."
                        )

                elif procedure_type == constants.SPLIT_PROCEDURE:
                    procedure_actors[constants.GROUP_PERMISSION].disband()
                    if allow_sound:
                        status.displayed_mob.selection_sound()

                elif procedure_type == constants.UNCREW_PROCEDURE:
                    if (
                        procedure_actors[
                            constants.ACTIVE_VEHICLE_PERMISSION
                        ].subscribed_passengers
                        or procedure_actors[
                            constants.ACTIVE_VEHICLE_PERMISSION
                        ].get_held_items()
                    ):
                        text_utility.print_to_screen(
                            f"You cannot remove the crew from a {procedure_actors[constants.ACTIVE_VEHICLE_PERMISSION].name} with passengers or cargo."
                        )
                    else:
                        procedure_actors[
                            constants.ACTIVE_VEHICLE_PERMISSION
                        ].crew.uncrew_vehicle(
                            procedure_actors[constants.ACTIVE_VEHICLE_PERMISSION]
                        )
                        if allow_sound:
                            status.displayed_mob.selection_sound()

            if procedure_type == constants.INVALID_PROCEDURE:
                if constants.MERGE_PROCEDURE in self.allowed_procedures:
                    text_utility.print_to_screen(
                        "This button executes merge procedures, which require workers and an officer in the same location"
                    )
                elif constants.SPLIT_PROCEDURE in self.allowed_procedures:
                    text_utility.print_to_screen(
                        "This button executes split procedures, which require a group to be selected"
                    )
                elif constants.CREW_PROCEDURE in self.allowed_procedures:
                    text_utility.print_to_screen(
                        "This button executes crew procedures, which require a worker and an uncrewed vehicle in the same location"
                    )
                elif constants.UNCREW_PROCEDURE in self.allowed_procedures:
                    text_utility.print_to_screen(
                        "This button executes uncrew procedures, which require a crewed vehicle to be selected"
                    )


class cycle_autofill_button(button):
    """
    Button that cycles the autofill input cells to find the next available worker/officer available for a merge operation
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = None: pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'autofill_target_type': string value - Type of autofill target that this button cycles through - autofill target types are 'officer', 'worker', and 'group'
        Output:
            None
        """
        self.autofill_target_type = input_dict["autofill_target_type"]
        super().__init__(input_dict)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button can be shown. An autofill cycle button is only shown when an autofill is occurring and other options are available - allow cycling
                autofill if current autofill is a real, non-selected mob and there is at least 1 valid alternative - it makes no sense to cycle a dummy mob for a real one
                in the same location, and the selected mob is locked and can't be cycled
        Input:
            None
        Output:
            boolean: Returns True if this button can appear, otherwise returns False
        """
        if super().can_show(skip_parent_collection=skip_parent_collection):
            if (
                self.parent_collection.autofill_actors.get(
                    self.autofill_target_type, None
                )
                != status.displayed_mob
            ):
                if self.parent_collection.autofill_actors.get(
                    self.autofill_target_type, None
                ):
                    if not self.parent_collection.autofill_actors[
                        self.autofill_target_type
                    ].get_permission(constants.DUMMY_PERMISSION):
                        if self.autofill_target_type == constants.WORKER_PERMISSION:
                            return status.displayed_mob.location.has_unit_by_filter(
                                [constants.WORKER_PERMISSION], required_number=2
                            )
                        elif self.autofill_target_type == constants.OFFICER_PERMISSION:
                            return status.displayed_mob.location.has_unit_by_filter(
                                [constants.OFFICER_PERMISSION], required_number=2
                            )
                        elif (
                            self.autofill_target_type
                            == constants.CREW_VEHICLE_PERMISSION
                        ):
                            return status.displayed_mob.location.has_unit_by_filter(
                                [constants.CREW_VEHICLE_PERMISSION],
                                required_number=2,
                            )
                        elif (
                            self.autofill_target_type
                            == constants.INACTIVE_VEHICLE_PERMISSION
                        ):
                            return status.displayed_mob.location.has_unit_by_filter(
                                [constants.INACTIVE_VEHICLE_PERMISSION],
                                required_number=2,
                            )
                        # Allow cycling autofill if current autofill is a real, non-selected mob and there is at least 1 alternative
                        #   It makes no sense to cycle a dummy mob for a real one in the same location, and the selected mob is locked and can't be cycled
        return False

    def on_click(self):
        """
        Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button cycles the unit in an autofill input
            cell to the next valid alternative - assumes that there is a valid alternative, as on_click is only possible if can_show is True
        """
        self.parent_collection.search_start_index = (
            status.displayed_mob.location.subscribed_mobs.index(
                self.parent_collection.autofill_actors[self.autofill_target_type]
            )
            + 1
        )
        self.parent_collection.calibrate(status.displayed_mob)
        # Start autofill search for corresponding target type at index right after the current target actor


class action_button(button):
    """
    Customizable button with basic functionality entirely determined by the functions mapped to by its corresponding action function
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = None: pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'attached_label': label value - Label that this button is attached to, optional except for label-specific buttons, like disembarking a particular passenger
                    based on which passenger label the button is attached to
                'corresponding_action': function value - Function that this button references for all of its basic functionality - depending on the input,
                    like 'can_show' or 'on_click', this function maps to other local functions of the matching name with any passed arguments
        Output:
            None
        """
        self.corresponding_action = input_dict["corresponding_action"]
        self.corresponding_action.button = self
        super().__init__(input_dict)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button can be shown, depending on its mapped 'can_show' function
        Input:
            None
        Output:
            boolean: Returns True if this button can appear, otherwise returns False
        """
        return (
            super().can_show(skip_parent_collection=skip_parent_collection)
            and self.corresponding_action.can_show()
        )

    @property
    def tooltip_text(self) -> List[List[str]]:
        """
        Provides the tooltip for this object
        """
        return self.corresponding_action.tooltip_text

    def get_matching_unit(self):
        """
        Returns the unit this button appears next to
        """
        if self.corresponding_action.actor_type == constants.MOB_ACTOR_TYPE:
            return status.displayed_mob
        elif self.corresponding_action.actor_type == constants.LOCATION_ACTOR_TYPE:
            return status.displayed_location
        elif self.corresponding_action.actor_type in [
            constants.MINISTER_ACTOR_TYPE,
            constants.PROSECUTION_ACTOR_TYPE,
        ]:
            if constants.current_game_mode == constants.TRIAL_MODE:
                return status.displayed_prosecution
            else:
                return status.displayed_minister

    def on_click(self):
        """
        Does a certain action when clicked or when corresponding key is pressed, depending on this button's mapped 'on_click' function
        """
        self.corresponding_action.on_click(self.get_matching_unit())


class anonymous_button(button):
    """
    Customizable button with basic functionality entirely determined by its button_type input dictionary
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = None: pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'attached_label': label value - Label that this button is attached to, optional except for label-specific buttons, like disembarking a particular passenger
                    based on which passenger label the button is attached to
                'button_type': dictionary value - A button with a dictionary button_type value is created as an anonymous button, with basic functionality
                    entirely defined by the dictionary's contents:
                        'on_click': tuple value - Tuple containing function object followed by the parameters to be passed to it when this button is clicked
                        'tooltip': string list value - Tuple containing tooltip list to display for this button
                        'message': string value - Optional text to display over this button, intended for notification choice buttons
                'notification': notification value - Notification the button is attached to, if applicable
        Output:
            None
        """
        self.notification = input_dict.get("notification", None)
        button_info_dict = input_dict["button_type"]
        self.on_click_info = button_info_dict.get("on_click", None)
        if self.on_click_info and type(self.on_click_info[0]) != list:
            self.on_click_info = ([self.on_click_info[0]], [self.on_click_info[1]])
        self.tooltip = button_info_dict["tooltip"]
        self.message = button_info_dict.get("message")

        super().__init__(input_dict)
        self.font = constants.fonts["default_notification"]
        if self.notification:
            self.in_notification = True
        else:
            self.in_notification = False

    def on_click(self):
        """
        Controls this button's behavior when clicked. Choice buttons remove their notifications when clicked, along with the normal behaviors associated with their button_type
        """
        super().on_click()
        if self.on_click_info:
            for index in range(len(self.on_click_info[0])):
                self.on_click_info[0][index](
                    *self.on_click_info[1][index]
                )  # calls each item function with corresponding parameters
        if self.in_notification:
            self.notification.on_click(choice_button_override=True)

    def draw(self):
        """
        Draws this button below its choice notification and draws a description of what it does on top of it
        """
        super().draw()
        if self.showing and self.in_notification:
            constants.game_display.blit(
                text_utility.text(self.message, self.font),
                (
                    self.x + scaling.scale_width(10),
                    constants.display_height - (self.y + self.height),
                ),
            )

    @property
    def tooltip_text(self) -> List[List[str]]:
        """
        Provides the tooltip for this object
        """
        return self.tooltip


class map_mode_button(button):
    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = None: pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'map_mode": Map mode that this button sets, like "default" or constants.ALTITUDE
        Output:
            None
        """
        self.map_mode = input_dict["map_mode"]
        super().__init__(input_dict)

    def can_show(self):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns True if this button can appear during the current game mode and map modes are enabled, otherwise returns False
        """
        self.showing_outline = constants.current_map_mode == self.map_mode
        return super().can_show()

    def on_click(self):
        """
        Sets the current map mode to this button's map mode
        """
        constants.current_map_mode = self.map_mode
        constants.EventBus.publish(constants.UPDATE_MAP_MODE_ROUTE, self.map_mode)
        status.current_world.update_globe_projection()

    @property
    def tooltip_text(self) -> List[List[str]]:
        """
        Provides the tooltip for this object
        """
        return [f"Sets the map mode to {self.map_mode}"]
