import random
from modules.util import csv_utility
from modules.constants import constants, status, flags


class flavor_text_manager_template:
    """
    Object that reads flavor text from .csv files and distributes it to other parts of the program when requested
    """

    def __init__(self):
        """
        Initializes this object
        """
        self.subject_dict = {}
        self.set_flavor_text("exploration", "text/explorer.csv")
        self.set_flavor_text("advertising_campaign", "text/advertising.csv")
        self.set_flavor_text("settlement_names", "text/settlement_names.csv")
        self.set_flavor_text("loading_screen_quotes", "text/loading_screen_quotes.csv")
        self.set_flavor_text("planet_names", "text/planet_names.csv")

    def set_flavor_text(self, topic, file):
        """
        Description:
            Sets this flavor text manager's list of flavor text for the inputted topic to the contents of the inputted csv file
        Input:
            string topic: Topic for the flavor text to set, like 'minister_first_names'
            string file: File to set flavor text to, like 'text/flavor_minister_first_names.csv'
        Output:
            None
        """
        flavor_text_list = []
        current_flavor_text = csv_utility.read_csv(file)
        for line in current_flavor_text:  # each line is a list
            flavor_text_list.append(line[0])
        self.subject_dict[topic] = flavor_text_list

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
