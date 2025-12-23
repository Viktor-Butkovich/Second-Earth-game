from __future__ import annotations
import itertools
from math import log
from typing import List, Dict, Any
from modules.util import utility, actor_utility
from modules.constructs import terrain_types
from modules.constructs.actor_types import locations
from modules.constants import constants, status, flags


class world_handler:
    """
    "Single source of truth" handler for planet-wide characteristics
    Can be a full world with multiple locations, an orbital world representing a planet's orbit, or an abstract world for
        a single-location world
    """

    def __init__(self, from_save: bool, input_dict: Dict[str, any]) -> None:
        """
        Description:
            Initializes this object
        Input:
            bool from_save: True if loading world, False if creating new one
            dictionary input_dict: Dictionary of saved information necessary to recreate this location if loading grid, or None if creating new location
        Output:
            None
        """
        from modules.interface_components import grids

        self.uuid: str = constants.UuidManager.assign_uuid()
        status.world_list.append(self)
        self.subscribed_grids: List[grids.grid] = []
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
            self.current_atmosphere_offset = input_dict.get(
                "current_atmosphere_offset", self.initial_atmosphere_offset
            )
            for key in constants.global_parameters:
                self.set_parameter(
                    key, input_dict.get("global_parameters", {}).get(key, 0)
                )
            self.average_temperature: float = input_dict.get("average_temperature", 0.0)

        self.location_list: List[locations.location] = []
        if from_save:
            self.location_list = [
                [
                    constants.ActorCreationManager.create(
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
                    constants.ActorCreationManager.create(
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

    @property
    def coordinate_width(self) -> int:
        """
        Returns this world's coordinate width
        """
        return self.world_dimensions

    @property
    def coordinate_height(self) -> int:
        """
        Returns this world's coordinate height
        """
        return self.world_dimensions

    @property
    def is_earth(self) -> bool:
        """
        Returns whether this is the Earth abstract world - False unless overridden by subclass
        """
        return False

    @property
    def is_abstract_world(self) -> bool:
        """
        Returns whether this is an abstract world - False unless overridden by subclass
        """
        return False

    @property
    def is_orbital_world(self) -> bool:
        """
        Returns whether this is an orbital world - False unless overridden by subclass
        """
        return False

    def configure_event_subscriptions(self) -> None:
        """
        Subscribes events related to this location, triggering updates to respond to dependency changes
        """
        constants.EventBus.subscribe(
            self.update_contained_mob_habitability,
            self.uuid,
            constants.WORLD_SET_PARAMETER_ROUTE,
        )  # Update contained mob habitability when world parameters change

    def remove(self) -> None:
        """
        Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        """
        status.world_list.remove(self)
        for current_location in self.get_flat_location_list():
            current_location.remove()

    def update_location_image_bundles(self, update_globe: bool = False) -> None:
        """
        Description:
            Manually updates all of this world's location image bundles
        Input:
            bool update_globe: True if the globe projection should also be updated (only used by subclasses)
        Output:
            None
        """
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

    def subscribe_grid(self, grid: Any) -> None:
        """
        Description:
            Subscribes the inputted grid to this world, removing it from any previous world
                Grids instruct their cells to subscribe to the corresponding locations in this world
        Input:
            grid grid: Grid to subscribe to this world
        Output:
            None
        """
        self.subscribed_grids.append(grid)
        grid.world_handler = self

    def unsubscribe_grid(self, grid: Any) -> None:
        """
        Description:
            Unsubscribes the inputted grid from this location - precondition that grid is subscribed to this location
        Input:
            grid grid: Grid to unsubscribe from this location
        Output:
            None
        """
        self.subscribed_grids.remove(grid)
        grid.world_handler = None

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
        constants.EventBus.publish(self.uuid, constants.WORLD_SET_PARAMETER_ROUTE)

    def update_contained_mob_habitability(self) -> None:
        """
        Updates the habitability of all contained mobs in this world
        """
        for current_mob in status.mob_list:
            if current_mob.location.true_world_handler == self:
                current_mob.update_habitability()

    def update_pressure(self) -> None:
        """
        Updates the planet's pressure to be a sum of its atmosphere components whenever any are changed
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
        return constants.TerrainManager.get_tuning(tuning_type)

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
            "current_atmosphere_offset": self.current_atmosphere_offset,
            "star_distance": self.star_distance,
            "water_vapor_multiplier": self.water_vapor_multiplier,
            "ghg_multiplier": self.ghg_multiplier,
            "albedo_multiplier": self.albedo_multiplier,
            "cloud_frequency": self.cloud_frequency,
            "toxic_cloud_frequency": self.toxic_cloud_frequency,
            "atmosphere_haze_alpha": self.atmosphere_haze_alpha,
        }

    def get_green_screen(
        self, terrain_type: terrain_types.terrain_type = None
    ) -> Dict[str, Dict[str, any]]:
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
        Re-calculates the average temperature of this world
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
        Re-calculates the average water of this world
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
        Re-calculates the average altitude of this world
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

    def update_target_average_temperature(self, estimate_water_vapor: bool = False):
        """
        Re-calculates the average temperature of this world, based on sun distance -> solation and greenhouse effect
            This average temperature is used as a target, changing local temperature until the average is reached
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

        fahrenheit = (
            ghg_multiplier
            * water_vapor_multiplier
            * self.albedo_multiplier
            * self.get_sun_effect()
        ) + constants.ABSOLUTE_ZERO
        self.average_temperature = utility.reverse_fahrenheit(fahrenheit)
        constants.EventBus.publish(
            self.uuid, constants.WORLD_UPDATE_TARGET_AVERAGE_TEMPERATURE_ROUTE
        )
