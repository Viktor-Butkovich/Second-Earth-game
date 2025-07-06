import random
import math
from typing import List, Dict, Any
from modules.util import actor_utility, main_loop_utility, utility
from modules.constructs.actor_types import actors
from modules.constructs import world_handlers, item_types, settlements
from modules.constants import constants, status, flags


class location(actors.actor):
    """
    "Single source of truth" handler for the terrain/local characteristics of part of a world
    """

    def __init__(
        self,
        from_save: bool,
        input_dict: Dict[str, any],
        original_constructor: bool = True,
    ) -> None:
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Dictionary of saved information necessary to recreate this location if loading grid, or None if creating new location
        Output:
            None
        """
        self.parent_world_handler: world_handlers.world_handler = input_dict[
            "world_handler"
        ]
        self.name_icon = None
        self.hosted_icons = []
        super().__init__(from_save, input_dict, original_constructor == False)
        self.image_dict = {**self.image_dict, constants.IMAGE_ID_LIST_INCLUDE_MOB: []}
        self.x: int = input_dict["coordinates"][0]
        self.y: int = input_dict["coordinates"][1]
        self.adjacent_list: List[location] = []
        self.adjacent_locations: Dict[str, location] = {}
        self.terrain_parameters: Dict[str, int] = input_dict.get(
            "terrain_parameters",
            {
                constants.KNOWLEDGE: 0,
                constants.ALTITUDE: 0,
                constants.TEMPERATURE: 0,
                constants.ROUGHNESS: 0,
                constants.VEGETATION: 0,
                constants.SOIL: 0,
                constants.WATER: 0,
            },
        )
        self.local_weather_offset = input_dict.get(
            "local_weather_offset", random.uniform(-0.2, 0.2)
        )
        self.terrain_variant: int = input_dict.get("terrain_variant", 0)
        self.current_clouds: List[Dict[str, any]] = input_dict.get("current_clouds", [])
        self.pole_distance_multiplier: float = input_dict.get(
            "pole_distance_multiplier", 1.0
        )  # 0.1 for polar cells, 1.0 for equatorial cells
        self.north_pole_distance_multiplier: float = input_dict.get(
            "north_pole_distance_multiplier", 1.0
        )
        self.inverse_pole_distance_multiplier: float = 1.0
        self.minima = {constants.TEMPERATURE: -6}
        self.maxima = {constants.TEMPERATURE: 11}
        self.terrain: str = None
        self.terrain_features: Dict[str, bool] = {}
        for terrain_feature in input_dict.get("terrain_features", {}).values():
            self.add_terrain_feature(terrain_feature)
        self.set_terrain(
            constants.TerrainManager.classify(self.terrain_parameters),
            update_image_bundle=False,
        )
        self.resource: item_types.item_type = status.item_types.get(
            input_dict.get("resource", None), None
        )
        self.subscribed_cells: list = []
        self.expected_temperature_offset: float = 0.0
        self.subscribed_mobs: List[actors.actor] = (
            []
        )  # List of top-level contained mobs
        self.contained_buildings: Dict[str, Any] = {}
        self.settlement: settlements.settlement = None
        if from_save:
            for current_mob_dict in input_dict.get("subscribed_mobs", []):
                constants.ActorCreationManager.create(
                    from_save=True,
                    input_dict={
                        **current_mob_dict,
                        "location": self,
                    },
                )
            for current_building_dict in input_dict.get("contained_buildings", []):
                constants.ActorCreationManager.create(
                    from_save=True,
                    input_dict={
                        **current_building_dict,
                        "location": self,
                    },
                )
            if input_dict.get("settlement", None):
                constants.ActorCreationManager.create(
                    from_save=True,
                    input_dict={
                        **input_dict["settlement"],
                        "location": self,
                    },
                )
        self.configure_event_subscriptions()
        self.update_image_bundle()

    @property
    def actor_type(self) -> str:
        """
        Returns this object's actor type, differentiating it from mobs and ministers
        """
        return constants.LOCATION_ACTOR_TYPE

    @property
    def contained_mobs(self) -> List[Any]:
        """
        All mobs contained within this actor
            Can use instead of manually finding all mobs somewhere, even ones that are not directly subscribed to the location
        """
        contained_mobs = []
        for current_mob in self.subscribed_mobs:
            contained_mobs += current_mob.contained_mobs
        if self.get_building(constants.RESOURCE):
            contained_mobs += self.get_building(constants.RESOURCE).contained_mobs
        return contained_mobs

    @property
    def is_abstract_location(self) -> bool:
        """
        Returns whether this is the single location of an abstract world, or part of a full world
        """
        return self.world_handler.is_abstract_world

    @property
    def is_earth_location(self) -> bool:
        """
        Returns whether this is the Earth abstract world location
        """
        return self.true_world_handler.is_earth

    @property
    def infinite_inventory_capacity(self) -> bool:
        """
        Returns whether this location has infinite inventory capacity
            Earth has infinite inventory capacity
        """
        return self.is_earth_location

    @property
    def insufficient_inventory_capacity(self) -> bool:
        """
        Returns whether this location's inventory exceeds its inventory capacity
        """
        return (
            not self.infinite_inventory_capacity
        ) and self.get_inventory_used() > self.inventory_capacity

    def configure_event_subscriptions(self) -> None:
        """
        Subscribes events related to this location, triggering updates to respond to dependency changes
        """
        constants.EventBus.subscribe(
            self.update_image_bundle, self.uuid, constants.LOCATION_ADD_BUILDING_ROUTE
        )  # Update image bundle when building is added
        constants.EventBus.subscribe(
            self.update_image_bundle,
            self.uuid,
            constants.LOCATION_REMOVE_BUILDING_ROUTE,
        )  # Update image bundle when building is removed from
        constants.EventBus.subscribe(
            self.update_image_bundle, self.uuid, constants.LOCATION_SET_PARAMETER_ROUTE
        )  # Update image bundle when terrain parameters change
        constants.EventBus.subscribe(
            self.update_image_bundle, self.uuid, constants.LOCATION_SUBSCRIBE_MOB_ROUTE
        )  # Update image bundle when subscribing a mob
        constants.EventBus.subscribe(
            self.update_image_bundle,
            self.uuid,
            constants.LOCATION_UNSUBSCRIBE_MOB_ROUTE,
        )  # Update image bundle when unsubscribing a mob
        constants.EventBus.subscribe(
            self.update_image_bundle, self.uuid, constants.LOCATION_SET_NAME_ROUTE
        )  # Update image bundle when setting name
        constants.EventBus.subscribe(
            self.update_image_bundle, self.uuid, constants.LOCATION_UPDATE_CLOUDS_ROUTE
        )  # Update image bundle when clouds change
        constants.EventBus.subscribe(
            self.update_image_bundle,
            self.uuid,
            constants.UPDATE_TERRAIN_FEATURE_ROUTE,
        )  # Update image bundle when terrain features change
        if self.is_abstract_location:
            constants.EventBus.subscribe(
                self.update_image_bundle,
                self.world_handler.uuid,
                constants.ABSTRACT_WORLD_UPDATE_IMAGE_ROUTE,
            )  # If abstract location, update image bundle when abstract world does
        else:
            constants.EventBus.subscribe(
                self.update_image_bundle, constants.UPDATE_MAP_MODE_ROUTE
            )  # If not abstract location, update image bundle when map mode changes
            constants.EventBus.subscribe(
                self.update_expected_temperature_offset,
                self.uuid,
                constants.LOCATION_SET_PARAMETER_ROUTE,
                constants.TEMPERATURE,
            )  # Update offset from expected temperature when local temperature changes
            constants.EventBus.subscribe(
                self.update_expected_temperature_offset,
                self.world_handler.uuid,
                constants.WORLD_UPDATE_TARGET_AVERAGE_TEMPERATURE_ROUTE,
            )  # Update offset from expected temperature when world's target average temperature changes
        constants.EventBus.subscribe(
            self.update_contained_mob_habitability,
            self.uuid,
            constants.LOCATION_SET_PARAMETER_ROUTE,
        )  # Update contained mob habitability when terrain parameters change

    def update_expected_temperature_offset(self) -> None:
        """
        Updates this location's deviation from the expected temperature for the region and climate
        When location temperatures change, those that most deviate from expected are selected first
        Upon world creation, local temperature variations are preserved as "local weather", ensuring variety while
            still detecting deviation from expected as conditions change
        """
        self.expected_temperature_offset = (
            self.get_parameter(constants.TEMPERATURE) - self.get_expected_temperature()
        )

    def local_attrition(self, attrition_type="health"):
        """
        Description:
            Returns the result of a roll that determines if a given unit or set of stored items should suffer attrition based on this location's terrain and buildings. Bad terrain increases attrition frequency while infrastructure
                decreases it
        Input:
            string attrition_type = 'health': 'health' or 'inventory', refers to type of attrition being tested for. Used because inventory attrition can occur on Earth but not health attrition
        Output:
            boolean: Returns whether attrition should happen here based on this location's terrain and buildings
        """
        if (
            constants.EffectManager.effect_active("boost_attrition")
            and random.randrange(1, 7) >= 4
        ):
            return True
        if self.is_earth_location:
            if attrition_type == "health":  # No health attrition on Earth
                return False
            elif (
                attrition_type == "inventory"
            ):  # losing inventory in warehouses and such is uncommon but not impossible on Earth, but no health attrition on Earth
                if (
                    random.randrange(1, 7) >= 2 or random.randrange(1, 7) >= 3
                ):  # same effect as clear area with port
                    return False
        else:
            if random.randrange(1, 7) <= min(
                self.get_habitability_dict(omit_perfect=False).values()
            ):
                # Attrition only occurs if a random roll is higher than the habitability - more attrition for worse habitability
                return False

            if (
                self.has_building(constants.TRAIN_STATION)
                or self.has_building(constants.SPACEPORT)
                or self.has_building(constants.RESOURCE)
                or self.has_building(constants.FORT)
            ):
                if random.randrange(1, 7) >= 3:  # removes 2/3 of attrition
                    return False
            elif self.has_building(constants.ROAD) or self.has_building(
                constants.RAILROAD
            ):
                if random.randrange(1, 7) >= 5:  # removes 1/3 of attrition
                    return False
        return True

    def remove(self) -> None:
        """
        Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        """
        super().remove()
        for cell in self.subscribed_cells.copy():
            self.unsubscribe_cell(cell)
        for mob in self.subscribed_mobs.copy():
            mob.remove()
        for building in self.contained_buildings.copy().values():
            building.remove()

    def has_building(self, building_type: str) -> bool:
        """
        Description:
            Returns whether this location has a building of the inputted type, even if the building is damaged
        Input:
            string building_type: type of building to search for
        Output:
            boolean: Returns whether this location has a building of the inputted type
        """
        if building_type in [constants.ROAD, constants.RAILROAD]:
            return self.has_building(constants.INFRASTRUCTURE)
        else:
            return bool(self.contained_buildings.get(building_type, None))

    def has_intact_building(self, building_type: str) -> bool:
        """
        Description:
            Returns whether this location has an undamaged building of the inputted type
        Input:
            string building_type: Type of building to search for
        Output:
            boolean: Returns whether this location has an undamaged building of the inputted type
        """
        if building_type in [constants.ROAD, constants.RAILROAD]:
            return self.has_intact_building(constants.INFRASTRUCTURE)
        else:
            present_building = self.get_building(building_type)
            return present_building and not present_building.damaged

    def add_building(self, building: Any) -> None:
        """
        Description:
            Adds the inputted building to this location
        Input:
            building building: Building to add to this location
        Output:
            None
        """
        self.contained_buildings[building.building_type.key] = building

        constants.EventBus.subscribe(
            self.update_image_bundle,
            building.uuid,
            constants.BUILDING_SET_DAMAGED_ROUTE,
        )
        # Update image bundle when building's damaged status changes

        self.publish_events(constants.LOCATION_ADD_BUILDING_ROUTE)

    def remove_building(self, building: Any) -> None:
        """
        Description:
            Removes the inputted building from this location
        Input:
            building building: Building to remove from this location
        Output:
            None
        """
        if self.get_building(building.building_type.key) == building:
            del self.contained_buildings[building.building_type.key]
            self.publish_events(constants.LOCATION_REMOVE_BUILDING_ROUTE)
            constants.EventBus.unsubscribe(
                self.update_image_bundle,
                building.uuid,
                constants.BUILDING_SET_DAMAGED_ROUTE,
            )

    def get_building(self, building_type: str):
        """
        Description:
            Returns this location's building of the inputted type, or None if that building is not present
        Input:
            string building_type: Type of building to search for
        Output:
            building/string: Returns whether this location's building of the inputted type, or None if that building is not present
        """
        if building_type in [constants.ROAD, constants.RAILROAD]:
            return self.get_building(constants.INFRASTRUCTURE)
        else:
            return self.contained_buildings.get(building_type, None)

    def get_intact_building(self, building_type: str):
        """
        Description:
            Returns this location's undamaged building of the inputted type, or None if that building is damaged or not present
        Input:
            string building_type: Type of building to search for
        Output:
            building/string: Returns this location's undamaged building of the inputted type, or None if that building is damaged or not present
        """
        if building_type in [constants.ROAD, constants.RAILROAD]:
            return self.get_intact_building(constants.INFRASTRUCTURE)
        elif self.has_intact_building(building_type):
            return self.get_building(building_type)
        else:
            return None

    def get_buildings(self) -> List[Any]:
        """
        Description:
            Returns a list of the buildings contained in this location
        Input:
            None
        Output:
            building list: Buildings contained in this location
        """
        return [
            contained_building
            for contained_building in self.contained_buildings.values()
            if contained_building
        ]

    def get_intact_buildings(self) -> List[Any]:
        """
        Description:
            Returns a list of the nondamaged buildings contained in this location
        Input:
            None
        Output:
            building list contained_buildings_list: nondamaged buildings contained in this location
        """
        return [
            contained_building
            for contained_building in self.contained_buildings
            if contained_building and self.has_intact_building(contained_building.key)
        ]

    def has_destructible_buildings(self):
        """
        Description:
            Finds and returns if this location is adjacent has any buildings that can be damaged by enemies (not roads or railroads), used for enemy location targeting
        Input:
            None
        Output:
            boolean: Returns if this location has any buildings that can be damaged by enemies
        """
        return any(
            [
                status.building_types[contained_building.key].can_damage
                for contained_building in self.get_intact_buildings()
            ]
        )

    def get_warehouses_cost(self):
        """
        Description:
            Calculates and returns the cost of the next warehouses upgrade in this location, based on the number of past warehouses upgrades
        Input:
            None
        Output:
            int: Returns the cost of the next warehouses upgrade in this location, based on the number of past warehouse upgrades
        """
        warehouses = self.get_building(constants.WAREHOUSES)
        if warehouses:
            warehouses_built = warehouses.upgrade_fields[constants.WAREHOUSE_LEVEL]
        else:
            warehouses_built = 0
        warehouses_built -= len(
            [
                building
                for building in self.get_buildings()
                if building.building_type.warehouse_level > 0
            ]
        )
        # Don't include warehouses included with other buildings in the new warehouse cost

        return self.get_building(constants.WAREHOUSES).building_type.upgrade_fields[
            constants.WAREHOUSE_LEVEL
        ]["cost"] * (
            2**warehouses_built
        )  # 5 * 2^0 = 5 if none built, 5 * 2^1 = 10 if 1 built, 20, 40...

    def find_adjacent_locations(self):
        """
        Records a list of the locations directly adjacent to this one. Also records these locations as values in a dictionary with string keys corresponding to their direction relative to this location
        """
        self.adjacent_list = []
        self.adjacent_locations = {}
        world_dimensions = self.world_handler.world_dimensions
        for x, y, direction in [
            ((self.x - 1) % world_dimensions, self.y, "left"),
            ((self.x + 1) % world_dimensions, self.y, "right"),
            (self.x, (self.y + 1) % world_dimensions, "up"),
            (self.x, (self.y - 1) % world_dimensions, "down"),
        ]:
            self.adjacent_locations[direction] = self.world_handler.find_location(x, y)
            if self.adjacent_locations[direction]:
                self.adjacent_list.append(self.adjacent_locations[direction])

    def get_parameter_habitability(self, parameter_name: str) -> int:
        """
        Description:
            Calculates and returns the habitability effect of a particular parameter
        Input:
            string parameter_name: Name of the parameter to calculate habitability for
        Output:
            int: Returns the habitability effect of the inputted parameter, from 0 to 5 (5 is perfect, 0 is deadly)
        """
        if parameter_name in constants.global_parameters:
            return self.true_world_handler.get_parameter_habitability(parameter_name)
        elif parameter_name == constants.TEMPERATURE:
            return actor_utility.get_temperature_habitability(
                self.get_parameter(parameter_name)
            )
        elif parameter_name == constants.WATER:
            if self.get_parameter(constants.WATER) >= 4 and self.get_parameter(
                constants.TEMPERATURE
            ) > self.true_world_handler.get_tuning("water_freezing_point"):
                return constants.HABITABILITY_DEADLY
            else:
                return constants.HABITABILITY_PERFECT
        else:
            return constants.HABITABILITY_PERFECT

    def get_habitability_dict(self, omit_perfect: bool = True) -> Dict[str, int]:
        """
        Description:
            Returns a dictionary of the habitability of each parameter of this terrain, with perfect values omitted
        Input:
            None
        Output:
            dictionary: Dictionary with key/value pairs of parameter type and parameter habitability, with perfect values omitted
        """
        habitability_dict = {}
        for terrain_parameter in (
            constants.terrain_parameters + constants.global_parameters
        ):
            habitability = self.get_parameter_habitability(terrain_parameter)
            if (not omit_perfect) or habitability != constants.HABITABILITY_PERFECT:
                habitability_dict[terrain_parameter] = self.get_parameter_habitability(
                    terrain_parameter
                )
        return habitability_dict

    def get_unit_habitability(self, unit=None) -> int:
        """
        Description:
            Returns the habitability of this location for the inputted units
        Input:
            Mob unit: Unit to check the habitability of this location for
        Output:
            int: Returns habitability of this location for the inputted unit
        """
        if (
            self.is_abstract_location
            and self.world_handler.abstract_world_type == constants.ORBITAL_WORLD
        ):
            default_habitability = constants.HABITABILITY_DEADLY
        else:
            default_habitability = min(
                self.get_habitability_dict(omit_perfect=False).values()
            )
        if unit and unit.any_permissions(
            constants.SPACESUITS_PERMISSION,
            constants.VEHICLE_PERMISSION,
            constants.IN_VEHICLE_PERMISSION,
        ):
            default_habitability = constants.HABITABILITY_PERFECT
        return default_habitability

    def get_known_habitability(self) -> int:
        """
        Description:
            Returns the habitability of this location based on current knowledge
        Input:
            None
        Output:
            int: Returns the habitability of this location based on current knowledge
        """
        habitability_dict = self.get_habitability_dict()
        if self.is_abstract_location:  # If global habitability
            habitability_dict[constants.TEMPERATURE] = (
                actor_utility.get_temperature_habitability(
                    round(self.true_world_handler.average_temperature)
                )
            )
            overall_habitability = min(habitability_dict.values())
        elif (
            self.get_parameter(constants.KNOWLEDGE)
            < constants.TERRAIN_PARAMETER_KNOWLEDGE_REQUIREMENT
        ):  # If no temperature knowledge
            if constants.TEMPERATURE in habitability_dict:
                del habitability_dict[constants.TEMPERATURE]
            if not habitability_dict:
                overall_habitability = constants.HABITABILITY_PERFECT
            else:
                overall_habitability = min(habitability_dict.values())
        else:  # If full knowledge
            if not habitability_dict:
                overall_habitability = constants.HABITABILITY_PERFECT
            else:
                overall_habitability = min(habitability_dict.values())
        return overall_habitability

    def get_expected_temperature(self) -> float:
        """
        Description:
            Returns the expected temperature of this terrain based on the world's average temperature and the cell's pole distance
                When selecting a location to change temperature, greatest outliers should be selected (farthest from expected)
        Input:
            None
        Output:
            float: Expected temperature of this terrain
        """
        if self.true_world_handler:
            altitude_effect = (
                -1 * self.get_parameter(constants.ALTITUDE)
            ) + self.true_world_handler.average_altitude
            altitude_effect_weight = 0.5
            # Colder to the extent that location is higher than average altitude, and vice versa
            return (
                self.true_world_handler.average_temperature
                - 3.5
                + (5 * self.pole_distance_multiplier)
                + (altitude_effect * altitude_effect_weight)
            )
        else:
            return 0.0

    def add_terrain_feature(self, terrain_feature_dict: Dict[str, Any]) -> None:
        """
        Description:
            Adds a terrain feature with the inputted dictionary to this location
        Input:
            dictionary terrain_feature_dict: Dictionary containing information about the terrain feature to add
                Requires feature type and anything unique about this particular instance, like name
        Output:
            None
        """
        self.terrain_features[terrain_feature_dict["feature_type"]] = (
            terrain_feature_dict
        )
        feature_type = status.terrain_feature_types[
            terrain_feature_dict["feature_type"]
        ]
        feature_key = terrain_feature_dict["feature_type"].replace(" ", "_")

        if feature_type.tracking_type == constants.UNIQUE_FEATURE_TRACKING:
            setattr(status, feature_key, self)
        elif feature_type.tracking_type == constants.LIST_FEATURE_TRACKING:
            feature_key += "_list"
            getattr(status, feature_key).append(self)
        self.publish_events(constants.UPDATE_TERRAIN_FEATURE_ROUTE)

    def knowledge_available(self, information_type: str) -> bool:
        """
        Description:
            Returns whether the inputted type of information is visible for this location, based on knowledge of the location
        Input:
            string information_type: Type of information to check visibility of, like 'terrain' or 'hidden_units'
        Output:
            None
        """
        if information_type == constants.TERRAIN_KNOWLEDGE:
            return (
                self.get_parameter(constants.KNOWLEDGE)
                >= constants.TERRAIN_KNOWLEDGE_REQUIREMENT
            )
        elif information_type == constants.TERRAIN_PARAMETER_KNOWLEDGE:
            return (
                self.get_parameter(constants.KNOWLEDGE)
                >= constants.TERRAIN_PARAMETER_KNOWLEDGE_REQUIREMENT
            )
        else:
            return True

    def change_parameter(
        self, parameter_name: str, change: int, update_display: bool = True
    ) -> None:
        """
        Description:
            Changes the value of a parameter for this location
        Input:
            string parameter_name: Name of the parameter to change
            int change: Amount to change the parameter by
            boolean update_image: Whether to update the image of any subscribed locations after changing the parameter
        Output:
            None
        """
        self.set_parameter(
            parameter_name,
            self.terrain_parameters[parameter_name] + change,
            update_display=update_display,
        )

    def publish_events(self, *routes: str) -> None:
        """
        Description:
            Publishes to all applicable endpoints with the inputted routes
            If setting location's temperature: publish_events(LOCATION_SET_PARAMETER_ROUTE, TEMPERATURE)
            Suppose this is the displayed location - publishes to the endpoints:
                - uuid - any subscriptions that watch all changes to this location
                - true_world_handler.uuid - any subscriptions that watch all changes to the world
                - DISPLAYED_LOCATION_ENDPOINT - any subscriptions watching changes to the displayed location
            With the following topics:
                - endpoints/LOCATION_SET_PARAMETER_ROUTE - any subscriptions watching changes to parameters of the above
                - endpoints/LOCATION_SET_PARAMETER_ROUTE/TEMPERATURE - any subscriptions watching changes to the temperature parameter of the above
            uuid/LOCATION_SET_PARAMETER_ROUTE might invoke this location's update_image_bundle to update the image
            true_world_handler.uuid/LOCATION_SET_PARAMETER_ROUTE/TEMPERATURE might update the world's average temperature
            DISPLAYED_LOCATION_ENDPOINT/LOCATION_SET_PARAMETER_ROUTE/TEMPERATURE might update the content of the location temperature label
        Input:
            string list routes: Hierarchical of routes to publish to
        Output:
            None
        """
        endpoints = [f"{self.uuid}", f"{self.true_world_handler.uuid}"]
        if self == status.displayed_location:
            endpoints.append(constants.DISPLAYED_LOCATION_ENDPOINT)
        for endpoint in endpoints:
            constants.EventBus.publish(endpoint, *routes)

    def set_parameter(
        self, parameter_name: str, new_value: int, update_display: bool = True
    ) -> None:
        """
        Description:
            Sets the value of a parameter for this location's cells
        Input:
            string parameter_name: Name of the parameter to change
            int new_value: New value for the parameter
            boolean update_image: Whether to update the image of any subscribed cells after setting the parameter
        Output:
            None
        """
        overlay_images = self.get_overlay_images()
        if parameter_name in [constants.WATER, constants.TEMPERATURE]:
            old_value = self.terrain_parameters[parameter_name]
        elif parameter_name == constants.ALTITUDE:
            old_color_filter = self.get_color_filter()
        self.terrain_parameters[parameter_name] = max(
            self.minima.get(parameter_name, 0),
            min(new_value, self.maxima.get(parameter_name, 5)),
        )
        new_value = self.terrain_parameters[parameter_name]
        # if parameter_name == constants.WATER and not self.is_abstract_location:
        # self.true_world_handler.update_average_water()
        if parameter_name == constants.ALTITUDE and not self.is_abstract_location:
            self.true_world_handler.update_average_altitude()
        elif parameter_name == constants.TEMPERATURE and not self.is_abstract_location:
            # If changing temperature, re-distribute water around the planet
            # Causes melting glaciers and vice versa
            if new_value != old_value:
                water_displaced = random.randrange(
                    0, self.get_parameter(constants.WATER) + 1
                )
                self.set_parameter(
                    constants.WATER,
                    self.get_parameter(constants.WATER) - water_displaced,
                    update_display=False,
                )
                for i in range(water_displaced):
                    self.true_world_handler.place_water(update_display=update_display)

        new_terrain = constants.TerrainManager.classify(self.terrain_parameters)

        if (
            constants.current_map_mode != "terrain"
            or self.terrain != new_terrain
            or overlay_images != self.get_overlay_images()
            or (
                parameter_name == constants.ALTITUDE
                and old_color_filter != self.get_color_filter()
            )
            or parameter_name == constants.KNOWLEDGE
        ):
            self.set_terrain(new_terrain, update_image_bundle=update_display)
            if update_display and not flags.loading:
                status.current_world.update_globe_projection()

        if status.displayed_location == self:
            actor_utility.calibrate_actor_info_display(
                status.location_info_display, self
            )
        self.publish_events(constants.LOCATION_SET_PARAMETER_ROUTE, parameter_name)

    def update_contained_mob_habitability(self) -> None:
        """
        Updates the habitability of all contained mobs in this location
        """
        for current_mob in self.contained_mobs:
            current_mob.update_habitability()

    def has_snow(self) -> bool:
        """
        Description:
            Returns whether this terrain would have snow based on its temperature and water levels
        Input:
            None
        Output:
            boolean: True if this terrain would have snow, False if not
        """
        return (
            self.get_parameter(constants.TEMPERATURE)
            <= constants.TerrainManager.get_tuning("water_freezing_point")
            and self.get_parameter(constants.WATER) >= 1
        )

    def boiling(self) -> bool:
        """
        Description:
            Returns whether this terrain would have visible steam based on its temperature and water levels
        Input:
            None
        Output:
            boolean: True if this terrain would have visible steam, False if not
        """
        return (
            self.get_parameter(constants.TEMPERATURE)
            >= constants.TerrainManager.get_tuning("water_boiling_point") - 4
            and self.get_parameter(constants.WATER) >= 1
        )

    def get_overlay_images(self) -> List[str]:
        """
        Description:
            Gets any non-cloud overlay images that are part of terrain but not from original image
        Input:
            None
        Output:
            string list: List of overlay image file paths
        """
        return_list = []
        if self.has_snow():
            return_list.append(f"terrains/snow_{self.terrain_variant % 4}.png")

        steam_list = []
        if self.boiling():  # If 4 below boiling, add steam
            steam_list.append(f"terrains/boiling_{self.terrain_variant % 4}.png")
            if self.get_parameter(constants.WATER) >= 2 and self.get_parameter(
                constants.TEMPERATURE
            ) >= constants.TerrainManager.get_tuning("water_boiling_point"):
                # If boiling, add more steam as water increases
                steam_list.append(
                    f"terrains/boiling_{(self.terrain_variant + 1) % 4}.png"
                )
                if self.get_parameter(constants.WATER) >= 4:
                    steam_list.append(
                        f"terrains/boiling_{(self.terrain_variant + 2) % 4}.png"
                    )
        return_list += [
            {
                "image_id": current_steam,
                "green_screen": [self.world_handler.steam_color],
                "detail_level": constants.CLOUDS_DETAIL_LEVEL,
                "override_green_screen_colors": [(140, 183, 216)],
                "level": constants.TERRAIN_CLOUDS_LEVEL,
            }
            for current_steam in steam_list
        ]

        return return_list

    def to_save_dict(self) -> Dict[str, any]:
        """
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                'terrain': string value - Terrain type of this location, like 'swamp'
                'terrain_variant': int value - Variant number to use for image file path, like mountains_0
                'terrain_features': string/boolean dictionary value - Dictionary containing an entry for each terrain feature in this location
                'terrain_parameters': string/int dictionary value - Dictionary containing 1-6 parameters for this location, like 'temperature': 1
                'resource': string value - Item type key of natural resource in this location, like "Gold" or None
                'local_weather_offset': float value - Temperature offset of this location from expected for the latitude
        """
        return {
            **super().to_save_dict(),
            "init_type": constants.LOCATION,
            "coordinates": (self.x, self.y),
            "terrain_variant": self.terrain_variant,
            "terrain_features": self.terrain_features,
            "terrain_parameters": self.terrain_parameters,
            "terrain": self.terrain,
            "resource": self.resource.key if self.resource else None,
            "north_pole_distance_multiplier": self.north_pole_distance_multiplier,
            "pole_distance_multiplier": self.pole_distance_multiplier,
            "current_clouds": self.current_clouds,
            "local_weather_offset": self.local_weather_offset,
            "subscribed_mobs": [
                current_mob.to_save_dict()
                for current_mob in reversed(self.subscribed_mobs)
            ],
            "settlement": self.settlement.to_save_dict() if self.settlement else None,
            "contained_buildings": [
                building.to_save_dict()
                for building in self.contained_buildings.values()
            ],
        }

    def get_parameter(self, parameter_name: str) -> int:
        """
        Description:
            Returns the value of the inputted parameter from this location
        Input:
            string parameter: Name of the parameter to get
        Output:
            None
        """
        return self.terrain_parameters[parameter_name]

    def set_terrain(self, new_terrain: str, update_image_bundle: bool = True) -> None:
        """
        Description:
            Sets this location's terrain type, automatically generating a variant (not used for loading with pre-defined variant)
        Input:
            string new_terrain: New terrain type for this location, like 'swamp'
        Output:
            None
        """
        try:
            if hasattr(
                self, "terrain_variant"
            ) and constants.TerrainManager.terrain_variant_dict.get(
                self.terrain, 1
            ) == constants.TerrainManager.terrain_variant_dict.get(
                new_terrain, 1
            ):
                pass  # Keep same terrain variant if number of variants is the same - keep same basic mountain layout, etc.
            else:
                self.terrain_variant = random.randrange(
                    0,
                    constants.TerrainManager.terrain_variant_dict.get(new_terrain, 1),
                )
        except:
            print(f"Error loading {new_terrain} variant")
            self.terrain_variant = random.randrange(
                0, constants.TerrainManager.terrain_variant_dict.get(new_terrain, 1)
            )
        self.terrain = new_terrain

        if new_terrain in constants.TerrainManager.terrain_list:
            self.default_image_id = f"terrains/{new_terrain}_{self.terrain_variant}.png"

    def subscribe_cell(self, cell) -> None:
        """
        Description:
            Subscribes the inputted cell to this location, removing it from any previous location and updating its parameters to match this location
        Input:
            cell: Cell to subscribe to this location
        Output:
            None
        """
        if cell.location:
            cell.location.unsubscribe_cell(cell)
        self.subscribed_cells.append(cell)
        cell.subscribed_location = self
        if cell.grid == status.minimap_grid:
            cell.set_image(
                self.image_dict[constants.IMAGE_ID_LIST_INCLUDE_MINIMAP_OVERLAY]
            )
        else:
            cell.set_image(self.image_dict[constants.IMAGE_ID_LIST_INCLUDE_MOB])
        # Update cell's rendered image

    def subscribe_mob(self, mob) -> None:
        """
        Description:
            Subscribes the inputted mob to this location, removing it from any previous location
        Input:
            mob mob: Mob to subscribe to this location
        Output:
            None
        """
        if (
            mob.subscribed_location
        ):  # Note that this is distinct from get_location(), which recursively checks through containers
            mob.subscribed_location.unsubscribe_mob(mob)
        self.subscribed_mobs.insert(0, mob)
        mob.subscribed_location = self
        self.publish_events(
            constants.LOCATION_SUBSCRIBE_MOB_ROUTE
        )  # Publish events of this location subscribing a mob
        mob.publish_events(
            constants.LOCATION_SUBSCRIBE_MOB_ROUTE
        )  # Publish events of this mob subscribing a location
        if mob == status.displayed_mob and self != status.displayed_location:
            actor_utility.calibrate_actor_info_display(
                status.location_info_display, self
            )

    def unsubscribe_cell(self, cell) -> None:
        """
        Description:
            Unsubscribes the inputted cell from this location - precondition that cell is in this location
        Input:
            cell cell: Cell to unsubscribe from this location
        Output:
            None
        """
        self.subscribed_cells.remove(cell)
        cell.subscribed_location = None

    def unsubscribe_mob(self, mob) -> None:
        """
        Description:
            Unsubscribes the inputted mob from this location - precondition that mob is in this location
        Input:
            mob mob: Mob to unsubscribe from this location
        Output:
            None
        """
        self.subscribed_mobs.remove(mob)
        mob.subscribed_location = None
        self.publish_events(constants.LOCATION_UNSUBSCRIBE_MOB_ROUTE)

    def flow(self) -> None:
        """
        Recursively flows water from this location to any adjacent locations, if possible. Water flows between locations based on altitude and temperature - water flows to
            non-higher altitudes if there is much more water at the origin and if the origin water is liquid
        """
        flowed = False
        if (
            self.get_parameter(constants.WATER) >= 4
            and self.get_parameter(constants.TEMPERATURE)
            > constants.TerrainManager.get_tuning("water_freezing_point") - 1
        ):  # If enough liquid water to flow - frozen or 1 lower (occasionally liquid)
            for adjacent_location in self.adjacent_list:
                if adjacent_location.get_parameter(
                    constants.ALTITUDE
                ) <= self.get_parameter(
                    constants.ALTITUDE
                ) and adjacent_location.get_parameter(
                    constants.TEMPERATURE
                ) < constants.TerrainManager.get_tuning(
                    "water_boiling_point"
                ):
                    if (
                        adjacent_location.get_parameter(constants.WATER)
                        <= self.terrain_parameters[constants.WATER] - 2
                    ):
                        adjacent_location.change_parameter(
                            constants.WATER, 1, update_display=False
                        )
                        self.change_parameter(constants.WATER, -1, update_display=False)
                        flowed = True

        if flowed:  # Flow could recursively trigger flows in adjacent cells
            for adjacent_location in self.adjacent_list:
                adjacent_location.flow()

    def get_color_filter(self) -> Dict[str, int]:
        """
        Description:
            Gets the color filter for this location's world, if any
        Input:
            None
        Output:
            dictionary: Color filter for this location's world
        """
        if self.true_world_handler:
            color_filter = self.true_world_handler.color_filter.copy()
            for key in color_filter:
                color_filter[key] = round(
                    color_filter[key]
                    + ((self.get_parameter(constants.ALTITUDE) / 10) - 0.2)
                    * constants.ALTITUDE_BRIGHTNESS_MULTIPLIER,
                    2,
                )
            return color_filter
        else:
            return {
                constants.COLOR_RED: 1,
                constants.COLOR_GREEN: 1,
                constants.COLOR_BLUE: 1,
            }

    @property
    def world_handler(self) -> world_handlers.world_handler:
        """
        Description:
            Returns the world handler corresponding to this location
        Input:
            None
        Output:
            world_handler: World handler corresponding to this location, or None if none exists yet
        """
        return self.parent_world_handler

    @property
    def true_world_handler(self) -> world_handlers.world_handler:
        """
        Description:
            Returns the actual world handler corresponding to this location, mapping to the actual world if this is an orbital world
        Input:
            None
        Output:
            world_handler: Actual world handler corresponding to this location, or None if none exists yet
        """
        world_handler = self.world_handler
        if world_handler.is_orbital_world:
            return world_handler.full_world
        else:
            return world_handler

    def get_green_screen(self) -> Dict[str, Dict[str, any]]:
        """
        Description:
            Returns a "smart green screen" dictionary for this location, or None for default appearance
                {
                    'water': {
                        'base_color': (20, 20, 200),
                        'tolerance': 50,
                        'replacement_color': (200, 20, 20)
                    },
                    'sand': {
                        ...
                    }...
                }
                Take all colors that are within 50 (tolerance) of the base color and replace them with a new color, while retaining the same difference from
                    the new color as it did with the old color. If a spot of water is slightly darker than the base water color, replace it with something
                    slightly darker than the replacement color, while ignoring anything that is not within 50 of the base water color.
                Each category can have a preset base color/tolerance determined during asset creation, as well as a procedural replacement color
                Each category can have a preset smart green screen, with per-terrain or per-location modifications controlled by world and locations
                    World handler handles per-terrain modifications, like dunes sand being slightly different from desert sand, while both are still "Mars red"
                    Location handles local modifications, like earth-imported soil looking different from default planet soil
                This system could also work for skin shading, polar dust, light levels, vegetation, resources, building appearances, etc.
            Serves as authoritative source for terrain green screens, used by get_image_id_list and referencing constants for presets and world handler for world variations
        Input:
            None
        Output:
            dictionary: Smart green screen dictionary for this location, or None for default location appearance
        """
        world_green_screen = self.world_handler.get_green_screen(self.terrain)

        # Make any per-location modifications

        return world_green_screen
        # return world_green_screen

    def get_brightness(self) -> float:
        """
        Description:
            Calculates and returns the average RGB value of this location's terrain
        Input:
            None
        Output:
            float: Returns the average RGB value of this location's terrain
        """
        if self.is_earth_location:
            return 1.0 - self.true_world_handler.get_tuning("earth_albedo_multiplier")
        elif not self.is_abstract_location:
            status.albedo_free_image.set_image(
                self.image_dict[constants.IMAGE_ID_LIST_ALBEDO]
            )
            return (
                sum(
                    [
                        sum(
                            status.albedo_free_image.image.combined_surface.get_at(
                                (x, y)
                            )[0:3]
                        )
                        / 3
                        for x, y in [(0, 0), (0, 1), (1, 0), (1, 1)]
                    ]
                )
                / 4
            )
        else:  # Orbital world and other abstract worlds don't need brightness calculation
            return 1.0

    def update_clouds(
        self, num_cloud_variants: int, num_solid_cloud_variants: int
    ) -> None:
        """
        Updates this location's cloud images with the inputted variant options
            Cloud color, transparency, and frequency depend on global conditions
        """
        self.current_clouds = []

        cloud_type = None
        if random.random() < self.world_handler.cloud_frequency:
            cloud_type = "water vapor"
        elif random.random() < self.world_handler.toxic_cloud_frequency:
            cloud_type = "toxic"
        if cloud_type:
            self.current_clouds.append(
                {
                    "image_id": "misc/shader.png",
                    "detail_level": constants.CLOUDS_DETAIL_LEVEL,
                }
            )
        if self.world_handler.atmosphere_haze_alpha > 0:
            self.current_clouds.append(
                {
                    "image_id": f"terrains/clouds_solid_{random.randrange(0, num_solid_cloud_variants)}.png",
                    "alpha": self.world_handler.atmosphere_haze_alpha,
                    "detail_level": constants.CLOUDS_DETAIL_LEVEL,
                    "green_screen": {
                        "clouds": {
                            "base_colors": [(174, 37, 19)],
                            "tolerance": 60,
                            "replacement_color": self.world_handler.sky_color,
                        },
                    },
                }
            )
        if cloud_type == "water vapor":
            self.current_clouds.append(
                {
                    "image_id": f"terrains/clouds_base_{random.randrange(0, num_cloud_variants)}.png",
                    "detail_level": constants.CLOUDS_DETAIL_LEVEL,
                    "green_screen": {
                        "clouds": {
                            "base_colors": [(174, 37, 19)],
                            "tolerance": 60,
                            "replacement_color": self.world_handler.steam_color,
                        },
                    },
                }
            )
        elif cloud_type == "toxic":
            self.current_clouds.append(
                {
                    "image_id": f"terrains/clouds_base_{random.randrange(0, num_cloud_variants)}.png",
                    "detail_level": constants.CLOUDS_DETAIL_LEVEL,
                    "green_screen": {
                        "clouds": {
                            "base_colors": [(174, 37, 19)],
                            "tolerance": 60,
                            "replacement_color": [
                                round(color * 0.8)
                                for color in self.world_handler.sky_color
                            ],
                        },
                    },
                }
            )
        self.publish_events(constants.LOCATION_UPDATE_CLOUDS_ROUTE)

    def get_image_id_list(
        self,
        terrain_only=False,
        force_clouds=False,
        force_pixellated=False,
        allow_mapmodes=True,
        allow_clouds=True,
    ):
        """
        Description:
            Generates and returns a list this actor's image file paths and dictionaries that can be passed to any image object to display those images together in a particular order and
                orientation
        Input:
            boolean terrain_only = False: Whether to just show terrain or other contents as well
        Output:
            list: Returns list of string image file paths, possibly combined with string key dictionaries with extra information for offset images
        """
        if self.is_abstract_location:
            image_id_list = self.world_handler.image_id_list
        else:
            image_id_list = []
            if (
                (not allow_mapmodes)
                or constants.current_map_mode == "terrain"
                or constants.MAP_MODE_ALPHA
            ):
                image_id_list.append(
                    {
                        "image_id": self.default_image_id,
                        "level": constants.TERRAIN_BACKDROP_LEVEL,
                        "color_filter": self.get_color_filter(),
                        "green_screen": self.get_green_screen(),
                        "pixellated": force_pixellated
                        or not self.knowledge_available(constants.TERRAIN_KNOWLEDGE),
                        "detail_level": constants.TERRAIN_DETAIL_LEVEL,
                    }
                )
                if allow_clouds:
                    for terrain_overlay_image in self.get_overlay_images():
                        if type(terrain_overlay_image) == str:
                            terrain_overlay_image = {
                                "image_id": terrain_overlay_image,
                            }
                        terrain_overlay_image.update(
                            {
                                "level": terrain_overlay_image.get(
                                    "level", constants.TERRAIN_OVERLAY_LEVEL
                                ),
                                "color_filter": self.get_color_filter(),
                                "pixellated": force_pixellated
                                or not self.knowledge_available(
                                    constants.TERRAIN_KNOWLEDGE
                                ),
                                "detail_level": terrain_overlay_image.get(
                                    "detail_level", constants.TERRAIN_DETAIL_LEVEL
                                ),
                            }
                        )
                        if not terrain_overlay_image.get("green_screen", None):
                            terrain_overlay_image["green_screen"] = (
                                self.get_green_screen()
                            )
                        image_id_list.append(terrain_overlay_image)
                if allow_clouds and (
                    constants.EffectManager.effect_active("show_clouds")
                    or force_clouds
                    or not self.knowledge_available(constants.TERRAIN_KNOWLEDGE)
                ):
                    for cloud_image in self.current_clouds:
                        image_id_list.append(cloud_image.copy())
                        if not image_id_list[-1].get("detail_level", None):
                            image_id_list[-1][
                                "detail_level"
                            ] = constants.TERRAIN_DETAIL_LEVEL
                        image_id_list[-1]["level"] = constants.TERRAIN_CLOUDS_LEVEL
                        if not image_id_list[-1].get("green_screen", None):
                            image_id_list[-1]["green_screen"] = self.get_green_screen()
                if not terrain_only:
                    for terrain_feature in self.terrain_features:
                        if (
                            status.terrain_feature_types[terrain_feature].display_type
                            == constants.APPENDED_IMAGE_TERRAIN_FEATURE
                        ):
                            image_id_list = utility.combine(
                                image_id_list,
                                status.terrain_feature_types[terrain_feature].image_id,
                            )
                    # if (
                    #    self.resource
                    # ):  # If resource visible based on current knowledge
                    #    resource_icon = actor_utility.generate_resource_icon(self)
                    #    if type(resource_icon) == str:
                    #        image_id_list.append(resource_icon)
                    #    else:
                    #        image_id_list += resource_icon
                    image_id_list += [
                        image_id
                        for current_building in self.get_buildings()
                        for image_id in current_building.get_image_id_list()
                    ]  # Add each of each building's images to the image ID list

            if constants.current_map_mode != "terrain" and allow_mapmodes:
                map_mode_image = "misc/map_modes/none.png"
                if constants.current_map_mode in constants.terrain_parameters:
                    if self.knowledge_available(constants.TERRAIN_PARAMETER_KNOWLEDGE):
                        if constants.current_map_mode in [
                            constants.WATER,
                            constants.TEMPERATURE,
                            constants.VEGETATION,
                        ]:
                            map_mode_image = f"misc/map_modes/{constants.current_map_mode}/{self.get_parameter(constants.current_map_mode)}.png"
                        else:
                            map_mode_image = f"misc/map_modes/{self.get_parameter(constants.current_map_mode)}.png"
                elif constants.current_map_mode == "magnetic":
                    if self.terrain_features.get(
                        "southern tropic", False
                    ) or self.terrain_features.get("northern tropic", False):
                        map_mode_image = "misc/map_modes/equator.png"
                    elif self.terrain_features.get("north pole", False):
                        map_mode_image = "misc/map_modes/north_pole.png"
                    elif self.terrain_features.get("south pole", False):
                        map_mode_image = "misc/map_modes/south_pole.png"
                image_id_list.append(
                    {
                        "image_id": map_mode_image,
                        "detail_level": 1.0,
                        "level": constants.MAP_MODE_LEVEL,
                    }
                )
                if constants.MAP_MODE_ALPHA:
                    image_id_list[-1]["alpha"] = constants.MAP_MODE_ALPHA
        return image_id_list

    def get_mob_image_id_list(self):
        """
        Gets the image IDs added to this location if showing mobs
        """
        if self.subscribed_mobs:
            return self.subscribed_mobs[0].image_dict[constants.IMAGE_ID_LIST_FULL_MOB]
        else:
            return []

    def get_minimap_overlay_image_id_list(self):
        """
        Gets a list of image IDs for each minimap overlay terrain feature in this location
        """
        return utility.combine(
            *[
                status.terrain_feature_types[terrain_feature].image_id
                for terrain_feature in self.terrain_features
                if status.terrain_feature_types[terrain_feature].display_type
                == constants.MINIMAP_OVERLAY_TERRAIN_FEATURE
            ],
            *[hosted_icon.get_image_id_list() for hosted_icon in self.hosted_icons],
        )

    def update_image_bundle(self, override_image=None, update_mob_only: bool = False):
        """
        Description:
            Updates this actor's images with its current image id list, also updating the minimap grid version if applicable
        Input:
            image_bundle override_image=None: Image bundle to update image with, setting this location's image to a copy of the image bundle instead of generating a new image
                bundle
        Output:
            None
        """
        previous_image_dict = self.image_dict.copy()
        previous_mob_image_id_list = self.image_dict[
            constants.IMAGE_ID_LIST_INCLUDE_MOB
        ]

        if not update_mob_only:
            if override_image:
                self.image_dict[constants.IMAGE_ID_LIST_DEFAULT] = override_image
                self.image_dict[constants.IMAGE_ID_LIST_TERRAIN] = override_image
                self.image_dict[constants.IMAGE_ID_LIST_ORBITAL_VIEW] = override_image
                self.image_dict[constants.IMAGE_ID_LIST_ALBEDO] = override_image
            else:
                self.image_dict[constants.IMAGE_ID_LIST_DEFAULT] = (
                    self.get_image_id_list()
                )  # Includes buildings, terrain, clouds, etc. - whatever shows in strategic map (includes mapmodes and toggleable clouds)
                self.image_dict[constants.IMAGE_ID_LIST_TERRAIN] = (
                    self.get_image_id_list(terrain_only=True)
                )  # Includes terrain, clouds, etc. - whatever shows in tactical map (includes mapmodes and toggleable clouds)
                self.image_dict[constants.IMAGE_ID_LIST_ORBITAL_VIEW] = (
                    self.get_image_id_list(terrain_only=True, force_clouds=True)
                )  # Includes terrain, clouds, etc. - view from space (no mapmodes, clouds always show)
                self.image_dict[constants.IMAGE_ID_LIST_ALBEDO] = (
                    self.get_image_id_list(
                        terrain_only=True,
                        force_pixellated=True,
                        allow_mapmodes=False,
                        allow_clouds=False,
                    )
                )  # Pixellated pure terrain appearance with no clouds for terrain albedo calculation

        self.image_dict[constants.IMAGE_ID_LIST_INCLUDE_MOB] = (
            self.image_dict[constants.IMAGE_ID_LIST_DEFAULT]
            + self.get_mob_image_id_list()
        )

        self.image_dict[constants.IMAGE_ID_LIST_INCLUDE_MINIMAP_OVERLAY] = (
            self.image_dict[constants.IMAGE_ID_LIST_INCLUDE_MOB]
            + self.get_minimap_overlay_image_id_list()
        )

        if previous_image_dict != self.image_dict:
            if (
                previous_mob_image_id_list
                == self.image_dict[constants.IMAGE_ID_LIST_INCLUDE_MOB]
            ):
                self.refresh_attached_images(
                    include_mobs=False
                )  # No need to update mob interface if only terrain images changed
            else:
                self.refresh_attached_images(include_mobs=True)

    def refresh_attached_images(self, include_mobs: bool = True):
        """
        Updates this location's images wherever they are shown (locations and info displays)
            Should be invoked after any changes to the image bundle
        """
        if self == status.displayed_location:
            actor_utility.calibrate_actor_info_display(
                status.location_info_display, self
            )
        if (
            include_mobs
            and status.displayed_mob
            and status.displayed_mob.location == self
        ):
            actor_utility.calibrate_actor_info_display(
                status.mob_info_display, status.displayed_mob
            )
        for current_cell in self.subscribed_cells:
            if current_cell.grid == status.minimap_grid:
                current_cell.set_image(
                    self.image_dict[constants.IMAGE_ID_LIST_INCLUDE_MINIMAP_OVERLAY]
                )
            else:
                current_cell.set_image(
                    self.image_dict[constants.IMAGE_ID_LIST_INCLUDE_MOB]
                )

    def has_unit_by_filter(self, permissions, required_number=1):
        """
        Description:
            Returns whether this location contains the requested amount of units with all the inputted permissions
        Input:
            string list permissions: List of permissions to search for
            int required_number=1: Number of units that must be found to return True
        Output:
            boolean: Returns whether this location contains the requested amount of units with all the inputted permissions
        """
        return (
            len(self.get_unit_by_filter(permissions, get_all=True)) >= required_number
        )

    def get_unit_by_filter(
        self, permissions, start_index: int = 0, get_all: bool = False
    ):
        """
        Description:
            Returns the first unit in this location with all the inputted permissions, or None if none are present
        Input:
            string list permissions: List of permissions to search for
            int start_index=0: Index of subscribed_mobs to start search from - if starting in middle, wraps around iteration to ensure all items are still checked
                Allows finding different units with repeated calls by changing start_index
            boolean get_all=False: If True, returns all units with the inputted permissions, otherwise returns the first
        Output:
            mob: Returns the first unit in this location with all the inputted permissions, or None if none are present
                If get_all, otherwise returns List[mob]: Returns all units in this location with all the inputted permissions
        """
        if not self.subscribed_mobs:
            return [] if get_all else None

        start_index = start_index % len(
            self.subscribed_mobs
        )  # Wrap around start_index to ensure it is within bounds

        iterated_list = (
            self.subscribed_mobs[start_index : len(self.subscribed_mobs)]
            + self.subscribed_mobs[0:start_index]
        )  # Get all mobs starting from start_index, wrapping around to the beginning of the list

        if get_all:
            return [
                current_mob
                for current_mob in iterated_list
                if current_mob.all_permissions(*permissions)
            ]
        else:
            return next(
                (
                    current_mob
                    for current_mob in iterated_list
                    if current_mob.all_permissions(*permissions)
                ),
                None,
            )

    def get_best_combatant(self):
        """
        Description:
            Finds and returns the best combatant in this location. Combat ability is based on the unit's combat modifier and veteran status
                Assumes all mobs have already detached from vehicles and buildings
        Input:
            None
        Output:
            mob: Returns the best combatant of the inputted type in this location
        """
        if not self.subscribed_mobs:
            return None

        max_modifier = max(
            self.subscribed_mobs, key=lambda m: m.get_combat_modifier()
        ).get_combat_modifier()
        strongest_candidates = [
            current_mob
            for current_mob in self.subscribed_mobs
            if current_mob.get_combat_modifier() == max_modifier
        ]
        veteran_candidates = [
            current_mob
            for current_mob in strongest_candidates
            if current_mob.get_permission(constants.VETERAN_PERMISSION)
        ]
        if veteran_candidates:
            return random.choice(veteran_candidates)
        else:
            return random.choice(strongest_candidates)

    def get_noncombatants(self):
        """
        Description:
            Finds and returns all units of the inputted type in this location that have 0 combat strength. Assumes that units in vehicles and buildings have already detached upon being attacked
        Input:
            None
        Output:
            mob list: Returns the noncombatants of the inputted type in this location
        """
        return [
            current_mob
            for current_mob in self.subscribed_mobs
            if current_mob.get_combat_strength() == 0
            and current_mob.get_permission(constants.PMOB_PERMISSION)
        ]

    @property
    def batch_tooltip_list(self):
        """
        Gets a 2D list of strings to use as this object's tooltip
            Each string is displayed on a separate line, while each sublist is displayed in a separate box
        """
        return [self.tooltip_text] + list(
            reversed([current_mob.tooltip_text for current_mob in self.subscribed_mobs])
        )

    @property
    def batch_tooltip_list_omit_mobs(self):
        """
        Gets a 2D list of strings to use as this object's tooltip, omitting mobs
            Each string is displayed on a separate line, while each sublist is displayed in a separate box
        """
        return [self.tooltip_text]

    @property
    def tooltip_text(self) -> List[List[str]]:
        """
        Provides the tooltip for this object
        """
        tooltip_message = []
        if self.is_abstract_location:
            tooltip_message.append(self.name)
        else:
            tooltip_message.append(f"Coordinates: ({self.x}, {self.y})")

            knowledge_value = self.get_parameter(constants.KNOWLEDGE)
            knowledge_keyword = constants.TerrainManager.terrain_parameter_keywords[
                constants.KNOWLEDGE
            ][knowledge_value]
            knowledge_maximum = maximum = self.maxima.get(constants.KNOWLEDGE, 5)
            tooltip_message.append(
                f"Knowledge: {knowledge_keyword} ({knowledge_value}/{knowledge_maximum})"
            )

            if self.knowledge_available(constants.TERRAIN_KNOWLEDGE):
                tooltip_message.append(f"    Terrain: {self.terrain.replace('_', ' ')}")
                if self.knowledge_available(constants.TERRAIN_PARAMETER_KNOWLEDGE):
                    for terrain_parameter in constants.terrain_parameters:
                        if terrain_parameter != constants.KNOWLEDGE:
                            maximum = self.maxima.get(terrain_parameter, 5)
                            value = self.get_parameter(terrain_parameter)
                            keyword = (
                                constants.TerrainManager.terrain_parameter_keywords[
                                    terrain_parameter
                                ][value]
                            )
                            tooltip_message.append(
                                f"    {terrain_parameter.capitalize()}: {keyword} ({value}/{maximum})"
                            )
                else:
                    tooltip_message.append(f"    Details unknown")
            else:
                tooltip_message.append(f"    Terrain unknown")

        if self.is_abstract_location or self.knowledge_available(
            constants.TERRAIN_PARAMETER_KNOWLEDGE
        ):
            tooltip_message.append(
                f"Habitability: {constants.HABITABILITY_DESCRIPTIONS[self.get_known_habitability()].capitalize()}"
            )
        else:
            tooltip_message.append(
                f"Habitability: {constants.HABITABILITY_DESCRIPTIONS[self.get_known_habitability()].capitalize()} (estimated)"
            )

        for current_building in self.get_buildings():
            tooltip_message.append("")
            tooltip_message += current_building.tooltip_text

        # if self.resource:  # If resource present, show resource
        #    tooltip_message.append("")
        #    tooltip_message.append(
        #        f"this location has {utility.generate_article(self.resource.name)} {self.resource.name} resource"
        #    )
        for terrain_feature in self.terrain_features:
            if status.terrain_feature_types[terrain_feature].visible:
                tooltip_message.append("")
                tooltip_message += status.terrain_feature_types[
                    terrain_feature
                ].description

        held_items: List[item_types.item_type] = self.get_held_items()
        if (
            held_items
            or self.inventory_capacity > 0
            or self.infinite_inventory_capacity
        ):
            if self.infinite_inventory_capacity:
                tooltip_message.append(f"Inventory: {self.get_inventory_used()}")
            else:
                tooltip_message.append(
                    f"Inventory: {self.get_inventory_used()}/{self.inventory_capacity}"
                )
            if not held_items:
                tooltip_message.append("    None")
            else:
                for item_type in held_items:
                    tooltip_message.append(
                        f"    {item_type.name.capitalize()}: {self.get_inventory(item_type)}"
                    )

        return tooltip_message

    def select(self, music_override: bool = False):
        """
        Selects this location and switches music based on the type of location selected
        """
        if music_override or (
            flags.player_turn and main_loop_utility.action_possible()
        ):
            if constants.SoundManager.previous_state != "earth":
                constants.JobScheduler.clear()
                constants.SoundManager.play_random_music("earth")

    def get_all_local_inventory(self) -> Dict[str, float]:
        """
        Returns a dictionary of all items held by this location and local mobs
        """
        return utility.add_dicts(
            self.inventory, *[mob.inventory for mob in self.subscribed_mobs]
        )

    def consume_items(
        self, items: Dict[str, float], consuming_actor: actors.actor = None
    ) -> Dict[str, float]:
        """
        Description:
            Attempts to consume the inputted items from the inventories of actors in this unit's location
                First checks the location's warehouses, followed by this unit's inventory, followed by other present units' inventories
        Input:
            dictionary items: Dictionary of item type keys and quantities to consume
        Output:
            dictionary: Returns a dictionary of item type keys and quantities that were not available to be consumed
        """
        missing_consumption = {}
        for item_key, consumption_remaining in items.items():
            item_type = status.item_types[item_key]
            for current_actor in [consuming_actor, self] + self.subscribed_mobs:
                if current_actor:
                    if consumption_remaining <= 0:
                        break
                    availability = current_actor.get_inventory(item_type)
                    consumption = min(consumption_remaining, availability)
                    current_actor.change_inventory(item_type, -consumption)
                    consumption_remaining -= consumption
                    consumption_remaining = round(consumption_remaining, 2)
            if consumption_remaining > 0:
                missing_consumption[item_key] = consumption_remaining
        return missing_consumption

    def create_item_request(self, required_items: Dict[str, float]) -> Dict[str, float]:
        """
        Description:
            Given a dictionary of required items with amounts, create a dictionary of the amount of items that need to be externally sourced to meet the requirements
        Input:
            Dict[str, float] required_items: Dictionary of required items with amounts
        Output:
            Dict[str, float]: Dictionary of items with amounts that need to be externally sourced to meet the requirements
        """
        return {
            key: value
            for key, value in utility.subtract_dicts(
                required_items, self.get_all_local_inventory()
            ).items()
            if value > 0
        }

    def fulfill_item_request(
        self, requested_items: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Description:
            Attempt to externally source the requested items
        Input:
            Dict[str, float] requested_items: Dictionary of items with amounts that need to be externally sourced to meet the requirements
        Output:
            Dict[str, float]: Dictionary of items with amounts that can not be provided
        """
        if constants.ENERGY_ITEM in requested_items:
            missing_energy = self.consume_items(
                {constants.FUEL_ITEM: requested_items[constants.ENERGY_ITEM]}
            ).get(constants.FUEL_ITEM, 0)
            # Attempt to consume fuel equal to energy request - returns amount of request that cannot be met
            self.change_inventory(
                status.item_types[constants.ENERGY_ITEM],
                requested_items[constants.ENERGY_ITEM] - missing_energy,
            )  # Turn fuel into required energy
            requested_items[constants.ENERGY_ITEM] = missing_energy
        requested_items = {
            key: value for key, value in requested_items.items() if value > 0
        }  # Remove fulfilled requests
        return requested_items

    @property
    def location_item_upkeep_demand(self) -> Dict[str, float]:
        """
        Description:
            Returns the item upkeep requirements for all units in this location
        Input:
            None
        Output:
            dictionary: Returns the item upkeep requirements for all units in this location
        """
        return utility.add_dicts(
            *[
                mob.get_item_upkeep(
                    recurse=False, earth_exemption=self.is_earth_location
                )
                for mob in self.contained_mobs
            ]
        )

    def remove_excess_inventory(self):
        """
        Removes random excess items from this location until the number of items fits in this location's inventory capacity
        """
        lost_items: Dict[str, float] = {}
        if not self.infinite_inventory_capacity:
            amount_to_remove = self.get_inventory_used() - self.inventory_capacity
            if amount_to_remove > 0:
                for current_item_type in self.get_held_items():
                    decimal_amount = round(
                        self.get_inventory(current_item_type)
                        - math.floor(self.get_inventory(current_item_type)),
                        2,
                    )
                    if (
                        decimal_amount > 0
                    ):  # Best to remove partially consumed items first, since they each take an entire inventory slot
                        lost_items[current_item_type.key] = (
                            lost_items.get(current_item_type.key, 0) + decimal_amount
                        )
                        self.change_inventory(current_item_type, -decimal_amount)
                        amount_to_remove -= 1
                    if amount_to_remove <= 0:
                        break
            if amount_to_remove > 0:
                items_held = []
                for current_item_type in self.get_held_items():
                    items_held += [current_item_type] * self.get_inventory(
                        current_item_type
                    )
                item_types_removed = random.sample(
                    population=items_held, k=amount_to_remove
                )
                for (
                    current_item_type
                ) in item_types_removed:  # Randomly remove amount_to_remove items
                    lost_items[current_item_type.key] = (
                        lost_items.get(current_item_type.key, 0) + 1
                    )
                    self.change_inventory(current_item_type, -1)
        if sum(lost_items.values()) > 0:
            if sum(lost_items.values()) == 1:
                was_word = "was"
            else:
                was_word = "were"
            actor_utility.add_logistics_incident_to_report(
                self,
                f"{actor_utility.summarize_amount_dict(lost_items)} {was_word} lost due to insufficient storage space.",
            )

    def set_name(self, new_name):
        """
        Description:
            Sets this actor's name, also updating its name icon if applicable
        Input:
            string new_name: Name to set this actor's name to
        Output:
            None
        """
        super().set_name(new_name)
        if new_name == None:
            return
        if (
            not self.is_abstract_location
        ):  # Don't include name icon for abstract locations
            # Make sure user is not allowed to input default or *.png as a location name
            if self.name_icon:
                self.name_icon.remove()

            y_offset = -0.75
            has_building = any(
                current_building.building_type.key != constants.INFRASTRUCTURE
                for current_building in self.get_buildings()
            )
            if (
                has_building
            ):  # Modify location of name icon if any non-infrastructure buildings are present
                y_offset += 0.3

            self.name_icon = constants.ActorCreationManager.create_interface_element(
                {
                    "image_id": actor_utility.generate_label_image_id(
                        new_name, y_offset=y_offset
                    ),
                    "init_type": constants.HOSTED_ICON,
                    "location": self,
                },
            )
        self.publish_events(constants.LOCATION_SET_NAME_ROUTE)
