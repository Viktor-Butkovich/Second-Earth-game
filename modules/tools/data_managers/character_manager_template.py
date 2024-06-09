# Manages character generation, minister/officer/worker backgrounds, names, appearance, ethnicity, and other personal details

from typing import List, Dict
from ...util import csv_utility
import json
import random


class character_manager_template:
    """
    Object that controls character generation
    """

    def __init__(self) -> None:
        """
        Description:
            Initializes this object
        Input:
            None
        Output:
            None
        """
        with open("configuration/country_demographics.json") as active_file:
            country_dict = json.load(active_file)

        self.ethnic_groups: List[str] = []  # List of all ethnicities
        self.ethnic_group_weights: List[
            int
        ] = []  # List of weighted populations of each ethnicity
        self.countries_of_origin: List[str] = []  # List of all countries
        self.country_weights: List[
            int
        ] = []  # List of weighted populations to choose which country someone is from
        self.country_ethnicity_dict: Dict[
            str, Dict[str, Dict[str, list]]
        ] = (
            {}
        )  # Allows weighted selection of what ethnicity someone from a particular country is
        """
        In format:
        {
            "Russia": {
                "ethnic_groups": ["Eastern European", "Central Asian", "diaspora"],
                "ethnic_group_weights": [79, 20, 1]
            },
            "USA": ...
        }
        """
        ethnic_group_total_weights: Dict[str, float] = {}
        for group in country_dict:
            if group != "note":
                for country in country_dict[group]["populations"]:
                    self.countries_of_origin.append(country)
                    country_weighted_population = (
                        country_dict[group]["populations"][country]
                        * country_dict[group]["metadata"]["space_representation"]
                    )
                    self.country_weights.append(country_weighted_population)
                    # The chance of each country being selected for a character is proportional to the country's population and space representation
                    self.country_ethnicity_dict[country] = {
                        "ethnic_groups": [],
                        "ethnic_group_weights": [],
                    }

                    # The ethnicity of a character from a country is randomly selected from the country's demographic groups
                    if country in country_dict[group]["demographics"]:
                        if type(country_dict[group]["demographics"][country]) == str:
                            functional_country = country_dict[group]["demographics"][
                                country
                            ]  # Some countries will have equivalent demographics to another country
                        else:
                            functional_country = country
                    else:
                        functional_country = "default"  # Some countries will use the default demographics for their country group
                    for ethnicity in country_dict[group]["demographics"][
                        functional_country
                    ]:
                        ethnic_percentage = country_dict[group]["demographics"][
                            functional_country
                        ][ethnicity]
                        self.country_ethnicity_dict[country]["ethnic_groups"].append(
                            ethnicity
                        )
                        self.country_ethnicity_dict[country][
                            "ethnic_group_weights"
                        ].append(ethnic_percentage)
                        ethnic_group_total_weights[
                            ethnicity
                        ] = ethnic_group_total_weights.get(ethnicity, 0) + (
                            ethnic_percentage * country_weighted_population
                        )

        for ethnic_group in ethnic_group_total_weights:
            self.ethnic_groups.append(ethnic_group)
            self.ethnic_group_weights.append(
                round(ethnic_group_total_weights[ethnic_group])
            )

    def test(self) -> None:
        """
        Description:
            Prints 100 random names to the console
        Input:
            None
        Output:
            None
        """
        for i in range(100):
            country = self.generate_country()
            ethnicity = self.generate_ethnicity(country)
            print(ethnicity, "person from", country)
            print(
                self.get_name(ethnicity, last=False),
                self.get_name(ethnicity, last=True),
            )

    def generate_country(self) -> None:
        """
        Description:
            Generates a country of origin for a character
        Input:
            None
        Output:
            None
        """
        return random.choices(self.countries_of_origin, self.country_weights, k=1)[0]

    def generate_ethnicity(self, country_of_origin: str = None) -> str:
        """
        Description:
            Generates an ethnicity for a character based on their country of origin
        Input:
            string country_of_origin: The country of origin of the character
        Output:
            string: Returns ethnicity for a character
        """
        if not country_of_origin:
            country_of_origin = self.generate_country()
        choices = self.country_ethnicity_dict[country_of_origin]["ethnic_groups"]
        weights = self.country_ethnicity_dict[country_of_origin]["ethnic_group_weights"]
        return random.choices(choices, weights, k=1)[0]

    def generate_name(self, ethnicity: str = None) -> str:
        """
        Description:
            Generates a name for a character based on their ethnicity
        Input:
            string ethnicity: Ethnicity of the character
        Output:
            string: Returns name for a character
        """
        if not ethnicity:
            ethnicity = self.generate_ethnicity()
        if ethnicity == "disapora":
            ethnicity = random.choices(
                self.ethnic_groups, self.ethnic_group_weights, k=1
            )[0]

    def get_name(self, ethnicity: str, last: bool = False) -> str:
        """
        Description:
            Returns a random name for a character, using a file based on ethnicity and whether the name is a first or last name
        Input:
            string ethnicity: Ethnicity of the character
            bool last: Whether the name should be a last name
        Output:
            string: Returns name for a character
        """
        if last:
            file_name = (
                f"text/names/{ethnicity.lower().replace(' ', '_')}_last_names.csv"
            )
        else:
            file_name = (
                f"text/names/{ethnicity.lower().replace(' ', '_')}_first_names.csv"
            )
        return random.choice(csv_utility.read_csv(file_name))
