# Contains functionality for terrain management classes

import json
import os
from typing import List, Dict, Any
from modules.constants import constants, status, flags


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
        # Dictionary of terrain names to number of image variants possible
        self.terrain_variant_dict: Dict[str, int] = {}

        # Dictionary of parameter value combinations to terrain names
        self.parameter_to_terrain: Dict[str, str] = {}

        # Dictionary of terrain names to terrain definitions - better for giving parameter ranges but worse for classification
        self.terrain_range_dict: Dict[str, Dict[str, Any]] = {}

        self.terrain_list: List[str] = []  # List of all terrain names
        self.terrain_parameter_keywords = {
            constants.KNOWLEDGE: {
                0: "orbital view",
                1: "scouted",
                2: "visited",
                3: "surveyed",
                4: "sampled",
                5: "studied",
            },
            constants.ALTITUDE: {
                0: "very low",
                1: "low",
                2: "medium",
                3: "high",
                4: "very high",
                5: "stratospheric",
            },
            constants.TEMPERATURE: {
                -6: "freezing",
                -5: "freezing",
                -4: "freezing",
                -3: "freezing",
                -2: "freezing",
                -1: "freezing",
                0: "freezing",
                1: "cold",
                2: "cool",
                3: "warm",
                4: "hot",
                5: "scorching",
                6: "scorching",
                7: "scorching",
                8: "scorching",
                9: "scorching",
                10: "scorching",
                11: "scorching",
            },
            constants.ROUGHNESS: {
                0: "flat",
                1: "rolling",
                2: "hilly",
                3: "rugged",
                4: "mountainous",
                5: "extreme",
            },
            constants.VEGETATION: {
                0: "barren",
                1: "sparse",
                2: "light",
                3: "medium",
                4: "heavy",
                5: "lush",
            },
            constants.SOIL: {
                0: "rock",
                1: "sand",
                2: "clay",
                3: "silt",
                4: "peat",
                5: "loam",
            },
            constants.WATER: {
                0: "parched",
                1: "dry",
                2: "wet",
                3: "soaked",
                4: "shallow",
                5: "deep",
            },
        }
        self.temperature_bounds = {}
        for idx, bounds in enumerate(
            [
                (-185, -155),
                (-155, -125),
                (-125, -95),
                (-95, -65),
                (-65, -35),
                (-35, -5),
                (-5, 25),
                (25, 45),
                (45, 65),
                (65, 85),
                (85, 105),
                (105, 125),
                (125, 155),
                (155, 185),
                (185, 215),
                (215, 245),
                (245, 275),
                (275, 305),
            ]
        ):
            lower_bound, upper_bound = bounds
            if lower_bound == -185:
                self.temperature_bounds[idx - 6] = f"below {upper_bound} °F)"
            elif upper_bound == 305:
                self.temperature_bounds[idx - 6] = f"above {lower_bound} °F)"
            else:
                self.temperature_bounds[idx - 6] = (
                    f"between {lower_bound} °F and {upper_bound} °F)"
                )
        self.load_terrains("configuration/terrain_definitions.json")
        self.load_tuning("configuration/terrain_generation_tuning.json")

        if constants.effect_manager.effect_active("large_map"):
            world_dimensions_options = self.get_tuning("large_map_sizes")
        elif constants.effect_manager.effect_active("tiny_map"):
            world_dimensions_options = self.get_tuning("tiny_map_sizes")
        else:
            world_dimensions_options = self.get_tuning("map_sizes")
        constants.world_dimensions_options = world_dimensions_options
        constants.earth_dimensions = world_dimensions_options[
            self.get_tuning("earth_dimensions_index")
        ]

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
            self.terrain_range_dict = json.load(
                active_file
            )  # dictionary of terrain name keys and terrain dict values for each terrain
        for terrain_name in self.terrain_range_dict:
            self.terrain_list.append(terrain_name)
            terrain = self.terrain_range_dict[terrain_name]
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

            for special_terrain in [
                "clouds_base",
                "clouds_solid",
            ]:  # Load in terrains that need variants but don't occur in the terrain definitions
                current_variant = 0
                while os.path.exists(
                    f"graphics/terrains/{special_terrain}_{current_variant}.png"
                ):
                    current_variant += 1
                current_variant -= 1  # back up from index that didn't work
                self.terrain_variant_dict[special_terrain] = current_variant + 1

    def classify(self, terrain_parameters):
        """
        Description:
            Classifies the inputted terrain parameters into a terrain type
        Input:
            dictionary terrain_parameters: Dictionary of terrain parameters to classify
        Output:
            string: Returns the terrain type that the inputted parameters classify as
        """
        unbounded_temperature = f"{terrain_parameters['temperature'] + 1}{terrain_parameters['roughness'] + 1}{terrain_parameters['vegetation'] + 1}{terrain_parameters['soil'] + 1}{terrain_parameters['water'] + 1}"
        default = f"{max(min(terrain_parameters['temperature'] + 1, 6), 1)}{terrain_parameters['roughness'] + 1}{terrain_parameters['vegetation'] + 1}{terrain_parameters['soil'] + 1}{terrain_parameters['water'] + 1}"
        # Check -5 to 12 for temperature but use 1-6 if not defined
        # Terrain hypercube is fully defined within 1-6, but temperature terrains can exist outside of this range
        return self.parameter_to_terrain.get(
            unbounded_temperature, self.parameter_to_terrain[default]
        )
