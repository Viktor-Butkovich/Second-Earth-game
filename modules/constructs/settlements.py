# Contains functionality for settlements

from __future__ import annotations
from modules.util import actor_utility
from modules.constants import constants, status, flags


class settlement:
    """
    Object that represents a colonial settlement - attached to a resource production facility, port, and/or train station
    """

    def __init__(self, from_save, input_dict):
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'location': location value - Where this settlement is located
                'name': string value - Required if from save, starting name of settlement
        Output:
            None
        """
        self.subscribed_location = input_dict["location"]
        self.subscribed_location.settlement = self
        if not from_save:
            self.name = constants.FlavorTextManager.generate_flavor_text(
                "settlement_names"
            )
            if status.displayed_notification:
                on_remove_call = (
                    actor_utility.press_button,
                    [constants.RENAME_SETTLEMENT_BUTTON],
                )
                if constants.NotificationManager.notification_queue:
                    if not constants.NotificationManager.notification_queue[-1].get(
                        "on_remove", None
                    ):
                        constants.NotificationManager.notification_queue[-1][
                            "on_remove"
                        ] = []
                    constants.NotificationManager.notification_queue[-1][
                        "on_remove"
                    ].append(on_remove_call)
                else:
                    status.displayed_notification.on_remove.append(on_remove_call)
            else:
                actor_utility.press_button(constants.RENAME_SETTLEMENT_BUTTON)
        else:
            self.name = input_dict["name"]
        self.subscribed_location.set_name(self.name)

    def rename(self, new_name: str):
        """
        Description:
            Sets a new name for this settlement
        Input:
            string new_name: New name for this settlement
        Output:
            None
        """
        self.name = new_name
        status.displayed_location.set_name(self.name)

    def to_save_dict(self):
        """
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                'init_type': string value - Represents the type of actor this is, used to initialize the correct type of object on loading
                'name': string value - Name of this settlement
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
        """
        save_dict = {}
        save_dict["init_type"] = constants.SETTLEMENT
        save_dict["name"] = self.name
        return save_dict
