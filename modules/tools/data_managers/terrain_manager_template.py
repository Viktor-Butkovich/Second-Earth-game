# Contains functionality for terrain management classes

import random
import json
import os
from math import ceil
from typing import List, Dict, Tuple, Any
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
                -6: "frozen",
                -5: "frozen",
                -4: "frozen",
                -3: "frozen",
                -2: "frozen",
                -1: "frozen",
                0: "frozen",
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
        self.load_terrains("configuration/terrain_definitions.json")
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
        self.earth_size = constants.map_size_options[4] ** 2
        atmosphere_size = (
            self.default_grid.area * 6
        )  # Atmosphere units required for 1 bar pressure (like Earth)
        if not from_save:
            if input_dict["grid_type"] == "strategic_map_grid":
                if constants.effect_manager.effect_active("earth_preset"):
                    input_dict["color_filter"] = self.get_tuning("earth_color_filter")
                elif constants.effect_manager.effect_active("mars_preset"):
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
                            random.randrange(-6, 12),
                            self.get_tuning("base_temperature_lower_bound"),
                        ),
                        self.get_tuning("base_temperature_upper_bound"),
                    )

                else:
                    input_dict["default_temperature"] = random.randrange(
                        self.get_tuning("base_temperature_lower_bound"),
                        self.get_tuning("base_temperature_upper_bound") + 1,
                    )
                input_dict["expected_temperature_target"] = max(
                    min(
                        input_dict["default_temperature"] + random.uniform(-0.5, 0.5),
                        10.95,
                    ),
                    -5.95,
                )
                if constants.effect_manager.effect_active("earth_preset"):
                    input_dict["global_parameters"] = {
                        constants.GRAVITY: self.get_tuning("earth_gravity"),
                        constants.RADIATION: self.get_tuning("earth_radiation"),
                        constants.MAGNETIC_FIELD: self.get_tuning(
                            "earth_magnetic_field"
                        ),
                        constants.INERT_GASES: round(
                            self.get_tuning("earth_inert_gases")
                            * self.get_tuning("earth_pressure")
                            * atmosphere_size
                        ),
                        constants.OXYGEN: round(
                            self.get_tuning("earth_oxygen")
                            * self.get_tuning("earth_pressure")
                            * atmosphere_size
                        ),
                        constants.GHG: round(
                            self.get_tuning("earth_GHG")
                            * self.get_tuning("earth_pressure")
                            * atmosphere_size
                        ),
                        constants.TOXIC_GASES: round(
                            self.get_tuning("earth_toxic_gases")
                            * self.get_tuning("earth_pressure")
                            * atmosphere_size
                        ),
                    }
                    input_dict["default_temperature"] = self.get_tuning(
                        "earth_base_temperature"
                    )
                    input_dict["expected_temperature_target"] = self.get_tuning(
                        "earth_expected_temperature_target"
                    )
                    input_dict["average_water_target"] = self.get_tuning(
                        "earth_average_water_target"
                    )

                elif constants.effect_manager.effect_active("mars_preset"):
                    input_dict["global_parameters"] = {
                        constants.GRAVITY: self.get_tuning("mars_gravity"),
                        constants.RADIATION: self.get_tuning("mars_radiation"),
                        constants.MAGNETIC_FIELD: self.get_tuning(
                            "mars_magnetic_field"
                        ),
                        constants.INERT_GASES: round(
                            self.get_tuning("mars_inert_gases")
                            * self.get_tuning("mars_pressure")
                            * atmosphere_size,
                            1,
                        ),
                        constants.OXYGEN: round(
                            self.get_tuning("mars_oxygen")
                            * self.get_tuning("mars_pressure")
                            * atmosphere_size,
                            1,
                        ),
                        constants.GHG: round(
                            self.get_tuning("mars_GHG")
                            * self.get_tuning("mars_pressure")
                            * atmosphere_size,
                            1,
                        ),
                        constants.TOXIC_GASES: round(
                            self.get_tuning("mars_toxic_gases")
                            * self.get_tuning("mars_pressure")
                            * atmosphere_size,
                            1,
                        ),
                    }
                    input_dict["default_temperature"] = self.get_tuning(
                        "mars_base_temperature"
                    )
                    input_dict["expected_temperature_target"] = self.get_tuning(
                        "mars_expected_temperature_target"
                    )
                    input_dict["average_water_target"] = self.get_tuning(
                        "mars_average_water_target"
                    )
                elif constants.effect_manager.effect_active("venus_preset"):
                    input_dict["global_parameters"] = {
                        constants.GRAVITY: self.get_tuning("venus_gravity"),
                        constants.RADIATION: self.get_tuning("venus_radiation"),
                        constants.MAGNETIC_FIELD: self.get_tuning(
                            "venus_magnetic_field"
                        ),
                        constants.INERT_GASES: round(
                            self.get_tuning("venus_inert_gases")
                            * self.get_tuning("venus_pressure")
                            * atmosphere_size,
                            1,
                        ),
                        constants.OXYGEN: round(
                            self.get_tuning("venus_oxygen")
                            * self.get_tuning("venus_pressure")
                            * atmosphere_size,
                            1,
                        ),
                        constants.GHG: round(
                            self.get_tuning("venus_GHG")
                            * self.get_tuning("venus_pressure")
                            * atmosphere_size,
                            1,
                        ),
                        constants.TOXIC_GASES: round(
                            self.get_tuning("venus_toxic_gases")
                            * self.get_tuning("venus_pressure")
                            * atmosphere_size,
                            1,
                        ),
                    }
                    input_dict["default_temperature"] = self.get_tuning(
                        "venus_base_temperature"
                    )
                    input_dict["expected_temperature_target"] = self.get_tuning(
                        "venus_expected_temperature_target"
                    )
                    input_dict["average_water_target"] = self.get_tuning(
                        "venus_average_water_target"
                    )
                else:
                    input_dict["global_parameters"] = {}
                    input_dict["global_parameters"][constants.GRAVITY] = round(
                        (self.default_grid.area / (constants.map_size_options[4] ** 2))
                        * random.uniform(0.7, 1.3),
                        2,
                    )
                    input_dict["global_parameters"][constants.RADIATION] = max(
                        random.randrange(0, 5), random.randrange(0, 5)
                    )
                    input_dict["global_parameters"][
                        constants.MAGNETIC_FIELD
                    ] = random.choices([0, 1, 2, 3, 4, 5], [5, 2, 2, 2, 2, 2], k=1)[0]
                    atmosphere_type = random.choice(
                        ["thick", "medium", "thin", "thin", "none"]
                    )
                    if (
                        input_dict["global_parameters"][constants.MAGNETIC_FIELD]
                        >= input_dict["global_parameters"][constants.RADIATION]
                    ):
                        if atmosphere_type in ["thin", "none"]:
                            atmosphere_type = "medium"
                    elif (
                        input_dict["global_parameters"][constants.MAGNETIC_FIELD]
                        >= input_dict["global_parameters"][constants.RADIATION] - 2
                    ):
                        if atmosphere_type == "none":
                            atmosphere_type = "thin"

                    if atmosphere_type == "thick":
                        input_dict["global_parameters"][constants.GHG] = random.choices(
                            [
                                random.randrange(0, atmosphere_size * 90),
                                random.randrange(0, atmosphere_size * 10),
                                random.randrange(0, atmosphere_size * 5),
                                random.randrange(0, atmosphere_size),
                                random.randrange(0, ceil(atmosphere_size * 0.1)),
                            ],
                            [1, 2, 2, 4, 4],
                            k=1,
                        )[0]
                        input_dict["global_parameters"][
                            constants.OXYGEN
                        ] = random.choices(
                            [
                                random.randrange(0, atmosphere_size * 10),
                                random.randrange(0, atmosphere_size * 5),
                                random.randrange(0, atmosphere_size * 2),
                                random.randrange(0, ceil(atmosphere_size * 0.5)),
                                random.randrange(0, ceil(atmosphere_size * 0.01)),
                            ],
                            [1, 2, 2, 4, 4],
                            k=1,
                        )[
                            0
                        ]
                        input_dict["global_parameters"][
                            constants.INERT_GASES
                        ] = random.choices(
                            [
                                random.randrange(0, atmosphere_size * 90),
                                random.randrange(0, atmosphere_size * 10),
                                random.randrange(0, atmosphere_size * 5),
                                random.randrange(0, atmosphere_size),
                                random.randrange(0, ceil(atmosphere_size * 0.1)),
                            ],
                            [1, 2, 2, 4, 4],
                            k=1,
                        )[
                            0
                        ]  # Same distribution as GHG
                        input_dict["global_parameters"][
                            constants.TOXIC_GASES
                        ] = random.choices(
                            [
                                random.randrange(0, atmosphere_size * 10),
                                random.randrange(0, atmosphere_size * 5),
                                random.randrange(0, atmosphere_size * 2),
                                random.randrange(0, ceil(atmosphere_size * 0.5)),
                                random.randrange(0, ceil(atmosphere_size * 0.01)),
                            ],
                            [1, 2, 2, 4, 4],
                            k=1,
                        )[
                            0
                        ]  # Same distribution as oxygen
                    elif atmosphere_type == "medium":
                        input_dict["global_parameters"][constants.GHG] = random.choices(
                            [
                                random.randrange(0, atmosphere_size),
                                random.randrange(0, ceil(atmosphere_size * 0.5)),
                                random.randrange(0, ceil(atmosphere_size * 0.3)),
                                random.randrange(0, ceil(atmosphere_size * 0.1)),
                                random.randrange(0, ceil(atmosphere_size * 0.01)),
                            ],
                            [3, 3, 3, 3, 3],
                            k=1,
                        )[0]
                        input_dict["global_parameters"][
                            constants.OXYGEN
                        ] = random.choices(
                            [
                                random.randrange(0, ceil(atmosphere_size * 0.6)),
                                random.randrange(0, ceil(atmosphere_size * 0.3)),
                                random.randrange(0, ceil(atmosphere_size * 0.15)),
                                random.randrange(0, ceil(atmosphere_size * 0.05)),
                                random.randrange(0, ceil(atmosphere_size * 0.01)),
                            ],
                            [3, 3, 3, 3, 3],
                            k=1,
                        )[
                            0
                        ]
                        input_dict["global_parameters"][
                            constants.INERT_GASES
                        ] = random.choices(
                            [
                                random.randrange(0, atmosphere_size),
                                random.randrange(0, ceil(atmosphere_size * 0.5)),
                                random.randrange(0, ceil(atmosphere_size * 0.3)),
                                random.randrange(0, ceil(atmosphere_size * 0.1)),
                                random.randrange(0, ceil(atmosphere_size * 0.01)),
                            ],
                            [3, 3, 3, 3, 3],
                            k=1,
                        )[
                            0
                        ]  # Same distribution as GHG
                        input_dict["global_parameters"][
                            constants.TOXIC_GASES
                        ] = random.choices(
                            [
                                random.randrange(0, ceil(atmosphere_size * 0.6)),
                                random.randrange(0, ceil(atmosphere_size * 0.3)),
                                random.randrange(0, ceil(atmosphere_size * 0.15)),
                                random.randrange(0, ceil(atmosphere_size * 0.05)),
                                random.randrange(0, ceil(atmosphere_size * 0.01)),
                            ],
                            [3, 3, 3, 3, 3],
                            k=1,
                        )[
                            0
                        ]  # Same distribution as oxygen
                    elif atmosphere_type == "thin":
                        input_dict["global_parameters"][constants.GHG] = random.choices(
                            [
                                random.randrange(0, ceil(atmosphere_size * 0.05)),
                                random.randrange(0, ceil(atmosphere_size * 0.01)),
                                random.randrange(0, ceil(atmosphere_size * 0.005)),
                                random.randrange(0, ceil(atmosphere_size * 0.001)),
                                0,
                            ],
                            [3, 3, 3, 3, 3],
                            k=1,
                        )[0]
                        input_dict["global_parameters"][
                            constants.OXYGEN
                        ] = random.choices(
                            [
                                random.randrange(0, ceil(atmosphere_size * 0.01)),
                                random.randrange(0, ceil(atmosphere_size * 0.005)),
                                random.randrange(0, ceil(atmosphere_size * 0.001)),
                                0,
                                0,
                            ],
                            [3, 3, 3, 3, 3],
                            k=1,
                        )[
                            0
                        ]
                        input_dict["global_parameters"][
                            constants.INERT_GASES
                        ] = random.choices(
                            [
                                random.randrange(0, ceil(atmosphere_size * 0.05)),
                                random.randrange(0, ceil(atmosphere_size * 0.01)),
                                random.randrange(0, ceil(atmosphere_size * 0.005)),
                                random.randrange(0, ceil(atmosphere_size * 0.001)),
                                0,
                            ],
                            [3, 3, 3, 3, 3],
                            k=1,
                        )[
                            0
                        ]  # Same distribution as GHG
                        input_dict["global_parameters"][
                            constants.TOXIC_GASES
                        ] = random.choices(
                            [
                                random.randrange(0, ceil(atmosphere_size * 0.01)),
                                random.randrange(0, ceil(atmosphere_size * 0.005)),
                                random.randrange(0, ceil(atmosphere_size * 0.001)),
                                0,
                                0,
                            ],
                            [3, 3, 3, 3, 3],
                            k=1,
                        )[
                            0
                        ]  # Same distribution as oxygen
                    elif atmosphere_type == "none":
                        input_dict["global_parameters"][constants.GHG] = 0
                        input_dict["global_parameters"][constants.OXYGEN] = 0
                        input_dict["global_parameters"][constants.INERT_GASES] = 0
                        input_dict["global_parameters"][constants.TOXIC_GASES] = 0

                    input_dict["average_water_target"] = random.choice(
                        [
                            random.uniform(0.0, 5.0),
                            random.uniform(0.0, 0.2),
                            random.uniform(0.0, 2.5),
                        ]
                    )

                    radiation_effect = (
                        input_dict["global_parameters"][constants.RADIATION]
                        - input_dict["global_parameters"][constants.MAGNETIC_FIELD]
                    )
                    if radiation_effect >= 3:
                        input_dict["global_parameters"][constants.INERT_GASES] = 0
                        input_dict["global_parameters"][constants.OXYGEN] = 0
                        input_dict["global_parameters"][constants.TOXIC_GASES] = round(
                            input_dict["global_parameters"][constants.TOXIC_GASES] / 2
                        )
                        input_dict["global_parameters"][constants.GHG] = round(
                            input_dict["global_parameters"][constants.GHG] / 2
                        )
                    elif radiation_effect >= 1:
                        input_dict["global_parameters"][constants.INERT_GASES] = round(
                            input_dict["global_parameters"][constants.INERT_GASES] / 2
                        )
                        input_dict["global_parameters"][constants.OXYGEN] = round(
                            input_dict["global_parameters"][constants.OXYGEN] / 2
                        )
            elif (
                input_dict["grid_type"] == "earth_grid"
            ):  # Replace with a series of grid_type constants
                input_dict["global_parameters"] = {
                    constants.GRAVITY: self.get_tuning("earth_gravity"),
                    constants.RADIATION: self.get_tuning("earth_radiation"),
                    constants.MAGNETIC_FIELD: self.get_tuning("earth_magnetic_field"),
                    constants.INERT_GASES: round(
                        self.get_tuning("earth_inert_gases") * (self.earth_size * 6)
                    ),
                    constants.OXYGEN: round(
                        self.get_tuning("earth_oxygen") * (self.earth_size * 6)
                    ),
                    constants.GHG: round(
                        self.get_tuning("earth_GHG") * (self.earth_size * 6)
                    ),
                    constants.TOXIC_GASES: round(
                        self.get_tuning("earth_toxic_gases") * (self.earth_size * 6)
                    ),
                }
                input_dict["average_water"] = self.get_tuning(
                    "earth_average_water_target"
                )
                input_dict["global_water"] = (
                    input_dict["average_water"] * self.earth_size
                )
                input_dict["default_temperature"] = self.get_tuning(
                    "earth_base_temperature"
                )
                input_dict["average_temperature"] = self.get_tuning(
                    "earth_average_temperature"
                )
                input_dict["global_temperature"] = (
                    input_dict["average_temperature"] * self.default_grid.area
                )
                input_dict["size"] = self.earth_size

        input_dict["global_parameters"][constants.INERT_GASES] = round(
            input_dict["global_parameters"][constants.INERT_GASES], 1
        )
        input_dict["global_parameters"][constants.OXYGEN] = round(
            input_dict["global_parameters"][constants.OXYGEN], 1
        )
        input_dict["global_parameters"][constants.GHG] = round(
            input_dict["global_parameters"][constants.GHG], 1
        )
        input_dict["global_parameters"][constants.TOXIC_GASES] = round(
            input_dict["global_parameters"][constants.TOXIC_GASES], 1
        )

        self.green_screen: Dict[str, Dict[str, any]] = input_dict.get(
            "green_screen", {}
        )
        self.color_filter: Dict[str, float] = input_dict.get(
            "color_filter", {"red": 1, "green": 1, "blue": 1}
        )
        self.expected_temperature_target: float = input_dict.get(
            "expected_temperature_target", 0.0
        )
        self.default_temperature: int = input_dict.get("default_temperature", 0)
        self.average_water_target: float = input_dict.get("average_water_target", 0.0)
        self.earth_global_water = round(
            self.get_tuning("earth_average_water_target") * self.earth_size
        )
        self.earth_average_temperature = self.get_tuning("earth_average_temperature")
        self.global_water = input_dict.get(
            "global_water", 0
        )  # Each tile starts with water 0, adjust whenever changed
        self.average_water = input_dict.get("average_water", 0.0)
        self.global_temperature = input_dict.get("global_temperature", 0)
        self.average_temperature = input_dict.get(
            "average_temperature", self.default_temperature
        )
        self.size: int = input_dict.get("size", self.default_grid.area)
        self.global_parameters: Dict[str, int] = {}
        for key in constants.global_parameters:
            self.set_parameter(key, input_dict.get("global_parameters", {}).get(key, 0))

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
        self.global_parameters[parameter_name] = new_value
        if parameter_name in [
            constants.OXYGEN,
            constants.GHG,
            constants.INERT_GASES,
            constants.TOXIC_GASES,
        ]:
            self.update_pressure()

        if status.displayed_tile:
            actor_utility.calibrate_actor_info_display(
                status.tile_info_display, status.displayed_tile
            )

    def update_pressure(self) -> None:
        self.global_parameters[constants.PRESSURE] = sum(
            [
                self.get_parameter(parameter)
                for parameter in [
                    constants.OXYGEN,
                    constants.GHG,
                    constants.INERT_GASES,
                    constants.TOXIC_GASES,
                ]
            ]
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
            "global_parameters": self.global_parameters,
            "average_water": self.average_water,
            "average_temperature": self.average_temperature,
            "global_water": self.global_water,
            "global_temperature": self.global_temperature,
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
        if constants.effect_manager.effect_active("earth_preset"):
            water_color = self.get_tuning("earth_water_color")
            ice_color = self.get_tuning("earth_ice_color")
            sand_color = self.get_tuning("earth_sand_color")
            rock_color = self.get_tuning("earth_rock_color")
        elif constants.effect_manager.effect_active("mars_preset"):
            water_color = self.get_tuning("mars_water_color")
            ice_color = self.get_tuning("mars_ice_color")
            sand_color = self.get_tuning("mars_sand_color")
            rock_color = self.get_tuning("mars_rock_color")
        elif constants.effect_manager.effect_active("venus_preset"):
            water_color = self.get_tuning("venus_water_color")
            ice_color = self.get_tuning("venus_ice_color")
            sand_color = self.get_tuning("venus_sand_color")
            rock_color = self.get_tuning("venus_rock_color")
        else:
            sand_type = random.randrange(1, 7)
            if sand_type >= 5:
                sand_color = (
                    random.randrange(150, 240),
                    random.randrange(70, 196),
                    random.randrange(20, 161),
                )
            elif sand_type >= 3:
                base_sand_color = random.randrange(50, 200)
                sand_color = (
                    base_sand_color * random.uniform(0.8, 1.2),
                    base_sand_color * random.uniform(0.8, 1.2),
                    base_sand_color * random.uniform(0.8, 1.2),
                )
            else:
                sand_color = (
                    random.randrange(3, 236),
                    random.randrange(3, 236),
                    random.randrange(3, 236),
                )

            rock_multiplier = random.uniform(0.8, 1.4)
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
            ice_color = (
                random.randrange(140, 181),
                random.randrange(190, 231),
                random.randrange(220, 261),
            )
        # Tuning should include water, ice, rock, sand RGB values, replacing any randomly generated values
        return {
            "ice": {
                "base_colors": [(150, 203, 230)],
                "tolerance": 180,
                "replacement_color": (
                    round(ice_color[0]),
                    round(ice_color[1]),
                    round(ice_color[2]),
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
        self.terrain_variant: int = input_dict.get("terrain_variant", 0)
        self.pole_distance_multiplier: float = (
            1.0  # 0.1 for polar cells, 1.0 for equatorial cells
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
        if parameter_name in [constants.WATER, constants.TEMPERATURE]:
            old_value = self.terrain_parameters[parameter_name]
        self.terrain_parameters[parameter_name] = max(
            self.minima.get(parameter_name, 0),
            min(new_value, self.maxima.get(parameter_name, 5)),
        )
        if (
            parameter_name == constants.WATER
            and not self.get_world_handler().default_grid.is_abstract_grid
        ):
            self.get_world_handler().global_water += (
                self.terrain_parameters[parameter_name] - old_value
            )
            self.get_world_handler().average_water = round(
                self.get_world_handler().global_water / self.get_world_handler().size, 2
            )
        elif (
            parameter_name == constants.TEMPERATURE
            and not self.get_world_handler().default_grid.is_abstract_grid
        ):
            self.get_world_handler().global_temperature += (
                self.terrain_parameters[parameter_name] - old_value
            )
            self.get_world_handler().average_temperature = round(
                self.get_world_handler().global_temperature
                / self.get_world_handler().size,
                2,
            )
            self.expected_temperature_offset = (
                self.terrain_parameters[parameter_name]
                - self.get_expected_temperature()
            )
        new_terrain = constants.terrain_manager.classify(self.terrain_parameters)

        if (
            constants.current_map_mode != "terrain"
            or self.terrain != new_terrain
            or overlay_images != self.get_overlay_images()
            or parameter_name == constants.KNOWLEDGE
        ):
            self.set_terrain(new_terrain)
            for cell in self.attached_cells:
                if cell.tile:
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
            Gets any overlay images that are part of terrain but not from original image
        Input:
            None
        Output:
            string list: List of overlay image file paths
        """
        return_list = []
        if self.has_snow():
            return_list.append(f"terrains/snow_{self.terrain_variant % 4}.png")
        elif self.boiling():  # If 4 below boiling, add steam
            return_list.append(f"terrains/boiling_{self.terrain_variant % 4}.png")
            if self.get_parameter(constants.WATER) >= 2 and self.get_parameter(
                constants.TEMPERATURE
            ) >= constants.terrain_manager.get_tuning("water_boiling_point"):
                # If boiling, add more steam as water increases
                return_list.append(
                    f"terrains/boiling_{(self.terrain_variant + 1) % 4}.png"
                )
                if self.get_parameter(constants.WATER) >= 4:
                    return_list.append(
                        f"terrains/boiling_{(self.terrain_variant + 2) % 4}.png"
                    )
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
        # save_dict["apparent_terrain_parameters"] = self.apparent_terrain_parameters
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
        if self.terrain_parameters[constants.WATER] >= 4 and self.terrain_parameters[
            constants.TEMPERATURE
        ] > constants.terrain_manager.get_tuning(
            "water_freezing_point"
        ):  # If enough liquid water to flow
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
                        adjacent_cell.change_parameter(constants.WATER, 1)
                        self.change_parameter(constants.WATER, -1)
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
