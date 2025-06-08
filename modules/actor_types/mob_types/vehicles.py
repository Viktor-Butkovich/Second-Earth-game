# Contains functionality for vehicle units

import random
from typing import List, Dict
from modules.actor_types.mob_types.pmobs import pmob
from modules.util import text_utility, minister_utility, utility
from modules.constants import constants, status, flags


class vehicle(pmob):
    """
    pmob that requires an attached worker to function and can carry other mobs as passengers
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
                'image_dict': string/string dictionary value - dictionary of image type keys and file path values to the images used by this object in various situations, such as 'crewed': 'crewed_spaceship.png'
                'name': string value - Required if from save, this mob's name
                'modes': string list value - Game modes during which this mob's images can appear
                'end_turn_destination_coordinates': int tuple value - None if no saved destination, destination coordinates if saved destination
                'end_turn_destination_world_index': int value - Index of the world of the end turn destination, if any
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'max_movement_points': int value - Required if from save, maximum number of movement points this mob can have
                'crew': worker, string, or dictionary value - If no crew, equals None. Otherwise, if creating a new vehicle, equals a worker that serves as crew. If loading, equals a dictionary of the saved information necessary to
                    recreate the worker to serve as crew
                'passenger_dicts': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each of this vehicle's passengers
        Output:
            None
        """
        self.uncrewed_image_id: List[any] = input_dict["uncrewed_image_id"]
        self.moving_image_id: List[any] = input_dict["moving_image_id"]
        self.crew: pmob = None
        self.contained_mobs: List[pmob] = []
        self.ejected_crew = None
        self.ejected_passengers = []
        super().__init__(from_save, input_dict, original_constructor=False)
        if not from_save:
            self.set_crew(input_dict["crew"])
        else:  # Create crew and passengers through recruitment_manager and embark them
            if not input_dict["crew"]:
                self.set_crew(None)
            else:
                constants.actor_creation_manager.create(
                    True, {**input_dict["crew"], "location": input_dict["location"]}
                ).crew_vehicle(
                    self
                )  # creates worker and merges it as crew
            for current_passenger in input_dict["passenger_dicts"]:
                constants.actor_creation_manager.create(
                    True,
                    {
                        **current_passenger,
                        "location": input_dict["location"],
                    },
                ).embark_vehicle(
                    self
                )  # create passengers and merge as passengers
        if not self.get_permission(constants.ACTIVE_PERMISSION):
            self.remove_from_turn_queue()
        self.finish_init(original_constructor, from_save, input_dict)

    def get_item_upkeep(
        self, recurse: bool = False, earth_exemption: bool = True
    ) -> Dict[str, float]:
        """
        Description:
            Returns the item upkeep requirements for this unit type, optionally recursively adding the upkeep requirements of sub-mobs
        Input:
            None
        Output:
            dictionary: Returns the item upkeep requirements for this unit type
        """
        if recurse:
            return utility.add_dicts(
                super().get_item_upkeep(
                    recurse=recurse, earth_exemption=earth_exemption
                ),
                *[
                    current_sub_mob.get_item_upkeep(
                        recurse=recurse, earth_exemption=earth_exemption
                    )
                    for current_sub_mob in self.get_sub_mobs()
                ],
            )
        else:
            return super().get_item_upkeep(
                recurse=recurse, earth_exemption=earth_exemption
            )

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
        self.set_permission(constants.VEHICLE_PERMISSION, True)
        self.set_permission(constants.ACTIVE_PERMISSION, False)

    def set_crew(self, new_crew):
        """
        Description:
            Sets this vehicle's crew to the inputted workers
        Input:
            worker new_crew: New crew for this vehicle
        Output:
            None
        """
        self.crew = new_crew
        if new_crew:
            self.set_permission(
                constants.ACTIVE_PERMISSION, True, override=True, update_image=False
            )
            self.set_permission(
                constants.ACTIVE_VEHICLE_PERMISSION,
                True,
                override=True,
                update_image=False,
            )
            self.set_permission(
                constants.INACTIVE_VEHICLE_PERMISSION, False, override=True
            )
            self.set_inventory_capacity(self.unit_type.inventory_capacity)
        else:
            self.set_permission(
                constants.ACTIVE_PERMISSION, False, override=True, update_image=False
            )
            self.set_permission(
                constants.ACTIVE_VEHICLE_PERMISSION,
                None,
                override=True,
                update_image=False,
            )
            self.set_permission(
                constants.INACTIVE_VEHICLE_PERMISSION, True, override=True
            )
            self.set_inventory_capacity(0)

    def get_default_image_id_list(self, override_values={}):
        if not self.get_permission(
            constants.ACTIVE_PERMISSION,
            one_time_permissions=override_values.get("override_permissions", {}),
        ):
            return self.uncrewed_image_id
        elif self.get_permission(constants.TRAVELING_PERMISSION):
            return self.moving_image_id
        else:
            return super().get_default_image_id_list(override_values)

    def get_sub_mobs(self) -> List[pmob]:
        """
        Description:
            Returns a list of units managed by this unit
        Input:
            None
        Output:
            list: Returns a list of units managed by this unit
        """
        if self.crew:
            return [self.crew] + self.contained_mobs
        else:
            return self.contained_mobs

    def eject_crew(self, focus=True):
        """
        Description:
            Removes this vehicle's crew
        Input:
            None
        Output:
            None
        """
        if self.crew:
            self.ejected_crew = self.crew
            self.crew.uncrew_vehicle(self, focus=focus)

    def eject_passengers(self, focus=True):
        """
        Description:
            Removes this vehicle's passengers
        Input:
            None
        Output:
            None
        """
        while len(self.contained_mobs) > 0:
            current_mob = self.contained_mobs.pop(0)
            current_mob.disembark_vehicle(
                self, focus=focus and len(self.contained_mobs) == 1
            )  # Only focus on the last
            if (not flags.player_turn) or flags.enemy_combat_phase:
                self.ejected_passengers.append(current_mob)

    def reembark(self):
        """
        Description:
            After combat is finished, reembarks any surviving crew or passengers onto this vehicle, if possible
        Input:
            None
        Output:
            None
        """
        if self.ejected_crew:
            if self.ejected_crew in status.pmob_list:
                self.ejected_crew.crew_vehicle(self)
                for current_passenger in self.ejected_passengers:
                    if current_passenger in status.pmob_list:
                        current_passenger.embark_vehicle(self)
            self.ejected_crew = None
            self.ejected_passengers = []

    def die(self, death_type="violent"):
        """
        Description:
            Removes this object from relevant lists, prevents it from further appearing in or affecting the program, deselects it, and drops any items it is carrying. Also removes all of this vehicle's passengers
        Input:
            string death_type == 'violent': Type of death for this unit, determining the type of sound played
        Output:
            None
        """
        self.eject_passengers(focus=False)
        self.eject_crew(focus=False)
        super().die(death_type)

    def fire(self):
        """
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. Also fires this vehicle's crew and passengers
        Input:
            None
        Output:
            None
        """
        for current_sub_mob in self.get_sub_mobs():
            current_sub_mob.fire()
        self.contained_mobs = []
        self.set_crew(None)
        super().fire()

    def to_save_dict(self):
        """
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                Along with superclass outputs, also saves the following values:
                'image_dict': string value - dictionary of image type keys and file path values to the images used by this object in various situations, such as 'crewed': 'crewed_spaceship.png'
                'crew': string or dictionary value - If no crew, equals None. Otherwise, equals a dictionary of the saved information necessary to recreate the worker to serve as crew
                'passenger_dicts': dictionary list value - List of dictionaries of saved information necessary to recreate each of this vehicle's passengers
        """
        save_dict = super().to_save_dict()
        save_dict["uncrewed_image_id"] = self.uncrewed_image_id
        save_dict["moving_image_id"] = self.moving_image_id
        if self.crew:
            save_dict["crew"] = self.crew.to_save_dict()
        else:
            save_dict["crew"] = None

        save_dict["passenger_dicts"] = [
            current_mob.to_save_dict() for current_mob in self.contained_mobs
        ]
        # List of dictionaries for each passenger, on load a vehicle creates all of its passengers and embarks them
        return save_dict

    def can_move(self, x_change, y_change, can_print=True):
        """
        Description:
            Returns whether this mob can move to the location x_change to its and y_change upward. Movement can be prevented by not being able to move on water/land, the edge of the map, limited movement points, etc.
                Vehicles are not able to move without a crew
        Input:
            int x_change: How many cells would be moved to the right in the hypothetical movement
            int y_change: How many cells would be moved upward in the hypothetical movement
            boolean can_print = True: Whether to print messages to explain why a unit can't move in a certain direction
        Output:
            boolean: Returns True if this mob can move to the proposed destination, otherwise returns False
        """
        if self.get_permission(constants.ACTIVE_PERMISSION):
            if not self.get_permission(constants.MOVEMENT_DISABLED_PERMISSION):
                return super().can_move(x_change, y_change, can_print)
            elif can_print:
                text_utility.print_to_screen(
                    f"This {self.name} is still having its crew replaced and cannot move this turn."
                )
        elif can_print:
            text_utility.print_to_screen(f"A {self.name} cannot move without a crew.")
        return False

    def get_worker(self) -> "pmob":
        """
        Description:
            Returns the worker associated with this unit, if any (self if worker, crew if vehicle, worker component if group)
        Input:
            None
        Output:
            worker: Returns the worker associated with this unit, if any
        """
        if self.crew:
            return self.crew
        else:
            return super().get_worker()

    def update_habitability(self):
        """
        Description:
            Updates this unit's habitability and that of its passengers, based on the location it is in
        Input:
            None
        Output:
            None
        """
        super().update_habitability()
        for current_mob in self.contained_mobs:
            current_mob.update_habitability()
