# Runs setup and main loop on program start

from __future__ import annotations
import logging
import pygame
from modules.constants import constants, status, flags
from modules.config.constructs import (
    config_building_types,
    config_item_types,
    config_minister_types,
    config_terrain_feature_types,
    config_unit_types,
    config_actions,
)
from modules.config.info_displays import (
    location_info_display,
    minister_info_display,
    mob_info_display,
)
from modules.config.screens import earth_screen, ministers_screen, trial_screen
from modules.config.tabs import (
    global_conditions_tab,
    inventory_tabs,
    local_conditions_tab,
    settlement_tab,
    temperature_breakdown_tab,
    unit_organization_tab,
)
from modules.config.info_displays import (
    zone_info_display,
)
from modules.config import config_misc, config_buttons, config_value_trackers
from modules.util import main_loop_utility


def setup() -> None:
    """
    Description:
        Runs the inputted setup functions in order
    Input:
        function list args: List of setup functions to run
    Output:
        None
    """
    flags.startup_complete = False
    config_misc.config_misc()
    if not flags.loading:
        main_loop_utility.update_display()
    else:
        main_loop_utility.draw_loading_screen()
    config_misc.config_info_displays()
    config_item_types.config_item_types()
    config_terrain_feature_types.config_terrain_feature_types()
    config_minister_types.config_minister_types()
    config_building_types.config_building_types()
    config_unit_types.config_unit_types()
    config_actions.config_actions()
    config_value_trackers.config_value_trackers()
    config_buttons.config_buttons()
    earth_screen.config_earth_screen()
    ministers_screen.config_ministers_screen()
    trial_screen.config_trial_screen()
    location_info_display.config_location_info_display()
    zone_info_display.config_zone_info_display()
    mob_info_display.config_mob_info_display()
    unit_organization_tab.config_unit_organization_tab()
    local_conditions_tab.config_local_conditions_tab()
    global_conditions_tab.config_global_conditions_tab()
    temperature_breakdown_tab.config_temperature_breakdown_tab()
    settlement_tab.config_settlement_tab()
    inventory_tabs.config_inventory_tabs()
    minister_info_display.config_minister_info_display()
    flags.startup_complete = True
    flags.creating_new_game = False


def manage_crash(exception: Exception) -> None:
    """
    Description:
        Uses an exception to write a crash log and exit the game
    Input:
        Exception exception: Exception that caused the crash
    Output:
        None
    """
    crash_log_file = open("notes/Crash Log.txt", "w")
    crash_log_file.write("")  # clears crash report file
    console = (
        logging.StreamHandler()
    )  # sets logger to go to both console and crash log file
    logging.basicConfig(filename="notes/Crash Log.txt")
    logging.getLogger("").addHandler(console)

    logging.error(
        exception, exc_info=True
    )  # sends error message to console and crash log file

    crash_log_file.close()
    pygame.quit()
