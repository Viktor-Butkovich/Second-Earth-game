# Contains player profile achievement management singleton

import pickle
import os
from typing import List
from modules.util import scaling, action_utility
from modules.constants import constants, status, flags


class achievement_manager:
    """
    Object that controls achievements
    """

    def __init__(self):
        """
        Initializes this object
        """
        self.victory_conditions: List[str] = []
        self.achievements: List[str] = []
        loaded_achievements = []
        if os.path.exists(
            "save_games/achievements.pickle"
        ) and not constants.EffectManager.effect_active("reset_achievements"):
            with open("save_games/achievements.pickle", "rb") as file:
                loaded_achievements = pickle.load(file)
        input_dict = {
            "coordinates": scaling.scale_coordinates(
                constants.default_display_width - 45, 5
            ),
            "width": scaling.scale_width(10),
            "height": scaling.scale_height(30),
            "modes": [
                constants.STRATEGIC_MODE,
                constants.EARTH_MODE,
                constants.MINISTERS_MODE,
                constants.TRIAL_MODE,
                constants.MAIN_MENU_MODE,
                constants.NEW_GAME_SETUP_MODE,
            ],
            "init_type": constants.ORDERED_COLLECTION,
            "direction": "vertical",
            "reversed": True,
        }
        second_input_dict = input_dict.copy()
        second_input_dict["coordinates"] = scaling.scale_coordinates(
            constants.default_display_width - 90, 5
        )
        self.achievement_displays = [
            constants.ActorCreationManager.create_interface_element(input_dict),
            constants.ActorCreationManager.create_interface_element(second_input_dict),
        ]
        for achievement in loaded_achievements:
            self.achieve(achievement, verbose=False)

    def achieve(self, achievement_type: str, verbose: bool = True):
        """
        Achieves an achievement, creating corresponding interface element and saving the achievement
        """
        if (not achievement_type in self.achievements) or (
            achievement_type in self.victory_conditions
            and not achievement_type in flags.victories_this_game
        ):
            if verbose:
                attached_interface_elements = (
                    action_utility.generate_free_image_input_dict(
                        f"achievements/{achievement_type}.png",
                        120,
                        override_input_dict={
                            "member_config": {
                                "order_x_offset": scaling.scale_width(-75),
                            }
                        },
                    )
                )
                if achievement_type in self.victory_conditions:
                    flags.victories_this_game.append(achievement_type)
                    if achievement_type in self.achievements:
                        constants.NotificationManager.display_notification(
                            {
                                "message": f'Victory - "{achievement_type}": {self.get_description(achievement_type)} /n /n{self.get_quote(achievement_type)} /n /n',
                                "attached_interface_elements": [
                                    attached_interface_elements
                                ],
                                "choices": [
                                    "continue",
                                    constants.CHOICE_CONFIRM_MAIN_MENU_BUTTON,
                                ],
                            }
                        )
                    else:
                        constants.NotificationManager.display_notification(
                            {
                                "message": f'Victory achievement unlocked - "{achievement_type}": {self.get_description(achievement_type)} /n /n{self.get_quote(achievement_type)} /n /n',
                                "attached_interface_elements": [
                                    attached_interface_elements
                                ],
                                "choices": [
                                    "continue",
                                    constants.CHOICE_CONFIRM_MAIN_MENU_BUTTON,
                                ],
                            }
                        )
                else:
                    constants.NotificationManager.display_notification(
                        {
                            "message": f'Achievement unlocked - "{achievement_type}": {self.get_description(achievement_type)} /n /n{self.get_quote(achievement_type)} /n /n',
                            "attached_interface_elements": [
                                attached_interface_elements
                            ],
                            "notification_type": constants.ACTION_NOTIFICATION,
                        }
                    )

            if not achievement_type in self.achievements:
                self.achievements.append(achievement_type)
                constants.ActorCreationManager.create_interface_element(
                    {
                        "coordinates": scaling.scale_coordinates(0, 0),
                        "width": scaling.scale_width(40),
                        "height": scaling.scale_height(40),
                        "image_id": f"achievements/{achievement_type}.png",
                        "init_type": constants.TOOLTIP_FREE_IMAGE,
                        "parent_collection": self.achievement_displays[
                            len(self.achievements) // 16
                        ],
                        "preset_tooltip_text": [
                            f"{achievement_type}: {self.get_description(achievement_type)}",
                            self.get_quote(achievement_type),
                        ],
                    }
                )

        with open("save_games/achievements.pickle", "wb") as handle:
            pickle.dump(self.achievements, handle)
            handle.close()

    def get_description(self, achievement_type: str) -> str:
        """
        Returns the description of an achievement
        """
        return {
            "Entrepreneur": "Start a turn with 10,000 money",
            "Industrialist": "Upgrade a resource production facility to 6 efficiency and 6 scale",
            "Return on Investment": "Have at least 500 money after the start of the game",
            "I DECLARE BANKRUPTCY!": "Lose the game",
            "Guilty": "Win a trial",
            "Vilified": "Reach 0 public opinion",
            "Idolized": "Reach 100 public opinion",
        }[achievement_type]

    def get_quote(self, achievement_type: str) -> str:
        return {
            "Entrepreneur": '"I believe the power to make money is a gift from God." - John D. Rockefeller',
            "Industrialist": '"Never be a minion, always be an owner." - Cornelius Vanderbilt',
            "Return on Investment": '"For the immediate future, at least, the outlook is bright." - Irving Fisher',
            "I DECLARE BANKRUPTCY!": '"Everyone acquainted with the subject will recognize it as a conspicuous failure" - Henry Morton Stanley',
            "Guilty": '"We cannot stand idly by and allow our government to be run by a pack of incompetent ministers." - Lynn Messina',
            "Vilified": '"No great advance has ever been made in science, politics, or religion, without controversy." - Lyman Beecher',
            "Idolized": '"These expeditions respond to an extraordinarily civilizing Christian idea: to abolish slavery in Africa, to dispel the darkness that still reigns in part of the world... in short, pouring out the treasures of civilization" - Leopold II',
        }.get(achievement_type, "")

    def check_achievements(self, achievement_type: str = None) -> None:
        """
        Description:
            Checks if the inputted achievement is being achieved, or checks all achievements if no input is given
        """
        return
