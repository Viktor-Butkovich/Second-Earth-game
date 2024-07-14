# Contains functionality for terrain management classes

import random
import json
import os
from typing import List, Dict
from ...util import utility, actor_utility
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags


class terrain_manager_template:
    """
    Object that controls terrain templates
    """

    def __init__(self):
        """
        Description:
            Initializes this object
        Input:
            None
        Output:
            None
        """
        self.terrain_variant_dict: Dict[str, int] = {}
        self.parameter_to_terrain: Dict[str, str] = {}
        self.terrain_list: List[str] = []
        self.terrain_parameter_keywords = {
            "altitude": {
                1: "very low",
                2: "low",
                3: "medium",
                4: "high",
                5: "very high",
                6: "stratospheric",
            },
            "temperature": {
                -5: "frozen",
                -4: "frozen",
                -3: "frozen",
                -2: "frozen",
                -1: "frozen",
                0: "frozen",
                1: "frozen",
                2: "cold",
                3: "cool",
                4: "warm",
                5: "hot",
                6: "scorching",
                7: "scorching",
                8: "scorching",
                9: "scorching",
                10: "scorching",
                11: "scorching",
                12: "scorching",
            },
            "roughness": {
                1: "flat",
                2: "rolling",
                3: "hilly",
                4: "rugged",
                5: "mountainous",
                6: "extreme",
            },
            "vegetation": {
                1: "barren",
                2: "sparse",
                3: "light",
                4: "medium",
                5: "heavy",
                6: "lush",
            },
            "soil": {1: "rock", 2: "sand", 3: "clay", 4: "silt", 5: "peat", 6: "loam"},
            "water": {
                1: "parched",
                2: "dry",
                3: "wet",
                4: "soaked",
                5: "shallow",
                6: "deep",
            },
        }
        self.load_terrains("configuration/TDG.json")
        self.load_tuning("configuration/terrain_generation_tuning.json")

    def load_tuning(self, file_name):
        """
        Decription:
            Loads world generation tuning parameters from the inputted file
        Input:
            string file_name: File path to the tuning JSON file
        Output:
            None
        """
        with open(file_name) as active_file:
            self.tuning_dict = json.load(active_file)

    def get_tuning(self, tuning_type):
        """
        Description:
            Gets the tuning value for the inputted tuning type, returning the default version if none is available
        Input:
            string tuning_type: Tuning type to get the value of
        Output:
            any: Tuning value for the inputted tuning type
        """
        return self.tuning_dict[tuning_type]

    def load_terrains(self, file_name):
        """
        Description:
            Loads terrains from the inputted file, storing in format "11111": "cold_desert"
        Input:
            string file_name: File path to the TDG output JSON file (refer to misc/TDG)
        Output:
            None
        """
        with open(file_name) as active_file:
            terrain_dict = json.load(
                active_file
            )  # dictionary of terrain name keys and terrain dict values for each terrain
        for terrain_name in terrain_dict:
            self.terrain_list.append(terrain_name)
            terrain = terrain_dict[terrain_name]
            for temperature in range(
                terrain["min_temperature"], terrain["max_temperature"] + 1
            ):
                for roughness in range(
                    terrain["min_roughness"], terrain["max_roughness"] + 1
                ):
                    for vegetation in range(
                        terrain["min_vegetation"], terrain["max_vegetation"] + 1
                    ):
                        for soil in range(terrain["min_soil"], terrain["max_soil"] + 1):
                            for water in range(
                                terrain["min_water"], terrain["max_water"] + 1
                            ):
                                self.parameter_to_terrain[
                                    f"{temperature}{roughness}{vegetation}{soil}{water}"
                                ] = terrain_name

            current_variant = 0
            while os.path.exists(
                f"graphics/terrains/{terrain_name}_{current_variant}.png"
            ):
                current_variant += 1
            current_variant -= 1  # back up from index that didn't work
            self.terrain_variant_dict[terrain_name] = (
                current_variant + 1
            )  # number of variants, variants in format 'mountains_0', 'mountains_1', etc.

    def classify(self, terrain_parameters):
        """
        Description:
            Classifies the inputted terrain parameters into a terrain type
        Input:
            dictionary terrain_parameters: Dictionary of terrain parameters to classify
        Output:
            string: Returns the terrain type that the inputted parameters classify as
        """
        # return random.choice(["mesa", "mountains", "desert"])
        return self.parameter_to_terrain[
            f"{max(min(terrain_parameters['temperature'], 6), 1)}{terrain_parameters['roughness']}{terrain_parameters['vegetation']}{terrain_parameters['soil']}{terrain_parameters['water']}"
        ]


class world_handler:
    """
    "Single source of truth" handler for planet-wide characteristics
    """

    def __init__(
        self, attached_grid, from_save: bool, input_dict: Dict[str, any]
    ) -> None:
        """
        Description:
            Initializes this object
        Input:
            cell attached_grid: Default grid to attach this handler to
            dictionary input_dict: Dictionary of saved information necessary to recreate this terrain handler if loading grid, or None if creating new terrain handler
        """
        self.default_grid = attached_grid
        if not from_save and not self.default_grid.is_abstract_grid:
            if self.get_tuning("earth_preset"):
                input_dict["color_filter"] = self.get_tuning("earth_color_filter")
            elif self.get_tuning("mars_preset"):
                input_dict["color_filter"] = self.get_tuning("mars_color_filter")
            else:
                input_dict["color_filter"] = {
                    "red": random.randrange(95, 106) / 100,
                    "green": random.randrange(95, 106) / 100,
                    "blue": random.randrange(95, 106) / 100,
                }
            input_dict["green_screen"] = self.generate_green_screen()

            if self.get_tuning("weighted_temperature_bounds"):
                input_dict["default_temperature"] = min(
                    max(
                        random.randrange(-5, 13),
                        self.get_tuning("base_temperature_lower_bound"),
                    ),
                    self.get_tuning("base_temperature_upper_bound"),
                )
            else:
                input_dict["default_temperature"] = random.randrange(
                    self.get_tuning("base_temperature_lower_bound"),
                    self.get_tuning("base_temperature_upper_bound") + 1,
                )
            if self.get_tuning("earth_preset"):
                input_dict["default_temperature"] = self.get_tuning(
                    "earth_base_temperature"
                )
            elif self.get_tuning("mars_preset"):
                input_dict["default_temperature"] = self.get_tuning(
                    "mars_base_temperature"
                )

            if self.get_tuning("earth_preset"):
                input_dict["water_multiplier"] = self.get_tuning(
                    "earth_water_multiplier"
                )
            elif self.get_tuning("mars_preset"):
                input_dict["water_multiplier"] = self.get_tuning(
                    "mars_water_multiplier"
                )
            else:
                if random.randrange(1, 7) >= 5:
                    input_dict["water_multiplier"] = random.randrange(
                        self.get_tuning("min_water_multiplier"),
                        self.get_tuning("max_water_multiplier") + 1,
                    )
                else:
                    input_dict["water_multiplier"] = random.randrange(
                        self.get_tuning("min_water_multiplier"),
                        self.get_tuning("med_water_multiplier") + 1,
                    )

        self.green_screen: Dict[str, Dict[str, any]] = input_dict.get(
            "green_screen", {}
        )
        self.color_filter: Dict[str, float] = input_dict.get(
            "color_filter", {"red": 1, "green": 1, "blue": 1}
        )
        self.default_temperature: int = input_dict.get("default_temperature", 0)
        self.water_multiplier: int = input_dict.get("water_multiplier", 0)

    def get_tuning(self, tuning_type):
        """
        Description:
            Gets the tuning value for the inputted tuning type, returning the default version if none is available
        Input:
            string tuning_type: Tuning type to get the value of
        Output:
            any: Tuning value for the inputted tuning type
        """
        if self.default_grid.is_abstract_grid:
            return None
        else:  # If world grid
            return self.default_grid.get_tuning(tuning_type)

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
            "color_filter": self.color_filter,
            "green_screen": self.green_screen,
            "default_temperature": self.default_temperature,
            "water_multiplier": self.water_multiplier,
        }

    def generate_green_screen(self) -> Dict[str, Dict[str, any]]:
        """
        Description:
            Generate a smart green screen dictionary for this world handler, containing color configuration for each terrain surface type
        Input:
            None
        Output:
            None
        """
        if self.get_tuning("mars_preset"):
            sand_color = (170, 107, 60)

        elif random.randrange(1, 4) != 1:
            sand_color = (
                random.randrange(150, 240),
                random.randrange(70, 196),
                random.randrange(20, 161),
            )

        else:
            base_sand_color = random.randrange(50, 200)
            sand_color = (
                base_sand_color * random.randrange(80, 121) / 100,
                base_sand_color * random.randrange(80, 121) / 100,
                base_sand_color * random.randrange(80, 121) / 100,
            )

        rock_multiplier = random.randrange(80, 141) / 100
        rock_color = (
            sand_color[0] * 0.45 * rock_multiplier,
            sand_color[1] * 0.5 * rock_multiplier,
            max(50, sand_color[2] * 0.6) * rock_multiplier,
        )

        water_color = (
            random.randrange(7, 25),
            random.randrange(15, 96),
            random.randrange(150, 221),
        )

        return {
            "ice": {
                "base_colors": [(150, 203, 230)],
                "tolerance": 180,
                "replacement_color": (
                    round(random.randrange(140, 181)),
                    round(random.randrange(190, 231)),
                    round(random.randrange(220, 261)),
                ),
            },
            "dirt": {
                "base_colors": [(124, 99, 29)],
                "tolerance": 60,
                "replacement_color": (
                    round((sand_color[0] + rock_color[0]) / 2),
                    round((sand_color[1] + rock_color[1]) / 2),
                    round((sand_color[2] + rock_color[2]) / 2),
                ),
            },
            "sand": {
                "base_colors": [(220, 180, 80)],
                "tolerance": 50,
                "replacement_color": (
                    round(sand_color[0]),
                    round(sand_color[1]),
                    round(sand_color[2]),
                ),
            },
            "shadowed sand": {
                "base_colors": [(184, 153, 64)],
                "tolerance": 35,
                "replacement_color": (
                    round(sand_color[0] * 0.8),
                    round(sand_color[1] * 0.8),
                    round(sand_color[2] * 0.8),
                ),
            },
            "deep water": {
                "base_colors": [(24, 62, 152)],
                "tolerance": 75,
                "replacement_color": (
                    round(water_color[0] * 0.9),
                    round(water_color[1] * 0.9),
                    round(water_color[2] * 1),
                ),
            },
            "shallow water": {
                "base_colors": [(65, 26, 93)],
                "tolerance": 75,
                "replacement_color": (
                    round(water_color[0]),
                    round(water_color[1] * 1.1),
                    round(water_color[2] * 1),
                ),
            },
            "rock": {
                "base_colors": [(90, 90, 90)],
                "tolerance": 90,
                "replacement_color": (
                    round(rock_color[0]),
                    round(rock_color[1]),
                    round(rock_color[2]),
                ),
            },
            "mountaintop": {
                "base_colors": [(233, 20, 233)],
                "tolerance": 75,
                "replacement_color": (
                    round(rock_color[0] * 1.4),
                    round(rock_color[1] * 1.4),
                    round(rock_color[2] * 1.4),
                ),
            },
            "faults": {
                "base_colors": [(54, 53, 40)],
                "tolerance": 0,
                "replacement_color": (
                    round(rock_color[0] * 0.5),
                    round(rock_color[1] * 0.5),
                    round(rock_color[2] * 0.5),
                ),
            },
        }

    def get_green_screen(self, terrain: str) -> Dict[str, Dict[str, any]]:
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
        self.terrain_features: Dict[str, bool] = input_dict.get("terrain_features", {})
        self.terrain_parameters: Dict[str, int] = input_dict.get(
            "terrain_parameters",
            {
                "altitude": 1,
                "temperature": 1,
                "roughness": 1,
                "vegetation": 1,
                "soil": 1,
                "water": 1,
            },
        )
        self.terrain_variant: int = input_dict.get("terrain_variant", 0)
        self.pole_distance_multiplier: float = (
            1.0  # 0.1 for polar cells, 1.0 for equatorial cells
        )
        self.inverse_pole_distance_multiplier: float = 1.0
        self.minima = {"temperature": -5}
        self.maxima = {"temperature": 12}
        self.terrain: str = constants.terrain_manager.classify(self.terrain_parameters)
        self.resource: str = input_dict.get("resource", "none")
        self.visible: bool = input_dict.get("visible", True)
        self.default_cell = attached_cell
        self.attached_cells: list = []
        self.add_cell(attached_cell)

    def change_parameter(self, parameter_name: str, change: int) -> None:
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
            parameter_name, self.terrain_parameters[parameter_name] + change
        )

    def set_parameter(self, parameter_name: str, new_value: int) -> None:
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

        self.terrain_parameters[parameter_name] = max(
            self.minima.get(parameter_name, 1),
            min(new_value, self.maxima.get(parameter_name, 6)),
        )

        if parameter_name == "water" and self.terrain_parameters["temperature"] >= constants.terrain_manager.get_tuning("water_boiling_point"):
            while self.terrain_parameters["water"] > 1:
                self.terrain_parameters["water"] -= 1
                status.strategic_map_grid.place_water(frozen_bound=constants.terrain_manager.get_tuning("water_boiling_point") - 1)
        elif (
            parameter_name == "temperature"
            and self.terrain_parameters["temperature"] >= constants.terrain_manager.get_tuning("water_boiling_point")
        ):
            self.set_parameter("water", 1)

        new_terrain = constants.terrain_manager.classify(self.terrain_parameters)

        if constants.current_map_mode != "terrain" or self.terrain != new_terrain or overlay_images != self.get_overlay_images():
            self.set_terrain(new_terrain)
            for cell in self.attached_cells:
                if cell.tile != "none":
                    cell.tile.set_terrain(self.terrain, update_image_bundle=True)

        if status.displayed_tile:
            for cell in self.attached_cells:
                if cell.tile == status.displayed_tile:
                    actor_utility.calibrate_actor_info_display(
                        status.tile_info_display, cell.tile
                    )

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
            self.get_parameter("temperature")
            <= constants.terrain_manager.get_tuning("water_freezing_point")
            and self.get_parameter("water") >= 2
        )

    def boiling(self) -> bool:
        """
        Description:
            Returns whether this terrain would have snow based on its temperature and water levels
        Input:
            None
        Output:
            boolean: True if this terrain would have snow, False if not
        """
        return (
            self.get_parameter("temperature")
            >= constants.terrain_manager.get_tuning("water_boiling_point") - 4
            and self.get_parameter("water") >= 3
        )

    def get_overlay_images(self) -> List[str]:
        """
        Description:
            Gets any overlay images that are part of terrain but not from original image
        Input:
            None
        Output:
            string list: List of overlay image file paths
        """
        return_list = []
        if self.has_snow():
            return_list.append(f"terrains/snow_{self.terrain_variant % 4}.png")
        elif self.boiling():
            return_list.append(f"terrains/boiling_{self.terrain_variant % 4}.png")
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
        """
        save_dict = {}
        save_dict["terrain_variant"] = self.terrain_variant
        save_dict["terrain_features"] = self.terrain_features
        save_dict["terrain_parameters"] = self.terrain_parameters
        save_dict["terrain"] = self.terrain
        save_dict["resource"] = self.resource
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
            if cell.tile != "none":
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
            if cell.tile != "none":
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
                if cell.tile != "none":
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

        if cell.tile != "none":
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
        if self.terrain_parameters["water"] >= 3 and self.terrain_parameters[
            "temperature"
        ] > constants.terrain_manager.get_tuning(
            "water_freezing_point"
        ):  # If enough liquid water to flow
            for adjacent_cell in self.attached_cells[0].adjacent_list:
                if adjacent_cell.get_parameter("altitude") <= self.get_parameter(
                    "altitude"
                ) and adjacent_cell.get_parameter(
                    "temperature"
                ) < constants.terrain_manager.get_tuning(
                    "water_boiling_point"
                ):
                    if (
                        adjacent_cell.get_parameter("water")
                        <= self.terrain_parameters["water"] - 2
                    ):
                        adjacent_cell.change_parameter("water", 1)
                        self.change_parameter("water", -1)
                        flowed = True

        if flowed: # Flow could recursively trigger flows in adjacent cells
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
            return self.get_world_handler().color_filter
        else:
            return {"red": 1, "green": 1, "blue": 1}

    def get_world_handler(self) -> world_handler:
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

        return world_green_screen
