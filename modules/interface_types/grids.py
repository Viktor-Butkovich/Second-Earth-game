# Contains functionality for grids

import random
import pygame
import itertools
from typing import Dict, List, Tuple
from . import cells, interface_elements
from ..util import actor_utility, utility
from ..tools.data_managers import terrain_manager_template
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags


class grid(interface_elements.interface_element):
    """
    Grid of cells of the same size with different positions based on the grid's size and the number of cells. Each cell contains various actors, terrain, and resources
    """

    def __init__(self, from_save: bool, input_dict: Dict[str, any]) -> None:
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of the bottom left corner of this grid
                'width': int value - Pixel width of this grid
                'height': int value - Pixel height of this grid
                'coordinate_width': int value - Number of columns in this grid
                'coordinate_height': int value - Number of rows in this grid
                'internal_line_color': string value - Color in the color_dict dictionary for lines between cells, like 'bright blue'
                'external_line_color': string value - Color in the color_dict dictionary for lines on the outside of the grid, like 'bright blue'
                'list modes': string list value - Game modes during which this grid can appear
                'grid_line_width': int value - Pixel width of lines between cells. Lines on the outside of the grid are one pixel thicker
                'cell_list': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each cell in this grid
                'grid_type': str value - Type of grid, like 'strategic_map_grid' or 'earth_grid'
        Output:
            None
        """
        super().__init__(input_dict)
        status.grid_list.append(self)
        self.world_handler = None
        self.grid_type = input_dict["grid_type"]
        self.grid_line_width: int = input_dict.get("grid_line_width", 3)
        self.from_save = from_save
        self.is_mini_grid = False
        self.is_abstract_grid = False
        self.attached_grid = None
        self.coordinate_width: int = input_dict.get(
            "coordinate_size", input_dict.get("coordinate_width")
        )
        self.coordinate_height: int = input_dict.get(
            "coordinate_size", input_dict.get("coordinate_height")
        )
        self.area: int = self.coordinate_width * self.coordinate_height
        self.internal_line_color = input_dict.get("internal_line_color", "black")
        self.external_line_color = input_dict.get("external_line_color", "dark gray")
        self.mini_grids = []
        self.cell_list = [
            [None] * self.coordinate_height for y in range(self.coordinate_width)
        ]
        # printed list would be inverted - each row corresponds to an x value and each column corresponds to a y value, but can be indexed by cell_list[x][y]
        if (
            not from_save
        ):  # terrain created after grid initialization by create_strategic_map in game_transitions
            self.create_cells()
        else:
            self.load_cells(input_dict["cell_list"])

    def load_cells(self, cell_list):
        """
        Description:
            Creates this grid's cells with correct resources and terrain based on the inputted saved information
        Input:
            dictionary list cell_list: list of dictionaries of saved information necessary to recreate each cell in this grid
        Output:
            None
        """
        for current_cell_dict in cell_list:
            x, y = current_cell_dict["coordinates"]
            self.create_cell(x, y, save_dict=current_cell_dict)
        for current_cell in self.get_flat_cell_list():
            current_cell.find_adjacent_cells()

    def get_tuning(self, tuning_type: str) -> any:
        """
        Description:
            Returns the tuning value for the inputted tuning type
        Input:
            string tuning_type: Tuning type to return the value of
        Output:
            any: Returns the tuning value
        """
        return constants.terrain_manager.get_tuning(tuning_type)

    def draw_latitude_line(
        self,
        latitude_line,
        max_latitude_line_length: int,
        longitude_bulge_factor: float = 0.0,
        level: int = 0,
        min_width: bool = False,
    ):
        return_list = []
        center_position = 0.2
        total_height = 0.5
        x_marker_size = 0.1
        x_offset_position = 0.2
        tile_width = 0.03
        tile_height = 1.5
        drew_x = True

        # Force latitude lines to be of the same length as the largest line
        latitude_line = latitude_line.copy()  # Don't modify original
        while len(latitude_line) > max_latitude_line_length:
            latitude_line.pop(len(latitude_line) // 4)
            if len(latitude_line) > max_latitude_line_length:
                latitude_line.pop(3 * len(latitude_line) // 4)
        while len(latitude_line) < max_latitude_line_length:
            latitude_line.insert(
                len(latitude_line) // 4, latitude_line[len(latitude_line) // 4]
            )
            if len(latitude_line) < max_latitude_line_length:
                latitude_line.insert(
                    3 * len(latitude_line) // 4,
                    latitude_line[3 * len(latitude_line) // 4],
                )

        y_step_size = 1.4 * total_height / max_latitude_line_length
        y_step_size *= (max_latitude_line_length**0.5) / (
            constants.map_size_options[4] ** 0.5
        )

        for idx, coordinates in enumerate(latitude_line):
            pole_distance_factor = 1.0 - abs(
                (idx - len(latitude_line) // 2) / (len(latitude_line) // 2)
            )
            """
            The ellipse equation (x - h)^2 / a + (y - k)^2 / b = r^2 give an ellipse
                With parameters r = 0.5, h = 0.5, k = 0, a = 1, and b = bulge_effect, we can get a stretched ellipse with a configurable bulge effect
            # Solving (x - h)^2 / a + (y - k)^2 / b = r^2 for y
            # (y - k)^2 / b = r^2 - (x - h)^2 / a
            # (y - k)^2 = b * (r^2 - (x - h)^2 / a)
            # y - k = ±sqrt(b * (r^2 - (x - h)^2 / a))
            # y = k ± sqrt(b * (r^2 - (x - h)^2 / a))
            y = k + (b * (r**2 - ((x - h)**2) / a))**0.5
            """
            r = 0.5
            h = 0.5
            k = 0
            a = 1
            x = idx / (len(latitude_line) - 1)
            b = abs(longitude_bulge_factor**3) * 5
            ellipse_weight = 0.3
            linear_weight = 0.18
            if abs(longitude_bulge_factor) > 0.5:
                linear_weight *= 2.0  # Linearly bulge outwards more farther from center
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
            y_multiplier = 1.0
            steps_from_center = abs(idx - len(latitude_line) // 2)
            y_offset_position = center_position
            for i in range(steps_from_center):
                change = y_step_size * (0.85**i)
                if idx < len(latitude_line) // 2:
                    y_offset_position += change
                else:
                    y_offset_position -= change
            current_cell = self.find_cell(coordinates[0], coordinates[1])
            image_id = current_cell.tile.get_image_id_list()[0]
            if type(image_id) == str:
                image_id = {
                    "image_id": image_id,
                }

            x_penalty = 0.015 * (abs(longitude_bulge_factor))
            y_penalty = (
                0.10 * (1.0 - abs(pole_distance_factor)) ** 2
            )  # Possible square these factors
            tile_width, tile_height = (
                0.10 - x_penalty,
                0.12 - y_penalty,
            )
            tile_width *= 0.8
            if (
                min_width
            ) and pole_distance_factor > 0.1:  # Since rightmost (highest level) latitude line is not covered by any others, it should be thinner to avoid an obvious size difference
                tile_width = 0.015
            tile_height = 0.08  # 2.5 * total_height / len(latitude_line)
            tile_height -= y_penalty
            if tile_height < 0.02:
                tile_height = 0.02
            image_id.update(
                {
                    "x_offset": x_offset_position + (latitude_bulge_factor / 4.0),
                    "y_offset": y_offset_position,  # 0.2 - (0.3 * idx / len(latitude_line)),
                    "x_size": tile_width,  # .805 / self.coordinate_width,
                    "y_size": tile_height,  # * y_multiplier * total_height / len(latitude_line), # .805 / self.coordinate_height,
                    "level": level,
                }
            )
            image_id[
                "y_size"
            ] *= y_multiplier  # Squishing effect to be more sphere-like

            return_list.append(image_id)
            continue
            if (
                coordinates
                == (
                    status.scrolling_strategic_map_grid.center_x,
                    status.scrolling_strategic_map_grid.center_y,
                )
                and not drew_x
            ):
                return_list.append(
                    {
                        "image_id": "misc/x.png",
                        "x_offset": x_offset_position
                        + (index_multiplier * bulge_factor),
                        "y_offset": y_offset_position,  # 0.2 - (0.3 * idx / len(latitude_line)),
                        "x_size": x_marker_size,  # .805 / self.coordinate_width,
                        "y_size": x_marker_size,  # .805 / self.coordinate_height,
                        "level": level + 1,
                    }
                )
                drew_x = True

            adjacent_cell_info = []
            for offset in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
                adjacent_coordinates = (
                    (coordinates[0] + offset[0]) % self.coordinate_width,
                    (coordinates[1] + offset[1]) % self.coordinate_height,
                )
                adjacent_cell = self.find_cell(
                    adjacent_coordinates[0], adjacent_coordinates[1]
                )
                (
                    adjacent_latitude_index,
                    adjacent_latitude_line,
                ) = self.world_handler.get_latitude_line(adjacent_coordinates)
                adjacent_cell_info.append(
                    (
                        adjacent_coordinates,
                        adjacent_cell,
                        adjacent_latitude_index,
                        offset,
                    )
                )

            north_cell = None
            lowest_north_pole_distance = float("inf")
            south_cell = None
            highest_north_pole_distance = 0
            for _, adjacent_cell, _, _ in adjacent_cell_info:
                if (
                    adjacent_cell.terrain_handler.north_pole_distance_multiplier
                    < lowest_north_pole_distance
                ):
                    lowest_north_pole_distance = (
                        adjacent_cell.terrain_handler.north_pole_distance_multiplier
                    )
                    north_cell = adjacent_cell
                if (
                    adjacent_cell.terrain_handler.north_pole_distance_multiplier
                    > highest_north_pole_distance
                ):
                    highest_north_pole_distance = (
                        adjacent_cell.terrain_handler.north_pole_distance_multiplier
                    )
                    south_cell = adjacent_cell
            east_west_candidates = [
                info
                for info in adjacent_cell_info
                if info[1] != north_cell and info[1] != south_cell
            ]
            if east_west_candidates[0][2] > east_west_candidates[1][2] or (
                east_west_candidates[0][2] == 0
            ):
                # East if higher latitude, or if wrapped around to 0 longitude
                east_cell = east_west_candidates[0][1]
                west_cell = east_west_candidates[1][1]
            else:
                east_cell = east_west_candidates[1][1]
                west_cell = east_west_candidates[0][1]
            if idx == 0:  # If north pole
                north_cell = None
            elif idx == len(latitude_line) - 1:  # If south pole
                south_cell = None
            for adjacent_cell_info in [
                (north_cell, (0, 1)),
                (east_cell, (1, 0)),
                (south_cell, (0, -1)),
                (west_cell, (-1, 0)),
            ]:
                adjacent_cell = adjacent_cell_info[0]
                adjacent_coordinates = (
                    coordinates[0] + adjacent_cell_info[1][0],
                    coordinates[1] + adjacent_cell_info[1][1],
                )
                if adjacent_cell:
                    if constants.current_map_mode == "terrain":
                        image_id = adjacent_cell.tile.get_image_id_list()[0]
                    else:
                        image_id = adjacent_cell.tile.get_image_id_list()[-1]
                    if type(image_id) == str:
                        image_id = {
                            "image_id": image_id,
                        }
                    image_id.update(
                        {
                            "x_offset": x_offset_position + x_bulge_effect,
                            "y_offset": y_offset_position,  # 0.2 - (0.3 * idx / len(latitude_line)),
                            "x_size": tile_width,  # .805 / self.coordinate_width,
                            "y_size": tile_height
                            * y_multiplier
                            * total_height
                            / len(latitude_line),  # .805 / self.coordinate_height,
                            "level": level - 1,
                        }
                    )
                    if adjacent_cell == east_cell:
                        image_id["x_offset"] += image_id["x_size"] * 0.5  # 0.1
                    elif adjacent_cell == west_cell:
                        image_id["x_offset"] -= image_id["x_size"] * 0.5  # 0.1
                    if adjacent_cell == north_cell:
                        image_id["y_offset"] += image_id["y_size"] * 0.5  # 0.1
                    elif adjacent_cell == south_cell:
                        image_id["y_offset"] -= image_id["y_offset"] * 0.5  # 0.1
                    # image_id["y_offset"] += adjacent_cell_info[1][1] * 0.05

                    image_id[
                        "y_size"
                    ] *= y_multiplier  # Squishing effect to be more spherical

                    return_list.append(image_id)

                if (
                    adjacent_coordinates
                    == (
                        status.scrolling_strategic_map_grid.center_x,
                        status.scrolling_strategic_map_grid.center_y,
                    )
                    and (not drew_x)
                    and (not adjacent_coordinates in latitude_line)
                ):
                    return_list.append(
                        {
                            "image_id": "misc/x.png",
                            # "x_offset": x_offset_position + (index_multiplier * bulge_factor),
                            "y_offset": y_offset_position,  # 0.2 - (0.3 * idx / len(latitude_line)),
                            "x_size": x_marker_size,  # .805 / self.coordinate_width,
                            "y_size": x_marker_size,  # .805 / self.coordinate_height,
                            "level": level + 1,
                        }
                    )
                    drew_x = True

        return return_list

    def create_planet_image(self):
        centered_coordinates = (
            status.scrolling_strategic_map_grid.center_x,
            status.scrolling_strategic_map_grid.center_y,
        )
        index, latitude_lines = self.world_handler.get_latitude_line(
            centered_coordinates
        )
        return_list = []

        planet_width = len(latitude_lines)
        offset_width = round(planet_width / 2)
        largest_size = len(
            max(
                self.world_handler.latitude_lines
                + self.world_handler.alternate_latitude_lines,
                key=len,
            )
        )
        for offset in range(offset_width):
            if offset == 0:
                current_line = latitude_lines[index]
                return_list += self.draw_latitude_line(
                    current_line, largest_size, level=0
                )
            else:
                longitude_bulge_factor = (
                    offset / offset_width
                ) ** 0.5  # (offset / offset_width) ** 3
                # if longitude_bulge_factor < 0.5:
                #     longitude_bulge_factor /= 2
                level = offset_width * 2 - offset
                level = offset
                right_line = latitude_lines[(index + offset) % planet_width]
                if offset >= offset_width - 1:
                    return_list += self.draw_latitude_line(
                        right_line,
                        largest_size,
                        longitude_bulge_factor=longitude_bulge_factor,
                        level=level,
                        min_width=True,
                    )  # 0.03 * offset
                else:
                    return_list += self.draw_latitude_line(
                        right_line,
                        largest_size,
                        longitude_bulge_factor=longitude_bulge_factor,
                        level=level,
                    )
                level *= -1
                left_line = latitude_lines[(index - offset) % planet_width]
                if offset >= offset_width - 1:
                    return_list += self.draw_latitude_line(
                        left_line,
                        largest_size,
                        longitude_bulge_factor=-1 * longitude_bulge_factor,
                        level=level,
                        min_width=True,
                    )
                else:
                    return_list += self.draw_latitude_line(
                        left_line,
                        largest_size,
                        longitude_bulge_factor=-1 * longitude_bulge_factor,
                        level=level,
                    )

        # central_line = latitude_lines[index]
        # return_list += self.draw_latitude_line(central_line)

        # right_line = latitude_lines[(index + 1) % len(latitude_lines)]
        # return_list += self.draw_latitude_line(right_line, bulge_factor=0.1)

        # left_line = latitude_lines[(index - 1) % len(latitude_lines)]
        # return_list += self.draw_latitude_line(left_line, bulge_factor=-0.1)
        # Decent approximation of middle strip of planet - now repeat on adjacent latitude lines, with bulging effect to sides based on latitude index difference
        # Keep the total height constant, regardless of the number of cells in the latitude line
        return return_list

    def create_map_image(self):
        """
        Description:
            Creates and returns a map image of this grid
        Input:
            None
        Output:
            List: List of images representing this grid - approximation of very zoomed out grid
        """
        return_list = []
        for current_cell in self.get_flat_cell_list():
            if constants.current_map_mode == "terrain":
                image_id = current_cell.tile.get_image_id_list()[0]
            else:
                image_id = current_cell.tile.get_image_id_list()[-1]
            if type(image_id) == str:
                image_id = {
                    "image_id": image_id,
                }
            origin = (
                status.scrolling_strategic_map_grid.center_x
                - self.coordinate_width // 2,
                status.scrolling_strategic_map_grid.center_y
                - self.coordinate_height // 2,
            )
            effective_x = (
                current_cell.x - origin[0]
            ) % status.scrolling_strategic_map_grid.coordinate_width
            effective_y = (
                current_cell.y - origin[1]
            ) % status.scrolling_strategic_map_grid.coordinate_height
            image_id.update(
                {
                    "x_offset": effective_x / self.coordinate_width
                    - 0.5
                    + (0.7 / self.coordinate_width),
                    "y_offset": effective_y / self.coordinate_height
                    - 0.5
                    + (0.4 / self.coordinate_height),
                    "x_size": 1.05 / self.coordinate_width,
                    "y_size": 1.05 / self.coordinate_height,
                }
            )
            return_list.append(image_id)
        return return_list

    def to_save_dict(self):
        """
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                'grid_type': string value - String matching the status key of this grid, used to initialize the correct type of grid on loading
                'cell_list': dictionary list value - list of dictionaries of saved information necessary to recreate each cell in this grid
        """
        return {
            "grid_type": self.grid_type,
            "map_size": self.coordinate_width,
            "world_handler": self.world_handler.to_save_dict(),
            "cell_list": [
                current_cell.to_save_dict()
                for current_cell in self.get_flat_cell_list()
            ],
        }

    def draw(self):
        """
        Description:
            Draws each cell of this grid
        Input:
            None
        Output:
            None
        """
        for cell in self.get_flat_cell_list():
            cell.draw()
        self.draw_grid_lines()

    def draw_grid_lines(self):
        """
        Description:
            Draws lines between grid cells and on the outside of the grid. Also draws an outline of the area on this grid covered by this grid's minimap grid, if applicable
        Input:
            None
        Output:
            None
        """
        if flags.show_grid_lines:
            for x in range(0, self.coordinate_width + 1):
                pygame.draw.line(
                    constants.game_display,
                    constants.color_dict[self.internal_line_color],
                    self.convert_coordinates((x, 0)),
                    self.convert_coordinates((x, self.coordinate_height)),
                    self.grid_line_width,
                )
            for y in range(0, self.coordinate_height + 1):
                pygame.draw.line(
                    constants.game_display,
                    constants.color_dict[self.internal_line_color],
                    self.convert_coordinates((0, y)),
                    self.convert_coordinates((self.coordinate_width, y)),
                    self.grid_line_width,
                )
        pygame.draw.line(
            constants.game_display,
            constants.color_dict[self.external_line_color],
            self.convert_coordinates((0, 0)),
            self.convert_coordinates((0, self.coordinate_height)),
            self.grid_line_width + 1,
        )
        pygame.draw.line(
            constants.game_display,
            constants.color_dict[self.external_line_color],
            self.convert_coordinates((self.coordinate_width, 0)),
            self.convert_coordinates((self.coordinate_width, self.coordinate_height)),
            self.grid_line_width + 1,
        )
        pygame.draw.line(
            constants.game_display,
            constants.color_dict[self.external_line_color],
            self.convert_coordinates((0, 0)),
            self.convert_coordinates((self.coordinate_width, 0)),
            self.grid_line_width + 1,
        )
        pygame.draw.line(
            constants.game_display,
            constants.color_dict[self.external_line_color],
            self.convert_coordinates((0, self.coordinate_height)),
            self.convert_coordinates((self.coordinate_width, self.coordinate_height)),
            self.grid_line_width + 1,
        )
        if (
            self.mini_grids or self == status.scrolling_strategic_map_grid
        ) and flags.show_minimap_outlines:
            mini_map_outline_color = status.minimap_grid.external_line_color
            if self == status.scrolling_strategic_map_grid:
                left_x = (
                    self.coordinate_width // 2
                    - status.minimap_grid.coordinate_width // 2
                )
                right_x = (
                    self.coordinate_width // 2
                    + status.minimap_grid.coordinate_width // 2
                    + 1
                )
                down_y = (
                    self.coordinate_height // 2
                    - status.minimap_grid.coordinate_height // 2
                )
                up_y = (
                    self.coordinate_height // 2
                    + status.minimap_grid.coordinate_height // 2
                    + 1
                )
            else:
                left_x = status.minimap_grid.center_x - (
                    (status.minimap_grid.coordinate_width - 1) / 2
                )
                right_x = (
                    status.minimap_grid.center_x
                    + ((status.minimap_grid.coordinate_width - 1) / 2)
                    + 1
                )
                down_y = status.minimap_grid.center_y - (
                    (status.minimap_grid.coordinate_height - 1) / 2
                )
                up_y = (
                    status.minimap_grid.center_y
                    + ((status.minimap_grid.coordinate_height - 1) / 2)
                    + 1
                )
                if right_x > self.coordinate_width:
                    right_x = self.coordinate_width
                if left_x < 0:
                    left_x = 0
                if up_y > self.coordinate_height:
                    up_y = self.coordinate_height
                if down_y < 0:
                    down_y = 0
            pygame.draw.line(
                constants.game_display,
                constants.color_dict[mini_map_outline_color],
                self.convert_coordinates((left_x, down_y)),
                self.convert_coordinates((left_x, up_y)),
                self.grid_line_width + 1,
            )
            pygame.draw.line(
                constants.game_display,
                constants.color_dict[mini_map_outline_color],
                self.convert_coordinates((left_x, up_y)),
                self.convert_coordinates((right_x, up_y)),
                self.grid_line_width + 1,
            )
            pygame.draw.line(
                constants.game_display,
                constants.color_dict[mini_map_outline_color],
                self.convert_coordinates((right_x, up_y)),
                self.convert_coordinates((right_x, down_y)),
                self.grid_line_width + 1,
            )
            pygame.draw.line(
                constants.game_display,
                constants.color_dict[mini_map_outline_color],
                self.convert_coordinates((right_x, down_y)),
                self.convert_coordinates((left_x, down_y)),
                self.grid_line_width + 1,
            )

    def find_cell_center(self, coordinates) -> Tuple[int, int]:
        """
        Description:
            Returns the pixel coordinates of the center of this grid's cell that occupies the inputted grid coordinates
        Input:
            int tuple coordinates: Two values representing x and y grid coordinates of the cell whose center is found
        Output:
            int tuple: Two values representing x and y pixel coordinates of the center of the requested cell
        """
        x, y = coordinates
        return (
            (
                int((self.width / (self.coordinate_width)) * x)
                + self.x
                + int(self.get_cell_width() / 2)
            ),
            (
                constants.display_height
                - (
                    int((self.height / (self.coordinate_height)) * y)
                    + self.y
                    + int(self.get_cell_height() / 2)
                )
            ),
        )

    def convert_coordinates(self, coordinates):
        """
        Description:
            Returns the pixel coordinates of the bottom left corner of this grid's cell that occupies the inputted grid coordinates
        Input:
            int tuple coordinates: Two values representing x and y grid coordinates of the cell whose corner is found
        Output:
            int tuple: Two values representing x and y pixel coordinates of the bottom left corner of the requested cell
        """
        x, y = coordinates
        return (
            (int((self.width / (self.coordinate_width)) * x) + self.x),
            (
                constants.display_height
                - (int((self.height / (self.coordinate_height)) * y) + self.y)
            ),
        )

    def get_height(self):
        """
        Description:
            Returns how many rows this grid has
        Input:
            None
        Output:
            int: Number of rows this grid has
        """
        return self.coordinate_height

    def get_width(self):
        """
        Description:
            Returns how many columns this grid has
        Input:
            None
        Output:
            int: Number of columns this grid has
        """
        return self.coordinate_width

    def get_cell_width(self):
        """
        Description:
            Returns the pixel width of one of this grid's cells
        Input:
            None
        Output:
            int: Pixel width of one of this grid's cells
        """
        return int(self.width / self.coordinate_width) + 1

    def get_cell_height(self):
        """
        Description:
            Returns the pixel height of one of this grid's cells
        Input:
            None
        Output:
            int: Pixel height of one of this grid's cells
        """
        return int(self.height / self.coordinate_height) + 1

    def find_cell(self, x, y) -> cells.cell:
        """
        Description:
            Returns this grid's cell that occupies the inputted coordinates
        Input:
            int x: x coordinate for the grid location of the requested cell
            int y: y coordinate for the grid location of the requested cell
        Output:
            None/cell: Returns this grid's cell that occupies the inputted coordinates, or None if there are no cells at the inputted coordinates
        """
        if (
            x >= 0
            and x < self.coordinate_width
            and y >= 0
            and y < self.coordinate_height
        ):
            return self.cell_list[x][y]
        else:
            return None

    def choose_cell(self, requirements_dict):
        """
        Description:
            Uses a series of requirements to choose and a return a random cell in this grid that fits those requirements
        Input:
            dictionary choice_info_dict: String keys corresponding to various values such as 'allowed_terrains' to use as requirements for the chosen cell
        Output:
            cell: Returns a random cell in this grid that fits the inputted requirements
        """
        allowed_terrains = requirements_dict["allowed_terrains"]
        possible_cells = []
        for current_cell in self.get_flat_cell_list():
            if not current_cell.terrain_handler.terrain in allowed_terrains:
                continue
            possible_cells.append(current_cell)
        if len(possible_cells) == 0:
            possible_cells.append(None)
        return random.choice(possible_cells)

    def create_cells(self):
        """
        Description:
            Creates a cell for each of this grid's coordinates
        Input:
            None
        Output:
            None
        """
        for x in range(len(self.cell_list)):
            for y in range(len(self.cell_list[x])):
                self.create_cell(x, y)
        for current_cell in self.get_flat_cell_list():
            current_cell.find_adjacent_cells()

    def get_flat_cell_list(self) -> List[cells.cell]:
        """
        Description:
            Generates and returns a flattened version of this grid's 2-dimensional cell list
        Input:
            None
        Output:
            cell list: Returns a flattened version of this grid's 2-dimensional cell list
        """
        return itertools.chain.from_iterable(self.cell_list)

    def create_cell(self, x, y, save_dict=None) -> cells.cell:
        """
        Description:
            Creates a cell at the inputted coordinates
        Input:
            int x: x coordinate at which to create a cell
            int y: y coordinate at which to create a cell
        Output:
            cell: Returns created cell
        """
        return cells.cell(
            x,
            y,
            self.get_cell_width(),
            self.get_cell_height(),
            self,
            constants.color_dict["bright green"],
            save_dict,
        )

    def touching_mouse(self):
        """
        Description:
            Returns whether this grid is colliding with the mouse
        Input:
            None
        Output:
            boolean: Returns True if this grid is colliding with the mouse, otherwise returns False
        """
        if self.Rect.collidepoint(pygame.mouse.get_pos()):
            return True
        else:
            return False

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this grid can be shown. By default, it can be shown during game modes in which this grid can appear
        Input:
            None
        Output:
            boolean: Returns True if this grid can appear during the current game mode, otherwise returns False
        """
        return constants.current_game_mode in self.modes

    def can_draw(self):
        """
        Description:
            Calculates and returns whether it would be valid to call this object's draw()
        Input:
            None
        Output:
            boolean: Returns whether it would be valid to call this object's draw()
        """
        return self.showing

    def remove(self):
        """
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        Input:
            None
        Output:
            None
        """
        super().remove()
        status.grid_list = utility.remove_from_list(status.grid_list, self)


class mini_grid(grid):
    """
    Grid that zooms in on a small area of a larger attached grid, centered on a certain cell of the attached grid. Which cell is being centered on can be changed
    """

    def __init__(self, from_save: bool, input_dict: Dict[str, any]) -> None:
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of the bottom left corner of this grid
                'width': int value - Pixel width of this grid
                'height': int value - Pixel height of this grid
                'coordinate_width': int value - Number of columns in this grid
                'coordinate_height': int value - Number of rows in this grid
                'internal_line_color': string value - Color in the color_dict dictionary for lines between cells, like 'bright blue'
                'external_line_color': string value - Color in the color_dict dictionary for lines on the outside of the grid, like 'bright blue'
                'list modes': string list value - Game modes during which this grid can appear
                'attached_grid': grid value - grid to which this grid is attached
                'grid_line_width': int value - Pixel width of lines between cells. Lines on the outside of the grid are one pixel thicker
                'cell_list': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each cell in this grid
        Output:
            None
        """
        super().__init__(from_save, input_dict)
        self.is_mini_grid = True
        self.attached_grid = input_dict["attached_grid"]
        self.attached_grid.mini_grids.append(self)
        self.center_x = 0
        self.center_y = 0

    def calibrate(self, center_x, center_y, recursive=False):
        """
        Description:
            Centers this mini grid on the cell at the inputted coordinates of the attached grid, moving any displayed actors, terrain, and resources on this grid to their new locations as needed
        Input:
            int center_x: x coordinate on the attached grid to center on
            int center_y: y coordinate on the attached grid to center on
            boolean recursive: Whether this is a recursive calibrate call - prevents infinite recursion
        Output:
            None
        """
        if constants.current_game_mode in self.modes:
            self.center_x = center_x
            self.center_y = center_y
            if not recursive:
                for mini_grid in self.attached_grid.mini_grids:
                    if mini_grid != self:
                        mini_grid.calibrate(center_x, center_y, recursive=True)
                actor_utility.calibrate_actor_info_display(
                    status.tile_info_display,
                    self.attached_grid.find_cell(self.center_x, self.center_y).tile,
                )  # calibrate tile display information to centered tile
            for current_cell in self.get_flat_cell_list():
                attached_x, attached_y = self.get_main_grid_coordinates(
                    current_cell.x, current_cell.y
                )
                attached_cell = self.attached_grid.find_cell(attached_x, attached_y)
                current_cell.copy(attached_cell)
            for current_mob in status.mob_list:
                if current_mob.get_cell():
                    for current_image in current_mob.images:
                        if current_image.grid == self:
                            current_image.add_to_cell()
            if self == status.minimap_grid:
                for (
                    directional_indicator_image
                ) in status.directional_indicator_image_list:
                    directional_indicator_image.calibrate()
        if self == status.scrolling_strategic_map_grid:
            status.table_map_image.set_image(
                status.strategic_map_grid.create_planet_image()
            )
            # print(status.table_map_image.image)
            # print(status.table_map_image.image.generate_combined_surface())

    def get_main_grid_coordinates(self, mini_x, mini_y):
        """
        Description:
            Converts the inputted coordinates on this grid to the corresponding coordinates on the attached grid, returning the converted coordinates
        Input:
            int mini_x: x coordinate on this grid
            int mini_y: y coordinate on this grid
        Output:
            int: x coordinate of the attached grid corresponding to the inputted x coordinate
            int: y coordinate of the attached grid corresponding to the inputted y coordinate
        """
        attached_x = (
            self.center_x + mini_x - round((self.coordinate_width - 1) / 2)
        )  # if width is 5, ((5 - 1) / 2) = (4 / 2) = 2, since 2 is the center of a 5 width grid starting at 0
        attached_y = self.center_y + mini_y - round((self.coordinate_height - 1) / 2)
        if attached_x < 0:
            attached_x += self.attached_grid.coordinate_width
        elif attached_x >= self.attached_grid.coordinate_width:
            attached_x -= self.attached_grid.coordinate_width
        if attached_y < 0:
            attached_y += self.attached_grid.coordinate_height
        elif attached_y >= self.attached_grid.coordinate_height:
            attached_y -= self.attached_grid.coordinate_height
        return (attached_x, attached_y)

    def get_mini_grid_coordinates(self, original_x, original_y):
        """
        Description:
            Converts the inputted coordinates on the attached grid to the corresponding coordinates on this grid, returning the converted coordinates
        Input:
            int mini_x: x coordinate on the attached grid
            int mini_y: y coordinate on the attached grid
        Output:
            int: x coordinate of this grid corresponding to the inputted x coordinate
            int: y coordinate of this grid corresponding to the inputted y coordinate
        """
        return (
            (
                int(original_x - self.center_x + (round(self.coordinate_width - 1) / 2))
                % status.strategic_map_grid.coordinate_width
            )
            % self.coordinate_width,
            (
                int(
                    original_y - self.center_y + round((self.coordinate_height - 1) / 2)
                )
                % status.strategic_map_grid.coordinate_height
            )
            % self.coordinate_height,
        )

    def is_on_mini_grid(self, original_x, original_y):
        """
        Description:
            Returns whether the inputted attached grid coordinates are within the boundaries of this grid
        Input:
            int original_x: x coordinate on the attached grid
            int original_y: y coordinate on the attached grid
        Output:
            boolean: Returns True if the inputted attache grid coordinates are within the boundaries of this grid, otherwise returns False
        """
        minimap_x = (
            original_x - self.center_x + (round(self.coordinate_width - 1) / 2)
        ) % self.attached_grid.coordinate_width
        minimap_y = (
            original_y - self.center_y + (round(self.coordinate_height - 1) / 2)
        ) % self.attached_grid.coordinate_height
        if (
            minimap_x >= 0
            and minimap_x < self.coordinate_width
            and minimap_y >= 0
            and minimap_y < self.coordinate_height
        ):
            return True
        else:
            return False

    def draw_grid_lines(self):
        """
        Description:
            Draws lines between grid cells and on the outside of the grid
        Input:
            None
        Output:
            None
        """
        if (
            self == status.scrolling_strategic_map_grid
        ):  # Scrolling map acts more like a default grid than normal minimap
            super().draw_grid_lines()
            if (
                constants.effect_manager.effect_active("allow_planet_mask")
                and flags.show_planet_mask
            ):
                status.planet_view_mask.draw()
            return

        left_x, down_y = (0, 0)
        right_x, up_y = (self.coordinate_width, self.coordinate_height)
        if flags.show_grid_lines:
            for x in range(0, self.coordinate_width + 1):
                pygame.draw.line(
                    constants.game_display,
                    constants.color_dict[self.internal_line_color],
                    self.convert_coordinates((x, 0)),
                    self.convert_coordinates((x, self.coordinate_height)),
                    self.grid_line_width,
                )

            for y in range(0, self.coordinate_height + 1):
                pygame.draw.line(
                    constants.game_display,
                    constants.color_dict[self.internal_line_color],
                    self.convert_coordinates((0, y)),
                    self.convert_coordinates((self.coordinate_width, y)),
                    self.grid_line_width,
                )

        for y in range(0, self.coordinate_height + 1):
            pygame.draw.line(
                constants.game_display,
                constants.color_dict[self.external_line_color],
                self.convert_coordinates((left_x, down_y)),
                self.convert_coordinates((left_x, up_y)),
                self.grid_line_width + 1,
            )

        pygame.draw.line(
            constants.game_display,
            constants.color_dict[self.external_line_color],
            self.convert_coordinates((left_x, up_y)),
            self.convert_coordinates((right_x, up_y)),
            self.grid_line_width + 1,
        )

        pygame.draw.line(
            constants.game_display,
            constants.color_dict[self.external_line_color],
            self.convert_coordinates((right_x, up_y)),
            self.convert_coordinates((right_x, down_y)),
            self.grid_line_width + 1,
        )

        pygame.draw.line(
            constants.game_display,
            constants.color_dict[self.external_line_color],
            self.convert_coordinates((right_x, down_y)),
            self.convert_coordinates((left_x, down_y)),
            self.grid_line_width + 1,
        )


class abstract_grid(grid):
    """
    1-cell grid that is not directly connected to the primary strategic grid but can be moved to by mobs from the strategic grid and vice versa
    """

    def __init__(self, from_save: bool, input_dict: Dict[str, any]) -> None:
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of the bottom left corner of this grid
                'width': int value - Pixel width of this grid
                'height': int value - Pixel height of this grid
                'internal_line_color': string value - Color in the color_dict dictionary for lines between cells, like 'bright blue'
                'external_line_color': string value - Color in the color_dict dictionary for lines on the outside of the grid, like 'bright blue'
                'list modes': string list value - Game modes during which this grid can appear
                'grid_line_width': int value - Pixel width of lines between cells. Lines on the outside of the grid are one pixel thicker
                'cell_list': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each cell in this grid
                'tile_image_id': File path to the image used by this grid's tile
                'name': Name of this grid
        Output:
            None
        """
        input_dict["coordinate_width"] = 1
        input_dict["coordinate_height"] = 1
        super().__init__(from_save, input_dict)
        self.is_abstract_grid = True
        self.world_handler = terrain_manager_template.world_handler(
            self,
            from_save,
            input_dict.get("world_handler", {"grid_type": input_dict["grid_type"]}),
        )
        self.name = input_dict["name"]
        self.cell_list[0][0].terrain_handler.set_visibility(True)
