# Contains functionality for worker type templates, such as European, African, Asian, slave workers

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
            copy_to: worker_type = status.worker_types[input_dict["adjective"]]
            copy_to.upkeep = input_dict["upkeep"]
            copy_to.set_recruitment_cost(input_dict["recruitment_cost"])
        else:
            self.adjective: str = input_dict["adjective"]
            self.name: str = input_dict.get("name", self.adjective + " workers")
            self.number: int = 0
            status.worker_types[self.adjective] = self

            self.upkeep: float = input_dict.get("upkeep", 0.0)
            self.initial_upkeep: float = (
                self.upkeep
            )  # Make sure slave worker upkeep doesn't fluctuate
            self.min_upkeep: float = min(0.5, self.initial_upkeep)

            self.recruitment_cost: float
            self.set_recruitment_cost(input_dict.get("recruitment_cost", 0.0))
            self.initial_recruitment_cost: float = self.recruitment_cost
            self.min_recruitment_cost: float = min(2.0, self.recruitment_cost)

            self.fired_description: str = input_dict.get("fired_description", "")

            self.can_crew: List[str] = input_dict.get("can_crew", [])

            self.upkeep_variance: bool = input_dict.get("upkeep_variance", False)

            self.init_type: str = input_dict.get("init_type", "workers")

    def to_save_dict(self) -> Dict:
        """
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                'adjective': string value - Adjective describing this unit and its corresponding worker types entry
                'upkeep': float value - Cost of this unit each turn
                'recruitment_cost': float value - Cost of recruiting this unit
                'fired_description': string value - Description text to confirm firing of this unit
                'init_type': string value - Actor creation init type to use for this unit
        """
        return {
            "adjective": self.adjective,
            "upkeep": self.upkeep,
            "recruitment_cost": self.recruitment_cost,
            "init_type": self.init_type,
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
            "image": "mobs/" + self.name + "/default.png",
            "name": self.name,
            "init_type": self.init_type,
            "worker_type": self.adjective,
        }
        if (
            self.adjective == "Asian" and random.randrange(1, 7) >= 4
        ):  # Half chance each for East/South Asian variants
            input_dict["image"] = "mobs/" + self.name + " 1/default.png"
        return input_dict

    def on_recruit(self, purchased=True) -> None:
        """
        Description:
            Makes any updates required when worker first recruited (not on load)
        Input:
            boolean purchased=True: Whether this worker was purchased, only required for slave workers
        Output:
            None
        """
        if not self.adjective in ["religious", "slave"]:
            market_utility.attempt_worker_upkeep_change("increase", self.adjective)
            if self.adjective == "African":
                constants.achievement_manager.check_achievements("Minimum Wage")
        elif self.adjective == "slave":
            if purchased:  # as opposed to captured
                if not constants.effect_manager.effect_active("no_slave_trade_penalty"):
                    public_opinion_penalty = 5 + random.randrange(-3, 4)  # 2-8
                    current_public_opinion = constants.public_opinion_tracker.get()
                    constants.public_opinion_tracker.change(-1 * public_opinion_penalty)
                    resulting_public_opinion = constants.public_opinion_tracker.get()
                    if not resulting_public_opinion == current_public_opinion:
                        text_utility.print_to_screen(
                            "Participating in the slave trade has decreased your public opinion from "
                            + str(current_public_opinion)
                            + " to "
                            + str(resulting_public_opinion)
                            + "."
                        )
                else:
                    text_utility.print_to_screen(
                        "Your country's prolonged involvement with the slave trade prevented any public opinion penalty."
                    )
                market_utility.attempt_slave_recruitment_cost_change("increase")
                constants.evil_tracker.change(5)
                actor_utility.set_slave_traders_strength(
                    constants.slave_traders_strength + 1
                )
            else:
                public_opinion_penalty = 5 + random.randrange(-3, 4)  # 2-8
                current_public_opinion = constants.public_opinion_tracker.get()
                constants.public_opinion_tracker.change(-1 * public_opinion_penalty)
                resulting_public_opinion = constants.public_opinion_tracker.get()
                if not resulting_public_opinion == current_public_opinion:
                    text_utility.print_to_screen(
                        "Your use of captured slaves has decreased your public opinion from "
                        + str(current_public_opinion)
                        + " to "
                        + str(resulting_public_opinion)
                        + "."
                    )
                constants.evil_tracker.change(5)

    def on_fire(self, wander=False):
        """
        Description:
            Makes any updates required when worker fired
        Input:
            boolean wander=False: Whether this worker will wander after being fired
        Output:
            None
        """
        if not self.adjective in ["religious", "slave"]:
            market_utility.attempt_worker_upkeep_change("decrease", self.adjective)

        if self.adjective == "slave":
            constants.evil_tracker.change(-2)
            public_opinion_bonus = 4 + random.randrange(
                -3, 4
            )  # 1-7, less bonus than penalty for buying slaves on average
            current_public_opinion = constants.public_opinion_tracker.get()
            constants.public_opinion_tracker.change(public_opinion_bonus)
            resulting_public_opinion = constants.public_opinion_tracker.get()
            if not resulting_public_opinion == current_public_opinion:
                text_utility.print_to_screen(
                    "Freeing slaves has increased your public opinion from "
                    + str(current_public_opinion)
                    + " to "
                    + str(resulting_public_opinion)
                    + "."
                )

            if wander:
                text_utility.print_to_screen(
                    "These freed slaves will wander and eventually settle down in one of your slums."
                )
                constants.num_wandering_workers += 1
            status.worker_types["African"].on_fire(
                wander=wander
            )  # Also get effect of adding African worker to labor pool

        if self.adjective == "African" and wander:
            text_utility.print_to_screen(
                "These fired workers will wander and eventually settle down in one of your slums."
            )
            constants.num_wandering_workers += 1

        elif self.adjective in ["European", "religious"]:
            current_public_opinion = constants.public_opinion
            constants.public_opinion_tracker.change(-1)
            resulting_public_opinion = constants.public_opinion
            if not current_public_opinion == resulting_public_opinion:
                text_utility.print_to_screen(
                    "Firing "
                    + self.name
                    + " reflected poorly on your company and reduced your public opinion from "
                    + str(current_public_opinion)
                    + " to "
                    + str(resulting_public_opinion)
                    + "."
                )
