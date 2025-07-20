# Contains functionality for grids

from __future__ import annotations
import pygame
import itertools
from typing import Dict, List, Tuple
from modules.interface_components import cells, interface_elements
from modules.util import utility
from modules.constructs import world_handlers
from modules.constructs.actor_types import actors
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
        Output:
            None
        """
        self.cell_list: List[cells.cell] = []
        super().__init__(input_dict)
        status.grid_list.append(self)
        self.grid_line_width: int = input_dict.get("grid_line_width", 3)
        self.coordinate_width: int = input_dict.get(
            "coordinate_size", input_dict.get("coordinate_width")
        )
        self.coordinate_height: int = input_dict.get(
            "coordinate_size", input_dict.get("coordinate_height")
        )
        self.internal_line_color: str = input_dict.get(
            "internal_line_color", constants.COLOR_BLACK
        )
        self.external_line_color: str = input_dict.get(
            "external_line_color", constants.COLOR_DARK_GRAY
        )
        cell_width, cell_height = self.get_cell_width(), self.get_cell_height()
        self.cell_list: List[cells.cell] = [
            [
                constants.ActorCreationManager.create_interface_element(
                    {
                        "init_type": constants.CELL,
                        "grid": self,
                        "coordinates": self.convert_coordinates((x, y)),
                        "grid_coordinates": (x, y),
                        "width": cell_width,
                        "height": cell_height,
                        "override_no_parent_collection": True,
                    }
                )
                for y in range(self.coordinate_height)
            ]
            for x in range(self.coordinate_width)
        ]

    def set_origin(self, new_x: int, new_y: int) -> None:
        """
        Description:
            Sets this interface element's location at the inputted coordinates
        Input:
            int new_x: New x coordinate for this element's origin
            int new_y: New y coordinate for this element's origin
        Output:
            None
        """
        super().set_origin(new_x, new_y)
        for current_cell in self.get_flat_cell_list():
            current_cell.set_origin(
                *self.convert_coordinates((current_cell.grid_x, current_cell.grid_y))
            )

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

    @property
    def show_internal_grid_lines(self) -> bool:
        return flags.show_grid_lines

    @property
    def show_external_grid_lines(self) -> bool:
        return True

    def draw_grid_lines(self):
        """
        Draws lines between grid cells and on the outside of the grid
        """
        if self.show_internal_grid_lines:
            for x in range(1, self.coordinate_width):
                pygame.draw.line(
                    constants.game_display,
                    constants.color_dict[self.internal_line_color],
                    self.convert_coordinates((x, 0), reverse_y=True),
                    self.convert_coordinates(
                        (x, self.coordinate_height), reverse_y=True
                    ),
                    self.grid_line_width,
                )

            for y in range(1, self.coordinate_height):
                pygame.draw.line(
                    constants.game_display,
                    constants.color_dict[self.internal_line_color],
                    self.convert_coordinates((0, y), reverse_y=True),
                    self.convert_coordinates(
                        (self.coordinate_width, y), reverse_y=True
                    ),
                    self.grid_line_width,
                )

        if self.show_external_grid_lines:
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
                    self.convert_coordinates(origin, reverse_y=True),
                    self.convert_coordinates(destination, reverse_y=True),
                    self.grid_line_width + 1,
                )

    def convert_coordinates(
        self, coordinates: Tuple[int, int], reverse_y: bool = False
    ) -> Tuple[int, int]:
        """
        Description:
            Returns the pixel coordinates of the bottom left corner of this grid's cell that occupies the inputted grid coordinates
        Input:
            int tuple coordinates: Two values representing x and y grid coordinates of the cell whose corner is found
        Output:
            int tuple: Two values representing x and y pixel coordinates of the bottom left corner of the requested cell
        """
        x, y = coordinates
        if reverse_y:
            return (
                (int((self.width / (self.coordinate_width)) * x) + self.x),
                constants.display_height
                - (int((self.height / (self.coordinate_height)) * y) + self.y),
            )
        else:
            return (
                (int((self.width / (self.coordinate_width)) * x) + self.x),
                (int((self.height / (self.coordinate_height)) * y) + self.y),
            )

    def get_height(self) -> int:
        """
        Description:
            Returns how many rows this grid has
        Input:
            None
        Output:
            int: Number of rows this grid has
        """
        return self.coordinate_height

    def get_width(self) -> int:
        """
        Description:
            Returns how many columns this grid has
        Input:
            None
        Output:
            int: Number of columns this grid has
        """
        return self.coordinate_width

    def get_cell_width(self) -> int:
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

    def get_cell(self, x: int, y: int) -> cells.cell:
        """
        Description:
            Returns this grid's cell that occupies the inputted coordinates
        Input:
            int x: x coordinate for the grid location of the requested cell
            int y: y coordinate for the grid location of the requested cell
        Output:
            cell: Returns this grid's cell that occupies the inputted coordinates
        """
        return self.cell_list[x][y]

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

    def can_draw(self) -> bool:
        """
        Description:
            Calculates and returns whether it would be valid to call this object's draw()
        Input:
            None
        Output:
            boolean: Returns whether it would be valid to call this object's draw()
        """
        return self.showing

    def remove(self) -> None:
        """
        Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        """
        super().remove()
        status.grid_list = utility.remove_from_list(status.grid_list, self)


class table_grid(grid):
    """
    Grid of cells that display tabular data, such as lists and ledgers with accompanying icons and tooltips
    """

    def __init__(self, input_dict: Dict[str, any]) -> None:
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                Same as superclass, except:
                'subject': string value - Subject of this table grid, such as 'supply_chain'
                    Used to identify the type of content to populate the grid with
        Output:
            None
        """
        super().__init__(input_dict)
        self.subject: str = input_dict["subject"]

    @property
    def show_internal_grid_lines(self) -> bool:
        return True

    @property
    def show_external_grid_lines(self) -> bool:
        return False

    def calibrate(self, new_actor: actors.actor) -> None:
        """
        Placeholder to test matrix coordinate system
        """
        super().calibrate(new_actor)
        if self.subject == constants.SUPPLY_CHAIN_TABLE_SUBJECT:
            constants.ContentProvider.populate_table_location_content(self, new_actor)
        else:
            raise ValueError(f"Unexpected table grid subject: {self.subject}")

    def get_row(self, index: int) -> List[cells.cell]:
        """
        Description:
            Returns the row of cells at the inputted index, using standard matrix notation (top left is row 1, col 1)
        Input:
            int index: Index of the row to return
        Output:
            list: Returns the row of cells at the inputted index
        """
        return [col[len(col) - index] for col in self.cell_list]

    def get_col(self, index: int) -> List[cells.cell]:
        """
        Description:
            Returns the column of cells at the inputted index, using standard matrix notation (top left is row 1, col 1)
        Input:
            int index: Index of the column to return
        Output:
            list: Returns the column of cells at the inputted index
        """
        return self.cell_list[index - 1]

    def get_cell(self, row, column) -> cells.cell:
        """
        Description:
            Returns this grid's cell that occupies the inputted row and column, using standard matrix notation
                (top left is row 1, col 1)
        Input:
            int row: Row index for the grid location of the requested cell
            int column: Column index for the grid location of the requested cell
        Output:
            cell: Returns this grid's cell that occupies the inputted row and column
        """
        return self.cell_list[column - 1][len(self.cell_list[0]) - row]


class location_grid(grid):
    """
    Grid of cells that correspond to world locations, which can contain terrain, units, buildings, etc.
    """

    def __init__(self, input_dict: Dict[str, any]) -> None:
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                Same as superclass, except:
                'world_handler': world_handlers.world_handler value - World handler to which this grid is attached
        Output:
            None
        """
        status.location_grid_list.append(self)
        self.world_handler: world_handlers.world_handler = None
        input_dict["world_handler"].subscribe_grid(self)
        super().__init__(input_dict)
        for current_cell in self.get_flat_cell_list():
            self.world_handler.find_location(
                current_cell.x, current_cell.y
            ).subscribe_cell(current_cell)

    def get_absolute_coordinates(self, mini_x, mini_y):
        return mini_x, mini_y

    @property
    def is_mini_grid(self) -> bool:
        return False

    @property
    def is_abstract_grid(self) -> bool:
        return False

    def remove(self):
        """
        Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        """
        super().remove()
        self.world_handler.unsubscribe_grid(self)
        status.location_grid_list = utility.remove_from_list(
            status.location_grid_list, self
        )

    def draw_grid_lines(self):
        """
        Draws lines between grid cells and on the outside of the grid. Also draws an outline of the area on this grid covered by this grid's minimap grid, if applicable
        """
        super().draw_grid_lines()
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
                    self.convert_coordinates(origin, reverse_y=True),
                    self.convert_coordinates(destination, reverse_y=True),
                    self.grid_line_width + 1,
                )


class mini_grid(location_grid):
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

    def calibrate(self, center_x: int, center_y: int) -> None:
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
                        self.get_cell(x, y)
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
        if self.show_internal_grid_lines:
            for x in range(0, self.coordinate_width + 1):
                pygame.draw.line(
                    constants.game_display,
                    constants.color_dict[self.internal_line_color],
                    self.convert_coordinates((x, 0), reverse_y=True),
                    self.convert_coordinates(
                        (x, self.coordinate_height), reverse_y=True
                    ),
                    self.grid_line_width,
                )

            for y in range(0, self.coordinate_height + 1):
                pygame.draw.line(
                    constants.game_display,
                    constants.color_dict[self.internal_line_color],
                    self.convert_coordinates((0, y), reverse_y=True),
                    self.convert_coordinates(
                        (self.coordinate_width, y), reverse_y=True
                    ),
                    self.grid_line_width,
                )

        for y in range(0, self.coordinate_height + 1):
            pygame.draw.line(
                constants.game_display,
                constants.color_dict[self.external_line_color],
                self.convert_coordinates((left_x, down_y), reverse_y=True),
                self.convert_coordinates((left_x, up_y), reverse_y=True),
                self.grid_line_width + 1,
            )

        if self.show_external_grid_lines:
            pygame.draw.line(
                constants.game_display,
                constants.color_dict[self.external_line_color],
                self.convert_coordinates((left_x, up_y), reverse_y=True),
                self.convert_coordinates((right_x, up_y), reverse_y=True),
                self.grid_line_width + 1,
            )

            pygame.draw.line(
                constants.game_display,
                constants.color_dict[self.external_line_color],
                self.convert_coordinates((right_x, up_y), reverse_y=True),
                self.convert_coordinates((right_x, down_y), reverse_y=True),
                self.grid_line_width + 1,
            )

            pygame.draw.line(
                constants.game_display,
                constants.color_dict[self.external_line_color],
                self.convert_coordinates((right_x, down_y), reverse_y=True),
                self.convert_coordinates((left_x, down_y), reverse_y=True),
                self.grid_line_width + 1,
            )


class abstract_grid(location_grid):
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
