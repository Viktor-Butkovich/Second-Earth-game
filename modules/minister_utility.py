#Contains miscellaneous functions relating to minister functionality

def check_corruption(minister_type, global_manager):
    '''
    Description:
        Returns whether the minister in the inputted office would lie about the result of a given roll
    Input:
        string minister_type: Minister office to check the corruption of, like Minister of Trade
    Description:
        boolean: Returns whether the minister in the inputted office would lie about the result of a given roll
    '''
    return(global_manager.get('current_ministers')[minister_type].check_corruption)

def get_skill_modifier(minister_type, global_manager):
    '''
    Description:
        Returns the skill-based dice roll modifier of the minister in the inputted office
    Input:
        string 'minister_type': Minister office to check the corruption of, like Minister of Trade
    Output:
        int: Returns the skill-based dice roll modifier of the minister in the inputted office, between -1 and 1
    '''
    return(global_manager.get('current_ministers')[minister_type].get_skill_modifier)

def calibrate_minister_info_display(global_manager, new_minister):
    '''
    Description:
        Updates all relevant objects to display the inputted minister
    Input:
        global_manager_template global_manager: Object that accesses shared variables
        string new_minister: The new minister that is displayed
    Output:
        None
    '''
    global_manager.set('displayed_minister', new_minister)
    for current_object in global_manager.get('minister_info_display_list'):
        current_object.calibrate(new_minister)

def calibrate_trial_info_display(global_manager, info_display_list, new_minister):
    '''
    Description:
        Updates all relevant objects to display the inputted minister for a certain side of a trial
    Input:
        global_manager_template global_manager: Object that accesses shared variables
        button/actor list info_display_list: All buttons and actors that are updated when the displayed mob or tile changes. Can be 'prosecution_info_display_list' or 'defense_info_display_list' depending on the minister's side in
            the trial
        string new_minister: The new minister that is displayed
    Output:
        None
    '''
    if info_display_list == global_manager.get('defense_info_display_list'):
        global_manager.set('displayed_defense', new_minister)
    elif info_display_list == global_manager.get('prosecution_info_display_list'):
        global_manager.set('displayed_prosecution', new_minister)
    for current_object in info_display_list:
        current_object.calibrate(new_minister)

def trial_setup(defense, prosecution, global_manager):
    '''
    Description:
        Sets the trial info displays to the defense and prosecution ministers at the start of a trial
    Input:
        minister defense: Minister to calibrate defense info display to
        minister prosecution: Minsiter to calibrate prosecution info display to
    Output:
        None
    '''
    calibrate_trial_info_display(global_manager, global_manager.get('defense_info_display_list'), defense)
    calibrate_trial_info_display(global_manager, global_manager.get('prosecution_info_display_list'), prosecution)
    
def update_available_minister_display(global_manager):
    '''
    Description:
        Updates the display of available ministers to be hired, displaying 3 of them in order based on the current display index
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    available_minister_portrait_list = global_manager.get('available_minister_portrait_list')
    available_minister_left_index = global_manager.get('available_minister_left_index')
    available_minister_list = global_manager.get('available_minister_list')
    for current_index in range(len(available_minister_portrait_list)):
        minister_index = available_minister_left_index + current_index
        if minister_index < len(available_minister_list) and minister_index >= 0:
            available_minister_portrait_list[current_index].calibrate(available_minister_list[minister_index])
        else:
            available_minister_portrait_list[current_index].calibrate('none')
    if len(available_minister_list) > 0 and not available_minister_left_index + 2 >= len(available_minister_list):
        calibrate_minister_info_display(global_manager, available_minister_list[available_minister_left_index + 2])

def positions_filled(global_manager):
    '''
    Description:
        Returns whether all minister positions are currently filled. Any action in the game that could require minister rolls should only be allowed when all minister positions are filled
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        boolean: Returns whether all minister positions are currently filled
    '''
    completed = True
    for current_position in global_manager.get('minister_types'):
        if global_manager.get('current_ministers')[current_position] == 'none':
            completed = False
    return(completed)
