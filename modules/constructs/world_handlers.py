import random
import itertools
from math import log
from typing import List, Dict, Any
from modules.util import utility, actor_utility, world_utility
from modules.constants import constants, status, flags


class world_handler:
    """
    "Single source of truth" handler for planet-wide characteristics
    """

    def __init__(self, from_save: bool, input_dict: Dict[str, any]) -> None:
        """
        Description:
            Initializes this object
        Input:
            bool from_save: True if loading world, False if creating new one
            dictionary input_dict: Dictionary of saved information necessary to recreate this location if loading grid, or None if creating new location
        """
        status.world_list.append(self)
        self.attached_grids: List[Any] = []
        if not self.is_orbital_world:
            self.name: str = input_dict.get("name")
            self.world_dimensions: int = input_dict.get("world_dimensions")
            self.rotation_direction = input_dict.get("rotation_direction")
            self.rotation_speed = input_dict.get("rotation_speed")
            self.star_distance: float = input_dict.get("star_distance")

            self.sky_color = input_dict.get("sky_color", [0, 0, 0])
            self.default_sky_color = input_dict.get(
                "default_sky_color", self.sky_color.copy()
            )  # Never-modified copy of original sky color

            self.green_screen: Dict[str, Dict[str, any]] = input_dict.get(
                "green_screen", {}
            )
            self.color_filter: Dict[str, float] = input_dict.get(
                "color_filter",
                {
                    constants.COLOR_RED: 1,
                    constants.COLOR_GREEN: 1,
                    constants.COLOR_BLUE: 1,
                },
            )

            self.water_vapor_multiplier: float = input_dict.get(
                "water_vapor_multiplier", 1.0
            )
            self.ghg_multiplier: float = input_dict.get("ghg_multiplier", 1.0)
            self.albedo_multiplier: float = input_dict.get("albedo_multiplier", 1.0)
            self.average_water_target: float = input_dict.get(
                "average_water_target", 0.0
            )
            self.average_water: float = input_dict.get("average_water", 0.0)
            self.average_altitude: float = input_dict.get("average_altitude", 0.0)
            self.cloud_frequency: float = input_dict.get("cloud_frequency", 0.0)
            self.toxic_cloud_frequency: float = input_dict.get(
                "toxic_cloud_frequency", 0.0
            )
            self.atmosphere_haze_alpha: int = input_dict.get("atmosphere_haze_alpha", 0)

            self.steam_color = input_dict.get("steam_color", [0, 0, 0])
            self.global_parameters: Dict[str, int] = {}
            self.initial_atmosphere_offset = input_dict.get(
                "initial_atmosphere_offset", 0.001
            )
            for key in constants.global_parameters:
                self.set_parameter(
                    key, input_dict.get("global_parameters", {}).get(key, 0)
                )
            self.average_temperature: float = input_dict.get("average_temperature", 0.0)

        self.location_list: list = []
        if from_save:
            self.location_list = [
                [
                    constants.actor_creation_manager.create(
                        from_save=True,
                        input_dict={**current_location, "world_handler": self},
                    )
                    for current_location in row
                ]
                for row in input_dict["location_list"]
            ]
        else:
            self.location_list = [
                [
                    constants.actor_creation_manager.create(
                        from_save=False,
                        input_dict={
                            "init_type": constants.LOCATION,
                            "world_handler": self,
                            "coordinates": (x, y),
                        },
                    )
                    for y in range(self.coordinate_height)
                ]
                for x in range(self.coordinate_width)
            ]

        if not from_save:
            self.update_target_average_temperature(
                estimate_water_vapor=True, update_albedo=False
            )

    @property
    def coordinate_width(self) -> int:
        return self.world_dimensions

    @property
    def coordinate_height(self) -> int:
        return self.world_dimensions

    @property
    def is_earth(self) -> bool:
        return False

    @property
    def is_abstract_world(self) -> bool:
        return False

    @property
    def is_orbital_world(self) -> bool:
        return False

    def remove(self) -> None:
        status.world_list.remove(self)
        for current_location in self.get_flat_location_list():
            current_location.remove()

    def update_location_image_bundles(self, update_globe: bool = False) -> None:
        for current_location in self.get_flat_location_list():
            current_location.update_image_bundle()

    def rename(self, new_name: str) -> None:
        """
        Description:
            Renames this world
        Input:
            string new_name: New name for this world
        Output:
            None
        """
        if self.is_orbital_world:
            self.find_location(0, 0).set_name(new_name)
        elif not self.is_abstract_world:  # If full world
            self.name = new_name
            self.orbital_world.rename(new_name)

    def add_grid(self, grid: Any) -> None:
        self.attached_grids.append(grid)
        grid.world_handler = self

    def remove_grid(self, grid: Any) -> None:
        self.attached_grids.remove(grid)
        grid.world_handler = None

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
        for location in self.get_flat_location_list():
            location.set_parameter(
                constants.ALTITUDE, default_altitude, update_display=False
            )

        if constants.effect_manager.effect_active("map_customization"):
            return

        for i in range(constants.terrain_manager.get_tuning("altitude_worms")):
            min_length = (
                random.randrange(
                    self.get_tuning("min_altitude_worm_multiplier"),
                    self.get_tuning("med_altitude_worm_multiplier"),
                )
                * (self.world_dimensions**2)
            ) // 25**2
            max_length = (
                random.randrange(
                    self.get_tuning("med_altitude_worm_multiplier"),
                    self.get_tuning("max_altitude_worm_multiplier"),
                )
                * (self.world_dimensions**2)
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
        self.update_target_average_temperature(
            estimate_water_vapor=True, update_albedo=True
        )
        default_temperature = round(self.average_temperature)
        for location in self.get_flat_location_list():
            location.set_parameter(
                constants.TEMPERATURE,
                random.randrange(
                    default_temperature
                    - self.get_tuning("initial_temperature_variation"),
                    default_temperature
                    + self.get_tuning("initial_temperature_variation")
                    + 1,
                ),
                update_display=False,
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
                    constants.TEMPERATURE, default_temperature, update_display=False
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
                    * (self.world_dimensions**2)
                ) // 25**2
                max_length = (
                    random.randrange(
                        self.get_tuning("med_pole_worm_multiplier"),
                        self.get_tuning("max_pole_worm_multiplier"),
                    )
                    * (self.world_dimensions**2)
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
                temperature_source.x in [1, self.world_dimensions - 1]
                or temperature_source.y in [0, self.world_dimensions - 1]
            ):  # Avoids excessive heat at equator intersections
                min_length = (
                    random.randrange(
                        self.get_tuning("min_equator_worm_multiplier"),
                        self.get_tuning("med_equator_worm_multiplier"),
                    )
                    * (self.world_dimensions**2)
                ) // 40**2
                max_length = (
                    random.randrange(
                        self.get_tuning("med_equator_worm_multiplier"),
                        self.get_tuning("max_equator_worm_multiplier"),
                    )
                    * (self.world_dimensions**2)
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

        self.update_target_average_temperature(
            estimate_water_vapor=True, update_albedo=True
        )
        self.change_to_temperature_target(estimate_water_vapor=True)

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
        preset = world_utility.get_preset()
        if preset:
            num_worms = self.get_tuning(f"{preset}_roughness_multiplier")
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
                * (self.world_dimensions**2)
            ) // 25**2
            max_length = (
                random.randrange(
                    self.get_tuning("med_roughness_worm_multiplier"),
                    self.get_tuning("max_roughness_worm_multiplier"),
                )
                * (self.world_dimensions**2)
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
                Total water may be less than target average if repeatedly attempting to place in saturated locations, or if radiation removes some of the placed water
        Input:
            None
        Output:
            None
        """
        for _ in range(round(self.average_water_target * (self.world_dimensions**2))):
            self.place_water(radiation_effect=True, update_display=False)
        if constants.effect_manager.effect_active("map_customization"):
            attempts = 0
            while attempts < 10000 and not self.find_average(constants.WATER) == 5.0:
                self.place_water(radiation_effect=True, update_display=False)
                attempts += 1
        self.update_target_average_temperature(update_albedo=True)
        self.change_to_temperature_target()
        for location in self.get_flat_location_list():
            location.local_weather_offset = (
                location.expected_temperature_offset + random.uniform(-0.4, 0.4)
            )

    def place_water(
        self,
        frozen_bound=0,
        radiation_effect: bool = False,
        update_display: bool = True,
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
        for candidate in self.sample(
            k=round(
                self.get_tuning("water_placement_candidates")
                * (self.world_dimensions**2)
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
        for candidate in self.sample(
            k=round(
                self.get_tuning("ice_placement_candidates")
                * (self.world_dimensions**2)
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
                self.get_parameter(constants.RADIATION)
                - self.get_parameter(constants.MAGNETIC_FIELD),
            )
        else:
            radiation_effect = 0
        change = 1
        if not (
            self.get_pressure_ratio() < 0.05
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

    def remove_water(self, update_display: bool = True) -> None:
        """
        Description:
            Removes 1 unit of water from the map, depending on altitude and temperature
        Input:
            None
        Output:
            None
        """
        water_locations = [
            current_location
            for current_location in self.get_flat_location_list()
            if current_location.get_parameter(constants.WATER) > 0
        ]
        if water_locations:
            random.choices(
                water_locations,
                weights=[
                    current_location.get_parameter(constants.WATER)
                    for current_location in water_locations
                ],
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
            for location in self.get_flat_location_list():
                location.set_parameter(
                    constants.SOIL, random.randrange(0, 6), update_display=False
                )
        else:
            for location in self.get_flat_location_list():
                location.set_parameter(
                    constants.SOIL, random.randrange(0, 3), update_display=False
                )

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
                * (self.world_dimensions**2)
            ) // 25**2
            max_length = (
                random.randrange(
                    self.get_tuning("med_soil_worm_multiplier"),
                    self.get_tuning("max_soil_worm_multiplier"),
                )
                * (self.world_dimensions**2)
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
            update_display=False,
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
            for current_location in self.get_flat_location_list():
                if current_location.get_parameter(constants.TEMPERATURE) > 0:
                    if current_location.get_parameter(constants.WATER) < 4:
                        current_location.set_parameter(
                            constants.VEGETATION,
                            current_location.get_parameter(constants.WATER) * 3 + 2,
                            update_display=False,
                        )
                    else:
                        current_location.set_parameter(
                            constants.VEGETATION,
                            current_location.get_parameter(constants.ALTITUDE) + 2,
                            update_display=False,
                        )
            self.smooth(constants.VEGETATION)
        else:
            for current_location in self.get_flat_location_list():
                current_location.set_parameter(
                    constants.VEGETATION, 0, update_display=False
                )

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

    def bound(
        self, parameter: str, minimum: int, maximum: int, update_display: bool = True
    ) -> None:
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
        for current_location in self.get_flat_location_list():
            current_location.set_parameter(
                parameter,
                max(
                    min(current_location.get_parameter(parameter), maximum),
                    minimum,
                ),
                update_display=update_display,
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
        flat_location_list = list(self.get_flat_location_list())
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
        ) / (self.world_dimensions**2)

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
            for location in self.get_flat_location_list()
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
        start_location: Any = None,
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
            location start_location: Location to start the worm from, otherwise a random location is chosen
            str weight_parameter: Location parameter to weight direction selection by, if any
        Output:
            None
        """
        if start_location:
            start_x, start_y = start_location.x, start_location.y
        else:
            start_x = random.randrange(0, self.world_dimensions)
            start_y = random.randrange(0, self.world_dimensions)

        current_x = start_x
        current_y = start_y
        worm_length = random.randrange(min_len, max_len + 1)

        original_value = self.find_location(current_x, current_y).get_parameter(
            parameter
        )
        upper_bound = original_value + bound
        lower_bound = original_value - bound

        counter = 0
        while counter != worm_length:
            current_location = self.find_location(current_x, current_y)
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
                    current_y = (current_y + 1) % self.world_dimensions
                elif direction == 2:
                    current_x = (current_x + 1) % self.world_dimensions
                elif direction == 1:
                    current_y = (current_y - 1) % self.world_dimensions
                elif direction == 4:
                    current_x = (current_x - 1) % self.world_dimensions

    def generate_terrain_features(self):
        """
        Description:
            Randomly place features in each location, based on terrain
        Input:
            None
        Output:
            None
        """
        for terrain_feature_type in status.terrain_feature_types:
            for location in self.get_flat_location_list():
                if status.terrain_feature_types[terrain_feature_type].allow_place(
                    location
                ):
                    location.terrain_features[terrain_feature_type] = {
                        "feature_type": terrain_feature_type
                    }
                    location.update_image_bundle()

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
            abs(location1.x - (location2.x + self.world_dimensions)),
            abs(location1.x - (location2.x - self.world_dimensions)),
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
            abs(x1 - (x2 + self.world_dimensions)),
            abs(x1 - (x2 - self.world_dimensions)),
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
            abs(cell1.y - (cell2.y + self.world_dimensions)),
            abs(cell1.y - (cell2.y - self.world_dimensions)),
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
            abs(y1 - (y2 + self.world_dimensions)),
            abs(y1 - (y2 - self.world_dimensions)),
        )

    def euclidean_distance(self, location1, location2):
        """
        Description:
            Calculates and returns the Euclidean distance between two locations (Pythagorean theorem)
        Input:
            location location1: First location
            location location2: Second location
        Output:
            int: Returns the distance between the two locations
        """
        return (
            self.x_distance(location1, location2) ** 2
            + self.y_distance(location1, location2) ** 2
        ) ** 0.5

    def manhattan_distance(self, location1, location2):
        """
        Description:
            Calculates and returns the Manhattan distance between two locations (absolute differences on each axis)
        Input:
            location location1: First location
            location location2: Second location
        Output: int: Returns the non-diagonal distance between the two locations
        """
        return self.x_distance(location1, location2) + self.y_distance(
            location1, location2
        )

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
            location_list = list(self.get_flat_location_list())
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
        self.find_location(0, 0).add_terrain_feature(
            {
                "feature_type": "north pole",
            }
        )

        max_distance = 0

        south_pole = None
        for location in self.get_flat_location_list():
            if self.euclidean_distance(location, status.north_pole) > max_distance:
                max_distance = self.euclidean_distance(location, status.north_pole)
                south_pole = location

        south_pole.add_terrain_feature(
            {
                "feature_type": "south pole",
            }
        )

        equatorial_distance = (
            self.euclidean_distance(status.north_pole, status.south_pole) / 2
        )
        for (
            location
        ) in (
            self.get_flat_location_list()
        ):  # Results in clean equator lines in odd-sized planets
            north_pole_distance = self.euclidean_distance(location, status.north_pole)
            south_pole_distance = self.euclidean_distance(location, status.south_pole)
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
                self.manhattan_distance(status.south_pole, location)
                == self.world_dimensions // 3
            ):
                location.add_terrain_feature(
                    {
                        "feature_type": "southern tropic",
                    }
                )

            if (
                self.manhattan_distance(status.north_pole, location)
                == self.world_dimensions // 3
            ):
                location.add_terrain_feature(
                    {
                        "feature_type": "northern tropic",
                    }
                )

    def sample(self, k: int = 1):
        """
        Description:
            Randomly samples k locations from the grid
        Input:
            int k: Number of locations to sample
        Output:
            list: Returns a list of k locations
        """
        return random.choices(list(self.get_flat_location_list()), k=k)

    def get_flat_location_list(self) -> itertools.chain:
        """
        Description:
            Generates and returns a flattened version of this world's 2-dimensional location list
        Input:
            None
        Output:
            cell list: Returns a flattened version of this world's 2-dimensional cell list
        """
        return itertools.chain.from_iterable(self.location_list)

    def find_location(self, x: int, y: int) -> Any:
        return self.location_list[x % self.coordinate_width][y % self.coordinate_height]

    def change_to_temperature_target(self, estimate_water_vapor: bool = False):
        """
        Description:
            Modifies local temperatures until the target world average is reached
                Must be called after re-calculating the average temperature
            Selects locations that are most different from their ideal temperatures
        Input:
            boolean estimate_water_vapor: Whether to estimate the water vapor contribution or to directly calculate
                Setting up temperature before water requires estimating water vapor amount
        Output:
            None
        """
        if abs(self.average_temperature - self.get_average_local_temperature()) > 0.03:
            while (
                self.average_temperature > self.get_average_local_temperature()
                and self.get_average_local_temperature() < 10.5
            ):
                self.warm()
                self.update_target_average_temperature(
                    estimate_water_vapor=estimate_water_vapor, update_albedo=False
                )
            while (
                self.average_temperature < self.get_average_local_temperature()
                and self.get_average_local_temperature() > -5.5
            ):
                self.cool()
                self.update_target_average_temperature(
                    estimate_water_vapor=estimate_water_vapor, update_albedo=False
                )
            self.bound(
                constants.TEMPERATURE,
                round(self.average_temperature)
                - self.get_tuning("final_temperature_variations")[0],
                round(self.average_temperature)
                + self.get_tuning("final_temperature_variations")[1],
            )
            self.smooth(constants.TEMPERATURE)

    def change_parameter(self, parameter_name: str, change: int) -> None:
        """
        Description:
            Changes the value of a parameter for this handler's cells
        Input:
            string parameter_name: Name of the parameter to change
            int change: Amount to change the parameter by
            boolean update_image: Whether to update the image of any attached locations after changing the parameter
        Output:
            None
        """
        self.set_parameter(
            parameter_name, round(self.global_parameters[parameter_name] + change, 2)
        )

    def set_parameter(self, parameter_name: str, new_value: int) -> None:
        """
        Description:
            Sets the value of a parameter for this handler's cells
        Input:
            string parameter_name: Name of the parameter to change
            int new_value: New value for the parameter
            boolean update_image: Whether to update the image of any attached locations after setting the parameter
        Output:
            None
        """
        self.global_parameters[parameter_name] = max(0, new_value)
        if parameter_name in constants.ATMOSPHERE_COMPONENTS:
            self.update_pressure()

        if status.displayed_location:
            actor_utility.calibrate_actor_info_display(
                status.location_info_display, status.displayed_location
            )
        for mob in status.mob_list:
            if (
                mob.get_location()
                and mob.get_location().get_true_world_handler() == self
            ):
                mob.update_habitability()

    def update_pressure(self) -> None:
        """
        Description:
            Updates the planet's pressure to be a sum of its atmosphere components whenever any are changed
        Input:
            None
        Output:
            None
        """
        self.global_parameters[constants.PRESSURE] = round(
            sum(
                [
                    self.get_parameter(atmosphere_component)
                    for atmosphere_component in constants.ATMOSPHERE_COMPONENTS
                ]
            ),
            1,
        )

    def update_sky_color(
        self, set_initial_offset: bool = False, update_water: bool = False
    ) -> None:
        """
        Description:
            Updates the sky color of this world handler based on the current atmosphere composition
                The sky color is a weighted average of the original sky color and that of Earth, with weights depending on atmosphere terraforming progress
            Optionally records the original atmosphere offset from Earth's atmosphere for initial setup
        Input:
            bool set_initial_offset: Whether to record the original atmosphere offset from Earth's atmosphere
            update_water: Whether to update the water color
        Output:
            None
        """
        if self.get_parameter(constants.PRESSURE) == 0:
            if set_initial_offset:
                self.initial_atmosphere_offset = 0
        earth_sky_color = self.get_tuning("earth_sky_color")
        total_offset = 0
        for atmosphere_component in constants.ATMOSPHERE_COMPONENTS:
            if self.get_parameter(constants.PRESSURE) == 0:
                composition = 0.01
            else:
                composition = self.get_composition(atmosphere_component)
            ideal = self.get_tuning(f"earth_{atmosphere_component}")
            if atmosphere_component == constants.TOXIC_GASES:
                offset = max(0, (composition - 0.001) / 0.001)
            if ideal != 0:
                offset = abs(composition - ideal) / ideal
            total_offset += offset
        if set_initial_offset:
            self.initial_atmosphere_offset = max(50.0, total_offset)

        # Record total offset in each call - only update colors if total offset changed
        total_offset = min(total_offset, self.initial_atmosphere_offset)
        progress = (self.initial_atmosphere_offset - total_offset) / (
            self.initial_atmosphere_offset
        )
        self.sky_color = [
            round(
                max(
                    0,
                    min(
                        255,
                        self.default_sky_color[i] * (1.0 - progress)
                        + earth_sky_color[i] * progress,
                    ),
                )
            )
            for i in range(3)
        ]
        self.steam_color = [min(240, sky_color + 80) for sky_color in self.sky_color]
        if update_water:
            inherent_water_color = (11, 24, 144)
            sky_weight = 0.4
            water_color = [
                round(
                    (
                        inherent_water_color[i] * (1.0 - sky_weight)
                        + ((self.sky_color[i] - 50) * sky_weight)
                    )
                )
                for i in range(3)
            ]
            if self.green_screen:
                self.green_screen["deep water"]["replacement_color"] = (
                    water_color[0] * 0.9,
                    water_color[1] * 0.9,
                    water_color[2] * 1,
                )
                self.green_screen["shallow water"]["replacement_color"] = (
                    water_color[0],
                    water_color[1] * 1.1,
                    water_color[2] * 1,
                )

        if not flags.loading:
            status.current_world.update_globe_projection(update_button=True)

    def get_water_vapor_contributions(
        self, estimated_temperature: float = None
    ) -> float:
        """
        Description:
            Calculates the average water vapor for the planet, depending on local water and temperature
        Input:
            None
        Output:
            float: Average water vapor for the planet
        """
        total_water_vapor = 0
        water_vapor_max_contribution = (
            self.get_tuning("water_boiling_point")
            - self.get_tuning("water_freezing_point")
            + 2
        )
        if estimated_temperature != None:
            water_vapor_contribution = (
                estimated_temperature - self.get_tuning("water_freezing_point") + 2
            )
            contribution_ratio = water_vapor_contribution / water_vapor_max_contribution
            if contribution_ratio > 0:
                average_water_vapor = (
                    (0.4 + (0.6 * contribution_ratio)) * self.average_water_target * 1.5
                )
            else:
                average_water_vapor = 0
            return average_water_vapor
        else:
            for location in self.get_flat_location_list():
                water_vapor_contribution = (
                    location.get_parameter(constants.TEMPERATURE)
                    - self.get_tuning("water_freezing_point")
                    + 2
                )
                contribution_ratio = (
                    water_vapor_contribution / water_vapor_max_contribution
                )
                if contribution_ratio > 0:
                    total_water_vapor += (
                        (0.4 + (0.6 * contribution_ratio))
                        * location.get_parameter(constants.WATER)
                        * 1.5
                    )
            return total_water_vapor / (self.world_dimensions**2)

    def update_cloud_frequencies(self, estimated_temperature: bool = None) -> float:
        """
        Description:
            Creates random clouds for each location, with frequency depending on water vapor
        Input:
            None
        Output:
            None
        """
        num_cloud_variants = constants.terrain_manager.terrain_variant_dict.get(
            "clouds_base", 1
        )
        num_solid_cloud_variants = constants.terrain_manager.terrain_variant_dict.get(
            "clouds_solid", 1
        )
        self.cloud_frequency = max(
            0,
            min(
                1,
                0.25
                * (
                    self.get_water_vapor_contributions(
                        estimated_temperature=estimated_temperature
                    )
                    / self.get_tuning("earth_water_vapor")
                ),
            ),
        )
        if self.get_parameter(constants.PRESSURE) > 0:
            toxic_cloud_composition_frequency = min(
                0.5,
                self.get_parameter(constants.TOXIC_GASES)
                / self.get_parameter(constants.PRESSURE)
                * 10,
            )
        else:
            toxic_cloud_composition_frequency = 0
        toxic_cloud_quantity_frequency = min(
            0.5,
            (
                self.get_parameter(constants.PRESSURE)
                / self.get_ideal_parameter(constants.PRESSURE)
            )
            * 0.25,
        )
        self.toxic_cloud_frequency = (
            toxic_cloud_quantity_frequency * toxic_cloud_composition_frequency
        )

    def update_clouds(self, estimated_temperature: float = None) -> None:
        """
        Description:
            Creates random clouds for each location, with frequency depending on water vapor
        Input:
            None
        Output:
            None
        """
        num_cloud_variants = constants.terrain_manager.terrain_variant_dict.get(
            "clouds_base", 1
        )
        num_solid_cloud_variants = constants.terrain_manager.terrain_variant_dict.get(
            "clouds_solid", 1
        )
        self.update_cloud_frequencies(estimated_temperature=estimated_temperature)
        # Toxic cloud frequency depends on both toxic gas % and total pressure

        pressure_alpha = max(0, self.get_pressure_ratio() * 7 - 14)
        toxic_alpha = min(
            255, log(1 + (self.get_pressure_ratio(constants.TOXIC_GASES)), 2) * 255
        )
        self.atmosphere_haze_alpha = min(255, pressure_alpha + toxic_alpha)

        # Atmosphere haze depends on total pressure, with toxic gases greatly over-represented

        for location in self.get_flat_location_list():
            location.current_clouds = []

            cloud_type = None
            if random.random() < self.cloud_frequency:
                cloud_type = "water vapor"
            elif random.random() < self.toxic_cloud_frequency:
                cloud_type = "toxic"
            if cloud_type:
                location.current_clouds.append(
                    {
                        "image_id": "misc/shader.png",
                        "detail_level": constants.CLOUDS_DETAIL_LEVEL,
                    }
                )
            if self.atmosphere_haze_alpha > 0:
                location.current_clouds.append(
                    {
                        "image_id": f"terrains/clouds_solid_{random.randrange(0, num_solid_cloud_variants)}.png",
                        "alpha": self.atmosphere_haze_alpha,
                        "detail_level": constants.CLOUDS_DETAIL_LEVEL,
                        "green_screen": {
                            "clouds": {
                                "base_colors": [(174, 37, 19)],
                                "tolerance": 60,
                                "replacement_color": self.sky_color,
                            },
                        },
                    }
                )
            if cloud_type == "water vapor":
                location.current_clouds.append(
                    {
                        "image_id": f"terrains/clouds_base_{random.randrange(0, num_cloud_variants)}.png",
                        "detail_level": constants.CLOUDS_DETAIL_LEVEL,
                        "green_screen": {
                            "clouds": {
                                "base_colors": [(174, 37, 19)],
                                "tolerance": 60,
                                "replacement_color": self.steam_color,
                            },
                        },
                    }
                )
            elif cloud_type == "toxic":
                location.current_clouds.append(
                    {
                        "image_id": f"terrains/clouds_base_{random.randrange(0, num_cloud_variants)}.png",
                        "detail_level": constants.CLOUDS_DETAIL_LEVEL,
                        "green_screen": {
                            "clouds": {
                                "base_colors": [(174, 37, 19)],
                                "tolerance": 60,
                                "replacement_color": [
                                    round(color * 0.8) for color in self.sky_color
                                ],
                            },
                        },
                    }
                )
        if not flags.loading:
            status.current_world.update_globe_projection(update_button=True)

    def get_parameter(self, parameter_name: str) -> int:
        """
        Description:
            Returns the value of the inputted parameter from this world handler
        Input:
            string parameter: Name of the parameter to get
        Output:
            None
        """
        return self.global_parameters.get(parameter_name, 0)

    def get_tuning(self, tuning_type):
        """
        Description:
            Gets the tuning value for the inputted tuning type, returning the default version if none is available
        Input:
            string tuning_type: Tuning type to get the value of
        Output:
            any: Tuning value for the inputted tuning type
        """
        return constants.terrain_manager.get_tuning(tuning_type)

    def to_save_dict(self) -> Dict[str, any]:
        """
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
        """
        return {
            "world_dimensions": self.world_dimensions,
            "location_list": [
                [location.to_save_dict() for location in row]
                for row in self.location_list
            ],
            "color_filter": self.color_filter,
            "green_screen": self.green_screen,
            "global_parameters": self.global_parameters,
            "average_water": self.average_water,
            "average_temperature": self.average_temperature,
            "rotation_direction": self.rotation_direction,
            "rotation_speed": self.rotation_speed,
            "name": self.name,
            "sky_color": self.sky_color,
            "default_sky_color": self.default_sky_color,
            "steam_color": self.steam_color,
            "initial_atmosphere_offset": self.initial_atmosphere_offset,
            "star_distance": self.star_distance,
            "water_vapor_multiplier": self.water_vapor_multiplier,
            "ghg_multiplier": self.ghg_multiplier,
            "albedo_multiplier": self.albedo_multiplier,
            "cloud_frequency": self.cloud_frequency,
            "toxic_cloud_frequency": self.toxic_cloud_frequency,
            "atmosphere_haze_alpha": self.atmosphere_haze_alpha,
        }

    def get_green_screen(self, terrain: str = None) -> Dict[str, Dict[str, any]]:
        """
        Description:
            Returns the green screen for the inputted terrain type on this world
        Input:
            None
        Output:
            dictionary: Green screen for the inputted terrain type on this world
        """
        # Make any per-terrain modifications

        return self.green_screen

    def get_ideal_parameter(self, parameter_name: str) -> float:
        """
        Description:
            Gets the ideal value of the inputted terrain parameter
        Input:
            string parameter_name: Name of the parameter to get the ideal value of
        Output:
            float: Ideal value of the inputted parameter, like 1.0 gravity or 21% of atmosphere's pressure for oxygen
        """
        if parameter_name in constants.ATMOSPHERE_COMPONENTS:
            return round(
                (self.world_dimensions**2)
                * 6
                * self.get_tuning(f"earth_{parameter_name}"),
                2,
            )
        elif parameter_name == constants.RADIATION:
            return 0.0
        elif parameter_name == constants.PRESSURE:
            if (self.world_dimensions**2) == 1:
                return (
                    (constants.earth_dimensions**2)
                    * 6
                    * self.get_tuning("earth_pressure")
                )
            else:
                return (
                    (self.world_dimensions**2) * 6 * self.get_tuning("earth_pressure")
                )
        else:
            return self.get_tuning(f"earth_{parameter_name}")

    def get_pressure_ratio(self, component=None) -> float:
        """
        Description:
            Returns the ratio of the current pressure to the ideal pressure
        Input:
            string component: Component of the pressure to get the ratio of, default to entire pressure
        Output:
            float: Ratio of the current pressure to the ideal pressure
        """
        if not component:
            component = constants.PRESSURE
        return self.get_parameter(component) / self.get_ideal_parameter(
            constants.PRESSURE
        )

    def get_composition(self, component: str) -> float:
        """
        Description:
            Calculates and returns the % composition of an inputted atmosphere component
        Input:
            string component: Component of the atmosphere to calculate the composition of
        Output:
            float: Returns the % composition of the inputted atmosphere component
        """
        if self.get_parameter(component) == 0:
            return 0.0
        else:
            return self.get_parameter(component) / self.get_parameter(
                constants.PRESSURE
            )

    def get_parameter_habitability(self, parameter_name: str) -> int:
        """
        Description:
            Calculates and returns the habitability effect of a particular global parameter
        Input:
            string parameter_name: Name of the parameter to calculate habitability for
        Output:
            int: Returns the habitability effect of the inputted parameter, from 0 to 5 (5 is perfect, 0 is deadly)
        """
        value = self.get_parameter(parameter_name)
        ideal = self.get_ideal_parameter(parameter_name)
        deadly_lower_bound, deadly_upper_bound = constants.DEADLY_PARAMETER_BOUNDS.get(
            parameter_name, (None, None)
        )
        (
            perfect_lower_bound,
            perfect_upper_bound,
        ) = constants.PERFECT_PARAMETER_BOUNDS.get(parameter_name, (None, None))

        if parameter_name == constants.PRESSURE:
            ratio = round(value / ideal, 2)
            if ratio >= deadly_upper_bound:
                return constants.HABITABILITY_DEADLY
            elif ratio >= 10:
                return constants.HABITABILITY_DANGEROUS
            elif ratio >= 4:
                return constants.HABITABILITY_HOSTILE
            elif ratio >= 2.5:
                return constants.HABITABILITY_UNPLEASANT
            elif ratio >= 1.1:
                return constants.HABITABILITY_TOLERABLE
            elif ratio >= 0.9:
                return constants.HABITABILITY_PERFECT
            elif ratio >= 0.75:
                return constants.HABITABILITY_TOLERABLE
            elif ratio >= 0.55:
                return constants.HABITABILITY_UNPLEASANT
            elif ratio >= 0.21:
                return constants.HABITABILITY_HOSTILE
            elif ratio >= deadly_lower_bound:
                return constants.HABITABILITY_DANGEROUS
            else:
                return constants.HABITABILITY_DEADLY
        elif parameter_name == constants.OXYGEN:
            if self.get_parameter(constants.PRESSURE) == 0:
                return constants.HABITABILITY_PERFECT
            composition = round(self.get_composition(constants.OXYGEN), 2)
            if composition >= 0.6:
                return constants.HABITABILITY_HOSTILE
            elif composition >= 0.24:
                return constants.HABITABILITY_UNPLEASANT
            elif composition >= perfect_upper_bound:
                return constants.HABITABILITY_TOLERABLE
            elif composition >= perfect_lower_bound:
                return constants.HABITABILITY_PERFECT
            elif composition >= 0.19:
                return constants.HABITABILITY_TOLERABLE
            elif composition >= 0.17:
                return constants.HABITABILITY_UNPLEASANT
            elif composition >= 0.14:
                return constants.HABITABILITY_HOSTILE
            elif composition >= deadly_lower_bound:
                return constants.HABITABILITY_DANGEROUS
            else:
                return constants.HABITABILITY_DEADLY
        elif parameter_name == constants.GHG:
            if self.get_parameter(constants.PRESSURE) == 0:
                return constants.HABITABILITY_PERFECT
            composition = round(self.get_composition(constants.GHG), 3)
            if composition >= deadly_upper_bound:
                return constants.HABITABILITY_DEADLY
            elif composition >= 0.02:
                return constants.HABITABILITY_DANGEROUS
            elif composition >= 0.015:
                return constants.HABITABILITY_HOSTILE
            elif composition >= 0.01:
                return constants.HABITABILITY_UNPLEASANT
            elif composition >= perfect_upper_bound:
                return constants.HABITABILITY_TOLERABLE
            else:
                return constants.HABITABILITY_PERFECT

        elif parameter_name == constants.INERT_GASES:
            if self.get_parameter(constants.PRESSURE) == 0:
                return constants.HABITABILITY_PERFECT
            composition = round(self.get_composition(constants.INERT_GASES), 3)
            if composition >= perfect_upper_bound:
                return constants.HABITABILITY_TOLERABLE
            elif composition >= perfect_lower_bound:
                return constants.HABITABILITY_PERFECT
            elif composition >= 0.5:
                return constants.HABITABILITY_TOLERABLE
            else:
                return constants.HABITABILITY_UNPLEASANT

        elif parameter_name == constants.TOXIC_GASES:
            if self.get_parameter(constants.PRESSURE) == 0:
                return constants.HABITABILITY_PERFECT
            composition = round(self.get_composition(constants.TOXIC_GASES), 5)
            if composition >= deadly_upper_bound:
                return constants.HABITABILITY_DEADLY
            elif composition >= 0.003:
                return constants.HABITABILITY_DANGEROUS
            elif composition >= 0.002:
                return constants.HABITABILITY_HOSTILE
            elif composition >= 0.001:
                return constants.HABITABILITY_UNPLEASANT
            elif composition >= perfect_upper_bound:
                return constants.HABITABILITY_TOLERABLE
            else:
                return constants.HABITABILITY_PERFECT

        elif parameter_name == constants.GRAVITY:
            ratio = round(value / ideal, 2)
            if ratio >= 5:
                return constants.HABITABILITY_DEADLY
            elif ratio >= 4:
                return constants.HABITABILITY_DANGEROUS
            elif ratio >= 2:
                return constants.HABITABILITY_HOSTILE
            elif ratio >= 1.4:
                return constants.HABITABILITY_UNPLEASANT
            elif ratio >= perfect_upper_bound:
                return constants.HABITABILITY_TOLERABLE
            elif ratio >= perfect_lower_bound:
                return constants.HABITABILITY_PERFECT
            elif ratio >= 0.6:
                return constants.HABITABILITY_TOLERABLE
            elif ratio >= 0.3:
                return constants.HABITABILITY_UNPLEASANT
            else:
                return constants.HABITABILITY_HOSTILE

        elif parameter_name == constants.RADIATION:
            radiation_effect = value - self.get_parameter(constants.MAGNETIC_FIELD)
            if radiation_effect >= deadly_upper_bound:
                return constants.HABITABILITY_DEADLY
            elif radiation_effect >= 2:
                return constants.HABITABILITY_DANGEROUS
            elif radiation_effect >= 1:
                return constants.HABITABILITY_HOSTILE
            else:
                return constants.HABITABILITY_PERFECT
        elif parameter_name == constants.MAGNETIC_FIELD:
            return constants.HABITABILITY_PERFECT

    def get_average_local_temperature(self):
        """
        Description:
            Re-calculates the average temperature of this world
        Input:
            None
        Output:
            None
        """
        return round(
            sum(
                [
                    location.get_parameter(constants.TEMPERATURE)
                    for location in self.get_flat_location_list()
                ]
            )
            / (self.world_dimensions**2),
            2,
        )

    def update_average_water(self):
        """
        Description:
            Re-calculates the average water of this world
        Input:
            None
        Output:
            None
        """
        self.average_water = round(
            sum(
                [
                    location.get_parameter(constants.WATER)
                    for location in self.get_flat_location_list()
                ]
            )
            / (self.world_dimensions**2),
            3,
        )

    def update_average_altitude(self):
        """
        Description:
            Re-calculates the average altitude of this world
        Input:
            None
        Output:
            None
        """
        self.average_altitude = round(
            sum(
                [
                    location.get_parameter(constants.ALTITUDE)
                    for location in self.get_flat_location_list()
                ]
            )
            / (self.world_dimensions**2),
            2,
        )

    def get_insolation(self):
        """
        Description:
            Calculates and returns the insolation of this planet based on its star distance
        Input:
            None
        Output:
            Returns the insolation of this planet based on its star distance
        """
        return round((1 / (self.star_distance) ** 2), 2)

    def get_sun_effect(self):
        """
        Description:
            Calculates and returns the base amount of heat caused by the sun on this planet, before including greenhouse effect and albedo
                Note that Earth's albedo is divided out so that multiplying in Earth's albedo later cancels out, resulting in the correct sun effect for Earth
        Input:
            None
        Output:
            Returns the base amount of heat caused by the sun on this planet
        """
        return (
            (
                self.get_tuning("earth_base_temperature_fahrenheit")
                - constants.ABSOLUTE_ZERO
            )
            * (self.get_insolation() ** 0.25)
            / self.get_tuning("earth_albedo_multiplier")
        )

    def get_ghg_effect_multiplier(self, weight: float = 1.0) -> float:
        """
        Description:
            Calculates and returns the greenhouse effect caused by greenhouse gases on this planet
        Input:
            float weight: Weight of the greenhouse gas effect in the overall temperature calculation
        Output:
            Returns the greenhouse effect caused by greenhouse gases on this planet
        """
        atm = self.get_pressure_ratio(constants.GHG)
        if atm < 0.0002:  # Linear relationship for very low GHG values
            ghg_multiplier = 1.0 + (weight * (0.05 * (atm / 0.0002)))
        else:  # Logarithmic relationship for Earth-like GHG values, such that doubling/halving GHG changes temperature by about 5 degrees Fahrenheit
            ghg_multiplier = 1.0 + (weight * (0.06 + (log(atm / 0.0004, 2) * 0.01)))
        ghg_multiplier += min(
            0.43, weight * atm
        )  # Add significant increases for GHG values from ~0-1 atm, up to 0.43x
        ghg_multiplier += min(
            0.43, weight * (atm * 0.272 * 0.5 * 0.5)
        )  # Add significant increases for moderately large GHG values, up to 0.43x
        ghg_multiplier += weight * (
            atm * 0.015 * 0.26
        )  # Continue adding significant increases for very large GHG values
        # Tune to get yield correct Venus temperature

        if (
            self.get_pressure_ratio() < 0.5
        ):  # Apply negative penalty to GHG multiplier in thin atmospheres, as more heat is lost directly to space
            ghg_multiplier -= 0.1 * (0.5 - self.get_pressure_ratio())

        self.ghg_multiplier = ghg_multiplier
        return self.ghg_multiplier

    def get_water_vapor_effect_multiplier(
        self,
        weight: float = 1.0,
        estimated_temperature: float = None,
    ) -> float:
        """
        Description:
            Calculates and returns the greenhouse effect caused by water vapor on this planet
                Optionally uses an estimated final temperature to use if attempting to calculate water vapor effect before water is generated
                    Water vapor both causes and is caused by temperature changes, so an estimated baseline is required
        Input:
            float weight: Weight of the water vapor effect in the overall temperature calculation
            float estimated_temperature: Estimated temperature of the planet, used to calculate water vapor effect before water is generated
        Output:
            Returns the greenhouse effect caused by water vapor on this planet
        """
        if self.is_earth:
            water_vapor = self.get_tuning("earth_water_vapor")
        else:
            water_vapor = self.get_water_vapor_contributions(
                estimated_temperature=estimated_temperature
            )

        water_vapor_multiplier = 1.0 + (
            water_vapor / self.get_tuning("earth_water_vapor") * weight * 0.5 * 0.124
        )
        self.water_vapor_multiplier = water_vapor_multiplier
        return self.water_vapor_multiplier

    def get_albedo_effect_multiplier(self):
        """
        Description:
            Re-calculates and returns the albedo multiplier to heat received by this planet, based on clouds and location brightnesss
        Input:
            None
        Output:
            None
        """
        self.update_location_image_bundles(update_globe=False)
        cloud_albedo = 0.75
        cloud_frequency = min(
            1,
            self.cloud_frequency
            + self.toxic_cloud_frequency
            + (self.atmosphere_haze_alpha / 255),
        )

        average_brightness = sum(
            [location.get_brightness() for location in self.get_flat_location_list()]
        ) / (self.world_dimensions**2)
        terrain_albedo = min(0.5, max(0.0, (0.5 / 255) * average_brightness * 0.85))

        albedo_weight = 0.4  # Draw albedo effect towards that of Earth
        total_albedo = (cloud_albedo * cloud_frequency) + (
            terrain_albedo * (1 - cloud_frequency)
        )
        self.albedo_multiplier = ((1 - total_albedo) * albedo_weight) + (
            self.get_tuning("earth_albedo_multiplier") * (1 - albedo_weight)
        )

        return self.albedo_multiplier

    def get_total_heat(self):
        """
        Description:
            Calculates and returns the total heat received by this planet, including greenhouse effect, water vapor, albedo, and base sunlight received
        Input:
            None
        Output:
            float: Returns the total heat received by this planet
        """
        return round(
            self.water_vapor_multiplier
            * self.ghg_multiplier
            * self.albedo_multiplier
            * self.get_sun_effect(),
            2,
        )

    def update_target_average_temperature(
        self, estimate_water_vapor: bool = False, update_albedo: bool = False
    ):
        """
        Description:
            Re-calculates the average temperature of this world, based on sun distance -> solation and greenhouse effect
                This average temperature is used as a target, changing local temperature until the average is reached
        Input:
            None
        Output:
            None
        """
        if self.is_orbital_world:
            return
        pressure = self.get_pressure_ratio()
        if pressure >= 1:  # Linear relationship from 1, 1 to 10, 3/2
            min_effect = 1
            max_effect = 2.45
            min_pressure = 1
            max_pressure = 25
            min_pressure = 1
        else:
            min_effect = 0  # Tune value to make Mars the correct temperature
            max_effect = 1
            min_pressure = 0
            max_pressure = 1
            min_pressure = 0
        pressure_effect = min(
            max_effect,
            max(
                min_effect,
                min_effect
                + ((pressure - min_pressure) * (max_effect - min_effect))
                / (max_pressure - min_pressure),
            ),
        )
        water_vapor_weight, ghg_weight = (
            1.0 * pressure_effect,
            1.0 * pressure_effect,
        )  # Increase GHG effect for higher pressures and vice versa

        ghg_multiplier = self.get_ghg_effect_multiplier(weight=ghg_weight)

        if estimate_water_vapor:
            estimated_temperature = utility.reverse_fahrenheit(
                (ghg_multiplier * 1.03 * self.get_sun_effect())
                + constants.ABSOLUTE_ZERO
            )
            water_vapor_multiplier = self.get_water_vapor_effect_multiplier(
                weight=water_vapor_weight,
                estimated_temperature=estimated_temperature,
            )
        else:
            estimated_temperature = None
            water_vapor_multiplier = self.get_water_vapor_effect_multiplier(
                weight=water_vapor_weight,
            )

        if update_albedo:
            self.update_cloud_frequencies(estimated_temperature=estimated_temperature)
            self.get_albedo_effect_multiplier()
        fahrenheit = (
            ghg_multiplier
            * water_vapor_multiplier
            * self.albedo_multiplier
            * self.get_sun_effect()
        ) + constants.ABSOLUTE_ZERO
        self.average_temperature = utility.reverse_fahrenheit(fahrenheit)
        for location in self.get_flat_location_list():
            location.expected_temperature_offset = (
                location.terrain_parameters[constants.TEMPERATURE]
                - location.get_expected_temperature()
            )
        self.average_temperature = utility.reverse_fahrenheit(fahrenheit)
