# Contains functions that manage what happens at the end of each turn, like worker upkeep and price changes

import random
from . import (
    text_utility,
    actor_utility,
    trial_utility,
    market_utility,
    utility,
    game_transitions,
)
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags


def end_turn():
    """
    Description:
        Ends the turn, completing any pending movements, removing any commodities that can't be stored, and doing resource production
    Input:
        None
    Output:
        None
    """
    remove_excess_inventory()
    for current_pmob in status.pmob_list:
        current_pmob.end_turn_move()
    flags.player_turn = False
    status.player_turn_queue = []
    start_enemy_turn()


def start_enemy_turn():
    """
    Description:
        Starts the ai's turn, resetting their units to maximum movement points, spawning warriors, etc.
    Input:
        first_turn = False: Whether this is the first turn - do not pay upkeep, etc. when the game first starts
    Output:
        None
    """
    manage_warriors()
    manage_beasts()
    reset_mobs("npmobs")
    # manage_combat() #should probably do reset_mobs, manage_production, etc. after combat completed in a separate function
    # the manage_combat function starts the player turn


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
    text_utility.print_to_screen("")
    text_utility.print_to_screen("Turn " + str(constants.turn + 1))
    if not first_turn:
        for current_pmob in status.pmob_list:
            if current_pmob.is_vehicle:
                current_pmob.reembark()
        for current_building in status.building_list:
            if current_building.building_type == "resource":
                current_building.reattach_work_crews()
        manage_attrition()  # have attrition before or after enemy turn? Before upkeep?
        manage_production()
        reset_mobs("pmobs")
        manage_villages()
        manage_public_opinion()
        manage_upkeep()
        manage_loans()
        manage_slave_traders()
        manage_worker_price_changes()
        manage_worker_migration()
        manage_commodity_sales()
        manage_ministers()
        manage_subsidies()  # subsidies given after public opinion changes
        manage_financial_report()
        manage_lore()
        actor_utility.reset_action_prices()
        game_end_check()

    flags.player_turn = (
        True  # player_turn also set to True in main_loop when enemies done moving
    )
    flags.enemy_combat_phase = False
    constants.turn_tracker.change(1)

    if not first_turn:
        market_utility.adjust_prices()

    if status.displayed_mob == None or status.displayed_mob.is_npmob:
        game_transitions.cycle_player_turn(True)

    if status.displayed_mob:
        status.displayed_mob.select()
    else:
        actor_utility.calibrate_actor_info_display(
            status.mob_info_display, None, override_exempt=True
        )
    constants.achievement_manager.check_achievements("start of turn")


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
            current_pmob.set_disorganized(False)
    elif mob_type == "npmobs":
        for current_npmob in status.npmob_list:
            current_npmob.reset_movement_points()
            current_npmob.set_disorganized(False)
            # if not current_npmob.creation_turn == constants.turn: #if not created this turn
            current_npmob.turn_done = False
            status.enemy_turn_queue.append(current_npmob)
    else:
        for current_mob in status.mob_list:
            current_mob.reset_movement_points()
            current_mob.set_disorganized(False)


def manage_attrition():
    """
    Description:
        Checks each unit and commodity storage location to see if attrition occurs. Health attrition forces parts of units to die and need to be replaced, costing money, removing experience, and preventing them from acting in the next
            turn. Commodity attrition causes up to half of the commodities stored in a warehouse or carried by a unit to be lost. Both types of attrition are more common in bad terrain and less common in areas with more infrastructure
    Input:
        None
    Output:
        None
    """
    for current_pmob in status.pmob_list:
        if not (
            current_pmob.in_vehicle or current_pmob.in_group or current_pmob.in_building
        ):  # vehicles, groups, and buildings handle attrition for their submobs
            current_pmob.manage_health_attrition()
    for current_building in status.building_list:
        if current_building.building_type == "resource":
            current_building.manage_health_attrition()

    for current_pmob in status.pmob_list:
        current_pmob.manage_inventory_attrition()

    terrain_cell_lists = [status.strategic_map_grid.get_flat_cell_list()]
    for current_grid in status.grid_list:
        if current_grid.grid_type in constants.abstract_grid_type_list:
            terrain_cell_lists.append([current_grid.cell_list[0][0]])
    for cell_list in terrain_cell_lists:
        for current_cell in cell_list:
            current_tile = current_cell.tile
            if len(current_tile.get_held_commodities()) > 0:
                current_tile.manage_inventory_attrition()


def remove_excess_inventory():
    """
    Description:
        Removes any commodities that exceed their tile's storage capacities
    Input:
        None
    Output:
        None
    """
    terrain_cell_lists = [status.strategic_map_grid.get_flat_cell_list()]
    for current_grid in status.grid_list:
        if current_grid.grid_type in constants.abstract_grid_type_list:
            terrain_cell_lists.append([current_grid.cell_list[0][0]])
    for cell_list in terrain_cell_lists:
        for current_cell in cell_list:
            current_tile = current_cell.tile
            if current_tile.inventory:
                current_tile.remove_excess_inventory()


def manage_production():
    """
    Description:
        Orders each work crew in a production building to attempt commodity production and displays a production report of commodities for which production was attempted and how much of each was produced
    Input:
        None
    Output:
        None
    """
    expected_production = {}
    for current_commodity in constants.collectable_resources:
        constants.commodities_produced[current_commodity] = 0
        expected_production[current_commodity] = 0
    for current_resource_building in status.resource_building_list:
        if not current_resource_building.damaged:
            for current_work_crew in current_resource_building.contained_work_crews:
                if current_work_crew.movement_points >= 1:
                    if current_work_crew.veteran:
                        expected_production[
                            current_resource_building.resource_type
                        ] += (0.75 * current_resource_building.efficiency)
                    else:
                        expected_production[
                            current_resource_building.resource_type
                        ] += (0.5 * current_resource_building.efficiency)
            current_resource_building.produce()
            if (
                not current_resource_building.resource_type
                in constants.attempted_commodities
            ):
                constants.attempted_commodities.append(
                    current_resource_building.resource_type
                )
    manage_production_report(expected_production)


def manage_production_report(expected_production):
    """
    Description:
        Displays a production report at the end of the turn, showing expected and actual production for each commodity the company has the capacity to produce
    """
    attempted_commodities = constants.attempted_commodities
    displayed_commodities = []
    production_minister = status.current_ministers[
        constants.type_minister_dict["production"]
    ]
    if (
        not len(constants.attempted_commodities) == 0
    ):  # if any attempted, do production report
        text = (
            production_minister.current_position
            + " "
            + production_minister.name
            + " reports the following commodity production: /n /n"
        )
        while len(displayed_commodities) < len(attempted_commodities):
            max_produced = 0
            max_commodity = "none"
            for current_commodity in attempted_commodities:
                if not current_commodity in displayed_commodities:
                    if (
                        constants.commodities_produced[current_commodity]
                        >= max_produced
                    ):
                        max_commodity = current_commodity
                        max_produced = constants.commodities_produced[current_commodity]
                        expected_production[max_commodity] = status.current_ministers[
                            "Prosecutor"
                        ].estimate_expected(expected_production[max_commodity])
            displayed_commodities.append(max_commodity)
            text += (
                max_commodity.capitalize()
                + ": "
                + str(max_produced)
                + " (expected "
                + str(expected_production[max_commodity])
                + ") /n /n"
            )
        status.previous_production_report = text
        production_minister.display_message(text)


def manage_upkeep():
    """
    Description:
        Pays upkeep for all units at the end of a turn. Currently, only workers cost upkeep
    Input:
        None
    Output:
        None
    """
    total_upkeep = market_utility.calculate_total_worker_upkeep()
    constants.money_tracker.change(round(-1 * total_upkeep, 2), "worker_upkeep")


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


def manage_slave_traders():
    """
    Description:
        Regenerates the strength of slave traders up to the natural maximum over time
    Input:
        None
    Output:
        None
    """
    if (
        constants.slave_traders_strength < constants.slave_traders_natural_max_strength
        and constants.slave_traders_strength > 0
    ):
        # if below natural max but not eradicated
        actor_utility.set_slave_traders_strength(constants.slave_traders_strength + 1)


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
            "Trending toward a neutral attitude, public opinion toward your company increased from "
            + str(current_public_opinion)
            + " to "
            + str(current_public_opinion + 1)
        )
    elif current_public_opinion > 50:
        constants.public_opinion_tracker.change(-1)
        text_utility.print_to_screen(
            "Trending toward a neutral attitude, public opinion toward your company decreased from "
            + str(current_public_opinion)
            + " to "
            + str(current_public_opinion - 1)
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
        Randomly changes the prices of slave purchase and European worker upkeep at the end of the turn, generally trending down to compensate for increases when recruited
    Input:
        None
    Output:
        None
    """
    for worker_type in status.worker_types:
        if status.worker_types[worker_type].upkeep_variance:
            worker_roll = random.randrange(1, 7)
            if worker_roll >= 5:
                current_price = status.worker_types[worker_type].upkeep
                changed_price = round(
                    current_price - constants.worker_upkeep_increment, 2
                )
                if changed_price >= status.worker_types[worker_type].min_upkeep:
                    status.worker_types[worker_type].upkeep = changed_price
                    text_utility.print_to_screen(
                        "An influx of "
                        + worker_type
                        + " workers has decreased their upkeep from "
                        + str(current_price)
                        + " to "
                        + str(changed_price)
                        + "."
                    )
            elif worker_roll == 1:
                current_price = status.worker_types[worker_type].upkeep
                changed_price = round(
                    current_price + constants.worker_upkeep_increment, 2
                )
                status.worker_types[worker_type].upkeep = changed_price
                text_utility.print_to_screen(
                    "A shortage of "
                    + worker_type
                    + " workers has increased their upkeep from "
                    + str(current_price)
                    + " to "
                    + str(changed_price)
                    + "."
                )

    if constants.slave_traders_strength > 0:
        worker_roll = random.randrange(1, 7)
        if worker_roll == 6:
            current_price = status.worker_types["slave"].recruitment_cost
            changed_price = round(
                current_price - constants.slave_recruitment_cost_increment, 2
            )
            if changed_price >= status.worker_types["slave"].min_recruitment_cost:
                status.worker_types["slave"].set_recruitment_cost(changed_price)
                text_utility.print_to_screen(
                    "An influx of captured slaves has decreased the purchase cost of slave workers from "
                    + str(current_price)
                    + " to "
                    + str(changed_price)
                    + "."
                )
        elif worker_roll == 1:
            current_price = status.worker_types["slave"].recruitment_cost
            changed_price = round(
                current_price + constants.slave_recruitment_cost_increment, 2
            )
            status.worker_types["slave"].set_recruitment_cost(changed_price)
            text_utility.print_to_screen(
                "A shortage of captured slaves has increased the purchase cost of slave workers from "
                + str(current_price)
                + " to "
                + str(changed_price)
                + "."
            )


def manage_worker_migration():
    """
    Description:
        Checks if a workerm migration event occurs and resolves it if it does occur
    Input:
        None
    Output:
        None
    """
    num_village_workers = (
        actor_utility.get_num_available_workers("village")
        + constants.num_wandering_workers
    )
    num_slums_workers = actor_utility.get_num_available_workers("slums")
    if (
        num_village_workers > num_slums_workers and random.randrange(1, 7) >= 5
    ):  # 1/3 chance of activating
        trigger_worker_migration()

    for current_slums in status.slums_list:
        population_increase = 0
        for current_worker in range(current_slums.available_workers):
            if (
                random.randrange(1, 7) == 1
                and random.randrange(1, 7) == 1
                and random.randrange(1, 7) == 1
            ):
                population_increase += 1
                market_utility.attempt_worker_upkeep_change("decrease", "African")
        if population_increase > 0:
            current_slums.change_population(population_increase)


def trigger_worker_migration():  # resolves migration if it occurs
    """
    Description:
        When a migration event occurs, about half of available workers in villages and all wandering workers move to a slum around a colonial port, train station, or resource production facility. The chance to move to a slum on a tile
            is weighted by the number of people already in that tile's slum and the number of employment buildings on that tile. Also displays a report of the movements that occurred
    Input:
        None
    Output:
        None
    """
    possible_source_village_list = (
        actor_utility.get_migration_sources()
    )  # list of villages that could have migration
    destination_cell_list = actor_utility.get_migration_destinations()

    if destination_cell_list:
        weighted_destination_cell_list = create_weighted_migration_destinations(
            destination_cell_list
        )

        village_destination_dict = {}
        village_num_migrated_dict = {}
        for source_village in possible_source_village_list:
            num_migrated = 0
            for available_worker in range(source_village.available_workers):
                if random.randrange(1, 7) >= 4:
                    num_migrated += 1

            if num_migrated > 0:
                destination = random.choice(weighted_destination_cell_list)
                if not destination.has_building("slums"):
                    destination.create_slums()
                source_village.change_available_workers(-1 * num_migrated)
                source_village.change_population(-1 * num_migrated)
                destination.get_building("slums").change_population(num_migrated)
                village_destination_dict[source_village] = destination
                village_num_migrated_dict[source_village] = num_migrated

        wandering_num_migrated_dict = {}
        for i in range(constants.num_wandering_workers):
            destination = random.choice(weighted_destination_cell_list)
            if not destination.has_building("slums"):
                destination.create_slums()
            destination.get_building("slums").change_population(1)
            constants.num_wandering_workers -= 1
            wandering_num_migrated_dict[destination] = (
                wandering_num_migrated_dict.get(destination, 0) + 1
            )

        if village_num_migrated_dict or wandering_num_migrated_dict:
            migration_report_text = "A wave of migration from villages to your colony has occurred as African workers search for employment. /n /n"
            for (
                source_village
            ) in (
                village_destination_dict
            ):  # 2 workers migrated from villageName village to the slums surrounding Port Young at (0, 0). /n /n
                destination = village_destination_dict[source_village]
                destination_settlement = destination.settlement

                current_notification_text = f"{village_num_migrated_dict[source_village]} worker{utility.generate_plural(village_num_migrated_dict[source_village])} migrated from the village of {source_village.name} to the slums surrounding {destination_settlement.name} at ({destination.x}, {destination.y}). /n /n"

                constants.notification_manager.display_notification(
                    {
                        "message": migration_report_text + current_notification_text,
                        "zoom_destination": destination.tile,
                    }
                )

            for (
                destination
            ) in (
                wandering_num_migrated_dict
            ):  # 3 wandering workers settled in the slums surrounding Port Young at (0, 0). /n /n
                destination_settlement = destination.settlement

                current_notification_text = f"{wandering_num_migrated_dict[destination]} wandering worker{utility.generate_plural(wandering_num_migrated_dict[destination])} settled in the slums surrounding {destination_settlement.name} at ({destination.x}, {destination.y}). /n /n"

                constants.notification_manager.display_notification(
                    {
                        "message": migration_report_text + current_notification_text,
                        "zoom_destination": destination.tile,
                    }
                )


def create_weighted_migration_destinations(destination_cell_list):
    """
    Description:
        Analyzes a list of destinations for a migration event and creates a weighted list from which cells with more employment buildings and lower slum populations are more likely to be chosen
    Input:
        cell list destination_cell_list: list of cells that have employment buildings to migrate to
    Output:
        cell list: Returns a weighted list of cells in which cells with more employment buildings and lower slum populations appear a greater number of times
    """
    weighted_cell_list = []
    for current_cell in destination_cell_list:
        num_poi = 0  # points of interest
        if current_cell.has_intact_building("port"):
            num_poi += 1
        if current_cell.has_intact_building("train_station"):
            num_poi += 1
        if current_cell.has_intact_building("resource"):
            num_poi += 1
        max_population_weight = 5
        if not current_cell.has_building("slums"):  # 0
            population_weight = max_population_weight
        elif (
            current_cell.get_building("slums").available_workers < max_population_weight
        ):  # 1-4
            population_weight = (
                max_population_weight
                - current_cell.get_building("slums").available_workers
            )
        else:  # 5+
            population_weight = 1
        total_weight = population_weight * num_poi
        for i in range(total_weight):
            weighted_cell_list.append(current_cell)
    return weighted_cell_list


def manage_warriors():
    """
    Description:
        Controls native warrior spawning/despawning
    Input:
        None
    Output:
        None
    """
    for current_village in status.village_list:
        current_village.manage_warriors()


def manage_villages(verbose: bool = True):
    """
    Description:
        Controls the aggressiveness and population changes of villages and native warrior spawning/despawning
    Input:
        None
    Output:
        None
    """
    for current_village in status.village_list:
        if current_village.population > 0:
            previous_aggressiveness = current_village.aggressiveness
            roll = random.randrange(1, 7)
            if roll <= 2:  # 1-2
                current_village.change_aggressiveness(-1)
            # 3-4 does nothing
            elif roll >= 5:  # 5-6
                current_village.change_aggressiveness(1)
            if (
                current_village.cell.has_intact_building("mission")
                and previous_aggressiveness == 3
                and current_village.aggressiveness == 4
            ):
                if (
                    verbose
                ):  # Should not display this message when simulating turns before the start of the game
                    text = (
                        "The previously pacified village of "
                        + current_village.name
                        + " at ("
                        + str(current_village.cell.x)
                        + ", "
                        + str(current_village.cell.y)
                        + ") has increased in aggressiveness and now has a chance of sending out hostile warriors. /n /n"
                    )
                    constants.notification_manager.display_notification(
                        {
                            "message": text,
                            "zoom_destination": current_village.cell.tile,
                        }
                    )
        if random.randrange(1, 7) == 6 and random.randrange(1, 7) == 6:
            previous_population = current_village.population
            current_village.change_population(1)
            if (
                previous_population <= 0
                and current_village.cell.visible
                and constants.current_game_mode in current_village.cell.grid.modes
            ):
                text = (
                    "The previously abandonded village of "
                    + current_village.name
                    + " at ("
                    + str(current_village.cell.x)
                    + ", "
                    + str(current_village.cell.y)
                    + ") is now being re-settled. /n /n"
                )
                constants.notification_manager.display_notification(
                    {
                        "message": text,
                        "zoom_destination": current_village.cell.tile,
                    }
                )


def manage_beasts():
    """
    Description:
        Controls beast spawning/despawning
    Input:
        None
    Output:
        None
    """
    return
    beast_list = status.beast_list
    for current_beast in beast_list:
        current_beast.check_despawn()

    if random.randrange(1, 7) == 1:
        actor_utility.spawn_beast()


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
    removed_ministers = []
    for current_minister in status.minister_list:
        removing_current_minister = False
        if (
            current_minister.just_removed
            and current_minister.current_position == "none"
        ):
            current_minister.respond("fired")
            removing_current_minister = True
        elif (
            current_minister.current_position == "none"
            and random.randrange(1, 7) == 1
            and random.randrange(1, 7) <= 2
        ):  # 1/18 chance of switching out available ministers
            removed_ministers.append(current_minister)
        elif (
            random.randrange(1, 7) == 1
            and random.randrange(1, 7) <= 2
            and random.randrange(1, 7) <= 2
            and (
                random.randrange(1, 7) <= 3 or constants.evil > random.randrange(0, 100)
            )
        ) or constants.effect_manager.effect_active("farm_upstate"):
            removed_ministers.append(current_minister)
        else:  # if not retired/fired
            if (
                random.randrange(1, 7) == 1 and random.randrange(1, 7) == 1
            ):  # 1/36 chance to increase relevant specific skill
                current_minister.gain_experience()
        current_minister.just_removed = False

        if current_minister.fabricated_evidence > 0:
            prosecutor = status.current_ministers["Prosecutor"]
            if (
                prosecutor.check_corruption()
            ):  # corruption is normally resolved during a trial, but prosecutor can still steal money from unused fabricated evidence if no trial occurs
                prosecutor.steal_money(
                    trial_utility.get_fabricated_evidence_cost(
                        current_minister.fabricated_evidence, True
                    ),
                    "fabricated_evidence",
                )
            text_utility.print_to_screen(
                f"The {current_minister.fabricated_evidence} fabricated evidence against {current_minister.name} is no longer usable."
            )
            current_minister.corruption_evidence -= current_minister.fabricated_evidence
            current_minister.fabricated_evidence = 0

        evidence_lost = 0
        for i in range(current_minister.corruption_evidence):
            if random.randrange(1, 7) == 1 and random.randrange(1, 7) == 1:
                evidence_lost += 1
        if evidence_lost > 0:
            if current_minister.current_position == "none":
                current_position = ""
            else:
                current_position = current_minister.current_position
            if evidence_lost == current_minister.corruption_evidence:
                current_minister.display_message(
                    f"All of the {current_minister.corruption_evidence} evidence of {current_position} {current_minister.name}'s corruption has lost potency over time and will no longer be usable in trials against him. /n /n"
                )
            else:
                current_minister.display_message(
                    f"{evidence_lost} of the {current_minister.corruption_evidence} evidence of {current_position} {current_minister.name}'s corruption has lost potency over time and will no longer be usable in trials against him. /n /n"
                )
            current_minister.corruption_evidence -= evidence_lost
        if removing_current_minister:
            current_minister.remove_complete()
    if flags.prosecution_bribed_judge:
        text_utility.print_to_screen(
            "The effect of bribing the judge has faded and will not affect the next trial."
        )
    flags.prosecution_bribed_judge = False

    while len(removed_ministers) > 0:
        current_minister = removed_ministers.pop(0)
        current_minister.respond("retirement")

        if current_minister.current_position != "none":
            current_minister.appoint("none")
        current_minister.remove_complete()

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
    first_roll = random.randrange(1, 7)
    second_roll = random.randrange(1, 7)
    if first_roll == 1 and second_roll <= 3:
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
            current_minister.attempt_rumor("loyalty", "none")
        for skill_type in constants.minister_types:
            if skill_type == current_minister.current_position:
                if random.randrange(1, 7) == 1 and random.randrange(1, 7) == 1:
                    current_minister.attempt_rumor(skill_type, "none")
            elif (
                random.randrange(1, 7) == 1
                and random.randrange(1, 7) == 1
                and random.randrange(1, 7) == 1
            ):
                current_minister.attempt_rumor(skill_type, "none")
        # 1/36 of getting loyalty report
        # if currently employed, 1/36 of getting report on working skill
        # if currently employed, 1/216 of getting report on each non-working skill
        # if not employed, 1/216 of getting report on each skill


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
                "choices": ["confirm main menu", "quit"],
            }
        )


def manage_commodity_sales():
    """
    Description:
        Orders the minister of trade to process all commodity sales started in the player's turn, allowing the minister to use skill/corruption to modify how much money is received by the company
    Input:
        None
    Output:
        None
    """
    sold_commodities = constants.sold_commodities
    trade_minister = status.current_ministers[constants.type_minister_dict["trade"]]
    stealing = False
    money_stolen = 0
    reported_revenue = 0
    text = (
        trade_minister.current_position
        + " "
        + trade_minister.name
        + " reports the following commodity sales: /n /n"
    )
    any_sold = False
    for current_commodity in constants.commodity_types:
        if sold_commodities[current_commodity] > 0:
            any_sold = True
            sell_price = constants.item_prices[current_commodity]
            expected_revenue = sold_commodities[current_commodity] * sell_price
            expected_revenue = status.current_ministers["Prosecutor"].estimate_expected(
                expected_revenue, False
            )
            actual_revenue = 0

            for i in range(sold_commodities[current_commodity]):
                individual_sell_price = (
                    sell_price
                    + random.randrange(-1, 2)
                    + trade_minister.get_roll_modifier()
                )
                if trade_minister.check_corruption() and individual_sell_price > 1:
                    money_stolen += 1
                    individual_sell_price -= 1
                if individual_sell_price < 1:
                    individual_sell_price = 1
                reported_revenue += individual_sell_price
                actual_revenue += individual_sell_price
                if random.randrange(1, 7) <= 1:  # 1/6 chance
                    market_utility.change_price(current_commodity, -1)

            text += (
                str(sold_commodities[current_commodity])
                + " "
                + current_commodity
                + " sold for "
                + str(actual_revenue)
                + " money (expected "
                + str(expected_revenue)
                + ") /n /n"
            )

    constants.money_tracker.change(reported_revenue, "sold_commodities")

    if any_sold:
        trade_minister.display_message(text)
        status.previous_sales_report = text
    if money_stolen > 0:
        trade_minister.steal_money(money_stolen, "sold_commodities")

    for current_commodity in constants.commodity_types:
        constants.sold_commodities[current_commodity] = 0


def manage_lore():
    """
    Description:
        Controls the spawning of new lore missions
    Input:
        None
    Output:
        None
    """
    if status.current_lore_mission == None:
        if (
            random.randrange(1, 7) == 1 and random.randrange(1, 7) <= 2
        ) or constants.effect_manager.effect_active("instant_lore_mission"):
            constants.actor_creation_manager.create_lore_mission(False, {})


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
        if (
            current_minister.just_removed
            and current_minister.current_position == "none"
        ):
            text = (
                "Warning: if you do not reappoint "
                + current_minister.name
                + " by the end of the turn, he will be considered fired, leaving the candidate pool and incurring a large public opinion penalty. /n /n"
            )
            current_minister.display_message(text)

    for (
        current_cell
    ) in (
        status.strategic_map_grid.get_flat_cell_list()
    ):  # Warn for insufficient warehouses
        if (
            current_cell.visible
            and current_cell.tile.get_inventory_used()
            > current_cell.tile.inventory_capacity
        ):
            text = (
                "Warning: the warehouses at ("
                + str(current_cell.x)
                + ", "
                + str(current_cell.y)
                + ") are not sufficient to hold the commodities stored there. /n /n"
            )
            text += "Any commodities exceeding the tile's storage capacity will be lost at the end of the turn. /n /n"
            constants.notification_manager.display_notification(
                {
                    "message": text,
                    "zoom_destination": current_cell.tile,
                }
            )
    for current_grid in status.grid_list:
        if current_grid.is_abstract_grid:
            current_cell = current_grid.cell_list[0][0]
            if (
                current_cell.tile.get_inventory_used()
                > current_cell.tile.inventory_capacity
                and not current_cell.tile.infinite_inventory_capacity
            ):
                text = (
                    "Warning: the warehouses in "
                    + current_grid.cell_list[0][0].tile.name
                    + " are not sufficient to hold the commodities stored there. /n /n"
                )
                text += "Any commodities exceeding the tile's storage capacity will be lost at the end of the turn. /n /n"
                constants.notification_manager.display_notification(
                    {
                        "message": text,
                        "zoom_destination": current_cell.tile,
                    }
                )

    for (
        grid_type
    ) in (
        constants.abstract_grid_type_list
    ):  # Warn for leaving units behind in non-Earth grids
        if grid_type != "earth_grid":
            current_cell = getattr(status, grid_type).find_cell(0, 0)
            num_leaving, num_reserve = (
                00,
                0,
            )  # Vehicles leaving, and vehicles staying behind, respectively
            for current_mob in current_cell.contained_mobs:
                if (
                    current_mob.end_turn_destination != "none"
                    and current_mob.is_vehicle
                ):
                    num_leaving += 1
                elif current_mob.is_vehicle and current_mob.has_crew:
                    num_reserve += 1
            num_stranded = len(current_cell.contained_mobs) - (
                num_leaving + num_reserve
            )  # Number of non-vehicles left behind
            grid_name = (
                grid_type[:-5].replace("_", " ").capitalize()
            )  # slave_traders_grid -> Slave traders
            if (
                num_leaving > 0 and num_stranded > 0 and num_reserve == 0
            ):  # If at least 1 vehicle leaving grid and at least 1 unit left behind, give warning
                text = (
                    "Warning: at least 1 unit is being left behind in "
                    + grid_name
                    + " and will not be able to leave without another ship. /n /n"
                )
                constants.notification_manager.display_notification(
                    {"message": text, "zoom_destination": current_cell.tile}
                )

    for minister in status.minister_list:
        if minister.fabricated_evidence > 0:
            text = f"WARNING: Your {minister.fabricated_evidence} piece{utility.generate_plural(minister.fabricated_evidence)} of fabricated evidence against {minister.current_position} {minister.name} will disappear at the end of the turn if left unused. /n /n"
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
