# Contains functionality for actor display buttons

import pygame
from typing import Dict, List, Any, Callable
from modules.interface_components import buttons
from modules.constructs import buildings, minister_types
from modules.util import (
    main_loop_utility,
    actor_utility,
    minister_utility,
    trial_utility,
    text_utility,
    game_transitions,
    utility,
    scaling,
)
from modules.constructs import minister_types
from modules.constants import constants, status, flags


class embark_all_passengers_button(buttons.button):
    """
    Button that commands a vehicle to take all other mobs in its location as passengers
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
        Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a vehicle to take all other mobs in its location as passengers
        """
        if main_loop_utility.action_possible():
            vehicle = status.displayed_mob
            can_embark = True
            if (
                self.vehicle_type == constants.TRAIN_PERMISSION
                and not vehicle.location.get_inact_building(constants.TRAIN_STATION)
            ):
                text_utility.print_to_screen(
                    "A train can only pick up passengers at a train station."
                )
                can_embark = False
            if can_embark:
                vehicle.set_permission(constants.SENTRY_MODE_PERMISSION, False)
                for subscribed_mob in vehicle.location.subscribed_mobs.copy():
                    if subscribed_mob.get_permission(
                        constants.PMOB_PERMISSION
                    ) and not subscribed_mob.get_permission(
                        constants.VEHICLE_PERMISSION
                    ):  # vehicles and enemies won't be picked up as passengers
                        subscribed_mob.embark_vehicle(
                            vehicle,
                            focus=subscribed_mob
                            == vehicle.location.subscribed_mobs[-1],
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
        result = super().can_show(
            skip_parent_collection=skip_parent_collection
        ) and status.displayed_mob.get_permission(constants.ACTIVE_VEHICLE_PERMISSION)
        if result:
            if (
                status.displayed_mob.get_permission(constants.SPACESHIP_PERMISSION)
                and self.vehicle_type != constants.SPACESHIP_PERMISSION
            ):
                self.vehicle_type = constants.SPACESHIP_PERMISSION
                self.image.set_image(f"buttons/embark_spaceship_button.png")
            elif (
                status.displayed_mob.get_permission(constants.TRAIN_PERMISSION)
                and self.vehicle_type != constants.TRAIN_PERMISSION
            ):
                self.vehicle_type = constants.TRAIN_PERMISSION
                self.image.set_image(f"buttons/embark_train_button.png")
        return result


class disembark_all_passengers_button(buttons.button):
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
        Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a vehicle to eject all of its passengers
        """
        if main_loop_utility.action_possible():
            vehicle = status.displayed_mob
            can_disembark = True
            if vehicle.get_permission(constants.TRAIN_PERMISSION):
                if not vehicle.location.has_building(constants.TRAIN_STATION):
                    text_utility.print_to_screen(
                        "A train can only drop off passengers at a train station."
                    )
                    can_disembark = False
            if can_disembark:
                vehicle.set_permission(constants.SENTRY_MODE_PERMISSION, False)
                if len(vehicle.subscribed_passengers) > 0:
                    vehicle.subscribed_passengers[-1].selection_sound()
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
        result = super().can_show(
            skip_parent_collection=skip_parent_collection
        ) and status.displayed_mob.get_permission(constants.ACTIVE_VEHICLE_PERMISSION)
        if result:
            if (
                status.displayed_mob.get_permission(constants.SPACESHIP_PERMISSION)
                and self.vehicle_type != constants.SPACESHIP_PERMISSION
            ):
                self.vehicle_type = constants.SPACESHIP_PERMISSION
                self.image.set_image(f"buttons/disembark_spaceship_button.png")
            elif (
                status.displayed_mob.get_permission(constants.TRAIN_PERMISSION)
                and self.vehicle_type != constants.TRAIN_PERMISSION
            ):
                self.vehicle_type = constants.TRAIN_PERMISSION
                self.image.set_image(f"buttons/disembark_train_button.png")
        return result


class enable_sentry_mode_button(buttons.button):
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
            elif displayed_mob.get_permission(constants.SENTRY_MODE_PERMISSION):
                return False
            elif displayed_mob.get_permission(
                constants.VEHICLE_PERMISSION
            ) and not displayed_mob.get_permission(constants.ACTIVE_VEHICLE_PERMISSION):
                return False
        return result

    def on_click(self):
        """
        Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button activates sentry mode for the selected unit
        """
        if main_loop_utility.action_possible():
            status.displayed_mob.set_permission(constants.SENTRY_MODE_PERMISSION, True)
            if (
                constants.EffectManager.effect_active("promote_on_sentry")
                and status.displayed_mob.any_permissions(
                    constants.GROUP_PERMISSION, constants.OFFICER_PERMISSION
                )
                and not status.displayed_mob.get_permission(
                    constants.VETERAN_PERMISSION
                )
            ):  # Purely for promotion testing, not normal functionality
                status.displayed_mob.promote()
        else:
            text_utility.print_to_screen("You are busy and cannot enable sentry mode.")


class disable_sentry_mode_button(buttons.button):
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
        return super().can_show(
            skip_parent_collection=skip_parent_collection
        ) and status.displayed_mob.all_permissions(
            constants.PMOB_PERMISSION, constants.SENTRY_MODE_PERMISSION
        )

    def on_click(self):
        """
        Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button deactivates sentry mode for the selected unit
        """
        if main_loop_utility.action_possible():
            status.displayed_mob.set_permission(constants.SENTRY_MODE_PERMISSION, False)
        else:
            text_utility.print_to_screen("You are busy and cannot disable sentry mode.")


class enable_automatic_replacement_button(buttons.button):
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
        Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button enables automatic replacement for the selected unit
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


class disable_automatic_replacement_button(buttons.button):
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
        Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button disables automatic replacement for the selected unit
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


class end_unit_turn_button(buttons.button):
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
        Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button removes the selected unit from the current turn's turn cycle queue
        """
        if main_loop_utility.action_possible():
            status.displayed_mob.remove_from_turn_queue()
            game_transitions.cycle_player_turn()
        else:
            text_utility.print_to_screen(
                "You are busy and cannot end this unit's turn."
            )


class remove_work_crew_button(buttons.button):
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
        Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button removes a work crew from a building
        """
        if main_loop_utility.action_possible():
            self.attached_label.attached_list[
                self.attached_label.list_index
            ].leave_building(
                self.attached_label.actor.location.get_building(self.building_type)
            )
        else:
            text_utility.print_to_screen(
                "You are busy and cannot remove a work crew from a building."
            )


class disembark_vehicle_button(buttons.button):
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
        Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button disembarks a passenger from a vehicle
        """
        if main_loop_utility.action_possible():
            if len(self.attached_label.actor.subscribed_passengers) > 0:
                can_disembark = True
                if self.vehicle_type == constants.TRAIN_PERMISSION:
                    if not self.attached_label.actor.location.has_intact_building(
                        constants.TRAIN_STATION
                    ):
                        text_utility.print_to_screen(
                            "A train can only drop off passengers at a train station."
                        )
                        can_disembark = False
                if can_disembark:
                    passenger = self.attached_label.attached_list[
                        self.attached_label.list_index
                    ]
                    passenger.set_permission(constants.SENTRY_MODE_PERMISSION, False)
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


class embark_vehicle_button(buttons.button):
    """
    Button that commands a selected mob to embark a vehicle of the correct type in the same location
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
            boolean: Returns False if the selected mob cannot embark vehicles or if there is no vehicle in the location to embark, otherwise returns same as superclass
        """
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_mob = status.displayed_mob
            result = (
                displayed_mob
                and displayed_mob.get_permission(constants.PMOB_PERMISSION)
                and not displayed_mob.get_permission(constants.VEHICLE_PERMISSION)
                and displayed_mob.location.has_unit_by_filter(
                    [self.vehicle_type, constants.ACTIVE_VEHICLE_PERMISSION]
                )
            )
        self.was_showing = result
        return result

    def on_click(self):
        """
        Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a selected mob to embark a vehicle of the correct type in the same location
        """
        if main_loop_utility.action_possible():
            if status.displayed_mob.location.has_unit_by_filter(
                [self.vehicle_type, constants.ACTIVE_VEHICLE_PERMISSION]
            ):
                rider = status.displayed_mob
                vehicles = rider.location.get_unit_by_filter(
                    [self.vehicle_type, constants.ACTIVE_VEHICLE_PERMISSION],
                    get_all=True,
                )
                can_embark = True
                if vehicles[0].get_permission(constants.TRAIN_PERMISSION):
                    if not vehicles[0].location.has_intact_building(
                        constants.TRAIN_STATION
                    ):
                        text_utility.print_to_screen(
                            "A train can only pick up passengers at a train station."
                        )
                        can_embark = False
                if can_embark:
                    rider.set_permission(constants.SENTRY_MODE_PERMISSION, False)
                    if len(vehicles) > 1:
                        vehicles[0].select()
                        for vehicle in vehicles:
                            constants.NotificationManager.display_notification(
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
                        vehicle.set_permission(constants.SENTRY_MODE_PERMISSION, False)
                        rider.embark_vehicle(vehicle)
            else:
                text_utility.print_to_screen(
                    f"You must select a unit in the same location as a crewed vehicle to embark."
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
        constants.NotificationManager.clear_notification_queue()  # Skip remaining embark notifications
        vehicle.set_permission(constants.SENTRY_MODE_PERMISSION, False)
        rider.embark_vehicle(vehicle)

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


class cycle_passengers_button(buttons.button):
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
                not len(displayed_mob.subscribed_passengers) > 3
            ):  # only show if vehicle with 3+ passengers
                return False
            if displayed_mob.get_permission(constants.SPACESHIP_PERMISSION):
                self.vehicle_type = constants.SPACESHIP_PERMISSION
            elif displayed_mob.get_permission(constants.TRAIN_PERMISSION):
                self.vehicle_type = constants.TRAIN_PERMISSION
        return result

    def on_click(self):
        """
        Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button cycles the order of passengers displayed in a vehicle
        """
        if main_loop_utility.action_possible():
            displayed_mob = status.displayed_mob
            moved_mob = displayed_mob.subscribed_passengers.pop(0)
            displayed_mob.subscribed_passengers.append(moved_mob)
            actor_utility.calibrate_actor_info_display(
                status.mob_info_display, displayed_mob
            )  # updates mob info display list to show changed passenger order
        else:
            text_utility.print_to_screen("You are busy and cannot cycle passengers.")


class cycle_work_crews_button(buttons.button):
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
            boolean: Returns same as superclass if the displayed location has a resource building containing more than 3 work crews, otherwise returns False
        """
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            if not status.displayed_location.has_intact_building(constants.RESOURCE):
                self.previous_showing_result = False
                return False
            elif (
                len(
                    status.displayed_location.get_intact_building(
                        constants.RESOURCE
                    ).subscribed_work_crews
                )
                > 3
            ):
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
        Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button cycles the order of work crews displayed in a building
        """
        if main_loop_utility.action_possible():
            displayed_location = status.displayed_location
            moved_mob = displayed_location.get_intact_building(
                constants.RESOURCE
            ).subscribed_work_crews.pop(0)
            displayed_location.get_intact_building(
                constants.RESOURCE
            ).subscribed_work_crews.append(moved_mob)
            actor_utility.calibrate_actor_info_display(
                status.location_info_display, displayed_location
            )  # Updates location info display list to show changed work crew order
        else:
            text_utility.print_to_screen("You are busy and cannot cycle work crews.")


class work_crew_to_building_button(buttons.button):
    """
    Button that commands a work crew to work in a certain type of building in its location
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
        self.attached_building: buildings.resource_building = None
        super().__init__(input_dict)

    def update_info(self):
        """
        Updates the building this button assigns workers to depending on the buildings present in this location
        """
        self.attached_work_crew = status.displayed_mob
        if self.attached_work_crew and self.attached_work_crew.get_permission(
            constants.WORK_CREW_PERMISSION
        ):
            self.attached_building = (
                self.attached_work_crew.location.get_intact_building(self.building_type)
            )
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

    @property
    def tooltip_text(self) -> List[List[str]]:
        """
        Provides the tooltip for this object
        """
        if self.attached_work_crew and self.attached_building:
            if self.building_type == constants.RESOURCE:
                return [
                    f"Assigns the selected work crew to the {self.attached_building.name}, producing {self.attached_building.resource_type.name} over time."
                ]
            else:
                return ["placeholder"]
        elif self.attached_work_crew:
            if self.building_type == constants.RESOURCE:
                return [
                    "Assigns the selected work crew to a resource building, producing resources over time."
                ]
        return ["placeholder"]

    def on_click(self):
        """
        Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a work crew to work in a certain type of building in its location
        """
        if main_loop_utility.action_possible():
            if self.attached_building:
                if self.attached_building.upgrade_fields[
                    constants.RESOURCE_SCALE
                ] > len(
                    self.attached_building.subscribed_work_crews
                ):  # if has extra space
                    self.attached_work_crew.set_permission(
                        constants.SENTRY_MODE_PERMISSION, False
                    )
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
                    "This work crew must be in the same location as a resource production building to work in it"
                )
        else:
            text_utility.print_to_screen(
                "You are busy and cannot attach a work crew to a building."
            )


class switch_theatre_button(buttons.button):
    """
    Button starts choosing a destination for a spaceship to travel between theatres, like between Earth and the current world. A destination is chosen when the player clicks a location in another theatre.
    """

    def on_click(self):
        """
        Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button starts choosing a destination for a spaceship to travel between theatres, like between Earth and the planet. A
            destination is chosen when the player clicks a location in another theatre.
        """
        if main_loop_utility.action_possible():
            current_mob = status.displayed_mob
            if current_mob.movement_points >= 1:
                current_mob.set_permission(constants.SENTRY_MODE_PERMISSION, False)
                if not constants.current_game_mode == constants.STRATEGIC_MODE:
                    game_transitions.set_game_mode(constants.STRATEGIC_MODE)
                current_mob.clear_automatic_route()
                current_mob.end_turn_destination = None
                status.displayed_mob.set_permission(
                    constants.TRAVELING_PERMISSION, False
                )
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


class appoint_minister_button(buttons.button):
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
        Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button appoints the selected minister to the office corresponding to this button
        """
        if main_loop_utility.action_possible():
            appointed_minister = status.displayed_minister
            appointed_minister.appoint(self.appoint_type)
            if not appointed_minister.just_removed:
                appointed_minister.respond("first hired")
        else:
            text_utility.print_to_screen("You are busy and cannot appoint a minister.")


class reappoint_minister_button(buttons.button):
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
            and constants.current_game_mode == constants.MINISTERS_MODE
        )

    def on_click(self):
        """
        Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button removes the selected minister from their current office, returning them to the pool of available
            ministers
        """
        if main_loop_utility.action_possible():
            status.displayed_minister.just_removed = True
            status.displayed_minister.appoint(None)
        else:
            text_utility.print_to_screen(
                "You are busy and cannot reappoint a minister."
            )


class fire_minister_button(buttons.button):
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
            and constants.current_game_mode == constants.MINISTERS_MODE
        )

    def on_click(self):
        """
        Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button removes the selected minister from their current office, returning them to the pool of available
            ministers
        """
        if main_loop_utility.action_possible():
            if len(status.minister_list) > len(
                status.minister_types
            ):  # If there are sufficient appointees to refill the positions
                appointed_minister = status.displayed_minister
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
                constants.NotificationManager.display_notification(
                    {
                        "message": text,
                        "choices": [
                            constants.CHOICE_CONFIRM_FIRE_MINISTER_BUTTON,
                            None,
                        ],
                    }
                )
            else:
                text_utility.print_to_screen(
                    "You do not have enough available candidates to refill this minister's position."
                )
        else:
            text_utility.print_to_screen("You are busy and cannot remove a minister.")


class to_trial_button(buttons.button):
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
        Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button goes to the trial screen to remove the selected minister from the game and confiscate a portion of their
            stolen money
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


class fabricate_evidence_button(buttons.button):
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
        Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button spends money to fabricate a piece of evidence against the selected minister
        """
        if main_loop_utility.action_possible():
            if constants.money >= self.get_cost():
                constants.MoneyTracker.change(-1 * self.get_cost(), "trial")
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


class bribe_judge_button(buttons.button):
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
        Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button spends money to bribe the judge
        """
        if main_loop_utility.action_possible():
            if constants.money >= self.get_cost():
                if not flags.prosecution_bribed_judge:
                    constants.MoneyTracker.change(-1 * self.get_cost(), "trial")
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


class automatic_route_button(buttons.button):
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
        Does a certain action when clicked or when corresponding key is pressed, depending on button_type. Clear automatic route buttons remove the selected unit's automatic route. Draw automatic route buttons enter the route
            drawing mode, in which the player can click on consecutive locations to add them to the route. Execute automatic route buttons command the selected unit to execute its in-progress automatic route, stopping when it cannot
            continue the route for any reason
        """
        attached_mob = status.displayed_mob
        if main_loop_utility.action_possible():
            if not attached_mob.location.is_abstract_location:
                if self.button_type == constants.CLEAR_AUTOMATIC_ROUTE_BUTTON:
                    attached_mob.clear_automatic_route()

                elif self.button_type == constants.DRAW_AUTOMATIC_ROUTE_BUTTON:
                    if (
                        attached_mob.get_permission(constants.VEHICLE_PERMISSION)
                        and attached_mob.vehicle_type == constants.TRAIN_PERMISSION
                        and not attached_mob.location.has_intact_building(
                            constants.TRAIN_STATION
                        )
                    ):
                        text_utility.print_to_screen(
                            "A train can only start a movement route from a train station."
                        )
                        return ()
                    attached_mob.clear_automatic_route()
                    attached_mob.add_to_automatic_route(attached_mob.location)
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
                    f"You can only create movement routes on a planetary surface."
                )
        else:
            if self.button_type == constants.EXECUTE_AUTOMATIC_ROUTE_BUTTON:
                text_utility.print_to_screen("You are busy and cannot move this unit.")
            else:
                text_utility.print_to_screen(
                    "You are busy and cannot modify this unit's movement route."
                )


class toggle_button(buttons.button):
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
        elif constants.EffectManager.effect_exists(self.toggle_variable):
            return constants.EffectManager.effect_active(self.toggle_variable)
        else:
            return getattr(flags, self.toggle_variable)

    def on_click(self):
        """
        Toggles this button's variable on the attached actor
        """
        if self.attached_to_actor:
            setattr(
                self.attached_label.actor,
                self.toggle_variable,
                not self.get_value(),
            )
        elif constants.EffectManager.effect_exists(self.toggle_variable):
            constants.EffectManager.set_effect(
                self.toggle_variable, not self.get_value()
            )
            if self.toggle_variable in ["remove_fog_of_war", "show_clouds"]:
                constants.update_terrain_knowledge_requirements()
                constants.EventBus.publish(constants.UPDATE_MAP_MODE_ROUTE)
            elif self.toggle_variable in [
                "earth_preset",
                "mars_preset",
                "venus_preset",
            ]:
                for variable in ["earth_preset", "mars_preset", "venus_preset"]:
                    if variable != self.toggle_variable:
                        constants.EffectManager.set_effect(variable, False)
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

    @property
    def tooltip_text(self) -> List[List[str]]:
        """
        Provides the tooltip for this object
        """
        return [
            constants.toggle_button_tooltips[self.toggle_variable]["default"],
            constants.toggle_button_tooltips[self.toggle_variable][
                str(self.get_value())
            ],
        ]


class change_parameter_button(buttons.button):
    """
    Button that, when god mode is enabled, allows changing the selected location's location's parameter values
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
        Changes this button's parameter of its label's location
        """
        if main_loop_utility.action_possible():
            if (
                self.attached_label.actor_label_type.removesuffix("_label")
                in constants.global_parameters
            ):
                status.displayed_location.true_world_handler.change_parameter(
                    self.attached_label.actor_label_type.removesuffix("_label"),
                    self.change,
                )
            elif self.attached_label.actor_label_type == constants.AVERAGE_WATER_LABEL:
                if self.change > 0:
                    for i in range(abs(self.change)):
                        status.displayed_location.true_world_handler.place_water(
                            update_display=False,
                            repeat_on_fail=True,
                            radiation_effect=False,
                        )
                else:
                    for i in range(abs(self.change)):
                        status.displayed_location.true_world_handler.remove_water(
                            update_display=False
                        )
                status.displayed_location.true_world_handler.update_location_image_bundles()
            else:
                status.displayed_location.change_parameter(
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
        if not constants.EffectManager.effect_active("god_mode"):
            return False
        if (
            self.attached_label.actor_label_type == constants.AVERAGE_WATER_LABEL
            or self.attached_label.actor_label_type.removesuffix("_label")
            in constants.global_parameters
        ):
            return (
                super().can_show(skip_parent_collection=skip_parent_collection)
                and not self.attached_label.actor.is_earth_location
            )
        else:
            return super().can_show(skip_parent_collection=skip_parent_collection)


class help_button(buttons.button):
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
            in constants.HelpManager.subjects[constants.HELP_GLOBAL_PARAMETERS]
        ):
            context[constants.HELP_WORLD_HANDLER_CONTEXT] = (
                self.attached_label.actor.true_world_handler
            )
        return context

    def on_click(self):
        """
        Displays a help message for the attached label
        """
        if main_loop_utility.action_possible():
            message = constants.HelpManager.generate_message(
                self.attached_label.actor_label_type, context=self.generate_context()
            )
            if (
                self.attached_label.actor_label_type
                in constants.HelpManager.subjects[constants.HELP_GLOBAL_PARAMETERS]
                and status.current_ministers[constants.ECOLOGY_MINISTER]
            ):
                status.current_ministers[constants.ECOLOGY_MINISTER].display_message(
                    message,
                    override_input_dict={
                        "audio": {
                            "sound_id": utility.get_voice_line(
                                status.current_ministers[constants.ECOLOGY_MINISTER],
                                "acknowledgement",
                            ),
                            "radio_effect": status.current_ministers[
                                constants.ECOLOGY_MINISTER
                            ].get_radio_effect(),
                        },
                    },
                )
            else:
                constants.NotificationManager.display_notification({"message": message})
        else:
            text_utility.print_to_screen(
                "You are busy and cannot receive a help message."
            )

    @property
    def tooltip_text(self) -> List[List[str]]:
        """
        Provides the tooltip for this object
        """
        return constants.HelpManager.generate_tooltip(
            self.attached_label.actor_label_type, context=self.generate_context()
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


class actor_icon(buttons.button):
    """
    Button that displays an actor's image and tooltip
    """

    def __init__(self, input_dict) -> None:
        """
        Same as superclass, but with additional input:
            callable dynamic_tooltip_factory: Function that takes an actor_display_label and returns a list of strings to use as the tooltip for this button
            image ID list image_id: Default image ID list to use if no actor is attached
            actor type actor_type: Type of actor to display the information of, like constants.MOB_ACTOR_TYPE
            actor calibrate_to: Optional actor to automatically and permanently calibrate this icon to
        """
        input_dict["image_id"] = input_dict.get(
            "image_id", [{"image_id": "misc/empty.png"}]
        )
        super().__init__(input_dict)
        self.actor = None
        self.dynamic_tooltip_factory: Callable[["actor_icon"], List[str]] = (
            input_dict.get("dynamic_tooltip_factory", None)
        )
        self.default_image_id: List[Dict[str, Any]] = input_dict["image_id"]
        if type(self.default_image_id) != list:
            raise TypeError(
                f"Expected image_id to be an image ID list, received {self.default_image_id}"
            )
        self.actor_type: str = input_dict["actor_type"]
        self.calibrate_to = input_dict.get("calibrate_to", None)
        if self.calibrate_to:
            self.calibrate(self.calibrate_to)

    @property
    def batch_tooltip_list(self):
        """
        Gets a 2D list of strings to use as this object's tooltip
            Each string is displayed on a separate line, while each sublist is displayed in a separate box
        """
        if self.actor:
            if self.actor.actor_type == constants.LOCATION_ACTOR_TYPE:
                return self.actor.batch_tooltip_list_omit_mobs
            else:
                return self.actor.batch_tooltip_list
        elif self.dynamic_tooltip_factory:
            return [self.dynamic_tooltip_factory(self)]
        else:
            return []

    def on_click(self):
        """
        Handles on-click behavior for this button
        """
        if (
            self.calibrate_to or not self.actor
        ):  # If empty or if always bound to the same actor
            return
        if not main_loop_utility.action_possible():
            conversion = {
                constants.MOB_ACTOR_TYPE: "unit",
                constants.LOCATION_ACTOR_TYPE: "location",
                constants.MINISTER_ACTOR_TYPE: "minister",
            }
            text_utility.print_to_screen(
                f"You are busy and cannot select this {conversion[self.actor.actor_type]}."
            )
        if self.actor.actor_type == constants.MOB_ACTOR_TYPE:
            if self.actor.get_permission(constants.DUMMY_PERMISSION):
                if self.actor.get_permission(constants.ACTIVE_VEHICLE_PERMISSION):
                    status.reorganize_vehicle_right_button.on_click(allow_sound=False)
                elif status.displayed_mob.get_permission(
                    constants.ACTIVE_VEHICLE_PERMISSION
                ):
                    status.reorganize_vehicle_left_button.on_click(allow_sound=False)
                elif self.actor.any_permissions(
                    constants.WORKER_PERMISSION, constants.OFFICER_PERMISSION
                ):
                    status.reorganize_group_left_button.on_click(allow_sound=False)
                elif self.actor.get_permission(constants.GROUP_PERMISSION):
                    status.reorganize_group_right_button.on_click(allow_sound=False)

                if not self.actor.get_permission(
                    constants.DUMMY_PERMISSION
                ):  # Only select if dummy unit successfully became real
                    self.actor.cycle_select()
                    self.actor.selection_sound()
            else:  # If already existing, simply select unit
                self.actor.cycle_select()
        elif self.actor.actor_type == constants.LOCATION_ACTOR_TYPE:
            actor_utility.calibrate_actor_info_display(
                status.mob_info_display, None
            )  # Focus on location info display when clicked
        elif self.actor_type == constants.MINISTER_ACTOR_TYPE:
            if constants.current_game_mode != constants.TRIAL_MODE:
                selected_minister = (
                    self.actor
                )  # Saved in case switching game modes re-calibrates the icon
                if constants.current_game_mode != constants.MINISTERS_MODE:
                    game_transitions.set_game_mode(constants.MINISTERS_MODE)
                actor_utility.calibrate_actor_info_display(
                    status.minister_info_display, selected_minister
                )
                selected_minister.play_voice_line("acknowledgement")

    def calibrate(self, new_actor):
        """
        Description:
            Attaches this label to the inputted actor and updates this label's information based on the inputted actor
        Input:
            string/actor new_actor: The displayed actor whose information is matched by this label. If this equals None, the label does not match any actors.
        Output:
            None
        """
        if (
            self.actor_type == constants.MINISTER_ACTOR_TYPE
            and new_actor
            and new_actor.actor_type == constants.MOB_ACTOR_TYPE
        ):
            self.calibrate(new_actor.controlling_minister)
            return  # If minister icon attempts to calibrate to mob, calibrate to its minister instead
        self.actor = new_actor
        self.image.set_image(self.image_id_list)

    @property
    def image_id_list(self) -> List[Dict[str, Any]]:
        """
        Provides this icon's image ID list based on its calibrated actor
        """
        image_id_list = []
        if self.actor:
            if self.actor.actor_type == constants.LOCATION_ACTOR_TYPE:
                image_id_list += self.actor.image_dict[constants.IMAGE_ID_LIST_TERRAIN]
                image_id_list.append(
                    {
                        "image_id": "misc/location_outline.png",
                        "detail_level": 1.0,
                        "level": constants.FRONT_LEVEL,
                    }
                )
            elif self.actor.actor_type == constants.MOB_ACTOR_TYPE:
                image_id_list += self.actor.image_dict[constants.IMAGE_ID_LIST_FULL_MOB]
                if self.actor.get_permission(constants.SPACESHIP_PERMISSION) or (
                    self.actor.location.is_abstract_location
                    and not self.actor.location.is_earth_location
                ):
                    image_id_list.append(
                        {
                            "image_id": "misc/actor_backgrounds/space_background.png",
                            "level": constants.BACKGROUND_LEVEL,
                        }
                    )
                else:
                    image_id_list.append(
                        {
                            "image_id": "misc/actor_backgrounds/mob_background.png",
                            "level": constants.BACKGROUND_LEVEL,
                        }
                    )
                if self.actor.get_permission(constants.DUMMY_PERMISSION):
                    image_id_list.append(
                        {
                            "image_id": "misc/dark_shader.png",
                            "level": constants.FRONT_LEVEL - 1,  # Behind outline
                        }
                    )

                if self.actor.get_permission(constants.PMOB_PERMISSION):
                    image_id_list.append(
                        {
                            "image_id": "misc/actor_backgrounds/pmob_outline.png",
                            "detail_level": 1.0,
                            "level": constants.FRONT_LEVEL,
                        }
                    )
                elif self.actor.get_permission(constants.NPMOB_PERMISSION):
                    image_id_list.append(
                        {
                            "image_id": "misc/actor_backgrounds/npmob_outline.png",
                            "detail_level": 1.0,
                            "level": constants.FRONT_LEVEL,
                        }
                    )
            elif self.actor.actor_type == constants.MINISTER_ACTOR_TYPE:
                image_id_list = self.actor.image_dict[constants.IMAGE_ID_LIST_DEFAULT]
                if self.actor.current_position:
                    image_id_list.append(
                        {
                            "image_id": f"ministers/icons/{self.actor.current_position.skill_type}.png",
                            "level": constants.BACKGROUND_LEVEL,
                        }
                    )
                else:
                    image_id_list.append(
                        {
                            "image_id": "misc/actor_backgrounds/minister_background.png",
                            "level": constants.BACKGROUND_LEVEL,
                        }
                    )
            elif self.actor.actor_type in [
                constants.MOB_INVENTORY_ACTOR_TYPE,
                constants.LOCATION_INVENTORY_ACTOR_TYPE,
            ]:
                image_id_list = self.actor.image.image_id
            else:
                raise ValueError(f"Unexpected actor type: {self.actor.actor_type}")
        if not image_id_list:
            image_id_list += self.default_image_id
        return image_id_list


class minister_icon(actor_icon):
    """
    Abstract class with shared minister table icon/available minister icon flashing outline and name label functionality
    """

    @property
    def image_id_list(self) -> List[Dict[str, Any]]:
        """
        Provides this icon's image ID list based on its calibrated actor
        """
        if self.actor:
            return super().image_id_list + actor_utility.generate_label_image_id(
                self.actor.get_f_lname(use_prefix=True)
            )
        else:
            return super().image_id_list

    def draw(self) -> None:
        """
        Draws this button, along with an outline if its keybind is being pressed
        """
        if (
            self.can_show()
            and self.actor_type == constants.MINISTER_ACTOR_TYPE
            and constants.current_game_mode == constants.MINISTERS_MODE
        ):  # Draw flashing outline around icon if minister selected
            if (
                status.displayed_minister
                and status.displayed_minister == self.actor
                and flags.show_selection_outlines
            ):
                pygame.draw.rect(
                    constants.game_display,
                    constants.color_dict[constants.COLOR_BRIGHT_GREEN],
                    self.outline,
                )
        super().draw()


class minister_table_icon(minister_icon):
    """
    Actor icon that calibrates to the current minister in a particular position, rather than the currently selected one
    """

    def __init__(self, input_dict) -> None:
        """
        Same as superclass, but with additional input:
            minister_type minister_type: Type of minister linked to this icon - always calibrates to the current minister
                of that type
        """
        super().__init__(input_dict)
        self.minister_type: minister_types.minister_type = input_dict["minister_type"]
        status.minister_types[self.minister_type.key].minister_table_icon = self

    @property
    def batch_tooltip_list(self) -> List[List[str]]:
        """
        Gets a 2D list of strings to use as this object's tooltip
            Each string is displayed on a separate line, while each sublist is displayed in a separate box
        """
        if self.actor or self.dynamic_tooltip_factory:
            return super().batch_tooltip_list
        else:
            return [
                [
                    f"No {self.minister_type.name} is currently appointed.",
                    f"Without a {self.minister_type.name}, {self.minister_type.skill_type.replace('_', ' ')}-oriented actions are not possible",
                ]
            ]


class available_minister_icon(minister_icon):
    """
    Minister icon indicating an available minister candidate for hiring
    """

    def __init__(self, input_dict) -> None:
        """
        Same as superclass, but with additional configuration
        """
        super().__init__(input_dict)
        status.available_minister_icon_list.append(self)
        self.insert_collection_above()
        self.warning_image = constants.ActorCreationManager.create_interface_element(
            {
                "attached_image": self,
                "init_type": constants.WARNING_IMAGE,
                "parent_collection": self.parent_collection,
                "member_config": {"x_offset": scaling.scale_width(-100), "y_offset": 0},
            }
        )

    def on_click(self):
        """
        Handles on-click behavior for this button
        """
        super().on_click()
        if self.actor and main_loop_utility.action_possible():
            new_center_index = status.available_minister_list.index(self.actor)
            new_left_index = new_center_index - 2
            constants.available_minister_left_index = new_left_index
            minister_utility.update_available_minister_display()

    def can_show_warning(self):
        """
        Description:
            Returns whether this image should display its warning image - when attached minister will be fired at the end of the turn
        Input:
            None
        Output:
            Returns whether this image should display its warning image
        """
        return self.actor and self.actor.just_removed

    @property
    def batch_tooltip_list(self) -> List[List[str]]:
        """
        Gets a 2D list of strings to use as this object's tooltip
            Each string is displayed on a separate line, while each sublist is displayed in a separate box
        """
        if self.actor or self.dynamic_tooltip_factory:
            return super().batch_tooltip_list
        else:
            return [["There is no available candidate in this slot."]]
