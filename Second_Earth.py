# Runs setup and main loop on program start

import modules.main_loop as main_loop
from modules.setup import *

try:
    setup(
        misc,
        equipment_types_config,
        terrain_feature_types_config,
        commodities,
        minister_types_config,
        unit_types_config,
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
        vehicle_organization_interface,
        settlement_interface,
        terrain_interface,
        inventory_interface,
        minister_interface,
    )
    main_loop.main_loop()

except Exception:  # Displays error message and records error message in crash log file
    manage_crash(Exception)

# Tasks:
#   General (game-agnostic):
# Add type hints on sight - gradual process
# add minister speech bubbles
# Add random events
# Add debug settings menu within game, rather than needing to edit .json out of game
# Add autosave and multiple save slots
# Add ambient sounds
# Continue adding new songs

#
#   New SE features:
# Strange issue - in non-ordered collections, height of collection incorrectly affects y positions of elements, and without any apparent modification to their y values
# Continue adding hairstyles
# Minister table_map_image not using smart green screens, probably because it directly uses tile image ID
# Add new unit art
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
#   Prosecutor -> Security (finding corruption, security)
#   Transportation -> Transportation (planetary transportation, logistics)
#   Production -> Industry (construction, factories, mining, agriculture)
#   Construction -> Energy (power plants, energy infrastructure)

# Upcoming work queue:
# Add spaceships images
# Add astronauts/cosmonauts group with corresponding officer
# Allow vehicles to be crewed by groups instead of workers
# Add building type classes that each instance can belong to
# Add new resource types, allowing buying on Earth, transporting, and using to build when it is in the builder's tile
# Allow building basic buildings like mines, farms, etc. with work crew functionality
# Allow large items to be stored in inventory, with supporting interface
# Add radio distortion versions of voice lines, either as separate files or runtime filter
# Add terrain details tile interface panel, such that terrain details aren't always showing
# For tiles with knowledge 1, possibly change every turn to a cloud or normal pixellated version, depending on atmosphere conditions
# Load in all minister portraits on minister creation, not when first viewed
# Expand permissions system to include temporary states, like sentry mode
# Possibly add permissions for ministers, if relevant
# Add new autofill interface for vehicle passengers, and possibly building work crews
# Modify vehicle classes to fit more with unit_type system - should not have their own permissions, especially can_swim and can_walk
# Look into caching surface objects for faster rendering, and render during loading before needed
#
# Fix this rare crash
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
