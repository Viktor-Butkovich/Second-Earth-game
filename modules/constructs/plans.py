from __future__ import annotations
from typing import Dict, List, Any
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
        self.stored: float = float(self.parent_plan.stored.get(item_type.key, 0.0))
        self.local: float = float(self.parent_plan.local.get(item_type.key, 0.0))
        self.delta: float = self.parent_plan.delta.get(item_type.key, 0.0)

    @property
    def total(self) -> float:
        """
        Calculates and returns the amount of this item type after considering initial stored, demand, and request delta
            If possible, locations should create requests until all effective amounts are non-negative
        """
        return round(self.local + self.delta - self.demand, 2)


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

    def generate_datatable(self) -> List[Dict[str, Any]]:
        """
        Description:
            Generates datatable representation of the location's supply chain plan
                Includes item type, present, demand, delivered, and net amount fields
        """
        datatable = []
        for subplan in self.subplans.values():
            datatable.append(
                {
                    "item_type": subplan.item_type.name.title(),
                    "present": subplan.local if subplan.local != 0 else "",
                    "delivering": subplan.delta if subplan.delta != 0 else "",
                    "consuming": (
                        subplan.demand * -1 if subplan.demand != 0 else ""
                    ),  # Display demand as negative due to expected decrease in amount, while still using positives for calculations
                    "total": subplan.total if subplan.total != 0 else "",
                }
            )
        return datatable

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
            del total_demand[constants.ENERGY_ITEM]
        # Add logic to include requests from other locations
        return total_demand
