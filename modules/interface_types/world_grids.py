# Contains functionality for world grids and creating grid objects

import random
import json
import math
import pygame
from typing import Dict, List, Tuple
from modules.interface_types.grids import grid, mini_grid, abstract_grid
from modules.interface_types.cells import cell
from modules.util import scaling, actor_utility
from modules.constructs import world_handlers, locations
from modules.constants import constants, status, flags


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
        self.world_handler = world_handlers.world_handler(
            self,
            from_save,
            input_dict.get("world_handler", {"grid_type": input_dict["grid_type"]}),
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
                cell.location.set_resource(
                    status.item_types.get(cell.save_dict["resource"], None)
                )
        else:
            self.generate_poles_and_equator()
            self.world_handler.update_clouds(estimated_temperature=True)
            self.generate_terrain_parameters()
            self.generate_terrain_features()
            self.world_handler.update_sky_color(
                set_initial_offset=True, update_water=True
            )
            self.world_handler.update_clouds()
            for i in range(5):  # Simulate time passing until equilibrium is reached
                self.world_handler.update_target_average_temperature(update_albedo=True)
                self.world_handler.change_to_temperature_target()

    def generate_altitude(self) -> None:
        """
        Description:
            Randomly generates altitude
        Input:
            None
        Output:
            None
        """
        if constants.effect_manager.effect_active("map_customization"):
            default_altitude = 2
        else:
            default_altitude = 0
        for location in self.world_handler.get_flat_location_list():
            location.set_parameter(constants.ALTITUDE, default_altitude)

        if constants.effect_manager.effect_active("map_customization"):
            return

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
            Nones
        """
        self.world_handler.update_target_average_temperature(
            estimate_water_vapor=True, update_albedo=True
        )
        default_temperature = round(self.world_handler.average_temperature)
        for location in self.world_handler.get_flat_location_list():
            location.set_parameter(
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
                        round(min_length * pole_worm_length_multiplier),
                        round(max_length * pole_worm_length_multiplier),
                        constants.TEMPERATURE,
                        -1,
                        bound=1,
                        start_location=temperature_source,
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
                    start_location=temperature_source,
                    weight_parameter="pole_distance_multiplier",
                )

        self.world_handler.update_target_average_temperature(
            estimate_water_vapor=True, update_albedo=True
        )
        self.world_handler.change_to_temperature_target(estimate_water_vapor=True)

    def generate_roughness(self) -> None:
        """
        Description:
            Randomly generates roughness
        Input:
            None
        Output:
            None
        """
        if constants.effect_manager.effect_active("map_customization"):
            return
        if constants.effect_manager.effect_active("earth_preset"):
            num_worms = self.get_tuning("earth_roughness_multiplier")
        elif constants.effect_manager.effect_active("mars_preset"):
            num_worms = self.get_tuning("mars_roughness_multiplier")
        elif constants.effect_manager.effect_active("venus_preset"):
            num_worms = self.get_tuning("venus_roughness_multiplier")
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
            Randomly generates water, placing enough water to reach the generated target average
                Total water may be less than target average if repeatedly attempting to place in full tiles, or if radiation removes some of the placed water
        Input:
            None
        Output:
            None
        """
        for _ in range(
            round(self.world_handler.average_water_target * self.world_handler.size)
        ):
            self.place_water(radiation_effect=True)
        if constants.effect_manager.effect_active("map_customization"):
            attempts = 0
            while attempts < 10000 and not self.find_average(constants.WATER) == 5.0:
                self.place_water(radiation_effect=True)
                attempts += 1
        self.world_handler.update_target_average_temperature(update_albedo=True)
        self.world_handler.change_to_temperature_target()
        for location in self.world_handler.get_flat_location_list():
            location.local_weather_offset = (
                location.expected_temperature_offset + random.uniform(-0.4, 0.4)
            )

    def place_water(
        self,
        frozen_bound=0,
        radiation_effect: bool = False,
        update_display: bool = False,
        repeat_on_fail: bool = False,
    ) -> None:
        """
        Description:
            Places 1 unit of water on the map, depending on altitude and temperature
        Input:
            int frozen_bound: Temperature below which water will "freeze"
        Output:
            None
        """
        best_frozen = None
        best_liquid = None
        best_gas = None
        for candidate in self.world_handler.sample(
            k=round(
                self.get_tuning("water_placement_candidates")
                * (self.coordinate_width**2)
                / (20**2)
            )
        ):
            if (
                candidate.get_parameter(constants.WATER) < 5
                and candidate.get_parameter(constants.TEMPERATURE) > frozen_bound - 1
            ):
                if candidate.get_parameter(constants.TEMPERATURE) >= self.get_tuning(
                    "water_boiling_point"
                ):
                    best_gas = candidate
                else:
                    if best_liquid == None or candidate.get_parameter(
                        constants.ALTITUDE
                    ) < best_liquid.get_parameter(constants.ALTITUDE):
                        best_liquid = candidate
        for candidate in self.world_handler.sample(
            k=round(
                self.get_tuning("ice_placement_candidates")
                * (self.coordinate_width**2)
                / (20**2)
            )
        ):
            if candidate.get_parameter(constants.WATER) < 5:
                if (
                    candidate.get_parameter(constants.TEMPERATURE) <= frozen_bound - 1
                ):  # Water can go to coldest freezing location
                    if best_frozen == None or candidate.get_parameter(
                        constants.TEMPERATURE
                    ) < best_frozen.get_parameter(constants.TEMPERATURE):
                        best_frozen = candidate
        if best_frozen == None and best_liquid == None and best_gas == None:
            return
        choice = random.choices(
            [best_frozen, best_liquid, best_gas],
            weights=[
                (
                    abs((1 - best_frozen.get_parameter(constants.TEMPERATURE)))
                    if best_frozen
                    else 0
                ),  # Weight frozen placement for low temperature
                (
                    abs(16 - best_liquid.get_parameter(constants.ALTITUDE))
                    if best_liquid
                    else 0
                ),  # Weight liquid placement for low altitude
                13.5 if best_gas else 0,
            ],
            k=1,
        )[0]
        if radiation_effect:
            radiation_effect = max(
                0,
                self.world_handler.get_parameter(constants.RADIATION)
                - self.world_handler.get_parameter(constants.MAGNETIC_FIELD),
            )
        else:
            radiation_effect = 0
        change = 1
        if not (
            self.world_handler.get_pressure_ratio() < 0.05
            and choice.get_parameter(constants.TEMPERATURE)
            >= self.get_tuning("water_freezing_point")
        ):
            # If insufficient pressure, any evaporated water disappears
            if choice.get_parameter(constants.TEMPERATURE) <= frozen_bound - 1:
                # If during setup
                if choice.get_parameter(constants.TEMPERATURE) >= self.get_tuning(
                    "water_freezing_point"
                ):  # Lose most water if sometimes above freezing
                    if radiation_effect >= 3:
                        if random.randrange(1, 13) >= 2:
                            # choice.change_parameter(constants.WATER, -1)
                            change = 0
                    elif radiation_effect >= 1:
                        if random.randrange(1, 13) >= 4:
                            # choice.change_parameter(constants.WATER, -1)
                            change = 0
                # If far below freezing, retain water regardless of radiation
                if change != 0:
                    choice.change_parameter(
                        constants.WATER, change, update_display=update_display
                    )
            else:
                # If during setup
                if (
                    radiation_effect >= 3
                ):  # Lose almost all water if consistently above freezing
                    if random.randrange(1, 13) >= 2:
                        change = 0
                elif (
                    radiation_effect >= 1
                ):  # Lose most water if consistently above freezing
                    if random.randrange(1, 13) >= 4:
                        change = 0
                if change != 0:
                    choice.change_parameter(
                        constants.WATER, change, update_display=update_display
                    )
                    choice.flow()
        if change == 0 and repeat_on_fail:
            self.place_water(
                radiation_effect=radiation_effect,
                update_display=update_display,
                repeat_on_fail=repeat_on_fail,
            )

    def remove_water(self, update_display: bool = False) -> None:
        """
        Description:
            Removes 1 unit of water from the map, depending on altitude and temperature
        Input:
            None
        Output:
            None
        """
        water_cells = [
            cell
            for cell in self.get_flat_cell_list()
            if cell.get_parameter(constants.WATER) > 0
        ]
        if water_cells:
            random.choices(
                water_cells,
                weights=[cell.get_parameter(constants.WATER) for cell in water_cells],
                k=1,
            )[0].change_parameter(constants.WATER, -1, update_display=update_display)

    def generate_soil(self) -> None:
        """
        Description:
            Randomly generates soil
        Input:
            None
        Output:
            None
        """
        if constants.effect_manager.effect_active("map_customization"):
            return
        if constants.effect_manager.effect_active("earth_preset"):
            for location in self.world_handler.get_flat_location_list():
                location.set_parameter(constants.SOIL, random.randrange(0, 6))
        else:
            for location in self.world_handler.get_flat_location_list():
                location.set_parameter(constants.SOIL, random.randrange(0, 3))

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
            0,
            2,
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
        if constants.effect_manager.effect_active("map_customization"):
            return
        if constants.effect_manager.effect_active("earth_preset"):
            for current_location in self.world_handler.get_flat_location_list():
                if current_location.get_parameter(constants.TEMPERATURE) > 0:
                    if current_location.get_parameter(constants.WATER) < 4:
                        current_location.set_parameter(
                            constants.VEGETATION,
                            current_location.get_parameter(constants.WATER) * 3 + 2,
                        )
                    else:
                        current_location.set_parameter(
                            constants.VEGETATION,
                            current_location.get_parameter(constants.ALTITUDE) + 2,
                        )
            self.smooth(constants.VEGETATION)
        else:
            for current_location in self.world_handler.get_flat_location_list():
                current_location.set_parameter(constants.VEGETATION, 0)

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
        for current_location in self.world_handler.get_flat_location_list():
            current_location.set_parameter(
                parameter,
                max(
                    min(current_location.get_parameter(parameter), maximum),
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
            bool: Returns True if any locations were smoothed (indicates that smoothing should continue), otherwise False
        """
        flat_location_list = list(self.world_handler.get_flat_location_list())
        random.shuffle(flat_location_list)
        smoothed = False
        for current_location in flat_location_list:
            for adjacent_location in current_location.adjacent_list:
                if (
                    abs(
                        adjacent_location.get_parameter(parameter)
                        - current_location.get_parameter(parameter)
                    )
                    >= 2
                ):
                    if current_location.get_parameter(
                        parameter
                    ) > adjacent_location.get_parameter(parameter):
                        if direction != "up":
                            current_location.change_parameter(
                                parameter, -1, update_display=False
                            )
                    else:
                        if direction != "down":
                            current_location.change_parameter(
                                parameter, 1, update_display=False
                            )
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

    def warm(self) -> None:
        """
        Description:
            Warms the grid, increasing temperature
                Selects the cell with the furthest temperature below its expected temperature
        Input:
            None
        Output:
            None
        """
        self.place_temperature(change=1, bound=11, choice_function=min)

    def cool(self) -> None:
        """
        Description:
            Cools the grid, decreasing temperature
                Selects the cell with the furthest temperature above its expected temperature
        Input:
            None
        Output:
            None
        """
        self.place_temperature(change=-1, bound=-6, choice_function=max)

    def place_temperature(
        self, change: int, bound: int, choice_function: callable
    ) -> None:
        """
        Description:
            Changes the temperature of the grid by the inputted amount, selecting the cell that most differs from its expected temperature
        Input:
            int change: Amount to change the temperature by
            int bound: Maximum temperature value in the direction being changed
            callable choice_function: Function to determine which offset to choose - min or max
        Output:
            None
        """
        offsets = [
            (
                location,
                location.expected_temperature_offset + location.local_weather_offset,
            )
            for location in self.world_handler.get_flat_location_list()
            if not location.get_parameter(constants.TEMPERATURE) == bound
        ]
        if offsets:
            outlier = choice_function(offsets, key=lambda x: x[1])[
                0
            ]  # Choose baesd on min or max expected temperature offset
            outlier.change_parameter(
                constants.TEMPERATURE, change, update_display=False
            )

    def make_random_terrain_parameter_worm(
        self,
        min_len: int,
        max_len: int,
        parameter: str,
        change: int,
        bound: int = 0,
        set: bool = False,
        start_location: locations.location = None,
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
            cell start_location: Location to start the worm from, otherwise a random location is chosen
            str weight_parameter: Location parameter to weight direction selection by, if any
        Output:
            None
        """
        if start_location:
            start_x, start_y = start_location.x, start_location.y
        else:
            start_x = random.randrange(0, self.coordinate_width)
            start_y = random.randrange(0, self.coordinate_height)

        current_x = start_x
        current_y = start_y
        worm_length = random.randrange(min_len, max_len + 1)

        original_value = self.world_handler.find_location(
            current_x, current_y
        ).get_parameter(parameter)
        upper_bound = original_value + bound
        lower_bound = original_value - bound

        counter = 0
        while counter != worm_length:
            current_location = self.world_handler.find_location(current_x, current_y)
            if set:
                resulting_value = original_value + change
            else:
                resulting_value = current_location.get_parameter(parameter) + change

            if bound == 0 or (
                resulting_value <= upper_bound and resulting_value >= lower_bound
            ):
                current_location.change_parameter(
                    parameter, change, update_display=False
                )
            counter = counter + 1
            if weight_parameter:
                selected_location = self.parameter_weighted_sample(
                    weight_parameter, restrict_to=current_location.adjacent_list, k=1
                )[0]
                current_x, current_y = selected_location.x, selected_location.y
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
            for location in self.world_handler.get_flat_location_list():
                if status.terrain_feature_types[terrain_feature_type].allow_place(
                    location
                ):
                    location.terrain_features[terrain_feature_type] = {
                        "feature_type": terrain_feature_type
                    }
                    for cell in location.attached_cells:
                        cell.tile.update_image_bundle()

    def x_distance(self, location1, location2):
        """
        Description:
            Calculates and returns the x distance between two locations
        Input:
            location location1: First location
            location location2: Second location
        Output:
            int: Returns the x distance between the two locations
        """
        return min(
            abs(location1.x - location2.x),
            abs(location1.x - (location2.x + self.coordinate_width)),
            abs(location1.x - (location2.x - self.coordinate_width)),
        )

    def x_distance_coords(self, x1, x2):
        """
        Description:
            Calculates and returns the x distance between two x coordinates
        Input:
            int x1: First x coordinate
            int x2: Second x coordinate
        Output:
            int: Returns the x distance between the two x coordinates
        """
        return min(
            abs(x1 - x2),
            abs(x1 - (x2 + self.coordinate_width)),
            abs(x1 - (x2 - self.coordinate_width)),
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

    def y_distance_coords(self, y1, y2):
        """
        Description:
            Calculates and returns the y distance between two y coordinates
        Input:
            int y1: First y coordinate
            int y2: Second y coordinate
        Output:
            int: Returns the y distance between the two y coordinates
        """
        return min(
            abs(y1 - y2),
            abs(y1 - (y2 + self.coordinate_height)),
            abs(y1 - (y2 - self.coordinate_height)),
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

    def location_distance(self, location1, location2):
        """
        Description:
            Calculates and returns the non-diagonal distance between two cells
        Input:
            location location1: First location
            location location2: Second location
        Output: int: Returns the non-diagonal distance between the two cells
        """
        return self.x_distance(location1, location2) + self.y_distance(
            location1, location2
        )

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
        self.world_handler.find_location(current_x, current_y).set_terrain(terrain)
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
            self.world_handler.find_location(current_x, current_y).set_terrain(terrain)

    def parameter_weighted_sample(
        self, parameter: str, restrict_to: list = None, k: int = 1
    ) -> List:
        """
        Description:
            Randomly samples k locations from the grid, with the probability of a cell being chosen being proportional to its value of the inputted parameter
        Input:
            string parameter: Parameter to sample by
            location list restrict_to: List of locations to sample from, otherwise all locations are sampled
            int k: Number of locations to sample
        Output:
            list: Returns a list of k locations
        """
        if not restrict_to:
            location_list = list(self.world_handler.get_flat_location_list())
        else:
            location_list = restrict_to

        if parameter in constants.terrain_parameters:
            weight_list = [
                location.get_parameter(parameter) for location in location_list
            ]
        else:
            weight_list = [getattr(location, parameter) for location in location_list]
        return random.choices(location_list, weights=weight_list, k=k)

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
        self.world_handler.find_location(0, 0).add_terrain_feature(
            {
                "feature_type": "north pole",
            }
        )

        max_distance = 0

        south_pole = None
        for location in self.world_handler.get_flat_location_list():
            if self.distance(location, status.north_pole) > max_distance:
                max_distance = self.distance(location, status.north_pole)
                south_pole = location

        south_pole.add_terrain_feature(
            {
                "feature_type": "south pole",
            }
        )

        equatorial_distance = self.distance(status.north_pole, status.south_pole) / 2
        for (
            location
        ) in (
            self.world_handler.get_flat_location_list()
        ):  # Results in clean equator lines in odd-sized planets
            north_pole_distance = self.distance(location, status.north_pole)
            south_pole_distance = self.distance(location, status.south_pole)
            location.pole_distance_multiplier = max(
                min(
                    min(north_pole_distance, south_pole_distance) / equatorial_distance,
                    1.0,
                ),
                0.1,
            )
            location.inverse_pole_distance_multiplier = max(
                1 - location.pole_distance_multiplier, 0.1
            )
            location.north_pole_distance_multiplier = (
                max(min(1.0 - (north_pole_distance / equatorial_distance), 1.0), 0.1)
                ** 2
            )
            location.south_pole_distance_multiplier = (
                max(min(1.0 - (south_pole_distance / equatorial_distance), 1.0), 0.1)
                ** 2
            )

            if (
                (south_pole_distance == north_pole_distance)
                or (
                    location.y > location.x
                    and abs(south_pole_distance - north_pole_distance) <= 1
                    and south_pole_distance < north_pole_distance
                )
                or (
                    location.y < location.x
                    and abs(south_pole_distance - north_pole_distance) <= 1
                    and south_pole_distance > north_pole_distance
                )
            ):
                location.add_terrain_feature(
                    {
                        "feature_type": "equator",
                    }
                )

            if (
                self.location_distance(status.south_pole, location)
                == self.coordinate_width // 3
            ):
                location.add_terrain_feature(
                    {
                        "feature_type": "southern tropic",
                    }
                )

            if (
                self.location_distance(status.north_pole, location)
                == self.coordinate_width // 3
            ):
                location.add_terrain_feature(
                    {
                        "feature_type": "northern tropic",
                    }
                )

    def update_globe_projection(
        self, center_coordinates: Tuple[int, int] = None, update_button: bool = True
    ):
        """
        Description:
            Updates the globe projection to the current state of the world grid
        Input:
            int tuple center_coordinates: Coordinates to center the globe projection on - defaults to currently centered location
            bool update_button: True if the strategic mode button should also be updated
        Output:
            None
        """
        status.globe_projection_image.set_image(
            status.strategic_map_grid.create_planet_image(
                center_coordinates=center_coordinates
            )
        )
        status.globe_projection_surface = status.globe_projection_image.image
        size = status.globe_projection_surface.get_size()
        status.globe_projection_surface = pygame.transform.scale(  # Decrease detail of each image before applying pixel mutations to speed processing
            status.globe_projection_surface,
            (
                math.floor(size[0] * constants.GLOBE_PROJECTION_DETAIL_LEVEL),
                math.floor(size[1] * constants.GLOBE_PROJECTION_DETAIL_LEVEL),
            ),
        )

        globe_projection_tile = status.globe_projection_grid.find_cell(0, 0).tile
        globe_projection_image_id = [
            "misc/space.png",
            {
                "image_id": status.globe_projection_surface,
                "size": 0.8,
            },
        ]
        globe_projection_tile.image.set_image(globe_projection_image_id)
        globe_projection_tile.grid_image_id = globe_projection_image_id

        if update_button:
            status.to_strategic_button.image.set_image(
                actor_utility.generate_frame(
                    "misc/space.png",
                )
                + [
                    {
                        "image_id": status.globe_projection_surface,
                        "size": 0.6,
                    }
                ]
            )

    def create_map_image(self):
        """
        Description:
            Creates and returns a map image of this grid
        Input:
            None
        Output:
            List: List of images representing this grid - approximation of very zoomed out grid
        """
        return_list = []
        for current_cell in self.get_flat_cell_list():
            if constants.current_map_mode == "terrain":
                image_id = current_cell.tile.get_image_id_list()[0]
            else:
                image_id = current_cell.tile.get_image_id_list()[-1]
            if type(image_id) == str:
                image_id = {
                    "image_id": image_id,
                }
            origin = (
                status.scrolling_strategic_map_grid.center_x
                - self.coordinate_width // 2,
                status.scrolling_strategic_map_grid.center_y
                - self.coordinate_height // 2,
            )
            effective_x = (
                current_cell.x - origin[0]
            ) % status.scrolling_strategic_map_grid.coordinate_width
            effective_y = (
                current_cell.y - origin[1]
            ) % status.scrolling_strategic_map_grid.coordinate_height
            image_id.update(
                {
                    "x_offset": effective_x / self.coordinate_width
                    - 0.5
                    + (0.7 / self.coordinate_width),
                    "y_offset": effective_y / self.coordinate_height
                    - 0.5
                    + (0.4 / self.coordinate_height),
                    "x_size": 1.05 / self.coordinate_width,
                    "y_size": 1.05 / self.coordinate_height,
                }
            )
            return_list.append(image_id)
        return return_list

    def create_planet_image(self, center_coordinates: Tuple[int, int] = None):
        """
        Description:
            Creates and returns a global projection of the planet on this grid, centered at the scrolling map grid's calibration point
        Input:
            None
        Output:
            list: Image ID list of each point of the global projection of the planet
        """
        if not center_coordinates:
            center_coordinates = (
                status.scrolling_strategic_map_grid.center_x,
                status.scrolling_strategic_map_grid.center_y,
            )
        index, latitude_lines = self.world_handler.get_latitude_line(center_coordinates)

        planet_width = len(latitude_lines)
        offset_width = planet_width // 2
        largest_size = len(
            max(
                self.world_handler.latitude_lines
                + self.world_handler.alternate_latitude_lines,
                key=len,
            )
        )
        return_list = []
        for offset in range(offset_width):
            min_width = (
                offset >= offset_width - 1
            )  # If leftmost or rightmost latitude line, use minimum width to avoid edge tiles looking too wide
            if (
                offset == 0
            ):  # For center offset, just draw a straight vertical latitude line
                current_line = latitude_lines[index]
                return_list += self.draw_latitude_line(
                    current_line,
                    largest_size,
                    level=offset + 20,
                    offset=offset,
                    offset_width=offset_width,
                )
            else:  # For non-center offsets, draw symmetrical curved latitude lines, progressively farther from center
                longitude_bulge_factor = (offset / offset_width) ** 0.5

                return_list += self.draw_latitude_line(
                    latitude_lines[(index + offset) % planet_width],
                    largest_size,
                    longitude_bulge_factor=longitude_bulge_factor,
                    level=offset + 20,
                    min_width=min_width,
                    offset=offset,
                    offset_width=offset_width,
                )
                return_list += self.draw_latitude_line(
                    latitude_lines[(index - offset) % planet_width],
                    largest_size,
                    longitude_bulge_factor=-1 * longitude_bulge_factor,
                    level=(-1 * offset) + 20,
                    min_width=min_width,
                    offset=offset,
                    offset_width=offset_width,
                )
        return return_list

    def draw_latitude_line(
        self,
        latitude_line,
        max_latitude_line_length: int,
        longitude_bulge_factor: float = 0.0,
        level: int = 0,
        min_width: bool = False,
        offset: int = 0,
        offset_width: int = 0,
    ):
        """
        Description:
            Returns an image ID list for a latitude line of a global map projection, creating a curve between poles that bulges at the equator
        Input:
            tuple list latitude_line: List of coordinates for each point in the latitude line
            int max_latitude_line_length: Length of the longest latitude line - to minimize size warping, latitude lines are extended to all be the same size,
                duplicating coordinates or inserting nearby coordinates that are not in latitude lines
            float longitude_bulge_factor: Factor to determine how much the latitude line bulges outwards at the equator
                Lines at longitudes farther from the center of the projection bulge further outwards and are thinner
            int level: Image ID level of the latitude line - further right latitude lines have higher levels
            boolean min_width: Whether the latitude line should use the minimum width instead of the calculated one
                Latitude lines on the edge of the projection look more evenly sized if using the minimum width
        Output:
            list: List of image IDs for the points of the latitude line
        """
        return_list = []
        center_position = (0.0, 0.0)
        total_height = 0.5  # Multiplier for y offset step sizes between each latitude
        size_multiplier = [1.5, 1.7, 1.8, 2.0, 2.2, 2.4, 2.6, 2.65][
            constants.map_size_options.index(max_latitude_line_length)
        ]
        base_tile_width = 0.10
        base_tile_height = 0.12

        # Force latitude lines to be of the same length as the largest line
        latitude_line = latitude_line.copy()  # Don't modify original
        while len(latitude_line) > max_latitude_line_length:
            latitude_line.pop(len(latitude_line) // 4)
            if len(latitude_line) > max_latitude_line_length:
                latitude_line.pop(3 * len(latitude_line) // 4)
        while len(latitude_line) < max_latitude_line_length:
            latitude_line.insert(
                *self.get_next_unaccounted_coordinates(
                    latitude_line, latitude_line[len(latitude_line) // 4]
                )
            )
            if len(latitude_line) < max_latitude_line_length:
                latitude_line.insert(
                    *self.get_next_unaccounted_coordinates(
                        latitude_line, latitude_line[3 * len(latitude_line) // 4]
                    )
                )

        y_step_size = (
            1.4 * total_height / max_latitude_line_length
        )  # Y step size between each coordinate of the latitude line
        y_step_size *= (max_latitude_line_length**0.5) / (
            constants.map_size_options[4] ** 0.5
        )

        for idx, coordinates in enumerate(
            latitude_line
        ):  # Calculate position and size of each coordinate in the latitude line
            pole_distance_factor = 1.0 - abs(
                (idx - len(latitude_line) // 2) / (len(latitude_line) // 2)
            )
            """
            The ellipse equation (x - h)^2 / a + (y - k)^2 / b = r^2 give an ellipse
                With parameters r = 0.5, h = 0.5, k = 0, a = 1, and b = bulge_effect, we can get a stretched ellipse with a configurable bulge effect
            # Solving (x - h)^2 / a + (y - k)^2 / b = r^2 for y
            # (y - k)^2 / b = r^2 - (x - h)^2 / a
            # (y - k)^2 = b * (r^2 - (x - h)^2 / a)
            # y - k = sqrt(b * (r^2 - (x - h)^2 / a))
            # y = k + sqrt(b * (r^2 - (x - h)^2 / a))
            y = k + (b * (r**2 - ((x - h)**2) / a))**0.5
            """
            r = 0.5
            h = 0.5
            k = 0
            a = 1
            x = idx / (len(latitude_line) - 1)
            b = abs(longitude_bulge_factor**3) * 5
            ellipse_weight = 0.32  # Extent to which x position is determined by ellipse function based on longitude bulge factor
            linear_weight = 0.15  # Extent to which x position is determined by linear function based on distance from center index
            if abs(longitude_bulge_factor) > 0.5:
                linear_weight *= 2.5  # Have stronger linear effect for edge latitude lines to minimize blocky corners
            elif abs(longitude_bulge_factor) > 0.35:
                linear_weight *= 1.3
            if max_latitude_line_length >= constants.map_size_options[-3]:
                ellipse_weight *= 1 / 3
                linear_weight *= 1.5
            latitude_bulge_factor = (
                k + (b * (r**2 - ((x - h) ** 2) / a)) ** 0.5
            ) * ellipse_weight
            latitude_bulge_factor += pole_distance_factor * linear_weight
            if (
                longitude_bulge_factor == 0
            ):  # If center line, don't bulge outwards, even if near equator
                latitude_bulge_factor = 0
            maximum_latitude_bulge_factor = k + (b**0.5 * r)
            if longitude_bulge_factor < 0:
                latitude_bulge_factor *= -1
                maximum_latitude_bulge_factor *= -1

            x_offset = latitude_bulge_factor / 4.0
            y_offset = 0
            for i in range(
                abs(idx - len(latitude_line) // 2)
            ):  # Move up or down for each index away from center
                change = y_step_size * (
                    0.85**i
                )  # Since each latitude is shorter than the last, the step size should also decrease
                if idx < len(latitude_line) // 2:
                    y_offset += change
                else:
                    y_offset -= change

            width_penalty = 0.015 * (
                abs(longitude_bulge_factor)
            )  # Decrease width of lines horizontally farther from the center
            height_penalty = (
                0.10 * (1.0 - abs(pole_distance_factor)) ** 2
            )  # Decrease height of lines vertically farther from the center
            if (
                max_latitude_line_length <= constants.map_size_options[1]
            ):  # Increase height for smaller maps to avoid empty space near poles
                height_penalty *= 0.6
            if max_latitude_line_length >= constants.map_size_options[-3]:
                width_penalty *= 2
            tile_width, tile_height = (
                base_tile_width - width_penalty,
                base_tile_height - height_penalty,
            )
            tile_width *= 0.8
            if (
                min_width
            ) and pole_distance_factor > 0.1:  # Since rightmost (highest level) latitude line is not covered by any others, it should be thinner to avoid an obvious size difference
                tile_width = 0.015
            tile_height = max(0.02, 0.08 - height_penalty)
            projection = {
                "x_offset": (center_position[0] + x_offset) * size_multiplier,
                "y_offset": (center_position[1] + y_offset) * size_multiplier,
                "x_size": tile_width * size_multiplier,
                "y_size": tile_height * size_multiplier,
                "level": level,
            }
            for image_id in self.find_cell(
                coordinates[0], coordinates[1]
            ).tile.get_image_id_list(terrain_only=True, force_clouds=True):
                # Apply projection offsets to each image in the tile's terrain
                if type(image_id) == str:
                    image_id = {"image_id": image_id}
                image_id.update(projection)
                return_list.append(image_id)

            if (
                self.world_handler.get_pressure_ratio() > 10.0
            ):  # If high pressure, also have sky effects for 3rd farthest latitude line
                threshold = 3
            else:  # If normal or low pressure, only have sky effects for 2nd farthest latitude line
                threshold = 2
            if (
                (offset_width - offset <= threshold and not min_width)
                and self.world_handler.get_parameter(constants.PRESSURE) > 0
                and constants.current_map_mode == "terrain"
            ):  # If 2nd farthest latitude line
                sky_effect = {
                    "image_id": "misc/green_screen_base.png",
                    "detail_level": 1.0,
                    "green_screen": tuple(self.world_handler.sky_color),
                }
                sky_effect.update(projection)
                sky_effect["level"] += 10
                if threshold <= 3 or abs(longitude_bulge_factor) > 0.5:
                    sky_effect["x_size"] *= 0.4

                sky_effect["alpha"] = 75
                pressure_ratio = self.world_handler.get_pressure_ratio()
                if pressure_ratio <= 1.0:  # More transparent for lower pressure
                    sky_effect["alpha"] = 50 + int(25 * min(pressure_ratio, 1))
                else:  # Less transparent for higher pressure
                    sky_effect["alpha"] = 75 + int(
                        25 * min((pressure_ratio - 1) / 99, 1)
                    )
                if offset != 0:
                    x_offset_magnitude = 0.02
                    if max_latitude_line_length <= constants.map_size_options[1]:
                        x_offset_magnitude *= 1.6
                    elif max_latitude_line_length >= constants.map_size_options[5]:
                        x_offset_magnitude *= 1.6
                    else:
                        x_offset_magnitude *= 1.6
                    x_offset += x_offset_magnitude * (
                        1 if longitude_bulge_factor >= 0 else -1
                    )  # Shift right if on right side and vice versa
                    sky_effect["x_offset"] = (
                        center_position[0] + x_offset
                    ) * size_multiplier

                return_list.append(sky_effect)
        return return_list

    def get_next_unaccounted_coordinates(
        self, latitude_line: List[Tuple[int, int]], default_coordinates: Tuple[int, int]
    ):
        """
        Description:
            If mode is equator_shift, shows the adjacent coordinate that is closer to the equator
                Reduces latitude distortions (tiles appear at accurate latitudes, slightly distorted to bulge equator) but misses some tiles
            If mode is closest_unerpresnted, scans a latitude line for any nearby coordinates that have no latitude line, allowing extending a latitude line's length while also missing fewer cells
                Misses fewer coordinates but introduces latitude distortions (tiles appearing at significantly inaccurate latitude)
        Input:
            list latitude_line: List of coordinates for each point in the latitude line
            tuple default_coordinates: Coordinates to insert if no other coordinates are found
        Output:
            int: Index of latitude line to insert coordinates at
            tuple: Coordinates to insert
        """
        inserted_coordinates = default_coordinates
        inserted_idx = latitude_line.index(default_coordinates)

        mode = "equator_shift"
        if (
            mode == "equator_shift"
        ):  # Insert nearby coordinates on the side closer to the equator
            if inserted_idx < round(len(latitude_line) / 2):
                inserted_idx += 1
            elif inserted_idx > round(len(latitude_line) / 2):
                inserted_idx -= 1
            inserted_coordinates = latitude_line[inserted_idx]

        elif (
            mode == "closest_unrepresented"
        ):  # Insert nearby latitudes that are not contained in any latitude lines
            for idx, coordinates in enumerate(latitude_line):
                for offset in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    adjacent_coordinates = (
                        (coordinates[0] + offset[0]) % self.coordinate_width,
                        (coordinates[1] + offset[1]) % self.coordinate_height,
                    )
                    if (
                        self.world_handler.latitude_lines_types[
                            adjacent_coordinates[0]
                        ][adjacent_coordinates[1]]
                        == None
                        and not adjacent_coordinates in latitude_line
                    ):
                        # If wouldn't be shown in any latitude lines, show here
                        inserted_coordinates = adjacent_coordinates
                        inserted_idx = idx
        return inserted_idx, inserted_coordinates


def create_grid(
    from_save: bool, grid_type: str, input_dict: Dict[str, any] = None
) -> grid:
    """
    Description:
        Creates a grid of the inputted type
    Input:
        boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
        grid_type: str value - Type of grid, like 'strategic_map_grid' or 'earth_grid'
        dictionary input_dict: Keys corresponding to the values needed to initialize this object
    Output:
        grid: Returns the newly created grid
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

    if grid_type == constants.STRATEGIC_MAP_GRID_TYPE:
        if constants.effect_manager.effect_active("large_map"):
            map_size_list = constants.terrain_manager.get_tuning("large_map_sizes")
        elif constants.effect_manager.effect_active("tiny_map"):
            map_size_list = constants.terrain_manager.get_tuning("tiny_map_sizes")
        else:
            map_size_list = constants.terrain_manager.get_tuning("map_sizes")
        constants.map_size_options = map_size_list
        map_size = input_dict.get("map_size", random.choice(map_size_list))
        if constants.effect_manager.effect_active(
            "earth_preset"
        ) or constants.effect_manager.effect_active("venus_preset"):
            map_size = map_size_list[4]
        elif constants.effect_manager.effect_active("mars_preset"):
            map_size = map_size_list[1]
        input_dict.update(
            {
                "modes": [],  # Acts as source of truth for mini grids, but this grid is not directly shown
                "coordinates": scaling.scale_coordinates(
                    constants.strategic_map_x_offset, constants.strategic_map_y_offset
                ),
                "width": scaling.scale_width(constants.strategic_map_pixel_width),
                "height": scaling.scale_height(constants.strategic_map_pixel_height),
                "coordinate_width": map_size,
                "coordinate_height": map_size,
                "grid_line_width": 2,
            }
        )
        return_grid = world_grid(from_save, input_dict)
        status.strategic_map_grid = return_grid

    elif grid_type == constants.SCROLLING_STRATEGIC_MAP_GRID_TYPE:
        input_dict.update(
            {
                "coordinates": scaling.scale_coordinates(
                    constants.strategic_map_x_offset, constants.strategic_map_y_offset
                ),
                "width": scaling.scale_width(constants.strategic_map_pixel_width),
                "height": scaling.scale_height(constants.strategic_map_pixel_height),
                "coordinate_size": status.strategic_map_grid.coordinate_width,
                "grid_line_width": 2,
                "attached_grid": status.strategic_map_grid,
            }
        )
        return_grid = mini_grid(from_save, input_dict)
        status.scrolling_strategic_map_grid = return_grid

    elif grid_type == constants.MINIMAP_GRID_TYPE:
        input_dict.update(
            {
                "coordinates": scaling.scale_coordinates(
                    constants.minimap_grid_x_offset,
                    -1 * (constants.minimap_grid_pixel_height + 25)
                    + constants.minimap_grid_y_offset,
                ),
                "width": scaling.scale_width(constants.minimap_grid_pixel_width),
                "height": scaling.scale_height(constants.minimap_grid_pixel_height),
                "coordinate_size": constants.minimap_grid_coordinate_size,
                "external_line_color": constants.COLOR_BRIGHT_RED,
                "attached_grid": status.strategic_map_grid,
            }
        )
        return_grid = mini_grid(from_save, input_dict)
        status.minimap_grid = return_grid

    elif grid_type in constants.abstract_grid_type_list:
        input_dict.update(
            {
                "coordinates": scaling.scale_coordinates(
                    getattr(constants, grid_type + "_x_offset"),
                    getattr(constants, grid_type + "_y_offset"),
                ),
                # Like (earth_grid_x_offset, earth_grid_y_offset)
                "width": scaling.scale_width(getattr(constants, grid_type + "_width")),
                "height": scaling.scale_height(
                    getattr(constants, grid_type + "_height")
                ),
            }
        )
        if grid_type == constants.EARTH_GRID_TYPE:
            input_dict["modes"].append(constants.EARTH_MODE)
        return_grid = abstract_grid(from_save, input_dict)
        if grid_type == constants.EARTH_GRID_TYPE:
            status.earth_grid = return_grid
        elif grid_type == constants.GLOBE_PROJECTION_GRID_TYPE:
            status.globe_projection_grid = return_grid
    return return_grid
