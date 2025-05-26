# Contains functionality for creating new games, saving, and loading

import random
import pickle
import pygame
from typing import Dict
from math import ceil
from modules.util import (
    game_transitions,
    turn_management_utility,
    text_utility,
    market_utility,
    minister_utility,
    actor_utility,
    tutorial_utility,
    scaling,
)
from modules.constructs import unit_types
from modules.constants import constants, status, flags


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

        self.copied_statuses = []
        self.copied_statuses.append("previous_production_report")
        self.copied_statuses.append("previous_sales_report")
        self.copied_statuses.append("previous_financial_report")
        self.copied_statuses.append("initial_tutorial_completed")
        self.copied_statuses.append("transaction_history")

        self.copied_flags = []
        self.copied_flags.append("prosecution_bribed_judge")
        self.copied_flags.append("victories_this_game")

    def generate_world_input_dict(self, world_type: str):
        return_dict = {}
        if world_type == "full_world":
            return_dict["init_type"] = constants.FULL_WORLD
            preset = None
            world_dimensions = None
            if constants.effect_manager.effect_active("earth_preset"):
                preset = "earth"
                world_dimensions = constants.earth_dimensions
            elif constants.effect_manager.effect_active("venus_preset"):
                preset = "venus"
                world_dimensions = constants.venus_dimensions
            elif constants.effect_manager.effect_active("mars_preset"):
                preset = "mars"
                world_dimensions = constants.mars_dimensions

            if preset:
                return_dict["name"] = preset.capitalize()
                return_dict["world_dimensions"] = world_dimensions
                return_dict["rotation_direction"] = (
                    constants.terrain_manager.get_tuning(f"{preset}_rotation_direction")
                )
                return_dict["rotation_speed"] = constants.terrain_manager.get_tuning(
                    f"{preset}_rotation_speed"
                )
                return_dict["global_parameters"] = {
                    constants.GRAVITY: constants.terrain_manager.get_tuning(
                        f"{preset}_gravity"
                    ),
                    constants.RADIATION: constants.terrain_manager.get_tuning(
                        f"{preset}_radiation"
                    ),
                    constants.MAGNETIC_FIELD: constants.terrain_manager.get_tuning(
                        f"{preset}_magnetic_field"
                    ),
                    constants.INERT_GASES: round(
                        constants.terrain_manager.get_tuning(f"{preset}_inert_gases")
                        * world_dimensions**2,
                        1,
                    ),
                    constants.OXYGEN: round(
                        constants.terrain_manager.get_tuning(f"{preset}_oxygen")
                        * world_dimensions**2,
                        1,
                    ),
                    constants.GHG: round(
                        constants.terrain_manager.get_tuning(f"{preset}_GHG")
                        * world_dimensions**2,
                        1,
                    ),
                    constants.TOXIC_GASES: round(
                        constants.terrain_manager.get_tuning(f"{preset}_toxic_gases")
                        * world_dimensions**2,
                        1,
                    ),
                }
                return_dict["average_water"] = constants.terrain_manager.get_tuning(
                    f"{preset}_average_water_target"
                )
                return_dict["sky_color"] = constants.terrain_manager.get_tuning(
                    f"{preset}_sky_color"
                )
                return_dict["star_distance"] = constants.terrain_manager.get_tuning(
                    f"{preset}_star_distance"
                )
            else:  # If creating random world
                return_dict["name"] = (
                    constants.flavor_text_manager.generate_flavor_text("planet_names")
                )
                return_dict["world_dimensions"] = random.choice(
                    constants.world_dimensions_options
                )
                ideal_atmosphere_size = (
                    return_dict["world_dimensions"] ** 2
                ) * 6  # Atmosphere units required for 1 atm pressure (like Earth) - 6 units per location
                return_dict["star_distance"] = round(random.uniform(0.5, 2.0), 3)

                return_dict["rotation_direction"] = random.choice([1, -1])
                return_dict["rotation_speed"] = random.choice([1, 2, 2, 3, 4, 5])
                return_dict["average_water_target"] = random.choice(
                    [
                        random.uniform(0.0, 5.0),
                        random.uniform(0.0, 1.0),
                        random.uniform(0.0, 4.0),
                    ]
                )
                return_dict["sky_color"] = [
                    random.randrange(0, 256) for _ in range(3)
                ]  # Random sky color

                global_parameters: Dict[str, float] = {}
                global_parameters[constants.GRAVITY] = round(
                    (
                        (return_dict["world_dimensions"] ** 2)
                        / (constants.earth_dimensions**2)
                    )
                    * random.uniform(0.7, 1.3),
                    2,
                )
                global_parameters[constants.RADIATION] = max(
                    random.randrange(0, 5), random.randrange(0, 5)
                )
                global_parameters[constants.MAGNETIC_FIELD] = random.choices(
                    [0, 1, 2, 3, 4, 5], [5, 2, 2, 2, 2, 2], k=1
                )[0]
                atmosphere_type = random.choice(
                    ["thick", "thick", "medium", "medium", "medium", "thin"]
                )
                if (
                    global_parameters[constants.MAGNETIC_FIELD]
                    >= global_parameters[constants.RADIATION]
                ):
                    if atmosphere_type in ["thin", "none"]:
                        atmosphere_type = "medium"
                elif (
                    global_parameters[constants.MAGNETIC_FIELD]
                    >= global_parameters[constants.RADIATION] - 2
                ):
                    if atmosphere_type == "none":
                        atmosphere_type = "thin"

                if atmosphere_type == "thick":
                    global_parameters[constants.GHG] = random.choices(
                        [
                            random.randrange(0, ideal_atmosphere_size * 90),
                            random.randrange(0, ideal_atmosphere_size * 10),
                            random.randrange(0, ideal_atmosphere_size * 5),
                            random.randrange(0, ideal_atmosphere_size),
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.1)),
                            0,
                        ],
                        [2, 4, 4, 4, 6, 6],
                        k=1,
                    )[0]
                    global_parameters[constants.OXYGEN] = random.choices(
                        [
                            random.randrange(0, ideal_atmosphere_size * 10),
                            random.randrange(0, ideal_atmosphere_size * 5),
                            random.randrange(0, ideal_atmosphere_size * 2),
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.5)),
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.01)),
                            0,
                        ],
                        [2, 4, 4, 4, 6, 6],
                        k=1,
                    )[0]
                    global_parameters[constants.INERT_GASES] = random.choices(
                        [
                            random.randrange(0, ideal_atmosphere_size * 90),
                            random.randrange(0, ideal_atmosphere_size * 10),
                            random.randrange(0, ideal_atmosphere_size * 5),
                            random.randrange(0, ideal_atmosphere_size),
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.1)),
                            0,
                        ],
                        [2, 4, 4, 4, 6, 6],
                        k=1,
                    )[
                        0
                    ]  # Same distribution as GHG
                    global_parameters[constants.TOXIC_GASES] = random.choices(
                        [
                            random.randrange(0, ideal_atmosphere_size * 10),
                            random.randrange(0, ideal_atmosphere_size * 5),
                            random.randrange(0, ideal_atmosphere_size * 2),
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.5)),
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.01)),
                            0,
                        ],
                        [2, 4, 4, 4, 6, 6],
                        k=1,
                    )[
                        0
                    ]  # Same distribution as oxygen
                elif atmosphere_type == "medium":
                    global_parameters[constants.GHG] = random.choices(
                        [
                            random.randrange(0, ideal_atmosphere_size),
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.5)),
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.3)),
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.1)),
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.01)),
                            0,
                        ],
                        [3, 3, 3, 3, 3, 3],
                        k=1,
                    )[0]
                    global_parameters[constants.OXYGEN] = random.choices(
                        [
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.6)),
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.3)),
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.15)),
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.05)),
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.01)),
                            0,
                        ],
                        [3, 3, 3, 3, 3, 3],
                        k=1,
                    )[0]
                    global_parameters[constants.INERT_GASES] = random.choices(
                        [
                            random.randrange(0, ideal_atmosphere_size),
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.5)),
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.3)),
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.1)),
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.01)),
                            0,
                        ],
                        [3, 3, 3, 3, 3, 3],
                        k=1,
                    )[
                        0
                    ]  # Same distribution as GHG
                    global_parameters[constants.TOXIC_GASES] = random.choices(
                        [
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.6)),
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.3)),
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.15)),
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.05)),
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.01)),
                            0,
                        ],
                        [3, 3, 3, 3, 3, 3],
                        k=1,
                    )[
                        0
                    ]  # Same distribution as oxygen
                elif atmosphere_type == "thin":
                    global_parameters[constants.GHG] = random.choices(
                        [
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.05)),
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.01)),
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.005)),
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.001)),
                            0,
                            0,
                        ],
                        [3, 3, 3, 3, 3, 3],
                        k=1,
                    )[0]
                    global_parameters[constants.OXYGEN] = random.choices(
                        [
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.01)),
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.005)),
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.001)),
                            0,
                            0,
                        ],
                        [3, 3, 3, 3, 3],
                        k=1,
                    )[0]
                    global_parameters[constants.INERT_GASES] = random.choices(
                        [
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.05)),
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.01)),
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.005)),
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.001)),
                            0,
                            0,
                        ],
                        [3, 3, 3, 3, 3, 3],
                        k=1,
                    )[
                        0
                    ]  # Same distribution as GHG
                    global_parameters[constants.TOXIC_GASES] = random.choices(
                        [
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.01)),
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.005)),
                            random.randrange(0, ceil(ideal_atmosphere_size * 0.001)),
                            0,
                            0,
                        ],
                        [3, 3, 3, 3, 3],
                        k=1,
                    )[
                        0
                    ]  # Same distribution as oxygen
                elif atmosphere_type == "none":
                    global_parameters[constants.GHG] = 0
                    global_parameters[constants.OXYGEN] = 0
                    global_parameters[constants.INERT_GASES] = 0
                    global_parameters[constants.TOXIC_GASES] = 0

                radiation_effect = (
                    global_parameters[constants.RADIATION]
                    - global_parameters[constants.MAGNETIC_FIELD]
                )
                if radiation_effect >= 3:
                    global_parameters[constants.INERT_GASES] = 0
                    global_parameters[constants.OXYGEN] = 0
                    global_parameters[constants.TOXIC_GASES] /= 2
                    global_parameters[constants.GHG] /= 2
                elif radiation_effect >= 1:
                    global_parameters[constants.INERT_GASES] /= 2
                    global_parameters[constants.OXYGEN] /= 2

                for component in constants.ATMOSPHERE_COMPONENTS:
                    if random.randrange(1, 7) >= 5:
                        global_parameters[component] = 0
                    global_parameters[component] += random.uniform(-10.0, 10.0)
                    global_parameters[component] = max(
                        0, round(global_parameters[component], 1)
                    )

                return_dict["global_parameters"] = global_parameters
        elif world_type == "earth_abstract_world":
            return_dict["init_type"] = constants.ABSTRACT_WORLD
            return_dict["abstract_world_type"] = constants.EARTH
            return_dict["name"] = "Earth"
            return_dict["world_dimensions"] = 1
            return_dict["rotation_direction"] = constants.terrain_manager.get_tuning(
                "earth_rotation_direction"
            )
            return_dict["rotation_speed"] = constants.terrain_manager.get_tuning(
                "earth_rotation_speed"
            )
            return_dict["global_parameters"] = {
                constants.GRAVITY: constants.terrain_manager.get_tuning(
                    "earth_gravity"
                ),
                constants.RADIATION: constants.terrain_manager.get_tuning(
                    "earth_radiation"
                ),
                constants.MAGNETIC_FIELD: constants.terrain_manager.get_tuning(
                    "earth_magnetic_field"
                ),
                constants.INERT_GASES: round(
                    constants.terrain_manager.get_tuning("earth_inert_gases")
                    * constants.earth_dimensions**2
                    * 6,
                    1,
                ),
                constants.OXYGEN: round(
                    constants.terrain_manager.get_tuning("earth_oxygen")
                    * constants.earth_dimensions**2
                    * 6,
                    1,
                ),
                constants.GHG: round(
                    constants.terrain_manager.get_tuning("earth_GHG")
                    * constants.earth_dimensions**2
                    * 6,
                    1,
                ),
                constants.TOXIC_GASES: round(
                    constants.terrain_manager.get_tuning("earth_toxic_gases")
                    * constants.earth_dimensions**2
                    * 6,
                    1,
                ),
            }
            return_dict["average_water"] = constants.terrain_manager.get_tuning(
                "earth_average_water_target"
            )
            return_dict["size"] = constants.earth_dimensions**2
            return_dict["sky_color"] = constants.terrain_manager.get_tuning(
                "earth_sky_color"
            )
            return_dict["star_distance"] = constants.terrain_manager.get_tuning(
                "earth_star_distance"
            )
            return_dict["albedo_multiplier"] = constants.terrain_manager.get_tuning(
                "earth_albedo_multiplier"
            )
            return_dict["cloud_frequency"] = constants.terrain_manager.get_tuning(
                "earth_cloud_frequency"
            )
        return return_dict

    def create_grids(self):
        status.scrolling_strategic_map_grid = (
            constants.actor_creation_manager.create_interface_element(
                input_dict={
                    "init_type": constants.MINI_GRID,
                    "world_handler": status.current_world,
                    "coordinates": scaling.scale_coordinates(
                        constants.strategic_map_x_offset,
                        constants.strategic_map_y_offset,
                    ),
                    "width": scaling.scale_width(constants.strategic_map_pixel_width),
                    "height": scaling.scale_height(
                        constants.strategic_map_pixel_height
                    ),
                    "modes": [constants.STRATEGIC_MODE],
                    "coordinate_size": status.current_world.world_dimensions,
                    "grid_line_width": 2,
                    "parent_collection": status.grids_collection,
                }
            )
        )

        status.minimap_grid = constants.strategic_map_grid = (
            constants.actor_creation_manager.create_interface_element(
                input_dict={
                    "init_type": constants.MINI_GRID,
                    "world_handler": status.current_world,
                    "coordinates": scaling.scale_coordinates(
                        constants.minimap_grid_x_offset,
                        -1 * (constants.minimap_grid_pixel_height + 25)
                        + constants.minimap_grid_y_offset,
                    ),
                    "width": scaling.scale_width(constants.minimap_grid_pixel_width),
                    "height": scaling.scale_height(constants.minimap_grid_pixel_height),
                    "modes": [constants.STRATEGIC_MODE],
                    "coordinate_size": constants.minimap_grid_coordinate_size,
                    "external_line_color": constants.COLOR_BRIGHT_RED,
                    "parent_collection": status.grids_collection,
                }
            )
        )

        globe_projection_grid = (
            constants.actor_creation_manager.create_interface_element(
                input_dict={
                    "init_type": constants.ABSTRACT_GRID,
                    "world_handler": status.current_world.orbital_world,
                    "coordinates": scaling.scale_coordinates(
                        constants.globe_projection_grid_x_offset,
                        constants.globe_projection_grid_y_offset,
                    ),
                    "width": scaling.scale_width(constants.globe_projection_grid_width),
                    "height": scaling.scale_height(
                        constants.globe_projection_grid_height
                    ),
                    "modes": [constants.STRATEGIC_MODE],
                    "parent_collection": status.grids_collection,
                }
            )
        )

        status.earth_grid = constants.actor_creation_manager.create_interface_element(
            input_dict={
                "init_type": constants.ABSTRACT_GRID,
                "world_handler": status.earth_world,
                "coordinates": scaling.scale_coordinates(
                    constants.earth_grid_x_offset,
                    constants.earth_grid_y_offset,
                ),
                "width": scaling.scale_width(constants.earth_grid_width),
                "height": scaling.scale_height(constants.earth_grid_height),
                "modes": [constants.STRATEGIC_MODE, constants.EARTH_MODE],
                "parent_collection": status.grids_collection,
            }
        )

        status.minimap_grid.calibrate(
            round(0.75 * status.current_world.world_dimensions),
            round(0.75 * status.current_world.world_dimensions),
        )

    def new_game(self):
        """
        Description:
            Creates a new game and leaves the main menu
        Input:
            None
        Output:
            None
        """
        game_transitions.start_loading()
        status.cached_images = {}
        flags.creating_new_game = True
        flags.victories_this_game = []

        game_transitions.set_game_mode(constants.STRATEGIC_MODE)

        status.current_world = constants.actor_creation_manager.create(
            from_save=False,
            input_dict=self.generate_world_input_dict("full_world"),
        )
        status.earth_world = constants.actor_creation_manager.create(
            from_save=False,
            input_dict=self.generate_world_input_dict("earth_abstract_world"),
        )

        self.create_grids()

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

        constants.actor_creation_manager.create_initial_ministers()

        constants.available_minister_left_index = -2

        for key, worker_type in status.worker_types.items():
            worker_type.reset()
        actor_utility.reset_action_prices()
        flags.prosecution_bribed_judge = False

        constants.money_tracker.reset_transaction_history()
        constants.money_tracker.set(constants.INITIAL_MONEY)
        constants.turn_tracker.set(0)
        constants.public_opinion_tracker.set(constants.INITIAL_PUBLIC_OPINION)
        constants.money_tracker.change(0)  # updates projected income display
        constants.evil_tracker.set(0)
        constants.fear_tracker.set(1)

        minister_utility.update_available_minister_display()

        turn_management_utility.start_player_turn(True)
        if not constants.effect_manager.effect_active("skip_intro"):
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
        Description:
            Saves the game in the file corresponding to the inputted file path
        Input:
            None
        Output:
            None
        """
        file_path = "save_games/" + file_path

        if constants.effect_manager.effect_active("save_global_projection"):
            pygame.image.save(
                status.globe_projection_surface.convert_alpha(),
                "save_games/globe_projection.png",
            )

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

        saved_full_world = status.current_world.to_save_dict()
        saved_earth_abstract_world = status.earth_world.to_save_dict()

        saved_unit_types = [
            unit_type.to_save_dict()
            for key, unit_type in status.unit_types.items()
            if unit_type.save_changes
        ]

        saved_item_types = [
            item_type.to_save_dict() for key, item_type in status.item_types.items()
        ]

        saved_actor_dicts = []
        for current_pmob in status.pmob_list:
            if not current_pmob.any_permissions(
                constants.IN_GROUP_PERMISSION,
                constants.IN_VEHICLE_PERMISSION,
                constants.IN_BUILDING_PERMISSION,
            ):  # Containers save their contents and load them in, contents don't need to be saved/loaded separately
                saved_actor_dicts.append(current_pmob.to_save_dict())

        for current_npmob in status.npmob_list:
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
                    f"{current_minister.name}, {current_minister.current_position.name}, skill modifier: {current_minister.get_skill_modifier()}, corruption threshold: {current_minister.corruption_threshold}, stolen money: {current_minister.stolen_money}, personal savings: {current_minister.personal_savings}"
                )

        with open(file_path, "wb") as handle:  # write wb, read rb
            pickle.dump(saved_constants, handle)
            pickle.dump(saved_statuses, handle)
            pickle.dump(saved_flags, handle)
            pickle.dump(saved_full_world, handle)
            pickle.dump(saved_earth_abstract_world, handle)
            pickle.dump(saved_unit_types, handle)
            pickle.dump(saved_actor_dicts, handle)
            pickle.dump(saved_minister_dicts, handle)
            pickle.dump(saved_item_types, handle)
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
                saved_full_world = pickle.load(handle)
                saved_earth_abstract_world = pickle.load(handle)
                saved_worker_types = pickle.load(handle)
                saved_actor_dicts = pickle.load(handle)
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
        constants.money_tracker.set(constants.money)
        constants.money_tracker.transaction_history = status.transaction_history
        constants.turn_tracker.set(constants.turn)
        constants.public_opinion_tracker.set(constants.public_opinion)
        constants.evil_tracker.set(constants.evil)
        constants.fear_tracker.set(constants.fear)

        text_utility.print_to_screen("")
        text_utility.print_to_screen("Turn " + str(constants.turn))

        # Load worlds
        status.current_world = constants.actor_creation_manager.create(
            True, saved_full_world
        )
        status.earth_world = constants.actor_creation_manager.create(
            True, saved_earth_abstract_world
        )

        self.create_grids()

        game_transitions.set_game_mode(constants.STRATEGIC_MODE)

        for current_worker_type in saved_worker_types:
            unit_types.worker_type(True, current_worker_type)

        # Load actors
        for current_minister_dict in saved_minister_dicts:
            constants.actor_creation_manager.create_minister(
                True, current_minister_dict
            )
        for current_actor_dict in saved_actor_dicts:
            constants.actor_creation_manager.create(True, current_actor_dict)

        for current_item_type_dict in saved_item_types:
            status.item_types[current_item_type_dict["key"]].apply_save_dict(
                current_item_type_dict
            )

        constants.available_minister_left_index = -2
        minister_utility.update_available_minister_display()
        status.item_prices_label.update_label()

        status.minimap_grid.calibrate(
            round(0.75 * status.current_world.world_dimensions),
            round(0.75 * status.current_world.world_dimensions),
        )
        actor_utility.calibrate_actor_info_display(status.mob_info_display, None)
        actor_utility.calibrate_actor_info_display(status.tile_info_display, None)
        (
            status.displayed_defense,
            status.displayed_minister,
            status.displayed_mob,
            status.displayed_tile_inventory,
            status.displayed_tile,
            status.displayed_mob_inventory,
        ) = [None] * 6
        game_transitions.set_game_mode(constants.STRATEGIC_MODE)

        tutorial_utility.show_tutorial_notifications()

        flags.loading_save = False
