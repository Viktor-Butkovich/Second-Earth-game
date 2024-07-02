# Contains functionality for terrain management classes

import random
import json
import os
from typing import List, Dict
from ...util import utility
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
            )  # number of variants, variants in format 'mountain_0', 'mountain_1', etc.

    def classify(self, terrain_parameters):
        """
        Description:
            Classifies the inputted terrain parameters into a terrain type
        Input:
            dictionary terrain_parameters: Dictionary of terrain parameters to classify
        Output:
            string: Returns the terrain type that the inputted parameters classify as
        """
        return self.parameter_to_terrain[
            f"{max(min(terrain_parameters['temperature'], 6), 1)}{terrain_parameters['roughness']}{terrain_parameters['vegetation']}{terrain_parameters['soil']}{terrain_parameters['water']}"
        ]


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
        Output:
            None
        """
        self.terrain_parameters[parameter_name] = max(
            self.minima.get(parameter_name, 1),
            min(new_value, self.maxima.get(parameter_name, 6)),
        )

        if parameter_name == "water" and self.terrain_parameters["temperature"] >= 10:
            while self.terrain_parameters["water"] > 1:
                self.terrain_parameters["water"] -= 1
                status.strategic_map_grid.place_water(frozen_bound=9)

        old_terrain = self.terrain
        self.terrain = constants.terrain_manager.classify(self.terrain_parameters)
        if old_terrain != self.terrain:
            for cell in self.attached_cells:
                if cell.tile != "none":
                    cell.tile.set_terrain(self.terrain, update_image_bundle=True)

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
                'terrain_variant': int value - Variant number to use for image file path, like mountain_0
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
        self.terrain = new_terrain
        self.terrain_variant = random.randrange(
            0, constants.terrain_manager.terrain_variant_dict.get(new_terrain, 1)
        )
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
        if self.default_cell.grid.world_handler:
            return self.default_cell.grid.world_handler.color_filter
        else:
            return {"red": 1, "green": 1, "blue": 1}

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
        Input:
            None
        Output:
            dictionary: Smart green screen dictionary for this terrain handler, or None for default tile appearance
        """
        # This is the authoritative source for terrain green screens, used by get_image_id_list and referencing constants for presets and world handler for world variations
        return None


class world_handler:
    """
    "Single source of truth" handler for planet-wide characteristics
    """

    def __init__(self, attached_grid, input_dict: Dict[str, any]) -> None:
        """
        Description:
            Initializes this object
        Input:
            cell attached_grid: Default grid to attach this handler to
            dictionary input_dict: Dictionary of saved information necessary to recreate this terrain handler if loading grid, or None if creating new terrain handler
        """
        self.default_grid = attached_grid
        self.color_filter = input_dict["color_filter"]

    def to_save_dict(self) -> Dict[str, any]:
        """
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
        """
        return {"color_filter": self.color_filter}
