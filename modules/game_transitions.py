#Contains functions used when switching between parts of the game, like loading screen display

import time
from . import main_loop_tools
from . import text_tools
from . import tiles
from . import actor_utility
from . import minister_utility
from . import scaling

def cycle_player_turn(global_manager, start_of_turn = False):
    '''
    Description:
        Selects the next unit in the turn order, or gives a message if none remain
    Input:
        global_manager_template global_manager: Object that accesses shared variables
        boolean start_of_turn = False: Whether this is occuring automatically at the start of the turn or due to a player action during the turn
    Output:
        None
    '''
    turn_queue = global_manager.get('player_turn_queue')
    if len(turn_queue) == 0:
        if not start_of_turn:
            text_tools.print_to_screen("There are no units left to move this turn.", global_manager)
            actor_utility.deselect_all(global_manager)
            actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('mob_info_display_list'), 'none')
    else:
        if len(turn_queue) == 1 and not start_of_turn:
            text_tools.print_to_screen("There are no units left to move this turn.", global_manager)
        if global_manager.get('current_game_mode') == 'europe' and turn_queue[0].grids[0] == global_manager.get('strategic_map_grid'):
            set_game_mode('strategic', global_manager)
        if not turn_queue[0].selected:
            turn_queue[0].selection_sound()
        turn_queue[0].select()
        turn_queue[0].move_to_front()
        if not turn_queue[0].grids[0].mini_grid == 'none':
            turn_queue[0].grids[0].mini_grid.calibrate(turn_queue[0].x, turn_queue[0].y)
        else:
            actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('tile_info_display_list'), turn_queue[0].images[0].current_cell.tile)
        if not start_of_turn:
            turn_queue.append(turn_queue.pop(0))

def set_game_mode(new_game_mode, global_manager):
    '''
    Description:
        Changes the current game mode to the inputted game mode, changing which objects can be displayed and interacted with
    Input:
        string new_game_mode: Game mode that this switches to, like 'strategic', global_manager_template object
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    text_list = []
    previous_game_mode = global_manager.get('current_game_mode')
    if new_game_mode == previous_game_mode:
        return()
    else:
        if not (new_game_mode == 'trial' or global_manager.get('current_game_mode') == 'trial'): #the trial screen is not considered a full game mode by buttons that switch back to the previous game mode
            global_manager.set('previous_game_mode', global_manager.get('current_game_mode'))
        start_loading(global_manager)
        if new_game_mode == 'strategic':
            global_manager.set('current_game_mode', 'strategic')
            global_manager.set('default_text_box_height', scaling.scale_height(90, global_manager))#global_manager.set('default_text_box_height', 185)
            global_manager.set('text_box_height', global_manager.get('default_text_box_height'))
            #text_tools.print_to_screen("Entering strategic map", global_manager)
            centered_cell_x, centered_cell_y = global_manager.get('minimap_grid').center_x, global_manager.get('minimap_grid').center_y
            actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('tile_info_display_list'), global_manager.get('strategic_map_grid').find_cell(centered_cell_x, centered_cell_y).tile)
                #calibrate tile info to minimap center
        elif new_game_mode == 'europe':
            global_manager.set('current_game_mode', 'europe')
            #text_tools.print_to_screen("Entering European Company Headquarters", global_manager)
            actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('tile_info_display_list'), global_manager.get('europe_grid').cell_list[0].tile) #calibrate tile info to Europe
        elif new_game_mode == 'main menu':
            global_manager.set('current_game_mode', 'main_menu')
            global_manager.set('text_list', []) #clear text box when going to main menu
        elif new_game_mode == 'ministers':
            global_manager.set('current_game_mode', 'ministers')
            #text_tools.print_to_screen("Entering minister conference room", global_manager)
        elif new_game_mode == 'trial':
            global_manager.set('current_game_mode', 'trial')
        else:
            global_manager.set('default_text_box_height', scaling.scale_height(90, global_manager))#global_manager.set('default_text_box_height', 185)
            global_manager.set('text_box_height', global_manager.get('default_text_box_height'))
            global_manager.set('current_game_mode', new_game_mode)
    for current_mob in global_manager.get('mob_list'):
        current_mob.selected = False
        
    if previous_game_mode in ['strategic', 'europe']:
        actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('mob_info_display_list'), 'none') #deselect actors/ministers and remove any actor info from display when switching screens
        actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('minister_info_display_list'), 'none')

    if new_game_mode == 'ministers':
        global_manager.set('available_minister_left_index', -2)
        minister_utility.update_available_minister_display(global_manager)
        minister_utility.calibrate_minister_info_display(global_manager, 'none')
        
    elif previous_game_mode == 'trial':
        minister_utility.calibrate_trial_info_display(global_manager, global_manager.get('defense_info_display_list'), 'none')
        minister_utility.calibrate_trial_info_display(global_manager, global_manager.get('prosecution_info_display_list'), 'none')
    if global_manager.get('startup_complete'):
        global_manager.get('notification_manager').update_notification_layout()
    
def create_strategic_map(global_manager):
    '''
    Description:
        Creates a tile attached to each cell of each grid and randomly sets resources and villages when applicable
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    #text_tools.print_to_screen('Creating map...', global_manager)
    main_loop_tools.update_display(global_manager)

    for current_grid in global_manager.get('grid_list'):
        if current_grid in global_manager.get('abstract_grid_list'): #if europe/slave traders grid
            input_dict = {}
            input_dict['grid'] = current_grid
            input_dict['image'] = current_grid.tile_image_id
            input_dict['name'] = current_grid.name
            input_dict['modes'] = current_grid.modes
            new_terrain = tiles.abstract_tile(False, input_dict, global_manager)
        else:
            input_dict = {}
            input_dict['grid'] = current_grid
            input_dict['image'] = 'misc/empty.png'
            input_dict['name'] = 'default'
            input_dict['modes'] = ['strategic']
            input_dict['show_terrain'] = True
            for current_cell in current_grid.cell_list:
                input_dict['coordinates'] = (current_cell.x, current_cell.y)
                new_terrain = tiles.tile(False, input_dict, global_manager)
            current_grid.set_resources()

def start_loading(global_manager):
    '''
    Description:
        Records when loading started and displays a loading screen when the program is launching or switching between game modes
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    global_manager.set('loading', True)
    global_manager.set('loading_start_time', time.time())
    main_loop_tools.update_display(global_manager)

def to_main_menu(global_manager, override = False):
    '''
    Description:
        Exits the game to the main menu without saving
    Input:
        global_manager_template global_manager: Object that accesses shared variables
        boolean override = False: If True, forces game to exit to main menu regardless of current game circumstances
    Output:
        None
    '''
    #if main_loop_tools.action_possible(global_manager) or override: #if game over, go to main menu regardless of circumstances
    actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('mob_info_display_list'), 'none')
    actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('tile_info_display_list'), 'none')
    minister_utility.calibrate_minister_info_display(global_manager, 'none')
    set_game_mode('main_menu', global_manager)
    for current_actor in global_manager.get('actor_list'):
        current_actor.remove()
    for current_grid in global_manager.get('grid_list'):
        current_grid.remove()
    for current_village in global_manager.get('village_list'):
        current_village.remove()
    for current_minister in global_manager.get('minister_list'):
        current_minister.remove()
    for current_notification in global_manager.get('notification_list'):
        current_notification.remove()
    for current_die in global_manager.get('dice_list'):
        current_die.remove()
    global_manager.set('loan_list', [])
    global_manager.set('displayed_mob', 'none')
    global_manager.set('displayed_tile', 'none')
    global_manager.set('end_turn_selected_mob', 'none')
    global_manager.set('message', '')
    global_manager.set('player_turn_queue', [])
    if not global_manager.get('current_instructions_page') == 'none':
        global_manager.get('current_instructions_page').remove()
        global_manager.set('current_instructions_page', 'none')
