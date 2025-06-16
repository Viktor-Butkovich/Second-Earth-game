# Contains functions that manage what happens at the end of each turn, like worker upkeep and price changes

import random
import os
from typing import Dict
from modules.util import (
    text_utility,
    actor_utility,
    trial_utility,
    market_utility,
    utility,
    minister_utility,
    main_loop_utility,
)
from modules.constructs import item_types
from modules.constants import constants, status, flags


def end_turn():
    """
    Description:
        Ends the turn, completing any pending movements, removing any items that can't be stored, and doing resource production
    Input:
        None
    Output:
        None
    """
    actor_utility.calibrate_actor_info_display(status.location_info_display, None)
    actor_utility.calibrate_actor_info_display(status.mob_info_display, None)
    flags.player_turn = False
    status.player_turn_queue = []
    prepare_planet_rotation()
    start_enemy_turn()


def start_player_turn(first_turn=False):
    """
    Description:
        Starts the player's turn, resetting their units to maximum movement points, adjusting prices, paying upkeep, etc.
    Input:
        None
        first_turn = False: Whether this is the first turn - do not pay upkeep, etc. when the game first starts
    Output:
        None
    """
    (
        status.previous_production_report,
        status.previous_sales_report,
        status.previous_financial_report,
    ) = (None, None, None)
    status.logistics_incident_list = []
    for current_pmob in status.pmob_list:
        current_pmob.end_turn_move()  # Make sure no units that suffered attrition move when they shouldn't have
    manage_upkeep_expenditure()
    remove_excess_inventory()
    text_utility.print_to_screen("")
    text_utility.print_to_screen("Turn " + str(constants.turn + 1))
    if not first_turn:
        constants.notification_manager.set_lock(
            True
        )  # Don't attempt to show notifications until all processing completed
        main_loop_utility.update_display()
        for current_pmob in status.pmob_list:
            if current_pmob.get_permission(constants.VEHICLE_PERMISSION):
                current_pmob.reembark()
        for current_building in status.building_list:
            if current_building.building_type == constants.RESOURCE:
                current_building.reattach_work_crews()
        manage_missing_upkeep_penalties()
        manage_environmental_conditions()
        manage_attrition()  # Have attrition before or after enemy turn? Before upkeep?
        manage_logistics_report()
        manage_production()
        reset_mobs("pmobs")
        if not constants.effect_manager.effect_active("skip_start_of_turn"):
            manage_public_opinion()
            manage_loans()
            manage_worker_price_changes()
            manage_item_sales()
            manage_ministers()
            manage_subsidies()  # Note that subsidies are managed after public opinion changes
            manage_financial_report()
        actor_utility.reset_action_prices()
        game_end_check()
        status.current_world.update_clouds()
        status.current_world.simulate_temperature_equilibrium(5)
        status.current_world.update_sky_color(update_water=True)
        status.current_world.update_clouds()
        constants.notification_manager.set_lock(False)

    flags.player_turn = (
        True  # player_turn also set to True in main_loop when enemies done moving
    )
    flags.enemy_combat_phase = False
    constants.turn_tracker.change(1)

    if not first_turn:
        market_utility.adjust_prices()

    actor_utility.calibrate_minimap_grids(
        status.current_world,
        status.minimap_grid.center_x,
        status.minimap_grid.center_y,
    )
    actor_utility.calibrate_actor_info_display(
        status.location_info_display, status.displayed_location
    )
    actor_utility.calibrate_actor_info_display(
        status.mob_info_display, status.displayed_mob
    )
    constants.achievement_manager.check_achievements("start of turn")


def prepare_planet_rotation():
    """
    Description:
        Prepares constant values for planet rotation, starting from currently selected location
    Input:
        None
    Output:
        None
    """
    if constants.effect_manager.effect_active("save_global_projection"):
        folder_path = "save_games/globe_rotations"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
    center_coordinates = (
        status.scrolling_strategic_map_grid.center_x,
        status.scrolling_strategic_map_grid.center_y,
    )
    (
        center_index,
        latitude_lines,
    ) = status.current_world.get_latitude_line(center_coordinates)
    if latitude_lines == status.current_world.latitude_lines:
        constants.TIME_PASSING_EQUATORIAL_COORDINATES = (
            status.current_world.equatorial_coordinates
        )
    elif latitude_lines == status.current_world.alternate_latitude_lines:
        constants.TIME_PASSING_EQUATORIAL_COORDINATES = (
            status.current_world.alternate_equatorial_coordinates
        )
    constants.TIME_PASSING_EARTH_ROTATIONS = 0
    constants.TIME_PASSING_ROTATION = 0
    constants.TIME_PASSING_ITERATIONS = 0
    for index, coordinates in enumerate(latitude_lines[center_index]):
        if coordinates in constants.TIME_PASSING_EQUATORIAL_COORDINATES:
            constants.TIME_PASSING_INITIAL_ORIENTATION = (
                constants.TIME_PASSING_EQUATORIAL_COORDINATES.index(coordinates)
            )
            break

    if status.current_world.rotation_speed > 2:
        frame_interval = (
            3  # Long interval causes more visible choppiness on slower rotations
        )
    else:
        frame_interval = (
            2  # Short interval causes more visible distortion on faster rotations
        )
    planet_frames = len(constants.TIME_PASSING_EQUATORIAL_COORDINATES) // frame_interval
    earth_frames = len(os.listdir("graphics/locations/earth_rotations")) // 3
    rotation_seconds = 2.5 * 0.92  # Ends up taking more than allocated time
    total_timesteps = round(
        rotation_seconds / (constants.end_turn_wait_time)
    )  # 4 seconds of rotation with rotation_speed rotations for each planet
    # There should be sufficient timesteps for Earth to rotate earth_rotation_speed times
    # Each full rotation requires # transitions equal to # frames

    constants.TIME_PASSING_EARTH_SCHEDULE = [False] * total_timesteps
    num_earth_rotations = constants.terrain_manager.get_tuning("earth_rotation_speed")
    earth_step_interval = total_timesteps / (earth_frames * num_earth_rotations)
    for i in range(round(earth_frames * num_earth_rotations)):
        constants.TIME_PASSING_EARTH_SCHEDULE[round(i * earth_step_interval)] = True

    constants.TIME_PASSING_PLANET_SCHEDULE = [False] * total_timesteps
    num_planet_rotations = status.current_world.rotation_speed
    planet_step_interval = total_timesteps / (planet_frames * num_planet_rotations)
    for i in range(round(planet_frames * num_planet_rotations)):
        constants.TIME_PASSING_PLANET_SCHEDULE[round(i * planet_step_interval)] = True


def start_enemy_turn():
    """
    Description:
        Starts the ai's turn, resetting their units to maximum movement points, spawning warriors, etc.
    Input:
        first_turn = False: Whether this is the first turn - do not pay upkeep, etc. when the game first starts
    Output:
        None
    """
    reset_mobs("npmobs")
    # manage_combat() # Should probably do reset_mobs, manage_production, etc. after combat completed in a separate function
    # the manage_combat function starts the player turn


def reset_mobs(mob_type):
    """
    Description:
        Starts the turn for mobs of the inputed type, resetting their movement points and removing the disorganized status
    Input:
        string mob_type: Can be pmob or npmob, determines which mobs' turn starts
    Output:
        None
    """
    if mob_type == "pmobs":
        for current_pmob in status.pmob_list:
            current_pmob.reset_movement_points()
            if constants.ALLOW_DISORGANIZED:
                current_pmob.set_permission(constants.DISORGANIZED_PERMISSION, False)
    elif mob_type == "npmobs":
        for current_npmob in status.npmob_list:
            current_npmob.reset_movement_points()
            if constants.ALLOW_DISORGANIZED:
                current_npmob.set_permission(constants.DISORGANIZED_PERMISSION, False)
            # if not current_npmob.creation_turn == constants.turn: # If not created this turn
            current_npmob.turn_done = False
            status.enemy_turn_queue.append(current_npmob)
    else:
        for current_mob in status.mob_list:
            current_mob.reset_movement_points()
            if constants.ALLOW_DISORGANIZED:
                current_mob.set_permission(constants.DISORGANIZED_PERMISSION, False)


def manage_attrition():
    """
    Description:
        Checks each unit and item storage location to see if attrition occurs. Health attrition forces parts of units to die and need to be replaced, costing money, removing experience, and preventing them from acting in the next
            turn. Inventory attrition causes up to half of the items stored in a warehouse or carried by a unit to be lost. Both types of attrition are more common in bad terrain and less common in areas with more infrastructure
    Input:
        None
    Output:
        None
    """
    for current_pmob in status.pmob_list.copy():
        current_pmob.manage_health_attrition()
        if current_pmob.get_held_items():
            current_pmob.manage_inventory_attrition()

    for current_world in status.world_list:
        for current_location in current_world.get_flat_location_list():
            if current_location.get_held_items():
                current_location.manage_inventory_attrition()


def manage_logistics_report() -> None:
    """
    Description:
        Displays an attrition report at the end of the turn, showing reports of attrition at each location
    Input:
        Dict[str, item_types.item_type] expected_production: The expected production of each item type
    Output:
        None
    """
    transportation_minister = minister_utility.get_minister(
        constants.TRANSPORTATION_MINISTER
    )
    attrition_binned_by_location = {}
    for attrition_cause_dict in status.logistics_incident_list:
        location_string = str(attrition_cause_dict["location"])
        attrition_binned_by_location[location_string] = (
            attrition_binned_by_location.get(location_string, [])
            + [attrition_cause_dict]
        )
    for local_logistics_incident_list in attrition_binned_by_location.values():
        remaining_incidents = local_logistics_incident_list
        n = 5
        while remaining_incidents:
            first_n_incidents = remaining_incidents[:n]
            remaining_incidents = remaining_incidents[n:]
            # Recall that any dead unit can no longer check their location
            location = local_logistics_incident_list[0]["location"]
            if len(local_logistics_incident_list) == 1:
                text = f"{transportation_minister.current_position.name} {transportation_minister.name} reports a logistical incident "
            else:
                text = f"{transportation_minister.current_position.name} {transportation_minister.name} reports the following logistical incidents "

            if location.is_abstract_location:
                text += f"in orbit of {location.get_true_world_handler().name}: /n /n"
            elif location.name != "default":
                text += f"at {location.name}: /n /n"
            else:
                text += f"at ({location.x}, {location.y}): /n /n"

            for local_logistics_incident in first_n_incidents:
                text += f"{local_logistics_incident.get('explanation')} /n /n"

            if remaining_incidents:
                if len(remaining_incidents) == 1:
                    text += f"({len(remaining_incidents)} more incident on following pages) /n /n"
                else:
                    text += f"({len(remaining_incidents)} more incidents on following pages) /n /n"
            transportation_minister.display_message(
                text, override_input_dict={"zoom_destination": location}
            )


def remove_excess_inventory():
    """
    Description:
        Removes any items that exceed their location's storage capacities
    Input:
        None
    Output:
        None
    """
    for current_world in status.world_list:
        for current_location in current_world.get_flat_location_list():
            if current_location.inventory:
                current_location.remove_excess_inventory()


def manage_environmental_conditions():
    """
    Description:
        Kills any units in deadly environmental conditions
    Input:
        None
    Output:
        None
    """
    for current_pmob in status.pmob_list.copy():
        if current_pmob.in_deadly_environment():
            current_pmob.record_logistics_incident(
                incident_type=constants.UPKEEP_MISSING_PENALTY_DEATH,
                cause="environmental conditions",
            )
            current_pmob.die()


def manage_production():
    """
    Description:
        Orders each work crew in a production building to attempt item production and displays a production report of items for which production was attempted and how much of each was produced
    Input:
        None
    Output:
        None
    """
    expected_production = {}
    for current_item in status.item_types.values():
        current_item.amount_produced_this_turn = 0
        expected_production[current_item.key] = 0
    for current_resource_building in status.resource_building_list:
        if not current_resource_building.damaged:
            for current_work_crew in current_resource_building.contained_work_crews:
                if current_work_crew.movement_points >= 1:
                    if current_work_crew.get_permission(constants.VETERAN_PERMISSION):
                        expected_production[
                            current_resource_building.resource_type.key
                        ] += (
                            0.75
                            * current_resource_building.upgrade_fields[
                                constants.RESOURCE_EFFICIENCY
                            ]
                        )
                    else:
                        expected_production[
                            current_resource_building.resource_type.key
                        ] += (
                            0.5
                            * current_resource_building.upgrade_fields[
                                constants.RESOURCE_EFFICIENCY
                            ]
                        )
            current_resource_building.produce()
            current_resource_building.resource_type.production_attempted_this_turn = (
                True
            )
    manage_production_report(expected_production)


def manage_production_report(
    expected_production: Dict[str, item_types.item_type],
) -> None:
    """
    Description:
        Displays a production report at the end of the turn, showing expected and actual production for each item the company has the capacity to produce
    Input:
        Dict[str, item_types.item_type] expected_production: The expected production of each item type
    Output:
        None
    """
    industry_minister = minister_utility.get_minister(constants.INDUSTRY_MINISTER)
    attempted_item_types = [
        current_item_type
        for current_item_type in status.item_types.values()
        if current_item_type.production_attempted_this_turn
    ]
    if attempted_item_types:  # If any attempted, create production report
        text = f"{industry_minister.current_position.name} {industry_minister.name} reports the following resource production: /n /n"
        messages = []
        for current_item_type in status.item_types.values():
            if current_item_type.production_attempted_this_turn:
                expected_production = minister_utility.get_minister(
                    constants.SECURITY_MINISTER
                ).estimate_expected(expected_production[current_item_type.key])
                messages.append(
                    (
                        current_item_type.amount_produced_this_turn,
                        f"{current_item_type.name.capitalize()}: {current_item_type.amount_produced_this_turn} (expected {expected_production}) /n /n",
                    )
                )
        messages.sort(
            key=lambda x: x[0], reverse=True
        )  # Sort by amount produced in descending order
        for message in messages:
            text += message[1]
        status.previous_production_report = text
        industry_minister.display_message(text)


def manage_upkeep_expenditure() -> None:
    """
    Description:
        Pays upkeep for all units at the end of a turn. Currently, only workers cost upkeep
    Input:
        None
    Output:
        None
    """
    for current_world in status.world_list:
        for current_location in current_world.get_flat_location_list():
            if current_location.subscribed_mobs:
                item_upkeep = current_location.get_item_upkeep(recurse=True)
                item_request = current_location.create_item_request(item_upkeep)
                unfulfilled_item_request = current_location.fulfill_item_request(
                    item_request.copy()
                )
                if constants.effect_manager.effect_active("track_item_requests"):
                    if (
                        current_world.is_abstract_world
                        or current_location.name != "default"
                    ):
                        name = current_location.name.capitalize()
                    else:
                        name = f"({current_location.x}, {current_location.y})"
                    print(f"{name} total upkeep {item_upkeep}")
                    print(f"{name} requesting external {item_request}")
                    print(
                        f"{name} unfulfilled external requests {unfulfilled_item_request}"
                    )
                for current_mob in current_location.subscribed_mobs:
                    current_mob.check_item_availability()
                for current_mob in current_location.subscribed_mobs:
                    current_mob.consume_item_upkeep()
                current_location.set_inventory(
                    status.item_types[constants.ENERGY_ITEM], 0
                )

    total_money_upkeep = market_utility.calculate_total_worker_upkeep()
    constants.money_tracker.change(round(-1 * total_money_upkeep, 2), "worker_upkeep")


def manage_missing_upkeep_penalties() -> None:
    """
    Description:
        Resolves any penalties for missed upkeep
            Note that upkeep missing penalties are handled for all mobs, while upkeep expenditure is managed at a location grain with recursive calculations for sub-mobs
    Input:
        None
    Output:
        None
    """
    for current_pmob in status.pmob_list.copy():
        current_pmob.resolve_upkeep_missing_penalty()


def manage_loans():
    """
    Description:
        Pays interest on all current loans at the end of a turn
    Input:
        None
    Output:
        None
    """
    for current_loan in status.loan_list:
        current_loan.make_payment()


def manage_public_opinion():
    """
    Description:
        Changes public opinion at the end of the turn to move back toward 50
    Input:
        None
    Output:
        None
    """
    current_public_opinion = round(constants.public_opinion)
    if current_public_opinion < 50:
        constants.public_opinion_tracker.change(1)
        text_utility.print_to_screen(
            f"Trending toward a neutral attitude, public opinion toward your company increased from {current_public_opinion} to {current_public_opinion + 1}"
        )
    elif current_public_opinion > 50:
        constants.public_opinion_tracker.change(-1)
        text_utility.print_to_screen(
            f"Trending toward a neutral attitude, public opinion toward your company decreased from {current_public_opinion} to {current_public_opinion - 1}"
        )
    constants.evil_tracker.change(-2)
    if constants.effect_manager.effect_active("show_evil"):
        print("Evil number: " + str(constants.evil))
    if constants.effect_manager.effect_active("show_fear"):
        print("Fear number: " + str(constants.fear))


def manage_subsidies():
    """
    Description:
        Receives subsidies at the end of the turn based on public opinion
    Input:
        None
    Output:
        None
    """
    subsidies_received = market_utility.calculate_subsidies()
    text_utility.print_to_screen(
        "You received "
        + str(subsidies_received)
        + " money in subsidies from the government based on your public opinion and colonial efforts"
    )
    constants.money_tracker.change(subsidies_received, "subsidies")


def manage_financial_report():
    """
    Description:
        Displays a financial report at the end of the turn, showing revenue in each area, costs in each area, and total profit from the last turn
    Input:
        None
    Output:
        None
    """
    financial_report_text = constants.money_tracker.prepare_financial_report()
    constants.notification_manager.display_notification(
        {
            "message": financial_report_text,
        }
    )
    status.previous_financial_report = financial_report_text
    constants.money_tracker.reset_transaction_history()


def manage_worker_price_changes():
    """
    Description:
        Randomly changes the prices of colonist upkeep at the end of the turn, generally trending down to compensate for increases when recruited
    Input:
        None
    Output:
        None
    """
    for key, worker_type in status.worker_types.items():
        if worker_type.upkeep_variance:
            worker_roll = random.randrange(1, 7)
            if worker_roll >= 5:
                current_price = worker_type.upkeep
                changed_price = round(
                    current_price - constants.worker_upkeep_increment, 2
                )
                if changed_price >= worker_type.min_upkeep:
                    worker_type.upkeep = changed_price
                    text_utility.print_to_screen(
                        f"An influx of {worker_type.name} has decreased their upkeep from {current_price} to {changed_price}."
                    )
            elif worker_roll == 1:
                current_price = worker_type.upkeep
                changed_price = round(
                    current_price + constants.worker_upkeep_increment, 2
                )
                worker_type.upkeep = changed_price
                text_utility.print_to_screen(
                    f"A shortage of {worker_type.name} has increased their upkeep from {current_price} to {changed_price}."
                )


def manage_enemy_movement():
    """
    Description:
        Moves npmobs at the end of the turn towards player-controlled mobs/buildings
    Input:
        None
    Output:
        None
    """
    for current_npmob in status.npmob_list:
        if (
            not current_npmob.creation_turn == constants.turn
        ):  # if not created this turn
            current_npmob.end_turn_move()


def manage_combat():
    """
    Description:
        Resolves, in order, each possible combat that was triggered by npmobs moving into cells with pmobs. When a possible combat is resolved, it should call the next possible combat until all are resolved
    Input:
        None
    Output:
        None
    """
    if len(status.attacker_queue) > 0:
        status.attacker_queue.pop(0).attempt_local_combat()
    else:
        start_player_turn()


def manage_ministers():
    """
    Description:
        Controls minister retirement, new ministers appearing, and evidence loss over time
    Input:
        None
    Output:
        None
    """
    for current_minister in status.minister_list.copy():
        if current_minister.just_removed and not current_minister.current_position:
            current_minister.respond("fired")
            current_minister.remove()
    for current_minister in status.minister_list.copy():
        if constants.effect_manager.effect_active(
            "farm_upstate"
        ):  # Retire all ministers
            current_minister.respond("retirement")
            current_minister.appoint(None)
            current_minister.remove()
        elif (
            current_minister.current_position == None
            and random.randrange(1, 7) == 1
            and random.randrange(1, 7) <= 2
        ):  # 1/18 chance of switching out available ministers
            current_minister.respond("retirement")
            current_minister.remove()
        elif current_minister.current_position:
            if (
                random.randrange(1, 7) == 1
                and random.randrange(1, 7) <= 2
                and random.randrange(1, 7) <= 2
                and (
                    random.randrange(1, 7) <= 3
                    or constants.evil > random.randrange(0, 100)
                )
            ):
                current_minister.respond("retirement")
                current_minister.appoint(None)
                current_minister.remove()
            else:  # If remaining in office
                if (
                    random.randrange(1, 7) == 1 and random.randrange(1, 7) == 1
                ):  # Chance to gain experience
                    current_minister.gain_experience()
                current_minister.just_removed = False
                if current_minister.fabricated_evidence > 0:
                    prosecutor = minister_utility.get_minister(
                        constants.SECURITY_MINISTER
                    )
                    if prosecutor.check_corruption():
                        # Corruption is normally resolved during a trial, but prosecutor can still steal money from unused fabricated evidence if no trial occurs
                        prosecutor.steal_money(
                            trial_utility.get_fabricated_evidence_cost(
                                current_minister.fabricated_evidence, True
                            ),
                            "fabricated_evidence",
                        )
                    text_utility.print_to_screen(
                        f"The {current_minister.fabricated_evidence} fabricated evidence against {current_minister.name} is no longer usable."
                    )
                    current_minister.corruption_evidence -= (
                        current_minister.fabricated_evidence
                    )
                    current_minister.fabricated_evidence = 0

                    evidence_lost = sum(
                        [
                            int(
                                random.randrange(1, 7) == 1
                                and random.randrange(1, 7) == 1
                            )
                            for i in range(current_minister.corruption_evidence)
                        ]
                    )
                    if evidence_lost > 0:
                        if evidence_lost == current_minister.corruption_evidence:
                            current_minister.display_message(
                                f"All of the {current_minister.corruption_evidence} evidence of {current_minister.current_position.name} {current_minister.name}'s corruption has lost potency over time and will no longer be usable in trials against them. /n /n"
                            )
                        else:
                            current_minister.display_message(
                                f"{evidence_lost} of the {current_minister.corruption_evidence} evidence of {current_minister.current_position.name} {current_minister.name}'s corruption has lost potency over time and will no longer be usable in trials against them. /n /n"
                            )
                        current_minister.corruption_evidence -= evidence_lost

    if flags.prosecution_bribed_judge:
        text_utility.print_to_screen(
            "The effect of bribing the judge has faded and will not affect the next trial."
        )
    flags.prosecution_bribed_judge = False

    if (
        len(status.minister_list) <= constants.minister_limit - 2
        and random.randrange(1, 7) >= 4
    ) or len(
        status.minister_list
    ) <= 10:  # Chance if at least 2 missing or guaranteed if not enough to fill cabinet
        while len(status.minister_list) < constants.minister_limit:
            constants.actor_creation_manager.create_minister(False, {})
        constants.notification_manager.display_notification(
            {
                "message": "Several new minister candidates are available for appointment and can be found in the candidate pool. /n /n",
            }
        )
    if random.randrange(1, 7) == 1 and random.randrange(1, 7) <= 3:
        constants.fear_tracker.change(-1)
    manage_minister_rumors()


def manage_minister_rumors():
    """
    Description:
        Passively checks for rumors on each minister each turn
    Input:
        None
    Output:
        None
    """
    for current_minister in status.minister_list:
        if random.randrange(1, 7) == 1 and random.randrange(1, 7) == 1:
            current_minister.attempt_rumor("loyalty", None)
        for key, minister_type in status.minister_types.items():
            if (
                current_minister.current_position
                and minister_type.skill_type
                == current_minister.current_position.skill_type
            ):
                if random.randrange(1, 7) == 1 and random.randrange(1, 7) == 1:
                    current_minister.attempt_rumor(minister_type.skill_type, None)
            elif (
                random.randrange(1, 7) == 1
                and random.randrange(1, 7) == 1
                and random.randrange(1, 7) == 1
            ):
                current_minister.attempt_rumor(minister_type.skill_type, None)
        # 1/36 of getting loyalty report
        # If currently employed, 1/36 of getting report on working skill
        # If currently employed, 1/216 of getting report on each non-working skill
        # If not employed, 1/216 of getting report on each skill


def game_end_check():
    """
    Description:
        Checks each turn if the company is below 0 money, causing the player to lose the game
    Input:
        None
    Output:
        None
    """
    if constants.money < 0:
        text = ""
        text += "Your company does not have enough money to pay its expenses and has gone bankrupt. /n /nGAME OVER"
        constants.achievement_manager.achieve("I DECLARE BANKRUPTCY!")
        constants.notification_manager.display_notification(
            {
                "message": text,
                "choices": [
                    constants.CHOICE_CONFIRM_MAIN_MENU_BUTTON,
                    constants.CHOIEC_QUIT_BUTTON,
                ],
            }
        )


def manage_item_sales():
    """
    Description:
        Orders the minister of trade to process all item sales started in the player's turn, allowing the minister to use skill/corruption to modify how much money is received by the company
    Input:
        None
    Output:
        None
    """
    trade_minister = minister_utility.get_minister(constants.TERRAN_AFFAIRS_MINISTER)
    money_stolen = 0
    reported_revenue = 0
    text = f"{trade_minister.current_position.name} {trade_minister.name} reports the following item sales: /n /n"
    any_sold = False
    for item_type in status.item_types.values():
        if item_type.amount_sold_this_turn > 0:
            any_sold = True
            expected_revenue = minister_utility.get_minister(
                constants.SECURITY_MINISTER
            ).estimate_expected(
                item_type.amount_sold_this_turn * item_type.price, False
            )
            actual_revenue = 0
            for i in range(item_type.amount_sold_this_turn):
                individual_price = (
                    item_type.price
                    + random.randrange(-1, 2)
                    + trade_minister.get_roll_modifier()
                )
                if (
                    trade_minister.check_corruption() and individual_price > 1
                ):  # Minister might steal from each sale, but prosecutor only detects at the end
                    money_stolen += 1
                    individual_price -= 1
                if individual_price < 1:
                    individual_price = 1
                reported_revenue += individual_price
                actual_revenue += individual_price
                if random.randrange(1, 7) <= 1:  # 1/6 chance
                    market_utility.change_price(item_type, -1)
            text += f"{item_type.amount_sold_this_turn} {item_type.name} sold for {actual_revenue} money (expected {expected_revenue}) /n /n"
            item_type.amount_sold_this_turn = 0

    constants.money_tracker.change(reported_revenue, "sold_items")

    if any_sold:
        trade_minister.display_message(text)
        status.previous_sales_report = text
    if money_stolen > 0:
        trade_minister.steal_money(money_stolen, "sold_items")


def end_turn_warnings():
    """
    Description:
        Displays any warnings for player to see before ending turn - can cancel end turn based on any of these
    Input:
        None
    Output:
        None
    """
    for current_minister in status.minister_list:  # Warn for firing minister
        if current_minister.just_removed and not current_minister.current_position:
            current_minister.display_message(
                f"Warning: if you do not reappoint {current_minister.name} by the end of the turn, they will be considered fired, leaving the candidate pool and incurring a large public opinion penalty. /n /n"
            )

    for current_world in status.world_list:  # Warn for insufficient warehouses
        for current_location in current_world.get_flat_location_list():
            if current_location.insufficient_inventory_capacity:
                if current_world.is_abstract_world:
                    constants.notification_manager.display_notification(
                        {
                            "message": f"Warning: the warehouses in {current_location.name} are not sufficient to hold the items stored there. /n /nAny items exceeding the location's storage capacity will be lost at the end of the turn. /n /n",
                            "zoom_destination": current_location,
                        }
                    )
                else:
                    constants.notification_manager.display_notification(
                        {
                            "message": f"Warning: the warehouses at {current_location.x}, {current_location.y} are not sufficient to hold the items stored there. /n /nAny items exceeding the location's storage capacity will be lost at the end of the turn. /n /n",
                            "zoom_destination": current_location,
                        }
                    )

    for current_world in status.world_list:
        if (
            current_world.is_abstract_world and not current_world.is_earth
        ):  # Warn for leaving units behind in non-Earth grids
            current_location = current_world.find_location(0, 0)
            num_leaving = 0
            num_reserve = 0
            # Number of vehicles leaving and number of vehicles staying behind, respectively
            for current_mob in current_location.subscribed_mobs:
                if current_mob.end_turn_destination and current_mob.get_permission(
                    constants.VEHICLE_PERMISSION
                ):
                    num_leaving += 1
                elif current_mob.all_permissions(
                    constants.VEHICLE_PERMISSION, constants.ACTIVE_PERMISSION
                ):
                    num_reserve += 1
            num_stranded = len(current_location.subscribed_mobs) - (
                num_leaving + num_reserve
            )  # Number of non-vehicles left behind
            if (
                num_leaving > 0 and num_stranded > 0 and num_reserve == 0
            ):  # If at least 1 vehicle leaving grid and at least 1 unit left behind, give warning
                text += f"Warning: at least 1 unit is being left behind in {current_world.name} and will not be able to leave without another spaceship. /n /n"
                constants.notification_manager.display_notification(
                    {"message": text, "zoom_destination": current_location}
                )

    for minister in status.minister_list:
        if minister.fabricated_evidence > 0:
            text = f"WARNING: Your {minister.fabricated_evidence} piece{utility.generate_plural(minister.fabricated_evidence)} of fabricated evidence against {minister.current_position.name} {minister.name} will disappear at the end of the turn if left unused. /n /n"
            constants.notification_manager.display_notification(
                {
                    "message": text,
                }
            )

    if flags.prosecution_bribed_judge:
        text = "WARNING: The effect of bribing the judge will disappear at the end of the turn if left unused. /n /n"
        constants.notification_manager.display_notification(
            {
                "message": text,
            }
        )

    for pmob in status.pmob_list:
        if (not pmob.get_permission(constants.SURVIVABLE_PERMISSION)) and (
            not pmob.get_permission(constants.IN_GROUP_PERMISSION)
        ):
            text = "WARNING: At least 1 unit is in deadly environmental conditions and will die at the end of the turn. /n /n"
            constants.notification_manager.display_notification(
                {
                    "message": text,
                    "zoom_destination": pmob,
                }
            )
            break

    for current_world in status.world_list:
        for current_location in current_world.get_flat_location_list():
            if current_location.subscribed_mobs:
                item_upkeep = current_location.get_item_upkeep(recurse=True)
                item_request = current_location.create_item_request(item_upkeep)
                if constants.ENERGY_ITEM in item_request:
                    missing_fuel = current_location.create_item_request(
                        {constants.FUEL_ITEM: item_request[constants.ENERGY_ITEM]}
                    ).get(constants.FUEL_ITEM, 0)
                    if missing_fuel == 0:
                        del item_request[constants.ENERGY_ITEM]
                    else:
                        item_request[constants.ENERGY_ITEM] = missing_fuel
                if (
                    item_request
                ):  # For each current_location that cannot meet its upkeep requirements, issue a warning
                    if (
                        current_world.is_abstract_world
                        or current_location.name != "default"
                    ):
                        name = current_location.name.capitalize()
                    else:
                        name = f"({current_location.x}, {current_location.y})"
                    text = f"WARNING: {name} does not have enough items to meet its local upkeep requirements. /n /n"
                    text += f"Required items: {actor_utility.summarize_amount_dict(item_upkeep)} /n /n"
                    text += f"Missing items: {actor_utility.summarize_amount_dict(item_request)} /n /n"
                    text += f"Depending on item type, this deficit may result in unit death or morale penalties. /n /n"
                    constants.notification_manager.display_notification(
                        {
                            "message": text,
                            "zoom_destination": current_location,
                        }
                    )
