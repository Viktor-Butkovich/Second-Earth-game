# Contains .csv flavor text management singleton

from __future__ import annotations
import random
from modules.util import csv_utility


class flavor_text_manager:
    """
    Object that reads flavor text from .csv files and distributes it to other parts of the program when requested
    """

    def __init__(self):
        """
        Initializes this object
        """
        self.subject_dict = {
            "exploration": csv_utility.read_csv("text/explorer.csv"),
            "advertising_campaign": csv_utility.read_csv("text/advertising.csv"),
            "settlement_names": csv_utility.read_csv("text/settlement_names.csv"),
            "loading_screen_quotes": csv_utility.read_csv(
                "text/loading_screen_quotes.csv"
            ),
            "planet_names": csv_utility.read_csv("text/planet_names.csv"),
        }

    def generate_substituted_flavor_text(self, subject, replace_char, replace_with):
        """
        Description:
            Returns a random flavor text statement based on the inputted string, with all instances of replace_char replaced with replace_with
        Input:
            string subject: Represents the type of flavor text to return
        Output:
            string: Random flavor text statement of the inputted subject
        """
        base_text = random.choice(self.subject_dict[subject])
        return_text = ""
        for current_character in base_text:
            if current_character == replace_char:
                return_text += replace_with
            else:
                return_text += current_character
        return return_text

    def generate_substituted_indexed_flavor_text(
        self, subject, replace_char, replace_with
    ):
        """
        Description:
            Returns a random flavor text statement based on the inputted string, with all instances of replace_char replaced with replace_with
        Input:
            string subject: Represents the type of flavor text to return
        Output:
            string, int tuple: Random flavor text statement of the inputted subject, followed by the index in the flavor text list of the outputted flavor text
        """
        base_text = random.choice(self.subject_dict[subject])
        index = self.subject_dict[subject].index(base_text)
        return_text = ""
        for current_character in base_text:
            if current_character == replace_char:
                return_text += replace_with
            else:
                return_text += current_character
        return (return_text, index)

    def generate_flavor_text(self, subject):
        """
        Description:
            Returns a random flavor text statement based on the inputted string
        Input:
            string subject: Represents the type of flavor text to return
        Output:
            string: Random flavor text statement of the inputted subject
        """
        return random.choice(self.subject_dict[subject])
