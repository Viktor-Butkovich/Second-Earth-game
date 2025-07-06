import pygame
import math
import random
import time
from typing import List, Dict, Tuple, Any
from modules.util import actor_utility, world_utility, utility
from modules.constructs import world_handlers
from modules.constants import constants, status, flags


class abstract_world_handler(world_handlers.world_handler):
    """
    World handler corresponding to a single location
    Can either be an orbital world, presenting an interface between the orbital tile and the actual world, or an
        abstract representation of a world like Earth or a possible outpost location
    """

    def __init__(self, from_save: bool, input_dict: Dict[str, Any]) -> None:
        """
        Description:
            Initializes this object
        Input:
            bool from_save: True if loading world, False if creating new one
            dictionary input_dict: Dictionary of saved information necessary to recreate this location if loading grid, or None if creating new location
        Output:
            None
        """
        self.abstract_world_type: str = input_dict["abstract_world_type"]
        self.image_id_list: List[any] = input_dict.get("image_id_list", [])
        super().__init__(from_save, input_dict)
        self.set_image(input_dict.get("image_id_list", []))
        self.find_location(0, 0).set_name(
            self.name
        )  # Create a way to ensure abstract location name and world name always match
        # Probably replace .name in location with get_name and set_name, which can access world name as needed

    def set_image(self, new_image: List[any]) -> None:
        """
        Description:
            Sets the image for this abstract world's location
            Unlike usual locations, abstract locations use the image of their world, which is externally generated
        Input:
            image ID list new_image: Image ID to use for this abstract world
        Output:
            None
        """
        self.image_id_list = new_image
        constants.EventBus.publish(
            self.uuid, constants.ABSTRACT_WORLD_UPDATE_IMAGE_ROUTE
        )  # Update images subscribed to this world's image

    def to_save_dict(self) -> Dict[str, Any]:
        """
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
        """
        return {
            **super().to_save_dict(),
            "init_type": constants.ABSTRACT_WORLD,
            "abstract_world_type": self.abstract_world_type,
            "image_id_list": self.image_id_list,
        }

    @property
    def coordinate_width(self) -> int:
        """
        Returns this world's coordinate width (always 1 for abstract worlds)
        """
        return 1

    @property
    def coordinate_height(self) -> int:
        """
        Returns this world's coordinate height (always 1 for abstract worlds)
        """
        return 1

    @property
    def is_abstract_world(self) -> bool:
        """
        Returns whether this is an abstract world (always True for abstract worlds)
        """
        return True

    @property
    def is_earth(self) -> bool:
        """
        Returns whether this is the Earth abstract world
        """
        return self.abstract_world_type == constants.EARTH_WORLD


class orbital_world_handler(abstract_world_handler):
    """
    World handler that has its own abstract grid and location but copies the attributes of the full world it orbits
    Allows planet orbit to have its own orbital location while using the full world's parameters
    """

    def __init__(self, from_save: bool, input_dict: Dict[str, Any]) -> None:
        """
        Description:
            Initializes this object
        Input:
            bool from_save: True if loading world, False if creating new one
            dictionary input_dict: Dictionary of saved information necessary to recreate this location if loading grid, or None if creating new location
        Output:
            None
        """
        self.full_world: full_world_handler = input_dict["full_world"]
        input_dict["abstract_world_type"] = constants.ORBITAL_WORLD
        super().__init__(from_save, input_dict)

    def set_parameter(self, parameter_name: str, new_value: int) -> None:
        """
        Interface to set global parameters through the full world instead of this abstract world
        """
        self.full_world.set_parameter(parameter_name, new_value)

    def change_parameter(self, parameter_name: str, change: int) -> None:
        """
        Interface to change global parameters through the full world instead of this abstract world
        """
        self.full_world.change_parameter(parameter_name, change)

    def get_parameter(self, parameter_name: str) -> int:
        """
        Interface to get global parameters through the full world instead of this abstract world
        """
        return self.full_world.get_parameter(parameter_name)

    def to_save_dict(self) -> Dict[str, Any]:
        """
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
                Orbital worlds are saved as part of their full world, rather than independently
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
        """
        return {
            "init_type": constants.ORBITAL_WORLD,
            "location_list": [  # All other information saved by the full world
                [location.to_save_dict() for location in row]
                for row in self.location_list
            ],
        }

    @property
    def is_orbital_world(self) -> bool:
        """
        Returns whether this is an orbital world (always True for orbital worlds)
        """
        return True

    @property
    def name(self) -> str:
        """
        Interface to get name through the full world instead of this abstract world
        """
        return self.full_world.name

    @property
    def world_dimensions(self) -> int:
        """
        Interface to get world dimensions through the full world instead of this abstract world
        """
        return self.full_world.world_dimensions

    @property
    def rotation_direction(self) -> int:
        """
        Interface to get rotation direction through the full world instead of this abstract world
        """
        return self.full_world.rotation_direction

    @property
    def rotation_speed(self) -> int:
        """
        Interface to get rotation speed through the full world instead of this abstract world
        """
        return self.full_world.rotation_speed

    @property
    def star_distance(self) -> float:
        """
        Interface to get star distance through the full world instead of this abstract world
        """
        return self.full_world.star_distance

    @property
    def sky_color(self) -> Tuple[int, int, int]:
        """
        Interface to get sky color through the full world instead of this abstract world
        """
        return self.full_world.sky_color

    @property
    def default_sky_color(self) -> Tuple[int, int, int]:
        """
        Interface to get default sky color through the full world instead of this abstract world
        """
        return self.full_world.default_sky_color

    @property
    def average_water(self) -> float:
        """
        Interface to get average water through the full world instead of this abstract world
        """
        return self.full_world.average_water

    @property
    def average_temperature(self) -> float:
        """
        Interface to get average temperature through the full world instead of this abstract world
        """
        return self.full_world.average_temperature

    @property
    def water_vapor_multiplier(self) -> float:
        """
        Interface to get water vapor multiplier through the full world instead of this abstract world
        """
        return self.full_world.water_vapor_multiplier

    @property
    def ghg_multiplier(self) -> float:
        """
        Interface to get greenhouse gas multiplier through the full world instead of this abstract world
        """
        return self.full_world.ghg_multiplier

    @property
    def albedo_multiplier(self) -> float:
        """
        Interface to get albedo multiplier through the full world instead of this abstract world
        """
        return self.full_world.albedo_multiplier


class full_world_handler(world_handlers.world_handler):
    """
    World handler corresponding to a world with a full playable map, with >1 locations
    """

    def __init__(self, from_save: bool, input_dict: Dict[str, Any]) -> None:
        """
        Description:
            Initializes this object
        Input:
            bool from_save: True if loading world, False if creating new one
            dictionary input_dict: Dictionary of saved information necessary to recreate this location if loading grid, or None if creating new location
        Output:
            None
        """
        super().__init__(from_save, input_dict)

        constants.EventBus.subscribe(
            self.update_average_water,
            self.uuid,
            constants.LOCATION_SET_PARAMETER_ROUTE,
            constants.WATER,
        )  # Subscribes for update_average_water to be invoked whenever the water of any location in this world is set
        constants.EventBus.subscribe(
            self.update_globe_projection, constants.UPDATE_MAP_MODE_ROUTE
        )  # Subscribes for globe projection to be updated whenever the map mode is changed
        for current_location in self.get_flat_location_list():
            current_location.find_adjacent_locations()

        self.latitude_lines_setup()

        if not from_save:  # Initial full world generation
            if constants.EffectManager.effect_active("benchmark_world_creation"):
                start_time = time.time()
                print(f"Starting world creation at time: {start_time}")
            self.update_sky_color(set_initial_offset=True, update_water=True)
            self.generate_poles_and_equator()
            self.generate_terrain_parameters()
            self.generate_terrain_features()
            for location in self.get_flat_location_list():
                location.local_weather_offset = (
                    location.expected_temperature_offset + random.uniform(-0.4, 0.4)
                )
            self.apply_low_pressure()
            self.apply_radiation()
            self.simulate_climate_equilibrium()
            if constants.EffectManager.effect_active("benchmark_world_creation"):
                end_time = time.time()
                elapsed = end_time - start_time
                elapsed_per_location = elapsed / (self.world_dimensions**2)
                print(
                    f"Finished world creation at time: {end_time}, took {round(elapsed, 2)} seconds ({round(elapsed_per_location, 6)} seconds per location)"
                )

        self.orbital_world: orbital_world_handler = (
            constants.ActorCreationManager.create(
                from_save,
                {
                    **input_dict.get("orbital_world", {}),
                    "init_type": constants.ORBITAL_WORLD,
                    "full_world": self,
                },
            )
        )

    def generate_terrain_parameters(self):
        """
        Randomly sets terrain parameters for each cell
        """
        self.generate_altitude()
        self.generate_roughness()
        self.generate_temperature()
        self.generate_water()
        self.generate_soil()
        self.generate_vegetation()

    def generate_altitude(self) -> None:
        """
        Randomly generates altitude
        """
        if constants.EffectManager.effect_active("map_customization"):
            default_altitude = 2
        else:
            default_altitude = 0
        for location in self.get_flat_location_list():
            location.set_parameter(
                constants.ALTITUDE, default_altitude, update_display=False
            )

        if constants.EffectManager.effect_active("map_customization"):
            return

        for i in range(constants.TerrainManager.get_tuning("altitude_worms")):
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
        Randomly generates temperature
        """
        self.update_target_average_temperature(estimate_water_vapor=True)
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
        self.simulate_climate_equilibrium(
            estimate_water_vapor=True, update_cloud_images=False
        )

    def generate_roughness(self) -> None:
        """
        Randomly generates roughness
        """
        if constants.EffectManager.effect_active("map_customization"):
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
        Randomly generates water, placing enough water to reach the generated target average
            Total water may be less than target average if repeatedly attempting to place in saturated locations, or if radiation removes some of the placed water
        """
        for _ in range(round(self.average_water_target * (self.world_dimensions**2))):
            self.place_water(update_display=False, during_setup=True)
        if constants.EffectManager.effect_active("map_customization"):
            attempts = 0
            while attempts < 10000 and not self.find_average(constants.WATER) == 5.0:
                self.place_water(update_display=False, during_setup=True)
                attempts += 1

    def apply_radiation(self) -> None:
        """
        Applies radiation effects to water, particularly non-frozen water, based on unmitigated radiation
        """
        radiation_effect = max(
            0,
            self.get_parameter(constants.RADIATION)
            - self.get_parameter(constants.MAGNETIC_FIELD),
        )
        if radiation_effect > 0:
            for current_location in self.get_flat_location_list():
                if current_location.get_parameter(
                    constants.TEMPERATURE
                ) <= self.get_tuning("water_freezing_point"):
                    if current_location.get_parameter(
                        constants.TEMPERATURE
                    ) == self.get_tuning(
                        "water_freezing_point"
                    ):  # Lose most water if sometimes above freezing
                        if radiation_effect >= 3:
                            retention_chance = 1 / 3
                        else:
                            retention_chance = 2 / 3
                    else:  # If far below freezing, retain water regardless of radiation
                        retention_chance = 1
                else:  # If consistently above freezing
                    if (
                        radiation_effect >= 3
                    ):  # Lose almost all water if consistently above freezing
                        retention_chance = 1 / 12
                    elif (
                        radiation_effect >= 1
                    ):  # Lose most water if consistently above freezing
                        retention_chance = 1 / 3
                water_retained = sum(
                    random.random() < retention_chance
                    for _ in range(current_location.get_parameter(constants.WATER))
                )
                current_location.set_parameter(
                    constants.WATER, water_retained, update_display=False
                )
                current_location.flow()

    def apply_low_pressure(self) -> None:
        """
        If insufficient pressure, any evaporated water is lost
        """
        if self.get_pressure_ratio() < 0.05:
            for current_location in self.get_flat_location_list():
                if current_location.get_parameter(
                    constants.TEMPERATURE
                ) >= self.get_tuning("water_freezing_point"):
                    current_location.set_parameter(
                        constants.WATER, 0, update_display=False
                    )

    def place_water(
        self,
        update_display: bool = True,
        during_setup: bool = False,
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
            if candidate.get_parameter(constants.WATER) < 5 and candidate.get_parameter(
                constants.TEMPERATURE
            ) >= self.get_tuning("water_freezing_point"):
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
                    candidate.get_parameter(constants.TEMPERATURE)
                    <= self.get_tuning("water_freezing_point") - 1
                ):  # Water can go to coldest freezing location
                    if best_frozen == None or candidate.get_parameter(
                        constants.TEMPERATURE
                    ) < best_frozen.get_parameter(constants.TEMPERATURE):
                        best_frozen = candidate
        if best_frozen == None and best_liquid == None and best_gas == None:
            self.place_water(update_display=update_display)
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
        choice.change_parameter(constants.WATER, 1, update_display=update_display)
        if during_setup and choice.get_parameter(
            constants.TEMPERATURE
        ) >= self.get_tuning("water_freezing_point"):
            choice.flow()

    def remove_water(self, update_display: bool = True) -> None:
        """
        Removes 1 unit of water from the map, depending on altitude and temperature
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
        Randomly generates soil
        """
        if constants.EffectManager.effect_active("map_customization"):
            return
        if constants.EffectManager.effect_active("earth_preset"):
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
        Randomly generates vegetation
        """
        if constants.EffectManager.effect_active("map_customization"):
            return
        if constants.EffectManager.effect_active("earth_preset"):
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
        Warms the grid, increasing temperature
            Selects the cell with the furthest temperature below its expected temperature
        """
        self.place_temperature(change=1, bound=11, choice_function=min)

    def cool(self) -> None:
        """
        Cools the grid, decreasing temperature
            Selects the cell with the furthest temperature above its expected temperature
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
        Randomly place features in each location, based on terrain
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
        Generates the poles and equator for the world grid
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
            while (
                self.average_temperature < self.get_average_local_temperature()
                and self.get_average_local_temperature() > -5.5
            ):
                self.cool()
            self.bound(
                constants.TEMPERATURE,
                round(self.average_temperature)
                - self.get_tuning("final_temperature_variations")[0],
                round(self.average_temperature)
                + self.get_tuning("final_temperature_variations")[1],
            )
            self.smooth(constants.TEMPERATURE)

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
            update_water: Whether to update the water color of local terrains
        Output:
            None
        """
        earth_sky_color = self.get_tuning("earth_sky_color")
        current_atmosphere_offset = 0
        for atmosphere_component in constants.ATMOSPHERE_COMPONENTS:
            if self.get_parameter(constants.PRESSURE) == 0:
                composition = 0.01
            else:
                composition = self.get_composition(atmosphere_component)
            ideal = self.get_tuning(f"earth_{atmosphere_component}")
            if atmosphere_component == constants.TOXIC_GASES:
                offset = max(0, (composition - 0.001) / 0.005)
                # Increase offset by 1 for each 0.5% above ideal composition
            elif atmosphere_component == constants.GHG:
                offset = max(0, (composition - 0.025) / 0.2)
                # Increase offset by 1 for each 20% above ideal composition
            else:
                offset = abs(composition - ideal) / ideal
                # Increase offset by 1 for each set of ideal composition excess or missing
            current_atmosphere_offset += offset
        if set_initial_offset:
            self.initial_atmosphere_offset = max(5.0, current_atmosphere_offset)
            self.current_atmosphere_offset = self.initial_atmosphere_offset

        delta_offset = abs(self.current_atmosphere_offset - current_atmosphere_offset)
        if (
            abs(self.current_atmosphere_offset - current_atmosphere_offset) < 0.01
            and not set_initial_offset
        ):
            if constants.EffectManager.effect_active("debug_atmosphere_update"):
                print(
                    f"Skipping sky color update from atmosphere offset {round(self.current_atmosphere_offset, 2)} to {round(current_atmosphere_offset, 2)} (delta: {round(delta_offset, 2)})"
                )
            return
        else:
            if constants.EffectManager.effect_active("debug_atmosphere_update"):
                print(
                    f"Updating sky color from atmosphere offset {round(self.current_atmosphere_offset, 2)} to {round(current_atmosphere_offset, 2)} (delta: {round(delta_offset, 2)})"
                )

        # Record total offset in each call - only update colors if total offset changed
        self.current_atmosphere_offset = min(
            current_atmosphere_offset, self.initial_atmosphere_offset
        )
        progress = (self.initial_atmosphere_offset - self.current_atmosphere_offset) / (
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
            self.update_location_image_bundles(update_globe=False)

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
        Creates random clouds for each location, with frequency depending on water vapor
        """
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
        # Toxic cloud frequency depends on both toxic gas % and total pressure

        pressure_alpha = max(0, self.get_pressure_ratio() * 7 - 14)
        toxic_alpha = min(
            255, math.log(1 + (self.get_pressure_ratio(constants.TOXIC_GASES)), 2) * 255
        )
        self.atmosphere_haze_alpha = min(255, pressure_alpha + toxic_alpha)
        # Atmosphere haze depends on total pressure, with toxic gases greatly over-represented

    def update_clouds(self) -> None:
        """
        Creates random cloud images for each location, with frequency depending on water vapor
            Purely cosmetic
        """
        num_cloud_variants = constants.TerrainManager.terrain_variant_dict.get(
            "clouds_base", 1
        )
        num_solid_cloud_variants = constants.TerrainManager.terrain_variant_dict.get(
            "clouds_solid", 1
        )
        for location in self.get_flat_location_list():
            location.update_clouds(num_cloud_variants, num_solid_cloud_variants)

        if not flags.loading:
            status.current_world.update_globe_projection(update_button=True)

    def update_albedo_effect_multiplier(self):
        """
        Re-calculates the albedo multiplier to heat received by this planet, based on clouds and location brightnesss
        """
        # self.update_location_image_bundles(update_globe=False)
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

    def remove(self) -> None:
        """
        Removes this object from relevant lists, prevents it from further appearing in or affecting the program, and removes it from the location it occupies
        """
        super().remove()
        constants.EventBus.unsubscribe(
            self.update_average_water,
            self.uuid,
            constants.LOCATION_SET_PARAMETER_ROUTE,
            constants.WATER,
        )
        constants.EventBus.unsubscribe(
            self.update_globe_projection,
            constants.UPDATE_MAP_MODE_ROUTE,
        )

    def to_save_dict(self) -> Dict[str, Any]:
        """
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
        """
        return {
            **super().to_save_dict(),
            "orbital_world": self.orbital_world.to_save_dict(),
            "init_type": constants.FULL_WORLD,
        }

    def update_location_image_bundles(self, update_globe: bool = True) -> None:
        """
        Description:
            Manually updates all of this world's location image bundles and the globe projection
        Input:
            bool update_globe: True if the globe projection should also be updated
        Output:
            None
        """
        super().update_location_image_bundles(update_globe=update_globe)
        if update_globe:
            self.update_globe_projection(
                center_coordinates=(
                    status.scrolling_strategic_map_grid.center_x,
                    status.scrolling_strategic_map_grid.center_y,
                ),
                update_button=True,
            )

    def simulate_climate_equilibrium(
        self,
        max_iterations: int = 10,
        update_cloud_images: bool = True,
        estimate_water_vapor: bool = False,
    ) -> None:
        """
        Description:
            Simulates the temperature equilibrium of the world by updating the target average temperature and changing to that target
        Input:
            int iterations: Maximum number of iterations to simulate
            bool update_cloud_images: True if the cloud images should be updated after the simulation
            boolean estimate_water_vapor: Whether to estimate the water vapor contribution or to directly calculate
                Setting up temperature before water requires estimating water vapor amount
        Output:
            None
        """
        if constants.EffectManager.effect_active("benchmark_climate_simulation"):
            start_time = time.time()
            print(f"Starting climate simulation at time: {start_time}")

        self.update_sky_color(update_water=True)
        # Note that update_sky_color with update_water is a very expensive operation

        for i in range(max_iterations):
            self.update_cloud_frequencies()  # Update haze and frequency of clouds for albedo calculations
            # Cloud frequency depends on local parameters and could've been affected over the past turn and the last iteration

            self.update_albedo_effect_multiplier()
            # Albedo effect multiplier depends on local parameters and cloud frequency

            if constants.EffectManager.effect_active("debug_atmosphere_update"):
                print(f"Simulating atmosphere equilibrium: iteration {i + 1}")
            initial_average_temperature = self.average_temperature
            self.update_target_average_temperature(
                estimate_water_vapor=estimate_water_vapor
            )
            if abs(initial_average_temperature - self.average_temperature) < 0.01:
                if constants.EffectManager.effect_active("debug_atmosphere_update"):
                    print(
                        f"Skipping temperature change for {round(utility.fahrenheit(initial_average_temperature), 2)} °F to target {round(utility.fahrenheit(self.average_temperature), 2)} °F"
                    )
                    print(
                        f"Atmosphere equilibrium reached at {round(utility.fahrenheit(self.average_temperature), 2)} °F"
                    )
                break
            else:
                if constants.EffectManager.effect_active("debug_atmosphere_update"):
                    print(
                        f"Changing temperature from {round(utility.fahrenheit(initial_average_temperature), 2)} °F to target {round(utility.fahrenheit(self.average_temperature), 2)} °F"
                    )
            self.change_to_temperature_target(estimate_water_vapor=estimate_water_vapor)
            # Note that the act of changing to the temperature target can shift the temperature target for future iterations
        if update_cloud_images:
            self.update_clouds()  # Update actual cloud images
        if constants.EffectManager.effect_active("benchmark_climate_simulation"):
            end_time = time.time()
            elapsed = end_time - start_time
            elapsed_per_location = elapsed / (self.world_dimensions**2)
            print(
                f"Finished climate simulation at time: {end_time}, took {round(elapsed, 2)} seconds ({round(elapsed_per_location, 6)} seconds per location)"
            )

    def latitude_lines_setup(self):
        """
        15 x 15 grid has north pole 0, 0 and south pole 7, 7
        If centered at (11, 11), latitude line should include (0, 0), (14, 14), (13, 13), (12, 12), (11, 11), (10, 10), (9, 9), (8, 8), (7, 7)
            The above line should be used if centered at any of the above coordinates
        If centered at (3, 11), latitude line should include (0, 0), (1, 14), (1, 13), (2, 12), (3, 11), (4, 10), (5, 9), (6, 8), (7, 7)

        Need to draw latitude lines using the above method, centered on (0, 7), (1, 6), (2, 5), (3, 4), (4, 3), (5, 2), (6, 1), (7, 0), (8, 14), (9, 13), (10, 12), (11, 11), (12, 10), (13, 9), (14, 8)
            ^ Forms diagonal line
        Also need to draw latitude lines on other cross: (0, 8), (1, 9), (2, 10), (3, 11), (4, 12), (5, 13), (6, 14), (7, 0), (8, 1), (9, 2), (10, 3), (11, 4), (12, 5), (13, 6), (14, 7)
        """
        if self.is_abstract_world:
            return
        self.latitude_lines = []
        self.alternate_latitude_lines = []
        self.latitude_lines_types = [
            [None for _ in range(self.world_dimensions)]
            for _ in range(self.world_dimensions)
        ]
        north_pole = (0, 0)
        south_pole = (
            self.world_dimensions // 2,
            self.world_dimensions // 2,
        )
        self.equatorial_coordinates = []
        self.alternate_equatorial_coordinates = []
        for equatorial_x in range(self.world_dimensions):
            equatorial_y = (
                (self.world_dimensions // 2) - equatorial_x
            ) % self.world_dimensions
            current_line = self.draw_coordinate_line(
                north_pole, (equatorial_x, equatorial_y)
            ) + self.draw_coordinate_line(
                (equatorial_x, equatorial_y), south_pole, omit_origin=True
            )
            for coordinate in current_line:
                self.latitude_lines_types[coordinate[0]][coordinate[1]] = True
            self.latitude_lines.append(current_line)
            self.equatorial_coordinates.append((equatorial_x, equatorial_y))

            equatorial_y = (
                (self.world_dimensions // 2) + equatorial_x + 1
            ) % self.world_dimensions
            current_line = self.draw_coordinate_line(
                north_pole, (equatorial_x, equatorial_y)
            ) + self.draw_coordinate_line(
                (equatorial_x, equatorial_y), south_pole, omit_origin=True
            )
            for coordinate in current_line:
                self.latitude_lines_types[coordinate[0]][coordinate[1]] = False
            self.alternate_latitude_lines.append(current_line)
            self.alternate_equatorial_coordinates.append((equatorial_x, equatorial_y))

    def get_latitude_line(
        self, coordinates: Tuple[int, int]
    ) -> Tuple[int, List[List[Tuple[int, int]]]]:
        """
        Description:
            Finds and returns the latitude line that the inputted coordinates are on
        Input:
            int tuple coordinates: Coordinates to find the latitude line of
        Output:
            int tuple list: Returns a latitude line (list of coordinates from 1 pole to the other) that the inputted coordinates are on
        """
        # Possible sporadic error here - coordinates passed in seem to be out of bounds
        try:
            latitude_line_type = self.latitude_lines_types[coordinates[0]][
                coordinates[1]
            ]
        except:
            constants.SaveLoadManager.save_game("save1.pickle")
            raise IndexError(
                f"Invalid indexes: {coordinates} for world dimensions {self.world_dimensions}. Saved crash report to 'save1.pickle'."
            )
        if latitude_line_type == None:
            for offset in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                latitude_line_type = self.latitude_lines_types[
                    (coordinates[0] + offset[0]) % self.world_dimensions
                ][(coordinates[1] + offset[1]) % self.world_dimensions]
                if latitude_line_type != None:
                    coordinates = (
                        (coordinates[0] + offset[0]) % self.world_dimensions,
                        (coordinates[1] + offset[1]) % self.world_dimensions,
                    )
                    break
        if latitude_line_type == True:
            for idx, latitude_line in enumerate(self.latitude_lines):
                if coordinates in latitude_line:
                    return idx, self.latitude_lines
        else:
            for idx, latitude_line in enumerate(self.alternate_latitude_lines):
                if coordinates in latitude_line:
                    return idx, self.alternate_latitude_lines

    def draw_coordinate_line(
        self,
        origin: Tuple[int, int],
        destination: Tuple[int, int],
        omit_origin: bool = False,
    ) -> List[Tuple[int, int]]:
        """
        Description:
            Finds and returns a list of adjacent/diagonal coordinates leading from the origin to the destination
        Input:
            int tuple origin: Origin coordinate
            int tuple destination: Destination coordinate
            boolean omit_origin: Whether to omit the origin from the list
        Output:
            int tuple list: List of adjacent/diagonal coordinates leading from the origin to the destination
        """
        line = []
        if not omit_origin:
            line.append(origin)
        x, y = origin
        while (x, y) != destination:
            x_distance = self.x_distance_coords(x, destination[0])
            y_distance = self.y_distance_coords(y, destination[1])
            if x_distance != 0:
                slope = y_distance / x_distance

            if x_distance == 0:
                traverse = ["Y"]
            elif y_distance == 0:
                traverse = ["X"]
            elif slope > 2:
                traverse = ["Y"]
            elif slope < 0.5:
                traverse = ["X"]
            else:
                traverse = ["X", "Y"]

            if "X" in traverse:
                if (
                    self.x_distance_coords(
                        (x + 1) % self.world_dimensions, destination[0]
                    )
                    < x_distance
                ):
                    x = (x + 1) % self.world_dimensions
                else:
                    x = (x - 1) % self.world_dimensions
            if "Y" in traverse:
                if (
                    self.y_distance_coords(
                        (y + 1) % self.world_dimensions, destination[1]
                    )
                    < y_distance
                ):
                    y = (y + 1) % self.world_dimensions
                else:
                    y = (y - 1) % self.world_dimensions
            line.append((x, y))
        return line

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
            self.create_planet_image(center_coordinates)
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
        status.current_world.orbital_world.set_image(
            world_utility.generate_abstract_world_image(
                planet=constants.GLOBE_PROJECTION_WORLD
            )
        )

        if update_button:
            status.to_strategic_button.image.set_image(
                actor_utility.generate_frame(
                    world_utility.generate_abstract_world_image(
                        planet=constants.GLOBE_PROJECTION_WORLD,
                        size=0.6,
                    )
                )
            )

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
            center_coordinates = (  # Required here since globe appearance is actually determined based on the state of the interface
                status.scrolling_strategic_map_grid.center_x,
                status.scrolling_strategic_map_grid.center_y,
            )
        index, latitude_lines = self.get_latitude_line(center_coordinates)

        offset_width = self.world_dimensions // 2
        largest_size = len(
            max(
                self.latitude_lines + self.alternate_latitude_lines,
                key=len,
            )
        )
        return_list = []
        for offset in range(offset_width):
            min_width = (
                offset >= offset_width - 1
            )  # If leftmost or rightmost latitude line, use minimum width to avoid edge locations looking too wide
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
                    latitude_lines[(index + offset) % self.world_dimensions],
                    largest_size,
                    longitude_bulge_factor=longitude_bulge_factor,
                    level=offset + 20,
                    min_width=min_width,
                    offset=offset,
                    offset_width=offset_width,
                )
                return_list += self.draw_latitude_line(
                    latitude_lines[(index - offset) % self.world_dimensions],
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
            constants.world_dimensions_options.index(max_latitude_line_length)
        ]
        base_location_width = 0.10
        base_location_height = 0.12

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
            constants.earth_dimensions**0.5
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
            if max_latitude_line_length >= constants.world_dimensions_options[-3]:
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
                max_latitude_line_length <= constants.world_dimensions_options[1]
            ):  # Increase height for smaller maps to avoid empty space near poles
                height_penalty *= 0.6
            if max_latitude_line_length >= constants.world_dimensions_options[-3]:
                width_penalty *= 2
            location_width, location_height = (
                base_location_width - width_penalty,
                base_location_height - height_penalty,
            )
            location_width *= 0.8
            if (
                min_width
            ) and pole_distance_factor > 0.1:  # Since rightmost (highest level) latitude line is not covered by any others, it should be thinner to avoid an obvious size difference
                location_width = 0.015
            location_height = max(0.02, 0.08 - height_penalty)
            projection = {
                "x_offset": (center_position[0] + x_offset) * size_multiplier,
                "y_offset": (center_position[1] + y_offset) * size_multiplier,
                "x_size": location_width * size_multiplier,
                "y_size": location_height * size_multiplier,
                "level": level,
            }
            for base_image_id in self.find_location(*coordinates).image_dict[
                constants.IMAGE_ID_LIST_ORBITAL_VIEW
            ]:
                # Apply projection offsets to each image in the location's terrain
                if type(base_image_id) == str:
                    base_image_id = {"image_id": base_image_id}
                image_id = base_image_id.copy()
                image_id.update(projection)
                return_list.append(image_id)

            if (
                self.get_pressure_ratio() > 10.0
            ):  # If high pressure, also have sky effects for 3rd farthest latitude line
                threshold = 3
            else:  # If normal or low pressure, only have sky effects for 2nd farthest latitude line
                threshold = 2
            if (
                (offset_width - offset <= threshold and not min_width)
                and self.get_parameter(constants.PRESSURE) > 0
                and constants.current_map_mode == "terrain"
            ):  # If 2nd farthest latitude line
                sky_effect = {
                    "image_id": "misc/green_screen_base.png",
                    "detail_level": 1.0,
                    "green_screen": tuple(self.sky_color),
                }
                sky_effect.update(projection)
                sky_effect["level"] += 10
                if threshold <= 3 or abs(longitude_bulge_factor) > 0.5:
                    sky_effect["x_size"] *= 0.4

                sky_effect["alpha"] = 75
                pressure_ratio = self.get_pressure_ratio()
                if pressure_ratio <= 1.0:  # More transparent for lower pressure
                    sky_effect["alpha"] = 50 + int(25 * min(pressure_ratio, 1))
                else:  # Less transparent for higher pressure
                    sky_effect["alpha"] = 75 + int(
                        25 * min((pressure_ratio - 1) / 99, 1)
                    )
                if offset != 0:
                    x_offset_magnitude = 0.02
                    if (
                        max_latitude_line_length
                        <= constants.world_dimensions_options[1]
                    ):
                        x_offset_magnitude *= 1.6
                    elif (
                        max_latitude_line_length
                        >= constants.world_dimensions_options[5]
                    ):
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
                Reduces latitude distortions (locations appear at accurate latitudes, slightly distorted to bulge equator) but misses some locations
            If mode is closest_unerpresnted, scans a latitude line for any nearby coordinates that have no latitude line, allowing extending a latitude line's length while also missing fewer cells
                Misses fewer coordinates but introduces latitude distortions (locations appearing at significantly inaccurate latitude)
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
                        self.latitude_lines_types[adjacent_coordinates[0]][
                            adjacent_coordinates[1]
                        ]
                        == None
                        and not adjacent_coordinates in latitude_line
                    ):
                        # If wouldn't be shown in any latitude lines, show here
                        inserted_coordinates = adjacent_coordinates
                        inserted_idx = idx
        return inserted_idx, inserted_coordinates
