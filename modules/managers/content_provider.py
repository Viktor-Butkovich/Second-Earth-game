# Contains singleton to extract relevant content from actors to populate interface components

from modules.interface_components import grids
from modules.constructs.actor_types import locations
from modules.constants import constants, status, flags


class content_provider:
    """
    Object that extracts relevant content from actors to populate interface components
    """

    def __init__(self) -> None:
        """
        Initializes this object
        """
        return

    def populate_table_location_content(
        self, table: grids.table_grid, location: locations.location
    ) -> None:
        if table.subject == constants.SUPPLY_CHAIN_TABLE_SUBJECT:
            for col, col_name in enumerate(
                [
                    "Item Type",
                    "Present",
                    "Demand",
                    "Requested",
                    "Unfulfilled",
                    "Expected",
                ]
            ):
                table.get_cell(1, col + 1).set_text(col_name)
