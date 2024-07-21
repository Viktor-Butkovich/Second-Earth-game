# Runs setup and main loop on program start

import modules.main_loop as main_loop
from modules.setup import *

try:
    setup(
        misc,
        worker_types_config,
        equipment_types_config,
        terrain_feature_types_config,
        commodities,
        def_ministers,
        new_game_setup_screen,
        info_displays,
        transactions,
        actions,
        value_trackers,
        buttons,
        earth_screen,
        ministers_screen,
        trial_screen,
        mob_interface,
        tile_interface,
        unit_organization_interface,
        settlement_interface,
        inventory_interface,
        minister_interface,
    )
    main_loop.main_loop()

except Exception:  # displays error message and records error message in crash log file
    manage_crash(Exception)

# tasks:
#   general (game-agnostic):
# replace usages of 'none' with None
# Add type hints on sight - gradual process
# add minister speech bubbles
# Add random events
# Add debug settings menu within game, rather than needing to edit .json out of game
# Add autosave and multiple save slots
# Add ambient sounds
# Continue adding new songs
#
# Possible issues:
# Look into special character glitch for Queiros Portuguese name, possibly font issue not having correct special character in the settlement font (but does in minister screen font)
#
#   new SE features:
# Continue adding hairstyles
# Minister table projection not using smart green screens, probably because it directly uses tile image ID
# Add new unit art
# Add new minister positions with placehold color-coded squares
# Add new minister appointing system - selecting an unappointed minister should highlight all available positions, and clicking on one appoint w/ a confirmation check
# Add more variety to water/ice colors
# Eventually add hydrogen fuel cells - process to convert hydrogen and oxygen into water, actually releases energy but requires facility and hydrogen/oxygen input
