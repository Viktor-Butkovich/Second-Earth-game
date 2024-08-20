# Contains functionality for worker type templates, such as European, religious workers

import random
from typing import Dict, List
import modules.constants.status as status
import modules.constants.constants as constants
import modules.util.market_utility as market_utility
import modules.util.text_utility as text_utility
import modules.util.actor_utility as actor_utility


class worker_type:
    """
    Worker template that tracks the current number, upkeep, and recruitment cost of a particular worker type
    """

    def __init__(self, from_save: bool, input_dict: Dict) -> None:
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'key': string value - Constant uniquely identifying this type of worker across the program
                'adjective': string value - Adjective describing this unit and its corresponding worker types entry
                'name': string value - Name of the corresponding unit, adjective + ' workers' by default
                'upkeep': float value - Cost of this unit each turn, default of 0.0
                'recruitment_cost': float value - Cost of recruiting this unit, default of 0.0
                'fired_description': string value - Description text to confirm firing of this unit
                'can_crew': list value - Types of vehicles this worker type can crew
                'upkeep_variance': bool value - Whether this worker type's upkeep can randomly fluctuate each turn
                'init_type': string value - Actor creation init type to use for this unit, default of 'workers'
        Output:
            None
        """
        if (
            from_save
        ):  # If from save, rather than creating full worker type template, just edit existing one
            copy_to: worker_type = status.worker_types[input_dict["key"]]
            copy_to.upkeep = input_dict["upkeep"]
            copy_to.set_recruitment_cost(input_dict["recruitment_cost"])
        else:
            self.permissions: List[str] = input_dict.get("permissions", [])
            self.key: str = input_dict["key"]
            self.adjective: str = input_dict["adjective"]
            self.name: str = input_dict.get("name", self.adjective + " workers")
            self.number: int = 0
            status.worker_types[input_dict["key"]] = self

            self.upkeep: float = input_dict.get("upkeep", 0.0)
            self.initial_upkeep: float = self.upkeep
            self.min_upkeep: float = min(0.5, self.initial_upkeep)

            self.recruitment_cost: float
            self.set_recruitment_cost(input_dict.get("recruitment_cost", 0.0))
            self.initial_recruitment_cost: float = self.recruitment_cost
            self.min_recruitment_cost: float = min(2.0, self.recruitment_cost)

            self.fired_description: str = input_dict.get("fired_description", "")

            self.can_crew: List[str] = input_dict.get("can_crew", [])

            self.upkeep_variance: bool = input_dict.get("upkeep_variance", False)

    def to_save_dict(self) -> Dict:
        """
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                'key': string value - Constant uniquely identifying this type of worker across the program
                'upkeep': float value - Cost of this unit each turn
                'recruitment_cost': float value - Cost of recruiting this unit
                'fired_description': string value - Description text to confirm firing of this unit
                'init_type': string value - Actor creation init type to use for this unit
        """
        return {
            "key": self.key,
            "upkeep": self.upkeep,
            "recruitment_cost": self.recruitment_cost,
        }

    def set_recruitment_cost(self, new_number: float) -> None:
        """
        Description:
            Sets this worker type's recruitment cost
        Input:
            float new_number: New recruitment cost
        Output:
            None
        """
        self.recruitment_cost = new_number
        constants.recruitment_costs[self.adjective + " workers"] = self.recruitment_cost

    def reset(self) -> None:
        """
        Description:
            Resets this worker type's values when a new game is created
        Input:
            None
        Output:
            None
        """
        self.number = 0
        self.upkeep = self.initial_upkeep
        self.set_recruitment_cost(self.initial_recruitment_cost)

    def get_total_upkeep(self) -> float:
        """
        Description:
            Calculates and returns the total upkeep of this worker type's units
        Input:
            None
        Output:
            float: Returns the total upkeep of this worker type's units
        """
        return self.number * self.upkeep

    def generate_input_dict(self) -> Dict:
        """
        Description:
            Generates an input dict to create a worker of this type
        Input:
            None
        Output:
            dictionary: Returns dictionary with standard entries for this worker type
        """
        input_dict = {
            "image": f"mobs/{self.key}/default.png",
            "name": self.name,
            "init_type": self.key,
            "worker_type": self,
        }
        return input_dict

    def on_recruit(self) -> None:
        """
        Description:
            Makes any updates required when worker first recruited (not on load)
        Input:
            None
        Output:
            None
        """
        if self.key != constants.CHURCH_VOLUNTEERS:
            market_utility.attempt_worker_upkeep_change("increase", self)

    def on_fire(self, wander=False):
        """
        Description:
            Makes any updates required when worker fired
        Input:
            boolean wander=False: Whether this worker will wander after being fired
        Output:
            None
        """
        if self.key != constants.CHURCH_VOLUNTEERS:
            market_utility.attempt_worker_upkeep_change("decrease", self)

        if self.adjective in ["European", "religious"]:
            current_public_opinion = constants.public_opinion
            constants.public_opinion_tracker.change(-1)
            resulting_public_opinion = constants.public_opinion
            if not current_public_opinion == resulting_public_opinion:
                text_utility.print_to_screen(
                    f"Firing {self.name} reflected poorly on your company and reduced your public opinion from {current_public_opinion} to {resulting_public_opinion}."
                )
