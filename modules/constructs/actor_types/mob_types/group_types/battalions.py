# Contains functionality for battalions

from modules.constructs.actor_types.mob_types.groups import group
from modules.constants import constants, status, flags


class battalion(group):
    """
    A group with a major officer that can attack enemies
    """

    def __init__(self, from_save, input_dict):
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
                'end_turn_destination_coordinates': int tuple value - None if no saved destination, destination coordinates if saved destination
                'end_turn_destination_world_index': int value - Index of the world of the end turn destination, if any
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'max_movement_points': int value - Required if from save, maximum number of movement points this mob can have
                'worker': worker or dictionary value - If creating a new group, equals a worker that is part of this group. If loading, equals a dictionary of the saved information necessary to recreate the worker
                'officer': worker or dictionary value - If creating a new group, equals an officer that is part of this group. If loading, equals a dictionary of the saved information necessary to recreate the officer
        Output:
            None
        """
        super().__init__(from_save, input_dict)
        if not from_save:
            if constants.ALLOW_DISORGANIZED:
                self.set_permission(constants.DISORGANIZED_PERMISSION, True)

    def get_movement_cost(self, x_change, y_change, post_attack=False):
        """
        Description:
            Returns the cost in movement points of moving by the inputted amounts. Only works when one inputted amount is 0 and the other is 1 or -1, with 0 and -1 representing moving 1 location downward
        Input:
            int x_change: How many locations would be moved to the right in the hypothetical movement
            int y_change: How many locations would be moved upward in the hypothetical movement
            boolean post_attack = False: Whether this movement is occuring directly after an attack order or not. A battalion can move into a location to attack it by using only 1 movement point but must return afterward if not
                enough movement points to move there normally
        Output:
            double: How many movement points would be spent by moving by the inputted amount
        """
        cost = self.movement_cost

        direction = None
        if x_change < 0:
            direction = "left"
        elif x_change > 0:
            direction = "right"
        elif y_change > 0:
            direction = "up"
        elif y_change < 0:
            direction = "down"
        elif x_change == 0 and y_change == 0:
            direction = None

        if direction:
            adjacent_location = self.location.adjacent_locations[direction]
        else:
            adjacent_location = self.location

        if adjacent_location:
            if (
                (not post_attack)
                and self.get_permission(constants.BATTALION_PERMISSION)
                and adjacent_location.get_best_combatant("npmob")
            ):  # if battalion attacking
                cost = 1
            else:
                cost = super().get_movement_cost(x_change, y_change)
        return cost

    def move(self, x_change, y_change, attack_confirmed=False):
        """
        Description:
            Moves this mob x_change to the right and y_change upward. If moving into a location with an npmob, asks for a confirmation to attack instead of moving. If the attack
                is confirmed, move is called again to cause a combat to start
        Input:
            int x_change: How many locations are moved to the right in the movement
            int y_change: How many locations are moved upward in the movement
            boolean attack_confirmed = False: Whether an attack has already been confirmed. If an attack has been confirmed, a move into the target location will occur and a combat will start
        Output:
            None
        """
        flags.show_selection_outlines = True
        flags.show_minimap_outlines = True
        constants.last_selection_outline_switch = (
            constants.current_time
        )  # outlines should be shown immediately when selected
        if not status.actions["combat"].on_click(
            self,
            on_click_info_dict={
                "x_change": x_change,
                "y_change": y_change,
                "attack_confirmed": attack_confirmed,
            },
        ):  # if destination empty or attack already confirmed, move in
            initial_movement_points = self.movement_points
            if attack_confirmed:
                original_disorganized = self.get_permission(
                    constants.DISORGANIZED_PERMISSION
                )
            super().move(x_change, y_change)
            if attack_confirmed:
                self.set_permission(
                    constants.DISORGANIZED_PERMISSION, original_disorganized
                )  # cancel effect from moving into water until after combat
            if attack_confirmed:
                self.set_movement_points(
                    initial_movement_points
                )  # gives back movement points for moving, movement points will be consumed anyway for attacking but will allow unit to move onto beach after disembarking ship
