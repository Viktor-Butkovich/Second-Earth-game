# Contains functionality for creating new games, saving, and loading

import random
import pickle
from ...util import (
    scaling,
    game_transitions,
    turn_management_utility,
    text_utility,
    market_utility,
    minister_utility,
    actor_utility,
    tutorial_utility,
)
from ...interface_types import grids
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags
import modules.constructs.worker_types as worker_types


class save_load_manager_template:
    """
    Object that controls creating new games, saving, and loading
    """

    def __init__(self):
        """
        Description:
            Initializes this object
        Input:
            None
        Output:
            None
        """
        self.copied_constants = []
        self.copied_statuses = []
        self.copied_flags = []
        self.set_copied_elements()

    def set_copied_elements(self):
        """
        Description:
            Determines which variables should be saved and loaded
        Input:
            None
        Output:
            None
        """
        self.copied_constants = []
        self.copied_constants.append("action_prices")
        self.copied_constants.append("turn")
        self.copied_constants.append("public_opinion")
        self.copied_constants.append("money")
        self.copied_constants.append("evil")
        self.copied_constants.append("fear")
        self.copied_constants.append("sold_commodities")
        self.copied_constants.append("item_prices")
        self.copied_constants.append("recruitment_costs")
        self.copied_constants.append("num_wandering_workers")
        self.copied_constants.append("slave_traders_strength")
        self.copied_constants.append("slave_traders_natural_max_strength")
        self.copied_constants.append("completed_lore_mission_types")
        self.copied_constants.append("completed_lore_missions")

        self.copied_statuses = []
        self.copied_statuses.append("current_country_name")
        self.copied_statuses.append("previous_production_report")
        self.copied_statuses.append("previous_sales_report")
        self.copied_statuses.append("previous_financial_report")
        self.copied_statuses.append("minister_appointment_tutorial_completed")
        self.copied_statuses.append("exit_minister_screen_tutorial_completed")
        self.copied_statuses.append("transaction_history")

        self.copied_flags = []
        self.copied_flags.append("prosecution_bribed_judge")
        self.copied_flags.append("any_slaves")
        self.copied_flags.append("victories_this_game")

    def new_game(self, country):
        """
        Description:
            Creates a new game and leaves the main menu
        Input:
            country country: Country being played in the new game
        Output:
            None
        """
        flags.creating_new_game = True
        flags.any_slaves = False
        flags.victories_this_game = []
        country.select()

        for grid_type in constants.grid_types_list:
            grids.create(from_save=False, grid_type=grid_type)

        game_transitions.set_game_mode("strategic")
        game_transitions.create_strategic_map(from_save=False)
        status.minimap_grid.calibrate(2, 2)

        for current_commodity in constants.commodity_types:
            if current_commodity != "consumer goods":
                price = round((random.randrange(1, 7) + random.randrange(1, 7)) / 2)
                increase = 0
                if current_commodity == "gold":
                    increase = random.randrange(1, 7)
                elif current_commodity == "diamond":
                    increase = random.randrange(1, 7) + random.randrange(1, 7)
                price += increase
                market_utility.set_price(current_commodity, price)  # 2-5
            else:
                market_utility.set_price(
                    current_commodity, constants.consumer_goods_starting_price
                )

        constants.slave_traders_natural_max_strength = 10  # regenerates to natural strength, can increase indefinitely when slaves are purchased
        actor_utility.set_slave_traders_strength(
            constants.slave_traders_natural_max_strength
        )
        flags.player_turn = True
        status.previous_financial_report = None

        constants.actor_creation_manager.create_initial_ministers()

        constants.available_minister_left_index = -2

        for worker_type_name in status.worker_types:
            status.worker_types[worker_type_name].reset()
        constants.num_wandering_workers = 0
        actor_utility.reset_action_prices()
        for current_commodity in constants.commodity_types:
            constants.sold_commodities[current_commodity] = 0
        constants.attempted_commodities = []
        flags.prosecution_bribed_judge = False

        constants.money_tracker.reset_transaction_history()
        constants.money_tracker.set(500)
        constants.turn_tracker.set(0)
        constants.public_opinion_tracker.set(50)
        constants.money_tracker.change(0)  # updates projected income display
        constants.evil_tracker.set(0)
        constants.fear_tracker.set(1)

        for i in range(1, random.randrange(5, 8)):
            turn_management_utility.manage_villages(verbose=False)
            turn_management_utility.manage_warriors()
            actor_utility.spawn_beast()

        minister_utility.update_available_minister_display()

        turn_management_utility.start_player_turn(True)
        if not constants.effect_manager.effect_active("skip_intro"):
            status.minister_appointment_tutorial_completed = False
            status.exit_minister_screen_tutorial_completed = False
            game_transitions.set_game_mode("ministers")
            tutorial_utility.show_tutorial_notifications()
        else:
            status.minister_appointment_tutorial_completed = True
            status.exit_minister_screen_tutorial_completed = True
            for current_minister_position_index in range(len(constants.minister_types)):
                status.minister_list[current_minister_position_index].appoint(
                    constants.minister_types[current_minister_position_index]
                )
            game_transitions.set_game_mode("strategic")
        flags.creating_new_game = False

    def save_game(self, file_path):
        """
        Description:
            Saves the game in the file corresponding to the inputted file path
        Input:
            None
        Output:
            None
        """
        file_path = "save_games/" + file_path
        status.transaction_history = constants.money_tracker.transaction_history
        saved_constants = {}
        for current_element in self.copied_constants:
            saved_constants[current_element] = getattr(constants, current_element)

        saved_statuses = {}
        for current_element in self.copied_statuses:
            saved_statuses[current_element] = getattr(status, current_element)

        saved_flags = {}
        for current_element in self.copied_flags:
            saved_flags[current_element] = getattr(flags, current_element)

        saved_grid_dicts = []
        for current_grid in status.grid_list:
            if not current_grid.is_mini_grid:  # minimap grid doesn't need to be saved
                saved_grid_dicts.append(current_grid.to_save_dict())

        saved_worker_types = [
            status.worker_types[worker_type_name].to_save_dict()
            for worker_type_name in status.worker_types
        ]

        saved_actor_dicts = []
        for current_pmob in status.pmob_list:
            if not (
                current_pmob.in_group
                or current_pmob.in_vehicle
                or current_pmob.in_building
            ):  # containers save their contents and load them in, contents don't need to be saved/loaded separately
                saved_actor_dicts.append(current_pmob.to_save_dict())

        for current_npmob in status.npmob_list:
            if (
                current_npmob.saves_normally
            ):  # for units like native warriors that are saved as part a village and not as their own unit, do not attempt to save from here
                saved_actor_dicts.append(current_npmob.to_save_dict())

        for current_building in status.building_list:
            saved_actor_dicts.append(current_building.to_save_dict())

        for current_settlement in status.settlement_list:
            saved_actor_dicts.append(current_settlement.to_save_dict())

        for current_loan in status.loan_list:
            saved_actor_dicts.append(current_loan.to_save_dict())

        saved_minister_dicts = []
        for current_minister in status.minister_list:
            saved_minister_dicts.append(current_minister.to_save_dict())
            if constants.effect_manager.effect_active("show_corruption_on_save"):
                print(
                    current_minister.name
                    + ", "
                    + current_minister.current_position
                    + ", skill modifier: "
                    + str(current_minister.get_skill_modifier())
                    + ", corruption threshold: "
                    + str(current_minister.corruption_threshold)
                    + ", stolen money: "
                    + str(current_minister.stolen_money)
                    + ", personal savings: "
                    + str(current_minister.personal_savings)
                )

        saved_lore_mission_dicts = []
        for current_lore_mission in status.lore_mission_list:
            saved_lore_mission_dicts.append(current_lore_mission.to_save_dict())

        with open(file_path, "wb") as handle:  # write wb, read rb
            pickle.dump(saved_constants, handle)
            pickle.dump(saved_statuses, handle)
            pickle.dump(saved_flags, handle)
            pickle.dump(saved_grid_dicts, handle)
            pickle.dump(saved_worker_types, handle)
            pickle.dump(saved_actor_dicts, handle)
            pickle.dump(saved_minister_dicts, handle)
            pickle.dump(saved_lore_mission_dicts, handle)
            handle.close()
        text_utility.print_to_screen("Game successfully saved to " + file_path)

    def load_game(self, file_path):
        """
        Description:
            Loads a saved game from the file corresponding to the inputted file path
        Input:
            None
        Output:
            None
        """
        flags.loading_save = True

        text_utility.print_to_screen("")
        text_utility.print_to_screen("Loading " + file_path)
        game_transitions.start_loading()
        # Load file
        try:
            file_path = "save_games/" + file_path
            with open(file_path, "rb") as handle:
                saved_constants = pickle.load(handle)
                saved_statuses = pickle.load(handle)
                saved_flags = pickle.load(handle)
                saved_grid_dicts = pickle.load(handle)
                saved_worker_types = pickle.load(handle)
                saved_actor_dicts = pickle.load(handle)
                saved_minister_dicts = pickle.load(handle)
                saved_lore_mission_dicts = pickle.load(handle)
                handle.close()
        except:
            text_utility.print_to_screen("There is no " + file_path + " save file yet.")
            return ()

        # Load variables
        for current_element in self.copied_constants:
            setattr(constants, current_element, saved_constants[current_element])
        for current_element in self.copied_statuses:
            setattr(status, current_element, saved_statuses[current_element])
        for current_element in self.copied_flags:
            setattr(flags, current_element, saved_flags[current_element])
        constants.money_tracker.set(constants.money)
        constants.money_tracker.transaction_history = status.transaction_history
        constants.turn_tracker.set(constants.turn)
        constants.public_opinion_tracker.set(constants.public_opinion)
        constants.evil_tracker.set(constants.evil)
        constants.fear_tracker.set(constants.fear)

        getattr(
            status, status.current_country_name
        ).select()  # selects the country object with the same identifier as the saved country name

        text_utility.print_to_screen("")
        text_utility.print_to_screen("Turn " + str(constants.turn))

        # Load grids
        for current_grid_dict in saved_grid_dicts:
            grids.create(
                from_save=True,
                grid_type=current_grid_dict["grid_type"],
                input_dict=current_grid_dict,
            )
        grids.create(from_save=False, grid_type="minimap_grid")

        game_transitions.set_game_mode("strategic")
        game_transitions.create_strategic_map(from_save=True)
        if constants.effect_manager.effect_active("eradicate_slave_trade"):
            actor_utility.set_slave_traders_strength(0)
        else:
            actor_utility.set_slave_traders_strength(constants.slave_traders_strength)

        for current_worker_type in saved_worker_types:
            worker_types.worker_type(True, current_worker_type)

        # Load actors
        for current_actor_dict in saved_actor_dicts:
            constants.actor_creation_manager.create(True, current_actor_dict)
        for current_minister_dict in saved_minister_dicts:
            constants.actor_creation_manager.create_minister(
                True, current_minister_dict
            )
        for current_lore_mission_dict in saved_lore_mission_dicts:
            constants.actor_creation_manager.create_lore_mission(
                True, current_lore_mission_dict
            )
        constants.available_minister_left_index = -2
        minister_utility.update_available_minister_display()
        status.commodity_prices_label.update_label()

        status.minimap_grid.calibrate(2, 2)
        game_transitions.set_game_mode("strategic")

        for current_completed_lore_type in constants.completed_lore_mission_types:
            status.lore_types_effects_dict[current_completed_lore_type].apply()

        tutorial_utility.show_tutorial_notifications()

        flags.loading_save = False
