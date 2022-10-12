#Contains functionality for objects that manage notifications, variables, files, etc.

import random
import pygame

from . import csv_tools
from . import notifications
from . import choice_notifications
from . import action_notifications
from . import scaling
from . import text_tools

class global_manager_template():
    '''
    Object designed to manage a dictionary of shared variables and be passed between functions and objects as a simpler alternative to passing each variable or object separately
    '''
    def __init__(self):
        '''
        Description:
            Initializes this object
        Input:
            None
        Output:
            None
        '''
        self.global_dict = {}
        
    def get(self, name):
        '''
        Description:
            Returns the value in this object's dictionary corresponding to the inputted key
        Input:
            string name: Name of a key in this object's dictionary
        Output:
            any type: The value corresponding to the inputted key's entry in this object's dictionary
        '''
        return(self.global_dict[name])
    
    def set(self, name, value):
        '''
        Description:
            Sets or initializes the inputted value for the inputted key in this object's dictionary
        Input:
            string name: Name of the key in this object's dictionary to initialize/modify
            any type value: Value corresponding to the new/modified key
        Output:
            None
        '''
        self.global_dict[name] = value

class input_manager_template():
    '''
    Object designed to manage the passing of typed input from the text box to different parts of the program
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
        self.previous_input = ''
        self.taking_input = False
        self.old_taking_input = self.taking_input
        self.stored_input = ''
        self.send_input_to = ''
        
    def check_for_input(self):
        '''
        Description:
            Returns true if input was just being taken and is no longer being taken, showing that there is input ready. Otherwise, returns False.
        Input:
            None
        Output:
            boolean: True if input was just being taken and is no longer being taken, showing that there is input ready. Otherwise, returns False.
        '''
        if self.old_taking_input == True and self.taking_input == False: 
            return(True)
        else:
            return(False)
        
    def start_receiving_input(self, solicitant, message):
        '''
        Description:
            Displays the prompt for the user to enter input and prepares to receive input and send it to the part of the program requesting input
        Input:
            string solicitant: Represents the part of the program to send input to
            string message: Prompt given to the player to enter input
        Output:
            None
        '''
        text_tools.print_to_screen(message, self.global_manager)
        self.send_input_to = solicitant
        self.taking_input = True
        
    def update_input(self):
        '''
        Description:
            Updates whether this object is currently taking input
        Input:
            None
        Output:
            None
        '''
        self.old_taking_input = self.taking_input
        
    def receive_input(self, received_input):
        '''
        Description:
            Sends the inputted string to the part of the program that initially requested input
        Input:
            String received_input: Input entered by the user into the text box
        Output:
            None
        '''
        if self.send_input_to == 'do something':
            if received_input == 'done':
                self.global_manager.set('crashed', True)
            else:
                text_tools.print_to_screen("I didn't understand that.")

class flavor_text_manager_template():
    '''
    Object that reads flavor text from .csv files and distributes it to other parts of the program when requested
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
        self.subject_dict = {}
        
        self.explorer_flavor_text_list = []
        current_flavor_text = csv_tools.read_csv('text/flavor_explorer.csv')
        for line in current_flavor_text: #each line is a list
            self.explorer_flavor_text_list.append(line[0])
        self.subject_dict['explorer'] = self.explorer_flavor_text_list
        
        self.minister_first_names_flavor_text_list = []
        current_flavor_text = csv_tools.read_csv('text/flavor_minister_first_names.csv')
        for line in current_flavor_text:
            self.minister_first_names_flavor_text_list.append(line[0])
        self.subject_dict['minister_first_names'] = self.minister_first_names_flavor_text_list

        self.minister_last_names_flavor_text_list = []
        current_flavor_text = csv_tools.read_csv('text/flavor_minister_last_names.csv')
        for line in current_flavor_text:
            self.minister_last_names_flavor_text_list.append(line[0])
        self.subject_dict['minister_last_names'] = self.minister_last_names_flavor_text_list
                
    def generate_flavor_text(self, subject):
        '''
        Description:
            Returns a random flavor text statement based on the inputted string
        Input:
            string subject: Represents the type of flavor text to return
        Output:
            string: Random flavor text statement of the inputted subject
        '''
        return(random.choice(self.subject_dict[subject]))

    def generate_minister_name(self, background):
        '''
        Description:
            Generates and returns a random combination of minister first and last names
        Input:
            None
        Output:
            string: Returns a random combination of minister first and last names
        '''
        first_name = self.generate_flavor_text('minister_first_names')
        titles = ['Duke', 'Marquess', 'Earl', 'Viscount', 'Baron', 'Sir', 'Prince', 'Lord']
        if background in ['royal heir', 'aristocrat']:
            while not first_name in titles:
                first_name = self.generate_flavor_text('minister_first_names')
        else:
            while first_name in titles:
                first_name = self.generate_flavor_text('minister_first_names')
        return(first_name + ' ' + self.generate_flavor_text('minister_last_names'))

class value_tracker():
    '''
    Object that controls the value of a certain variable
    '''
    def __init__(self, value_key, initial_value, min_value, max_value, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            string value_key: Key used to access this tracker's variable in the global manager
            any type initial_value: Value that this tracker's variable is set to when initialized
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.global_manager = global_manager
        self.global_manager.set(value_key, initial_value)
        self.value_label = 'none'
        self.value_key = value_key
        self.min_value = min_value
        self.max_value = max_value

    def get(self):
        '''
        Description:
            Returns the value of this tracker's variable
        Input:
            None
        Output:
            any type: Value of this tracker's variable
        '''
        return(self.global_manager.get(self.value_key))

    def change(self, value_change):
        '''
        Description:
            Changes the value of this tracker's variable by the inputted amount. Only works if this tracker's variable is a type that can be added to, like int, float, or string
        Input:
            various types value_change: Amount that this tracker's variable is changed. Must be the same type as this tracker's variable
        Output:
            None
        '''
        #self.global_manager.set(self.value_key, self.get() + value_change)
        self.set(self.get() + value_change)
        if not self.value_label == 'none':
            self.value_label.update_label(self.get())
    
    def set(self, new_value):
        '''
        Description:
            Sets the value of this tracker's variable to the inputted amount
        Input:
            any type value_change: Value that this tracker's variable is set to
        Output:
            None
        '''
        self.global_manager.set(self.value_key, new_value)
        if not self.min_value == 'none':
            if self.get() < self.min_value:
                self.global_manager.set(self.value_key, self.min_value)
        if not self.max_value == 'none':
            if self.get() > self.max_value:
                self.global_manager.set(self.value_key, self.max_value)
        if not self.value_label == 'none':
            self.value_label.update_label(self.get())

class money_tracker(value_tracker):
    '''
    Value tracker that tracks money and causes the game to be lost when money runs out
    '''
    def __init__(self, initial_value, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            any type initial_value: Value that the money variable is set to when initialized
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.transaction_history = {}
        self.transaction_types = global_manager.get('transaction_types')
        self.reset_transaction_history()
        super().__init__('money', initial_value, 'none', 'none', global_manager)

    def reset_transaction_history(self):
        '''
        Description:
            Resets the stored transactions from the last turn, allowing new transactions to be recorded for the current turn's financial report
        Input:
            None
        Output:
            None
        '''
        self.transaction_history = {}
        for current_transaction_type in self.transaction_types:
            self.transaction_history[current_transaction_type] = 0

    def change(self, value_change, change_type = 'misc.'):
        '''
        Description:
            Changes the money variable by the inputted amount
        Input:
            int value_change: Amount that the money variable is changed
        Output:
            None
        '''
        if change_type == 'misc.':
            if value_change > 0:
                change_type = 'misc. revenue'
            else:
                change_type = 'misc. expenses'
        self.transaction_history[change_type] += value_change
        if not value_change == 0:
            if abs(value_change) < 15:
                self.global_manager.get('sound_manager').play_sound('coins 1')
            else:
                self.global_manager.get('sound_manager').play_sound('coins 2')
        super().change(value_change)

    def set(self, new_value):
        '''
        Description:
            Sets the money variable to the inputted amount
        Input:
            int value_change: Value that the money variable is set to
        Output:
            None
        '''
        super().set(round(new_value, 2))

    def prepare_financial_report(self):
        '''
        Description:
            Creates and formats the text for a financial report based on the last turn's transactions
        Input:
            None
        Output:
            string: Formatted financial report text with /n being a new line
        '''
        notification_text = "Financial report: /n /n"
        notification_text += "Revenue: /n "
        total_revenue = 0
        for transaction_type in self.transaction_types:
            if self.transaction_history[transaction_type] > 0:
                if transaction_type == 'misc. revenue':
                    notification_text += '  Misc: ' + str(self.transaction_history[transaction_type]) + ' /n'
                else:
                    notification_text += '  ' + transaction_type.capitalize() + ': ' + str(self.transaction_history[transaction_type]) + ' /n'
                total_revenue += self.transaction_history[transaction_type]
        if total_revenue == 0:
            notification_text += '  None /n'
        
        notification_text += "/nExpenses: /n"
        total_expenses = 0
        for transaction_type in self.transaction_types:
            if self.transaction_history[transaction_type] < 0:
                if transaction_type == 'misc. expenses':
                    notification_text += '  Misc: ' + str(self.transaction_history[transaction_type]) + ' /n'
                else:
                    notification_text += '  ' + transaction_type.capitalize() + ': ' + str(self.transaction_history[transaction_type]) + ' /n'
                total_expenses += self.transaction_history[transaction_type]
        if total_expenses == 0:
            notification_text += '  None /n'
        notification_text += ' /n'
        notification_text += 'Total revenue: ' + str(round(total_revenue, 2)) + ' /n'
        notification_text += 'Total expenses: ' + str(round(total_expenses, 2)) + ' /n'
        notification_text += 'Total profit: ' + str(round(total_revenue + total_expenses, 2)) + ' /n'
        return(notification_text)
                    
class notification_manager_template():
    '''
    Object that controls the displaying of notifications
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
        self.notification_queue = []
        self.notification_type_queue = []
        self.notification_dice_queue = []
        self.choice_notification_choices_queue = []
        self.choice_notification_info_dict_queue = []
        self.minister_message_queue = []
        self.global_manager = global_manager
        self.update_notification_layout()
        self.notification_modes = ['strategic', 'europe', 'ministers', 'trial']

    def update_notification_layout(self, notification_height = 0):
        '''
        Description:
            Changes where notifications are displayed depending on the current game mode to avoid blocking relevant information. Also changes the height of the notification based on how much text it contains
        Input:
            int notification_height = 0: Height in pixels of the notification text. If the notification text height is greater than the default notification height, the notification will scale its height to the text
        Output:
            None
        '''
        self.notification_width = 500
        self.notification_height = 300#500#600
        self.notification_y = 336#236#186
        height_difference = notification_height - self.notification_height
        if height_difference > 0: #if notification height greater than default notification height
            self.notification_y -= (height_difference / 2) #lower by half of height change
            self.notification_height += height_difference #increase height by height change
            #should change top and bottom locations while keeping same center
        if self.global_manager.get('current_game_mode') in ['strategic', 'none']: #move notifications out of way of minimap on strategic mode or during setup
            self.notification_x = self.global_manager.get('minimap_grid_origin_x') - (self.notification_width + 40)
        else: #show notifications in center on europe mode
            self.notification_x = 610

    def get_notification_height(self, notification_text):
        '''
        Description:
            Returns the height in pixels of the inputted text if it were put in a notification
        Input:
            string notification_text: Text that will appear on the notification with lines separated by /n
        Output:
            int: height in pixels of the inputted text if it were put in a notification
        '''
        new_message = []
        next_line = ""
        next_word = ""
        font_size = 25
        font_name = self.global_manager.get('font_name')
        font = pygame.font.SysFont(font_name, font_size)
        for index in range(len(notification_text)):
            if not ((not (index + 2) > len(notification_text) and notification_text[index] + notification_text[index + 1]) == "/n"): #don't add if /n
                if not (index > 0 and notification_text[index - 1] + notification_text[index] == "/n"): #if on n after /, skip
                    next_word += notification_text[index]
            if notification_text[index] == " ":
                if text_tools.message_width(next_line + next_word, font_size, font_name) > self.notification_width:
                    new_message.append(next_line)
                    next_line = ""
                next_line += next_word
                next_word = ""
            elif (not (index + 2) > len(notification_text) and notification_text[index] + notification_text[index + 1]) == "/n": #don't check for /n if at last index
                new_message.append(next_line)
                next_line = ""
                next_line += next_word
                next_word = ""
        if text_tools.message_width(next_line + next_word, font_size, font_name) > self.notification_width:
            new_message.append(next_line)
            next_line = ""
        next_line += next_word
        new_message.append(next_line)
        new_message.append("Click to remove this notification.")
        return(scaling.scale_height(len(new_message) * font_size, self.global_manager))#self.message = new_message
            
    def notification_to_front(self, message):
        '''
        Description:
            Displays a new notification with text matching the inputted string and a type based on what is in the front of this object's notification type queue
        Input:
            string message: The text to put in the displayed notification
        Output:
            None
        '''
        self.update_notification_layout(self.get_notification_height(message))
        notification_type = self.notification_type_queue.pop(0)
        notification_dice = self.notification_dice_queue.pop(0) #number of dice of selected mob to show when notification is visible
        if notification_type == 'roll':
            new_notification = action_notifications.dice_rolling_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width, self.global_manager),
                scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, notification_dice, self.global_manager)
            
            for current_die in self.global_manager.get('dice_list'):
                current_die.start_rolling()

        elif notification_type in ['stop_trade', 'stop_trade_attacked', 'trade', 'trade_promotion', 'final_trade', 'successful_commodity_trade', 'failed_commodity_trade']:
            is_last = False
            commodity_trade = False
            commodity_trade_type = notification_type #for successful/failed_commodity_trade
            stops_trade = False
            dies = False
            if notification_type == 'stop_trade':
                stops_trade = True
            elif notification_type == 'stop_trade_attacked':
                stops_trade = True
                dies = True
            elif notification_type == 'final_trade':
                is_last = True
            elif notification_type in ['successful_commodity_trade', 'failed_commodity_trade']:
                commodity_trade = True
            elif notification_type == 'trade_promotion':
                self.global_manager.get('trade_result')[0].promote() #promotes caravan
            trade_info_dict = {'is_last': is_last, 'commodity_trade': commodity_trade, 'commodity_trade_type': notification_type, 'stops_trade': stops_trade, 'dies': dies}
            new_notification = action_notifications.trade_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width, self.global_manager),
                scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, trade_info_dict, notification_dice, self.global_manager)
                
        elif notification_type == 'exploration':
            new_notification = action_notifications.exploration_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width, self.global_manager),
                scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, False, notification_dice, self.global_manager)

        elif notification_type == 'final_exploration':
            new_notification = action_notifications.exploration_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width, self.global_manager),
                scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, True, notification_dice, self.global_manager)

        elif notification_type == 'off_tile_exploration':
            new_notification = action_notifications.off_tile_exploration_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager),
                scaling.scale_width(self.notification_width, self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message,
                notification_dice, self.global_manager)

        elif notification_type == 'religious_campaign':
            new_notification = action_notifications.religious_campaign_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, False, notification_dice, self.global_manager)
            
        elif notification_type == 'final_religious_campaign':
            new_notification = action_notifications.religious_campaign_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, True, notification_dice, self.global_manager)

        elif notification_type == 'public_relations_campaign':
            new_notification = action_notifications.public_relations_campaign_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, False, notification_dice, self.global_manager)
            
        elif notification_type == 'final_public_relations_campaign':
            new_notification = action_notifications.public_relations_campaign_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, True, notification_dice, self.global_manager)

        elif notification_type == 'advertising_campaign':
            new_notification = action_notifications.advertising_campaign_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, False, notification_dice, self.global_manager)
            
        elif notification_type == 'final_advertising_campaign':
            new_notification = action_notifications.advertising_campaign_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, True, notification_dice, self.global_manager)

        elif notification_type == 'conversion':
            new_notification = action_notifications.conversion_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, False, notification_dice, self.global_manager)
            
        elif notification_type == 'final_conversion':
            new_notification = action_notifications.conversion_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, True, notification_dice, self.global_manager)

        elif notification_type == 'slave_capture':
            new_notification = action_notifications.capture_slaves_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, False, notification_dice, self.global_manager)
            
        elif notification_type == 'final_slave_capture':
            new_notification = action_notifications.capture_slaves_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, True, notification_dice, self.global_manager)

        elif notification_type == 'construction':
            new_notification = action_notifications.construction_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, False, notification_dice, self.global_manager)
            
        elif notification_type == 'final_construction':
            new_notification = action_notifications.construction_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), ['strategic', 'europe'], 'misc/default_notification.png', message, True, notification_dice, self.global_manager)

        elif notification_type == 'combat':
            new_notification = action_notifications.combat_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, False, notification_dice, self.global_manager)
            
        elif notification_type == 'final_combat':
            new_notification = action_notifications.combat_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, True, notification_dice, self.global_manager)

        elif notification_type == 'trial':
            new_notification = action_notifications.trial_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, True, notification_dice, self.global_manager)
            
        elif notification_type == 'choice':
            choice_notification_choices = self.choice_notification_choices_queue.pop(0)
            choice_notification_info_dict = self.choice_notification_info_dict_queue.pop(0)
            new_notification = choice_notifications.choice_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width, self.global_manager),
                scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, choice_notification_choices, choice_notification_info_dict, notification_dice,
                self.global_manager)

        elif notification_type == 'zoom':
            target = self.choice_notification_choices_queue.pop(0) #repurposing communication method used for choice notifications to tell notification which target
            self.choice_notification_info_dict_queue.pop(0)
            new_notification = notifications.zoom_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width, self.global_manager),
                scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, target, self.global_manager)     
            
        elif notification_type == 'minister':
            new_notification = notifications.minister_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width, self.global_manager),
                scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, self.global_manager, self.minister_message_queue.pop(0))

        else:
            new_notification = notifications.notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width, self.global_manager),
                scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, self.global_manager)
                #coordinates, ideal_width, minimum_height, showing, modes, image, message

class sound_manager_template():
    '''
    Object that controls sounds
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

    def play_sound(self, file_name):
        '''
        Description:
            Plays the sound effect from the inputted file
        Input:
            string file_name: Name of .wav file to play sound of
        Output:
            None
        '''
        current_sound = pygame.mixer.Sound('sounds/' + file_name + '.wav')
        current_sound.play()

    def play_music(self, file_name):
        '''
        Description:
            Starts repeating the music from the inputted file, replacing any current music
        Input:
            string file_name: Name of .wav file to play music of
        Output:
            None
        '''
        pygame.mixer.music.load('sounds/' + file_name + '.wav')
        pygame.mixer.music.play(999)
