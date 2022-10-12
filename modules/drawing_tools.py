#Contains functions that control the display of images

import pygame

def rect_to_surface(rect):
    '''
    Description:
        Converts the inputted Rect to a Surface and returns it, allowing an image or text to be drawn on it
    Input:
        pygame.Rect rect: Rect to convert to a Surface
    Output:
        pygame.Surface: Returns a version of the inputted Rect converted to a Surface
    '''
    return pygame.Surface((rect.width, rect.height))

def display_image(image, x, y, global_manager):
    '''
    Description:
        Draws the inputted image at the inputted coordinates
    Input:
        pygame.image image: Image to be displayed
        int x: Pixel x coordinate at which to display the image
        int y: Pixel y coordinate at which to display the image
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    global_manager.get('game_display').blit(image, (x, y))

def display_image_angle(image, x, y, angle, global_manager):
    '''
    Description:
        Draws the inputted image at the inputted coordinates tilted at the inputted angle
    Input:
        pygame.image image: Image to be displayed
        int x: Pixel x coordinate at which to display the image
        int y: Pixel y coordinate at which to display the image
        int angle: Angle in degrees at which to display the image
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    topleft = (x, y)
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)
    global_manager.get('game_display').blit(rotated_image, new_rect.topleft)
