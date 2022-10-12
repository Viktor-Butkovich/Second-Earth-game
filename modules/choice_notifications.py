#Contains functionality for choice notifications

import pygame
from .buttons import button
from .notifications import notification
from . import text_tools
from . import scaling
from . import market_tools
from . import utility

class choice_notification(notification):
    '''
    Notification that presents 2 choices and is removed when one is chosen rather than when the notification itself is clicked, causing a different outcome depending on the chosen option
    '''
    def __init__(self, coordinates, ideal_width, minimum_height, modes, image, message, button_types, choice_info_dict, notification_dice, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this notification
            int ideal_width: Pixel width that this notification will try to retain. Each time a word is added to the notification, if the word extends past the ideal width, the next line will be started
            int minimum_height: Minimum pixel height of this notification. Its height will increase if the contained text would extend past the bottom of the notification
            string list modes: Game modes during which this notification can appear
            string image: File path to the image used by this object
            string message: Text that will appear on the notification with lines separated by /n
            string list button_types: List of strings that correspond to the button types of this notification's choice buttons, like ['end turn', 'none'] for an end turn button and a do nothing button
            dictionary choice_info_dict: String keys corresponding to various values used by this notification's choice buttons when clicked
            int notification_dice: Number of dice attached to this notification, allowing the correct ones to be shown during the notification when multiple notifications are queued
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        button_height = scaling.scale_height(50, global_manager)
        super().__init__(coordinates, ideal_width, minimum_height, modes, image, message, global_manager)
        self.choice_buttons = []
        self.choice_info_dict = choice_info_dict
        for current_button_type_index in range(len(button_types)):
            button_type = button_types[current_button_type_index]
            if button_type == 'recruitment':
                new_choice_button = recruitment_choice_button((self.x + (current_button_type_index * round(self.width / len(button_types))), self.y - button_height), round(self.width / len(button_types)), button_height,
                                              button_type, modes, 'misc/paper_label.png', self, global_manager)
            else:
                new_choice_button = choice_button((self.x + (current_button_type_index * round(self.width / len(button_types))), self.y - button_height), round(self.width / len(button_types)), button_height,
                                              button_type, modes, 'misc/paper_label.png', self, global_manager)
            self.choice_buttons.append(new_choice_button)
        self.global_manager.set('making_choice', True)

    def format_message(self):
        '''
        Description:
            Converts this notification's string message to a list of strings, with each string representing a line of text. Each line of text ends when its width exceeds the ideal_width or when a '/n' is encountered in the text. Does
                not add a prompt to close the notification
        Input:
            none
        Output:
            None
        '''
        super().format_message()
        self.message.pop(-1)

    def on_click(self):
        '''
        Description:
            Controls this notification's behavior when clicked. Choice notifications do nothing when clicked, instead acting when their choice buttons are clicked
        Input:
            None
        Output:
            None
        '''
        nothing = 0 #does not remove self when clicked

    def update_tooltip(self):
        '''
        Description:
            Sets this notification's tooltip to what it should be. Choice notifications prompt the user to click on one of its choice buttons to close it
        Input:
            None
        Output:
            None
        '''
        self.set_tooltip(['Choose an option to close this notification'])

    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. When a notification is removed, the next notification is shown, if there is one. Choice notifications are removed
                when one of their choice buttons is clicked
        Input:
            None
        Output:
            None
        '''
        self.global_manager.set('making_choice', False)
        super().remove()
        for current_choice_button in self.choice_buttons:
            current_choice_button.remove()

class choice_button(button):
    '''
    Button with no keybind that is attached to a choice notification and removes its notification when clicked
    '''
    def __init__(self, coordinates, width, height, button_type, modes, image_id, notification, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string button_type: Determines the function of this button, like 'end turn'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            choice_notification notification: notification to which this choice button is attached
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.notification = notification
        if button_type == 'recruitment':
            self.recruitment_type = self.notification.choice_info_dict['recruitment_type']
            if self.recruitment_type in ['steamship', 'slave workers']:
                self.message = 'Purchase'
                self.verb = 'purchase'
            else:
                self.message = 'Hire'
                self.verb = 'hire'
            self.cost = self.notification.choice_info_dict['cost']
            self.mob_image_id = self.notification.choice_info_dict['mob_image_id']
            
        elif button_type == 'exploration':
            self.message = 'Explore'
            self.cost = self.notification.choice_info_dict['cost']
            self.expedition = self.notification.choice_info_dict['expedition']
            self.x_change = self.notification.choice_info_dict['x_change']
            self.y_change = self.notification.choice_info_dict['y_change']

        elif button_type == 'attack':
            self.message = 'Attack'
            self.cost = self.notification.choice_info_dict['cost']
            self.battalion = self.notification.choice_info_dict['battalion']
            self.x_change = self.notification.choice_info_dict['x_change']
            self.y_change = self.notification.choice_info_dict['y_change']
            
        elif button_type in ['start religious campaign', 'start public relations campaign', 'start advertising campaign']:
            self.message = 'Start campaign'
            if button_type == 'start advertising campaign':
                self.commodity = self.notification.choice_info_dict['commodity']

        elif button_type == 'start loan search':
            self.message = 'Find loan'

        elif button_type == 'start converting':
            self.message = 'Convert'

        elif button_type == 'start capture slaves':
            self.message = 'Capture slaves'
            
        elif button_type in ['stop religious campaign', 'stop public relations campaign', 'stop advertising campaign']:
            self.message = 'Stop campaign'

        elif button_type == 'stop loan search':
            self.message = 'Stop search'

        elif button_type == 'accept loan offer':
            self.message = 'Accept'

        elif button_type == 'decline loan offer':
            self.message = 'Decline'
            
        elif button_type in ['none', 'stop exploration', 'stop attack', 'stop capture slaves']:
            self.message = 'Do nothing'

        elif button_type == 'confirm main menu':
            self.message = 'Main menu'

        elif button_type == 'confirm remove minister':
            self.message = 'Confirm'

        elif button_type == 'quit':
            self.message = 'Exit game'
    
        else:
            self.message = button_type.capitalize() #stop trading -> Stop trading
            
        super().__init__(coordinates, width, height, 'blue', button_type, 'none', modes, image_id, global_manager)
        self.font_size = scaling.scale_width(25, global_manager)
        self.font_name = self.global_manager.get('font_name')#"Times New Roman"
        self.font = pygame.font.SysFont(self.font_name, self.font_size)
        self.in_notification = True

    def on_click(self):
        '''
        Description:
            Controls this button's behavior when clicked. Choice buttons remove their notifications when clicked, along with the normal behaviors associated with their button_type
        Input:
            None
        Output:
            None
        '''
        super().on_click()
        if self.can_show(): #copying conditions of superclass on_click to make sure that notification is only removed when effect of click is done
            self.notification.remove()

    def draw(self):
        '''
        Description:
            Draws this button below its choice notification and draws a description of what it does on top of it
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.image.draw()
            self.global_manager.get('game_display').blit(text_tools.text(self.message, self.font, self.global_manager), (self.x + scaling.scale_width(10, self.global_manager), self.global_manager.get('display_height') -
                (self.y + self.height)))

    def update_tooltip(self):
        '''
        Description:
            Sets this image's tooltip to what it should be, depending on its button_type
        Input:
            None
        Output:
            None
        '''
        if self.button_type == 'recruitment':
            if self.recruitment_type in ['African worker village', 'African worker slums', 'African worker labor broker']:
                self.set_tooltip([utility.capitalize(self.verb) + ' an African worker for ' + str(self.cost) + ' money'])
            else:
                self.set_tooltip([utility.capitalize(self.verb) + ' a ' + self.recruitment_type + ' for ' + str(self.cost) + ' money'])

        elif self.button_type == 'end turn':
            self.set_tooltip(['End the current turn'])
            
        elif self.button_type == 'exploration':
            self.set_tooltip(['Attempt an exploration for ' + str(self.cost) + ' money'])

        elif self.button_type == 'attack':
            self.set_tooltip(['Supply an attack for ' + str(self.cost) + ' money'])
            
        elif self.button_type == 'trade':
            self.set_tooltip(['Attempt to trade by giving consumer goods'])

        elif self.button_type == 'start trading':
            self.set_tooltip(['Start trading, allowing consumer goods to be sold for commodities if the villagers are willing'])

        elif self.button_type == 'start religious campaign':
            self.set_tooltip(['Start a religious campaign, possibly convincing church volunteers to join you'])

        elif self.button_type == 'start public relations campaign':
            self.set_tooltip(["Start a public relations campaign, possibly improving your company's public opinion"])

        elif self.button_type == 'start advertising campaign':
            self.set_tooltip(['Starts an advertising campaign for ' + self.commodity])

        elif self.button_type == 'start loan search':
            self.set_tooltip(['Starts a search for a low-interest loan offer'])

        elif self.button_type == 'start converting':
            self.set_tooltip(['Start converting natives, possibly reducing their aggressiveness'])

        elif self.button_type == 'start capture slaves':
            self.set_tooltip(['Start attempting to capture native villagers as slaves'])

        elif self.button_type == 'accept loan offer':
            self.set_tooltip(['Accepts the loan offer'])

        elif self.button_type == 'reject loan offer':
            self.set_tooltip(['Rejects the loan offer'])

        elif self.button_type == 'confirm main menu':
            self.set_tooltip(['Exits to the main menu without saving'])

        elif self.button_type == 'quit':
            self.set_tooltip(['Exits the game without saving'])

        elif self.button_type == 'none':
            self.set_tooltip(['Do nothing'])
            
        else:
            self.set_tooltip([self.button_type.capitalize()]) #stop trading -> ['Stop trading']

class recruitment_choice_button(choice_button):
    '''
    choice_button that recruits a unit when clicked
    '''
    def __init__(self, coordinates, width, height, button_type, modes, image_id, notification, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string button_type: Determines the function of this button, like 'end turn'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            choice_notification notification: notification to which this choice button is attached
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, width, height, button_type, modes, image_id, notification, global_manager)

    def on_click(self):
        '''
        Description:
            Controls this button's behavior when clicked. Recruitment choice buttons recruit a unit, pay for the unit's cost, and remove their attached notification when clicked
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            input_dict = {}
            if self.recruitment_type == 'slave workers':
                input_dict = {}
                self.global_manager.get('money_tracker').change(-1 * self.cost, 'unit recruitment')
                input_dict['grids'] = [self.global_manager.get('slave_traders_grid')]
                attached_cell = input_dict['grids'][0].cell_list[0]
                input_dict['coordinates'] = (attached_cell.x, attached_cell.y)
                input_dict['image'] = 'mobs/slave workers/default.png'
                input_dict['modes'] = ['strategic']
                input_dict['name'] = 'slave workers'
                input_dict['init_type'] = 'slaves'
                input_dict['purchased'] = True
                self.global_manager.get('actor_creation_manager').create(False, input_dict, self.global_manager)
            elif self.recruitment_type == 'African worker village':
                self.global_manager.get('displayed_tile').cell.get_building('village').recruit_worker()
            elif self.recruitment_type == 'African worker slums':
                self.global_manager.get('displayed_tile').cell.get_building('slums').recruit_worker()
            elif self.recruitment_type == 'African worker labor broker':
                recruiter = self.global_manager.get('displayed_mob')
                input_dict['coordinates'] = (recruiter.x, recruiter.y)
                input_dict['grids'] = recruiter.grids
                input_dict['image'] = 'mobs/African workers/default.png'
                input_dict['modes'] = ['strategic']
                input_dict['name'] = 'African workers'
                input_dict['init_type'] = 'workers'
                input_dict['worker_type'] = 'African'
                
                self.global_manager.get('money_tracker').change(-1 * self.notification.choice_info_dict['cost'], 'unit recruitment')
                self.notification.choice_info_dict['village'].change_population(-1)
                market_tools.attempt_worker_upkeep_change('decrease', 'African', self.global_manager) #adds 1 worker to the pool

                worker = self.global_manager.get('actor_creation_manager').create(False, input_dict, self.global_manager)
                if recruiter.is_vehicle:
                    #if recruiter.has_infinite_movement:
                    #    recruiter.temp_disable_movement()
                    #else:
                    recruiter.set_movement_points(0)
                    worker.crew_vehicle(recruiter)
                else:
                    recruiter.set_movement_points(0)
                    self.global_manager.get('actor_creation_manager').create_group(worker, recruiter, self.global_manager)
                    
            else:
                input_dict['coordinates'] = (0, 0)
                input_dict['grids'] = [self.global_manager.get('europe_grid')]
                input_dict['image'] = self.mob_image_id
                input_dict['modes'] = ['strategic', 'europe']
                self.showing_outline = True
                self.global_manager.get('money_tracker').change(-1 * self.cost, 'unit recruitment')
                if self.recruitment_type in self.global_manager.get('officer_types'): #'explorer':
                    name = ''
                    for character in self.recruitment_type:
                        if not character == '_':
                            name += character
                        else:
                            name += ' '
                    input_dict['name'] = name
                    input_dict['init_type'] = self.recruitment_type
                    input_dict['officer_type'] = self.recruitment_type
                elif self.recruitment_type == 'European workers':
                    input_dict['name'] = 'European workers'
                    input_dict['init_type'] = 'workers'
                    input_dict['worker_type'] = 'European'
                elif self.recruitment_type == 'African workers':
                    input_dict['name'] = 'African workers'
                    input_dict['init_type'] = 'workers'
                    input_dict['worker_type'] = 'African'
                elif self.recruitment_type == 'steamship':
                    image_dict = {'default': self.mob_image_id, 'crewed': self.mob_image_id, 'uncrewed': 'mobs/steamship/uncrewed.png'}
                    input_dict['image_dict'] = image_dict
                    input_dict['name'] = 'steamship'
                    input_dict['crew'] = 'none'
                    input_dict['init_type'] = 'ship'
                self.global_manager.get('actor_creation_manager').create(False, input_dict, self.global_manager)
        super().on_click()
