#Contains functions that control the display of new notifications

def display_notification(message, notification_type, global_manager, num_dice_shown = 0): #default, exploration, or roll
    '''
    Description:
        Adds a future notification to the notification queue with the inputted text and type. If other notifications are already in the notification queue, adds this notification to the back, causing it to appear last. When a
            notification is closed, the next notification in the queue is shown
    Input:
        string message: Text for future notification
        string notification_type: Type of notification created, like 'roll, 'choice', or 'exploration'
        global_manager_template global_manager: Object that accesses shared variables
        int num_dice_shown = 0: Determines number of dice allowed to be shown during the displayed notification, allowing the correct ones to be shown when multiple notifications are queued
    Output:
        None
    '''
    global_manager.get('notification_manager').notification_queue.append(message)#global_manager.get('notification_queue').append(message)
    global_manager.get('notification_manager').notification_type_queue.append(notification_type)#global_manager.get('notification_type_queue').append(notification_type)
    global_manager.get('notification_manager').notification_dice_queue.append(num_dice_shown)
    if len(global_manager.get('notification_manager').notification_queue) == 1: #_type_queue
        global_manager.get('notification_manager').notification_to_front(message)#notifications.notification_to_front(message, global_manager)

def display_choice_notification(message, choices, choice_info_dict, global_manager): #default, exploration, or roll
    '''
    Description:
        Adds a future notification to the notification queue with the inputted text and type. If other notifications are already in the notification queue, adds this notification to the back, causing it to appear last. When a
            notification is closed, the next notification in the queue is shown
    Input:
        string message: Text for future notification
        string list choices: Types of buttons for the choices on the choice notification, like 'end turn' or 'none'
        dictionary choice_info_dict: dictionary containing various information needed for the choice notifications and its buttons correctly, such as by recording which caravan is trading during a trade notification to allow the
            bought commodities to go to the correct mob. Contains different information based on the situation and the choices list
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    global_manager.get('notification_manager').notification_queue.append(message)#global_manager.get('notification_queue').append(message)
    global_manager.get('notification_manager').notification_type_queue.append('choice')#global_manager.get('notification_type_queue').append(notification_type)
    global_manager.get('notification_manager').notification_dice_queue.append(0)
    global_manager.get('notification_manager').choice_notification_choices_queue.append(choices)
    global_manager.get('notification_manager').choice_notification_info_dict_queue.append(choice_info_dict)
    if len(global_manager.get('notification_manager').notification_queue) == 1: #_type_queue
        global_manager.get('notification_manager').notification_to_front(message)#notifications.notification_to_front(message, global_manager)

def display_zoom_notification(message, target, global_manager):
    '''
    Description:
        Adds a future notification to the notification queue with the inputted text and type. If other notifications are already in the notification queue, adds this notification to the back, causing it to appear last. When a
            notification is closed, the next notification in the queue is shown. A zoom notification selects the target and moves the minimap to it when revealed
    Input:
        string message: Text for future notification
        actor target: Can be a tile or mob, object to select when the zoom notification is revealed
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    global_manager.get('notification_manager').notification_queue.append(message)
    global_manager.get('notification_manager').notification_type_queue.append('zoom')
    global_manager.get('notification_manager').notification_dice_queue.append(0)
    global_manager.get('notification_manager').choice_notification_choices_queue.append(target)
    global_manager.get('notification_manager').choice_notification_info_dict_queue.append('n/a')
    if len(global_manager.get('notification_manager').notification_queue) == 1:
        global_manager.get('notification_manager').notification_to_front(message)   

def show_tutorial_notifications(global_manager):
    '''
    Description:
        Displays tutorial messages at various points in the program. The exact message depends on how far the player has advanced through the tutorial   
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    if not global_manager.get('minister_appointment_tutorial_completed'):
        message = "Welcome to Scramble for Africa! /n /n"
        message += "Your goal as colonial governor is to bring glory to your country's name by conquering and enlightening this hostile continent, hopefully becoming fabulously rich in the process. /n /n"
        display_notification(message, 'default', global_manager)
        
        message = "Welcome to Scramble for Africa! /n /n"
        message += "You must start the game by appointing ministers to control each part of your company's operations. Choose wisely, as skilled, loyal ministers will prove to be capable and reliable in their exploits while the "
        message += "corrupt will lie and steal and the incompetent will repeatedly try and fail, losing money and lives in the process. /n /n"
        display_notification(message, 'default', global_manager)

        message = "Welcome to Scramble for Africa! /n /n"
        message += "To appoint a minister, scroll through the available ministers in the lower right and click on one to select it. Then, see the selected minister in the upper left and select an office to appoint them to. /n /n"
        message += "Repeat this until all offices are filled. /n /n"
        display_notification(message, 'default', global_manager)
    elif not global_manager.get('exit_minister_screen_tutorial_completed'):
        message = "Now a minister has been appointed for each part of your company. Throughout the game, you will order these ministers to complete various actions and they will report their success or failure through dice rolls. "
        message += "These dice rolls are not purely random - a skilled minister may have higher results while a corrupt one may report a failure and steal the money given for the action without even "
        message += "attempting it. /n /nIs an unsuccessful minister incompetent, corrupt, or merely unlucky? Perhaps all three? /n /n"
        display_notification(message, 'default', global_manager)

        message = "Now, exit the minister screen through the button in the top left corner. You may use the same button to return here in the future to modify minister appointments and examine potential recruits. /n /n"
        display_notification(message, 'default', global_manager)
                             
