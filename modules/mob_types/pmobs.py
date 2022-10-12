#Contains functionality for player-controlled mobs

import pygame
import random

from ..mobs import mob
from .. import text_tools
from .. import utility
from .. import actor_utility
from .. import notification_tools
from .. import dice
from .. import scaling
from .. import images
from .. import dice_utility
from .. import turn_management_tools
from .. import minister_utility
from ..tiles import status_icon

class pmob(mob):
    '''
    Short for player-controlled mob, mob controlled by the player
    '''
    def __init__(self, from_save, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'grids': grid list value - grids in which this mob's images can appear
                'image': string value - File path to the image used by this object
                'name': string value - Required if from save, this mob's name
                'modes': string list value - Game modes during which this mob's images can appear
                'end_turn_destination': string or int tuple value - Required if from save, 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'max_movement_points': int value - Required if from save, maximum number of movement points this mob can have
                'sentry_mode': boolean value - Required if from save, whether this unit is in sentry mode, preventing it from being in the turn order
                'in_turn_queue': boolean value - Required if from save, whether this unit is in the turn order, allowing end unit turn commands, etc. to persist after saving/loading
                'base_automatic_route': int tuple list value - Required if from save, list of the coordinates in this unit's automatic movement route, with the first coordinates being the start and the last being the end. List empty if
                    no automatic movement route has been designated
                'in_progress_automatic_route': string/int tuple list value - Required if from save, list of the coordinates and string commands this unit will execute, changes as the route is executed
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.sentry_mode = False
        super().__init__(from_save, input_dict, global_manager)
        self.selection_outline_color = 'bright green'
        global_manager.get('pmob_list').append(self)
        self.is_pmob = True

        self.set_controlling_minister_type('none')
        if from_save:
            if not input_dict['end_turn_destination'] == 'none': #end turn destination is a tile and can't be pickled, need to find it again after loading
                end_turn_destination_x, end_turn_destination_y = input_dict['end_turn_destination']
                end_turn_destination_grid = self.global_manager.get(input_dict['end_turn_destination_grid_type'])
                self.end_turn_destination = end_turn_destination_grid.find_cell(end_turn_destination_x, end_turn_destination_y).tile
            self.default_name = input_dict['default_name']
            self.set_name(self.default_name)
            self.set_sentry_mode(input_dict['sentry_mode'])
            if input_dict['in_turn_queue'] and input_dict['end_turn_destination'] == 'none':
                self.add_to_turn_queue()
            else:
                self.remove_from_turn_queue()
            self.base_automatic_route = input_dict['base_automatic_route']
            self.in_progress_automatic_route = input_dict['in_progress_automatic_route']
        else:
            self.default_name = self.name
            self.set_max_movement_points(4)
            actor_utility.deselect_all(self.global_manager)
            self.select()
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.images[0].current_cell.tile)
            self.set_sentry_mode(False)
            self.add_to_turn_queue()
            self.base_automatic_route = [] #first item is start of route/pickup, last item is end of route/dropoff
            self.in_progress_automatic_route = [] #first item is next step, last item is current location
        self.current_roll_modifier = 0
        self.default_min_success = 4
        self.default_max_crit_fail = 1
        self.default_min_crit_success = 6
        self.attached_dice_list = []

    def to_save_dict(self):
        '''
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                Along with superclass outputs, also saves the following values:
                'default_name': string value - This actor's name without modifications like veteran
                'end_turn_destination': string or int tuple value- 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'sentry_mode': boolean value - Whether this unit is in sentry mode, preventing it from being in the turn order
                'in_turn_queue': boolean value - Whether this unit is in the turn order, allowing end unit turn commands, etc. to persist after saving/loading
                'base_automatic_route': int tuple list value - List of the coordinates in this unit's automatic movement route, with the first coordinates being the start and the last being the end. List empty if
                    no automatic movement route has been designated
                'in_progress_automatic_route': string/int tuple list value - List of the coordinates and string commands this unit will execute, changes as the route is executed
        '''
        save_dict = super().to_save_dict()
        if self.end_turn_destination == 'none':
            save_dict['end_turn_destination'] = 'none'
        else: #end turn destination is a tile and can't be pickled, need to save its location to find it again after loading
            for grid_type in self.global_manager.get('grid_types_list'):
                if self.end_turn_destination.grid == self.global_manager.get(grid_type):
                    save_dict['end_turn_destination_grid_type'] = grid_type
            save_dict['end_turn_destination'] = (self.end_turn_destination.x, self.end_turn_destination.y)
        save_dict['default_name'] = self.default_name
        save_dict['sentry_mode'] = self.sentry_mode
        save_dict['in_turn_queue'] = (self in self.global_manager.get('player_turn_queue'))
        save_dict['base_automatic_route'] = self.base_automatic_route
        save_dict['in_progress_automatic_route'] = self.in_progress_automatic_route
        return(save_dict)

    def add_to_automatic_route(self, new_coordinates):
        '''
        Description:
            Adds the inputted coordinates to this unit's automated movement route, changing the in-progress route as needed
        Input:
            int tuple new_coordinates: New x and y coordinates to add to the route
        Output:
            None
        '''
        self.base_automatic_route.append(new_coordinates)
        self.calculate_automatic_route()
        if self == self.global_manager.get('displayed_mob'):
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self)

    def calculate_automatic_route(self):
        '''
        Description:
            Creates an in-progress movement route based on the base movement route when the base movement route changes
        Input:
            None
        Output:
            None
        '''
        reversed_base_automatic_route = utility.copy_list(self.base_automatic_route)
        reversed_base_automatic_route.reverse()
    
        self.in_progress_automatic_route = ['start']
        #imagine base route is [0, 1, 2, 3, 4]
        #reverse route is [4, 3, 2, 1, 0]
        for current_index in range(1, len(self.base_automatic_route)): #first destination is 2nd item in list
            self.in_progress_automatic_route.append(self.base_automatic_route[current_index])
        #now in progress route is ['start', 1, 2, 3, 4]

        self.in_progress_automatic_route.append('end')
        for current_index in range(1, len(reversed_base_automatic_route)):
            self.in_progress_automatic_route.append(reversed_base_automatic_route[current_index])
        #now in progress route is ['start', 1, 2, 3, 4, 'end', 3, 2, 1, 0]

    def can_follow_automatic_route(self):
        '''
        Description:
            Returns whether the next step of this unit's in-progress movement route could be completed at this moment
        Input:
            None
        Output
            boolean: Returns whether the next step of this unit's in-progress movement route could be completed at this moment
        '''
        next_step = self.in_progress_automatic_route[0]
        if next_step == 'end': #can drop off freely unless train without train station
            if not (self.is_vehicle and self.vehicle_type == 'train' and not self.images[0].current_cell.has_intact_building('train_station')):
                return(True)
            else:
                return(False)
        elif next_step == 'start': 
            if len(self.images[0].current_cell.tile.get_held_commodities(True)) > 0 or self.get_inventory_used() > 0: #only start round trip if there is something to deliver, either from tile or in inventory already
                if not (self.is_vehicle and self.vehicle_type == 'train' and not self.images[0].current_cell.has_intact_building('train_station')): #can pick up freely unless train without train station
                    return(True)
                else:
                    return(False)
            else:
                return(False)
        else: #must have enough movement points, not blocked
            x_change = next_step[0] - self.x
            y_change = next_step[1] - self.y
            return(self.can_move(x_change, y_change, False))

    def follow_automatic_route(self):
        '''
        Description:
            Moves along this unit's in-progress movement route until it can not complete the next step. A unit will wait for commodities to transport from the start, then pick them up and move along the path, picking up others along
                the way. At the end of the path, it drops all commodities and moves back towards the start
        Input:
            None
        Output:
            None
        '''
        progressed = False
        
        if len(self.in_progress_automatic_route) > 0:
            while self.can_follow_automatic_route():
                next_step = self.in_progress_automatic_route[0]
                if next_step == 'start':
                    self.pick_up_all_commodities(True)
                elif next_step == 'end':
                    self.drop_inventory()
                else:
                    x_change = next_step[0] - self.x
                    y_change = next_step[1] - self.y
                    self.move(x_change, y_change)
                    if not (self.is_vehicle and self.vehicle_type == 'train' and not self.images[0].current_cell.has_intact_building('train_station')):
                        if self.get_next_automatic_stop() == 'end': #only pick up commodities on way to end
                            self.pick_up_all_commodities(True)
                progressed = True
                self.in_progress_automatic_route.append(self.in_progress_automatic_route.pop(0)) #move first item to end
                
        return(progressed) #returns whether unit did anything to show unit in movement routes report

    def get_next_automatic_stop(self):
        '''
        Description:
            Returns the next stop for this unit's in-progress automatic route, or 'none' if there are stops
        Input:
            None
        Output:
            string: Returns the next stop for this unit's in-progress automatic route, or 'none' if there are stops
        '''
        for current_stop in self.in_progress_automatic_route:
            if current_stop in ['start', 'end']:
                return(current_stop)
        return('none')

    def pick_up_all_commodities(self, ignore_consumer_goods = False):
        '''
        Description:
            Adds as many local commodities to this unit's inventory as possible, possibly choosing not to pick up consumer goods based on the inputted boolean
        Input:
            boolean ignore_consumer_goods = False: Whether to not pick up consumer goods from this unit's tile
        Output:
            None
        '''
        tile = self.images[0].current_cell.tile
        while self.get_inventory_remaining() > 0 and len(tile.get_held_commodities(ignore_consumer_goods)) > 0:
            commodity = tile.get_held_commodities(ignore_consumer_goods)[0]
            self.change_inventory(commodity, 1)
            tile.change_inventory(commodity, -1)

    def clear_automatic_route(self):
        '''
        Description:
            Removes this unit's saved automatic movement route
        Input:
            None
        Output:
            None
        '''
        self.base_automatic_route = []
        self.in_progress_automatic_route = []
        if self == self.global_manager.get('displayed_mob'):
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self)

    def selection_sound(self):
        '''
        Description:
            Plays a sound when this unit is selected, with a varying sound based on this unit's type
        Input:
            None
        Output:
            None
        '''
        if self.is_officer or self.is_group or self.is_vehicle:
            if self.is_battalion or self.is_safari or (self.is_officer and self.officer_type in ['hunter', 'major']):
                self.global_manager.get('sound_manager').play_sound('bolt action 2')
            possible_sounds = ['voices/voice 1', 'voices/voice 2']
            if self.is_vehicle and self.vehicle_type == 'ship':
                possible_sounds.append('voices/ship 2')
            self.global_manager.get('sound_manager').play_sound(random.choice(possible_sounds))

    def set_sentry_mode(self, new_value):
        '''
        Description:
            Sets a new sentry mode of this status, creating a sentry icon or removing the existing one as needed
        Input:
            boolean new_value: New sentry mode status for this unit
        Output:
            None
        '''
        old_value = self.sentry_mode
        if not old_value == new_value:
            self.sentry_mode = new_value
            if new_value == True:
                for current_grid in self.grids:
                    if current_grid == self.global_manager.get('minimap_grid'):
                        sentry_icon_x, sentry_icon_y = current_grid.get_mini_grid_coordinates(self.x, self.y)
                    elif current_grid == self.global_manager.get('europe_grid'):
                        sentry_icon_x, sentry_icon_y = (0, 0)
                    else:
                        sentry_icon_x, sentry_icon_y = (self.x, self.y)
                    input_dict = {}
                    input_dict['coordinates'] = (sentry_icon_x, sentry_icon_y)
                    input_dict['grid'] = current_grid
                    input_dict['image'] = 'misc/sentry_icon.png'
                    input_dict['name'] = 'sentry icon'
                    input_dict['modes'] = ['strategic', 'europe']
                    input_dict['show_terrain'] = False
                    input_dict['actor'] = self
                    input_dict['status_icon_type'] = 'sentry'
                    self.status_icons.append(status_icon(False, input_dict, self.global_manager))
                self.remove_from_turn_queue()
                if self.global_manager.get('displayed_mob') == self:
                    actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #updates actor info display with sentry icon
            else:
                remaining_icons = []
                for current_status_icon in self.status_icons:
                    if current_status_icon.status_icon_type == 'sentry':
                        current_status_icon.remove()
                    else:
                        remaining_icons.append(current_status_icon)
                self.status_icons = remaining_icons
                if self.movement_points > 0 and not (self.is_vehicle and self.crew == 'none'):
                    self.add_to_turn_queue()
            if self == self.global_manager.get('displayed_mob'):
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self)
        

    def add_to_turn_queue(self):
        '''
        Description:
            At the start of the turn or once removed from another actor/building, attempts to add this unit to the list of units to cycle through with tab. Units in sentry mode or without movement are not added
        Input:
            None
        Output:
            None
        '''
        if (not self.sentry_mode) and self.movement_points > 0 and self.end_turn_destination == 'none':
            turn_queue = self.global_manager.get('player_turn_queue')
            if not self in turn_queue:
                turn_queue.append(self)

    def remove_from_turn_queue(self):
        '''
        Description:
            Removes this unit from the list of units to cycle through with tab
        Input:
            None
        Output:
            None
        '''
        turn_queue = self.global_manager.get('player_turn_queue')
        self.global_manager.set('player_turn_queue', utility.remove_from_list(turn_queue, self))

    def replace(self):
        '''
        Description:
            Replaces this unit for a new version of itself when it dies from attrition, removing all experience and name modifications
        Input:
            None
        Output:
            None
        '''
        self.set_name(self.default_name)
        if (self.is_group or self.is_officer) and self.veteran:
            self.veteran = False
            new_status_icons = []
            for current_status_icon in self.status_icons:
                if current_status_icon.status_icon_type == 'veteran':
                    current_status_icon.remove()
                else:
                    new_status_icons.append(current_status_icon)
            self.status_icons = new_status_icons

    def manage_health_attrition(self, current_cell = 'default'): #other versions of manage_health_attrition in group, vehicle, and resource_building
        '''
        Description:
            Checks this mob for health attrition each turn
        Input:
            string/cell current_cell = 'default': Records which cell the attrition is taking place in, used when a unit is in a building or another mob and does not technically exist in any cell
        Output:
            None
        '''
        if current_cell == 'default':
            current_cell = self.images[0].current_cell
        if current_cell.local_attrition():
            transportation_minister = self.global_manager.get('current_ministers')[self.global_manager.get('type_minister_dict')['transportation']]
            if transportation_minister.no_corruption_roll(6) == 1 or self.global_manager.get('DEBUG_boost_attrition'):
                worker_type = 'none'
                if self.is_worker:
                    worker_type = self.worker_type
                if (not worker_type in ['African', 'slave']) or random.randrange(1, 7) <= 2:
                    self.attrition_death()

    def attrition_death(self):
        '''
        Description:
            Kills this unit, takes away its next turn, and automatically buys a replacement when it fails its rolls for health attrition. If an officer dies, the replacement costs the officer's usual recruitment cost and does not have
                the previous officer's experience. If a worker dies, the replacement is found and recruited from somewhere else on the map, increasing worker upkeep colony-wide as usual
        Input:
            None
        Output:
            None
        '''
        self.global_manager.get('evil_tracker').change(3)
        if self.is_officer or self.is_worker:
            self.temp_disable_movement()
            self.replace()
            notification_tools.display_zoom_notification(utility.capitalize(self.name) + " has died from attrition at (" + str(self.x) + ", " + str(self.y) + ") /n /n The unit will remain inactive for the next turn as replacements are found.",
                self.images[0].current_cell.tile, self.global_manager)
        else:
            notification_tools.display_zoom_notification(utility.capitalize(self.name) + " has died from attrition at (" + str(self.x) + ", " + str(self.y) + ")", self.images[0].current_cell.tile, self.global_manager)
            self.die()

    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. Also deselects this mob and drops any commodities it is carrying
        Input:
            None
        Output:
            None
        '''
        if (not self.images[0].current_cell == 'none') and (not self.images[0].current_cell.tile == 'none'): #drop inventory on death
            current_tile = self.images[0].current_cell.tile
            for current_commodity in self.global_manager.get('commodity_types'):
                current_tile.change_inventory(current_commodity, self.get_inventory(current_commodity))
        self.remove_from_turn_queue()
        super().remove()
        self.global_manager.set('pmob_list', utility.remove_from_list(self.global_manager.get('pmob_list'), self)) #make a version of pmob_list without self and set pmob_list to it

    def draw_outline(self):
        '''
        Description:
            Draws a flashing outline around this mob if it is selected, also shows its end turn destination, if any
        Input:
            None
        Output:
            None
        '''
        if self.global_manager.get('show_selection_outlines'):
            for current_image in self.images:
                if not current_image.current_cell == 'none' and self == current_image.current_cell.contained_mobs[0]: #only draw outline if on top of stack
                    pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')[self.selection_outline_color], (current_image.outline), current_image.outline_width)

                    if len(self.base_automatic_route) > 0:
                        start_coordinates = self.base_automatic_route[0]
                        end_coordinates = self.base_automatic_route[-1]
                        for current_coordinates in self.base_automatic_route:
                            current_tile = self.grids[0].find_cell(current_coordinates[0], current_coordinates[1]).tile
                            equivalent_tile = current_tile.get_equivalent_tile()
                            if current_coordinates == start_coordinates:
                                color = 'purple'
                            elif current_coordinates == end_coordinates:
                                color = 'yellow'
                            else:
                                color = 'bright blue'
                            current_tile.draw_destination_outline(color)
                            if not equivalent_tile == 'none':
                                equivalent_tile.draw_destination_outline(color)
                    
            if (not self.end_turn_destination == 'none') and self.end_turn_destination.images[0].can_show(): #only show outline if tile is showing
                self.end_turn_destination.draw_destination_outline()
                equivalent_tile = self.end_turn_destination.get_equivalent_tile()
                if not equivalent_tile == 'none':
                    equivalent_tile.draw_destination_outline()
                        
                    

    def check_if_minister_appointed(self):
        '''
        Description:
            Returns whether there is currently an appointed minister to control this unit
        Input:
            None
        Output:
            boolean: Returns whether there is currently an appointed minister to control this unit
        '''
        if minister_utility.positions_filled(self.global_manager): #not self.controlling_minister == 'none':
            return(True)
        else:
            #keyword = self.global_manager.get('minister_type_dict')[self.controlling_minister_type]
            text_tools.print_to_screen("", self.global_manager)
            text_tools.print_to_screen("You can not do that until all ministers have been appointed", self.global_manager)
            text_tools.print_to_screen("Press q or the button in the upper left corner of the screen to manage your ministers", self.global_manager)
            return(False)

    def set_controlling_minister_type(self, new_type):
        '''
        Description:
            Sets the type of minister that controls this unit, like "Minister of Trade"
        Input:
            string new_type: Type of minister to control this unit, like "Minister of Trade"
        Output:
            None
        '''
        self.controlling_minister_type = new_type
        self.update_controlling_minister()

    def update_controlling_minister(self):
        '''
        Description:
            Sets the minister that controls this unit to the one occupying the office that has authority over this unit
        Input:
            None
        Output:
            None
        '''
        if self.controlling_minister_type == 'none':
            self.controlling_minister = 'none'
        else:
            self.controlling_minister = self.global_manager.get('current_ministers')[self.controlling_minister_type]
            for current_minister_type_image in self.global_manager.get('minister_image_list'):
                if current_minister_type_image.minister_type == self.controlling_minister_type:
                    current_minister_type_image.calibrate(self.controlling_minister)

    def end_turn_move(self):
        '''
        Description:
            If this mob has any pending movement orders at the end of the turn, this executes the movement. Currently used to move ships between Africa and Europe at the end of the turn
        Input:
            None
        Output:
            None
        '''
        if not self.end_turn_destination == 'none':
            if self.grids[0] in self.end_turn_destination.grids: #if on same grid
                nothing = 0 #do once queued movement is added
            else: #if on different grid
                if self.can_travel():
                    self.go_to_grid(self.end_turn_destination.grids[0], (self.end_turn_destination.x, self.end_turn_destination.y))
                    self.manage_inventory_attrition() #do an inventory check when crossing ocean, using the destination's terrain
            self.end_turn_destination = 'none'
    
    def can_travel(self): #if can move between Europe, Africa, etc.
        '''
        Description:
            Returns whether this mob can cross the ocean, like going between Africa and Europe. By default, mobs cannot cross the ocean, but subclasses like ship are able to return True
        Input:
            None
        Output:
            boolean: Returns True if this mob can cross the ocean, otherwise returns False
        '''
        return(False) #different for subclasses

    def change_inventory(self, commodity, change):
        '''
        Description:
            Changes the number of commodities of a certain type held by this mob. Also ensures that the mob info display is updated correctly
        Input:
            string commodity: Type of commodity to change the inventory of
            int change: Amount of commodities of the inputted type to add. Removes commodities of the inputted type if negative
        Output:
            None
        '''
        if self.can_hold_commodities:
            self.inventory[commodity] += change
            if self.global_manager.get('displayed_mob') == self:
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self)

    def set_inventory(self, commodity, new_value):
        '''
        Description:
            Sets the number of commodities of a certain type held by this mob. Also ensures that the mob info display is updated correctly
        Input:
            string commodity: Type of commodity to set the inventory of
            int new_value: Amount of commodities of the inputted type to set inventory to
        Output:
            None
        '''
        if self.can_hold_commodities:
            self.inventory[commodity] = new_value
            if self.global_manager.get('displayed_mob') == self:
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self)

    def fire(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. Has different effects from die in certain subclasses
        Input:
            None
        Output:
            None
        '''
        self.die()

    def can_move(self, x_change, y_change, can_print = True):
        '''
        Description:
            Returns whether this mob can move to the tile x_change to the right of it and y_change above it. Movement can be prevented by not being able to move on water/land, the edge of the map, limited movement points, etc.
        Input:
            int x_change: How many cells would be moved to the right in the hypothetical movement
            int y_change: How many cells would be moved upward in the hypothetical movement
            boolean can_print = True: Whether to print messages to explain why a unit can't move in a certain direction
        Output:
            boolean: Returns True if this mob can move to the proposed destination, otherwise returns False
        '''
        future_x = self.x + x_change
        future_y = self.y + y_change
        transportation_minister = self.global_manager.get('current_ministers')[self.global_manager.get('type_minister_dict')['transportation']]
        if not transportation_minister == 'none':
            if self.can_leave():
                if not self.grid in self.global_manager.get('abstract_grid_list'):
                    if future_x >= 0 and future_x < self.grid.coordinate_width and future_y >= 0 and future_y < self.grid.coordinate_height:
                        future_cell = self.grid.find_cell(future_x, future_y)
                        if future_cell.visible or self.can_explore:
                            destination_type = 'land'
                            if future_cell.terrain == 'water':
                                destination_type = 'water' #if can move to destination, possible to move onto ship in water, possible to 'move' into non-visible water while exploring
                            passed = False
                            if destination_type == 'land':
                                if self.can_walk or self.can_explore or (future_cell.has_intact_building('port') and self.images[0].current_cell.terrain == 'water'):
                                    passed = True
                            elif destination_type == 'water':
                                if destination_type == 'water':
                                    if self.can_swim or (future_cell.has_vehicle('ship', self.is_worker) and not self.is_vehicle) or (self.can_explore and not future_cell.visible) or (self.is_battalion and (not future_cell.get_best_combatant('npmob') == 'none')):
                                        passed = True

                            if passed:
                                if destination_type == 'water':
                                    if not (future_cell.has_vehicle('ship', self.is_worker) and not self.is_vehicle): #doesn't matter if can move in ocean or rivers if boarding ship
                                        if not (self.is_battalion and (not future_cell.get_best_combatant('npmob') == 'none')): #battalions can attack enemies in water, but must retreat afterward
                                            if (future_y == 0 and not self.can_swim_ocean) or (future_y > 0 and not self.can_swim_river):
                                                if can_print:
                                                    if future_y == 0:
                                                        text_tools.print_to_screen("This unit can not move into the ocean.", self.global_manager)
                                                    elif future_y > 0:
                                                        text_tools.print_to_screen("This unit can not move through rivers.", self.global_manager)
                                                return(False)
                                    
                                if self.movement_points >= self.get_movement_cost(x_change, y_change) or self.has_infinite_movement and self.movement_points > 0: #self.movement_cost:
                                    if (not future_cell.has_npmob()) or self.is_battalion or self.is_safari or (self.can_explore and not future_cell.visible): #non-battalion units can't move into enemies
                                        return(True)
                                    else:
                                        if can_print:
                                            text_tools.print_to_screen("You can not move through enemy units.", self.global_manager)
                                        return(False)
                                else:
                                    if can_print:
                                        text_tools.print_to_screen("You do not have enough movement points to move.", self.global_manager)
                                        text_tools.print_to_screen("You have " + str(self.movement_points) + " movement points while " + str(self.get_movement_cost(x_change, y_change)) + " are required.", self.global_manager)
                                    return(False)
                            elif destination_type == 'land' and not self.can_walk: #if trying to walk on land and can't
                                #if future_cell.visible or self.can_explore: #already checked earlier
                                if can_print:
                                    text_tools.print_to_screen("You can not move on land with this unit unless there is a port.", self.global_manager)
                                return(False)
                            else: #if trying to swim in water and can't 
                                #if future_cell.visible or self.can_explore: #already checked earlier
                                if can_print:
                                    text_tools.print_to_screen("You can not move on water with this unit.", self.global_manager)
                                return(False)
                        else:
                            if can_print:
                                text_tools.print_to_screen("You can not move into an unexplored tile.", self.global_manager)
                            return(False)
                    else:
                        text_tools.print_to_screen("You can not move off of the map.", self.global_manager)
                        return(False)
                else:
                    if can_print:
                        text_tools.print_to_screen("You can not move while in this area.", self.global_manager)
                    return(False)
        else:
            if can_print:
                text_tools.print_to_screen("You can not move units before a Minister of Transportation has been appointed.", self.global_manager)
            return(False)

    def can_show_tooltip(self):
        '''
        Description:
            Returns whether this mob's tooltip can be shown. Along with the superclass' requirements, mob tooltips can not be shown when attached to another actor, such as when working in a building
        Input:
            None
        Output:
            None
        '''
        if self.in_vehicle or self.in_group or self.in_building:
            return(False)
        else:
            return(super().can_show_tooltip())

    def embark_vehicle(self, vehicle):
        '''
        Description:
            Hides this mob and embarks it on the inputted vehicle as a passenger. Any commodities held by this mob are put on the vehicle if there is cargo space, or dropped in its tile if there is no cargo space
        Input:
            vehicle vehicle: vehicle that this mob becomes a passenger of
        Output:
            None
        '''
        self.in_vehicle = True
        self.vehicle = vehicle
        self.selected = False
        for current_commodity in self.get_held_commodities(): #gives inventory to ship
            num_held = self.get_inventory(current_commodity)
            for current_commodity_unit in range(num_held):
                if vehicle.get_inventory_remaining() > 0:
                    vehicle.change_inventory(current_commodity, 1)
                else:
                    self.images[0].current_cell.tile.change_inventory(current_commodity, 1)
        self.hide_images()
        self.remove_from_turn_queue()
        vehicle.contained_mobs.append(self)
        self.inventory_setup() #empty own inventory
        vehicle.hide_images()
        vehicle.show_images() #moves vehicle images to front
        if not vehicle.initializing: #don't select vehicle if loading in at start of game
            vehicle.select()
        if not self.global_manager.get('loading_save'):
            self.global_manager.get('sound_manager').play_sound('footsteps')
        self.clear_automatic_route()

    def disembark_vehicle(self, vehicle):
        '''
        Description:
            Shows this mob and disembarks it from the inputted vehicle after being a passenger
        Input:
            vehicle vehicle: vehicle that this mob disembarks from
        Output:
            None
        '''
        vehicle.contained_mobs = utility.remove_from_list(vehicle.contained_mobs, self)
        self.vehicle = 'none'
        self.in_vehicle = False
        self.x = vehicle.x
        self.y = vehicle.y
        for current_image in self.images:
            current_image.add_to_cell()
        vehicle.selected = False
        if self.images[0].current_cell.get_intact_building('port') == 'none':
            self.set_disorganized(True)
        if self.can_trade and self.can_hold_commodities: #if caravan
            consumer_goods_present = vehicle.get_inventory('consumer goods')
            if consumer_goods_present > 0:
                consumer_goods_transferred = consumer_goods_present
                if consumer_goods_transferred > self.inventory_capacity:
                    consumer_goods_transferred = self.inventory_capacity
                vehicle.change_inventory('consumer goods', -1 * consumer_goods_transferred)
                self.change_inventory('consumer goods', consumer_goods_transferred)
                text_tools.print_to_screen(utility.capitalize(self.name) + " automatically took " + str(consumer_goods_transferred) + " consumer goods from " + vehicle.name + "'s cargo.", self.global_manager)
                
        self.select()
        self.add_to_turn_queue()
        if self.global_manager.get('minimap_grid') in self.grids:
            self.global_manager.get('minimap_grid').calibrate(self.x, self.y)
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.images[0].current_cell.tile)
        self.global_manager.get('sound_manager').play_sound('footsteps')

    def start_combat(self, combat_type, enemy):
        '''
        Description
            Used when any player unit is involved in combat, displays a notification that combat is starting and starts the combat process. Unlike most action start functions, the choice to start combat is in a separate
                battalion-specific function
        Input:
            string combat_type: Type of combat, either defending or attacking
            npmob enemy: Enemy that the combat is being fought against
        Output:
            None
        '''
        if combat_type == 'defending': #if being attacked on main grid, move minimap there to show location
            if self.sentry_mode:
                self.set_sentry_mode(False)
            if self.global_manager.get('strategic_map_grid') in self.grids:
                self.global_manager.get('minimap_grid').calibrate(self.x, self.y)
                self.select()
                self.move_to_front()
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #should solve issue with incorrect unit displayed during combat causing issues with combat notifications
        self.global_manager.set('ongoing_combat', True)
        if combat_type == 'defending':
            message = utility.capitalize(enemy.name) + " " + utility.conjugate('be', enemy.number) + " attacking your " + self.name + " at (" + str(self.x) + ", " + str(self.y) + ")."
        elif combat_type == 'attacking':
            message = "Your " + self.name + " " + utility.conjugate('be', self.number) + " attacking the " + enemy.name + " at (" + str(self.x) + ", " + str(self.y) + ")."
        self.current_combat_type = combat_type
        self.current_enemy = enemy
        
        if self.veteran: #tells notifications how many of the currently selected mob's dice to show while rolling. Has 1 more die than usual because enemy also rolls
            num_dice = 3
        else:
            num_dice = 2
            
        notification_tools.display_notification(message, 'combat', self.global_manager, num_dice)
        self.global_manager.get('sound_manager').play_sound('bolt action 1')
        self.combat() #later call next step when closing combat action notification instead of immediately

    def combat(self):
        '''
        Description:
            Controls the combat process, determining and displaying its result through a series of notifications. Unlike most action functions, uses 2 competing rolls instead of a roll against a difficulty class
        Input:
            None
        Output:
            None
        '''
        combat_type = self.current_combat_type
        enemy = self.current_enemy
        own_combat_modifier = self.get_combat_modifier()
        enemy_combat_modifier = enemy.get_combat_modifier()
        if combat_type == 'attacking' or (self.is_safari and enemy.npmob_type == 'beast') or (self.is_battalion and not enemy.npmob_type == 'beast'):
            uses_minister = True
        else:
            uses_minister = False
        if self.veteran: #tells notifications how many of the currently selected mob's dice to show while rolling. Has 1 more die than usual because enemy also rolls
            num_dice = 3
        else:
            num_dice = 2

        text = ""
        text += "The " + self.name + " " + utility.conjugate('attempt', self.number) +" to defeat the " + enemy.name + ". /n /n"

        if self.veteran:
            if self.is_officer:
                text += "The " + self.name + " can roll twice and pick the higher result. /n"
            elif self.is_group:
                text += "The " + self.officer.name + " can roll twice and pick the higher result. /n"

        if self.is_battalion:
            if self.battalion_type == 'imperial':
                text += "Your professional imperial soldiers will receive a +2 bonus after their roll. /n"
            else:
                text += "Though your African soldiers are not accustomed to using modern equipment, they will receive a +1 bonus after their roll. /n"
        elif self.is_safari:
            if enemy.npmob_type == 'beast':
                text += "Your safari is trained in hunting beasts and will receive a +2 bonus after their roll. /n"
                own_combat_modifier += 3 #target-based modifiers not included in initial combat modifier calculation, cancels out -1 non-combat unit penalty
            else:
                text += "Your safari is not accustomed to conventional combat and will receive a -1 penalty after their roll. /n"
        elif self.is_officer:
            text += "As a lone officer, your " + self.name + " will receive a -2 penalty after their roll. /n"
        else:
            text += "As a non-military unit, your " + self.name + " will receive a -1 penalty after their roll. /n"
            
        if self.disorganized:
            text += "The " + self.name + " " + utility.conjugate('be', self.number) + " disorganized and will receive a -1 penalty after their roll. /n"
        elif enemy.disorganized:
            if enemy.npmob_type == 'beast':
                text += "The " + enemy.name + " " + utility.conjugate('be', enemy.number) + " injured and will receive a -1 after its roll. /n"
            else:
                text += "The " + enemy.name + " " + utility.conjugate('be', enemy.number) + " disorganized and will receive a -1 after their roll. /n"

        if enemy.npmob_type == 'beast' and not self.is_safari:
            text += "The " + self.name + " " + utility.conjugate('be', self.number) + " not trained in hunting beasts and will receive a -1 penalty after their roll. /n"
            own_combat_modifier -= 1


        if self.images[0].current_cell.has_intact_building('fort'):
            text += "The fort in this tile grants your " + self.name + " a +1 bonus after their roll. /n"
            own_combat_modifier += 1
            
        if self.veteran:
            text += "The outcome will be based on the difference between your highest roll and the enemy's roll. /n /n"
        else:
            text += "The outcome will be based on the difference between your roll and the enemy's roll. /n /n"

        notification_tools.display_notification(text + "Click to roll. ", 'combat', self.global_manager, num_dice)

        notification_tools.display_notification(text + "Rolling... ", 'roll', self.global_manager, num_dice)

        die_x = self.global_manager.get('notification_manager').notification_x - 140

        if self.veteran:
            if combat_type == 'attacking': #minister only involved in attacks
                if self.is_battalion:
                    cost_type = 'combat'
                elif self.is_safari:
                    cost_type = 'hunting'
                minister_rolls = self.controlling_minister.attack_roll_to_list(own_combat_modifier, enemy_combat_modifier, self.attack_cost, cost_type, num_dice - 1)
                enemy_roll = minister_rolls.pop(0) #first minister roll is for enemies
                results = minister_rolls
            #results = self.controlling_minister.roll_to_list(6, self.current_min_success, self.current_max_crit_fail, 2)
            elif (self.is_safari and enemy.npmob_type == 'beast') or (self.is_battalion and not enemy.npmob_type == 'beast'):
                results = [self.controlling_minister.no_corruption_roll(6), self.controlling_minister.no_corruption_roll(6)]
            else:
                results = [random.randrange(1, 7), random.randrange(1, 7)] #civilian ministers don't get to roll for combat with their units
            first_roll_list = dice_utility.combat_roll_to_list(6, "Combat roll", self.global_manager, results[0], own_combat_modifier)
            self.display_die((die_x, 440), first_roll_list[0], 0, 7, 0, False) #only 1 die needs uses_minister because only 1 minister portrait should be displayed
           
            second_roll_list = dice_utility.combat_roll_to_list(6, "second_combat", self.global_manager, results[1], own_combat_modifier)
            self.display_die((die_x - 120, 440), second_roll_list[0], 0, 7, 0, uses_minister) #die won't show result, so give inputs that make it green
                                
            text += (first_roll_list[1] + second_roll_list[1]) #add strings from roll result to text
            roll_result = max(first_roll_list[0], second_roll_list[0])
            result_outcome_dict = {}
            text += ("The higher result, " + str(roll_result + own_combat_modifier) + ", was used. /n")
        else:
            if combat_type == 'attacking': #minister only involved in attacks
                if self.is_battalion:
                    cost_type = 'combat'
                elif self.is_safari:
                    cost_type = 'hunting'
                minister_rolls = self.controlling_minister.attack_roll_to_list(own_combat_modifier, enemy_combat_modifier, self.attack_cost, cost_type, num_dice - 1)
                enemy_roll = minister_rolls.pop(0) #first minister roll is for enemies
                result = minister_rolls[0]
            elif (self.is_safari and enemy.npmob_type == 'beast') or (self.is_battalion and not enemy.npmob_type == 'beast'):
                result = self.controlling_minister.no_corruption_roll(6)
            else:
                result = random.randrange(1, 7)#self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail)
            roll_list = dice_utility.combat_roll_to_list(6, "Combat roll", self.global_manager, result, own_combat_modifier)
            self.display_die((die_x, 440), roll_list[0], 0, 7, 0, uses_minister) #die won't show result, so give inputs that make it green
            #(die_x, 440), roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail
                
            text += roll_list[1]
            roll_result = roll_list[0]

        own_roll = roll_result
        if not combat_type == 'attacking':
            enemy_roll = random.randrange(1, 7)

        text += "The enemy rolled a " + str(enemy_roll)
        if enemy_combat_modifier > 0:
            text += " + " + str(enemy_combat_modifier) + " = " + str(enemy_roll + enemy_combat_modifier)
        elif enemy_combat_modifier < 0:
            text += " - " + str(enemy_combat_modifier * -1) + " = " + str(enemy_roll + enemy_combat_modifier)
        text += ' /n'

        
        if num_dice == 2: #displays enemy dice
            self.display_die((die_x, 560), enemy_roll, 7, 7, 0, False) #die won't show result, so give inputs that make it red
        elif num_dice == 3:
            self.display_die((die_x - 60, 560), enemy_roll, 7, 7, 0, False) #die won't show result, so give inputs that make it red

        overall_result = own_roll + own_combat_modifier - (enemy_roll + enemy_combat_modifier)
        
        if overall_result <= -2:
            conclusion = 'lose'
            description = 'DEFEAT'
        elif overall_result <= 1:
            conclusion = 'draw'
            description = 'STALEMATE'
        else:
            conclusion = 'win'
            description = 'VICTORY'

        text += "Overall result: /n"
        text += str(own_roll + own_combat_modifier) + " - " + str(enemy_roll + enemy_combat_modifier) + " = " + str(overall_result) + ": " + description + " /n" #1 - 6 = -5: DEFEAT
        
        notification_tools.display_notification(text + "Click to continue.", 'combat', self.global_manager, num_dice)

        text += "/n"
        if conclusion == 'win':
            if combat_type == 'attacking':
                if enemy.npmob_type == 'beast':
                    text += "Your " + self.name + " tracked down and killed the " + enemy.name + ". /n /n"
                    self.public_opinion_increase = random.randrange(1, 7)
                    text += "Sensationalized stories of your safari's exploits and the death of the " + enemy.name + " increase public opinion by " + str(self.public_opinion_increase) + ". /n /n"
                else:
                    text += "Your " + self.name + " decisively defeated and destroyed the " + enemy.name + ". /n /n"
            elif combat_type == 'defending':
                if enemy.last_move_direction[0] > 0: #if enemy attacked by going east
                    retreat_direction = 'west'
                elif enemy.last_move_direction[0] < 0: #if enemy attacked by going west
                    retreat_direction = 'east'
                elif enemy.last_move_direction[1] > 0: #if enemy attacked by going north
                    retreat_direction = 'south'
                elif enemy.last_move_direction[1] < 0: #if enemy attacked by going south
                    retreat_direction = 'north'
                if enemy.npmob_type == 'beast':
                    text += "Your " + self.name + " injured and scared off the attacking " + enemy.name + ", which was seen running to the " + retreat_direction + " and will be vulnerable as it heals. /n /n"           
                else:
                    text += "Your " + self.name + " decisively routed the attacking " + enemy.name + ", who " + utility.conjugate('be', enemy.number, 'preterite') + " seen scattering to the " + retreat_direction
                    text += " and will be vulnerable to counterattack. /n /n"
            
        elif conclusion == 'draw':
            if combat_type == 'attacking':
                if enemy.npmob_type == 'beast':
                    text += "Your " + self.name + " failed to track the " + enemy.name + " to its lair and " + utility.conjugate('be', self.number, 'preterite') + " forced to withdraw. /n /n"
                else:
                    text += "Your " + self.name + " failed to push back the defending " + enemy.name + " and " + utility.conjugate('be', self.number, 'preterite') + " forced to withdraw. /n /n"
            if combat_type == 'defending':
                if enemy.last_move_direction[0] > 0: #if enemy attacked by going east
                    retreat_direction = 'west'
                elif enemy.last_move_direction[0] < 0: #if enemy attacked by going west
                    retreat_direction = 'east'
                elif enemy.last_move_direction[1] > 0: #if enemy attacked by going north
                    retreat_direction = 'south'
                elif enemy.last_move_direction[1] < 0: #if enemy attacked by going south
                    retreat_direction = 'north'
                if enemy.npmob_type == 'beast':
                    text += "Your " + self.name + " managed to scare off the attacking " + enemy.name + ", which was seen running to the " + retreat_direction + ". /n /n"           
                else:
                    text += "Your " + self.name + " managed to repel the attacking " + enemy.name + ", who " + utility.conjugate('be', enemy.number, 'preterite') + " seen withdrawing to the " + retreat_direction + ". /n /n"

        elif conclusion == 'lose':
            if combat_type == 'attacking':
                if enemy.npmob_type == 'beast':
                    text += "Your " + self.name + " were slowly picked off as they tracked the " + enemy.name + " to its lair. The survivors eventually fled in terror and will be vulnerable to counterattack. /n /n"
                else:
                    text += "The " + enemy.name + " decisively routed your " + self.name + ", who " + utility.conjugate('be', enemy.number) +"  scattered and will be vulnerable to counterattack. /n /n"
            elif combat_type == 'defending':
                if enemy.npmob_type == 'beast':
                    self.public_opinion_change = random.randrange(1, 4) * -1
                    if self.number == 1:
                        text += "The " + enemy.name + " slaughtered your " + self.name + ". /n /n"
                    else:
                        text += "The " + enemy.name + " slaughtered most of your " + self.name + " and the survivors deserted, promising to never return. /n /n"
                    killed_by_beast_flavor = ["Onlookers in Europe wonder how the world's greatest empire could be bested by mere beasts. /n /n",
                                              "Parliament concludes that its subsidies are being wasted on incompetents who can't deal with a few wild animals.",
                                              'Sensationalized news stories circulate of "brave conquerors" aimlessly wandering the jungle at the mercy of beasts, no better than savages.']
                    text += random.choice(killed_by_beast_flavor) + " Public opinion has decreased by " + str(self.public_opinion_change * -1) + ". /n /n"
                else:
                    self.public_opinion_change = random.randrange(-3, 4)
                    if self.number == 1:
                        text += "The " + enemy.name + " decisively defeated your " + self.name + ", who was either slain or captured. /n /n"
                    else:
                        text += "The " + enemy.name + " decisively defeated your " + self.name + ", who have all been slain or captured. /n /n"
                    if self.public_opinion_change > 0:
                        killed_by_natives_flavor = ["Onlookers in Europe rally in support of their beleaguered heroes overseas. /n /n",
                                                  "Parliament realizes that your company will require increased subsidies if these savages are to be shown their proper place.",
                                                  "Sensationalized news stories circulate of uungrateful savages attempting to resist their benevolent saviors."]
                        text += random.choice(killed_by_natives_flavor) + " Public opinion has increased by " + str(self.public_opinion_change) + ". /n /n"
                    elif self.public_opinion_change < 0:
                        killed_by_natives_flavor = ["Onlookers in Europe wonder how the world's greatest empire could be bested by mere savages. /n /n",
                                                  "Parliament concludes that its subsidies are being wasted on incompetents who can't deal with a few savages and considers lowering them in the future.",
                                                  "Sensationalized news stories circulate of indolent ministers sending the empire's finest to die in some jungle."]
                        text += random.choice(killed_by_natives_flavor) + " Public opinion has decreased by " + str(self.public_opinion_change * -1) + ". /n /n"
        if (not self.veteran) and own_roll >= 6 and ((self.is_battalion and not enemy.npmob_type == 'beast') or (self.is_safari and enemy.npmob_type == 'beast')): #civilian units can not become veterans through combat
            if self.is_battalion:
                self.just_promoted = True
                text += " This battalion's major is now a veteran. /n /n"  
            elif self.is_safari:
                self.just_promoted = True
                text += " This safari's hunter is now a veteran. /n /n"
        notification_tools.display_notification(text + " Click to remove this notification.", 'final_combat', self.global_manager)
        self.global_manager.set('combat_result', [self, conclusion])


    def complete_combat(self):
        '''
        Description:
            Used when the player finishes rolling for combat, shows the combat's results and makes any changes caused by the result. If attacking, outcomes include destroying the enemy unit, retreating, and retreating with a temporary
                debuff against counterattacks. If defending, outcomes include forcing enemy to retreat with a temporary debuff against counterattacks, forcing enemy to retreat, and being destroyed.
        Input:
            None
        Output:
            None
        '''
        combat_type = self.current_combat_type
        enemy = self.current_enemy
        conclusion = self.global_manager.get('combat_result')[1]
        if conclusion == 'win':
            if combat_type == 'attacking':
                if len(enemy.images[0].current_cell.contained_mobs) > 2: #len == 2 if only attacker and defender in tile
                    self.retreat() #attacker retreats in draw or if more defenders remaining
                elif self.is_battalion and self.images[0].current_cell.terrain == 'water': #if battalion attacks unit in water, it must retreat afterward
                    notification_tools.display_notification("While the attack was successful, this unit can not move freely through water and was forced to withdraw. /n /n",
                        'default', self.global_manager)
                    self.retreat()
                elif not self.movement_points + 1 >= self.get_movement_cost(0, 0, True): #if can't afford movement points to stay in attacked tile
                    notification_tools.display_notification("While the attack was successful, this unit did not have the " + str(self.get_movement_cost(0, 0, True)) + " movement points required to fully move into the attacked tile and was forced to withdraw. /n /n",
                        'default', self.global_manager)
                    self.retreat()
                enemy.die()
                if not enemy.npmob_type == 'beast':
                    self.global_manager.get('evil_tracker').change(8)
                else:
                    self.global_manager.get('public_opinion_tracker').change(self.public_opinion_increase)
            elif combat_type == 'defending':
                enemy.retreat()
                enemy.set_disorganized(True)
        elif conclusion == 'draw': #attacker retreats in draw or if more defenders remaining
            if combat_type == 'attacking':
                self.retreat()
                if not enemy.npmob_type == 'beast':
                    self.global_manager.get('evil_tracker').change(4)
            elif combat_type == 'defending':
                enemy.retreat()
        elif conclusion == 'lose':
            if combat_type == 'attacking':
                self.retreat()
                self.set_disorganized(True)
                if not enemy.npmob_type == 'beast':
                    self.global_manager.get('evil_tracker').change(4)
            elif combat_type == 'defending':
                current_cell = self.images[0].current_cell
                if len(current_cell.contained_mobs) > 2: #if len(self.grids[0].find_cell(self.x, self.y).contained_mobs) > 2: #if len(self.images[0].current_cell.contained_mobs) > 2:
                    enemy.retreat() #return to original tile if enemies still in other tile, can't be in tile with enemy units or have more than 1 offensive combat per turn
                self.die()
                if current_cell.get_best_combatant('pmob') == 'none':
                    enemy.kill_noncombatants()
                    enemy.damage_buildings()
                    if enemy.npmob_type == 'beast':
                        enemy.set_hidden(True)
                self.global_manager.get('public_opinion_tracker').change(self.public_opinion_change)

        if combat_type == 'attacking':
            self.set_movement_points(0)
        
        if self.just_promoted:
            self.promote()
            
        self.global_manager.set('ongoing_combat', False)
        if len(self.global_manager.get('attacker_queue')) > 0:
            self.global_manager.get('attacker_queue').pop(0).attempt_local_combat()
        elif self.global_manager.get('enemy_combat_phase'): #if enemy combat phase done, go to player turn
            turn_management_tools.start_player_turn(self.global_manager)

    def start_construction(self, building_info_dict):
        '''
        Description
            Used when the player clicks on a construct building or train button, displays a choice notification that allows the player to construct it or not. Choosing to construct starts the construction process, costs an amount based
                on the building built, and consumes the group's movement points
        Input:
            dictionary building_info_dict: string keys corresponding to various values used to determine the building constructed
                string building_type: type of building, like 'resource'
                string building_name: name of building, like 'ivory camp'
                string attached_resource: optional, type of resource building produces, like 'ivory'
        Output:
            None
        '''
        self.building_type = building_info_dict['building_type']
        self.building_name = building_info_dict['building_name']
        if self.building_type == 'resource':
            self.attached_resource = building_info_dict['attached_resource']
        else:
            self.attached_resource = ''
        
        self.current_roll_modifier = 0
        self.current_min_success = self.default_min_success
        self.current_max_crit_fail = 0 #construction shouldn't have critical failures
        self.current_min_crit_success = self.default_min_crit_success
        
        self.current_min_success -= self.current_roll_modifier #positive modifier reduces number required for succcess, reduces maximum that can be crit fail
        self.current_max_crit_fail -= self.current_roll_modifier
        if self.current_min_success > self.current_min_crit_success:
            self.current_min_crit_success = self.current_min_success #if 6 is a failure, should not be critical success. However, if 6 is a success, it will always be a critical success
        choice_info_dict = {'constructor': self, 'type': 'start construction'}
        self.global_manager.set('ongoing_construction', True)
        message = "Are you sure you want to start constructing a " + self.building_name + "? /n /n"
        
        cost = actor_utility.get_building_cost(self.global_manager, self, self.building_type, self.building_name)

        message += "The planning and materials will cost " + str(cost) + " money. /n /n"
        
        message += "If successful, a " + self.building_name + " will be built. " #change to match each building
        if self.building_type == 'resource':
            message += "A " + self.building_name + " expands the tile's warehouse capacity, and each work crew attached to it can attempt to produce " + self.attached_resource + " each turn. /n /n"
            message += "Upgrades to the " + self.building_name + " can increase the maximum number of work crews attached and/or how much " + self.attached_resource + " each attached work crew can attempt to produce each turn. "
        elif self.building_type == 'infrastructure':
            if self.building_name == 'road':
                message += "A road halves movement cost when moving to another tile that has a road or railroad and can later be upgraded to a railroad. "
            elif self.building_name == 'railroad':
                message += "A railroad, like a road, halves movement cost when moving to another tile that has a road or railroad. "
                message += "It is also required for trains to move and for a train station to be built."
        elif self.building_type == 'port':
            message += "A port allows steamboats and steamships to enter the tile and expands the tile's warehouse capacity. "
            if self.y == 1:
                message += "/n /nThis port would be adjacent to the ocean, allowing it to be used as a destination or starting point for steamships traveling between theatres. "
            else:
                message += "/n /nThis port would not be adjacent to the ocean. "
                
            if self.adjacent_to_river():
                message += "/n /nThis port would be adjacent to a river, allowing steamboats to be built there. "
            else:
                message += "/n /nThis port would not be adjacent to a river."
        elif self.building_type == 'train_station':
            message += "A train station is required for a train to exchange cargo and passengers, allows trains to be built, and expands the tile's warehouse capacity"
        elif self.building_type == 'trading_post':
            message += "A trading post increases the likelihood that the natives of the local village will be willing to trade and reduces the risk of hostile interactions when trading."
        elif self.building_type == 'mission':
            message += "A mission decreases the difficulty of converting the natives of the local village and reduces the risk of hostile interactions when converting."
        elif self.building_type == 'fort':
            message += "A fort increases the combat effectiveness of your units standing in this tile."
        elif self.building_type == 'train':
            message += "A train is a unit that can carry commodities and passengers at very high speed along railroads. It can only exchange cargo and passengers at a train station. "
            message += "It also requires an attached worker as crew to function."
        elif self.building_type == 'steamboat':
            message += "A steamboat is a unit that can carry commodities and passengers at high speed along rivers. "
            message += "It also requires an attached worker as crew to function."
        else:
            message += "Placeholder building description"
        message += " /n /n"
            
        notification_tools.display_choice_notification(message, ['start construction', 'stop construction'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager
        
    def construct(self):
        '''
        Description:
            Controls the construction process, determining and displaying its result through a series of notifications
        Input:
            None
        Output:
            None
        '''
        self.current_construction_type = 'default'
        roll_result = 0
        self.just_promoted = False
        self.set_movement_points(0)
        if self.veteran: #tells notifications how many of the currently selected mob's dice to show while rolling
            num_dice = 2
        else:
            num_dice = 1
            
        cost = actor_utility.get_building_cost(self.global_manager, self, self.building_type, self.building_name)

        if self.building_name in ['train', 'steamboat']:
            verb = 'assemble'
            preterit_verb = 'assembled'
            noun = 'assembly'
        else:
            verb = 'construct'
            preterit_verb = 'constructed'
            noun = 'construction'

        self.global_manager.get('money_tracker').change(-1 * cost, 'construction')
        text = ""

        text += "The " + self.name + " attempts to " + verb + " a " + self.building_name + ". /n /n"
        if not self.veteran:    
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required to succeed.", 'construction', self.global_manager, num_dice)
        else:
            text += ("The " + self.officer.name + " can roll twice and pick the higher result. /n /n")
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required on at least 1 die to succeed.", 'construction', self.global_manager, num_dice)

        notification_tools.display_notification(text + "Rolling... ", 'roll', self.global_manager, num_dice)

        die_x = self.global_manager.get('notification_manager').notification_x - 140

        if self.veteran:
            results = self.controlling_minister.roll_to_list(6, self.current_min_success, self.current_max_crit_fail, cost, 'construction', 2)
            #result = self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail)
            first_roll_list = dice_utility.roll_to_list(6, noun.capitalize() + " roll", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, results[0])
            self.display_die((die_x, 500), first_roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)

            #result = self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail)
            second_roll_list = dice_utility.roll_to_list(6, "second", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, results[1])
            self.display_die((die_x, 380), second_roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, False)
                                
            text += (first_roll_list[1] + second_roll_list[1]) #add strings from roll result to text
            roll_result = max(first_roll_list[0], second_roll_list[0])
            result_outcome_dict = {}
            for i in range(1, 7):
                if i <= self.current_max_crit_fail:
                    word = "CRITICAL FAILURE"
                elif i >= self.current_min_crit_success:
                    word = "CRITICAL SUCCESS"
                elif i >= self.current_min_success:
                    word = "SUCCESS"
                else:
                    word = "FAILURE"
                result_outcome_dict[i] = word
            text += ("The higher result, " + str(roll_result) + ": " + result_outcome_dict[roll_result] + ", was used. /n")
        else:
            result = self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail, cost, 'construction')
            roll_list = dice_utility.roll_to_list(6, noun.capitalize() + " roll", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, result)
            self.display_die((die_x, 440), roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)
                
            text += roll_list[1]
            roll_result = roll_list[0]

        notification_tools.display_notification(text + "Click to continue.", 'construction', self.global_manager, num_dice)
            
        text += "/n"
        if roll_result >= self.current_min_success:
            text += "The " + self.name + " successfully " + preterit_verb + " the " + self.building_name + ". /n"
        else:
            text += "Little progress was made and the " + self.officer.name + " requests more time and funds to complete the " + noun + " of the " + self.building_name + ". /n"

        if (not self.veteran) and roll_result >= self.current_min_crit_success:
            self.just_promoted = True
            text += " /nThe " + self.officer.name + " managed the " + noun + " well enough to become a veteran. /n"
        if roll_result >= 4:
            notification_tools.display_notification(text + " /nClick to remove this notification.", 'final_construction', self.global_manager)
        else:
            notification_tools.display_notification(text, 'default', self.global_manager)
        self.global_manager.set('construction_result', [self, roll_result])
        
    def complete_construction(self):
        '''
        Description:
            Used when the player finishes rolling for construction, shows the construction's results and makes any changes caused by the result. If successful, the building is constructed, promotes engineer to a veteran on critical
                success
        Input:
            None
        Output:
            None
        '''
        roll_result = self.global_manager.get('construction_result')[1]
        if roll_result >= self.current_min_success: #if campaign succeeded
            if roll_result >= self.current_min_crit_success and not self.veteran:
                self.promote()
            self.set_movement_points(0)

            input_dict = {}
            input_dict['coordinates'] = (self.x, self.y)
            input_dict['grids'] = self.grids
            input_dict['name'] = self.building_name
            input_dict['modes'] = ['strategic']
            input_dict['init_type'] = self.building_type
            if not self.building_type in ['train', 'steamboat']:
                if self.images[0].current_cell.has_building(self.building_type): #if building of same type exists, remove it and replace with new one
                    self.images[0].current_cell.get_building(self.building_type).remove()
            if self.building_type == 'resource':
                input_dict['image'] = self.global_manager.get('resource_building_dict')[self.attached_resource]
                input_dict['resource_type'] = self.attached_resource
            elif self.building_type == 'infrastructure':
                building_image_id = 'none'
                if self.building_name == 'road':
                    building_image_id = 'buildings/infrastructure/road.png'
                elif self.building_name == 'railroad':
                    building_image_id = 'buildings/infrastructure/railroad.png'
                input_dict['image'] = building_image_id
                input_dict['infrastructure_type'] = self.building_name
            elif self.building_type == 'port':
                input_dict['image'] = 'buildings/port.png'
            elif self.building_type == 'train_station':
                input_dict['image'] = 'buildings/train_station.png'
            elif self.building_type == 'trading_post':
                input_dict['image'] = 'buildings/trading_post.png'
            elif self.building_type == 'mission':
                input_dict['image'] = 'buildings/mission.png'
            elif self.building_type == 'fort':
                input_dict['image'] = 'buildings/fort.png'
            elif self.building_type == 'train':
                image_dict = {'default': 'mobs/train/crewed.png', 'crewed': 'mobs/train/crewed.png', 'uncrewed': 'mobs/train/uncrewed.png'}
                input_dict['image_dict'] = image_dict
                input_dict['crew'] = 'none'
            elif self.building_type == 'steamboat':
                image_dict = {'default': 'mobs/steamboat/crewed.png', 'crewed': 'mobs/steamboat/crewed.png', 'uncrewed': 'mobs/steamboat/uncrewed.png'}
                input_dict['image_dict'] = image_dict
                input_dict['crew'] = 'none'
                input_dict['init_type'] = 'boat'
            else:
                input_dict['image'] = 'buildings/' + self.building_type + '.png'
            new_building = self.global_manager.get('actor_creation_manager').create(False, input_dict, self.global_manager)

            if self.building_type in ['port', 'train_station', 'resource']:
                warehouses = self.images[0].current_cell.get_building('warehouses')
                if not warehouses == 'none':
                    if warehouses.damaged:
                        warehouses.set_damaged(False)
                    warehouses.upgrade()
                else:
                    input_dict['image'] = 'misc/empty.png'
                    input_dict['name'] = 'warehouses'
                    input_dict['init_type'] = 'warehouses'
                    self.global_manager.get('actor_creation_manager').create(False, input_dict, self.global_manager)
                    
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.images[0].current_cell.tile) #update tile display to show new building
            if self.building_type in ['steamboat', 'train']:
                new_building.move_to_front()
                new_building.select()
            else:
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #update mob display to show new upgrade possibilities
        self.global_manager.set('ongoing_construction', False)

    def display_die(self, coordinates, result, min_success, min_crit_success, max_crit_fail, uses_minister = True):
        '''
        Description:
            Creates a die object at the inputted location and predetermined roll result to use for multi-step notification dice rolls. Also shows a picture of the minister controlling the roll. The color of the die's outline depends on
                the result
        Input:
            int tuple coordinates: Two values representing x and y pixel coordinates for the bottom left corner of the die
            int result: Predetermined result that the die will end on after rolling
            int min_success: Minimum roll required for a success
            int min_crit_success: Minimum roll required for a critical success
            int max_crit_fail: Maximum roll required for a critical failure
            boolean uses_minister = True: Determines if the roll is controlled by a minister and whether a minister portrait should be shown during the roll
        Output:
            None
        '''
        result_outcome_dict = {'min_success': min_success, 'min_crit_success': min_crit_success, 'max_crit_fail': max_crit_fail}
        outcome_color_dict = {'success': 'dark green', 'fail': 'dark red', 'crit_success': 'bright green', 'crit_fail': 'bright red', 'default': 'black'}
        new_die = dice.die(scaling.scale_coordinates(coordinates[0], coordinates[1], self.global_manager), scaling.scale_width(100, self.global_manager), scaling.scale_height(100, self.global_manager), self.modes, 6,
            result_outcome_dict, outcome_color_dict, result, self.global_manager)
        self.attached_dice_list.append(new_die)
        if uses_minister:
            if self.global_manager.get('ongoing_combat'): #combat has a different dice layout
                minister_icon_coordinates = (coordinates[0] - 120, coordinates[1] + 5)
            else:
                minister_icon_coordinates = (coordinates[0], coordinates[1] + 120)
            minister_position_icon = images.dice_roll_minister_image(scaling.scale_coordinates(minister_icon_coordinates[0], minister_icon_coordinates[1], self.global_manager), scaling.scale_width(100, self.global_manager), scaling.scale_height(100, self.global_manager), self.modes, self.controlling_minister,
                'position', self.global_manager)
            minister_portrait_icon = images.dice_roll_minister_image(scaling.scale_coordinates(minister_icon_coordinates[0], minister_icon_coordinates[1], self.global_manager), scaling.scale_width(100, self.global_manager), scaling.scale_height(100, self.global_manager), self.modes, self.controlling_minister,
                'portrait', self.global_manager)
        
    def start_repair(self, building_info_dict):
        '''
        Description
            Used when the player clicks on a repair building button, displays a choice notification that allows the player to repair it or not. Choosing to repair starts the repair process, costs an amount based on the building's total
                cost with upgrades, and consumes the construction gang's movement points
        Input:
            dictionary building_info_dict: string keys corresponding to various values used to determine the building constructed
                string building_type: type of building to repair, like 'resource'
                string building_name: name of building, like 'ivory camp'
        Output:
            None
        '''
        self.building_type = building_info_dict['building_type']
        self.building_name = building_info_dict['building_name']
        self.repaired_building = self.images[0].current_cell.get_building(self.building_type)
        
        self.current_roll_modifier = 0
        self.current_min_success = self.default_min_success - 1 #easier than building new building
        self.current_max_crit_fail = 0 #construction shouldn't have critical failures
        self.current_min_crit_success = self.default_min_crit_success
        
        self.current_min_success -= self.current_roll_modifier #positive modifier reduces number required for succcess, reduces maximum that can be crit fail
        self.current_max_crit_fail -= self.current_roll_modifier
        if self.current_min_success > self.current_min_crit_success:
            self.current_min_crit_success = self.current_min_success #if 6 is a failure, should not be critical success. However, if 6 is a success, it will always be a critical success
        choice_info_dict = {'constructor': self, 'type': 'start repair'}
        self.global_manager.set('ongoing_construction', True)
        message = "Are you sure you want to start repairing the " + self.building_name + "? /n /n"
        message += "The planning and materials will cost " + str(self.repaired_building.get_repair_cost()) + " money, half the initial cost of the building's construction. /n /n"
        message += "If successful, the " + self.building_name + " will be restored to full functionality. /n /n"
            
        notification_tools.display_choice_notification(message, ['start repair', 'stop repair'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager

    def repair(self):
        '''
        Description:
            Controls the repair process, determining and displaying its result through a series of notifications
        Input:
            None
        Output:
            None
        '''
        self.current_construction_type = 'repair'
        roll_result = 0
        self.just_promoted = False
        self.set_movement_points(0)

        if self.veteran: #tells notifications how many of the currently selected mob's dice to show while rolling
            num_dice = 2
        else:
            num_dice = 1
        
        self.global_manager.get('money_tracker').change(self.repaired_building.get_repair_cost() * -1, 'construction')
        text = ""
        text += "The " + self.name + " attempts to repair the " + self.building_name + ". /n /n"
        if not self.veteran:    
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required to succeed.", 'construction', self.global_manager, num_dice)
        else:
            text += ("The " + self.officer.name + " can roll twice and pick the higher result. /n /n")
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required on at least 1 die to succeed.", 'construction', self.global_manager, num_dice)

        notification_tools.display_notification(text + "Rolling... ", 'roll', self.global_manager, num_dice)

        die_x = self.global_manager.get('notification_manager').notification_x - 140

        if self.veteran:
            results = self.controlling_minister.roll_to_list(6, self.current_min_success, self.current_max_crit_fail, self.repaired_building.get_repair_cost(), 'construction', 2)
            first_roll_list = dice_utility.roll_to_list(6, "Construction roll", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, results[0])
            self.display_die((die_x, 500), first_roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)

            second_roll_list = dice_utility.roll_to_list(6, "second", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, results[1])
            self.display_die((die_x, 380), second_roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, False)
                                
            text += (first_roll_list[1] + second_roll_list[1]) #add strings from roll result to text
            roll_result = max(first_roll_list[0], second_roll_list[0])
            result_outcome_dict = {}
            for i in range(1, 7):
                if i <= self.current_max_crit_fail:
                    word = "CRITICAL FAILURE"
                elif i >= self.current_min_crit_success:
                    word = "CRITICAL SUCCESS"
                elif i >= self.current_min_success:
                    word = "SUCCESS"
                else:
                    word = "FAILURE"
                result_outcome_dict[i] = word
            text += ("The higher result, " + str(roll_result) + ": " + result_outcome_dict[roll_result] + ", was used. /n")
        else:
            result = self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail, self.repaired_building.get_repair_cost(), 'construction')
            roll_list = dice_utility.roll_to_list(6, "Construction roll", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, result)
            self.display_die((die_x, 440), roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)
                
            text += roll_list[1]
            roll_result = roll_list[0]

        notification_tools.display_notification(text + "Click to continue.", 'construction', self.global_manager, num_dice)
            
        text += "/n"
        if roll_result >= self.current_min_success: #3+ required on D6 for repair
            text += "The " + self.name + " successfully repaired the " + self.building_name + ". /n"
        else:
            text += "Little progress was made and the " + self.officer.name + " requests more time and funds to complete the repair. /n"

        if (not self.veteran) and roll_result >= self.current_min_crit_success:
            self.just_promoted = True
            text += " /nThe " + self.officer.name + " managed the construction well enough to become a veteran. /n"
        if roll_result >= 4:
            notification_tools.display_notification(text + " /nClick to remove this notification.", 'final_construction', self.global_manager)
        else:
            notification_tools.display_notification(text, 'default', self.global_manager)
        self.global_manager.set('construction_result', [self, roll_result])  

    def complete_repair(self):
        '''
        Description:
            Used when the player finishes rolling for a repair, shows the repair's results and makes any changes caused by the result. If successful, the building is repaired and returned to full functionality, promotes engineer to a
                veteran on critical success
        Input:
            None
        Output:
            None
        '''
        roll_result = self.global_manager.get('construction_result')[1]
        if roll_result >= self.current_min_success: #if repair succeeded
            if roll_result >= self.current_min_crit_success and not self.veteran:
                self.promote()
            self.set_movement_points(0)
            self.repaired_building.set_damaged(False)
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.images[0].current_cell.tile) #update tile display to show repaired building
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #update mob info display to hide repair button
        self.global_manager.set('ongoing_construction', False)
