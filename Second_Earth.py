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
        building_types_config,
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
# Future subsystems:
"""
1. Add new resource types (water, food, oxygen, goods) - allow buying on Earth, transporting, and being used as unit upkeep
    Die instantly if not enough water, food, or oxygen - prompt before ending turn
2. Add new building types, including modules that can be transported and worked while on a vehicle
    Modules should take more than 1 inventory capacity each
    Possibly allow pre-upgraded modules?
    Building types:
        Warehouses
        Domes
            A dome can fit some number of buildings (include total upgrade level), allowing inhabitants to work without suits and use default attrition/upkeep
                Possibly use sprawl stat for amount of space a building takes, s.t. buildings like mines may take more space?
                After initial construction, any building can receive a life support upgrade w/ radiation shielding, contained atmosphere, etc. to work without suits
                    A dome should be more cost-effective than individual life support upgrades for multiple buildings
                    Even if housing and dome have 
            Dome itself can be upgraded to increase capacity
        Housing
            Workers must always have housing (housing can be a temporary vehicle, if necessary)
            Housing must be within transportation network of workplace, spending some network capacity each turn to commute if in different tiles
                A domed city could easily provide workers for a nearby outpost, if connected by a transportation network
            Some buildings will have some function as well as housing, such that its worker can live and work there - e.g. a fort, spaceship, etc.
                Buildings would first provide housing to their own workers, but one like a spaceship may have extra housing for others
            Housing also follows the life support upgrade system
                1/3 of upkeep/attrition should be allocated to housing, commute, and workplace
                    If living and working in the same dome, no suits required, and default attrition
                    If living and working in shielded buildings in the same tile, no suits required, and default attrition
                    If living and working in shielded buildings w/ unshielded vehicle/path as commute, suits required, and use 1/3 of suit attrition
                    If living in shielded building w/ unshielded commute and workplace, suits required, and use 2/3 of suit attrition
                    If living in unshielded building w/ unshielded commute and workplace, use full suit attrition
                        If a unit is not attached to a building, consider its workplace to be the most shielded building in its tile
                This allows quickly setting up outpost w/ minimal dome infrastructure, but requires more resources, suits, and attrition
                Alternatively, a dome or habitable planet trivializes these concerns
        Work-crew style buildings, which can extract resources, convert between 2 resources, spend use resources to gain some functionality
        Specialized buildings, including space elevator, plasma torus, teleoperation center, etc.
        Infrastructure
            Note - to create networks, calculating a minimal spanning tree could minimize total distances required (suggest most efficient road structure?)
                Cormen et al., Chapter 21
3. Add new unit types, such as astronauts/cosmonauts (allow crewing spaceship)
4. Add new minister backgrounds
5. Add new spaceship images
6. Add alien vegetation
7. Add alien animals
8. Add star system map
    Populate star system map with star in center and random planets/moons, where colonies can be founded
    Designate terraforming candidate
    Include edge of system as special area - allow steamship-style travel from Earth to planet and vice versa
        Moving to/from edge of system takes 1 turn, and moving from Earth to system takes x=distance turns, during which unit is at destination but inactive
    During exploration, show the current star system map - allow moving to next or investigating further
    Once planet is chosen, only ever show that star system's map again
    Add new "solar" game mode, with most interface overlapping between "solar" and "strategic" maps
    While on "solar", display miniature planet map, which transitions to "strategic" when clicked, and vice versa (such that clicking "zooms in")
    Unit can instantly (as an action) switch from "solar" to "strategic" map by landing/launching - only exists on 1 at a time - no hovering above a tile
9. Add fuel resource, with vehicle fuel mechanics
10. Add research screen
11. Add ideology system
12. Modify most actions to spend resources/time, rather than money - initially only allow ones from tile/inventory, then allow transportation networks
13. Add energy system with energy networks
14. Add supply networks
15. Add atmosphere mechanics
16. Add depositing/extracting gas/unpurified water to/from environment
17. Add randomized special resources
"""
# Find a way to load in all minister images on creating, rather than when first viewed - causing noticeable latency - populate rendered_images on creation
# Introduce TypeDicts (reference keyboard assignment), particularly for input_dicts and image_dicts
# Eventually look into planets where magnetic tilt != sun direction, tidally locked, etc.
# Add new colors for soil mapmode - gray to dark brown
# Add label icons for names of minister offices on ministers screen - possible add to SFA as well
# When creating new settlement, add notification that says what the name is and directs where to change it - also move this to SFA
# Possibly add procedurally generated names, with consistent style for each planet
#   Create new program to analyze series of inputs and extract letter/syllable frequencies - possibly combine with an ML method to output words of the same style
# Strange issue - in non-ordered collections, height of collection incorrectly affects y positions of elements, and without any apparent modification to their y values
# Continue adding hairstyles
# Minister table_map_image not using smart green screens, probably because it directly uses tile image ID
# Add new unit art
# Add new minister appointing system - selecting an unappointed minister should highlight all available positions, and clicking on one appoint w/ a confirmation check
# Add more variety to water/ice colors
# Eventually add hydrogen fuel cells - process to convert hydrogen and oxygen into water, actually releases energy but requires facility and hydrogen/oxygen input
# Include "advancement level" of building materials - 1 ~ stone/wood, etc. for basic shelters in atmosphere, 2 ~ for industrial steel/concrete for factories,
#   basic planetary construction, 3 ~ for titanium, carbon fiber, advanced modern-day materials, spaceships, etc., 4+ for more advanced
# Add minister deaths - may occur in assassination, attrition, freak accidents, heroic sacrifices, etc.

# Upcoming work queue:
# Replace get_worker, get_officer, etc. with get_unit, and same for has_unit
# Add modern minister outfits
# Add astronauts art
# Allow vehicles to be crewed by groups instead of workers
# Add new resource types, allowing buying on Earth, transporting, and using to build when it is in the builder's tile
# Allow building basic buildings like mines, farms, etc. with work crew functionality
# Allow large items to be stored in inventory, with supporting interface
# Add radio distortion versions of voice lines, either as separate files or runtime filter
# Add terrain details tile interface panel, such that terrain details aren't always showing
# For tiles with knowledge 1, possibly change every turn to a cloud or normal pixellated version, depending on atmosphere conditions
# Expand permissions system to include temporary states, like sentry mode
# Possibly add permissions for ministers, if relevant
# Add new autofill interface for vehicle passengers, and possibly building work crews
# Modify vehicle classes to fit more with unit_type system - should not have their own permissions, especially can_swim and can_walk
# Convert actor_type ("tile", "mob", "minister") to use constant keys
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
