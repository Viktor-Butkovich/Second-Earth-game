# Contains functionality for dummies, which replicate other objects or act as models of hypothetical objects with fake attribute values and tooltips

from typing import Dict, Any
from modules.constructs.actor_types.mob_types import pmobs
from modules.constants import constants, status, flags


class dummy(pmobs.pmob):
    """
    Mock mob that can take any attribute values needed to get certain image or tooltip outputs without affecting rest of program
    """

    def __init__(self, input_dict):
        """
        input dict always includes dummy_type, which is generally equal to the init type of the unit being replicated?
        """
        self.default_permissions: Dict[str, Any] = {}
        self.override_permissions: Dict[str, Any] = {}
        for key in input_dict:
            setattr(self, key, input_dict[key])
        self.set_permission(constants.DUMMY_PERMISSION, True)

    def get_image_id_list(self):
        """
        Description:
            Generates and returns a list this actor's image file paths and dictionaries that can be passed to any image object to display those images together in a particular order and
                orientation
        Input:
            None
        Output:
            list: Returns list of string image file paths, possibly combined with string key dictionaries with extra information for offset images
        """
        return super().get_image_id_list()

    def update_image_bundle(self):
        """
        Updates this actor's images with its current image id list
        """
        return
