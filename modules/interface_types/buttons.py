# Contains functionality for buttons

import pygame
from typing import List
from ..util import (
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
from ..constructs import equipment_types
from . import interface_elements
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags


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
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'button_type': string value - Determines the function of this button, like 'end turn'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
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
        self.button_type = input_dict["button_type"]
        status.button_list.append(self)
        self.keybind_id = input_dict.get("keybind_id", "none")
        self.has_keybind = self.keybind_id != "none"
        if self.has_keybind:
            self.set_keybind(self.keybind_id)
        if "color" in input_dict:
            self.color = constants.color_dict[input_dict["color"]]
        self.has_button_press_override = False
        self.enable_shader = input_dict.get("enable_shader", False)
        self.showing_outline = False
        self.showing_background = True
        self.button_type = input_dict["button_type"]
        self.tooltip_text = []
        self.update_tooltip()
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
            string/actor new_actor: The minister whose information is matched by this button. If this equals 'none', this button is detached from any ministers
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

    def update_tooltip(self):
        """
        Description:
            Sets this button's tooltip to what it should be, depending on its button_type
        Input:
            None
        Output:
            None
        """
        if self.button_type in ["move up", "move down", "move left", "move right"]:
            direction = "none"
            x_change = 0
            y_change = 0
            if self.button_type == "move up":
                direction = "north"
                non_cardinal_direction = "up"
                y_change = 1
            elif self.button_type == "move down":
                direction = "south"
                non_cardinal_direction = "down"
                y_change = -1
            elif self.button_type == "move left":
                direction = "west"
                non_cardinal_direction = "left"
                x_change = -1
            elif self.button_type == "move right":
                direction = "east"
                non_cardinal_direction = "right"
                x_change = 1

            tooltip_text = []

            current_mob = status.displayed_mob
            if current_mob:
                movement_cost = current_mob.get_movement_cost(x_change, y_change)
                local_cell = current_mob.get_cell()
                adjacent_cell = local_cell.adjacent_cells[non_cardinal_direction]
                local_infrastructure = local_cell.get_intact_building("infrastructure")
                if adjacent_cell.terrain_handler.visible:
                    tooltip_text.append("Press to move to the " + direction)
                    adjacent_infrastructure = adjacent_cell.get_intact_building(
                        "infrastructure"
                    )
                    connecting_roads = False
                    if (
                        current_mob.get_permission(constants.BATTALION_PERMISSION)
                        and adjacent_cell.get_best_combatant("npmob") != "none"
                    ):
                        tooltip_text += status.actions["combat"].update_tooltip(
                            tooltip_info_dict={
                                "adjacent_infrastructure": adjacent_infrastructure,
                                "local_infrastructure": local_infrastructure,
                                "x_change": x_change,
                                "y_change": y_change,
                                "local_cell": local_cell,
                                "adjacent_cell": adjacent_cell,
                            }
                        )
                    else:
                        message = ""
                        if (
                            current_mob.get_permission(constants.VEHICLE_PERMISSION)
                            and current_mob.vehicle_type == "train"
                        ):
                            if (
                                adjacent_infrastructure != "none"
                                and adjacent_infrastructure.is_railroad
                                and local_infrastructure != "none"
                                and local_infrastructure.is_railroad
                                and local_cell.has_walking_connection(adjacent_cell)
                            ):
                                message = f"Costs {movement_cost} movement point{utility.generate_plural(movement_cost)} because the adjacent tile has connecting railroads"
                            else:
                                message = "Not possible because the adjacent tile does not have connecting railroads"
                            tooltip_text.append(message)
                            tooltip_text.append("A train can only move along railroads")
                        else:
                            message = f"Costs {movement_cost} movement point{utility.generate_plural(movement_cost)} because the adjacent tile has {adjacent_cell.terrain_handler.terrain.replace('_', ' ')} terrain"
                            if local_cell.has_walking_connection(adjacent_cell):
                                if (
                                    local_infrastructure != "none"
                                    and adjacent_infrastructure != "none"
                                ):  # if both have infrastructure
                                    connecting_roads = True
                                    message += "and connecting roads"
                                elif (
                                    local_infrastructure == "none"
                                    and adjacent_infrastructure != "none"
                                ):  # if local has no infrastructure but adjacent does
                                    message += "and no connecting roads"
                                elif (
                                    local_infrastructure != "none"
                                ):  # if local has infrastructure but not adjacent
                                    message += "and no connecting roads"  # + local_infrastructure.infrastructure_type
                                else:
                                    message += "and no connecting roads"

                            tooltip_text.append(message)
                            if (
                                current_mob.can_walk
                                and adjacent_cell.terrain_handler.terrain == "water"
                                and (not current_mob.can_swim)
                            ) and not local_cell.has_walking_connection(adjacent_cell):
                                tooltip_text.append(
                                    "Moving into a water tile costs an entire turn of movement points for units without boats"
                                )
                            else:
                                tooltip_text.append(
                                    f"Moving into a {adjacent_cell.terrain_handler.terrain.replace('_', ' ')} tile costs {constants.terrain_movement_cost_dict[adjacent_cell.terrain_handler.terrain]} movement points"
                                )
                    if (
                        (not current_mob.get_permission(constants.VEHICLE_PERMISSION))
                        and current_mob.get_cell().terrain_handler.terrain == "water"
                        and current_mob.get_cell().has_vehicle("ship")
                    ):
                        if (
                            not current_mob.can_swim
                        ):  # if could not naturally move into current tile, must be from vehicle
                            tooltip_text.append(
                                "Moving from a steamship in the water after disembarking requires all remaining movement points, at least the usual amount"
                            )
                    if connecting_roads:
                        tooltip_text.append(
                            "Moving between 2 tiles with roads or railroads costs half as many movement points."
                        )
                else:
                    tooltip_text += status.actions["exploration"].update_tooltip(
                        tooltip_info_dict={"direction": direction}
                    )

            self.set_tooltip(tooltip_text)

        elif self.button_type == "execute movement routes":
            self.set_tooltip(
                ["Press to move all valid units along their designated movement routes"]
            )

        elif self.button_type == "instructions":
            self.set_tooltip(
                [
                    "Shows the game's instructions",
                    "Press this when instructions are not opened to open them",
                    "Press this when instructions are opened to close them",
                ]
            )

        elif self.button_type == "merge":
            if status.displayed_mob and status.displayed_mob.all_permissions(
                constants.OFFICER_PERMISSION, constants.EVANGELIST_PERMISSION
            ):
                self.set_tooltip(
                    [
                        "Merges this evangelist with church volunteers in the same tile to form a group of missionaries",
                        "Requires that an evangelist is selected in the same tile as church volunteers",
                    ]
                )
            else:
                self.set_tooltip(
                    [
                        "Merges this officer with a worker in the same tile to form a group with a type based on that of the officer",
                        "Requires that an officer is selected in the same tile as a worker",
                    ]
                )

        elif self.button_type == "split":
            self.set_tooltip(["Splits a group into its worker and officer"])

        elif self.button_type == "crew":  # clicked on vehicle side
            self.set_tooltip(
                [
                    "Merges this "
                    + self.vehicle_type
                    + " with a worker in the same tile to form a crewed "
                    + self.vehicle_type,
                    "Requires that an uncrewed "
                    + self.vehicle_type
                    + " is selected in the same tile as a worker",
                ]
            )

        elif self.button_type == "worker to crew":  # clicked on worker side
            self.set_tooltip(
                [
                    "Merges this worker with a "
                    + self.vehicle_type
                    + " in the same tile to form a crewed "
                    + self.vehicle_type,
                    "Requires that a worker is selected in the same tile as an uncrewed "
                    + self.vehicle_type,
                ]
            )

        elif self.button_type == "uncrew":
            self.set_tooltip(
                [
                    "Orders this "
                    + self.vehicle_type
                    + "'s crew to abandon the "
                    + self.vehicle_type
                    + "."
                ]
            )

        elif self.button_type == "embark":
            self.set_tooltip(
                [
                    "Orders this unit to embark a "
                    + self.vehicle_type
                    + " in the same tile",
                    "Requires that a unit is selected in the same tile as a crewed "
                    + self.vehicle_type,
                ]
            )

        elif self.button_type == "disembark":
            if self.vehicle_type == "train":
                self.set_tooltip(
                    ["Orders this unit to disembark the " + self.vehicle_type]
                )
            else:
                self.set_tooltip(
                    [
                        "Orders this unit to disembark the " + self.vehicle_type,
                        "Disembarking a unit outside of a port renders it disorganized until the next turn, decreasing its combat effectiveness",
                    ]
                )

        elif self.button_type == "embark all":
            self.set_tooltip(
                [
                    "Orders this "
                    + self.vehicle_type
                    + " to take all non-vehicle units in this tile as passengers"
                ]
            )

        elif self.button_type == "disembark all":
            if self.vehicle_type == "train":
                self.set_tooltip(
                    [
                        "Orders this "
                        + self.vehicle_type
                        + " to disembark all of its passengers"
                    ]
                )
            else:
                self.set_tooltip(
                    [
                        "Orders this "
                        + self.vehicle_type
                        + " to disembark all of its passengers",
                        "Disembarking a unit outside of a port renders it disorganized until the next turn, decreasing its combat effectiveness",
                    ]
                )

        elif self.button_type == "remove worker":
            if not self.attached_label.attached_building == "none":
                self.set_tooltip(
                    [
                        "Detaches this work crew from the "
                        + self.attached_label.attached_building.name
                    ]
                )
            else:
                self.set_tooltip(["none"])

        elif (
            self.button_type == "start end turn"
        ):  # different from end turn from choice buttons - start end turn brings up a choice notification
            self.set_tooltip(["Ends the current turn"])

        elif self.button_type in [
            "sell commodity",
            "sell all commodity",
            "sell each commodity",
        ]:
            if status.displayed_tile:
                if self.button_type == "sell commodity":
                    self.set_tooltip(
                        [
                            "Orders your "
                            + constants.type_minister_dict["trade"]
                            + " to sell 1 unit of "
                            + self.attached_label.actor.current_item
                            + " for about "
                            + str(
                                constants.item_prices[
                                    self.attached_label.actor.current_item
                                ]
                            )
                            + " money at the end of the turn",
                            "The amount each commodity was sold for is reported at the beginning of your next turn",
                            "Each unit of "
                            + self.attached_label.actor.current_item
                            + " sold has a chance of reducing its sale price",
                        ]
                    )
                elif self.button_type == "sell all commodity":
                    num_present = status.displayed_tile.get_inventory(
                        self.attached_label.actor.current_item
                    )
                    self.set_tooltip(
                        [
                            "Orders your "
                            + constants.type_minister_dict["trade"]
                            + " to sell your entire stockpile of "
                            + self.attached_label.actor.current_item
                            + " for about "
                            + str(
                                constants.item_prices[
                                    self.attached_label.actor.current_item
                                ]
                            )
                            + " money each at the end of the turn, "
                            + "for a total of about "
                            + str(
                                constants.item_prices[
                                    self.attached_label.actor.current_item
                                ]
                                * num_present
                            )
                            + " money",
                            "The amount each commodity was sold for is reported at the beginning of your next turn",
                            "Each unit of "
                            + self.attached_label.actor.current_item
                            + " sold has a chance of reducing its sale price",
                        ]
                    )
                else:
                    self.set_tooltip(
                        [
                            "Orders your "
                            + constants.type_minister_dict["trade"]
                            + " to sell all commodities at the end of the turn, "
                            + "The amount each commodity was sold for is reported at the beginning of your next turn",
                            "Each commodity sold has a chance of reducing its sale price",
                        ]
                    )
            else:
                self.set_tooltip(["none"])

        elif self.button_type == "pick up each commodity":
            self.set_tooltip(["Orders the selected unit to pick up all items"])

        elif self.button_type == "drop each commodity":
            self.set_tooltip(["Orders the selected unit to drop all items"])

        elif self.button_type == "use equipment":
            if status.displayed_tile:
                self.set_tooltip(
                    [
                        "Orders the selected unit to equip "
                        + self.attached_label.actor.current_item
                    ]
                )

        elif self.button_type == "remove equipment":
            if status.displayed_mob:
                self.set_tooltip(
                    ["Click to unequip " + self.equipment_type]
                    + status.equipment_types[self.equipment_type].description
                )

        elif self.button_type == "switch theatre":
            self.set_tooltip(
                [
                    "Moves this steamship across the ocean to another theatre at the end of the turn",
                    "Once clicked, the mouse pointer can be used to click on the destination",
                    "The destination, once chosen, will having a flashing yellow outline",
                    "Requires that this steamship is able to move",
                ]
            )

        elif self.button_type == "cycle passengers":
            tooltip_text = [
                "Cycles through this " + self.vehicle_type + "'s passengers"
            ]
            tooltip_text.append("Passengers: ")
            if self.showing:
                for current_passenger in status.displayed_mob.contained_mobs:
                    tooltip_text.append("    " + current_passenger.name)
            self.set_tooltip(tooltip_text)

        elif self.button_type == "cycle work crews":
            tooltip_text = ["Cycles through this  building's work crews"]
            tooltip_text.append("Work crews: ")
            if self.showing:
                for current_work_crew in status.displayed_tile.cell.get_building(
                    "resource"
                ).contained_work_crews:
                    tooltip_text.append("    " + current_work_crew.name)
            self.set_tooltip(tooltip_text)

        elif self.button_type == "cycle tile mobs":
            tooltip_text = ["Cycles through this tile's units"]
            tooltip_text.append("Units: ")
            if self.showing:
                for current_mob in status.displayed_tile.cell.contained_mobs:
                    tooltip_text.append("    " + current_mob.name)
            self.set_tooltip(tooltip_text)

        elif self.button_type == "build train":
            actor_utility.update_descriptions("train")
            cost = actor_utility.get_building_cost(status.displayed_mob, "train")
            self.set_tooltip(
                [
                    "Orders parts for and attempts to assemble a train in this unit's tile for "
                    + str(cost)
                    + " money",
                    "Can only be assembled on a train station",
                    "Costs all remaining movement points, at least 1",
                    "Unlike buildings, the cost of vehicle assembly is not impacted by local terrain",
                ]
            )

        elif self.button_type == "cycle units":
            tooltip_text = ["Selects the next unit in the turn order"]
            turn_queue = status.player_turn_queue
            if len(turn_queue) > 0:
                for current_pmob in turn_queue:
                    tooltip_text.append("    " + utility.capitalize(current_pmob.name))
            self.set_tooltip(tooltip_text)

        elif self.button_type == "new game":
            self.set_tooltip(["Starts a new game"])

        elif self.button_type == "save game":
            self.set_tooltip(["Saves this game"])

        elif self.button_type == "load game":
            self.set_tooltip(["Loads a saved game"])

        elif self.button_type == "cycle available ministers":
            self.set_tooltip(
                ["Cycles through the candidates available to be appointed"]
            )

        elif self.button_type == "appoint minister":
            self.set_tooltip(["Appoints this candidate as " + self.appoint_type])

        elif self.button_type == "remove minister":
            self.set_tooltip(["Removes this minister from their current office"])

        elif self.button_type == "to trial":
            self.set_tooltip(
                [
                    "Opens the trial planning screen to attempt to imprison this minister for corruption",
                    "A trial has a higher success chance as more evidence of that minister's corruption is found",
                    "While entering this screen is free, a trial costs "
                    + str(constants.action_prices["trial"])
                    + " money once started",
                    "Each trial attempted doubles the cost of other trials in the same turn",
                ]
            )

        elif self.button_type == "fabricate evidence":
            if constants.current_game_mode == "trial":
                self.set_tooltip(
                    [
                        "Creates a unit of fake evidence against this minister to improve the trial's success chance for "
                        + str(self.get_cost())
                        + " money",
                        "Each piece of evidence fabricated in a trial becomes increasingly expensive.",
                        "Unlike real evidence, fabricated evidence disappears at the end of the turn and is never preserved after a failed trial",
                    ]
                )
            else:
                self.set_tooltip(["placeholder"])

        elif self.button_type == "bribe judge":
            self.set_tooltip(
                [
                    "Bribes the judge of the next trial this turn for "
                    + str(self.get_cost())
                    + " money",
                    "While having unpredictable results, bribing the judge may swing the trial in your favor or blunt the defense's efforts to do the same",
                ]
            )

        elif self.button_type == "recruit workers":
            actor_utility.update_descriptions(self.worker_type + " workers")
            self.set_tooltip(
                [
                    "Recruits a unit of "
                    + self.worker_type
                    + " workers for "
                    + str(status.worker_types[self.worker_type].recruitment_cost)
                    + " money"
                ]
                + constants.list_descriptions[self.worker_type + " workers"]
            )

        elif self.button_type == "rename settlement":
            self.set_tooltip(["Displays a typing prompt to rename this settlement"])

        elif self.button_type == "show previous reports":
            self.set_tooltip(
                [
                    "Displays the previous turn's production, sales, and financial reports"
                ]
            )

        elif self.button_type in ["enable sentry mode", "disable sentry mode"]:
            if self.button_type == "enable sentry mode":
                verb = "enable"
            elif self.button_type == "disable sentry mode":
                verb = "disable"
            self.set_tooltip(
                [
                    utility.capitalize(verb) + "s sentry mode for this unit",
                    "A unit in sentry mode is removed from the turn order and will be skipped when cycling through unmoved units",
                ]
            )

        elif self.button_type in [
            "enable automatic replacement",
            "disable automatic replacement",
        ]:
            if self.button_type == "enable automatic replacement":
                verb = "enable"
                operator = "not "
            elif self.button_type == "disable automatic replacement":
                verb = "disable"
                operator = ""
            if self.target_type == "unit":
                target = "unit"
            else:
                target = "unit's " + self.target_type  # worker or officer
            self.set_tooltip(
                [
                    utility.capitalize(verb)
                    + "s automatic replacement for this "
                    + target,
                    "A unit with automatic replacement will be automatically replaced if it dies from attrition",
                    "This "
                    + target
                    + " is currently set to "
                    + operator
                    + "be automatically replaced",
                ]
            )

        elif self.button_type == "wake up all":
            self.set_tooltip(
                [
                    "Disables sentry mode for all units",
                    "A unit in sentry mode is removed from the turn order and will be skipped when cycling through unmoved units",
                ]
            )

        elif self.button_type == "end unit turn":
            self.set_tooltip(
                [
                    "Ends this unit's turn, skipping it when cycling through unmoved units for the rest of the turn"
                ]
            )

        elif self.button_type == "clear automatic route":
            self.set_tooltip(
                ["Removes this unit's currently designated movement route"]
            )

        elif self.button_type == "draw automatic route":
            self.set_tooltip(
                [
                    "Starts customizing a new movement route for this unit",
                    "Add to the route by clicking on valid tiles adjacent to the current destination",
                    "The start is outlined in purple, the destination is outlined in yellow, and the path is outlined in blue",
                    "When moving along its route, a unit will pick up as many commodities as possible at the start and drop them at the destination",
                    "A unit may not be able to move along its route because of enemy units, a lack of movement points, or not having any commodities to pick up at the start",
                ]
            )

        elif self.button_type == "execute automatic route":
            self.set_tooltip(
                ["Moves this unit along its currently designated movement route"]
            )

        elif self.button_type == "generate crash":
            self.set_tooltip(["Exits the game"])

        elif self.button_type == "minimize interface collection":
            if self.parent_collection.minimized:
                verb = "Opens"
            else:
                verb = "Minimizes"
            self.set_tooltip([verb + " the " + self.parent_collection.description])

        elif self.button_type == "move interface collection":
            if self.parent_collection.move_with_mouse_config["moving"]:
                verb = "Stops moving"
            else:
                verb = "Moves"
            self.set_tooltip([verb + " the " + self.parent_collection.description])

        elif self.button_type == "reset interface collection":
            self.set_tooltip(
                [
                    "Resets the "
                    + self.parent_collection.description
                    + " to its original location"
                ]
            )

        elif self.button_type == "tab":
            if hasattr(self.linked_element, "description"):
                description = self.linked_element.description
            else:
                description = "attached panel"
            self.set_tooltip(["Displays the " + description])

        elif self.button_type == "manually calibrate":
            if self.input_source == "none":
                self.set_tooltip(["Empties this reorganization cell"])
            else:
                self.set_tooltip(
                    ["Uploads the selected unit to this reorganization cell"]
                )

        elif self.button_type == "cycle autofill":
            if (
                self.parent_collection.autofill_actors[self.autofill_target_type]
                != "none"
            ):
                amount = 1
                if self.autofill_target_type == "worker":
                    amount = 2
                verb = utility.conjugate("be", amount, "preterite")  # was or were
                self.set_tooltip(
                    [
                        f"The {self.parent_collection.autofill_actors[self.autofill_target_type].name} here {verb} automatically selected for the {self.parent_collection.autofill_actors['procedure']} procedure",
                        f"Press to cycle to the next available {self.autofill_target_type}",
                    ]
                )
        elif self.button_type == "change parameter":
            self.set_tooltip(
                [
                    f"Changes this tile's {self.attached_label.actor_label_type} by {self.change}"
                ]
            )
        else:
            self.set_tooltip(["placeholder"])

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

    def set_tooltip(self, tooltip_text: List[str]):
        """
        Description:
            Sets this actor's tooltip to the inputted list, with each inputted list representing a line of the tooltip
        Input:
            string list new_tooltip: Lines for this actor's tooltip
        Output:
            None
        """
        self.tooltip_text = tooltip_text
        if self.has_keybind:
            self.tooltip_text.append("Press " + self.keybind_name + " to use.")
        font = constants.fonts["default"]
        tooltip_width = font.size
        for text_line in tooltip_text:
            tooltip_width = max(
                tooltip_width, font.calculate_size(text_line) + scaling.scale_width(10)
            )
        tooltip_height = (len(self.tooltip_text) * font.size) + scaling.scale_height(5)
        self.tooltip_box = pygame.Rect(self.x, self.y, tooltip_width, tooltip_height)
        self.tooltip_outline_width = 1
        self.tooltip_outline = pygame.Rect(
            self.x - self.tooltip_outline_width,
            self.y + self.tooltip_outline_width,
            tooltip_width + (2 * self.tooltip_outline_width),
            tooltip_height + (self.tooltip_outline_width * 2),
        )

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
        Description:
            Returns whether this button's tooltip can be shown. By default, its tooltip can be shown when it is visible and colliding with the mouse
        Input:
            None
        Output:
            None
        """
        if self.touching_mouse() and self.showing:
            return True
        else:
            return False

    def draw(self, allow_show_outline=True):
        """
        Description:
            Draws this button with a description of its keybind if it has one, along with an outline if its keybind is being pressed
        Input:
            None
        Output:
            None
        """
        if self.showing:
            if self.showing_outline and allow_show_outline:
                pygame.draw.rect(
                    constants.game_display,
                    constants.color_dict["white"],
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
                color = "white"
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

    def draw_tooltip(self, below_screen, beyond_screen, height, width, y_displacement):
        """
        Description:
            Draws this button's tooltip when moused over. The tooltip's location may vary when the tooltip is near the edge of the screen or if multiple tooltips are being shown
        Input:
            boolean below_screen: Whether any of the currently showing tooltips would be below the bottom edge of the screen. If True, moves all tooltips up to prevent any from being below the screen
            boolean beyond_screen: Whether any of the currently showing tooltips would be beyond the right edge of the screen. If True, moves all tooltips to the left to prevent any from being beyond the screen
            int height: Combined pixel height of all tooltips
            int width: Pixel width of the widest tooltip
            int y_displacement: How many pixels below the mouse this tooltip should be, depending on the order of the tooltips
        Output:
            None
        """
        if self.showing:
            self.update_tooltip()
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if below_screen:
                mouse_y = constants.display_height + 10 - height
            if beyond_screen:
                mouse_x = constants.display_width - width
            mouse_y += y_displacement
            self.tooltip_box.x = mouse_x
            self.tooltip_box.y = mouse_y
            self.tooltip_outline.x = self.tooltip_box.x - self.tooltip_outline_width
            self.tooltip_outline.y = self.tooltip_box.y - self.tooltip_outline_width
            pygame.draw.rect(
                constants.game_display,
                constants.color_dict["black"],
                self.tooltip_outline,
            )
            pygame.draw.rect(
                constants.game_display, constants.color_dict["white"], self.tooltip_box
            )
            for text_line_index in range(len(self.tooltip_text)):
                text_line = self.tooltip_text[text_line_index]
                constants.game_display.blit(
                    text_utility.text(text_line, constants.myfont),
                    (
                        self.tooltip_box.x + scaling.scale_width(10),
                        self.tooltip_box.y + (text_line_index * constants.font_size),
                    ),
                )

    def on_rmb_click(self):
        """
        Description:
            Controls this button's behavior when right clicked. By default, the button's right click behavior is the same as its left click behavior.
        Input:
            None
        Output:
            None
        """
        self.on_click()

    def on_click(self):
        """
        Description:
            Controls this button's behavior when left clicked. This behavior depends on the button's button_type
        Input:
            None
        Output:
            None
        """
        if self.button_type in ["move left", "move right", "move up", "move down"]:
            x_change = 0
            y_change = 0
            if self.button_type == "move left":
                x_change = -1
            elif self.button_type == "move right":
                x_change = 1
            elif self.button_type == "move up":
                y_change = 1
            elif self.button_type == "move down":
                y_change = -1
            if main_loop_utility.action_possible():
                if minister_utility.positions_filled():
                    current_mob = status.displayed_mob
                    if current_mob:
                        if constants.current_game_mode == "strategic":
                            if current_mob.can_move(
                                x_change, y_change, can_print=False
                            ):
                                current_mob.move(x_change, y_change)
                                flags.show_selection_outlines = True
                                constants.last_selection_outline_switch = (
                                    constants.current_time
                                )
                                if current_mob.sentry_mode:
                                    current_mob.set_sentry_mode(False)
                                current_mob.clear_automatic_route()

                            elif current_mob.get_permission(
                                constants.VEHICLE_PERMISSION
                            ):  # If moving into unreachable land, have each passenger attempt to move
                                if current_mob.contained_mobs:
                                    passengers = current_mob.contained_mobs.copy()
                                    current_mob.eject_passengers()
                                    last_moved = None
                                    for current_passenger in passengers:
                                        if (
                                            not status.displayed_notification
                                        ) and current_passenger.can_move(
                                            x_change, y_change, can_print=True
                                        ):
                                            current_passenger.move(x_change, y_change)
                                            last_moved = current_passenger
                                    if (
                                        not status.displayed_notification
                                    ):  # If attacking, don't reembark
                                        for current_passenger in passengers:
                                            if (
                                                current_passenger.x,
                                                current_passenger.y,
                                            ) == (
                                                current_mob.x,
                                                current_mob.y,
                                            ):  # Re-embark any units that couldn't move
                                                current_passenger.embark_vehicle(
                                                    current_mob
                                                )
                                    if last_moved and not last_moved.in_vehicle:
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
                                current_mob.can_move(x_change, y_change, can_print=True)
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

        elif self.button_type == "execute movement routes":
            if main_loop_utility.action_possible():
                if minister_utility.positions_filled():
                    if not constants.current_game_mode == "strategic":
                        game_transitions.set_game_mode("strategic")

                    unit_types = ["porters", "steamship", "train"]
                    moved_units = {}
                    attempted_units = {}
                    for current_unit_type in unit_types:
                        moved_units[current_unit_type] = 0
                        attempted_units[current_unit_type] = 0
                    last_moved = None
                    for current_pmob in status.pmob_list:
                        if len(current_pmob.base_automatic_route) > 0:
                            if current_pmob.get_permission(
                                constants.VEHICLE_PERMISSION
                            ):
                                if current_pmob.vehicle_type == "train":
                                    unit_type = "train"
                                elif current_pmob.can_swim:
                                    unit_type = "steamship"
                            else:
                                unit_type = "porters"
                            attempted_units[unit_type] += 1

                            progressed = current_pmob.follow_automatic_route()
                            if progressed:
                                moved_units[unit_type] += 1
                                last_moved = current_pmob
                            current_pmob.remove_from_turn_queue()
                    if last_moved:
                        last_moved.select()  # updates mob info display if automatic route changed anything
                    # actor_utility.calibrate_actor_info_display(status.mob_info_display, status.displayed_mob)
                    types_moved = 0
                    text = ""
                    for current_unit_type in unit_types:
                        if attempted_units[current_unit_type] > 0:

                            if current_unit_type == "porters":
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
                                    text += (
                                        "The "
                                        + singular
                                        + " made progress on its designated movement route. /n /n"
                                    )
                                else:
                                    text += (
                                        "All "
                                        + str(num_attempted)
                                        + " of the "
                                        + plural
                                        + " made progress on their designated movement routes. /n /n"
                                    )
                            else:
                                if num_progressed == 0:
                                    if num_attempted == 1:
                                        text += (
                                            "The "
                                            + singular
                                            + " made no progress on its designated movement route. /n /n"
                                        )
                                    else:
                                        text += (
                                            "None of the "
                                            + plural
                                            + " made progress on their designated movement routes. /n /n"
                                        )
                                else:
                                    text += (
                                        "Only "
                                        + str(num_progressed)
                                        + " of the "
                                        + str(num_attempted)
                                        + " "
                                        + plural
                                        + " made progress on their designated movement routes. /n /n"
                                    )

                    transportation_minister = status.current_ministers[
                        constants.type_minister_dict["transportation"]
                    ]
                    if types_moved > 0:
                        transportation_minister.display_message(text)
                    else:
                        transportation_minister.display_message(
                            "There were no units with designated movement routes. /n /n"
                        )
            else:
                text_utility.print_to_screen("You are busy and cannot move units.")

        elif self.button_type == "attack":
            self.battalion.clear_attached_cell_icons()
            self.battalion.move(self.x_change, self.y_change, True)

        elif self.button_type == "remove worker":
            if not self.attached_label.attached_building == "none":
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

        elif self.button_type == "start end turn":
            if main_loop_utility.action_possible():
                stopping = False
                for current_position in constants.minister_types:
                    if status.current_ministers[current_position] == None:
                        stopping = True
                if stopping:
                    game_transitions.force_minister_appointment()
                else:
                    if not constants.current_game_mode == "strategic":
                        game_transitions.set_game_mode("strategic")
                    turn_management_utility.end_turn_warnings()

                    choice_info_dict = {"type": "end turn"}

                    constants.notification_manager.display_notification(
                        {
                            "message": "Are you sure you want to end your turn? ",
                            "choices": ["end turn", "none"],
                            "extra_parameters": choice_info_dict,
                        }
                    )

            else:
                text_utility.print_to_screen("You are busy and cannot end your turn.")

        elif self.button_type == "end turn":
            turn_management_utility.end_turn()

        elif self.button_type in ["pick up each commodity", "drop each commodity"]:
            if self.button_type == "pick up each commodity":
                source_type = "tile_inventory"
            else:
                source_type = "mob_inventory"
            equipment_types.transfer("each", "all", source_type)
            if status.displayed_tile_inventory:
                status.displayed_tile_inventory.on_click()
            if status.displayed_mob_inventory:
                status.displayed_mob_inventory.on_click()

        elif self.button_type in [
            "sell commodity",
            "sell all commodity",
            "sell each commodity",
        ]:
            if self.button_type == "sell each commodity":
                commodities = constants.collectable_resources
            else:
                commodities = [self.attached_label.actor.current_item]
            if minister_utility.positions_filled():
                for commodity in commodities:
                    num_present: int = status.displayed_tile.get_inventory(commodity)
                    if num_present > 0:
                        num_sold: int
                        if self.button_type == "sell commodity":
                            num_sold = 1
                        else:
                            num_sold = num_present
                        market_utility.sell(status.displayed_tile, commodity, num_sold)

                actor_utility.calibrate_actor_info_display(
                    status.tile_info_display, status.displayed_tile
                )
                if (
                    status.displayed_tile_inventory
                    and status.displayed_tile_inventory.current_item
                ):
                    actor_utility.calibrate_actor_info_display(
                        status.tile_inventory_info_display,
                        status.displayed_tile_inventory,
                    )
                else:
                    actor_utility.calibrate_actor_info_display(
                        status.tile_inventory_info_display, None
                    )

        elif self.button_type == "use equipment":
            if main_loop_utility.action_possible():
                if status.displayed_mob and status.displayed_mob.get_permission(
                    constants.PMOB_PERMISSION
                ):
                    equipment = status.equipment_types[
                        self.attached_label.actor.current_item
                    ]
                    if equipment.check_requirement(status.displayed_mob):
                        if not status.displayed_mob.equipment.get(
                            equipment.equipment_type, False
                        ):
                            equipment.equip(status.displayed_mob)
                            status.displayed_tile.change_inventory(
                                equipment.equipment_type, -1
                            )
                            actor_utility.calibrate_actor_info_display(
                                status.tile_info_display, status.displayed_tile
                            )
                            actor_utility.calibrate_actor_info_display(
                                status.mob_info_display, status.displayed_mob
                            )
                            actor_utility.select_interface_tab(
                                status.mob_tabbed_collection,
                                status.mob_inventory_collection,
                            )
                            if (
                                status.displayed_tile_inventory
                                and status.displayed_tile_inventory.current_item
                            ):
                                actor_utility.calibrate_actor_info_display(
                                    status.tile_inventory_info_display,
                                    status.displayed_tile_inventory,
                                )
                            else:
                                actor_utility.calibrate_actor_info_display(
                                    status.tile_inventory_info_display, None
                                )
                        else:
                            text_utility.print_to_screen(
                                "This unit already has "
                                + equipment.equipment_type
                                + " equipped."
                            )
                    else:
                        text_utility.print_to_screen(
                            "This type of unit can not equip "
                            + equipment.equipment_type
                            + "."
                        )
                else:
                    text_utility.print_to_screen(
                        "There is no unit to use this equipment."
                    )
            else:
                text_utility.print_to_screen(
                    "You are busy and cannot transfer equipment."
                )

        elif self.button_type == "remove equipment":
            if main_loop_utility.action_possible():
                status.equipment_types[self.equipment_type].unequip(
                    status.displayed_mob
                )
                status.displayed_tile.change_inventory(self.equipment_type, 1)
                actor_utility.calibrate_actor_info_display(
                    status.mob_info_display, status.displayed_mob
                )
            else:
                text_utility.print_to_screen(
                    "You are busy and cannot transfer equipment."
                )

        elif self.button_type == "cycle units":
            if main_loop_utility.action_possible():
                game_transitions.cycle_player_turn()
            else:
                text_utility.print_to_screen(
                    "You are busy and cannot cycle through units."
                )

        elif self.button_type == "new game":
            if constants.current_game_mode == "new_game_setup":
                constants.save_load_manager.new_game()
            else:
                game_transitions.set_game_mode("new_game_setup")

        elif self.button_type == "save game":
            if main_loop_utility.action_possible():
                constants.save_load_manager.save_game("save1.pickle")
                constants.notification_manager.display_notification(
                    {
                        "message": "Game successfully saved to save1.pickle /n /n",
                    }
                )
            else:
                text_utility.print_to_screen("You are busy and cannot save the game")

        elif self.button_type == "load game":
            constants.save_load_manager.load_game("save1.pickle")

        elif self.button_type == "fire":
            fired_unit = status.displayed_mob
            fired_unit.fire()

        elif self.button_type == "confirm main menu":
            game_transitions.to_main_menu()

        elif self.button_type == "quit":
            flags.crashed = True

        elif self.button_type == "wake up all":
            if main_loop_utility.action_possible():
                for current_pmob in status.pmob_list:
                    if current_pmob.sentry_mode:
                        current_pmob.set_sentry_mode(False)
                actor_utility.calibrate_actor_info_display(
                    status.mob_info_display, status.displayed_mob
                )
            else:
                text_utility.print_to_screen(
                    "You are busy and cannot disable sentry mode."
                )

        elif self.button_type == "confirm remove minister":
            removed_minister = status.displayed_minister
            removed_minister.just_removed = True
            removed_minister.appoint("none")
            public_opinion_penalty = removed_minister.status_number
            constants.public_opinion_tracker.change(-1 * public_opinion_penalty)

        elif self.button_type == "generate crash":
            if constants.effect_manager.effect_active("enable_crash_button"):
                print(1 / 0)
            else:
                flags.crashed = True

        elif self.button_type == "minimize interface collection":
            self.attached_collection.minimized = not self.attached_collection.minimized
            if not self.attached_collection.minimized:
                # If any movement within the collection occurred while minimized, makes sure all newly shown elements are at their correct locations
                self.attached_collection.set_origin(
                    self.parent_collection.x, self.parent_collection.y
                )

        elif self.button_type == "move interface collection":
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

        elif self.button_type == "reset interface collection":
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

        elif self.button_type == "tab":
            tabbed_collection = self.parent_collection.parent_collection
            tabbed_collection.current_tabbed_member = self.linked_element
            if (
                self.identifier == "inventory"
                and constants.effect_manager.effect_active("link_inventory_tabs")
            ):
                if tabbed_collection == status.mob_tabbed_collection:
                    alternate_collection = status.tile_tabbed_collection
                else:
                    alternate_collection = status.mob_tabbed_collection
                for linked_tab in alternate_collection.tabbed_members:
                    linked_tab_button = linked_tab.linked_tab_button
                    if linked_tab_button.identifier == "inventory":
                        linked_tab_button.parent_collection.parent_collection.current_tabbed_member = (
                            linked_tab_button.linked_element
                        )

        elif self.button_type == "rename settlement":
            if main_loop_utility.action_possible():
                constants.input_manager.start_receiving_input(
                    status.displayed_tile.cell.settlement.rename,
                    prompt="Type new settlement name: ",
                )
            else:
                text_utility.print_to_screen(
                    "You are busy and cannot rename this settlement."
                )

    def on_rmb_release(self):
        """
        Description:
            Controls what this button does when right clicked and released. By default, buttons will stop showing their outlines when released.
        Input:
            None
        Output:
            None
        """
        self.on_release()

    def on_release(self):
        """
        Description:
            Controls what this button does when left clicked and released. By default, buttons will stop showing their outlines when released.
        Input:
            None
        Output:
            None
        """
        self.showing_outline = False
        self.has_released = True

    def remove(self):
        """
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        Input:
            None
        Output:
            None
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
            self.button_type == "move interface collection"
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
            if self.button_type in ["move left", "move right", "move down", "move up"]:
                if status.displayed_mob == None or (
                    not status.displayed_mob.get_permission(constants.PMOB_PERMISSION)
                ):
                    return False
            elif self.button_type in ["sell commodity", "sell all commodity"]:
                return (
                    status.displayed_tile
                    and status.earth_grid in status.displayed_tile.grids
                    and self.attached_label.actor.current_item
                    in constants.collectable_resources
                )
            elif self.button_type == "sell each commodity":
                if (
                    status.displayed_tile
                    and status.earth_grid in status.displayed_tile.grids
                ):
                    for commodity in constants.collectable_resources:
                        if status.displayed_tile.get_inventory(commodity) > 0:
                            return True
                return False
            elif self.button_type in ["pick up each commodity", "drop each commodity"]:
                return self.attached_label.actor.get_inventory_used() > 0
            elif self.button_type == "use equipment":
                return self.attached_label.actor.current_item in status.equipment_types
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
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'equipment_type': string value - Type of equipment, like 'rifles'
        Output:
            None
        """
        input_dict["button_type"] = "remove equipment"
        self.equipment_type = input_dict["equipment_type"]
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
            and self.attached_label.actor.equipment.get(self.equipment_type, False)
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
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
        Output:
            None
        """
        input_dict["button_type"] = "start end turn"
        super().__init__(input_dict)

        image_input_dict = {"attached_image": self, "init_type": "warning image"}
        if self.parent_collection != "none":
            image_input_dict["parent_collection"] = self.parent_collection
            image_input_dict["member_config"] = {
                "order_exempt": True,
                "order_x_offset": 100,
            }
        self.warning_image = constants.actor_creation_manager.create_interface_element(
            image_input_dict
        )

        self.warning_image.set_image("misc/enemy_turn_icon.png")
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
    ):  # show warning if enemy movements or combat are still occurring
        """
        Description:
            Whether this button can show its enemy turn version using the 'warning' system, returning True if is the enemy's turn or if it is the enemy combat phase (not technically during enemy turn)
        Input:
            none
        Output:
            boolean: Returns whether this button's enemy turn version should be shown
        """
        if flags.player_turn and not flags.enemy_combat_phase:
            return False
        return True


class cycle_same_tile_button(button):
    """
    Button that appears near the displayed tile and cycles the order of mobs displayed in a tile
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
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
        Output:
            None
        """
        input_dict["button_type"] = "cycle tile mobs"
        super().__init__(input_dict)

    def on_click(self):
        """
        Description:
            Controls this button's behavior when clicked. This type of button cycles the order of mobs displayed in a tile, moving the first one shown to the bottom and moving others up
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            cycled_tile = status.displayed_tile
            moved_mob = cycled_tile.cell.contained_mobs.pop(0)
            cycled_tile.cell.contained_mobs.append(moved_mob)
            cycled_tile.cell.contained_mobs[0].cycle_select()
            actor_utility.calibrate_actor_info_display(
                status.tile_info_display, cycled_tile
            )  # updates mob info display list to show changed passenger order
        else:
            text_utility.print_to_screen("You are busy and cannot cycle units.")

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the currently displayed tile contains 3 or less mobs. Otherwise, returns same as superclass
        """
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_tile = status.displayed_tile
            if displayed_tile and len(displayed_tile.cell.contained_mobs) >= 4:
                return True
        return False


class same_tile_icon(button):
    """
    Button that appears near the displayed tile and selects mobs that are not currently at the top of the tile
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
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'index': int value - Index to determine which item of the displayed tile's cell's list of contained mobs is selected by this button
                'is_last': boolean value - Whether this is the last of the displayed tile's selection icons. If it is last, it will show all mobs are not being shown rather than being
                        attached to a specific mob
        Output:
            None
        """
        self.attached_mob = "none"
        input_dict["button_type"] = "same tile"
        super().__init__(input_dict)
        self.old_contained_mobs = []
        self.default_image_id = input_dict["image_id"]
        self.index = input_dict["index"]
        self.is_last = input_dict["is_last"]
        if self.is_last:
            self.name_list = []
        status.same_tile_icon_list.append(self)

    def reset(self):
        """
        Description:
            Resets this icon when a new tile is selected, forcing it to re-calibrate with any new units
        Input:
            None
        Output:
            None
        """
        self.resetting = True

    def on_click(self):
        """
        Description:
            Controls this button's behavior when clicked. This type of button selects the mob that it is currently attached to when clicked
        Input:
            None
        Output:
            None
        """
        if (not self.is_last) and self.attached_mob != "none":
            self.attached_mob.cycle_select()

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if there is no tile selected or if the selected tile has not been explored, otherwise returns same as superclass
        """
        self.update()
        return (
            status.displayed_tile
            and status.displayed_tile.cell.terrain_handler.visible
            and len(self.old_contained_mobs) > self.index
            and super().can_show()
        )

    def can_show_tooltip(self):
        """
        Description:
            Returns whether this button's tooltip can be shown. A same tile icon has the the normal requirements for a tooltip to be shown, along with requiring that it is attached to a unit
        Input:
            None
        Output:
            None
        """
        return self.attached_mob != "none" and super().can_show_tooltip()

    def update(self):
        """
        Description:
            Updates this icon's appearance based on the corresponding unit in the displayed tile, if any
        Input:
            None
        Output:
            None
        """
        if (
            status.displayed_tile
            and status.displayed_tile.cell.terrain_handler.visible
            and super().can_show()
        ):
            displayed_tile = status.displayed_tile
            if displayed_tile:
                new_contained_mobs = displayed_tile.cell.contained_mobs
                if (new_contained_mobs != self.old_contained_mobs) or self.resetting:
                    self.resetting = False
                    self.old_contained_mobs = []
                    for current_item in new_contained_mobs:
                        self.old_contained_mobs.append(current_item)
                    if self.is_last and len(new_contained_mobs) > self.index:
                        self.attached_mob = "last"
                        self.image.set_image("buttons/extra_selected_button.png")
                        name_list = []
                        for current_mob_index in range(len(self.old_contained_mobs)):
                            if current_mob_index > self.index - 1:
                                name_list.append(
                                    self.old_contained_mobs[current_mob_index].name
                                )
                        self.name_list = name_list

                    elif len(self.old_contained_mobs) > self.index:
                        self.attached_mob = self.old_contained_mobs[self.index]
                        self.image.set_image(self.attached_mob.images[0].image_id)
            else:
                self.attached_mob = "none"

    def draw(self):
        """
        Description:
            Draws this button and draws a copy of the this button's attached mob's image on top of it
        Input:
            None
        Output:
            None
        """
        if self.showing:
            if self.index == 0 and status.displayed_tile:
                if status.displayed_tile.cell.contained_mobs[0] == status.displayed_mob:
                    pygame.draw.rect(
                        constants.game_display,
                        constants.color_dict["bright green"],
                        self.outline,
                    )
                else:
                    pygame.draw.rect(
                        constants.game_display,
                        constants.color_dict["white"],
                        self.outline,
                    )
            super().draw()

    def update_tooltip(self):
        """
        Description:
            Sets this button's tooltip to what it should be, depending on its button_type. This type of button copies the tooltip of its attached mob
        Input:
            None
        Output:
            None
        """
        if not self.showing:
            self.set_tooltip([])
        else:
            if self.is_last:
                self.set_tooltip(["More: "] + self.name_list)
            else:
                self.attached_mob.update_tooltip()
                self.set_tooltip(
                    self.attached_mob.tooltip_text + ["Click to select this unit"]
                )


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
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
        Output:
            None
        """
        self.attached_mob = "none"
        input_dict["button_type"] = "fire unit"
        super().__init__(input_dict)

    def on_click(self):
        """
        Description:
            Controls this button's behavior when clicked. This type of button fires the selected unit
        Input:
            None
        Output:
            None
        """
        if (
            main_loop_utility.action_possible()
        ):  # when clicked, calibrate minimap to attached mob and move it to the front of each stack
            if not (
                self.attached_mob.get_permission(constants.VEHICLE_PERMISSION)
                and self.attached_mob.vehicle_type == "ship"
                and not self.attached_mob.can_leave()
            ):
                message = "Are you sure you want to fire this unit? Firing this unit would remove it, any units attached to it, and any associated upkeep from the game. /n /n"
                worker = self.attached_mob.get_worker()
                if worker:
                    message += status.worker_types[worker.worker_type].fired_description
                constants.notification_manager.display_notification(
                    {"message": message, "choices": ["fire", "cancel"]}
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

    def update_tooltip(self):
        """
        Description:
            Sets this button's tooltip to what it should be, depending on its button_type. This type of button describes how firing units works
        Input:
            None
        Output:
            None
        """
        if not self.showing:
            self.set_tooltip([])
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
            self.set_tooltip(tooltip_text)


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
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'to_mode': string value - Game mode that this button switches to. If this equals 'previous', it switches to the previous game mode rather than a preset one
        Output:
            None
        """
        self.to_mode = input_dict["to_mode"]
        self.to_mode_tooltip_dict = {}
        self.to_mode_tooltip_dict["main_menu"] = [
            "Exits to the main menu",
            "Does not automatically save the game",
        ]
        self.to_mode_tooltip_dict["strategic"] = ["Enters the strategic map screen"]
        self.to_mode_tooltip_dict["earth"] = ["Enters the Earth headquarters screen"]
        self.to_mode_tooltip_dict["ministers"] = [
            "Enters the minister conference room screen"
        ]
        input_dict["button_type"] = "switch game mode"
        super().__init__(input_dict)

    def on_click(self):
        """
        Description:
            Controls this button's behavior when clicked. This type of button transtions from the current game mode to either the previous game mode or one specified on button initialization
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            if self.to_mode == "main_menu":
                constants.notification_manager.display_notification(
                    {
                        "message": "Are you sure you want to exit to the main menu without saving? /n /n",
                        "choices": ["confirm main menu", "none"],
                    }
                )
            if self.to_mode != "main_menu":
                game_transitions.set_game_mode(self.to_mode)
        else:
            text_utility.print_to_screen("You are busy and cannot switch screens.")

    def update_tooltip(self):
        """
        Description:
            Sets this button's tooltip to what it should be, depending on its button_type. This type of button describes which game mode it switches to
        Input:
            None
        Output:
            None
        """
        self.set_tooltip(utility.copy_list(self.to_mode_tooltip_dict[self.to_mode]))

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns whether this button should be drawn
        """
        if self.to_mode != "main_menu":
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
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'minister_type': string value - Minister office that this button is linked to, causing this button to always be connected to the minister in that office. If equals 'none',
                    can be calibrated to an available minister candidate
        Output:
            None
        """
        self.default_image_id = "ministers/empty_portrait.png"
        self.current_minister = "none"
        input_dict["image_id"] = self.default_image_id
        input_dict["button_type"] = "minister portrait"
        super().__init__(input_dict)
        self.insert_collection_above()
        self.minister_type = input_dict["minister_type"]  # Position, like General
        if self.minister_type == "none":  # If available minister portrait
            if "ministers" in self.modes:
                status.available_minister_portrait_list.append(self)
            warning_x_offset = scaling.scale_width(-100)
        else:
            self.type_keyword = constants.minister_type_dict[self.minister_type]
            warning_x_offset = 0
        status.minister_image_list.append(self)

        self.warning_image = constants.actor_creation_manager.create_interface_element(
            {
                "attached_image": self,
                "init_type": "warning image",
                "parent_collection": self.parent_collection,
                "member_config": {"x_offset": warning_x_offset, "y_offset": 0},
            }
        )
        self.parent_collection.can_show_override = self  # Parent collection is considered showing when this label can show, allowing ordered collection to work correctly

        self.calibrate("none")

    def can_show_warning(self):
        """
        Description:
            Returns whether this image should display its warning image. It should be shown when this image is visible and its attached minister is about to be fired at the end of the turn
        Input:
            None
        Output:
            Returns whether this image should display its warning image
        """
        if not self.current_minister == "none":
            if (
                self.current_minister.just_removed
                and self.current_minister.current_position == "none"
            ):
                return True
        elif (
            self.minister_type != "none"
        ):  # If portrait in minister table and no minister assigned for office
            return True
        return False

    def draw(self):
        """
        Description:
            Draws this button's image along with a white background and, if its minister is currently selected, a flashing green outline
        Input:
            None
        Output:
            None
        """
        showing = False
        if (
            self.showing and constants.current_game_mode == "ministers"
        ):  # Draw outline around portrait if minister selected
            showing = True
            if self.current_minister != "none":
                pygame.draw.rect(
                    constants.game_display, constants.color_dict["white"], self.Rect
                )  # draw white background
                if (
                    status.displayed_minister == self.current_minister
                    and flags.show_selection_outlines
                ):
                    pygame.draw.rect(
                        constants.game_display,
                        constants.color_dict["bright green"],
                        self.outline,
                    )
        super().draw(
            allow_show_outline=(constants.current_game_mode == "ministers")
        )  # Show outline for selection icons on ministers mode but not the overlapping ones on strategic mode
        if showing and self.warning_image.showing:
            self.warning_image.draw()

    def on_click(self):
        """
        Description:
            Controls this button's behavior when clicked. This type of button selects its attached minister when clicked
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            if (
                constants.current_game_mode == "ministers"
                and self.current_minister != "none"
            ):
                if self.current_minister != "none":
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
                constants.current_game_mode != "ministers"
            ):  # If clicked while not on ministers screen, go to ministers screen and select that minister
                old_minister = self.current_minister
                game_transitions.set_game_mode("ministers")
                self.current_minister = old_minister
                if self.current_minister != "none":
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
            string/minister new_minister: The minister whose information is matched by this button. If this equals 'none', this button is detached from any ministers
        Output:
            None
        """
        if new_minister == None:
            new_minister = "none"
        if (
            new_minister != "none"
        ):  # If calibrated to non-minister, attempt to calibrate to that unit's controlling minister
            if new_minister.actor_type != "minister":
                if hasattr(new_minister, "controlling_minister"):
                    new_minister = new_minister.controlling_minister
                else:
                    new_minister = "none"

        if new_minister != "none":
            new_minister.update_tooltip()
            self.tooltip_text = new_minister.tooltip_text
            if "ministers" in self.modes:
                self.image.set_image(
                    new_minister.image_id
                    + actor_utility.generate_label_image_id(new_minister.get_f_lname())
                )
            else:
                self.image.set_image(new_minister.image_id)
        elif "ministers" in self.modes:  # Show empty minister if minister screen icon
            if self.minister_type == "none":  # If available minister portrait
                self.tooltip_text = ["There is no available candidate in this slot."]
            else:  # If appointed minister portrait
                self.tooltip_text = [
                    "No " + self.minister_type + " is currently appointed.",
                    "Without a "
                    + self.minister_type
                    + ", "
                    + self.type_keyword
                    + "-oriented actions are not possible",
                ]
            self.image.set_image(self.default_image_id)
        else:  # If minister icon on strategic mode, no need to show empty minister
            self.image.set_image("misc/empty.png")
        self.current_minister = new_minister

    def update_tooltip(self):
        """
        Description:
            Sets this button's tooltip to what it should be, depending on its button_type. This type of button copies the tooltip text of its attached minister, or says there is no attached minister if there is none attached
        Input:
            None
        Output:
            None
        """
        if not self.current_minister == "none":
            self.current_minister.update_tooltip()
            self.tooltip_text = self.current_minister.tooltip_text
        self.set_tooltip(self.tooltip_text)


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
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'direction': string value - If equals 'right', this button cycles forward in the list of available ministers. If equals 'left', this button cycles backwards in the list of
                    available ministers
        Output:
            None
        """
        self.direction = input_dict["direction"]
        input_dict["button_type"] = "cycle available ministers"
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
        Description:
            Controls this button's behavior when clicked. This type of button changes the range of available ministers that are displayed depending on its direction
        Input:
            None
        Output:
            None
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
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
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
        Description:
            When this button is clicked, increment/decrement the corresponding value of the parent collection and update its display
        Input:
            None
        Output:
            None
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

    def update_tooltip(self) -> None:
        """
        Description:
            Sets this button's tooltip to what it should be, describing its scroll functionality
        Input:
            None
        Output:
            None
        """
        if self.increment > 0:
            descriptor = "down"
        elif self.increment < 0:
            descriptor = "up"
        self.set_tooltip(
            [
                "Click to scroll "
                + descriptor
                + " "
                + str(abs(self.increment))
                + " "
                + self.value_name.replace("_", " ")
            ]
        )


class commodity_button(button):
    """
    Button appearing near commodity prices label that can be clicked as a target for advertising campaigns
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
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'commodity': string value - Commodity that this button corresponds to
        Output:
            None
        """
        self.commodity = input_dict["commodity"]
        input_dict["button_type"] = "commodity selection"
        super().__init__(input_dict)
        self.showing_background = False
        self.outline.width = 0
        self.outline.height = 0
        self.outline.x = 0
        self.outline.y = 0

    def on_click(self):
        """
        Description:
            Controls this button's behavior when clicked. When the player is choosing a target for an advertising campaign, clicking on this button starts an advertising campaign for this button's commodity
        Input:
            None
        Output:
            None
        """
        if flags.choosing_advertised_commodity:
            if self.commodity == "consumer goods":
                text_utility.print_to_screen("You cannot advertise consumer goods.")
            else:
                can_advertise = False
                for current_commodity in constants.collectable_resources:
                    if (
                        current_commodity != self.commodity
                        and constants.item_prices[current_commodity] > 1
                    ):
                        can_advertise = True
                        break
                if can_advertise:
                    status.actions["advertising_campaign"].start(
                        status.displayed_mob, self.commodity
                    )
                else:
                    text_utility.print_to_screen(
                        "You cannot advertise "
                        + self.commodity
                        + " because all other commodities are already at the minimum price."
                    )

    def can_show_tooltip(self):
        """
        Description:
            Returns whether this button's tooltip can be shown. A commodity button never shows a tooltip
        Input:
            None
        Output:
            None
        """
        return False


class show_previous_reports_button(button):
    """
    Button appearing near money label that can be clicked to display the previous turn's production, sales, and financial reports again
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
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
        Output:
            None
        """
        input_dict["button_type"] = "show previous reports"
        super().__init__(input_dict)

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
        Description:
            Controls this button's behavior when clicked. This type of button displays the previous turn's financial report again
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            for report in [
                status.previous_production_report,
                status.previous_sales_report,
                status.previous_financial_report,
            ]:
                if report:
                    constants.notification_manager.display_notification(
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
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'linked_element': Member collection of tabbed collection that this button is associated with
                'identifier': Description of type of tab button, like 'settlement' or 'inventory'
        Output:
            None
        """
        input_dict["button_type"] = "tab"
        self.linked_element = input_dict["linked_element"]
        self.linked_element.linked_tab_button = self
        self.identifier = input_dict["identifier"]
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
            if self.identifier == "settlement":
                return_value = bool(
                    status.displayed_tile.cell.settlement
                    or status.displayed_tile.cell.has_building("infrastructure")
                )

            elif self.identifier == "inventory":
                if self.linked_element == status.tile_inventory_collection:
                    return_value = (
                        status.displayed_tile.inventory
                        or status.displayed_tile.inventory_capacity > 0
                        or status.displayed_tile.infinite_inventory_capacity
                    )
                else:
                    return_value = status.displayed_mob.inventory_capacity > 0 or (
                        status.displayed_mob.get_permission(constants.PMOB_PERMISSION)
                        and status.displayed_mob.equipment
                    )

            elif self.identifier == "reorganization":
                return_value = status.displayed_mob.get_permission(
                    constants.PMOB_PERMISSION
                )

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
    Button that reorganizes 1 or more units into 1 or more other units, based on which are present - such as combining a ship and explorer to a ship with explorer as a
        passenger, or combining a worker and explorer to an expedition
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
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'input_sources': string list value - List of interface elements to use to determine the pmobs to use as formula input
                'output_destinations': string list value - List of interface elements to send formula results to
                'allowed_procedures': string list value - Types of merge/split procedure this button can execute
        Output:
            None
        """
        input_dict["button_type"] = "reorganize unit"
        self.allowed_procedures = input_dict["allowed_procedures"]
        super().__init__(input_dict)
        self.has_button_press_override = True

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
        return (
            super().enable_shader_condition()
            and not self.parent_collection.autofill_actors["procedure"]
            in self.allowed_procedures
        )

    def update_tooltip(self):
        """
        Description:
            Sets this button's tooltip to what it should be, depending on its button_type. This type of button describes the current procedure that it would complete
        Input:
            None
        Output:
            None
        """
        if "merge" in self.allowed_procedures:
            self.tooltip_text = [
                "Combines the units on the left to form the unit on the right"
            ]
        else:
            self.tooltip_text = [
                "Separates the unit on the right to form the units on the left"
            ]
        if (
            self.parent_collection.autofill_actors["procedure"]
            in self.allowed_procedures
        ):
            if self.parent_collection.autofill_actors["procedure"] == "merge":
                self.tooltip_text.append(
                    f"Press to combine the {self.parent_collection.autofill_actors['officer'].name} and the {self.parent_collection.autofill_actors['worker'].name} into a {self.parent_collection.autofill_actors['group'].name}"
                )
            elif self.parent_collection.autofill_actors["procedure"] == "split":
                self.tooltip_text.append(
                    f"Press to separate the {self.parent_collection.autofill_actors['group'].name} into a {self.parent_collection.autofill_actors['officer'].name} and {self.parent_collection.autofill_actors['worker'].name}"
                )
            elif self.parent_collection.autofill_actors["procedure"] == "crew":
                self.tooltip_text.append(
                    f"Press to combine the {self.parent_collection.autofill_actors['officer'].name} and the {self.parent_collection.autofill_actors['worker'].name} into a crewed {self.parent_collection.autofill_actors['group'].name}"
                )
            elif self.parent_collection.autofill_actors["procedure"] == "uncrew":
                self.tooltip_text.append(
                    f"Press to separate the {self.parent_collection.autofill_actors['group'].name} into {self.parent_collection.autofill_actors['worker'].name} and a non-crewed {self.parent_collection.autofill_actors['officer'].name}"
                )
        elif self.parent_collection.autofill_actors["procedure"] != "none":
            self.tooltip_text.append(
                f"The {self.parent_collection.autofill_actors['procedure']} procedure is controlled by the other button"
            )
        else:
            self.tooltip_text.append(
                "The current combination of units has no valid reorganization procedure"
            )

        self.set_tooltip(self.tooltip_text)

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button completes the determined procedure based
            on the current input cell contents
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            procedure_actors = self.parent_collection.autofill_actors
            if procedure_actors["procedure"] in self.allowed_procedures:
                procedure_type = "none"
                dummy_autofill_target_to_procedure_dict = {
                    "officer": "split",
                    "worker": "split",
                    "group": "merge",
                }
                # type of procedure to do if dummy version of corresponding unit found - if a dummy officer is found, the procedure must be a split

                for autofill_target_type in dummy_autofill_target_to_procedure_dict:
                    if procedure_actors[autofill_target_type] != "none":
                        if procedure_type != "invalid" and procedure_actors[
                            autofill_target_type
                        ].get_permission(constants.DUMMY_PERMISSION):
                            procedure_type = dummy_autofill_target_to_procedure_dict[
                                autofill_target_type
                            ]
                    else:
                        procedure_type = "invalid"

                if procedure_type == "split" and procedure_actors[
                    "officer"
                ].get_permission(
                    constants.VEHICLE_PERMISSION
                ):  # if the 'officer' unit is actually a vehicle, do the vehicle version of the procedure
                    procedure_type = "uncrew"
                elif procedure_type == "merge" and procedure_actors[
                    "officer"
                ].get_permission(constants.VEHICLE_PERMISSION):
                    procedure_type = "crew"

                if procedure_type == "merge":
                    if procedure_actors[
                        "worker"
                    ].worker_type == "religious" and not procedure_actors[
                        "officer"
                    ].get_permission(
                        constants.EVANGELIST_PERMISSION
                    ):
                        text_utility.print_to_screen(
                            "Church volunteers can only be combined with evangelists."
                        )
                    elif (
                        procedure_actors["officer"].get_permission(
                            constants.EVANGELIST_PERMISSION
                        )
                        and procedure_actors["worker"].worker_type != "religious"
                    ):
                        text_utility.print_to_screen(
                            "Evangelists can only be combined with church volunteers."
                        )
                    else:
                        constants.actor_creation_manager.create_group(
                            procedure_actors["worker"], procedure_actors["officer"]
                        ).select()

                elif procedure_type == "crew":
                    if (
                        procedure_actors["officer"].get_vehicle_name()
                        in status.worker_types[
                            procedure_actors["worker"].worker_type
                        ].can_crew
                    ):
                        procedure_actors["worker"].crew_vehicle(
                            procedure_actors["officer"]
                        )
                    else:
                        text_utility.print_to_screen(
                            f"{status.worker_types[procedure_actors['worker'].worker_type].name.capitalize()} cannot crew {procedure_actors['officer'].get_vehicle_name()}s."
                        )

                elif procedure_type == "split":
                    procedure_actors["group"].disband()

                elif procedure_type == "uncrew":
                    if (
                        procedure_actors["group"].contained_mobs
                        or procedure_actors["group"].get_held_commodities()
                    ):
                        text_utility.print_to_screen(
                            f"You cannot remove the crew from a {procedure_actors['group'].vehicle_type} with passengers or cargo."
                        )
                    else:
                        procedure_actors["group"].crew.uncrew_vehicle(
                            procedure_actors["group"]
                        )
            elif "merge" in self.allowed_procedures:
                text_utility.print_to_screen(
                    "This button executes merge and crew procedures, which require workers and an officer/uncrewed vehicle in the same tile"
                )
            elif "split" in self.allowed_procedures:
                text_utility.print_to_screen(
                    "This button executes split and uncrew procedures, which require a group or crewed vehicle to be selected"
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
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'autofill_target_type': string value - Type of autofill target that this button cycles through - autofill target types are 'officer', 'worker', and 'group'
        Output:
            None
        """
        self.autofill_target_type = input_dict["autofill_target_type"]
        input_dict["button_type"] = "cycle autofill"
        super().__init__(input_dict)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button can be shown. An autofill cycle button is only shown when an autofill is occurring and other options are available - allow cycling
                autofill if current autofill is a real, non-selected mob and there is at least 1 valid alternative - it makes no sense to cycle a dummy mob for a real one
                in the same tile, and the selected mob is locked and can't be cycled
        Input:
            None
        Output:
            boolean: Returns True if this button can appear, otherwise returns False
        """
        if super().can_show(skip_parent_collection=skip_parent_collection):
            if (
                self.parent_collection.autofill_actors[self.autofill_target_type]
                != status.displayed_mob
            ):
                if (
                    self.parent_collection.autofill_actors[self.autofill_target_type]
                    != "none"
                ):
                    if not self.parent_collection.autofill_actors[
                        self.autofill_target_type
                    ].get_permission(constants.DUMMY_PERMISSION):
                        if self.autofill_target_type == "worker":
                            return status.displayed_mob.images[
                                0
                            ].current_cell.has_worker(required_number=2)
                        elif self.autofill_target_type == "officer":
                            return status.displayed_mob.images[
                                0
                            ].current_cell.has_officer(required_number=2)
                        # allow cycling autofill if current autofill is a real, non-selected mob and there is at least 1 alternative
                        # it makes no sense to cycle a dummy mob for a real one in the same tile, and the selected mob is locked and can't be cycled
        return False

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button cycles the unit in an autofill input
                cell to the next valid alternative - assumes that there is a valid alternative, as on_click is only possible if can_show is True
        Input:
            None
        Output:
            None
        """
        current_cell = status.displayed_mob.get_cell()
        self.parent_collection.search_start_index = (
            current_cell.contained_mobs.index(
                self.parent_collection.autofill_actors[self.autofill_target_type]
            )
            + 1
        )
        self.parent_collection.calibrate(status.displayed_mob)
        # start autofill search for corresponding target type at index right after the current target actor


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
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
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
        input_dict["button_type"] = "action"
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

    def update_tooltip(self):
        """
        Description:
            Sets this button's tooltip to what it should be, depending on its mapped 'update_tooltip' function
        Input:
            None
        Output:
            None
        """
        self.set_tooltip(self.corresponding_action.update_tooltip())

    def get_unit(self):
        """
        Description:
            Returns the unit this button appears next to
        Input:
            None
        Output:
            None
        """
        if self.corresponding_action.actor_type == "mob":
            return status.displayed_mob
        elif self.corresponding_action.actor_type == "tile":
            return status.displayed_tile
        elif self.corresponding_action.actor_type in ["minister", "prosecutor"]:
            if constants.current_game_mode == "trial":
                return status.displayed_prosecution
            else:
                return status.displayed_minister

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on this button's mapped 'on_click' function
        Input:
            None
        Output:
            None
        """
        self.corresponding_action.on_click(self.get_unit())


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
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
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
        input_dict["button_type"] = "anonymous"
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
        Description:
            Controls this button's behavior when clicked. Choice buttons remove their notifications when clicked, along with the normal behaviors associated with their button_type
        Input:
            None
        Output:
            None
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
        Description:
            Draws this button below its choice notification and draws a description of what it does on top of it
        Input:
            None
        Output:
            None
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

    def update_tooltip(self):
        """
        Description:
            Sets this image's tooltip to what it should be, depending on its button_type
        Input:
            None
        Output:
            None
        """
        self.set_tooltip(self.tooltip)


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
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'map_mode": Map mode that this button sets, like "default" or "altitude"
        Output:
            None
        """
        input_dict["button_type"] = "map mode"
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
        constants.current_map_mode = self.map_mode
        for grid in status.grid_list:
            for cell in grid.get_flat_cell_list():
                cell.tile.update_image_bundle()

    def update_tooltip(self):
        """
        Description:
            Sets this button's tooltip to what it should be, depending on its mapped 'update_tooltip' function
        Input:
            None
        Output:
            None
        """
        self.set_tooltip([f"Sets the map mode to {self.map_mode}"])
