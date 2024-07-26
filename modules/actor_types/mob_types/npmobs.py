# Contains functionality for non-player-controlled mobs

import random
from ..mobs import mob
from ...util import utility, turn_management_utility
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags


class npmob(mob):
    """
    Short for non-player-controlled mob, mob not controlled by the player
    """

    def __init__(self, from_save, input_dict):
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
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'max_movement_points': int value - Required if from save, maximum number of movement points this mob can have
        Output:
            None
        """
        super().__init__(from_save, input_dict)
        self.can_swim = True
        self.hostile = False
        self.can_damage_buildings = False
        self.is_npmob = True
        self.npmob_type = "npmob"
        self.aggro_distance = 0
        self.selection_outline_color = "bright red"
        if self.y == 0:  # should fix any case of npmob trying to retreat off the map
            self.last_move_direction = (0, 1)
        else:
            self.last_move_direction = (0, -1)
        status.npmob_list.append(self)
        self.turn_done = True

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
        status.npmob_list = utility.remove_from_list(status.npmob_list, self)

    def combat_roll(self) -> int:
        """
        Description:
            Calculates and returns this unit's combat roll - default of 1D6 with no modifiers
        Input:
            None
        Output:
            int: Returns this unit's combat roll
        """
        return random.randrange(1, 7)

    def visible(self):
        """
        Description:
            Returns whether this unit is currently visible to the player. npmobs in unexplored tiles are not visible
        Input:
            None
        Output:
            boolean: Returns whether this unit is currently visible to the player
        """
        return self.get_cell() != "none" and self.get_cell().terrain_handler.visible

    def find_closest_target(self):
        """
        Description:
            Find and returns one of the closest reachable pmobs or buildings
        Input:
            None
        Output:
            string/actor: Returns one of the closest reachable pmobs or buildings, or returns 'none' if none are reachable
        """
        target_list = []
        for current_building in status.building_list:
            if current_building.can_damage() and not current_building.damaged:
                target_list.append(current_building)
        target_list += status.pmob_list
        min_distance = -1
        closest_targets = ["none"]
        for possible_target in target_list:
            if (
                not possible_target.y == 0
            ):  # ignore units in the ocean if can't swim in ocean
                if possible_target.actor_type == "building" or not (
                    possible_target.in_vehicle
                    or possible_target.in_group
                    or possible_target.in_building
                ):
                    distance = utility.find_grid_distance(self, possible_target)
                    if (
                        distance <= self.aggro_distance
                    ):  # will ignore player's units more than 6 tiles away
                        if min_distance == -1 and (
                            not distance == -1
                        ):  # automatically choose first one to replace initial value
                            min_distance = distance
                            closest_targets = [possible_target]
                        else:
                            if not distance == -1:  # if on same grid
                                if (
                                    distance < min_distance
                                ):  # if closer than any previous, replace all previous
                                    min_distance = distance
                                    closest_targets = [possible_target]
                                elif (
                                    distance == min_distance
                                ):  # if as close as previous, add as alternative to previous
                                    closest_targets.append(possible_target)
        return random.choice(
            closest_targets
        )  # return one of the closest ones, or 'none' if none were found

    def attempt_local_combat(self):
        """
        Description:
            When this unit moves, it checks if combat is possible in the cell it moved into. If combat is possible, it will attempt to start a combat at the end of the turn with any local pmobs. If, for example, another npmob killed
                the pmob found in this npmob's cell, then this npmob will not start a combat
        Input:
            None
        Output:
            None
        """
        if self.get_cell() == "none":
            current_cell = self.grids[0].find_cell(self.x, self.y)
        else:
            current_cell = self.get_cell()
        status.minimap_grid.calibrate(self.x, self.y)
        for current_mob in current_cell.contained_mobs:
            if current_mob.get_permission(constants.VEHICLE_PERMISSION):
                current_mob.eject_passengers()
                current_mob.eject_crew()
        if current_cell.has_intact_building("resource"):
            current_cell.get_intact_building("resource").eject_work_crews()
        defender = current_cell.get_best_combatant("pmob", self.npmob_type)
        if defender != "none":
            status.actions["combat"].middle(
                {"defending": True, "opponent": self, "current_unit": defender}
            )
        else:
            self.kill_noncombatants()
            self.damage_buildings()
            if len(status.attacker_queue) > 0:
                status.attacker_queue.pop(0).attempt_local_combat()
            elif (
                flags.enemy_combat_phase
            ):  # if enemy combat phase done, go to player turn
                turn_management_utility.start_player_turn()

    def kill_noncombatants(self):
        """
        Description:
            Kills all defenseless units, such as lone officers and vehicles, in this cell after combat if no possible combatants, like workers or soldiers, remain
        Input:
            None
        Output:
            None
        """
        if self.get_cell() == "none":
            current_cell = self.grids[0].find_cell(self.x, self.y)
        else:
            current_cell = self.get_cell()

        noncombatants = current_cell.get_noncombatants("pmob")
        for current_noncombatant in noncombatants:
            constants.notification_manager.display_notification(
                {
                    "message": "The undefended "
                    + current_noncombatant.name
                    + " has been killed by "
                    + self.name
                    + " at ("
                    + str(self.x)
                    + ", "
                    + str(self.y)
                    + "). /n",
                }
            )
            current_noncombatant.die()

    def damage_buildings(self):
        """
        Description:
            Damages all undefended buildings in this cell after combat if no possible combatants, like workers or soldiers, remain
        Input:
            None
        Output:
            None
        """
        if self.get_cell() == "none":
            current_cell = self.grids[0].find_cell(self.x, self.y)
        else:
            current_cell = self.get_cell()

        for current_building in current_cell.get_intact_buildings():
            if current_building.can_damage():
                constants.notification_manager.display_notification(
                    {
                        "message": "The undefended "
                        + current_building.name
                        + " has been damaged by "
                        + self.name
                        + " at ("
                        + str(self.x)
                        + ", "
                        + str(self.y)
                        + "). /n",
                    }
                )
                current_building.set_damaged(True)

    def end_turn_move(self):
        """
        Description: Moves this npmob towards pmobs and buildings at the end of the turn and schedules this npmob to start combat if any pmobs are encountered. Movement is weighted based on the distance on each axis, so movement towards a pmob
            that is far to the north and slightly to the east will be more likely to move north than east. An npmob will use end_turn_move each time it moves during the enemy turn, which may happen multiple times depending on distance
            moved
        Input:
            None
        Output:
            None
        """
        closest_target = self.find_closest_target()
        if random.randrange(1, 7) <= 3:  # half chance of moving randomly instead
            if not self.visible():
                current_cell = self.grids[0].find_cell(self.x, self.y)
            else:
                current_cell = self.get_cell()
            closest_target = random.choice(current_cell.adjacent_list)
            while (
                closest_target.y == 0
            ):  # npmobs avoid the ocean if can't swim in ocean
                closest_target = random.choice(current_cell.adjacent_list)
        if closest_target != "none":
            if not (
                closest_target.x == self.x and closest_target.y == self.y
            ):  # don't move if target is own tile
                if closest_target.x > self.x:  # decides moving left or right
                    horizontal_multiplier = 1
                elif closest_target.x == self.x:
                    horizontal_multiplier = 0
                else:
                    horizontal_multiplier = -1

                if closest_target.y > self.y:  # decides moving up or down
                    vertical_multiplier = 1
                elif closest_target.y == self.y:
                    vertical_multiplier = 0
                else:
                    vertical_multiplier = -1

                if horizontal_multiplier == 0:
                    if not vertical_multiplier == 0:
                        # while self.movement_points > 0:
                        if self.movement_points >= self.get_movement_cost(
                            0, 1 * vertical_multiplier
                        ):
                            self.move(0, 1 * vertical_multiplier)
                        else:
                            self.movement_points -= 1
                elif vertical_multiplier == 0:
                    # while self.movement_points > 0:
                    if self.movement_points >= self.get_movement_cost(
                        1 * horizontal_multiplier, 0
                    ):
                        self.move(1 * horizontal_multiplier, 0)
                    else:
                        self.movement_points -= 1
                else:
                    horizontal_difference = abs(
                        self.x - closest_target.x
                    )  # decides moving left/right or up/down
                    vertical_difference = abs(self.y - closest_target.y)
                    total_difference = (
                        horizontal_difference + vertical_difference
                    )  # if horizontal is 3 and vertical is 2, move horizontally if random from 1 to 5 is 3 or lower: 60% chance of moving horizontally, 40% of moving vertically
                    if (
                        random.randrange(0, total_difference + 1)
                        <= horizontal_difference
                    ):  # allows weighting of movement to be more likely to move along more different axis
                        if self.movement_points >= self.get_movement_cost(
                            1 * horizontal_multiplier, 0
                        ):
                            self.move(1 * horizontal_multiplier, 0)
                        else:
                            self.movement_points -= 1
                    else:
                        if self.movement_points >= self.get_movement_cost(
                            0, 1 * vertical_multiplier
                        ):
                            self.move(0, 1 * vertical_multiplier)
                        else:
                            self.movement_points -= 1
                if horizontal_multiplier == 0 and vertical_multiplier == 0:
                    self.movement_points -= 1
            else:
                self.movement_points -= 1
            if self.combat_possible():
                status.attacker_queue.append(self)
                self.movement_points = 0
            else:
                if not self.visible():
                    current_cell = self.grids[0].find_cell(self.x, self.y)
                else:
                    current_cell = self.get_cell()
                if current_cell.has_pmob() or (
                    self.can_damage_buildings
                    and current_cell.has_destructible_buildings()
                ):
                    self.kill_noncombatants()
                    if self.can_damage_buildings:
                        self.damage_buildings()
                    self.movement_points = 0
            if self.movement_points == 0:
                self.turn_done = True
        else:
            self.turn_done = True

    def move(self, x_change, y_change):
        """
        Description:
            Moves this mob x_change to the right and y_change upward
        Input:
            int x_change: How many cells are moved to the right in the movement
            int y_change: How many cells are moved upward in the movement
        Output:
            None
        """
        for current_image in self.images:
            current_image.remove_from_cell()
        self.movement_points -= self.get_movement_cost(x_change, y_change)
        self.x += x_change
        self.y += y_change
        for current_image in self.images:
            current_image.add_to_cell()
        self.movement_sound()
        self.last_move_direction = (x_change, y_change)
