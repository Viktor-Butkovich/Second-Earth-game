# Contains functionality for table grids

from __future__ import annotations
from typing import Dict, List, Tuple
from modules.util import scaling
from modules.interface_components import cells, grids
from modules.constructs.actor_types import actors
from modules.constants import constants, status, flags


class table_grid(grids.grid):
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
        self.subject: str = input_dict["subject"]
        self.flex_width: bool = True
        # Whether this table grid should adjust its width based on content - eventually add as a configurable parameter
        if self.flex_width:
            self.column_widths: List[int] = [10] * input_dict["coordinate_width"]
        super().__init__(input_dict)

    @property
    def show_internal_grid_lines(self) -> bool:
        return True

    @property
    def show_external_grid_lines(self) -> bool:
        return False

    def update_flex_widths(self, content: List[List[str]]) -> None:
        """
        Updates the column widths based on the content provided
        """
        margin = scaling.scale_width(5)
        for row in content:
            for col_index, cell_data in enumerate(row):
                font = constants.fonts[constants.DEFAULT_NOTIFICATION_FONT]
                text_width, text_height = font.pygame_font.size(cell_data)
                self.column_widths[col_index] = max(
                    self.column_widths[col_index], text_width + (margin * 2)
                )

        # Update cell widths based on the new column widths
        for row in range(1, self.coordinate_height + 1):
            for col in range(1, self.coordinate_width + 1):
                cell = self.get_cell(row, col)
                cell.set_state(
                    *self.convert_coordinates((cell.grid_x, cell.grid_y)),
                    self.column_widths[col - 1],
                    cell.height,
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

        # Calculate the x-coordinate dynamically based on column widths
        pixel_x = self.x + sum(self.column_widths[:x])

        # Calculate the y-coordinate
        if reverse_y:
            pixel_y = constants.display_height - (
                int((self.height / self.coordinate_height) * y) + self.y
            )
        else:
            pixel_y = int((self.height / self.coordinate_height) * y) + self.y

        return pixel_x, pixel_y

    def calibrate(self, new_actor: actors.actor) -> None:
        """
        Description:
            Calibrates this table grid to the inputted actor, populating it with content based on table subject
        Input:
            actor new_actor: Actor to calibrate this table grid to
        Output:
            None
        """
        super().calibrate(new_actor)
        if self.subject == constants.SUPPLY_CHAIN_TABLE_SUBJECT:
            content = constants.ContentProvider.table_location_content(self, new_actor)
        else:
            raise ValueError(f"Unexpected table grid subject: {self.subject}")

        if self.flex_width:
            self.update_flex_widths(content)

        # Populate the table cells with the content
        for row_index, row_data in enumerate(content[: self.coordinate_height]):
            for col_index, cell_data in enumerate(row_data[: self.coordinate_width]):
                self.get_cell(row_index + 1, col_index + 1).set_text(cell_data)

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
