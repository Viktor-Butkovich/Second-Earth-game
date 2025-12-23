# Contains singleton to extract relevant content from actors to populate interface components

from __future__ import annotations
from typing import Dict, List, Any
from modules.interface_components import tables
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

    def table_location_content(
        self, table: tables.table_grid, location: locations.location
    ) -> List[List[str]]:
        if location is None:
            return []

        body: List[Dict[str, Any]] = []
        headers: List[str] = []
        if table.subject == constants.SUPPLY_CHAIN_TABLE_SUBJECT:
            # Generate the datatable from the location's supply chain plan
            body = location.supply_chain_plan.generate_datatable()
            headers = [
                "item_type",
                "present",
                "delivering",
                "consuming",
                "total",
            ]
        else:
            raise ValueError(f"Unexpected table grid subject: {table.subject}")

        # Provide first row as headers and subsequent rows as JSON body content
        return [[col_name.replace("_", " ").title() for col_name in headers]] + [
            [str(data[col_name]) for col_name in headers] for data in body
        ]
