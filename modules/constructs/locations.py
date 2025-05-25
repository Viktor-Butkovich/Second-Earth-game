import random
from typing import List, Dict, Any
from modules.util import actor_utility
from modules.constructs import world_handlers, item_types
from modules.constants import constants, status, flags


class location:
    """
    "Single source of truth" handler for the terrain/local characteristics of each version of a cell on different grids
    """

    def __init__(self, from_save: bool, input_dict: Dict[str, any] = None) -> None:
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Dictionary of saved information necessary to recreate this location if loading grid, or None if creating new location
        """
        if not input_dict:
            input_dict = {}
        self.x: int = input_dict["x"]
        self.y: int = input_dict["y"]
        self.world_handler: world_handlers.world_handler = input_dict["world_handler"]
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
        self.terrain: str = constants.terrain_manager.classify(self.terrain_parameters)
        self.resource: item_types.item_type = status.item_types.get(
            input_dict.get("resource", None), None
        )
        self.visible: bool = input_dict.get("visible", True)
        self.attached_cells: list = []
        self.expected_temperature_offset: float = 0.0
        self.terrain_features: Dict[str, bool] = {}
        for key, value in input_dict.get("terrain_features", {}).items():
            self.add_terrain_feature(value)
        self.contained_buildings: Dict[str, Any] = {}

    def local_attrition(self, attrition_type="health"):
        """
        Description:
            Returns the result of a roll that determines if a given unit or set of stored items should suffer attrition based on this cell's terrain and buildings. Bad terrain increases attrition frequency while infrastructure
                decreases it
        Input:
            string attrition_type = 'health': 'health' or 'inventory', refers to type of attrition being tested for. Used because inventory attrition can occur on Earth but not health attrition
        Output:
            boolean: Returns whether attrition should happen here based on this cell's terrain and buildings
        """
        if (
            constants.effect_manager.effect_active("boost_attrition")
            and random.randrange(1, 7) >= 4
        ):
            return True
        if self.get_world_handler().is_earth():
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
        self.update_appearance()

    def update_appearance(self) -> None:
        """
        Description:
            Forces an update and re-render of this locations subscribed tiles
        Input:
            None
        Output:
            None
        """
        self.attached_cells[0].tile.update_image_bundle()

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
            self.update_appearance()

    def get_building(self, building_type: str):
        """
        Description:
            Returns this cell's building of the inputted type, or None if that building is not present
        Input:
            string building_type: Type of building to search for
        Output:
            building/string: Returns whether this cell's building of the inputted type, or None if that building is not present
        """
        if building_type in [constants.ROAD, constants.RAILROAD]:
            return self.get_building(constants.INFRASTRUCTURE)
        else:
            return self.contained_buildings.get(building_type, None)

    def get_intact_building(self, building_type: str):
        """
        Description:
            Returns this cell's undamaged building of the inputted type, or None if that building is damaged or not present
        Input:
            string building_type: Type of building to search for
        Output:
            building/string: Returns this cell's undamaged building of the inputted type, or None if that building is damaged or not present
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
            Returns a list of the buildings contained in this cell
        Input:
            None
        Output:
            building list: Buildings contained in this cell
        """
        return [
            contained_building
            for contained_building in self.contained_buildings.values()
            if contained_building
        ]

    def get_intact_buildings(self) -> List[Any]:
        """
        Description:
            Returns a list of the nondamaged buildings contained in this cell
        Input:
            None
        Output:
            building list contained_buildings_list: nondamaged buildings contained in this cell
        """
        return [
            contained_building
            for contained_building in self.contained_buildings
            if contained_building and self.has_intact_building(contained_building.key)
        ]

    def has_destructible_buildings(self):
        """
        Description:
            Finds and returns if this cell is adjacent has any buildings that can be damaged by enemies (not roads or railroads), used for enemy cell targeting
        Input:
            None
        Output:
            boolean: Returns if this cell has any buildings that can be damaged by enemies
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
            Calculates and returns the cost of the next warehouses upgrade in this tile, based on the number of past warehouses upgrades
        Input:
            None
        Output:
            int: Returns the cost of the next warehouses upgrade in this tile, based on the number of past warehouse upgrades
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
        Description:
            Records a list of the cells directly adjacent to this cell. Also records these cells as values in a dictionary with string keys corresponding to their direction relative to this cell
        Input:
            None
        Output:
            None
        """
        self.adjacent_list = []
        self.adjacent_locations = {}
        world_dimensions = self.get_world_handler().world_dimensions
        for x, y, direction in [
            ((self.x - 1) % world_dimensions, self.y, "left"),
            ((self.x + 1) % world_dimensions, self.y, "right"),
            (self.x, (self.y + 1) % world_dimensions, "up"),
            (self.x, (self.y - 1) % world_dimensions, "down"),
        ]:
            self.adjacent_locations[direction] = self.get_world_handler().find_location(
                x, y
            )
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
            return self.get_world_handler().get_parameter_habitability(parameter_name)
        elif parameter_name == constants.TEMPERATURE:
            return actor_utility.get_temperature_habitability(
                self.get_parameter(parameter_name)
            )
        elif parameter_name == constants.WATER:
            if self.get_parameter(constants.WATER) >= 4 and self.get_parameter(
                constants.TEMPERATURE
            ) > self.get_world_handler().get_tuning("water_freezing_point"):
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
            Returns the habitability of this tile for the inputted units
        Input:
            Mob unit: Unit to check the habitability of this tile for
        Output:
            int: Returns habitability of this tile for the inputted unit
        """
        if (
            self.attached_cells[0].grid == status.globe_projection_grid
        ):  # If in orbit of planet
            self.get_world_handler() == status.globe_projection_grid.world_handler
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
            Returns the habitability of this tile based on current knowledge
        Input:
            None
        Output:
            int: Returns the habitability of this tile based on current knowledge
        """
        habitability_dict = self.get_habitability_dict()
        if self.get_world_handler().size > 1:  # If global habitability
            habitability_dict[constants.TEMPERATURE] = (
                actor_utility.get_temperature_habitability(
                    round(self.get_world_handler().average_temperature)
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
                When selecting a tile to change temperature, the most outlier tiles should be selected (farthest from expected)
        Input:
            None
        Output:
            float: Expected temperature of this terrain
        """
        if self.get_world_handler():
            average_temperature = self.get_world_handler().average_temperature
            altitude_effect = (
                -1 * self.get_parameter(constants.ALTITUDE)
            ) + self.get_world_handler().average_altitude
            altitude_effect_weight = 0.5
            # Colder to the extent that tile is higher than average altitude, and vice versa
            return (
                average_temperature
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

    def knowledge_available(self, information_type: str) -> bool:
        """
        Description:
            Returns whether the inputted type of information is visible for this location, based on knowledge of the tile
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
            boolean update_image: Whether to update the image of any subscribed tiles after changing the parameter
        Output:
            None
        """
        self.set_parameter(
            parameter_name,
            self.terrain_parameters[parameter_name] + change,
            update_display=update_display,
        )

    def set_parameter(
        self, parameter_name: str, new_value: int, update_display: bool = True
    ) -> None:
        """
        Description:
            Sets the value of a parameter for this location's cells
        Input:
            string parameter_name: Name of the parameter to change
            int new_value: New value for the parameter
            boolean update_image: Whether to update the image of any attached tiles after setting the parameter
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
        if (
            parameter_name == constants.WATER
            and not self.get_world_handler().is_abstract_world()
        ):
            self.get_world_handler().update_average_water()
        elif (
            parameter_name == constants.ALTITUDE
            and not self.get_world_handler().is_abstract_world()
        ):
            self.get_world_handler().update_average_altitude()
        elif (
            parameter_name == constants.TEMPERATURE
            and not self.get_world_handler().is_abstract_world()
        ):
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
                    self.get_world_handler().place_water(
                        radiation_effect=False, repeat_on_fail=True
                    )

        new_terrain = constants.terrain_manager.classify(self.terrain_parameters)

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
            self.set_terrain(new_terrain)
            if update_display and not flags.loading:
                status.current_world.update_globe_projection()

        if status.displayed_tile and status.displayed_tile.cell in self.attached_cells:
            actor_utility.calibrate_actor_info_display(
                status.tile_info_display, status.displayed_tile
            )

        for mob in status.mob_list:
            if mob.get_location() == self:
                mob.update_habitability()

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
            <= constants.terrain_manager.get_tuning("water_freezing_point")
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
            >= constants.terrain_manager.get_tuning("water_boiling_point") - 4
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
            ) >= constants.terrain_manager.get_tuning("water_boiling_point"):
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
                "green_screen": [self.get_world_handler().steam_color],
                "detail_level": constants.CLOUDS_DETAIL_LEVEL,
                "override_green_screen_colors": [(140, 183, 216)],
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
                'visible': boolean value - Whether this location is visible or not
                'terrain': string value - Terrain type of this location, like 'swamp'
                'terrain_variant': int value - Variant number to use for image file path, like mountains_0
                'terrain_features': string/boolean dictionary value - Dictionary containing an entry for each terrain feature in this location
                'terrain_parameters': string/int dictionary value - Dictionary containing 1-6 parameters for this location, like 'temperature': 1
                'resource': string value - Item type key of natural resource in this location, like "Gold" or None
                'local_weather_offset': float value - Temperature offset of this location from expected for the latitude
        """
        save_dict = {}
        save_dict["init_type"] = constants.LOCATION
        save_dict["coordinates"] = (self.x, self.y)
        save_dict["inventory"] = self.attached_cells[0].tile.inventory
        save_dict["terrain_variant"] = self.terrain_variant
        save_dict["terrain_features"] = self.terrain_features
        save_dict["terrain_parameters"] = self.terrain_parameters
        save_dict["terrain"] = self.terrain
        if self.resource:
            save_dict["resource"] = self.resource.key
        else:
            save_dict["resource"] = None
        save_dict["north_pole_distance_multiplier"] = (
            self.north_pole_distance_multiplier
        )
        save_dict["pole_distance_multiplier"] = self.pole_distance_multiplier
        save_dict["current_clouds"] = self.current_clouds
        save_dict["local_weather_offset"] = self.local_weather_offset
        return save_dict

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

    def set_terrain(self, new_terrain) -> None:
        """
        Description:
            Sets this location's terrain type, automatically generating a variant (not used for loading with pre-defined variant)
        Input:
            string new_terrain: New terrain type for this location and their tiles, like 'swamp'
        Output:
            None
        """
        try:
            if hasattr(
                self, "terrain_variant"
            ) and constants.terrain_manager.terrain_variant_dict.get(
                self.terrain, 1
            ) == constants.terrain_manager.terrain_variant_dict.get(
                new_terrain, 1
            ):
                pass  # Keep same terrain variant if number of variants is the same - keep same basic mountain layout, etc.
            else:
                self.terrain_variant = random.randrange(
                    0,
                    constants.terrain_manager.terrain_variant_dict.get(new_terrain, 1),
                )
        except:
            print(f"Error loading {new_terrain} variant")
            self.terrain_variant = random.randrange(
                0, constants.terrain_manager.terrain_variant_dict.get(new_terrain, 1)
            )
        self.terrain = new_terrain
        for cell in self.attached_cells:
            if cell.tile:
                cell.tile.set_terrain(self.terrain, update_image_bundle=False)

    def set_resource(self, new_resource: item_types.item_type) -> None:
        """
        Description:
            Sets this location's resource type
        Input:
            item_type new_resource: New resource type for this location, like "Gold" or None
        Output:
            None
        """
        self.resource = new_resource
        for cell in self.attached_cells:
            if cell.tile:
                cell.tile.set_resource(self.resource, update_image_bundle=False)

    def set_visibility(self, new_visibility, update_image_bundle=False) -> None:
        """
        Description:
            Sets the visibility of this cell and its attached tile to the inputted value. A visible cell's terrain and resource can be seen by the player.
        Input:
            boolean new_visibility: This cell's new visibility status
            boolean update_image_bundle: Whether to update the image bundle - if multiple sets are being used on a tile, optimal to only update after the last one
        Output:
            None
        """
        self.visible = new_visibility
        if update_image_bundle:
            for cell in self.attached_cells:
                if cell.tile:
                    cell.tile.update_image_bundle()

    def add_cell(self, cell) -> None:
        """
        Description:
            Subscribes the inputted cell to this location, removing it from any previous location and updating its parameters to match this location
        Input:
            cell: Cell to add to this location
        Output:
            None
        """
        if cell.location:
            cell.location.remove_cell(cell)
        self.attached_cells.append(cell)
        cell.location = self

        if cell.tile:
            cell.tile.set_terrain(self.terrain, update_image_bundle=False)
            cell.tile.set_resource(self.resource, update_image_bundle=False)
            cell.tile.update_image_bundle()

    def remove_cell(self, cell) -> None:
        """
        Description:
            Removes the inputted cell from the terrain location - precondition that cell is in the terrain location
        Input:
            cell cell: Cell to remove from the terrain location
        Output:
            None
        """
        self.attached_cells.remove(cell)
        cell.location = None
        if not self.attached_cells:
            del self

    def flow(self) -> None:
        """
        Description:
            Recursively flows water from this cell to any adjacent cells, if possible. Water flows between cells based on altitude and temperature - water flows to
                non-higher altitudes if there is much more water at the origin and if the origin water is liquid
        Input:
            None
        Output:
            None
        """
        flowed = False
        if (
            self.get_parameter(constants.WATER) >= 4
            and self.get_parameter(constants.TEMPERATURE)
            > constants.terrain_manager.get_tuning("water_freezing_point") - 1
        ):  # If enough liquid water to flow - frozen or 1 lower (occasionally liquid)
            for adjacent_location in self.adjacent_list:
                if adjacent_location.get_parameter(
                    constants.ALTITUDE
                ) <= self.get_parameter(
                    constants.ALTITUDE
                ) and adjacent_location.get_parameter(
                    constants.TEMPERATURE
                ) < constants.terrain_manager.get_tuning(
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
        if self.get_world_handler():
            color_filter = self.get_world_handler().color_filter.copy()
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

    def get_world_handler(self) -> world_handlers.world_handler:
        """
        Description:
            Returns the world handler corresponding to this location
        Input:
            None
        Output:
            world_handler: World handler corresponding to this location, or None if none exists yet
        """
        return self.world_handler

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
                Each category can have a preset smart green screen, with per-terrain or per-tile modifications controlled by world and locations
                    World handler handles per-terrain modifications, like dunes sand being slightly different from desert sand, while both are still "Mars red"
                    Location handles local modifications, like a tile with earth-imported soil looking different from default planet soil
                This system could also work for skin shading, polar dust, light levels, vegetation, resources, building appearances, etc.
            Serves as authoritative source for terrain green screens, used by get_image_id_list and referencing constants for presets and world handler for world variations
        Input:
            None
        Output:
            dictionary: Smart green screen dictionary for this location, or None for default tile appearance
        """
        world_green_screen = self.get_world_handler().get_green_screen(self.terrain)

        # Make any per-tile modifications

        return constants.WORLD_GREEN_SCREEN_DEFAULTS
        # return world_green_screen

    def get_brightness(self) -> float:
        """
        Description:
            Calculates and returns the average RGB value of this tile's terrain
        Input:
            None
        Output:
            float: Returns the average RGB value of this tile's terrain
        """
        if self.attached_cells:
            image_id = self.attached_cells[0].tile.get_image_id_list(
                terrain_only=True,
                force_pixellated=True,
                allow_mapmodes=False,
                allow_clouds=False,
            )
            status.albedo_free_image.set_image(image_id)
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
        else:
            return 1.0 - self.get_world_handler().get_tuning("earth_albedo_multiplier")
