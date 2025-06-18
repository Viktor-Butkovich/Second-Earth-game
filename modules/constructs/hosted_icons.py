# contains functionality for cell icons, which act as hybrid interface element-actors

from typing import List, Dict


class hosted_icon:
    """
    An icon that exists within a location, indicating some current condition
        Displayed in the attached location's minimap overlay
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'image_id': image ID lists value - Image ID(s) for this icon
                'location': location value - Location where this icon is hosted
        Output:
            None
        """
        self.image_id: List[Dict[str, any]] = input_dict["image_id"]
        self.location = input_dict["location"]
        self.location.hosted_icons.append(self)

    def get_location(self) -> any:
        return self.location

    def get_image_id_list(self) -> List[Dict[str, any]]:
        return self.image_id

    def remove(self) -> None:
        self.location.hosted_icons.remove(self)
