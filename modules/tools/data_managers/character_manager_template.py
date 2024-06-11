# Manages character generation, minister/officer/worker backgrounds, names, appearance, ethnicity, and other personal details

from typing import List, Dict
from ...util import csv_utility, utility, actor_utility
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
        self.demographics_setup()
        self.appearances_setup()

    def appearances_setup(self) -> None:
        """
        Description:
            Reads in possible character appearances image files
        Input:
            None
        Output:
            None
        """
        self.portrait_section_types = [
            "base_skin",
            "mouth",
            "nose",
            "eyes",
            "hair",
            "outfit",
            "facial_hair",
            "accessories",
            "hat",
            "portrait",
        ]
        self.hair_colors = actor_utility.extract_folder_colors(
            "ministers/portraits/hair/colors/"
        )
        self.skin_colors = actor_utility.extract_folder_colors(
            "ministers/portraits/base_skin/colors/"
        )
        self.clothing_colors = actor_utility.extract_folder_colors(
            "ministers/portraits/outfit/suit_colors/"
        )
        self.accessory_colors = actor_utility.extract_folder_colors(
            "ministers/portraits/outfit/accessory_colors/"
        )

        self.skin_images = actor_utility.get_image_variants(
            "ministers/portraits/base_skin/default.png", "base_skin"
        )
        self.hat_images = actor_utility.get_image_variants(
            "ministers/portraits/hat/default.png", "hat"
        )
        self.all_hair_images = actor_utility.get_image_variants(
            "ministers/portraits/hair/default.png", "hair"
        ) + actor_utility.get_image_variants(
            "ministers/portraits/hair/default.png", "no_hat"
        )
        self.hat_compatible_hair_images = actor_utility.get_image_variants(
            "ministers/portraits/hair/default.png", "hair"
        )
        self.outfit_images = actor_utility.get_image_variants(
            "ministers/portraits/outfit/default.png", "outfit"
        )
        self.facial_hair_images = actor_utility.get_image_variants(
            f"ministers/portraits/facial_hair/default.png", "facial_hair"
        )
        self.accessories_images = {
            "glasses": actor_utility.get_image_variants(
                f"ministers/portraits/accessories/default.png", "glasses"
            ),
        }
        self.mouth_images = actor_utility.get_image_variants(
            f"ministers/portraits/mouth/default.png", "mouth"
        )
        self.nose_images = actor_utility.get_image_variants(
            f"ministers/portraits/nose/default.png", "nose"
        )
        self.eyes_images = actor_utility.get_image_variants(
            f"ministers/portraits/eyes/default.png", "eyes"
        )
        self.portrait_images = actor_utility.get_image_variants(
            f"ministers/portraits/portrait/default.png", "portrait"
        )

    def generate_appearance(self, minister) -> None:
        """
        Description:
            Generates random portrait sections for the inputted minister during initialization
        Input:
            minister minister: Minister to generate appearance of
        Output:
            List[image_id]: Returns list of image id's for each portrait section
        """
        portrait_sections = []
        metadata = {
            "hair_color": random.choice(self.hair_colors),
            "skin_color": random.choice(self.skin_colors),
            "suit_colors": random.sample(self.clothing_colors, 2)
            + [random.choice(self.accessory_colors)],
            "has_hat": random.randrange(1, 7) >= 5,
        }

        self.generate_skin(portrait_sections, metadata)
        self.generate_outfit(portrait_sections, metadata)
        self.generate_hair(portrait_sections, metadata)
        self.generate_facial_hair(portrait_sections, metadata)
        self.generate_nose(portrait_sections, metadata)
        self.generate_mouth(portrait_sections, metadata)
        self.generate_eyes(portrait_sections, metadata)
        self.generate_accessories(portrait_sections, metadata)
        self.generate_portrait(portrait_sections, metadata)

        return portrait_sections

    def generate_outfit(self, portrait_sections, metadata) -> None:
        """
        Description:
            Generates random outfit for a character, adding it to the inputted list
        Input:
            image_id list: List of image id's for each portrait section
            dictionary metadata: Metadata for the character, allowing coordination between sections
        Output:
            None
        """
        portrait_sections.append(
            {
                "image_id": random.choice(self.outfit_images),
                "green_screen": metadata["suit_colors"],
            }
        )

    def generate_hair(self, portrait_sections, metadata) -> None:
        """
        Description:
            Generates random hair for a character, adding it to the inputted list
        Input:
            image_id list: List of image id's for each portrait section
            dictionary metadata: Metadata for the character, allowing coordination between sections
        Output:
            None
        """
        portrait_sections.append(
            {
                "image_id": random.choice(self.hair_images),
                "green_screen": metadata["hair_color"],
            }
        )

    def generate_skin(self, portrait_sections, metadata) -> None:
        """
        Description:
            Generates random skin for a character, adding it to the inputted list
        Input:
            image_id list: List of image id's for each portrait section
            dictionary metadata: Metadata for the character, allowing coordination between sections
        Output:
            None
        """
        portrait_sections.append(
            {
                "image_id": random.choice(self.skin_images),
                "green_screen": metadata["skin_color"],
            }
        )

    def generate_hair(self, portrait_sections, metadata) -> None:
        """
        Description:
            Generates random hair for a character, adding it to the inputted list
        Input:
            image_id list: List of image id's for each portrait section
            dictionary metadata: Metadata for the character, allowing coordination between sections
        Output:
            None
        """
        if random.randrange(1, 11) != 0:
            if metadata["has_hat"]:
                possible_hair_images = self.hat_compatible_hair_images
            else:
                possible_hair_images = self.all_hair_images
            portrait_sections.append(
                {
                    "image_id": random.choice(possible_hair_images),
                    "green_screen": metadata["hair_color"],
                    "layer": 3,
                }
            )

    def generate_facial_hair(self, portrait_sections, metadata) -> None:
        """
        Description:
            Generates random facial hair for a character, adding it to the inputted list
        Input:
            image_id list: List of image id's for each portrait section
            dictionary metadata: Metadata for the character, allowing coordination between sections
        Output:
            None
        """
        if random.randrange(1, 6) != 0:
            portrait_sections.append(
                {
                    "image_id": random.choice(self.facial_hair_images),
                    "green_screen": metadata["hair_color"],
                }
            )

    def generate_accessories(self, portrait_sections, metadata) -> None:
        """
        Description:
            Generates random accessories for a character, adding them to the inputted list
        Input:
            image_id list: List of image id's for each portrait section
            dictionary metadata: Metadata for the character, allowing coordination between sections
        Output:
            None
        """
        if random.randrange(1, 7) >= 4:
            portrait_sections.append(
                {
                    "image_id": random.choice(self.accessories_images["glasses"]),
                    "green_screen": random.choice(self.clothing_colors),
                    "layer": 2,
                }
            )
        if metadata["has_hat"]:
            portrait_sections.append(
                {
                    "image_id": random.choice(self.hat_images),
                    "green_screen": metadata["suit_colors"],
                    "layer": 4,
                }
            )

    def generate_nose(self, portrait_sections, metadata) -> None:
        """
        Description:
            Generates a random nose for a character, adding it to the inputted list
        Input:
            image_id list: List of image id's for each portrait section
            dictionary metadata: Metadata for the character, allowing coordination between sections
        Output:
            None
        """
        portrait_sections.append(random.choice(self.nose_images))

    def generate_mouth(self, portrait_sections, metadata) -> None:
        """
        Description:
            Generates a random mouth for a character, adding it to the inputted list
        Input:
            image_id list: List of image id's for each portrait section
            dictionary metadata: Metadata for the character, allowing coordination between sections
        Output:
            None
        """
        portrait_sections.append(random.choice(self.mouth_images))

    def generate_eyes(self, portrait_sections, metadata) -> None:
        """
        Description:
            Generates random eyes for a character, adding it to the inputted list
        Input:
            image_id list: List of image id's for each portrait section
            dictionary metadata: Metadata for the character, allowing coordination between sections
        Output:
            None
        """
        portrait_sections.append(random.choice(self.eyes_images))

    def generate_portrait(self, portrait_sections, metadata) -> None:
        """
        Description:
            Generates a random background portrait for a character, adding it to the inputted list
        Input:
            image_id list: List of image id's for each portrait section
            dictionary metadata: Metadata for the character, allowing coordination between sections
        Output:
            None
        """
        portrait_sections.append(random.choice(self.portrait_images))

    def demographics_setup(self) -> None:
        """
        Description:
            Sets up character generation demographics
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
        self.countries_of_origin: List[
            str
        ] = []  # List of all non-miscellaneous countries
        self.miscellaneous_countries: Dict[
            str, List[str]
        ] = (
            {}
        )  # Countries with 1-5 million population, used for Misc. country of origin
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
            for country in country_dict[group]["populations"]:
                if country.startswith("Misc."):
                    self.miscellaneous_countries[country] = country_dict[group][
                        "miscellaneous"
                    ]
                self.countries_of_origin.append(country)
                country_weighted_population = (
                    country_dict[group]["populations"][country]
                    * country_dict[group]["metadata"]["space_representation"]
                )
                self.country_weights.append(country_weighted_population)
                # The chance of each country being selected for a character is proportional to the country's population and space representation

                if country.startswith("Misc."):
                    cycled_countries = self.miscellaneous_countries[country]
                else:
                    cycled_countries = [country]
                for current_country in cycled_countries:
                    self.country_ethnicity_dict[current_country] = {
                        "ethnic_groups": [],
                        "ethnic_group_weights": [],
                    }
                    # The ethnicity of a character from a country is randomly selected from the country's demographic groups
                    if current_country in country_dict[group]["demographics"]:
                        if (
                            type(country_dict[group]["demographics"][current_country])
                            == str
                        ):
                            functional_country = country_dict[group]["demographics"][
                                current_country
                            ]  # Some countries will have equivalent demographics to another country
                        else:
                            functional_country = current_country
                    else:
                        functional_country = "default"  # Some countries will use the default demographics for their country group
                    for ethnicity in country_dict[group]["demographics"][
                        functional_country
                    ]:
                        ethnic_percentage = country_dict[group]["demographics"][
                            functional_country
                        ][ethnicity]
                        self.country_ethnicity_dict[current_country][
                            "ethnic_groups"
                        ].append(ethnicity)
                        self.country_ethnicity_dict[current_country][
                            "ethnic_group_weights"
                        ].append(ethnic_percentage)
                        if (
                            current_country == cycled_countries[0]
                        ):  # Don't repeat counts for misc. countries
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

    def demographics_test(self) -> None:
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
            masculine = random.choice([True, False])
            print(
                f"{self.generate_name(ethnicity=ethnicity, masculine=masculine)}, {utility.generate_article(ethnicity)} {ethnicity} person from {country}"
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
        country = random.choices(self.countries_of_origin, self.country_weights, k=1)[0]
        if country.startswith(
            "Misc."
        ):  # If selected "Misc." population, choose a miscellaneous country, like Luxembourg for "Misc. Western"
            country = random.choice(self.miscellaneous_countries[country])
        return country

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

    def generate_name(self, ethnicity: str = None, masculine: bool = False) -> str:
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
        while ethnicity == "diaspora":
            ethnicity = random.choices(
                self.ethnic_groups, self.ethnic_group_weights, k=1
            )[0]
        return (
            self.get_name(ethnicity, last=False, masculine=masculine),
            self.get_name(ethnicity, last=True),
        )

    def get_name(
        self, ethnicity: str, last: bool = False, masculine: bool = False
    ) -> str:
        """
        Description:
            Returns a random name for a character, using a file based on ethnicity and whether the name is a first or last name
        Input:
            string ethnicity: Ethnicity of the character
            bool last: Whether the name should be a last name
            bool masculine: Whether the name should be masculine or feminine, if a first name
        Output:
            string: Returns name for a character
        """
        if last:
            file_name = (
                f"text/names/{ethnicity.lower().replace(' ', '_')}_last_names.csv"
            )
        else:
            if masculine:
                file_name = f"text/names/{ethnicity.lower().replace(' ', '_')}_first_names_male.csv"
            else:
                file_name = f"text/names/{ethnicity.lower().replace(' ', '_')}_first_names_female.csv"
        return random.choice(csv_utility.read_csv(file_name))[0]
