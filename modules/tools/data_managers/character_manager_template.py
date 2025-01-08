# Manages character generation, minister/officer/worker backgrounds, names, appearance, ethnicity, and other personal details

import json
import random
import pygame
from typing import List, Dict, Tuple
from modules.util import csv_utility, utility, actor_utility
from modules.constants import constants, status, flags


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
        self.backgrounds_setup()
        self.appearances_setup()

    def backgrounds_setup(self) -> None:
        """
        Description:
            Reads in possible character backgrounds
        Input:
            None
        Output:
            None
        """
        with open("configuration/character_backgrounds.json") as active_file:
            self.backgrounds_dict: Dict[str, any] = json.load(active_file)
        self.outfit_types = list(
            set(
                [
                    details.get("outfit_type", constants.DEFAULT_MINISTER_OUTFIT_TYPE)
                    for details in self.backgrounds_dict.values()
                ]
            )
        )

    def generate_weighted_background(self) -> str:
        """
        Description:
            Generates a random background for a character, weighted by background frequencty
        Input:
            None
        Output:
            string: Returns background for a character
        """
        return random.choices(
            [background for background in self.backgrounds_dict],
            [details["weight"] for details in self.backgrounds_dict.values()],
            k=1,
        )[0]

    def get_status_number(self, background: str) -> int:
        """
        Description:
            Returns the social status of a background
        Input:
            string background: Background to check
        Output:
            int: Returns social status of background
        """
        return self.backgrounds_dict[background]["status"]

    def generate_skill_modifiers(self, background: str) -> Dict[str, int]:
        """
        Description:
            Generates random skill modifiers for a character based on their background
        Input:
            string background: Background to generate stat modifiers for
        Output:
            dictionary: Returns skill modifiers for a character, in the format
                {
                    "space": 0,
                    "industry": 1,
                    ...
                    "energy": -1,
                }
        """
        stat_modifiers = {}
        for skill in constants.skill_types:
            stat_modifiers[skill] = 0
        for skill, modifier in self.backgrounds_dict[background]["skills"].items():
            num_modifiers = abs(modifier)
            multiplier = 1
            if modifier != num_modifiers:
                multiplier = -1
            if skill == "random":  # If random, apply each point to a random skill
                for _ in range(num_modifiers):
                    stat_modifiers[
                        random.choice(constants.skill_types)
                    ] += multiplier * random.randrange(0, 2)
            else:  # If not random, apply 1 modifier for each of the background's point in the stat
                if not skill in constants.skill_types:
                    raise ValueError(
                        f"Within configuration/character_backgrounds.json[{background}], {skill} is not a valid skill type."
                    )
                stat_modifiers[skill] += sum(
                    [random.randrange(0, 2) * multiplier for _ in range(num_modifiers)]
                )
        return stat_modifiers

    def generate_corruption_modifier(self, background: str) -> int:
        """
        Description:
            Generates a random corruption modifier for a character based on their background
        Input:
            string background: Background to generate corruption modifier for
        Output:
            int: Returns corruption modifier for a character
        """
        modifier = self.backgrounds_dict[background].get("corruption", 0)
        num_modifiers = abs(modifier)
        multiplier = 1
        if modifier != num_modifiers:
            multiplier = -1
        return sum([multiplier * random.randrange(0, 2) for _ in range(num_modifiers)])

    def generate_prefix(self, background: str, masculine: bool) -> str:
        """
        Description:
            Generates a random prefix, like Dr., for a character based on their background
        Input:
            string background: Background to generate prefix for
            bool masculine: Whether the character is masculine or feminine
        Output:
            string: Returns prefix for a character
        """
        if random.random() < self.backgrounds_dict[background].get("prefix_chance", 0):
            return random.choice(self.backgrounds_dict[background]["prefixes"])
        elif masculine:
            return "Mr."
        else:
            return random.choice(["Ms.", "Mrs."])

    def appearances_setup(self) -> None:
        """
        Description:
            Reads in possible character appearances image files
        Input:
            None
        Output:
            None
        """
        with open("configuration/character_appearances.json") as active_file:
            appearances_dict: Dict[str, any] = json.load(active_file)
        self.portrait_section_types: List[str] = [
            constants.SKIN_PORTRAIT_SECTION,
            constants.MOUTH_PORTRAIT_SECTION,
            constants.NOSE_PORTRAIT_SECTION,
            constants.EYES_PORTRAITS_SECTION,
            constants.HAIR_PORTRAIT_SECTION,
            constants.OUTFIT_PORTRAIT_SECTION,
            constants.FACIAL_HAIR_PORTAIT_SECTION,
            "accessories",
            constants.HAT_PORTRAIT_SECTION,
            constants.FRAME_PORTRAIT_SECTION,
        ]
        self.skin_colors: Dict[str, List[Tuple[int, int, int]]] = {}
        for ethnicity, color_list in appearances_dict["skin_color"].items():
            self.skin_colors[ethnicity] = []
            for color in color_list:
                self.skin_colors[ethnicity].append(
                    pygame.image.load(
                        f"graphics/ministers/portraits/base_skin/colors/color{color}.png"
                    ).get_at((0, 0))[:3]
                )
                # Get RGB values of first pixel's color from each skin color image in the allowed [0, 1, ...] numbers for that ethnicity

        self.hair_colors: Dict[str, List[Tuple[int, int, int]]] = {}
        for ethnicity, color_list in appearances_dict["hair_color"].items():
            self.hair_colors[ethnicity] = []
            for color in color_list:
                self.hair_colors[ethnicity].append(
                    pygame.image.load(
                        f"graphics/ministers/portraits/hair/colors/color{color}.png"
                    ).get_at((0, 0))[:3]
                )

        self.hair_types: dict = {}
        for ethnicity, hair_type_dict in appearances_dict["hair_types"].items():
            self.hair_types[ethnicity] = hair_type_dict

        self.facial_hair_frequencies: Dict[str, float] = {}
        for ethnicity, frequency in appearances_dict["facial_hair"].items():
            self.facial_hair_frequencies[ethnicity] = frequency

        self.eye_colors: Dict[str, List[Tuple[int, int, int]]] = {}
        for ethnicity, color_list in appearances_dict["eye_color"].items():
            self.eye_colors[ethnicity] = []
            for color in color_list:
                self.eye_colors[ethnicity].append(
                    pygame.image.load(
                        f"graphics/ministers/portraits/eyes/colors/color{color}.png"
                    ).get_at((0, 0))[:3]
                )

        self.clothing_colors: List[
            Tuple[int, int, int]
        ] = actor_utility.extract_folder_colors(
            "ministers/portraits/outfit/suit_colors/"
        )
        self.accessory_colors: List[
            Tuple[int, int, int]
        ] = actor_utility.extract_folder_colors(
            "ministers/portraits/outfit/accessory_colors/"
        )

        self.skin_images: Dict[bool, List[str]] = {
            True: actor_utility.get_image_variants(
                "ministers/portraits/base_skin/default.png", "masculine"
            ),
            False: actor_utility.get_image_variants(
                "ministers/portraits/base_skin/default.png", "feminine"
            ),
        }

        self.hat_images: Dict[List[str]] = {}
        for outfit_type in self.outfit_types:
            self.hat_images[outfit_type] = actor_utility.get_image_variants(
                f"ministers/portraits/hat/{outfit_type}/default.png", outfit_type
            )

        self.hair_images: Dict[bool, Dict[str, List[str]]] = {True: {}, False: {}}
        for hair_type in self.hair_types["types"]:
            self.hair_images[True][hair_type] = actor_utility.get_image_variants(
                f"ministers/portraits/hair/masculine/default.png", hair_type
            )
            self.hair_images[False][hair_type] = actor_utility.get_image_variants(
                f"ministers/portraits/hair/feminine/default.png", hair_type
            )

        self.outfit_images: Dict[List[str]] = {}
        for outfit_type in self.outfit_types:
            self.outfit_images[outfit_type] = actor_utility.get_image_variants(
                f"ministers/portraits/outfit/{outfit_type}/default.png", outfit_type
            )

        self.facial_hair_images: List[str] = actor_utility.get_image_variants(
            f"ministers/portraits/facial_hair/default.png",
            constants.FACIAL_HAIR_PORTAIT_SECTION,
        )
        self.accessories_images: Dict[str, List[str]] = {
            constants.GLASSES_PORTRAIT_SECTION: actor_utility.get_image_variants(
                f"ministers/portraits/accessories/default.png",
                constants.GLASSES_PORTRAIT_SECTION,
            ),
        }
        self.mouth_images: List[str] = actor_utility.get_image_variants(
            f"ministers/portraits/mouth/default.png", constants.MOUTH_PORTRAIT_SECTION
        )
        self.exaggerated_mouth_images: List[str] = actor_utility.get_image_variants(
            f"ministers/portraits/mouth/default.png", "exaggerated"
        )
        self.nose_images: List[str] = actor_utility.get_image_variants(
            f"ministers/portraits/nose/default.png", constants.NOSE_PORTRAIT_SECTION
        )
        self.eyes_images: Dict[bool, List[str]] = {
            True: actor_utility.get_image_variants(
                "ministers/portraits/eyes/default.png", "masculine"
            ),
            False: actor_utility.get_image_variants(
                "ministers/portraits/eyes/default.png", "feminine"
            ),
        }
        self.portrait_images: List[str] = actor_utility.get_image_variants(
            f"ministers/portraits/frame/default.png", constants.FRAME_PORTRAIT_SECTION
        )

    def find_portrait_section(self, section: str, portrait_image_id: List[any]) -> int:
        """
        Description:
            Finds the index of a section of the inputted portrait, such as which image dict is the hair section
        Input:
            string section: Section to find
            list portrait_image_id: Portrait list image_id to search through
        Output:
            int: Returns index of section in list, if section present
        """
        for i, portrait_section in enumerate(portrait_image_id):
            if (
                portrait_section.get("metadata", {}).get("portrait_section", None)
                == section
            ):
                return i
        return None

    def generate_unit_portrait(
        self, unit, metadata: Dict[str, any] = None
    ) -> List[Dict[str, any]]:
        """
        Description:
            Generates a minister-style portrait for the inputted unit
                This makes a base portrait, while actor_utility's generate_unit_component_portrait edits the base portrait for display in the correct part of
                    the unit image
        Input:
            mob unit: Unit to generate portrait of
        Output:
            List[Dict[str, any]]: Returns list of image id's for each portrait section
        """
        minister_face = []
        if unit.get_permission(constants.PMOB_PERMISSION) and unit.any_permissions(
            constants.OFFICER_PERMISSION, constants.WORKER_PERMISSION
        ):
            minister_face = self.generate_appearance(
                unit, full_body=True, metadata=metadata
            )
            for part in minister_face:
                part["x_size"] = part.get("size", 1.0) * part.get("x_size", 1.0) * 0.47
                part["y_size"] = part.get("size", 1.0) * part.get("y_size", 1.0) * 0.47
                part["x_offset"] = part.get("x_offset", 0) + 0.01
                part["y_offset"] = part.get("y_offset", 0) + 0.342
                part["level"] = part.get("level", 1) - 5
                if part["metadata"]["portrait_section"] not in [
                    constants.FULL_BODY_PORTRAIT_SECTION,
                    constants.HAT_PORTRAIT_SECTION,
                    constants.BACKPACK_PORTRAIT_SECTION,
                ]:
                    part["detail_level"] = constants.BUNDLE_IMAGE_DETAIL_LEVEL / 2

            if unit.get_permission(constants.WORKER_PERMISSION):
                hidden_sections = [
                    constants.EYES_PORTRAITS_SECTION,
                ]
            else:
                hidden_sections = [
                    constants.EYES_PORTRAITS_SECTION,
                ]
            minister_face[
                self.find_portrait_section(
                    constants.HAT_PORTRAIT_SECTION, minister_face
                )
            ]["image_id"] = "misc/empty.png"

            for (
                section
            ) in (
                hidden_sections
            ):  # While officer, hide any unapplicable portrait sections but save for later
                section_index = self.find_portrait_section(section, minister_face)
                if section_index != None:
                    minister_face[section_index] = {
                        "image_id": "misc/empty.png",
                        "metadata": minister_face[section_index].get("metadata", {}),
                        "original_section": minister_face[section_index],
                    }

        return minister_face

    def generate_appearance(
        self, minister, full_body: bool = False, metadata: Dict[str, any] = None
    ) -> List[Dict[str, any]]:
        """
        Description:
            Generates random portrait sections for the inputted minister during initialization
        Input:
            minister minister: Minister to generate appearance of
        Output:
            List[image_id]: Returns list of image id's for each portrait section
        """
        portrait_sections = []

        if minister and hasattr(
            minister, "ethnicity"
        ):  # Choose a proportionally random ethnicity if minister does not have one yet or no minister inputted
            ethnicity = minister.ethnicity
        elif metadata.get("ethnicity", None):
            ethnicity = metadata["ethnicity"]
        else:
            ethnicity = self.generate_ethnicity()
        while ethnicity == "diaspora":
            ethnicity = random.choices(
                self.ethnic_groups, self.ethnic_group_weights, k=1
            )[0]

        if not full_body:
            if minister:
                background = minister.background
            else:
                background = self.generate_weighted_background()
            outfit_type = self.backgrounds_dict[background].get(
                "outfit_type", constants.DEFAULT_MINISTER_OUTFIT_TYPE
            )
        else:  # If generating for unit - maybe determine here to use unit-specific outfit?
            outfit_type = None

        if minister and hasattr(minister, "masculine"):
            masculine = minister.masculine
        elif metadata.get("masculine", None) != None:
            masculine = metadata["masculine"]
        else:
            masculine = random.choice([True, False])

        hair_color = random.choice(
            self.hair_colors[ethnicity.lower().replace(" ", "_")]
        )
        if (
            random.randrange(1, 7) == 1
        ):  # 1/6 chance of some shade of gray/white hair, regardless of ethnicity
            base = random.randrange(83, 229)
            hair_color = (base, base, base)

        hair_type = random.choices(
            list(self.hair_types[ethnicity.lower().replace(" ", "_")].keys()),
            self.hair_types[ethnicity.lower().replace(" ", "_")].values(),
            k=1,
        )[0]
        # Randomly choose hair type from ethnicity's weighted hair types

        has_facial_hair = (
            masculine
            and random.random()
            < self.facial_hair_frequencies[ethnicity.lower().replace(" ", "_")]
        )

        if not metadata:
            metadata = {}
        metadata.update(
            {
                "hair_color": hair_color,
                "hair_type": hair_type,
                "skin_color": random.choice(
                    self.skin_colors[ethnicity.lower().replace(" ", "_")]
                ),
                "eye_color": random.choice(
                    self.eye_colors[ethnicity.lower().replace(" ", "_")]
                ),
                "suit_colors": random.sample(self.clothing_colors, 2)
                + [random.choice(self.accessory_colors)],
                "has_hat": random.randrange(1, 7) >= 6,
                "has_facial_hair": has_facial_hair,
                "full_body": full_body,
                "ethnicity": ethnicity,
                "masculine": masculine,
                "outfit_type": outfit_type,
            }
        )

        self.generate_skin(portrait_sections, metadata)
        self.generate_hair(portrait_sections, metadata)
        self.generate_facial_hair(portrait_sections, metadata)
        self.generate_nose(portrait_sections, metadata)
        self.generate_mouth(portrait_sections, metadata)
        self.generate_eyes(portrait_sections, metadata)
        self.generate_accessories(portrait_sections, metadata)
        self.generate_portrait(portrait_sections, metadata)
        if full_body:
            self.generate_body(portrait_sections, metadata)
        else:
            self.generate_portrait(portrait_sections, metadata)
            self.generate_outfit(portrait_sections, metadata)

        return portrait_sections

    def generate_body(
        self, portrait_sections: List[any], metadata: Dict[str, any]
    ) -> None:
        """
        Description:
            Generates random full-body outfit for a character, adding it to the inputted list
        Input:
            image_id list: List of image id's for each portrait section
            dictionary metadata: Metadata for the character, allowing coordination between sections
        Output:
            None
        """
        portrait_sections.append(
            {
                "image_id": metadata["body_image"],
                "x_size": 2.2,
                "y_size": 2.18,
                "y_offset": -0.34,
                "x_offset": -0.015,
                "green_screen": metadata["skin_color"],
                "level": constants.DEFAULT_LEVEL,
                "metadata": {"portrait_section": constants.FULL_BODY_PORTRAIT_SECTION},
            }
        )

    def generate_outfit(
        self, portrait_sections: List[any], metadata: Dict[str, any]
    ) -> None:
        """
        Description:
            Generates random "bust" outfit for a character, adding it to the inputted list
        Input:
            image_id list: List of image id's for each portrait section
            dictionary metadata: Metadata for the character, allowing coordination between sections
        Output:
            None
        """
        portrait_sections.append(
            {
                "image_id": random.choice(self.outfit_images[metadata["outfit_type"]]),
                "green_screen": metadata["suit_colors"],
                "metadata": {"portrait_section": constants.OUTFIT_PORTRAIT_SECTION},
                "level": constants.HAIR_LEVEL + random.choice([-1, 1]),
            }
        )

    def generate_skin(
        self, portrait_sections: List[any], metadata: Dict[str, any]
    ) -> None:
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
                "image_id": random.choice(self.skin_images[metadata["masculine"]]),
                "green_screen": metadata["skin_color"],
                "level": constants.DEFAULT_LEVEL,
                "metadata": {"portrait_section": constants.SKIN_PORTRAIT_SECTION},
            }
        )

    def generate_hair(
        self, portrait_sections: List[any], metadata: Dict[str, any]
    ) -> None:
        """
        Description:
            Generates random hair for a character, adding it to the inputted list
        Input:
            image_id list: List of image id's for each portrait section
            dictionary metadata: Metadata for the character, allowing coordination between sections
        Output:
            None
        """
        if random.randrange(1, 11) != 0 or (not metadata["masculine"]):
            possible_hair_images = self.hair_images[metadata["masculine"]][
                metadata["hair_type"]
            ]
        else:
            possible_hair_images = ["misc/empty.png"]
        portrait_sections.append(
            {
                "image_id": random.choice(possible_hair_images),
                "green_screen": metadata["hair_color"],
                "level": constants.HAIR_LEVEL,
                "metadata": {"portrait_section": constants.HAIR_PORTRAIT_SECTION},
            }
        )

    def generate_facial_hair(
        self, portrait_sections: List[any], metadata: Dict[str, any]
    ) -> None:
        """
        Description:
            Generates random facial hair for a character, adding it to the inputted list
        Input:
            image_id list: List of image id's for each portrait section
            dictionary metadata: Metadata for the character, allowing coordination between sections
        Output:
            None
        """
        if metadata["has_facial_hair"]:
            portrait_sections.append(
                {
                    "image_id": random.choice(self.facial_hair_images),
                    "green_screen": metadata["hair_color"],
                    "metadata": {
                        "portrait_section": constants.FACIAL_HAIR_PORTAIT_SECTION
                    },
                    "level": constants.FACIAL_HAIR_LEVEL,
                }
            )

    def generate_accessories(
        self, portrait_sections: List[any], metadata: Dict[str, any]
    ) -> None:
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
                    "image_id": random.choice(
                        self.accessories_images[constants.GLASSES_PORTRAIT_SECTION]
                    ),
                    "green_screen": random.choice(self.clothing_colors),
                    "level": constants.GLASSES_LEVEL,
                    "metadata": {
                        "portrait_section": constants.GLASSES_PORTRAIT_SECTION
                    },
                }
            )
        if metadata["has_hat"]:
            hat_images = self.hat_images.get(
                metadata["outfit_type"],
                self.hat_images[constants.DEFAULT_MINISTER_OUTFIT_TYPE],
            )
        else:
            hat_images = ["misc/empty.png"]
        portrait_sections.append(
            {
                "image_id": random.choice(hat_images),
                "green_screen": metadata["suit_colors"],
                "level": constants.HAT_LEVEL,
                "detail_level": 1.0,
                "metadata": {"portrait_section": constants.HAT_PORTRAIT_SECTION},
            }
        )
        portrait_sections.append(
            {
                "image_id": "misc/empty.png",
                "x_size": 2.2,
                "y_size": 2.18,
                "y_offset": -0.34,
                "x_offset": -0.015,
                "level": constants.BACKPACK_LEVEL,
                "detail_level": 1.0,
                "metadata": {"portrait_section": constants.BACKPACK_PORTRAIT_SECTION},
            }
        )

    def generate_nose(
        self, portrait_sections: List[any], metadata: Dict[str, any]
    ) -> None:
        """
        Description:
            Generates a random nose for a character, adding it to the inputted list
        Input:
            image_id list: List of image id's for each portrait section
            dictionary metadata: Metadata for the character, allowing coordination between sections
        Output:
            None
        """
        portrait_sections.append(
            {
                "image_id": random.choice(self.nose_images),
                "detail_level": 1.0,
                "metadata": {"portrait_section": constants.NOSE_PORTRAIT_SECTION},
                "level": constants.DEFAULT_LEVEL,
            }
        )

    def generate_mouth(
        self, portrait_sections: List[any], metadata: Dict[str, any]
    ) -> None:
        """
        Description:
            Generates a random mouth for a character, adding it to the inputted list
        Input:
            image_id list: List of image id's for each portrait section
            dictionary metadata: Metadata for the character, allowing coordination between sections
        Output:
            None
        """
        if metadata["full_body"]:
            image_id = random.choice(self.exaggerated_mouth_images)
        else:
            image_id = random.choice(self.mouth_images)
        portrait_sections.append(
            {
                "image_id": image_id,
                "detail_level": 1.0,
                "metadata": {"portrait_section": constants.MOUTH_PORTRAIT_SECTION},
                "level": constants.DEFAULT_LEVEL,
            }
        )

    def generate_eyes(
        self, portrait_sections: List[any], metadata: Dict[str, any]
    ) -> None:
        """
        Description:
            Generates random eyes for a character, adding it to the inputted list
        Input:
            image_id list: List of image id's for each portrait section
            dictionary metadata: Metadata for the character, allowing coordination between sections
        Output:
            None
        """
        portrait_sections.append(
            {
                "image_id": random.choice(self.eyes_images[metadata["masculine"]]),
                "detail_level": 1.0,
                "green_screen": [metadata["eye_color"], metadata["hair_color"]],
                "metadata": {"portrait_section": constants.EYES_PORTRAITS_SECTION},
                "level": constants.EYES_LEVEL,
            }
        )

    def generate_portrait(
        self, portrait_sections: List[any], metadata: Dict[str, any]
    ) -> None:
        """
        Description:
            Generates a random background portrait for a character, adding it to the inputted list
        Input:
            image_id list: List of image id's for each portrait section
            dictionary metadata: Metadata for the character, allowing coordination between sections
        Output:
            None
        """
        if not metadata["full_body"]:
            portrait_sections.append(
                {
                    "image_id": random.choice(self.portrait_images),
                    "metadata": {"portrait_section": constants.FRAME_PORTRAIT_SECTION},
                    "level": constants.PORTRAIT_LEVEL,
                }
            )

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
                "ethnic_groups": ["Slavic", "Central Asian", "diaspora"],
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
