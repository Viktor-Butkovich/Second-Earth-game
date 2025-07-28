# Contains supply chain request engine singleton

from __future__ import annotations
from typing import List
from modules.util import actor_utility
from modules.constructs import plans


class supply_chain_request_engine:
    """
    Object that organizes all location-level supply chain plans and prescribes inter-location requests
        After resetting location plans, check for any plans with negative effective amounts
        Any plan with negative effective amounts should be considered a sink in the supply chain graph
        Any plans with positive effective amounts should be considered a source in the supply chain graph
        Request engine uses this graph to prescribe optimal requests to each location
        Once requests are prescribed, each location can present these results in the supply chain datatable
        At the end of the turn, request engine then executes all requests in a valid order
        Any player-assigned strategic preferences should be used as request engine parameters
        Note that each distinct item type would likely have its own supply chain graph - consider overlaps like
            warehouse space and transportation capacity that interact between item types
    """

    def __init__(self):
        """
        Initializes this object
        """
        self.location_plans: List[plans.supply_chain_plan] = []
        self.reset_location_plans()

    def reset_location_plans(self) -> None:
        for current_location in actor_utility.all_locations():
            current_location.supply_chain_plan = plans.supply_chain_plan(
                current_location
            )
            if not current_location.supply_chain_plan.trivial:
                self.location_plans.append(current_location.supply_chain_plan)

    # Prescribing requests WIP
