#Contains functionality for dice icons

import pygame
import time
import random
from .buttons import button
from . import utility

class die(button):
    '''
    A die with a predetermined result that will appear, show random rolling, and end with the predetermined result and an outline with a color based on the result
    '''
    def __init__(self, coordinates, width, height, modes, num_sides, result_outcome_dict, outcome_color_dict, final_result, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this die
            int width: Pixel width of this die
            int height: Pixel height of this die
            string list modes: Game modes during which this button can appear
            int num_sides: Number of sides for this die
            string/int dictionary result_outcome_dict: dictionary of string result type keys and int die result values determining which die results are successes/failures or critical successes/failures
            string/int outcome_color_dict: dictionary of string color name keys and int die result values determining what colors are shown for certain die results
            int final_result: Predetermined final result of this roll that the die will end on
            global_manager_template global_manager: Object that accesses shared variables
        Ouptut:
            None
        '''
        self.result_outcome_dict = result_outcome_dict #min_success: 4, min_crit_success: 6, max_crit_fail: 1
        self.outcome_color_dict = outcome_color_dict #'success': 'green', 'crit_success': 'bright green', 'fail': 'red', crit_fail: 'black', 'default': 'gray'
        self.rolls_completed = 0
        self.num_sides = num_sides
        if global_manager.get('DEBUG_ministry_of_magic'):
            self.num_rolls = 1
        else:
            self.num_rolls = random.randrange(-3, 4) + 7 #4-10
        self.roll_interval = 0.3
        self.rolling = False
        self.last_roll = 0
        self.highlighted = False
        self.normal_die = True
        if (self.result_outcome_dict['min_success'] <= 0 or self.result_outcome_dict['min_success'] >= 7) and self.result_outcome_dict['max_crit_fail'] <= 0 and result_outcome_dict['min_crit_success'] >= 7:
            #if roll without normal success/failure results, like combat
            image_id = 'misc/dice/4.png'
            self.normal_die = False
        elif self.result_outcome_dict['min_success'] <= 6:
            image_id = 'misc/dice/' + str(self.result_outcome_dict['min_success']) + '.png'
        else:
            image_id = 'misc/dice/impossible.png'
        super().__init__(coordinates, width, height, 'green', 'label', 'none', modes, image_id, global_manager)
        global_manager.get('dice_list').append(self)
        self.final_result = final_result
        self.Rect = pygame.Rect(self.x, self.global_manager.get('display_height') - (self.y + height), width, height)#create pygame rect with width and height, set color depending on roll result, maybe make a default gray appearance
        self.highlight_Rect = pygame.Rect(self.x - 3, self.global_manager.get('display_height') - (self.y + height + 3), width + 6, height + 6)
        self.color = 'white'
        if self.normal_die:
            self.outline_color = self.outcome_color_dict['default']
        else:
            if self.result_outcome_dict['min_success'] <= 0: #if green combat die
                self.outline_color = self.outcome_color_dict['success']
                self.special_die_type = 'green'
            else: #if red combat die
                self.outline_color = self.outcome_color_dict['fail']
                self.special_die_type = 'red'
        self.in_notification = True #dice are attached to notifications and should be drawn over other buttons

    def on_click(self):
        '''
        Description:
            Controls this button's behavior when clicked. A die copies the on_click behavior of its attached notification, which should cause the die to start rolling
        Input:
            None
        Output:
            None
        '''
        if self.global_manager.get('notification_manager').notification_type_queue[0] == 'roll': #if next notification is rolling... notification, clicking on die is alternative to clicking on notification
            self.global_manager.get('notification_list')[0].on_click()#self.start_rolling()

    def update_tooltip(self):
        '''
        Description:
            Sets this image's tooltip to what it should be, depending on its button_type. If a die is not rolling yet, a description of the results required for different outcomes will be displayed. If a die is currently rolling, its
                current value will be displayed. If a die is finished rolling, its final value and a description that it has finished rolling and whether its result was selected will be displayed.
        Input:
            None
        Output:
            None
        '''
        tooltip_list = []
        if self.rolls_completed == 0:
            if self.normal_die: #if has normal success/failure results
                if self.result_outcome_dict['min_success'] <= 6:
                    tooltip_list.append(str(self.result_outcome_dict['min_success']) + '+ required for success')
                else:
                    tooltip_list.append(str('Success is impossible'))
                if not self.result_outcome_dict['min_crit_success'] > self.num_sides: #do not mention critical success if impossible 
                    if self.result_outcome_dict['min_crit_success'] == self.num_sides:
                        tooltip_list.append(str(self.result_outcome_dict['min_crit_success']) + ' required for critical success')
                    else:
                        tooltip_list.append(str(self.result_outcome_dict['min_crit_success']) + '+ required for critical success')
                if not self.result_outcome_dict['max_crit_fail'] <= 0: #do not mention critical failure if impossible 
                    if self.result_outcome_dict['max_crit_fail'] == self.num_sides:
                        tooltip_list.append(str(self.result_outcome_dict['max_crit_fail']) + ' required for critical failure')
                    else:
                        tooltip_list.append(str(self.result_outcome_dict['max_crit_fail']) + ' or lower required for critical failure')
            tooltip_list.append('Click to roll')
        else:
            tooltip_list.append(str(self.roll_result))
            if not self.rolling: #if rolls completed
                tooltip_list.append('Finished rolling')
                if self.highlighted and len(self.global_manager.get('dice_list')) > 1: #if other dice present and this die chosen
                    tooltip_list.append('This result was chosen')
        self.set_tooltip(tooltip_list)

    def start_rolling(self):
        '''
        Description:
            Causes this die to start rolling, after which it will switch to a different side every roll_interval seconds   
        Input:
            None
        Output:
            None
        '''
        self.last_roll = time.time()
        self.rolling = True
        dice_list = self.global_manager.get('dice_list')
        if self == dice_list[0]: #only 1 die at a time makes noise
            if len(dice_list) == 1:
                self.global_manager.get('sound_manager').play_sound('dice 1')
            elif len(dice_list) == 2:
                self.global_manager.get('sound_manager').play_sound('dice 2')
            else:
                self.global_manager.get('sound_manager').play_sound('dice 3')
                
        
    def roll(self):
        '''
        Description:
            Rolls this die to a random face, or to the predetermined result if it is the last roll. When all dice finish rolling, dice rolling notifications will be removed
        Input:
            None
        Output:
            None
        '''
        self.last_roll = time.time()
        if self.rolls_completed == self.num_rolls: #if last roll just happened, stop rolling - allows slight pause after last roll during which you don't know if it is the final one
            self.rolling = False
            dice_rolling = False
            for current_die in self.global_manager.get('dice_list'):
                if current_die.rolling:
                    dice_rolling = True
            if (not self.global_manager.get('current_dice_rolling_notification') == 'none') and not dice_rolling: #if notification present and dice finished rolling, remove notification
                self.global_manager.get('current_dice_rolling_notification').remove()
        else:
            self.roll_result = 0
            if self.rolls_completed == self.num_rolls - 1: #if last roll
                self.roll_result = self.final_result
            else:
                self.roll_result = random.randrange(1, self.num_sides + 1) #1 - num_sides, inclusive
            if self.normal_die:
                if self.roll_result >= self.result_outcome_dict['min_success']: #if success
                    if self.roll_result >= self.result_outcome_dict['min_crit_success']: #if crit success
                        self.outline_color = self.outcome_color_dict['crit_success']
                    else: #if normal success
                        self.outline_color = self.outcome_color_dict['success']
                else: #if failure
                    if self.roll_result <= self.result_outcome_dict['max_crit_fail']: #if crit fail
                        self.outline_color = self.outcome_color_dict['crit_fail']
                    else: #if normal fail
                        self.outline_color = self.outcome_color_dict['fail']
            self.image.set_image('misc/dice/' + str(self.roll_result) + '.png')#self.set_label(str(self.roll_result))
            self.rolls_completed += 1

    def draw(self):
        '''
        Description:
            If enough time has passed since the last roll and this die is still rolling, this will roll the die again. Additionally, this draws the die with a face corresponding to its current value. If the die is finished rolling and
                its result was used, an outline with a color corresponding to the roll's result will be displayed.
        Input:
            None
        Output:
            None
        '''
        if self.can_show(): #if self.global_manager.get('current_game_mode') in self.modes:
            if self.rolling and time.time() >= self.last_roll + self.roll_interval: #if roll_interval time has passed since last_roll
                self.roll()
            pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')[self.color], self.Rect)
            if self.highlighted or not self.normal_die:
                pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')[self.outline_color], self.Rect, 6)
            else:
                pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['black'], self.Rect, 6)
            self.image.draw()        

    def remove(self):
        '''
        Description:
            Removes the object from relevant lists and prevents it from further appearing in or affecting the program
        Input:
            None
        Output:
            None
        '''
        self.global_manager.set('label_list', utility.remove_from_list(self.global_manager.get('label_list'), self))
        self.global_manager.set('button_list', utility.remove_from_list(self.global_manager.get('button_list'), self))
        self.global_manager.set('dice_list', utility.remove_from_list(self.global_manager.get('dice_list'), self))
        self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), self.image))
        if self.global_manager.get('displayed_mob') in self.global_manager.get('mob_list'): #only need to remove die from mob's list if mob still alive
            self.global_manager.get('displayed_mob').attached_dice_list = utility.remove_from_list(self.global_manager.get('displayed_mob').attached_dice_list, self)

    def can_show(self):
        '''
        Description:
            Returns whether this die should be shown. The currently displayed notification should have a number of dice attached to it, and only that many of existing dice are shown at once, starting from the those first created
        Input:
            None
        Output:
            boolean: Returns whether this die should be shown
        '''
        if super().can_show():
            if self.global_manager.get('ongoing_trial'): #rolls during a trial are not done through a mob, so always show them
                return(True)
            displayed_mob_dice_list = self.global_manager.get('displayed_mob').attached_dice_list
            num_notification_dice = self.global_manager.get('notification_list')[0].notification_dice
            if self in displayed_mob_dice_list:
                if displayed_mob_dice_list.index(self) <= (num_notification_dice - 1): #if 1 notification die, index must be <= 0 to be shown
                    return(True)
        return(False)
