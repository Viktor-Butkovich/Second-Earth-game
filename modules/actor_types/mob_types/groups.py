# Contains functionality for group units

import random
import math
from typing import Dict, List
from modules.actor_types.mob_types.pmobs import pmob
from modules.util import actor_utility, minister_utility, utility
from modules.constants import constants, status, flags


class group(pmob):
    """
    pmob that is created by a combination of a worker and officer, has special capabilities depending on its officer, and separates its worker and officer upon being disbanded
    """

    def __init__(self, from_save, input_dict, original_constructor=True):
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'grids': grid list value - grids in which this group's images can appear
                'image': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'name': string value - Required if from save, this group's name
                'modes': string list value - Game modes during which this group's images can appear
                'end_turn_destination': string or int tuple value - Required if from save, None if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not None, matches the status key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'max_movement_points': int value - Required if from save, maximum number of movement points this mob can have
                'worker': worker or dictionary value - If creating a new group, equals a worker that is part of this group. If loading, equals a dictionary of the saved information necessary to recreate the worker
                'officer': worker or dictionary value - If creating a new group, equals an officer that is part of this group. If loading, equals a dictionary of the saved information necessary to recreate the officer
        Output:
            None
        """
        if not from_save:
            self.worker: pmob = input_dict["worker"]
            self.officer: pmob = input_dict["officer"]
        else:
            self.worker: pmob = constants.actor_creation_manager.create(
                True, input_dict["worker"]
            )
            self.officer: pmob = constants.actor_creation_manager.create(
                True, input_dict["officer"]
            )
        super().__init__(from_save, input_dict, original_constructor=False)
        self.worker.join_group(self)
        self.officer.join_group(self)
        for current_mob in [
            self.worker,
            self.officer,
        ]:  # Merges individual inventory to group inventory and clears individual inventory
            for current_item_type in current_mob.get_held_items():
                self.change_inventory(
                    current_item_type, current_mob.get_inventory(current_item_type)
                )
                current_mob.set_inventory(current_item_type, 0)

        if not from_save:
            for equipment in set(self.worker.equipment.keys()).union(
                self.officer.equipment.keys()
            ):
                if status.equipment_types[equipment].check_requirement(self):
                    if self.worker.equipment.get(
                        equipment, False
                    ) and self.officer.equipment.get(
                        equipment, False
                    ):  # If both worker and officer had same equipment, drop extra
                        self.get_cell().tile.change_inventory(equipment, 1)
                    status.equipment_types[equipment].equip(self)

        if not from_save:
            self.set_permission(
                constants.DISORGANIZED_PERMISSION,
                self.worker.get_permission(constants.DISORGANIZED_PERMISSION),
            )
        if self.officer.get_permission(constants.VETERAN_PERMISSION):
            self.promote()
        if not from_save:
            self.status_icons = self.officer.status_icons
            for current_status_icon in self.status_icons:
                current_status_icon.actor = self
            self.set_movement_points(
                actor_utility.generate_group_movement_points(self.worker, self.officer)
            )
        if self.get_permission(constants.EXPEDITION_PERMISSION):
            self.on_move()
        self.finish_init(original_constructor, from_save, input_dict)

    def get_item_upkeep(self, recurse: bool = False) -> Dict[str, float]:
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
                super().get_item_upkeep(recurse=recurse),
                self.worker.get_item_upkeep(recurse=recurse),
                self.officer.get_item_upkeep(recurse=recurse),
            )
        else:
            return super().get_item_upkeep(recurse=recurse)

    def get_sub_mobs(self) -> List[pmob]:
        """
        Description:
            Returns a list of units managed by this unit
        Input:
            None
        Output:
            list: Returns a list of units managed by this unit
        """
        return [self.worker, self.officer]

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
        self.set_permission(constants.GROUP_PERMISSION, True)

    def replace_worker(self, new_worker_type):
        """
        Description:
            Fires this group's current worker and replaces it with a worker of the inputted type, affecting worker upkeep prices and public opinion as usual
        Input:
            worker_type new_worker_type: New type of worker to create
        Output:
            None
        """
        input_dict = {
            "coordinates": (self.x, self.y),
            "grids": self.grids,
            "modes": self.modes,
        }

        input_dict.update(new_worker_type.generate_input_dict())
        constants.money_tracker.change(
            -1 * new_worker_type.recruitment_cost,
            "unit_recruitment",
        )
        previous_selected = status.displayed_mob
        new_worker = constants.actor_creation_manager.create(False, input_dict)
        new_worker.set_automatically_replace(self.worker.automatically_replace)
        self.worker.fire(wander=False)
        self.worker = new_worker
        self.worker.update_image_bundle()
        self.worker.join_group(self)
        self.update_image_bundle()
        if previous_selected:
            previous_selected.select()

    def move(self, x_change, y_change):
        """
        Description:
            Moves this mob x_change to the right and y_change upward, also making sure to update the positions of the group's worker and officer
        Input:
            int x_change: How many cells are moved to the right in the movement
            int y_change: How many cells are moved upward in the movement
        Output:
            None
        """
        super().move(x_change, y_change)
        self.calibrate_sub_mob_positions()

    def calibrate_sub_mob_positions(self):
        """
        Description:
            Updates the positions of this mob's submobs (mobs inside of a building or other mob that are not able to be independently viewed or selected) to match this mob
        Input:
            None
        Output:
            None
        """
        self.officer.x = self.x
        self.officer.y = self.y
        self.worker.x = self.x
        self.worker.y = self.y
        self.on_move()

    def fire(self):
        """
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. Also fires this group's worker and officer
        Input:
            None
        Output:
            None
        """
        self.drop_inventory()
        self.officer.fire()
        self.worker.fire()
        self.remove_complete()

    def to_save_dict(self):
        """
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                Same pairs as superclass, along with:
                'worker': dictionary value - dictionary of the saved information necessary to recreate the worker
                'officer': dictionary value - dictionary of the saved information necessary to recreate the officer
        """
        save_dict = super().to_save_dict()
        save_dict["worker"] = self.worker.to_save_dict()
        save_dict["officer"] = self.officer.to_save_dict()
        return save_dict

    def promote(self):
        """
        Description:
            Promotes this group's officer to a veteran after performing various actions particularly well, improving the capabilities of groups the officer is attached to in the future. Creates a veteran star icon that follows this
                group and its officer
        Input:
            None
        Output:
            None
        """
        if self.get_permission(constants.PORTERS_PERMISSION):
            self.set_max_movement_points(6, initial_setup=False)
        if not self.officer.get_permission(constants.VETERAN_PERMISSION):
            self.officer.promote()
        if not self.get_permission(constants.VETERAN_PERMISSION):
            self.set_name("veteran " + self.name)
        self.set_permission(constants.VETERAN_PERMISSION, True)
        if (
            self.get_permission(constants.IN_VEHICLE_PERMISSION)
            and status.displayed_mob == self.vehicle
        ):
            actor_utility.calibrate_actor_info_display(
                status.mob_info_display, self.vehicle
            )

    def go_to_grid(self, new_grid, new_coordinates):
        """
        Description:
            Links this group to a grid, causing it to appear on that grid and its minigrid at certain coordinates. Used when crossing the ocean and when a group that was previously attached to another actor becomes independent and
                visible, like when a group disembarks a ship. Also moves its officer and worker to the new grid
        Input:
            grid new_grid: grid that this group is linked to
            int tuple new_coordinates: Two values representing x and y coordinates to start at on the inputted grid
        Output:
            None
        """
        super().go_to_grid(new_grid, new_coordinates)
        self.officer.go_to_grid(new_grid, new_coordinates)
        self.officer.join_group(self)
        self.worker.go_to_grid(new_grid, new_coordinates)
        self.worker.join_group(self)

    def disband(self, focus=True):
        """
        Description:
            Separates this group into its officer and worker, destroying the group
        Input:
            None
        Output:
            None
        """
        for equipment, equipped in list(self.equipment.items()):
            if equipped:
                if status.equipment_types[equipment].check_requirement(self.worker):
                    status.equipment_types[equipment].unequip(self)
                    status.equipment_types[equipment].equip(self.worker)
                elif status.equipment_types[equipment].check_requirement(self.officer):
                    status.equipment_types[equipment].unequip(self)
                    status.equipment_types[equipment].equip(self.officer)
        self.drop_inventory()
        self.worker.leave_group(self, focus=False)

        movement_ratio_remaining = self.movement_points / self.max_movement_points
        self.worker.set_movement_points(
            math.floor(movement_ratio_remaining * self.worker.max_movement_points)
        )
        self.officer.status_icons = self.status_icons
        for current_status_icon in self.status_icons:
            current_status_icon.actor = self.officer
        self.officer.leave_group(self, focus=focus)
        self.officer.set_movement_points(
            math.floor(movement_ratio_remaining * self.officer.max_movement_points)
        )
        self.remove_complete()

    def die(self, death_type="violent"):
        """
        Description:
            Removes this object from relevant lists, prevents it from further appearing in or affecting the program, deselects it, and drops any items it is carrying. Unlike remove, this is used when the group dies because it
                also removes its worker and officer
        Input:
            string death_type == 'violent': Type of death for this unit, determining the type of sound played
        Output:
            None
        """
        super().die(death_type)
        self.officer.die(None)
        self.worker.die(None)

    def get_worker(self) -> "pmob":
        """
        Description:
            Returns the worker associated with this unit, if any (self if worker, crew if vehicle, worker component if group)
        Input:
            None
        Output:
            worker: Returns the worker associated with this unit, if any
        """
        return self.worker
