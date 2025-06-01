# Contains functions used in the game's main loop and event management

import pygame
import time
from modules.util import (
    scaling,
    text_utility,
    actor_utility,
    utility,
    traversal_utility,
    minister_utility,
)
from modules.constants import constants, status, flags


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
        draw_loading_screen()
    else:
        traversal_utility.draw_interface_elements(status.independent_interface_elements)
        # could modify with a layer dictionary to display elements on different layers - currently, drawing elements in order of collection creation is working w/o overlap
        # issues

        tooltip_drawer = None
        if (
            time.time() > constants.mouse_moved_time + 0.15
        ):  # Wait until mouse is still before drawing tooltips
            for current_grid in status.grid_list:
                if not tooltip_drawer:
                    tooltip_drawer = next(
                        (
                            current_cell
                            for current_cell in current_grid.get_flat_cell_list()
                            if current_cell.can_show_tooltip()
                        ),
                        None,
                    )  # Find the first cell that can draw a tooltip

            notification_tooltip_button = False
            for current_button in status.button_list:
                if current_button.can_show_tooltip():
                    if (
                        current_button.in_notification
                        and current_button != status.current_instructions_page
                    ):
                        tooltip_drawer = current_button
                        notification_tooltip_button = True
                    else:
                        tooltip_drawer = current_button

            if not notification_tooltip_button:
                for current_free_image in status.free_image_list:
                    if current_free_image.can_show_tooltip():
                        tooltip_drawer = current_free_image
                        break

        draw_text_box()

        constants.mouse_follower.draw()

        if status.current_instructions_page:
            status.current_instructions_page.draw()
            if (
                status.current_instructions_page.can_show_tooltip()
            ):  # While multiple actor tooltips can be shown at once, if a button tooltip is showing no other tooltips should be showing
                tooltip_drawer = (
                    status.current_instructions_page
                )  # instructions have highest priority over everything
        if (constants.old_mouse_x, constants.old_mouse_y) != pygame.mouse.get_pos():
            constants.mouse_moved_time = constants.current_time
            constants.old_mouse_x, constants.old_mouse_y = pygame.mouse.get_pos()
        if tooltip_drawer:
            manage_tooltip_drawing(tooltip_drawer)

    pygame.display.update()

    if constants.effect_manager.effect_active("track_fps"):
        current_time = time.time()
        constants.frames_this_second += 1
        if current_time > constants.last_fps_update + 1 and flags.startup_complete:
            constants.fps_tracker.set(constants.frames_this_second)
            constants.frames_this_second = 0
            constants.last_fps_update = current_time

    if (
        constants.effect_manager.effect_active("track_mouse_position")
        and flags.startup_complete
    ):
        constants.mouse_position_tracker.set(pygame.mouse.get_pos())


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
        or flags.choosing_advertised_item
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
    status.loading_screen_quote_banner.showing = True
    status.loading_screen_quote_banner.draw()
    constants.loading_loops += 1
    if constants.loading_loops > 2:
        flags.loading = False
        if status.loading_screen_quote_banner.message != [""]:  # If loading into game
            status.loading_screen_continue_banner.showing = True
            status.loading_screen_continue_banner.draw()
            pygame.event.get()
            for current_button in status.button_list:
                current_button.on_release()
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        return
                    elif event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    elif event.type == constants.music_endevent:
                        constants.sound_manager.song_done()
                pygame.display.update()


def manage_tooltip_drawing(tooltip_drawer):
    """
    Description:
        Decides whether each of the inputted objects should have their tooltips drawn based on if they are covered by other objects. The tooltip of each chosen object is drawn in order with correct placement and spacing
    Input:
        object tooltip_drawer: Object to draw tooltip for
    Output:
        None
    """
    font = constants.fonts["default"]
    y_displacement = scaling.scale_width(30)  # estimated mouse size
    if (
        hasattr(tooltip_drawer, "supports_batch_tooltip")
        and tooltip_drawer.supports_batch_tooltip
    ):
        height = y_displacement
        width = 0
        batch_tooltip_list = tooltip_drawer.batch_tooltip_list
        for tooltip in batch_tooltip_list:
            height += font.size * (len(tooltip["text"]) + 1)
            if tooltip["box"].width > width:
                width = tooltip["box"].width
        mouse_x, mouse_y = pygame.mouse.get_pos()
        below_screen = False  # if goes below bottom side
        beyond_screen = False  # if goes beyond right side
        if (constants.display_height + 10 - mouse_y) - height < 0:
            below_screen = True
        if mouse_x + width > constants.display_width:
            beyond_screen = True

        for tooltip in batch_tooltip_list:
            draw_tooltip(
                tooltip, below_screen, beyond_screen, height, width, y_displacement
            )
            y_displacement += font.size * (len(tooltip["text"]) + 1)
    else:  # If only showing 1 tooltip
        height = y_displacement
        height += font.size * (len(tooltip_drawer.tooltip_text) + 1)
        tooltip_drawer.update_tooltip()
        width = tooltip_drawer.tooltip_box.width
        mouse_x, mouse_y = pygame.mouse.get_pos()
        below_screen = False
        beyond_screen = False
        if (constants.display_height + 10 - mouse_y) - height < 0:
            below_screen = True
        if mouse_x + width > constants.display_width:
            beyond_screen = True
        tooltip_drawer.draw_tooltip(
            below_screen, beyond_screen, height, width, y_displacement
        )


def draw_tooltip(tooltip, below_screen, beyond_screen, height, width, y_displacement):
    """
    Description:
        Draws the inputted tooltip when moused over. The tooltip's location may vary when the tooltip is near the edge of the screen or if multiple tooltips are being shown
    Input:
        dict tooltip: Dictionary containing the tooltip's text (string list), box (pygame.Rect), and outline (pygame.Rect)
        boolean below_screen: Whether any of the currently showing tooltips would be below the bottom edge of the screen. If True, moves all tooltips up to prevent any from being below the screen
        boolean beyond_screen: Whether any of the currently showing tooltips would be beyond the right edge of the screen. If True, moves all tooltips to the left to prevent any from being beyond the screen
        int height: Combined pixel height of all tooltips
        int width: Pixel width of the widest tooltip
        int y_displacement: How many pixels below the mouse this tooltip should be, depending on the order of the tooltips
    Output:
        None
    """
    mouse_x, mouse_y = pygame.mouse.get_pos()
    if below_screen:
        mouse_y = constants.display_height + 10 - height
    if beyond_screen:
        mouse_x = constants.display_width - width
    mouse_y += y_displacement

    if (mouse_x + tooltip["box"].width) > constants.display_width:
        mouse_x = constants.display_width - tooltip["box"].width
    tooltip["box"].x = mouse_x
    tooltip["box"].y = mouse_y
    tooltip["outline"].x = tooltip["box"].x - tooltip["outline_width"]
    tooltip["outline"].y = tooltip["box"].y - tooltip["outline_width"]
    pygame.draw.rect(
        constants.game_display,
        constants.color_dict[constants.COLOR_BLACK],
        tooltip["outline"],
    )
    pygame.draw.rect(
        constants.game_display,
        constants.color_dict[constants.COLOR_WHITE],
        tooltip["box"],
    )
    for text_line_index in range(len(tooltip["text"])):
        text_line = tooltip["text"][text_line_index]
        constants.game_display.blit(
            text_utility.text(text_line, constants.myfont),
            (
                tooltip["box"].x + scaling.scale_width(10),
                tooltip["box"].y + (text_line_index * constants.fonts["default"].size),
            ),
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
        constants.color_dict[constants.COLOR_WHITE],
        (x, y, text_box_width, constants.text_box_height),
    )  # draws white rect to prevent overlapping
    if flags.typing:
        color = constants.COLOR_RED
    else:
        color = constants.COLOR_BLACK
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
                        current_location = current_cell.get_location()
                        if len(current_location.subscribed_mobs) > 1:
                            moved_mob = current_location.subscribed_mobs[1]
                            while moved_mob != current_location.subscribed_mobs[0]:
                                current_location.subscribed_mobs.append(
                                    current_location.subscribed_mobs.pop(0)
                                )
                            current_location.update_image_bundle()
                            flags.show_selection_outlines = True
                            constants.last_selection_outline_switch = (
                                constants.current_time
                            )

                            for attached_cell in current_location.attached_cells:
                                if attached_cell.grid.is_mini_grid:
                                    attached_cell.grid.calibrate(
                                        current_location.x, current_location.y
                                    )
                            moved_mob.select()
                            if moved_mob.get_permission(constants.PMOB_PERMISSION):
                                moved_mob.selection_sound()
    elif flags.drawing_automatic_route:
        stopping = True
        flags.drawing_automatic_route = False
        if len(status.displayed_mob.base_automatic_route) > 1:
            destination_location = (
                status.displayed_mob.get_location()
                .get_world_handler()
                .find_location(
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
        status.minimap_grid.calibrate(status.displayed_mob.x, status.displayed_mob.y)
        actor_utility.calibrate_actor_info_display(
            status.location_info_display, status.displayed_mob.get_location()
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
        or flags.choosing_advertised_item
        or flags.drawing_automatic_route
    ):
        if not clicked_button and (
            not (
                flags.choosing_destination
                or flags.choosing_advertised_item
                or flags.drawing_automatic_route
            )
        ):  # Do not do selecting operations if user was trying to click a button # and action_possible()
            if constants.current_game_mode == constants.MINISTERS_MODE:
                minister_utility.calibrate_minister_info_display(None)
            click_move_minimap(select_unit=True)

        elif (
            not clicked_button
        ) and flags.choosing_destination:  # if clicking to move somewhere
            for current_grid in status.grid_list:  # destination_grids:
                if current_grid.can_show():
                    for current_cell in current_grid.get_flat_cell_list():
                        if current_cell.touching_mouse():
                            click_move_minimap(select_unit=False)
                            target_location = None
                            if (
                                current_cell.get_location()
                                .get_world_handler()
                                .is_abstract_world
                            ):
                                target_location = current_cell.get_location()
                            else:
                                target_location = (
                                    current_cell.get_location()
                                    .get_world_handler()
                                    .find_location(
                                        status.minimap_grid.center_x,
                                        status.minimap_grid.center_y,
                                    )
                                )
                            if (
                                current_grid.world_handler
                                != status.displayed_mob.get_location().get_world_handler()
                            ):
                                status.displayed_mob.end_turn_destination = (
                                    target_location
                                )
                                status.displayed_mob.set_permission(
                                    constants.TRAVELING_PERMISSION, True
                                )
                                status.displayed_mob.travel_sound()
                                flags.show_selection_outlines = True
                                constants.last_selection_outline_switch = (
                                    constants.current_time
                                )  # Outlines should be shown immediately once destination is chosen
                                status.displayed_mob.remove_from_turn_queue()
                                status.displayed_mob.select()
                                status.displayed_mob.get_location().select()
                            else:  # Cannot move to same world
                                actor_utility.calibrate_actor_info_display(
                                    status.mob_info_display, None
                                )
                                text_utility.print_to_screen(
                                    "You can only send ships to other theatres."
                                )
            flags.choosing_destination = False

        elif (not clicked_button) and flags.choosing_advertised_item:
            flags.choosing_advertised_item = False

        elif (not clicked_button) and flags.drawing_automatic_route:
            for current_grid in status.grid_list:  # destination_grids:
                for current_cell in current_grid.get_flat_cell_list():
                    if current_cell.touching_mouse():
                        if (
                            current_cell.get_location()
                            .get_world_handler()
                            .is_abstract_world
                        ):
                            text_utility.print_to_screen(
                                "Only locations adjacent to the most recently chosen destination can be added to the movement route."
                            )
                        else:
                            target_location = current_cell.get_location()
                            destination_x, destination_y = (
                                target_location.x,
                                target_location.y,
                            )
                            (
                                previous_destination_x,
                                previous_destination_y,
                            ) = status.displayed_mob.base_automatic_route[-1]
                            if (
                                utility.find_coordinate_distance(
                                    (destination_x, destination_y),
                                    (previous_destination_x, previous_destination_y),
                                )
                                == 1
                            ):
                                destination_infrastructure = (
                                    target_location.get_building(
                                        constants.INFRASTRUCTURE
                                    )
                                )
                                if not target_location.visible:
                                    text_utility.print_to_screen(
                                        "Movement routes cannot be created through unexplored locations."
                                    )
                                    return ()
                                elif (
                                    status.displayed_mob.get_permission(
                                        constants.VEHICLE_PERMISSION
                                    )
                                    and status.displayed_mob.get_permission(
                                        constants.TRAIN_PERMISSION
                                    )
                                    and not target_location.has_building(
                                        constants.RAILROAD
                                    )
                                ):
                                    text_utility.print_to_screen(
                                        "Trains can only create movement routes along railroads."
                                    )
                                    return ()
                                elif (
                                    target_location.terrain == "water"
                                    and not status.displayed_mob.get_permission(
                                        constants.SWIM_PERMISSION
                                    )
                                ) and (
                                    status.displayed_mob.get_permission(
                                        constants.VEHICLE_PERMISSION
                                    )
                                    and destination_infrastructure == None
                                ):
                                    # Non-train units can still move slowly through water, even w/o canoes or a bridge
                                    # Railroad bridge allows anything to move through
                                    text_utility.print_to_screen(
                                        "This unit cannot create movement routes through water."
                                    )
                                    return ()
                                elif (
                                    (not target_location.terrain == "water")
                                    and (
                                        not status.displayed_mob.get_permission(
                                            constants.WALK_PERMISSION
                                        )
                                    )
                                    and not target_location.has_intact_building(
                                        constants.SPACEPORT
                                    )
                                ):
                                    text_utility.print_to_screen(
                                        "This unit cannot create movement routes on land, except through ports."
                                    )
                                    return ()

                                status.displayed_mob.add_to_automatic_route(
                                    (destination_x, destination_y)
                                )
                                click_move_minimap()
                                flags.show_selection_outlines = True
                                constants.last_selection_outline_switch = (
                                    constants.current_time
                                )
                            else:
                                text_utility.print_to_screen(
                                    "Only locations adjacent to the most recently chosen destination can be added to the movement route."
                                )

        elif not clicked_button:
            click_move_minimap()


def click_move_minimap(select_unit: bool = True):
    """
    Description:
        When a cell on the strategic map grid is clicked, centers the minimap on that cell
    Input:
        None
    Output:
        None
    """
    if select_unit:
        actor_utility.calibrate_actor_info_display(
            status.location_info_display, None, override_exempt=True
        )
        actor_utility.calibrate_actor_info_display(
            status.mob_info_display, None, override_exempt=True
        )
    for (
        current_grid
    ) in status.grid_list:  # If grid clicked, move minimap to location clicked
        if current_grid.showing:
            for current_cell in current_grid.get_flat_cell_list():
                if current_cell.touching_mouse():
                    if select_unit and current_cell.get_location().subscribed_mobs:
                        current_cell.get_location().subscribed_mobs[0].select()
                    else:
                        actor_utility.calibrate_actor_info_display(
                            status.location_info_display, current_cell.get_location()
                        )

                    (absolute_x, absolute_y) = (
                        current_cell.get_location().x,
                        current_cell.get_location().y,
                    )
                    for attached_cell in current_cell.get_location().attached_cells:
                        attached_cell.grid.calibrate(absolute_x, absolute_y)
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
