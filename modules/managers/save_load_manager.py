# Contains functionality for creating new games, saving, and loading

import random
import pickle
import pygame
from modules.util import (
    game_transitions,
    turn_management_utility,
    text_utility,
    market_utility,
    minister_utility,
    actor_utility,
    tutorial_utility,
    world_utility,
)
from modules.constructs import unit_types
from modules.constants import constants, status, flags


class save_load_manager:
    """
    Object that controls creating new games, saving, and loading
    """

    def __init__(self):
        """
        Initializes this object
        """
        self.copied_constants = []
        self.copied_statuses = []
        self.copied_flags = []
        self.set_copied_elements()

    def set_copied_elements(self):
        """
        Determines which variables should be saved and loaded
        """
        self.copied_constants = []
        self.copied_constants.append("action_prices")
        self.copied_constants.append("turn")
        self.copied_constants.append("public_opinion")
        self.copied_constants.append("money")
        self.copied_constants.append("evil")
        self.copied_constants.append("fear")

        self.copied_statuses = []
        self.copied_statuses.append("previous_production_report")
        self.copied_statuses.append("previous_sales_report")
        self.copied_statuses.append("previous_financial_report")
        self.copied_statuses.append("initial_tutorial_completed")
        self.copied_statuses.append("transaction_history")

        self.copied_flags = []
        self.copied_flags.append("prosecution_bribed_judge")
        self.copied_flags.append("victories_this_game")

    def new_game(self):
        """
        Creates a new game and leaves the main menu
        """
        game_transitions.start_loading()
        status.cached_images = {}
        flags.creating_new_game = True
        flags.victories_this_game = []

        game_transitions.set_game_mode(constants.STRATEGIC_MODE)

        world_utility.new_worlds()

        game_transitions.create_grids()

        status.current_world.simulate_temperature_equilibrium(5)
        # Since world's appearance can change albedo, we need to simulate temperature equilibrium after creating UI

        for current_item in status.item_types.values():
            if current_item.key == constants.CONSUMER_GOODS_ITEM:
                market_utility.set_price(
                    current_item, constants.consumer_goods_starting_price
                )
            else:
                market_utility.set_price(
                    current_item,
                    round((random.randrange(1, 7) + random.randrange(1, 7)) / 2),
                )  # 2-5

        for item_type in status.item_types.values():
            item_type.amount_produced_this_turn = 0
            item_type.amount_sold_this_turn = 0
            item_type.production_attempted_this_turn = False

        flags.player_turn = True
        status.previous_financial_report = None

        constants.ActorCreationManager.create_initial_ministers()

        constants.available_minister_left_index = -2

        for key, worker_type in status.worker_types.items():
            worker_type.reset()
        actor_utility.reset_action_prices()
        flags.prosecution_bribed_judge = False

        constants.MoneyTracker.reset_transaction_history()
        constants.MoneyTracker.set(constants.INITIAL_MONEY)
        constants.TurnTracker.set(0)
        constants.PublicOpinionTracker.set(constants.INITIAL_PUBLIC_OPINION)
        constants.MoneyTracker.change(0)  # updates projected income display
        constants.EvilTracker.set(0)
        constants.FearTracker.set(1)

        minister_utility.update_available_minister_display()

        turn_management_utility.start_player_turn(True)
        if not constants.EffectManager.effect_active("skip_intro"):
            status.initial_tutorial_completed = False
            game_transitions.set_game_mode(constants.MINISTERS_MODE)
            tutorial_utility.show_tutorial_notifications()
        else:
            status.initial_tutorial_completed = True
            for index, minister_type_tuple in enumerate(status.minister_types.items()):
                key, minister_type = minister_type_tuple
                status.minister_list[index].appoint(minister_type)
            minister_utility.calibrate_minister_info_display(None)
            game_transitions.set_game_mode(constants.STRATEGIC_MODE)
        flags.creating_new_game = False

    def save_game(self, file_path):
        """
        Saves the game in the file corresponding to the inputted file path
        """
        file_path = "save_games/" + file_path

        if constants.EffectManager.effect_active("save_global_projection"):
            pygame.image.save(
                status.globe_projection_surface.convert_alpha(),
                "save_games/globe_projection.png",
            )

        status.transaction_history = constants.MoneyTracker.transaction_history
        saved_constants = {}
        for current_element in self.copied_constants:
            saved_constants[current_element] = getattr(constants, current_element)

        saved_statuses = {}
        for current_element in self.copied_statuses:
            saved_statuses[current_element] = getattr(status, current_element)

        saved_flags = {}
        for current_element in self.copied_flags:
            saved_flags[current_element] = getattr(flags, current_element)

        saved_worlds = world_utility.save_worlds()

        saved_unit_types = [
            unit_type.to_save_dict()
            for key, unit_type in status.unit_types.items()
            if unit_type.save_changes
        ]

        saved_item_types = [
            item_type.to_save_dict() for key, item_type in status.item_types.items()
        ]

        saved_loan_dicts = [
            current_loan.to_save_dict() for current_loan in status.loan_list
        ]

        saved_minister_dicts = []
        for current_minister in status.minister_list:
            saved_minister_dicts.append(current_minister.to_save_dict())
            if constants.EffectManager.effect_active("show_corruption_on_save"):
                print(
                    f"{current_minister.name}, {current_minister.current_position.name}, skill modifier: {current_minister.get_skill_modifier()}, corruption threshold: {current_minister.corruption_threshold}, stolen money: {current_minister.stolen_money}, personal savings: {current_minister.personal_savings}"
                )

        with open(file_path, "wb") as handle:  # write wb, read rb
            pickle.dump(saved_constants, handle)
            pickle.dump(saved_statuses, handle)
            pickle.dump(saved_flags, handle)
            pickle.dump(saved_worlds, handle)
            pickle.dump(saved_unit_types, handle)
            pickle.dump(saved_loan_dicts, handle)
            pickle.dump(saved_minister_dicts, handle)
            pickle.dump(saved_item_types, handle)
            handle.close()
        text_utility.print_to_screen("Game successfully saved to " + file_path)

    def load_game(self, file_path):
        """
        Loads a saved game from the file corresponding to the inputted file path
        """
        flags.loading_save = True

        text_utility.print_to_screen("")
        text_utility.print_to_screen("Loading " + file_path)
        game_transitions.start_loading(
            previous_game_mode=constants.MAIN_MENU_MODE,
            new_game_mode=constants.STRATEGIC_MODE,
        )
        # Load file
        try:
            file_path = "save_games/" + file_path
            with open(file_path, "rb") as handle:
                saved_constants = pickle.load(handle)
                saved_statuses = pickle.load(handle)
                saved_flags = pickle.load(handle)
                saved_worlds = pickle.load(handle)
                saved_worker_types = pickle.load(handle)
                saved_loan_dicts = pickle.load(handle)
                saved_minister_dicts = pickle.load(handle)
                saved_item_types = pickle.load(handle)
                handle.close()
        except:
            text_utility.print_to_screen(f"There is no {file_path} save file yet.")
            return ()

        # Load variables
        for current_element in self.copied_constants:
            setattr(constants, current_element, saved_constants[current_element])
        for current_element in self.copied_statuses:
            setattr(status, current_element, saved_statuses[current_element])
        for current_element in self.copied_flags:
            setattr(flags, current_element, saved_flags[current_element])
        constants.MoneyTracker.set(constants.money)
        constants.MoneyTracker.transaction_history = status.transaction_history
        constants.MoneyTracker.set(constants.turn)
        constants.PublicOpinionTracker.set(constants.public_opinion)
        constants.EvilTracker.set(constants.evil)
        constants.FearTracker.set(constants.fear)

        text_utility.print_to_screen("")
        text_utility.print_to_screen("Turn " + str(constants.turn))

        world_utility.load_worlds(saved_worlds)
        # Note that loading in worlds loads locations, which loads settlements, mobs, and buildings

        game_transitions.create_grids()

        game_transitions.set_game_mode(constants.STRATEGIC_MODE)

        for current_worker_type in saved_worker_types:
            unit_types.worker_type(True, current_worker_type)

        # Load actors
        for current_minister_dict in saved_minister_dicts:
            constants.ActorCreationManager.create_minister(True, current_minister_dict)
        for current_loan_dict in saved_loan_dicts:
            constants.ActorCreationManager.create(True, current_loan_dict)

        for current_item_type_dict in saved_item_types:
            status.item_types[current_item_type_dict["key"]].apply_save_dict(
                current_item_type_dict
            )

        constants.available_minister_left_index = -2
        minister_utility.update_available_minister_display()
        status.item_prices_label.update_label()

        actor_utility.calibrate_minimap_grids(
            status.current_world,
            round(0.75 * status.current_world.world_dimensions),
            round(0.75 * status.current_world.world_dimensions),
        )
        actor_utility.calibrate_actor_info_display(status.mob_info_display, None)
        actor_utility.calibrate_actor_info_display(status.location_info_display, None)
        status.displayed_defense = None
        status.displayed_minister = None
        status.displayed_mob = None
        status.displayed_mob_inventory = None
        status.displayed_location_inventory = None
        status.displayed_location = None
        game_transitions.set_game_mode(constants.STRATEGIC_MODE)

        tutorial_utility.show_tutorial_notifications()

        flags.loading_save = False
