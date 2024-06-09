# Contains functionality for ministers

import random, os
from typing import List, Tuple, Dict
from ..util import (
    utility,
    minister_utility,
    scaling,
)
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags


class minister:
    """
    Person that can be appointed to control a certain part of the company and will affect actions based on how skilled and corrupt they are
    """

    def __init__(self, from_save, input_dict):
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'first_name': string value - Required if from save, this minister's first name
                'last_name': string value - Required if from save, this minister's last name
                'current_position': string value - Office that this minister is currently occupying, or 'none' if no office occupied
                'background': string value - Career background of minister, determines social status and skills
                'personal savings': double value - How much non-stolen money this minister has based on their social status
                'general_skill': int value - Value from 1 to 3 that changes what is added to or subtracted from dice rolls
                'specific_skills': dictionary value - String keys corresponding to int values to record skill values for each minister office
                'interests': string list value - List of strings describing the skill categories this minister is interested in
                'corruption': int value - Measure of how corrupt a minister is, with 6 having a 1/2 chance to steal, 5 having 1/3 chance, etc.
                'image_id': string value - File path to the image used by this minister
                'stolen_money': double value - Amount of money this minister has stolen or taken in bribes
                'just_removed': boolean value - Whether this minister was just removed from office and will be fired at the end of the turn
                'corruption_evidence': int value - Number of pieces of evidence that can be used against this minister in a trial, includes fabricated evidence
                'fabricated_evidence': int value - Number of temporary fabricated pieces of evidence that can be used against this minister in a trial this turn
        Output:
            None
        """
        self.initializing = True
        self.actor_type = "minister"  # used for actor display labels and images
        status.minister_list.append(self)
        self.tooltip_text: List[str] = []
        self.portrait_section_types: List[str] = [
            "base_skin",
            "mouth",
            "nose",
            "eyes",
            "hair",
            "outfit",
            "facial_hair",
            "hat",
            "portrait",
        ]
        self.portrait_sections: Dict = {}
        status_number_dict: Dict[int, str] = {
            1: "low",
            2: "moderate",
            3: "high",
            4: "very high",
        }
        if from_save:
            self.first_name: str = input_dict["first_name"]
            self.last_name: str = input_dict["last_name"]
            self.name: str = self.first_name + " " + self.last_name
            self.current_position: str = input_dict["current_position"]
            self.background: str = input_dict["background"]
            self.status_number: int = constants.background_status_dict[self.background]
            self.status: str = status_number_dict[self.status_number]
            self.personal_savings: float = input_dict["personal_savings"]
            self.general_skill: int = input_dict["general_skill"]
            self.specific_skills: Dict[str, int] = input_dict["specific_skills"]
            self.apparent_skills: Dict[str, int] = input_dict["apparent_skills"]
            self.apparent_skill_descriptions: Dict[str, str] = input_dict[
                "apparent_skill_descriptions"
            ]
            self.apparent_corruption: int = input_dict["apparent_corruption"]
            self.apparent_corruption_description: str = input_dict[
                "apparent_corruption_description"
            ]
            self.interests: Tuple[str, str] = input_dict["interests"]
            self.corruption: int = input_dict["corruption"]
            self.corruption_threshold: int = 10 - self.corruption
            self.portrait_sections = input_dict["portrait_sections"]
            self.update_image_bundle()
            self.stolen_money: float = input_dict["stolen_money"]
            self.undetected_corruption_events: List[Tuple[float, str]] = input_dict[
                "undetected_corruption_events"
            ]
            self.corruption_evidence: int = input_dict["corruption_evidence"]
            self.fabricated_evidence: int = input_dict["fabricated_evidence"]
            self.just_removed: bool = input_dict["just_removed"]
            self.voice_set = input_dict["voice_set"]
            self.voice_setup(from_save)
            if self.current_position != "none":
                self.appoint(self.current_position)
            else:
                status.available_minister_list.append(self)
        else:
            self.background: str = random.choice(constants.weighted_backgrounds)
            self.first_name: str
            self.last_name: str
            (
                self.first_name,
                self.last_name,
            ) = constants.character_manager.generate_name()
            self.name = self.first_name + " " + self.last_name
            self.status_number: int = constants.background_status_dict[self.background]
            self.status: str = status_number_dict[self.status_number]
            self.personal_savings: float = 5 ** (
                self.status_number - 1
            ) + random.randrange(
                0, 6
            )  # 1-6 for lowborn, 5-10 for middle, 25-30 for high, 125-130 for very high
            self.current_position: str = "none"
            self.skill_setup()
            self.voice_setup()
            self.interests_setup()
            self.corruption_setup()
            status.available_minister_list.append(self)
            self.portrait_sections = constants.character_manager.generate_appearance(
                self
            )
            self.update_image_bundle()
            self.stolen_money: int = 0
            self.undetected_corruption_events: List[Tuple[float, str]] = []
            self.corruption_evidence: int = 0
            self.fabricated_evidence: int = 0
            self.just_removed: bool = False
        minister_utility.update_available_minister_display()
        self.stolen_already: bool = False
        self.update_tooltip()
        self.initializing: bool = False

    def get_f_lname(self):
        """
        Description:
            Returns this minister's name in the form [first initial] [last name] - uses full aristocratic titles, if applicable
        Input:
            None
        Output:
            str: Returns this minister's name in the form [first initial] [last name]
        """
        if self.first_name in constants.titles:
            return self.name
        else:
            return self.first_name[0] + ". " + self.last_name

    def update_tooltip(self):
        """
        Description:
            Sets this minister's tooltip to what it should be whenever the player looks at the tooltip. By default, sets tooltip to this minister's name and current office
        Input:
            None
        Output:
            None
        """
        self.tooltip_text = []
        if not self.current_position == "none":
            keyword = constants.minister_type_dict[
                self.current_position
            ]  # type, like military
            self.tooltip_text.append(
                "This is " + self.name + ", your " + self.current_position + "."
            )
        else:
            self.tooltip_text.append(
                "This is " + self.name + ", an available minister candidate."
            )
        self.tooltip_text.append("Background: " + self.background)
        self.tooltip_text.append("Social status: " + self.status)
        self.tooltip_text.append(
            "Interests: " + self.interests[0] + " and " + self.interests[1]
        )

        if self.apparent_corruption_description != "unknown":
            self.tooltip_text.append("Loyalty: " + self.apparent_corruption_description)

        if self.current_position == "none":
            displayed_skill = self.get_max_apparent_skill()
        else:
            displayed_skill = self.current_position

        if displayed_skill != "unknown":
            displayed_skill_name = constants.minister_type_dict[
                displayed_skill
            ]  # like General to military]
            if self.apparent_skill_descriptions[displayed_skill] != "unknown":
                if self.current_position == "none":
                    message = (
                        "Highest ability: "
                        + self.apparent_skill_descriptions[displayed_skill]
                        + " ("
                        + displayed_skill_name
                        + ")"
                    )
                else:
                    message = (
                        displayed_skill_name.capitalize()
                        + " ability: "
                        + self.apparent_skill_descriptions[displayed_skill]
                    )
                self.tooltip_text.append(message)

        rank = 0
        for skill_value in range(6, 0, -1):  # iterates backwards from 6 to 1
            for skill_type in self.apparent_skills:
                if self.apparent_skills[skill_type] == skill_value:
                    rank += 1
                    skill_name = constants.minister_type_dict[
                        skill_type
                    ]  # like General to military
                    self.tooltip_text.append(
                        f"    {rank}. {skill_name.capitalize()}: {self.apparent_skill_descriptions[skill_type]}"
                    )

        self.tooltip_text.append("Evidence: " + str(self.corruption_evidence))
        if self.just_removed and self.current_position == "none":
            self.tooltip_text.append(
                "This minister was just removed from office and expects to be reappointed to an office by the end of the turn."
            )
            self.tooltip_text.append(
                "If not reappointed by the end of the turn, he will be permanently fired, incurring a large public opinion penalty."
            )

    def generate_icon_input_dicts(self, alignment="left"):
        """
        Description:
            Generates the input dicts for this minister's face and position background to be attached to a notification
        Input:
            None
        Output:
            dictionary list: Returns list of input dicts for this minister's face and position background
        """
        minister_position_icon_dict = {
            "coordinates": (0, 0),
            "width": scaling.scale_width(100),
            "height": scaling.scale_height(100),
            "modes": ["strategic", "ministers", "earth", "trial"],
            "attached_minister": self,
            "minister_image_type": "position",
            "init_type": "dice roll minister image",
            "minister_message_image": True,
            "member_config": {
                "order_overlap": True,
                "second_dimension_alignment": alignment,
                "centered": True,
            },
        }

        minister_portrait_icon_dict = minister_position_icon_dict.copy()
        minister_portrait_icon_dict["member_config"] = {
            "second_dimension_alignment": "leftmost",
            "centered": True,
        }
        minister_portrait_icon_dict["minister_image_type"] = "portrait"
        return [minister_position_icon_dict, minister_portrait_icon_dict]

    def display_message(self, text, audio="none", transfer=False):
        """
        Description:
            Displays a notification message from this minister with an attached portrait
        Input:
            string text: Message to display in notification
            string audio: Any audio to play with notification
            boolean transfer: Whether the minister icon should carry on to future notifications - should set to True for actions, False for misc. messages
        Output:
            None
        """
        constants.notification_manager.display_notification(
            {
                "message": text + "Click to remove this notification. /n /n",
                "notification_type": "action",
                "audio": audio,
                "attached_minister": self,
                "attached_interface_elements": self.generate_icon_input_dicts(
                    alignment="left"
                ),
                "transfer_interface_elements": transfer,
            }
        )

    def can_pay(self, value):
        """
        Description:
            Checks if this minister has enough money to pay the inputted amount
        Input:
            double value: Amount of money being paid
        Output:
            boolean: Returns whether this minister is able to pay the inputted amount
        """
        return self.personal_savings + self.stolen_money >= value

    def pay(self, target, value):
        """
        Description:
            Pays the inputted amount of money to the inputted minister, taking money from savings if needed. Assumes that can_pay was True for the value
        Input:
            minister target: Minister being paid
            double value: Amount of money being paid
        Output:
            None
        """
        self.stolen_money -= value
        if self.stolen_money < 0:
            self.personal_savings += self.stolen_money
            self.stolen_money = 0
        target.stolen_money += value

    def attempt_prosecutor_detection(self, value=0, theft_type="none"):
        """
        Description:
            Resolves the outcome of the prosecutor attempting to detect a corrupt action, regardless of if money was immediately stolen
        Input:
            double value = 0: Amount of money stolen
            string theft_type = 'none': Type of theft, used in prosecutor report description
        Output:
            bool: Returns whether the prosecutor detected the theft
        """
        prosecutor = status.current_ministers["Prosecutor"]
        if prosecutor != "none":
            if constants.effect_manager.effect_active("show_minister_stealing"):
                print(
                    f"{self.current_position} {self.name} stole {value} money from {constants.transaction_descriptions[theft_type]}."
                )
            difficulty = self.no_corruption_roll(6, "minister_stealing")
            result = prosecutor.no_corruption_roll(6, "minister_stealing_detection")
            if (
                prosecutor != self and result >= difficulty
            ):  # caught by prosecutor if prosecutor succeeds skill contest roll
                required_bribe_amount = max(value / 2, 5)
                if prosecutor.check_corruption() and self.can_pay(
                    required_bribe_amount
                ):  # if prosecutor takes bribe, split money
                    self.pay(prosecutor, required_bribe_amount)
                    if constants.effect_manager.effect_active("show_minister_stealing"):
                        print(
                            "The theft was caught by the prosecutor, who accepted a bribe to not create evidence."
                        )
                        print(
                            f"{prosecutor.current_position} {prosecutor.name} has now stolen a total of {prosecutor.stolen_money} money."
                        )
                else:  # if prosecutor refuses bribe, still keep money but create evidence
                    self.corruption_evidence += 1
                    evidence_message = ""
                    evidence_message += f"Prosecutor {prosecutor.name} suspects that {self.current_position} {self.name} just engaged in corrupt activity relating to "
                    evidence_message += f"{constants.transaction_descriptions[theft_type]} and has filed a piece of evidence against him. /n /n"
                    evidence_message += f"There are now {self.corruption_evidence} piece{utility.generate_plural(self.corruption_evidence)} of evidence against {self.name}. /n /n"
                    evidence_message += "Each piece of evidence can help in a trial to remove a corrupt minister from office. /n /n"
                    prosecutor.display_message(
                        evidence_message,
                        prosecutor.get_voice_line("evidence"),
                        transfer=False,
                    )  # Don't need to transfer since evidence is last step in action
                    if constants.effect_manager.effect_active("show_minister_stealing"):
                        print(
                            "The theft was caught by the prosecutor, who chose to create evidence."
                        )
                    return True
            else:
                if (
                    constants.effect_manager.effect_active("show_minister_stealing")
                    and prosecutor != self
                ):
                    print("The theft was not caught by the prosecutor.")
        return False

    def steal_money(self, value, theft_type="none", allow_prosecutor_detection=True):
        """
        Description:
            Steals money from a company action, giving this minister money but causing a chance of prosecutor detection
        Input:
            double value: Amount of money stolen
            string theft_type = 'none': Type of theft, used in prosecutor report description
        Output:
            None
        """
        self.stolen_money += value
        detected: bool = False
        if allow_prosecutor_detection:
            detected = self.attempt_prosecutor_detection(
                value=value, theft_type=theft_type
            )

        if not detected:
            self.undetected_corruption_events.append((value, theft_type))

        if constants.effect_manager.effect_active("show_minister_stealing"):
            print(
                f"{self.current_position} {self.name} has now stolen a total of {self.stolen_money} money."
            )

        if value > 0:
            constants.evil_tracker.change(1)

    def to_save_dict(self):
        """
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                'first_name': string value - This minister's first name
                'last_name': string value - This minister's last name
                'current_position': string value - Office that this minister is currently occupying, or 'none' if no office occupied
                'background': string value - Career background of minister, determines social status and skills
                'personal savings': double value - How much non-stolen money this minister has based on their social status
                'general_skill': int value - Value from 1 to 3 that changes what is added to or subtracted from dice rolls
                'specific_skills': dictionary value - String keys corresponding to int values to record skill values for each minister office
                'apparent_skills': dictionary value - String keys corresponding to 'unknown'/int values for estimate of minister skill, based on prosecutor and rumors
                'apparent_skill_descriptions': dictionary value - String keys corresponding to string description values for estimate of minister skill
                'apparent_corruption': int/string value - Value from 1 to 6 or 'unknown' corresponding to estimate of minister corruption
                'apparent_corruption_description': string value - String description value for estimate of minister corruption
                'interests': string list value - List of strings describing the skill categories this minister is interested in
                'corruption': int value - Measure of how corrupt a minister is, with 6 having a 1/2 chance to steal, 5 having 1/3 chance, etc.
                'undetected_corruption_events': tuple list value - List of tuples containing records of past stealing amounts and types
                'stolen_money': double value - Amount of money this minister has stolen or taken in bribes
                'just_removed': boolean value - Whether this minister was just removed from office and will be fired at the end of the turn
                'corruption_evidence': int value - Number of pieces of evidence that can be used against this minister in a trial, includes fabricated evidence
                'fabricated_evidence': int value - Number of temporary fabricated pieces of evidence that can be used against this minister in a trial this turn
                'portrait_sections': string list value - List of image file paths for each of this minister's portrait sections
                'voice_set': string value - Name of voice set assigned to this minister
        """
        save_dict = {}
        save_dict["first_name"] = self.first_name
        save_dict["last_name"] = self.last_name
        save_dict["current_position"] = self.current_position
        save_dict["general_skill"] = self.general_skill
        save_dict["specific_skills"] = self.specific_skills
        save_dict["apparent_skills"] = self.apparent_skills
        save_dict["apparent_skill_descriptions"] = self.apparent_skill_descriptions
        save_dict["apparent_corruption"] = self.apparent_corruption
        save_dict[
            "apparent_corruption_description"
        ] = self.apparent_corruption_description
        save_dict["interests"] = self.interests
        save_dict["corruption"] = self.corruption
        save_dict["undetected_corruption_events"] = self.undetected_corruption_events
        save_dict["stolen_money"] = self.stolen_money
        save_dict["corruption_evidence"] = self.corruption_evidence
        save_dict["fabricated_evidence"] = self.fabricated_evidence
        save_dict["just_removed"] = self.just_removed
        save_dict["background"] = self.background
        save_dict["personal_savings"] = self.personal_savings
        save_dict["portrait_sections"] = self.portrait_sections
        save_dict["voice_set"] = self.voice_set
        return save_dict

    def get_image_id_list(self, override_values={}):
        """
        Description:
            Generates and returns a list this actor's image file paths and dictionaries that can be passed to any image object to display those images together in a particular order and
                orientation
        Input:
            None
        Output:
            list: Returns list of string image file paths, possibly combined with string key dictionaries with extra information for offset images
        """
        image_id_list = []
        for portrait_section_type in self.portrait_section_types:
            image_id_list.append(self.portrait_sections[portrait_section_type])
        return image_id_list

    def update_image_bundle(self):
        self.image_id = self.get_image_id_list()

    def roll(
        self,
        num_sides,
        min_success,
        max_crit_fail,
        value,
        roll_type,
        predetermined_corruption=False,
    ):
        """
        Description:
            Rolls and returns the result of a die with the inputted number of sides, modifying the result based on skill and possibly lying about the result based on corruption
        Input:
            int num_sides: Number of sides on the die rolled
            int min_success: Minimum roll required for a success
            int max_crit_fail: Maximum roll required for a critical failure
            double value: Amount of money being spent by company to make this roll, can be stolen
            string roll_type: Type of roll being made, used in prosector report description if minister steals money and is caught and to apply action-specific modifiers
            boolean predetermined_corruption = False: Whether the corruption roll has already been made for this situation
        Output:
            int: Returns the roll's modified result
        """
        min_result = 1
        max_result = num_sides
        result = self.no_corruption_roll(num_sides, roll_type)

        if predetermined_corruption or self.check_corruption():
            if not self.stolen_already:  # true if stealing
                self.steal_money(value, roll_type)
            result = random.randrange(
                max_crit_fail + 1, min_success
            )  # if crit fail on 1 and success on 4+, do random.randrange(2, 4), pick between 2 and 3

        if result < min_result:
            result = min_result
        elif result > max_result:
            result = max_result

        # if corrupt, chance to choose random non-critical failure result
        if result > num_sides:
            result = num_sides
        return result

    def no_corruption_roll(self, num_sides: int = 6, roll_type: str = "none"):
        """
        Description:
            Rolls and returns the result of a die with the inputted number of sides, modifying the result based on skill with the assumption that corruption has already failed to occur or otherwise does not allow for corruption
        Input:
            int num_sides: Number of sides on the die rolled
            string roll_type = 'none': Type of roll being done, used to apply action-specific modifiers
        Output:
            int: Returns the roll's modified result
        """
        min_result = 1
        max_result = num_sides
        result = random.randrange(1, num_sides + 1) + self.get_roll_modifier(roll_type)
        result = max(min_result, result)
        result = min(max_result, result)
        return result

    def roll_to_list(
        self, num_sides, min_success, max_crit_fail, value, roll_type, num_dice
    ):  # use when multiple dice are being rolled, makes corruption independent of dice
        """
        Description:
            Rolls and returns the result of the inputted number of dice each with the inputted number of sides, modifying the results based on skill and possibly lying about the result based on corruption
        Input:
            int num_sides: Number of sides on the die rolled
            int min_success: Minimum roll required for a success
            int max_crit_fail: Maximum roll required for a critical failure
            double value: Amount of money being spent by company to make this roll, can be stolen
            string roll_type: Type of roll being made, used in prosector report description if minister steals money and is caught
            int num_dice: How many dice to roll
        Output:
            int list: Returns a list of the rolls' modified results
        """
        results = []
        if self.check_corruption() and value > 0:
            self.steal_money(value, roll_type)
            self.stolen_already = True
            corrupt_index = random.randrange(0, num_dice)
            for i in range(
                num_dice
            ):  # num_sides, min_success, max_crit_fail, value, roll_type, predetermined_corruption = False
                if (
                    i == corrupt_index
                ):  # if rolling multiple dice, choose one of the dice randomly and make it the corrupt result, making it a non-critical failure
                    results.append(
                        self.roll(
                            num_sides, min_success, max_crit_fail, value, "none", True
                        )
                    )  # use roll_type none because roll is fake, does not apply modifiers
                else:  # for dice that are not chosen, can be critical or non-critical failure because higher will be chosen in case of critical failure, no successes allowed
                    results.append(
                        self.roll(num_sides, min_success, 0, value, "none", True)
                    )  # 0 for max_crit_fail allows critical failure numbers to be chosen
        else:  # if not corrupt, just roll with minister modifier
            for i in range(num_dice):
                results.append(self.no_corruption_roll(num_sides, roll_type))
        self.stolen_already = False
        return results

    def attack_roll_to_list(
        self, own_modifier, enemy_modifier, opponent, value, roll_type, num_dice
    ):
        """
        Description:
            Rolls and returns the result of the inputted number of 6-sided dice along with the enemy unit's roll in combat, modifying the results based on skill and possibly lying about the result based on corruption
        Input:
            int own_modifier: Modifier added to the friendly unit's roll, used to create realistic inconclusive results when corrupt
            int enemy_modifier: Modifier added to the enemy unit's roll, used to create realistic inconclusive results when corrupt
            npmob opponent: Enemy unit being rolled against
            double value: Amount of money being spent by company to make this roll, can be stolen
            string roll_type: Type of roll being made, used in prosector report description if minister steals money and is caught
            int num_dice: number of dice rolled by the friendly unit, not including the one die rolled by the enemy unit
        Output:
            int list: Returns a list of the rolls' modified results, with the first item being the enemy roll
        """
        results = []
        if self.check_corruption():
            self.steal_money(value, roll_type)
            self.stolen_already = True
            for i in range(num_dice):
                results.append(0)
            difference = 10
            while (
                difference >= 2
            ):  # keep rolling until a combination of attacker and defender rolls with an inconclusive result is found
                own_roll = random.randrange(1, 7)
                enemy_roll = random.randrange(1, 7)
                difference = abs(
                    (own_roll + own_modifier) - (enemy_roll + enemy_modifier)
                )
            corrupt_index = random.randrange(0, num_dice)
            for i in range(num_dice):
                if (
                    i == corrupt_index
                ):  # if rolling multiple dice, choose one of the dice randomly to be the chosen result, with the others being lower
                    results[i] = own_roll
                else:
                    results[i] = random.randrange(
                        1, own_roll + 1
                    )  # if own_roll is 1, range is 1-2 non-inclusive, always chooses 1
            results = [enemy_roll] + results  # inserts enemy roll at beginning

        else:  # if not corrupt, just roll with minister modifier
            for i in range(num_dice):
                results.append(self.no_corruption_roll(6, roll_type))
            enemy_roll = opponent.combat_roll()
            results = [enemy_roll] + results
        self.stolen_already = False
        return results

    def appoint(self, new_position):
        """
        Description:
            Appoints this minister to a new office, putting it in control of relevant units. If the new position is 'none', removes the minister from their current office
        Input:
            string new_position: Office to appoint this minister to, like 'Minister of Trade'. If this equals 'none', fires this minister
        Output:
            None
        """
        old_position = self.current_position
        if self.current_position != "none":  # if removing, set old position to none
            status.current_ministers[self.current_position] = None
        self.current_position = new_position
        status.current_ministers[new_position] = self
        for current_pmob in status.pmob_list:
            current_pmob.update_controlling_minister()
        if new_position != "none":  # if appointing
            status.available_minister_list = utility.remove_from_list(
                status.available_minister_list, self
            )
            if (
                constants.available_minister_left_index
                >= len(status.available_minister_list) - 3
            ):
                constants.available_minister_left_index = (
                    len(status.available_minister_list) - 3
                )  # move available minister display up because available minister was removed
        else:
            status.available_minister_list.append(self)
            constants.available_minister_left_index = (
                len(status.available_minister_list) - 3
            )  # move available minister display to newly fired minister

        for current_minister_type_image in status.minister_image_list:
            if current_minister_type_image.get_actor_type() == None:
                if current_minister_type_image.minister_type == new_position:
                    current_minister_type_image.calibrate(self)
                elif current_minister_type_image.minister_type == old_position:
                    current_minister_type_image.calibrate("none")

        if status.displayed_minister == self:
            minister_utility.calibrate_minister_info_display(
                self
            )  # update minister label

        minister_utility.update_available_minister_display()

    def skill_setup(self):
        """
        Description:
            Sets up the general and specific skills for this minister when it is created
        Input:
            None
        Output:
            None
        """
        self.general_skill = random.randrange(
            1, 4
        )  # 1-3, general skill as in all fields, not military
        self.specific_skills = {}
        self.apparent_skills = {}
        self.apparent_skill_descriptions = {}
        background_skill = random.choice(
            constants.background_skills_dict[self.background]
        )
        if background_skill == "random":
            background_skill = random.choice(constants.skill_types)
        for current_minister_type in constants.minister_types:
            self.specific_skills[current_minister_type] = random.randrange(0, 4)  # 0-3
            if (
                constants.minister_type_dict[current_minister_type] == background_skill
                and (self.specific_skills[current_minister_type] + self.general_skill)
                < 6
            ):
                self.specific_skills[current_minister_type] += 1
            if constants.effect_manager.effect_active("transparent_ministers"):
                self.set_apparent_skill(
                    current_minister_type,
                    self.specific_skills[current_minister_type] + self.general_skill,
                )
            else:
                self.set_apparent_skill(current_minister_type, 0)

    def set_apparent_skill(self, skill_type, new_value):
        """
        Description:
            Sets this minister's apparent skill and apparent skill description to match the new apparent skill value for the inputted skill type
        Input:
            string skill_type: Type of skill to set, like 'Minister of Transportation'
            int new_value: New skill value from 0-6, with 0 corresponding to 'unknown'
        """
        if (not skill_type in self.apparent_skills) or self.apparent_skills[
            skill_type
        ] != new_value:
            self.apparent_skills[skill_type] = new_value
            self.apparent_skill_descriptions[skill_type] = random.choice(
                constants.minister_skill_to_description_dict[new_value]
            )
            if not (flags.creating_new_game or self.initializing):
                self.update_tooltip()
            if status.displayed_minister == self:
                minister_utility.calibrate_minister_info_display(self)

    def voice_setup(self, from_save: bool = False):
        """
        Description:
            Gathers a set of voice lines for this minister, either using a saved voice set or a random new one
        Input:
            boolean from_save=False: Whether this minister is being loaded and has an existing voice set that should be used
        Output:
            None
        """
        if not from_save:
            self.voice_set = random.choice(os.listdir("sounds/voices/voice sets"))
        self.voice_lines = {
            "acknowledgement": [],
            "fired": [],
            "evidence": [],
            "hired": [],
        }
        self.last_voice_line: str = None
        folder_path = "voices/voice sets/" + self.voice_set
        for file_name in os.listdir("sounds/" + folder_path):
            for key in self.voice_lines:
                if file_name.startswith(key):
                    file_name = file_name[:-4]  # cuts off last 4 characters - .wav
                    self.voice_lines[key].append(folder_path + "/" + file_name)

    def interests_setup(self):
        """
        Description:
            Chooses and sets 2 interest categories for this minister. One of a minister's interests is one of their best skills, while the other is randomly chosen
        Input:
            None
        Output:
            None
        """
        type_minister_dict = constants.type_minister_dict
        highest_skills = []
        highest_skill_number = 0
        for current_skill in constants.skill_types:
            if (
                len(highest_skills) == 0
                or self.specific_skills[type_minister_dict[current_skill]]
                > highest_skill_number
            ):
                highest_skills = [current_skill]
                highest_skill_number = self.specific_skills[
                    type_minister_dict[current_skill]
                ]
            elif (
                self.specific_skills[type_minister_dict[current_skill]]
                == highest_skill_number
            ):
                highest_skills.append(current_skill)
        first_interest = random.choice(highest_skills)
        second_interest = first_interest
        while second_interest == first_interest:
            second_interest = random.choice(constants.skill_types)

        if random.randrange(1, 7) >= 4:
            self.interests = (first_interest, second_interest)
        else:
            self.interests = (second_interest, first_interest)

    def corruption_setup(self):
        """
        Description:
            Sets up the corruption level for this minister when it is created
        Input:
            None
        Output:
            None
        """
        self.corruption = random.randrange(1, 7)  # 1-6
        self.corruption_threshold = (
            10 - self.corruption
        )  # minimum roll on D6 required for corruption to occur

        if constants.effect_manager.effect_active("transparent_ministers"):
            self.set_apparent_corruption(self.corruption)
        else:
            self.set_apparent_corruption(0)

    def set_apparent_corruption(self, new_value):
        """
        Description:
            Sets this minister's apparent corruption and apparent corruption description to match the new apparent corruption value
        Input:
            int new_value: New corruption value from 0-6, with 0 corresponding to 'unknown'
        """
        if (
            not hasattr(self, "apparent_corruption")
        ) or self.apparent_corruption != new_value:
            self.apparent_corruption = new_value
            self.apparent_corruption_description = random.choice(
                constants.minister_corruption_to_description_dict[new_value]
            )
            if not (flags.creating_new_game or self.initializing):
                self.update_tooltip()
            if status.displayed_minister == self:
                minister_utility.calibrate_minister_info_display(self)

    def get_average_apparent_skill(self):
        """
        Description:
            Calculates and returns the average apparent skill number for this minister
        Input:
            None
        Output:
            string/double: Returns average of all esimated apparent skill numbers for this minister, or 'unknown' if no skills have estimates
        """
        num_data_points = 0
        total_apparent_skill = 0
        for skill_type in constants.minister_types:
            if self.apparent_skills[skill_type] != "unknown":
                num_data_points += 1
                total_apparent_skill += self.apparent_skills[skill_type]
        if num_data_points == 0:
            return "unknown"
        else:
            return total_apparent_skill / num_data_points

    def get_max_apparent_skill(self):
        """
        Description:
            Calculates and returns the highest apparent skill category for this minister, like 'Minister of Transportation'
        Input:
            None
        Output:
            string: Returns highest apparent skill category for this minister
        """
        max_skills = ["unknown"]
        max_skill_value = 0
        for skill_type in constants.minister_types:
            if self.apparent_skills[skill_type] != "unknown":
                if self.apparent_skills[skill_type] > max_skill_value:
                    max_skills = [skill_type]
                    max_skill_value = self.apparent_skills[skill_type]
                elif self.apparent_skills[skill_type] == max_skill_value:
                    max_skills.append(skill_type)
        return max_skills[0]

    def attempt_rumor(self, rumor_type, prosecutor):
        """
        Description:
            Orders the inputted prosecutor to attempt to find a rumor about this minister's rumor_type field - the result will be within a range of error, and a discovered
                low loyalty could result in a bribe to report a high loyalty
        Input:
            string rumor_type: Type of field to uncover, like 'loyalty' or some skill type
            minister/string prosecutor: Prosecutor finding the rumor, or 'none' for passive rumors
        Output:
            None
        """
        if prosecutor == "none":
            roll_result = random.randrange(1, 7) - random.randrange(
                0, 2
            )  # as if done by a prosecutor with a negative skill modifier
        else:
            roll_result = prosecutor.no_corruption_roll(6)

        if rumor_type == "loyalty":
            apparent_value = self.corruption
        else:
            apparent_value = self.general_skill + self.specific_skills[rumor_type]

        if roll_result < 5:  # 5+ accuracy roll
            for i in range(3):
                apparent_value += random.randrange(-1, 2)

        apparent_value = max(apparent_value, 1)
        apparent_value = min(apparent_value, 6)

        if rumor_type == "loyalty":
            if apparent_value >= 4 and prosecutor != "none":
                if (self.check_corruption() or self.check_corruption()) and (
                    prosecutor.check_corruption() or prosecutor.check_corruption()
                ):  # conspiracy check with advantage
                    bribe_cost = 5
                    if self.personal_savings + self.stolen_money >= bribe_cost:
                        self.personal_savings -= bribe_cost
                        if (
                            self.personal_savings < 0
                        ):  # spend from personal savings, transfer stolen to personal savings if not enough
                            self.stolen_money += self.personal_savings
                            self.personal_savings = 0
                        prosecutor.steal_money(bribe_cost, "bribery")
                        apparent_value = random.randrange(1, 4)
            self.set_apparent_corruption(apparent_value)
        else:
            self.set_apparent_skill(rumor_type, apparent_value)

        if prosecutor == "none":
            if not flags.creating_new_game:
                message = "A rumor has been found that " + self.name + ","
                if self.current_position == "none":
                    message += " a potential minister candidate, "
                else:
                    message += " your " + self.current_position + ", "
                message += "has "
                if rumor_type == "loyalty":
                    message += self.apparent_corruption_description + " loyalty"
                else:
                    skill_name = constants.minister_type_dict[rumor_type]
                    message += (
                        utility.generate_article(
                            self.apparent_skill_descriptions[rumor_type]
                        )
                        + " "
                        + self.apparent_skill_descriptions[rumor_type]
                        + " "
                        + skill_name
                        + " ability"
                    )
                message += ". /n /n"
                self.display_message(message)

    def check_corruption(self):  # returns true if stealing for this roll
        """
        Description:
            Checks and returns whether this minister will steal funds and lie about the dice roll results on a given roll
        Input:
            None
        Output:
            boolean: Returns True if this minister will be corrupt for the roll
        """
        if constants.effect_manager.effect_active("band_of_thieves") or (
            (
                constants.effect_manager.effect_active("lawbearer")
                and self != status.current_ministers["Prosecutor"]
            )
        ):
            return_value = True
        elif constants.effect_manager.effect_active("ministry_of_magic") or (
            constants.effect_manager.effect_active("lawbearer")
            and self == status.current_ministers["Prosecutor"]
        ):
            return_value = False
        elif random.randrange(1, 7) >= self.corruption_threshold:
            if (
                random.randrange(1, 7) >= constants.fear
            ):  # higher fear reduces chance of exceeding threshold and stealing
                return_value = True
            else:
                if constants.effect_manager.effect_active("show_fear"):
                    print(self.name + " was too afraid to steal money")
                return_value = False
        else:
            return_value = False
        return return_value

    def gain_experience(self):
        """
        Description:
            Gives this minister a chance of gaining skill in their current cabinet position if they have one
        Input:
            None
        Output:
            None
        """
        if not self.current_position == "none":
            if self.specific_skills[self.current_position] < 3:
                self.specific_skills[self.current_position] += 1

    def estimate_expected(self, base, allow_decimals=True):
        """
        Description:
            Calculates and returns an expected number within a certain range of the inputted base amount, with accuracy based on this minister's skill. A prosecutor will attempt to estimate what the output of production, commodity
                sales, etc. should be
        Input:
            double base: Target amount that estimate is approximating
        Output:
            double: Returns the estimaed number
        """
        if self.no_corruption_roll(6) >= 4:
            return base
        else:
            multiplier = random.randrange(80, 121)
            multiplier /= 100
            if allow_decimals:
                return round(base * multiplier, 2)
            else:
                return round(base * multiplier)

    def get_skill_modifier(self):
        """
        Description:
            Checks and returns the dice roll modifier for this minister's current office. A combined general and specific skill of <= 2 gives a -1 modifier, >5 5 gives a +1 modifier and other give a 0 modifier
        Input:
            None
        Output:
            int: Returns the dice roll modifier for this minister's current office
        """
        if not self.current_position == "none":
            skill = self.general_skill + self.specific_skills[self.current_position]
        else:
            skill = self.general_skill
        if skill <= 2:  # 1-2
            return -1
        elif skill <= 4:  # 3-4
            return 0
        else:  # 5-6
            return 1

    def get_roll_modifier(self, roll_type="none"):
        """
        Description:
            Returns the modifier this minister will apply to a given roll. As skill has only a half chance of applying to a given roll, the returned value may vary
        Input:
            string roll_type = 'none': Type of roll being done, used to apply action-specific modifiers
        Output:
            int: Returns the modifier this minister will apply to a given roll. As skill has only a half chance of applying to a given roll, the returned value may vary
        """
        modifier = 0
        if constants.effect_manager.effect_active("ministry_of_magic") or (
            constants.effect_manager.effect_active("lawbearer")
            and self == status.current_ministers["Prosecutor"]
        ):
            return 5
        elif constants.effect_manager.effect_active("nine_mortal_men"):
            return -10
        if (
            random.randrange(1, 7) >= 4
        ):  # half chance to apply skill modifier, otherwise return 0
            modifier += self.get_skill_modifier()
            if constants.effect_manager.effect_active("show_modifiers"):
                if modifier >= 0:
                    print(f"Minister gave modifier of +{modifier} to {roll_type} roll.")
                else:
                    print(f"Minister gave modifier of {modifier} to {roll_type} roll.")
        if constants.effect_manager.effect_active(roll_type + "_plus_modifier"):
            if random.randrange(1, 7) >= 4:
                modifier += 1
                if constants.effect_manager.effect_active("show_modifiers"):
                    print("Generic modifier of +1 to " + roll_type + " roll.")
            elif constants.effect_manager.effect_active("show_modifiers"):
                print(f"Attempted to give generic +1 modifier to {roll_type} roll.")
        elif constants.effect_manager.effect_active(roll_type + "_minus_modifier"):
            if random.randrange(1, 7) >= 4:
                modifier -= 1
                if constants.effect_manager.effect_active("show_modifiers"):
                    print("Gneric modifier of of -1 to " + roll_type + " roll.")
            elif constants.effect_manager.effect_active("show_modifiers"):
                print(f"Attempted to give generic -1 modifier to {roll_type} roll.")
        return modifier

    def remove_complete(self):
        """
        Description:
            Removes this object and deallocates its memory - defined for any removable object w/o a superclass
        Input:
            None
        Output:
            None
        """
        self.remove()
        del self

    def remove(self):
        """
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        Input:
            None
        Output:
            None
        """
        if self.current_position != "none":
            status.current_ministers[self.current_position] = None
            for current_minister_image in status.minister_image_list:
                if current_minister_image.minister_type == self.current_position:
                    current_minister_image.calibrate("none")
            self.current_position = "none"
        status.minister_list = utility.remove_from_list(status.minister_list, self)
        status.available_minister_list = utility.remove_from_list(
            status.available_minister_list, self
        )
        minister_utility.update_available_minister_display()

    def respond(self, event):
        """
        Description:
            Causes this minister to display a message notification and sometimes cause effects based on their background and social status when an event like being fired happens
        Input:
            string event: Type of event the minister is responding to, like 'fired'
        Output:
            None
        """
        text = ""
        audio = "none"
        public_opinion_change = 0

        if self.status_number >= 3:
            if self.background == "politician":
                third_party = ["the media", "the prime minister", "Parliament"]
            elif self.background in ["industrialist", "business magnate"]:
                third_party = ["the business community", "my investors", "my friends"]
            else:  # royal heir or aristocrat
                third_party = ["my family", "my cousins", "the nobility"]

        if event == "first hired":
            if self.status_number >= 3:
                public_opinion_change = self.status_number + random.randrange(-1, 2)
                if self.status_number == 4:
                    public_opinion_change += 6
            text += "From: " + self.name + " /n /n"
            intro_options = [
                "You have my greatest thanks for appointing me to your cabinet. ",
                "Honored governor, my gratitude knows no limits. ",
                "Finally, a chance to bring glory to our empire! ",
            ]
            text += random.choice(intro_options)

            middle_options = [
                "I shall ensure my duties are completed with the utmost precision and haste. ",
                "I will never betray you, I swear. ",
                "Nothing will keep us from completing our divine mission. ",
            ]
            text += random.choice(middle_options)

            if self.status_number >= 3:
                conclusion_options = [
                    "I'll make sure to put a good word in with "
                    + random.choice(third_party)
                    + " about you.",
                    "I'm sure "
                    + random.choice(third_party)
                    + " would enjoy hearing about this wise decision.",
                    "Perhaps I could pull some strings with "
                    + random.choice(third_party)
                    + " to help repay you?",
                ]
                text += random.choice(conclusion_options)
                text += (
                    " /n /n /nYou have gained "
                    + str(public_opinion_change)
                    + " public opinion. /n /n"
                )

            else:
                heres_to_options = ["victory", "conquest", "glory"]
                conclusion_options = [
                    "Please send the other ministers my regards - I look forward to working with them. ",
                    "Here's to " + random.choice(heres_to_options) + "!",
                    "We're going to make a lot of money together! ",
                ]
                text += random.choice(conclusion_options) + " /n /n /n"

            if self.status_number == 1:
                public_opinion_change = -1
                text += "While lowborn can easily be removed should they prove incompetent or disloyal, it reflects poorly on the company to appoint them as ministers. /n /n"
                text += (
                    "You have lost "
                    + str(-1 * public_opinion_change)
                    + " public opinion. /n /n"
                )
            audio = self.get_voice_line("hired")

        elif event == "fired":
            multiplier = random.randrange(8, 13) / 10.0  # 0.8-1.2
            public_opinion_change = (
                -10 * self.status_number * multiplier
            )  # 4-6 for lowborn, 32-48 for very high
            constants.evil_tracker.change(1)
            text += "From: " + self.name + " /n /n"
            intro_options = [
                "How far our empire has fallen... ",
                "You have made a very foolish decision in firing me. ",
                "I was just about to retire, and you had to do this? ",
                "I was your best minister - you're all doomed without me. ",
            ]
            text += random.choice(intro_options)

            if self.background == "royal heir":
                family_members = [
                    "father",
                    "mother",
                    "father",
                    "mother",
                    "uncle",
                    "aunt",
                    "brother",
                    "sister",
                ]
                threats = [
                    "killed",
                    "executed",
                    "decapitated",
                    "thrown in jail",
                    "banished",
                    "exiled",
                ]
                text += (
                    "My "
                    + random.choice(family_members)
                    + " could have you "
                    + random.choice(threats)
                    + " for this. "
                )
            elif self.status_number >= 3:
                warnings = [
                    "You better be careful making enemies in high places, friend. ",
                    "Parliament will cut your funding before you can even say 'bribe'. ",
                    "You have no place in our empire, you greedy upstart. ",
                    "Learn how to respect your betters - we're not savages. ",
                ]
                text += random.choice(warnings)
            else:
                warnings = [
                    "Think of what will happen to the "
                    + random.choice(constants.commodity_types)
                    + " prices after the media hears about this! ",
                    "You think you can kick me down from your palace in the clouds? ",
                    "I'll make sure to tell all about those judges you bribed. ",
                    "So many dead... what will be left of this land by the time you're done? ",
                    "You'll burn in hell for this. ",
                    "Watch your back, friend. ",
                ]
                text += random.choice(warnings)
            text += (
                " /n /n /nYou have lost "
                + str(-1 * public_opinion_change)
                + " public opinion. /n"
            )
            text += self.name + " has been fired and removed from the game. /n /n"
            audio = self.get_voice_line("fired")

        elif event == "prison":
            text += "From: " + self.name + " /n /n"
            if self.status_number >= 3:
                intro_options = [
                    "Do you know what we used to do to upstarts like you?",
                    "This is nothing, "
                    + random.choice(third_party)
                    + " will get me out within days.",
                    "You better be careful making enemies in high places, friend. ",
                ]
            else:
                intro_options = [
                    "I would've gotten away with it, too, if it weren't for that meddling prosecutor.",
                    "Get off your high horse - we could have done great things together.",
                    "How much money would it take to change your mind?",
                ]
            intro_options.append(
                "Do you even know how many we killed? We all deserve this."
            )
            intro_options.append("I'm innocent, I swear!")
            intro_options.append("You'll join me here soon: sic semper tyrannis.")

            text += random.choice(intro_options)
            text += " /n /n /n"
            text += (
                self.name
                + " is now in prison and has been removed from the game. /n /n"
            )
            audio = self.get_voice_line("fired")

        elif event == "retirement":
            if self.current_position == "none":
                text = (
                    self.name
                    + " no longer desires to be appointed as a minister and has left the pool of available minister appointees. /n /n"
                )
            else:
                if random.randrange(0, 100) < constants.evil:
                    tone = "guilty"
                else:
                    tone = "content"

                if self.stolen_money >= 10.0 and random.randrange(1, 7) >= 4:
                    tone = "confession"

                if tone == "guilty":
                    intro_options = [
                        "I can't believe some of the things I saw here. ",
                        "What gave us the right to conquer this place? ",
                        "I see them every time I close my eyes - I can't keep doing this.",
                    ]
                    middle_options = [
                        "I hear God weeping at the crimes we commit in His name.",
                        "We sent so many young men to die just to fill our coffers. ",
                    ]
                    conclusion_options = [
                        "I pray we will be forgiven for the things we've done, and you ought to do the same. ",
                        "Was it all worth it? ",
                        "I promise to never again set foot on this stolen continent. ",
                    ]
                elif tone == "content":
                    intro_options = [
                        "I'm sorry to say it, but I've gotten too old for this. ",
                        "This has been a pleasant journey, but life has greater opportunities planned for me. ",
                        "Unfortunately, I can no longer work in your cabinet - I am needed back home. ",
                    ]
                    middle_options = [
                        "Can you believe it, though? We singlehandedly civilized this place. ",
                        "I wish I could stay. The thrill of adventure, the wonders I've seen here. It's like I was made for this. ",
                        "Never has the world seen such glory as what we have brought here. ",
                    ]
                    conclusion_options = [
                        "I trust you'll continue to champion the cause of our God and our empire. ",
                        "I hope to live many more years, but my best were spent here with you. ",
                        "Promise me you'll protect what we built here. Never forget our mission, and never grow complacent. ",
                    ]
                elif tone == "confession":
                    intro_options = [
                        "You fool! I took "
                        + str(self.stolen_money)
                        + " money from behind your back, and you just looked the other way. ",
                        "I'll have an amazing retirement with the "
                        + str(self.stolen_money)
                        + " money you let me steal. ",
                        "I could tell you just how much money I stole from you over the years, but I'll spare you the tears. ",
                    ]
                    middle_options = [
                        "We represent the empire's best, but so many of the ministers are just thieves behind your back. ",
                        "Did you really believe all those setbacks and delays I invented? ",
                        "Believe it or not, I was always one of the lesser offenders. ",
                    ]
                    conclusion_options = [
                        "We aren't so different, you and I - we're both just here to make money. Who ever cared about the empire? ",
                        "You'll never see me again, of course, but I wish I could see the look on your face. ",
                        "If I had the chance, I'd do it all again. ",
                    ]
                text += (
                    random.choice(intro_options)
                    + random.choice(middle_options)
                    + random.choice(conclusion_options)
                )
                text += (
                    " /n /n /n"
                    + self.current_position
                    + " "
                    + self.name
                    + " has chosen to step down and retire. /n /n"
                )
                text += "Their position will need to be filled by a replacement as soon as possible for your company to continue operations. /n /n"
        constants.public_opinion_tracker.change(public_opinion_change)
        if text != "":
            self.display_message(text, audio)

    def get_voice_line(self, type):
        """
        Description:
            Attempts to retrieve one of this minister's voice lines of the inputted type
        Input:
            string type: Type of voice line to retrieve
        Output:
            string: Returns sound_manager file path of retrieved voice line
        """
        selected_line = None
        if len(self.voice_lines[type]) > 0:
            selected_line = random.choice(self.voice_lines[type])
            while (
                len(self.voice_lines[type]) > 1
                and selected_line == self.last_voice_line
            ):
                selected_line = random.choice(self.voice_lines[type])
        self.last_voice_line = selected_line
        return selected_line

    def play_voice_line(self, type):
        """
        Description:
            Attempts to play one of this minister's voice lines of the inputted type
        Input:
            string type: Type of voice line to play
        Output:
            None
        """
        if len(self.voice_lines[type]) > 0:
            constants.sound_manager.play_sound(self.get_voice_line(type))
