#Contains functions that manage the text box and other miscellaneous text display utility

import pygame

def message_width(message, fontsize, font_name):
    '''
    Description:
        Returns the pixel width of the inputted text if rendered with the inputted font and font size
    Input:
        String message: Text whose width will be found
        int fontsize: Font size of the text whose width will be found, like 12
        string font_name: Font name of the text whose width will be found, like 'times new roman'
    Output:
        int: Pixel width of the inputted text
    '''
    current_font = pygame.font.SysFont(font_name, fontsize)
    text_width, text_height = current_font.size(message)
    return(text_width)


def get_input(solicitant, message, global_manager):
    '''
    Description:
        Tells the input manager to displays the prompt for the user to enter input and prepare to receive input and send it to the part of the program requesting input
    Input:
        string solicitant: Represents the part of the program to send input to
        string message: Prompt given to the player to enter input
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    global_manager.get('input_manager').start_receiving_input(solicitant, message)

def text(message, font, global_manager):
    '''
    Description:
        Returns a rendered pygame.Surface of the inputted text
    Input:
        string message: Text to be rendered
        pygame.font font: pygame font with which the text is rendered
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        pygame.Surface: Rendered pygame.Surface of the inputted text
    '''
    return(font.render(message, False, global_manager.get('color_dict')['black']))

def manage_text_list(text_list, max_length):
    '''
    Description:
        Removes any text lines in the inputted list past the inputted length
    Input:
        string list text_list: List of text lines contained in the text box
        int max_length: Maximum number of text lines that the text box should be able to have
    Output:
        string list: Inputted list shortened to the inputted length
    '''
    if len(text_list) > max_length:
        while not len(text_list) == max_length:
            text_list.pop(0)
    return(text_list)


def print_to_screen(input_message, global_manager):
    '''
    Description:
        Adds the inputted message to the bottom of the text box
    Input:
        string input_message: Message to be added to the text box
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    global_manager.get('text_list').append(input_message)

    
def print_to_previous_message(message, global_manager):
    '''
    Description:
        Adds the inputted message to the most recently displayed message of the text box
    Input:
        string message: Message to be added to the text box
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    global_manager.get('text_list')[-1] = global_manager.get('text_list')[-1] + message

    
def clear_message(global_manager):
    '''
    Description:
        Deletes the text box line that is currently being typed
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    global_manager.set('message', '')

def remove_underscores(message):
    '''
    Description:
        Replaces underscores in the inputted message with spaces
    Input:
        string message: a message with underscores
    Output:
        string: the inputted message but with spaces
    '''
    return_message = ''
    for current_character in message:
        if current_character == '_':
            return_message += ' '
        else:
            return_message += current_character
    return(return_message)
