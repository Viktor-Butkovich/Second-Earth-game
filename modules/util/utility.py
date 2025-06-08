# Contains miscellaneous functions, like removing an item from a list or finding the distance between 2 points
import random
import os
from typing import List, Tuple, Dict
from copy import deepcopy


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


def generate_possessive(word):
    """
    Description:
        Returns the possessive form of the inputted noun
    Input:
        string word: Word to generate a possessive form for
    Output:
        string: Returns the possessive form of the inputted noun
    """
    if word != "" and word[-1] == "s":
        return f"{word}'"
    else:
        return f"{word}'s"


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


def pretty_print_image_dict(image_dict: dict):
    """
    Description:
        Pretty-prints an image_dict, displaying indented image_id and metadata for each component
    Input:
        dict image_dict: image_dict in following format:
        {
            "default": "unit.png",
            "portrait": [
                {
                    "image_id": "unit_hat.png",
                    "size": 0.95,
                    "x_offset": 0,
                    "y_offset": 0,
                    "level": 1,
                    "green_screen": False
                }
                ...
            ],
            "left portrait": [
                ...
            ],
            ...
        }
    Output:
        None
    """
    printed_dict = deepcopy(image_dict)
    for key, portrait in printed_dict.items():
        print(f"{key}:")
        if type(portrait) != list:
            print(f"    {portrait}")
        else:
            for item in portrait:
                if "x_size" in item:
                    del item["x_size"]
                if "y_size" in item:
                    del item["y_size"]
                if "x_offset" in item:
                    del item["x_offset"]
                if "y_offset" in item:
                    del item["y_offset"]
                if "level" in item:
                    del item["level"]
                if "green_screen" in item:
                    del item["green_screen"]
                print(f"    {item}")


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
    return None


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
        Returns the approximate fahrenheit temperature for the inputted local temperature
    Input:
        int temperature: Temperature in game units
    Output:
        int: Returns temperature in fahrenheit
    """
    if temperature < 0:
        return temperature * 30 + 10
    elif temperature > 5:
        return temperature * 30 - 40
    else:
        return temperature * 20 + 15


def reverse_fahrenheit(temperature: int):
    """
    Description:
        Returns the approximate local temperature for the inputted fahrenheit temperature
    Input:
        int temperature: Temperature in fahrenheit
    Output:
        int: Returns temperature in game units
    """
    if temperature < fahrenheit(0):
        return (temperature - 10) / 30
    elif temperature > fahrenheit(5):
        return (temperature + 40) / 30
    else:
        return (temperature - 15) / 20


def extract_voice_set(
    masculine: bool, voice_set: str = None
) -> Tuple[str, Dict[str, List[str]]]:
    """
    Description:
        Gathers a set of voice lines for this minister, either using a saved voice set or a random new one
    Input:
        boolean masculine: Determines whether the voice set should be masculine or feminine
        string voice_set = None: If not None, uses this voice set instead of generating a new one
    Output:
        None
    """
    if not voice_set:
        if masculine:
            voice_set = f"masculine/{random.choice(os.listdir('sounds/voices/voice sets/masculine'))}"
        else:
            voice_set = f"feminine/{random.choice(os.listdir('sounds/voices/voice sets/feminine'))}"
    voice_lines = {
        "acknowledgement": [],
        "fired": [],
        "evidence": [],
        "hired": [],
    }
    folder_path = f"voices/voice sets/{voice_set}"
    for file_name in os.listdir("sounds/" + folder_path):
        for key in voice_lines:
            if file_name.startswith(key):
                file_name = file_name[:-4]  # cuts off last 4 characters - .ogg/.wav
                voice_lines[key].append(folder_path + "/" + file_name)
    return voice_set, voice_lines


def get_voice_line(unit, type):
    """
    Description:
        Attempts to retrieve one of this minister's voice lines of the inputted type
    Input:
        unit: Minister or officer to retrieve voice line for
        string type: Type of voice line to retrieve
    Output:
        string: Returns sound_manager file path of retrieved voice line
    """
    selected_line = None
    if len(unit.voice_lines[type]) > 0:
        selected_line = random.choice(unit.voice_lines[type])
        while len(unit.voice_lines[type]) > 1 and selected_line == unit.last_voice_line:
            selected_line = random.choice(unit.voice_lines[type])
    unit.last_voice_line = selected_line
    return selected_line


def add_dicts(*args: Dict[str, float]) -> Dict[str, float]:
    """
    Description:
        Adds any number of inputted dictionaries together, returning the result
    Input:
        *args: Any number of inputted dictionaries with numerical values
    Output:
        dict: Returns the sum of the inputted dictionaries
    """
    return_dict = {
        key: round(sum(dictionary.get(key, 0) for dictionary in args), 2)
        for dictionary in args
        for key in dictionary
    }
    return return_dict


def subtract_dicts(
    dict_1: Dict[str, float], dict_2: Dict[str, float]
) -> Dict[str, float]:
    """
    Description:
        Subtracts the second inputted dictionary from the first inputted dictionary, returning the result
    Input:
        dict dict_1: Dictionary with numerical values to subtract from
        dict dict_2: Dictionary with numerical values to subtract
    Output:
        dict: Returns the result of subtracting the second dictionary from the first dictionary
    """
    return_dict = {
        key: round(dict_1.get(key, 0) - dict_2.get(key, 0), 2) for key in dict_1
    }
    return return_dict
