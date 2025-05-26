import pygame
import math
from typing import List, Dict, Tuple
from modules.util import actor_utility
from modules.constructs import world_handlers
from modules.constants import constants, status, flags


class abstract_world_handler(world_handlers.world_handler):
    def __init__(self, from_save: bool, input_dict: Dict[str, any]) -> None:
        self.abstract_world_type = input_dict["abstract_world_type"]
        super().__init__(from_save, input_dict)

    @property
    def coordinate_width(self) -> int:
        return 1

    @property
    def coordinate_height(self) -> int:
        return 1

    def is_abstract_world(self) -> bool:
        return True

    def is_earth(self) -> bool:
        return self.abstract_world_type == constants.EARTH


class orbital_world_handler(abstract_world_handler):
    """
    World handler that has its own abstract grid and location but copies the attributes of the full world it orbits
    Allows planet orbit to have its own orbital location while using the full world's parameters
    """

    def __init__(self, from_save: bool, input_dict: Dict[str, any]) -> None:
        self.full_world: full_world_handler = input_dict["full_world"]
        input_dict["abstract_world_type"] = constants.ORBITAL_WORLD
        super().__init__(from_save, input_dict)

    @property
    def name(self) -> str:
        return self.full_world.name

    @name.setter
    def name(self, value: str) -> None:
        pass

    @property
    def world_dimensions(self) -> int:
        return self.full_world.world_dimensions

    @world_dimensions.setter
    def world_dimensions(self, value: int) -> None:
        pass

    @property
    def rotation_direction(self) -> int:
        return self.full_world.rotation_direction

    @rotation_direction.setter
    def rotation_direction(self, value: int) -> None:
        pass

    @property
    def rotation_speed(self) -> int:
        return self.full_world.rotation_speed

    @rotation_speed.setter
    def rotation_speed(self, value: int) -> None:
        pass

    @property
    def star_distance(self) -> float:
        return self.full_world.star_distance

    @star_distance.setter
    def star_distance(self, value: float) -> None:
        pass

    @property
    def global_parameters(self) -> Dict[str, any]:
        return self.full_world.global_parameters

    @global_parameters.setter
    def global_parameters(self, value: Dict[str, any]) -> None:
        pass

    @property
    def sky_color(self) -> Tuple[int, int, int]:
        return self.full_world.sky_color

    @sky_color.setter
    def sky_color(self, value: Tuple[int, int, int]) -> None:
        pass

    @property
    def default_sky_color(self) -> Tuple[int, int, int]:
        return self.full_world.default_sky_color

    @default_sky_color.setter
    def default_sky_color(self, value: Tuple[int, int, int]) -> None:
        pass


class full_world_handler(world_handlers.world_handler):
    def __init__(self, from_save: bool, input_dict: Dict[str, any]) -> None:
        super().__init__(from_save, input_dict)

        if not from_save:  # Initial full world generation
            self.generate_poles_and_equator()
            self.update_clouds(estimated_temperature=True)
            self.generate_terrain_parameters()
            self.generate_terrain_features()
            self.update_sky_color(set_initial_offset=True, update_water=True)
            self.update_clouds()
            for i in range(5):  # Simulate time passing until equilibrium is reached
                self.update_target_average_temperature(update_albedo=True)
                self.change_to_temperature_target()

        self.orbital_world: orbital_world_handler = (
            constants.actor_creation_manager.create(
                from_save,
                {
                    **input_dict.get("orbital_world", {}),
                    "init_type": constants.ORBITAL_WORLD,
                    "full_world": self,
                },
            )
        )

    def to_save_dict(self) -> Dict[str, any]:
        save_dict = super().to_save_dict()
        save_dict["orbital_world"] = self.orbital_world.to_save_dict()
        return save_dict

    def update_globe_projection(
        self, center_coordinates: Tuple[int, int] = None, update_button: bool = True
    ):
        """
        Description:
            Updates the globe projection to the current state of the world grid
        Input:
            int tuple center_coordinates: Coordinates to center the globe projection on - defaults to currently centered location
            bool update_button: True if the strategic mode button should also be updated
        Output:
            None
        """
        status.globe_projection_image.set_image(
            self.create_planet_image(center_coordinates)
        )
        status.globe_projection_surface = status.globe_projection_image.image
        size = status.globe_projection_surface.get_size()
        status.globe_projection_surface = pygame.transform.scale(  # Decrease detail of each image before applying pixel mutations to speed processing
            status.globe_projection_surface,
            (
                math.floor(size[0] * constants.GLOBE_PROJECTION_DETAIL_LEVEL),
                math.floor(size[1] * constants.GLOBE_PROJECTION_DETAIL_LEVEL),
            ),
        )

        globe_projection_tile = (
            status.current_world.orbital_world.find_location(0, 0)
            .attached_cells[0]
            .tile
        )
        globe_projection_image_id = [
            "misc/space.png",
            {
                "image_id": status.globe_projection_surface,
                "size": 0.8,
            },
        ]
        globe_projection_tile.image.set_image(globe_projection_image_id)
        globe_projection_tile.grid_image_id = globe_projection_image_id

        if update_button:
            status.to_strategic_button.image.set_image(
                actor_utility.generate_frame(
                    "misc/space.png",
                )
                + [
                    {
                        "image_id": status.globe_projection_surface,
                        "size": 0.6,
                    }
                ]
            )

    def create_planet_image(self, center_coordinates: Tuple[int, int] = None):
        """
        Description:
            Creates and returns a global projection of the planet on this grid, centered at the scrolling map grid's calibration point
        Input:
            None
        Output:
            list: Image ID list of each point of the global projection of the planet
        """
        if not center_coordinates:
            center_coordinates = (  # Required here since globe appearance is actually determined based on the state of the interface
                status.scrolling_strategic_map_grid.center_x,
                status.scrolling_strategic_map_grid.center_y,
            )
        index, latitude_lines = self.get_latitude_line(center_coordinates)

        offset_width = self.world_dimensions // 2
        largest_size = len(
            max(
                self.latitude_lines + self.alternate_latitude_lines,
                key=len,
            )
        )
        return_list = []
        for offset in range(offset_width):
            min_width = (
                offset >= offset_width - 1
            )  # If leftmost or rightmost latitude line, use minimum width to avoid edge tiles looking too wide
            if (
                offset == 0
            ):  # For center offset, just draw a straight vertical latitude line
                current_line = latitude_lines[index]
                return_list += self.draw_latitude_line(
                    current_line,
                    largest_size,
                    level=offset + 20,
                    offset=offset,
                    offset_width=offset_width,
                )
            else:  # For non-center offsets, draw symmetrical curved latitude lines, progressively farther from center
                longitude_bulge_factor = (offset / offset_width) ** 0.5

                return_list += self.draw_latitude_line(
                    latitude_lines[(index + offset) % self.world_dimensions],
                    largest_size,
                    longitude_bulge_factor=longitude_bulge_factor,
                    level=offset + 20,
                    min_width=min_width,
                    offset=offset,
                    offset_width=offset_width,
                )
                return_list += self.draw_latitude_line(
                    latitude_lines[(index - offset) % self.world_dimensions],
                    largest_size,
                    longitude_bulge_factor=-1 * longitude_bulge_factor,
                    level=(-1 * offset) + 20,
                    min_width=min_width,
                    offset=offset,
                    offset_width=offset_width,
                )
        return return_list

    def draw_latitude_line(
        self,
        latitude_line,
        max_latitude_line_length: int,
        longitude_bulge_factor: float = 0.0,
        level: int = 0,
        min_width: bool = False,
        offset: int = 0,
        offset_width: int = 0,
    ):
        """
        Description:
            Returns an image ID list for a latitude line of a global map projection, creating a curve between poles that bulges at the equator
        Input:
            tuple list latitude_line: List of coordinates for each point in the latitude line
            int max_latitude_line_length: Length of the longest latitude line - to minimize size warping, latitude lines are extended to all be the same size,
                duplicating coordinates or inserting nearby coordinates that are not in latitude lines
            float longitude_bulge_factor: Factor to determine how much the latitude line bulges outwards at the equator
                Lines at longitudes farther from the center of the projection bulge further outwards and are thinner
            int level: Image ID level of the latitude line - further right latitude lines have higher levels
            boolean min_width: Whether the latitude line should use the minimum width instead of the calculated one
                Latitude lines on the edge of the projection look more evenly sized if using the minimum width
        Output:
            list: List of image IDs for the points of the latitude line
        """
        return_list = []
        center_position = (0.0, 0.0)
        total_height = 0.5  # Multiplier for y offset step sizes between each latitude
        size_multiplier = [1.5, 1.7, 1.8, 2.0, 2.2, 2.4, 2.6, 2.65][
            constants.world_dimensions_options.index(max_latitude_line_length)
        ]
        base_tile_width = 0.10
        base_tile_height = 0.12

        # Force latitude lines to be of the same length as the largest line
        latitude_line = latitude_line.copy()  # Don't modify original
        while len(latitude_line) > max_latitude_line_length:
            latitude_line.pop(len(latitude_line) // 4)
            if len(latitude_line) > max_latitude_line_length:
                latitude_line.pop(3 * len(latitude_line) // 4)
        while len(latitude_line) < max_latitude_line_length:
            latitude_line.insert(
                *self.get_next_unaccounted_coordinates(
                    latitude_line, latitude_line[len(latitude_line) // 4]
                )
            )
            if len(latitude_line) < max_latitude_line_length:
                latitude_line.insert(
                    *self.get_next_unaccounted_coordinates(
                        latitude_line, latitude_line[3 * len(latitude_line) // 4]
                    )
                )

        y_step_size = (
            1.4 * total_height / max_latitude_line_length
        )  # Y step size between each coordinate of the latitude line
        y_step_size *= (max_latitude_line_length**0.5) / (
            constants.earth_dimensions**0.5
        )

        for idx, coordinates in enumerate(
            latitude_line
        ):  # Calculate position and size of each coordinate in the latitude line
            pole_distance_factor = 1.0 - abs(
                (idx - len(latitude_line) // 2) / (len(latitude_line) // 2)
            )
            """
            The ellipse equation (x - h)^2 / a + (y - k)^2 / b = r^2 give an ellipse
                With parameters r = 0.5, h = 0.5, k = 0, a = 1, and b = bulge_effect, we can get a stretched ellipse with a configurable bulge effect
            # Solving (x - h)^2 / a + (y - k)^2 / b = r^2 for y
            # (y - k)^2 / b = r^2 - (x - h)^2 / a
            # (y - k)^2 = b * (r^2 - (x - h)^2 / a)
            # y - k = sqrt(b * (r^2 - (x - h)^2 / a))
            # y = k + sqrt(b * (r^2 - (x - h)^2 / a))
            y = k + (b * (r**2 - ((x - h)**2) / a))**0.5
            """
            r = 0.5
            h = 0.5
            k = 0
            a = 1
            x = idx / (len(latitude_line) - 1)
            b = abs(longitude_bulge_factor**3) * 5
            ellipse_weight = 0.32  # Extent to which x position is determined by ellipse function based on longitude bulge factor
            linear_weight = 0.15  # Extent to which x position is determined by linear function based on distance from center index
            if abs(longitude_bulge_factor) > 0.5:
                linear_weight *= 2.5  # Have stronger linear effect for edge latitude lines to minimize blocky corners
            elif abs(longitude_bulge_factor) > 0.35:
                linear_weight *= 1.3
            if max_latitude_line_length >= constants.world_dimensions_options[-3]:
                ellipse_weight *= 1 / 3
                linear_weight *= 1.5
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

            x_offset = latitude_bulge_factor / 4.0
            y_offset = 0
            for i in range(
                abs(idx - len(latitude_line) // 2)
            ):  # Move up or down for each index away from center
                change = y_step_size * (
                    0.85**i
                )  # Since each latitude is shorter than the last, the step size should also decrease
                if idx < len(latitude_line) // 2:
                    y_offset += change
                else:
                    y_offset -= change

            width_penalty = 0.015 * (
                abs(longitude_bulge_factor)
            )  # Decrease width of lines horizontally farther from the center
            height_penalty = (
                0.10 * (1.0 - abs(pole_distance_factor)) ** 2
            )  # Decrease height of lines vertically farther from the center
            if (
                max_latitude_line_length <= constants.world_dimensions_options[1]
            ):  # Increase height for smaller maps to avoid empty space near poles
                height_penalty *= 0.6
            if max_latitude_line_length >= constants.world_dimensions_options[-3]:
                width_penalty *= 2
            tile_width, tile_height = (
                base_tile_width - width_penalty,
                base_tile_height - height_penalty,
            )
            tile_width *= 0.8
            if (
                min_width
            ) and pole_distance_factor > 0.1:  # Since rightmost (highest level) latitude line is not covered by any others, it should be thinner to avoid an obvious size difference
                tile_width = 0.015
            tile_height = max(0.02, 0.08 - height_penalty)
            projection = {
                "x_offset": (center_position[0] + x_offset) * size_multiplier,
                "y_offset": (center_position[1] + y_offset) * size_multiplier,
                "x_size": tile_width * size_multiplier,
                "y_size": tile_height * size_multiplier,
                "level": level,
            }
            for image_id in (
                self.find_location(coordinates[0], coordinates[1])
                .attached_cells[0]
                .tile.get_image_id_list(terrain_only=True, force_clouds=True)
            ):
                # Apply projection offsets to each image in the tile's terrain
                if type(image_id) == str:
                    image_id = {"image_id": image_id}
                image_id.update(projection)
                return_list.append(image_id)

            if (
                self.get_pressure_ratio() > 10.0
            ):  # If high pressure, also have sky effects for 3rd farthest latitude line
                threshold = 3
            else:  # If normal or low pressure, only have sky effects for 2nd farthest latitude line
                threshold = 2
            if (
                (offset_width - offset <= threshold and not min_width)
                and self.get_parameter(constants.PRESSURE) > 0
                and constants.current_map_mode == "terrain"
            ):  # If 2nd farthest latitude line
                sky_effect = {
                    "image_id": "misc/green_screen_base.png",
                    "detail_level": 1.0,
                    "green_screen": tuple(self.sky_color),
                }
                sky_effect.update(projection)
                sky_effect["level"] += 10
                if threshold <= 3 or abs(longitude_bulge_factor) > 0.5:
                    sky_effect["x_size"] *= 0.4

                sky_effect["alpha"] = 75
                pressure_ratio = self.get_pressure_ratio()
                if pressure_ratio <= 1.0:  # More transparent for lower pressure
                    sky_effect["alpha"] = 50 + int(25 * min(pressure_ratio, 1))
                else:  # Less transparent for higher pressure
                    sky_effect["alpha"] = 75 + int(
                        25 * min((pressure_ratio - 1) / 99, 1)
                    )
                if offset != 0:
                    x_offset_magnitude = 0.02
                    if (
                        max_latitude_line_length
                        <= constants.world_dimensions_options[1]
                    ):
                        x_offset_magnitude *= 1.6
                    elif (
                        max_latitude_line_length
                        >= constants.world_dimensions_options[5]
                    ):
                        x_offset_magnitude *= 1.6
                    else:
                        x_offset_magnitude *= 1.6
                    x_offset += x_offset_magnitude * (
                        1 if longitude_bulge_factor >= 0 else -1
                    )  # Shift right if on right side and vice versa
                    sky_effect["x_offset"] = (
                        center_position[0] + x_offset
                    ) * size_multiplier

                return_list.append(sky_effect)
        return return_list

    def get_next_unaccounted_coordinates(
        self, latitude_line: List[Tuple[int, int]], default_coordinates: Tuple[int, int]
    ):
        """
        Description:
            If mode is equator_shift, shows the adjacent coordinate that is closer to the equator
                Reduces latitude distortions (tiles appear at accurate latitudes, slightly distorted to bulge equator) but misses some tiles
            If mode is closest_unerpresnted, scans a latitude line for any nearby coordinates that have no latitude line, allowing extending a latitude line's length while also missing fewer cells
                Misses fewer coordinates but introduces latitude distortions (tiles appearing at significantly inaccurate latitude)
        Input:
            list latitude_line: List of coordinates for each point in the latitude line
            tuple default_coordinates: Coordinates to insert if no other coordinates are found
        Output:
            int: Index of latitude line to insert coordinates at
            tuple: Coordinates to insert
        """
        inserted_coordinates = default_coordinates
        inserted_idx = latitude_line.index(default_coordinates)

        mode = "equator_shift"
        if (
            mode == "equator_shift"
        ):  # Insert nearby coordinates on the side closer to the equator
            if inserted_idx < round(len(latitude_line) / 2):
                inserted_idx += 1
            elif inserted_idx > round(len(latitude_line) / 2):
                inserted_idx -= 1
            inserted_coordinates = latitude_line[inserted_idx]

        elif (
            mode == "closest_unrepresented"
        ):  # Insert nearby latitudes that are not contained in any latitude lines
            for idx, coordinates in enumerate(latitude_line):
                for offset in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    adjacent_coordinates = (
                        (coordinates[0] + offset[0]) % self.coordinate_width,
                        (coordinates[1] + offset[1]) % self.coordinate_height,
                    )
                    if (
                        self.latitude_lines_types[adjacent_coordinates[0]][
                            adjacent_coordinates[1]
                        ]
                        == None
                        and not adjacent_coordinates in latitude_line
                    ):
                        # If wouldn't be shown in any latitude lines, show here
                        inserted_coordinates = adjacent_coordinates
                        inserted_idx = idx
        return inserted_idx, inserted_coordinates
