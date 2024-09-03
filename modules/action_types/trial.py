# Contains all functionality for trial actions

import random
from . import action
from ..util import (
    action_utility,
    text_utility,
    trial_utility,
    utility,
    minister_utility,
    game_transitions,
    scaling,
)
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags


class trial(action.campaign):
    """
    Action to launch trial against a minister
    """

    def initial_setup(self):
        """
        Description:
            Completes any configuration required for this action during setup - automatically called during action_setup
        Input:
            None
        Output:
            None
        """
        super().initial_setup()
        constants.transaction_descriptions[self.action_type] = "trial fees"
        self.name = "trial"
        self.actor_type = "minister"
        self.current_trial = {}
        self.allow_critical_failures = False
        self.placement_type = "free"

    def can_show(self):
        """
        Description:
            Returns whether a button linked to this action should be drawn
        Input:
            None
        Output:
            boolean: Returns whether a button linked to this action should be drawn
        """
        return True

    def button_setup(self, initial_input_dict):
        """
        Description:
            Completes the inputted input_dict with any values required to create a button linked to this action - automatically called during actor display label
                setup
        Input:
            None
        Output:
            None
        """
        button_width = 150
        initial_input_dict["coordinates"] = scaling.scale_coordinates(
            (constants.default_display_width / 2) - (button_width / 2),
            constants.default_display_height / 2 - (button_width / 2),
        )
        initial_input_dict["width"] = scaling.scale_width(button_width)
        initial_input_dict["height"] = scaling.scale_height(button_width)
        initial_input_dict["modes"] = [constants.TRIAL_MODE]
        initial_input_dict["image_id"] = "buttons/to_trial_button.png"
        return super().button_setup(initial_input_dict)

    def pre_start(self, unit):
        """
        Description:
            Prepares for starting an action starting with roll modifiers, setting ongoing action, etc.
        Input:
            pmob unit: Unit selected when the linked button is clicked
        Output:
            None
        """
        super().pre_start(unit)
        self.current_min_success = 5  # alternative to subtracting a roll modifier, which would change the max crit fail
        self.current_min_crit_success = 5

    def update_tooltip(self):
        """
        Description:
            Sets this tooltip of a button linked to this action
        Input:
            None
        Output:
            None
        """
        return [
            f"Tries the defending minister in an attempt to remove them from office and imprison them for corruption",
            f"Costs {self.get_price()} money",
            f"Each trial attempted doubles the cost of other trials in the same turn",
        ]

    def generate_audio(self, subject):
        """
        Description:
            Returns list of audio dicts of sounds to play when notification appears, based on the inputted subject and other current circumstances
        Input:
            string subject: Determines sound dicts
        Output:
            dictionary list: Returns list of sound dicts for inputted subject
        """
        audio = []
        if subject == "initial":
            audio.append("voices/trial starting")
        return audio

    def generate_notification_text(self, subject):
        """
        Description:
            Returns text regarding a particular subject for this action
        Input:
            string subject: Determines type of text to return
        Output:
            string: Returns text for the inputted subject
        """
        text = super().generate_notification_text(subject)
        if subject == "confirmation":
            text += f"Are you sure you want to start a trial against {status.displayed_defense.name}? You have {status.displayed_defense.corruption_evidence} pieces of evidence to use. /n /n"
            text += "Your prosecutor may roll 1 die for each piece of evidence, and the trial is successful with a 5+ on any evidence dice. /n /n"
            text += "However, the defense may spend from their personal savings (perhaps stolen from your company) to hire lawyers and negate some of the evidence. /n /n"
            text += f"Along with any money paid for bribery or fabricated evidence, a trial fee of {self.get_price()} money is also required. /n /n"
        elif subject == "initial":
            new_clothing_types = ["jewelry", "robes", "wig"]
            if not (
                self.current_trial["defense_bribed_judge"]
                or flags.prosecution_bribed_judge
            ):
                if self.current_trial["judge_bias"] == 1:
                    text = "Even before evidence is presented, the judge has a suspicious bias in favor of the defense, removing 1 of your evidence rolls."
                    self.current_trial["judge_modifier"] = -1
                elif self.current_trial["judge_bias"] == 6:
                    text = "Despite not being bribed, the judge has a healthy bias in favor of the prosecution, giving 1 additional evidence roll."
                    self.current_trial["judge_modifier"] = 1
                else:
                    text = "The judge does not seem to favor any particular side."

            elif (
                self.current_trial["defense_bribed_judge"]
                and not flags.prosecution_bribed_judge
            ):
                if self.current_trial["judge_bias"] <= 5:
                    text = "Even before evidence is presented, the judge has a suspicious bias in favor of the defense, removing 1 of your evidence rolls."
                    self.current_trial["judge_modifier"] = -1
                else:
                    text = "The judge does not seem to favor any particular side and does not modify your evidence rolls."
            elif (
                flags.prosecution_bribed_judge
                and not self.current_trial["defense_bribed_judge"]
            ):
                if (
                    self.current_trial["judge_bias"] == 1
                    or self.current_trial["prosecutor_corrupt"]
                ):  # judge never received the money
                    text = "You could have sworn you sent your prosecutor to bribe the judge, but the judge gives the prosecution neither knowing glances nor special treatment."
                else:
                    text = (
                        "Smiling and flaunting his fancy new "
                        + random.choice(new_clothing_types)
                        + ", the judge has a healthy bias in favor of the prosecution, giving 1 additional evidence roll."
                    )
                    self.current_trial["judge_modifier"] = 1
            else:  # if both sides bribed judge
                if self.current_trial["judge_bias"] <= 2:
                    text = (
                        "Despite his fancy new "
                        + random.choice(new_clothing_types)
                        + ", the judge has a suspicious bias in favor of the defense, removing 1 of your evidence rolls."
                    )
                    self.current_trial["judge_modifier"] = -1
                elif self.current_trial["judge_bias"] <= 4:
                    text = "You could have sworn you sent your prosecutor to bribe the judge, but the judge gives the prosecution neither knowing glances nor special treatment."
                else:
                    text = (
                        "Smiling and flaunting his fancy new "
                        + random.choice(new_clothing_types)
                        + ", the judge has a healthy bias in favor of the prosecution, giving 1 additional evidence roll."
                    )
                    self.current_trial["judge_modifier"] = 1
            text += " /n /n"
            self.current_trial["effective_evidence"] += self.current_trial[
                "judge_modifier"
            ]

            if self.current_trial["num_lawyers"] == 0:
                text += f"As the defense decided not to hire any additional lawyers, each piece of evidence remains usable, allowing {self.current_trial['effective_evidence']} evidence rolls to attempt to win the trial. /n /n"
            else:
                text += f"The defense hired {self.current_trial['num_lawyers']} additional lawyer{utility.generate_plural(self.current_trial['num_lawyers'])}, cancelling out {self.current_trial['num_lawyers']} piece"
                text += f"{utility.generate_plural(self.current_trial['num_lawyers'])} of evidence. This leaves {self.current_trial['effective_evidence']} evidence roll"
                text += f"{utility.generate_plural(self.current_trial['effective_evidence'])} to attempt to win the trial. /n /n"

            text += f"{self.current_trial['corruption_evidence']} initial evidence - "
            text += f"{self.current_trial['num_lawyers']} defense lawyers "
            if self.current_trial["judge_modifier"] < 0:
                text += f"- {abs(self.current_trial['judge_modifier'])} judge bias "
            elif self.current_trial["judge_bias"] > 0:
                text += f"+ {self.current_trial['judge_modifier']} judge bias "
            else:
                text += "+ 0 judge bias "
            text += f"= {self.current_trial['effective_evidence']} evidence rolls /n /n"
        return text

    def on_click(self, unit):
        """
        Description:
            Used when the player clicks a linked action button - checks if the unit can do the action, proceeding with 'start' if applicable
        Input:
            pmob unit: Unit selected when the linked button is clicked
        Output:
            None
        """
        if super().on_click(unit):
            if status.displayed_defense.corruption_evidence <= 0:
                text_utility.print_to_screen(
                    "No real or fabricated evidence currently exists, so the trial has no chance of success."
                )
            else:
                self.start(unit)

    def start(self, unit):
        """
        Description:
            Used when the player clicks on the start action button, displays a choice notification that allows the player to start or not
        Input:
            pmob unit: Unit selected when the linked button is clicked
        Output:
            None
        """
        if super().start(unit):
            constants.notification_manager.display_notification(
                {
                    "message": self.generate_notification_text("confirmation"),
                    "transfer_interface_elements": True,
                    "choices": [
                        {
                            "on_click": (self.middle, []),
                            "tooltip": ["Start trial"],
                            "message": "Start trial",
                        },
                        {"tooltip": ["Cancel"], "message": "Cancel"},
                    ],
                }
            )

    def middle(self):
        """
        Description:
            Controls the campaign process, determining and displaying its result through a series of notifications
        Input:
            None
        Output:
            None
        """
        price = self.process_payment()
        defense = status.displayed_defense
        prosecution = status.displayed_prosecution
        prosecutor_corrupt = prosecution.check_corruption()
        if prosecutor_corrupt:
            prosecution.steal_money(price, "trial")
            prosecution.steal_money(
                trial_utility.get_fabricated_evidence_cost(
                    defense.fabricated_evidence, True
                ),
                "trial",
            )
            if flags.prosecution_bribed_judge:
                prosecution.steal_money(
                    trial_utility.get_fabricated_evidence_cost(0), "trial"
                )

        self.current_trial = {}
        trial_utility.manage_defense(defense.corruption_evidence, prosecutor_corrupt)
        self.current_trial["judge_modifier"] = 0
        self.current_trial["judge_bias"] = (
            prosecution.no_corruption_roll(6) - defense.get_roll_modifier()
        )  # D6 with both skill modifiers competing
        self.current_trial["judge_bias"] = max(self.current_trial["judge_bias"], 1)
        self.current_trial["judge_bias"] = min(self.current_trial["judge_bias"], 6)
        self.current_trial["trial_rolls"] = []
        self.current_trial["prosecutor_corrupt"] = prosecutor_corrupt
        if prosecutor_corrupt:
            max_roll = 4
        else:
            max_roll = 6
        text = self.generate_notification_text("initial")

        constants.notification_manager.display_notification(
            {
                "message": text,
                "notification_type": constants.ACTION_NOTIFICATION,
                "audio": self.generate_audio("initial"),
            }
        )

        self.current_trial["trial_rolls"] = [
            prosecution.no_corruption_roll(max_roll)
            for i in range(0, self.current_trial["effective_evidence"])
        ]
        self.roll_lists = self.generate_roll_lists(self.current_trial["trial_rolls"])
        self.roll_result = 0
        roll_result_index = self.current_trial["effective_evidence"] - 1
        for index in range(self.current_trial["effective_evidence"]):
            if self.roll_result < 5 and self.current_trial["trial_rolls"][index] >= 5:
                self.roll_result = self.current_trial["trial_rolls"][index]
                roll_result_index = index
        if self.current_trial["trial_rolls"]:
            for i in range(0, roll_result_index + 1):
                remaining_rolls_message = (
                    f"Evidence rolls remaining: {len(self.roll_lists)} /n /n"
                )
                constants.notification_manager.display_notification(
                    {
                        "message": f"{remaining_rolls_message}{text}{self.generate_notification_text('roll_message')}",
                        "notification_type": constants.ACTION_NOTIFICATION,
                        "attached_interface_elements": self.generate_attached_interface_elements(
                            "die"
                        ),
                        "transfer_interface_elements": True,
                    }
                )
                constants.notification_manager.display_notification(
                    {
                        "message": remaining_rolls_message + text + "Rolling... ",
                        "notification_type": constants.DICE_ROLLING_NOTIFICATION,
                        "transfer_interface_elements": True,
                        "audio": self.generate_audio("roll_started"),
                    }
                )
                current_roll_list = self.roll_lists.pop(0)
                constants.notification_manager.display_notification(
                    {
                        "message": f"{remaining_rolls_message}{text}{current_roll_list[1]}",
                        "notification_type": constants.ACTION_NOTIFICATION,
                    }
                )
                if i == roll_result_index:
                    text += current_roll_list[1]
            constants.notification_manager.display_notification(
                {
                    "message": text + "Click to remove this notification. /n /n",
                    "notification_type": constants.ACTION_NOTIFICATION,
                    "transfer_interface_elements": True,
                    "on_remove": self.complete,
                    "audio": self.generate_audio("roll_finished"),
                }
            )
        else:
            constants.notification_manager.display_notification(
                {
                    "message": "As you have no evidence rolls remaining, you automatically lose the trial. /n /n",
                    "notification_type": constants.ACTION_NOTIFICATION,
                    "on_remove": self.complete,
                }
            )

    def leave_trial_screen(self):
        """
        Description:
            Callback function to return to ministers screen after trial is completed, regardless of result
        Input:
            None
        Output:
            None
        """
        game_transitions.set_game_mode(constants.MINISTERS_MODE)

    def complete(self):
        """
        Description:
            Used when the player finishes rolling, shows the action's results and makes any changes caused by the result
        Input:
            None
        Output:
            None
        """
        prosecution = status.displayed_prosecution
        defense = status.displayed_defense
        if self.roll_result >= self.current_min_success:
            confiscated_money = defense.stolen_money / 2.0
            text = f"You have won the trial, removing {defense.name} as {defense.current_position.name} and putting them in prison. /n /n"
            if confiscated_money > 0:
                text += f"While most of {defense.name}'s money was spent on the trial or unaccounted for, authorities managed to confiscate {str(confiscated_money)} money, which has been given to your company as compensation. /n /n"
                text += " /n /n"
                constants.money_tracker.change(confiscated_money, "trial_compensation")
            else:
                text += f"Authorities searched {defense.name}'s properties but were not able to find any stolen money with which to compensate your company. Perhaps it remains hidden, had already been spent, or had never been stolen. /n /n"
            constants.notification_manager.display_notification(
                {
                    "message": text,
                    "notification_type": constants.ACTION_NOTIFICATION,
                    "audio": "voices/guilty",
                }
            )
            defense.appoint(None)
            minister_utility.calibrate_minister_info_display(None)
            defense.respond("prison")
            defense.remove_complete()
            constants.fear_tracker.change(1)
            text = "Whether or not the defendant was truly guilty, this vigilant show of force may make your ministers reconsider any attempts to steal money for the time being. /n /n"
            constants.notification_manager.display_notification(
                {
                    "message": text,
                    "notification_type": constants.ACTION_NOTIFICATION,
                    "on_remove": self.leave_trial_screen,
                }
            )
            constants.achievement_manager.achieve("Guilty")

        else:
            text += f"You have lost the trial and {defense.name} goes unpunished, remaining your {defense.current_position.name}. /n /n"
            fabricated_evidence = defense.fabricated_evidence
            real_evidence = defense.corruption_evidence - defense.fabricated_evidence

            remaining_evidence = 0
            lost_evidence = 0
            for i in range(0, real_evidence):
                if prosecution.no_corruption_roll(6) >= 4:
                    remaining_evidence += 1
                else:
                    lost_evidence += 1

            if fabricated_evidence > 0:
                text += f"Fabricated evidence is temporary, so the {fabricated_evidence} piece{utility.generate_plural(fabricated_evidence)} of fabricated evidence used in this trial "
                text += f"{utility.conjugate('be', fabricated_evidence)} now irrelevant to future trials. /n /n"

            if real_evidence > 0:
                if lost_evidence == 0:  # if no evidence lost
                    text += "All of the real evidence used in this trial remains potent enough to be used in future trials against "
                    text += defense.name + ". /n /n"
                elif lost_evidence < real_evidence:  # if some evidence lost
                    text += f"Of the {real_evidence} piece{utility.generate_plural(real_evidence)} of real evidence used in this trial, {remaining_evidence}"
                    text += f" {utility.conjugate('remain', remaining_evidence)} potent enough to be relevant to future trials against {defense.name}, while {lost_evidence} {utility.conjugate('be', lost_evidence)}"
                    text += " now irrelevant. /n /n"
                else:  # if all evidence lost
                    text += f"Of the {real_evidence} piece{utility.generate_plural(real_evidence)} of real evidence used in this trial, none remain potent enough to be relevant to future trials against {defense.name}. /n /n"

            defense.fabricated_evidence = 0
            defense.corruption_evidence = remaining_evidence
            constants.notification_manager.display_notification(
                {
                    "message": text,
                    "notification_type": constants.ACTION_NOTIFICATION,
                    "audio": "voices/not guilty",
                    "on_remove": self.leave_trial_screen,
                }
            )
            minister_utility.calibrate_minister_info_display(defense)
        flags.prosecution_bribed_judge = False
        self.current_trial = {}
        super().complete()
