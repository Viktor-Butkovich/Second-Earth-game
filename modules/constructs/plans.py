from __future__ import annotations
from typing import Dict, List, Any, Generator, Tuple
from modules.constructs.actor_types import locations
from modules.constructs import item_types
from modules.util import utility
from modules.constants import constants, status, flags


class supply_chain_request:
    def __init__(
        self,
        item_type: item_types.item_type,
        amount: int,
        origin: locations.location,
        destination: locations.location,
    ):
        # Implement priority as a new parameter later
        self.item_type: item_types.item_type = item_type
        self.amount: int = amount
        self.origin: locations.location = origin
        self.destination: locations.location = destination

    def execute(self) -> None:
        pass


class supply_chain_subplan:
    def __init__(self, item_type: item_types.item_type, parent_plan: supply_chain_plan):
        self.item_type: item_types.item_type = item_type
        self.parent_plan: supply_chain_plan = parent_plan
        self.location: locations.location = parent_plan.location
        self.demand: float = self.parent_plan.demand.get(item_type.key, 0.0)
        self.consumption: float = self.parent_plan.consumption.get(item_type.key, 0.0)
        self.stored: float = float(self.parent_plan.stored.get(item_type.key, 0.0))
        self.local: float = float(self.parent_plan.local.get(item_type.key, 0.0))
        self.delta: float = self.parent_plan.delta.get(item_type.key, 0.0)

    @property
    def expected(self) -> float:
        """
        Calculates and returns the amount of this item type after considering initial stored, demand, and request delta
            If possible, locations should create requests until all effective amounts are non-negative
        """
        return round(self.local + self.delta - self.consumption, 2)


class supply_chain_plan:
    """
    Location-wide plan for item type demand, stored inventory, and request deltas
    """

    def __init__(self, location: locations.location) -> None:
        """
        Description:
            Initializes the supply chain plan for a given location
                Demand: Amount of item type expected to be consumed at this location this turn
                Stored: Amount of item type directly stored in this location's warehouses
                Local: Amount of item type available at this location, including subscribed mobs
                Delta: Amount of item type expected to be delivered in or out this turn
            A subplan is created for each of the plan's item types
        Input:
            location location: Location for which this plan is created
        Output:
            None
        """
        self.location: locations.location = location
        self.demand: Dict[str, float] = self.calculate_demand()
        self.consumption: Dict[str, float] = location.location_item_upkeep_consumption
        self.stored: Dict[str, float] = location.inventory.copy()
        self.local: Dict[str, float] = utility.add_dicts(
            self.stored,
            *[current_mob.inventory for current_mob in location.subscribed_mobs],
        )
        self.delta: Dict[str, float] = (
            {}
        )  # Populated with estimates from ingoing and outgoing requests
        self.subplans: Dict[str, supply_chain_subplan] = {
            item_type.key: supply_chain_subplan(item_type, self)
            for item_type in self.get_relevant_item_types()
        }

    @property
    def trivial(self) -> bool:
        return not self.subplans

    def get_sorted_subplans(self) -> List[supply_chain_subplan]:
        """
        Returns an iterator of subplans sorted by amount of item already present, in descending order
        """
        return sorted(
            self.subplans.values(), key=lambda subplan: subplan.item_type.name.lower()
        )

    def get_sorted_subplan_index(self, item_key: str) -> int:
        """
        Returns the index of the inputted item key in the sorted subplan list
        """
        return list(self.get_sorted_subplans()).index(self.subplans[item_key])

    def generate_datatable(self) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Description:
            Generates datatable representation of the location's supply chain plan
                Includes item type, present, demand, delivered, and net amount fields
        Input:
            None
        Output:
            Tuple of body and header data
                List of dictionaries: Each body dictionary corresponds to a row, with keys for each column and dictionaries of description, tooltip, etc. for each cell
                Dictionary: Header dictionary with keys for each column and dictionaries of description, tooltip, etc. for each header cell
        """
        header = {
            "item_type": {
                constants.TABLEDATA_TEXT_KEY: "Item Type",
                constants.TABLEDATA_BATCH_TOOLTIP_KEY: [["Each supply chain section covers a specific item type."]],
            },
            "present": {
                constants.TABLEDATA_TEXT_KEY: "Present",
                constants.TABLEDATA_BATCH_TOOLTIP_KEY: [["There is this amount of the item stored among local warehouses and units."]],
            },
            "delivering": {
                constants.TABLEDATA_TEXT_KEY: "Delivering",
                constants.TABLEDATA_BATCH_TOOLTIP_KEY: [["Ingoing and outgoing deliveries are forecasted to cause a net change of this amount in stored inventory."]],
            },
            "consuming": {
                constants.TABLEDATA_TEXT_KEY: "Consuming",
                constants.TABLEDATA_BATCH_TOOLTIP_KEY: [["This location is forecasted to consume this amount of the item this turn."]],
            },
            "expected": {
                constants.TABLEDATA_TEXT_KEY: "Expected",
                constants.TABLEDATA_BATCH_TOOLTIP_KEY: [["This location is forecasted to have this amount of the item after the end of the turn."]],
            }
        }

        body = []
        # Sort item type subplans by amount present, in descending order
        for subplan in self.get_sorted_subplans():
            cells = {
                "item_type": {"description": f"This row summarizes the local {subplan.item_type.name} supply chain."},
                "present": {"description": f"{subplan.local} of {subplan.item_type.name} are stored among local warehouses and units."},
                "delivering": {"description": f"Ingoing and outgoing deliveries are forecasted to cause a net change of {subplan.delta} in stored {subplan.item_type.name}."},
                "consuming": {"description": f"This location is forecasted to consume {subplan.consumption} {subplan.item_type.name} this turn."},
                "expected": {"description": f"This location is forecasted to have {subplan.expected} {subplan.item_type.name} after the end of the turn."},
            }
            for key in cells:
                cells[key][constants.TABLEDATA_BATCH_TOOLTIP_KEY] = []
            for cell in [
                "item_type",
                "present",
            ]:
                if (
                    status.displayed_location_inventory
                    and status.displayed_location_inventory.current_item
                    == subplan.item_type
                ) or (
                    status.displayed_mob_inventory
                    and status.displayed_mob_inventory.current_item == subplan.item_type
                ):
                    cells[cell][constants.TABLEDATA_BACKGROUND_IMAGE_ID_KEY] = [
                        {
                            "image_id": "colors/selected_item_row_background.png",
                            "level": constants.TABLE_BACKGROUND_IMAGE_LEVEL,
                        }
                    ]
                # Highlight background of row if item type is currently selected
            cells["item_type"][constants.TABLEDATA_TEXT_KEY] = subplan.item_type.name.title()
            cells["present"][constants.TABLEDATA_TEXT_KEY] = str(subplan.local)
            cells["delivering"][constants.TABLEDATA_TEXT_KEY] = (
                str(subplan.delta) if subplan.delta != 0 else ""
            )

            cells["consuming"][constants.TABLEDATA_TEXT_KEY] = (
                str(subplan.consumption * -1) if subplan.consumption != 0 else ""
            )
            # Display demand as negative due to expected decrease in amount, while still using positives

            cells["expected"][constants.TABLEDATA_TEXT_KEY] = str(subplan.expected)
            if (
                not self.location.is_earth_location
            ) or constants.EffectManager.effect_active("enable_earth_upkeep"):
                if subplan.expected < 0:
                    cells["expected"][constants.TABLEDATA_BACKGROUND_IMAGE_ID_KEY] = [
                        {
                            "image_id": "colors/insufficient_upkeep_background.png",
                            "level": constants.TABLE_BACKGROUND_IMAGE_LEVEL,
                        }
                    ]
                    cells["expected"][constants.TABLEDATA_BATCH_TOOLTIP_KEY].append([
                        f"Since {subplan.item_type.name} demand exceeds the available stockpile by {abs(subplan.expected)}, this location will suffer penalties at the end of the turn.",
                    ])
                elif subplan.demand > subplan.local: # Officers have 0.1 demand but no consumption, so they require 0.1 to be present.
                    cells["expected"][constants.TABLEDATA_BACKGROUND_IMAGE_ID_KEY] = [
                        {
                            "image_id": "colors/insufficient_upkeep_background.png",
                            "level": constants.TABLE_BACKGROUND_IMAGE_LEVEL,
                        }
                    ]
                    cells["expected"][constants.TABLEDATA_BATCH_TOOLTIP_KEY].append([
                        f"This location requires at least {subplan.demand} {subplan.item_type.name} stored to avoid penalties at the end of the turn.",
                        f"Even units that only consume a negligible amount of {subplan.item_type.name} per turn (officers) require some amount to be present.",
                    ])
            for key in cells:
                cell = cells[key]
                cell[constants.TABLEDATA_BATCH_TOOLTIP_KEY].append([cell["description"]])
            body.append(
                {
                    constants.TABLECOL_ITEM_TYPE: cells["item_type"],
                    constants.TABLECOL_PRESENT: cells["present"],
                    constants.TABLECOL_DELIVERING: cells["delivering"],
                    constants.TABLECOL_CONSUMING: cells["consuming"],
                    constants.TABLECOL_EXPECTED: cells["expected"],
                }
            )
        return body, header

    def get_relevant_item_types(self) -> List[item_types.item_type]:
        """
        Description:
            Gets the union of all local item types and demanded item types at this plan's location
                Unfortunately, this is used for applications that expect preserving original order, so is not
                compatible with built-in set operations
        Input:
            None
        Output:
            item_type list: List of item types relevant to this plan
        """
        return [status.item_types[key] for key in self.local.keys()] + [
            status.item_types[key]
            for key in self.demand.keys()
            if key not in self.local
        ]

    def calculate_demand(self) -> Dict[str, float]:
        """
        Description:
            Calculate total demand for all item types at this plan's location
                This includes the initial demand and any additional requests made
        Input:
            None
        Output:
            dict: Dictionary with item type keys and total demand values
        """
        total_demand = self.location.location_item_upkeep_demand.copy()
        if constants.ENERGY_ITEM in total_demand:
            total_demand[constants.FUELS_ITEM] = (
                total_demand.get(constants.FUELS_ITEM, 0.0)
                + total_demand[constants.ENERGY_ITEM]
            )
            del total_demand[
                constants.ENERGY_ITEM
            ]  # Remap energy demand to fuel demand
        # Add logic to include requests from other locations
        return total_demand
