#Contains functionality for notifications

import time
from .labels import multi_line_label
from . import text_tools
from . import utility
from . import scaling
from . import actor_utility
from . import game_transitions

class notification(multi_line_label):
    '''
    Multi-line label that prompts the user to click on it, and disappears when clicked
    '''
    def __init__(self, coordinates, ideal_width, minimum_height, modes, image, message, global_manager):
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
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.global_manager = global_manager
        self.global_manager.get('notification_list').append(self)
        super().__init__(coordinates, ideal_width, minimum_height, modes, image, message, global_manager)
        self.in_notification = True
        self.is_action_notification = False
        self.notification_dice = 0 #by default, do not show any dice when notification shown
        self.global_manager.get('sound_manager').play_sound('opening_letter')
        self.creation_time = time.time()
        self.notification_type = 'default'

    def format_message(self):
        '''
        Description:
            Converts this notification's string message to a list of strings, with each string representing a line of text. Each line of text ends when its width exceeds the ideal_width or when a '/n' is encountered in the text
        Input:
            None
        Output:
            None
        '''
        super().format_message()
        self.message.append("Click to remove this notification.")
                    
    def update_tooltip(self):
        '''
        Description:
            Sets this notification's tooltip to what it should be. By default, notifications prompt the player to close them
        Input:
            None
        Output:
            None
        '''
        self.set_tooltip(["Click to remove this notification"])

    def on_click(self):
        '''
        Description:
            Controls this notification's behavior when clicked. By default, notifications are removed when clicked
        Input:
            None
        Output:
            None
        '''
        if time.time() - 0.1 > self.creation_time: #don't accidentally remove notifications instantly when clicking between them
            self.remove()
            
    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. By default, notifications are removed when clicked. When a notification is removed, the next notification is shown,
                if there is one
        Input:
            None
        Output:
            None
        '''
        super().remove()
        notification_manager = self.global_manager.get('notification_manager')
        self.global_manager.set('notification_list', utility.remove_from_list(self.global_manager.get('notification_list'), self))
        if len(notification_manager.notification_queue) >= 1:
            notification_manager.notification_queue.pop(0)
        if len(notification_manager.notification_queue) > 0:
            notification_manager.notification_to_front(notification_manager.notification_queue[0])

class minister_notification(notification):
    '''
    Notification that is a message from a minister and has a minister portrait attached
    '''
    def __init__(self, coordinates, ideal_width, minimum_height, modes, image, message, global_manager, attached_minister):
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
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, ideal_width, minimum_height, modes, image, message, global_manager)
        self.attached_minister = attached_minister
        self.notification_type = 'minister'
        
    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. By default, notifications are removed when clicked. When a notification is removed, the next notification is shown,
                if there is one
        Input:
            None
        Output:
            None
        '''
        super().remove()
        num_removed = 0
        for current_minister_image in self.global_manager.get('dice_roll_minister_images'):
            if current_minister_image.attached_minister == self.attached_minister and num_removed < 2: #each minister message has up to 2 images
                current_minister_image.remove()
                num_removed += 1
        
        
class zoom_notification(notification):
    '''
    Notification that selects a certain tile or mob and moves the minimap to it when first displayed
    '''
    def __init__(self, coordinates, ideal_width, minimum_height, modes, image, message, target, global_manager):
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
            actor target: Tile or mob to select and move the minimap to when this notification is first displayed
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, ideal_width, minimum_height, modes, image, message, global_manager)
        self.notification_type = 'default'
        self.reselect = True
        if self.global_manager.get('strategic_map_grid') in target.grids:
            self.global_manager.get('minimap_grid').calibrate(target.x, target.y)
        if target.actor_type == 'tile':
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), target)
            if not target.cell.grid.mini_grid == 'none':
                target.grids[0].mini_grid.calibrate(target.x, target.y)
        elif target.actor_type == 'mob':
            if not target.images[0].current_cell == 'none': #if non-hidden mob, move to front of tile and select
                if self.global_manager.get('displayed_mob') == target:
                    self.reselect = False
                target.select()
                target.move_to_front()
                #actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('tile_info_display_list'), target.images[0].current_cell.tile)
                if (not target.grids[0].mini_grid == 'none'): #if not in abstract grid, calibrate mini map to mob location
                   target.grids[0].mini_grid.calibrate(target.x, target.y)

            else: #if hidden mob, move to location and select tile
                target.grids[0].mini_grid.calibrate(target.x, target.y)
                actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('tile_info_display_list'), target.grids[0].find_cell(target.x, target.y).tile)

    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. By default, notifications are removed when clicked. When a notification is removed, the next notification is shown,
                if there is one
        Input:
            None
        Output:
            None
        '''
        if self.reselect:
            game_transitions.cycle_player_turn(self.global_manager, True)
        super().remove()

