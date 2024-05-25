import pickle
import os
from typing import List
from ...util import scaling, action_utility
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags


class achievement_manager_template:
    """
    Object that controls achievements
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
        self.victory_conditions: List[str] = [
            "Entrepreneur",
            "Heart of Darkness",
            "It Belongs in a Museum",
            "Industrialist",
            "Minimum Wage",
        ]
        self.achievements: List[str] = []
        loaded_achievements = []
        if os.path.exists(
            "save_games/achievements.pickle"
        ) and not constants.effect_manager.effect_active("reset_achievements"):
            with open("save_games/achievements.pickle", "rb") as file:
                loaded_achievements = pickle.load(file)
        input_dict = {
            "coordinates": scaling.scale_coordinates(
                constants.default_display_width - 45, 5
            ),
            "width": scaling.scale_width(10),
            "height": scaling.scale_height(30),
            "modes": [
                "strategic",
                "earth",
                "ministers",
                "trial",
                "main_menu",
                "new_game_setup",
            ],
            "init_type": "ordered collection",
            "direction": "vertical",
            "reversed": True,
        }
        second_input_dict = input_dict.copy()
        second_input_dict["coordinates"] = scaling.scale_coordinates(
            constants.default_display_width - 90, 5
        )
        self.achievement_displays = [
            constants.actor_creation_manager.create_interface_element(input_dict),
            constants.actor_creation_manager.create_interface_element(
                second_input_dict
            ),
        ]
        for achievement in loaded_achievements:
            self.achieve(achievement, verbose=False)

    def achieve(self, achievement_type: str, verbose: bool = True):
        """
        Description:
            Achieves an achievement, creating corresponding interface element and saving the achievement
        Input:
            None
        Output:
            None
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
                        constants.notification_manager.display_notification(
                            {
                                "message": f'Victory - "{achievement_type}": {self.get_description(achievement_type)} /n /n{self.get_quote(achievement_type)} /n /n',
                                "attached_interface_elements": [
                                    attached_interface_elements
                                ],
                                "choices": ["continue", "confirm main menu"],
                            }
                        )
                    else:
                        constants.notification_manager.display_notification(
                            {
                                "message": f'Victory achievement unlocked - "{achievement_type}": {self.get_description(achievement_type)} /n /n{self.get_quote(achievement_type)} /n /n',
                                "attached_interface_elements": [
                                    attached_interface_elements
                                ],
                                "choices": ["continue", "confirm main menu"],
                            }
                        )
                else:
                    constants.notification_manager.display_notification(
                        {
                            "message": f'Achievement unlocked - "{achievement_type}": {self.get_description(achievement_type)} /n /n{self.get_quote(achievement_type)} /n /n',
                            "attached_interface_elements": [
                                attached_interface_elements
                            ],
                            "notification_type": "action",
                        }
                    )

            if not achievement_type in self.achievements:
                self.achievements.append(achievement_type)
                constants.actor_creation_manager.create_interface_element(
                    {
                        "coordinates": scaling.scale_coordinates(0, 0),
                        "width": scaling.scale_width(40),
                        "height": scaling.scale_height(40),
                        "image_id": f"achievements/{achievement_type}.png",
                        "init_type": "tooltip free image",
                        "parent_collection": self.achievement_displays[
                            len(self.achievements) // 16
                        ],
                        "tooltip_text": [
                            achievement_type
                            + ": "
                            + self.get_description(achievement_type),
                            self.get_quote(achievement_type),
                        ],
                    }
                )

        if achievement_type in self.victory_conditions and verbose == True:
            if status.current_country:
                if (
                    status.current_country.name == "Britain"
                    and "Victorian Man" not in self.achievements
                ):
                    self.achieve("Victorian Man")
                elif (
                    status.current_country.name == "France"
                    and "L'enterprise, c'est moi" not in self.achievements
                ):
                    self.achieve("L'enterprise, c'est moi")
                elif (
                    status.current_country.name == "Germany"
                    and "Second Reich" not in self.achievements
                ):
                    self.achieve("Second Reich")
                elif (
                    status.current_country.name == "Belgium"
                    and "Absolutely Flemished" not in self.achievements
                ):
                    self.achieve("Absolutely Flemished")
                elif (
                    status.current_country.name == "Italy"
                    and "New Empire" not in self.achievements
                ):
                    self.achieve("New Empire")
                elif (
                    status.current_country.name == "Portugal"
                    and "Mapa Cor-de-Rosa" not in self.achievements
                ):
                    self.achieve("Mapa Cor-de-Rosa")

            if not flags.any_slaves and "Land of the Free" not in self.achievements:
                self.achieve("Land of the Free")

        with open("save_games/achievements.pickle", "wb") as handle:
            pickle.dump(self.achievements, handle)
            handle.close()

    def get_description(self, achievement_type: str) -> str:
        """
        Description:
            Returns the description of an achievement
        Input:
            None
        Output:
            None
        """
        return {
            "Entrepreneur": "Start a turn with 10,000 money",
            "Heart of Darkness": "Explore the entire map",
            "It Belongs in a Museum": "Complete 3 lore missions",
            "Industrialist": "Upgrade a resource production facility to 6 efficiency and 6 scale",
            "Minimum Wage": "Decrease African worker upkeep to 0.5 while employing at least 10 African workers",
            "Victorian Man": "Win a game as Britain",
            "L'enterprise, c'est moi": "Win a game as France",
            "Second Reich": "Win a game as Germany",
            "Absolutely Flemished": "Win a game as Belgium",
            "Mapa Cor-de-Rosa": "Win a game as Portugal",
            "New Empire": "Win a game as Italy",
            "Return on Investment": "Have at least 500 money after the start of the game",
            "I DECLARE BANKRUPTCY!": "Lose the game",
            "Land of the Free": "Win a game without ever having slaves",
            "Abolitionist": "End the slave trade",
            "Naught but Ashes": "Destroy a village",
            "Guilty": "Win a trial",
            "Vilified": "Reach 0 public opinion",
            "Idolized": "Reach 100 public opinion",
            "Explorer": "Find a river source",
            "Archaeologist": "Complete 1 lore mission",
            "Big Game Hunter": "Kill a beast",
        }[achievement_type]

    def get_quote(self, achievement_type: str) -> str:
        return {
            "Entrepreneur": '"I believe the power to make money is a gift from God." - John D. Rockefeller',
            "Heart of Darkness": '"We live in the flicker - may it last as long as the old earth keeps rolling! But darkness was here yesterday." - Joseph Conrad',
            "It Belongs in a Museum": '"Archaeologists only look at what lies beneath their feet. The sky and heavens don\'t exist for them." - Agatha Christie',
            "Industrialist": '"Never be a minion, always be an owner." - Cornelius Vanderbilt',
            "Minimum Wage": '"Everything now is profit. I am what we\'ve always been to the empire: pure, [expletive] profit. A natural resource to exploit and exploit, denigrate, and exploit." - Natasha Brown',
            "Victorian Man": '"Remember that you are an Englishman, and have consequently won first prize in the lottery of life." - Cecil John Rhodes',
            "L'enterprise, c'est moi": 'I see only my objective - the obstacles must give way." - Napoleon Bonaparte',
            "Second Reich": '"The great questions of the day will not be settled by means of speeches and majority decisions but by iron and blood." - Otto von Bismarck',
            "Absolutely Flemished": 'There are no small countries, only small minds." - Leopold II',
            "Mapa Cor-de-Rosa": '"To speak of Portuguese colonies in East Africa is to speak of a mere fiction - a fiction colourably sustained by a few scattered seaboard settlements, beyond whose narrow littoral and local limits colonisation and government have no existence." - Henry O\'Neill',
            "New Empire": '"I offer neither pay, nor quarters, nor food; I offer only hunger, thirst, forced marches, battles, and death. Let him who loves his country with his heart, and not merely with his lips, follow me." - Giuseppe Garibaldi',
            "Return on Investment": '"For the immediate future, at least, the outlook is bright." - Irving Fisher',
            "I DECLARE BANKRUPTCY!": '"Everyone acquainted with the subject will recognize it as a conspicuous failure" - Henry Morton Stanley',
            "Land of the Free": '"Slaves cannot breathe in England; if their lungs receive our air, that moment they are free." - William Cowper',
            "Abolitionist": '"Enslavement was not destined to end, and it is wrong to claim our present circumstance... as the redemption for the lives of people who never asked for the... glory of dying for their children. Our triumphs can never compensate for this." - Ta-Nehisi Coates',
            "Naught but Ashes": "\"'What a villain you are, to boast of killing women and children of your own nation! What will God say when you appear before him?' 'He will say,' replied he, 'that I was a very clever fellow.'\" ― David Livingstone",
            "Guilty": '"We cannot stand idly by and allow our government to be run by a pack of incompetent ministers." - Lynn Messina',
            "Vilified": '"No great advance has ever been made in science, politics, or religion, without controversy." - Lyman Beecher',
            "Idolized": '"These expeditions respond to an extraordinarily civilizing Christian idea: to abolish slavery in Africa, to dispel the darkness that still reigns in part of the world... in short, pouring out the treasures of civilization" - Leopold II',
            "Explorer": '"But my estimates, for instance, based upon book information, were simply ridiculous. Fanciful images of African attractions were soon dissipated... and all crude ideas began to resolve themselves into shape." - Henry Morton Stanley',
            "Archaeologist": '"The British Museum is great for seeing how excellent we were at stealing things." - Russell Howard',
            "Big Game Hunter": '"Some thought they were.. the spirits of dead medicine men come back to spread madness. For others, they were the devil, sent to stop the white men from owning the world." - Samuel "the Muslim""',
        }.get(achievement_type, "")

    def check_achievements(self, achievement_type: str = None) -> None:
        """
        Description:
            Checks if the inputted achievement is being achieved, or checks all achievements if no input is given
        """
        if achievement_type == "Entrepreneur" or achievement_type == "start of turn":
            if constants.money_tracker.get() >= 10000:
                self.achieve("Entrepreneur")

        if achievement_type == "Heart of Darkness":
            if status.strategic_map_grid:
                for current_cell in status.strategic_map_grid.get_flat_cell_list():
                    if not current_cell.visible:
                        return
                self.achieve("Heart of Darkness")

        if achievement_type == "It Belongs in a Museum":
            if len(constants.completed_lore_missions) >= 3:
                self.achieve("It Belongs in a Museum")

            if len(constants.completed_lore_missions) >= 1:
                self.achieve("Archaeologist")

        if achievement_type == "Minimum Wage":
            if (
                status.worker_types["African"].upkeep <= 0.5
                and status.worker_types["African"].number >= 10
            ):
                self.achieve("Minimum Wage")

        if achievement_type == "Return on Investment":
            if constants.money_tracker.get() >= 500:
                self.achieve("Return on Investment")
