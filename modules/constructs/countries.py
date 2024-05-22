# Contains functionality for different player countries

import pygame
from ..util import actor_utility
import modules.constants.constants as constants
import modules.constants.status as status


class country:
    """
    Country with associated flavor text, art, images, and abilities that can be selected to play as
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'name': string value - Name for this country, like 'France'
                'adjective': string value - Descriptor for this country used in descriptions and associated art and flavor text files, like 'french'
                'government_type_adjective': string value - Descriptor for institutions of the country, like 'Royal' or 'National' Geographical Society
                'religion': string value - Descriptor for the primary religion of this country, like 'protestant' or 'catholic'
                'allow_particles': boolean value - Whether ministers of this country are allowed to have name particles, like de Rouvier
                'aristocratic_particles': boolean value - Whether name particles for this country are reserved for aristocratic ministers
                'allow_double_last_names': boolean value - Whether ministers of this country are allowed to have hyphenated last names, like Dupont-Rouvier
                'background_set': string list value - Weighted list of backgrounds available to ministers of this country, like ['lowborn', 'lowborn', 'aristocrat']
                'country_effect': effect value - Effect that is applied when this country is selected and vice versa
        Output:
            None
        """
        self.actor_type = "country"
        status.country_list.append(self)
        self.tooltip_text = []
        self.name = input_dict["name"]
        self.adjective = input_dict["adjective"]
        self.government_type_adjective = input_dict["government_type_adjective"]
        self.religion = input_dict["religion"]
        self.allow_particles = input_dict["allow_particles"]
        self.aristocratic_particles = input_dict["aristocratic_particles"]
        self.allow_double_last_names = input_dict["allow_double_last_names"]
        self.image_id = "locations/europe/" + self.name + ".png"
        self.flag_image_id = "locations/flags/" + self.adjective + ".png"
        self.background_set = input_dict["background_set"]
        self.country_effect = input_dict["country_effect"]
        self.has_aristocracy = input_dict.get("has_aristocracy", True)
        self.colors = actor_utility.extract_folder_colors(
            "locations/country_colors/" + self.adjective + "/"
        )

    def select(self):
        """
        Description:
            Selects this country and modifies various game elements to match it, like setting the first name flavor text to this country's first name list
        Input:
            None
        Output:
            None
        """
        if status.current_country:
            status.current_country.country_effect.remove()
        status.current_country = self
        status.current_country_name = self.name

        constants.flavor_text_manager.set_flavor_text(
            "minister_first_names", "text/names/" + self.adjective + "_first_names.csv"
        )
        constants.flavor_text_manager.allow_particles = self.allow_particles
        if self.allow_particles:
            constants.flavor_text_manager.set_flavor_text(
                "minister_particles", "text/names/" + self.adjective + "_particles.csv"
            )
        constants.flavor_text_manager.aristocratic_particles = (
            self.aristocratic_particles
        )
        constants.flavor_text_manager.allow_double_last_names = (
            self.allow_double_last_names
        )
        constants.flavor_text_manager.set_flavor_text(
            "minister_last_names", "text/names/" + self.adjective + "_last_names.csv"
        )
        constants.flavor_text_manager.set_flavor_text(
            "settlement_names",
            "text/locations/" + self.adjective + "_settlement_names.csv",
        )
        constants.weighted_backgrounds = self.background_set
        for current_recruitment_button in status.recruitment_button_list:
            if (
                current_recruitment_button.recruitment_type
                in constants.country_specific_units
            ):
                current_recruitment_button.calibrate(self)
        for current_flag_icon in status.flag_icon_list:
            if type(current_flag_icon.image) == pygame.Surface:
                current_flag_icon.set_image(self.flag_image_id)
            else:
                current_flag_icon.image.set_image(self.flag_image_id)
        self.country_effect.apply()

    def deselect(self):
        """
        Description:
            Deselects this country and modifies various game elements to match this not being selected
        Input:
            None
        Output:
            None
        """
        status.current_country.country_effect.remove()
        status.current_country = None
        status.current_country_name = None

    def get_effect_descriptor(self):
        """
        Description:
            Returns a descriptor string for the effect of this country's effect
        Input:
            None
        Output:
            string: Returns a descriptor string for the effect of this country's effect
        """
        if self.country_effect.effect_type == "construction_plus_modifier":
            return "Bonus for construction"
        elif self.country_effect.effect_type == "conversion_plus_modifier":
            return "Bonus when converting natives"
        elif self.country_effect.effect_type == "combat_plus_modifier":
            return "Bonus when attacking natives"
        elif self.country_effect.effect_type == "slave_capture_plus_modifier":
            return "Bonus when capturing slaves"
        elif self.country_effect.effect_type == "no_slave_trade_penalty":
            return "No slave trade penalty"
        elif self.country_effect.effect_type == "combat_minus_modifier":
            return "Penalty when attacking natives"

    def update_tooltip(self):
        """
        Description:
            Sets this country's tooltip to what it should be whenever the player looks at the tooltip
        Input:
            None
        Output:
            None
        """
        self.tooltip_text = []
        self.tooltip_text.append("Name: " + self.name)


class hybrid_country(country):
    """
    Country that uses combination of multiple namesets, like Belgium
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object, the same keys as superclass except without allow_particles, aristocratic_particles,
                or allow_double_last_names
        Output:
            None
        """
        input_dict["allow_particles"] = False
        input_dict["aristocratic_particles"] = False
        input_dict["allow_double_last_names"] = False
        super().__init__(input_dict)

    def select(self):
        """
        Description:
            Selects this country and modifies various game elements to match it, like setting the first name flavor text to this country's first name list
        Input:
            None
        Output:
            None
        """
        if status.current_country:
            status.current_country.country_effect.remove()
        status.current_country = self
        status.current_country_name = self.name

        # specific text files are managed in flavor_text_manager for the time being, don't try to set to nonexistent belgium nameset
        constants.flavor_text_manager.allow_particles = self.allow_particles
        constants.flavor_text_manager.aristocratic_particles = (
            self.aristocratic_particles
        )
        constants.flavor_text_manager.allow_double_last_names = (
            self.allow_double_last_names
        )
        constants.flavor_text_manager.set_flavor_text(
            "settlement_names",
            "text/locations/" + self.adjective + "_settlement_names.csv",
        )
        constants.weighted_backgrounds = self.background_set
        for current_recruitment_button in status.recruitment_button_list:
            if (
                current_recruitment_button.recruitment_type
                in constants.country_specific_units
            ):
                current_recruitment_button.calibrate(self)
        for current_flag_icon in status.flag_icon_list:
            if type(current_flag_icon.image) == pygame.Surface:
                current_flag_icon.set_image(self.flag_image_id)
            else:
                current_flag_icon.image.set_image(self.flag_image_id)
        self.country_effect.apply()
