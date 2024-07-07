# Contains miscellaneous functions, like removing an item from a list or finding the distance between 2 points

from typing import List


def find_object_distance(first, second):
    """
    Description:
        Returns the distance between the positions of the inputted objects. Functions correctly regardless of whether the x and y coordinate attributes are pixel coordinates or grid coordinates
    Input:
        object first: Object with x and y coordinate attributes
        object second: Object with x and y coordinate attributes
    Output:
        double: Returns the distance between the positions of the inputted objects
    """
    return (((first.x - second.x) ** 2) + ((first.y - second.y) ** 2)) ** 0.5


def find_coordinate_distance(first, second):
    """
    Description:
        Returns the distance between the positions of the inputted coordinates. Functions correctly regardless of whether the x and y coordinates are pixel coordinates or grid coordinates
    Input:
        int tuple first: Two values representing x and y coordinates
        int tuple second: Two values representing x and y coordinates
    Output:
        double: Returns the distance between the positions of the inputted coordinates
    """
    first_x, first_y = first
    second_x, second_y = second
    return (((first_x - second_x) ** 2) + ((first_y - second_y) ** 2)) ** 0.5


def find_grid_distance(first, second):
    """
    Description:
        Returns the sum of the horizontal and vertical distances between the positions of the inputted objects. Works for calculating movement distance on a grid. Returns -1 for objects on different grids
    Input:
        object first: Object with x and y coordinate attributes
        object second: Object with x and y coordinate attributes
    Output:
        int: Returns the sum of the horizontal and vertical distance between the positions of the inputted objects
    """
    horizontal_distance = abs(first.x - second.x)
    vertical_distance = abs(first.y - second.y)
    if not first.grids[0] in second.grids:
        return -1
    return horizontal_distance + vertical_distance


def remove_from_list(received_list, item_to_remove):
    """
    Description:
        Returns a version of the inputted list with all instances of the inputted item removed
    Input:
        any type list received list: list to remove items from
        any type item_to_remove: Item to remove from the list
    Output:
        any type list: Returns a version of the inputted list with all instances of the inputted item removed
    """
    output_list = []
    for item in received_list:
        if not item == item_to_remove:
            output_list.append(item)
    return output_list


def copy_list(
    received_list,
):  # allows setting to new list by copying data instead of just pointer
    """
    Description:
        Returns a deep copy of the inputted list with shallow copies of each of its elements - the list contents refer to the exact same objects, but adding an item to 1 list will not change
            the other
    Input:
        list received_list: list to Copy
    Output:
        list: Returns a copy of the inputted list
    """
    return_list = []
    for item in received_list:
        return_list.append(item)
    return return_list


def generate_article(word, add_space=False):
    """
    Description:
        Returns 'an' if the inputted word starts with a vowel or 'a' if the inputted word does not start with a vowel. In certain exception cases, the correct article will be returned regardless of the first letter. Used to correctly
            describe a word
    Input:
        string word: Word to generate an article for
    Output:
        string: Returns 'an' if the inputed word starts with a vowel, otherwise returns 'a'
    """
    if add_space:
        space = " "
    else:
        space = ""
    vowels = ["a", "e", "i", "o", "u"]
    plural_exceptions = ["hills", "genius", "brainless", "treacherous"]
    a_an_exceptions = ["European", "unit"]
    if word[-1] == "s" and (not word in plural_exceptions) and (not " " in word):
        return ""
    elif word[0].lower() in vowels and (not word in a_an_exceptions):
        return "an" + space
    else:
        return "a" + space


def generate_plural(amount):
    """
    Description:
        Returns an empty string if the inputted amount is equal to 1. Otherwise returns 's'. Allows the correct words to be used when describing a variable's value
    Input:
        int amount: It is determined whether this value is plural or not
    Output:
        string: Returns an empty string if the inputted amount is equal to 1, otherwise returns 's'
    """
    if amount == 1:
        return ""
    else:
        return "s"


def generate_capitalized_article(word):
    """
    Description:
        Returns 'An' if the inputted word starts with a vowel or 'A' if the inputted word does not start with a vowel. In certain exception cases, the correct article will be returned regardless of the first letter. Used to correctly
            describe a word at the beginning of a sentence
    Input:
        string word: Word to generate an article for
    Output:
        string: Returns 'An' if the inputed word starts with a vowel, otherwise returns 'A'
    """
    vowels = ["a", "e", "i", "o", "u"]
    plural_exceptions = []
    a_an_exceptions = ["European", "unit"]
    if word[-1] == "s" and (not word in plural_exceptions):
        return " "
    elif word[0] in vowels and (not word in a_an_exceptions):
        return "An "
    else:
        return "A "


def conjugate(infinitive, amount, tense="present"):
    """
    Description:
        Returns a singular or plural conjugated version of the inputted verb
    Input:
        string infinitive: base word to conjugate, like 'be' or 'attack'
        int amount: quantity of subject, determining if singular or plural verb should be used
        string tense = 'present': tense of verb, determining version of verb, like 'was' or 'is', to use
    Output:
        string: Returns conjugated word with the correct number, like 'is' or 'attacks'
    """
    if infinitive == "be":
        if tense == "present":
            if amount == 1:
                return "is"
            else:
                return "are"
        elif tense == "preterite":
            if amount == 1:
                return "was"
            else:
                return "were"
    else:
        if amount == 1:
            return infinitive + "s"
        else:
            return infinitive
    return "none"


def capitalize(string):
    """
    Description:
        Capitalizes the first letter of the inputted string and returns the resulting string. Unlike python's default capitalize method, does not make the rest of the string lowercase
    Input:
        string string: string that is being capitalized
    Output:
        string: Returns capitalized string
    """
    if len(string) > 1:
        return string[:1].capitalize() + string[1:]
    else:
        return string[:1].capitalize()


def combine(*args) -> List:
    """
    Description:
        Combines any number of inputted arguments into a single list
    Input:
        *args: Any number of inputted non-keyword arguments
    Output:
        List: Returns combination of inputted arguments
    """
    return_list: List = []
    for arg in args:
        if type(arg) == list:
            if return_list:
                return_list += arg
            else:
                return_list = arg.copy()
        else:
            return_list.append(arg)
    return return_list


def fahrenheit(temperature: int):
    """
    Description:
        Returns the approximate fahrenheit temperature for the inputted tile temperature
    Input:
        int temperature: Temperature in game units
    Output:
        int: Returns temperature in fahrenheit
    """
    if temperature < 1:
        return temperature * 30 - 20
    elif temperature > 6:
        return temperature * 30 - 70
    else:
        return temperature * 20 - 5
