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
        tile_interface,
        mob_interface,
        organization_interface,
        vehicle_organization_interface,
        unit_organization_interface,
        terrain_interface,
        settlement_interface,
        inventory_interface,
        mob_sub_interface,
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
1. Add new resource types (water, food, oxygen, goods, energy) - allow buying on Earth, transporting, and being used as unit upkeep
    Die instantly if not enough water, food, or oxygen - prompt before ending turn
    Grant free upkeep/housing to any units on Earth - functionally unlimited
    Possibly require different types of food for health bonuses
    Insufficient goods or energy is unpleasant but does not cause instant death
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
        Air miners
            Use building/work crew to collect small amounts of useful materials from atmosphere, particularly when they are common
        Work-crew style buildings, which can extract resources, convert between 2 resources, spend use resources to gain some functionality0
        Specialized buildings, including space elevator, plasma torus, teleoperation center, etc.
        Infrastructure
            Note - to create networks, calculating a minimal spanning tree could minimize total distances required (suggest most efficient road structure?)
                Cormen et al., Chapter 21
            Buildings should have some quality/durability, secretly determined on creation along with failure/success roll
                A corrupt roll may only steal some of the materials, actually using the rest but creating a faultier result
                Each building would preserve which minister created it, and quality could be discovered by Minister of Security after creation
                    Same system also applies to vehicles, organisms, etc.
                For units/items bought from Earth, the Terran Affairs minister would be responsible for ensuring the quality, as if built themselves
3. Add randomized special resources
    Implement Mars dry ice caps as special resources on the poles (likely known from the start, particularly South pole)
    Regardless of planet, there should be souvenirs (i.e. moon rocks) you can bring back to Earth for early money if you can transport it
        The price of souvenir would quickly collapse, and should not be profitable later in the game
4. Add depositing/extracting gas/unpurified water to/from environment
5. Add atmosphere mechanics
    Pressure
        A typical planet w/ 400 tiles would require an optimal of 2400 atmosphere units (6/tile) to be 15 psi or 1 bar
            Each "transaction" will involve about 0.1 atmosphere units - a plant may have a chance of converting 0.1 GHG to 0.1 oxygen
            With optimal conditions:
                78% inert gases
                    1872 units
                21% oxygen
                    504 units
                1% GHG
                    24 units
            Venus has 93 bar (223,200 units), Mars has 0.006 bar (10 units), Earth has 1 bar
        Modern "atmospheric diving suits" can go down to 610 meters below sea level (61 bar)
            Such a suit would not be able to sustain Venus' 93 bar atmosphere, but would likely be just able to at the time of this game
            https://en.wikipedia.org/wiki/Atmospheric_diving_suit
                Exosuit doesn't require decompression, and has 50 hours of life support w/ oxygen recycling
        Humans cannot dive below 40 meters without equipment - (4 bar)
            Humans could probably survive in 0.5-2 bar atmosphere with moderate attrition, 0.25-4 bar with severe attrition, instant death outside
                Regardless of composition (although oxygen/GHG levels could be dangerous even if pressure is tolerable)
        We could possibly have "effective pressure" that uses global pressure combined w/ altitude
            
    Water
        A typical planet w/ 400 tiles would require an optimal of 4.5 water units per tile = 1800 water units
    Temperature
        Keep track of planet's average temperature - distance from the sun and GHG levels should change levels until suitable average reached
            Create a function for what planet's average temperature should be
    Inert gases
        Any level of inert gas is safe, helps contribute to pressure without issues of oxygen and GHG
            In the future, we could add things like cooling inert gases ()
            Note: Venus only has 3.5% inert gases, but since pressure is 93 bar, it has 4 times as much nitrogen as Earth
    GHG
        0 - 0.5%: Safe, global cooling
        .5 - 1%: Safe
        1 - 2%: Global warming, long term exposure limit - moderate attrition and penalties
        2 - 3%: Global warming, short term exposure limit - severe attrition and penalties
        3% - 100%: Global warming, instant death
            Note: Earth with no GHG would have an -18 C/0 F average, rather than 14 C/57 F
                0 GHG would result in about -2 average temperature - each 0.5% contributes about 1 average temperature
                Earth with 6x GHG would increase by about 10 C average, as in permian extinction
                def average_temperature(distance, GHG):
                    return min(12, max(-5, 12 - distance + 2 * GHG pressure)) for random distances on some scale
                    Note that GHG pressure is based on the absolute # GHG units / planet size, rather than proportion of current atmosphere
                Venus has 96.5% CO2 and 3.5% inert gases
    Oxygen
        By OSHA guidelines:
            0% - 10%: nauseau, unconsciousness, heart failure - essentially instant death
            10% - 14%: Exhaustion, poor judgement - severe attrition and penalties but not instant death
            14% - 20%: Oxygen-deficient, impaired coordination, increased pulse/breathing rate - moderate attrition and penalties
            20% - 24%: Safe
            24% - 60%: Hyperoxia, higher flammability, long-term health problems - moderate attrition and penalties, higher accident risk
            60% - 100%: Oxygen toxicity, very high risk of explosion - severe attrition and penalties, very high accident risk
                Imagine a possible "oxygen world" with very high oxygen levels and near-constant fires
    Toxic gases
        0% - 0.1%: Safe
        0.1% - 0.5%: Moderate attrition and penalties
        0.5% - 1%: Severe attrition and penalties
        1% - 100%: Instant death
        Venus has ~1% toxic gases from sulfur dioxide, carbon monoxide, hydrogen chloride, hydrogen fluoride being common

    Radiation
        Keep track of radiation levels received globally
            Mitigate radiation levels with global shielding from magnetic field, atmosphere, etc.
                Show global radiation on global conditions panel and how much is blocked by magnetic field
            Mitigate radiation levels with local shielding from roughness
                Show local radiation on tile conditions panel and how much it is blocked by roughness
            Suits/buildings need to be shielded enough to block the remaining radiation not blocked by global/local shielding

    Magnetic field
        Based on magnetic field strength
        Magnetic field blocks some amount of incoming radiation
        Any unblocked radiation reaches tiles and causes a solar wind effect
        Solar wind removes a small amount of each gas each turn
            Light solar winds only remove water (lightest gas)
            Moderate solar winds remove oxygen, inert gases, water (heavier gases)
                Note: Planets like Mars and Venus tend to lose non-solid water to solar winds, while oxygen tends to stay but react to make FeO2, CO2, etc.
            Heavier solar winds remove all gases (heavier gases)
            On Mars, solar wind removes 100 grams (~0.25 pounds) of atmosphere per second
            Solar wind/radiation is slightly mitigated by distance from the sun - more than 50,000 AU/2 light years from the sun, it can no longer repel 

    Summary:
        Mars:
            No magnetic field - all atmosphere is eventually lost, with water being removed relatively quickly and oxygen/CO2 being removed very slowly
            0.006 bar atmsosphere
                w/ 400 tiles, 15/2400 atmosphere units: 0.8/1872 inert gases, 0/504 O2, 14.2/24 GHG, 0/2.4 toxic gases
                    GHG provides 9 F of warming - about 0.5 temperature units more than distance from sun would cause
            Strong radiation, mitigated by roughness locally (especially in chaos and canyon regions)
                240-300 mSv/year, with suggested limit of 20 mSv/year
            The dry ice on Mars, if evaporated, would increase the atmosphere pressure 43x, from 0.15 psi to 6.5 psi
        Venus:
            Light induced magnetic field - moderate amount of radiation gets through - introducing water long-term would require a magnetic field
            93 bar atmosphere - 3.5% inert gases, 95.5% GHG, 1% toxic gases
                w/ 400 tiles, 223,200/2400 atmosphere units: 7,812/1872 inert gases, 0/504 O2, 213,156/24 GHG, 2,232/2.4 toxic gases
            Moderate radiation, mitigated by roughness locally
            93 times ideal atmosphere pressure, 23x survivable atmosphere pressure
                Has twice the insolation of Earth - with Earth's atmosphere, it would have about 8 average temperature (poles would be habitable)
                    On Earth, doubling insolation goes from Canada temperatures to Mexico temperatures - about 60 F increase, 3 temperature steps
                    https://en.wikipedia.org/wiki/Solar_irradiance
        Earth:
            Strong magnetic field - minimal radiation gets through
            1 bar atmosphere - 78.5% inert gases, 21% O2, 0.5% GHG
                w/ 400 tiles, 2400/2400 atmosphere units: 1,884/1884 inert gases, 504/504 O2, 12/12 GHG, 0/2.4 toxic gases
        Create interface that conveys total pressure w/ proportions as well as quantities of O2, GHG, inert gases, toxic gases, followed by total water, radiation, and magnetic field
            - ~8 labels
    Appearance: Determine some random appearance of the atmosphere, based on composition and some random factors
        A planet with an Earth-like atmosphere would have an Earth-like blue sky and white clouds covering ~50% of the surface, but other compositions could be unpredictable
        Show sky as a transparent ring around the perimeter of the globe projection, and show clouds both on the projection and optionally on the tile map
            Mars has slight sky effect but no clouds due to low atmosphere, Venus is fully covered, Luna has no sky effect or clouds
        Additionally, the sky color largely determines the water color
            As atmosphere approaches 0, water color approaches space color or ground color, for deep water and shallow water, respectively
            For thicker atmosphere, sky color will be some random color based on composition, getting closer to Earth as atmosphere approaches earth-like composition
            For very thick atmospheres, sky effect should approach that of Venus
        When displaying clouds, have ~6 custom cloud images that are overlayed by picking 2
            Cloud frequency should be based on the amount of liquid water in the tile and nearby tiles (or just average water?)
            Change clouds at end of turn and while globes are spinning

6. Add alien vegetation
7. Add alien animals
    Add ancillary system - similar to equipment, but a person - attached to unit to enhance capabilities
    Could include "alien hunter" ancillary attached to marines to improve alien combat abilities
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
    Star system map should be next to the planet map, between Earth and the planet
    Initial expedition could contain a shuttle ship that must stay on the colony ship
        Since the shuttle itself could have cargo, it should take a net of 9 cargo on the colony ship
        Shuttle vs freighter distinction?
    Once a colony ship is landed on any planet, there should be a confirmation, confirming you want to stay on this planet for the rest of the game
        Once colony is created, other viable exoplanets in the system then become normal outpost locations
        Don't necessarily ask directly, but lock in once a colony ship is successfully landed
    Ship types should include colony ship, shuttle, and rocket
        Colony ship is very large and required at the start of the game
        Shuttle is smaller and can go on multiple trips
            It would be much more difficult for a shuttle to start a self-sustaining colony if it can't hold the necessary modules/work crews
        Rocket is uncrewed and one-way - similar to an airdrop or a missile
            Rockets must be uncrewed to prevent an over-supply of astronaut crews at either destination
    Can launch probes from within star system to explore parts of a planet or an outpost location
9. Add fuel resource, with vehicle fuel mechanics
    Possibly have lower fuel costs for launching from near the equator
10. Add research screen
    Scientists at labs should be able to research new technologies - likely focus on an area to improve and random advances will occur, with per-turn progress
    Possible technologies:
        Fusion power
        Floating infrastructure for Venusian planets
        Moholes
        Magnetic field generators
        Space elevators
        Improved spaceship fuel efficiency
        Better organism customization
        Studies of the planet itself - weather prediction, uses for new resources, etc.
        Construction teleoperation
            Implement robots as a single "software" unit working at a server to teleoperate many at once
        Improved spacesuit/building environmental tolerance ranges
        Gene repair/anti-aging
        VR training simulations
    Add some capability for the advances and techniques learned on the planet to help improve the state of Earth
11. Add ideology system
    Colonist morale and Earth public opinion should change based on your actions
    Colonist morale should approach 50 (indifferent), and Earth public opinion should approach 0 (constant progress expected)
12. Modify most actions to spend resources/time, rather than money - initially only allow ones from tile/inventory, then allow transportation networks
13. Add energy system with energy networks
14. Add supply networks
    Use network system for transportation/supply networks, energy networks, etc.
    An area of connected tiles should have a certain transportation capacity between them - any needed resources will automatically be transported
        Have special inventory interface showing what could be delivered here this turn
    Possibly use some variant of a max-flow algorithm like Ford-Fulkerson to calculate capacity and routes
    Supply network reaches out 1 tile from core (hiking distance)
    Trucks and rovers contribute less than trains but can extend the hiking distance to be a farther driving distance
    An isolated, exploring unit could safely move within 1 tile of its vehicle (portable housing/warehouse)
    Any networks without trains would be restricted to a core warehouse and vehicle driving distance away
    Include map modes for energy and supply networks
15. Add volcanic activity
    Volcanic activity strength/being present is a function of planet age and size, but there are exceptions
    Volcanic activity tends to output GHG and toxic gases, as well as temporarily increase the temperature
    Plate tectonics tend to cause lines of volcanoes on edges of plates, while planets w/o plate tectonics have larger volcanoes at arbitrary locations
        Plate tectonics allow deposition of GHG and toxic gases back out of the atmosphere, while planets w/o plate tectonics tend to accumulate them in the atmosphere
    Volcanic activity is generally (but not always) associated with a magnetic field, with both caused by a molten core
16. Add outposts/colonies
    Allow colonies on other planets/moons in the system - abstracted single tile that can produce resources not found on the planet
    Water import from Europa, ice/metals from Ceres, GHG/inert gases from Venus, etc., solid nitrogen/water from Pluto
    Various buildings could be built on the colony, but it is never directly colonized
    It would require a fully equipped colony ship like that on the main planet to colonize one of these
    Need to decide level of detail to require for colony management
    Many building could have outpost-specific variants
        Outpost buildings can upgrade scale, efficiency, or number (equivalent to expanding to multiple tiles)
    Possibly allow a shuttle (or higher technology ship) to create a transportation network within the system, allowing transporting resources automatically between them
    Reference notes/Planning.docx for Sol system outpost locations
        Particularly allow outposts to take the role of Io Mining Industries, Water Import from Europa, Phobos Space Haven, nitrogen imports, etc.
17. Temperature rework
    Local tile temperature could be a function of solation (distance from poles * distance from sun), GHG, random "weather modifier", albedo
        Avoid loops where temperature determines terrain, which determines albedo, which determines temperature
18. Organism customization
    Environmental engineers at a lab should be able to work towards creating a customized organism, with progress each turn based on success rolls
        Minister stealing part of materials should result in an organism that doesn't act quite as expected
            If encountered later, could be interpereted as a mutation, bad luck, or theft
        Customize features like range of habitability, growth rate/proliferation/reproduction method, energy method/objective
        Ideally use the same system for plants, animals, microbes, and even construction of customized buildings/equipment
    Examples:
        Slow-growing, extremely hardy lichen that can perform limited photosynthesis to improve oxygen and soil on Mars' initial condiitons
            Incorrect creation or mutation could cause different growth rates, habitability range, actuall decreasing soil quality, etc.
        Specialized, infectious microbe to eliminate a particular type of native plant
        Prolific algae focused on producing oxygen in wet areas
        Soil processing bacteria that improve soil quality
    Include templates for base organisms that are easier to start from, with extra difficulty for each modification (like JWE)
19. AI entities
    There should be various AI-controlled entities throughout the game, such as alien vegetation/animals, Earth-controlled units, other corporations, and rebelling units
    You may allow in a corporation and its units, and they will pursue their own goals on the planet, which may align with yours
        May introduce non-productive/parasitic elven bungalow-style buildings
    Alternatively, you may refuse the demands of Earth's government and provoke an attack of AI-controlled shuttles/marines
20. Planetary weather
    Add planetary weather and disasters such as earthquakes, dust storms, tsunamis, etc.
    More able to predict these as the game progresses - when you first land, you haven't done the long-term study to know what is even possible
21. New officer types
    The colony ship should include X number of each officer type, since Earth will send the most skilled people of every field
    These officers should be recruitable from a limited pool in your "capital" tile, similar to SFA slums
        You should be able to return an officer to the pool whenever you want, with a button like sentry mode (should not allow instant transport)
    Officer types:
        Scientists
        Executive/lobbyist
        Medical officer
        Environmental engineer
        Astronaut commander
        Marines
        Do land vehicles require crew?
        Technician (power plants)
        Foreman (work crews)
            Work crews create items that take inventory space, while other units make units/buildings or abstract products like research, money, energy
22. Space projects
    Include various large-scale projects in space
    Space projects are a major terraforming method - solettas, comets, etc.
    Can additionally be useful as infrastructure, such as orbital habitats and space elevators
    These should be expensive but impactful, with various opportunities throughout the game
23. Add new terrains
    Add crater, canyon terrain variants for each terrain type
        Ideally variants of high-roughness terrains that will occur if certain local features are present
    Add vegetation terrains, with Earth-dominated and alien-dominated variants
        Appearance should possibly depend on organisms present
"""
# Introduce TypeDicts (reference keyboard assignment), particularly for input_dicts and image_dicts
# Eventually look into planets where magnetic tilt != sun direction, tidally locked, etc.
# Add new colors for soil mapmode - gray to dark brown
# Add label icons for names of minister offices on ministers screen - possible add to SFA as well
# When creating new settlement, add notification that says what the name is and directs where to change it - also move this to SFA
# Possibly add procedurally generated names, with consistent style for each planet
#   Create new program to analyze series of inputs and extract letter/syllable frequencies - possibly combine with an ML method to output words of the same style
# Strange issue - in non-ordered collections, height of collection incorrectly affects y positions of elements, and without any apparent modification to their y values
# Continue adding hairstyles
# Add new unit art
# Add new minister appointing system - selecting an unappointed minister should highlight all available positions, and clicking on one appoint w/ a confirmation check
# Add more variety to water/ice colors
# Eventually add hydrogen fuel cells - process to convert hydrogen and oxygen into water, actually releases energy but requires facility and hydrogen/oxygen input
# Include "advancement level" of building materials - 1 ~ stone/wood, etc. for basic shelters in atmosphere, 2 ~ for industrial steel/concrete for factories,
#   basic planetary construction, 3 ~ for titanium, carbon fiber, advanced modern-day materials, spaceships, etc., 4+ for more advanced
# Add minister deaths - may occur in assassination, attrition, freak accidents, heroic sacrifices, etc.
# Rework/remove automatic replacement system - probably use "stun" effects w/o replacement, or death effects w/o replacement - no automatic replacement actions required
# Various resolution issues, particularly with tall resolutions
# Add manually created Earth map - should look similar to the UN flag, with a north pole projection
# Transcribe Super-Earth planet names from https://science.nasa.gov/exoplanets/exoplanet-catalog/?pageno=1&planet_type=Super+Earth&content_list=true
# God mode changes to make habitabilty deadly/not deadly not correctly calibrating reorganization projection of ship crew - fix if ever relevant outside of god mode
# Maybe track when tiles change habitability, as well as display habitability mode

# Upcoming work queue:
# Add temperature calculation - distance from sun/solation, GHG, random weather
#   Once planet brightness is determined, show the planet brightness with a transparent white/black filter on each tile - similar to atmosphere haze
#       Possibly draw this and clouds/atmosphere haze over units rather than under - modify how tiles are drawn
# Add 4+ water as deadly in local habitability equation (but not in global habitability summary)
# Add spacesuits image have helmeted/helmetless versions depending on if unit is outside
# Add modern minister outfits
# Add astronauts art
# Add new resource types, allowing buying on Earth, transporting, and using to build when it is in the builder's tile
# Allow building basic buildings like mines, farms, etc. with work crew functionality
# Allow large items to be stored in inventory, with supporting interface
# Add radio distortion versions of voice lines, either as separate files or runtime filter
#    Add radio voice lines for units in spacesuits
# Expand permissions system to include temporary states, like sentry mode
# Possibly add permissions for ministers, if relevant
# Convert actor_type ("tile", "mob", "minister") to use constant keys
# Investigate adding bolded, colored fonts in labels - similar to "/n" parsing
# Add altitude effect to local pressure
# Include pressure in landing difficulty
# Sort inventory display in ascending order, such that most abundant items are shown last and do not block other items
# Show key/legend with keywords on parameter map modes
# Use keywords instead of numbers for all local parameters (local fahrenheit average range for temperature)
# Include penalties on most rolls for wearing spacesuits
# Fix unit/tile outlines to blit in draw order, rather than appearing in front at all times (would fix occasional notification overlap)
# Store local resolution (possibly as save game metadata) to better recreate resolution errors
# Improve clarity for astronauts acting as ship crew - include in tooltips, rather than just in labels
# Improve parameter tooltips - most are currently empty
# Create and display standard movement cost formula based on parameter values
# Look into minister speech bubbles for minister messages, particularly tutorial messages
# Prevent polar tiles from appearing too close to equator in globe projection - primary cause of visible distortions
#   Copy an adjacent tile instead of far away tiles, even if the other tile doesn't have a latitude line
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
