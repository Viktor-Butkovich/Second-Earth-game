# contains functionality for cell icons, which act as hybrid interface element-actors

from ..actor_types.actors import actor
from ..util import utility
from ..constructs import images
import modules.constants.constants as constants
import modules.constants.status as status


class cell_icon(actor):
    """
    An actor that exists in a tile while also acting as an interface element
    """

    def __init__(self, from_save, input_dict):
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'grid': grid value - grid in which this tile can appear
                'modes': string list value - Game modes during which this actor's images can appear
        Output:
            None
        """
        super().__init__(from_save, input_dict)
        status.independent_interface_elements.append(self)
        self.showing = False
        self.image_dict = {"default": input_dict["image"]}
        self.images = [
            images.actor_image(
                self,
                current_grid.get_cell_width(),
                current_grid.get_cell_height(),
                current_grid,
                "default",
            )
            for current_grid in self.grids
        ]

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this icon can be shown. By default, it can be shown during game modes in which this grid can appear
        Input:
            None
        Output:
            boolean: Returns True if this grid can appear during the current game mode, otherwise returns False
        """
        return constants.current_game_mode in self.modes

    def can_draw(self):
        """
        Description:
            Calculates and returns whether it would be valid to call this object's draw()
        Input:
            None
        Output:
            boolean: Returns whether it would be valid to call this object's draw()
        """
        return self.showing

    def draw(self):
        """
        Description:
            Draws each of this icon's images
        Input:
            None
        Output:
            None
        """
        for current_image in self.images:
            current_image.draw()

    def remove(self):
        """
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        Input:
            None
        Output:
            None
        """
        super().remove()
        if self in status.independent_interface_elements:
            status.independent_interface_elements = utility.remove_from_list(
                status.independent_interface_elements, self
            )

    def can_show_tooltip(self):
        """
        Description:
            Returns whether this actor's tooltip can be shown. Cell icons should not have tooltips
        Input:
            None
        Output:
            None
        """
        return False


class name_icon(cell_icon):
    def __init__(self, from_save, input_dict):
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'grid': grid value - grid in which this tile can appear
                'modes': string list value - Game modes during which this actor's images can appear
        Output:
            None
        """
        super().__init__(from_save, input_dict)
        self.tile = input_dict["tile"]

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this icon can be shown. A name icon will be shown if its tile is visible and if it would not cover the currently selected unit
        Input:
            None
        Output:
            boolean: Returns True if this grid can appear during the current game mode, otherwise returns False
        """
        return super().can_show() and self.tile.cell.visible
