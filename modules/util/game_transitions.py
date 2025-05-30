# Contains functions used when switching between parts of the game, like loading screen display

from modules.util import (
    main_loop_utility,
    text_utility,
    actor_utility,
    minister_utility,
    scaling,
)
from modules.constants import constants, status, flags


def cycle_player_turn(start_of_turn=False):
    """
    Description:
        Selects the next unit in the turn order, or gives a message if none remain
    Input:
        boolean start_of_turn = False: Whether this is occuring automatically at the start of the turn or due to a player action during the turn
    Output:
        None
    """
    turn_queue = status.player_turn_queue
    if len(turn_queue) == 0:
        if (
            not start_of_turn
        ):  # print no units message if there are no units in turn queue
            text_utility.print_to_screen("There are no units left to move this turn.")
            actor_utility.calibrate_actor_info_display(
                status.mob_info_display, None, override_exempt=True
            )
    else:
        if (
            len(turn_queue) == 1
            and (not start_of_turn)
            and turn_queue[0] == status.displayed_mob
        ):  # only print no other units message if there is only 1 unit in turn queue and it is already selected
            text_utility.print_to_screen(
                "There are no other units left to move this turn."
            )
        if turn_queue[0] != status.displayed_mob:
            turn_queue[0].selection_sound()
        else:
            turn_queue.append(
                turn_queue.pop(0)
            )  # if unit is already selected, move it to the end and shift to the next one
        cycled_mob = turn_queue[0]
        if (
            constants.current_game_mode == constants.EARTH_MODE
            and not status.earth_grid in cycled_mob.grids
        ):
            set_game_mode(constants.STRATEGIC_MODE)
        elif constants.current_game_mode == constants.MINISTERS_MODE:
            set_game_mode(constants.STRATEGIC_MODE)
        actor_utility.calibrate_actor_info_display(
            status.mob_info_display, None, override_exempt=True
        )
        cycled_mob.select()
        if not start_of_turn:
            turn_queue.append(turn_queue.pop(0))


def set_game_mode(new_game_mode):
    """
    Description:
        Changes the current game mode to the inputted game mode, changing which objects can be displayed and interacted with
    Input:
        string new_game_mode: Game mode that this switches to, like 'strategic'
    Output:
        None
    """
    previous_game_mode = constants.current_game_mode
    if new_game_mode == previous_game_mode:
        return ()
    else:
        if previous_game_mode in [
            constants.MAIN_MENU_MODE,
            constants.NEW_GAME_SETUP_MODE,
        ] and not new_game_mode in [
            constants.MAIN_MENU_MODE,
            constants.NEW_GAME_SETUP_MODE,
        ]:
            constants.event_manager.clear()
            constants.sound_manager.play_random_music("earth")
        elif (
            not previous_game_mode
            in [constants.MAIN_MENU_MODE, constants.NEW_GAME_SETUP_MODE]
        ) and new_game_mode in [
            constants.MAIN_MENU_MODE,
            constants.NEW_GAME_SETUP_MODE,
        ]:  # game starts in None mode so this would work on startup
            constants.event_manager.clear()
            constants.sound_manager.play_random_music("main menu")

        if (
            new_game_mode == constants.MAIN_MENU_MODE
            or previous_game_mode == constants.NEW_GAME_SETUP_MODE
        ):
            start_loading(
                previous_game_mode=previous_game_mode, new_game_mode=new_game_mode
            )
        constants.current_game_mode = new_game_mode
        if new_game_mode == constants.STRATEGIC_MODE:
            constants.default_text_box_height = constants.font_size * 5.5
            constants.text_box_height = constants.default_text_box_height
        elif new_game_mode == constants.MAIN_MENU_MODE:
            constants.default_text_box_height = constants.font_size * 5.5
            constants.text_box_height = constants.default_text_box_height
            status.text_list = []  # Clear text box when going to main menu
            for effect in [
                "mars_preset",
                "earth_preset",
                "venus_preset",
            ]:  # Clear new game configurations when going to main menu
                constants.effect_manager.set_effect(effect, False)
        elif not new_game_mode in [constants.TRIAL_MODE, constants.NEW_GAME_SETUP_MODE]:
            constants.default_text_box_height = constants.font_size * 5.5
            constants.text_box_height = constants.default_text_box_height

    if previous_game_mode in [
        constants.STRATEGIC_MODE,
        constants.NEW_GAME_SETUP_MODE,
        constants.EARTH_MODE,
        constants.MINISTERS_MODE,
    ]:
        if new_game_mode == constants.MINISTERS_MODE or not (
            status.displayed_location
            and status.displayed_location.get_world_handler().is_earth
        ):
            actor_utility.calibrate_actor_info_display(
                status.mob_info_display, None, override_exempt=True
            )  # Deselect actors/ministers and remove any actor info from display when switching screens
            actor_utility.calibrate_actor_info_display(
                status.location_info_display, None, override_exempt=True
            )
            minister_utility.calibrate_minister_info_display(None)
            if new_game_mode == constants.EARTH_MODE:
                actor_utility.calibrate_actor_info_display(
                    status.location_info_display, status.earth_world.find_location(0, 0)
                )  # Calibrate location info to Earth
            elif new_game_mode == constants.STRATEGIC_MODE:
                if status.current_world:
                    actor_utility.calibrate_actor_info_display(
                        status.location_info_display,
                        status.current_world.find_location(
                            status.minimap_grid.center_x,
                            status.minimap_grid.center_y,
                        ),
                    )  # Calibrate location info to minimap center
    if new_game_mode == constants.MINISTERS_MODE:
        constants.available_minister_left_index = -2
        minister_utility.update_available_minister_display()
        minister_utility.calibrate_minister_info_display(None)

    elif previous_game_mode == constants.TRIAL_MODE:
        minister_utility.calibrate_trial_info_display(status.defense_info_display, None)
        minister_utility.calibrate_trial_info_display(
            status.prosecution_info_display, None
        )

    if flags.startup_complete and not new_game_mode in [
        constants.MAIN_MENU_MODE,
        constants.NEW_GAME_SETUP_MODE,
    ]:
        constants.notification_manager.update_notification_layout()


def start_loading(previous_game_mode: str = None, new_game_mode: str = None):
    """
    Description:
        Records when loading started and displays a loading screen when the program is launching or switching between game modes
    Input:
        string previous_game_mode = None: Game mode that loading is transitioning from
        string new_game_mode = None: Game mode that loading is transitioning to
    Output:
        None
    """
    if new_game_mode in [
        constants.STRATEGIC_MODE,
        constants.EARTH_MODE,
        constants.MINISTERS_MODE,
    ]:  # If loading into game
        status.loading_screen_quote_banner.set_label(
            constants.flavor_text_manager.generate_flavor_text("loading_screen_quotes")
        )
    else:
        status.loading_screen_quote_banner.set_label("")
    flags.loading = True
    constants.loading_loops = 0
    main_loop_utility.update_display()


def to_main_menu(override=False):
    """
    Description:
        Exits the game to the main menu without saving
    Input:
        boolean override = False: If True, forces game to exit to main menu regardless of current game circumstances
    Output:
        None
    """
    actor_utility.calibrate_actor_info_display(
        status.mob_info_display, None, override_exempt=True
    )
    actor_utility.calibrate_actor_info_display(status.location_info_display, None)
    minister_utility.calibrate_minister_info_display(None)
    for current_actor in status.actor_list:
        current_actor.remove_complete()
    for current_grid in status.grid_list:
        current_grid.remove_complete()
    for current_minister in status.minister_list:
        current_minister.remove_complete()
    for current_die in status.dice_list:
        current_die.remove_complete()
    status.loan_list = []
    status.displayed_mob = None
    status.displayed_location = None
    constants.message = ""
    status.player_turn_queue = []
    if status.current_instructions_page:
        status.current_instructions_page.remove_complete()
        status.current_instructions_page = None
    for key, terrain_feature_type in status.terrain_feature_types.items():
        terrain_feature_type.clear_tracking()
    set_game_mode(constants.MAIN_MENU_MODE)


def force_minister_appointment():
    """
    Description:
        Navigates to the ministers mode and instructs player to fill all minister positions when an action has been prevented due to not having all positions
            filled
    Input:
        None
    Output:
        None
    """
    set_game_mode(constants.MINISTERS_MODE)
    constants.notification_manager.display_notification(
        {
            "message": "You cannot do that until all minister positions have been appointed. /n /n",
            "notification_type": constants.NOTIFICATION,
        }
    )


def create_grids() -> None:
    """
    Description:
        Creates grids (current world minimaps, Earth abstract grid, etc.) upon loading or creating a new game
    Input:
        None
    Output:
        None
    """
    status.scrolling_strategic_map_grid = (
        constants.actor_creation_manager.create_interface_element(
            input_dict={
                "init_type": constants.MINI_GRID,
                "world_handler": status.current_world,
                "coordinates": scaling.scale_coordinates(
                    constants.strategic_map_x_offset,
                    constants.strategic_map_y_offset,
                ),
                "width": scaling.scale_width(constants.strategic_map_pixel_width),
                "height": scaling.scale_height(constants.strategic_map_pixel_height),
                "modes": [constants.STRATEGIC_MODE],
                "coordinate_size": status.current_world.world_dimensions,
                "grid_line_width": 2,
                "parent_collection": status.grids_collection,
            }
        )
    )

    status.minimap_grid = constants.strategic_map_grid = (
        constants.actor_creation_manager.create_interface_element(
            input_dict={
                "init_type": constants.MINI_GRID,
                "world_handler": status.current_world,
                "coordinates": scaling.scale_coordinates(
                    constants.minimap_grid_x_offset,
                    -1 * (constants.minimap_grid_pixel_height + 25)
                    + constants.minimap_grid_y_offset,
                ),
                "width": scaling.scale_width(constants.minimap_grid_pixel_width),
                "height": scaling.scale_height(constants.minimap_grid_pixel_height),
                "modes": [constants.STRATEGIC_MODE],
                "coordinate_size": constants.minimap_grid_coordinate_size,
                "external_line_color": constants.COLOR_BRIGHT_RED,
                "parent_collection": status.grids_collection,
            }
        )
    )

    globe_projection_grid = constants.actor_creation_manager.create_interface_element(
        input_dict={
            "init_type": constants.ABSTRACT_GRID,
            "world_handler": status.current_world.orbital_world,
            "coordinates": scaling.scale_coordinates(
                constants.globe_projection_grid_x_offset,
                constants.globe_projection_grid_y_offset,
            ),
            "width": scaling.scale_width(constants.globe_projection_grid_width),
            "height": scaling.scale_height(constants.globe_projection_grid_height),
            "modes": [constants.STRATEGIC_MODE],
            "parent_collection": status.grids_collection,
        }
    )

    status.earth_grid = constants.actor_creation_manager.create_interface_element(
        input_dict={
            "init_type": constants.ABSTRACT_GRID,
            "world_handler": status.earth_world,
            "coordinates": scaling.scale_coordinates(
                constants.earth_grid_x_offset,
                constants.earth_grid_y_offset,
            ),
            "width": scaling.scale_width(constants.earth_grid_width),
            "height": scaling.scale_height(constants.earth_grid_height),
            "modes": [constants.STRATEGIC_MODE, constants.EARTH_MODE],
            "parent_collection": status.grids_collection,
        }
    )

    status.minimap_grid.calibrate(
        round(0.75 * status.current_world.world_dimensions),
        round(0.75 * status.current_world.world_dimensions),
    )
