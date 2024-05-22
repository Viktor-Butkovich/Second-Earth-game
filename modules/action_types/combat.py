# Contains all functionality for combat

import random
from . import action
from ..util import (
    action_utility,
    text_utility,
    actor_utility,
    dice_utility,
    utility,
    turn_management_utility,
)
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags


class combat(action.action):
    """
    Action for battalion/safari to attack or for any unit to defend
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
        for action_type in ["combat", "hunting"]:
            self.action_type = action_type
            super().initial_setup()
            constants.transaction_descriptions[action_type] = "combat supplies"
        self.name = "combat"
        self.opponent = None
        self.direction = None
        self.defending = None
        self.x_change = None
        self.y_change = None
        self.opponent_roll_result = None
        self.total_roll_result = None
        self.public_opinion_change = None

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
        return

    def update_tooltip(self, tooltip_info_dict=None):
        """
        Description:
            Sets this tooltip of a button linked to this action - in this case, the tooltip is added to movement button tooltips when an attack is possible
        Input:
            None
        Output:
            None
        """
        message = []
        final_movement_cost = status.displayed_mob.get_movement_cost(
            tooltip_info_dict["x_change"], tooltip_info_dict["y_change"]
        )
        message.append(
            "Attacking an enemy unit costs 5 money and requires only 1 movement point, but staying in the enemy's tile afterward would require the usual movement"
        )
        text = (
            "Staying afterward would cost "
            + str(final_movement_cost - 1)
            + " more movement point"
            + utility.generate_plural(final_movement_cost - 1)
            + " because the adjacent tile has "
            + tooltip_info_dict["adjacent_cell"].terrain
            + " terrain "
        )
        if tooltip_info_dict["local_cell"].has_walking_connection(
            tooltip_info_dict["adjacent_cell"]
        ):
            local_infrastructure = tooltip_info_dict["local_infrastructure"]
            adjacent_infrastructure = tooltip_info_dict["adjacent_infrastructure"]
            if local_infrastructure != "none" and adjacent_infrastructure != "none":
                text += "and connecting roads"
            elif local_infrastructure == "none" and adjacent_infrastructure != "none":
                text += "and no connecting roads"
            elif local_infrastructure != "none":
                text += "and no connecting roads"
            else:
                text += "and no connecting roads"
        message.append(text)
        return message

    def generate_attached_interface_elements(self, subject):
        """
        Description:
            Returns list of input dicts of interface elements to attach to a notification regarding a particular subject for this action
        Input:
            string subject: Determines input dicts
        Output:
            dictionary list: Returns list of input dicts for inputted subject
        """
        return_list = super().generate_attached_interface_elements(subject)
        if subject == "dice":
            return_list = []
            background_dict = action_utility.generate_background_image_input_dict()
            pmob_image_id_list = (
                [background_dict]
                + self.current_unit.get_image_id_list()
                + ["misc/pmob_outline.png"]
            )
            npmob_image_id_list = (
                [background_dict]
                + self.opponent.get_image_id_list()
                + ["misc/npmob_outline.png"]
            )

            image_size = 120
            return_list.append(
                action_utility.generate_free_image_input_dict(
                    pmob_image_id_list,
                    image_size,
                    override_input_dict={"member_config": {"centered": True}},
                )
            )

            return_list += [
                action_utility.generate_die_input_dict(
                    (0, 0),
                    roll_list[0],
                    self,
                    override_input_dict={"member_config": {"centered": True}},
                )
                for roll_list in self.roll_lists
            ]

            return_list.append(
                action_utility.generate_die_input_dict(
                    (0, 0),
                    self.opponent_roll_result,
                    self,
                    override_input_dict={
                        "result_outcome_dict": {
                            "min_success": 7,
                            "min_crit_success": 7,
                            "max_crit_fail": self.current_max_crit_fail,
                        },
                        "member_config": {"centered": True},
                    },
                )
            )
            return_list.append(
                action_utility.generate_free_image_input_dict(
                    npmob_image_id_list,
                    image_size,
                    override_input_dict={"member_config": {"centered": True}},
                )
            )
            if not self.defending:
                return_list += (
                    self.current_unit.controlling_minister.generate_icon_input_dicts(
                        alignment="left"
                    )
                )
        return return_list

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
            if self.opponent.npmob_type == "beast":
                text += f"Are you sure you want to spend {str(self.get_price())} money to hunt the {self.opponent.name} to the {self.direction}? /n /nRegardless of the result, the rest of this unit's movement points will be consumed."
            else:
                text += f"Are you sure you want to spend {str(self.get_price())} money to attack the {self.opponent.name} to the {self.direction}? /n /nRegardless of the result, the rest of this unit's movement points will be consumed."
        elif subject == "initial":
            if self.defending:
                text += f"{utility.capitalize(self.opponent.name)} {utility.conjugate('be', self.opponent.number)} attacking your {self.current_unit.name} at ({str(self.current_unit.x)}, {str(self.current_unit.y)})."
            else:
                text += f"Your {self.current_unit.name} {utility.conjugate('be', self.current_unit.number)} attacking the {self.opponent.name} at ({str(self.current_unit.x)}, {str(self.current_unit.y)})."

        elif subject == "modifier_breakdown":
            text += f"The {self.current_unit.name} {utility.conjugate('attempt', self.current_unit.number)} to defeat the {self.opponent.name}. /n /n"

            if self.current_unit.veteran:
                text += f"The {self.current_unit.officer.name} can roll twice and pick the higher result. /n"

            if self.current_unit.is_battalion:
                if self.current_unit.battalion_type == "imperial":
                    text += "Your professional imperial soldiers will receive a +2 bonus after their roll. /n"
                else:
                    text += "Though your African soldiers are not accustomed to using modern equipment, they will receive a +1 bonus after their roll. /n"
            elif self.current_unit.is_safari:
                if self.opponent.npmob_type == "beast":
                    text += "Your safari is trained in hunting beasts and will receive a +2 bonus after their roll. /n"
                else:
                    text += "Your safari is not accustomed to conventional combat and will receive a -1 penalty after their roll. /n"
            else:
                text += f"As a non-military unit, your {self.current_unit.name} will receive a -1 penalty after their roll. /n"

            if self.current_unit.disorganized:
                text += f"The {self.current_unit.name} {utility.conjugate('be', self.current_unit.number)} disorganized and will receive a -1 penalty after their roll. /n"
            elif self.opponent.disorganized:
                if self.opponent.npmob_type == "beast":
                    text += f"The {self.opponent.name} {utility.conjugate('be', self.opponent.number)} injured and will receive a -1 after its roll. /n"
                else:
                    text += f"The {self.opponent.name} {utility.conjugate('be', self.opponent.number)} disorganized and will receive a -1 after their roll. /n"

            if self.opponent.npmob_type == "beast" and not self.current_unit.is_safari:
                text += f"The {self.current_unit.name} {utility.conjugate('be', self.current_unit.number)} not trained in hunting beasts and will receive a -1 penalty after their roll. /n"

            if self.current_unit.images[0].current_cell.has_intact_building("fort"):
                text += f"The fort in this tile grants your {self.current_unit.name} a +1 bonus after their roll. /n"

            if self.current_unit.veteran:
                text += "The outcome will be based on the difference between your highest roll and the enemy's roll. /n /n"
            else:
                text += "The outcome will be based on the difference between your roll and the enemy's roll. /n /n"
        elif subject == "opponent_roll":
            text += f"The enemy rolled a {str(self.opponent_roll_result)}"
            if self.opponent_roll_modifier > 0:
                text += f" + {str(self.opponent_roll_modifier)} = {str(self.opponent_roll_result + self.opponent_roll_modifier)}"
            elif self.opponent_roll_modifier < 0:
                text += f" - {str(self.opponent_roll_modifier * -1)} = {str(self.opponent_roll_result + self.opponent_roll_modifier)}"
            text += " /n"
        elif subject == "critical_failure":  # lose
            if self.defending:
                if self.opponent.npmob_type == "beast":
                    self.public_opinion_change = random.randrange(1, 4) * -1
                    if self.current_unit.number == 1:
                        text += f"The {self.opponent.name} slaughtered your {self.current_unit.name}. /n /n"
                    else:
                        text += f"The {self.opponent.name} slaughtered most of your {self.current_unit.name} and the survivors deserted, promising to never return. /n /n"
                    killed_by_beast_flavor = [
                        "Onlookers in Europe wonder how the world's greatest empire could be bested by mere beasts. /n /n",
                        "Parliament concludes that its subsidies are being wasted on incompetents who can't deal with a few wild animals.",
                        "Sensationalized news stories circulate of 'brave conquerors' aimlessly wandering the jungle at the mercy of beasts, no better than savages.",
                    ]
                    text += f"{random.choice(killed_by_beast_flavor)} Public opinion has decreased by {self.public_opinion_change * -1}. /n /n"
                else:
                    self.public_opinion_change = random.randrange(-3, 4)
                    if self.current_unit.number == 1:
                        phrase = "was "
                    else:
                        phrase = "were all "
                    if self.opponent.origin_village.has_cannibals():
                        ending = "dragged off screaming"
                    else:
                        ending = "either slain or captured"

                    text += f"The {self.opponent.name} decisively defeated your {self.current_unit.name}, who {phrase} {ending}. /n /n"

                    if self.public_opinion_change > 0:
                        killed_by_natives_flavor = [
                            "Onlookers in Europe rally in support of their beleaguered heroes overseas. /n /n",
                            "Parliament realizes that your company will require increased subsidies if these savages are to be shown their proper place.",
                            "Sensationalized news stories circulate of ungrateful savages attempting to resist their benevolent saviors.",
                        ]
                        text += f"{random.choice(killed_by_natives_flavor)} Public opinion has increased by {self.public_opinion_change}. /n /n"
                    elif self.public_opinion_change < 0:
                        killed_by_natives_flavor = [
                            "Onlookers in Europe wonder how the world's greatest empire could be bested by mere savages. /n /n",
                            "Parliament concludes that its subsidies are being wasted on incompetents who can't deal with a few savages and considers lowering them in the future.",
                            "Sensationalized news stories circulate of indolent ministers sending the empire's finest to die in distant jungles.",
                        ]
                        text += f"{random.choice(killed_by_natives_flavor)} Public opinion has decreased by {self.public_opinion_change * -1}. /n /n"
            else:
                if self.opponent.npmob_type == "beast":
                    text += f"Your {self.current_unit.name} were slowly picked off as they tracked the {self.opponent.name} to its lair. The survivors eventually fled in terror and will be vulnerable to counterattack. /n /n"
                else:
                    text += f"The {self.opponent.name} decisively routed your {self.current_unit.name}, who {utility.conjugate('be', self.opponent.number)} scattered and will be vulnerable to counterattack. /n /n"

        elif subject == "failure":  # draw
            if self.defending:
                if (
                    self.opponent.last_move_direction[0] > 0
                ):  # if enemy attacked by going east
                    retreat_direction = "west"
                elif (
                    self.opponent.last_move_direction[0] < 0
                ):  # if enemy attacked by going west
                    retreat_direction = "east"
                elif (
                    self.opponent.last_move_direction[1] > 0
                ):  # if enemy attacked by going north
                    retreat_direction = "south"
                elif (
                    self.opponent.last_move_direction[1] < 0
                ):  # if enemy attacked by going south
                    retreat_direction = "north"
                if self.opponent.npmob_type == "beast":
                    text += f"Your {self.current_unit.name} managed to scare off the attacking {self.opponent.name}, which was seen running to the {retreat_direction}. /n /n"
                else:
                    text += f"Your {self.current_unit.name} managed to repel the attacking {self.opponent.name}, who {utility.conjugate('be', self.opponent.number, 'preterite')} seen withdrawing to the {retreat_direction}. /n /n"
            else:
                if self.opponent.npmob_type == "beast":
                    text += f"Your {self.current_unit.name} failed to track the {self.opponent.name} to its lair and {utility.conjugate('be', self.current_unit.number, 'preterite')} forced to withdraw. /n /n"
                else:
                    text += f"Your {self.current_unit.name} failed to push back the defending {self.opponent.name} and {utility.conjugate('be', self.current_unit.number, 'preterite')} forced to withdraw. /n /n"
        elif subject == "success":  # win
            if self.defending:
                if (
                    self.opponent.last_move_direction[0] > 0
                ):  # if enemy attacked by going east
                    retreat_direction = "west"
                elif (
                    self.opponent.last_move_direction[0] < 0
                ):  # if enemy attacked by going west
                    retreat_direction = "east"
                elif (
                    self.opponent.last_move_direction[1] > 0
                ):  # if enemy attacked by going north
                    retreat_direction = "south"
                elif (
                    self.opponent.last_move_direction[1] < 0
                ):  # if enemy attacked by going south
                    retreat_direction = "north"
                if self.opponent.npmob_type == "beast":
                    text += f"Your {self.current_unit.name} injured and scared off the attacking {self.opponent.name}, which was seen running to the {retreat_direction} and will be vulnerable as it heals. /n /n"
                else:
                    text += f"Your {self.current_unit.name} decisively routed the attacking {self.opponent.name}, who {utility.conjugate('be', self.opponent.number, 'preterite')} seen scattering to the {retreat_direction} and will be vulnerable to counterattack. /n /n"
            else:
                if self.opponent.npmob_type == "beast":
                    text += f"Your {self.current_unit.name} tracked down and killed the {self.opponent.name}. /n /n"
                    self.public_relations_change = random.randrange(1, 7)
                    text += f"Sensationalized stories of your safari's exploits and the death of the {self.opponent.name} increase public opinion by {str(self.public_relations_change)}. /n /n"
                else:
                    text += f"Your {self.current_unit.name} decisively defeated and destroyed the {self.opponent.name}. /n /n"
        elif (
            subject == "critical_success"
        ):  # win with a 6 and correct unit/enemy combination to promote - civilian units can't promote from defensive combat
            text += self.generate_notification_text("success")
            text += f"This {self.current_unit.name}'s {self.current_unit.officer.name} is now a veteran. /n /n"
        return text

    def generate_current_roll_modifier(self, opponent=False):
        """
        Description:
            Calculates and returns the current flat roll modifier for this action - this is always applied, while many modifiers are applied only half the time.
                A positive modifier increases the action's success chance and vice versa
        Input:
            None
        Output:
            int: Returns the current flat roll modifier for this action
        """
        if opponent:
            roll_modifier = self.opponent.get_combat_modifier()
        else:
            roll_modifier = super().generate_current_roll_modifier()
            roll_modifier += self.current_unit.get_combat_modifier(
                opponent=self.opponent, include_tile=True
            )
        return roll_modifier

    def on_click(self, unit, on_click_info_dict=None):
        """
        Description:
            Used when the player clicks a linked action button - checks if the unit can do the action, proceeding with 'start' if applicable
        Input:
            pmob unit: Unit selected when the linked button is clicked
        Output:
            None
        """
        self.x_change = on_click_info_dict["x_change"]
        self.y_change = on_click_info_dict["y_change"]
        if on_click_info_dict.get("attack_confirmed", False):
            return False
        else:
            future_cell = unit.grid.find_cell(
                self.x_change + unit.x, self.y_change + unit.y
            )
            opponent = "none"
            if unit.is_battalion:
                opponent = future_cell.get_best_combatant("npmob")
                self.action_type = "combat"
            elif unit.is_safari:
                opponent = future_cell.get_best_combatant("npmob", "beast")
                self.action_type = "hunting"
            if opponent == "none":
                if (
                    unit.is_battalion
                    and not future_cell.get_best_combatant("npmob", "beast") == "none"
                ) or (
                    unit.is_safari
                    and not future_cell.get_best_combatant("npmob") == "none"
                ):  # if wrong type of defender present
                    if unit.is_battalion:
                        text_utility.print_to_screen("Battalions cannot attack beasts.")
                    elif unit.is_safari:
                        text_utility.print_to_screen("Safaris can only attack beasts.")
                else:
                    return False
            elif super().on_click(unit):
                self.current_unit = unit
                if self.x_change > 0:
                    self.direction = "east"
                elif self.x_change < 0:
                    self.direction = "west"
                elif self.y_change > 0:
                    self.direction = "north"
                elif self.y_change < 0:
                    self.direction = "south"
                else:
                    self.direction = "none"
                if (
                    not on_click_info_dict["attack_confirmed"]
                ) and opponent != "none":  # if enemy in destination tile and attack not confirmed yet
                    self.opponent = opponent
                    self.defending = False
                    self.start(unit)
                    unit.create_cell_icon(
                        unit.x + self.x_change,
                        unit.y + self.y_change,
                        "misc/attack_mark/" + self.direction + ".png",
                    )
            return True

    def pre_start(self, unit):
        """
        Description:
            Prepares for starting an action starting with roll modifiers, setting ongoing action, etc.
        Input:
            pmob unit: Unit selected when the linked button is clicked
        Output:
            none
        """
        super().pre_start(unit)
        self.current_max_crit_fail = 0
        self.current_min_success = 0
        self.current_max_crit_fail = 0
        if (unit.is_safari and self.opponent.npmob_type == "beast") or (
            unit.is_battalion and self.opponent.npmob_type != "beast"
        ):
            self.current_min_crit_success = 6
        else:
            self.current_min_crit_success = 7
        self.public_relations_change = 0

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
                    "message": action_utility.generate_risk_message(self, unit)
                    + self.generate_notification_text("confirmation"),
                    "choices": [
                        {
                            "on_click": (self.middle, [{"defending": False}]),
                            "tooltip": ["Starts attack"],
                            "message": "Attack",
                        },
                        {
                            "on_click": (
                                self.current_unit.clear_attached_cell_icons,
                                [],
                            ),
                            "tooltip": ["Stop attack"],
                            "message": "Stop attack",
                        },
                    ],
                }
            )

    def get_price(self):
        """
        Description:
            Calculates and returns the price of this action
        Input:
            None
        Output:
            float: Returns price of this action
        """
        if self.defending:
            return 0
        else:
            return super().get_price()

    def generate_audio(self, subject):
        """
        Description:
            Returns list of audio dicts of sounds to play when notification appears, based on the inputted subject and other current circumstances
        Input:
            string subject: Determines sound dicts
        Output:
            dictionary list: Returns list of sound dicts for inputted subject
        """
        audio = super().generate_audio(subject)
        if subject == "initial":
            if self.current_unit.is_battalion or self.current_unit.is_safari:
                audio.append("effects/bolt_action_1")
        elif subject == "roll_started":
            if self.current_unit.is_battalion or self.current_unit.is_safari:
                audio.append("effects/gunfire")
        return audio

    def middle(self, combat_info_dict=None):
        """
        Description:
            Controls the campaign process, determining and displaying its result through a series of notifications
        Input:
            None
        Output:
            None
        """
        constants.notification_manager.set_lock(True)
        self.defending = combat_info_dict.get("defending", False)
        self.opponent = combat_info_dict.get("opponent", self.opponent)
        self.current_unit = combat_info_dict.get("current_unit", self.current_unit)
        if (
            self.defending
        ):  # if being attacked on main grid, move minimap there to show location
            self.pre_start(
                self.current_unit
            )  # do action set up if defense skipped to middle stage
            if self.current_unit.sentry_mode:
                self.current_unit.set_sentry_mode(False)
            if status.strategic_map_grid in self.current_unit.grids:
                status.minimap_grid.calibrate(self.current_unit.x, self.current_unit.y)
                self.current_unit.select()
                actor_utility.calibrate_actor_info_display(
                    status.mob_info_display, self.current_unit
                )  # should solve issue with incorrect unit displayed during combat causing issues with combat notifications
        else:
            self.current_unit.clear_attached_cell_icons()
            self.current_unit.move(self.x_change, self.y_change, True)

        self.roll_lists = []
        if self.current_unit.veteran:
            num_dice = 2
        else:
            num_dice = 1

        self.roll_result = 0

        price = self.process_payment()

        insert_index = len(constants.notification_manager.notification_queue)
        # roll messages should be inserted between any previously queued notifications and any minister messages that appear as a result of the roll

        self.current_roll_modifier = self.generate_current_roll_modifier(opponent=False)
        self.opponent_roll_modifier = self.generate_current_roll_modifier(opponent=True)
        if not self.defending:
            action_type = self.action_type
            minister_rolls = self.current_unit.controlling_minister.attack_roll_to_list(  # minister rolls need to be made with enemy roll in mind, as corrupt result needs to be inconclusive
                self.current_roll_modifier,
                self.opponent_roll_modifier,
                self.opponent,
                price,
                action_type,
                num_dice,
            )
            results = minister_rolls
        elif (self.current_unit.is_safari and self.opponent.npmob_type == "beast") or (
            self.current_unit.is_battalion and self.opponent.npmob_type != "beast"
        ):
            # Minister/country 'combat' modifiers don't apply on defense because no roll type is specified in no_corruption_roll, while unit modifiers do apply on defense
            #   Defense is a more spontaneous action that should only rely on what is immediately on-site, but this could be modified in the future
            results = [self.opponent.combat_roll()] + [
                self.current_unit.controlling_minister.no_corruption_roll(6)
                for i in range(num_dice)
            ]
        else:
            results = [self.opponent.combat_roll()] + [
                random.randrange(1, 7) for i in range(num_dice)
            ]  # civilian ministers don't get to roll for combat with their units
        for index, current_result in enumerate(results):
            if index > 0:  # If not enemy roll
                results[index] = max(
                    min(current_result + self.random_unit_modifier(), 6), 1
                )  # Adds unit-specific modifiers

        if constants.effect_manager.effect_active("ministry_of_magic"):
            results = [1] + [6 for i in range(num_dice)]
        elif constants.effect_manager.effect_active("nine_mortal_men"):
            results = [6] + [1 for i in range(num_dice)]

        self.opponent_roll_result = results.pop(0)  # Enemy roll is index 0
        roll_types = (self.name.capitalize() + " roll", "second")
        for index in range(num_dice):
            self.roll_lists.append(
                dice_utility.combat_roll_to_list(
                    6, roll_types[index], results[index], self.current_roll_modifier
                )
            )

        attached_interface_elements = []
        attached_interface_elements = self.generate_attached_interface_elements("dice")

        for roll_list in self.roll_lists:
            self.roll_result = max(roll_list[0], self.roll_result)
        self.total_roll_result = (
            self.roll_result
            + self.current_roll_modifier
            - (self.opponent_roll_result + self.opponent_roll_modifier)
        )

        constants.notification_manager.display_notification(
            {
                "message": self.generate_notification_text("initial"),
                "notification_type": "action",
                "audio": self.generate_audio("initial"),
                "attached_interface_elements": attached_interface_elements,
                "transfer_interface_elements": True,
            },
            insert_index=insert_index,
        )

        text = self.generate_notification_text("modifier_breakdown")
        roll_message = self.generate_notification_text("roll_message")

        constants.notification_manager.display_notification(
            {
                "message": text + roll_message,
                "notification_type": "action",
                "transfer_interface_elements": True,
            },
            insert_index=insert_index + 1,
        )

        constants.notification_manager.display_notification(
            {
                "message": text + "Rolling... ",
                "notification_type": "roll",
                "transfer_interface_elements": True,
                "audio": self.generate_audio("roll_started"),
            },
            insert_index=insert_index + 2,
        )

        constants.notification_manager.set_lock(
            False
        )  # locks notifications so that corruption messages will occur after the roll notification

        for roll_list in self.roll_lists:
            text += roll_list[1]
        text += self.generate_notification_text("opponent_roll")

        if len(self.roll_lists) > 1:
            text += "The higher result, " + str(self.roll_result) + ", was used. /n"
        else:
            text += "/n"

        if self.total_roll_result <= -2:
            description = "DEFEAT"
        elif self.total_roll_result <= 1:
            description = "STALEMATE"
        else:
            description = "VICTORY"
        text += "Overall result: /n"
        text += (
            str(self.roll_result + self.current_roll_modifier)
            + " - "
            + str(self.opponent_roll_result + self.opponent_roll_modifier)
            + " = "
            + str(self.total_roll_result)
            + ": "
            + description
            + " /n /n"
        )

        constants.notification_manager.display_notification(
            {
                "message": text + "Click to remove this notification. /n /n",
                "notification_type": "action",
                "transfer_interface_elements": True,
                "on_remove": self.complete,
                "audio": self.generate_audio("roll_finished"),
            }
        )

        if self.total_roll_result <= -2:
            result = "critical_failure"
        elif self.total_roll_result <= 1:
            result = "failure"
        else:
            result = "success"
            if (
                not self.current_unit.veteran
            ) and self.roll_result >= self.current_min_crit_success:
                result = "critical_success"

        text += self.generate_notification_text(result)

        constants.notification_manager.display_notification(
            {
                "message": text + "Click to remove this notification. /n /n",
                "notification_type": "action",
                "attached_interface_elements": self.generate_attached_interface_elements(
                    result
                ),
            }
        )

    def complete(self):
        """
        Description:
            Used when the player finishes rolling, shows the action's results and makes any changes caused by the result
        Input:
            None
        Output:
            None
        """
        combat_cell = self.current_unit.images[0].current_cell
        if self.total_roll_result <= -2:  # defeat
            if self.defending:
                self.current_unit.die()
                if combat_cell.get_best_combatant("pmob") == "none":
                    self.opponent.kill_noncombatants()
                    self.opponent.damage_buildings()
                    if self.opponent.npmob_type == "beast":
                        self.opponent.set_hidden(True)
                else:  # return to original tile if non-defenseless enemies still in other tile, can't be in tile with enemy units or have more than 1 offensive combat per turn
                    self.opponent.retreat()
                constants.public_opinion_tracker.change(self.public_opinion_change)
            else:
                self.current_unit.retreat()
                self.current_unit.set_disorganized(True)

        elif self.total_roll_result <= 1:  # draw
            if self.defending:
                self.opponent.retreat()
            else:
                self.current_unit.retreat()

        else:  # victory
            if self.defending:
                self.opponent.retreat()
                self.opponent.set_disorganized(True)
            else:
                if (
                    len(combat_cell.contained_mobs) > 2
                ):  # len == 2 if only attacker and defender in tile
                    self.current_unit.retreat()  # attacker retreats in draw or if more defenders remaining
                elif (
                    self.current_unit.movement_points
                    < self.current_unit.get_movement_cost(0, 0, True)
                ):  # if can't afford movement points to stay in attacked tile
                    constants.notification_manager.display_notification(
                        {
                            "message": "While the attack was successful, this unit did not have the "
                            + str(self.current_unit.get_movement_cost(0, 0, True))
                            + " movement points required to fully move into the attacked tile and was forced to withdraw. /n /n",
                        }
                    )
                    self.current_unit.retreat()
                self.opponent.die()
                if self.opponent.npmob_type != "beast":
                    constants.evil_tracker.change(4)
                else:
                    constants.public_opinion_tracker.change(
                        self.public_relations_change
                    )
                    constants.achievement_manager.achieve("Big Game Hunter")

        if not self.defending:
            self.current_unit.set_movement_points(0)
            if (
                combat_cell.terrain == "water"
                and combat_cell.y > 0
                and not self.current_unit.can_swim_river
            ):  # if attacked river and can't swim, become disorganized after combat
                self.current_unit.set_disorganized(True)

        super().complete()

        if len(status.attacker_queue) > 0:
            status.attacker_queue.pop(0).attempt_local_combat()
        elif flags.enemy_combat_phase:  # if enemy combat phase done, go to player turn
            turn_management_utility.start_player_turn()
        else:
            for current_pmob in status.pmob_list:
                if current_pmob.is_vehicle:
                    current_pmob.reembark()
            for current_building in status.building_list:
                if current_building.building_type == "resource":
                    current_building.reattach_work_crews()
