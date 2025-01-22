# Contains functionality for actor display buttons

import random
from typing import Dict, Any
from modules.interface_types.buttons import button
from modules.util import (
    main_loop_utility,
    actor_utility,
    minister_utility,
    trial_utility,
    text_utility,
    game_transitions,
)
from modules.constructs import minister_types
from modules.constants import constants, status, flags


class embark_all_passengers_button(button):
    """
    Button that commands a vehicle to take all other mobs in its tile as passengers
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = None: pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
        Output:
            None
        """
        self.vehicle_type = None
        super().__init__(input_dict)

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a vehicle to take all other mobs in its tile as passengers
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            vehicle = status.displayed_mob
            can_embark = True
            if self.vehicle_type == constants.TRAIN_PERMISSION:
                if not vehicle.get_cell().get_inact_building(constants.TRAIN_STATION):
                    text_utility.print_to_screen(
                        "A train can only pick up passengers at a train station."
                    )
                    can_embark = False
            if can_embark:
                if vehicle.sentry_mode:
                    vehicle.set_sentry_mode(False)
                for contained_mob in vehicle.get_cell().contained_mobs:
                    passenger = contained_mob
                    if passenger.get_permission(
                        constants.PMOB_PERMISSION
                    ) and not passenger.get_permission(
                        constants.VEHICLE_PERMISSION
                    ):  # vehicles and enemies won't be picked up as passengers
                        passenger.embark_vehicle(vehicle)
                constants.sound_manager.play_sound(
                    f"voices/all aboard {random.randrange(1, 4)}",
                    radio_effect=vehicle.get_radio_effect(),
                )
        else:
            text_utility.print_to_screen(
                "You are busy and cannot embark all passengers."
            )

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn. Also updates this button to reflect a train or spaceship depending on the selected vehicle
        Input:
            None
        Output:
            boolean: Returns False if the selected vehicle has no crew, otherwise returns same as superclass
        """
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_mob = status.displayed_mob
            if displayed_mob.get_permission(constants.ACTIVE_PERMISSION):
                if (
                    displayed_mob.get_permission(constants.SPACESHIP_PERMISSION)
                    and self.vehicle_type != constants.SPACESHIP_PERMISSION
                ):
                    self.vehicle_type = constants.SPACESHIP_PERMISSION
                    self.image.set_image(f"buttons/embark_spaceship_button.png")
                elif (
                    displayed_mob.get_permission(constants.TRAIN_PERMISSION)
                    and self.vehicle_type != constants.TRAIN_PERMISSION
                ):
                    self.vehicle_type = constants.TRAIN_PERMISSION
                    self.image.set_image(f"buttons/embark_train_button.png")
        return result


class disembark_all_passengers_button(button):
    """
    Button that commands a vehicle to eject all of its passengers
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = None: pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
        Output:
            None
        """
        self.vehicle_type = None
        super().__init__(input_dict)

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a vehicle to eject all of its passengers
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            vehicle = status.displayed_mob
            can_disembark = True
            if vehicle.get_permission(constants.TRAIN_PERMISSION):
                if not vehicle.get_cell().has_building(constants.TRAIN_STATION):
                    text_utility.print_to_screen(
                        "A train can only drop off passengers at a train station."
                    )
                    can_disembark = False
            if can_disembark:
                if vehicle.sentry_mode:
                    vehicle.set_sentry_mode(False)
                if len(vehicle.contained_mobs) > 0:
                    vehicle.contained_mobs[-1].selection_sound()
                vehicle.eject_passengers()
        else:
            text_utility.print_to_screen(
                "You are busy and cannot disembark all passengers."
            )

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn. Also updates this button to reflect a train or spaceship depending on the selected vehicle
        Input:
            None
        Output:
            boolean: Returns False if the selected vehicle has no crew, otherwise returns same as superclass
        """
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_mob = status.displayed_mob
            if displayed_mob.get_permission(constants.ACTIVE_PERMISSION):
                if (
                    displayed_mob.get_permission(constants.SPACESHIP_PERMISSION)
                    and self.vehicle_type != constants.SPACESHIP_PERMISSION
                ):
                    self.vehicle_type = constants.SPACESHIP_PERMISSION
                    self.image.set_image(f"buttons/disembark_spaceship_button.png")
                elif (
                    displayed_mob.get_permission(constants.TRAIN_PERMISSION)
                    and self.vehicle_type != constants.TRAIN_PERMISSION
                ):
                    self.vehicle_type = constants.TRAIN_PERMISSION
                    self.image.set_image(f"buttons/disembark_train_button.png")
        return result


class enable_sentry_mode_button(button):
    """
    Button that enables sentry mode for a unit, causing it to not be added to the turn cycle queue
    """

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns True if the selected mob is a pmob and is not already in sentry mode, otherwise returns False
        """
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_mob = status.displayed_mob
            if not displayed_mob.get_permission(constants.PMOB_PERMISSION):
                return False
            elif displayed_mob.sentry_mode:
                return False
        return result

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button activates sentry mode for the selected unit
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            displayed_mob = status.displayed_mob
            displayed_mob.set_sentry_mode(True)
            if (
                constants.effect_manager.effect_active("promote_on_sentry")
                and displayed_mob.any_permissions(
                    constants.GROUP_PERMISSION, constants.OFFICER_PERMISSION
                )
                and not displayed_mob.get_permission(constants.VETERAN_PERMISSION)
            ):  # purely for promotion testing, not normal functionality
                displayed_mob.promote()
        else:
            text_utility.print_to_screen("You are busy and cannot enable sentry mode.")


class disable_sentry_mode_button(button):
    """
    Button that disables sentry mode for a unit, causing it to not be added to the turn cycle queue
    """

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns True if the selected mob is a pmob and is in sentry mode, otherwise returns False
        """
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_mob = status.displayed_mob
            if not displayed_mob.get_permission(constants.PMOB_PERMISSION):
                return False
            elif not displayed_mob.sentry_mode:
                return False
        return result

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button deactivates sentry mode for the selected unit
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            displayed_mob = status.displayed_mob
            displayed_mob.set_sentry_mode(False)
            actor_utility.calibrate_actor_info_display(
                status.mob_info_display, displayed_mob
            )
        else:
            text_utility.print_to_screen("You are busy and cannot disable sentry mode.")


class enable_automatic_replacement_button(button):
    """
    Button that enables automatic attrition replacement for a unit or one of its components
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = None: pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'target_type': string value - Type of unit/subunit targeted by this button, such as 'unit', 'officer', or 'worker'
        Output:
            None
        """
        self.target_type = input_dict["target_type"]
        super().__init__(input_dict)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns True if the targeted unit component is present and does not already have automatic replacement, otherwise returns False
        """
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_mob = status.displayed_mob
            if not displayed_mob.get_permission(constants.PMOB_PERMISSION):
                return False
            elif displayed_mob.get_permission(constants.VEHICLE_PERMISSION):
                return False
            elif (
                displayed_mob.get_permission(constants.GROUP_PERMISSION)
                and self.target_type == "unit"
            ):
                return False
            elif (
                not displayed_mob.get_permission(constants.GROUP_PERMISSION)
            ) and self.target_type != "unit":
                return False
            elif (
                (self.target_type == "unit" and displayed_mob.automatically_replace)
                or (
                    self.target_type == "worker"
                    and displayed_mob.worker.automatically_replace
                )
                or (
                    self.target_type == "officer"
                    and displayed_mob.officer.automatically_replace
                )
            ):
                return False
        return result

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button enables automatic replacement for the selected unit
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            displayed_mob = status.displayed_mob
            if self.target_type == "unit":
                target = displayed_mob
            elif self.target_type == "worker":
                target = displayed_mob.worker
            elif self.target_type == "officer":
                target = displayed_mob.officer
            target.set_automatically_replace(True)
        else:
            text_utility.print_to_screen(
                "You are busy and cannot enable automatic replacement."
            )


class disable_automatic_replacement_button(button):
    """
    Button that disables automatic attrition replacement for a unit or one of its components
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = None: pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'target_type': string value - Type of unit/subunit targeted by this button, such as 'unit', 'officer', or 'worker'
        Output:
            None
        """
        self.target_type = input_dict["target_type"]
        input_dict["button_type"] = "disable automatic replacement"
        super().__init__(input_dict)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns True if the targeted unit component is present and has automatic replacement, otherwise returns False
        """
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_mob = status.displayed_mob
            if not displayed_mob.get_permission(constants.PMOB_PERMISSION):
                return False
            elif displayed_mob.get_permission(constants.VEHICLE_PERMISSION):
                return False
            elif (
                displayed_mob.get_permission(constants.GROUP_PERMISSION)
                and self.target_type == "unit"
            ):
                return False
            elif (
                not displayed_mob.get_permission(constants.GROUP_PERMISSION)
            ) and self.target_type != "unit":
                return False
            elif (
                (self.target_type == "unit" and not displayed_mob.automatically_replace)
                or (
                    self.target_type == "worker"
                    and not displayed_mob.worker.automatically_replace
                )
                or (
                    self.target_type == "officer"
                    and not displayed_mob.officer.automatically_replace
                )
            ):
                return False
        return result

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button disables automatic replacement for the selected unit
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            displayed_mob = status.displayed_mob
            if self.target_type == "unit":
                target = displayed_mob
            elif self.target_type == "worker":
                target = displayed_mob.worker
            elif self.target_type == "officer":
                target = displayed_mob.officer
            target.set_automatically_replace(False)
        else:
            text_utility.print_to_screen(
                "You are busy and cannot disable automatic replacement."
            )


class end_unit_turn_button(button):
    """
    Button that ends a unit's turn, removing it from the current turn's turn cycle queue
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = None: pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
        Output:
            None
        """
        input_dict["button_type"] = "end unit turn"
        super().__init__(input_dict)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns True if the selected mob is a pmob in the turn queue, otherwise returns False
        """
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_mob = status.displayed_mob
            if not displayed_mob.get_permission(constants.PMOB_PERMISSION):
                return False
            elif not displayed_mob in status.player_turn_queue:
                return False
        return result

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button removes the selected unit from the current turn's turn cycle queue
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            status.displayed_mob.remove_from_turn_queue()
            game_transitions.cycle_player_turn()
        else:
            text_utility.print_to_screen(
                "You are busy and cannot end this unit's turn."
            )


class remove_work_crew_button(button):
    """
    Button that removes a work crew from a building
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = None: pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'attached_label': label value - Label that this button is attached to
                'building_type': Type of building to remove workers from, like constants.RESOURCE
        Output:
            None
        """
        self.building_type = input_dict["building_type"]
        super().__init__(input_dict)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if there is not a corresponding work crew to remove, otherwise returns same as superclass
        """
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            if not self.attached_label.attached_list[
                self.attached_label.list_index
            ].get_permission(constants.IN_BUILDING_PERMISSION):
                return False
        return result

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button removes a work crew from a building
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            self.attached_label.attached_list[
                self.attached_label.list_index
            ].leave_building(
                self.attached_label.actor.cell.contained_buildings[self.building_type]
            )
        else:
            text_utility.print_to_screen(
                "You are busy and cannot remove a work crew from a building."
            )


class disembark_vehicle_button(button):
    """
    Button that disembarks a passenger from a vehicle
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = None: pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'attached_label': label value - Label that this button is attached to
        Output:
            None
        """
        self.vehicle_type = None
        super().__init__(input_dict)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn. Also updates this button to reflect a train or spaceship depending on the selected vehicle
        Input:
            None
        Output:
            boolean: Returns False if there is not a corresponding passenger to disembark, otherwise returns same as superclass
        """
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            if not self.attached_label.attached_list[
                self.attached_label.list_index
            ].get_permission(constants.IN_VEHICLE_PERMISSION):
                return False
            if (
                self.attached_label.actor.get_permission(constants.SPACESHIP_PERMISSION)
                and self.vehicle_type != constants.SPACESHIP_PERMISSION
            ):
                self.vehicle_type = constants.SPACESHIP_PERMISSION
                self.image.set_image(f"buttons/disembark_spaceship_button.png")

            elif (
                self.attached_label.actor.get_permission(constants.TRAIN_PERMISSION)
                and self.vehicle_type != constants.TRAIN_PERMISSION
            ):
                self.vehicle_type = constants.TRAIN_PERMISSION
                self.image.set_image(f"buttons/disembark_train_button.png")
        return result

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button disembarks a passenger from a vehicle
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            if len(self.attached_label.actor.contained_mobs) > 0:
                can_disembark = True
                if self.vehicle_type == constants.TRAIN_PERMISSION:
                    if not self.attached_label.actor.images[
                        0
                    ].current_cell.contained_buildings[constants.TRAIN_STATION]:
                        text_utility.print_to_screen(
                            "A train can only drop off passengers at a train station."
                        )
                        can_disembark = False
                if can_disembark:
                    passenger = self.attached_label.attached_list[
                        self.attached_label.list_index
                    ]
                    if passenger.sentry_mode:
                        passenger.set_sentry_mode(False)
                    passenger.selection_sound()
                    self.attached_label.attached_list[
                        self.attached_label.list_index
                    ].disembark_vehicle(self.attached_label.actor)
            else:
                text_utility.print_to_screen(
                    f"You must select a vehicle with passengers to disembark passengers."
                )
        else:
            text_utility.print_to_screen(f"You are busy and cannot disembark.")


class embark_vehicle_button(button):
    """
    Button that commands a selected mob to embark a vehicle of the correct type in the same tile
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = None: pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'vehicle_type': string value - Permission of vehicle this button embarks, like constants.TRAIN_PERMISSION or constants.SPACESHIP_PERMISSION
        Output:
            None
        """
        self.vehicle_type = input_dict["vehicle_type"]
        self.was_showing = False
        super().__init__(input_dict)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob cannot embark vehicles or if there is no vehicle in the tile to embark, otherwise returns same as superclass
        """
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_mob = status.displayed_mob
            result = (
                displayed_mob
                and displayed_mob.get_permission(constants.PMOB_PERMISSION)
                and not displayed_mob.get_permission(constants.VEHICLE_PERMISSION)
                and displayed_mob.get_cell().has_unit(
                    [self.vehicle_type, constants.ACTIVE_VEHICLE_PERMISSION]
                )
            )
        self.was_showing = result
        return result

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a selected mob to embark a vehicle of the correct type in the same tile
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            if status.displayed_mob.get_cell().has_unit(
                [self.vehicle_type, constants.ACTIVE_VEHICLE_PERMISSION]
            ):
                rider = status.displayed_mob
                vehicles = rider.get_cell().get_unit(
                    [self.vehicle_type, constants.ACTIVE_VEHICLE_PERMISSION],
                    get_all=True,
                )
                can_embark = True
                if vehicles[0].get_permission(constants.TRAIN_PERMISSION):
                    if (
                        not vehicles[0]
                        .get_cell()
                        .contained_buildings[constants.TRAIN_STATION]
                    ):
                        text_utility.print_to_screen(
                            "A train can only pick up passengers at a train station."
                        )
                        can_embark = False
                if can_embark:
                    rider.set_sentry_mode(False)
                    if len(vehicles) > 1:
                        vehicles[0].select()
                        for vehicle in vehicles:
                            constants.notification_manager.display_notification(
                                {
                                    "message": f"There are {len(vehicles)} possible vehicles to embark - click next until you find the vehicle you would like to embark. /n /n",
                                    "choices": [
                                        {
                                            "on_click": (
                                                self.finish_embark_vehicle,
                                                [rider, vehicle],
                                            ),
                                            "tooltip": ["Embarks this vehicle"],
                                            "message": "Embark",
                                        },
                                        {
                                            "on_click": (
                                                self.skip_embark_vehicle,
                                                [
                                                    rider,
                                                    vehicles,
                                                    vehicles.index(vehicle),
                                                ],
                                            ),
                                            "tooltip": [
                                                "Cycles to the next possible vehicle"
                                            ],
                                            "message": "Next vehicle",
                                        },
                                    ],
                                }
                            )
                    else:
                        vehicle = vehicles[0]
                        if vehicle.sentry_mode:
                            vehicle.set_sentry_mode(False)
                        rider.embark_vehicle(vehicle)
                        constants.sound_manager.play_sound(
                            f"voices/all aboard {random.randrange(1, 4)}",
                            radio_effect=vehicle.get_radio_effect(),
                        )
            else:
                text_utility.print_to_screen(
                    f"You must select a unit in the same tile as a crewed vehicle to embark."
                )
        else:
            text_utility.print_to_screen(f"You are busy and cannot embark.")

    def finish_embark_vehicle(self, rider, vehicle):
        """
        Description:
            Selects a vehicle to embark when multiple vehicle options are available, called by choice notification
        Input:
            pmob rider: Unit embarking vehicle
            vehicle vehicle: Vehicle to embark
        Output:
            None
        """
        constants.notification_manager.clear_notification_queue()  # Skip remaining embark notifications
        vehicle.set_sentry_mode(False)
        rider.embark_vehicle(vehicle)
        constants.sound_manager.play_sound(
            f"voices/all aboard {random.randrange(1, 4)}",
            radio_effect=vehicle.get_radio_effect(),
        )

    def skip_embark_vehicle(self, rider, vehicles, index):
        """
        Description:
            Selects the next possible vehicle to embark when multiple vehicle options are available, called by choice notification
        Input:
            pmob rider: Unit embarking vehicle
            vehicle vehicle: Vehicle to embark
        Output:
            None
        """
        if index == len(vehicles) - 1:
            rider.select()
        else:
            vehicles[index + 1].select()


class cycle_passengers_button(button):
    """
    Button that cycles the order of passengers displayed in a vehicle
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = None: pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
        Output:
            None
        """
        self.vehicle_type = None
        super().__init__(input_dict)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not a vehicle or if the vehicle does not have enough passengers to cycle through, otherwise returns same as superclass
        """
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_mob = status.displayed_mob
            if not displayed_mob.get_permission(constants.VEHICLE_PERMISSION):
                return False
            elif (
                not len(displayed_mob.contained_mobs) > 3
            ):  # only show if vehicle with 3+ passengers
                return False
            if displayed_mob.get_permission(constants.SPACESHIP_PERMISSION):
                self.vehicle_type = constants.SPACESHIP_PERMISSION
            elif displayed_mob.get_permission(constants.TRAIN_PERMISSION):
                self.vehicle_type = constants.TRAIN_PERMISSION
        return result

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button cycles the order of passengers displayed in a vehicle
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            displayed_mob = status.displayed_mob
            moved_mob = displayed_mob.contained_mobs.pop(0)
            displayed_mob.contained_mobs.append(moved_mob)
            actor_utility.calibrate_actor_info_display(
                status.mob_info_display, displayed_mob
            )  # updates mob info display list to show changed passenger order
        else:
            text_utility.print_to_screen("You are busy and cannot cycle passengers.")


class cycle_work_crews_button(button):
    """
    Button that cycles the order of work crews in a building
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = None: pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'attached_label': label value - Label that this button is attached to
        Output:
            None
        """
        self.previous_showing_result = False
        super().__init__(input_dict)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if the displayed tile's cell has a resource building containing more than 3 work crews, otherwise returns False
        """
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_tile = status.displayed_tile
            if not displayed_tile.cell.contained_buildings[constants.RESOURCE]:
                self.previous_showing_result = False
                return False
            elif (
                not len(
                    displayed_tile.cell.contained_buildings[
                        constants.RESOURCE
                    ].contained_work_crews
                )
                > 3
            ):  # only show if building with 3+ work crews
                self.previous_showing_result = False
                return False
        if self.previous_showing_result == False and result == True:
            self.previous_showing_result = result
            self.attached_label.set_label(
                self.attached_label.message
            )  # update label to update this button's location
        self.previous_showing_result = result
        return result

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button cycles the order of work crews displayed in a building
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            displayed_tile = status.displayed_tile
            moved_mob = displayed_tile.cell.contained_buildings[
                constants.RESOURCE
            ].contained_work_crews.pop(0)
            displayed_tile.cell.contained_buildings[
                constants.RESOURCE
            ].contained_work_crews.append(moved_mob)
            actor_utility.calibrate_actor_info_display(
                status.tile_info_display, displayed_tile
            )  # updates tile info display list to show changed work crew order
        else:
            text_utility.print_to_screen("You are busy and cannot cycle work crews.")


class work_crew_to_building_button(button):
    """
    Button that commands a work crew to work in a certain type of building in its tile
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = None: pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'building_type': string value - Type of buliding this button attaches workers to, like constants.RESOURCE
        Output:
            None
        """
        self.building_type = input_dict["building_type"]
        self.attached_work_crew = None
        self.attached_building = None
        super().__init__(input_dict)

    def update_info(self):
        """
        Description:
            Updates the building this button assigns workers to depending on the buildings present in this tile
        Input:
            None
        Output:
            None
        """
        self.attached_work_crew = status.displayed_mob
        if self.attached_work_crew and self.attached_work_crew.get_permission(
            constants.WORK_CREW_PERMISSION
        ):
            self.attached_building = self.attached_work_crew.images[
                0
            ].current_cell.get_intact_building(self.building_type)
        else:
            self.attached_building = None

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not a work crew, otherwise returns same as superclass
        """
        self.update_info()
        return (
            super().can_show(skip_parent_collection=skip_parent_collection)
            and self.attached_work_crew
            and self.attached_work_crew.get_permission(constants.WORK_CREW_PERMISSION)
        )

    def update_tooltip(self):
        """
        Description:
            Sets this button's tooltip depending on the building it assigns workers to
        Input:
            None
        Output:
            None
        """
        if self.attached_work_crew and self.attached_building:
            if self.building_type == constants.RESOURCE:
                self.set_tooltip(
                    [
                        f"Assigns the selected work crew to the {self.attached_building.name}, producing {self.attached_building.resource_type} over time."
                    ]
                )
            else:
                self.set_tooltip(["placeholder"])
        elif self.attached_work_crew:
            if self.building_type == constants.RESOURCE:
                self.set_tooltip(
                    [
                        "Assigns the selected work crew to a resource building, producing commodities over time."
                    ]
                )
        else:
            self.set_tooltip(["placeholder"])

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a work crew to work in a certain type of building in its tile
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            if self.attached_building:
                if self.attached_building.upgrade_fields[
                    constants.RESOURCE_SCALE
                ] > len(
                    self.attached_building.contained_work_crews
                ):  # if has extra space
                    if self.attached_work_crew.sentry_mode:
                        self.attached_work_crew.set_sentry_mode(False)
                    self.attached_work_crew.work_building(self.attached_building)
                else:
                    text_utility.print_to_screen(
                        "This building is at its work crew capacity."
                    )
                    text_utility.print_to_screen(
                        "Upgrade the building's scale to increase work crew capacity."
                    )
            else:
                text_utility.print_to_screen(
                    "This work crew must be in the same tile as a resource production building to work in it"
                )
        else:
            text_utility.print_to_screen(
                "You are busy and cannot attach a work crew to a building."
            )


class switch_theatre_button(button):
    """
    Button starts choosing a destination for a spaceship to travel between theatres, like between Earth and the planet. A destination is chosen when the player clicks a tile in another theatre.
    """

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button starts choosing a destination for a spaceship to travel between theatres, like between Earth and the planet. A
                destination is chosen when the player clicks a tile in another theatre.
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            current_mob = status.displayed_mob
            if current_mob.movement_points >= 1:
                if current_mob.sentry_mode:
                    current_mob.set_sentry_mode(False)
                if not constants.current_game_mode == constants.STRATEGIC_MODE:
                    game_transitions.set_game_mode(constants.STRATEGIC_MODE)
                current_mob.clear_automatic_route()
                current_mob.end_turn_destination = None
                current_mob.add_to_turn_queue()
                flags.choosing_destination = True
            else:
                text_utility.print_to_screen(
                    "Traveling through space requires all remaining movement points, at least 1."
                )
        else:
            text_utility.print_to_screen("You are busy and cannot move.")

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not capable of traveling between theatres, otherwise returns same as superclass
        """
        return (
            super().can_show(skip_parent_collection=skip_parent_collection)
            and status.displayed_mob.get_permission(constants.PMOB_PERMISSION)
            and status.displayed_mob.can_travel()
        )


class appoint_minister_button(button):
    """
    Button that appoints the selected minister to the office corresponding to this button
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = None: pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'appoint_type': minister_type value - Office appointed to by this button, like the "Minister of Trade" minister_type object
        Output:
            None
        """
        self.appoint_type: minister_types.minister_type = input_dict["appoint_type"]
        input_dict["modes"] = [constants.MINISTERS_MODE]
        input_dict["image_id"] = f"ministers/icons/{self.appoint_type.skill_type}.png"
        super().__init__(input_dict)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if the minister office that this button is attached to is open, otherwise returns False
        """
        return (
            super().can_show(skip_parent_collection=skip_parent_collection)
            and status.displayed_minister
            and status.displayed_minister.current_position == None
            and not minister_utility.get_minister(self.appoint_type.key)
        )

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button appoints the selected minister to the office corresponding to this button
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            appointed_minister = status.displayed_minister
            appointed_minister.appoint(self.appoint_type)
            if not appointed_minister.just_removed:
                appointed_minister.respond("first hired")
        else:
            text_utility.print_to_screen("You are busy and cannot appoint a minister.")


class reappoint_minister_button(button):
    """
    Button that removes the selected minister from their current office, allowing them to be reappointed
    """

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if the selected minister is currently in an office, otherwise returns False
        """
        return (
            super().can_show(skip_parent_collection=skip_parent_collection)
            and status.displayed_minister
            and status.displayed_minister.current_position
        )

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button removes the selected minister from their current office, returning them to the pool of available
                ministers
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            status.displayed_minister.just_removed = True
            status.displayed_minister.appoint(None)
        else:
            text_utility.print_to_screen(
                "You are busy and cannot reappoint a minister."
            )


class fire_minister_button(button):
    """
    Button that fires the selected minister
    """

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if the selected minister is currently in an office, otherwise returns False
        """
        return (
            super().can_show(skip_parent_collection=skip_parent_collection)
            and status.displayed_minister
            and status.displayed_minister.current_position
        )

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button removes the selected minister from their current office, returning them to the pool of available
                ministers
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            appointed_minister = status.displayed_minister
            public_opinion_penalty = appointed_minister.status_number
            text = f"Are you sure you want to fire {appointed_minister.name}, your {appointed_minister.current_position.name}? /n /n"
            text += f"This will incur a public opinion penalty: "
            if appointed_minister.status_number >= 4:
                text += f"{appointed_minister.name} is of very high social status, so firing them would cause widespread outrage. /n /n"
            elif appointed_minister.status_number == 3:
                text += f"{appointed_minister.name} is of high social status, so firing them would reflect particularly poorly on public opinion. /n /n"
            elif appointed_minister.status_number == 2:
                text += f"{appointed_minister.name} is of moderate social status, so firing them would have a modest impact on public opinion. /n /n"
            elif appointed_minister.status_number <= 1:
                text += f"{appointed_minister.name} is of low social status, so firing them would have a minimal impact on public opinion. /n /n"
            constants.notification_manager.display_notification(
                {
                    "message": text,
                    "choices": [constants.CHOICE_CONFIRM_FIRE_MINISTER_BUTTON, None],
                }
            )
        else:
            text_utility.print_to_screen("You are busy and cannot remove a minister.")


class to_trial_button(button):
    """
    Button that goes to the trial screen to remove the selected minister from their current office
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = None: pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
        Output:
            None
        """
        input_dict["modes"] = input_dict["attached_label"].modes
        input_dict["image_id"] = "buttons/to_trial_button.png"
        super().__init__(input_dict)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if a non-prosecutor minister with an office to be removed from is selected
        """
        if (
            super().can_show(skip_parent_collection=skip_parent_collection)
            and status.displayed_minister
            and status.displayed_minister.current_position
            and status.displayed_minister.current_position.key
            != constants.SECURITY_MINISTER
        ):
            return True

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button goes to the trial screen to remove the selected minister from the game and confiscate a portion of their
                stolen money
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            if constants.money >= constants.action_prices["trial"]:
                if minister_utility.positions_filled():
                    if len(status.minister_list) > 8:  # if any available appointees
                        defense = status.displayed_minister
                        prosecution = minister_utility.get_minister(
                            constants.SECURITY_MINISTER
                        )
                        game_transitions.set_game_mode(constants.TRIAL_MODE)
                        minister_utility.trial_setup(
                            defense, prosecution
                        )  # sets up defense and prosecution displays
                    else:
                        text_utility.print_to_screen(
                            "There are currently no available appointees to replace this minister in the event of a successful trial."
                        )
            else:
                text_utility.print_to_screen(
                    f"You do not have the {constants.action_prices['trial']} money needed to start a trial."
                )
        else:
            text_utility.print_to_screen("You are busy and cannot start a trial.")


class fabricate_evidence_button(button):
    """
    Button in the trial screen that fabricates evidence to use against the defense in the current trial. Fabricated evidence disappears at the end of the trial or at the end of the turn
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = None: pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
        Output:
            None
        """
        input_dict["modes"] = [constants.TRIAL_MODE, constants.MINISTERS_MODE]
        input_dict["image_id"] = "buttons/fabricate_evidence_button.png"
        super().__init__(input_dict)

    def get_cost(self):
        """
        Description:
            Returns the cost of fabricating another piece of evidence. The cost increases for each existing fabricated evidence against the selected minister
        Input:
            None
        Output:
            Returns the cost of fabricating another piece of evidence
        """
        defense = status.displayed_defense
        return trial_utility.get_fabricated_evidence_cost(defense.fabricated_evidence)

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button spends money to fabricate a piece of evidence against the selected minister
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            if constants.money >= self.get_cost():
                constants.money_tracker.change(-1 * self.get_cost(), "trial")
                defense = status.displayed_defense
                prosecutor = status.displayed_prosecution
                prosecutor.display_message(
                    f"{prosecutor.current_position.name} {prosecutor.name} reports that evidence has been successfully fabricated for {str(self.get_cost())} money. /n /nEach new fabricated evidence will cost twice as much as the last, and fabricated evidence becomes useless at the end of the turn or after it is used in a trial. /n /n"
                )
                defense.fabricated_evidence += 1
                defense.corruption_evidence += 1
                minister_utility.calibrate_trial_info_display(
                    status.defense_info_display, defense
                )  # updates trial display with new evidence
            else:
                text_utility.print_to_screen(
                    f"You do not have the {str(self.get_cost())} money needed to fabricate evidence."
                )
        else:
            text_utility.print_to_screen("You are busy and cannot fabricate evidence.")


class bribe_judge_button(button):
    """
    Button in the trial screen that bribes the judge to get an advantage in the next trial this turn
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = None: pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
        Output:
            None
        """
        input_dict["modes"] = [constants.TRIAL_MODE]
        input_dict["image_id"] = "buttons/bribe_judge_button.png"
        super().__init__(input_dict)

    def get_cost(self):
        """
        Description:
            Returns the cost of bribing the judge, which is as much as the first piece of fabricated evidence
        Input:
            None
        Output:
            Returns the cost of bribing the judge
        """
        return trial_utility.get_fabricated_evidence_cost(
            0
        )  # costs as much as 1st piece of fabricated evidence

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if judge has not been bribed yet, otherwise returns False
        """
        if super().can_show(skip_parent_collection=skip_parent_collection):
            if not flags.prosecution_bribed_judge:
                return True
        return False

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button spends money to bribe the judge
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            if constants.money >= self.get_cost():
                if not flags.prosecution_bribed_judge:
                    constants.money_tracker.change(-1 * self.get_cost(), "trial")
                    flags.prosecution_bribed_judge = True
                    prosecutor = status.displayed_prosecution
                    prosecutor.display_message(
                        f"{prosecutor.current_position.name} {prosecutor.name} reports that the judge has been successfully bribed for {self.get_cost()} money. /n /nThis may provide a bonus in the next trial this turn. /n /n"
                    )
                else:
                    text_utility.print_to_screen(
                        "The judge has already been bribed for this trial."
                    )
            else:
                text_utility.print_to_screen(
                    f"You do not have the {self.get_cost()} money needed to bribe the judge."
                )
        else:
            text_utility.print_to_screen("You are busy and cannot fabricate evidence.")


class automatic_route_button(button):
    """
    Button that modifies a unit's automatic movement route, with an effect depending on the button's type
    """

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn. All automatic route buttons can only appear if the selected unit is porters or a crewed vehicle. Additionally, clear and execute automatic route buttons require that an automatic
                route already exists
        Input:
            None
        Output:
            boolean: Returns whether this button should be drawn
        """
        if super().can_show(skip_parent_collection=skip_parent_collection):
            attached_mob = status.displayed_mob
            if (
                attached_mob.inventory_capacity > 0
                and not attached_mob.any_permissions(
                    constants.CARAVAN_PERMISSION, constants.INACTIVE_VEHICLE_PERMISSION
                )
            ):
                if self.button_type in [
                    constants.CLEAR_AUTOMATIC_ROUTE_BUTTON,
                    constants.EXECUTE_AUTOMATIC_ROUTE_BUTTON,
                ]:
                    if len(attached_mob.base_automatic_route) > 0:
                        return True
                else:
                    return True
        return False

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. Clear automatic route buttons remove the selected unit's automatic route. Draw automatic route buttons enter the route
            drawing mode, in which the player can click on consecutive tiles to add them to the route. Execute automatic route buttons command the selected unit to execute its in-progress automatic route, stopping when it cannot
            continue the route for any reason
        Input:
            None
        Output:
            None
        """
        attached_mob = status.displayed_mob
        if main_loop_utility.action_possible():
            if status.strategic_map_grid in attached_mob.grids:
                if self.button_type == constants.CLEAR_AUTOMATIC_ROUTE_BUTTON:
                    attached_mob.clear_automatic_route()

                elif self.button_type == constants.DRAW_AUTOMATIC_ROUTE_BUTTON:
                    if (
                        attached_mob.get_permission(constants.VEHICLE_PERMISSION)
                        and attached_mob.vehicle_type == constants.TRAIN_PERMISSION
                        and not attached_mob.get_cell().has_intact_building(
                            constants.TRAIN_STATION
                        )
                    ):
                        text_utility.print_to_screen(
                            "A train can only start a movement route from a train station."
                        )
                        return ()
                    attached_mob.clear_automatic_route()
                    attached_mob.add_to_automatic_route(
                        (attached_mob.x, attached_mob.y)
                    )
                    flags.drawing_automatic_route = True

                elif self.button_type == constants.EXECUTE_AUTOMATIC_ROUTE_BUTTON:
                    if attached_mob.can_follow_automatic_route():
                        attached_mob.follow_automatic_route()
                        attached_mob.remove_from_turn_queue()
                        actor_utility.calibrate_actor_info_display(
                            status.mob_info_display, attached_mob
                        )  # updates mob info display if automatic route changed anything
                    else:
                        text_utility.print_to_screen(
                            "This unit is currently not able to progress along its designated route."
                        )
            else:
                text_utility.print_to_screen(
                    "You can only create movement routes in Africa."
                )
        else:
            if self.button_type == constants.EXECUTE_AUTOMATIC_ROUTE_BUTTON:
                text_utility.print_to_screen("You are busy and cannot move this unit.")
            else:
                text_utility.print_to_screen(
                    "You are busy and cannot modify this unit's movement route."
                )


class toggle_button(button):
    """
    Button that monitors and toggles a boolean variable on the attached actor
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = None: pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'toggle_variable': string value - Name of the variable that this button toggles
                'attached_to_actor': boolean value - Whether this button is an actor display button or a default button
        Output:
            None
        """
        self.toggle_variable: str = input_dict["toggle_variable"]
        self.attached_to_actor: bool = input_dict.get("attached_to_actor", True)
        super().__init__(input_dict)

    def get_value(self):
        """
        Description:
            Returns the value of the variable this button toggles
        Input:
            None
        Output:
            boolean: Returns the value of the variable this button toggles
        """
        if self.attached_to_actor:
            if self.attached_label.actor:
                return getattr(self.attached_label.actor, self.toggle_variable)
            return False
        elif constants.effect_manager.effect_exists(self.toggle_variable):
            return constants.effect_manager.effect_active(self.toggle_variable)
        else:
            return getattr(flags, self.toggle_variable)

    def on_click(self):
        """
        Description:
            Toggles this button's variable on the attached actor
        Input:
            None
        Output:
            None
        """
        if self.attached_to_actor:
            setattr(
                self.attached_label.actor,
                self.toggle_variable,
                not self.get_value(),
            )
        elif constants.effect_manager.effect_exists(self.toggle_variable):
            constants.effect_manager.set_effect(
                self.toggle_variable, not self.get_value()
            )
            if self.toggle_variable in ["remove_fog_of_war", "show_clouds"]:
                constants.update_terrain_knowledge_requirements()
                status.minimap_grid.calibrate(
                    status.minimap_grid.center_x, status.minimap_grid.center_y
                )
                if status.displayed_mob:
                    actor_utility.calibrate_actor_info_display(
                        status.mob_info_display, status.displayed_mob
                    )
                if status.displayed_tile:
                    actor_utility.calibrate_actor_info_display(
                        status.tile_info_display, status.displayed_tile
                    )
            elif self.toggle_variable in [
                "earth_preset",
                "mars_preset",
                "venus_preset",
            ]:
                for variable in ["earth_preset", "mars_preset", "venus_preset"]:
                    if variable != self.toggle_variable:
                        constants.effect_manager.set_effect(variable, False)
        else:
            setattr(flags, self.toggle_variable, not self.get_value())

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn. All automatic route buttons require that an automatic route already exists
        Input:
            None
        Output:
            boolean: Returns whether this button should be drawn
        """
        if not self.attached_to_actor:
            self.showing_outline = self.get_value()
            return super().can_show()

        if self.attached_label.actor and self.attached_label.actor.get_permission(
            constants.PMOB_PERMISSION
        ):
            self.showing_outline = self.get_value()
            if super().can_show(skip_parent_collection=skip_parent_collection):
                if self.toggle_variable == "wait_until_full":
                    return bool(status.displayed_mob.base_automatic_route)
                else:
                    return True
        return False

    def update_tooltip(self):
        """
        Description:
            Sets this button's tooltip depending on the variable it toggles
        Input:
            None
        Output:
            None
        """
        self.set_tooltip(
            [
                constants.toggle_button_tooltips[self.toggle_variable]["default"],
                constants.toggle_button_tooltips[self.toggle_variable][
                    str(self.get_value())
                ],
            ]
        )


class change_parameter_button(button):
    """
    Button that, when god mode is enabled, allows changing the selected tile's terrain handler parameter values
    """

    def __init__(self, input_dict) -> None:
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
        Output:
            None
        """
        self.change = input_dict["change"]
        super().__init__(input_dict)

    def on_click(self) -> None:
        """
        Description;
            Changes this button's parameter of its label's tile's terrain handler
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            if (
                self.attached_label.actor_label_type.removesuffix("_label")
                in constants.global_parameters
            ):
                self.attached_label.actor.cell.grid.world_handler.change_parameter(
                    self.attached_label.actor_label_type.removesuffix("_label"),
                    self.change,
                )
            elif self.attached_label.actor_label_type == constants.AVERAGE_WATER_LABEL:
                if self.change > 0:
                    for i in range(abs(self.change) - 1):
                        self.attached_label.actor.cell.grid.world_handler.default_grid.place_water(
                            repeat_on_fail=True, radiation_effect=False
                        )
                    self.attached_label.actor.cell.grid.world_handler.default_grid.place_water(
                        update_display=True, repeat_on_fail=True, radiation_effect=False
                    )
                else:
                    for i in range(abs(self.change) - 1):
                        self.attached_label.actor.cell.grid.world_handler.default_grid.remove_water()
                    self.attached_label.actor.cell.grid.world_handler.default_grid.remove_water(
                        update_display=True
                    )
                actor_utility.calibrate_actor_info_display(
                    status.tile_info_display, status.displayed_tile
                )
            else:
                self.attached_label.actor.cell.terrain_handler.change_parameter(
                    self.attached_label.actor_label_type.removesuffix("_label"),
                    self.change,
                )
        else:
            text_utility.print_to_screen(
                "You are busy and cannot change this parameter."
            )

    def can_show(self, skip_parent_collection: bool = False) -> bool:
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns True if this button is a local parameter button or is a global parameter button for the planet grid, otherwise returns False
        """
        if (
            self.attached_label.actor_label_type == constants.AVERAGE_WATER_LABEL
            or self.attached_label.actor_label_type.removesuffix("_label")
            in constants.global_parameters
        ):
            return (
                super().can_show(skip_parent_collection=skip_parent_collection)
                and self.attached_label.actor.cell.grid != status.earth_grid
            )
        else:
            return super().can_show(skip_parent_collection=skip_parent_collection)


class help_button(button):
    """
    Button that displays a help message for an attached label
    """

    def generate_context(self) -> Dict[str, Any]:
        """
        Description:
            Generates required context for help message generation
        Input:
            None
        Output:
            Dict[str, Any]: Returns a dictionary of context values
        """
        context = {}
        if (
            self.attached_label.actor
            and self.attached_label.actor_label_type
            in constants.help_manager.subjects[constants.HELP_GLOBAL_PARAMETERS]
        ):
            context[
                constants.HELP_WORLD_HANDLER_CONTEXT
            ] = self.attached_label.actor.cell.grid.world_handler
        return context

    def on_click(self):
        """
        Description:
            Displays a help message for the attached label
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            message = constants.help_manager.generate_message(
                self.attached_label.actor_label_type, context=self.generate_context()
            )
            if (
                self.attached_label.actor_label_type
                in constants.help_manager.subjects[constants.HELP_GLOBAL_PARAMETERS]
                and status.current_ministers[constants.ECOLOGY_MINISTER]
            ):
                status.current_ministers[constants.ECOLOGY_MINISTER].display_message(
                    message,
                    override_input_dict={
                        "audio": {
                            "sound_id": status.current_ministers[
                                constants.ECOLOGY_MINISTER
                            ].get_voice_line("acknowledgement"),
                            "radio_effect": status.current_ministers[
                                constants.ECOLOGY_MINISTER
                            ].get_radio_effect(),
                        },
                    },
                )
            else:
                constants.notification_manager.display_notification(
                    {"message": message}
                )
        else:
            text_utility.print_to_screen(
                "You are busy and cannot receive a help message."
            )

    def update_tooltip(self):
        """
        Description:
            Sets this button's tooltip depending on the attached label
        Input:
            None
        Output:
            None
        """
        self.set_tooltip(
            constants.help_manager.generate_tooltip(
                self.attached_label.actor_label_type, context=self.generate_context()
            )
        )

    def can_show(self):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns whether this button should be drawn
        """
        return True
