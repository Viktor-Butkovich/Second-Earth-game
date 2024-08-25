# Contains functions that control the results and messages of dice rolls

import random
from . import text_utility
import modules.constants.constants as constants


def roll(
    num_sides, roll_type, requirement, min_crit_success, max_crit_fail, result=None
):  # Optional predetermined result
    """
    Description:
        Conducts a dice roll and prints a description of the outcome to the text box. Does not actually create a die object, instead providing information that can be used to show the result through a die object
    Input:
        int num_sides: Number of sides of the simulated die
        string roll_type: Represents the purpose of the roll, affecting the roll's description
        int requirement: Minimum value required for the roll to succeed
        int min_crit_success: Minimum value required for the roll to critically succed
        max_crit_fail: Maximum value required for the roll to critically fail
        string/int result = None: If value passed, the die will roll to a predetermined result
    Output:
        int: Returns the random value rolled
    """
    if result == None:
        result = random.randrange(1, num_sides + 1)
    text_utility.print_to_screen(
        roll_type + ": " + str(requirement) + "+ required to succeed"
    )
    if result >= requirement:
        if result >= min_crit_success:
            text_utility.print_to_screen(
                "You rolled a " + str(result) + ": CRITICAL SUCCESS!"
            )
        else:
            text_utility.print_to_screen("You rolled a " + str(result) + ": SUCCESS!")
    else:
        if result <= max_crit_fail:
            text_utility.print_to_screen(
                "You rolled a " + str(result) + ": CRITICAL FAILURE"
            )
        else:
            text_utility.print_to_screen("You rolled a " + str(result) + ": FAILURE")
    return result


def roll_to_list(
    num_sides, roll_type, requirement, min_crit_success, max_crit_fail, result=None
):
    """
    Description:
        Conducts a dice roll and returns a list that contains the roll's result and a description of the roll. Does not actually create a die object, instead providing information that can be used to show the result through a die object
    Input:
        int num_sides: Number of sides of the simulated die
        string roll_type: Represents the purpose of the roll, affecting the roll's description
        int requirement: Minimum value required for the roll to succeed
        int min_crit_success: Minimum value required for the roll to critically succed
        max_crit_fail: Maximum value required for the roll to critically fail
        string/int result = None: If value passed, the die will roll to a predetermined result
    Output:
        int/string list: List representing the roll's outcome, with the first item being the roll's int result and the second item being a string description of the roll
    """
    if result == None:
        result = random.randrange(1, num_sides + 1)
    text = ""

    if not roll_type == "second":  # do not show again for 2nd die rolled by veteran
        text += roll_type + ": " + str(requirement) + "+ required to succeed /n"
    if result >= requirement:
        if result >= min_crit_success:
            text += "You rolled a " + str(result) + ": CRITICAL SUCCESS! /n"
        else:
            text += "You rolled a " + str(result) + ": SUCCESS! /n"
    else:
        if result <= max_crit_fail:
            text += "You rolled a " + str(result) + ": CRITICAL FAILURE /n"
        else:
            text += "You rolled a " + str(result) + ": FAILURE /n"
    return [result, text]


def combat_roll_to_list(num_sides, roll_type, result, modifier):
    """
    Description:
        Conducts a dice roll and returns a list that contains the roll's result and a description of the roll. Unlike normal rolls, a combat roll does not have an inherent success or failure, as it uses competing rolls instead of a
            difficulty class
    Input:
        int num_sides: Number of sides of the simulated die
        string roll_type: Represents the purpose of the roll, affecting the roll's description
        string/int result = None: If value passed, the die will roll to a predetermined result
        int modifier: Value added to the dice roll and shown in the description of the calculation
    """
    if result == None:
        result = random.randrange(1, num_sides + 1)
    text = ""
    if roll_type == "second":
        text += "Second roll: /n"
    else:
        text += roll_type + ": /n"
    text += "You rolled a " + str(result) + " "
    if modifier > 0:
        text += "+ " + str(modifier) + " = " + str(result + modifier)
    elif modifier < 0:
        text += "- " + str(modifier * -1) + " = " + str(result + modifier)
    text += " /n"
    return [result, text]
