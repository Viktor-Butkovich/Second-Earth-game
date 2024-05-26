# Contains functionality for villages

import random
from ..util import village_name_generator, actor_utility, utility
import modules.constants.constants as constants
import modules.constants.status as status


class village:
    """
    Object that represents a native village in a cell on the strategic map grid
    """

    def __init__(self, from_save, input_dict):
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'name': string value - Required if from save, starting name of village
                'population': int value - Required if from save, starting population of village
                'aggressiveness': int value - Required if from save, starting aggressiveness
                'available_workers': int value - Required if from save, starting number of available workers
                'cell': cell value - cell on strategic map grid in which this village exists
        Output:
            None
        """
        self.attached_warriors = []
        self.cell = input_dict["cell"]
        self.x = self.cell.x
        self.y = self.cell.y
        self.tiles = []  # added in set_resource for tiles

        if not from_save:
            self.set_initial_population()
            self.set_initial_aggressiveness()
            self.available_workers = 0
            self.name = village_name_generator.create_village_name()
            self.found_rumors = False
        else:  # village recreated through saved dictionary given by tile.set_resource from the cell's save_dict
            self.name = input_dict["name"]
            self.population = input_dict["population"]
            self.set_aggressiveness(input_dict["aggressiveness"])
            self.available_workers = input_dict["available_workers"]
            self.found_rumors = input_dict["found_rumors"]
            for current_save_dict in input_dict["attached_warriors"]:
                current_save_dict["origin_village"] = self
                constants.actor_creation_manager.create(True, current_save_dict)
        if constants.effect_manager.effect_active("infinite_village_workers"):
            self.available_workers = self.population

        if (
            not self.cell.grid.is_mini_grid
        ):  # villages should not be created in mini grid cells, so do not allow village to be visible to rest of program if it is on a mini grid cell
            status.village_list.append(self)  # have more permanent fix later
            if not self.cell.settlement:
                self.cell.tile.set_name(self.name)

    def has_cannibals(self) -> bool:
        """
        Description:
            Returns whether this village has cannibals
        Input:
            None
        Output:
            boolean: Returns whether this village has cannibals
        """
        return bool(self.cell.terrain_handler.terrain_features.get("cannibals", False))

    def remove_cannibals(self) -> None:
        """
        Description:
            Removes cannibals from this village, if any
        Input:
            None
        Output:
            None
        """
        if self.has_cannibals():
            del self.cell.terrain_handler.terrain_features["cannibals"]
            self.cell.tile.update_image_bundle()

    def remove_complete(self):
        """
        Description:
            Removes this object and deallocates its memory - defined for any removable object w/o a superclass
        Input:
            None
        Output:
            None
        """
        self.remove()
        del self

    def remove(self):
        """
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        Input:
            None
        Output:
            None
        """
        status.village_list = utility.remove_from_list(status.village_list, self)

    def manage_warriors(self):
        """
        Description:
            Controls the spawning and despawning of native warriors, with higher-population and highly aggressive villages being more likely to spawn. Spawned warriors temporarily leave the population and return when despawned
        Input:
            None
        Output:
            None
        """
        for current_attached_warrior in self.attached_warriors:
            current_attached_warrior.check_despawn()

        if (
            self.can_spawn_warrior() and random.randrange(1, 7) >= 3
        ):  # 2/3 chance of even attempting
            min_spawn_result = (
                6 + self.get_aggressiveness_modifier()
            )  # 6-1 = 5 on high aggressiveness, 6 on average aggressiveness, 6+1 = 7 on low aggressiveness
            if (
                random.randrange(1, 7) >= min_spawn_result
            ):  # 1/3 on high, 1/6 on average, 0 on low
                self.spawn_warrior()

    def can_spawn_warrior(self):
        """
        Description:
            Returns whether this village can currently spawn a warrior. A village with 0 population cannot spawn warriors, and available workers will not become warriors
        Input:
            None
        Output:
            Returns whether this village can currently spawn a warrior
        """
        if constants.effect_manager.effect_active("block_native_warrior_spawning"):
            return False
        if self.population > self.available_workers:
            return True
        return False

    def can_recruit_worker(self):
        """
        Description:
            Returns whether a worker can be recruited from this village
        Input:
            None
        Output:
            boolean: Returns True if this village has any available workers, otherwise returns False
        """
        if self.available_workers > 0:
            return True
        return False

    def spawn_warrior(self):
        """
        Description:
            Creates a native warrior at this village's location from one of its population units
        Input:
            None
        Output:
            native_warriors: Returns the created native warriors unit
        """
        new_warrior = constants.actor_creation_manager.create(
            False,
            {
                "coordinates": (self.cell.x, self.cell.y),
                "grids": [self.cell.grid] + self.cell.grid.mini_grids,
                "image": "mobs/native warriors/default.png",
                "canoes_image": "mobs/native warriors/canoe_default.png",
                "modes": self.cell.grid.modes,
                "name": "native warriors",
                "init_type": "native_warriors",
                "origin_village": self,
            },
        )
        self.change_population(-1)
        return new_warrior

    def recruit_worker(self):
        """
        Description:
            Hires one of this village's available workers by creating a worker, reducing the village's population and number of available workers
        Input:
            None
        Output:
            None
        """
        input_dict = {
            "select_on_creation": True,
            "coordinates": (self.cell.x, self.cell.y),
            "grids": [self.cell.grid] + self.cell.grid.mini_grids,
            "modes": self.cell.grid.modes,
        }
        input_dict.update(status.worker_types["African"].generate_input_dict())
        constants.actor_creation_manager.create(False, input_dict)
        self.change_available_workers(-1)
        self.change_population(-1)

    def set_initial_population(self):
        """
        Description:
            Sets this village's population to a random number between 1 and 9
        Input:
            None
        Output:
            None
        """
        self.population = random.randrange(1, 10)

    def set_initial_aggressiveness(self):
        """
        Description:
            Sets this village's population to its aggressiveness changed randomly. Change based on 9 rolls of D6, decrease on 1-2, increase on 5-6, roll again on 1 or 6
        Input:
            None
        Output:
            None
        """
        self.aggressiveness = self.population
        remaining_rolls = 9
        while remaining_rolls > 0:
            remaining_rolls -= 1
            roll = random.randrange(1, 7)
            if roll <= 2:  # 1-2
                self.aggressiveness -= 1
                if roll == 1:
                    remaining_rolls += 1
            # 3-4 does nothing
            elif roll >= 5:  # 5-6
                self.aggressiveness += 1
                if roll == 6:
                    remaining_rolls += 1
            self.set_aggressiveness(self.aggressiveness)

    def set_aggressiveness(self, new_aggressiveness):
        """
        Description:
            Sets this village's aggressiveness to the inputted value, with bounded by 1-9
        Input:
            int new_aggressiveness: New aggressiveness value
        Output:
            None
        """
        self.aggressiveness = min(max(new_aggressiveness, 1), 9)
        if self.tiles:
            self.tiles[0].update_image_bundle()
        if (
            self.cell.tile == status.displayed_tile
        ):  # if being displayed, change displayed aggressiveness value
            actor_utility.calibrate_actor_info_display(
                status.tile_info_display, self.cell.tile
            )

    def get_tooltip(self):
        """
        Description:
            Returns this village's tooltip. Its tooltip describes its name, population, how many of its population are willing to become workers, and aggressiveness
        Input:
            None
        Output:
            string list: list with each item representing a line of this village's tooltip
        """
        tooltip_text = []
        tooltip_text.append("Village name: " + self.name)
        tooltip_text.append("    Total population: " + str(self.population))
        tooltip_text.append("    Available workers: " + str(self.available_workers))
        tooltip_text.append("    Aggressiveness: " + str(self.aggressiveness))
        return tooltip_text

    def get_aggressiveness_modifier(
        self,
    ):  # modifier affects roll difficulty, not roll result
        """
        Description:
            Returns a modifier corresponding to this village's aggressiveness, with higher aggressiveness causing lower modifiers. These modifiers affect the difficulty of actions relating to this village
        Input:
            None
        Output:
            int: Returns 1 if this village's aggressiveness is between 0 and 3, returns 0 if this village's aggressiveness if between 4 and 6, otherwise returns -1
        """
        if self.aggressiveness <= 3:  # 1-3
            return 1
        elif self.aggressiveness <= 6:  # 4 - 6
            return 0
        else:  # 7 - 9
            return -1

    def get_aggressiveness_adjective(self):
        """
        Description:
            Returns an adjective corresponding to this village's aggressiveness modifier
        Input:
            None
        Output:
            string: Returns an adjective corresponding to this village's aggressiveness modifier
        """
        aggressiveness_modifier = self.get_aggressiveness_modifier()
        if aggressiveness_modifier == 1:
            return "peaceful"
        elif aggressiveness_modifier == 0:
            return "neutral"
        elif aggressiveness_modifier == -1:
            return "aggressive"

    def get_population_modifier(
        self,
    ):  # modifier affects roll difficulty, not roll result
        """
        Description:
            Returns a modifier corresponding to this village's population with higher population causing lower modifiers. These modifiers affect the difficulty and reward level of actions relating to this village
        Input:
            None
        Output:
            int: Returns 1 if this village's aggressiveness is between 0 and 3, returns 0 if this village's aggressiveness if between 4 and 6, otherwise returns -1
        """
        if self.population <= 3:  # 1-3
            return 1
        elif self.population <= 6:  # 4 - 6
            return 0
        else:  # 7 - 9
            return -1

    def change_available_workers(self, change):
        """
        Description:
            Changes this village's number of available workers by the inputted amount, updating the tile info display as applicable
        Input:
            int change: amount this village's population is changed by
        Output:
            None
        """
        self.available_workers += change
        if (
            self.cell.tile == status.displayed_tile
        ):  # if being displayed, change displayed available workers value
            actor_utility.calibrate_actor_info_display(
                status.tile_info_display, self.cell.tile
            )

    def set_available_workers(self, new_value):
        """
        Description:
            Sets this village's number of avavilable workers to the inputted amount
        Input:
            None
        Output:
            None
        """
        self.available_workers = new_value
        if (
            self.cell.tile == status.displayed_tile
        ):  # if being displayed, change displayed available workers value
            actor_utility.calibrate_actor_info_display(
                status.tile_info_display, self.cell.tile
            )

    def change_population(self, change):
        """
        Description:
            Changes this village's population by the inputted amount. Prevents the value from exiting the allowed range of 1-9 and updates the tile info display as applicable
        Input:
            int change: amount this village's population is changed by
        Output:
            None
        """
        self.population += change
        if self.population > 9:
            self.population = 9
        elif self.population < 0:
            self.population = 0
        if self.available_workers > self.population:
            self.set_available_workers(self.population)
        if self.population == 0 and len(self.attached_warriors) == 0:
            self.set_aggressiveness(1)
        self.tiles[0].update_image_bundle()
        if (
            self.cell.tile == status.displayed_tile
        ):  # if being displayed, change displayed population value
            actor_utility.calibrate_actor_info_display(
                status.tile_info_display, self.cell.tile
            )

    def change_aggressiveness(self, change):
        """
        Description:
            Changes this village's aggressiveness by the inputted amount. Prevents the value from exiting the allowed range of 1-9 and updates the tile info display as applicable
        Input:
            int change: amount this village's aggressivness is changed by
        Output:
            None
        """
        self.set_aggressiveness(self.aggressiveness + change)
