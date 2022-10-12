#Contains functions that manage what happens at the end of each turn, like worker upkeep and price changes

import random

from . import text_tools
from . import actor_utility
from . import trial_utility
from . import market_tools
from . import notification_tools
from . import utility
from . import game_transitions

def end_turn(global_manager):
    '''
    Description:
        Ends the turn, completing any pending movements, removing any commodities that can't be stored, and doing resource production
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    remove_excess_inventory(global_manager)
    for current_pmob in global_manager.get('pmob_list'):
        current_pmob.end_turn_move()

    actor_utility.deselect_all(global_manager)
        
    global_manager.set('player_turn', False)
    global_manager.set('player_turn_queue', [])
    start_enemy_turn(global_manager)

def start_enemy_turn(global_manager):
    '''
    Description:
        Starts the ai's turn, resetting their units to maximum movement points, spawning warriors, etc.
    Input:
        global_manager_template global_manager: Object that accesses shared variables
        first_turn = False: Whether this is the first turn - do not pay upkeep, etc. when the game first starts
    Output:
        None
    '''
    manage_villages(global_manager)
    manage_beasts(global_manager)
    reset_mobs('npmobs', global_manager)
    #manage_enemy_movement(global_manager)
    #manage_combat(global_manager) #should probably do reset_mobs, manage_production, etc. after combat completed in a separate function
    #the manage_combat function starts the player turn
    
def start_player_turn(global_manager, first_turn = False):
    '''
    Description:
        Starts the player's turn, resetting their units to maximum movement points, adjusting prices, paying upkeep, etc.
    Input:
        global_manager_template global_manager: Object that accesses shared variables
        first_turn = False: Whether this is the first turn - do not pay upkeep, etc. when the game first starts
    Output:
        None
    '''
    text_tools.print_to_screen("", global_manager)
    text_tools.print_to_screen("Turn " + str(global_manager.get('turn') + 1), global_manager)
    if not first_turn:
        for current_pmob in global_manager.get('pmob_list'):
            if current_pmob.is_vehicle:
                current_pmob.reembark()
        for current_building in global_manager.get('building_list'):
            if current_building.building_type == 'resource':
                current_building.reattach_work_crews()
        manage_attrition(global_manager) #have attrition before or after enemy turn? Before upkeep?
        reset_mobs('pmobs', global_manager)
        manage_production(global_manager)
        manage_public_opinion(global_manager)
        manage_upkeep(global_manager)
        manage_loans(global_manager)
        manage_worker_price_changes(global_manager)
        manage_worker_migration(global_manager)
        manage_commodity_sales(global_manager)
        manage_ministers(global_manager)
        manage_subsidies(global_manager) #subsidies given after public opinion changes
        manage_financial_report(global_manager)
        actor_utility.reset_action_prices(global_manager)
        game_end_check(global_manager)

    global_manager.set('player_turn', True) #player_turn also set to True in main_loop when enemies done moving
    global_manager.set('enemy_combat_phase', False)
    global_manager.get('turn_tracker').change(1)
        
    if not first_turn:
        market_tools.adjust_prices(global_manager)#adjust_prices(global_manager)

    if global_manager.get('displayed_mob') == 'none' or global_manager.get('displayed_mob').is_npmob:
        actor_utility.deselect_all(global_manager)
        game_transitions.cycle_player_turn(global_manager, True)
    elif not global_manager.get('displayed_mob').selected:
        global_manager.get('displayed_mob').select()

def reset_mobs(mob_type, global_manager):
    '''
    Description:
        Starts the turn for mobs of the inputed type, resetting their movement points and removing the disorganized status
    Input:
        string mob_type: Can be pmob or npmob, determines which mobs' turn starts
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    if mob_type == 'pmobs':
        for current_pmob in global_manager.get('pmob_list'):
            current_pmob.reset_movement_points()
            current_pmob.set_disorganized(False)
    elif mob_type == 'npmobs':
        for current_npmob in global_manager.get('npmob_list'):
            current_npmob.reset_movement_points()
            current_npmob.set_disorganized(False)
            #if not current_npmob.creation_turn == global_manager.get('turn'): #if not created this turn
            current_npmob.turn_done = False
            global_manager.get('enemy_turn_queue').append(current_npmob)
    else:
        for current_mob in global_manager.get('mob_list'):
            current_mob.reset_movement_points()
            current_mob.set_disorganized(False)

def manage_attrition(global_manager):
    '''
    Description:
        Checks each unit and commodity storage location to see if attrition occurs. Health attrition forces parts of units to die and need to be replaced, costing money, removing experience, and preventing them from acting in the next
            turn. Commodity attrition causes up to half of the commodities stored in a warehouse or carried by a unit to be lost. Both types of attrition are more common in bad terrain and less common in areas with more infrastructure
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    for current_pmob in global_manager.get('pmob_list'):
        if not (current_pmob.in_vehicle or current_pmob.in_group or current_pmob.in_building): #vehicles, groups, and buildings handle attrition for their submobs
            current_pmob.manage_health_attrition()
    for current_building in global_manager.get('building_list'):
        if current_building.building_type == 'resource':
            current_building.manage_health_attrition()

    for current_pmob in global_manager.get('pmob_list'):
        current_pmob.manage_inventory_attrition()

    terrain_cells = global_manager.get('strategic_map_grid').cell_list + global_manager.get('slave_traders_grid').cell_list + global_manager.get('europe_grid').cell_list
    for current_cell in terrain_cells:
        current_tile = current_cell.tile
        if len(current_tile.get_held_commodities()) > 0:
            current_tile.manage_inventory_attrition()

def remove_excess_inventory(global_manager):
    '''
    Description:
        Removes any commodities that exceed their tile's storage capacities
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    terrain_cells = global_manager.get('strategic_map_grid').cell_list + global_manager.get('slave_traders_grid').cell_list + global_manager.get('europe_grid').cell_list
    for current_cell in terrain_cells:
        current_tile = current_cell.tile
        if len(current_tile.get_held_commodities()) > 0:
            current_tile.remove_excess_inventory()
    
def manage_production(global_manager):
    '''
    Description:
        Orders each work crew in a production building to attempt commodity production and displays a production report of commodities for which production was attempted and how much of each was produced
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    global_manager.set('attempted_commodities', [])
    expected_production = {}
    for current_commodity in global_manager.get('collectable_resources'):
        global_manager.get('commodities_produced')[current_commodity] = 0
        expected_production[current_commodity] = 0
    for current_resource_building in global_manager.get('resource_building_list'):
        if not current_resource_building.damaged:
            for current_work_crew in current_resource_building.contained_work_crews:
                if current_work_crew.movement_points >= 1:
                    if current_work_crew.veteran:
                        expected_production[current_resource_building.resource_type] += 0.75 * current_resource_building.efficiency
                    else:
                        expected_production[current_resource_building.resource_type] += 0.5 * current_resource_building.efficiency
            current_resource_building.produce()
            if len(current_resource_building.contained_work_crews) == 0:
                if not current_resource_building.resource_type in global_manager.get('attempted_commodities'):
                    global_manager.get('attempted_commodities').append(current_resource_building.resource_type)

    attempted_commodities = global_manager.get('attempted_commodities')
    displayed_commodities = []
    production_minister = global_manager.get('current_ministers')[global_manager.get('type_minister_dict')['production']]
    
    if not len(global_manager.get('attempted_commodities')) == 0: #if any attempted, do production report
        text = production_minister.current_position + " " + production_minister.name + " reports the following commodity production: /n /n"
        while len(displayed_commodities) < len(attempted_commodities):
            max_produced = 0
            max_commodity = 'none'
            for current_commodity in attempted_commodities:
                if not current_commodity in displayed_commodities:
                    if global_manager.get('commodities_produced')[current_commodity] >= max_produced:
                        max_commodity = current_commodity
                        max_produced = global_manager.get('commodities_produced')[current_commodity]
                        expected_production[max_commodity] = global_manager.get('current_ministers')['Prosecutor'].estimate_expected(expected_production[max_commodity])
            displayed_commodities.append(max_commodity)
            text += max_commodity.capitalize() + ": " + str(max_produced) + ' (expected ' + str(expected_production[max_commodity]) + ') /n /n'
        production_minister.display_message(text)       

def manage_upkeep(global_manager):
    '''
    Description:
        Pays upkeep for all units at the end of a turn. Currently, only workers cost upkeep
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    african_worker_upkeep = round(global_manager.get('num_african_workers') * global_manager.get('african_worker_upkeep'), 2)
    european_worker_upkeep = round(global_manager.get('num_european_workers') * global_manager.get('european_worker_upkeep'), 2)
    slave_worker_upkeep = round(global_manager.get('num_slave_workers') * global_manager.get('slave_worker_upkeep'), 2)
    num_workers = global_manager.get('num_african_workers') + global_manager.get('num_european_workers') + global_manager.get('num_slave_workers')
    total_upkeep = round(african_worker_upkeep + european_worker_upkeep + slave_worker_upkeep, 2)
    global_manager.get('money_tracker').change(round(-1 * total_upkeep, 2), 'worker upkeep')

def manage_loans(global_manager):
    '''
    Description:
        Pays interest on all current loans at the end of a turn
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    for current_loan in global_manager.get('loan_list'):
        current_loan.make_payment()

def manage_public_opinion(global_manager):
    '''
    Description:
        Changes public opinion at the end of the turn to move back toward 50
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    current_public_opinion = round(global_manager.get('public_opinion'))
    if current_public_opinion < 50:
        global_manager.get('public_opinion_tracker').change(1)
        text_tools.print_to_screen("Trending toward a neutral attitude, public opinion toward your company increased from " + str(current_public_opinion) + " to " + str(current_public_opinion + 1), global_manager)
    elif current_public_opinion > 50:
        global_manager.get('public_opinion_tracker').change(-1)
        text_tools.print_to_screen("Trending toward a neutral attitude, public opinion toward your company decreased from " + str(current_public_opinion) + " to " + str(current_public_opinion - 1), global_manager)
    global_manager.get('evil_tracker').change(-1)
    if global_manager.get('DEBUG_show_evil'):
        print("Evil number: " + str(global_manager.get('evil')))
    if global_manager.get('DEBUG_show_fear'):
        print("Fear number: " + str(global_manager.get('fear')))
    
def manage_subsidies(global_manager):
    '''
    Description:
        Receives subsidies at the end of the turn based on public opinion
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    subsidies_received = market_tools.calculate_subsidies(global_manager)
    text_tools.print_to_screen("You received " + str(subsidies_received) + " money in subsidies from the government based on your public opinion and colonial efforts", global_manager)
    global_manager.get('money_tracker').change(subsidies_received, 'subsidies')


def manage_financial_report(global_manager):
    '''
    Description:
        Displays a financial report at the end of the turn, showing revenue in each area, costs in each area, and total profit from the last turn
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    financial_report_text = global_manager.get('money_tracker').prepare_financial_report()
    notification_tools.display_notification(financial_report_text, 'default', global_manager)
    global_manager.set('previous_financial_report', financial_report_text)
    global_manager.get('money_tracker').reset_transaction_history()

def manage_worker_price_changes(global_manager):
    '''
    Description:
        Randomly changes the prices of slave purchase and European worker upkeep at the end of the turn, generally trending down to compensate for increases when recruited
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    european_worker_roll = random.randrange(1, 7)
    if european_worker_roll >= 5:
        current_price = global_manager.get('european_worker_upkeep')
        changed_price = round(current_price - global_manager.get('worker_upkeep_fluctuation_amount'), 2)
        if changed_price >= global_manager.get('min_european_worker_upkeep'):
            global_manager.set('european_worker_upkeep', changed_price)
            text_tools.print_to_screen("An influx of workers from Europe has decreased the upkeep of European workers from " + str(current_price) + " to " + str(changed_price) + ".", global_manager)
    elif european_worker_roll == 1:
        current_price = global_manager.get('european_worker_upkeep')
        changed_price = round(current_price + global_manager.get('worker_upkeep_fluctuation_amount'), 2)
        global_manager.set('european_worker_upkeep', changed_price)
        text_tools.print_to_screen("An shortage of workers from Europe has increased the upkeep of European workers from " + str(current_price) + " to " + str(changed_price) + ".", global_manager)

    slave_worker_roll = random.randrange(1, 7)
    if slave_worker_roll == 6:
        current_price = global_manager.get('recruitment_costs')['slave workers']
        changed_price = round(current_price - global_manager.get('slave_recruitment_cost_fluctuation_amount'), 2)
        if changed_price >= global_manager.get('min_slave_worker_recruitment_cost'):
            global_manager.get('recruitment_costs')['slave workers'] = changed_price
            text_tools.print_to_screen("An influx of captured slaves has decreased the purchase cost of slave workers from " + str(current_price) + " to " + str(changed_price) + ".", global_manager)
    elif slave_worker_roll == 1:
        current_price = global_manager.get('recruitment_costs')['slave workers']
        changed_price = round(current_price + global_manager.get('slave_recruitment_cost_fluctuation_amount'), 2)
        global_manager.get('recruitment_costs')['slave workers'] = changed_price
        text_tools.print_to_screen("A shortage of captured slaves has increased the purchase cost of slave workers from " + str(current_price) + " to " + str(changed_price) + ".", global_manager)
        
def manage_worker_migration(global_manager): 
    '''
    Description:
        Checks if a workerm migration event occurs and resolves it if it does occur
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    num_village_workers = actor_utility.get_num_available_workers('village', global_manager) + global_manager.get('num_wandering_workers')
    num_slums_workers = actor_utility.get_num_available_workers('slums', global_manager)
    if num_village_workers > num_slums_workers and random.randrange(1, 7) >= 5: #1/3 chance of activating
        trigger_worker_migration(global_manager)

    for current_slums in global_manager.get('slums_list'):
        population_increase = 0
        for current_worker in range(current_slums.available_workers):
            if random.randrange(1, 7) == 1 and random.randrange(1, 7) == 1 and random.randrange(1, 7) == 1:
                population_increase += 1
                market_tools.attempt_worker_upkeep_change('decrease', 'African', global_manager)
        if population_increase > 0:
            current_slums.change_population(population_increase)

def trigger_worker_migration(global_manager): #resolves migration if it occurs
    '''
    Description:
        When a migration event occurs, about half of available workers in villages and all wandering workers move to a slum around a colonial port, train station, or resource production facility. The chance to move to a slum on a tile
            is weighted by the number of people already in that tile's slum and the number of employment buildings on that tile. Also displays a report of the movements that occurred
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    possible_source_village_list = actor_utility.get_migration_sources(global_manager) #list of villages that could have migration
    destination_cell_list = actor_utility.get_migration_destinations(global_manager)
    if not len(destination_cell_list) == 0:
        weighted_destination_cell_list = create_weighted_migration_destinations(destination_cell_list)
        village_destination_dict = {}
        village_destination_coordinates_dict = {}
        village_num_migrated_dict = {}
        source_village_list = [] #list of villages that actually had migration occur
        any_migrated = False
        #resolve village worker migration
        for source_village in possible_source_village_list:
            num_migrated = 0
            for available_worker in range(source_village.available_workers):
                if random.randrange(1, 7) >= 4:
                    num_migrated += 1
                    
            if num_migrated > 0:
                any_migrated = True
                
                source_village_list.append(source_village)
                destination = random.choice(weighted_destination_cell_list) #random.choice(destination_cell_list)
                if not destination.has_building('slums'):
                    destination.create_slums()
                source_village.change_available_workers(-1 * num_migrated)
                source_village.change_population(-1 * num_migrated)
                destination.get_building('slums').change_population(num_migrated)
                if destination.has_intact_building('port'):
                    destination_type = 'port'
                elif destination.has_intact_building('resource'):
                    destination_type = destination.get_building('resource').name
                elif destination.has_intact_building('train_station'):
                    destination_type = 'train station'
                village_destination_dict[source_village] = destination_type
                village_destination_coordinates_dict[source_village] = (destination.x, destination.y)
                village_num_migrated_dict[source_village] = num_migrated

        
        #resolve wandering worker migration
        wandering_destinations = []
        wandering_destination_dict = {}
        wandering_destination_coordinates_dict = {}
        wandering_num_migrated_dict = {}
        num_migrated = global_manager.get('num_wandering_workers')
        if num_migrated > 0:
            any_migrated = True
            for i in range(num_migrated):
                destination = random.choice(weighted_destination_cell_list) #random.choice(destination_cell_list)
                if not destination.has_building('slums'):
                    destination.create_slums()
                destination.get_building('slums').change_population(1) #num_migrated
                global_manager.set('num_wandering_workers', global_manager.get('num_wandering_workers') - 1)
                if destination.has_intact_building('port'):
                    destination_type = 'port'
                elif destination.has_intact_building('resource'):
                    destination_type = destination.get_building('resource').name
                elif destination.has_intact_building('train_station'):
                    destination_type = 'train station'
                wandering_destination_dict[destination] = destination_type #destination 0: port
                wandering_destination_coordinates_dict[destination] = (destination.x, destination.y) #destination 0: (2, 2)
                if destination in wandering_destinations:
                    wandering_num_migrated_dict[destination] += 1
                else:
                    wandering_num_migrated_dict[destination] = 1
                    wandering_destinations.append(destination)
                
        if any_migrated:        
            migration_report_text = 'A wave of migration from villages to your colony has occurred as African workers search for employment. /n'
            for source_village in source_village_list: #1 worker migrated from villageName village to the slums surrounding your iron mine at (0, 0). /n
                current_line = str(village_num_migrated_dict[source_village]) + ' worker' + utility.generate_plural(village_num_migrated_dict[source_village]) + ' migrated from ' + source_village.name
                current_line += " village to the slums surrounding your " + village_destination_dict[source_village]
                current_line += " at (" + str(village_destination_coordinates_dict[source_village][0]) + ', ' + str(village_destination_coordinates_dict[source_village][1]) + ').'
                migration_report_text += current_line + ' /n'
            for wandering_destination in wandering_destinations:
                current_line = str(wandering_num_migrated_dict[wandering_destination]) + ' wandering worker' + utility.generate_plural(wandering_num_migrated_dict[wandering_destination]) + ' settled in the slums surrounding your '
                current_line += wandering_destination_dict[wandering_destination] + " at (" + str(wandering_destination_coordinates_dict[wandering_destination][0]) + ', ' + str(wandering_destination_coordinates_dict[wandering_destination][1]) + ').'
                migration_report_text += current_line + ' /n'
            notification_tools.display_notification(migration_report_text, 'default', global_manager)
    
def create_weighted_migration_destinations(destination_cell_list):
    '''
    Description:
        Analyzes a list of destinations for a migration event and creates a weighted list from which cells with more employment buildings and lower slum populations are more likely to be chosen
    Input:
        cell list destination_cell_list: list of cells that have employment buildings to migrate to
    Output:
        cell list: Returns a weighted list of cells in which cells with more employment buildings and lower slum populations appear a greater number of times
    '''
    weighted_cell_list = []
    for current_cell in destination_cell_list:
        num_poi = 0 #points of interest
        if current_cell.has_intact_building('port'):
            num_poi += 1
        if current_cell.has_intact_building('train_station'):
            num_poi += 1
        if current_cell.has_intact_building('resource'):
            num_poi += 1
        max_population_weight = 5
        if not current_cell.has_building('slums'): #0
            population_weight = max_population_weight
        elif current_cell.get_building('slums').available_workers < max_population_weight: #1-4
            population_weight = max_population_weight - current_cell.get_building('slums').available_workers
        else: #5+
            population_weight = 1
        total_weight = population_weight * num_poi
        for i in range(total_weight):
            weighted_cell_list.append(current_cell)
    return(weighted_cell_list)


def manage_villages(global_manager):
    '''
    Description:
        Controls the aggressiveness and population changes of villages and native warrior spawning/despawning
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    for current_village in global_manager.get('village_list'):
        current_village.manage_warriors()
    
    for current_village in global_manager.get('village_list'):
        if current_village.population > 0:
            previous_aggressiveness = current_village.aggressiveness
            roll = random.randrange(1, 7)
            if roll <= 2: #1-2
                current_village.change_aggressiveness(-1)
            #3-4 does nothing
            elif roll >= 5: #5-6
                current_village.change_aggressiveness(1)
            if current_village.cell.has_intact_building('mission') and previous_aggressiveness == 3 and current_village.aggressiveness == 4:
                text = "The previously pacified village at (" + str(current_village.cell.x) + ", " + str(current_village.cell.y) + ") has increased in aggressiveness and now has a chance of sending out hostile warriors. /n /n"
                notification_tools.display_zoom_notification(text, current_village.cell.tile, global_manager)

        roll = random.randrange(1, 7)
        second_roll = random.randrange(1, 7)
        if roll == 6 and second_roll == 6:
            current_village.change_population(1)

def manage_beasts(global_manager):
    '''
    Description:
        Controls beast spawning/despawning
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    beast_list = global_manager.get('beast_list')
    for current_beast in beast_list:
        current_beast.check_despawn()

    if random.randrange(1, 7) == 1:
        actor_utility.spawn_beast(global_manager)
    

def manage_enemy_movement(global_manager):
    '''
    Description:
        Moves npmobs at the end of the turn towards player-controlled mobs/buildings
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    for current_npmob in global_manager.get('npmob_list'):
        if not current_npmob.creation_turn == global_manager.get('turn'): #if not created this turn
            current_npmob.end_turn_move()

def manage_combat(global_manager):
    '''
    Description:
        Resolves, in order, each possible combat that was triggered by npmobs moving into cells with pmobs. When a possible combat is resolved, it should call the next possible combat until all are resolved
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    if len(global_manager.get('attacker_queue')) > 0:
        global_manager.get('attacker_queue').pop(0).attempt_local_combat()
    else:
        start_player_turn(global_manager)

def manage_ministers(global_manager):
    '''
    Description:
        Controls minister retirement, new ministers appearing, and evidence loss over time
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    removed_ministers = []
    for current_minister in global_manager.get('minister_list'):
        if current_minister.just_removed and current_minister.current_position == 'none':
            current_minister.respond('fired')
            current_minister.remove()
        elif current_minister.current_position == 'none' and random.randrange(1, 7) == 1 and random.randrange(1, 7) <= 2: #1/18 chance of switching out available ministers
            removed_ministers.append(current_minister)
        elif (random.randrange(1, 7) == 1 and random.randrange(1, 7) <= 2 and random.randrange(1, 7) <= 2 and (random.randrange(1, 7) <= 3 or global_manager.get('evil') > random.randrange(0, 100))) or global_manager.get('DEBUG_farm_upstate'):
            removed_ministers.append(current_minister)
        else: #if not retired/fired
            if random.randrange(1, 7) == 1 and random.randrange(1, 7) == 1: #1/36 chance to increase relevant specific skill
                current_minister.gain_experience()

        if current_minister.fabricated_evidence > 0:
            prosecutor = global_manager.get('current_ministers')['Prosecutor']
            if prosecutor.check_corruption(): #corruption is normally resolved during a trial, but prosecutor can still steal money from unused fabricated evidence if no trial occurs
                prosecutor.steal_money(trial_utility.get_fabricated_evidence_cost(current_minister.fabricated_evidence, True), 'fabricated evidence')
            text_tools.print_to_screen("The " + str(current_minister.fabricated_evidence) + " fabricated evidence against " + current_minister.name + " is no longer usable.", global_manager)
            current_minister.corruption_evidence -= current_minister.fabricated_evidence
            current_minister.fabricated_evidence = 0

        evidence_lost = 0
        for i in range(current_minister.corruption_evidence):
            if random.randrange(1, 7) == 1 and random.randrange(1, 7) == 1:
                evidence_lost += 1
        if evidence_lost > 0:
            if current_minister.current_position == 'none':
                current_position = ''
            else:
                current_position = current_minister.current_position
            if evidence_lost == current_minister.corruption_evidence:
                current_minister.display_message("All of the " + str(current_minister.corruption_evidence) + " evidence of " + current_position + " " + current_minister.name + "'s corruption has lost potency over time and will no longer be usable in trials against him. /n /n")
            else:
                current_minister.display_message(str(evidence_lost) + " of the " + str(current_minister.corruption_evidence) + " evidence of " + current_position + " " + current_minister.name + "'s corruption has lost potency over time and will no longer be usable in trials against him. /n /n")
            current_minister.corruption_evidence -= evidence_lost

    if global_manager.get('prosecution_bribed_judge'):
        text_tools.print_to_screen("The effect of bribing the judge has faded and will not affect the next trial.", global_manager)
    global_manager.set('prosecution_bribed_judge', False)
            
    while len(removed_ministers) > 0:
        current_minister = removed_ministers.pop(0)
        current_minister.respond('retirement')

        #notification_tools.display_notification(text, 'default', global_manager)
        
        if not current_minister.current_position == 'none':
            current_minister.appoint('none')
        current_minister.remove()

    if (len(global_manager.get('minister_list')) <= global_manager.get('minister_limit') - 2 and random.randrange(1, 7) == 1) or len(global_manager.get('minister_list')) <= 9: #chance if at least 2 missing or guaranteed if not enough to fill cabinet
        while len(global_manager.get('minister_list')) < global_manager.get('minister_limit'):
            global_manager.get('actor_creation_manager').create_minister(global_manager)
        notification_tools.display_notification("Several new ministers candidates are available for appointment and can be found in the available minister pool. /n /n", 'default', global_manager)
    first_roll = random.randrange(1, 7)
    second_roll = random.randrange(1, 7)
    if first_roll == 1 and second_roll <= 3:
        global_manager.get('fear_tracker').change(-1)

def game_end_check(global_manager):
    '''
    Description:
        Checks each turn if the company is below 0 money, causing the player to lose the game
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    if global_manager.get('money') < 0:
        global_manager.set('game_over', True)
        text = ""
        text += "Your company does not have enough money to pay its expenses and has gone bankrupt. /n /nGAME OVER"
        notification_tools.display_choice_notification(text, ['confirm main menu', 'quit'], {}, global_manager)

def manage_commodity_sales(global_manager):
    '''
    Description:
        Orders the minister of trade to process all commodity sales started in the player's turn, allowing the minister to use skill/corruption to modify how much money is received by the company
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    sold_commodities = global_manager.get('sold_commodities')
    trade_minister = global_manager.get('current_ministers')[global_manager.get('type_minister_dict')['trade']]
    stealing = False
    money_stolen = 0
    text = trade_minister.current_position + " " + trade_minister.name + " reports the following commodity sales: /n /n"
    any_sold = False
    for current_commodity in global_manager.get('commodity_types'):
        if sold_commodities[current_commodity] > 0:
            any_sold = True
            sell_price = global_manager.get('commodity_prices')[current_commodity]
            expected_revenue = sold_commodities[current_commodity] * sell_price
            expected_revenue = global_manager.get('current_ministers')['Prosecutor'].estimate_expected(expected_revenue, False)
            actual_revenue = 0
                
            for i in range(sold_commodities[current_commodity]):
                individual_sell_price = sell_price + random.randrange(-1, 2) + trade_minister.get_roll_modifier()
                if trade_minister.check_corruption() and individual_sell_price > 1:
                    money_stolen += 1
                    individual_sell_price -= 1
                if individual_sell_price < 1:
                    individual_sell_price = 1
                global_manager.get('money_tracker').change(individual_sell_price, 'commodities sold')
                actual_revenue += individual_sell_price
                if random.randrange(1, 7) <= 1: #1/6 chance
                    market_tools.change_price(current_commodity, -1, global_manager)

            text += str(sold_commodities[current_commodity]) + " " + current_commodity + " sold for " + str(actual_revenue) + " money (expected " + str(expected_revenue) + ") /n /n"

    if any_sold:
        trade_minister.display_message(text)
    if money_stolen > 0:
        trade_minister.steal_money(money_stolen, 'sold commodities')

    for current_commodity in global_manager.get('commodity_types'):
        global_manager.get('sold_commodities')[current_commodity] = 0
