#Contains functionality for expeditions

import time
import random
from .groups import group
from ..tiles import tile
from .. import actor_utility
from .. import text_tools
from .. import dice_utility
from .. import notification_tools

class expedition(group):
    '''
    A group with an explorer officer that is able to explore and move on water
    '''
    def __init__(self, from_save, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'grids': grid list value - grids in which this group's images can appear
                'image': string value - File path to the image used by this object
                'name': string value - Required if from save, this group's name
                'modes': string list value - Game modes during which this group's images can appear
                'end_turn_destination': string or int tuple value - Required if from save, 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'max_movement_points': int value - Required if from save, maximum number of movement points this mob can have
                'worker': worker or dictionary value - If creating a new group, equals a worker that is part of this group. If loading, equals a dictionary of the saved information necessary to recreate the worker
                'officer': worker or dictionary value - If creating a new group, equals an officer that is part of this group. If loading, equals a dictionary of the saved information necessary to recreate the officer
                'canoes_image': string value - File path tothe image used by this object when it is in a river
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(from_save, input_dict, global_manager)
        self.exploration_mark_list = []
        self.exploration_cost = self.global_manager.get('action_prices')['exploration']#2
        self.can_explore = True
        self.can_swim = True
        self.can_swim_river = True
        self.can_swim_ocean = False
        
        self.has_canoes = True
        self.image_dict['canoes'] = input_dict['canoes_image']
        self.image_dict['no_canoes'] = self.image_dict['default']
        self.update_canoes()
        
        self.set_group_type('expedition')
        self.destination_cells = [] #used for off tile exploration, like when seeing nearby tiles when on water
        self.public_opinion_increases = []
        if not self.images[0].current_cell == 'none': #if did not just board vehicle
            self.resolve_off_tile_exploration()

    def move(self, x_change, y_change):
        '''
        Description:
            Moves this mob x_change to the right and y_change upward. Moving to a ship in the water automatically embarks the ship. Also allows exploration when moving into unexplored areas. Attempting an exploration starts the
                exploration process, which requires various dice rolls to succeed and can also result in the death of the expedition or the promotion of its explorer. A successful exploration uncovers the area and units to move into it
                normally in the future. As expeditions move, they automatically discover adjacent water tiles, and they also automatically discover all adjacent tiles when looking from a water tile
        Input:
            int x_change: How many cells are moved to the right in the movement
            int y_change: How many cells are moved upward in the movement
        Output:
            None
        '''
        self.global_manager.set('show_selection_outlines', True)
        self.global_manager.set('show_minimap_outlines', True)
        self.global_manager.set('last_selection_outline_switch', time.time())#outlines should be shown immediately when selected
        self.global_manager.set('last_minimap_outline_switch', time.time())
        future_x = self.x + x_change
        future_y = self.y + y_change
        roll_result = 0
        if x_change > 0:
            direction = 'east'
        elif x_change < 0:
            direction = 'west'
        elif y_change > 0:
            direction = 'north'
        elif y_change < 0:
            direction = 'south'
        else:
            direction = 'none'
        future_cell = self.grid.find_cell(future_x, future_y)
        if future_cell.visible == False: #if moving to unexplored area, try to explore it
            if self.global_manager.get('money_tracker').get() >= self.exploration_cost:
                if self.check_if_minister_appointed():
                    choice_info_dict = {'expedition': self, 'x_change': x_change, 'y_change': y_change, 'cost': self.exploration_cost, 'type': 'exploration'}
                    
                    self.current_roll_modifier = 0
                    self.current_min_success = self.default_min_success
                    self.current_max_crit_fail = self.default_max_crit_fail
                    self.current_min_crit_success = self.default_min_crit_success
                    
                    self.current_min_success -= self.current_roll_modifier #positive modifier reduces number required for succcess, reduces maximum that can be crit fail
                    self.current_max_crit_fail -= self.current_roll_modifier
                    if self.current_min_success > self.current_min_crit_success:
                        self.current_min_crit_success = self.current_min_success #if 6 is a failure, should not be critical success. However, if 6 is a success, it will always be a critical success
                    message = ""

                    risk_value = -1 * self.current_roll_modifier #modifier of -1 means risk value of 1
                    if self.veteran: #reduce risk if veteran
                        risk_value -= 1

                    if risk_value < 0: #0/6 = no risk
                        message = "RISK: LOW /n /n" + message  
                    elif risk_value == 0: #1/6 death = moderate risk
                        message = "RISK: MODERATE /n /n" + message #puts risk message at beginning
                    elif risk_value == 1: #2/6 = high risk
                        message = "RISK: HIGH /n /n" + message
                    elif risk_value > 1: #3/6 or higher = extremely high risk
                        message = "RISK: DEADLY /n /n" + message
                    
                    notification_tools.display_choice_notification(message + "Are you sure you want to spend " + str(choice_info_dict['cost']) + " money to attempt an exploration to the " + direction + "?", ['exploration', 'stop exploration'],
                        choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager
                    self.global_manager.set('ongoing_exploration', True)
                    for current_grid in self.grids:
                        coordinates = (0, 0)
                        if current_grid.is_mini_grid:
                            coordinates = current_grid.get_mini_grid_coordinates(self.x + x_change, self.y + y_change)
                        else:
                            coordinates = (self.x + x_change, self.y + y_change)
                        input_dict = {}
                        input_dict['coordinates'] = coordinates
                        input_dict['grid'] = current_grid
                        input_dict['image'] = 'misc/exploration_x/' + direction + '_x.png'
                        input_dict['name'] = 'exploration mark'
                        input_dict['modes'] = ['strategic']
                        input_dict['show_terrain'] = False
                        self.global_manager.get('exploration_mark_list').append(tile(False, input_dict, self.global_manager))
            else:
                text_tools.print_to_screen("You do not have enough money to attempt an exploration.", self.global_manager)
        else: #if moving to explored area, move normally
            super().move(x_change, y_change)
            if not self.images[0].current_cell == 'none': #if not in vehicle
                self.destination_cells = [] #used for off tile exploration, like when seeing nearby tiles when on water
                self.public_opinion_increases = []
                self.resolve_off_tile_exploration()

    def disembark_vehicle(self, vehicle):
        '''
        Description:
            Shows this mob and disembarks it from the inputted vehicle after being a passenger. Also automatically explores nearby tiles when applicable, as if this expedition had moved
        Input:
            vehicle vehicle: vehicle that this mob disembarks from
        Output:
            None
        '''
        super().disembark_vehicle(vehicle)
        self.destination_cells = [] #used for off tile exploration, like when seeing nearby tiles when on water
        self.public_opinion_increases = []
        self.resolve_off_tile_exploration()

    def start_exploration(self, x_change, y_change):
        '''
        Description:
            Used when the player issues a move order into an unexplored area with an expedition, displays a choice notification that allows the player to explore or not. Choosing to explore starts the exploration process. This function
                also determines the expedition's result, but the results are only shown to the player after a dice roll and the complete_exploration function
        Input:
            None
        Output:
            None
        '''
        self.global_manager.get('money_tracker').change(self.exploration_cost * -1, 'exploration')

        if self.veteran: #tells notifications how many of the currently selected mob's dice to show while rolling
            num_dice = 2
        else:
            num_dice = 1
        
        future_x = self.x + x_change
        future_y = self.y + y_change
        roll_result = 0
        if x_change > 0:
            direction = 'east'
        elif x_change < 0:
            direction = 'west'
        elif y_change > 0:
            direction = 'north'
        elif y_change < 0:
            direction = 'south'
        else:
            direction = 'none'
        future_cell = self.grid.find_cell(future_x, future_y)
        
        self.just_promoted = False
        text = ""
        text += "The expedition heads towards the " + direction + ". /n /n"
        text += (self.global_manager.get('flavor_text_manager').generate_flavor_text('explorer') + " /n /n")
        
        if not self.veteran:    
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required to succeed.", 'exploration', self.global_manager, num_dice)
        else:
            text += ("The veteran explorer can roll twice and pick the higher result. /n /n")
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required on at least 1 die to succeed.", 'exploration', self.global_manager, num_dice)

        notification_tools.display_notification(text + "Rolling... ", 'roll', self.global_manager, num_dice)

        die_x = self.global_manager.get('notification_manager').notification_x - 140

        if self.veteran:
            results = self.controlling_minister.roll_to_list(6, self.current_min_success, self.current_max_crit_fail, self.exploration_cost, 'exploration', 2)
            first_roll_list = dice_utility.roll_to_list(6, "Exploration roll", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, results[0])
            self.display_die((die_x, 500), first_roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)

            second_roll_list = dice_utility.roll_to_list(6, "second", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, results[1])
            self.display_die((die_x, 380), second_roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, False)
                                
            text += (first_roll_list[1] + second_roll_list[1]) #add strings from roll result to text
            roll_result = max(first_roll_list[0], second_roll_list[0])
            result_outcome_dict = {}
            for i in range(1, 7):
                if i <= self.current_max_crit_fail:
                    word = "CRITICAL FAILURE"
                elif i >= self.current_min_crit_success:
                    word = "CRITICAL SUCCESS"
                elif i >= self.current_min_success:
                    word = "SUCCESS"
                else:
                    word = "FAILURE"
                result_outcome_dict[i] = word
            text += ("The higher result, " + str(roll_result) + ": " + result_outcome_dict[roll_result] + ", was used. /n")
        else:
            result = self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail, self.exploration_cost, 'exploration')
            roll_list = dice_utility.roll_to_list(6, "Exploration roll", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, result)
            self.display_die((die_x, 440), roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)
                
            text += roll_list[1]
            roll_result = roll_list[0]

        notification_tools.display_notification(text + "Click to continue.", 'exploration', self.global_manager, num_dice)
            
        text += "/n"
        public_opinion_increase = 0
        if roll_result >= self.current_min_success: #4+ required on D6 for exploration by default
            public_opinion_increase = random.randrange(0, 3)
            if not future_cell.resource == 'none':
                if future_cell.resource == 'natives':
                    text += "The expedition has discovered a " + future_cell.terrain.upper() + " tile containing the village of " + future_cell.village.name + ". /n /n"
                else:
                    text += "The expedition has discovered a " + future_cell.terrain.upper() + " tile with a " + future_cell.resource.upper() + " resource. /n /n"
                public_opinion_increase += 3
            else:
                text += "The expedition has  discovered a " + future_cell.terrain.upper() + " tile. /n /n"
        else:
            text += "You were not able to explore the tile. /n /n"
        if roll_result <= self.current_max_crit_fail:
            text += "Everyone in the expedition has died. /n /n" #actual death occurs when exploration completes

        if public_opinion_increase > 0:
            text += "The Royal Geographical Society is pleased with these findings, increasing your public opinion by " + str(public_opinion_increase) + ". /n /n"

        if (not self.veteran) and roll_result >= self.current_min_crit_success:
            self.veteran = True
            self.just_promoted = True
            text += "This explorer is now a veteran. /n /n"
        
        if roll_result >= self.current_min_success:
            self.destination_cell = future_cell
            self.destination_cells = [] #used for off tile exploration, like when seeing nearby tiles when on water
            self.public_opinion_increases = []
            notification_tools.display_notification(text + "Click to remove this notification.", 'final_exploration', self.global_manager)
        else:
            notification_tools.display_notification(text, 'default', self.global_manager)
        self.global_manager.set('exploration_result', [self, roll_result, x_change, y_change, public_opinion_increase])

    def complete_exploration(self): #roll_result, x_change, y_change
        '''
        Description:
            Used when the player finishes rolling for an exploration, shows the exploration's results and makes any changes caused by the result. If successful, the expedition moves into the explored area, consumes its movement
                points, promotes its explorer to a veteran on critical success. If not successful, the expedition consumes its movement points and dies on critical failure
        Input:
            None
        Output:
            None
        '''
        exploration_result = self.global_manager.get('exploration_result')
        roll_result = exploration_result[1]
        x_change = exploration_result[2]
        y_change = exploration_result[3]
        self.global_manager.get('public_opinion_tracker').change(exploration_result[4])
        future_cell = self.grid.find_cell(x_change + self.x, y_change + self.y)
        died = False
        if roll_result >= self.current_min_success:
            future_cell.set_visibility(True)
            if self.movement_points >= self.get_movement_cost(x_change, y_change):
                if self.can_move(x_change, y_change): #checks for npmobs in explored tile
                    self.move(x_change, y_change)
                else:
                    self.global_manager.get('minimap_grid').calibrate(self.x, self.y) #changes minimap to show unexplored tile without moving
            else:
                notification_tools.display_notification("This unit's " + str(self.movement_points) + " remaining movement points are not enough to move into the newly explored tile. /n /n", 'default', self.global_manager)
                self.global_manager.get('minimap_grid').calibrate(self.x, self.y)
        self.set_movement_points(0)
        if self.just_promoted:
            self.promote()
        elif roll_result <= self.current_max_crit_fail:
            self.die()
            died = True
        actor_utility.stop_exploration(self.global_manager) #make function that sets ongoing exploration to false and destroys exploration marks

    def resolve_off_tile_exploration(self):
        '''
        Description:
            Whenever an expedition arrives in a tile for any reason, they automatically discover any adjacent water tiles. Additionally, when standing on water, they automatically discover all adjacent tiles
        Input:
            None
        Output:
            None
        '''
        cardinal_directions = {'up': 'north', 'down': 'south', 'right': 'east', 'left': 'west'}
        current_cell = self.images[0].current_cell
        for current_direction in ['up', 'down', 'left', 'right']:
            target_cell = current_cell.adjacent_cells[current_direction]
            if (not target_cell == 'none') and (not target_cell.visible):
                if current_cell.terrain == 'water' or target_cell.terrain == 'water': #if on water, discover all adjacent undiscovered tiles. Also, discover all adjacent water tiles, regardless of if currently on water
                    if current_cell.terrain == 'water':
                        text = "From the water, the expedition has discovered a "
                    elif target_cell.terrain == 'water':
                        text = "The expedition has discovered a "
                    public_opinion_increase = random.randrange(0, 3)
                    if not target_cell.resource == 'none':
                        if target_cell.resource == 'natives':
                            text += target_cell.terrain.upper() + " tile to the " + cardinal_directions[current_direction] + " that contains the village of " + target_cell.village.name + ". /n /n"
                        else:
                            text += target_cell.terrain.upper() + " tile with a " + target_cell.resource.upper() + " resource to the " + cardinal_directions[current_direction] + ". /n /n"
                        public_opinion_increase += 3
                    else:
                        text += target_cell.terrain.upper() + " tile to the " + cardinal_directions[current_direction] + ". /n /n"

                    if public_opinion_increase > 0:
                        text += "The Royal Geographical Society is pleased with these findings, increasing your public opinion by " + str(public_opinion_increase) + ". /n /n"
                    
                    self.destination_cells.append(target_cell)
                    self.public_opinion_increases.append(public_opinion_increase)
                    notification_tools.display_notification(text, 'off_tile_exploration', self.global_manager)
