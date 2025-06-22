# Contains game's main loop

import time
import pygame
from modules.util import (
    main_loop_utility,
    text_utility,
    turn_management_utility,
    actor_utility,
    world_utility,
)
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
            main_loop_utility.update_display()
        else:
            main_loop_utility.draw_loading_screen()
        constants.input_manager.update_input()
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
                            case pygame.K_p if constants.effect_manager.effect_active(
                                "debug_print"
                            ):
                                main_loop_utility.debug_print()
                        if flags.typing and event.key in constants.key_codes:
                            if flags.capital:
                                constants.message += constants.uppercase_key_values[
                                    constants.key_codes.index(event.key)
                                ]
                            else:
                                constants.message += constants.lowercase_key_values[
                                    constants.key_codes.index(event.key)
                                ]
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
                                if constants.input_manager.taking_input:
                                    if constants.message:
                                        constants.input_manager.receive_input(
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
                    constants.sound_manager.song_done()

        flags.old_lmb_down, flags.old_rmb_down, flags.old_mmb_down = (
            flags.lmb_down,
            flags.rmb_down,
            flags.mmb_down,
        )
        flags.lmb_down, flags.mmb_down, flags.rmb_down = pygame.mouse.get_pressed()

        if flags.old_rmb_down != flags.rmb_down:  # if rmb changes
            if not flags.rmb_down:  # if user just released rmb
                clicked_button = False
                stopping = False
                if status.current_instructions_page == None:
                    for current_button in status.button_list:  # here
                        if (
                            current_button.touching_mouse()
                            and current_button.showing
                            and (current_button.in_notification)
                            and not stopping
                        ):  # if notification, click before other buttons
                            current_button.on_rmb_click()
                            current_button.on_rmb_release()
                            clicked_button = True
                            stopping = True
                            break
                else:
                    if (
                        status.current_instructions_page.touching_mouse()
                        and status.current_instructions_page.showing
                    ):
                        status.current_instructions_page.on_rmb_click()
                        clicked_button = True
                        stopping = True
                if not stopping:
                    for current_button in status.button_list:
                        if current_button.touching_mouse() and current_button.showing:
                            current_button.on_rmb_click()
                            current_button.on_rmb_release()
                            clicked_button = True
                main_loop_utility.manage_rmb_down(clicked_button)

        if flags.old_lmb_down != flags.lmb_down:  # if lmb changes
            if not flags.lmb_down:  # If user just released lmb
                clicked_button = False  # If any button, including a panel, is clicked, do not deselect units
                allow_on_click = True  # Certain buttons, like panels, allow clicking on another button at the same time
                stopping = False
                if status.current_instructions_page == None:
                    for current_button in status.button_list:
                        if (
                            current_button.touching_mouse()
                            and current_button.showing
                            and (current_button.in_notification)
                            and not stopping
                        ):  # If notification, click before other buttons
                            current_button.on_click()
                            current_button.on_release()
                            clicked_button = True
                            allow_on_click = False
                            stopping = True
                            break
                else:
                    if (
                        status.current_instructions_page.touching_mouse()
                        and status.current_instructions_page.showing
                    ):  # if instructions, click before other buttons
                        status.current_instructions_page.on_click()
                        clicked_button = True
                        allow_on_click = False
                        stopping = True
                        break

                if not stopping:
                    for current_button in reversed(status.button_list):
                        if (
                            current_button.touching_mouse()
                            and current_button.showing
                            and allow_on_click
                        ):  # Only click 1 button at a time
                            if (
                                current_button.on_click()
                            ):  # If on_click has return value, nothing happened - allow other buttons to click but do not deselect units
                                allow_on_click = True
                            else:
                                allow_on_click = False
                            current_button.on_release()
                            clicked_button = True
                main_loop_utility.manage_lmb_down(
                    clicked_button
                )  # Whether button was clicked or not determines whether characters are deselected

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
        constants.event_manager.update(constants.current_time)
        if (
            not flags.player_turn
            and constants.previous_turn_time + constants.end_turn_wait_time
            <= constants.current_time
        ):  # If enough time has passed based on delay from previous movement
            equatorial_coordinates = constants.TIME_PASSING_EQUATORIAL_COORDINATES
            if constants.TIME_PASSING_ITERATIONS < len(
                constants.TIME_PASSING_PLANET_SCHEDULE
            ):
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
                        update_button=constants.effect_manager.effect_active(
                            "rotate_game_mode_buttons"
                        ),
                    )
                    if constants.effect_manager.effect_active("save_global_projection"):
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
                    if constants.effect_manager.effect_active(
                        "rotate_game_mode_buttons"
                    ):
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
            else:  # End time passing logic
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
                    world_utility.generate_abstract_world_image(
                        planet=constants.EARTH_WORLD
                    )
                )
                if constants.effect_manager.effect_active("rotate_game_mode_buttons"):
                    status.to_earth_button.image.set_image(
                        actor_utility.generate_frame(
                            world_utility.generate_abstract_world_image(
                                planet=constants.EARTH_WORLD, size=0.6
                            ),
                        )
                    )
                main_loop_utility.update_display()
                flags.enemy_combat_phase = True
                turn_management_utility.manage_combat()

            if constants.effect_manager.effect_active("fast_turn"):
                constants.end_turn_wait_time = 0
            constants.previous_turn_time = constants.current_time
    pygame.quit()
