#Contains functionality for creating new games, saving, and loading

import random
import pickle

from . import scaling
from . import notification_tools
from . import game_transitions
from . import grids
from . import data_managers
from . import turn_management_tools
from . import text_tools
from . import market_tools
from . import minister_utility
from . import actor_utility

class save_load_manager_template():
    '''
    Object that controls creating new games, saving, and loading
    '''
    def __init__(self, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.global_manager = global_manager
        self.set_copied_elements()

    def set_copied_elements(self):
        '''
        Description:
            Determines which variables should be saved and loaded
        Input:
            None
        Output:
            None
        '''
        self.copied_elements = []
        self.copied_elements.append('money')
        self.copied_elements.append('turn')
        self.copied_elements.append('public_opinion')
        self.copied_elements.append('evil')
        self.copied_elements.append('fear')
        self.copied_elements.append('commodity_prices')
        self.copied_elements.append('african_worker_upkeep')
        self.copied_elements.append('european_worker_upkeep')
        self.copied_elements.append('slave_worker_upkeep')
        self.copied_elements.append('recruitment_costs')
        self.copied_elements.append('minister_appointment_tutorial_completed')
        self.copied_elements.append('exit_minister_screen_tutorial_completed')
        self.copied_elements.append('current_game_mode')
        self.copied_elements.append('transaction_history')
        self.copied_elements.append('previous_financial_report')
        self.copied_elements.append('num_wandering_workers')
        self.copied_elements.append('prosecution_bribed_judge')
        self.copied_elements.append('sold_commodities')
        self.copied_elements.append('action_prices')
        
    def new_game(self):
        '''
        Description:
            Creates a new game and leaves the main menu
        Input:
            None
        Output:
            None
        '''
        self.global_manager.set('creating_new_game', True)
        strategic_grid_height = 300
        strategic_grid_width = 320
        mini_grid_height = 600
        mini_grid_width = 640

        input_dict = {}
        input_dict['origin_coordinates'] = scaling.scale_coordinates(self.global_manager.get('default_display_width') - (strategic_grid_width + 100), self.global_manager.get('default_display_height') - (strategic_grid_height + 25),
            self.global_manager)
        input_dict['pixel_width'] = scaling.scale_width(strategic_grid_width, self.global_manager)
        input_dict['pixel_height'] = scaling.scale_height(strategic_grid_height, self.global_manager)
        input_dict['coordinate_width'] = 16
        input_dict['coordinate_height'] = 15
        input_dict['internal_line_color'] = 'black'
        input_dict['external_line_color'] = 'black'
        input_dict['modes'] = ['strategic']
        input_dict['strategic_grid'] = True
        input_dict['grid_line_width'] = 2
        strategic_map_grid = grids.grid(False, input_dict, self.global_manager)
        self.global_manager.set('strategic_map_grid', strategic_map_grid)

        input_dict = {}
        input_dict['origin_coordinates'] = scaling.scale_coordinates(self.global_manager.get('default_display_width') - (mini_grid_width + 100),
            self.global_manager.get('default_display_height') - (strategic_grid_height + mini_grid_height + 50), self.global_manager)
        input_dict['pixel_width'] = scaling.scale_width(mini_grid_width, self.global_manager)
        input_dict['pixel_height'] = scaling.scale_height(mini_grid_height,self.global_manager)
        input_dict['coordinate_width'] = 5
        input_dict['coordinate_height'] = 5
        input_dict['internal_line_color'] = 'black'
        input_dict['external_line_color'] = 'bright red'
        input_dict['modes'] = ['strategic']
        input_dict['grid_line_width'] = 3
        input_dict['attached_grid'] = strategic_map_grid
        minimap_grid = grids.mini_grid(False, input_dict, self.global_manager)
        self.global_manager.set('minimap_grid', minimap_grid)

        self.global_manager.set('notification_manager', data_managers.notification_manager_template(self.global_manager))
    

        europe_grid_x = self.global_manager.get('default_display_width') - (strategic_grid_width + 340)
        europe_grid_y = self.global_manager.get('default_display_height') - (strategic_grid_height + 25)

        input_dict = {}
        input_dict['origin_coordinates'] = scaling.scale_coordinates(europe_grid_x, europe_grid_y, self.global_manager)
        input_dict['pixel_width'] = scaling.scale_width(120, self.global_manager)
        input_dict['pixel_height'] = scaling.scale_height(120, self.global_manager)
        input_dict['internal_line_color'] = 'black'
        input_dict['external_line_color'] = 'black'
        input_dict['modes'] = ['strategic', 'europe']
        input_dict['tile_image_id'] = 'locations/europe.png' 
        input_dict['grid_line_width'] = 3
        input_dict['name'] = 'Europe'
        europe_grid = grids.abstract_grid(False, input_dict, self.global_manager)
        self.global_manager.set('europe_grid', europe_grid)


        slave_traders_grid_x = self.global_manager.get('default_display_width') - (strategic_grid_width + 340)
        slave_traders_grid_y = self.global_manager.get('default_display_height') - (strategic_grid_height - 120) #started at 25, -120 for europe grid y, -25 for space between

        input_dict = {}
        input_dict['origin_coordinates'] = scaling.scale_coordinates(slave_traders_grid_x, slave_traders_grid_y, self.global_manager)
        input_dict['pixel_width'] = scaling.scale_width(120, self.global_manager)
        input_dict['pixel_height'] = scaling.scale_height(120, self.global_manager)
        input_dict['internal_line_color'] = 'black'
        input_dict['external_line_color'] = 'black'
        input_dict['modes'] = ['strategic']
        input_dict['tile_image_id'] = 'locations/slave_traders.png' 
        input_dict['grid_line_width'] = 3
        input_dict['name'] = 'Slave traders'
        slave_traders_grid = grids.abstract_grid(False, input_dict, self.global_manager)
        self.global_manager.set('slave_traders_grid', slave_traders_grid)

        
        game_transitions.set_game_mode('strategic', self.global_manager)
        game_transitions.create_strategic_map(self.global_manager)
        self.global_manager.get('minimap_grid').calibrate(2, 2)

        game_transitions.set_game_mode('ministers', self.global_manager)

        for current_commodity in self.global_manager.get('commodity_types'):
            if not current_commodity == 'consumer goods':
                market_tools.set_price(current_commodity, random.randrange(self.global_manager.get('commodity_min_starting_price'), self.global_manager.get('commodity_max_starting_price') + 1), self.global_manager) #2-5
            else:
                market_tools.set_price(current_commodity, self.global_manager.get('consumer_goods_starting_price'), self.global_manager)

        self.global_manager.get('money_tracker').reset_transaction_history()
        self.global_manager.get('money_tracker').set(500)
        self.global_manager.get('turn_tracker').set(0)
        self.global_manager.get('public_opinion_tracker').set(50)
        self.global_manager.get('evil_tracker').set(0)
        self.global_manager.get('fear_tracker').set(1)

        self.global_manager.set('player_turn', True)
        self.global_manager.set('previous_financial_report', 'none')

        self.global_manager.get('actor_creation_manager').create_placeholder_ministers(self.global_manager)

        self.global_manager.set('available_minister_left_index', -2) #so that first index is in middle

        self.global_manager.set('num_african_workers', 0)
        self.global_manager.set('num_european_workers', 0)
        self.global_manager.set('num_slave_workers', 0)
        self.global_manager.set('num_wandering_workers', 0)
        self.global_manager.set('african_worker_upkeep', self.global_manager.get('initial_african_worker_upkeep'))
        self.global_manager.set('european_worker_upkeep', self.global_manager.get('initial_european_worker_upkeep'))
        self.global_manager.set('slave_worker_upkeep', self.global_manager.get('initial_slave_worker_upkeep'))
        self.global_manager.get('recruitment_costs')['slave workers'] = self.global_manager.get('base_slave_recruitment_cost')
        actor_utility.reset_action_prices(self.global_manager)

        for i in range(1, random.randrange(5, 8)):
            turn_management_tools.manage_villages(self.global_manager)
            actor_utility.spawn_beast(self.global_manager)
        
        minister_utility.update_available_minister_display(self.global_manager)

        turn_management_tools.start_player_turn(self.global_manager, True)

        self.global_manager.set('minister_appointment_tutorial_completed', False)
        self.global_manager.set('exit_minister_screen_tutorial_completed', False)
        notification_tools.show_tutorial_notifications(self.global_manager)
        self.global_manager.set('creating_new_game', False)
        
    def save_game(self, file_path):
        '''
        Description:
            Saves the game in the file corresponding to the inputted file path
        Input:
            None
        Output:
            None
        '''
        file_path = 'save_games/' + file_path
        saved_global_manager = data_managers.global_manager_template()
        self.global_manager.set('transaction_history', self.global_manager.get('money_tracker').transaction_history)
        for current_element in self.copied_elements: #save necessary data into new global manager
            saved_global_manager.set(current_element, self.global_manager.get(current_element))


        saved_grid_dicts = []
        for current_grid in self.global_manager.get('grid_list'):
            if not current_grid.is_mini_grid: #minimap grid doesn't need to be saved
                saved_grid_dicts.append(current_grid.to_save_dict())

            
        saved_actor_dicts = []
        for current_pmob in self.global_manager.get('pmob_list'):
            if not (current_pmob.in_group or current_pmob.in_vehicle or current_pmob.in_building): #containers save their contents and load them in, contents don't need to be saved/loaded separately
                saved_actor_dicts.append(current_pmob.to_save_dict())
                
        for current_npmob in self.global_manager.get('npmob_list'):
            if current_npmob.saves_normally: #for units like native warriors that are saved as part a village and not as their own unit, do not attempt to save from here
                saved_actor_dicts.append(current_npmob.to_save_dict())
            
        for current_building in self.global_manager.get('building_list'):
            saved_actor_dicts.append(current_building.to_save_dict())
            
        for current_loan in self.global_manager.get('loan_list'):
            saved_actor_dicts.append(current_loan.to_save_dict())


        saved_minister_dicts = []        
        for current_minister in self.global_manager.get('minister_list'):
            saved_minister_dicts.append(current_minister.to_save_dict())
            if self.global_manager.get('DEBUG_show_corruption_on_save'):
                print(current_minister.name + ', ' + current_minister.current_position + ', skill modifier: ' + str(current_minister.get_skill_modifier()) + ', corruption threshold: ' + str(current_minister.corruption_threshold) +
                    ', stolen money: ' + str(current_minister.stolen_money) + ', personal savings: ' + str(current_minister.personal_savings))


        with open(file_path, 'wb') as handle: #write wb, read rb
            pickle.dump(saved_global_manager, handle) #saves new global manager with only necessary information to file
            pickle.dump(saved_grid_dicts, handle)
            pickle.dump(saved_actor_dicts, handle)
            pickle.dump(saved_minister_dicts, handle)
        text_tools.print_to_screen("Game successfully saved to " + file_path, self.global_manager)

    def load_game(self, file_path):
        '''
        Description:
            Loads a saved game from the file corresponding to the inputted file path
        Input:
            None
        Output:
            None
        '''
        self.global_manager.set('loading_save', True)
        
        text_tools.print_to_screen("", self.global_manager)
        text_tools.print_to_screen("Loading " + file_path, self.global_manager)
        game_transitions.start_loading(self.global_manager)
        #load file
        try:
            file_path = 'save_games/' + file_path
            with open(file_path, 'rb') as handle:
                new_global_manager = pickle.load(handle)
                saved_grid_dicts = pickle.load(handle)
                saved_actor_dicts = pickle.load(handle)
                saved_minister_dicts = pickle.load(handle)
        except:
            text_tools.print_to_screen("The " + file_path + " file does not exist.", self.global_manager)
            return()

        #load variables
        for current_element in self.copied_elements:
            self.global_manager.set(current_element, new_global_manager.get(current_element))
        self.global_manager.get('money_tracker').set(new_global_manager.get('money'))
        self.global_manager.get('money_tracker').transaction_history = self.global_manager.get('transaction_history')
        self.global_manager.get('turn_tracker').set(new_global_manager.get('turn'))
        self.global_manager.get('public_opinion_tracker').set(new_global_manager.get('public_opinion'))
        self.global_manager.get('evil_tracker').set(new_global_manager.get('evil'))
        self.global_manager.get('fear_tracker').set(new_global_manager.get('fear'))

        text_tools.print_to_screen("", self.global_manager)
        text_tools.print_to_screen("Turn " + str(self.global_manager.get('turn')), self.global_manager)

        #load grids
        strategic_grid_height = 300
        strategic_grid_width = 320
        mini_grid_height = 600
        mini_grid_width = 640
        europe_grid_x = self.global_manager.get('default_display_width') - (strategic_grid_width + 340)
        europe_grid_y = self.global_manager.get('default_display_height') - (strategic_grid_height + 25)
        slave_traders_grid_x = self.global_manager.get('default_display_width') - (strategic_grid_width + 340)
        slave_traders_grid_y = self.global_manager.get('default_display_height') - (strategic_grid_height - 120)
        for current_grid_dict in saved_grid_dicts:
            input_dict = current_grid_dict
            if current_grid_dict['grid_type'] == 'strategic_map_grid':
                input_dict['origin_coordinates'] = scaling.scale_coordinates(self.global_manager.get('default_display_width') - (strategic_grid_width + 100), self.global_manager.get('default_display_height') - (strategic_grid_height + 25),
                    self.global_manager)
                input_dict['pixel_width'] = scaling.scale_width(strategic_grid_width, self.global_manager)
                input_dict['pixel_height'] = scaling.scale_height(strategic_grid_height, self.global_manager)
                input_dict['coordinate_width'] = 16
                input_dict['coordinate_height'] = 15
                input_dict['internal_line_color'] = 'black'
                input_dict['external_line_color'] = 'black'
                input_dict['modes'] = ['strategic']
                input_dict['strategic_grid'] = True
                input_dict['grid_line_width'] = 2
                strategic_map_grid = grids.grid(True, input_dict, self.global_manager)
                self.global_manager.set('strategic_map_grid', strategic_map_grid)
                
            elif current_grid_dict['grid_type'] in ['europe_grid', 'slave_traders_grid']:
                input_dict['pixel_width'] = scaling.scale_width(120, self.global_manager)
                input_dict['pixel_height'] = scaling.scale_height(120, self.global_manager)
                input_dict['internal_line_color'] = 'black'
                input_dict['external_line_color'] = 'black'
                input_dict['grid_line_width'] = 3
                if current_grid_dict['grid_type'] == 'europe_grid':
                    input_dict['modes'] = ['strategic', 'europe']
                    input_dict['origin_coordinates'] = scaling.scale_coordinates(europe_grid_x, europe_grid_y, self.global_manager)
                    input_dict['tile_image_id'] = 'locations/europe.png' 
                    input_dict['name'] = 'Europe'
                    europe_grid = grids.abstract_grid(True, input_dict, self.global_manager)
                    self.global_manager.set('europe_grid', europe_grid)
                else:
                    input_dict['modes'] = ['strategic']
                    input_dict['origin_coordinates'] = scaling.scale_coordinates(slave_traders_grid_x, slave_traders_grid_y, self.global_manager)
                    input_dict['tile_image_id'] = 'locations/slave_traders.png' 
                    input_dict['name'] = 'Slave traders'
                    slave_traders_grid = grids.abstract_grid(True, input_dict, self.global_manager)
                    self.global_manager.set('slave_traders_grid', slave_traders_grid)
                    
        input_dict = {}
        input_dict['origin_coordinates'] = scaling.scale_coordinates(self.global_manager.get('default_display_width') - (mini_grid_width + 100),
            self.global_manager.get('default_display_height') - (strategic_grid_height + mini_grid_height + 50), self.global_manager)
        input_dict['pixel_width'] = scaling.scale_width(mini_grid_width, self.global_manager)
        input_dict['pixel_height'] = scaling.scale_height(mini_grid_height,self.global_manager)
        input_dict['coordinate_width'] = 5
        input_dict['coordinate_height'] = 5
        input_dict['internal_line_color'] = 'black'
        input_dict['external_line_color'] = 'bright red'
        input_dict['modes'] = ['strategic']
        input_dict['grid_line_width'] = 3
        input_dict['attached_grid'] = strategic_map_grid
        minimap_grid = grids.mini_grid(False, input_dict, self.global_manager)
        self.global_manager.set('minimap_grid', minimap_grid)
        
        self.global_manager.set('notification_manager', data_managers.notification_manager_template(self.global_manager))
        
        game_transitions.set_game_mode('strategic', self.global_manager)
        game_transitions.create_strategic_map(self.global_manager)

        self.global_manager.get('minimap_grid').calibrate(2, 2)

        #load actors
        for current_actor_dict in saved_actor_dicts:
            self.global_manager.get('actor_creation_manager').create(True, current_actor_dict, self.global_manager)
        for current_minister_dict in saved_minister_dicts:
            self.global_manager.get('actor_creation_manager').load_minister(current_minister_dict, self.global_manager)
        self.global_manager.set('available_minister_left_index', -2) #so that first index is in middle
        minister_utility.update_available_minister_display(self.global_manager)
        self.global_manager.get('commodity_prices_label').update_label()
        
        self.global_manager.get('minimap_grid').calibrate(2, 2)
        if not new_global_manager.get('current_game_mode') == 'strategic':
            game_transitions.set_game_mode(new_global_manager.get('current_game_mode'), self.global_manager)

        notification_tools.show_tutorial_notifications(self.global_manager)

        self.global_manager.set('loading_save', False)
