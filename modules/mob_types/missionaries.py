#Contains functionality for missionaries

import random
from .groups import group
from .. import actor_utility
from .. import dice_utility
from .. import utility
from .. import notification_tools

class missionaries(group):
    '''
    A group with an evangelist officer and church volunteer workers that can build churches and convert native villages
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
        self.number = 2 #missionaries is plural
        self.can_convert = True
        self.set_group_type('missionaries')
        if not from_save:
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #updates mob info display list to account for new missionary actions

    def start_converting(self):
        '''
        Description:
            Used when the player clicks on the start converting button, displays a choice notification that allows the player to convert or not. Choosing to convert starts the conversion process and consumes the missionaries'
                movement points
        Input:
            None
        Output:
            None
        '''
        village = self.images[0].current_cell.get_building('village')
        self.current_roll_modifier = 0
        self.current_min_success = self.default_min_success
        self.current_max_crit_fail = self.default_max_crit_fail
        self.current_min_crit_success = self.default_min_crit_success
        message = "Are you sure you want to attempt to convert the natives? If successful, the natives will be less aggressive and easier to cooperate with. /n /n"
        message += "The conversion will cost " + str(self.global_manager.get('action_prices')['convert']) + " money. /n /n "
                            
        if not village.cell.has_intact_building('mission'): #penalty for no mission
            self.current_roll_modifier -= 1
            message += "Without an established mission, the missionaries will have difficulty converting the villagers. /n /n"
            
        aggressiveness_modifier = village.get_aggressiveness_modifier()
        if aggressiveness_modifier < 0:
            message += "The villagers are hostile and are unlikely to listen to the teachings of the missionaries. /n /n"
        elif aggressiveness_modifier > 0:
            message += "The villagers are friendly and are likely to listen to the teachings of the missionaries. /n /n"
        else:
            message += "The villagers are wary of the missionaries but may be willing to listen to their teachings. /n /n"
        self.current_roll_modifier += aggressiveness_modifier

        population_modifier = village.get_population_modifier()
        if population_modifier < 0:
            message += "The high population of this village will require more effort to convert. /n /n"
        elif population_modifier > 0:
            message += "The low population of this village will require less effort to convert. /n /n"
        self.current_roll_modifier += population_modifier

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
        
        choice_info_dict = {'evangelist': self,'type': 'start converting'}
        self.current_roll_modifier = 0
        if self.current_min_success > 6:
            message += "As a " + str(self.current_min_success) + "+ would be required to succeed this roll, it is impossible and may not be attempted. Build a mission to reduce the roll's difficulty. /n /n"
            notification_tools.display_notification(message, 'default', self.global_manager)
        else:
            self.global_manager.set('ongoing_conversion', True)
            notification_tools.display_choice_notification(message, ['start converting', 'stop converting'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager+

    def convert(self):
        '''
        Description:
            Controls the conversion process, determining and displaying its result through a series of notifications
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
        
        self.global_manager.get('money_tracker').change(self.global_manager.get('action_prices')['convert'] * -1, 'religious conversion')
        village = self.images[0].current_cell.get_building('village')
        text = ""
        text += "The missionaries try to convert the natives to reduce their aggressiveness. /n /n"

        if not self.veteran:    
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required to succeed.", 'convert', self.global_manager, num_dice)
        else:
            text += ("The veteran evangelist can roll twice and pick the higher result. /n /n")
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required on at least 1 die to succeed.", 'convert', self.global_manager, num_dice)

        notification_tools.display_notification(text + "Rolling... ", 'roll', self.global_manager, num_dice)

        die_x = self.global_manager.get('notification_manager').notification_x - 140

        if self.veteran:
            results = self.controlling_minister.roll_to_list(6, self.current_min_success, self.current_max_crit_fail, self.global_manager.get('action_prices')['convert'], 'conversion', 2)
            first_roll_list = dice_utility.roll_to_list(6, "Conversion roll", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, results[0])
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
            result = self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail, self.global_manager.get('action_prices')['convert'], 'conversion')
            roll_list = dice_utility.roll_to_list(6, "Conversion roll", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, result)
            self.display_die((die_x, 440), roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)
                
            text += roll_list[1]
            roll_result = roll_list[0]

        notification_tools.display_notification(text + "Click to continue.", 'conversion', self.global_manager, num_dice)
            
        text += "/n"
        if roll_result >= self.current_min_success: #4+ required on D6 for exploration
            text += "The missionaries have made progress in converting the natives and have reduced their aggressiveness from " + str(village.aggressiveness) + " to " + str(village.aggressiveness - 1) + ". /n /n"
        else:
            text += "The missionaries made little progress in converting the natives. /n /n"
        if roll_result <= self.current_max_crit_fail:
            text += "Angered by the missionaries' attempts to destroy their spiritual traditions, the natives attack the missionaries. " # The entire group of missionaries has died"
            #if village.cell.has_intact_building('mission'):
            #    text += " and the village's mission has been damaged."
            text += ". /n"

        if (not self.veteran) and roll_result >= self.current_min_crit_success:
            self.just_promoted = True
            text += " /nThe evangelist has gained insights into converting natives and demonstrating connections between their beliefs and Christianity. /n"
            text += " /nThe evangelist is now a veteran and will be more successful in future ventures. /n"
            
        public_opinion_increase = 0
        if roll_result >= self.current_min_success:
            public_opinion_increase = random.randrange(0, 2)
            if public_opinion_increase > 0:
                text += "/nWorking to fulfill your company's proclaimed mission of enlightening the heathens of Africa has increased your public opinion by " + str(public_opinion_increase) + ". /n"
            notification_tools.display_notification(text + "/nClick to remove this notification.", 'final_conversion', self.global_manager)
        else:
            notification_tools.display_notification(text, 'default', self.global_manager)
        self.global_manager.set('conversion_result', [self, roll_result, village, public_opinion_increase])

    def complete_conversion(self):
        '''
        Description:
            Used when the player finishes rolling for religious conversion, shows the conversion's results and makes any changes caused by the result. If successful, reduces village aggressiveness, promotes evangelist to a veteran on
                critical success. Native warriors spawn on critical failure
        Input:
            None
        Output:
            None
        '''
        roll_result = self.global_manager.get('conversion_result')[1]
        village = self.global_manager.get('conversion_result')[2]
        public_opinion_increase = self.global_manager.get('conversion_result')[3]
        if roll_result >= self.current_min_success: #if campaign succeeded
            village.change_aggressiveness(-1)
            self.global_manager.get('public_opinion_tracker').change(public_opinion_increase)
            if roll_result >= self.current_min_crit_success and not self.veteran:
                self.promote()
        if roll_result <= self.current_max_crit_fail:
            warrior = village.spawn_warrior()
            warrior.show_images()
            warrior.attack_on_spawn()
        self.global_manager.set('ongoing_conversion', False)
