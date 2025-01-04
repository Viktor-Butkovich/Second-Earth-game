import random
from typing import List, Dict, Any
from modules.util import actor_utility
from modules.constructs import world_handlers
from modules.constants import constants, status, flags


class terrain_handler:
    """
    "Single source of truth" handler for the terrain/local characteristics of each version of a cell on different grids
    """

    def __init__(self, attached_cell, input_dict: Dict[str, any] = None) -> None:
        """
        Description:
            Initializes this object
        Input:
            cell attached_cell: Default strategic_map_grid cell to attach this handler to
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Dictionary of saved information necessary to recreate this terrain handler if loading grid, or None if creating new terrain handler
        """
        if not input_dict:
            input_dict = {}
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
        self.resource: str = input_dict.get("resource", None)
        self.visible: bool = input_dict.get("visible", True)
        self.default_cell = attached_cell
        self.attached_cells: list = []
        self.add_cell(attached_cell)
        self.expected_temperature_offset: float = 0.0
        self.terrain_features: Dict[str, bool] = {}
        for key, value in input_dict.get("terrain_features", {}).items():
            self.add_terrain_feature(value)

    def calculate_parameter_habitability(self, parameter_name: str) -> int:
        """
        Description:
            Calculates and returns the habitability effect of a particular parameter
        Input:
            string parameter_name: Name of the parameter to calculate habitability for
        Output:
            int: Returns the habitability effect of the inputted parameter, from 0 to 5 (5 is perfect, 0 is deadly)
        """
        if parameter_name in constants.global_parameters:
            return self.get_world_handler().calculate_parameter_habitability(
                parameter_name
            )
        elif parameter_name == constants.TEMPERATURE:
            return actor_utility.calculate_temperature_habitability(
                self.get_parameter(parameter_name)
            )
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
            habitability = self.calculate_parameter_habitability(terrain_parameter)
            if (not omit_perfect) or habitability != constants.HABITABILITY_PERFECT:
                habitability_dict[
                    terrain_parameter
                ] = self.calculate_parameter_habitability(terrain_parameter)
        return habitability_dict

    def get_unit_habitability(self, unit) -> int:
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
        if unit.any_permissions(
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
        if self.default_cell.grid.is_abstract_grid:  # If global habitability
            habitability_dict[
                constants.TEMPERATURE
            ] = actor_utility.calculate_temperature_habitability(
                round(self.get_world_handler().average_temperature)
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
            return average_temperature - 3.5 + (5 * self.pole_distance_multiplier)
        else:
            return 0.0

    def add_terrain_feature(self, terrain_feature_dict: Dict[str, Any]) -> None:
        """
        Description:
            Adds a terrain feature with the inputted dictionary to this terrain handler
        Input:
            dictionary terrain_feature_dict: Dictionary containing information about the terrain feature to add
                Requires feature type and anything unique about this particular instance, like name
        Output:
            None
        """
        self.terrain_features[
            terrain_feature_dict["feature_type"]
        ] = terrain_feature_dict
        feature_type = status.terrain_feature_types[
            terrain_feature_dict["feature_type"]
        ]
        feature_key = terrain_feature_dict["feature_type"].replace(" ", "_")

        if feature_type.tracking_type == constants.UNIQUE_FEATURE_TRACKING:
            setattr(status, feature_key, self.attached_cells[0])
        elif feature_type.tracking_type == constants.LIST_FEATURE_TRACKING:
            feature_key += "_list"
            getattr(status, feature_key).append(self.attached_cells[0])

    def knowledge_available(self, information_type: str) -> bool:
        """
        Description:
            Returns whether the inputted type of information is visible for this terrain handler, based on knowledge of the tile
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
            Changes the value of a parameter for this handler's cells
        Input:
            string parameter_name: Name of the parameter to change
            int change: Amount to change the parameter by
            boolean update_image: Whether to update the image of any attached tiles after changing the parameter
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
            Sets the value of a parameter for this handler's cells
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
            and not self.get_world_handler().default_grid.is_abstract_grid
        ):
            self.get_world_handler().update_average_water()
        elif (
            parameter_name == constants.TEMPERATURE
            and not self.get_world_handler().default_grid.is_abstract_grid
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
                    self.get_world_handler().default_grid.place_water(
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
            for cell in self.attached_cells:
                if cell.tile:
                    cell.tile.set_terrain(self.terrain, update_image_bundle=True)
            if update_display and not flags.loading:
                status.strategic_map_grid.update_globe_projection()

        if status.displayed_tile:
            for cell in self.attached_cells:
                if cell.tile == status.displayed_tile:
                    actor_utility.calibrate_actor_info_display(
                        status.tile_info_display, cell.tile
                    )
        for mob in status.mob_list:
            if mob.get_cell() and mob.get_cell().terrain_handler == self:
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
                'visible': boolean value - Whether this handler's cells are visible or not
                'terrain': string value - Terrain type of this handler's cells and their tiles, like 'swamp'
                'terrain_variant': int value - Variant number to use for image file path, like mountains_0
                'terrain_features': string/boolean dictionary value - Dictionary containing an entry for each terrain feature in this handler's cells
                'terrain_parameters': string/int dictionary value - Dictionary containing 1-6 parameters for this handler's cells, like 'temperature': 1
                'resource': string value - Resource type of this handler's cells and their tiles, like 'exotic wood'
                'local_weather_offset': float value - Temperature offset of this handler's cells from the usual at the same location
        """
        save_dict = {}
        save_dict["terrain_variant"] = self.terrain_variant
        save_dict["terrain_features"] = self.terrain_features
        save_dict["terrain_parameters"] = self.terrain_parameters
        save_dict["terrain"] = self.terrain
        save_dict["resource"] = self.resource
        save_dict[
            "north_pole_distance_multiplier"
        ] = self.north_pole_distance_multiplier
        save_dict["pole_distance_multiplier"] = self.pole_distance_multiplier
        save_dict["current_clouds"] = self.current_clouds
        save_dict["local_weather_offset"] = self.local_weather_offset
        return save_dict

    def get_parameter(self, parameter_name: str) -> int:
        """
        Description:
            Returns the value of the inputted parameter from this terrain handler
        Input:
            string parameter: Name of the parameter to get
        Output:
            None
        """
        return self.terrain_parameters[parameter_name]

    def set_terrain(self, new_terrain) -> None:
        """
        Description:
            Sets this handler's terrain type, automatically generating a variant (not used for loading with pre-defined variant)
        Input:
            string new_terrain: New terrain type for this handler's cells and their tiles, like 'swamp'
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

    def set_resource(self, new_resource) -> None:
        """
        Description:
            Sets this handler's resource type
        Input:
            string new_terrain: New resource type for this handler's cells and their tiles, like 'rubber'
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
            Adds the inputted cell to this handler, removing it from any previous handler and updating its parameters to this handler's
        Input:
            cell: Cell to add to this handler
        Output:
            None
        """
        if cell.terrain_handler:
            cell.terrain_handler.remove_cell(cell)
        self.attached_cells.append(cell)
        cell.terrain_handler = self

        if cell.tile:
            cell.tile.set_terrain(self.terrain, update_image_bundle=False)
            cell.tile.set_resource(self.resource, update_image_bundle=False)
            cell.tile.update_image_bundle()

    def remove_cell(self, cell) -> None:
        """
        Description:
            Removes the inputted cell from the terrain handler - precondition that cell is in the terrain handler
        Input:
            cell cell: Cell to remove from the terrain handler
        Output:
            None
        """
        self.attached_cells.remove(cell)
        cell.terrain_handler = None
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
            self.terrain_parameters[constants.WATER] >= 4
            and self.terrain_parameters[constants.TEMPERATURE]
            > constants.terrain_manager.get_tuning("water_freezing_point") - 1
        ):  # If enough liquid water to flow - frozen or 1 lower (occasionally liquid)
            for adjacent_cell in self.attached_cells[0].adjacent_list:
                if adjacent_cell.get_parameter(
                    constants.ALTITUDE
                ) <= self.get_parameter(
                    constants.ALTITUDE
                ) and adjacent_cell.get_parameter(
                    constants.TEMPERATURE
                ) < constants.terrain_manager.get_tuning(
                    "water_boiling_point"
                ):
                    if (
                        adjacent_cell.get_parameter(constants.WATER)
                        <= self.terrain_parameters[constants.WATER] - 2
                    ):
                        adjacent_cell.change_parameter(
                            constants.WATER, 1, update_display=False
                        )
                        self.change_parameter(constants.WATER, -1, update_display=False)
                        flowed = True

        if flowed:  # Flow could recursively trigger flows in adjacent cells
            for adjacent_cell in self.attached_cells[0].adjacent_list:
                adjacent_cell.terrain_handler.flow()

    def get_color_filter(self) -> Dict[str, int]:
        """
        Description:
            Returns the color filter for this terrain handler's world handler, if any
        Input:
            None
        Output:
            dictionary: Color filter for this terrain handler's world handler
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
            return {"red": 1, "green": 1, "blue": 1}

    def get_world_handler(self) -> world_handlers.world_handler:
        """
        Description:
            Returns the world handler corresponding to this terrain handler
        Input:
            None
        Output:
            world_handler: World handler corresponding to this terrain handler, or None if none exists yet
        """
        return self.default_cell.grid.world_handler

    def get_green_screen(self) -> Dict[str, Dict[str, any]]:
        """
        Description:
            Returns a "smart green screen" dictionary for this terrain handler, or None for default tile appearance
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
                Each category can have a preset smart green screen, with per-terrain or per-tile modifications controlled by world and terrain handlers
                    World handler handles per-terrain modifications, like dunes sand being slightly different from desert sand, while both are still "Mars red"
                    Terrain handler handler per-tile modifications, like a tile with earth-imported soil looking different from default planet soil
                This system could also work for skin shading, polar dust, light levels, vegetation, resources, building appearances, etc.
            Serves as authoritative source for terrain green screens, used by get_image_id_list and referencing constants for presets and world handler for world variations
        Input:
            None
        Output:
            dictionary: Smart green screen dictionary for this terrain handler, or None for default tile appearance
        """
        world_green_screen = self.get_world_handler().get_green_screen(self.terrain)

        # Make any per-tile modifications

        return constants.WORLD_GREEN_SCREEN_DEFAULTS
        # return world_green_screen
