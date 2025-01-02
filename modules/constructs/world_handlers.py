import random
from math import ceil
from typing import List, Dict, Tuple
from modules.util import actor_utility
from modules.constants import constants, status, flags


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
        self.ideal_atmosphere_size = (
            self.default_grid.area * 6
        )  # Atmosphere units required for 1 atm pressure (like Earth)
        if not from_save:
            if input_dict["grid_type"] == constants.STRATEGIC_MAP_GRID_TYPE:
                input_dict["green_screen"] = self.generate_green_screen()

                preset = None
                if constants.effect_manager.effect_active("earth_preset"):
                    preset = "earth"
                elif constants.effect_manager.effect_active("mars_preset"):
                    preset = "mars"
                elif constants.effect_manager.effect_active("venus_preset"):
                    preset = "venus"

                if preset:
                    input_dict["name"] = preset.capitalize()
                    input_dict["rotation_direction"] = self.get_tuning(
                        f"{preset}_rotation_direction"
                    )
                    input_dict["rotation_speed"] = self.get_tuning(
                        f"{preset}_rotation_speed"
                    )
                    input_dict["global_parameters"] = {
                        constants.GRAVITY: self.get_tuning(f"{preset}_gravity"),
                        constants.RADIATION: self.get_tuning(f"{preset}_radiation"),
                        constants.MAGNETIC_FIELD: self.get_tuning(
                            f"{preset}_magnetic_field"
                        ),
                        constants.INERT_GASES: round(
                            self.get_tuning(f"{preset}_inert_gases")
                            * self.get_tuning(f"{preset}_pressure")
                            * self.ideal_atmosphere_size,
                            1,
                        ),
                        constants.OXYGEN: round(
                            self.get_tuning(f"{preset}_oxygen")
                            * self.get_tuning(f"{preset}_pressure")
                            * self.ideal_atmosphere_size,
                            1,
                        ),
                        constants.GHG: round(
                            self.get_tuning(f"{preset}_GHG")
                            * self.get_tuning(f"{preset}_pressure")
                            * self.ideal_atmosphere_size,
                            1,
                        ),
                        constants.TOXIC_GASES: round(
                            self.get_tuning(f"{preset}_toxic_gases")
                            * self.get_tuning(f"{preset}_pressure")
                            * self.ideal_atmosphere_size,
                            1,
                        ),
                    }
                    input_dict["default_temperature"] = self.get_tuning(
                        f"{preset}_base_temperature"
                    )
                    input_dict["expected_temperature_target"] = self.get_tuning(
                        f"{preset}_expected_temperature_target"
                    )
                    input_dict["average_water_target"] = self.get_tuning(
                        f"{preset}_average_water_target"
                    )
                    input_dict["sky_color"] = self.get_tuning(f"{preset}_sky_color")

                else:  # If no preset, create a random planet
                    input_dict.update(self.generate_global_parameters())
            elif (
                input_dict["grid_type"] == constants.EARTH_GRID_TYPE
            ):  # Replace with a series of grid_type constants
                input_dict["name"] = "Earth"
                input_dict["rotation_direction"] = self.get_tuning(
                    "earth_rotation_direction"
                )
                input_dict["rotation_speed"] = self.get_tuning("earth_rotation_speed")
                input_dict["global_parameters"] = {
                    constants.GRAVITY: self.get_tuning("earth_gravity"),
                    constants.RADIATION: self.get_tuning("earth_radiation"),
                    constants.MAGNETIC_FIELD: self.get_tuning("earth_magnetic_field"),
                    constants.INERT_GASES: round(
                        self.get_tuning("earth_inert_gases") * (self.earth_size * 6), 1
                    ),
                    constants.OXYGEN: round(
                        self.get_tuning("earth_oxygen") * (self.earth_size * 6), 1
                    ),
                    constants.GHG: round(
                        self.get_tuning("earth_GHG") * (self.earth_size * 6), 1
                    ),
                    constants.TOXIC_GASES: round(
                        self.get_tuning("earth_toxic_gases") * (self.earth_size * 6), 1
                    ),
                }
                input_dict["average_water"] = self.get_tuning(
                    "earth_average_water_target"
                )
                input_dict["default_temperature"] = self.get_tuning(
                    "earth_base_temperature"
                )
                input_dict["average_temperature"] = self.get_tuning(
                    "earth_expected_temperature_target"
                )
                input_dict["size"] = self.earth_size
                input_dict["sky_color"] = self.get_tuning("earth_sky_color")
            input_dict["default_sky_color"] = input_dict["sky_color"].copy()

        self.terrain_handlers: list = [
            current_cell.terrain_handler
            for current_cell in self.default_grid.get_flat_cell_list()
        ]
        self.name = input_dict["name"]
        self.rotation_direction = input_dict["rotation_direction"]
        self.rotation_speed = input_dict["rotation_speed"]
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
        self.average_temperature: float = input_dict.get("average_temperature", 0.0)
        self.earth_average_temperature = self.get_tuning(
            "earth_expected_temperature_target"
        )

        self.average_water_target: float = input_dict.get("average_water_target", 0.0)
        self.average_water: float = input_dict.get("average_water", 0.0)

        self.size: int = input_dict.get("size", self.default_grid.area)
        self.sky_color = input_dict["sky_color"]
        self.default_sky_color = input_dict["default_sky_color"]
        self.steam_color = [0, 0, 0]
        self.global_parameters: Dict[str, int] = {}
        self.initial_atmosphere_offset = input_dict.get(
            "initial_atmosphere_offset", 0.001
        )
        for key in constants.global_parameters:
            self.set_parameter(key, input_dict.get("global_parameters", {}).get(key, 0))
        self.latitude_lines_setup()

    def generate_global_parameters(self) -> Dict[str, int]:
        """
        Description:
            Calculates and returns global parameter values for a ranodm planet
        Input:
            None
        Output:
            dictionary: Returns a dictionary of global parameter values for a random planet
        """
        input_dict: Dict[str, any] = {}

        input_dict["name"] = constants.flavor_text_manager.generate_flavor_text(
            "planet_names"
        )

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

        input_dict["rotation_direction"] = random.choice([1, -1])
        input_dict["rotation_speed"] = random.choice([1, 2, 2, 3, 4, 5])
        input_dict["average_water_target"] = random.choice(
            [
                random.uniform(0.0, 5.0),
                random.uniform(0.0, 1.0),
                random.uniform(0.0, 4.0),
            ]
        )
        input_dict["sky_color"] = [
            random.randrange(0, 256) for _ in range(3)
        ]  # Random sky color

        global_parameters: Dict[str, float] = {}
        global_parameters[constants.GRAVITY] = round(
            (self.default_grid.area / (constants.map_size_options[4] ** 2))
            * random.uniform(0.7, 1.3),
            2,
        )
        global_parameters[constants.RADIATION] = max(
            random.randrange(0, 5), random.randrange(0, 5)
        )
        global_parameters[constants.MAGNETIC_FIELD] = random.choices(
            [0, 1, 2, 3, 4, 5], [5, 2, 2, 2, 2, 2], k=1
        )[0]
        atmosphere_type = random.choice(
            ["thick", "thick", "medium", "thin", "thin", "none"]
        )
        if (
            global_parameters[constants.MAGNETIC_FIELD]
            >= global_parameters[constants.RADIATION]
        ):
            if atmosphere_type in ["thin", "none"]:
                atmosphere_type = "medium"
        elif (
            global_parameters[constants.MAGNETIC_FIELD]
            >= global_parameters[constants.RADIATION] - 2
        ):
            if atmosphere_type == "none":
                atmosphere_type = "thin"

        if atmosphere_type == "thick":
            global_parameters[constants.GHG] = random.choices(
                [
                    random.randrange(0, self.ideal_atmosphere_size * 90),
                    random.randrange(0, self.ideal_atmosphere_size * 10),
                    random.randrange(0, self.ideal_atmosphere_size * 5),
                    random.randrange(0, self.ideal_atmosphere_size),
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.1)),
                ],
                [2, 4, 4, 4, 6],
                k=1,
            )[0]
            global_parameters[constants.OXYGEN] = random.choices(
                [
                    random.randrange(0, self.ideal_atmosphere_size * 10),
                    random.randrange(0, self.ideal_atmosphere_size * 5),
                    random.randrange(0, self.ideal_atmosphere_size * 2),
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.5)),
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.01)),
                ],
                [2, 4, 4, 4, 6],
                k=1,
            )[0]
            global_parameters[constants.INERT_GASES] = random.choices(
                [
                    random.randrange(0, self.ideal_atmosphere_size * 90),
                    random.randrange(0, self.ideal_atmosphere_size * 10),
                    random.randrange(0, self.ideal_atmosphere_size * 5),
                    random.randrange(0, self.ideal_atmosphere_size),
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.1)),
                ],
                [2, 4, 4, 4, 6],
                k=1,
            )[
                0
            ]  # Same distribution as GHG
            global_parameters[constants.TOXIC_GASES] = random.choices(
                [
                    random.randrange(0, self.ideal_atmosphere_size * 10),
                    random.randrange(0, self.ideal_atmosphere_size * 5),
                    random.randrange(0, self.ideal_atmosphere_size * 2),
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.5)),
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.01)),
                ],
                [2, 4, 4, 4, 6],
                k=1,
            )[
                0
            ]  # Same distribution as oxygen
        elif atmosphere_type == "medium":
            global_parameters[constants.GHG] = random.choices(
                [
                    random.randrange(0, self.ideal_atmosphere_size),
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.5)),
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.3)),
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.1)),
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.01)),
                ],
                [3, 3, 3, 3, 3],
                k=1,
            )[0]
            global_parameters[constants.OXYGEN] = random.choices(
                [
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.6)),
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.3)),
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.15)),
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.05)),
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.01)),
                ],
                [3, 3, 3, 3, 3],
                k=1,
            )[0]
            global_parameters[constants.INERT_GASES] = random.choices(
                [
                    random.randrange(0, self.ideal_atmosphere_size),
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.5)),
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.3)),
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.1)),
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.01)),
                ],
                [3, 3, 3, 3, 3],
                k=1,
            )[
                0
            ]  # Same distribution as GHG
            global_parameters[constants.TOXIC_GASES] = random.choices(
                [
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.6)),
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.3)),
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.15)),
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.05)),
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.01)),
                ],
                [3, 3, 3, 3, 3],
                k=1,
            )[
                0
            ]  # Same distribution as oxygen
        elif atmosphere_type == "thin":
            global_parameters[constants.GHG] = random.choices(
                [
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.05)),
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.01)),
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.005)),
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.001)),
                    0,
                ],
                [3, 3, 3, 3, 3],
                k=1,
            )[0]
            global_parameters[constants.OXYGEN] = random.choices(
                [
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.01)),
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.005)),
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.001)),
                    0,
                    0,
                ],
                [3, 3, 3, 3, 3],
                k=1,
            )[0]
            global_parameters[constants.INERT_GASES] = random.choices(
                [
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.05)),
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.01)),
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.005)),
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.001)),
                    0,
                ],
                [3, 3, 3, 3, 3],
                k=1,
            )[
                0
            ]  # Same distribution as GHG
            global_parameters[constants.TOXIC_GASES] = random.choices(
                [
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.01)),
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.005)),
                    random.randrange(0, ceil(self.ideal_atmosphere_size * 0.001)),
                    0,
                    0,
                ],
                [3, 3, 3, 3, 3],
                k=1,
            )[
                0
            ]  # Same distribution as oxygen
        elif atmosphere_type == "none":
            global_parameters[constants.GHG] = 0
            global_parameters[constants.OXYGEN] = 0
            global_parameters[constants.INERT_GASES] = 0
            global_parameters[constants.TOXIC_GASES] = 0

        radiation_effect = (
            global_parameters[constants.RADIATION]
            - global_parameters[constants.MAGNETIC_FIELD]
        )
        if radiation_effect >= 3:
            global_parameters[constants.INERT_GASES] = 0
            global_parameters[constants.OXYGEN] = 0
            global_parameters[constants.TOXIC_GASES] /= 2
            global_parameters[constants.GHG] /= 2
        elif radiation_effect >= 1:
            global_parameters[constants.INERT_GASES] /= 2
            global_parameters[constants.OXYGEN] /= 2

        for component in constants.ATMOSPHERE_COMPONENTS:
            if global_parameters[component] != 0:
                global_parameters[component] += random.uniform(-1.0, 1.0)
            global_parameters[component] = max(
                0, round(global_parameters[component], 1)
            )

        input_dict["global_parameters"] = global_parameters
        return input_dict

    def latitude_lines_setup(self):
        """
        Description:
            15 x 15 grid has north pole 0, 0 and south pole 7, 7
            If centered at (11, 11), latitude line should include (0, 0), (14, 14), (13, 13), (12, 12), (11, 11), (10, 10), (9, 9), (8, 8), (7, 7)
                The above line should be used if centered at any of the above coordinates
            If centered at (3, 11), latitude line should include (0, 0), (1, 14), (1, 13), (2, 12), (3, 11), (4, 10), (5, 9), (6, 8), (7, 7)

            Need to draw latitude lines using the above method, centered on (0, 7), (1, 6), (2, 5), (3, 4), (4, 3), (5, 2), (6, 1), (7, 0), (8, 14), (9, 13), (10, 12), (11, 11), (12, 10), (13, 9), (14, 8)
                ^ Forms diagonal line
            Also need to draw latitude lines on other cross: (0, 8), (1, 9), (2, 10), (3, 11), (4, 12), (5, 13), (6, 14), (7, 0), (8, 1), (9, 2), (10, 3), (11, 4), (12, 5), (13, 6), (14, 7)
        Input:
            None
        Output:
            None
        """
        self.latitude_lines = []
        self.alternate_latitude_lines = []
        self.latitude_lines_types = [
            [None for _ in range(self.default_grid.coordinate_height)]
            for _ in range(self.default_grid.coordinate_width)
        ]
        north_pole = (0, 0)
        south_pole = (
            self.default_grid.coordinate_width // 2,
            self.default_grid.coordinate_height // 2,
        )
        self.equatorial_coordinates = []
        self.alternate_equatorial_coordinates = []
        for equatorial_x in range(self.default_grid.coordinate_width):
            equatorial_y = (
                (self.default_grid.coordinate_width // 2) - equatorial_x
            ) % self.default_grid.coordinate_height
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
                (self.default_grid.coordinate_height // 2) + equatorial_x + 1
            ) % self.default_grid.coordinate_height
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
        latitude_line_type = self.latitude_lines_types[coordinates[0]][coordinates[1]]
        if latitude_line_type == None:
            for offset in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                latitude_line_type = self.latitude_lines_types[
                    (coordinates[0] + offset[0]) % self.default_grid.coordinate_width
                ][(coordinates[1] + offset[1]) % self.default_grid.coordinate_height]
                if latitude_line_type != None:
                    coordinates = (
                        (coordinates[0] + offset[0])
                        % self.default_grid.coordinate_width,
                        (coordinates[1] + offset[1])
                        % self.default_grid.coordinate_height,
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
            x_distance = self.default_grid.x_distance_coords(x, destination[0])
            y_distance = self.default_grid.y_distance_coords(y, destination[1])
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
                    self.default_grid.x_distance_coords(
                        (x + 1) % self.default_grid.coordinate_width, destination[0]
                    )
                    < x_distance
                ):
                    x = (x + 1) % self.default_grid.coordinate_width
                else:
                    x = (x - 1) % self.default_grid.coordinate_width
            if "Y" in traverse:
                if (
                    self.default_grid.y_distance_coords(
                        (y + 1) % self.default_grid.coordinate_height, destination[1]
                    )
                    < y_distance
                ):
                    y = (y + 1) % self.default_grid.coordinate_height
                else:
                    y = (y - 1) % self.default_grid.coordinate_height
            line.append((x, y))
        return line

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
            parameter_name, round(self.global_parameters[parameter_name] + change, 2)
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
        self.global_parameters[parameter_name] = max(0, new_value)
        if parameter_name in constants.ATMOSPHERE_COMPONENTS:
            self.update_pressure()

        if status.displayed_tile:
            actor_utility.calibrate_actor_info_display(
                status.tile_info_display, status.displayed_tile
            )
        for mob in status.mob_list:
            if mob.get_cell() and mob.get_cell().grid.world_handler == self:
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
        default_sky_color = self.default_sky_color
        earth_sky_color = self.get_tuning("earth_sky_color")
        total_offset = 0
        for atmosphere_component in constants.ATMOSPHERE_COMPONENTS:
            if self.get_parameter(constants.PRESSURE) == 0:
                composition = 0.01
            else:
                composition = self.get_parameter(
                    atmosphere_component
                ) / self.get_parameter(constants.PRESSURE)
            ideal = self.get_tuning(f"earth_{atmosphere_component}")
            if atmosphere_component == constants.TOXIC_GASES:
                offset = max(0, (composition - 0.001) / 0.001)
            if ideal != 0:
                offset = abs(composition - ideal) / ideal
            total_offset += offset
        if set_initial_offset:
            self.initial_atmosphere_offset = max(0.001, total_offset)

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
                        default_sky_color[i] * (1.0 - progress)
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
            status.strategic_map_grid.update_globe_projection(update_button=True)

    def get_water_vapor_contributions(self):
        """
        Description:
            Calculates the average water vapor for the planet, depending on local water and temperature
        Input:
            None
        Output:
            float: Average water vapor for the planet
        """
        total_water_vapor = 0
        for terrain_handler in self.terrain_handlers:
            if terrain_handler.get_parameter(constants.TEMPERATURE) >= self.get_tuning(
                "water_freezing_point"
            ):
                total_water_vapor += terrain_handler.get_parameter(constants.WATER)
            if terrain_handler.get_parameter(constants.TEMPERATURE) >= self.get_tuning(
                "water_boiling_point"
            ):  # Count boiling twice
                total_water_vapor += terrain_handler.get_parameter(constants.WATER)
        return total_water_vapor / self.default_grid.area

    def update_clouds(self):
        """
        Description:
            Creates random clouds for each terrain handler, with frequency depending on water vapor
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
        cloud_frequency = max(
            0,
            min(
                1,
                0.25
                * (
                    self.get_water_vapor_contributions()
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
        # Toxic cloud frequency depends on both toxic gas % and total pressure

        for terrain_handler in self.terrain_handlers:
            terrain_handler.current_clouds = []

            cloud_type = None
            if random.random() < cloud_frequency:
                cloud_type = "water vapor"
            elif (
                random.random() < toxic_cloud_quantity_frequency
                and random.random() < toxic_cloud_composition_frequency
            ):
                cloud_type = "toxic"
            if cloud_type:
                terrain_handler.current_clouds.append(
                    {
                        "image_id": "misc/shader.png",
                        "detail_level": constants.CLOUDS_DETAIL_LEVEL,
                    }
                )
            alpha = min(255, (self.get_pressure_ratio() * 7) - 14)
            if alpha > 0:
                terrain_handler.current_clouds.append(
                    {
                        "image_id": f"terrains/clouds_solid_{random.randrange(0, num_solid_cloud_variants)}.png",
                        "alpha": alpha,
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
                terrain_handler.current_clouds.append(
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
                terrain_handler.current_clouds.append(
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
            status.strategic_map_grid.update_globe_projection(update_button=True)

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
            "rotation_direction": self.rotation_direction,
            "rotation_speed": self.rotation_speed,
            "name": self.name,
            "sky_color": self.sky_color,
            "default_sky_color": self.default_sky_color,
            "initial_atmosphere_offset": self.initial_atmosphere_offset,
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
            "clouds": {
                "base_colors": [(174, 37, 19)],
                "tolerance": 60,
                "replacement_color": (0, 0, 0),
                # Replacement color updated when sky color changes
            },
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
                self.default_grid.area * 6 * self.get_tuning(f"earth_{parameter_name}"),
                2,
            )
        elif parameter_name == constants.RADIATION:
            return 0.0
        elif parameter_name == constants.PRESSURE:
            if self.default_grid.area == 1:
                return self.earth_size * 6 * self.get_tuning("earth_pressure")
            else:
                return self.default_grid.area * 6 * self.get_tuning("earth_pressure")
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

    def calculate_parameter_habitability(self, parameter_name: str) -> int:
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
        if parameter_name == constants.PRESSURE:
            ratio = round(value / ideal, 2)
            if ratio >= 30:
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
            elif ratio >= 0.12:
                return constants.HABITABILITY_DANGEROUS
            else:
                return constants.HABITABILITY_DEADLY
        elif parameter_name == constants.OXYGEN:
            if self.get_parameter(constants.PRESSURE) == 0:
                return constants.HABITABILITY_PERFECT
            composition = round(value / self.get_parameter(constants.PRESSURE), 2)
            if composition >= 0.6:
                return constants.HABITABILITY_HOSTILE
            elif composition >= 0.24:
                return constants.HABITABILITY_UNPLEASANT
            elif composition >= 0.22:
                return constants.HABITABILITY_TOLERABLE
            elif composition >= 0.2:
                return constants.HABITABILITY_PERFECT
            elif composition >= 0.19:
                return constants.HABITABILITY_TOLERABLE
            elif composition >= 0.17:
                return constants.HABITABILITY_UNPLEASANT
            elif composition >= 0.14:
                return constants.HABITABILITY_HOSTILE
            elif composition >= 0.1:
                return constants.HABITABILITY_DANGEROUS
            else:
                return constants.HABITABILITY_DEADLY
        elif parameter_name == constants.GHG:
            if self.get_parameter(constants.PRESSURE) == 0:
                return constants.HABITABILITY_PERFECT
            composition = round(value / self.get_parameter(constants.PRESSURE), 3)
            if composition >= 0.03:
                return constants.HABITABILITY_DEADLY
            elif composition >= 0.02:
                return constants.HABITABILITY_DANGEROUS
            elif composition >= 0.015:
                return constants.HABITABILITY_HOSTILE
            elif composition >= 0.01:
                return constants.HABITABILITY_UNPLEASANT
            elif composition >= 0.006:
                return constants.HABITABILITY_TOLERABLE
            else:
                return constants.HABITABILITY_PERFECT

        elif parameter_name == constants.INERT_GASES:
            if self.get_parameter(constants.PRESSURE) == 0:
                return constants.HABITABILITY_PERFECT
            composition = round(value / self.get_parameter(constants.PRESSURE), 2)
            if composition >= 0.80:
                return constants.HABITABILITY_TOLERABLE
            elif composition >= 0.76:
                return constants.HABITABILITY_PERFECT
            elif composition >= 0.5:
                return constants.HABITABILITY_TOLERABLE
            else:
                return constants.HABITABILITY_UNPLEASANT

        elif parameter_name == constants.TOXIC_GASES:
            if self.get_parameter(constants.PRESSURE) == 0:
                return constants.HABITABILITY_PERFECT
            composition = round(value / self.get_parameter(constants.PRESSURE), 4)
            if composition >= 0.004:
                return constants.HABITABILITY_DEADLY
            elif composition >= 0.003:
                return constants.HABITABILITY_DANGEROUS
            elif composition >= 0.002:
                return constants.HABITABILITY_HOSTILE
            elif composition >= 0.001:
                return constants.HABITABILITY_UNPLEASANT
            elif composition > 0:
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
            elif ratio >= 1.41:
                return constants.HABITABILITY_UNPLEASANT
            elif ratio >= 1.21:
                return constants.HABITABILITY_TOLERABLE
            elif ratio >= 0.8:
                return constants.HABITABILITY_PERFECT
            elif ratio >= 0.6:
                return constants.HABITABILITY_TOLERABLE
            elif ratio >= 0.3:
                return constants.HABITABILITY_UNPLEASANT
            else:
                return constants.HABITABILITY_HOSTILE

        elif parameter_name == constants.RADIATION:
            radiation_effect = value - self.get_parameter(constants.MAGNETIC_FIELD)
            if radiation_effect >= 4:
                return constants.HABITABILITY_DEADLY
            elif radiation_effect >= 2:
                return constants.HABITABILITY_DANGEROUS
            elif radiation_effect >= 1:
                return constants.HABITABILITY_HOSTILE
            else:
                return constants.HABITABILITY_PERFECT
        elif parameter_name == constants.MAGNETIC_FIELD:
            return constants.HABITABILITY_PERFECT

    def update_average_temperature(self):
        """
        Description:
            Re-calculates the average temperature of this world
        Input:
            None
        Output:
            None
        """
        self.average_temperature = round(
            sum(
                [
                    terrain_handler.get_parameter(constants.TEMPERATURE)
                    for terrain_handler in self.terrain_handlers
                ]
            )
            / self.default_grid.area,
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
                    terrain_handler.get_parameter(constants.WATER)
                    for terrain_handler in self.terrain_handlers
                ]
            )
            / self.default_grid.area,
            3,
        )
