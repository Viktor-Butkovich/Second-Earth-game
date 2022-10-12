#Contains functionality for native warriors units

import random
from .npmobs import npmob
from .. import utility

class native_warriors(npmob):
    '''
    npmob that represents a population unit that temporarily leaves an aggressive village to attack player-controlled mobs/buildings
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
                'canoes_image': string value - File path tothe image used by this object when it is in a river
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(from_save, input_dict, global_manager)
        self.number = 2 #native warriors is plural
        self.hostile = True
        self.can_damage_buildings = True
        self.aggro_distance = 3
        self.saves_normally = False #saves as part of village
        self.origin_village = input_dict['origin_village']
        self.origin_village.attached_warriors.append(self)
        self.npmob_type = 'native_warriors'
        self.despawning = False
        
        self.has_canoes = True
        self.image_dict['canoes'] = input_dict['canoes_image']
        self.image_dict['no_canoes'] = self.image_dict['default']
        self.update_canoes()
        if not from_save:
            self.set_max_movement_points(4)
            if not global_manager.get('creating_new_game'):
                self.hide_images() #show native warriors spawning in main_loop during enemy turn, except during setup

    def attack_on_spawn(self):
        '''
        Description:
            Upon spawning, checks if there are any pmobs or destructible buildings in this tile and attacks them as applicable
        Input:
            None
        Output:
            None
        '''
        if self.combat_possible(): #attack any player-controlled units in tile when spawning
            available_directions = [(0, 1), (0, -1), (1, 0), (-1, 0)] #all directions
            possible_directions = [] #only directions that can be retreated in
            for direction in available_directions:
                cell = self.images[0].current_cell.grid.find_cell(self.x - direction[0], self.y - direction[1])
                if not cell == 'none':
                    if not cell.has_pmob() and not cell.y == 0: #can't retreat to ocean or into player units
                        possible_directions.append(direction)
            if len(possible_directions) > 0:
                self.last_move_direction = random.choice(possible_directions)
                if self.global_manager.get('player_turn'):
                    if self.grids[0].find_cell(self.x, self.y).get_best_combatant('pmob', self.npmob_type) == 'none':
                        self.kill_noncombatants()
                        self.damage_buildings()
                    else:
                        self.attempt_local_combat() #if spawned by failed trade or conversion during player turn, attack immediately
                else:
                    self.global_manager.get('attacker_queue').append(self)
            else:
                self.remove()
                self.origin_village.change_population(1) #despawn if pmob on tile and can't retreat anywhere
        else:
            self.damage_buildings()

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
        self.origin_village.attached_warriors = utility.remove_from_list(self.origin_village.attached_warriors, self)

    def check_despawn(self):
        '''
        Description:
            Gives each native warrior a 1/6 chance of despawning and returning to its home village at the end of the turn
        Input:
            None
        Output:
            None
        '''
        if random.randrange(1, 7) >= 4 and random.randrange(1, 7) >= 4: #1/4 chance of despawn
            #self.remove()
            self.despawning = True
            self.origin_village.change_population(1)
