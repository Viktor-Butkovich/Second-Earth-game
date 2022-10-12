#Contains functionality for wild beasts

import random
from .npmobs import npmob
from .. import utility

class beast(npmob):
    '''
    Beasts that wander the map hidden, prefer certain terrains, attack/demoralize nearby units, and can be tracked down by a safari
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
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'max_movement_points': int value - Required if from save, maximum number of movement points this mob can have
                'animal_type': string value - Type of beast, like 'lion'
                'adjective': string value - Descriptor for beast, like 'man-eating'
                'hidden': boolean value - Whether this beast is currently hidden
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.hidden = False
        global_manager.get('beast_list').append(self)
        self.animal_type = input_dict['animal_type']
        self.adjective = input_dict['adjective']
        if self.adjective == 'king':
            input_dict['name'] = self.animal_type + ' ' + self.adjective + ' '
        else:
            input_dict['name'] = self.adjective + ' ' + self.animal_type
        super().__init__(from_save, input_dict, global_manager)
        
        self.npmob_type = 'beast'
        self.hostile = True
        self.preferred_terrains = global_manager.get('animal_terrain_dict')[self.animal_type]
        if from_save:
            self.set_hidden(input_dict['hidden'])
        else:
            self.set_hidden(True, True)
            self.set_max_movement_points(4)
            
        if global_manager.get('DEBUG_reveal_beasts'):
            self.set_hidden(False, True)
            
        self.just_revealed = False

    def get_movement_cost(self, x_change, y_change):
        '''
        Description:
            Returns the cost in movement points of moving by the inputted amounts. Unlike most mobs, beasts ignore terrain movement penalties and use their default movement cost regardless of terrain moved to
        Input:
            int x_change: How many cells would be moved to the right in the hypothetical movement
            int y_change: How many cells would be moved upward in the hypothetical movement
        Output:
            double: How many movement points would be spent by moving by the inputted amount
        '''
        return(self.movement_cost) #beasts ignore terrain penalties

    def to_save_dict(self):
        '''
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                Along with superclass outputs, also saves the following values:
                'hidden': boolean value - Whether this beast is currently hidden
                'preferred_terrains': string list value - List of the terrains that this beast can enter
                'animal-type': string value - Type of beast, like 'lion'
                'adjective': string value - Descriptor for beast, like 'man-eating'
        '''
        save_dict = super().to_save_dict()
        save_dict['hidden'] = self.hidden
        save_dict['preferred_terrains'] = self.preferred_terrains
        save_dict['animal_type'] = self.animal_type
        save_dict['adjective'] = self.adjective
        return(save_dict) 

    def find_closest_target(self):
        '''
        Description:
            Finds and returns an adjacent cell to move to. A beast will only move to cells of its, will tend to move torwards nearby pmobs, and may choose to stay in its current tile 
        Input:
            None
        Output:
            cell: Returns a cell to move to
        '''
        target_list = []
        current_cell = self.grids[0].find_cell(self.x, self.y)
        possible_cells = current_cell.adjacent_list + [current_cell]
        if random.randrange(1, 7) >= 3: #1/3 chance of moving to pmob if present, 2/3 chance of moving randomly, possibly torward pmob but not necessarily
            ignoring_pmobs = True
        else:
            ignoring_pmobs = False
        enemy_found = False
        for current_cell in possible_cells:
            if not (current_cell.y == 0 and self.can_swim and not self.can_swim_ocean): #cancel if trying to go into ocean and can't swim in ocean
                if current_cell.terrain in self.preferred_terrains:
                    if not enemy_found:
                        if current_cell.has_pmob() and not ignoring_pmobs:
                            target_list = [current_cell]
                            enemy_found = True
                        else:
                            target_list.append(current_cell)
                    else:
                        if current_cell.has_pmob():
                            target_list.append(current_cell)
        if len(target_list) == 0:
            target_list.append(self.images[0].current_cell)
        return(random.choice(target_list))

    def end_turn_move(self):
        '''
        Description:
            Moves this npmob at the end of the turn and schedules this npmob to start combat if any pmobs are encountered. Unlike other npmobs, only focuses on adjacent tiles and remains hidden until reaching a pmob. An npmob
                will use end_turn_move each time it moves during the enemy turn, which may happen multiple times depending on distance moved
        Input:
            None
        Output:
            None
        ''' 
        self.just_revealed = False
        self.set_hidden(True)
        super().end_turn_move()
        if self.grids[0].find_cell(self.x, self.y).has_pmob():
            self.set_hidden(False)

    def retreat(self):
        '''
        Description:
            Causes a free movement to the last cell this unit moved from, following a failed attack. Also hides the beast after it retreats
        Input:
            None
        Output:
            None
        '''
        if not self.just_revealed:
            self.set_hidden(True)
        super().retreat()

        
    def set_hidden(self, new_hidden, on_load = False):
        '''
        Description:
            Sets this beast's new hidden status. A hidden beast can move around the map as usual and can not be attacked until revealed. A beast reveals itself as it attacks (hiding itself afterward) and can be revealed by a safari
                beasts nearby 
        '''
        self.hidden = new_hidden
        if new_hidden == True:
            self.hide_images()
        else:
            self.show_images()
            if not on_load:
                self.global_manager.get('sound_manager').play_sound('beasts/' + self.animal_type)
            
    
    def check_despawn(self):
        '''
        Description:
            Gives each beast warrior a 1/36 chance of despawning at the end of the turn
        Input:
            None
        Output:
            None
        '''
        if random.randrange(1, 7) == 1 and random.randrange(1, 7) == 1:
            self.remove()  

    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        Input:
            None
        Output:
            None
        '''
        super().remove()
        self.global_manager.set('beast_list', utility.remove_from_list(self.global_manager.get('beast_list'), self))

    def damage_buildings(self):
        '''
        Description:
            While most npmobs would damagee all undefended buildings in this cell after combat if no possible combatants, like workers or soldiers, remain, beasts ignore buildings
        Input:
            None
        Output:
            None
        '''
        nothing = 0 #beasts ignore buildings
