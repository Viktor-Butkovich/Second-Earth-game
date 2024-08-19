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
# Include "advancement level" of building materials - 1 ~ stone/wood, etc. for basic shelters in atmosphere, 2 ~ for industrial steel/concrete for factories,
#   basic planetary construction, 3 ~ for titanium, carbon fiber, advanced modern-day materials, spaceships, etc., 4+ for more advanced
# Also document a list of officers for each minister position
# Minister types:
#   Exploration -> Science (research, exploration, surveying)
#   Trade -> Terran Affairs (foreign/diplomacy/marketing)
#   Religion -> Health and Environment (settler health, ecology, terraforming)
#   Military -> Space (space transportation, space colonies, space construction, space special projects)
#   Prosecutor -> Auditor (finding corruption, security)
#   Transportation -> Transportation (planetary transportation, logistics)
#   Production -> Industry (construction, factories, mining, agriculture)
#   Construction -> Energy (power plants, energy infrastructure)

# Upcoming work queue:
# Incorporate A Strange New World, Flying in my Spaceship, Going Underground, Out of Time, Space Song 3
# Add a unit permissions system - any unit type has a dictionary of True/False permissions for each possible action, using defaults if none specified
#   Use similar system to terrain knowledge privileges, using set of constants to identify each permission type
#   Something like canoes or suits would modify a unit's default permissions
#   Next add permissions for temporary states, sentry mode, etc.
#   Add permissions for ministers as well as mobs
#   Replace worker_type logic with permissions handling
# Add new minister positions
# Add astronauts/cosmonauts group with corresponding officer
# Add support for vehicles being crewed by groups, combining in new interface with any group attaching/detaching, like to mines/factories
#   This allows embarking/disembarking to be part of the reorganization interface
# Add spaceships
# Allow large items to be stored in inventory, with supporting interface
# Add radio distortion versions of voice lines, either as separate files or runtime filter
# Add terrain details tile interface panel, such that terrain details aren't always showing
# For tiles with knowledge 1, possibly change every turn to a cloud or normal pixellated version, depending on atmosphere conditions
#
# Fix this crash
# ERROR:root:<class 'Exception'>
# Traceback (most recent call last):
#   File "c:\Users\vikto\Documents\Projects\Second Earth\Second_Earth.py", line 30, in <module>
#     main_loop.main_loop()
#   File "c:\Users\vikto\Documents\Projects\Second Earth\modules\main_loop.py", line 56, in main_loop
#     current_button.on_click()
#   File "c:\Users\vikto\Documents\Projects\Second Earth\modules\interface_types\buttons.py", line 1350, in on_click
#     constants.save_load_manager.new_game()
#   File "c:\Users\vikto\Documents\Projects\Second Earth\modules\tools\data_managers\save_load_manager_template.py", line 87, in new_game
#     game_transitions.create_strategic_map(from_save=False)
#   File "c:\Users\vikto\Documents\Projects\Second Earth\modules\util\game_transitions.py", line 191, in create_strategic_map
#    current_grid.create_world(from_save)
#  File "c:\Users\vikto\Documents\Projects\Second Earth\modules\interface_types\world_grids.py", line 62, in create_world
#     self.generate_terrain_parameters()
#   File "c:\Users\vikto\Documents\Projects\Second Earth\modules\interface_types\world_grids.py", line 430, in generate_terrain_parameters
#     self.generate_temperature()
#   File "c:\Users\vikto\Documents\Projects\Second Earth\modules\interface_types\world_grids.py", line 210, in generate_temperature
#     self.make_random_terrain_parameter_worm(
#   File "c:\Users\vikto\Documents\Projects\Second Earth\modules\interface_types\world_grids.py", line 537, in make_random_terrain_parameter_worm
#     original_value = self.find_cell(current_x, current_y).get_parameter(parameter)
#  AttributeError: 'NoneType' object has no attribute 'get_parameter'
