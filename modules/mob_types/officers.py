#Contains functionality for officer units
import random

from .pmobs import pmob
from ..tiles import status_icon
from .. import actor_utility
from .. import utility
from .. import notification_tools
from .. import text_tools
from .. import market_tools
from .. import dice_utility
from .. import scaling
from .. import images

class officer(pmob):
    '''
    pmob that is considered an officer and can join groups and become a veteran
    '''
    def __init__(self, from_save, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'grids': grid list value - grids in which this mob's images can appear
                'image': string value - File path to the image used by this object
                'name': string value - Required if from save, this mob's name
                'modes': string list value - Game modes during which this mob's images can appear
                'officer_type': string value - Type of officer that this is, like 'explorer', or 'engineer'
                'end_turn_destination': string or int tuple - Required if from save, 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'max_movement_points': int value - Required if from save, maximum number of movement points this mob can have
                'veteran': boolean value - Required if from save, whether this officer is a veteran
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(from_save, input_dict, global_manager)
        global_manager.get('officer_list').append(self)
        self.is_officer = True
        self.officer_type = input_dict['officer_type']
        self.set_controlling_minister_type(self.global_manager.get('officer_minister_dict')[self.officer_type])
        if not from_save:
            self.veteran = False
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #updates mob info display list to account for is_officer changing
            self.selection_sound()
        else:
            self.veteran = input_dict['veteran']
            if self.veteran:
                self.load_veteran()

    def replace(self, attached_group = 'none'):
        '''
        Description:
            Replaces this unit for a new version of itself when it dies from attrition, removing all experience and name modifications. Also charges the usual officer recruitment cost
        Input:
            None
        Output:
            None
        '''
        super().replace()
        self.global_manager.get('money_tracker').change(self.global_manager.get('recruitment_costs')[self.default_name] * -1, 'attrition replacements')
        if not attached_group == 'none':
            attached_group.set_name(attached_group.default_name)
            attached_group.veteran = False
            new_status_icons = []
            for current_status_icon in attached_group.status_icons:
                if current_status_icon.status_icon_type == 'veteran':
                    current_status_icon.remove()
                else:
                    new_status_icons.append(current_status_icon)
            attached_group.status_icons = new_status_icons

    def to_save_dict(self):
        '''
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                Along with superclass outputs, also saves the following values:
                'officer_type': Type of officer that this is, like 'explorer' or 'engineer'
                'veteran': Whether this officer is a veteran
        '''
        save_dict = super().to_save_dict()
        save_dict['officer_type'] = self.officer_type
        save_dict['veteran'] = self.veteran
        return(save_dict)

    def promote(self):
        '''
        Description:
            Promotes this officer to a veteran after performing various actions particularly well, improving the officer's future capabilities. Creates a veteran star icon that follows this officer
        Input:
            None
        Output:
            None
        '''
        self.just_promoted = False
        self.veteran = True
        self.set_name("veteran " + self.name)
        for current_grid in self.grids:
            if current_grid == self.global_manager.get('minimap_grid'):
                veteran_icon_x, veteran_icon_y = current_grid.get_mini_grid_coordinates(self.x, self.y)
            elif current_grid == self.global_manager.get('europe_grid'):
                veteran_icon_x, veteran_icon_y = (0, 0)
            else:
                veteran_icon_x, veteran_icon_y = (self.x, self.y)
            input_dict = {}
            input_dict['coordinates'] = (veteran_icon_x, veteran_icon_y)
            input_dict['grid'] = current_grid
            input_dict['image'] = 'misc/veteran_icon.png'
            input_dict['name'] = 'veteran icon'
            input_dict['modes'] = ['strategic', 'europe']
            input_dict['show_terrain'] = False
            input_dict['actor'] = self
            input_dict['status_icon_type'] = 'veteran'
            self.status_icons.append(status_icon(False, input_dict, self.global_manager))
        if self.global_manager.get('displayed_mob') == self:
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #updates actor info display with veteran icon

    def load_veteran(self):
        '''
        Description:
            Promotes this officer to a veteran while loading, changing the name as needed to prevent the word veteran from being added multiple times
        Input:
            None
        Output:
            None
        '''
        name = self.default_name
        self.promote()
        #self.set_name(name)
        if self.global_manager.get('displayed_mob') == self:
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self)

    def can_show_tooltip(self):
        '''
        Description:
            Returns whether this officer's tooltip can be shown. Along with the superclass' requirements, officer tooltips can not be shown when attached to another actor, such as when part of a group
        Input:
            None
        Output:
            None
        '''
        if not (self.in_group or self.in_vehicle):
            return(super().can_show_tooltip())
        else:
            return(False)

    def join_group(self):
        '''
        Description:
            Hides this officer when joining a group, preventing it from being directly interacted with until the group is disbanded
        Input:
            None
        Output:
            None
        '''
        self.in_group = True
        self.selected = False
        self.hide_images()
        self.remove_from_turn_queue()

    def leave_group(self, group):
        '''
        Description:
            Reveals this officer when its group is disbanded, allowing it to be directly interacted with. Also selects this officer, rather than the group's worker
        Input:
            group group: group from which this officer is leaving
        Output:
            None
        '''
        self.in_group = False
        self.x = group.x
        self.y = group.y
        self.show_images()
        #self.disorganized = group.disorganized #officers should not become disorganized
        self.go_to_grid(self.images[0].current_cell.grid, (self.x, self.y))
        self.select()
        if self.movement_points > 0:
            self.add_to_turn_queue()
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.images[0].current_cell.tile) #calibrate info display to officer's tile upon disbanding

    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        Input:
            None
        Output:
            None
        '''
        super().remove()
        self.global_manager.set('officer_list', utility.remove_from_list(self.global_manager.get('officer_list'), self))

class evangelist(officer):
    '''
    Officer that can start religious and public relations campaigns and can merge with church volunteers to form missionaries
    '''
    def __init__(self, from_save, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'grids': grid list value - grids in which this mob's images can appear
                'image': string value - File path to the image used by this object
                'name': string value - Required if from save, this mob's name
                'modes': string list value - Game modes during which this mob's images can appear
                'end_turn_destination': string or int tuple - Required if from save, 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'max_movement_points': int value - Required if from save, maximum number of movement points this mob can have
                'veteran': boolean value - Required if from save, whether this officer is a veteran
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['officer_type'] = 'evangelist'
        super().__init__(from_save, input_dict, global_manager)
        self.current_roll_modifier = 0
        self.default_min_success = 4
        self.default_max_crit_fail = 1
        self.default_min_crit_success = 6

    def start_religious_campaign(self): 
        '''
        Description:
            Used when the player clicks on the start religious campaign button, displays a choice notification that allows the player to campaign or not. Choosing to campaign starts the campaign process and consumes the evangelist's
                movement points
        Input:
            None
        Output:
            None
        '''
        self.current_roll_modifier = 0
        self.current_min_success = self.default_min_success
        self.current_max_crit_fail = self.default_max_crit_fail
        self.current_min_crit_success = self.default_min_crit_success
        
        self.current_min_success -= self.current_roll_modifier #positive modifier reduces number required for succcess, reduces maximum that can be crit fail
        self.current_max_crit_fail -= self.current_roll_modifier
        if self.current_min_success > self.current_min_crit_success:
            self.current_min_crit_success = self.current_min_success #if 6 is a failure, should not be critical success. However, if 6 is a success, it will always be a critical success
        choice_info_dict = {'evangelist': self,'type': 'start religious campaign'}
        self.global_manager.set('ongoing_religious_campaign', True)
        message = "Are you sure you want to start a religious campaign? /n /nIf successful, a religious campaign will convince church volunteers to join you, allowing the formation of groups of missionaries that can convert native "
        message += "villages. /n /n The campaign will cost " + str(self.global_manager.get('action_prices')['religious_campaign']) + " money. /n /n"
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
            
        notification_tools.display_choice_notification(message, ['start religious campaign', 'stop religious campaign'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager

    def religious_campaign(self): #called when start religious campaign clicked in choice notification
        '''
        Description:
            Controls the religious campaign process, determining and displaying its result through a series of notifications
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

        price = self.global_manager.get('action_prices')['religious_campaign']
        self.global_manager.get('money_tracker').change(self.global_manager.get('action_prices')['religious_campaign'] * -1, 'religious campaigns')
        actor_utility.double_action_price(self.global_manager, 'religious_campaign')
        text = ""
        text += "The evangelist campaigns for the support of church volunteers to join him in converting the African natives. /n /n"
        if not self.veteran:    
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required to succeed.", 'religious_campaign', self.global_manager, num_dice)
        else:
            text += ("The veteran evangelist can roll twice and pick the higher result. /n /n")
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required on at least 1 die to succeed.", 'religious_campaign', self.global_manager, num_dice)

        notification_tools.display_notification(text + "Rolling... ", 'roll', self.global_manager, num_dice)

        die_x = self.global_manager.get('notification_manager').notification_x - 140

        if self.veteran:
            results = self.controlling_minister.roll_to_list(6, self.current_min_success, self.current_max_crit_fail, price, 'religious campaign', 2)
            #result = self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail)
            first_roll_list = dice_utility.roll_to_list(6, "Religous campaign roll", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, results[0])
            self.display_die((die_x, 500), first_roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)

            #result = self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail)
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
            result = self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail, price, 'religious campaign')
            roll_list = dice_utility.roll_to_list(6, "Religious campaign roll", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, result)
            self.display_die((die_x, 440), roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)
                
            text += roll_list[1]
            roll_result = roll_list[0]

        notification_tools.display_notification(text + "Click to continue.", 'religious_campaign', self.global_manager, num_dice)
            
        text += "/n"
        if roll_result >= self.current_min_success: #4+ required on D6 for exploration
            text += "Inspired by the evangelist's message to save the heathens from their own ignorance, a group of church volunteers joins you. /n /n"
        else:
            text += "Whether by a lack of charisma, a reluctant audience, or a doomed cause, the evangelist fails to gather any volunteers. /n /n"
        if roll_result <= self.current_max_crit_fail:
            text += "The evangelist is disturbed by the lack of faith of your country's people and decides to abandon your company. /n /n" #actual 'death' occurs when religious campaign completes

        if (not self.veteran) and roll_result >= self.current_min_crit_success:
            self.just_promoted = True
            text += "With fiery word and true belief in his cause, the evangelist becomes a veteran and will be more successful in future ventures. /n /n"
        if roll_result >= 4:
            notification_tools.display_notification(text + "Click to remove this notification.", 'final_religious_campaign', self.global_manager)
        else:
            notification_tools.display_notification(text, 'default', self.global_manager)
        self.global_manager.set('religious_campaign_result', [self, roll_result])

    def complete_religious_campaign(self):
        '''
        Description:
            Used when the player finishes rolling for a religious campaign, shows the campaign's results and making any changes caused by the result. If successful, recruits church volunteers, promotes evangelist to a veteran on
                critical success. If not successful, the evangelist consumes its movement points and dies on critical failure
        Input:
            None
        Output:
            None
        '''
        roll_result = self.global_manager.get('religious_campaign_result')[1]
        if roll_result >= self.current_min_success: #if campaign succeeded
            input_dict = {}
            input_dict['coordinates'] = (0, 0)
            input_dict['grids'] = [self.global_manager.get('europe_grid')]
            input_dict['image'] = 'mobs/church_volunteers/default.png'
            input_dict['name'] = 'church volunteers'
            input_dict['modes'] = ['strategic', 'europe']
            input_dict['init_type'] = 'church_volunteers'
            input_dict['worker_type'] = 'religious' #not european - doesn't count as a European worker for upkeep
            church_volunteers = self.global_manager.get('actor_creation_manager').create(False, input_dict, self.global_manager)
            if roll_result >= self.current_min_crit_success and not self.veteran:
                self.promote()
            self.global_manager.get('actor_creation_manager').create_group(church_volunteers, self, self.global_manager)
            #for current_image in self.images: #move mob to front of each stack it is in - also used in button.same_tile_icon.on_click(), make this a function of all mobs to move to front of tile
            #    if not current_image.current_cell == 'none':
            #        while not self == current_image.current_cell.contained_mobs[0]:
            #            current_image.current_cell.contained_mobs.append(current_image.current_cell.contained_mobs.pop(0))
        elif roll_result <= self.current_max_crit_fail:
            self.die()
        self.global_manager.set('ongoing_religious_campaign', False)

    def start_public_relations_campaign(self):
        '''
        Description:
            Used when the player clicks on the start PR campaign button, displays a choice notification that allows the player to campaign or not. Choosing to campaign starts the campaign process and consumes the evangelist's
                movement points
        Input:
            None
        Output:
            None
        '''
        self.current_roll_modifier = 0
        self.current_min_success = self.default_min_success
        self.current_max_crit_fail = self.default_max_crit_fail
        self.current_min_crit_success = self.default_min_crit_success
        
        self.current_min_success -= self.current_roll_modifier #positive modifier reduces number required for succcess, reduces maximum that can be crit fail
        self.current_max_crit_fail -= self.current_roll_modifier
        if self.current_min_success > self.current_min_crit_success:
            self.current_min_crit_success = self.current_min_success #if 6 is a failure, should not be critical success. However, if 6 is a success, it will always be a critical success
        choice_info_dict = {'evangelist': self,'type': 'start public relations campaign'}
        self.global_manager.set('ongoing_public_relations_campaign', True)
        message = "Are you sure you want to start a public relations campaign? /n /nIf successful, your company's public opinion will increase by between 1 and 6 /n /n"
        message += "The campaign will cost " + str(self.global_manager.get('action_prices')['public_relations_campaign']) + " money. /n /n"
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
            
        notification_tools.display_choice_notification(message, ['start public relations campaign', 'stop public relations campaign'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager

    def public_relations_campaign(self):
        '''
        Description:
            Controls the PR campaign process, determining and displaying its result through a series of notifications
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

        price = self.global_manager.get('action_prices')['public_relations_campaign']
        self.global_manager.get('money_tracker').change(self.global_manager.get('action_prices')['public_relations_campaign'] * -1, 'public relations campaigns')
        actor_utility.double_action_price(self.global_manager, 'public_relations_campaign')
        text = ""
        text += "The evangelist campaigns to increase your company's public opinion with word of your company's benevolent goals and righteous deeds in Africa. /n /n"
        if not self.veteran:    
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required to succeed.", 'public_relations_campaign', self.global_manager, num_dice)
        else:
            text += ("The veteran evangelist can roll twice and pick the higher result. /n /n")
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required on at least 1 die to succeed.", 'public_relations_campaign', self.global_manager, num_dice)

        notification_tools.display_notification(text + "Rolling... ", 'roll', self.global_manager, num_dice)

        die_x = self.global_manager.get('notification_manager').notification_x - 140

        if self.veteran:
            results = self.controlling_minister.roll_to_list(6, self.current_min_success, self.current_max_crit_fail, price, 'public relations campaign', 2)
            first_roll_list = dice_utility.roll_to_list(6, "Public relations campaign roll", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, results[0])
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
            result = self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail, price, 'public relations campaign')
            roll_list = dice_utility.roll_to_list(6, "Public relations campaign roll", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, result)
            self.display_die((die_x, 440), roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)
                
            text += roll_list[1]
            roll_result = roll_list[0]

        notification_tools.display_notification(text + "Click to continue.", 'public_relations_campaign', self.global_manager, num_dice)
            
        text += "/n"
        public_relations_change = 0
        if roll_result >= self.current_min_success: #4+ required on D6 for exploration
            public_relations_change = random.randrange(1, 7)
            text += "Met with gullible and enthusiastic audiences, the evangelist successfully improves your company's public opinion by " + str(public_relations_change) + ". /n /n"
        else:
            text += "Whether by a lack of charisma, a reluctant audience, or a doomed cause, the evangelist fails to improve your company's public opinion. /n /n"
        if roll_result <= self.current_max_crit_fail:
            text += "The evangelist is deeply embarassed by this public failure and decides to abandon your company. /n /n" #actual 'death' occurs when religious campaign completes

        if (not self.veteran) and roll_result >= self.current_min_crit_success:
            self.just_promoted = True
            text += "With fiery word and true belief in his cause, the evangelist becomes a veteran and will be more successful in future ventures. /n /n"
        if roll_result >= 4:
            notification_tools.display_notification(text + "Click to remove this notification.", 'final_public_relations_campaign', self.global_manager)
        else:
            notification_tools.display_notification(text, 'default', self.global_manager)
        self.global_manager.set('public_relations_campaign_result', [self, roll_result, public_relations_change])

    def complete_public_relations_campaign(self):
        '''
        Description:
            Used when the player finishes rolling for a PR campaign, shows the campaign's results and making any changes caused by the result. If successful, increases public opinion by random amount, promotes evangelist to a veteran on
                critical success. Evangelist dies on critical failure
        Input:
            None
        Output:
            None
        '''
        roll_result = self.global_manager.get('public_relations_campaign_result')[1]
        if roll_result >= self.current_min_success: #if campaign succeeded
            self.global_manager.get('public_opinion_tracker').change(self.global_manager.get('public_relations_campaign_result')[2])
            if roll_result >= self.current_min_crit_success and not self.veteran:
                self.promote()
            self.select()
        elif roll_result <= self.current_max_crit_fail:
            self.die()
        self.global_manager.set('ongoing_public_relations_campaign', False)

class merchant(officer):
    '''
    Officer that can start advertising campaigns and merge with workers to form a caravan
    '''
    def __init__(self, from_save, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'grids': grid list value - grids in which this mob's images can appear
                'image': string value - File path to the image used by this object
                'name': string value - Required if from save, this mob's name
                'modes': string list value - Game modes during which this mob's images can appear
                'end_turn_destination': string or int tuple - Required if from save, 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'max_movement_points': int value - Required if from save, maximum number of movement points this mob can have
                'veteran': boolean value - Required if from save, whether this officer is a veteran
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['officer_type'] = 'merchant'
        super().__init__(from_save, input_dict, global_manager)
        self.current_roll_modifier = 0
        self.default_min_success = 5
        self.default_max_crit_fail = 1
        self.default_min_crit_success = 6

    def start_loan_search(self):
        '''
        Description:
            Used when the player clicks on the start loan search button, displays a choice notification that asks that allows the player to search or not. Starts the loan search process and consumes the merchant's movement points.
                Also shows a picture of the minister controlling the roll.
        Input:
            None
        Output:
            None
        '''
        self.current_roll_modifier = 0
        self.current_min_success = self.default_min_success
        self.current_max_crit_fail = self.default_max_crit_fail
        self.current_min_crit_success = self.default_min_crit_success
        
        self.current_min_success -= self.current_roll_modifier #positive modifier reduces number required for succcess, reduces maximum that can be crit fail
        self.current_max_crit_fail -= self.current_roll_modifier
        if self.current_min_success > self.current_min_crit_success:
            self.current_min_crit_success = self.current_min_success #if 6 is a failure, should not be critical success. However, if 6 is a success, it will always be a critical success
        choice_info_dict = {'merchant': self, 'type': 'start loan'}
        self.global_manager.set('ongoing_loan_search', True)

        minister_icon_coordinates = (440, self.global_manager.get('notification_manager').notification_x - 140) #show minister in start loan search notification, remove on start/stop loan search
        minister_position_icon = images.dice_roll_minister_image(minister_icon_coordinates, scaling.scale_width(100, self.global_manager), scaling.scale_height(100, self.global_manager), self.modes, self.controlling_minister,
            'position', self.global_manager)
        minister_portrait_icon = images.dice_roll_minister_image(minister_icon_coordinates, scaling.scale_width(100, self.global_manager), scaling.scale_height(100, self.global_manager), self.modes, self.controlling_minister,
            'portrait', self.global_manager)
        
        message = "Are you sure you want to search for a 100 money loan? A loan will always be available, but the merchant's success will determine the interest rate found. /n /n"
        message += "The search will cost " + str(self.global_manager.get('action_prices')['loan_search']) + " money. /n /n "
        notification_tools.display_choice_notification(message, ['start loan search', 'stop loan search'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager

    def loan_search(self):
        '''
        Description:
            Controls the process of searching for a loan. Unlike most actions, this action uses hidden dice rolls - starting the search immediately shows the resulting interest cost of the loan found and the controlling minister's
                position and portrait. Allows the player to choose whether to accept the loan after seeing the interest cost.
        Input:
            None
        Output:
            None
        '''
        just_promoted = False
        self.set_movement_points(0)

        num_dice = 0 #don't show dice roll for loan

        self.global_manager.get('money_tracker').change(self.global_manager.get('action_prices')['loan_search'] * -1, 'loan searches')
        actor_utility.double_action_price(self.global_manager, 'loan_search')
        
        principal = 100
        initial_interest = 11
        interest = initial_interest
        found_loan = False
        while not found_loan: #doesn't account for corruption yet, fix this
            if self.veteran: 
                roll = max(random.randrange(1, 7) + self.controlling_minister.get_roll_modifier(), random.randrange(1, 7) + self.controlling_minister.get_roll_modifier())
            else:
                roll = random.randrange(1, 7) + self.controlling_minister.get_roll_modifier()
            if roll >= 5: #increase interest on 1-4, stop on 5-6
                found_loan = True
            else:
                interest += 1
        corrupt = False
        if self.controlling_minister.check_corruption():
            interest += 2 #increase interest by 20% if corrupt
            corrupt = True
            #self.controlling_minister.steal_money(20, 'loan interest') #money stolen once loan actually accepted
            
        if roll == 6 and interest == initial_interest and not self.veteran: #if rolled 6 on first try, promote
            just_promoted = True
                    
        if just_promoted:
            notification_tools.display_notification('The merchant negotiated the loan offer well enough to become a veteran.', 'default', self.global_manager, num_dice)
            self.promote()
            
        choice_info_dict = {}
        choice_info_dict['principal'] = principal
        choice_info_dict['interest'] = interest
        choice_info_dict['corrupt'] = corrupt

        total_paid = interest * 10 #12 interest -> 120 paid
        interest_percent = (interest - 10) * 10 #12 interest -> 20%
        message = ""
        message += 'Loan offer: /n /n'
        message += 'The company will be provided an immediate sum of ' + str(principal) + ' money, which it may spend as it sees fit. /n'
        message += 'In return, the company will be obligated to pay back ' + str(interest) + ' money per turn for 10 turns, for a total of ' + str(total_paid) + ' money. /n /n'
        message += "Do you accept this exchange? /n"
        notification_tools.display_choice_notification(message, ['accept loan offer', 'decline loan offer'], choice_info_dict, self.global_manager)

    def start_advertising_campaign(self, target_commodity):
        '''
        Description:
            Used when the player clicks on the start advertising campaign button and then clicks a commodity button, displays a choice notification that allows the player to campaign or not. Choosing to campaign starts the campaign
                process and consumes the merchant's movement points
        Input:
            string target_commodity: Name of commodity that advertising campaign is targeting
        Output:
            None
        '''
        self.current_roll_modifier = 0
        self.current_min_success = self.default_min_success
        self.current_max_crit_fail = self.default_max_crit_fail
        self.current_min_crit_success = self.default_min_crit_success
        
        self.current_min_success -= self.current_roll_modifier #positive modifier reduces number required for succcess, reduces maximum that can be crit fail
        self.current_max_crit_fail -= self.current_roll_modifier
        if self.current_min_success > self.current_min_crit_success:
            self.current_min_crit_success = self.current_min_success #if 6 is a failure, should not be critical success. However, if 6 is a success, it will always be a critical success
        choice_info_dict = {'merchant': self, 'type': 'start advertising campaign', 'commodity': target_commodity}
        self.global_manager.set('ongoing_advertising_campaign', True)
        message = "Are you sure you want to start an advertising campaign for " + target_commodity + "? If successful, the price of " + target_commodity + " will increase, decreasing the price of another random commodity. /n /n"
        message += "The campaign will cost " + str(self.global_manager.get('action_prices')['advertising_campaign']) + " money. /n /n "
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

        self.current_advertised_commodity = target_commodity
        self.current_unadvertised_commodity = random.choice(self.global_manager.get('commodity_types'))
        while (self.current_unadvertised_commodity == 'consumer goods') or (self.current_unadvertised_commodity == self.current_advertised_commodity) or (self.global_manager.get('commodity_prices')[self.current_unadvertised_commodity] == 1):
            self.current_unadvertised_commodity = random.choice(self.global_manager.get('commodity_types'))
        notification_tools.display_choice_notification(message, ['start advertising campaign', 'stop advertising campaign'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager

    def advertising_campaign(self): #called when start commodity icon clicked
        '''
        Description:
            Controls the advertising campaign process, determining and displaying its result through a series of notifications
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

        price = self.global_manager.get('action_prices')['advertising_campaign']
        self.global_manager.get('money_tracker').change(self.global_manager.get('action_prices')['advertising_campaign'] * -1, 'advertising')
        actor_utility.double_action_price(self.global_manager, 'advertising_campaign')
        
        text = ""
        text += "The merchant attempts to increase public demand for " + self.current_advertised_commodity + ". /n /n"
        if not self.veteran:    
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required to succeed.", 'advertising_campaign', self.global_manager, num_dice)
        else:
            text += ("The veteran merchant can roll twice and pick the higher result. /n /n")
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required on at least 1 die to succeed.", 'advertising_campaign', self.global_manager, num_dice)

        notification_tools.display_notification(text + "Rolling... ", 'roll', self.global_manager, num_dice)

        die_x = self.global_manager.get('notification_manager').notification_x - 140

        if self.veteran:
            results = self.controlling_minister.roll_to_list(6, self.current_min_success, self.current_max_crit_fail, price, 'advertising campaign', 2)
            first_roll_list = dice_utility.roll_to_list(6, "Advertising campaign roll", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, results[0])
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
            result = self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail, price, 'advertising campaign')
            roll_list = dice_utility.roll_to_list(6, "Advertising campaign roll", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, result)
            self.display_die((die_x, 440), roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)
                
            text += roll_list[1]
            roll_result = roll_list[0]

        notification_tools.display_notification(text + "Click to continue.", 'advertising_campaign', self.global_manager, num_dice)
            
        text += "/n"
        if roll_result >= self.current_min_success: #4+ required on D6 for exploration
            increase = 1
            if roll_result >= self.current_min_crit_success:
                increase += 1
            advertised_original_price = self.global_manager.get('commodity_prices')[self.current_advertised_commodity]
            unadvertised_original_price = self.global_manager.get('commodity_prices')[self.current_unadvertised_commodity]
            text += "The merchant successfully advertised for " + self.current_advertised_commodity + ", increasing its price from " + str(advertised_original_price) + " to "
            unadvertised_final_price = unadvertised_original_price - increase
            if unadvertised_final_price < 1:
                unadvertised_final_price = 1
            text += str(advertised_original_price + increase) + ". The price of " + self.current_unadvertised_commodity + " decreased from " + str(unadvertised_original_price) + " to " + str(unadvertised_final_price) + ". /n /n"
        else:
            text += "The merchant failed to increase the popularity of " + self.current_advertised_commodity + ". /n /n"
        if roll_result <= self.current_max_crit_fail:
            text += "Embarassed by this utter failure, the merchant quits your company. /n /n" 

        if roll_result >= self.current_min_crit_success:
            if not self.veteran:
                self.just_promoted = True
            text += "The advertising campaign was so popular that the value of " + self.current_advertised_commodity + " increased by 2 instead of 1. /n /n"
        if roll_result >= self.current_min_success:
            notification_tools.display_notification(text + "Click to remove this notification.", 'final_advertising_campaign', self.global_manager)
        else:
            notification_tools.display_notification(text, 'default', self.global_manager)
        self.global_manager.set('advertising_campaign_result', [self, roll_result])

    def complete_advertising_campaign(self):
        '''
        Description:
            Used when the player finishes rolling for an advertising, shows the campaign's results and making any changes caused by the result. If successful, increases target commodity price and decreases other commodity price,
                promotes merchant to veteran and increasing more on critical success. If not successful, the evangelist consumes its movement points and dies on critical failure
        Input:
            None
        Output:
            None
        '''
        roll_result = self.global_manager.get('advertising_campaign_result')[1]
        if roll_result >= self.current_min_success: #if campaign succeeded
            #change prices
            increase = 1
            if roll_result >= self.current_min_crit_success:
                increase += 1
            market_tools.change_price(self.current_advertised_commodity, increase, self.global_manager)
            market_tools.change_price(self.current_unadvertised_commodity, -1 * increase, self.global_manager)
            if roll_result >= self.current_min_crit_success and not self.veteran:
                self.promote()
            self.select()
        elif roll_result <= self.current_max_crit_fail:
            self.die()
        self.global_manager.set('ongoing_advertising_campaign', False)
