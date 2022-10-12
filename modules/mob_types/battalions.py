#Contains functionality for battalions
import time
import random
from .groups import group
from ..tiles import tile
from .. import actor_utility
from .. import utility
from .. import notification_tools
from .. import text_tools
from .. import dice_utility

class battalion(group):
    '''
    A group with a major officer that can attack non-beast enemies
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
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(from_save, input_dict, global_manager)
        self.set_group_type('battalion')
        self.is_battalion = True
        if self.worker.worker_type == 'European':
            self.battalion_type = 'imperial'
        else: #colonial
            self.battalion_type = 'colonial'
        self.attack_cost = self.global_manager.get('action_prices')['attack']
        self.attack_mark_list = []
        if not from_save:
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #updates label to show new combat strength

    def get_movement_cost(self, x_change, y_change, post_attack = False):
        '''
        Description:
            Returns the cost in movement points of moving by the inputted amounts. Only works when one inputted amount is 0 and the other is 1 or -1, with 0 and -1 representing moving 1 cell downward
        Input:
            int x_change: How many cells would be moved to the right in the hypothetical movement
            int y_change: How many cells would be moved upward in the hypothetical movement
            boolean post_attack = False: Whether this movement is occuring directly after an attack order or not. A battalion/safari can move into a cell to attack it by using only 1 movement point but must return afterward if not
                enough movement points to move there normally
        Output:
            double: How many movement points would be spent by moving by the inputted amount
        '''
        cost = self.movement_cost
        if not (self.is_npmob and not self.visible()):
            local_cell = self.images[0].current_cell
        else:
            local_cell = self.grids[0].find_cell(self.x, self.y)

        direction = 'none'
        if x_change < 0:
            direction = 'left'
        elif x_change > 0:
            direction = 'right'
        elif y_change > 0:
            direction = 'up'
        elif y_change < 0:
            direction = 'down'
        elif x_change == 0 and y_change == 0:
            direction = 'none'
            
        if direction == 'none':
            adjacent_cell = local_cell
        else:
            adjacent_cell = local_cell.adjacent_cells[direction]
            
        if not adjacent_cell == 'none':
            if (not post_attack) and self.is_battalion and not adjacent_cell.get_best_combatant('npmob') == 'none': #if battalion attacking non-beast
                cost = 1
            elif (not post_attack) and self.is_safari and not adjacent_cell.get_best_combatant('npmob', 'beast') == 'none': #if safari attacking beast
                cost = 1
            else:
                cost = cost * self.global_manager.get('terrain_movement_cost_dict')[adjacent_cell.terrain]
            
                if self.is_pmob:
                    if local_cell.has_building('road') or local_cell.has_building('railroad'): #if not local_infrastructure == 'none':
                        if adjacent_cell.has_building('road') or adjacent_cell.has_building('railroad'): #if not adjacent_infrastructure == 'none':
                            cost = cost / 2
                    if (not adjacent_cell.visible) and self.can_explore:
                        cost = self.movement_cost
        return(cost)

    def move(self, x_change, y_change, attack_confirmed = False):
        '''
        Description:
            Moves this mob x_change to the right and y_change upward. Moving to a ship in the water automatically embarks the ship. If moving into a cell with an npmob, asks for a confirmation to attack instead of moving. If the attack
                is confirmed, move is called again to cause a combat to start
        Input:
            int x_change: How many cells are moved to the right in the movement
            int y_change: How many cells are moved upward in the movement
            boolean attack_confirmed = False: Whether an attack has already been confirmed. If an attack has been confirmed, a move into the target cell will occur and a combat will start
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
        if self.is_battalion:
            defender = future_cell.get_best_combatant('npmob')
        elif self.is_safari:
            defender = future_cell.get_best_combatant('npmob', 'beast')
        
        if (not attack_confirmed) and (not defender == 'none'): #if enemy in destination tile and attack not confirmed yet
            if self.global_manager.get('money_tracker').get() >= self.attack_cost:
                if self.check_if_minister_appointed():
                    choice_info_dict = {'battalion': self, 'x_change': x_change, 'y_change': y_change, 'cost': self.attack_cost, 'type': 'combat'}
                    
                    message = ""

                    risk_value = -1 * self.get_combat_modifier() #should be low risk with +2/veteran, moderate with +2 or +1/veteran, high with +1
                    if self.veteran: #reduce risk if veteran
                        risk_value -= 1
                    if defender.npmob_type == 'beast':
                        if self.is_safari:
                            risk_value -= 3
                        elif self.is_battalion:
                            risk_value += 1

                    if risk_value < -2:
                        message = "RISK: LOW /n /n" + message  
                    elif risk_value == -2:
                        message = "RISK: MODERATE /n /n" + message
                    elif risk_value == -1: #2/6 = high risk
                        message = "RISK: HIGH /n /n" + message
                    elif risk_value > 0:
                        message = "RISK: DEADLY /n /n" + message

                    if defender.npmob_type == 'beast':
                        notification_tools.display_choice_notification(message + "Are you sure you want to spend " + str(choice_info_dict['cost']) + " money to hunt the " + defender.name + " to the " + direction + "? /n /nRegardless of the result, the rest of this unit's movement points will be consumed.",
                            ['attack', 'stop attack'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager
                    else:
                        notification_tools.display_choice_notification(message + "Are you sure you want to spend " + str(choice_info_dict['cost']) + " money to attack the " + defender.name + " to the " + direction + "? /n /nRegardless of the result, the rest of this unit's movement points will be consumed.",
                            ['attack', 'stop attack'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager
                    self.global_manager.set('ongoing_combat', True)
                    for current_grid in self.grids:
                        coordinates = (0, 0)
                        if current_grid.is_mini_grid:
                            coordinates = current_grid.get_mini_grid_coordinates(self.x + x_change, self.y + y_change)
                        else:
                            coordinates = (self.x + x_change, self.y + y_change)
                        input_dict = {}
                        input_dict['coordinates'] = coordinates
                        input_dict['grid'] = current_grid
                        input_dict['image'] = 'misc/attack_mark/' + direction + '.png'
                        input_dict['name'] = 'exploration mark'
                        input_dict['modes'] = ['strategic']
                        input_dict['show_terrain'] = False
                        self.attack_mark_list.append(tile(False, input_dict, self.global_manager))
            else:
                if defender.npmob_type == 'beast':
                    text_tools.print_to_screen("You do not have enough money to supply a hunt.", self.global_manager)
                else:
                    text_tools.print_to_screen("You do not have enough money to supply an attack.", self.global_manager)
        elif defender == 'none' and ((self.is_battalion and not future_cell.get_best_combatant('npmob', 'beast') == 'none') or (self.is_safari and not future_cell.get_best_combatant('npmob') == 'none')): #if wrong type of defender present
            if self.is_battalion:
                text_tools.print_to_screen("Battalions can not attack beasts.", self.global_manager)
            elif self.is_safari:
                text_tools.print_to_screen("Safaris can only attack beasts.", self.global_manager)
        else: #if destination empty and
            initial_movement_points = self.movement_points
            super().move(x_change, y_change)
            if attack_confirmed:
                self.set_movement_points(initial_movement_points) #gives back movement points for moving, movement points will be consumed anyway for attacking but will allow unit to move onto beach after disembarking ship
            if not self.in_vehicle:
                self.attempt_local_combat()

    def attempt_local_combat(self):
        '''
        Description:
            When this unit moves, it checks if combat is possible in the cell it moved into. If combat is possible, it will immediately start a combat with the strongest local non-beast npmob and pay to supply the attack
        Input:
            None
        Output:
            None
        '''
        defender = self.images[0].current_cell.get_best_combatant('npmob')
        if not defender == 'none':
            self.global_manager.get('money_tracker').change(self.attack_cost * -1, 'combat supplies')
            self.start_combat('attacking', defender)

    def remove_attack_marks(self):
        '''
        Description:
            Removes all of the attack marks used to show the direction of a proposed attack during its confirmation
        Input:
            None
        Output:
            None
        '''
        for attack_mark in self.attack_mark_list:
            attack_mark.remove()
        self.attack_mark_list = []

    def start_capture_slaves(self):
        '''
        Description:
            Used when the player clicks on the start capturing slaves, displays a choice notification that allows the player to capture slaves or not. Choosing to capture slaves starts the slave capture and consumes the battalion's
                movement points
        Input:
            None
        Output:
            None
        '''
        village = self.images[0].current_cell.get_building('village')
        self.current_roll_modifier = 0
        self.current_min_success = self.default_min_success
        self.current_max_crit_fail = 2 #higher than usual
        self.current_min_crit_success = self.default_min_crit_success
        message = "Are you sure you want to attempt to capture slaves? If successful, captures 1 of the village's population as a unit of slave workers. /n /n"
        message += "Regardless of success, this may increase the village's aggressiveness and/or decrease public opinion. /n /n"
        message += "The attack will cost " + str(self.global_manager.get('action_prices')['capture_slaves']) + " money. /n /n "
            
        aggressiveness_modifier = village.get_aggressiveness_modifier()
        if aggressiveness_modifier < 0:
            message += "The villagers are hostile and are likely to resist capture. /n /n"
        elif aggressiveness_modifier > 0:
            message += "The villagers are friendly and may not suspect your harmful intentions. /n /n"
        else:
            message += "The villagers are wary of the battalion and may resist capture. /n /n"
        self.current_roll_modifier += aggressiveness_modifier

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
            
        self.current_min_success -= self.current_roll_modifier #positive modifier reduces number required for succcess, reduces maximum that can be crit fail
        self.current_max_crit_fail -= self.current_roll_modifier
        if self.current_min_success > self.current_min_crit_success:
            self.current_min_crit_success = self.current_min_success #if 6 is a failure, should not be critical success. However, if 6 is a success, it will always be a critical success
        choice_info_dict = {'battalion': self,'type': 'start capture slaves'}
        self.current_roll_modifier = 0
        self.global_manager.set('ongoing_slave_capture', True)
        notification_tools.display_choice_notification(message, ['start capture slaves', 'stop capture slaves'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager+

    def capture_slaves(self):
        '''
        Description:
            Controls the slave capture process, determining and displaying its result through a series of notifications
        Input:
            None
        Output:
            None
        '''
        roll_result = 0
        self.just_promoted = False
        self.set_movement_points(0)

        if self.veteran: #tells notifications how many of the currently selected mob's dice to show while rolling
            num_dice = 2
        else:
            num_dice = 1

        if not self.global_manager.get('action_prices')['capture_slaves'] == 0:
            self.global_manager.get('money_tracker').change(self.global_manager.get('action_prices')['capture_slaves'] * -1, 'slave capture')
        self.global_manager.get('evil_tracker').change(3)
        village = self.images[0].current_cell.get_building('village')
        text = ""
        text += "The battalion tries to capture the natives as slaves. /n /n"

        if not self.veteran:    
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required to succeed.", 'slave_capture', self.global_manager, num_dice)
        else:
            text += ("The veteran major can roll twice and pick the higher result. /n /n")
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required on at least 1 die to succeed.", 'slave_capture', self.global_manager, num_dice)

        notification_tools.display_notification(text + "Rolling... ", 'roll', self.global_manager, num_dice)

        die_x = self.global_manager.get('notification_manager').notification_x - 140

        minister_corrupt = self.controlling_minister.check_corruption()
        if minister_corrupt:
            self.controlling_minister.steal_money(self.global_manager.get('action_prices')['capture_slaves'], 'slave capture')
            
        if self.veteran:
            if minister_corrupt:
                first_roll = random.randrange(self.current_max_crit_fail + 1, self.current_min_success)
                second_roll = random.randrange(1, self.current_min_success)
                if random.randrange(1, 7) >= 4:
                    results = [first_roll, second_roll]
                else:
                    results = [second_roll, first_roll]
            else:
                results = [self.controlling_minister.no_corruption_roll(6), self.controlling_minister.no_corruption_roll(6)]
            #results = self.controlling_minister.roll_to_list(6, self.current_min_success, self.current_max_crit_fail, self.global_manager.get('action_prices')['convert'], 'slave capture', 2)
            first_roll_list = dice_utility.roll_to_list(6, "Slave capture roll", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, results[0])
            self.display_die((die_x, 500), first_roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)
           
            second_roll_list = dice_utility.roll_to_list(6, "second", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, results[1])
            self.display_die((die_x, 380), second_roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)
                                
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
            if minister_corrupt:
                result = random.randrange(self.current_max_crit_fail + 1, self.current_min_success)
            else:
                result = self.controlling_minister.no_corruption_roll(6)
            roll_list = dice_utility.roll_to_list(6, "Slave capture roll", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, result)
            self.display_die((die_x, 440), roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)
                
            text += roll_list[1]
            roll_result = roll_list[0]

        notification_tools.display_notification(text + "Click to continue.", 'slave_capture', self.global_manager, num_dice)
            
        text += "/n"
        if roll_result >= self.current_min_success: #4+ required on D6 for exploration
            text += "/nThe battalion successfully captured enough slaves to create a slave workers unit. /n "
        else:
            text += "/nA majority of the natives managed to evade capture. /n "
        if roll_result <= self.current_max_crit_fail:
            text += "/nAngered by the battalion's brutal attempts at subjugation, the natives attack the battalion. /n " # The entire group of missionaries has died"

        if (not self.veteran) and roll_result >= self.current_min_crit_success:
            self.just_promoted = True
            text += " /nThe major has gained insights into the optimal strategies to intimidate and defeat the African natives. /n"
            text += " /nThe major is now a veteran and will be more successful in future ventures. /n"

        if (not minister_corrupt) and random.randrange(1, 7) >= 4 and (not village.aggressiveness >= 9):
            village_aggressiveness_increase = 1
            text += " /nThe natives of this village have grown wary of and even vengeful torwards the invaders, increasing their aggressiveness by 1. /n"
        else:
            village_aggressiveness_increase = 0
            
        public_opinion_decrease = 0
        if not minister_corrupt:
            public_opinion_decrease = -1 * random.randrange(0, 3)
            text += "/nRumors of your company's brutal treatment of the natives reaches Europe, decreasing public opinion by " + str(-1 * public_opinion_decrease) + ". /n"

        if roll_result >= self.current_min_success:
            notification_tools.display_notification(text + "/nClick to remove this notification.", 'final_slave_capture', self.global_manager)
        else:
            notification_tools.display_notification(text, 'default', self.global_manager)
        self.global_manager.set('capture_slaves_result', [self, roll_result, village, public_opinion_decrease, village_aggressiveness_increase])

    def complete_capture_slaves(self):
        '''
        Description:
            Used when the player finishes rolling for slave capture, shows the conversion's results and makes any changes caused by the result. If successful, capture village population unit as slaves, promotes major to a veteran on
                critical success. Native warriors spawn on critical failure. Regardless of success, may decrease public opinion and/or increase aggressiveness
        Input:
            None
        Output:
            None
        '''
        roll_result = self.global_manager.get('capture_slaves_result')[1]
        village = self.global_manager.get('capture_slaves_result')[2]
        public_opinion_decrease = self.global_manager.get('capture_slaves_result')[3]
        village_aggressiveness_increase = self.global_manager.get('capture_slaves_result')[4]
        
        village.change_aggressiveness(village_aggressiveness_increase)
        if roll_result >= self.current_min_success: #if campaign succeeded

            input_dict = {}
            input_dict['coordinates'] = (self.x, self.y)
            input_dict['grids'] = self.grids
            input_dict['image'] = 'mobs/slave workers/default.png'
            input_dict['name'] = 'slave workers'
            input_dict['modes'] = ['strategic']
            input_dict['init_type'] = 'slaves'
            input_dict['purchased'] = False
            input_dict['worker_type'] = 'slave' #not european - doesn't count as a European worker for upkeep
            self.global_manager.get('actor_creation_manager').create(False, input_dict, self.global_manager)

            village.change_population(-1)
            if roll_result >= self.current_min_crit_success and not self.veteran:
                self.promote()

        if roll_result <= self.current_max_crit_fail:
            warrior = village.spawn_warrior()
            warrior.show_images()
            warrior.attack_on_spawn()
        self.global_manager.set('ongoing_slave_capture', False)

class safari(battalion):
    '''
    A group with a hunter officer that can track down and attack beast enemies
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
        self.set_group_type('safari')
        self.is_battalion = False
        self.is_safari = True
        self.can_swim = True
        self.can_swim_river = True
        self.can_swim_ocean = False
        
        self.has_canoes = True
        self.image_dict['canoes'] = input_dict['canoes_image']
        self.image_dict['no_canoes'] = self.image_dict['default']
        self.update_canoes()
        
        self.battalion_type = 'none'
        self.attack_cost = self.global_manager.get('action_prices')['hunt']
        if not from_save:
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #updates label to show new combat strength

    def attempt_local_combat(self):
        '''
        Description:
            When this unit moves, it checks if combat is possible in the cell it moved into. If combat is possible, it will immediately start a combat with the strongest local beast npmob and pay to supply the hunt
        Input:
            None
        Output:
            None
        '''
        defender = self.images[0].current_cell.get_best_combatant('npmob', 'beast')
        if not defender == 'none':
            self.global_manager.get('money_tracker').change(self.attack_cost * -1, 'hunting supplies')
            self.start_combat('attacking', defender)

    def track_beasts(self):
        '''
        Description:
            Spends 1 movement point to check this tile and all adjacent explored tiles for beasts, revealing all nearby beasts on a 4+ roll. If a 6 is rolled, hunter becomes veteran. If a beast is found on the safari's tile, it will
                attack and be revealed afterward for the safari to follow up against
        '''
        result = self.controlling_minister.no_corruption_roll(6)
        if self.veteran:
            second_result = self.controlling_minister.no_corruption_roll(6)
            if second_result > result:
                result = second_result
        beasts_found = []
        ambush_list = []
        if result >= 4:
            for current_beast in self.global_manager.get('beast_list'):
                if current_beast.hidden:
                    if utility.find_grid_distance(self, current_beast) <= 1: #if different by 1 in x or y or at same coordinates
                        beast_cell = self.grids[0].find_cell(current_beast.x, current_beast.y)
                        if beast_cell.visible: #if beasts's cell has been discovered
                            current_beast.set_hidden(False)
                            beasts_found.append(current_beast)
        text = ""
        if len(beasts_found) == 0:
            text += "Though beasts may still be hiding nearby, the safari was not able to successfully track any beasts. /n /n"
        else:
            text = ""
            for current_beast in beasts_found:
                if current_beast.x == self.x and current_beast.y == self.y:
                    text += "As the safari starts searching for their quarry, they soon realize that the " + current_beast.name + " had been stalking them the whole time. They have only moments to prepare for the ambush. /n /n"
                    ambush_list.append(current_beast)
                elif current_beast.x > self.x:
                    text += "The safari finds signs of " + utility.generate_article(current_beast.name) + " " + current_beast.name + " to the east. /n /n"
                elif current_beast.x < self.x:
                    text += "The safari finds signs of " + utility.generate_article(current_beast.name) + " " + current_beast.name + " to the west. /n /n"
                elif current_beast.y > self.y:
                    text += "The safari finds signs of " + utility.generate_article(current_beast.name) + " " + current_beast.name + " to the north. /n /n"
                elif current_beast.y < self.y:
                    text += "The safari finds signs of " + utility.generate_article(current_beast.name) + " " + current_beast.name + " to the south. /n /n"
                current_beast.set_hidden(False)
                current_beast.just_revealed = True
            if result == 6 and not self.veteran:
                text += "This safari's hunter tracked the " + random.choice(beasts_found).name + " well enough to become a veteran. /n /n"
                self.promote()

        self.controlling_minister.display_message(text)
        for current_beast in ambush_list:
            current_beast.attempt_local_combat()
        self.change_movement_points(-1)
