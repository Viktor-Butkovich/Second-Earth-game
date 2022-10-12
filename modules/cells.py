#Contains functionality for grid cells

import pygame
import random
from . import actor_utility

class cell():
    '''
    Object representing one cell of a grid corresponding to one of its coordinates, able to contain terrain, resources, mobs, and tiles
    '''
    def __init__(self, x, y, width, height, grid, color, save_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int x: the x coordinate of this cell in its grid
            int y: the y coordinate of this cell in its grid
            int width: Pixel width of this button
            int height: Pixel height of this button
            grid grid: The grid that this cell is attached to
            string color: Color in the color_dict dictionary for this cell when nothing is covering it
            string or dictionary save_dict: Equals 'none' if creating new grid, equals dictionary of saved information necessary to recreate this cell if loading grid
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.global_manager = global_manager
        self.move_priority = 99
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.grid = grid
        self.color = color
        self.pixel_x, self.pixel_y = self.grid.convert_coordinates((self.x, self.y))
        self.Rect = pygame.Rect(self.pixel_x, self.pixel_y - self.height, self.width, self.height) #(left, top, width, height)
        self.corners = [(self.Rect.left, self.Rect.top ), (self.Rect.left + self.Rect.width, self.Rect.top), (self.Rect.left, self.Rect.top - self.Rect.height), (self.Rect.left + self.Rect.width, self.Rect.top - self.Rect.height)]
        self.grid.cell_list.append(self)
        self.tile = 'none'
        self.resource = 'none'
        self.village = 'none'
        self.terrain = 'none'
        self.set_terrain('clear')
        self.contained_mobs = []
        self.reset_buildings()
        self.adjacent_cells = {'up': 'none', 'down': 'none', 'right': 'none', 'left': 'none'}        
        if not save_dict == 'none':
            self.save_dict = save_dict
            if global_manager.get('DEBUG_remove_fog_of_war'):
                save_dict['visible'] = True
            self.set_visibility(save_dict['visible'])
        else:
            if global_manager.get('DEBUG_remove_fog_of_war'):
                self.set_visibility(True)
            else:
                self.set_visibility(False)

    def to_save_dict(self):
        '''
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'visible': boolean value - Whether this cell is visible or not
                'terrain': string value - Terrain type of this cell and its tile, like 'swamp'
                'resource': string value - Resource type of this cell and its tile, like 'exotic wood'
                'inventory': string/string dictionary value - Version of the inventory dictionary of this cell's tile only containing commodity types with 1+ units held
                'village_name': Only saved if resource is natives, name of this cell's village
                'village_population': Only saved if resource is natives, population of this cell's village
                'village_aggressiveness': Only saved if resource is natives, aggressiveness of this cell's village
                'village_available_workers': Only saved if resource is natives, how many workers this cell's village has
        '''
        save_dict = {}
        save_dict['coordinates'] = (self.x, self.y)
        save_dict['visible'] = self.visible
        save_dict['terrain'] = self.terrain
        save_dict['resource'] = self.resource

        saved_inventory = {}
        if self.tile.can_hold_commodities: #only save inventory if not empty
            for current_commodity in self.global_manager.get('commodity_types'):
               if self.tile.inventory[current_commodity] > 0:
                   saved_inventory[current_commodity] = self.tile.inventory[current_commodity]
        save_dict['inventory'] = saved_inventory
        
        if self.resource == 'natives':
            save_dict['village_name'] = self.village.name
            save_dict['village_population'] = self.village.population
            save_dict['village_aggressiveness'] = self.village.aggressiveness
            save_dict['village_available_workers'] = self.village.available_workers
            save_dict['village_attached_warriors'] = []
            for attached_warrior in self.village.attached_warriors:
                save_dict['village_attached_warriors'].append(attached_warrior.to_save_dict())
        return(save_dict)

    def local_attrition(self, attrition_type = 'health'):
        '''
        Description:
            Returns the result of a roll that determines if a given unit or set of stored commodities should suffer attrition based on this cell's terrain and buildings. Bad terrain increases attrition frequency while infrastructure
                decreases it
        Input:
            string attrition_type = 'health': 'health' or 'inventory', refers to type of attrition being tested for. Used because inventory attrition can occur in Europe but not health attrition
        Output:
            boolean: Returns whether attrition should happen here based on this cell's terrain and buildings
        '''
        #terrain_list = ['clear', 'mountain', 'hills', 'jungle', 'swamp', 'desert']
        if self.grid in [self.global_manager.get('europe_grid'), self.global_manager.get('slave_traders_grid')]: #no attrition in Europe or with slave traders
            if attrition_type == 'health':
                return(False)
            elif attrition_type == 'inventory': #losing inventory in warehouses and such is uncommon but not impossible in Europe, but no health attrition in Europe
                if random.randrange(1, 7) >= 2 or random.randrange(1, 7) >= 3: #same effect as clear area with port
                    return(False)
        else:
            if self.terrain in ['clear', 'hills']:
                if random.randrange(1, 7) >= 2: #only attrition on 1's
                    return(False)
            elif self.terrain in ['mountain', 'desert', 'water']:
                if random.randrange(1, 7) >= 3: #attrition on 1's and 2's
                    return(False)
            elif self.terrain in ['jungle', 'swamp']:
                if random.randrange(1, 7) >= 4: #attrition on 1-3
                    return(False)

            if self.has_building('village') or self.has_building('train_station') or self.has_building('port') or self.has_building('resource') or self.has_building('fort'):
                if random.randrange(1, 7) >= 3: #removes 2/3 of attrition
                    return(False)
            elif self.has_building('road') or self.has_building('railroad'):
                if random.randrange(1, 7) >= 5: #removes 1/3 of attrition
                    return(False)

        return(True)

    def has_building(self, building_type): #accepts village, train_station, port, trading_post, mission, fort, road, railroad, resource, slums. No forts in game yet
        '''
        Description:
            Returns whether this cell has a building of the inputted type, even if the building is damaged
        Input:
            string building_type: type of building to search for
        Output:
            boolean: Returns whether this cell has a building of the inputted type
        '''
        if building_type == 'village':
            if self.village == 'none':
                return(False)
            else:
                return(True)
            
        elif building_type in ['road', 'railroad']:
            if self.contained_buildings['infrastructure'] == 'none':
                return(False)
            elif building_type == 'road' and self.contained_buildings['infrastructure'].is_road:
                return(True)
            elif building_type == 'railroad' and self.contained_buildings['infrastructure'].is_railroad:
                return(True)
            else:
                return(False)
            
        else:
            if self.contained_buildings[building_type] == 'none':
                return(False)
            else:
                return(True)

    def has_intact_building(self, building_type):
        '''
        Description:
            Returns whether this cell has an undamaged building of the inputted type
        Input:
            string building_type: Type of building to search for
        Output:
            boolean: Returns whether this cell has an undamaged building of the inputted type
        '''
        if building_type == 'village':
            if self.village == 'none':
                return(False)
            else:
                returned_building = self.village
                
        elif building_type in ['road', 'railroad']:
            if self.contained_buildings['infrastructure'] == 'none':
                return(False)
            elif building_type == 'road' and self.contained_buildings['infrastructure'].is_road:
                returned_building = self.contained_buildings['infrastructure']
            elif building_type == 'railroad' and self.contained_buildings['infrastructure'].is_railroad:
                returned_building = self.contained_buildings['infrastructure']
            else:
                return(False)
            
        else:
            if self.contained_buildings[building_type] == 'none':
                return(False)
            else:
                returned_building = self.contained_buildings[building_type]

        if not returned_building.damaged:
            return(True)
        else:
            return(False)
        
    def get_building(self, building_type):
        '''
        Description:
            Returns this cell's building of the inputted type, or 'none' if that building is not present
        Input:
            string building_type: Type of building to search for
        Output:
            building/string: Returns whether this cell's building of the inputted type, or 'none' if that building is not present
        '''
        if self.has_building(building_type):
            if building_type == 'village':
                return(self.village)
                
            elif building_type in ['road', 'railroad']:
                return(self.contained_buildings['infrastructure'])
                
            else:
                return(self.contained_buildings[building_type])
            
        else:
            return('none')

    def get_intact_building(self, building_type):
        '''
        Description:
            Returns this cell's undamaged building of the inputted type, or 'none' if that building is damaged or not present
        Input:
            string building_type: Type of building to search for
        Output:
            building/string: Returns this cell's undamaged building of the inputted type, or 'none' if that building is damaged or not present
        '''
        if self.has_intact_building(building_type):
            if building_type == 'village':
                return(self.village)
                
            elif building_type in ['road', 'railroad']:
                return(self.contained_buildings['infrastructure'])
                
            else:
                return(self.contained_buildings[building_type])
            
        else:
            return('none')

    def reset_buildings(self):
        '''
        Description:
            Resets the values of this cell's dictionary of contained buildings to 'none', initializing the dictionary or removing existing buildings
        Input:
            None
        Output:
            None
        '''
        self.contained_buildings = {}
        for current_building_type in self.global_manager.get('building_types'):
            self.contained_buildings[current_building_type] = 'none'

    def get_buildings(self):
        '''
        Description:
            Returns a list of the buildings contained in this cell
        Input:
            None
        Output:
            building list contained_buildings_list: buildings contained in this cell
        '''
        contained_buildings_list = []
        for current_building_type in self.global_manager.get('building_types'):
            if self.has_building(current_building_type):
                contained_buildings_list.append(self.contained_buildings[current_building_type])
        return(contained_buildings_list)

    def get_intact_buildings(self):
        '''
        Description:
            Returns a list of the nondamaged buildings contained in this cell
        Input:
            None
        Output:
            building list contained_buildings_list: nondamaged buildings contained in this cell
        '''
        contained_buildings_list = []
        for current_building_type in self.global_manager.get('building_types'):
            if self.has_intact_building(current_building_type):
                contained_buildings_list.append(self.contained_buildings[current_building_type])
        return(contained_buildings_list)

    def adjacent_to_buildings(self):
        '''
        Description:
            Finds and returns if this cell is adjacent to any buildings, used for beast spawning
        Input:
            None
        Output:
            boolean: Returns if this cell is adjacent to any buildings
        '''
        for current_adjacent_cell in (self.adjacent_list + [self]):
            if len(current_adjacent_cell.get_buildings()) > 0:
                return(True)
        return(False)

    def has_destructible_buildings(self):
        '''
        Description:
            Finds and returns if this cell is adjacent has any buildings that can be damaged by native warriors (not roads or railroads), used for native warriors cell targeting
        Input:
            None
        Output:
            boolean: Returns if this cell has any buildings that can be damaged by native warriors
        '''
        for current_building in self.get_intact_buildings():
            if current_building.can_damage():
                return(True)
        return(False)

    def get_warehouses_cost(self):
        warehouses = self.get_building('warehouses')
        if warehouses == 'none':
            warehouses_built = 0
        else:
            warehouses_built = warehouses.warehouse_level
        if self.has_building('port'):
            warehouses_built -= 1
        if self.has_building('train_station'):
            warehouses_built -= 1
        if self.has_building('resource'):
            warehouses_built -= 1

        return(self.global_manager.get('building_prices')['warehouses'] * (2 ** warehouses_built)) #5 * 2^0 = 5 if none built, 5 * 2^1 = 10 if 1 built, 20, 40...
    
    def create_slums(self):
        '''
        Description:
            Creates an empty slums building when a worker migrates to this cell, if there is not already one present
        Input:
            None
        Outptu:
            None
        '''
        input_dict = {}
        input_dict['coordinates'] = (self.x, self.y)
        input_dict['grids'] = [self.grid, self.grid.mini_grid]
        input_dict['name'] = 'slums'
        input_dict['modes'] = ['strategic']
        input_dict['init_type'] = 'slums'
        self.global_manager.get('actor_creation_manager').create(False, input_dict, self.global_manager)
        if self.tile == self.global_manager.get('displayed_tile'):
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.tile) #update tile display to show new building

    def has_vehicle(self, vehicle_type, is_worker = False):
        '''
        Description:
            Returns whether this cell contains a crewed vehicle of the inputted type
        Input:
            string vehicle_type: 'train' or 'ship', determines what kind of vehicle is searched for
        Output:
            boolean: Returns True if this cell contains a crewed vehicle of the inputted type, otherwise returns False
        '''
        for current_mob in self.contained_mobs:
            if current_mob.is_vehicle and (current_mob.has_crew or is_worker) and current_mob.vehicle_type == vehicle_type:
                return(True)
        return(False)

    def get_vehicle(self, vehicle_type, is_worker = False):
        '''
        Description:
            Returns the first crewed vehicle of the inputted type in this cell, or 'none' if none are present
        Input:
            string vehicle_type: 'train' or 'ship', determines what kind of vehicle is searched for
        Output:
            string/vehicle: Returns the first crewed vehicle of the inputted type in this cell, or 'none' if none are present
        '''
        for current_mob in self.contained_mobs:
            if current_mob.is_vehicle and (current_mob.has_crew or is_worker) and current_mob.vehicle_type == vehicle_type:
                return(current_mob)
        return('none')

    def has_uncrewed_vehicle(self, vehicle_type):
        '''
        Description:
            Returns whether this cell contains an uncrewed vehicle of the inputted type
        Input:
            string vehicle_type: 'train' or 'ship', determines what kind of vehicle is searched for
        Output:
            boolean: Returns True if this cell contains an uncrewed vehicle of the inputted type, otherwise returns False
        '''
        for current_mob in self.contained_mobs:
            if current_mob.is_vehicle and (not current_mob.has_crew) and current_mob.vehicle_type == vehicle_type:
                return(True)
        return(False)

    def get_uncrewed_vehicle(self, vehicle_type, worker_type = 'default'):
        '''
        Description:
            Returns the first uncrewed vehicle of the inputted type in this cell, or 'none' if none are present
        Input:
            string vehicle_type: 'train' or 'ship', determines what kind of vehicle is searched for
            string worker_type = 'default': If a worker type is inputted, only vehicles that the inputted worker type oculd crew are returned
        Output:
            string/vehicle: Returns the first uncrewed vehicle of the inputted type in this cell, or 'none' if none are present
        '''
        if worker_type == 'slave':
            return('none')
        for current_mob in self.contained_mobs:
            if current_mob.is_vehicle and (not current_mob.has_crew) and current_mob.vehicle_type == vehicle_type:
                if not (worker_type == 'African' and current_mob.can_swim and current_mob.can_swim_ocean):
                    return(current_mob)
        return('none')

    def has_worker(self, possible_types = ['African', 'European', 'slave', 'religious']):
        '''
        Description:
            Returns whether this cell contains a worker of one of the inputted types
        Input:
            string list possible_types: Type of worker that can be detected, includes all workers by default
        Output:
            Returns True if this cell contains a worker of one of the inputted types, otherwise returns False
        '''
        for current_mob in self.contained_mobs:
            if current_mob in self.global_manager.get('worker_list') and current_mob.worker_type in possible_types: 
                return(True)
        return(False)

    def get_worker(self, possible_types = ['African', 'European', 'slave', 'religious']):
        '''
        Description:
            Returns the first worker in this cell of the inputted types, or 'none' if none are present
        Input:
            string list possible_types: Type of worker that can be returned, includes all workers by default
        Output:
            string/worker: Returns the first worker in this cell of the inputted types, or 'none' if none are present
        '''
        for current_mob in self.contained_mobs:
            if current_mob in self.global_manager.get('worker_list') and current_mob.worker_type in possible_types:
                return(current_mob)
        return('none')

    def has_pmob(self):
        '''
        Description:
            Returns whether this cell contains a pmob
        Input:
            None
        Output:
            boolean: Returns whether this cell contains a pmob
        '''
        for current_mob in self.contained_mobs:
            if current_mob.is_pmob:
                return(True)
        if self.has_intact_building('resource'):
            if len(self.get_intact_building('resource').contained_work_crews) > 0:
                return(True)
        return(False)

    def get_pmob(self):
        '''
        Description:
            Returns the first pmob in this cell, or 'none' if none are present
        Input:
            None
        Output:
            string/pmob: Returns the first pmob in this cell, or 'none' if none are present
        '''
        for current_mob in self.contained_mobs:
            if current_mob.is_pmob:
                return(current_mob)
        return('none')

    def has_npmob(self):
        '''
        Description:
            Returns whether this cell contains an npmob
        Input:
            None
        Output:
            boolean: Returns whether this cell contains an npmob
        '''
        for current_mob in self.contained_mobs:
            if current_mob.is_npmob:
                return(True)
        return(False)

    def get_best_combatant(self, mob_type, target_type = 'human'):
        '''
        Description:
            Finds and returns the best combatant of the inputted type in this cell. Combat ability is based on the unit's combat modifier and veteran status. Assumes that units in vehicles and buildings have already detached upon being
                attacked
        Input:
            string mob_type: Can be npmob or pmob, determines what kind of mob is searched for. An attacking pmob will search for the most powerful npmob and vice versa
            string target_type = 'human': Regardless of the mob type being searched for, target_type gives information about the npmob: when a pmob searches for an npmob, it will search for a 'human' or 'beast' npmob. When an npmob
                searches for a pmob, it will say whether it is a 'human' or 'beast' to correctly choose pmobs specialized at fighting that npmob type, like safaris against beasts
        Output;
            mob: Returns the best combatant of the inputted type in this cell
        '''
        best_combatants = ['none']
        best_combat_modifier = 0
        if mob_type == 'npmob':
            for current_mob in self.contained_mobs:
                if current_mob.is_npmob:
                    if (target_type == 'human' and not current_mob.npmob_type == 'beast') or (target_type == 'beast' and current_mob.npmob_type == 'beast'):
                        current_combat_modifier = current_mob.get_combat_modifier()
                        if best_combatants[0] == 'none' or current_combat_modifier > best_combat_modifier: #if first mob or better than previous mobs, set as only best
                            best_combatants = [current_mob]
                            best_combat_modifier = current_combat_modifier
                        elif current_combat_modifier == best_combat_modifier: #if equal to previous mobs, add to best
                            best_combatants.append(current_mob)
        elif mob_type == 'pmob':
            for current_mob in self.contained_mobs:
                if current_mob.is_pmob:
                    if current_mob.get_combat_strength() > 0: #unit with 0 combat strength can not fight
                        current_combat_modifier = current_mob.get_combat_modifier()
                        if current_mob.is_safari and target_type == 'beast': #more likely to pick safaris for defense against beasts
                            current_combat_modifier += 3
                        elif target_type == 'beast':
                            current_combat_modifier -= 1
                        if best_combatants[0] == 'none' or current_combat_modifier > best_combat_modifier:
                            best_combatants = [current_mob]
                            best_combat_modifier = current_combat_modifier
                        elif current_combat_modifier == best_combat_modifier:
                            if current_mob.veteran and not best_combatants[0].veteran: #use veteran as tiebreaker
                                best_combatants = [current_mob]
                                best_combatant_modifier = current_combat_modifier
                            else:
                                best_combatants.append(current_mob)
                        
        return(random.choice(best_combatants))

    def get_noncombatants(self, mob_type):
        '''
        Description:
            Finds and returns all units of the inputted type in this cell that have 0 combat strength. Assumes that units in vehicles and buildings have already detached upon being attacked
        Input:
            string mob_type: Can be npmob or pmob, determines what kind of mob is searched for. An attacking pmob will search for noncombatant pmobs and vice versa
        Output:
            mob list: Returns the noncombatants of the inputted type in this cell
        '''
        noncombatants = []
        if mob_type == 'npmob':
            for current_mob in self.contained_mobs:
                if current_mob.is_npmob and current_mob.get_combat_strength() == 0:
                    noncombatants.append(current_mob)
        elif mob_type == 'pmob':
            for current_mob in self.contained_mobs:
                if current_mob.is_pmob and current_mob.get_combat_strength() == 0:
                    noncombatants.append(current_mob)
        return(noncombatants)
                    
    def set_visibility(self, new_visibility):
        '''
        Description:
            Sets the visibility of this cell and its attached tile to the inputted value. A visible cell's terrain and resource can be seen by the player.
        Input:
            boolean new_visibility: This cell's new visibility status
        Output:
            None
        '''
        self.visible = new_visibility
        if not self.tile == 'none':
            self.tile.set_visibility(new_visibility)
    
    def set_resource(self, new_resource):
        '''
        Description:
            Sets the resource type of this cell and its attached tile to the inputted value
        Input:
            string new_resource: The new resource type of this cell and its attached tile, like 'exotic wood'
        Output:
            None
        '''
        self.resource = new_resource
        self.tile.set_resource(new_resource)

    def set_terrain(self, new_terrain):
        '''
        Description:
            Sets the terrain type of this cell and its attached tile to the inputted value
        Input:
            string new_terrain: The new terrain type of this cell and its attached tile, like 'swamp'
        Output:
            None
        '''
        self.terrain = new_terrain
        if (not self.tile == 'none'):
            self.tile.set_terrain(new_terrain)
        self.color = self.global_manager.get('terrain_colors')[new_terrain]
            
    def draw(self):
        '''
        Description:
            Draws this cell as a rectangle with a certain color on its grid, depending on this cell's color value
        Input:
            none
        Output:
            None
        '''
        current_color = self.color
        red = current_color[0]
        green = current_color[1]
        blue = current_color[2]
        pygame.draw.rect(self.global_manager.get('game_display'), (red, green, blue), self.Rect)

    def show_num_mobs(self):
        '''
        Description:
            Draws a number showing how many mobs are in this cell if it contains multiple mobs, otherwise does nothing
        Input:
            None
        Output:
            None
        '''
        length = len(self.contained_mobs)
        if length >= 2 and self.visible and not self.terrain == 'none':
            message = str(length)
            color = 'white'
            font_size = round(self.width * 0.3)
            current_font = pygame.font.SysFont(self.global_manager.get('font_name'), font_size)
            textsurface = current_font.render(message, False, self.global_manager.get('color_dict')[color])
            text_x = self.pixel_x + self.width - (font_size * 0.5)
            text_y = self.pixel_y - font_size
            self.global_manager.get('game_display').blit(textsurface, (text_x, text_y))

    def touching_mouse(self):
        '''
        Description:
            Returns True if this cell is colliding with the mouse, otherwise returns False
        Input:
            None
        Output:
            boolean: Returns True if this cell is colliding with the mouse, otherwise returns False
        '''
        if self.Rect.collidepoint(pygame.mouse.get_pos()):
            return(True)
        else:
            return(False)

    def find_adjacent_cells(self):
        '''
        Description:
            Records a list of the cells directly adjacent to this cell. Also records these cells as values in a dictionary with string keys corresponding to their direction relative to this cell
        Input:
            None
        Output:
            None
        '''
        adjacent_list = []
        if not self.x == 0:
            adjacent_cell = self.grid.find_cell(self.x - 1, self.y)
            adjacent_list.append(adjacent_cell)
            self.adjacent_cells['left'] = adjacent_cell
        if not self.x == self.grid.coordinate_width - 1:
            adjacent_cell = self.grid.find_cell(self.x + 1, self.y)
            adjacent_list.append(adjacent_cell)
            self.adjacent_cells['right'] = adjacent_cell
        if not self.y == 0:
            adjacent_cell = self.grid.find_cell(self.x, self.y - 1)
            adjacent_list.append(adjacent_cell)
            self.adjacent_cells['down'] = adjacent_cell
        if not self.y == self.grid.coordinate_height - 1:
            adjacent_cell = self.grid.find_cell(self.x, self.y + 1)
            adjacent_list.append(adjacent_cell)
            self.adjacent_cells['up'] = adjacent_cell
        self.adjacent_list = adjacent_list

