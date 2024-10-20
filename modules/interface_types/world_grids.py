# Contains functionality for world grids and creating grid objects

import random
import json
from typing import Dict, List
from .grids import grid, mini_grid, abstract_grid
from .cells import cell
from ..util import scaling, utility
from ..tools.data_managers import terrain_manager_template
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags


class world_grid(grid):
    """
    Grid representing the "single source of truth" for a particular world, containing original cells and terrain/world parameters
    """

    def __init__(self, from_save: bool, input_dict: Dict[str, any]) -> None:
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of the bottom left corner of this grid
                'width': int value - Pixel width of this grid
                'height': int value - Pixel height of this grid
                'coordinate_width': int value - Number of columns in this grid
                'coordinate_height': int value - Number of rows in this grid
                'internal_line_color': string value - Color in the color_dict dictionary for lines between cells, like 'bright blue'
                'external_line_color': string value - Color in the color_dict dictionary for lines on the outside of the grid, like 'bright blue'
                'list modes': string list value - Game modes during which this grid can appear
                'grid_line_width': int value - Pixel width of lines between cells. Lines on the outside of the grid are one pixel thicker
                'cell_list': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each cell in this grid
                'grid_type': str value - Type of grid, like 'strategic_map_grid' or 'earth_grid'
        Output:
            None
        """
        super().__init__(from_save, input_dict)
        self.world_handler: terrain_manager_template.world_handler = (
            terrain_manager_template.world_handler(
                self, from_save, input_dict.get("world_handler", {})
            )
        )

    def create_world(self, from_save: bool):
        """
        Description:
            Creates a world, either from scratch or from a save file
        Input:
            bool from_save: True if this object is being recreated from a save file, False if it is being newly created
        Output:
            None
        """
        if from_save:
            for cell in self.get_flat_cell_list():
                cell.terrain_handler.set_resource(cell.save_dict["resource"])
        else:
            self.generate_poles_and_equator()
            self.generate_terrain_parameters()
            self.generate_terrain_features()

    def get_tuning(self, tuning_type: str) -> any:
        """
        Description:
            Returns the tuning value for the inputted tuning type
        Input:
            string tuning_type: Tuning type to return the value of
        Output:
            any: Returns the tuning value
        """
        return constants.terrain_manager.get_tuning(tuning_type)

    def generate_altitude(self) -> None:
        """
        Description:
            Randomly generates altitude
        Input:
            None
        Output:
            None
        """
        default_altitude = 1
        for cell in self.get_flat_cell_list():
            cell.set_parameter(constants.ALTITUDE, default_altitude)

        for i in range(constants.terrain_manager.get_tuning("altitude_worms")):
            min_length = (
                random.randrange(
                    self.get_tuning("min_altitude_worm_multiplier"),
                    self.get_tuning("med_altitude_worm_multiplier"),
                )
                * self.area
            ) // 25**2
            max_length = (
                random.randrange(
                    self.get_tuning("med_altitude_worm_multiplier"),
                    self.get_tuning("max_altitude_worm_multiplier"),
                )
                * self.area
            ) // 25**2
            self.make_random_terrain_parameter_worm(
                min_length,
                max_length,
                constants.ALTITUDE,
                random.choice(self.get_tuning("altitude_changes")),
                bound=random.choice(self.get_tuning("altitude_bounds")),
            )
        if self.get_tuning("smooth_altitude"):
            while self.smooth(
                constants.ALTITUDE
            ):  # Continue running smooth until it doesn't make any more changes
                pass

    def generate_temperature(self) -> None:
        """
        Description:
            Randomly generates temperature
        Input:
            None
        Output:
            None
        """
        default_temperature = self.world_handler.default_temperature
        for cell in self.get_flat_cell_list():
            cell.set_parameter(
                constants.TEMPERATURE,
                random.randrange(
                    default_temperature
                    - self.get_tuning("initial_temperature_variation"),
                    default_temperature
                    + self.get_tuning("initial_temperature_variation")
                    + 1,
                ),
            )
        if self.get_tuning("smooth_temperature"):
            while self.smooth(
                constants.TEMPERATURE
            ):  # Random but smooth initialization to represent weather patterns
                pass

        temperature_sources = [
            status.north_pole,
            status.south_pole,
        ] + status.equator_list
        random.shuffle(
            temperature_sources
        )  # Avoids edge-case bias from poles or equator consistently being chosen first
        for temperature_source in temperature_sources:
            if temperature_source in [status.north_pole, status.south_pole]:
                temperature_source.set_parameter(
                    constants.TEMPERATURE, default_temperature
                )
                if temperature_source == status.north_pole:
                    weight_parameter = "north_pole_distance_multiplier"
                    if constants.effect_manager.effect_active(
                        "mars_preset"
                    ):  # Causes warmer north pole than south - ice caps at north pole, dry ice caps at south pole
                        temperature_source.set_parameter(
                            constants.TEMPERATURE, default_temperature + 1
                        )
                else:
                    weight_parameter = "south_pole_distance_multiplier"
                min_length = (
                    random.randrange(
                        self.get_tuning("min_pole_worm_multiplier"),
                        self.get_tuning("med_pole_worm_multiplier"),
                    )
                    * self.area
                ) // 25**2
                max_length = (
                    random.randrange(
                        self.get_tuning("med_pole_worm_multiplier"),
                        self.get_tuning("max_pole_worm_multiplier"),
                    )
                    * self.area
                ) // 25**2

                for pole_worm_length_multiplier in self.get_tuning(
                    "pole_worm_length_multipliers"
                ):
                    self.make_random_terrain_parameter_worm(
                        min_length * pole_worm_length_multiplier,
                        max_length * pole_worm_length_multiplier,
                        constants.TEMPERATURE,
                        -1,
                        bound=1,
                        start_cell=temperature_source,
                        weight_parameter=weight_parameter,
                    )

            elif not (
                temperature_source.x in [1, self.coordinate_width - 1]
                or temperature_source.y in [0, self.coordinate_height - 1]
            ):  # Avoids excessive heat at equator intersections
                min_length = (
                    random.randrange(
                        self.get_tuning("min_equator_worm_multiplier"),
                        self.get_tuning("med_equator_worm_multiplier"),
                    )
                    * self.area
                ) // 40**2
                max_length = (
                    random.randrange(
                        self.get_tuning("med_equator_worm_multiplier"),
                        self.get_tuning("max_equator_worm_multiplier"),
                    )
                    * self.area
                ) // 40**2
                self.make_random_terrain_parameter_worm(
                    min_length,
                    max_length,
                    constants.TEMPERATURE,
                    random.choice([1]),
                    bound=1,
                    start_cell=temperature_source,
                    weight_parameter="pole_distance_multiplier",
                )

        if self.get_tuning("smooth_temperature"):
            while self.smooth(
                constants.TEMPERATURE
            ):  # Continue running smooth until it doesn't make any more changes
                pass
        self.bound(
            constants.TEMPERATURE,
            default_temperature - self.get_tuning("final_temperature_variations")[0],
            default_temperature + self.get_tuning("final_temperature_variations")[1],
        )

    def generate_roughness(self) -> None:
        """
        Description:
            Randomly generates roughness
        Input:
            None
        Output:
            None
        """
        if self.get_tuning("earth_preset"):
            num_worms = self.get_tuning("earth_roughness_multiplier")
        elif self.get_tuning("mars_preset"):
            num_worms = self.get_tuning("mars_roughness_multiplier")
        else:
            num_worms = random.randrange(
                self.get_tuning("min_roughness_multiplier"),
                self.get_tuning("max_roughness_multiplier") + 1,
            )

        for i in range(num_worms):
            min_length = (
                random.randrange(
                    self.get_tuning("min_roughness_worm_multiplier"),
                    self.get_tuning("med_roughness_worm_multiplier"),
                )
                * self.area
            ) // 25**2
            max_length = (
                random.randrange(
                    self.get_tuning("med_roughness_worm_multiplier"),
                    self.get_tuning("max_roughness_worm_multiplier"),
                )
                * self.area
            ) // 25**2
            self.make_random_terrain_parameter_worm(
                min_length,
                max_length,
                constants.ROUGHNESS,
                1,
                bound=self.get_tuning("roughness_worm_bound"),
            )

    def generate_water(self) -> None:
        """
        Description:
            Randomly generates water
        Input:
            None
        Output:
            None
        """
        total_water = (self.world_handler.water_multiplier * self.area) // 10

        for water in range(total_water):
            self.place_water()

    def place_water(self, frozen_bound=1) -> None:
        """
        Description:
            Places 1 unit of water on the map, depending on altitude and temperature
        Input:
            int frozen_bound: Temperature below which water will "freeze" -
        Output:
            None
        """
        best_frozen = None
        best_liquid = None
        for candidate in self.sample(
            k=round(
                self.get_tuning("water_placement_candidates")
                * (self.coordinate_width**2)
                / (25**2)
            )
        ):
            if candidate.get_parameter(constants.WATER) < 6:
                if (
                    candidate.get_parameter(constants.TEMPERATURE) <= frozen_bound
                ):  # Water can go to coldest freezing location
                    if best_frozen == None or candidate.get_parameter(
                        constants.TEMPERATURE
                    ) < best_frozen.get_parameter(constants.TEMPERATURE):
                        best_frozen = candidate
                else:
                    if best_liquid == None or candidate.get_parameter(
                        constants.ALTITUDE
                    ) < best_liquid.get_parameter(constants.ALTITUDE):
                        best_liquid = candidate

        if best_frozen and best_liquid:
            choice = random.choices(
                [best_frozen, best_liquid],
                weights=[
                    abs(
                        (2 - best_frozen.get_parameter(constants.TEMPERATURE))
                    ),  # Weight frozen placement for low temperature
                    abs(
                        10 - best_liquid.get_parameter(constants.ALTITUDE)
                    ),  # Weight liquid placement for low altitude
                ],
                k=1,
            )[0]
            if choice == best_frozen:
                best_liquid = None
            else:
                best_frozen = None

        if best_frozen:
            best_frozen.change_parameter(constants.WATER, 1)
        elif best_liquid:
            best_liquid.change_parameter(constants.WATER, 1)
            best_liquid.terrain_handler.flow()

    def generate_soil(self) -> None:
        """
        Description:
            Randomly generates soil
        Input:
            None
        Output:
            None
        """
        if self.get_tuning("earth_preset"):
            for cell in self.get_flat_cell_list():
                cell.set_parameter(constants.SOIL, random.randrange(1, 7))
        else:
            for cell in self.get_flat_cell_list():
                cell.set_parameter(constants.SOIL, random.randrange(1, 4))

        num_worms = random.randrange(
            self.get_tuning("min_soil_multiplier"),
            self.get_tuning("max_soil_multiplier") + 1,
        )
        for i in range(num_worms):
            min_length = (
                random.randrange(
                    self.get_tuning("min_soil_worm_multiplier"),
                    self.get_tuning("med_soil_worm_multiplier"),
                )
                * self.area
            ) // 25**2
            max_length = (
                random.randrange(
                    self.get_tuning("med_soil_worm_multiplier"),
                    self.get_tuning("max_soil_worm_multiplier"),
                )
                * self.area
            ) // 25**2
            self.make_random_terrain_parameter_worm(
                min_length,
                max_length,
                constants.SOIL,
                random.choice([-1, 1]),
                bound=1,
            )

        self.bound(
            constants.SOIL,
            1,
            3,
        )

    def generate_vegetation(self) -> None:
        """
        Description:
            Randomly generates vegetation
        Input:
            None
        Output:
            None
        """
        if self.get_tuning("earth_preset"):
            for cell in self.get_flat_cell_list():
                if cell.get_parameter(constants.TEMPERATURE) > 1:
                    if cell.get_parameter(constants.WATER) < 5:
                        cell.set_parameter(
                            constants.VEGETATION,
                            cell.get_parameter(constants.WATER) * 3 - 1,
                        )
                    else:
                        cell.set_parameter(
                            constants.VEGETATION,
                            cell.get_parameter(constants.ALTITUDE) + 1,
                        )
            self.smooth(constants.VEGETATION)
        else:
            for cell in self.get_flat_cell_list():
                cell.set_parameter(constants.VEGETATION, 1)

    def generate_terrain_parameters(self):
        """
        Description:
            Randomly sets terrain parameters for each cell
        Input:
            None
        Output:
            None
        """
        self.generate_altitude()
        self.generate_roughness()
        self.generate_temperature()
        self.generate_water()
        self.generate_soil()
        self.generate_vegetation()

    def bound(self, parameter: str, minimum: int, maximum: int):
        """
        Description:
            Bounds the inputted parameter to the inputted minimum and maximum values
        Input:
            string parameter: Parameter to bound
            int minimum: Minimum value to bound the parameter to
            int maximum: Maximum value to bound the parameter to
        Output:
            None
        """
        for cell in self.get_flat_cell_list():
            cell.set_parameter(
                parameter,
                max(
                    min(cell.get_parameter(parameter), maximum),
                    minimum,
                ),
            )

    def smooth(self, parameter: str, direction: str = None) -> bool:
        """
        Description:
            Smooths the inputted parameter across the grid - if it is more than 1 away from any neighbors, change to be closer to neighbors
        Input:
            string parameter: Parameter to smooth
            string direction: Up, down, or None - indicates direction of smoothing
        Output:
            bool: Returns True if any cells were smoothed (indicates that smoothing should continue), otherwise False
        """
        flat_cell_list = list(self.get_flat_cell_list())
        random.shuffle(flat_cell_list)
        smoothed = False
        for cell in flat_cell_list:
            for adjacent_cell in cell.adjacent_list:
                if (
                    abs(
                        adjacent_cell.get_parameter(parameter)
                        - cell.get_parameter(parameter)
                    )
                    >= 2
                ):
                    if cell.get_parameter(parameter) > adjacent_cell.get_parameter(
                        parameter
                    ):
                        if direction != "up":
                            cell.change_parameter(parameter, -1)
                    else:
                        if direction != "down":
                            cell.change_parameter(parameter, 1)
                    smoothed = True
        return smoothed

    def find_average(self, parameter):
        """
        Description:
            Calculates and returns the average value of the inputted parameter for all cells in the grid
        Input:
            string parameter: Parameter to average
        Output:
            float: Returns the average value of the parameter
        """
        return sum(
            [cell.get_parameter(parameter) for cell in self.get_flat_cell_list()]
        ) / (self.coordinate_width * self.coordinate_height)

    def make_random_terrain_parameter_worm(
        self,
        min_len: int,
        max_len: int,
        parameter: str,
        change: int,
        bound: int = 0,
        set: bool = False,
        start_cell: cell = None,
        weight_parameter: str = None,
    ):
        """
        Description:
            Chooses a random terrain from the inputted list and fills a random length chain of adjacent grid cells with the chosen terrain. Can go to the same cell multiple times
        Input:
            int min_len: Minimum number of cells whose parameter can be changed
            int max_len: Maximum number of cells whose parameter can be changed, inclusive
            str parameter: Parameter to change
            int change: Amount to change the parameter by
            bool capped: True if the parameter change should be limited in how far it can go from starting cell's original value, otherwise False
            bool set: True if the parameter should be set to the change + original, False if it should be changed with each pass
            cell start_cell: Cell to start the worm from, otherwise a random cell is chosen
            str weight_parameter: Terrain handler parameter to weight direction selection by, if any
        Output:
            None
        """
        if start_cell:
            start_x, start_y = start_cell.x, start_cell.y
        else:
            start_x = random.randrange(0, self.coordinate_width)
            start_y = random.randrange(0, self.coordinate_height)

        current_x = start_x
        current_y = start_y
        worm_length = random.randrange(min_len, max_len + 1)

        original_value = self.find_cell(current_x, current_y).get_parameter(parameter)
        upper_bound = original_value + bound
        lower_bound = original_value - bound

        counter = 0
        while counter != worm_length:
            current_cell = self.find_cell(current_x, current_y)
            if set:
                resulting_value = original_value + change
            else:
                resulting_value = current_cell.get_parameter(parameter) + change

            if bound == 0 or (
                resulting_value <= upper_bound and resulting_value >= lower_bound
            ):
                current_cell.change_parameter(parameter, change)
            counter = counter + 1
            if weight_parameter:
                selected_cell = self.parameter_weighted_sample(
                    weight_parameter, restrict_to=current_cell.adjacent_list, k=1
                )[0]
                current_x, current_y = selected_cell.x, selected_cell.y
            else:
                direction = random.randrange(1, 5)  # 1 north, 2 east, 3 south, 4 west
                if direction == 3:
                    current_y = (current_y + 1) % self.coordinate_height
                elif direction == 2:
                    current_x = (current_x + 1) % self.coordinate_width
                elif direction == 1:
                    current_y = (current_y - 1) % self.coordinate_height
                elif direction == 4:
                    current_x = (current_x - 1) % self.coordinate_width

    def generate_terrain_features(self):
        """
        Description:
            Randomly place features in each tile, based on terrain
        Input:
            None
        Output:
            None
        """
        for terrain_feature_type in status.terrain_feature_types:
            for cell in self.get_flat_cell_list():
                if status.terrain_feature_types[terrain_feature_type].allow_place(cell):
                    cell.terrain_handler.terrain_features[terrain_feature_type] = {
                        "feature_type": terrain_feature_type
                    }
                    cell.tile.update_image_bundle()

    def x_distance(self, cell1, cell2):
        """
        Description:
            Calculates and returns the x distance between two cells
        Input:
            cell cell1: First cell
            cell cell2: Second cell
        Output:
            int: Returns the x distance between the two cells
        """
        return min(
            abs(cell1.x - cell2.x),
            abs(cell1.x - (cell2.x + self.coordinate_width)),
            abs(cell1.x - (cell2.x - self.coordinate_width)),
        )

    def y_distance(self, cell1, cell2):
        """
        Description:
            Calculates and returns the y distance between two cells
        Input:
            cell cell1: First cell
            cell cell2: Second cell
        Output:
            int: Returns the y distance between the two cells
        """
        return min(
            abs(cell1.y - cell2.y),
            abs(cell1.y - (cell2.y + self.coordinate_height)),
            abs(cell1.y - (cell2.y - self.coordinate_height)),
        )

    def distance(self, cell1, cell2):
        """
        Description:
            Calculates and returns the distance between two cells
        Input:
            cell cell1: First cell
            cell cell2: Second cell
        Output:
            int: Returns the distance between the two cells
        """
        return (
            self.x_distance(cell1, cell2) ** 2 + self.y_distance(cell1, cell2) ** 2
        ) ** 0.5

    def cell_distance(self, cell1, cell2):
        """
        Description:
            Calculates and returns the non-diagonal distance between two cells
        Input:
            cell cell1: First cell
            cell cell2: Second cell
        Output: int: Returns the non-diagonal distance between the two cells
        """
        return self.x_distance(cell1, cell2) + self.y_distance(cell1, cell2)

    def create_resource_list_dict(self):
        """
        Description:
            Creates and returns dictionary containing entries for each terrain type with the frequency of each resource type in that terrain
        Input:
            None
        Output:
            dictionary: Returns a dictionary in the format
                {'savannah': [('none', 140), ('diamond', 142)]}
                for resource_frequencies.json {'savannah': {'none': 140, 'diamond': 2}}
        """
        file = open("configuration/resource_frequencies.json")
        resource_frequencies = json.load(file)
        resource_list_dict = {}
        for current_terrain in resource_frequencies:
            resource_list_dict[current_terrain] = []
            total_frequency = 0
            for current_resource in resource_frequencies[current_terrain]:
                total_frequency += resource_frequencies[current_terrain][
                    current_resource
                ]
                resource_list_dict[current_terrain].append(
                    (current_resource, total_frequency)
                )
        file.close()
        return resource_list_dict

    def make_random_terrain_worm(self, min_len, max_len, possible_terrains):
        """
        Description:
            Chooses a random terrain from the inputted list and fills a random length chain of adjacent grid cells with the chosen terrain. Can go to the same cell multiple times
        Input:
            int min_len: minimum number of cells whose terrain can be changed
            int max_len: maximum number of cells whose terrain can be changed, inclusive
            string list possible_terrains: list of all terrain types that could randomly spawn, like 'swamp'
        Output:
            None
        """
        start_x = random.randrange(0, self.coordinate_width)
        start_y = random.randrange(0, self.coordinate_height)
        current_x = start_x
        current_y = start_y
        worm_length = random.randrange(min_len, max_len + 1)
        terrain = random.choice(possible_terrains)
        self.find_cell(current_x, current_y).terrain_handler.set_terrain(terrain)
        counter = 0
        while not counter == worm_length:
            counter = counter + 1
            direction = random.randrange(1, 5)  # 1 north, 2 east, 3 south, 4 west
            if direction == 3:
                current_y = (current_y + 1) % self.coordinate_height
            elif direction == 2:
                current_x = (current_x + 1) % self.coordinate_width
            elif direction == 1:
                current_y = (current_y - 1) % self.coordinate_height
            elif direction == 4:
                current_x = (current_x - 1) % self.coordinate_width
            self.find_cell(current_x, current_y).terrain_handler.set_terrain(terrain)

    def parameter_weighted_sample(
        self, parameter: str, restrict_to: List[cell] = None, k: int = 1
    ) -> List:
        """
        Description:
            Randomly samples k cells from the grid, with the probability of a cell being chosen being proportional to its value of the inputted parameter
        Input:
            string parameter: Parameter to sample by
            int k: Number of cells to sample
        Output:
            list: Returns a list of k cells
        """
        if not restrict_to:
            cell_list = self.get_flat_cell_list()
            cell_list = [cell for cell in cell_list]  # Converts from chain to list
        else:
            cell_list = restrict_to

        if parameter in constants.terrain_parameters:
            weight_list = [cell.get_parameter(parameter) for cell in cell_list]
        else:
            weight_list = [
                getattr(cell.terrain_handler, parameter) for cell in cell_list
            ]
        return random.choices(list(cell_list), weights=weight_list, k=k)

    def sample(self, k: int = 1):
        """
        Description:
            Randomly samples k cells from the grid
        Input:
            int k: Number of cells to sample
        Output:
            list: Returns a list of k cells
        """
        return random.choices(list(self.get_flat_cell_list()), k=k)

    def generate_poles_and_equator(self):
        """
        Description:
            Generates the poles and equator for the world grid
        Input:
            None
        Output:
            None
        """
        self.find_cell(0, 0).terrain_handler.add_terrain_feature(
            {
                "feature_type": "north pole",
            }
        )

        max_distance = 0

        south_pole = None
        for cell in self.get_flat_cell_list():
            if self.distance(cell, status.north_pole) > max_distance:
                max_distance = self.distance(cell, status.north_pole)
                south_pole = cell
        south_pole.terrain_handler.add_terrain_feature(
            {
                "feature_type": "south pole",
            }
        )

        equatorial_distance = self.distance(status.north_pole, status.south_pole) / 2
        for (
            cell
        ) in (
            self.get_flat_cell_list()
        ):  # Results in clean equator lines in odd-sized planets
            north_pole_distance = self.distance(cell, status.north_pole)
            south_pole_distance = self.distance(cell, status.south_pole)
            cell.terrain_handler.pole_distance_multiplier = max(
                min(
                    min(north_pole_distance, south_pole_distance) / equatorial_distance,
                    1.0,
                ),
                0.1,
            )
            cell.terrain_handler.inverse_pole_distance_multiplier = max(
                1 - cell.terrain_handler.pole_distance_multiplier, 0.1
            )
            cell.terrain_handler.north_pole_distance_multiplier = (
                max(min(1.0 - (north_pole_distance / equatorial_distance), 1.0), 0.1)
                ** 2
            )
            cell.terrain_handler.south_pole_distance_multiplier = (
                max(min(1.0 - (south_pole_distance / equatorial_distance), 1.0), 0.1)
                ** 2
            )

            if (
                (south_pole_distance == north_pole_distance)
                or (
                    cell.y > cell.x
                    and abs(south_pole_distance - north_pole_distance) <= 1
                    and south_pole_distance < north_pole_distance
                )
                or (
                    cell.y < cell.x
                    and abs(south_pole_distance - north_pole_distance) <= 1
                    and south_pole_distance > north_pole_distance
                )
            ):
                cell.terrain_handler.add_terrain_feature(
                    {
                        "feature_type": "equator",
                    }
                )

            if (
                self.cell_distance(status.south_pole, cell)
                == self.coordinate_width // 3
            ):
                cell.terrain_handler.add_terrain_feature(
                    {
                        "feature_type": "southern tropic",
                    }
                )

            if (
                self.cell_distance(status.north_pole, cell)
                == self.coordinate_width // 3
            ):
                cell.terrain_handler.add_terrain_feature(
                    {
                        "feature_type": "northern tropic",
                    }
                )


def create(from_save: bool, grid_type: str, input_dict: Dict[str, any] = None) -> grid:
    """
    Description:
    """
    if not input_dict:
        input_dict = {}

    input_dict.update(
        {
            "modes": [constants.STRATEGIC_MODE],
            "parent_collection": status.grids_collection,
            "grid_type": grid_type,
        }
    )

    if grid_type == "strategic_map_grid":
        if constants.effect_manager.effect_active("large_map"):
            map_size_list = constants.terrain_manager.get_tuning("large_map_sizes")
        elif constants.effect_manager.effect_active("tiny_map"):
            map_size_list = constants.terrain_manager.get_tuning("tiny_map_sizes")
        else:
            map_size_list = constants.terrain_manager.get_tuning("map_sizes")
        map_size = input_dict.get("map_size", random.choice(map_size_list))
        if constants.terrain_manager.get_tuning("earth_preset"):
            map_size = map_size_list[3]
        elif constants.terrain_manager.get_tuning("mars_preset"):
            map_size = map_size_list[1]
        input_dict.update(
            {
                "modes": [],  # Acts as source of truth for mini grids, but this grid is not directly shown
                "coordinates": scaling.scale_coordinates(320, 0),
                "width": scaling.scale_width(constants.strategic_map_pixel_width),
                "height": scaling.scale_height(constants.strategic_map_pixel_height),
                "coordinate_width": map_size,
                "coordinate_height": map_size,
                "grid_line_width": 2,
            }
        )
        return_grid = world_grid(from_save, input_dict)

    elif grid_type == "scrolling_strategic_map_grid":
        input_dict.update(
            {
                "coordinates": scaling.scale_coordinates(320, 0),
                "width": scaling.scale_width(constants.strategic_map_pixel_width),
                "height": scaling.scale_height(constants.strategic_map_pixel_height),
                "coordinate_size": status.strategic_map_grid.coordinate_width,
                "grid_line_width": 2,
                "attached_grid": status.strategic_map_grid,
            }
        )
        return_grid = mini_grid(from_save, input_dict)

    elif grid_type == "minimap_grid":
        input_dict.update(
            {
                "coordinates": scaling.scale_coordinates(
                    0, -1 * (constants.minimap_grid_pixel_height + 25)
                ),
                "width": scaling.scale_width(constants.minimap_grid_pixel_width),
                "height": scaling.scale_height(constants.minimap_grid_pixel_height),
                "coordinate_size": constants.minimap_grid_coordinate_size,
                "external_line_color": "bright red",
                "attached_grid": status.strategic_map_grid,
            }
        )
        return_grid = mini_grid(from_save, input_dict)

    elif grid_type in constants.abstract_grid_type_list:
        input_dict.update(
            {
                "coordinates": scaling.scale_coordinates(
                    getattr(constants, grid_type + "_x_offset"),
                    getattr(constants, grid_type + "_y_offset"),
                ),
                # Like (earth_grid_x_offset, earth_grid_y_offset)
                "width": scaling.scale_width(120),
                "height": scaling.scale_height(120),
            }
        )
        if grid_type == "earth_grid":
            input_dict["modes"].append(constants.EARTH_MODE)

        input_dict["name"] = (
            grid_type[:-5].replace("_", " ").capitalize()
        )  # Replaces earth_grid with Earth
        return_grid = abstract_grid(from_save, input_dict)

    setattr(status, grid_type, return_grid)
    return return_grid
