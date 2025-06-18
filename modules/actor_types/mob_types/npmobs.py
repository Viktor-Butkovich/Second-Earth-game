# Contains functionality for non-player-controlled mobs

import random
from modules.actor_types.mobs import mob
from modules.util import utility, turn_management_utility, actor_utility
from modules.constants import constants, status, flags


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
        self.hostile = False
        self.can_damage_buildings = False
        self.npmob_type = "npmob"
        self.aggro_distance = 0
        if (
            self.get_location().y == 0
        ):  # should fix any case of npmob trying to retreat off the map
            self.last_move_direction = (0, 1)
        else:
            self.last_move_direction = (0, -1)
        status.npmob_list.append(self)
        self.turn_done = True

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
        self.set_permission(constants.NPMOB_PERMISSION, True)

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
            Returns whether this unit is currently visible to the player
        Input:
            None
        Output:
            boolean: Returns whether this unit is currently visible to the player
        """
        return True  # return self.get_cell() and self.get_location().visible

    def find_closest_target(self):
        """
        Description:
            Find and returns one of the closest reachable pmobs or buildings
        Input:
            None
        Output:
            string/actor: Returns one of the closest reachable pmobs or buildings, or returns None if none are reachable
        """
        target_list = []
        #for current_building in status.building_list:
        #    if (
        #        current_building.building_type.can_damage
        #        and not current_building.damaged
        #    ):
        #        target_list.append(current_building)
        # Modify this to use settlements instead
        target_list += status.pmob_list
        min_distance = -1
        closest_targets = [None]
        for possible_target in target_list:
            target_location = possible_target.get_location()
            if (
                not target_location.y == 0
            ):  # Ignore units in the ocean if can't swim in ocean
                if not possible_target.any_permissions(
                    constants.IN_VEHICLE_PERMISSION,
                    constants.IN_GROUP_PERMISSION,
                    constants.IN_BUILDING_PERMISSION,
                ):
                    current_location = self.get_location()
                    distance = current_location.get_world_handler().manhattan_distance(
                        current_location, target_location
                    )
                    if (
                        distance <= self.aggro_distance
                    ):  # Ignore player's units more than 6 locations away
                        if min_distance == -1 and (
                            not distance == -1
                        ):  # Automatically choose first one to replace initial value
                            min_distance = distance
                            closest_targets = [possible_target]
                        else:
                            if not distance == -1:  # If on same grid
                                if (
                                    distance < min_distance
                                ):  # If closer than any previous, replace all previous
                                    min_distance = distance
                                    closest_targets = [possible_target]
                                elif (
                                    distance == min_distance
                                ):  # If as close as previous, add as alternative to previous
                                    closest_targets.append(possible_target)
        return random.choice(
            closest_targets
        )  # return one of the closest ones, or None if none were found

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
        current_location = self.get_location()
        actor_utility.focus_minimap_grids(current_location)
        for current_mob in current_location.subscribed_mobs:
            if current_mob.get_permission(constants.VEHICLE_PERMISSION):
                current_mob.eject_passengers()
                current_mob.eject_crew()
        if current_location.has_intact_building(constants.RESOURCE):
            current_location.get_intact_building(constants.RESOURCE).eject_work_crews()
        defender = current_location.get_best_combatant("pmob", self.npmob_type)
        if defender:
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
        current_location = self.get_location()
        noncombatants = current_location.get_noncombatants("pmob")
        for current_noncombatant in noncombatants:
            constants.notification_manager.display_notification(
                {
                    "message": f"The undefended {current_noncombatant.name} has been killed by {self.name} at ({current_location.x}, {current_location.y}). /n"
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
        current_location = self.get_location()
        for current_building in current_location.get_intact_buildings():
            if current_building.building_type.can_damage:
                constants.notification_manager.display_notification(
                    {
                        "message": f"The undefended {current_building.name} has been damaged by {self.name} at ({current_location.x}, {current_location.y}). /n"
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
        initial_location = self.get_location()
        if random.randrange(1, 7) <= 3:  # Half chance of moving randomly instead
            closest_target = random.choice(initial_location.adjacent_list)
            while (
                closest_target.get_location().y == 0
            ):  # npmobs avoid the ocean if can't swim in ocean
                closest_target = random.choice(initial_location.adjacent_list)
        target_location = closest_target.get_location() if closest_target else None
        if closest_target:
            if (
                initial_location != target_location
            ):  # Don't move if target is in the same location
                if (
                    target_location.x > initial_location.x
                ):  # Decides moving left or right
                    horizontal_multiplier = 1
                elif target_location.x == initial_location.x:
                    horizontal_multiplier = 0
                else:
                    horizontal_multiplier = -1

                if target_location.y > initial_location.y:  # Decides moving up or down
                    vertical_multiplier = 1
                elif target_location.y == initial_location.y:
                    vertical_multiplier = 0
                else:
                    vertical_multiplier = -1

                if horizontal_multiplier == 0:
                    if not vertical_multiplier == 0:
                        # While self.movement_points > 0:
                        if self.movement_points >= self.get_movement_cost(
                            0, 1 * vertical_multiplier
                        ):
                            self.move(0, 1 * vertical_multiplier)
                        else:
                            self.movement_points -= 1
                elif vertical_multiplier == 0:
                    # While self.movement_points > 0:
                    if self.movement_points >= self.get_movement_cost(
                        1 * horizontal_multiplier, 0
                    ):
                        self.move(1 * horizontal_multiplier, 0)
                    else:
                        self.movement_points -= 1
                else:
                    horizontal_distance = abs(
                        initial_location.x - target_location.x
                    )  # Decides moving left/right or up/down
                    vertical_distance = abs(initial_location.y - target_location.y)
                    manhattan_distance = (
                        horizontal_distance + vertical_distance
                    )  # If horizontal is 3 and vertical is 2, move horizontally if random from 1 to 5 is 3 or lower: 60% chance of moving horizontally, 40% of moving vertically
                    if (
                        random.randrange(0, manhattan_distance + 1)
                        <= horizontal_distance
                    ):  # Allows weighting of movement to be more likely to move along axis w/ greater distance
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
                if self.get_location().has_unit_by_filter(
                    [constants.PMOB_PERMISSION]
                ) or (
                    self.can_damage_buildings
                    and self.get_location().has_destructible_buildings()
                ):
                    self.kill_noncombatants()
                    if self.can_damage_buildings:
                        self.damage_buildings()
                    self.movement_points = 0
            if self.movement_points == 0:
                self.turn_done = True
        else:
            self.turn_done = True
