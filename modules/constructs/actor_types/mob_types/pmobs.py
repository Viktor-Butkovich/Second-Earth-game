# Contains functionality for player-controlled mobs

from __future__ import annotations
import random
from typing import Dict, List
from modules.constructs.actor_types.mobs import mob
from modules.util import text_utility, utility, actor_utility, minister_utility
from modules.constructs import item_types
from modules.constants import constants, status, flags


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
                'end_turn_destination_coordinates': int tuple value - None if no saved destination, destination coordinates if saved destination
                'end_turn_destination_world_index': int value - Index of the world of the end turn destination, if any
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
        super().__init__(from_save, input_dict, original_constructor=False)
        status.pmob_list.append(self)
        self.equipment = {}
        self.upkeep_missing_penalty: str = None
        self.upkeep_missing_item_key: str = None
        self.item_upkeep_present: Dict[str, bool] = {}
        for current_equipment in input_dict.get("equipment", {}):
            if input_dict.get("equipment", {}).get(current_equipment, False):
                status.equipment_types[current_equipment].equip(self)
        if from_save:
            self.default_name = input_dict["default_name"]
            self.set_name(self.default_name)
            self.set_automatically_replace(input_dict["automatically_replace"])
            if input_dict["in_turn_queue"] and not self.end_turn_destination:
                self.add_to_turn_queue()
            else:
                self.remove_from_turn_queue()
            self.base_automatic_route = input_dict["base_automatic_route"]
            self.in_progress_automatic_route = input_dict["in_progress_automatic_route"]
            self.wait_until_full = input_dict["wait_until_full"]
        else:
            self.default_name = self.name
            self.set_max_movement_points(self.unit_type.movement_points)
            self.set_automatically_replace(True)
            self.add_to_turn_queue()
            self.base_automatic_route = (
                []
            )  # first item is start of route/pickup, last item is end of route/dropoff
            self.in_progress_automatic_route = (
                []
            )  # first item is next step, last item is current location
            self.wait_until_full = False
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
            self.select()

    def permissions_setup(self) -> None:
        """
        Sets up this mob's permissions
        """
        super().permissions_setup()
        self.set_permission(constants.PMOB_PERMISSION, True)

    def crew_vehicle(self, vehicle):
        """
        Description:
            Orders this worker to crew the inputted vehicle, attaching this worker to the vehicle and allowing the vehicle to function
        Input:
            vehicle vehicle: vehicle to which this worker is attached
        Output:
            None
        """
        self.vehicle = vehicle
        self.location.unsubscribe_mob(self)
        self.set_permission(constants.IN_VEHICLE_PERMISSION, True)
        vehicle.set_crew(self)
        vehicle.move_to_front()
        self.remove_from_turn_queue()
        vehicle.add_to_turn_queue()
        if (
            not flags.loading_save
        ):  # Don't select vehicle if loading in at start of game
            actor_utility.calibrate_actor_info_display(
                status.mob_info_display, None, override_exempt=True
            )
            vehicle.select()
            constants.SoundManager.play_sound("effects/metal_footsteps", volume=1.0)
            constants.SoundManager.play_sound(
                "effects/spaceship_activation", volume=0.6
            )

    def uncrew_vehicle(self, vehicle, focus: bool = True):
        """
        Description:
            Orders this worker to stop crewing the inputted vehicle, making this worker independent from the vehicle and preventing the vehicle from functioning
        Input:
            vehicle vehicle: vehicle to which this worker is no longer attached
        Output:
            None
        """
        self.location.subscribe_mob(self)
        self.vehicle = None
        self.set_permission(constants.IN_VEHICLE_PERMISSION, False)
        if not self.location.get_intact_building(constants.SPACEPORT):
            if constants.ALLOW_DISORGANIZED:
                self.set_permission(constants.DISORGANIZED_PERMISSION, True)
        vehicle.set_crew(None)
        vehicle.end_turn_destination = None
        vehicle.set_permission(
            constants.TRAVELING_PERMISSION, False, update_image=False
        )
        vehicle.remove_from_turn_queue()
        if focus:
            self.select()
            constants.SoundManager.play_sound("effects/metal_footsteps", volume=1.0)
        self.add_to_turn_queue()

    def get_item_upkeep(
        self, recurse: bool = False, earth_exemption: bool = True
    ) -> Dict[str, float]:
        """
        Description:
            Returns the item upkeep requirements for this unit type
        Input:
            None
        Output:
            dictionary: Returns the item upkeep requirements for this unit type
        """
        if earth_exemption and self.location.is_earth_location:
            return {}
        elif (
            earth_exemption
            and self.location.get_unit_habitability() > constants.HABITABILITY_DEADLY
        ):
            item_upkeep = self.unit_type.item_upkeep.copy()
            item_upkeep.pop(
                constants.AIR_ITEM, None
            )  # Return a version without air requirements
            return item_upkeep
        else:
            return self.unit_type.item_upkeep

    def in_deadly_environment(self) -> bool:
        """
        Description:
            Returns whether this unit is imminently going to die to deadly environmental conditions
        Input:
            None
        Output:
            bool: Returns whether this unit is imminently going to die to deadly environmental conditions
        """
        if not self.get_permission(constants.SURVIVABLE_PERMISSION):
            if not (
                self.any_permissions(
                    constants.WORKER_PERMISSION, constants.OFFICER_PERMISSION
                )
                and self.get_permission(constants.IN_GROUP_PERMISSION)
            ):
                return True
        return False

    def consume_item_upkeep(self) -> None:
        """
        Consumes all available items required for this unit's item upkeep, logging an upkeep missing penalty for the most important missing item type
        """
        if self.in_deadly_environment():
            return  # Don't consume upkeep when in instant death conditions

        missing_upkeep = self.location.consume_items(
            self.get_item_upkeep(recurse=False), consuming_actor=self
        )
        for (
            item_key,
            item_present,
        ) in (
            self.item_upkeep_present.items()
        ):  # Register missing upkeep of 0 if none was present - allows officer attrition if no items present
            if not item_present:
                missing_upkeep[item_key] = missing_upkeep.get(item_key, 0)

        possible_penalties = [constants.UPKEEP_MISSING_PENALTY_NONE] + [
            self.unit_type.missing_upkeep_penalties[item_key]
            for item_key in missing_upkeep
        ]
        self.upkeep_missing_penalty, self.upkeep_missing_item_key = max(
            [(constants.UPKEEP_MISSING_PENALTY_NONE, None)]
            + [
                (self.unit_type.missing_upkeep_penalties[item_key], item_key)
                for item_key in missing_upkeep
            ],
            key=lambda x: x[0],
        )

        if constants.UPKEEP_MISSING_PENALTY_DEHYDRATION in possible_penalties:
            if self.get_permission(constants.DEHYDRATION_PERMISSION):
                # If would dehydrate again, die instead
                self.upkeep_missing_penalty = constants.UPKEEP_MISSING_PENALTY_DEATH
        else:
            # If received sufficient water, recover from any existing starvation
            self.set_permission(constants.DEHYDRATION_PERMISSION, False)

        if constants.UPKEEP_MISSING_PENALTY_STARVATION in possible_penalties:
            if self.get_permission(constants.STARVATION_PERMISSION):
                # If would starve again, die instead
                self.upkeep_missing_penalty = constants.UPKEEP_MISSING_PENALTY_DEATH
            elif (
                self.upkeep_missing_penalty
                == constants.UPKEEP_MISSING_PENALTY_DEHYDRATION
            ):  # Become starving even if dehydrating (doesn't make sense to only use most severe penalty in this context)
                self.set_permission(constants.STARVATION_PERMISSION, True)
                self.record_logistics_incident(
                    incident_type=constants.UPKEEP_MISSING_PENALTY_STARVATION,
                    cause=constants.FOOD_ITEM,
                )
        else:
            # If received sufficient food, recover from any existing starvation
            self.set_permission(constants.STARVATION_PERMISSION, False)

        self.record_upkeep_missing_penalty()

        # Get the most severe penalty of the resource types with any missed upkeep

        if constants.EffectManager.effect_active("debug_item_requests"):
            if missing_upkeep:
                print(
                    f"{self.name} attempted to consume {self.get_item_upkeep(recurse=False)}"
                )
                print(
                    f"{self.name} missing {missing_upkeep}, invoking upkeep penalty {constants.UPKEEP_MISSING_PENALTY_CODES[self.upkeep_missing_penalty]}"
                )
            else:
                print(
                    f"{self.name} successfully consumed {self.get_item_upkeep(recurse=False)}"
                )

    def check_item_availability(self) -> None:
        """
        Checks whether any of the items required for this unit's item upkeep are present (regardless of amount)
        """
        self.item_upkeep_present = {}
        for item_key in self.get_item_upkeep():
            self.item_upkeep_present[item_key] = self.item_present(
                status.item_types[item_key]
            )
            # Note whether any of the item type was present - officers require the presence of items, but don't consume them
            # In the future, check if any of the item type is present in the local supply network
        for current_sub_mob in self.get_sub_mobs():
            current_sub_mob.check_item_availability()

    def record_upkeep_missing_penalty(self) -> None:
        """
        Records this unit's most severe upkeep missing penalty as a message to display at the start of the turn
        """
        if self.upkeep_missing_penalty != constants.UPKEEP_MISSING_PENALTY_NONE:
            self.record_logistics_incident(
                incident_type=self.upkeep_missing_penalty,
                cause=self.upkeep_missing_item_key,
            )

    def resolve_upkeep_missing_penalty(self) -> None:
        """
        Apply an effect based on the most severe upkeep missing penalty type due to missing item upkeep from earlier in the turn (if any)
        """
        if self.upkeep_missing_penalty == constants.UPKEEP_MISSING_PENALTY_DEATH:
            self.die()
        elif (
            self.upkeep_missing_penalty == constants.UPKEEP_MISSING_PENALTY_DEHYDRATION
        ):
            self.set_permission(constants.DEHYDRATION_PERMISSION, True)
        elif self.upkeep_missing_penalty == constants.UPKEEP_MISSING_PENALTY_STARVATION:
            self.set_permission(constants.STARVATION_PERMISSION, True)
        elif self.upkeep_missing_penalty == constants.UPKEEP_MISSING_PENALTY_MORALE:
            constants.PublicOpinionTracker.change(-2)
        else:
            pass

    def get_sub_mobs(self) -> List["pmob"]:
        """
        Description:
            Returns a list of units managed by this unit
        Input:
            None
        Output:
            list: Returns a list of units managed by this unit
        """
        return []

    def die(self, death_type="violent"):
        """
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. Used instead of remove to improve consistency with groups/vehicles, whose die and remove have different
                functionalities
        Input:
            string death_type == 'violent': Type of death for this unit, determining the type of sound played
        Output:
            None
        """
        reembarked_units = None
        if self.get_permission(constants.IN_GROUP_PERMISSION):
            moved_unit = self.group
        else:
            moved_unit = self
        if moved_unit.get_permission(constants.IN_VEHICLE_PERMISSION):
            if moved_unit.vehicle.crew == moved_unit:
                moved_unit.vehicle.eject_passengers(focus=False)
                moved_unit.vehicle.drop_inventory()
                moved_unit.uncrew_vehicle(moved_unit.vehicle, focus=False)
            else:
                if self.get_permission(constants.IN_GROUP_PERMISSION):
                    if self.get_permission(constants.OFFICER_PERMISSION):
                        reembarked_units = (self.group.worker, self.group.vehicle)
                    else:
                        reembarked_units = (self.group.officer, self.group.vehicle)
                moved_unit.disembark_vehicle(moved_unit.vehicle, focus=False)
        if self.get_permission(constants.IN_GROUP_PERMISSION):
            self.group.disband(focus=False)
        super().die(death_type=death_type)
        if (
            reembarked_units
        ):  # If group member passenger dies, reembark other group member
            reembarked_units[0].embark_vehicle(reembarked_units[1], focus=False)

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
                'end_turn_destination_coordinates': int tuple value - None if no saved destination, destination coordinates if saved destination
                'end_turn_destination_world_index': int value - Index of the world of the end turn destination, if any
                'sentry_mode': boolean value - Whether this unit is in sentry mode, preventing it from being in the turn order
                'in_turn_queue': boolean value - Whether this unit is in the turn order, allowing end unit turn commands, etc. to persist after saving/loading
                'base_automatic_route': int tuple list value - List of the coordinates in this unit's automatic movement route, with the first coordinates being the start and the last being the end. List empty if
                    no automatic movement route has been designated
                'in_progress_automatic_route': string/int tuple list value - List of the coordinates and string commands this unit will execute, changes as the route is executed
                'automatically_replace': boolean value  Whether this unit or any of its components should be replaced automatically in the event of attrition
                'equipment': dictionary value - This actor's items equipped, with a boolean value corresponding to whether each type of equipment is equipped
        """
        save_dict = super().to_save_dict()
        if not self.end_turn_destination:
            save_dict["end_turn_destination_coordinates"] = None
        else:
            save_dict["end_turn_destination_coordinates"] = (
                self.end_turn_destination.x,
                self.end_turn_destination.y,
            )
            save_dict["end_turn_destination_world_index"] = status.world_list.index(
                self.end_turn_destination.world_handler
            )
        save_dict["default_name"] = self.default_name
        save_dict["in_turn_queue"] = self in status.player_turn_queue
        save_dict["base_automatic_route"] = self.base_automatic_route
        save_dict["in_progress_automatic_route"] = self.in_progress_automatic_route
        save_dict["wait_until_full"] = self.wait_until_full
        save_dict["automatically_replace"] = self.automatically_replace
        save_dict["equipment"] = self.equipment
        return save_dict

    def add_to_automatic_route(self, new_location):
        """
        Description:
            Adds the inputted coordinates to this unit's automated movement route, changing the in-progress route as needed
        Input:
            location tuple new_coordinates: New x and y coordinates to add to the route
        Output:
            None
        """
        self.base_automatic_route.append(new_location)
        self.calculate_automatic_route()
        if self == status.displayed_mob:
            actor_utility.calibrate_actor_info_display(status.mob_info_display, self)

    def calculate_automatic_route(self):
        """
        Creates an in-progress movement route based on the base movement route when the base movement route changes
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
        current_location = self.location
        next_step = self.in_progress_automatic_route[0]
        if next_step == "end":  # can drop off freely unless train without train station
            if not (
                self.all_permissions(
                    constants.VEHICLE_PERMISSION, constants.TRAIN_PERMISSION
                )
                and not current_location.has_intact_building(constants.TRAIN_STATION)
            ):
                return True
            else:
                return False
        elif next_step == "start":
            # ignores consumer goods
            if (
                self.wait_until_full
                and (
                    current_location.get_inventory_used() >= self.inventory_capacity
                    or current_location.insufficient_inventory_capacity
                )
            ) or (
                (not self.wait_until_full)
                and (
                    len(current_location.get_held_items(ignore_consumer_goods=True)) > 0
                    or self.get_inventory_used() > 0
                )
            ):  # Only start round trip if there is something to deliver, either from location or if already in inventory
                # If wait until full, instead wait until full load to transport or no warehouse space left
                if not (
                    self.all_permissions(
                        constants.VEHICLE_PERMISSION, constants.TRAIN_PERMISSION
                    )
                    and not current_location.has_intact_building(
                        constants.TRAIN_STATION
                    )
                ):  # Pick up freely unless train without train station
                    return True
                else:
                    return False
            else:
                return False
        else:  # Must have enough movement points, not blocked
            x_change = next_step.x - current_location.x
            y_change = next_step.y - current_location.y
            return self.can_move(x_change, y_change, False)

    def follow_automatic_route(self):
        """
        Moves along this unit's in-progress movement route until it cannot complete the next step. A unit will wait for items to transport from the start, then pick them up and move along the path, picking up others along
            the way. At the end of the path, it drops all items and moves back towards the start
        """
        progressed = False
        if len(self.in_progress_automatic_route) > 0:
            while self.can_follow_automatic_route():
                next_step = self.in_progress_automatic_route[0]
                if next_step == "start":
                    self.pick_up_all_items(True)
                elif next_step == "end":
                    self.drop_inventory()
                else:
                    if not (
                        self.all_permissions(
                            constants.VEHICLE_PERMISSION, constants.TRAIN_PERMISSION
                        )
                        and not self.location.has_intact_building(
                            constants.TRAIN_STATION
                        )
                    ):
                        if (
                            self.get_next_automatic_stop() == "end"
                        ):  # Only pick up items on way to end
                            self.pick_up_all_items(
                                True
                            )  # Attempt to pick up items both before and after moving
                    initial_location = self.location
                    x_change = next_step.x - initial_location.x
                    y_change = next_step.y - initial_location.y
                    self.move(x_change, y_change)
                    if not (
                        self.all_permissions(
                            constants.VEHICLE_PERMISSION, constants.TRAIN_PERMISSION
                        )
                        and not self.location.has_intact_building(
                            constants.TRAIN_STATION
                        )
                    ):
                        if (
                            self.get_next_automatic_stop() == "end"
                        ):  # only pick up items on way to end
                            self.pick_up_all_items(True)
                progressed = True
                self.in_progress_automatic_route.append(
                    self.in_progress_automatic_route.pop(0)
                )  # move first item to end

        return progressed  # returns whether unit did anything to show unit in movement routes report

    def get_next_automatic_stop(self):
        """
        Description:
            Returns the next stop for this unit's in-progress automatic route, or None if there are stops
        Input:
            None
        Output:
            string: Returns the next stop for this unit's in-progress automatic route, or None if there are stops
        """
        for current_stop in self.in_progress_automatic_route:
            if current_stop in ["start", "end"]:
                return current_stop
        return None

    def pick_up_all_items(self, ignore_consumer_goods=False):
        """
        Description:
            Adds as many local items to this unit's inventory as possible, possibly choosing not to pick up consumer goods based on the inputted boolean
        Input:
            boolean ignore_consumer_goods = False: Whether to not pick up consumer goods from this unit's location
        Output:
            None
        """
        while (
            self.get_inventory_remaining() > 0
            and len(
                self.location.get_held_items(
                    ignore_consumer_goods=ignore_consumer_goods
                )
            )
            > 0
        ):
            items_present = self.location.get_held_items(
                ignore_consumer_goods=ignore_consumer_goods
            )
            amount_transferred = min(
                self.get_inventory_remaining(),
                self.location.get_inventory(items_present[0]),
            )
            self.change_inventory(items_present[0], amount_transferred)
            self.location.change_inventory(items_present[0], -amount_transferred)

    def clear_automatic_route(self):
        """
        Removes this unit's saved automatic movement route
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

    def add_to_turn_queue(self):
        """
        At the start of the turn or once removed from another actor/building, attempts to add this unit to the list of units to cycle through with tab. Units in sentry mode or without movement are not added
        """
        if (
            (not self.get_permission(constants.SENTRY_MODE_PERMISSION))
            and self.movement_points > 0
            and self.end_turn_destination == None
            and not self in status.player_turn_queue
        ):
            if not self in status.player_turn_queue:
                status.player_turn_queue.append(self)

    def remove_from_turn_queue(self):
        """
        Removes this unit from the list of units to cycle through with tab
        """
        status.player_turn_queue = utility.remove_from_list(
            status.player_turn_queue, self
        )

    def replace(self):
        """
        Replaces this unit for a new version of itself when it dies from attrition, removing all experience and name modifications
        """
        self.set_name(self.default_name)
        if self.get_permission(constants.VETERAN_PERMISSION):
            self.set_permission(constants.VETERAN_PERMISSION, False)

    def manage_health_attrition(self) -> None:
        """
        Checks this mob for health attrition each turn
        """
        if self.any_permissions(
            constants.VEHICLE_PERMISSION, constants.GROUP_PERMISSION
        ):  # Groups and vehicles don't receive attrition - only their components
            return

        if (
            constants.EffectManager.effect_active("boost_attrition")
            and random.randrange(1, 7) >= 4
        ):  # Cause very frequent attrition if boost attrition active
            self.record_logistics_incident(
                incident_type=constants.UPKEEP_MISSING_PENALTY_DEATH,
                cause="health attrition",
            )
            self.die()
            return

        if (
            self.location.local_attrition() and random.randrange(1, 7) <= 2
        ):  # If local conditions may cause attrition, 1/3 chance of attrition check
            if (
                minister_utility.get_minister(
                    constants.TRANSPORTATION_MINISTER
                ).no_corruption_roll(6, "health_attrition")
                == 1
            ):  # For attrition check, see if minister fails
                self.record_logistics_incident(
                    incident_type=constants.UPKEEP_MISSING_PENALTY_DEATH,
                    cause="health attrition",
                )
                self.die()  # If minister fails attrition check, unit dies

    def record_logistics_incident(self, incident_type: int, cause: str):
        """
        Description:
            Explains the death of this unit to attrition, logging the explanation in a list of all attrition deaths this turn
        Input:
            int incident_type: Incident type code, such as constants.UPKEEP_MISSING_PENALTY_DEATH
            string cause: Cause explaining the incident, such as "health attrition" or constants.WATER_ITEM
        Output:
            None
        """
        constants.EvilTracker.change(1)
        insertion = ""
        if self.get_permission(constants.OFFICER_PERMISSION):
            name = f"{self.character_info['name']}"
            insertion = f" {utility.generate_article(self.name)} {self.name}"
        else:
            name = self.name.capitalize()

        if self.get_permission(constants.IN_GROUP_PERMISSION):
            if (
                self.group.get_permission(constants.IN_VEHICLE_PERMISSION)
                and self.group.vehicle.crew == self.group
            ):
                name += f",{insertion} within {self.group.name} crewing {self.group.vehicle.name},"
            elif self.group.get_permission(constants.IN_VEHICLE_PERMISSION):
                name += f",{insertion} within {self.group.name} aboard {self.group.vehicle.name},"
            else:
                name += f",{insertion} within {self.group.name},"
        elif self.get_permission(constants.IN_VEHICLE_PERMISSION):
            name += f",{insertion} aboard {self.vehicle.name},"
        elif insertion:
            name += f",{insertion},"

        explanation = None
        if incident_type == constants.UPKEEP_MISSING_PENALTY_DEHYDRATION:
            explanation = f"entered dehydration due to insufficient {status.item_types[cause].name}."
        elif incident_type == constants.UPKEEP_MISSING_PENALTY_STARVATION:
            explanation = f"entered starvation due to insufficient {status.item_types[cause].name}."
        elif incident_type == constants.UPKEEP_MISSING_PENALTY_DEATH:
            if cause in status.item_types.keys():
                explanation = f"died to insufficient {status.item_types[cause].name}."
            elif cause == "environmental conditions":
                explanation = f"died to deadly environmental conditions."
            elif cause == "health attrition":
                explanation = f"died to health attrition."
        elif incident_type == constants.UPKEEP_MISSING_PENALTY_MORALE:
            explanation = (
                f"lost morale due to insufficient {status.item_types[cause].name}."
            )
        if not explanation:
            raise ValueError(f"Invalid incident type {incident_type}")

        actor_utility.add_logistics_incident_to_report(self, f"{name} {explanation}")

    def remove(self):
        """
        Removes this object from relevant lists and prevents it from further appearing in or affecting the program. Also deselects this mob and drops any items it is carrying
        """
        for current_item_type in self.get_held_items():
            self.location.change_inventory(
                current_item_type, self.get_inventory(current_item_type)
            )
        self.remove_from_turn_queue()
        super().remove()
        status.pmob_list = utility.remove_from_list(status.pmob_list, self)

    def end_turn_move(self):
        """
        If this mob has any pending movement orders at the end of the turn, this executes the movement. Currently used to move ships between Earth and the planet at the end of the turn
        """
        if self.end_turn_destination and self.can_travel():
            self.end_turn_destination.subscribe_mob(self)
            self.on_move()
            self.manage_inventory_attrition()  # do an inventory check when crossing ocean, using the destination's terrain
            self.end_turn_destination = None
            self.set_permission(constants.TRAVELING_PERMISSION, False)
            self.movement_sound()

    def fire(self):
        """
        Removes this object from relevant lists and prevents it from further appearing in or affecting the program. Has different effects from die in certain subclasses
        """
        self.die("fired")

    def embark_vehicle(self, vehicle, focus=True):
        """
        Description:
            Hides this mob and embarks it on the inputted vehicle as a passenger. Any items held by this mob are put on the vehicle if there is cargo space, or dropped in its location if there is no cargo space
        Input:
            vehicle vehicle: vehicle that this mob becomes a passenger of
            boolean focus = False: Whether this action is being "focused on" by the player or done automatically
        Output:
            None
        """
        self.vehicle = vehicle
        for current_item in self.get_held_items():  # Give inventory to vehicle
            amount_held = self.get_inventory(current_item)

            amount_transferred = min(vehicle.get_inventory_remaining(), amount_held)
            vehicle.change_inventory(current_item, amount_transferred)

            amount_dropped = amount_held - amount_transferred
            self.location.change_inventory(current_item, amount_dropped)

        self.inventory = {}
        self.location.unsubscribe_mob(self)
        self.remove_from_turn_queue()
        vehicle.subscribed_passengers.append(self)
        constants.EventBus.publish(constants.VEHICLE_SUBMOB_ADDED_ROUTE)
        vehicle.move_to_front()
        self.set_permission(constants.IN_VEHICLE_PERMISSION, True)
        if (
            focus and not flags.loading_save
        ):  # don't select vehicle if loading in at start of game
            actor_utility.calibrate_actor_info_display(
                status.mob_info_display, None, override_exempt=True
            )
            vehicle.select()
            constants.SoundManager.play_sound("effects/metal_footsteps", volume=1.0)
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
        vehicle.subscribed_passengers = utility.remove_from_list(
            vehicle.subscribed_passengers, self
        )
        self.location.subscribe_mob(self)
        self.vehicle = None
        self.set_permission(constants.IN_VEHICLE_PERMISSION, False)
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
            self.select()
            constants.SoundManager.play_sound("effects/metal_footsteps", volume=1.0)

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

    def leave_group(self, group, focus=True):
        """
        Description:
            Reveals this unit when its group is disbanded, allowing it to be directly interacted with
        Input:
            group group: group from which this unit is leaving
        Output:
            None
        """
        self.location.subscribe_mob(self)
        self.group = None
        self.set_permission(constants.IN_GROUP_PERMISSION, False)
        if self.get_permission(constants.WORKER_PERMISSION):
            self.set_permission(
                constants.DISORGANIZED_PERMISSION,
                group.get_permission(constants.DISORGANIZED_PERMISSION),
            )
        if focus:
            self.select()
        if self.movement_points > 0:
            self.add_to_turn_queue()

    def join_group(self, group):
        """
        Description:
            Hides this officer when joining a group, preventing it from being directly interacted with until the group is disbanded
        Input:
            group group: Group this officer is joining
        Output:
            None
        """
        self.group = group
        self.set_permission(constants.IN_GROUP_PERMISSION, True)
        self.location.unsubscribe_mob(self)
        self.remove_from_turn_queue()
