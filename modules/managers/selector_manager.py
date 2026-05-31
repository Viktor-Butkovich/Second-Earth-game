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

        elif self.is_active(constants.AUTOMATIC_ROUTE_SELECTOR):
            target_cell = actor_utility.get_clicked_cell()
            if lmb:
                if target_cell:
                    append_automatic_route(target_cell)
                else:
                    text_utility.print_to_screen(
                        "Click on a location to add it to the movement route, or right click to finish the route."
                    )
            elif rmb:
                self.stop()
                complete_automatic_route()

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


def append_automatic_route(target_cell: cells.cell) -> None:
    """
    Description:
        Appends the target cell's location to the current mob's automatic movement route
    Input:
        cell target_cell: Cell that was clicked to append to the movement route
    Output:
        None
    """
    if target_cell.source.is_abstract_location:
        text_utility.print_to_screen(
            "Only locations adjacent to the most recently chosen destination can be added to the movement route."
        )
    else:
        target_location = target_cell.source
        previous_location = status.displayed_mob.base_automatic_route[-1]
        current_world = target_location.world_handler
        if current_world.manhattan_distance(target_location, previous_location) == 1:
            if not target_location.visible:
                text_utility.print_to_screen(
                    "Movement routes cannot be created through unexplored locations."
                )
            elif (
                status.displayed_mob.get_permission(constants.VEHICLE_PERMISSION)
                and status.displayed_mob.get_permission(constants.TRAIN_PERMISSION)
                and not target_location.has_building(constants.RAILROAD)
            ):
                text_utility.print_to_screen(
                    "Trains can only create movement routes along railroads."
                )
            elif not status.displayed_mob.get_permission(
                constants.WALK_PERMISSION
            ) and not target_location.has_intact_building(constants.SPACEPORT):
                text_utility.print_to_screen(
                    "This unit cannot create movement routes on land, except through ports."
                )
            else:
                status.displayed_mob.add_to_automatic_route(target_location)
                actor_utility.click_move_minimap(target_cell, select_unit=False)
                flags.show_selection_outlines = True
                constants.last_selection_outline_switch = constants.current_time
        else:
            text_utility.print_to_screen(
                "Only locations adjacent to the most recently chosen destination can be added to the movement route."
            )


def complete_automatic_route() -> None:
    """
    Validates and completes the creation of current mob's automatic movement route
    """
    if len(status.displayed_mob.base_automatic_route) > 1:
        destination_location = (
            status.displayed_mob.location.world_handler.find_location(
                status.displayed_mob.base_automatic_route[-1][0],
                status.displayed_mob.base_automatic_route[-1][1],
            )
        )
        if status.displayed_mob.all_permissions(
            constants.VEHICLE_PERMISSION, constants.TRAIN_PERMISSION
        ) and not destination_location.has_intact_building(constants.TRAIN_STATION):
            status.displayed_mob.clear_automatic_route()
            text_utility.print_to_screen(
                "A train's automatic route must start and end at a train station."
            )
            text_utility.print_to_screen("The invalid route has been erased.")
        else:
            text_utility.print_to_screen("Route saved")
    else:
        status.displayed_mob.clear_automatic_route()
        text_utility.print_to_screen(
            "The created route must go between at least 2 locations"
        )
    actor_utility.focus_minimap_grids(status.displayed_mob.location)
    actor_utility.calibrate_actor_info_display(
        status.location_info_display, status.displayed_mob.location
    )
