#Contains functionality for icons that follow the mouse pointer

import pygame

from .images import free_image

class mouse_follower(free_image):
    '''
    Free image that follows the mouse pointer and appears in certain situations, such as when choosing on a movement destination
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
        x, y = pygame.mouse.get_pos()
        super().__init__('misc/targeting_mouse.png', (x, y), 50, 50, ['strategic', 'europe'], global_manager)
        
    def update(self):
        ''''
        Description:
            Moves this image to follow the mouse pointer
        Input:
            None
        Output:
            None
        '''
        self.x, self.y = pygame.mouse.get_pos()
        self.x -= self.width // 2
        self.y += self.height // 2

    def draw(self):
        '''
        Description:
            Draws this image if the player is currently choosing a movement destination
        Input:
            None
        Output:
            None
        '''
        if self.global_manager.get('choosing_destination') or self.global_manager.get('choosing_advertised_commodity') or self.global_manager.get('drawing_automatic_route'):
            self.update()
            super().draw()
