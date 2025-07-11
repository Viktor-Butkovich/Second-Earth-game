# Contains all functionality for combat

import random
from typing import List
from modules.action_types import action
from modules.util import (
    action_utility,
    actor_utility,
    dice_utility,
    utility,
    turn_management_utility,
)
from modules.constants import constants, status, flags


class combat(action.action):
    """
    Action for battalion to attack or for any unit to defend
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

    @property
    def tooltip_text(self) -> List[List[str]]:
        """
        Provides the tooltip for this object
        """
        message = []
        # final_movement_cost = status.displayed_mob.get_movement_cost(
        #    tooltip_info_dict["x_change"], tooltip_info_dict["y_change"]
        # )
        message.append(
            "Attacking an enemy unit costs 5 money and requires only 1 movement point, but staying in the enemy's location afterward would require the usual movement"
        )
        # text = f"Staying afterward would cost {final_movement_cost - 1} more movement point{utility.generate_plural(final_movement_cost - 1)} because the adjacent location has {tooltip_info_dict['adjacent_location'].terrain.replace('_', ' ')} terrain"

        # local_infrastructure = tooltip_info_dict["local_infrastructure"]
        # adjacent_infrastructure = tooltip_info_dict["adjacent_infrastructure"]
        # if local_infrastructure and adjacent_infrastructure:
        #    text += " and connecting roads"
        # elif local_infrastructure == None and adjacent_infrastructure:
        #    text += " and no connecting roads"
        # elif local_infrastructure:
        #    text += " and no connecting roads"
        # else:
        #    text += " and no connecting roads"

        # message.append(text)
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
            background_image_id_list = (
                action_utility.generate_background_image_id_list()
            )
            pmob_image_id_list = (
                background_image_id_list
                + self.current_unit.image_dict[constants.IMAGE_ID_LIST_FULL_MOB]
                + ["misc/actor_backgrounds/pmob_outline.png"]
            )
            npmob_image_id_list = (
                background_image_id_list
                + self.opponent.image_dict[constants.IMAGE_ID_LIST_FULL_MOB]
                + ["misc/actor_backgrounds/npmob_outline.png"]
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
                    self.current_unit.controlling_minister.generate_icon_input_dict(
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
            text += f"Are you sure you want to spend {str(self.get_price())} money to attack the {self.opponent.name} to the {self.direction}? /n /nRegardless of the result, the rest of this unit's movement points will be consumed."
        elif subject == "initial":
            if self.defending:
                text += f"{utility.capitalize(self.opponent.name)} {utility.conjugate('be', self.opponent.unit_type.number)} attacking your {self.current_unit.name} at ({str(self.current_location.x)}, {str(self.current_location.y)})."
            else:
                text += f"Your {self.current_unit.name} {utility.conjugate('be', self.current_unit.unit_type.number)} attacking the {self.opponent.name} at ({str(self.current_location.x)}, {str(self.current_location.y)})."

        elif subject == "modifier_breakdown":
            text += f"The {self.current_unit.name} {utility.conjugate('attempt', self.current_unit.unit_type.number)} to defeat the {self.opponent.name}. /n /n"

            if self.current_unit.get_permission(constants.VETERAN_PERMISSION):
                text += f"The {self.current_unit.officer.name} can roll twice and pick the higher result. /n"

            if not self.current_unit.get_permission(constants.BATTALION_PERMISSION):
                text += f"As a non-military unit, your {self.current_unit.name} will receive a -1 penalty after their roll. /n"

            if self.current_unit.get_permission(constants.DISORGANIZED_PERMISSION):
                text += f"The {self.current_unit.name} {utility.conjugate('be', self.current_unit.unit_type.number)} disorganized and will receive a -1 penalty after their roll. /n"
            if self.opponent.get_permission(constants.DISORGANIZED_PERMISSION):
                text += f"The {self.opponent.name} {utility.conjugate('be', self.opponent.unit_type.number)} disorganized and will receive a -1 after their roll. /n"

            if self.current_unit.location.has_intact_building(constants.FORT):
                text += f"The fort in this location grants your {self.current_unit.name} a +1 bonus after their roll. /n"

            if self.current_unit.get_permission(constants.VETERAN_PERMISSION):
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
                self.public_opinion_change = random.randrange(-3, 4)
                if self.current_unit.unit_type.number == 1:
                    phrase = "was "
                else:
                    phrase = "were all "
                ending = "either slain or captured"

                text += f"The {self.opponent.name} decisively defeated your {self.current_unit.name}, who {phrase} {ending}. /n /n"
            else:
                text += f"The {self.opponent.name} decisively routed your {self.current_unit.name}, who {utility.conjugate('be', self.opponent.unit_type.number)} scattered and will be vulnerable to counterattack. /n /n"

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

                text += f"Your {self.current_unit.name} managed to repel the attacking {self.opponent.name}, who {utility.conjugate('be', self.opponent.unit_type.number, 'preterite')} seen withdrawing to the {retreat_direction}. /n /n"
            else:
                text += f"Your {self.current_unit.name} failed to push back the defending {self.opponent.name} and {utility.conjugate('be', self.current_unit.unit_type.number, 'preterite')} forced to withdraw. /n /n"
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
                text += f"Your {self.current_unit.name} decisively routed the attacking {self.opponent.name}, who {utility.conjugate('be', self.opponent.unit_type.number, 'preterite')} seen scattering to the {retreat_direction} and will be vulnerable to counterattack. /n /n"
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
                opponent=self.opponent, include_location=True
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
            current_location = unit.location
            future_location = current_location.world_handler.find_location(
                current_location.x + self.x_change,
                current_location.y + self.y_change,
            )
            opponent = None
            if unit.get_permission(constants.BATTALION_PERMISSION):
                opponent = future_location.get_best_combatant("npmob")
                self.action_type = "combat"
            if not opponent:
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
                    self.direction = None
                if (
                    opponent and not on_click_info_dict["attack_confirmed"]
                ):  # if enemy in destination and attack not confirmed yet
                    self.opponent = opponent
                    self.defending = False
                    self.start(unit)
                    constants.ActorCreationManager.create_interface_element(
                        input_dict={
                            "init_type": constants.HOSTED_ICON,
                            "location": future_location,
                            "image_id": [
                                {"image_id": f"misc/attack_mark/{self.direction}.png"}
                            ],
                        },
                    )
            return True

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
        self.current_max_crit_fail = 0
        self.current_min_success = 0
        self.current_max_crit_fail = 0
        if unit.get_permission(constants.BATTALION_PERMISSION):
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
            constants.NotificationManager.display_notification(
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
                            # "on_click": (
                            #    self.current_unit.clear_attached_cell_icons,
                            #    [],
                            # ),
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
            if self.current_unit.get_permission(constants.BATTALION_PERMISSION):
                audio.append("effects/bolt_action_1")
        elif subject == "roll_started":
            if self.current_unit.get_permission(constants.BATTALION_PERMISSION):
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
        constants.NotificationManager.set_lock(True)
        self.defending = combat_info_dict.get("defending", False)
        self.opponent = combat_info_dict.get("opponent", self.opponent)
        self.current_unit = combat_info_dict.get("current_unit", self.current_unit)
        if (
            self.defending
        ):  # if being attacked on main grid, move minimap there to show location
            self.pre_start(
                self.current_unit
            )  # do action set up if defense skipped to middle stage
            self.current_unit.set_permission(constants.SENTRY_MODE_PERMISSION, False)
            self.current_unit.select()

        else:
            # self.current_unit.clear_attached_cell_icons()
            self.current_unit.move(self.x_change, self.y_change, True)

        self.roll_lists = []
        if self.current_unit.get_permission(constants.VETERAN_PERMISSION):
            num_dice = 2
        else:
            num_dice = 1

        self.roll_result = 0

        price = self.process_payment()

        insert_index = len(constants.NotificationManager.notification_queue)
        # roll messages should be inserted between any previously queued notifications and any minister messages that appear as a result of the roll

        self.current_roll_modifier = self.generate_current_roll_modifier(opponent=False)
        self.opponent_roll_modifier = self.generate_current_roll_modifier(opponent=True)
        stealing = False
        if not self.defending:
            action_type = self.action_type
            (
                stealing,
                minister_rolls,
            ) = self.current_unit.controlling_minister.attack_roll_to_list(  # minister rolls need to be made with enemy roll in mind, as corrupt result needs to be inconclusive
                self.current_roll_modifier,
                self.opponent_roll_modifier,
                self.opponent,
                price,
                action_type,
                num_dice,
            )
            results = minister_rolls
        elif self.current_unit.get_permission(constants.BATTALION_PERMISSION):
            # 'combat' modifiers don't apply on defense because no roll type is specified in no_corruption_roll, while unit modifiers do apply on defense
            #   Defense is a more spontaneous action that should only rely on what is immediately on-site, but this could be modified in the future
            results = [self.opponent.combat_roll()] + [
                self.current_unit.controlling_minister.no_corruption_roll(6)
                for i in range(num_dice)
            ]
        else:
            results = [self.opponent.combat_roll()] + [
                random.randrange(1, 7) for i in range(num_dice)
            ]  # civilian ministers don't get to roll for combat with their units
        if not stealing:
            for index, current_result in enumerate(results):
                if index > 0:  # If not enemy roll
                    results[index] = max(
                        min(current_result + self.random_unit_modifier(), 6), 1
                    )  # Adds unit-specific modifiers

        if constants.EffectManager.effect_active("ministry_of_magic"):
            results = [1] + [6 for i in range(num_dice)]
        elif constants.EffectManager.effect_active("nine_mortal_men"):
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

        constants.NotificationManager.display_notification(
            {
                "message": self.generate_notification_text("initial"),
                "notification_type": constants.ACTION_NOTIFICATION,
                "audio": self.generate_audio("initial"),
                "attached_interface_elements": attached_interface_elements,
                "transfer_interface_elements": True,
            },
            insert_index=insert_index,
        )

        text = self.generate_notification_text("modifier_breakdown")
        roll_message = self.generate_notification_text("roll_message")

        constants.NotificationManager.display_notification(
            {
                "message": text + roll_message,
                "notification_type": constants.ACTION_NOTIFICATION,
                "transfer_interface_elements": True,
            },
            insert_index=insert_index + 1,
        )

        constants.NotificationManager.display_notification(
            {
                "message": text + "Rolling... ",
                "notification_type": constants.DICE_ROLLING_NOTIFICATION,
                "transfer_interface_elements": True,
                "audio": self.generate_audio("roll_started"),
            },
            insert_index=insert_index + 2,
        )

        constants.NotificationManager.set_lock(
            False
        )  # locks notifications so that corruption messages will occur after the roll notification

        for roll_list in self.roll_lists:
            text += roll_list[1]
        text += self.generate_notification_text("opponent_roll")

        if len(self.roll_lists) > 1:
            text += f"The higher result, {self.roll_result}, was used. /n"
        else:
            text += "/n"

        if self.total_roll_result <= -2:
            description = "DEFEAT"
        elif self.total_roll_result <= 1:
            description = "STALEMATE"
        else:
            description = "VICTORY"
        text += "Overall result: /n"
        text += f"{self.roll_result + self.current_roll_modifier} - {self.opponent_roll_result + self.opponent_roll_modifier} = {self.total_roll_result}: {description} /n /n"

        constants.NotificationManager.display_notification(
            {
                "message": text + "Click to remove this notification. /n /n",
                "notification_type": constants.ACTION_NOTIFICATION,
                "transfer_interface_elements": True,
                "on_remove": [(self.complete, [])],
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
                not self.current_unit.get_permission(constants.VETERAN_PERMISSION)
            ) and self.roll_result >= self.current_min_crit_success:
                result = "critical_success"

        text += self.generate_notification_text(result)

        constants.NotificationManager.display_notification(
            {
                "message": text + "Click to remove this notification. /n /n",
                "notification_type": constants.ACTION_NOTIFICATION,
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
        combat_location = self.current_unit.location
        if self.total_roll_result <= -2:  # Defeat
            if self.defending:
                self.current_unit.die()
                if not combat_location.get_best_combatant("pmob"):
                    self.opponent.kill_noncombatants()
                    self.opponent.damage_buildings()
                else:  # Return to original location if non-defenseless enemies still in other location, can't be in location with enemy units or have more than 1 offensive combat per turn
                    self.opponent.retreat()
                constants.PublicOpinionTracker.change(self.public_opinion_change)
            else:
                self.current_unit.retreat()
                self.current_unit.set_permission(
                    constants.DISORGANIZED_PERMISSION, True
                )

        elif self.total_roll_result <= 1:  # Draw
            if self.defending:
                self.opponent.retreat()
            else:
                self.current_unit.retreat()

        else:  # Victory
            if self.defending:
                self.opponent.retreat()
                if constants.ALLOW_DISORGANIZED:
                    self.opponent.set_permission(
                        constants.DISORGANIZED_PERMISSION, True
                    )
            else:
                if (
                    len(combat_location.subscribed_mobs) > 2
                ):  # len == 2 if only attacker and defender in location
                    self.current_unit.retreat()  # Attacker retreats in draw or if more defenders remaining
                elif (
                    self.current_unit.movement_points
                    < self.current_unit.get_movement_cost(0, 0, True)
                ):  # If can't afford movement points to stay in attacked location
                    constants.NotificationManager.display_notification(
                        {
                            "message": f"While the attack was successful, this unit did not have the {self.current_unit.get_movement_cost(0, 0, True)} movement points required to fully move into the attacked location and was forced to withdraw. /n /n",
                        }
                    )
                    self.current_unit.retreat()
                self.opponent.die()
                constants.EvilTracker.change(4)

        if not self.defending:
            self.current_unit.set_movement_points(0)
            if (
                combat_location.terrain == "water"
                and not self.current_unit.get_permission(constants.SWIM_PERMISSION)
            ):  # if attacked water and can't swim, become disorganized after combat
                self.current_unit.set_permission(
                    constants.DISORGANIZED_PERMISSION, True
                )

        super().complete()

        if len(status.attacker_queue) > 0:
            status.attacker_queue.pop(0).attempt_local_combat()
        elif flags.enemy_combat_phase:  # if enemy combat phase done, go to player turn
            turn_management_utility.start_player_turn()
        else:
            for current_pmob in status.pmob_list:
                if current_pmob.get_permission(constants.VEHICLE_PERMISSION):
                    current_pmob.reembark()
            for current_building in status.building_list:
                if current_building.building_type == constants.RESOURCE:
                    current_building.reattach_work_crews()
