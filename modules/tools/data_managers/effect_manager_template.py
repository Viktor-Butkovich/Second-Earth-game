import json
from .. import effects


class effect_manager_template:
    """
    Object that controls global effects
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
        self.possible_effects = []
        self.active_effects = []
        file = open("configuration/release_config.json")

        # returns JSON object as a dictionary
        debug_config = json.load(file)
        # Iterating through the json list
        for current_effect in debug_config["effects"]:
            self.create_effect("DEBUG_" + current_effect, current_effect)
        file.close()

        try:  # for testing/development, use active effects of local version of config file that is not uploaded to GitHub
            file = open("configuration/dev_config.json")
            active_effects_config = json.load(file)
            file.close()
        except:
            active_effects_config = debug_config
        for current_effect in active_effects_config["active_effects"]:
            if self.effect_exists(current_effect):
                self.set_effect(current_effect, True)
            else:
                print("Invalid effect: " + current_effect)

    def create_effect(self, effect_id, effect_type) -> effects.effect:
        """
        Description:
            Creates an effect with the inputted id and type
        Input:
            string effect_id: Name of effect, like 'zoology_completion_effect'
            string effect_type: Type of effect produced by this effect, like 'hunting_plus_modifier'
        Output:
            effect: Returns the created effect
        """
        return effects.effect(effect_id, effect_type, self)

    def __str__(self):
        """
        Description:
            Returns text for a description of this object when printed
        Input:
            None
        Output:
            string: Returns text to print
        """
        text = "Active effects: "
        for current_effect in self.active_effects:
            text += "\n    " + current_effect.__str__()
        return text

    def effect_active(self, effect_type):
        """
        Description:
            Finds and returns whether any effect of the inputted type is active
        Input:
            string effect_type: Type of effect to check for
        Output:
            boolean: Returns whether any effect of the inputted type is active
        """
        for current_effect in self.active_effects:
            if current_effect.effect_type == effect_type:
                return True
        return False

    def set_effect(self, effect_type, new_status):
        """
        Description:
            Finds activates/deactivates all effects of the inputted type, based on the inputted status
        Input:
            string effect_type: Type of effect to check for
            string new_status: New activated/deactivated status for effects
        Output:
            None
        """
        for current_effect in self.possible_effects:
            if current_effect.effect_type == effect_type:
                if new_status == True:
                    current_effect.apply()
                else:
                    current_effect.remove()

    def effect_exists(self, effect_type):
        """
        Description:
            Checks whether any effects of the inputted type exist
        Input:
            string effect_type: Type of effect to check for
        Output:
            boolean: Returns whether any effects of the inputted type exist
        """
        for current_effect in self.possible_effects:
            if current_effect.effect_type == effect_type:
                return True
        return False
