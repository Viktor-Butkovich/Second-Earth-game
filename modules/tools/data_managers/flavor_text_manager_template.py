import random
import modules.constants.constants as constants
import modules.constants.status as status
from ...util import csv_utility


class flavor_text_manager_template:
    """
    Object that reads flavor text from .csv files and distributes it to other parts of the program when requested
    """

    def __init__(self):
        """
        Description:
            Initializes this object
        Input:
            None
        Output:
            None
        """
        self.subject_dict = {}
        self.set_flavor_text("exploration", "text/explorer.csv")
        self.set_flavor_text("advertising_campaign", "text/advertising.csv")
        self.set_flavor_text("minister_first_names", "text/default.csv")
        self.set_flavor_text("minister_particles", "text/default.csv")
        self.set_flavor_text("minister_last_names", "text/default.csv")
        self.set_flavor_text("settlement_names", "text/default.csv")
        self.allow_particles = False

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

    def generate_minister_name(self, background):
        """
        Description:
            Generates and returns a random combination of minister first and last names
        Input:
            None
        Output:
            string tuple: Returns a tuple containing a random first name and random last name
        """

        first_name = self.generate_flavor_text("minister_first_names")
        if background in ["royal heir", "aristocrat"]:
            while not first_name in constants.titles:
                first_name = self.generate_flavor_text("minister_first_names")
                if background != "royal heir":
                    while first_name in [
                        "Prince",
                        "Infante",
                        "Reichsfürst",
                        "Principe",
                    ]:  # only allow prince titles for royal heir
                        first_name = self.generate_flavor_text("minister_first_names")
        else:
            while first_name in constants.titles:
                first_name = self.generate_flavor_text("minister_first_names")

        last_name = self.generate_flavor_text("minister_last_names")

        if self.allow_particles:
            if self.aristocratic_particles:
                if (
                    background in ["royal heir", "aristocrat"]
                    and self.aristocratic_particles
                ):
                    last_name = (
                        self.generate_flavor_text("minister_particles") + last_name
                    )
            elif random.randrange(1, 7) >= 4:
                last_name = self.generate_flavor_text("minister_particles") + last_name

        return (first_name, last_name)
