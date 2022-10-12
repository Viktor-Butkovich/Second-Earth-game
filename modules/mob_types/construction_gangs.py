#Contains functionality for construction gangs

from .groups import group
from .. import actor_utility
from .. import dice_utility
from .. import notification_tools

class construction_gang(group):
    '''
    A group with an engineer officer that is able to construct/upgrade buildings and trains
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
        self.can_construct = True
        self.set_group_type('construction_gang')
        if not from_save:
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #updates mob info display list to account for can_construct changing

    def start_upgrade(self, building_info_dict):
        '''
        Description
            Used when the player clicks on an upgrade building button, displays a choice notification that allows the player to upgrade it or not. Choosing to construct starts the upgrade process, costs an amount based on the number of
                previous upgrades to that building, and consumes the construction gang's movement points
        Input:
            dictionary building_info_dict: string keys corresponding to various values used to determine the building constructed
                string upgrade_type: type of upgrade, like 'scale' or 'efficiency'
                string building_name: name of building, like 'ivory camp'
                building upgraded_building: building object being upgraded
        Output:
            None
        '''
        self.upgrade_type = building_info_dict['upgrade_type']
        self.building_name = building_info_dict['building_name']
        self.upgraded_building = building_info_dict['upgraded_building']
        
        self.current_roll_modifier = 0
        self.current_min_success = self.default_min_success
        self.current_max_crit_fail = 0 #construction shouldn't have critical failures
        self.current_min_crit_success = self.default_min_crit_success
        
        self.current_min_success -= self.current_roll_modifier #positive modifier reduces number required for succcess, reduces maximum that can be crit fail
        self.current_max_crit_fail -= self.current_roll_modifier
        if self.current_min_success > self.current_min_crit_success:
            self.current_min_crit_success = self.current_min_success #if 6 is a failure, should not be critical success. However, if 6 is a success, it will always be a critical success
        choice_info_dict = {'constructor': self, 'type': 'start upgrade'}
        self.global_manager.set('ongoing_construction', True)
        if self.building_name == 'warehouses':
            message = "Are you sure you want to start upgrading this tile's warehouses? /n /n"
        else:
            message = "Are you sure you want to start upgrading the " + self.building_name + "'s " + self.upgrade_type + "? /n /n"
        message += "The planning and materials will cost " + str(self.upgraded_building.get_upgrade_cost()) + " money.  Each upgrade to a building increases the cost of all future upgrades for that building. /n /n"
        if self.upgrade_type == 'efficiency':
            message += "If successful, each work crew attached to this " + self.building_name + " will be able to make an additional attempt to produce commodities each turn."
        elif self.upgrade_type == 'scale':
            message += "If successful, the maximum number of work crews able to be attached to this " + self.building_name + " will increase by 1."
        elif self.upgrade_type == 'warehouse_level':
            message += "If successful, the warehouses' level will increase by 1, increasing the tile's inventory capacity by 9."
        else:
            message += "Placeholder upgrade description"
        message += " /n /n"
            
        notification_tools.display_choice_notification(message, ['start upgrade', 'stop upgrade'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager

    def upgrade(self):
        '''
        Description:
            Controls the upgrade process, determining and displaying its result through a series of notifications
        Input:
            None
        Output:
            None
        '''
        self.current_construction_type = 'upgrade'
        roll_result = 0
        self.just_promoted = False
        self.set_movement_points(0)

        if self.veteran: #tells notifications how many of the currently selected mob's dice to show while rolling
            num_dice = 2
        else:
            num_dice = 1
        
        self.global_manager.get('money_tracker').change(self.upgraded_building.get_upgrade_cost() * -1, 'construction')
        text = ""
        if self.building_name == 'warehouses':
            text += "The " + self.name + " attempts to upgrade the warehouses. /n /n"
        else:
            text += "The " + self.name + " attempts to upgrade the " + self.building_name + "'s " + self.upgrade_type + ". /n /n"
        if not self.veteran:    
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required to succeed.", 'construction', self.global_manager, num_dice)
        else:
            text += ("The " + self.officer.name + " can roll twice and pick the higher result. /n /n")
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required on at least 1 die to succeed.", 'construction', self.global_manager, num_dice)

        notification_tools.display_notification(text + "Rolling... ", 'roll', self.global_manager, num_dice)

        die_x = self.global_manager.get('notification_manager').notification_x - 140

        if self.veteran:
            results = self.controlling_minister.roll_to_list(6, self.current_min_success, self.current_max_crit_fail, self.upgraded_building.get_upgrade_cost(), 'construction', 2)
            first_roll_list = dice_utility.roll_to_list(6, "Construction roll", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, results[0])
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
            result = self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail, self.upgraded_building.get_upgrade_cost(), 'construction')
            roll_list = dice_utility.roll_to_list(6, "Construction roll", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, result)
            self.display_die((die_x, 440), roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)
                
            text += roll_list[1]
            roll_result = roll_list[0]

        notification_tools.display_notification(text + "Click to continue.", 'construction', self.global_manager, num_dice)
            
        text += "/n"
        if roll_result >= self.current_min_success: #4+ required on D6 for upgrade
            if self.building_name == 'warehouses':
                text += "The " + self.name + " successfully upgraded the warehouses. /n"
            else: 
                text += "The " + self.name + " successfully upgraded the " + self.building_name + "'s " + self.upgrade_type + ". /n"
        else:
            text += "Little progress was made and the " + self.officer.name + " requests more time and funds to complete the upgrade. /n"

        if (not self.veteran) and roll_result >= self.current_min_crit_success:
            self.just_promoted = True
            text += " /nThe " + self.officer.name + " managed the construction well enough to become a veteran. /n"
        if roll_result >= 4:
            notification_tools.display_notification(text + " /nClick to remove this notification.", 'final_construction', self.global_manager)
        else:
            notification_tools.display_notification(text, 'default', self.global_manager)
        self.global_manager.set('construction_result', [self, roll_result])  

        
    def complete_upgrade(self):
        '''
        Description:
            Used when the player finishes rolling for an upgrade, shows the upgrade's results and makes any changes caused by the result. If successful, the building is upgraded in a certain field, promotes engineer to a veteran on
                critical success
        Input:
            None
        Output:
            None
        '''
        roll_result = self.global_manager.get('construction_result')[1]
        if roll_result >= self.current_min_success: #if upgrade succeeded
            if roll_result >= self.current_min_crit_success and not self.veteran:
                self.promote()
            self.set_movement_points(0)
            self.upgraded_building.upgrade(self.upgrade_type)
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.images[0].current_cell.tile) #update tile display to show building upgrade
        self.global_manager.set('ongoing_construction', False)
