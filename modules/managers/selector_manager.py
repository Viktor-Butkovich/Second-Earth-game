# Contains selector management singleton

from __future__ import annotations
from modules.constants import constants, status, flags
from modules.util import main_loop_utility, text_utility, actor_utility
from modules.interface_components import cells
from modules.action_types import construction
from typing import Dict, Any


class selector_manager:
    """
    Object that manages mouse selection
    """

    def __init__(self):
        """
        Initializes this object
        """
        self.current_selector: str = None
        self.config: Dict[str, Any] = {}

    def stop(self) -> None:
        """
        Deselects any current selector
        """
        self.current_selector = None

    def start(self, selector_type: str, config: Dict[str, Any] = None) -> None:
        """
        Description:
            Starts a selection of the given type
        Input:
            string selector_type: Type of selector to start
        Output:
            None
        """
        self.current_selector = selector_type
        self.config = config

    def is_active(self, selector_type: str) -> bool:
        """
        Description:
            Returns whether the given selector type is the current active selector
        Input:
            string selector_type: Type of selector to check
        Output:
            boolean: True if the given selector type is the current active selector, False otherwise
        """
        return self.current_selector == selector_type

    def any_active(self) -> bool:
        """
        Description:
            Returns whether any selector is currently active
        Input:
            None
        Output:
            boolean: True if any selector is currently active, False otherwise
        """
        return self.current_selector is not None

    def none_active(self) -> bool:
        """
        Description:
            Returns whether no selector is currently active
        Input:
            None
        Output:
            boolean: True if no selector is currently active, False otherwise
        """
        return not self.any_active()

    def on_click(self, lmb: bool) -> None:
        """
        Description:
            Handles the mouse button down event behavior for the current selector
                Only invoked when the event did not click a button
        Input:
            bool lmb: True if this mouse down event was a left mouse button down, otherwise False for right mouse button down
        Output:
            None
        """
        rmb = not lmb
        if self.is_active(constants.DESTINATION_SELECTOR):
            if lmb:
                target_cell = actor_utility.get_clicked_cell()
                if target_cell:
                    if select_destination(target_cell):
                        self.stop()
                else:
                    text_utility.print_to_screen(
                        f"Click on a location to send the {status.displayed_mob.name} there, or right click to cancel."
                    )
            elif rmb:
                self.stop()

        elif self.is_active(constants.ADVERTISING_SELECTOR):
            if lmb:
                text_utility.print_to_screen(
                    "Click on a commodity to advertise it, or right click to cancel."
                )
            elif rmb:
                self.stop()

        elif self.is_active(constants.CONSTRUCTION_SELECTOR):
            construction_action: construction.construction = self.config[
                constants.SELECTOR_CONFIG_CONSTRUCTION_ACTION
            ]
            target_cell = actor_utility.get_clicked_cell()
            if lmb:
                if (
                    target_cell
                    and target_cell.source.actor_type == constants.ZONE_ACTOR_TYPE
                ):
                    self.stop()
                    construction_action.start(
                        construction_action.current_unit, target_cell.source
                    )
                else:
                    text_utility.print_to_screen(
                        f"Click on a zone to start building {construction_action.building_type.name}, or right click to cancel."
                    )
            elif rmb:
                self.stop()

        else:
            raise Exception(
                f"Unhandled SelectorManager state {constants.SelectorManager.current_selector}"
            )


def select_destination(target_cell: cells.cell) -> bool:
    """
    Description:
        Sets the target cell as the current mob's movement destination
    Input:
        cell target_cell: Cell that was clicked to set as the movement destination
    Output:
        bool: True if the destination was successfully set, otherwise False
    """
    # If clicking to move somewhere
    target_location = target_cell.source
    if target_cell.grid.world_handler != status.displayed_mob.location.world_handler:
        actor_utility.click_move_minimap(target_cell, select_unit=False)
        status.displayed_mob.end_turn_destination = target_location
        status.displayed_mob.set_permission(constants.TRAVELING_PERMISSION, True)
        status.displayed_mob.travel_sound()
        flags.show_selection_outlines = True
        constants.last_selection_outline_switch = (
            constants.current_time
        )  # Outlines should be shown immediately once destination is chosen
        status.displayed_mob.remove_from_turn_queue()
        status.displayed_mob.select()
        status.displayed_mob.location.select()
        return True
    else:  # Cannot move to same world
        text_utility.print_to_screen("You can only send ships to other theatres.")
        return False
