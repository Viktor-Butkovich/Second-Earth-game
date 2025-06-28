# Contains functionality for grids

import random
import pygame
import itertools
from typing import Dict, Tuple
from modules.interface_components import cells, interface_elements
from modules.util import utility, actor_utility
from modules.constructs import world_handlers
from modules.constants import constants, status, flags


class grid(interface_elements.interface_element):
    """
    Grid of cells of the same size with different positions based on the grid's size and the number of cells. Each cell contains various actors, terrain, and resources
    """

    def __init__(self, input_dict: Dict[str, any]) -> None:
        """
        Description:
            Initializes this object
        Input:
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
        self.world_handler: world_handlers.world_handler = None
        input_dict["world_handler"].subscribe_grid(self)
        self.grid_line_width: int = input_dict.get("grid_line_width", 3)
        self.coordinate_width: int = input_dict.get(
            "coordinate_size", input_dict.get("coordinate_width")
        )
        self.coordinate_height: int = input_dict.get(
            "coordinate_size", input_dict.get("coordinate_height")
        )
        self.internal_line_color = input_dict.get(
            "internal_line_color", constants.COLOR_BLACK
        )
        self.external_line_color = input_dict.get(
            "external_line_color", constants.COLOR_DARK_GRAY
        )
        cell_width, cell_height = self.get_cell_width(), self.get_cell_height()
        self.cell_list = [
            [
                cells.cell(
                    x,
                    y,
                    cell_width,
                    cell_height,
                    self,
                    constants.color_dict[constants.COLOR_BRIGHT_GREEN],
                )
                for y in range(self.coordinate_height)
            ]
            for x in range(self.coordinate_width)
        ]

    def get_absolute_coordinates(self, mini_x, mini_y):
        return mini_x, mini_y

    @property
    def is_mini_grid(self) -> bool:
        return False

    @property
    def is_abstract_grid(self) -> bool:
        return False

    def get_tuning(self, tuning_type: str) -> any:
        """
        Description:
            Returns the tuning value for the inputted tuning type
        Input:
            string tuning_type: Tuning type to return the value of
        Output:
            any: Returns the tuning value
        """
        return constants.TerrainManager.get_tuning(tuning_type)

    def draw(self):
        """
        Draws each cell of this grid
        """
        for cell in self.get_flat_cell_list():
            cell.draw()
        self.draw_grid_lines()

        if (
            status.displayed_location
            and self in status.displayed_location.world_handler.subscribed_grids
        ):
            for cell in status.displayed_location.subscribed_cells:
                cell.draw_outline(constants.COLOR_WHITE)
        if status.displayed_mob and (
            self in status.displayed_mob.location.world_handler.subscribed_grids
            or (
                status.displayed_mob.end_turn_destination
                and self
                in status.displayed_mob.end_turn_destination.world_handler.subscribed_grids
            )
        ):
            if flags.show_selection_outlines:
                for cell in status.displayed_location.subscribed_cells:
                    cell.draw_outline(constants.COLOR_BRIGHT_GREEN)

                    if len(status.displayed_mob.base_automatic_route) > 0:
                        start_coordinates = status.displayed_mob.base_automatic_route[0]
                        end_coordinates = status.displayed_mob.base_automatic_route[-1]
                        for (
                            current_coordinates
                        ) in status.displayed_mob.base_automatic_route:
                            if current_coordinates == start_coordinates:
                                color = constants.COLOR_PURPLE
                            elif current_coordinates == end_coordinates:
                                color = constants.COLOR_YELLOW
                            else:
                                color = constants.COLOR_BRIGHT_BLUE
                            for (
                                automatic_route_cell
                            ) in status.displayed_location.world_handler.find_location(
                                current_coordinates[0], current_coordinates[1]
                            ).subscribed_cells:
                                automatic_route_cell.draw_outline(color)
                if status.displayed_mob.end_turn_destination:
                    for (
                        destination_cell
                    ) in status.displayed_mob.end_turn_destination.subscribed_cells:
                        if destination_cell.grid.showing:
                            destination_cell.draw_outline(constants.COLOR_YELLOW)

    def draw_grid_lines(self):
        """
        Draws lines between grid cells and on the outside of the grid. Also draws an outline of the area on this grid covered by this grid's minimap grid, if applicable
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

        for origin, destination in [
            ((0, 0), (0, self.coordinate_height)),
            (
                (self.coordinate_width, 0),
                (self.coordinate_width, self.coordinate_height),
            ),
            ((0, 0), (self.coordinate_width, 0)),
            (
                (0, self.coordinate_height),
                (self.coordinate_width, self.coordinate_height),
            ),
        ]:
            pygame.draw.line(
                constants.game_display,
                constants.color_dict[self.external_line_color],
                self.convert_coordinates(origin),
                self.convert_coordinates(destination),
                self.grid_line_width + 1,
            )

        if flags.show_minimap_outlines and self == status.scrolling_strategic_map_grid:
            # Show an outline of the area that the minimap grid covers
            left_x = (
                self.coordinate_width // 2 - status.minimap_grid.coordinate_width // 2
            )
            right_x = (
                self.coordinate_width // 2
                + status.minimap_grid.coordinate_width // 2
                + 1
            )
            down_y = (
                self.coordinate_height // 2 - status.minimap_grid.coordinate_height // 2
            )
            up_y = (
                self.coordinate_height // 2
                + status.minimap_grid.coordinate_height // 2
                + 1
            )
            for origin, destination in [
                ((left_x, down_y), (left_x, up_y)),
                ((left_x, up_y), (right_x, up_y)),
                ((right_x, up_y), (right_x, down_y)),
                ((right_x, down_y), (left_x, down_y)),
            ]:
                pygame.draw.line(
                    constants.game_display,
                    constants.color_dict[status.minimap_grid.external_line_color],
                    self.convert_coordinates(origin),
                    self.convert_coordinates(destination),
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
            if not current_cell.location.terrain in allowed_terrains:
                continue
            possible_cells.append(current_cell)
        if len(possible_cells) == 0:
            possible_cells.append(None)
        return random.choice(possible_cells)

    def get_flat_cell_list(self) -> itertools.chain[cells.cell]:
        """
        Description:
            Generates and returns a flattened version of this grid's 2-dimensional cell list
        Input:
            None
        Output:
            cell list: Returns a flattened version of this grid's 2-dimensional cell list
        """
        return itertools.chain.from_iterable(self.cell_list)

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
        Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        """
        super().remove()
        status.grid_list = utility.remove_from_list(status.grid_list, self)
        self.world_handler.unsubscribe_grid(self)


class mini_grid(grid):
    """
    Grid that zooms in on a small area of a larger attached grid, centered on a certain cell of the attached grid. Which cell is being centered on can be changed
    """

    def __init__(self, input_dict: Dict[str, any]) -> None:
        """
        Description:
            Initializes this object
        Input:
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
        self.center_x = 0
        self.center_y = 0
        super().__init__(input_dict)

    @property
    def is_mini_grid(self) -> bool:
        return True

    def calibrate(self, center_x, center_y):
        """
        Description:
            Centers this mini grid on the cell at the inputted coordinates of the attached world, moving any displayed actors, terrain, and resources on this grid to their new locations as needed
        Input:
            int center_x: x coordinate on the attached world to center on
            int center_y: y coordinate on the attached world to center on
        Output:
            None
        """
        if constants.current_game_mode in self.modes and (
            self.center_x,
            self.center_y,
        ) != (center_x, center_y):
            self.center_x = center_x
            self.center_y = center_y

            for x in range(self.coordinate_width):
                for y in range(self.coordinate_height):
                    self.world_handler.find_location(
                        *self.get_absolute_coordinates(x, y)
                    ).subscribe_cell(
                        self.find_cell(x, y)
                    )  # Calibrate each cell to its the new location
            if self == status.minimap_grid:
                for (
                    directional_indicator_image
                ) in status.directional_indicator_image_list:
                    directional_indicator_image.calibrate()
            if self == status.scrolling_strategic_map_grid:
                status.current_world.update_globe_projection()

    def get_absolute_coordinates(self, mini_x, mini_y):
        """
        Description:
            Converts the inputted coordinates on this grid to the corresponding coordinates on the attached world, returning the converted coordinates
        Input:
            int mini_x: x coordinate on this grid
            int mini_y: y coordinate on this grid
        Output:
            int: x coordinate of the attached world corresponding to the inputted x coordinate
            int: y coordinate of the attached world corresponding to the inputted y coordinate
        """
        attached_x = (
            self.center_x + mini_x - round((self.coordinate_width - 1) / 2)
        )  # if width is 5, ((5 - 1) / 2) = (4 / 2) = 2, since 2 is the center of a 5 width grid starting at 0
        attached_y = self.center_y + mini_y - round((self.coordinate_height - 1) / 2)
        if attached_x < 0:
            attached_x += self.world_handler.world_dimensions
        elif attached_x >= self.world_handler.world_dimensions:
            attached_x -= self.world_handler.world_dimensions
        if attached_y < 0:
            attached_y += self.world_handler.world_dimensions
        elif attached_y >= self.world_handler.world_dimensions:
            attached_y -= self.world_handler.world_dimensions
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
                % status.current_world.world_dimensions
            )
            % self.coordinate_width,
            (
                int(
                    original_y - self.center_y + round((self.coordinate_height - 1) / 2)
                )
                % status.current_world.world_dimensions
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
        ) % status.current_world.world_dimensions
        minimap_y = (
            original_y - self.center_y + (round(self.coordinate_height - 1) / 2)
        ) % status.current_world.world_dimensions
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
        Draws lines between grid cells and on the outside of the grid
        """
        if (
            self == status.scrolling_strategic_map_grid
        ):  # Scrolling map acts more like a default grid than normal minimap
            super().draw_grid_lines()
            if (
                constants.EffectManager.effect_active("allow_planet_mask")
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

    def __init__(self, input_dict: Dict[str, any]) -> None:
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of the bottom left corner of this grid
                'width': int value - Pixel width of this grid
                'height': int value - Pixel height of this grid
                'internal_line_color': string value - Color in the color_dict dictionary for lines between cells, like 'bright blue'
                'external_line_color': string value - Color in the color_dict dictionary for lines on the outside of the grid, like 'bright blue'
                'list modes': string list value - Game modes during which this grid can appear
                'grid_line_width': int value - Pixel width of lines between cells. Lines on the outside of the grid are one pixel thicker
                'cell_list': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each cell in this grid
                'name': Name of this grid
        Output:
            None
        """
        input_dict["coordinate_width"] = 1
        input_dict["coordinate_height"] = 1
        super().__init__(input_dict)

    @property
    def name(self) -> str:
        return self.world_handler.name

    @property
    def is_abstract_grid(self) -> bool:
        return True
