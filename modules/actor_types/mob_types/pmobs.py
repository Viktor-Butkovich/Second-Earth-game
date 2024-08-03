# Contains functionality for player-controlled mobs

import pygame
import random
from ..mobs import mob
from ...util import (
    text_utility,
    utility,
    actor_utility,
)
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags
from typing import Dict


class pmob(mob):
    """
    Short for player-controlled mob, mob controlled by the player
    """

    def __init__(self, from_save, input_dict, original_constructor: bool = True):
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'grids': grid list value - grids in which this mob's images can appear
                'image': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'name': string value - Required if from save, this mob's name
                'modes': string list value - Game modes during which this mob's images can appear
                'end_turn_destination': string or int tuple value - Required if from save, 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string - Required if end_turn_destination is not 'none', matches the status key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'max_movement_points': int value - Required if from save, maximum number of movement points this mob can have
                'sentry_mode': boolean value - Required if from save, whether this unit is in sentry mode, preventing it from being in the turn order
                'in_turn_queue': boolean value - Required if from save, whether this unit is in the turn order, allowing end unit turn commands, etc. to persist after saving/loading
                'base_automatic_route': int tuple list value - Required if from save, list of the coordinates in this unit's automatic movement route, with the first coordinates being the start and the last being the end. List empty if
                    no automatic movement route has been designated
                'in_progress_automatic_route': string/int tuple list value - Required if from save, list of the coordinates and string commands this unit will execute, changes as the route is executed
                'inventory': dictionary value - This actor's initial items carried, with an integer value corresponding to amount of each item type
                'equipment': dictionary value - This actor's initial items equipped, with a boolean value corresponding to whether each type of equipment is equipped
        Output:
            None
        """
        self.sentry_mode = False
        super().__init__(from_save, input_dict, original_constructor=False)
        self.selection_outline_color = "bright green"
        status.pmob_list.append(self)
        self.set_controlling_minister_type("none")
        self.equipment = {}
        for current_equipment in input_dict.get("equipment", {}):
            if input_dict.get("equipment", {}).get(current_equipment, False):
                status.equipment_types[current_equipment].equip(self)
        if from_save:
            if (
                input_dict["end_turn_destination"] != "none"
            ):  # end turn destination is a tile and can't be pickled, need to find it again after loading
                end_turn_destination_x, end_turn_destination_y = input_dict[
                    "end_turn_destination"
                ]
                end_turn_destination_grid = getattr(
                    status, input_dict["end_turn_destination_grid_type"]
                )
                self.end_turn_destination = end_turn_destination_grid.find_cell(
                    end_turn_destination_x, end_turn_destination_y
                ).tile
            self.default_name = input_dict["default_name"]
            self.set_name(self.default_name)
            self.set_sentry_mode(input_dict["sentry_mode"])
            self.set_automatically_replace(input_dict["automatically_replace"])
            if (
                input_dict["in_turn_queue"]
                and input_dict["end_turn_destination"] == "none"
            ):
                self.add_to_turn_queue()
            else:
                self.remove_from_turn_queue()
            self.base_automatic_route = input_dict["base_automatic_route"]
            self.in_progress_automatic_route = input_dict["in_progress_automatic_route"]
            self.wait_until_full = input_dict["wait_until_full"]
        else:
            self.default_name = self.name
            self.set_max_movement_points(4)
            self.set_sentry_mode(False)
            self.set_automatically_replace(True)
            self.add_to_turn_queue()
            self.base_automatic_route = (
                []
            )  # first item is start of route/pickup, last item is end of route/dropoff
            self.in_progress_automatic_route = (
                []
            )  # first item is next step, last item is current location
            self.wait_until_full = False
        self.attached_cell_icon_list = []
        self.finish_init(original_constructor, from_save, input_dict)

    def finish_init(
        self,
        original_constructor: bool,
        from_save: bool,
        input_dict: Dict[str, any],
        create_portrait: bool = True,
    ):
        """
        Description:
            Finishes initialization of this actor, called after the original is finished
        Input:
            boolean original_constructor: Whether this is the original constructor call for this object
        Output:
            None
        """
        if original_constructor:
            super().finish_init(
                original_constructor,
                from_save,
                input_dict,
                create_portrait=create_portrait,
            )
            if ("select_on_creation" in input_dict) and input_dict[
                "select_on_creation"
            ]:
                self.on_move()

    def permissions_setup(self) -> None:
        """
        Description:
            Sets up this mob's permissions
        Input:
            None
        Output:
            None
        """
        super().permissions_setup()
        self.set_permission(constants.PMOB_PERMISSION, True)

    def on_move(self):
        """
        Description:
            Automatically called when unit arrives in a tile for any reason
        Input:
            None
        Output:
            None
        """
        super().on_move()
        if self.get_cell() != "none":
            for cell in [self.get_cell()] + self.get_cell().adjacent_list:
                if not cell.terrain_handler.knowledge_available(
                    constants.TERRAIN_KNOWLEDGE
                ):
                    cell.terrain_handler.set_parameter(
                        "knowledge", constants.TERRAIN_KNOWLEDGE_REQUIREMENT
                    )

    def to_save_dict(self):
        """
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                Along with superclass outputs, also saves the following values:
                'default_name': string value - This actor's name without modifications like veteran
                'end_turn_destination': string or int tuple value- 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not 'none', matches the status key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'sentry_mode': boolean value - Whether this unit is in sentry mode, preventing it from being in the turn order
                'in_turn_queue': boolean value - Whether this unit is in the turn order, allowing end unit turn commands, etc. to persist after saving/loading
                'base_automatic_route': int tuple list value - List of the coordinates in this unit's automatic movement route, with the first coordinates being the start and the last being the end. List empty if
                    no automatic movement route has been designated
                'in_progress_automatic_route': string/int tuple list value - List of the coordinates and string commands this unit will execute, changes as the route is executed
                'automatically_replace': boolean value  Whether this unit or any of its components should be replaced automatically in the event of attrition
                'equipment': dictionary value - This actor's items equipped, with a boolean value corresponding to whether each type of equipment is equipped
        """
        save_dict = super().to_save_dict()
        if self.end_turn_destination == "none":
            save_dict["end_turn_destination"] = "none"
        else:  # end turn destination is a tile and can't be pickled, need to save its location to find it again after loading
            for grid_type in constants.grid_types_list:
                if self.end_turn_destination.grid == getattr(status, grid_type):
                    save_dict["end_turn_destination_grid_type"] = grid_type
            save_dict["end_turn_destination"] = (
                self.end_turn_destination.x,
                self.end_turn_destination.y,
            )
        save_dict["default_name"] = self.default_name
        save_dict["sentry_mode"] = self.sentry_mode
        save_dict["in_turn_queue"] = self in status.player_turn_queue
        save_dict["base_automatic_route"] = self.base_automatic_route
        save_dict["in_progress_automatic_route"] = self.in_progress_automatic_route
        save_dict["wait_until_full"] = self.wait_until_full
        save_dict["automatically_replace"] = self.automatically_replace
        save_dict["equipment"] = self.equipment
        return save_dict

    def clear_attached_cell_icons(self):
        """
        Description:
            Removes all of this unit's cell icons
        Input:
            None
        Output:
            None
        """
        for current_cell_icon in self.attached_cell_icon_list:
            current_cell_icon.remove_complete()
        self.attached_cell_icon_list = []

    def create_cell_icon(self, x, y, image_id):
        """
        Description:
            Creates a cell icon managed by this mob with the inputted image at the inputted coordinates
        Input:
            int x: cell icon's x coordinate on main grid
            int y: cell icon's y coordinate on main grid
            string image_id: cell icon's image_id
            string init_type='cell icon': init type of actor to create
            dictionary extra_parameters=None: dictionary of any extra parameters to pass to the created actor
        """
        self.attached_cell_icon_list.append(
            constants.actor_creation_manager.create(
                False,
                {
                    "coordinates": (x, y),
                    "grids": self.grids,
                    "image": image_id,
                    "modes": self.grids[0].modes,
                    "init_type": "cell icon",
                },
            )
        )

    def add_to_automatic_route(self, new_coordinates):
        """
        Description:
            Adds the inputted coordinates to this unit's automated movement route, changing the in-progress route as needed
        Input:
            int tuple new_coordinates: New x and y coordinates to add to the route
        Output:
            None
        """
        self.base_automatic_route.append(new_coordinates)
        self.calculate_automatic_route()
        if self == status.displayed_mob:
            actor_utility.calibrate_actor_info_display(status.mob_info_display, self)

    def calculate_automatic_route(self):
        """
        Description:
            Creates an in-progress movement route based on the base movement route when the base movement route changes
        Input:
            None
        Output:
            None
        """
        reversed_base_automatic_route = utility.copy_list(self.base_automatic_route)
        reversed_base_automatic_route.reverse()

        self.in_progress_automatic_route = ["start"]
        # imagine base route is [0, 1, 2, 3, 4]
        # reverse route is [4, 3, 2, 1, 0]
        for current_index in range(
            1, len(self.base_automatic_route)
        ):  # first destination is 2nd item in list
            self.in_progress_automatic_route.append(
                self.base_automatic_route[current_index]
            )
        # now in progress route is ['start', 1, 2, 3, 4]

        self.in_progress_automatic_route.append("end")
        for current_index in range(1, len(reversed_base_automatic_route)):
            self.in_progress_automatic_route.append(
                reversed_base_automatic_route[current_index]
            )
        # now in progress route is ['start', 1, 2, 3, 4, 'end', 3, 2, 1, 0]

    def can_follow_automatic_route(self):
        """
        Description:
            Returns whether the next step of this unit's in-progress movement route could be completed at this moment
        Input:
            None
        Output
            boolean: Returns whether the next step of this unit's in-progress movement route could be completed at this moment
        """
        next_step = self.in_progress_automatic_route[0]
        if next_step == "end":  # can drop off freely unless train without train station
            if not (
                self.get_permission(constants.VEHICLE_PERMISSION)
                and self.vehicle_type == "train"
                and not self.get_cell().has_intact_building("train_station")
            ):
                return True
            else:
                return False
        elif next_step == "start":
            # ignores consumer goods
            if (
                self.wait_until_full
                and (
                    self.get_cell().tile.get_inventory_used() >= self.inventory_capacity
                    or self.get_cell().tile.get_inventory_remaining() <= 0
                )
            ) or (
                (not self.wait_until_full)
                and (
                    len(self.get_cell().tile.get_held_commodities(True)) > 0
                    or self.get_inventory_used() > 0
                )
            ):  # only start round trip if there is something to deliver, either from tile or in inventory already
                # If wait until full, instead wait until full load to transport or no warehouse space left
                if not (
                    self.get_permission(constants.VEHICLE_PERMISSION)
                    and self.vehicle_type == "train"
                    and not self.get_cell().has_intact_building("train_station")
                ):  # can pick up freely unless train without train station
                    return True
                else:
                    return False
            else:
                return False
        else:  # must have enough movement points, not blocked
            x_change = next_step[0] - self.x
            y_change = next_step[1] - self.y
            return self.can_move(x_change, y_change, False)

    def follow_automatic_route(self):
        """
        Description:
            Moves along this unit's in-progress movement route until it cannot complete the next step. A unit will wait for commodities to transport from the start, then pick them up and move along the path, picking up others along
                the way. At the end of the path, it drops all commodities and moves back towards the start
        Input:
            None
        Output:
            None
        """
        progressed = False
        if len(self.in_progress_automatic_route) > 0:
            while self.can_follow_automatic_route():
                next_step = self.in_progress_automatic_route[0]
                if next_step == "start":
                    self.pick_up_all_commodities(True)
                elif next_step == "end":
                    self.drop_inventory()
                else:
                    if not (
                        self.get_permission(constants.VEHICLE_PERMISSION)
                        and self.vehicle_type == "train"
                        and not self.get_cell().has_intact_building("train_station")
                    ):
                        if (
                            self.get_next_automatic_stop() == "end"
                        ):  # only pick up commodities on way to end
                            self.pick_up_all_commodities(
                                True
                            )  # attempt to pick up commodities both before and after moving
                    x_change = next_step[0] - self.x
                    y_change = next_step[1] - self.y
                    self.move(x_change, y_change)
                    if not (
                        self.get_permission(constants.VEHICLE_PERMISSION)
                        and self.vehicle_type == "train"
                        and not self.get_cell().has_intact_building("train_station")
                    ):
                        if (
                            self.get_next_automatic_stop() == "end"
                        ):  # only pick up commodities on way to end
                            self.pick_up_all_commodities(True)
                progressed = True
                self.in_progress_automatic_route.append(
                    self.in_progress_automatic_route.pop(0)
                )  # move first item to end

        return progressed  # returns whether unit did anything to show unit in movement routes report

    def get_next_automatic_stop(self):
        """
        Description:
            Returns the next stop for this unit's in-progress automatic route, or 'none' if there are stops
        Input:
            None
        Output:
            string: Returns the next stop for this unit's in-progress automatic route, or 'none' if there are stops
        """
        for current_stop in self.in_progress_automatic_route:
            if current_stop in ["start", "end"]:
                return current_stop
        return "none"

    def pick_up_all_commodities(self, ignore_consumer_goods=False):
        """
        Description:
            Adds as many local commodities to this unit's inventory as possible, possibly choosing not to pick up consumer goods based on the inputted boolean
        Input:
            boolean ignore_consumer_goods = False: Whether to not pick up consumer goods from this unit's tile
        Output:
            None
        """
        tile = self.get_cell().tile
        while (
            self.get_inventory_remaining() > 0
            and len(tile.get_held_commodities(ignore_consumer_goods)) > 0
        ):
            commodity = tile.get_held_commodities(ignore_consumer_goods)[0]
            self.change_inventory(commodity, 1)
            tile.change_inventory(commodity, -1)

    def clear_automatic_route(self):
        """
        Description:
            Removes this unit's saved automatic movement route
        Input:
            None
        Output:
            None
        """
        self.base_automatic_route = []
        self.in_progress_automatic_route = []
        if self == status.displayed_mob:
            actor_utility.calibrate_actor_info_display(status.mob_info_display, self)

    def set_automatically_replace(self, new_value):
        """
        Description:
            Sets this unit's automatically replace status
        Input:
            boolean new_value: New automatically replace value
        Output:
            None
        """
        self.automatically_replace = new_value
        displayed_mob = status.displayed_mob
        if self == displayed_mob:
            actor_utility.calibrate_actor_info_display(status.mob_info_display, self)
        elif (
            displayed_mob
            and displayed_mob.get_permission(constants.GROUP_PERMISSION)
            and self in [displayed_mob.officer, displayed_mob.worker]
        ):
            actor_utility.calibrate_actor_info_display(
                status.mob_info_display, displayed_mob
            )

    def get_image_id_list(self, override_values={}):
        """
        Description:
            Generates and returns a list this actor's image file paths and dictionaries that can be passed to any image object to display those images together in a particular order and
                orientation
        Input:
            None
        Output:
            list: Returns list of string image file paths, possibly combined with string key dictionaries with extra information for offset images
        """
        image_id_list = super().get_image_id_list(override_values)
        if self.get_permission(constants.VETERAN_PERMISSION):
            image_id_list.append("misc/veteran_icon.png")
        if self.sentry_mode:
            image_id_list.append("misc/sentry_icon.png")
        return image_id_list

    def set_sentry_mode(self, new_value):
        """
        Description:
            Sets a new sentry mode of this status, creating a sentry icon or removing the existing one as needed
        Input:
            boolean new_value: New sentry mode status for this unit
        Output:
            None
        """
        old_value = self.sentry_mode
        if self.get_permission(constants.GROUP_PERMISSION):
            self.officer.set_sentry_mode(new_value)
            self.worker.set_sentry_mode(new_value)
        if not old_value == new_value:
            self.sentry_mode = new_value
            self.update_image_bundle()
            if new_value == True:
                self.remove_from_turn_queue()
                if status.displayed_mob == self:
                    actor_utility.calibrate_actor_info_display(
                        status.mob_info_display, self
                    )  # updates actor info display with sentry icon
            else:
                if (
                    self.movement_points > 0
                    and not (
                        self.get_permission(constants.VEHICLE_PERMISSION)
                        and self.crew == "none"
                    )
                    and not (
                        self.get_permission(constants.VEHICLE_PERMISSION)
                        or self.in_group
                        or self.in_building
                    )
                ):
                    self.add_to_turn_queue()
            if self == status.displayed_mob:
                actor_utility.calibrate_actor_info_display(
                    status.mob_info_display, self
                )

    def add_to_turn_queue(self):
        """
        Description:
            At the start of the turn or once removed from another actor/building, attempts to add this unit to the list of units to cycle through with tab. Units in sentry mode or without movement are not added
        Input:
            None
        Output:
            None
        """
        if (
            (not self.sentry_mode)
            and self.movement_points > 0
            and self.end_turn_destination == "none"
            and not self in status.player_turn_queue
        ):
            if not self in status.player_turn_queue:
                status.player_turn_queue.append(self)

    def remove_from_turn_queue(self):
        """
        Description:
            Removes this unit from the list of units to cycle through with tab
        Input:
            None
        Output:
            None
        """
        status.player_turn_queue = utility.remove_from_list(
            status.player_turn_queue, self
        )

    def replace(self):
        """
        Description:
            Replaces this unit for a new version of itself when it dies from attrition, removing all experience and name modifications
        Input:
            None
        Output:
            None
        """
        self.set_name(self.default_name)
        if self.get_permission(constants.VETERAN_PERMISSION):
            self.set_permission(constants.VETERAN_PERMISSION, False)
            for current_image in self.images:
                current_image.image.remove_member("veteran_icon")

    def manage_health_attrition(
        self, current_cell="default"
    ):  # other versions of manage_health_attrition in group, vehicle, and resource_building
        """
        Description:
            Checks this mob for health attrition each turn
        Input:
            string/cell current_cell = 'default': Records which cell the attrition is taking place in, used when a unit is in a building or another mob and does not technically exist in any cell
        Output:
            None
        """
        if current_cell == "default":
            current_cell = self.get_cell()
        if current_cell == "none":
            return ()
        if current_cell.local_attrition():
            transportation_minister = status.current_ministers[
                constants.type_minister_dict["transportation"]
            ]
            if transportation_minister.no_corruption_roll(
                6, "health_attrition"
            ) == 1 or constants.effect_manager.effect_active("boost_attrition"):
                if random.randrange(1, 7) <= 2:
                    self.attrition_death()

    def attrition_death(self, show_notification=True):
        """
        Description:
            Kills this unit, takes away its next turn, and automatically buys a replacement when it fails its rolls for health attrition. If an officer dies, the replacement costs the officer's usual recruitment cost and does not have
                the previous officer's experience. If a worker dies, the replacement is found and recruited from somewhere else on the map, increasing worker upkeep colony-wide as usual
        Input:
            boolean show_notification: Whether a notification should be shown for this death - depending on where this was called, a notification may have already been shown
        Output:
            None
        """
        constants.evil_tracker.change(1)
        if (
            self.any_permissions(
                constants.OFFICER_PERMISSION, constants.WORKER_PERMISSION
            )
            and self.automatically_replace
        ):
            if show_notification:
                constants.notification_manager.display_notification(
                    {
                        "message": f"{utility.capitalize(self.name)} has died from attrition at ({self.x}, {self.y}) /n /n{self.generate_attrition_replacement_text()}",
                        "zoom_destination": self,
                    }
                )

            self.temp_disable_movement()
            self.replace()
            self.death_sound("violent")
        else:
            if show_notification:
                constants.notification_manager.display_notification(
                    {
                        "message": f"{utility.capitalize(self.name)} has died from attrition at ({self.x}, {self.y})",
                        "zoom_destination": self.get_cell().tile,
                    }
                )

            self.die()

    def generate_attrition_replacement_text(self):
        """
        Description:
            Generates text to use in attrition replacement notifications when this unit suffers health attrition
        Input:
            None
        Output:
            Returns text to use in attrition replacement notifications
        """
        text = "The unit will remain inactive for the next turn as replacements are found. /n /n"
        if self.get_permission(constants.OFFICER_PERMISSION):
            text += (
                str(constants.recruitment_costs["officer"])
                + " money has automatically been spent to recruit a replacement. /n /n"
            )
        return text

    def remove(self):
        """
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. Also deselects this mob and drops any commodities it is carrying
        Input:
            None
        Output:
            None
        """
        if (not self.get_cell() == "none") and (
            not self.get_cell().tile == "none"
        ):  # drop inventory on death
            current_tile = self.get_cell().tile
            for current_commodity in constants.commodity_types:
                current_tile.change_inventory(
                    current_commodity, self.get_inventory(current_commodity)
                )
        self.remove_from_turn_queue()
        super().remove()
        status.pmob_list = utility.remove_from_list(status.pmob_list, self)

    def draw_outline(self):
        """
        Description:
            Draws a flashing outline around this mob if it is selected, also shows its end turn destination, if any
        Input:
            None
        Output:
            None
        """
        if flags.show_selection_outlines:
            for current_image in self.images:
                if (
                    current_image.current_cell != "none"
                    and self == current_image.current_cell.contained_mobs[0]
                    and current_image.current_cell.grid.showing
                ):  # only draw outline if on top of stack
                    pygame.draw.rect(
                        constants.game_display,
                        constants.color_dict[self.selection_outline_color],
                        (current_image.outline),
                        current_image.outline_width,
                    )

                    if len(self.base_automatic_route) > 0:
                        start_coordinates = self.base_automatic_route[0]
                        end_coordinates = self.base_automatic_route[-1]
                        for current_coordinates in self.base_automatic_route:
                            current_tile = (
                                self.grids[0]
                                .find_cell(
                                    current_coordinates[0], current_coordinates[1]
                                )
                                .tile
                            )
                            if current_coordinates == start_coordinates:
                                color = "purple"
                            elif current_coordinates == end_coordinates:
                                color = "yellow"
                            else:
                                color = "bright blue"
                            current_tile.draw_destination_outline(color)
                            for equivalent_tile in current_tile.get_equivalent_tiles():
                                equivalent_tile.draw_destination_outline(color)
            if self.end_turn_destination != "none":
                self.end_turn_destination.draw_destination_outline()
                for equivalent_tile in self.end_turn_destination.get_equivalent_tiles():
                    equivalent_tile.draw_destination_outline()

    def set_controlling_minister_type(self, new_type):
        """
        Description:
            Sets the type of minister that controls this unit, like 'Minister of Trade'
        Input:
            string new_type: Type of minister to control this unit, like 'Minister of Trade'
        Output:
            None
        """
        self.controlling_minister_type = new_type
        self.update_controlling_minister()

    def update_controlling_minister(self):
        """
        Description:
            Sets the minister that controls this unit to the one occupying the office that has authority over this unit
        Input:
            None
        Output:
            None
        """
        if self.controlling_minister_type == "none":
            self.controlling_minister = "none"
        else:
            self.controlling_minister = status.current_ministers[
                self.controlling_minister_type
            ]
            if self.controlling_minister == None:
                self.controlling_minister = "none"
            for current_minister_type_image in status.minister_image_list:
                if (
                    current_minister_type_image.minister_type
                    == self.controlling_minister_type
                ):
                    current_minister_type_image.calibrate(self.controlling_minister)

    def end_turn_move(self):
        """
        Description:
            If this mob has any pending movement orders at the end of the turn, this executes the movement. Currently used to move ships between Earth and the world at the end of the turn
        Input:
            None
        Output:
            None
        """
        if self.end_turn_destination != "none" and self.can_travel():
            self.go_to_grid(
                self.end_turn_destination.grids[0],
                (self.end_turn_destination.x, self.end_turn_destination.y),
            )
            self.get_cell().tile.select(music_override=True)
            self.manage_inventory_attrition()  # do an inventory check when crossing ocean, using the destination's terrain
            self.end_turn_destination = "none"

    def can_travel(self):  # if can move between Earth, the planet, etc.
        """
        Description:
            Returns whether this mob can cross the ocean, like going between Earth and the planet. By default, mobs cannot cross the ocean, but subclasses like ship are able to return True
        Input:
            None
        Output:
            boolean: Returns True if this mob can cross the ocean, otherwise returns False
        """
        return False  # different for subclasses

    def set_inventory(self, commodity, new_value):
        """
        Description:
            Sets the number of commodities of a certain type held by this mob. Also ensures that the mob info display is updated correctly
        Input:
            string commodity: Type of commodity to set the inventory of
            int new_value: Amount of commodities of the inputted type to set inventory to
        Output:
            None
        """
        super().set_inventory(commodity, new_value)
        if status.displayed_mob == self:
            actor_utility.calibrate_actor_info_display(status.mob_info_display, self)

    def fire(self):
        """
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. Has different effects from die in certain subclasses
        Input:
            None
        Output:
            None
        """
        self.die("fired")

    def can_move(self, x_change, y_change, can_print=True):
        """
        Description:
            Returns whether this mob can move to the tile x_change to the right of it and y_change above it. Movement can be prevented by not being able to move on water/land, the edge of the map, limited movement points, etc.
        Input:
            int x_change: How many cells would be moved to the right in the hypothetical movement
            int y_change: How many cells would be moved upward in the hypothetical movement
            boolean can_print = True: Whether to print messages to explain why a unit can't move in a certain direction
        Output:
            boolean: Returns True if this mob can move to the proposed destination, otherwise returns False
        """
        return super().can_move(x_change, y_change, can_print=can_print)

    def can_show_tooltip(self):
        """
        Description:
            Returns whether this mob's tooltip can be shown. Along with the superclass' requirements, mob tooltips cannot be shown when attached to another actor, such as when working in a building
        Input:
            None
        Output:
            None
        """
        if self.in_vehicle or self.in_group or self.in_building:
            return False
        else:
            return super().can_show_tooltip()

    def embark_vehicle(self, vehicle, focus=True):
        """
        Description:
            Hides this mob and embarks it on the inputted vehicle as a passenger. Any commodities held by this mob are put on the vehicle if there is cargo space, or dropped in its tile if there is no cargo space
        Input:
            vehicle vehicle: vehicle that this mob becomes a passenger of
            boolean focus = False: Whether this action is being "focused on" by the player or done automatically
        Output:
            None
        """
        self.in_vehicle = True
        self.vehicle = vehicle
        for current_commodity in self.get_held_commodities():  # gives inventory to ship
            num_held = self.get_inventory(current_commodity)
            for current_commodity_unit in range(num_held):
                if vehicle.get_inventory_remaining() > 0:
                    vehicle.change_inventory(current_commodity, 1)
                else:
                    self.get_cell().tile.change_inventory(current_commodity, 1)
            self.inventory = {}
        self.hide_images()
        self.remove_from_turn_queue()
        vehicle.contained_mobs.append(self)
        vehicle.hide_images()
        vehicle.show_images()  # moves vehicle images to front
        if (
            focus and not flags.loading_save
        ):  # don't select vehicle if loading in at start of game
            actor_utility.calibrate_actor_info_display(
                status.mob_info_display, None, override_exempt=True
            )
            vehicle.select()
        if not flags.loading_save:
            self.movement_sound()
        self.clear_automatic_route()

    def disembark_vehicle(self, vehicle, focus=True):
        """
        Description:
            Shows this mob and disembarks it from the inputted vehicle after being a passenger
        Input:
            vehicle vehicle: vehicle that this mob disembarks from
            boolean focus = False: Whether this action is being "focused on" by the player or done automatically
        Output:
            None
        """
        vehicle.contained_mobs = utility.remove_from_list(vehicle.contained_mobs, self)
        self.vehicle = "none"
        self.in_vehicle = False
        self.x = vehicle.x
        self.y = vehicle.y
        for current_image in self.images:
            current_image.add_to_cell()
        if (
            vehicle.vehicle_type == "ship"
            and self.get_cell().grid == status.strategic_map_grid
            and self.get_cell().get_intact_building("port") == "none"
        ):
            self.set_permission(constants.DISORGANIZED_PERMISSION, True)
        if (
            self.get_permission(constants.CARAVAN_PERMISSION)
            and self.inventory_capacity > 0
        ):
            consumer_goods_present = vehicle.get_inventory("consumer goods")
            if consumer_goods_present > 0:
                consumer_goods_transferred = consumer_goods_present
                if consumer_goods_transferred > self.inventory_capacity:
                    consumer_goods_transferred = self.inventory_capacity
                vehicle.change_inventory(
                    "consumer goods", -1 * consumer_goods_transferred
                )
                self.change_inventory("consumer goods", consumer_goods_transferred)
                text_utility.print_to_screen(
                    f"{utility.capitalize(self.name)} automatically took {consumer_goods_transferred} consumer goods from {vehicle.name}'s cargo."
                )

        self.add_to_turn_queue()
        if focus:
            actor_utility.calibrate_actor_info_display(
                status.mob_info_display, None, override_exempt=True
            )
            self.select()
            self.movement_sound()
        self.on_move()

    def get_worker(self) -> "pmob":
        """
        Description:
            Returns the worker associated with this unit, if any (self if worker, crew if vehicle, worker component if group)
        Input:
            None
        Output:
            worker: Returns the worker associated with this unit, if any
        """
        return None
