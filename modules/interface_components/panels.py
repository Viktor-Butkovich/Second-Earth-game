# Contains functionality for panels

from __future__ import annotations
from modules.util import actor_utility, main_loop_utility
from modules.interface_components.buttons import button
from modules.constants import constants, status, flags


class panel(button):
    """
    A button that does nothing when clicked and has an optional tooltip
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
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
        Output:
            None
        """
        input_dict["button_type"] = "panel"
        super().__init__(input_dict)

    def on_click(self):
        """
        Description:
            Panels have no on_click behavior, but, since they aren't whitespace, they don't prevent units from being deselected
        Input:
            None
        Output:
            string: Returns None to designate that this click did nothing - still prevents units from deselected but also allows other buttons to be clicked
        """
        flags.choosing_advertised_item = False
        flags.choosing_destination = False
        return None

    def can_show_tooltip(self):
        """
        Panels have no tooltips
        """
        return False

    def draw(self):
        """
        Draws this panel, ignoring outlines from the panel being clicked
        """
        if self.showing:
            super().draw(allow_show_outline=False)


class safe_click_panel(panel):
    """
    Panel that prevents selected units/ministers/countries from being deselected when its area is clicked
    """

    def can_show(self):
        """
        Description:
            Returns whether this panel should be drawn - it is drawn when an actor is selected, or if on the location mode
        Input:
            None
        Output:
            boolean: Returns False if the selected vehicle has no crew, otherwise returns same as superclass
        """
        return super().can_show() and (
            status.displayed_mob
            or status.displayed_location
            or status.displayed_minister
            or constants.current_game_mode == constants.LOCATION_MODE
        )

    def on_click(self) -> None:
        if status.focused_location_grid.cell_list[0][0].touching_mouse():
            main_loop_utility.manage_lmb_down(clicked_button=False)
            return
        actor_utility.calibrate_actor_info_display(
            status.mob_inventory_info_display, None
        )
        actor_utility.calibrate_actor_info_display(
            status.location_inventory_info_display, None
        )

    def on_rmb_click(self) -> None:
        if status.focused_location_grid.cell_list[0][0].touching_mouse():
            main_loop_utility.manage_rmb_down(clicked_button=False)
            return
        super().on_rmb_click()
