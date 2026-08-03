# Contains functions used in the game's main loop and pygame input event management

from __future__ import annotations
import pygame
import time
from modules.util import (
    scaling,
    text_utility,
    actor_utility,
    traversal_utility,
    minister_utility,
    turn_management_utility,
    world_utility,
    drawing_utility,
)
from modules.interface_components import interface_elements
from modules.constants import constants, status, flags


def main_loop():
    """
    Description:
        Controls the main loop of the program, handling events such as mouse clicks and button presses, controlling timers, and drawing shapes and images. The program will end once this function stops
    Input:
        None
    Output:
        None
    """
    locked = False
    while not flags.crashed:
        if not flags.loading:
            update_display()
        else:
            draw_loading_screen()
        constants.InputManager.update_input()
        for event in pygame.event.get():
            flags.capital = flags.r_shift or flags.l_shift
            flags.ctrl = flags.r_ctrl or flags.l_ctrl
            match event.type:
                case pygame.QUIT:
                    flags.crashed = True
                case pygame.KEYDOWN:
                    if flags.typing or not locked:
                        button_keybind_clicked = False
                        for current_button in status.button_list:
                            if (
                                event.key == current_button.keybind_id
                                and (
                                    current_button.showing
                                    or (
                                        current_button.has_button_press_override
                                        and current_button.button_press_override()
                                    )
                                )
                                and not flags.typing
                                and not button_keybind_clicked
                            ):
                                if (
                                    current_button.has_released
                                ):  # if stuck on loading, don't want multiple 'key down' events to repeat on_click - shouldn't on_click again until released
                                    current_button.has_released = False
                                    current_button.being_pressed = True
                                    current_button.on_click()
                                    button_keybind_clicked = True  # Prevent any other buttons from being activated by this button press
                                    current_button.showing_outline = True
                                break
                            else:
                                current_button.confirming = False
                                current_button.being_pressed = False
                        match event.key:
                            case pygame.K_RSHIFT:
                                flags.r_shift = True
                            case pygame.K_LSHIFT:
                                flags.l_shift = True
                            case pygame.K_RCTRL:
                                flags.r_ctrl = True
                            case pygame.K_LCTRL:
                                flags.l_ctrl = True
                            case pygame.K_SPACE:
                                if flags.typing:
                                    constants.message += " "
                            case pygame.K_BACKSPACE:
                                if flags.typing:
                                    constants.message = constants.message[
                                        :-1
                                    ]  # remove last character from message and set message to it
                            case pygame.K_p if constants.EffectManager.effect_active(
                                "debug_print"
                            ):
                                debug_print()
                        if flags.typing and event.key in constants.key_codes:
                            if flags.capital:
                                constants.message += constants.uppercase_key_values[
                                    constants.key_codes.index(event.key)
                                ]
                            else:
                                constants.message += constants.lowercase_key_values[
                                    constants.key_codes.index(event.key)
                                ]
                        if constants.fonts[constants.DEFAULT_FONT].calculate_size(
                            f"Response: {constants.message}"
                        ) > scaling.scale_width(constants.DEFAULT_TEXT_BOX_WIDTH):
                            constants.message = constants.message[:-1]
                            text_utility.print_to_screen(
                                f"Maximum input length reached."
                            )
                    locked = True

                case pygame.KEYUP:
                    locked = False
                    for current_button in status.button_list:
                        if (
                            not flags.typing
                            or current_button.keybind_id == pygame.K_TAB
                            or current_button.keybind_id == pygame.K_e
                        ):
                            if current_button.has_keybind:
                                if event.key == current_button.keybind_id:
                                    current_button.on_release()
                    match event.key:
                        case pygame.K_RSHIFT:
                            flags.r_shift = False
                        case pygame.K_LSHIFT:
                            flags.l_shift = False
                        case pygame.K_LCTRL:
                            flags.l_ctrl = False
                        case pygame.K_RCTRL:
                            flags.r_ctrl = False
                        case pygame.K_RETURN:
                            if flags.typing:
                                if constants.InputManager.taking_input:
                                    if constants.message:
                                        constants.InputManager.receive_input(
                                            constants.message
                                        )
                                        text_utility.print_to_screen(constants.message)
                                        constants.message = ""
                                        flags.typing = False
                                else:
                                    text_utility.print_to_screen(constants.message)
                                    constants.message = ""
                                    flags.typing = False

                case constants.music_endevent:
                    constants.SoundManager.song_done()

        flags.old_lmb_down, flags.old_rmb_down, flags.old_mmb_down = (
            flags.lmb_down,
            flags.rmb_down,
            flags.mmb_down,
        )
        flags.lmb_down, flags.mmb_down, flags.rmb_down = pygame.mouse.get_pressed()

        if (
            flags.old_rmb_down == True and flags.rmb_down == False
        ):  # if rmb just released
            manage_mouse_down(lmb=False)

        if (
            flags.old_lmb_down == True and flags.lmb_down == False
        ):  # if lmb just released
            manage_mouse_down(lmb=True)

        if flags.lmb_down or flags.rmb_down:
            for current_button in status.button_list:
                if current_button.touching_mouse() and current_button.showing:
                    current_button.showing_outline = True
                elif not current_button.being_pressed:
                    current_button.showing_outline = False
        else:
            for current_button in status.button_list:
                if current_button.has_released:
                    current_button.showing_outline = False

        constants.current_time = time.time()
        if constants.current_time - constants.last_selection_outline_switch > 1:
            flags.show_selection_outlines = not flags.show_selection_outlines
            constants.last_selection_outline_switch = constants.current_time
        constants.JobScheduler.update(constants.current_time)
        if (
            not flags.player_turn
            and constants.previous_turn_time + constants.end_turn_wait_time
            <= constants.current_time
        ):  # If enough time has passed based on delay from previous movement
            if constants.TIME_PASSING_ITERATIONS < len(
                constants.TIME_PASSING_PLANET_SCHEDULE
            ):
                increment_globe_projection_rotation()
            else:  # End time passing logic
                complete_globe_projection_rotation()
                update_display()
                flags.enemy_combat_phase = True
                turn_management_utility.manage_combat()

            if constants.EffectManager.effect_active("fast_turn"):
                constants.end_turn_wait_time = 0
            constants.previous_turn_time = constants.current_time
    pygame.quit()


def manage_mouse_down(lmb: bool) -> None:
    """
    Description:
        If the player is choosing a movement destination and the player clicks on a cell, chooses that cell as the movement destination. If the player is choosing a movement destination but did not click a cell, cancels the movement
            destination selection process. Otherwise, if the player clicks on a cell, selects the top mob in that cell if any are present and moves the minimap to that cell. If the player clicks on a button, calls the on_click function
            of that button. If nothing was clicked, deselects the selected mob if any is selected
    Input:
        bool lmb: True if this mouse down event was a left mouse button down, otherwise False for right mouse button down
    Output:
        None
    """
    clicked_button = False
    for draw_priority in reversed(sorted(status.draw_list_prioritized.keys())):
        for current_interface_element in status.draw_list_prioritized[draw_priority]:
            if (
                hasattr(current_interface_element, "on_click")
                and current_interface_element.touching_mouse()
            ):
                click_result = None
                clicked_button = True
                if lmb:
                    click_result = current_interface_element.on_click()
                    current_interface_element.on_release()
                else:
                    click_result = current_interface_element.on_rmb_click()
                    current_interface_element.on_rmb_release()
                if click_result != True:
                    # When on_click returns True, it indicates that it should still allow other buttons to be clicked
                    #   This is utilized by safe click panel to prevent deselecting units while allowing other buttons to be clicked
                    return

    if (
        action_possible() or constants.SelectorManager.any_active()
    ):  # Only executes if no buttons were clicked
        if constants.SelectorManager.none_active():
            # Do not do selecting operations if user was trying to click a button # and action_possible()
            if constants.current_game_mode == constants.MINISTERS_MODE:
                minister_utility.calibrate_minister_info_display(None)
            else:
                current_cell = actor_utility.get_clicked_cell()
                if (
                    current_cell
                    and current_cell.source.actor_type == constants.LOCATION_ACTOR_TYPE
                ):
                    if lmb or len(current_cell.source.subscribed_mobs) < 2:
                        actor_utility.click_move_minimap(current_cell, select_unit=True)
                    else:  # Rmb on at least 2 units
                        actor_utility.cycle_units(current_cell)
                elif (
                    current_cell
                    and current_cell.source.actor_type == constants.ZONE_ACTOR_TYPE
                ):
                    actor_utility.click_move_minimap(current_cell, select_unit=True)
                elif not clicked_button:
                    actor_utility.click_move_minimap(None)
        else:
            constants.SelectorManager.on_click(lmb)


def complete_globe_projection_rotation():
    """
    Completes the world and Earth globe projection rotations, setting them to their static version for the new player turn
    """
    equatorial_coordinates = constants.TIME_PASSING_EQUATORIAL_COORDINATES
    constants.TIME_PASSING_ROTATION = 0
    status.current_world.update_globe_projection(
        center_coordinates=equatorial_coordinates[
            (
                constants.TIME_PASSING_ROTATION
                + constants.TIME_PASSING_INITIAL_ORIENTATION
            )
            % status.current_world.world_dimensions
        ]
    )

    status.earth_world.set_image(
        world_utility.generate_abstract_world_image(planet=constants.EARTH_WORLD)
    )
    if constants.EffectManager.effect_active("rotate_game_mode_buttons"):
        status.to_earth_button.image.set_image(
            actor_utility.generate_frame(
                world_utility.generate_abstract_world_image(
                    planet=constants.EARTH_WORLD, size=0.6
                ),
            )
        )


def increment_globe_projection_rotation():
    """
    Increment the globe projection rotation, rotating the world and Earth globe projections based on their rotation speeds.
    """
    equatorial_coordinates = constants.TIME_PASSING_EQUATORIAL_COORDINATES
    if constants.TIME_PASSING_PLANET_SCHEDULE[
        constants.TIME_PASSING_ITERATIONS
    ]:  # If scheduled to rotate planet at this iteration
        current_coordinates = equatorial_coordinates[
            (
                constants.TIME_PASSING_ROTATION
                + constants.TIME_PASSING_INITIAL_ORIENTATION
            )
            % status.current_world.world_dimensions
        ]
        status.current_world.update_globe_projection(
            center_coordinates=current_coordinates,
            update_button=constants.EffectManager.effect_active(
                "rotate_game_mode_buttons"
            ),
        )
        if constants.EffectManager.effect_active("save_global_projection"):
            pygame.image.save(
                status.globe_projection_surface.convert_alpha(),
                f"save_games/globe_rotations/{constants.TIME_PASSING_EARTH_ROTATIONS}.png",
            )
        if status.current_world.rotation_speed > 2:
            frame_interval = 3
        else:
            frame_interval = 2
        constants.TIME_PASSING_ROTATION += (
            frame_interval * status.current_world.rotation_direction
        )

    if constants.TIME_PASSING_EARTH_SCHEDULE[
        constants.TIME_PASSING_ITERATIONS
    ]:  # If scheduled to rotate Earth at this iteration
        status.earth_world.set_image(
            world_utility.generate_abstract_world_image(
                planet=constants.EARTH_WORLD,
                rotation=constants.TIME_PASSING_EARTH_ROTATIONS,
            )
        )
        if constants.EffectManager.effect_active("rotate_game_mode_buttons"):
            status.to_earth_button.image.set_image(
                actor_utility.generate_frame(
                    world_utility.generate_abstract_world_image(
                        planet=constants.EARTH_WORLD,
                        size=0.6,
                        rotation=constants.TIME_PASSING_EARTH_ROTATIONS,
                    ),
                )
            )
        constants.TIME_PASSING_EARTH_ROTATIONS += 1
    constants.TIME_PASSING_ITERATIONS += 1


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

        draw_text_box()

        constants.mouse_follower.draw()

        if status.current_instructions_page:
            status.current_instructions_page.draw()

        tooltip_drawer = None
        if (
            time.time() > constants.mouse_moved_time + 0.15
        ):  # Wait until mouse is still before drawing tooltips
            tooltip_drawer = detect_tooltip_drawer()

        if tooltip_drawer:
            manage_tooltip_drawing(tooltip_drawer)

        if (constants.old_mouse_x, constants.old_mouse_y) != pygame.mouse.get_pos():
            constants.mouse_moved_time = constants.current_time
            constants.old_mouse_x, constants.old_mouse_y = pygame.mouse.get_pos()

    pygame.display.update()

    if constants.EffectManager.effect_active("track_fps"):
        current_time = time.time()
        constants.frames_this_second += 1
        if current_time > constants.last_fps_update + 1 and flags.startup_complete:
            constants.FpsTracker.set(constants.frames_this_second)
            constants.frames_this_second = 0
            constants.last_fps_update = current_time

    if constants.EffectManager.effect_active("track_cached_image_memory"):
        current_time = time.time()
        if (
            current_time > constants.last_image_cache_check + 1
            and flags.startup_complete
        ):
            constants.ImageCacheTracker.set(
                round(drawing_utility.cached_surfaces_memory(), 2)
            )
            constants.last_image_cache_check = current_time

    if (
        constants.EffectManager.effect_active("track_mouse_position")
        and flags.startup_complete
    ):
        constants.mouse_position_tracker.set(pygame.mouse.get_pos())


def detect_tooltip_drawer() -> interface_elements.interface_element:
    """
    Description:
        Detects and returns the highest priority object (if any) that can show a tooltip based on mouse position
    Input:
        None
    Output:
        interface_element: Returns the highest priority object that can show a tooltip, otherwise returns None
    """
    for draw_priority in reversed(sorted(status.draw_list_prioritized.keys())):
        for current_interface_element in status.draw_list_prioritized[draw_priority]:
            if current_interface_element.can_show_tooltip():
                return current_interface_element
    return None


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
        or constants.SelectorManager.any_active()
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
        actor_utility.autogui_pipe_send("loaded")
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
                        constants.SoundManager.song_done()
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
    font = constants.fonts[constants.DEFAULT_FONT]
    y_displacement = scaling.scale_width(30)  # estimated mouse size

    mouse_x, mouse_y = pygame.mouse.get_pos()
    height = y_displacement
    width = 0
    formatted_tooltip_list = []
    for tooltip in tooltip_drawer.batch_tooltip_list:
        tooltip_width = 0
        for line in tooltip:
            tooltip_width = max(
                tooltip_width,
                font.calculate_size(line) + scaling.scale_width(10),
            )
        tooltip_height = (len(tooltip) * font.size) + scaling.scale_height(5)
        box = pygame.Rect(mouse_x, mouse_y, tooltip_width, tooltip_height)
        height += font.size * (len(tooltip) + 1)
        width = max(width, tooltip_width)
        outline = pygame.Rect(
            mouse_x - scaling.scale_width(1),
            mouse_y + scaling.scale_width(1),
            tooltip_width + (2 * scaling.scale_width(1)),
            tooltip_height + (scaling.scale_width(1) * 2),
        )
        tooltip_outline_width = scaling.scale_width(1)
        formatted_tooltip_list.append(
            {
                "text": tooltip,
                "box": box,
                "outline": outline,
                "outline_width": tooltip_outline_width,
            }
        )

    below_screen = False  # if goes below bottom side
    beyond_screen = False  # if goes beyond right side
    if (constants.display_height + 10 - mouse_y) - height < 0:
        below_screen = True
    if mouse_x + width > constants.display_width:
        beyond_screen = True

    for formatted_tooltip in reversed(formatted_tooltip_list):
        draw_tooltip(
            formatted_tooltip,
            below_screen,
            beyond_screen,
            height,
            width,
            y_displacement,
        )
        y_displacement += font.size * (len(formatted_tooltip["text"]) + 1)


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
                tooltip["box"].y
                + (text_line_index * constants.fonts[constants.DEFAULT_FONT].size),
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

    if flags.expand_text_box:
        constants.text_box_height = scaling.scale_height(
            constants.default_display_height - 60
        )
    else:
        constants.text_box_height = constants.default_text_box_height

    font = constants.fonts[constants.DEFAULT_FONT]
    max_screen_lines = (constants.default_display_height // font.size) - 1
    max_text_box_lines = (constants.text_box_height // font.size) - 1
    max_text_width = scaling.scale_width(constants.DEFAULT_TEXT_BOX_WIDTH)
    text_box_width = max_text_width + scaling.scale_width(10)
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
    if constants.InputManager.taking_input:
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
