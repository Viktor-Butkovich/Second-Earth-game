#Contains functionality for vehicle units

import random

from .pmobs import pmob
from .. import text_tools
from .. import utility
from .. import actor_utility
from .. import main_loop_tools
from .. import notification_tools
from ..buttons import button

class vehicle(pmob):
    '''
    pmob that requires an attached worker to function and can carry other mobs as passengers
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
                'image_dict': string/string dictionary value - dictionary of image type keys and file path values to the images used by this object in various situations, such as 'crewed': 'crewed_ship.png'
                'name': string value - Required if from save, this mob's name
                'modes': string list value - Game modes during which this mob's images can appear
                'end_turn_destination': string or int tuple value - Required if from save, 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'max_movement_points': int value - Required if from save, maximum number of movement points this mob can have
                'crew': worker, string, or dictionary value - If no crew, equals 'none'. Otherwise, if creating a new vehicle, equals a worker that serves as crew. If loading, equals a dictionary of the saved information necessary to
                    recreate the worker to serve as crew
                'passenger_dicts': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each of this vehicle's passengers
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.initializing = True #when pmobs embark a vehicle, the vehicle is selected if the vehicle is not initializing
        self.vehicle_type = 'vehicle'
        self.has_crew = False
        input_dict['image'] = input_dict['image_dict']['default']
        self.contained_mobs = []
        self.ejected_crew = 'none'
        self.ejected_passengers = []
        self.travel_possible = False
        super().__init__(from_save, input_dict, global_manager)
        self.image_dict = input_dict['image_dict'] #should have default and uncrewed
        self.is_vehicle = True
        if not from_save:
            self.crew = input_dict['crew']
            if self.crew == 'none':
                self.has_crew = False
                self.set_image('uncrewed')
            else:
                self.has_crew = True
                self.set_image('uncrewed')
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #updates mob info display list to account for is_vehicle changing
            self.selection_sound()
        else: #create crew and passengers through recruitment_manager and embark them
            if input_dict['crew'] == 'none':
                self.crew = 'none'
            else:
                self.global_manager.get('actor_creation_manager').create(True, input_dict['crew'], self.global_manager).crew_vehicle(self) #creates worker and merges it as crew
            for current_passenger in input_dict['passenger_dicts']:
                self.global_manager.get('actor_creation_manager').create(True, current_passenger, self.global_manager).embark_vehicle(self) #create passengers and merge as passengers
        self.initializing = False
        self.set_controlling_minister_type(self.global_manager.get('type_minister_dict')['transportation'])
        if not self.has_crew:
            self.remove_from_turn_queue()

    def manage_health_attrition(self, current_cell = 'default'):
        '''
        Description:
            Checks this mob, its, crew, and its passengers for health attrition each turn
        Input:
            string/cell current_cell = 'default': Records which cell the attrition is taking place in, used when a unit is in a building or another mob and does not technically exist in any cell
        Output:
            None
        '''
        if current_cell == 'default':
            current_cell = self.images[0].current_cell
        if self.crew == 'none':
            sub_mobs = []
        else:
            sub_mobs = [self.crew]
        sub_mobs += self.contained_mobs

        transportation_minister = self.global_manager.get('current_ministers')[self.global_manager.get('type_minister_dict')['transportation']]
        
        for current_sub_mob in sub_mobs:
            worker_type = 'none'
            if current_sub_mob.is_worker:
                worker_type = current_sub_mob.worker_type
            elif current_sub_mob.is_group:
                worker_type = current_sub_mob.worker.worker_type
            if current_cell.local_attrition() and random.randrange(1, 7) >= 4: #vehicle removes 1/2 of attrition, slightly less than forts, ports, etc.
                if transportation_minister.no_corruption_roll(6) == 1 or self.global_manager.get('DEBUG_boost_attrition'):
                    if (not worker_type in ['African', 'slave']) or random.randrange(1, 7) == 1: #only 1/6 chance of continuing attrition for African workers, others automatically continue
                        if current_sub_mob == self.crew:
                            self.crew_attrition_death()
                        elif current_sub_mob.is_group:
                            current_sub_mob.attrition_death(random.choice(['officer', 'worker']))
                        else:
                            text = "The " + current_sub_mob.name + " aboard the " + self.name + " at (" + str(self.x) + ", " + str(self.y) + ") have died from attrition. /n /n "
                            text += "The " + current_sub_mob.name + " will remain inactive for the next turn as replacements are found."
                            current_sub_mob.replace()
                            current_sub_mob.temp_disable_movement()
                            notification_tools.display_zoom_notification(text, self, self.global_manager)
                        
    def crew_attrition_death(self):
        '''
        Description:
            Resolves the vehicle's crew dying from attrition, preventing the ship from moving in the next turn and automatically recruiting a new worker
        Input:
            None
        Output:
            None
        '''
        self.global_manager.get('evil_tracker').change(3)
        text = "The " + self.crew.name + " crewing the " + self.name + " at (" + str(self.x) + ", " + str(self.y) + ") have died from attrition. /n /n "
        text += "The " + self.name + " will remain inactive for the next turn as replacements are found."
        self.crew.replace(self)
        notification_tools.display_zoom_notification(text, self, self.global_manager)
        self.temp_disable_movement()


    def move(self, x_change, y_change):
        '''
        Description:
            Moves this mob x_change to the right and y_change upward, also making sure to update the positions of the vehicle's crew and passengers
        Input:
            int x_change: How many cells are moved to the right in the movement
            int y_change: How many cells are moved upward in the movement
        Output:
            None
        '''
        super().move(x_change, y_change)
        self.calibrate_sub_mob_positions()

    def calibrate_sub_mob_positions(self):
        '''
        Description:
            Updates the positions of this mob's submobs (mobs inside of a building or other mob that are not able to be independently viewed or selected) to match this mob
        Input:
            None
        Output:
            None
        '''
        for current_passenger in self.contained_mobs:
            current_passenger.x = self.x
            current_passenger.y = self.y
            if current_passenger.is_group:
                current_passenger.calibrate_sub_mob_positions()
        if not self.crew == 'none':
            self.crew.x = self.x
            self.crew.y = self.y

    def eject_crew(self):
        '''
        Description:
            Removes this vehicle's crew
        Input:
            None
        Output:
            None
        '''
        if self.has_crew:
            self.ejected_crew = self.crew
            self.crew.uncrew_vehicle(self)
            
    def eject_passengers(self):
        '''
        Description:
            Removes this vehicle's passengers
        Input:
            None
        Output:
            None
        '''
        while len(self.contained_mobs) > 0:
            current_mob = self.contained_mobs.pop(0)
            current_mob.disembark_vehicle(self)
            if (not self.global_manager.get('player_turn')) or self.global_manager.get('enemy_combat_phase'):
                self.ejected_passengers.append(current_mob)

    def reembark(self):
        '''
        Description:
            After combat is finished, reembarks any surviving crew or passengers onto this vehicle, if possible
        Input:
            None
        Output:
            None
        '''
        if not self.ejected_crew == 'none':
            if self.ejected_crew in self.global_manager.get('pmob_list'): #not self.ejected_crew.dead:
                self.ejected_crew.crew_vehicle(self)
                for current_passenger in self.ejected_passengers:
                    if current_passenger in self.global_manager.get('pmob_list'): #not current_passenger.dead:
                        current_passenger.embark_vehicle(self)
            self.ejected_crew = 'none'
            self.ejected_passengers = []
        
    def die(self):
        '''
        Description:
            Removes this object from relevant lists, prevents it from further appearing in or affecting the program, deselects it, and drops any commodities it is carrying. Also removes all of this vehicle's passengers
        Input:
            None
        Output:
            None
        '''
        super().die()
        for current_passenger in self.contained_mobs:
            current_passenger.die()
        self.contained_mobs = []
        if not self.crew == 'none':
            self.crew.die()
            self.crew = 'none'

    def fire(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. Also fires this vehicle's crew and passengers
        Input:
            None
        Output:
            None
        '''
        for current_passenger in self.contained_mobs:
            current_passenger.fire()
        self.contained_mobs = []
        if not self.crew == 'none':
            self.crew.fire()
            self.crew = 'none'
        super().fire()

    def to_save_dict(self):
        '''
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                Along with superclass outputs, also saves the following values:
                'image_dict': string value - dictionary of image type keys and file path values to the images used by this object in various situations, such as 'crewed': 'crewed_ship.png'
                'crew': string or dictionary value - If no crew, equals 'none'. Otherwise, equals a dictionary of the saved information necessary to recreate the worker to serve as crew
                'passenger_dicts': dictionary list value - list of dictionaries of saved information necessary to recreate each of this vehicle's passengers
        '''
        save_dict = super().to_save_dict()
        save_dict['image_dict'] = self.image_dict
        if self.crew == 'none':
            save_dict['crew'] = 'none'
        else:
            save_dict['crew'] = self.crew.to_save_dict()
        save_dict['passenger_dicts'] = [] #list of dictionaries for each passenger, on load a vehicle creates all of its passengers and embarks them
        for current_mob in self.contained_mobs:
            save_dict['passenger_dicts'].append(current_mob.to_save_dict())
        return(save_dict)

    def can_move(self, x_change, y_change, can_print = True):
        '''
        Description:
            Returns whether this mob can move to the tile x_change to the right of it and y_change above it. Movement can be prevented by not being able to move on water/land, the edge of the map, limited movement points, etc. Vehicles
                are not able to move without a crew
        Input:
            int x_change: How many cells would be moved to the right in the hypothetical movement
            int y_change: How many cells would be moved upward in the hypothetical movement
            boolean can_print = True: Whether to print messages to explain why a unit can't move in a certain direction
        Output:
            boolean: Returns True if this mob can move to the proposed destination, otherwise returns False
        '''
        if self.has_crew:
            if not self.temp_movement_disabled:
                return(super().can_move(x_change, y_change, can_print))
            else:
                if can_print:
                    text_tools.print_to_screen("This " + self.name + " is still having its crew replaced and can not move this turn.", self.global_manager)
        else:
            if can_print:
                text_tools.print_to_screen("A " + self.vehicle_type + " can not move without crew.", self.global_manager)
            return(False)

    def go_to_grid(self, new_grid, new_coordinates):
        '''
        Description:
            Links this vehicle to a grid, causing it to appear on that grid and its minigrid at certain coordinates. Used when crossing the ocean. Also moves this vehicle's crew and its passengers
        Input:
            grid new_grid: grid that this vehicle is linked to
            int tuple new_coordinates: Two values representing x and y coordinates to start at on the inputted grid
        Output:
            None
        '''
        super().go_to_grid(new_grid, new_coordinates)
        for current_mob in (self.contained_mobs + [self.crew]): #make list of all mobs in vehicle
            current_mob.go_to_grid(new_grid, new_coordinates)
            current_mob.in_vehicle = True
            current_mob.selected = False
            current_mob.hide_images()
        if new_grid == self.global_manager.get('europe_grid') or self.images[0].current_cell.has_intact_building('port'):
            self.eject_passengers()
            self.drop_inventory()
        elif new_grid == self.global_manager.get('slave_traders_grid'):
            self.eject_passengers()

class train(vehicle):
    '''
    Vehicle that can only move along railroads, has large inventory capacity, and has 10 movement points
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
                'image_dict': string/string dictionary value - dictionary of image type keys and file path values to the images used by this object in various situations, such as 'crewed': 'crewed_ship.png'
                'name': string value - Required if from save, this mob's name
                'modes': string list value - Game modes during which this mob's images can appear
                'end_turn_destination': string or int tuple value - Required if from save, 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'crew': worker, string, or dictionary value - If no crew, equals 'none'. Otherwise, if creating a new vehicle, equals a worker that serves as crew. If loading, equals a dictionary of the saved information necessary to
                    recreate the worker to serve as crew
                'passenger_dicts': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each of this vehicle's passengers
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(from_save, input_dict, global_manager)
        self.set_max_movement_points(16)
        self.has_infinite_movement = False
        #self.has_infinite_movement = True
        self.vehicle_type = 'train'
        self.can_swim = False
        self.can_walk = True
        self.can_hold_commodities = True
        self.inventory_capacity = 27#9
        if not from_save:
            self.inventory_setup()
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self)
        else:
            self.load_inventory(input_dict['inventory'])

    def can_move(self, x_change, y_change, can_print = True):
        '''
        Description:
            Returns whether this mob can move to the tile x_change to the right of it and y_change above it. Movement can be prevented by not being able to move on water/land, the edge of the map, limited movement points, etc. Vehicles
                are not able to move without a crew. Trains can only move along railroads
        Input:
            int x_change: How many cells would be moved to the right in the hypothetical movement
            int y_change: How many cells would be moved upward in the hypothetical movement
            boolean can_print = True: Whether to print messages to explain why a unit can't move in a certain direction
        Output:
            boolean: Returns True if this mob can move to the proposed destination, otherwise returns False
        '''
        result = super().can_move(x_change, y_change, can_print)
        if result:
            if not (self.images[0].current_cell.has_intact_building('railroad') and self.grids[0].find_cell(self.x + x_change, self.y + y_change).has_intact_building('railroad')):
                if can_print:
                    text_tools.print_to_screen("Trains can only move along railroads.", self.global_manager)
                return(False)
        return(result)

    def get_movement_cost(self, x_change, y_change):
        '''
        Description:
            Returns the cost in movement points of moving by the inputted amounts. Unlike most pmobs, trains use their default movement cost to move to all railroad tiles
        Input:
            int x_change: How many cells would be moved to the right in the hypothetical movement
            int y_change: How many cells would be moved upward in the hypothetical movement
        Output:
            double: How many movement points would be spent by moving by the inputted amount
        '''
        return(self.movement_cost)

class ship(vehicle):
    '''
    Vehicle that can only move in ocean water and into ports, can cross the ocean, has large inventory capacity, and has infinite movement points
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
                'image_dict': string/string dictionary value - dictionary of image type keys and file path values to the images used by this object in various situations, such as 'crewed': 'crewed_ship.png'
                'name': string value - Required if from save, this mob's name
                'modes': string list value - Game modes during which this mob's images can appear
                'end_turn_destination': string or int tuple value - Required if from save, 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'crew': worker, string, or dictionary value - If no crew, equals 'none'. Otherwise, if creating a new vehicle, equals a worker that serves as crew. If loading, equals a dictionary of the saved information necessary to
                    recreate the worker to serve as crew
                'passenger_dicts': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each of this vehicle's passengers
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(from_save, input_dict, global_manager)
        self.set_max_movement_points(10)
        self.has_infinite_movement = True
        self.vehicle_type = 'ship'
        self.can_swim = True
        self.can_swim_river = False
        self.can_swim_ocean = True
        self.can_walk = False
        self.travel_possible = True #if this mob would ever be able to travel
        self.can_hold_commodities = True
        self.inventory_capacity = 27
        #if self.images[0].image_id in ['mobs/steamboat/default.png', 'mobs/steamboat/crewed.png', 'mobs/steamboat/uncrewed.png']:
        #    self.can_swim_river = True
        if not from_save:
            self.inventory_setup()
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #updates mob info display list to account for travel_possible changing
        else:
            self.load_inventory(input_dict['inventory'])

    def can_leave(self):
        '''
        Description:
            Returns whether this mob is allowed to move away from its current cell. A ship can not move away when there are any mobs in its tile that can not move on water and are not in a ship, preventing ships from leaving behind
                disembarking passengers
        Input:
            None
        Output:
            boolean: Returns False if this ship is in a water tile and there are any mobs in its tile that can not move on water and are not in a ship, otherwise returns True
        '''
        if self.images[0].current_cell.terrain == 'water':
            for current_mob in self.images[0].current_cell.contained_mobs:
                if current_mob.controllable and not current_mob.can_swim: #should change to check if current mob can swim in current type of water, ocean or river
                    text_tools.print_to_screen("A " + self.vehicle_type + " can not leave without taking unaccompanied units as passengers.", self.global_manager)
                    return(False)
        return(True)

    def can_travel(self): 
        '''
        Description:
            Returns whether this ship can cross the ocean, like going between Africa and Europe. Ships can only cross the ocean when they have a crew
        Input:
            None
        Output:
            boolean: Returs True if this ship has any crew, otherwise returns False
        '''
        if self.travel_possible:
            if self.has_crew:
                if not self.temp_movement_disabled:
                    return(True)
        return(False)

class boat(ship):
    '''
    Vehicle that behaves similarly to a ship but moves in river water instead and has large inventory capacity and limited movement points
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
                'image_dict': string/string dictionary value - dictionary of image type keys and file path values to the images used by this object in various situations, such as 'crewed': 'crewed_ship.png'
                'name': string value - Required if from save, this mob's name
                'modes': string list value - Game modes during which this mob's images can appear
                'end_turn_destination': string or int tuple value - Required if from save, 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'crew': worker, string, or dictionary value - If no crew, equals 'none'. Otherwise, if creating a new vehicle, equals a worker that serves as crew. If loading, equals a dictionary of the saved information necessary to
                    recreate the worker to serve as crew
                'passenger_dicts': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each of this vehicle's passengers
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(from_save, input_dict, global_manager)
        self.set_max_movement_points(12)
        self.has_infinite_movement = False
        self.vehicle_type = 'ship'
        self.can_swim_river = True
        self.can_swim_ocean = False
        self.can_walk = False
        self.travel_possible = False
        self.inventory_capacity = 27#9

    def get_movement_cost(self, x_change, y_change):
        '''
        Description:
            Returns the cost in movement points of moving by the inputted amounts. Unlike most pmobs, steamboats use their default movement cost to move to all water or port tiles
        Input:
            int x_change: How many cells would be moved to the right in the hypothetical movement
            int y_change: How many cells would be moved upward in the hypothetical movement
        Output:
            double: How many movement points would be spent by moving by the inputted amount
        '''
        return(self.movement_cost)
