# Contains functionality for native warriors units

import random
from ..npmobs import npmob
from ....util import utility
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags


class native_warriors(npmob):
    """
    npmob that represents a population unit that temporarily leaves an aggressive village to attack player-controlled mobs/buildings
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
                'canoes_image': string value - File path to the image used by this object when it is in a river
        Output:
            None
        """
        super().__init__(from_save, input_dict)
        self.number = 2  # native warriors is plural
        self.hostile = True
        self.can_damage_buildings = True
        self.aggro_distance = 3
        self.saves_normally = False  # saves as part of village
        self.origin_village = input_dict["origin_village"]
        self.origin_village.attached_warriors.append(self)
        self.npmob_type = "native_warriors"
        self.despawning = False
        if not from_save:
            self.set_max_movement_points(4)
            if not flags.creating_new_game:
                self.hide_images()  # show native warriors spawning in main_loop during enemy turn, except during setup
            self.second_image_variant = random.randrange(0, len(self.image_variants))
        self.set_has_canoes(True)
        self.update_canoes()

    def combat_roll(self) -> int:
        """
        Description:
            Calculates and returns this unit's combat roll - default of 1D6 with no modifiers
        Input:
            None
        Output:
            int: Returns this unit's combat roll
        """
        initial_result = super().combat_roll()
        if self.origin_village.has_cannibals():
            initial_result_copy = initial_result
            initial_result += random.randrange(0, 2)
            initial_result = min(initial_result, 6)
            if constants.effect_manager.effect_active("show_modifiers"):
                print(
                    f"Cannibals added {initial_result - initial_result_copy} to combat roll"
                )
        return initial_result

    def attack_on_spawn(self):
        """
        Description:
            Upon spawning, checks if there are any pmobs or destructible buildings in this tile and attacks them as applicable
        Input:
            None
        Output:
            None
        """
        if (
            self.combat_possible()
        ):  # attack any player-controlled units in tile when spawning
            available_directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # all directions
            possible_directions = []  # only directions that can be retreated in
            for direction in available_directions:
                cell = self.images[0].current_cell.grid.find_cell(
                    self.x - direction[0], self.y - direction[1]
                )
                if cell:
                    if (
                        not cell.has_pmob() and not cell.y == 0
                    ):  # can't retreat to ocean or into player units
                        possible_directions.append(direction)
            if len(possible_directions) > 0:
                self.last_move_direction = random.choice(possible_directions)
                if flags.player_turn:
                    if (
                        self.grids[0]
                        .find_cell(self.x, self.y)
                        .get_best_combatant("pmob", self.npmob_type)
                        == "none"
                    ):
                        self.kill_noncombatants()
                        self.damage_buildings()
                    else:
                        self.attempt_local_combat()  # if spawned by failed trade or conversion during player turn, attack immediately
                else:
                    status.attacker_queue.append(self)
            else:
                self.remove_complete()
                self.origin_village.change_population(
                    1
                )  # despawn if pmob on tile and can't retreat anywhere
        else:
            self.damage_buildings()

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
        self.origin_village.attached_warriors = utility.remove_from_list(
            self.origin_village.attached_warriors, self
        )
        if (
            self.origin_village.population == 0
            and len(self.origin_village.attached_warriors) == 0
        ):
            self.origin_village.set_aggressiveness(0)

    def check_despawn(self):
        """
        Description:
            Gives each native warrior a 1/6 chance of despawning and returning to its home village at the end of the turn
        Input:
            None
        Output:
            None
        """
        if (
            random.randrange(1, 7) >= 4 and random.randrange(1, 7) >= 4
        ):  # 1/4 chance of despawn
            self.despawning = True
            self.origin_village.change_population(1)

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
        image_id_list.remove(
            self.image_dict["default"]
        )  # remove default middle warrior
        left_warrior_dict = {
            "image_id": self.image_dict["default"],
            "size": 0.83,
            "x_offset": -0.23,
            "y_offset": 0,
            "level": -1,
        }
        image_id_list.append(left_warrior_dict)

        right_warrior_dict = left_warrior_dict.copy()
        right_warrior_dict["image_id"] = self.image_variants[self.second_image_variant]
        right_warrior_dict["x_offset"] *= -1
        image_id_list.append(right_warrior_dict)
        return image_id_list
