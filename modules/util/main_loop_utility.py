# Contains functions used in the game's main loop and event management

import pygame
import time
from . import (
    scaling,
    text_utility,
    actor_utility,
    minister_utility,
    utility,
    traversal_utility,
)
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags


def update_display():
    """
    Description:
        Draws all images and shapes and calls the functions to draw tooltips and the text box
    Input:
        None
    Output:
        None
    """
    if flags.loading:
        flags.loading_start_time -= (
            1  # end load timer faster once program starts repeating this part
        )
        draw_loading_screen()
    else:
        possible_tooltip_drawers = []
        traversal_utility.draw_interface_elements(status.independent_interface_elements)
        # could modify with a layer dictionary to display elements on different layers - currently, drawing elements in order of collection creation is working w/o overlap
        # issues

        displayed_tile = status.displayed_tile
        if displayed_tile:
            displayed_tile.draw_actor_match_outline(False)

        if status.displayed_mob:
            status.displayed_mob.draw_outline()

        for current_mob in status.mob_list:
            if current_mob.can_show_tooltip():
                for same_tile_mob in current_mob.images[0].current_cell.contained_mobs:
                    if (
                        same_tile_mob.can_show_tooltip()
                        and not same_tile_mob in possible_tooltip_drawers
                    ):  # if multiple mobs are in the same tile, draw their tooltips in order
                        possible_tooltip_drawers.append(same_tile_mob)

        for current_building in status.building_list:
            if current_building.can_show_tooltip():
                possible_tooltip_drawers.append(current_building)

        for current_actor in status.actor_list:
            if (
                current_actor.can_show_tooltip()
                and not current_actor in possible_tooltip_drawers
            ):
                possible_tooltip_drawers.append(
                    current_actor
                )  # only one of these will be drawn to prevent overlapping tooltips

        notification_tooltip_button = None
        for current_button in status.button_list:
            if (
                current_button.can_show_tooltip()
            ):  # while multiple actor tooltips can be shown at once, if a button tooltip is showing no other tooltips should be showing
                if (
                    current_button.in_notification
                    and current_button != status.current_instructions_page
                ):
                    notification_tooltip_button = current_button
                else:
                    possible_tooltip_drawers = [current_button]

        if notification_tooltip_button:
            possible_tooltip_drawers = [notification_tooltip_button]
        else:
            for current_free_image in status.free_image_list:
                if current_free_image.can_show_tooltip():
                    possible_tooltip_drawers = [current_free_image]

        draw_text_box()

        constants.mouse_follower.draw()

        if status.current_instructions_page:
            status.current_instructions_page.draw()
            if (
                status.current_instructions_page.can_show_tooltip()
            ):  # while multiple actor tooltips can be shown at once, if a button tooltip is showing no other tooltips should be showing
                possible_tooltip_drawers = [
                    status.current_instructions_page
                ]  # instructions have priority over everything
        if (constants.old_mouse_x, constants.old_mouse_y) != pygame.mouse.get_pos():
            constants.mouse_moved_time = constants.current_time
            constants.old_mouse_x, constants.old_mouse_y = pygame.mouse.get_pos()
        if (
            time.time() > constants.mouse_moved_time + 0.15
        ):  # show tooltip when mouse is still
            manage_tooltip_drawing(possible_tooltip_drawers)

    pygame.display.update()

    if constants.effect_manager.effect_active("track_fps"):
        current_time = time.time()
        constants.frames_this_second += 1
        if current_time > constants.last_fps_update + 1 and flags.startup_complete:
            constants.fps_tracker.set(constants.frames_this_second)
            constants.frames_this_second = 0
            constants.last_fps_update = current_time


def action_possible():
    """
    Description:
        Because of this function, ongoing events such as trading, exploring, and clicking on a movement destination prevent actions such as pressing buttons from being done except when required by the event
    Input:
        None
    Output:
        boolean: Returns False if the player is in an ongoing event that prevents other actions from being taken, otherwise returns True
    """
    return not (
        status.displayed_notification
        or (not flags.player_turn)
        or flags.choosing_destination
        or flags.choosing_advertised_commodity
        or flags.drawing_automatic_route
    )


def draw_loading_screen():
    """
    Description:
        Draws the loading screen, occupying the entire screen and blocking objects when the game is loading
    Input:
        None
    Output:
        None
    """
    status.loading_image.draw()
    if (
        flags.loading_start_time + 1.01 < time.time()
    ):  # max of 1 second, subtracts 1 in update_display to lower loading screen showing time
        flags.loading = False


def manage_tooltip_drawing(possible_tooltip_drawers):
    """
    Description:
        Decides whether each of the inputted objects should have their tooltips drawn based on if they are covered by other objects. The tooltip of each chosen object is drawn in order with correct placement and spacing
    Input:
        object list possible_tooltip_drawers: All objects that possess tooltips and are currently touching the mouse and being drawn
    Output:
        None
    """
    possible_tooltip_drawers_length = len(possible_tooltip_drawers)
    font = constants.fonts["default"]
    y_displacement = scaling.scale_width(30)  # estimated mouse size
    if possible_tooltip_drawers_length == 0:
        return ()
    elif possible_tooltip_drawers_length == 1:
        height = y_displacement
        height += font.size * (len(possible_tooltip_drawers[0].tooltip_text) + 1)
        possible_tooltip_drawers[0].update_tooltip()
        width = possible_tooltip_drawers[0].tooltip_box.width
        mouse_x, mouse_y = pygame.mouse.get_pos()
        below_screen = False
        beyond_screen = False
        if (constants.display_height + 10 - mouse_y) - height < 0:
            below_screen = True
        if mouse_x + width > constants.display_width:
            beyond_screen = True
        possible_tooltip_drawers[0].draw_tooltip(
            below_screen, beyond_screen, height, width, y_displacement
        )
    else:
        stopping = False
        height = y_displacement
        width = 0
        for possible_tooltip_drawer in possible_tooltip_drawers:
            possible_tooltip_drawer.update_tooltip()
            if possible_tooltip_drawer == status.current_instructions_page:
                height += font.size * (len(possible_tooltip_drawer.tooltip_text) + 1)
                width = possible_tooltip_drawer.tooltip_box.width
                stopping = True
            elif (
                possible_tooltip_drawer in status.button_list
                and possible_tooltip_drawer.in_notification
            ) and not stopping:
                height += font.size * (len(possible_tooltip_drawer.tooltip_text) + 1)
                width = possible_tooltip_drawer.tooltip_box.width
                stopping = True
        if not stopping:
            for possible_tooltip_drawer in possible_tooltip_drawers:
                height += font.size * (len(possible_tooltip_drawer.tooltip_text) + 1)
                if possible_tooltip_drawer.tooltip_box.width > width:
                    width = possible_tooltip_drawer.tooltip_box.width
        mouse_x, mouse_y = pygame.mouse.get_pos()
        below_screen = False  # if goes below bottom side
        beyond_screen = False  # if goes beyond right side
        if (constants.display_height + 10 - mouse_y) - height < 0:
            below_screen = True
        if mouse_x + width > constants.display_width:
            beyond_screen = True
        stopping = False
        for possible_tooltip_drawer in possible_tooltip_drawers:
            if possible_tooltip_drawer == status.current_instructions_page:
                possible_tooltip_drawer.draw_tooltip(
                    below_screen, beyond_screen, height, width, y_displacement
                )
                y_displacement += font.size * (
                    len(possible_tooltip_drawer.tooltip_text) + 1
                )
                stopping = True
            elif (
                possible_tooltip_drawer in status.button_list
                and possible_tooltip_drawer.in_notification
            ) and not stopping:
                possible_tooltip_drawer.draw_tooltip(
                    below_screen, beyond_screen, height, width, y_displacement
                )
                y_displacement += font.size * (
                    len(possible_tooltip_drawer.tooltip_text) + 1
                )
                stopping = True
        if not stopping:
            for possible_tooltip_drawer in possible_tooltip_drawers:
                possible_tooltip_drawer.draw_tooltip(
                    below_screen, beyond_screen, height, width, y_displacement
                )
                y_displacement += font.size * (
                    len(possible_tooltip_drawer.tooltip_text) + 1
                )


def draw_text_box():
    """
    Description:
        Draws the text input and output box at the bottom left of the screen along with the text it contains
    Input:
        None
    Output:
        None
    """
    greatest_width = scaling.scale_width(300)

    if flags.expand_text_box:
        constants.text_box_height = scaling.scale_height(
            constants.default_display_height - 60
        )
    else:
        constants.text_box_height = constants.default_text_box_height

    font = constants.fonts["default"]
    max_screen_lines = (constants.default_display_height // font.size) - 1
    max_text_box_lines = (constants.text_box_height // font.size) - 1
    for text_index in range(len(status.text_list)):
        if text_index < max_text_box_lines:
            greatest_width = max(
                greatest_width, font.calculate_size(status.text_list[-text_index - 1])
            )
    if constants.input_manager.taking_input:
        greatest_width = max(
            font.calculate_size("Response: " + constants.message), greatest_width
        )  # manages width of user input
    else:
        greatest_width = max(
            font.calculate_size(constants.message), greatest_width
        )  # manages width of user input
    text_box_width = greatest_width + scaling.scale_width(10)
    x, y = (0, constants.display_height - constants.text_box_height)
    pygame.draw.rect(
        constants.game_display,
        constants.color_dict["white"],
        (x, y, text_box_width, constants.text_box_height),
    )  # draws white rect to prevent overlapping
    if flags.typing:
        color = "red"
    else:
        color = "black"
    pygame.draw.rect(
        constants.game_display,
        constants.color_dict[color],
        (x, y, text_box_width, constants.text_box_height),
        scaling.scale_height(3),
    )  # black text box outline
    pygame.draw.line(
        constants.game_display,
        constants.color_dict[color],
        (
            0,
            constants.display_height - (font.size + scaling.scale_height(5)),
        ),  # input line
        (
            text_box_width,
            constants.display_height - (font.size + scaling.scale_height(5)),
        ),
    )

    status.text_list = text_utility.manage_text_list(
        status.text_list, max_screen_lines
    )  # number of lines

    for text_index in range(len(status.text_list)):
        if text_index < max_text_box_lines:
            textsurface = constants.myfont.pygame_font.render(
                status.text_list[(-1 * text_index) - 1], False, (0, 0, 0)
            )
            constants.game_display.blit(
                textsurface,
                (
                    scaling.scale_width(10),
                    (-1 * font.size * text_index)
                    + constants.display_height
                    - ((2 * font.size) + scaling.scale_height(5)),
                ),
            )
    if constants.input_manager.taking_input:
        textsurface = constants.myfont.pygame_font.render(
            "Response: " + constants.message, False, (0, 0, 0)
        )
    else:
        textsurface = constants.myfont.pygame_font.render(
            constants.message, False, (0, 0, 0)
        )
    constants.game_display.blit(
        textsurface,
        (
            scaling.scale_width(10),
            constants.display_height - (font.size + scaling.scale_height(5)),
        ),
    )


def manage_rmb_down(clicked_button):
    """
    Description:
        If the player is right clicking on a grid cell, cycles the order of the units in the cell. Otherwise, has same functionality as manage_lmb_down
    Input:
        boolean clicked_button: True if this click clicked a button, otherwise False
    Output:
        None
    """
    stopping = False
    if (not clicked_button) and action_possible():
        for current_grid in status.grid_list:
            if (
                current_grid.showing
            ):  # if constants.current_game_mode in current_grid.modes:
                for current_cell in current_grid.get_flat_cell_list():
                    if current_cell.touching_mouse():
                        stopping = True  # if doesn't reach this point, do same as lmb
                        if len(current_cell.contained_mobs) > 1:
                            moved_mob = current_cell.contained_mobs[1]
                            for current_image in moved_mob.images:
                                if not current_image.current_cell == "none":
                                    while (
                                        not moved_mob
                                        == current_image.current_cell.contained_mobs[0]
                                    ):
                                        current_image.current_cell.contained_mobs.append(
                                            current_image.current_cell.contained_mobs.pop(
                                                0
                                            )
                                        )
                            flags.show_selection_outlines = True
                            constants.last_selection_outline_switch = (
                                constants.current_time
                            )
                            if status.minimap_grid in moved_mob.grids:
                                status.minimap_grid.calibrate(moved_mob.x, moved_mob.y)
                            moved_mob.select()
                            if moved_mob.is_pmob:
                                moved_mob.selection_sound()
    elif flags.drawing_automatic_route:
        stopping = True
        flags.drawing_automatic_route = False
        if len(status.displayed_mob.base_automatic_route) > 1:
            destination_coordinates = (
                status.displayed_mob.base_automatic_route[-1][0],
                status.displayed_mob.base_automatic_route[-1][1],
            )
            if (
                status.displayed_mob.is_vehicle
                and status.displayed_mob.vehicle_type == "train"
                and not status.strategic_map_grid.find_cell(
                    destination_coordinates[0], destination_coordinates[1]
                ).has_intact_building("train_station")
            ):
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
                "The created route must go between at least 2 tiles"
            )
        status.minimap_grid.calibrate(status.displayed_mob.x, status.displayed_mob.y)
        actor_utility.calibrate_actor_info_display(
            status.tile_info_display, status.displayed_mob.images[0].current_cell.tile
        )
    if not stopping:
        manage_lmb_down(clicked_button)


def manage_lmb_down(clicked_button):
    """
    Description:
        If the player is choosing a movement destination and the player clicks on a cell, chooses that cell as the movement destination. If the player is choosing a movement destination but did not click a cell, cancels the movement
            destination selection process. Otherwise, if the player clicks on a cell, selects the top mob in that cell if any are present and moves the minimap to that cell. If the player clicks on a button, calls the on_click function
            of that button. If nothing was clicked, deselects the selected mob if any is selected
    Input:
        boolean clicked_button: True if this click clicked a button, otherwise False
    Output:
        None
    """
    if (
        action_possible()
        or flags.choosing_destination
        or flags.choosing_advertised_commodity
        or flags.drawing_automatic_route
    ):
        if not clicked_button and (
            not (
                flags.choosing_destination
                or flags.choosing_advertised_commodity
                or flags.drawing_automatic_route
            )
        ):  # do not do selecting operations if user was trying to click a button #and action_possible()
            selected_mob = False
            for current_grid in status.grid_list:
                if (
                    current_grid.showing
                ):  # if constants.current_game_mode in current_grid.modes:
                    for current_cell in current_grid.get_flat_cell_list():
                        if current_cell.touching_mouse():
                            if current_cell.terrain_handler.visible:
                                if len(current_cell.contained_mobs) > 0:
                                    selected_mob = True
                                    current_mob = current_cell.contained_mobs[0]
                                    actor_utility.calibrate_actor_info_display(
                                        status.mob_info_display,
                                        None,
                                        override_exempt=True,
                                    )
                                    current_mob.select()
                                    if current_mob.is_pmob:
                                        current_mob.selection_sound()
            if selected_mob:
                unit = status.displayed_mob
                if unit and unit.grids[0] == status.minimap_grid.attached_grid:
                    status.minimap_grid.calibrate(unit.x, unit.y)
            else:
                if constants.current_game_mode == "ministers":
                    minister_utility.calibrate_minister_info_display(None)
                elif constants.current_game_mode == "new_game_setup":
                    nothing = 0
                else:
                    actor_utility.calibrate_actor_info_display(
                        status.mob_info_display, None, override_exempt=True
                    )
                    actor_utility.calibrate_actor_info_display(
                        status.tile_info_display, None, override_exempt=True
                    )
                click_move_minimap()

        elif (
            not clicked_button
        ) and flags.choosing_destination:  # if clicking to move somewhere
            for current_grid in status.grid_list:  # destination_grids:
                if current_grid.can_show():
                    for current_cell in current_grid.get_flat_cell_list():
                        if current_cell.touching_mouse():
                            click_move_minimap()
                            target_cell = "none"
                            if current_cell.grid.is_abstract_grid:
                                target_cell = current_cell
                            else:
                                target_cell = status.strategic_map_grid.find_cell(
                                    status.minimap_grid.center_x,
                                    status.minimap_grid.center_y,
                                )  # center
                            if not current_grid in status.displayed_mob.grids:
                                stopping = False
                                if (
                                    not current_grid.is_abstract_grid
                                ):  # if grid has more than 1 cell, check if correct part of grid
                                    (
                                        destination_x,
                                        destination_y,
                                    ) = target_cell.tile.get_main_grid_coordinates()
                                    if (
                                        (
                                            not (
                                                destination_y == 0
                                                or (
                                                    destination_y == 1
                                                    and target_cell.has_intact_building(
                                                        "port"
                                                    )
                                                )
                                            )
                                        )
                                        and destination_x >= 0
                                        and destination_x
                                        < status.strategic_map_grid.coordinate_width
                                    ):  # or is harbor
                                        text_utility.print_to_screen(
                                            "You can only send ships to coastal waters and coastal ports."
                                        )
                                        stopping = False  # True
                                if not stopping:
                                    status.displayed_mob.end_turn_destination = (
                                        target_cell.tile
                                    )
                                    status.displayed_mob.movement_sound(
                                        allow_fadeout=False
                                    )
                                    flags.show_selection_outlines = True
                                    constants.last_selection_outline_switch = (
                                        constants.current_time
                                    )  # outlines should be shown immediately once destination is chosen
                                    status.displayed_mob.remove_from_turn_queue()
                                    status.displayed_mob.select()
                                    status.displayed_mob.images[
                                        0
                                    ].current_cell.tile.select()
                            else:  # cannot move to same continent
                                actor_utility.calibrate_actor_info_display(
                                    status.mob_info_display, None
                                )
                                text_utility.print_to_screen(
                                    "You can only send ships to other theatres."
                                )
            flags.choosing_destination = False

        elif (not clicked_button) and flags.choosing_advertised_commodity:
            flags.choosing_advertised_commodity = False

        elif (not clicked_button) and flags.drawing_automatic_route:
            for current_grid in status.grid_list:  # destination_grids:
                for current_cell in current_grid.get_flat_cell_list():
                    if current_cell.touching_mouse():
                        if current_cell.grid.is_abstract_grid:
                            text_utility.print_to_screen(
                                "Only tiles adjacent to the most recently chosen destination can be added to the movement route."
                            )
                        else:
                            displayed_mob = status.displayed_mob
                            if current_cell.grid.is_mini_grid:
                                target_tiles = current_cell.tile.get_equivalent_tiles()
                                if not target_tiles:
                                    return ()
                                else:
                                    target_cell = target_tiles[0].cell
                            else:
                                target_cell = current_cell
                            # target_cell = status.strategic_map_grid.find_cell(status.minimap_grid.center_x, status.minimap_grid.center_y)
                            destination_x, destination_y = (
                                target_cell.x,
                                target_cell.y,
                            )  # target_cell.tile.get_main_grid_coordinates()
                            (
                                previous_destination_x,
                                previous_destination_y,
                            ) = displayed_mob.base_automatic_route[-1]
                            if (
                                utility.find_coordinate_distance(
                                    (destination_x, destination_y),
                                    (previous_destination_x, previous_destination_y),
                                )
                                == 1
                            ):
                                destination_infrastructure = target_cell.get_building(
                                    "infrastructure"
                                )
                                if not target_cell.terrain_handler.visible:
                                    text_utility.print_to_screen(
                                        "Movement routes cannot be created through unexplored tiles."
                                    )
                                    return ()
                                elif (
                                    displayed_mob.is_vehicle
                                    and displayed_mob.vehicle_type == "train"
                                    and not target_cell.has_building("railroad")
                                ):
                                    text_utility.print_to_screen(
                                        "Trains can only create movement routes along railroads."
                                    )
                                    return ()
                                elif (
                                    target_cell.terrain_handler.terrain == "water"
                                    and not displayed_mob.can_swim
                                ) and (
                                    displayed_mob.is_vehicle
                                    and destination_infrastructure == "none"
                                ):
                                    # non-train units can still move slowly through water, even w/o canoes or a bridge
                                    # railroad bridge allows anything to move through
                                    text_utility.print_to_screen(
                                        "This unit cannot create movement routes through water."
                                    )
                                    return ()
                                elif (
                                    (not target_cell.terrain_handler.terrain == "water")
                                    and (not displayed_mob.can_walk)
                                    and not target_cell.has_intact_building("port")
                                ):
                                    text_utility.print_to_screen(
                                        "This unit cannot create movement routes on land, except through ports."
                                    )
                                    return ()

                                displayed_mob.add_to_automatic_route(
                                    (destination_x, destination_y)
                                )
                                click_move_minimap()
                                flags.show_selection_outlines = True
                                constants.last_selection_outline_switch = (
                                    constants.current_time
                                )
                            else:
                                text_utility.print_to_screen(
                                    "Only tiles adjacent to the most recently chosen destination can be added to the movement route."
                                )

        elif not clicked_button:
            click_move_minimap()


def click_move_minimap():
    """
    Description:
        When a cell on the strategic map grid is clicked, centers the minimap on that cell
    Input:
        None
    Output:
        None
    """
    for (
        current_grid
    ) in status.grid_list:  # if grid clicked, move minimap to location clicked
        if current_grid.showing:
            for current_cell in current_grid.get_flat_cell_list():
                if current_cell.touching_mouse():
                    if (
                        current_grid in status.strategic_map_grid.mini_grids
                    ):  # if minimap clicked, calibrate to corresponding place on main map and all mini maps
                        if (
                            current_cell.terrain_handler.terrain != "none"
                        ):  # if off map, do not move minimap there
                            main_x, main_y = current_grid.get_main_grid_coordinates(
                                current_cell.x, current_cell.y
                            )
                            current_grid.calibrate(main_x, main_y)
                    elif current_grid == status.strategic_map_grid:
                        status.minimap_grid.calibrate(current_cell.x, current_cell.y)
                    else:  # if abstract grid, show the inventory of the tile clicked without calibrating minimap
                        actor_utility.calibrate_actor_info_display(
                            status.tile_info_display, current_grid.cell_list[0][0].tile
                        )
                    return


def debug_print():
    """
    Description:
        Called by main_loop to print some value whenver p is pressed - printed value modified for various debugging purposes
    Input:
        None
    Output:
        None
    """
    print("")
    print(constants.effect_manager)
