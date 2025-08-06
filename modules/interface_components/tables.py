# Contains functionality for table grids

from __future__ import annotations
from typing import Dict, List, Tuple
from modules.util import scaling, actor_utility
from modules.interface_components import cells, grids, buttons
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
        self.content: List[List[str]] = []
        super().__init__(input_dict)
        self.flex_num_rows: bool = True
        # Whether this table grid should adjust # rows based on content
        if self.flex_num_rows:
            self.current_num_rows: int = self.coordinate_height
        self.pagination: bool = True
        if self.pagination:
            self.unpaginated_content: List[List[str]] = []
            self.insert_collection_above()
            self.rows_per_page: int = (
                self.coordinate_height
            )  # Note that this does not include the header row
            self.current_page: int = 0
            self.pagination_next_button: buttons.anonymous_button = (
                self.create_pagination_button(
                    change=1,
                    relative_coordinates=(
                        scaling.scale_width(-40),
                        0,
                    ),
                )
            )
            self.pagination_previous_button: buttons.anonymous_button = (
                self.create_pagination_button(
                    change=-1,
                    relative_coordinates=(
                        scaling.scale_width(-40),
                        self.height - scaling.scale_height(35),
                    ),
                )
            )
        self.has_header_row: bool = True
        self.actor: actors.actor = None

    @property
    def visible_coordinate_height(self) -> int:
        if self.flex_num_rows:
            return self.current_num_rows
        else:
            return super().visible_coordinate_height

    @property
    def show_internal_grid_lines(self) -> bool:
        return True

    @property
    def show_external_grid_lines(self) -> bool:
        return False

    @property
    def num_pages(self) -> int:
        """
        Returns the number of pages for this table based on content and page size
        """
        if self.pagination:
            if self.has_header_row:
                return (len(self.unpaginated_content) - 1) // (
                    self.rows_per_page - 1
                ) + 1
            else:
                return len(self.unpaginated_content) // self.rows_per_page + 1
        else:
            return 1

    def create_pagination_button(
        self,
        change: int,
        relative_coordinates: Tuple[int, int],
    ) -> buttons.anonymous_button:
        """
        Description:
            Creates a pagination button that changes the current page of this table grid by the inputted change
        Input:
            int change: Change in page number, positive to go forward, negative to go back
            tuple relative_coordinates: Coordinates relative to this table grid
        Output:
            anonymous_button: Returns a button that changes the current page of this table grid by the change value
        """
        return constants.ActorCreationManager.create_interface_element(
            {
                "coordinates": relative_coordinates,
                "width": scaling.scale_width(35),
                "height": scaling.scale_height(35),
                "parent_collection": self.parent_collection,
                "init_type": constants.ANONYMOUS_BUTTON,
                "image_id": (
                    "buttons/cycle_ministers_down_button.png"
                    if change > 0
                    else "buttons/cycle_ministers_up_button.png"
                ),
                "button_type": {
                    "on_click": [
                        (
                            self.change_pagination,
                            [change],
                        )
                    ],
                    "can_show": [
                        (
                            self.can_show_pagination,
                            [change],
                        )
                    ],
                    "tooltip": [
                        (
                            "Click to navigate to the next page of the table"
                            if change > 0
                            else "Click to navigate to the previous page of the table"
                        )
                    ],
                },
            },
        )

    def change_pagination(self, change: int) -> None:
        """
        Description:
            Changes the current page of this table grid by the inputted change value
        Input:
            int change: Change in page number, positive to go forward, negative to go back
        Output:
            None
        """
        self.current_page += change
        self.calibrate(self.actor)  # Re-populate the table with the new page content

    def can_show_pagination(self, change: int) -> bool:
        """
        Description:
            Checks if a pagination button can be shown based on the current page and change value
        Input:
            int change: Button's change in page number
        Output:
            bool: True if pagination can be shown, False otherwise
        """
        return (
            self.pagination
            and self.content
            and self.current_page + change >= 0
            and self.current_page + change < self.num_pages
        )

    def update_flex_widths(self) -> None:
        """
        Updates column widths to accommodate the current content
        """
        margin = scaling.scale_width(5)
        self.column_widths = [10] * self.coordinate_width
        for row in self.content:
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

    def update_flex_num_rows(self) -> None:
        """
        Updates the number of rows in this table grid to accommodate the current content
        """
        if not self.flex_num_rows:
            return

        self.current_num_rows = min(self.coordinate_height, max(1, len(self.content)))

        for row_index in range(1, self.coordinate_height + 1):
            for current_cell in self.get_row(row_index):
                current_cell.set_visible(row_index <= self.current_num_rows)

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

    def get_page_bounds(self) -> Tuple[int, int]:
        """
        Description:
            Returns the bounds of the current page in this table grid
        Input:
            None
        Output:
            int tuple: Two values representing the start and end indices of the current page
        """
        if (not self.pagination) or (not self.content):
            return 0, 0

        if self.has_header_row:
            non_header_rows_per_page = self.rows_per_page - 1
        else:
            non_header_rows_per_page = self.rows_per_page
        start_index = self.current_page * non_header_rows_per_page
        end_index = min(
            start_index + non_header_rows_per_page, len(self.unpaginated_content)
        )
        if self.has_header_row:
            start_index += 1
            end_index += 1
        return start_index, end_index

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
        self.actor = new_actor
        if self.subject == constants.SUPPLY_CHAIN_TABLE_SUBJECT:
            self.content = constants.ContentProvider.table_location_content(
                self, new_actor
            )
        else:
            raise ValueError(f"Unexpected table grid subject: {self.subject}")
        if len(self.content) == 1:
            # If there's only a header row, add an N/A row
            self.content.append(["N/A"] * self.coordinate_width)

        if self.pagination and self.content:
            self.unpaginated_content = self.content
            self.current_page = min(max(self.current_page, 0), self.num_pages - 1)
            current_page_bounds = self.get_page_bounds()
            if self.has_header_row:
                self.content = [self.content[0]] + self.content[
                    current_page_bounds[0] : current_page_bounds[1]
                ]
            else:
                self.content = self.content[
                    current_page_bounds[0] : current_page_bounds[1]
                ]

        if self.flex_width:
            self.update_flex_widths()

        if self.flex_num_rows:
            self.update_flex_num_rows()

        # Populate the table cells with the content
        for row_index, row_data in enumerate(self.content[: self.coordinate_height]):
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
