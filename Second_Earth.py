import pygame
import time
import random
import os
import logging

import modules.scaling as scaling
import modules.main_loop as main_loop
import modules.images as images
import modules.buttons as buttons
import modules.game_transitions as game_transitions
import modules.data_managers as data_managers
import modules.europe_transactions as europe_transactions
import modules.labels as labels
import modules.actor_display_tools.images as actor_display_images
import modules.actor_display_tools.labels as actor_display_labels
import modules.instructions as instructions
import modules.mouse_followers as mouse_followers
import modules.save_load_tools as save_load_tools
import modules.actor_creation_tools as actor_creation_tools
import modules.actor_utility as actor_utility

try:
    #fundamental setup
    pygame.init()
    pygame.mixer.init()

    global_manager = data_managers.global_manager_template()#manager of a dictionary of what would be global variables passed between functions and classes
    global_manager.set('startup_complete', False)
    global_manager.set('sound_manager', data_managers.sound_manager_template(global_manager))
    #global_manager.get('sound_manager').play_music('waltz_2')
    global_manager.set('save_load_manager', save_load_tools.save_load_manager_template(global_manager))
    global_manager.set('europe_grid', 'none')
    resolution_finder = pygame.display.Info()
    global_manager.set('default_display_width', 1728)#all parts of game made to be at default and scaled to display
    global_manager.set('default_display_height', 972)
    global_manager.set('display_width', resolution_finder.current_w - round(global_manager.get('default_display_width')/10))
    global_manager.set('display_height', resolution_finder.current_h - round(global_manager.get('default_display_height')/10))
    
    global_manager.set('loading', True)
    global_manager.set('loading_start_time', time.time())
    global_manager.set('previous_turn_time', time.time())
    global_manager.set('end_turn_wait_time', 0.8)

    global_manager.set('font_name', 'times new roman')
    global_manager.set('font_size', scaling.scale_width(15, global_manager))
    global_manager.set('myfont', pygame.font.SysFont(global_manager.get('font_name'), global_manager.get('font_size')))

    global_manager.set('game_display', pygame.display.set_mode((global_manager.get('display_width'), global_manager.get('display_height'))))

    pygame.display.set_caption('SFA')
    global_manager.set('color_dict',
        {
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'light gray': (230, 230, 230),
        'gray': (190, 190, 190),
        'dark gray': (150, 150, 150),
        'bright red': (255, 0, 0),
        'red': (200, 0, 0),
        'dark red': (150, 0, 0),
        'bright green': (0, 255, 0),
        'green': (0, 200, 0),
        'dark green': (0, 150, 0),
        'green': (0, 200, 0),
        'dark green': (0, 150, 0),
        'bright blue': (0, 0, 255),
        'blue': (0, 0, 200),
        'dark blue': (0, 0, 150),
        'yellow': (255, 255, 0),
        'brown': (132, 94, 59),
        'purple': (127, 0, 170)
        #'purple': (191, 0, 255)
        }
    )
    #fundamental setup



    #terrain setup
    terrain_list = ['clear', 'mountain', 'hills', 'jungle', 'swamp', 'desert']
    global_manager.set('terrain_list', terrain_list)

    global_manager.set('terrain_colors',
        {
        'clear': (150, 200, 104),
        'hills': (50, 205, 50),
        'jungle': (0, 100, 0),
        'water': (0, 0, 200),
        'mountain': (100, 100, 100),
        'swamp': (100, 100, 50),
        'desert': (255, 248, 104),
        'none': (0, 0, 0)
        }
    )

    global_manager.set('terrain_animal_dict',
        {
        'clear': ['lion', 'bull elephant', 'Cape buffalo'],
        'hills': ['gorilla', 'Cape buffalo', 'hippopotamus'],
        'jungle': ['gorilla', 'crocodile', 'leopard'],
        'water': ['crocodile', 'hippopotamus', 'leopard'],
        'mountain': ['lion', 'gorilla', 'leopard'],
        'swamp': ['bull elephant', 'crocodile', 'hippopotamus'],
        'desert': ['lion', 'bull elephant', 'Cape buffalo']
        }
    )
    
    global_manager.set('animal_terrain_dict',
        {
        'lion': ['clear', 'desert', 'mountain'],
        'bull elephant': ['clear', 'swamp', 'desert'],
        'Cape buffalo': ['clear', 'hills', 'desert'],
        'crocodile': ['water', 'swamp', 'jungle'],
        'hippopotamus': ['water', 'swamp', 'hills'],
        'gorilla': ['mountain', 'jungle', 'hills'],
        'leopard': ['jungle', 'mountain', 'water']
        }
    )

    global_manager.set('animal_adjectives', ['man-eating', 'bloodthirsty', 'rampaging', 'giant', 'ravenous', 'ferocious', 'king', 'lurking', 'spectral', 'infernal'])

    global_manager.set('terrain_movement_cost_dict',
        {
        'clear': 1,
        'hills': 2,
        'jungle': 3,
        'water': 1,
        'mountain': 3,
        'swamp': 3,
        'desert': 2
        }
    )

    global_manager.set('terrain_build_cost_multiplier_dict',
        {
        'clear': 1,
        'hills': 2,
        'jungle': 3,
        'water': 1,
        'mountain': 3,
        'swamp': 3,
        'desert': 2
        }
    )
    
    #terrain setup



    #commodity setup
    global_manager.set('commodity_types', ['consumer goods', 'coffee', 'copper', 'diamond', 'exotic wood', 'fruit', 'gold', 'iron', 'ivory', 'rubber'])
    global_manager.set('collectable_resources', ['coffee', 'copper', 'diamond', 'exotic wood', 'fruit', 'gold', 'iron', 'ivory', 'rubber'])
    global_manager.set('commodity_prices', {})
    global_manager.set('sold_commodities', {})

    for current_commodity in global_manager.get('commodity_types'):
        global_manager.get('commodity_prices')[current_commodity] = 0
        global_manager.get('sold_commodities')[current_commodity] = 0

    global_manager.set('commodities_produced', {})
    for current_commodity in global_manager.get('collectable_resources'):
        global_manager.get('commodities_produced')[current_commodity] = 0

    global_manager.set('resource_building_dict',
        {
        'coffee': 'buildings/plantation.png',
        'copper': 'buildings/mine.png',
        'diamond': 'buildings/mine.png',
        'exotic wood': 'buildings/plantation.png',
        'fruit': 'buildings/plantation.png',
        'gold': 'buildings/mine.png',
        'iron': 'buildings/mine.png',
        'ivory': 'buildings/camp.png',
        'rubber': 'buildings/plantation.png',
        }
    )

    global_manager.set('resource_building_button_dict',
        {
        'coffee': 'scenery/resources/production/coffee.png',
        'copper': 'scenery/resources/production/copper.png',
        'diamond': 'scenery/resources/production/diamond.png',
        'exotic wood': 'scenery/resources/production/exotic wood.png',
        'fruit': 'scenery/resources/production/fruit.png',
        'gold': 'scenery/resources/production/gold.png',
        'iron': 'scenery/resources/production/iron.png',
        'ivory': 'scenery/resources/production/ivory.png',
        'rubber': 'scenery/resources/production/rubber.png',
        'none': 'scenery/resources/production/none.png',
        }
    )

    for current_commodity in global_manager.get('commodity_types'):
        global_manager.set(current_commodity + ' buy button', 'none')

    global_manager.set('resource_types', global_manager.get('commodity_types') + ['natives'])

    global_manager.set('building_types', ['resource', 'port', 'infrastructure', 'train_station', 'trading_post', 'mission', 'fort', 'slums', 'warehouses'])
    #commodity setup



    #minister setup
    global_manager.set('weighted_backgrounds', [
        'lowborn', 'lowborn', 'lowborn', 'lowborn', 'lowborn',
        'banker',
        'merchant',
        'lawyer',
        'industrialist', 'industrialist', 'industrialist',
        'natural scientist',
        'doctor',
        'aristocrat', 'aristocrat', 'aristocrat', 'aristocrat',
        'royal heir',
        'politician', 'politician',
        'army officer',
        'naval officer',
        'priest'
        ]
    ) #5 low, 9 middle, 9 high, 1 very high

    global_manager.set('background_status_dict', {
        'lowborn': 1,
        'banker': 2,
        'merchant': 2,
        'lawyer': 2,
        'army officer': 2,
        'naval officer': 2,
        'priest': 2,
        'natural scientist': 2, 
        'doctor': 2,
        'industrialist': 3,
        'aristocrat': 3,
        'politician': 3,
        'royal heir': 4
        }
    )

    global_manager.set('background_skills_dict', {
        'lowborn': ['none'],
        'banker': ['trade'],
        'merchant': ['trade'],
        'lawyer': ['prosecution'],
        'army officer': ['military'],
        'naval officer': ['transportation'],
        'priest': ['religion'],
        'natural scientist': ['exploration'],
        'doctor': ['random'],
        'industrialist': ['construction', 'production', 'transportation'],
        'aristocrat': ['none', 'random'],
        'politician': ['none', 'random'],
        'royal heir': ['none', 'random']
        }
    )

    global_manager.set('skill_types', ['military', 'religion', 'trade', 'exploration', 'construction', 'production', 'transportation', 'prosecution'])
    global_manager.set('minister_types', ['General', 'Bishop', 'Minister of Trade', 'Minister of Geography', 'Minister of Engineering', 'Minister of Production', 'Minister of Transportation', 'Prosecutor'])
    global_manager.set('type_minister_dict',
        {
        'military': 'General',
        'religion': 'Bishop',
        'trade': 'Minister of Trade',
        'exploration': 'Minister of Geography',
        'construction': 'Minister of Engineering',
        'production': 'Minister of Production',
        'transportation': 'Minister of Transportation',
        'prosecution': 'Prosecutor'
        }
    )
    global_manager.set('minister_type_dict',
        {
        'General': 'military',
        'Bishop': 'religion',
        'Minister of Trade': 'trade',
        'Minister of Geography': 'exploration',
        'Minister of Engineering': 'construction',
        'Minister of Production': 'production',
        'Minister of Transportation': 'transportation',
        'Prosecutor': 'prosecution'
        }
    )
    global_manager.set('current_ministers', {})
    for current_minister_type in global_manager.get('minister_types'):
        global_manager.get('current_ministers')[current_minister_type] = 'none'

    minister_portraits = [] #put all images in graphics/minister/portraits folder in list
    for file_name in os.listdir('graphics/ministers/portraits'):
        if file_name.endswith('.png'): 
            minister_portraits.append('ministers/portraits/' + file_name)
            continue
        else:
            continue
    global_manager.set('minister_portraits', minister_portraits)


    global_manager.set('officer_types', ['explorer', 'hunter', 'engineer', 'driver', 'foreman', 'merchant', 'evangelist', 'major']) #change to driver
    global_manager.set('officer_group_type_dict',
        {
        'explorer': 'expedition',
        'hunter': 'safari',
        'engineer': 'construction_gang',
        'driver': 'porters',
        'foreman': 'work_crew',
        'merchant': 'caravan',
        'evangelist': 'missionaries',
        'major': 'battalion'
        }
    )

    type_minister_dict = global_manager.get('type_minister_dict')
    global_manager.set('officer_minister_dict',
        {
        'explorer': type_minister_dict['exploration'],
        'hunter': type_minister_dict['exploration'],
        'engineer': type_minister_dict['construction'],
        'driver': type_minister_dict['transportation'],
        'foreman': type_minister_dict['production'],
        'merchant': type_minister_dict['trade'],
        'evangelist': type_minister_dict['religion'],
        'major': type_minister_dict['military']
        }
    )

    global_manager.set('group_minister_dict',
        {
        'expedition': type_minister_dict['exploration'],
        'safari': type_minister_dict['exploration'],
        'construction_gang': type_minister_dict['construction'],
        'porters': type_minister_dict['transportation'],
        'work_crew': type_minister_dict['production'],
        'caravan': type_minister_dict['trade'],
        'missionaries': type_minister_dict['religion'],
        'battalion': type_minister_dict['military']
        }
    )
    #minister setup



    #price setup
    
    global_manager.set('recruitment_types', global_manager.get('officer_types') + ['European workers', 'steamship'])
    global_manager.set('recruitment_costs', {'European workers': 0, 'steamship': 10})
    for current_officer in global_manager.get('officer_types'):
        global_manager.get('recruitment_costs')[current_officer] = 5

    global_manager.set('num_african_workers', 0)
    global_manager.set('african_worker_upkeep', 0) #placeholder for labels, set to initial values on load/new game
    global_manager.set('initial_african_worker_upkeep', 4)
    global_manager.set('min_african_worker_upkeep', 0.5)

    global_manager.set('num_european_workers', 0)
    global_manager.set('european_worker_upkeep', 0)
    global_manager.set('initial_european_worker_upkeep', 6)
    global_manager.set('min_european_worker_upkeep', 0.5)

    global_manager.set('num_slave_workers', 0)
    global_manager.set('initial_slave_worker_upkeep', 2)
    global_manager.set('slave_worker_upkeep', 0)
    global_manager.set('base_slave_recruitment_cost', 5)
    global_manager.get('recruitment_costs')['slave workers'] = global_manager.get('base_slave_recruitment_cost')
    global_manager.set('min_slave_worker_recruitment_cost', 2)

    global_manager.set('recruitment_list_descriptions', {})
    global_manager.set('recruitment_string_descriptions', {})
    actor_utility.update_recruitment_descriptions(global_manager)

    global_manager.set('worker_upkeep_fluctuation_amount', 0.25)
    global_manager.set('slave_recruitment_cost_fluctuation_amount', 1)
    global_manager.set('base_upgrade_price', 20) #20 for 1st upgrade, 40 for 2nd, 80 for 3rd, etc.
    global_manager.set('commodity_min_starting_price', 2)
    global_manager.set('commodity_max_starting_price', 5)
    global_manager.set('consumer_goods_starting_price', 1)

    global_manager.set('action_types', ['exploration', 'convert', 'religious_campaign', 'public_relations_campaign', 'advertising_campaign', 'loan_search', 'trade', 'loan', 'attack', 'capture_slaves', 'trial', 'hunt', 'track_beasts'])
    global_manager.set('base_action_prices',
        {
        'exploration': 5,
        'convert': 5,
        'religious_campaign': 5,
        'public_relations_campaign': 5,
        'advertising_campaign': 5,
        'loan_search': 5,
        'trade': 0,
        'loan': 5,
        'attack': 5,
        'capture_slaves': 5,
        'trial': 5,
        'hunt': 5,
        'track_beasts': 0
        }
    )

    global_manager.set('action_prices', {})
    actor_utility.reset_action_prices(global_manager)    

    global_manager.set('building_prices',
        {
        'resource': 10,
        'road': 5,
        'railroad': 15,
        'port': 15,
        'train_station': 10,
        'trading_post': 5,
        'mission': 5,
        'fort': 5,
        'warehouses': 5,
        'train': 10,
        'steamboat': 10
       } 
    )
    
    #central place in program to change descriptions of actions to use in prosector reports
    global_manager.set('theft_type_descriptions',
        {
        'trial fees': 'trial fees',
        'bribery': 'bribery',
        'loan interest': 'loan interest',
        'exploration': 'exploration',
        'religious campaign': 'religious campaigning',
        'public relations campaign': 'public relations campaigning',
        'advertising campaign': 'advertising',
        'trade': 'trading with natives',
        'construction': 'construction',
        'conversion': 'religious conversion',
        'inventory attrition': 'missing commodities',
        'combat': 'combat supplies',
        'hunting': 'hunting supplies',
        'production': 'production',
        'slave capture': 'capturing slaves',
        'sold commodities': 'commodity sales',
        'none': 'miscellaneous company activities'
        }
    )

    global_manager.set('transaction_types', ['misc. revenue', 'misc. expenses', 'worker upkeep', 'subsidies', 'advertising', 'commodities sold', 'trial compensation', 'consumer goods', 'exploration', 'religious campaigns',
        'public relations campaigns', 'religious conversion', 'unit recruitment', 'loan interest', 'loans', 'loan searches', 'combat supplies', 'hunting supplies', 'construction', 'attrition replacements', 'trial fees', 'slave capture'])
    #price setup



    #misc. setup
    global_manager.get('game_display').fill(global_manager.get('color_dict')['white'])
    global_manager.set('button_list', [])
    global_manager.set('current_instructions_page', 'none')
    global_manager.set('current_dice_rolling_notification', 'none')
    global_manager.set('current_instructions_page_index', 0)
    global_manager.set('instructions_list', [])
    #page 1
    instructions_message = "Placeholder instructions, use += to add"
    global_manager.get('instructions_list').append(instructions_message)

    global_manager.set('minister_list', [])
    global_manager.set('available_minister_list', [])
    global_manager.set('grid_list', [])
    global_manager.set('grid_types_list', ['strategic_map_grid', 'europe_grid', 'slave_traders_grid'])
    global_manager.set('abstract_grid_list', [])
    global_manager.set('text_list', [])
    global_manager.set('image_list', [])
    global_manager.set('free_image_list', [])
    global_manager.set('minister_image_list', [])
    global_manager.set('available_minister_portrait_list', [])
    global_manager.set('background_image_list', [])
    global_manager.set('actor_list', [])
    global_manager.set('mob_list', [])
    global_manager.set('pmob_list', [])
    global_manager.set('npmob_list', [])
    global_manager.set('beast_list', [])
    global_manager.set('village_list', [])
    global_manager.set('building_list', [])
    global_manager.set('slums_list', [])
    global_manager.set('resource_building_list', [])
    global_manager.set('infrastructure_connection_list', [])
    global_manager.set('officer_list', [])
    global_manager.set('worker_list', [])
    global_manager.set('loan_list', [])
    global_manager.set('attacker_queue', [])
    global_manager.set('enemy_turn_queue', [])
    global_manager.set('player_turn_queue', [])

    global_manager.set('minister_limit', 15)

    global_manager.set('group_list', [])
    global_manager.set('tile_list', [])
    global_manager.set('exploration_mark_list', [])
    global_manager.set('overlay_tile_list', [])
    global_manager.set('notification_list', [])
    global_manager.set('label_list', [])
    global_manager.set('mob_info_display_list', [])
    global_manager.set('mob_ordered_label_list', [])
    global_manager.set('minister_info_display_list', [])
    global_manager.set('minister_ordered_label_list', [])
    global_manager.set('displayed_mob', 'none')
    global_manager.set('displayed_minister', 'none')
    global_manager.set('displayed_defense', 'none')
    global_manager.set('displayed_prosecution', 'none')
    global_manager.set('tile_info_display_list', [])
    global_manager.set('tile_ordered_label_list', [])
    global_manager.set('prosecution_info_display_list', [])
    global_manager.set('displayed_tile', 'none')
    global_manager.set('dice_list', [])
    global_manager.set('dice_roll_minister_images', [])
    global_manager.set('combatant_images', [])
    pygame.key.set_repeat(300, 200)
    global_manager.set('crashed', False)
    global_manager.set('lmb_down', False)
    global_manager.set('rmb_down', False)
    global_manager.set('mmb_down', False)
    global_manager.set('typing', False)
    global_manager.set('message', '')
    global_manager.set('show_grid_lines', True)
    global_manager.set('show_text_box', True)
    global_manager.set('show_selection_outlines', True)
    global_manager.set('show_minimap_outlines', True)
    global_manager.set('making_choice', False)
    global_manager.set('loading_save', False)
    global_manager.set('player_turn', True)
    global_manager.set('enemy_combat_phase', False)
    global_manager.set('choosing_destination', False)
    global_manager.set('choosing_destination_info_dict', {})
    global_manager.set('choosing_advertised_commodity', False)
    global_manager.set('choosing_advertised_commodity_info_dict', {})
    global_manager.set('drawing_automatic_route', False)
    global_manager.set('prosecution_bribed_judge', False)

    global_manager.set('ongoing_exploration', False)
    global_manager.set('ongoing_trade', False)
    global_manager.set('ongoing_religious_campaign', False)
    global_manager.set('ongoing_public_relations_campaign', False)
    global_manager.set('ongoing_advertising_campaign', False)
    global_manager.set('ongoing_loan_search', False)
    global_manager.set('ongoing_conversion', False)
    global_manager.set('ongoing_construction', False)
    global_manager.set('ongoing_combat', False)
    global_manager.set('ongoing_trial', False)
    global_manager.set('ongoing_slave_capture', False)
    global_manager.set('game_over', False)

    global_manager.set('r_shift', 'up')
    global_manager.set('l_shift', 'up')
    global_manager.set('capital', False)
    global_manager.set('r_ctrl', 'up')
    global_manager.set('l_ctrl', 'up')
    global_manager.set('ctrl', 'up')
    global_manager.set('start_time', time.time())
    global_manager.set('current_time', time.time())
    global_manager.set('last_selection_outline_switch', time.time())
    mouse_moved_time = time.time()
    global_manager.set('mouse_moved_time', time.time())
    old_mouse_x, old_mouse_y = pygame.mouse.get_pos()#used in tooltip drawing timing
    global_manager.set('old_mouse_x', old_mouse_x)
    global_manager.set('old_mouse_y', old_mouse_y)
    global_manager.set('available_minister_left_index', -2) #so that first index is in middle
    global_manager.set('flavor_text_manager', data_managers.flavor_text_manager_template(global_manager))
    global_manager.set('loading_image', images.loading_image_template('misc/loading.png', global_manager))
    global_manager.set('current_game_mode', 'none')
    global_manager.set('input_manager', data_managers.input_manager_template(global_manager))
    global_manager.set('actor_creation_manager', actor_creation_tools.actor_creation_manager_template())

    strategic_background_image = images.free_image('misc/background.png', (0, 0), global_manager.get('display_width'), global_manager.get('display_height'), ['strategic', 'europe', 'main_menu', 'ministers', 'trial'], global_manager)
    global_manager.get('background_image_list').append(strategic_background_image)
    strategic_grid_height = 300#450
    strategic_grid_width = 320#480
    mini_grid_height = 600#450
    mini_grid_width = 640#480

    global_manager.set('minimap_grid_origin_x', global_manager.get('default_display_width') - (mini_grid_width + 100))

    europe_grid_x = global_manager.get('default_display_width') - (strategic_grid_width + 340)
    europe_grid_y = global_manager.get('default_display_height') - (strategic_grid_height + 25)

    global_manager.set('mob_ordered_list_start_y', 0)
    global_manager.set('tile_ordered_list_start_y', 0)
    global_manager.set('minister_ordered_list_start_y', 0)

    global_manager.set('current_game_mode', 'main menu') #initial previous game mode
    game_transitions.set_game_mode('main_menu', global_manager)

    global_manager.set('mouse_follower', mouse_followers.mouse_follower(global_manager))
    #misc. setup



    #value tracker setup
    global_manager.set('public_opinion_tracker', data_managers.value_tracker('public_opinion', 0, 0, 100, global_manager))
    labels.value_label(scaling.scale_coordinates(330, global_manager.get('default_display_height') - 70, global_manager), scaling.scale_width(10, global_manager), scaling.scale_height(30, global_manager), ['strategic', 'europe', 'ministers'],
        'misc/default_label.png', 'public_opinion', global_manager)
    
    global_manager.set('money_tracker', data_managers.money_tracker(100, global_manager))
    labels.money_label(scaling.scale_coordinates(330, global_manager.get('default_display_height') - 30, global_manager), scaling.scale_width(10, global_manager), scaling.scale_height(30, global_manager),
        ['strategic', 'europe', 'ministers', 'trial'], 'misc/default_label.png', global_manager)

    global_manager.set('previous_financial_report', 'none')
    show_previous_financial_report_button = buttons.show_previous_financial_report_button(scaling.scale_coordinates(300, global_manager.get('default_display_height') - 30, global_manager), scaling.scale_width(30, global_manager),
        scaling.scale_height(30, global_manager), 'none', ['strategic', 'europe', 'ministers', 'trial'], 'buttons/instructions.png', global_manager)

    global_manager.set('turn_tracker', data_managers.value_tracker('turn', 0, 'none', 'none', global_manager))
    labels.value_label(scaling.scale_coordinates(545, global_manager.get('default_display_height') - 30, global_manager), scaling.scale_width(10, global_manager), scaling.scale_height(30, global_manager), ['strategic', 'europe', 'ministers'],
        'misc/default_label.png', 'turn', global_manager)
    
    global_manager.set('evil_tracker', data_managers.value_tracker('evil', 0, 0, 100, global_manager))
    
    global_manager.set('fear_tracker', data_managers.value_tracker('fear', 1, 1, 6, global_manager))
    #value tracker setup



    #button setup
    wake_up_all_button = buttons.button(scaling.scale_coordinates(165, global_manager.get('default_display_height') - 50, global_manager), scaling.scale_width(50, global_manager),
        scaling.scale_height(50, global_manager), 'blue', 'wake up all', 'none', ['strategic', 'europe'], 'buttons/disable_sentry_mode_button.png', global_manager)
    
    strategic_to_europe_button = buttons.switch_game_mode_button(scaling.scale_coordinates(europe_grid_x - 85, europe_grid_y, global_manager), scaling.scale_width(60, global_manager), scaling.scale_height(60, global_manager), 'blue',
        pygame.K_e, 'europe', ['strategic'], 'buttons/european_hq_button.png', global_manager)

    europe_to_strategic_button = buttons.switch_game_mode_button(scaling.scale_coordinates(europe_grid_x - 85, europe_grid_y, global_manager), scaling.scale_width(60, global_manager), scaling.scale_height(60, global_manager), 'blue',
        pygame.K_ESCAPE, 'strategic', ['europe'], 'buttons/exit_european_hq_button.png', global_manager)

    to_main_menu_button = buttons.switch_game_mode_button(scaling.scale_coordinates(global_manager.get('default_display_width') - 50, global_manager.get('default_display_height') - 50, global_manager),
        scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'blue', 'none', 'main menu', ['strategic', 'europe', 'ministers'], 'buttons/exit_european_hq_button.png', global_manager)

    to_ministers_button = buttons.switch_game_mode_button(scaling.scale_coordinates(0, global_manager.get('default_display_height') - 50, global_manager), scaling.scale_width(50, global_manager),
        scaling.scale_height(50, global_manager), 'blue', pygame.K_q, 'ministers', ['strategic', 'europe'], 'buttons/european_hq_button.png', global_manager)

    from_ministers_button = buttons.switch_game_mode_button(scaling.scale_coordinates(0, global_manager.get('default_display_height') - 50, global_manager), scaling.scale_width(50, global_manager),
        scaling.scale_height(50, global_manager), 'blue', pygame.K_ESCAPE, 'previous', ['ministers'], 'buttons/exit_european_hq_button.png', global_manager)

    from_trial_button = buttons.switch_game_mode_button(scaling.scale_coordinates(0, global_manager.get('default_display_height') - 50, global_manager), scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager),
        'blue', pygame.K_ESCAPE, 'ministers', ['trial'], 'buttons/exit_european_hq_button.png', global_manager)

    end_turn_button = buttons.end_turn_button(scaling.scale_coordinates(round(global_manager.get('default_display_width') * 0.4), global_manager.get('default_display_height') - 50,
        global_manager), scaling.scale_width(round(global_manager.get('default_display_width') * 0.2), global_manager), scaling.scale_height(50, global_manager), 'blue', pygame.K_SPACE, ['strategic', 'europe'],
        'buttons/end_turn_button.png', global_manager)

    new_game_button = buttons.button(scaling.scale_coordinates(round(global_manager.get('default_display_width') * 0.4), global_manager.get('default_display_height') / 2 - 50, global_manager),
        scaling.scale_width(round(global_manager.get('default_display_width') * 0.2), global_manager), scaling.scale_height(50, global_manager), 'blue', 'new game', pygame.K_n, ['main_menu'], 'buttons/new_game_button.png',
        global_manager)

    load_game_button = buttons.button(scaling.scale_coordinates(round(global_manager.get('default_display_width') * 0.4), global_manager.get('default_display_height') / 2 - 125, global_manager),
        scaling.scale_width(round(global_manager.get('default_display_width') * 0.2), global_manager), scaling.scale_height(50, global_manager), 'blue', 'load game', pygame.K_l, ['main_menu'], 'buttons/load_game_button.png',
        global_manager)


    button_start_x = 750#x position of leftmost button
    button_separation = 60#x separation between each button
    current_button_number = 0#tracks current button to move each one farther right

    left_arrow_button = buttons.button(scaling.scale_coordinates(button_start_x + (current_button_number * button_separation), 20, global_manager), scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'blue',
        'move left', pygame.K_a, ['strategic'], 'buttons/left_button.png', global_manager)
    current_button_number += 1

    down_arrow_button = buttons.button(scaling.scale_coordinates(button_start_x + (current_button_number * button_separation), 20, global_manager), scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'blue',
        'move down', pygame.K_s, ['strategic'], 'buttons/down_button.png', global_manager)#movement buttons should be usable in any mode with a grid


    up_arrow_button = buttons.button(scaling.scale_coordinates(button_start_x + (current_button_number * button_separation), 80, global_manager), scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'blue',
        'move up', pygame.K_w, ['strategic'], 'buttons/up_button.png', global_manager)
    current_button_number += 1

    right_arrow_button = buttons.button(scaling.scale_coordinates(button_start_x + (current_button_number * button_separation), 20, global_manager), scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'blue',
        'move right', pygame.K_d, ['strategic'], 'buttons/right_button.png', global_manager)


    expand_text_box_button = buttons.button(scaling.scale_coordinates(55, global_manager.get('default_display_height') - 50, global_manager), scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'black',
        'expand text box', pygame.K_j, ['strategic', 'europe', 'ministers'], 'buttons/text_box_size_button.png', global_manager) #'none' for no keybind

    #instructions_button = instructions.instructions_button(scaling.scale_coordinates(global_manager.get('default_display_width') - 50, global_manager.get('default_display_height') - 50, global_manager), scaling.scale_width(50, global_manager),
    #    scaling.scale_height(50, global_manager), 'blue', 'instructions', pygame.K_i, ['strategic', 'europe'], 'buttons/instructions.png', global_manager)

    save_game_button = buttons.button(scaling.scale_coordinates(global_manager.get('default_display_width') - 50, global_manager.get('default_display_height') - 125, global_manager), scaling.scale_width(50, global_manager),
        scaling.scale_height(50, global_manager), 'blue', 'save game', 'none', ['strategic', 'europe', 'ministers'], 'buttons/save_game_button.png', global_manager)

    cycle_units_button = buttons.button(scaling.scale_coordinates(110, global_manager.get('default_display_height') - 50, global_manager), scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'blue',
        'cycle units', pygame.K_TAB, ['strategic', 'europe'], 'buttons/cycle_units_button.png', global_manager)

    cycle_units_button = buttons.button(scaling.scale_coordinates(220, global_manager.get('default_display_height') - 50, global_manager), scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'blue',
        'execute movement routes', 'none', ['strategic', 'europe'], 'buttons/execute_movement_routes_button.png', global_manager)
    #button setup



    #trial setup
    trial_display_default_y = 500
    button_separation = 100
    distance_to_center = 300
    distance_to_notification = 100
    
    defense_current_y = trial_display_default_y
    defense_x = (global_manager.get('default_display_width') / 2) + (distance_to_center - button_separation) + distance_to_notification


    
    #defense_current_y -= button_separation * 2
    defense_type_image = images.minister_type_image(scaling.scale_coordinates(defense_x, defense_current_y, global_manager),
        scaling.scale_width(button_separation * 2 - 5, global_manager), scaling.scale_height(button_separation * 2 - 5, global_manager), ['trial'], 'none', 'none', global_manager)
    global_manager.get('defense_info_display_list').append(defense_type_image)

    defense_current_y -= button_separation * 2
    defense_portrait_image = buttons.minister_portrait_image(scaling.scale_coordinates(defense_x, defense_current_y, global_manager),
        scaling.scale_width(button_separation * 2 - 5, global_manager), scaling.scale_height(button_separation * 2 - 5, global_manager), ['trial'], 'none', global_manager)
    global_manager.get('defense_info_display_list').append(defense_portrait_image)

    defense_current_y -= 35
    defense_label = labels.label(scaling.scale_coordinates(defense_x, defense_current_y, global_manager), scaling.scale_width(10, global_manager), scaling.scale_height(30, global_manager), ['trial'],
        'misc/default_label.png', 'Defense', global_manager)

    defense_info_display_labels = ['minister_name', 'minister_office', 'evidence']
    for current_actor_label_type in defense_info_display_labels:
        defense_current_y -= 35
        global_manager.get('defense_info_display_list').append(actor_display_labels.actor_display_label(scaling.scale_coordinates(defense_x, defense_current_y, global_manager), scaling.scale_width(10, global_manager),
            scaling.scale_height(30, global_manager), ['trial'], 'misc/default_label.png', current_actor_label_type, 'minister', global_manager))    


    prosecution_current_y = trial_display_default_y
    prosecution_x = (global_manager.get('default_display_width') / 2) - (distance_to_center + button_separation) - distance_to_notification
    
    prosecution_type_image = images.minister_type_image(scaling.scale_coordinates(prosecution_x, prosecution_current_y, global_manager),
        scaling.scale_width(button_separation * 2 - 5, global_manager), scaling.scale_height(button_separation * 2 - 5, global_manager), ['trial'], 'none', 'none', global_manager)
    global_manager.get('prosecution_info_display_list').append(prosecution_type_image)

    prosecution_current_y -= button_separation * 2
    prosecution_portrait_image = buttons.minister_portrait_image(scaling.scale_coordinates(prosecution_x, prosecution_current_y, global_manager),
        scaling.scale_width(button_separation * 2 - 5, global_manager), scaling.scale_height(button_separation * 2 - 5, global_manager), ['trial'], 'none', global_manager)
    global_manager.get('prosecution_info_display_list').append(prosecution_portrait_image)

    prosecution_current_y -= 35
    prosecution_label = labels.label(scaling.scale_coordinates(prosecution_x, prosecution_current_y, global_manager), scaling.scale_width(10, global_manager), scaling.scale_height(30, global_manager), ['trial'],
        'misc/default_label.png', 'Prosecution', global_manager)

    prosecution_info_display_labels = ['minister_name', 'minister_office']
    for current_actor_label_type in prosecution_info_display_labels:
        prosecution_current_y -= 35
        global_manager.get('prosecution_info_display_list').append(actor_display_labels.actor_display_label(scaling.scale_coordinates(prosecution_x, prosecution_current_y, global_manager), scaling.scale_width(10, global_manager),
            scaling.scale_height(30, global_manager), ['trial'], 'misc/default_label.png', current_actor_label_type, 'minister', global_manager))    

    launch_trial_button_width = 150
    launch_trial_button = buttons.button(scaling.scale_coordinates((global_manager.get('default_display_width') / 2) - (launch_trial_button_width / 2), trial_display_default_y - 300, global_manager),
        scaling.scale_width(launch_trial_button_width, global_manager), scaling.scale_height(launch_trial_button_width, global_manager), 'blue', 'launch trial', 'none', ['trial'], 'buttons/to_trial_button.png', global_manager)

    bribed_judge_indicator = images.indicator_image('misc/bribed_judge.png', scaling.scale_coordinates((global_manager.get('default_display_width') / 2) - ((button_separation * 2 - 5) / 2), trial_display_default_y + 200, global_manager),
        scaling.scale_width(button_separation * 2 - 5, global_manager), scaling.scale_height(button_separation * 2 - 5, global_manager), ['trial'], 'prosecution_bribed_judge', global_manager)
    non_bribed_judge_indicator = images.indicator_image('misc/non_bribed_judge.png', scaling.scale_coordinates((global_manager.get('default_display_width') / 2) - ((button_separation * 2 - 5) / 2), trial_display_default_y + 200, global_manager),
        scaling.scale_width(button_separation * 2 - 5, global_manager), scaling.scale_height(button_separation * 2 - 5, global_manager), ['trial'], 'not prosecution_bribed_judge', global_manager)
        #image_id, coordinates, width, height, modes, indicator_type, global_manager
    #trial setup



    #minister info images setup
    minister_display_top_y = global_manager.get('default_display_height') - 205
    minister_display_current_y = minister_display_top_y
    global_manager.set('minister_ordered_list_start_y', minister_display_current_y)
    #minister background image
    minister_free_image_background = actor_display_images.minister_background_image('misc/mob_background.png', scaling.scale_coordinates(0, minister_display_current_y, global_manager), scaling.scale_width(125, global_manager),
        scaling.scale_height(125, global_manager), ['ministers'], global_manager)
    global_manager.get('minister_info_display_list').append(minister_free_image_background)

    #minister background image's tooltip
    minister_free_image_background_tooltip = actor_display_labels.actor_display_label(scaling.scale_coordinates(0, minister_display_current_y, global_manager), scaling.scale_width(125, global_manager), scaling.scale_height(125, global_manager),
        ['ministers'], 'misc/empty.png', 'tooltip', 'minister', global_manager) #coordinates, minimum_width, height, modes, image_id, actor_label_type, actor_type, global_manager
    global_manager.get('minister_info_display_list').append(minister_free_image_background_tooltip)

    #minister image
    minister_free_image = actor_display_images.actor_display_free_image(scaling.scale_coordinates(5, minister_display_current_y + 5, global_manager), scaling.scale_width(115, global_manager),
        scaling.scale_height(115, global_manager), ['ministers'], 'minister_default', global_manager) #coordinates, width, height, modes, global_manager
    global_manager.get('minister_info_display_list').append(minister_free_image)

    minister_display_current_y -= 35
    #minister info images setup



    #minister info labels setup
    minister_info_display_labels = ['minister_name', 'minister_office', 'background', 'social status', 'interests', 'evidence']
    for current_actor_label_type in minister_info_display_labels:
        x_displacement = 0
        global_manager.get('minister_info_display_list').append(actor_display_labels.actor_display_label(scaling.scale_coordinates(x_displacement, minister_display_current_y, global_manager), scaling.scale_width(10, global_manager),
            scaling.scale_height(30, global_manager), ['ministers'], 'misc/default_label.png', current_actor_label_type, 'minister', global_manager)) #coordinates, ideal_width, minimum_height, modes, image_id, mob_label_type, global_manager

    actor_display_top_y = global_manager.get('default_display_height') - 205
    actor_display_current_y = actor_display_top_y
    global_manager.set('mob_ordered_list_start_y', actor_display_current_y)
    #minister info labels setup



    #mob info images setup
    #pmob background image
    pmob_free_image_background = actor_display_images.mob_background_image('misc/pmob_background.png', scaling.scale_coordinates(0, actor_display_current_y, global_manager), scaling.scale_width(125, global_manager),
        scaling.scale_height(125, global_manager), ['strategic', 'europe'],global_manager)
    global_manager.get('mob_info_display_list').append(pmob_free_image_background)

    #npmob background image
    npmob_free_image_background = actor_display_images.mob_background_image('misc/npmob_background.png', scaling.scale_coordinates(0, actor_display_current_y, global_manager), scaling.scale_width(125, global_manager),
        scaling.scale_height(125, global_manager), ['strategic', 'europe'],global_manager)
    global_manager.get('mob_info_display_list').append(npmob_free_image_background)

    #mob background image's tooltip
    mob_free_image_background_tooltip = actor_display_labels.actor_display_label(scaling.scale_coordinates(0, actor_display_current_y, global_manager), scaling.scale_width(125, global_manager), scaling.scale_height(125, global_manager),
        ['strategic', 'europe'], 'misc/empty.png', 'tooltip', 'mob', global_manager) #coordinates, minimum_width, height, modes, image_id, actor_label_type, actor_type, global_manager
    global_manager.get('mob_info_display_list').append(mob_free_image_background_tooltip)

    #mob image
    mob_free_image = actor_display_images.actor_display_free_image(scaling.scale_coordinates(5, actor_display_current_y + 5, global_manager), scaling.scale_width(115, global_manager),
        scaling.scale_height(115, global_manager), ['strategic', 'europe'], 'default', global_manager) #coordinates, width, height, modes, global_manager
    global_manager.get('mob_info_display_list').append(mob_free_image)

    #veteran icon image
    mob_free_image = actor_display_images.actor_display_free_image(scaling.scale_coordinates(5, actor_display_current_y + 5, global_manager), scaling.scale_width(115, global_manager),
        scaling.scale_height(115, global_manager), ['strategic', 'europe'], 'veteran_icon', global_manager) #coordinates, width, height, modes, global_manager
    global_manager.get('mob_info_display_list').append(mob_free_image)


    #disorganized icon image
    mob_free_image = actor_display_images.actor_display_free_image(scaling.scale_coordinates(5, actor_display_current_y + 5, global_manager), scaling.scale_width(115, global_manager),
        scaling.scale_height(115, global_manager), ['strategic', 'europe'], 'disorganized_icon', global_manager) #coordinates, width, height, modes, global_manager
    global_manager.get('mob_info_display_list').append(mob_free_image)

    #sentry mode icon image
    mob_free_image = actor_display_images.actor_display_free_image(scaling.scale_coordinates(5, actor_display_current_y + 5, global_manager), scaling.scale_width(115, global_manager),
        scaling.scale_height(115, global_manager), ['strategic', 'europe'], 'sentry_icon', global_manager) #coordinates, width, height, modes, global_manager
    global_manager.get('mob_info_display_list').append(mob_free_image)
    
    fire_unit_button = buttons.fire_unit_button(scaling.scale_coordinates(130, actor_display_current_y, global_manager),
        scaling.scale_width(35, global_manager), scaling.scale_height(35, global_manager), 'gray', ['strategic', 'europe'], 'buttons/remove_minister_button.png', global_manager)
    #mob info images setup



    #mob info labels setup
    mob_info_display_labels = ['name', 'minister', 'officer', 'workers', 'movement', 'canoes', 'combat_strength', 'preferred_terrains', 'attitude', 'controllable', 'crew', 'passengers', 'current passenger'] #order of mob info display labels
    for current_actor_label_type in mob_info_display_labels:
        if current_actor_label_type == 'minister': #how far from edge of screen
            x_displacement = 40
        elif current_actor_label_type == 'current passenger':
            x_displacement = 30
        else:
            x_displacement = 0
            
        if not current_actor_label_type == 'current passenger':
            global_manager.get('mob_info_display_list').append(actor_display_labels.actor_display_label(scaling.scale_coordinates(x_displacement, actor_display_current_y, global_manager), scaling.scale_width(10, global_manager),
                scaling.scale_height(30, global_manager), ['strategic', 'europe'], 'misc/default_label.png', current_actor_label_type, 'mob', global_manager))
                #coordinates, ideal_width, minimum_height, modes, image_id, mob_label_type, global_manager
        else:
            for i in range(0, 3): #0, 1, 2
                #label for each passenger
                global_manager.get('mob_info_display_list').append(actor_display_labels.list_item_label(scaling.scale_coordinates(x_displacement, actor_display_current_y, global_manager), scaling.scale_width(10, global_manager),
                    scaling.scale_height(30, global_manager), ['strategic', 'europe'], 'misc/default_label.png', current_actor_label_type, i, 'ship', 'mob', global_manager))
                    #coordinates, minimum_width, height, modes, image_id, actor_label_type, list_index, list_type, global_manager
    #mob info labels setup
                


    #tile info images setup
    #tile background image
    actor_display_current_y = global_manager.get('default_display_height') - (580 + 35 + 35)
    global_manager.set('tile_ordered_list_start_y', actor_display_current_y)
    tile_free_image_background = actor_display_images.mob_background_image('misc/tile_background.png', scaling.scale_coordinates(0, actor_display_current_y, global_manager), scaling.scale_width(125, global_manager),
        scaling.scale_height(125, global_manager), ['strategic', 'europe'], global_manager) 
    global_manager.get('tile_info_display_list').append(tile_free_image_background)

    cycle_same_tile_button = buttons.cycle_same_tile_button(scaling.scale_coordinates(162, actor_display_current_y + 95, global_manager),
            scaling.scale_width(30, global_manager), scaling.scale_height(30, global_manager), 'gray', ['strategic', 'europe'], 'buttons/cycle_passengers_down.png', global_manager)
    for i in range(0, 3): #add button to cycle through
        same_tile_icon = buttons.same_tile_icon(scaling.scale_coordinates(130, actor_display_current_y + 95 - (32 * i), global_manager),
            scaling.scale_width(30, global_manager), scaling.scale_height(30, global_manager), 'gray', ['strategic', 'europe'], 'buttons/default_button.png', i, False, global_manager)
    same_tile_icon = buttons.same_tile_icon(scaling.scale_coordinates(130, actor_display_current_y + 95 - (32 * (i + 1)), global_manager),
        scaling.scale_width(30, global_manager), scaling.scale_height(30, global_manager), 'gray', ['strategic', 'europe'], 'buttons/default_button.png', i + 1, True, global_manager)

    #tile background image's tooltip
    tile_free_image_background_tooltip = actor_display_labels.actor_display_label(scaling.scale_coordinates(0, actor_display_current_y, global_manager), scaling.scale_width(125, global_manager), scaling.scale_height(125, global_manager),
        ['strategic', 'europe'], 'misc/empty.png', 'tooltip', 'tile', global_manager) #coordinates, minimum_width, height, modes, image_id, actor_label_type, actor_type, global_manager
    global_manager.get('tile_info_display_list').append(tile_free_image_background_tooltip)

    tile_info_display_images = ['terrain', 'infrastructure_middle', 'up', 'down', 'right', 'left', 'slums', 'resource', 'resource_building', 'port', 'train_station', 'trading_post', 'mission', 'fort']
    #note: if fog of war seems to be working incorrectly and/or resource icons are not showing, check for typos in above list
    for current_actor_image_type in tile_info_display_images:
        if not current_actor_image_type in ['up', 'down', 'right', 'left']:
            global_manager.get('tile_info_display_list').append(actor_display_images.actor_display_free_image(scaling.scale_coordinates(5, actor_display_current_y + 5, global_manager), scaling.scale_width(115, global_manager),
                scaling.scale_height(115, global_manager), ['strategic', 'europe'], current_actor_image_type, global_manager))
        else:
            global_manager.get('tile_info_display_list').append(actor_display_images.actor_display_infrastructure_connection_image(scaling.scale_coordinates(5, actor_display_current_y + 5, global_manager),
                scaling.scale_width(115, global_manager), scaling.scale_height(115, global_manager), ['strategic'], 'infrastructure_connection', current_actor_image_type, global_manager))
                #coordinates, width, height, modes, actor_image_type, direction, global_manager
    #tile info images setup
            


    #tile info labels setup
    tile_info_display_labels = ['coordinates', 'terrain', 'resource', 'slums',
                                'resource building', 'building efficiency', 'building work crews', 'current building work crew',
                                'village', 'native population', 'native available workers', 'native aggressiveness']
    for current_actor_label_type in tile_info_display_labels:
        if current_actor_label_type == 'current building work crew':
            x_displacement = 50
        elif current_actor_label_type in ['building efficiency', 'building work crews', 'native population', 'native available workers', 'native aggressiveness']:
            x_displacement = 25
        else:
            x_displacement = 0
        
        if not current_actor_label_type in ['building efficiency', 'building work crews', 'current building work crew', 'native population', 'native available workers', 'native aggressiveness']:
            global_manager.get('tile_info_display_list').append(actor_display_labels.actor_display_label(scaling.scale_coordinates(x_displacement, actor_display_current_y, global_manager), scaling.scale_width(10, global_manager),
                scaling.scale_height(30, global_manager), ['strategic', 'europe'], 'misc/default_label.png', current_actor_label_type, 'tile', global_manager))
                #coordinates, ideal_width, minimum_height, modes, image_id, actor_label_type, actor_type, global_manager
        elif current_actor_label_type == 'building efficiency':
            global_manager.get('tile_info_display_list').append(actor_display_labels.building_efficiency_label(scaling.scale_coordinates(x_displacement, actor_display_current_y, global_manager), scaling.scale_width(10, global_manager),
                scaling.scale_height(30, global_manager), ['strategic'], 'misc/default_label.png', 'resource', 'tile', global_manager))
        elif current_actor_label_type == 'building work crews':
            global_manager.get('tile_info_display_list').append(actor_display_labels.building_work_crews_label(scaling.scale_coordinates(x_displacement, actor_display_current_y, global_manager), scaling.scale_width(10, global_manager),
                scaling.scale_height(30, global_manager), ['strategic'], 'misc/default_label.png', 'resource', 'tile', global_manager))
        elif current_actor_label_type == 'current building work crew':
            for i in range(0, 3):
                global_manager.get('tile_info_display_list').append(actor_display_labels.list_item_label(scaling.scale_coordinates(x_displacement, actor_display_current_y, global_manager), scaling.scale_width(10, global_manager),
                    scaling.scale_height(30, global_manager), ['strategic'], 'misc/default_label.png', 'building work crew', i, 'resource building', 'tile', global_manager))
        elif current_actor_label_type in ['native population', 'native available workers', 'native aggressiveness']:
            global_manager.get('tile_info_display_list').append(actor_display_labels.native_info_label(scaling.scale_coordinates(x_displacement, actor_display_current_y, global_manager), scaling.scale_width(10, global_manager),
                scaling.scale_height(30, global_manager), ['strategic'], 'misc/default_label.png', current_actor_label_type, 'tile', global_manager))
    #tile info labels setup

            

    #commodity/inventory labels setup
    actor_display_current_y -= 35

    commodity_prices_x, commodity_prices_y = (870, 100)
    commodity_prices_height = 30 + (30 * len(global_manager.get('commodity_types')))
    commodity_prices_width = 200
    global_manager.set('commodity_prices_label', labels.commodity_prices_label(scaling.scale_coordinates(commodity_prices_x, commodity_prices_y, global_manager), scaling.scale_width(200, global_manager),
        scaling.scale_height(commodity_prices_height, global_manager), ['europe'], 'misc/commodity_prices_label.png', global_manager))
    for current_index in range(len(global_manager.get('commodity_types'))): #commodity prices in Europe
        new_commodity_button = buttons.commodity_button(scaling.scale_coordinates(commodity_prices_x - 35, commodity_prices_y + commodity_prices_height - 65 - (30 * current_index), global_manager), scaling.scale_width(30, global_manager),
            scaling.scale_height(30, global_manager), ['europe'], 'scenery/resources/large/' + global_manager.get('commodity_types')[current_index] + '.png', global_manager.get('commodity_types')[current_index], global_manager)

    mob_inventory_capacity_label = actor_display_labels.actor_display_label(scaling.scale_coordinates(300, global_manager.get('default_display_height') - 115, global_manager), scaling.scale_width(10, global_manager),
        scaling.scale_height(30, global_manager), ['strategic', 'europe'], 'misc/default_label.png', 'mob inventory capacity', 'mob', global_manager)
    global_manager.get('mob_info_display_list').append(mob_inventory_capacity_label)
    for current_index in range(len(global_manager.get('commodity_types'))): #commodities held in selected mob
        new_commodity_display_label = actor_display_labels.commodity_display_label(scaling.scale_coordinates(300, global_manager.get('default_display_height') - (150 + (35 * (current_index))), global_manager),
            scaling.scale_width(10, global_manager), scaling.scale_height(30, global_manager), ['strategic', 'europe'], 'misc/default_label.png', current_index, 'mob', global_manager)
        global_manager.get('mob_info_display_list').append(new_commodity_display_label)

    tile_inventory_capacity_label = actor_display_labels.actor_display_label(scaling.scale_coordinates(300, global_manager.get('default_display_height') - 455, global_manager), scaling.scale_width(10, global_manager),
        scaling.scale_height(30, global_manager), ['strategic', 'europe'], 'misc/default_label.png', 'tile inventory capacity', 'tile', global_manager)
    global_manager.get('tile_info_display_list').append(tile_inventory_capacity_label)

    for current_index in range(len(global_manager.get('commodity_types'))): #commodities held in selected tile
        new_commodity_display_label = actor_display_labels.commodity_display_label(scaling.scale_coordinates(300, global_manager.get('default_display_height') - (490 + (35 * (current_index))), global_manager),
            scaling.scale_width(10, global_manager), scaling.scale_height(30, global_manager), ['strategic', 'europe'], 'misc/default_label.png', current_index, 'tile', global_manager)
            #coordinates, ideal_width, minimum_height, modes, image_id, commodity_index, global_manager
        global_manager.get('tile_info_display_list').append(new_commodity_display_label)
    #commodity/inventory labels setup



    #Europe screen buttons setup
    #max of 8 in column
    buy_button_y = 0#140
    for recruitment_index in range(len(global_manager.get('recruitment_types'))):
        new_recruitment_button = europe_transactions.recruitment_button(scaling.scale_coordinates(1500 - (recruitment_index // 8) * 125, buy_button_y + (120 * (recruitment_index % 8)), global_manager), scaling.scale_width(100, global_manager),
            scaling.scale_height(100, global_manager), 'blue', global_manager.get('recruitment_types')[recruitment_index], 'none', ['europe'], global_manager)

    new_consumer_goods_buy_button = europe_transactions.buy_commodity_button(scaling.scale_coordinates(1500 - ((recruitment_index + 1) // 8) * 125, buy_button_y + (120 * ((recruitment_index + 1) % 8)), global_manager), scaling.scale_width(100, global_manager), scaling.scale_height(100, global_manager), 'blue',
        'consumer goods', ['europe'], global_manager)#coordinates, width, height, color, commodity_type, modes, global_manager
    #Europe screen buttons setup



    #minister table setup
    table_width = 400
    table_height = 800
    minister_table = images.free_image('misc/minister_table.png', scaling.scale_coordinates((global_manager.get('default_display_width') / 2) - (table_width / 2), 55, global_manager), scaling.scale_width(table_width, global_manager),
        scaling.scale_height(table_height, global_manager), ['ministers'], global_manager)

    position_icon_width = 125
    for current_index in range(0, 8): #creates an office icon and a portrait at a section of the table for each minister
        if current_index <= 3: #left side
            images.minister_type_image(scaling.scale_coordinates((global_manager.get('default_display_width') / 2) - (table_width / 2) + 10, current_index * 200 + 95, global_manager),
                scaling.scale_width(position_icon_width, global_manager), scaling.scale_height(position_icon_width, global_manager), ['ministers'], global_manager.get('minister_types')[current_index], 'none', global_manager)
            buttons.minister_portrait_image(scaling.scale_coordinates((global_manager.get('default_display_width') / 2) - (table_width / 2) - position_icon_width - 10, current_index * 200 + 95, global_manager),
                scaling.scale_width(position_icon_width, global_manager), scaling.scale_height(position_icon_width, global_manager), ['ministers'], global_manager.get('minister_types')[current_index], global_manager)
        else:
            images.minister_type_image(scaling.scale_coordinates((global_manager.get('default_display_width') / 2) + (table_width / 2) - position_icon_width - 10, (current_index - 4) * 200 + 95, global_manager),
                scaling.scale_width(position_icon_width, global_manager), scaling.scale_height(position_icon_width, global_manager), ['ministers'], global_manager.get('minister_types')[current_index], 'none', global_manager)
            buttons.minister_portrait_image(scaling.scale_coordinates((global_manager.get('default_display_width') / 2) + (table_width / 2) - position_icon_width + position_icon_width + 10, (current_index - 4) * 200 + 95, global_manager),
                scaling.scale_width(position_icon_width, global_manager), scaling.scale_height(position_icon_width, global_manager), ['ministers'], global_manager.get('minister_types')[current_index], global_manager)

    available_minister_display_x = global_manager.get('default_display_width')
    available_minister_display_y = 770
    cycle_left_button = buttons.cycle_available_ministers_button(scaling.scale_coordinates(available_minister_display_x - (position_icon_width / 2) - 25, available_minister_display_y, global_manager), scaling.scale_width(50, global_manager),
        scaling.scale_height(50, global_manager), pygame.K_w, ['ministers'], 'buttons/cycle_ministers_up_button.png', 'left', global_manager)

    for i in range(0, 5):
        available_minister_display_y -= (position_icon_width + 10)
        current_portrait = buttons.minister_portrait_image(scaling.scale_coordinates(available_minister_display_x - position_icon_width, available_minister_display_y, global_manager),
            scaling.scale_width(position_icon_width, global_manager), scaling.scale_height(position_icon_width, global_manager), ['ministers'], 'none', global_manager)

    available_minister_display_y -= 60                     
    cycle_right_button = buttons.cycle_available_ministers_button(scaling.scale_coordinates(available_minister_display_x - (position_icon_width / 2) - 25, available_minister_display_y, global_manager), scaling.scale_width(50, global_manager),
        scaling.scale_height(50, global_manager), pygame.K_s, ['ministers'], 'buttons/cycle_ministers_down_button.png', 'right', global_manager)
    #minister table setup



    #activating/disabling debugging tools
    global_manager.set('DEBUG_spawning_allowed', True) #True by default
    #allows villages to spawn native warriors
    
    global_manager.set('DEBUG_boost_attrition', False) #False by default
    #increases chance of any attrition occuring by a factor of 6
    
    global_manager.set('DEBUG_infinite_village_workers', False) #False by default
    #converts all villagers to available workers on startup
    
    global_manager.set('DEBUG_damaged_buildings', False) #False by default
    #causes all buildings to be damaged on startup
    
    global_manager.set('DEBUG_show_corruption_on_save', False) #False by default
    #prints the corruption and skill levels of each minister to the console when saving the game

    global_manager.set('DEBUG_show_minister_stealing', False) #False by default
    #prints information about the value and type of theft and the prosecutor's reaction when minister is corrupt

    global_manager.set('DEBUG_show_evil', False) #False by default
    #prints the players "evil" number at the end of each turn

    global_manager.set('DEBUG_show_fear', False) #False by default
    #prints the players "fear" number at the end of each turn and says when fear dissuades a minister from stealing

    global_manager.set('DEBUG_remove_fog_of_war', False) #False by default
    #reveals all cells

    global_manager.set('DEBUG_fast_turn', False) #False by default
    #removes end turn delays

    global_manager.set('DEBUG_reveal_beasts', False) #False by default
    #reveals beasts on load

    global_manager.set('DEBUG_infinite_commodities', False) #False by default
    #gives 10 of each commodity in Europe on new game

    global_manager.set('DEBUG_band_of_thieves', False) #False by default
    #causes all ministers to be corrupt whenever possible

    global_manager.set('DEBUG_ministry_of_magic', False) #False by default
    #causes all ministers to never be corrupt and succeed at all rolls, speeds up all dice rolls

    global_manager.set('DEBUG_farm_upstate', False)
    #retires all appointed ministers at the end of the turn
    
    #activating/disabling debugging tools

    global_manager.set('startup_complete', True)
    global_manager.set('creating_new_game', False)
    main_loop.main_loop(global_manager)
    pygame.quit()

except Exception as e: #displays error message and records error message in crash log file
    crash_log_file = open("notes/Crash Log.txt", "w")
    crash_log_file.write("") #clears crash report file
    console = logging.StreamHandler() #sets logger to go to both console and crash log file
    logging.basicConfig(filename = "notes/Crash Log.txt")
    logging.getLogger('').addHandler(console)
    
    logging.error(e, exc_info = True) #sends error message to console and crash log file
    
    crash_log_file.close()
    pygame.quit()

