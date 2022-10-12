#Contains functionality for villages

import random

from . import village_name_generator
from . import actor_utility
from . import utility

class village():
    '''
    Object that represents a native village in a cell on the strategic map grid
    '''
    def __init__(self, from_save, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'name': string value - Required if from save, starting name of village
                'population': int value - Required if from save, starting population of village
                'aggressiveness': int value - Required if from save, starting aggressiveness
                'available_workers': int value - Required if from save, starting number of available workers
                'cell': cell value - cell on strategic map grid in which this village exists
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.global_manager = global_manager
        self.attached_warriors = []
        if not from_save:
            self.set_initial_population()
            self.set_initial_aggressiveness()
            self.available_workers = 0
            self.attempted_trades = 0
            self.name = village_name_generator.create_village_name()
        else:
            self.name = input_dict['name']
            self.population = input_dict['population']
            self.aggressiveness = input_dict['aggressiveness']
            self.available_workers = input_dict['available_workers']
            for current_save_dict in input_dict['attached_warriors']:
                current_save_dict['origin_village'] = self
                self.global_manager.get('actor_creation_manager').create(True, current_save_dict, global_manager)
        if self.global_manager.get('DEBUG_infinite_village_workers'):
            self.available_workers = self.population
        self.cell = input_dict['cell']
        self.x = self.cell.x
        self.y = self.cell.y
        self.tiles = [] #added in set_resource for tiles
        if not self.cell.grid.is_mini_grid: #villages should not be created in mini grid cells, so do not allow village to be visible to rest of program if it is on a mini grid cell
            self.global_manager.get('village_list').append(self) #have more permanent fix later

    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        Input:
            None
        Output:
            None
        '''
        self.global_manager.set('village_list', utility.remove_from_list(self.global_manager.get('village_list'), self))

    def manage_warriors(self):
        '''
        Description:
            Controls the spawning and despawning of native warriors, with higher-population and highly aggressive villages being more likely to spawn. Spawned warriors temporarily leave the population and return when despawned
        Input:
            None
        Output:
            None
        '''
        for current_attached_warrior in self.attached_warriors:
            current_attached_warrior.check_despawn()

        if self.can_spawn_warrior() and random.randrange(1, 7) >= 3: #2/3 chance of even attempting
            min_spawn_result = 6 + self.get_aggressiveness_modifier() # 6-1 = 5 on high aggressiveness, 6 on average aggressiveness, 6+1 = 7 on low aggressiveness
            if random.randrange(1, 7) >= min_spawn_result: #1/3 on high, 1/6 on average, 0 on low
                self.spawn_warrior()
            
    def can_spawn_warrior(self):
        '''
        Description:
            Returns whether this village can currently spawn a warrior. A village with 0 population can not spawn warriors, and available workers will not become warriors
        Input:
            None
        Output:
            Returns whether this village can currently spawn a warrior
        '''
        if self.global_manager.get('DEBUG_spawning_allowed') and self.population > self.available_workers:
            return(True)
        return(False)
    
    def can_recruit_worker(self):
        '''
        Description:
            Returns whether a worker can be recruited from this village
        Input:
            None
        Output:
            boolean: Returns True if this village has any available workers, otherwise returns False
        '''
        if self.available_workers > 0:
            return(True)
        return(False)

    def spawn_warrior(self):
        '''
        Description:
            Creates a native warrior at this village's location from one of its population units
        Input:
            None
        Output:
            native_warriors: Returns the created native warriors unit
        '''
        input_dict = {}
        input_dict['coordinates'] = (self.cell.x, self.cell.y)
        input_dict['grids'] = [self.cell.grid, self.cell.grid.mini_grid]
        input_dict['image'] = 'mobs/native_warriors/default.png'
        input_dict['canoes_image'] = 'mobs/native_warriors/canoe_default.png'
        input_dict['modes'] = ['strategic']
        input_dict['name'] = 'native warriors'
        input_dict['init_type'] = 'native_warriors'
        input_dict['origin_village'] = self
        self.change_population(-1)
        #if self.available_workers > self.population: #if available worker leaves to be warrior, reduce number of available workers
        #    self.set_available_workers(self.population)
        return(self.global_manager.get('actor_creation_manager').create(False, input_dict, self.global_manager))

    def recruit_worker(self):
        '''
        Description:
            Hires one of this village's available workers by creating a worker, reducing the village's population and number of available workers
        Input:
            None
        Output:
            None
        '''
        input_dict = {}
        input_dict['coordinates'] = (self.cell.x, self.cell.y)
        input_dict['grids'] = [self.cell.grid, self.cell.grid.mini_grid]
        input_dict['image'] = 'mobs/African workers/default.png'
        input_dict['modes'] = ['strategic']
        input_dict['name'] = 'African workers'
        input_dict['init_type'] = 'workers'
        input_dict['worker_type'] = 'African'
        self.available_workers -= 1 #doesn't need to update tile display twice, so just directly change # available workers instead of change_available_workers(-1)
        self.change_population(-1)
        self.global_manager.get('actor_creation_manager').create(False, input_dict, self.global_manager)

    def set_initial_population(self):
        '''
        Description:
            Sets this village's population to a random number between 1 and 9
        Input:
            None
        Output:
            None
        '''
        self.population = random.randrange(1, 10)
    
    def set_initial_aggressiveness(self):
        '''
        Description:
            Sets this village's population to its aggressiveness changed randomly. Change based on 9 rolls of D6, decrease on 1-2, increase on 5-6, roll again on 1 or 6
        Input:
            None
        Output:
            None
        '''
        self.aggressiveness = self.population
        remaining_rolls = 9
        while remaining_rolls > 0:
            remaining_rolls -= 1
            roll = random.randrange(1, 7)
            if roll <= 2: #1-2
                self.aggressiveness -= 1
                if roll == 1:
                    remaining_rolls += 1
            #3-4 does nothing
            elif roll >= 5: #5-6
                self.aggressiveness += 1
                if roll == 6:
                    remaining_rolls += 1
            if self.aggressiveness < 1:
                self.aggressiveness = 1
            elif self.aggressiveness > 9:
                self.aggressiveness = 9
            
    def get_tooltip(self):
        '''
        Description:
            Returns this village's tooltip. Its tooltip describes its name, population, how many of its population are willing to become workers, and aggressiveness
        Input:
            None
        Output:
            string list: list with each item representing a line of this village's tooltip
        '''
        tooltip_text = []
        tooltip_text.append("Village name: " + self.name)
        tooltip_text.append("    Total population: " + str(self.population))
        tooltip_text.append("    Available workers: " + str(self.available_workers))
        tooltip_text.append("    Aggressiveness: " + str(self.aggressiveness))
        return(tooltip_text)

    def get_aggressiveness_modifier(self): #modifier affects roll difficulty, not roll result
        '''
        Description:
            Returns a modifier corresponding to this village's aggressiveness, with higher aggressiveness causing lower modifiers. These modifiers affect the difficulty of actions relating to this village
        Input:
            None
        Output:
            int: Returns 1 if this village's aggressiveness is between 0 and 3, returns 0 if this village's aggressiveness if between 4 and 6, otherwise returns -1
        '''
        if self.aggressiveness <= 3: #1-3
            return(1)
        elif self.aggressiveness <= 6: #4 - 6
            return(0)
        else: #7 - 9
            return(-1)

    def get_population_modifier(self): #modifier affects roll difficulty, not roll result
        '''
        Description:
            Returns a modifier corresponding to this village's population with higher population causing lower modifiers. These modifiers affect the difficulty and reward level of actions relating to this village
        Input:
            None
        Output:
            int: Returns 1 if this village's aggressiveness is between 0 and 3, returns 0 if this village's aggressiveness if between 4 and 6, otherwise returns -1
        '''
        if self.population <= 3: #1-3
            return(1)
        elif self.population <= 6: #4 - 6
            return(0)
        else: #7 - 9
            return(-1)

    def change_available_workers(self, change):
        '''
        Description:
            Changes this village's number of available workers by the inputted amount, updating the tile info display as applicable
        Input:
            int change: amount this village's population is changed by
        Output:
            None
        '''
        self.available_workers += change
        if self.cell.tile == self.global_manager.get('displayed_tile'): #if being displayed, change displayed available workers value
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.cell.tile)    

    def set_available_workers(self, new_value):
        '''
        Description:
            Sets this village's number of avavilable workers to the inputted amount
        Input:
            None
        Output:
            None
        '''
        self.available_workers = new_value
        if self.cell.tile == self.global_manager.get('displayed_tile'): #if being displayed, change displayed available workers value
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.cell.tile)
    
    def change_population(self, change):
        '''
        Description:
            Changes this village's population by the inputted amount. Prevents the value from exiting the allowed range of 1-9 and updates the tile info display as applicable
        Input:
            int change: amount this village's population is changed by
        Output:
            None
        '''
        self.population += change
        if self.population > 9:
            self.population = 9
        elif self.population < 0:
            self.population = 0
        if self.available_workers > self.population:
            self.set_available_workers(self.population)
        #if self.cell.visible:
        for current_tile in self.tiles:
            current_tile.update_resource_icon()
        if self.cell.tile == self.global_manager.get('displayed_tile'): #if being displayed, change displayed population value
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.cell.tile)

    def change_aggressiveness(self, change):
        '''
        Description:
            Changes this village's aggressiveness by the inputted amount. Prevents the value from exiting the allowed range of 1-9 and updates the tile info display as applicable
        Input:
            int change: amount this village's aggressivness is changed by
        Output:
            None
        '''
        self.aggressiveness += change
        if self.aggressiveness > 9:
            self.aggressiveness = 9
        elif self.aggressiveness < 1:
            self.aggressiveness = 1
        for current_tile in self.tiles:
            current_tile.update_resource_icon()
        if self.cell.tile == self.global_manager.get('displayed_tile'): #if being displayed, change displayed aggressiveness value
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.cell.tile)
