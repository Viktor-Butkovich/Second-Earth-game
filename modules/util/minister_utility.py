# Contains miscellaneous functions relating to minister functionality

from modules.util import game_transitions
from modules.constants import constants, status, flags


def get_minister(minister_type):
    """
    Description:
        Returns the minister in the inputted office
    Input:
        string minister_type: Minister office to get the minister of, like Minister of Trade
    Output:
        minister: Returns the minister in the inputted office
    """
    return status.current_ministers.get(minister_type, None)


def set_minister(minister_type, new_minister):
    """
    Description:
        Sets the minister in the inputted office to the inputted minister
    Input:
        string minister_type: Minister office to set the minister of, like Minister of Trade
        minister new_minister: Minister to set the office to
    Output:
        None
    """
    status.current_ministers[minister_type] = new_minister


def check_corruption(minister_type):
    """
    Description:
        Returns whether the minister in the inputted office would lie about the result of a given roll
    Input:
        string minister_type: Minister office to check the corruption of, like Minister of Trade
    Description:
        boolean: Returns whether the minister in the inputted office would lie about the result of a given roll
    """
    return get_minister(minister_type).check_corruption


def get_skill_modifier(minister_type):
    """
    Description:
        Returns the skill-based dice roll modifier of the minister in the inputted office
    Input:
        string 'minister_type': Minister office to check the corruption of, like Minister of Trade
    Output:
        int: Returns the skill-based dice roll modifier of the minister in the inputted office, between -1 and 1
    """
    return get_minister(minister_type).get_skill_modifier


def calibrate_minister_info_display(new_minister):
    """
    Description:
        Updates all relevant objects to display the inputted minister
    Input:
        string new_minister: The new minister that is displayed
    Output:
        None
    """
    status.displayed_minister = new_minister
    target = None
    if status.displayed_minister:
        target = new_minister
    status.minister_info_display.calibrate(target)
    flags.show_selection_outlines = True
    constants.last_selection_outline_switch = constants.current_time


def calibrate_trial_info_display(info_display, new_minister):
    """
    Description:
        Updates all relevant objects to display the inputted minister for a certain side of a trial
    Input:
        button/actor list info_display: Interface collection that is calibrated to the inputted minister
            the trial
        minister/string new_minister: The new minister that is displayed, or None
    Output:
        None
    """
    if type(info_display) == list:
        return
    target = None
    if new_minister:
        target = new_minister
    info_display.calibrate(target)
    if info_display == status.defense_info_display:
        status.displayed_defense = target
    elif info_display == status.prosecution_info_display:
        status.displayed_prosecution = target


def trial_setup(defense, prosecution):
    """
    Description:
        Sets the trial info displays to the defense and prosecution ministers at the start of a trial
    Input:
        minister defense: Minister to calibrate defense info display to
        minister prosecution: Minsiter to calibrate prosecution info display to
    Output:
        None
    """
    target = None
    if defense:
        target = defense
    calibrate_trial_info_display(status.defense_info_display, target)

    target = None
    if prosecution:
        target = prosecution
    calibrate_trial_info_display(status.prosecution_info_display, target)


def update_available_minister_display():
    """
    Description:
        Updates the display of available ministers to be hired, displaying 3 of them in order based on the current display index
    Input:
        None
    Output:
        None
    """
    for i, current_icon in enumerate(status.available_minister_icon_list):
        current_icon_index = constants.available_minister_left_index + i
        if current_icon_index >= 0 and current_icon_index < len(
            status.available_minister_list
        ):
            current_icon.calibrate(status.available_minister_list[current_icon_index])
        else:
            current_icon.calibrate(None)


def positions_filled():
    """
    Description:
        Returns whether all minister positions are currently filled. Any action in the game that could require minister rolls should only be allowed when all minister positions are filled
    Input:
        None
    Output:
        boolean: Returns whether all minister positions are currently filled
    """
    completed = True
    for key, current_position in status.minister_types.items():
        if not get_minister(current_position.key):
            completed = False
    if not completed:
        game_transitions.force_minister_appointment()
    return completed
