# Contains functionality for grids

import random
import pygame
import itertools
from typing import Dict, List, Tuple
from modules.interface_types import cells, interface_elements
from modules.util import actor_utility, utility
from modules.constructs import world_handlers
from modules.constants import constants, status, flags


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
        self.attached_grid: grid = None
        self.coordinate_width: int = input_dict.get(
            "coordinate_size", input_dict.get("coordinate_width")
        )
        self.coordinate_height: int = input_dict.get(
            "coordinate_size", input_dict.get("coordinate_height")
        )
        self.area: int = self.coordinate_width * self.coordinate_height
        self.internal_line_color = input_dict.get(
            "internal_line_color", constants.COLOR_BLACK
        )
        self.external_line_color = input_dict.get(
            "external_line_color", constants.COLOR_DARK_GRAY
        )
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
            "name": self.world_handler.name,
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
        cell_list = list(self.get_flat_cell_list())
        if self.attached_grid:
            cell_list += list(self.attached_grid.get_flat_cell_list())

        if status.displayed_tile and status.displayed_tile.cell in cell_list:
            status.displayed_tile.draw_actor_match_outline()
        if status.displayed_mob and (
            status.displayed_mob.get_cell() in cell_list
            or (
                status.displayed_mob.end_turn_destination
                and status.displayed_mob.end_turn_destination.cell in cell_list
            )
        ):
            status.displayed_mob.draw_outline()

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
            constants.color_dict[constants.COLOR_BRIGHT_GREEN],
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

    def calibrate(self, center_x, center_y, recursive=False, calibrate_center=True):
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
                if calibrate_center:
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
            status.strategic_map_grid.update_globe_projection()

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
        if input_dict["grid_type"] == constants.EARTH_GRID_TYPE:
            self.world_handler = world_handlers.world_handler(
                self,
                from_save,
                input_dict.get("world_handler", {"grid_type": input_dict["grid_type"]}),
            )
        elif input_dict["grid_type"] == constants.GLOBE_PROJECTION_GRID_TYPE:
            self.world_handler = status.strategic_map_grid.world_handler
        self.is_abstract_grid = True
        self.name = self.world_handler.name
        self.cell_list[0][0].terrain_handler.set_visibility(True)

    def rename(self, new_name: str) -> None:
        """
        Description:
            Renames this grid
        Input:
            string new_name: New name for this grid
        Output:
            None
        """
        self.name = new_name
        self.world_handler.name = new_name
        self.cell_list[0][0].tile.name = new_name
        if status.displayed_tile == self.cell_list[0][0].tile:
            actor_utility.calibrate_actor_info_display(
                status.tile_info_display, status.displayed_tile
            )
