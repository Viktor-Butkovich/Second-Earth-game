# Contains functionality for settlements

from modules.util import utility, actor_utility
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
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'name': string value - Required if from save, starting name of settlement
        Output:
            None
        """
        return
        # Rework settlements to be part of locations and saved with them
        self.x, self.y = input_dict["coordinates"]
        self.cell = status.strategic_map_grid.find_cell(self.x, self.y)
        self.cell.settlement = self
        self.x = self.cell.x
        self.y = self.cell.y
        if not from_save:
            self.name = constants.flavor_text_manager.generate_flavor_text(
                "settlement_names"
            )
            if status.displayed_notification:
                on_remove_call = (
                    actor_utility.press_button,
                    [constants.RENAME_SETTLEMENT_BUTTON],
                )
                if constants.notification_manager.notification_queue:
                    if not constants.notification_manager.notification_queue[-1].get(
                        "on_remove", None
                    ):
                        constants.notification_manager.notification_queue[-1][
                            "on_remove"
                        ] = []
                    constants.notification_manager.notification_queue[-1][
                        "on_remove"
                    ].append(on_remove_call)
                else:
                    status.displayed_notification.on_remove.append(on_remove_call)
            else:
                actor_utility.press_button(constants.RENAME_SETTLEMENT_BUTTON)
        else:
            self.name = input_dict["name"]
        self.cell.tile.set_name(self.name)
        status.actor_list.append(self)
        status.settlement_list.append(self)

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
        actor_utility.calibrate_actor_info_display(
            status.location_info_display, status.displayed_location
        )

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
        save_dict["coordinates"] = (self.x, self.y)
        return save_dict

    def remove(self):
        """
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        Input:
            None
        Output:
            None
        """
        status.actor_list = utility.remove_from_list(status.actor_list, self)
        status.settlement_list = utility.remove_from_list(status.settlement_list, self)
        self.cell.settlement = None

    def can_show_tooltip(self):
        """
        Description:
            Returns whether this actor's tooltip can be shown
        Input:
            None
        Output:
            None
        """
        return False
