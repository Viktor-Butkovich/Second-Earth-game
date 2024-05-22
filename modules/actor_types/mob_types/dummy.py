# Contains functionality for dummies, which replicate other objects or act as models of hypothetical objects with fake attribute values and tooltips

from .. import mobs
import modules.constants.constants as constants


class dummy(mobs.mob):
    """
    Mock mob that can take any attribute values needed to get certain image or tooltip outputs without affecting rest of program
    """

    def __init__(self, input_dict):
        """
        input dict always includes dummy_type, which is generally equal to the init type of the unit being replicated?
        """
        for key in input_dict:
            setattr(self, key, input_dict[key])
        self.is_dummy = True

    def set_tooltip(self, tooltip_text):
        """
        Description:
            Sets this actor's tooltip to the inputted list without attempting to modify member images
        Input:
            string list new_tooltip: Lines for this actor's tooltip
        Output:
            None
        """
        self.tooltip_text = tooltip_text

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
        return self.image_id_list
