#Contains functionality for buildings

import pygame
import random

from .actors import actor
from .buttons import button
from . import utility
from . import images
from . import actor_utility
from . import text_tools

class building(actor):
    '''
    Actor that exists in cells of multiple grids in front of tiles and behind mobs that can not be clicked
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
                'name': string value - Required if from save, this building's name
                'building_type': string value - Type of building, like 'port'
                'modes': string list value - Game modes during which this building's images can appear
                'contained_work_crews': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each work crew working in this building
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.actor_type = 'building'
        self.building_type = input_dict['building_type']
        self.damaged = False
        super().__init__(from_save, input_dict, global_manager)
        self.default_inventory_capacity = 0
        self.inventory_capacity = 0
        no_png_image = input_dict['image'][0:len(input_dict['image']) - 4]
        self.image_dict = {'default': input_dict['image'], 'damaged': no_png_image + '_damaged' + '.png', 'intact': input_dict['image']}
        if input_dict['building_type'] == 'warehouses':
            self.image_dict['damaged'] = self.image_dict['default']
        self.images = []
        for current_grid in self.grids:
            self.images.append(images.building_image(self, current_grid.get_cell_width(), current_grid.get_cell_height(), current_grid, 'default',
                self.global_manager)) #self, actor, width, height, grid, image_description, global_manager
        self.global_manager.get('building_list').append(self)
        self.set_name(input_dict['name'])
        self.contained_work_crews = []        
        if from_save:
            for current_work_crew in input_dict['contained_work_crews']:
                self.global_manager.get('actor_creation_manager').create(True, current_work_crew, self.global_manager).work_building(self)
            if self.can_damage():
                self.set_damaged(input_dict['damaged'], True)
        elif self.can_damage():
            self.set_damaged(False, True)
        for current_image in self.images:
            current_image.current_cell.contained_buildings[self.building_type] = self
            current_image.current_cell.tile.update_resource_icon()
        self.is_port = False #used to determine if port is in a tile to move there

        self.set_inventory_capacity(self.default_inventory_capacity)
        if global_manager.get('DEBUG_damaged_buildings'):
            if self.can_damage():
                self.set_damaged(True, True)

    def to_save_dict(self):
        '''
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                Along with superclass outputs, also saves the following values:
                'building_type': string value - Type of building, like 'port'
                'image': string value - File path to the image used by this object
                'contained_work_crews': dictionary list value - list of dictionaries of saved information necessary to recreate each work crew working in this building
                'damaged': boolean value - whether this building is currently damaged
        '''
        save_dict = super().to_save_dict()
        save_dict['building_type'] = self.building_type
        save_dict['contained_work_crews'] = [] #list of dictionaries for each work crew, on load a building creates all of its work crews and attaches them
        save_dict['image'] = self.image_dict['intact']
        save_dict['damaged'] = self.damaged
        for current_work_crew in self.contained_work_crews:
            save_dict['contained_work_crews'].append(current_work_crew.to_save_dict())
        return(save_dict)

    def can_damage(self):
        '''
        Description:
            Returns whether this building is able to be damaged. Roads, railroads, and slums cannot be damaged
        Input:
            None
        Output:
            boolean: Returns whether this building is able to be damaged
        '''
        return(True)

    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. Also removes this building from the tiles it occupies
        Input:
            None
        Output:
            None
        '''
        tiles = []
        for current_image in self.images:
            if not current_image.current_cell == 'none':
                current_image.current_cell.contained_buildings[self.building_type] = 'none'
                tiles.append(current_image.current_cell.tile)
            current_image.current_cell.contained_buildings[self.building_type] = 'none'
            current_image.remove_from_cell()
            current_image.remove()
        super().remove()
        self.global_manager.set('building_list', utility.remove_from_list(self.global_manager.get('building_list'), self))
        for current_tile in tiles:
            current_tile.update_resource_icon()
        if self.global_manager.get('displayed_tile') in tiles: #if currently displayed, update tile to show building removal
            self.global_manager.get('minimap_grid').calibrate(self.x, self.y)

    def update_tooltip(self): #should be shown below mob tooltips
        '''
        Description:
            Sets this image's tooltip to what it should be whenever the player looks at the tooltip. For buildings, sets tooltip to a description of the building
        Input:
            None
        Output:
            None
        '''
        tooltip_text = [self.name.capitalize()]
        if self.building_type == 'resource':
            tooltip_text.append("Work crews: " + str(len(self.contained_work_crews)) + '/' + str(self.scale))
            for current_work_crew in self.contained_work_crews:
                tooltip_text.append("    " + current_work_crew.name)
            tooltip_text.append("Lets " + str(self.scale) + " attached work crews each attempt to produce " + str(self.efficiency) + " units of " + self.resource_type + " each turn")
        elif self.building_type == 'port':
            tooltip_text.append("Allows ships to enter this tile")
        elif self.building_type == 'infrastructure':
            tooltip_text.append("Halves movement cost for units going to another tile with a road or railroad")
            if self.is_railroad:
                tooltip_text.append("Allows trains to move from this tile to other tiles that have railroads")
            else:
                tooltip_text.append("Can be upgraded to a railroad to allow trains to move through this tile")
        elif self.building_type == 'train_station':
            tooltip_text.append("Allows construction gangs to build trains on this tile")
            tooltip_text.append("Allows trains to drop off or pick up cargo or passengers in this tile")
        elif self.building_type == 'slums':
            tooltip_text.append("Contains " + str(self.available_workers) + " African workers in search of employment")
        elif self.building_type == 'trading_post':
            tooltip_text.append("Increases the success chance of caravans trading with this tile's village")
        elif self.building_type == 'mission':
            tooltip_text.append("Increases the success chance of missionaries converting this tile's village")
        elif self.building_type == 'fort':
            tooltip_text.append("Grants a +1 combat modifier to your units fighting in this tile")
        elif self.building_type == "warehouses":
            tooltip_text.append("Level " + str(self.warehouse_level) + " warehouses allow an inventory capacity of " + str(9 * self.warehouse_level))

        if self.damaged:
            tooltip_text.append("This building is damaged and is currently not functional.")
            
        self.set_tooltip(tooltip_text)

    def set_damaged(self, new_value, mid_setup = False):
        '''
        Description:
            Repairs or damages this building based on the inputted value. A damaged building still provides attrition resistance but otherwise loses its specialized capabilities
        Input:
            boolean new_value: New damaged/undamaged state of the building
        Output:
            None
        '''
        self.damaged = new_value
        if self.building_type == 'infrastructure':
            actor_utility.update_roads(self.global_manager)
        if self.damaged:
            self.set_inventory_capacity(0)
            self.image_dict['default'] = self.image_dict['damaged']
            self.set_image('default')
        else:
            self.set_inventory_capacity(self.default_inventory_capacity)
            self.image_dict['default'] = self.image_dict['intact']
            self.set_image('default')

        if (not mid_setup) and self.building_type in ['resource', 'port', 'train_station']:
            self.images[0].current_cell.get_building('warehouses').set_damaged(new_value)

    def set_default_inventory_capacity(self, new_value):
        '''
        Description:
            Sets a new default inventory capacity for a building. A building's inventory capacity may differ from its default inventory capacity if it becomes damaged
        Input:
            int new_value: New default inventory capacity for the building
        Output:
            None
        '''
        self.default_inventory_capacity = new_value
        self.set_inventory_capacity(new_value)
    
    def set_inventory_capacity(self, new_value):
        '''
        Description:
            Sets a new current inventory capacity for a building. A building's inventory capacity may change when it is upgraded, damaged, or repaired
        Input:
            int/string new_value: New current inventory capacity for the building. 'default' sets the inventory capacity to its default amount
        Output:
            None
        '''
        old_value = self.inventory_capacity
        if new_value == 'default':
            self.inventory_capacity = self.default_inventory_capacity
        else:
            self.inventory_capacity = new_value
        self.contribute_local_inventory_capacity(old_value, new_value)

    def contribute_local_inventory_capacity(self, previous_value, new_value):
        '''
        Description:
            Updates this building's tile's total inventory capacity based on changes to this buiding's current inventory capacity
        Input:
            int previous_value: Previous inventory capacity that had been used in the tile's total inventory capacity
            int new_value: New inventory capacity to be used in the tile's total inventory capacity
        Output:
            None
        '''
        current_index = 0
        for current_image in self.images:
            if current_index == 0:
                current_image.current_cell.tile.inventory_capacity -= previous_value
                current_image.current_cell.tile.inventory_capacity += new_value
            else:
                current_image.current_cell.tile.inventory_capacity = self.images[0].current_cell.tile.inventory_capacity
            current_index += 1
            
    def touching_mouse(self):
        '''
        Description:
            Returns whether any of this building's images is colliding with the mouse
        Input:
            None
        Output:
            boolean: Returns True if any of this building's images is colliding with the mouse, otherwise returns False
        '''
        for current_image in self.images:
            if current_image.change_with_other_images: #don't show tooltips for road connection images, only the base road building images
                if current_image.Rect.collidepoint(pygame.mouse.get_pos()): #if mouse is in image
                    if not (current_image.grid == self.global_manager.get('minimap_grid') and not current_image.grid.is_on_mini_grid(self.x, self.y)): #do not consider as touching mouse if off-map
                        return(True)
        return(False)

    def get_build_cost(self):
        '''
        Description:
            Returns the total cost of building this building and all of its upgrades, not accounting for failed attempts or terrain
        Input:
            None
        Output:
            double: Returns the total cost of building this building and all of its upgrades, not accounting for failed attempts or terrain
        '''
        return(self.global_manager.get('building_prices')[self.building_type])

    def get_repair_cost(self):
        '''
        Description:
            Returns the cost of repairing this building, not accounting for failed attempts. Repair cost if half of total build cost
        Input:
            None
        Output:
            double: Returns the cost of repairing this building, not accounting for failed attempts
        '''
        return(self.get_build_cost() / 2)

class infrastructure_building(building):
    '''
    Building that eases movement between tiles and is a road or railroad. Has images that show connections with other tiles that have roads or railroads
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
                'name': string value - Required if from save, this building's name
                'infrastructure_type': string value - Type of infrastructure, like 'road', or 'railroad'
                'modes': string list value - Game modes during which this building's images can appear
                'contained_work_crews': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each work crew working in this building
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.infrastructure_type = input_dict['infrastructure_type']
        if self.infrastructure_type == 'railroad':
            self.is_road = False
            self.is_railroad = True
        elif self.infrastructure_type == 'road':
            self.is_railroad = False
            self.is_road = True
        input_dict['building_type'] = 'infrastructure'
        super().__init__(from_save, input_dict, global_manager)
        self.image_dict['left_road'] = 'buildings/infrastructure/left_road.png'
        self.image_dict['right_road'] = 'buildings/infrastructure/right_road.png'
        self.image_dict['down_road'] = 'buildings/infrastructure/down_road.png'
        self.image_dict['up_road'] = 'buildings/infrastructure/up_road.png'
        self.image_dict['left_railroad'] = 'buildings/infrastructure/left_railroad.png'
        self.image_dict['right_railroad'] = 'buildings/infrastructure/right_railroad.png'
        self.image_dict['down_railroad'] = 'buildings/infrastructure/down_railroad.png'
        self.image_dict['up_railroad'] = 'buildings/infrastructure/up_railroad.png'
        self.image_dict['empty'] = 'misc/empty.png'
        self.infrastructure_connection_images = {}
        for current_grid in self.grids:
            up_image = images.infrastructure_connection_image(self, current_grid.get_cell_width(), current_grid.get_cell_height(), current_grid, 'default', 'up', self.global_manager)
            down_image = images.infrastructure_connection_image(self, current_grid.get_cell_width(), current_grid.get_cell_height(), current_grid, 'default', 'down', self.global_manager)
            right_image = images.infrastructure_connection_image(self, current_grid.get_cell_width(), current_grid.get_cell_height(), current_grid, 'default', 'right', self.global_manager)
            left_image = images.infrastructure_connection_image(self, current_grid.get_cell_width(), current_grid.get_cell_height(), current_grid, 'default', 'left', self.global_manager)
            #actor, width, height, grid, image_description, direction, global_manager
            self.images.append(up_image)
            self.images.append(down_image)
            self.images.append(right_image)
            self.images.append(left_image)
            self.infrastructure_connection_images['up'] = up_image
            self.infrastructure_connection_images['down'] = down_image
            self.infrastructure_connection_images['right'] = right_image
            self.infrastructure_connection_images['left'] = left_image
        actor_utility.update_roads(self.global_manager)

    def to_save_dict(self):
        '''
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                Along with superclass outputs, also saves the following values:
                'infrastructure_type': string value - Type of infrastructure, like 'road' or 'railroad'
        '''
        save_dict = super().to_save_dict()
        save_dict['infrastructure_type'] = self.infrastructure_type
        return(save_dict)

    def can_damage(self):
        '''
        Description:
            Returns whether this building is able to be damaged. Roads, railroads, and slums cannot be damaged
        Input:
            None
        Output:
            boolean: Returns whether this building is able to be damaged
        '''
        return(False)

class trading_post(building):
    '''
    Building in a village that increases success chance of trading
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
                'name': string value - Required if from save, this building's name
                'modes': string list value - Game modes during which this building's images can appear
                'contained_work_crews': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each work crew working in this building
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['building_type'] = 'trading_post'
        super().__init__(from_save, input_dict, global_manager)

class mission(building):
    '''
    Building in village that increases success chance of conversion
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
                'name': string value - Required if from save, this building's name
                'modes': string list value - Game modes during which this building's images can appear
                'contained_work_crews': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each work crew working in this building
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['building_type'] = 'mission'
        super().__init__(from_save, input_dict, global_manager)

class fort(building):
    '''
    Building that grants a +1 combat modifier to your units fighting in its tile
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
                'name': string value - Required if from save, this building's name
                'modes': string list value - Game modes during which this building's images can appear
                'contained_work_crews': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each work crew working in this building
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['building_type'] = 'fort'
        super().__init__(from_save, input_dict, global_manager)

class train_station(building):
    '''
    Building along a railroad that allows the construction of train, allows trains to pick up and drop off cargo/passengers, and increases the tile's inventory capacity
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
                'name': string value - Required if from save, this building's name
                'modes': string list value - Game modes during which this building's images can appear
                'contained_work_crews': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each work crew working in this building
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['building_type'] = 'train_station'
        super().__init__(from_save, input_dict, global_manager)

class port(building):
    '''
    Building adjacent to water that allows steamships/steamboats to enter the tile, allows ships to travel to this tile if it is along the ocean, and increases the tile's inventory capacity
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
                'name': string value - Required if from save, this building's name
                'modes': string list value - Game modes during which this building's images can appear
                'contained_work_crews': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each work crew working in this building
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['building_type'] = 'port'
        super().__init__(from_save, input_dict, global_manager)
        self.is_port = True #used to determine if port is in a tile to move there

class warehouses(building):
    '''
    Buiding attached to a port, train station, and/or resource production facility that stores commodities
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
                'name': string value - Required if from save, this building's name
                'modes': string list value - Game modes during which this building's images can appear
                'contained_work_crews': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each work crew working in this building
                'warehouse_level': int value - Required if from save, size of warehouse (9 inventory capacity per level)
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['building_type'] = 'warehouses'
        self.warehouse_level = 1
        super().__init__(from_save, input_dict, global_manager)
        self.set_default_inventory_capacity(9)
        if from_save:
            while self.warehouse_level < input_dict['warehouse_level']:
                self.upgrade()
                
        if global_manager.get('DEBUG_damaged_buildings'):
            if self.can_damage():
                self.set_damaged(True, True)
                
    def to_save_dict(self):
        '''
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                Along with superclass outputs, also saves the following values:
                'warehouse_level': int value - Size of warehouse (9 inventory capacity per level)
        '''
        save_dict = super().to_save_dict()
        save_dict['warehouse_level'] = self.warehouse_level
        return(save_dict)

    def can_upgrade(self, upgrade_type = 'warehouse_level'):
        '''
        Description:
            Returns whether this building can be upgraded in the inputted field. Warehouses can be upgraded infinitely
        Input:
            string upgrade_type = 'warehosue_level': Represents type of upgrade, like 'scale' or 'efficiency'
        Output:
            boolean: Returns True if this building can be upgraded in the inputted field, otherwise returns False
        '''
        return(True)

    def get_upgrade_cost(self):
        '''
        Description:
            Returns the cost of the next upgrade for this building. The first successful upgrade costs 5 money and each subsequent upgrade costs twice as much as the previous. Building a train station, resource production facility, or
                port gives a free upgrade that does not affect the costs of future upgrades
        Input:
            None
        Output:
            None
        '''
        return(self.images[0].current_cell.get_warehouses_cost())

    def upgrade(self, upgrade_type = 'warehouse_level'):
        self.warehouse_level += 1
        self.set_default_inventory_capacity(self.default_inventory_capacity + 9)

class resource_building(building):
    '''
    Building in a resource tile that allows work crews to attach to this building to produce commodities over time
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
                'name': string value - Required if from save, this building's name
                'resource_type': string value - Type of resource produced by this building, like 'exotic wood'
                'modes': string list value - Game modes during which this building's images can appear
                'contained_work_crews': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each work crew working in this building
                'scale': int value - Required if from save, maximum number of work crews that can be attached to this building
                'efficiency': int value - Required if from save, number of rolls made by work crews each turn to produce commodities at this building
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.resource_type = input_dict['resource_type']
        input_dict['building_type'] = 'resource'
        self.scale = 1
        self.efficiency = 1
        self.num_upgrades = 0
        self.ejected_work_crews = []
        super().__init__(from_save, input_dict, global_manager)
        global_manager.get('resource_building_list').append(self)
        if from_save:
            while self.scale < input_dict['scale']:
                self.upgrade('scale')
            while self.efficiency < input_dict['efficiency']:
                self.upgrade('efficiency')

    def to_save_dict(self):
        '''
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                Along with superclass outputs, also saves the following values:
                'contained_work_crews': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each work crew working in this building
                'resource_type': string value - Type of resource produced by this building, like 'exotic wood'
                'scale': int value - Maximum number of work crews that can be attached to this building
                'efficiency': int value - Number of rolls made by work crews each turn to produce commodities at this building
        '''
        save_dict = super().to_save_dict()
        save_dict['resource_type'] = self.resource_type
        save_dict['scale'] = self.scale
        save_dict['efficiency'] = self.efficiency
        return(save_dict)

    def eject_work_crews(self):
        '''
        Description:
            Removes this building's work crews
        Input:
            None
        Output:
            None
        '''
        #self.ejected_work_crews = []
        for current_work_crew in self.contained_work_crews:
            if not current_work_crew in self.ejected_work_crews:
                self.ejected_work_crews.append(current_work_crew)
        for current_work_crew in self.ejected_work_crews:
            current_work_crew.leave_building(self)

    def set_damaged(self, new_value, mid_setup = False):
        '''
        Description:
            Repairs or damages this building based on the inputted value. A damaged building still provides attrition resistance but otherwise loses its specialized capabilities. A damaged resource building ejects its work crews when
                damaged
        Input:
            boolean new_value: New damaged/undamaged state of the building
        Output:
            None
        '''
        if new_value == True:
            self.eject_work_crews()
        super().set_damaged(new_value, mid_setup)

    def reattach_work_crews(self):
        '''
        Description:
            After combat is finished, returns any surviving work crews to this building, if possible
        Input:
            None
        Output:
            None
        '''
        for current_work_crew in self.ejected_work_crews:
            if current_work_crew in self.global_manager.get('pmob_list'): #if not dead
                current_work_crew.work_building(self)
        self.ejected_work_crews = []

    def remove(self):
        '''
        Description:
            Removes this object from relevant lists, prevents it from further appearing in or affecting the program, and removes it from the tiles it occupies
        Input:
            None
        Output:
            None
        '''
        self.global_manager.set('resource_building_list', utility.remove_from_list(self.global_manager.get('resource_building_list'), self))
        super().remove()

    def manage_health_attrition(self, current_cell = 'default'):
        '''
        Description:
            Checks this building's work crews for health attrition each turn
        Input:
            string/cell current_cell = 'default': Records which cell the attrition is taking place in, used when a unit is in a building or another mob and does not technically exist in any cell
        Output:
            None
        '''
        if current_cell == 'default':
            current_cell = self.images[0].current_cell
        transportation_minister = self.global_manager.get('current_ministers')[self.global_manager.get('type_minister_dict')['transportation']]
        
        for current_work_crew in self.contained_work_crews:
            if current_cell.local_attrition():
                if transportation_minister.no_corruption_roll(6) == 1 or self.global_manager.get('DEBUG_boost_attrition'):
                    current_work_crew.attrition_death('officer')
            if current_cell.local_attrition():
                if transportation_minister.no_corruption_roll(6) == 1 or self.global_manager.get('DEBUG_boost_attrition'):
                    worker_type = current_work_crew.worker.worker_type
                    if (not worker_type in ['African', 'slave']) or random.randrange(1, 7) == 1:
                        current_work_crew.attrition_death('worker')

    def can_upgrade(self, upgrade_type):
        '''
        Description:
            Returns whether this building can be upgraded in the inputted field. A building can be upgraded not be ugpraded above 6 in a field
        Input:
            string upgrade_type: Represents type of upgrade, like 'scale' or 'efficiency'
        Output:
            boolean: Returns True if this building can be upgraded in the inputted field, otherwise returns False
        '''
        if upgrade_type == 'scale': #quantitative
            if self.scale < 6:
                return(True)
        elif upgrade_type == 'efficiency':
            if self.efficiency < 6:
                return(True)
        return(False)

    def upgrade(self, upgrade_type):
        '''
        Description:
            Upgrades this building in the inputted field, such as by increasing the building's efficiency by 1 when 'efficiency' is inputted
        Input:
            string upgrade_type: Represents type of upgrade, like 'scale' or 'effiency'
        Output:
            None
        '''
        if upgrade_type == 'scale':
            self.scale += 1
        elif upgrade_type == 'efficiency':
            self.efficiency += 1
        self.num_upgrades += 1

    def get_upgrade_cost(self):
        '''
        Description:
            Returns the cost of the next upgrade for this building. The first successful upgrade costs 20 money and each subsequent upgrade costs twice as much as the previous
        Input:
            None
        Output:
            None
        '''
        return(self.global_manager.get('base_upgrade_price') * (2 ** self.num_upgrades)) #20 for 1st upgrade, 40 for 2nd, 80 for 3rd, etc.

    def get_build_cost(self):
        '''
        Description:
            Returns the total cost of building this building, including all of its upgrades but not failed attempts or terrain
        Input:
            None
        Output:
            double: Returns the total cost of building this building
        '''
        cost = super().get_build_cost()
        for i in range(0, self.num_upgrades): #adds cost of each upgrade, each of which is more expensive than the last
            cost += (self.global_manager.get('base_upgrade_price') * (i + 1))
        return(cost)
    
    def produce(self):
        '''
        Description:
            Orders each work crew attached to this building to attempt producing commodities at the end of a turn. Based on work crew experience and minister skill/corruption, each work crew can produce a number of commodities up to the
                building's efficiency
        Input:
            None
        Output:
            None
        '''
        for current_work_crew in self.contained_work_crews:
            current_work_crew.attempt_production(self)

class slums(building):
    '''
    Building automatically formed by unemployed workers and freed slaves around places of employment
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
                'name': string value - Required if from save, this building's name
                'building_type': string value - Type of building, like 'port'
                'modes': string list value - Game modes during which this building's images can appear
                'contained_work_crews': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each work crew working in this building
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        global_manager.get('slums_list').append(self)
        input_dict['building_type'] = 'slums'
        self.available_workers = 0
        if from_save:
            self.available_workers = input_dict['available_workers']
        input_dict['image'] = 'buildings/slums/default.png'
        super().__init__(from_save, input_dict, global_manager)
        self.image_dict['default'] = 'buildings/slums/default.png'
        self.image_dict['small'] = 'buildings/slums/small.png'
        self.image_dict['medium'] = 'buildings/slums/default.png'
        self.image_dict['large'] = 'buildings/slums/large.png'
        if self.images[0].current_cell.tile == self.global_manager.get('displayed_tile'):
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.images[0].current_cell.tile) #show self after creation
        self.update_slums_image()
        
    def update_slums_image(self):
        '''
        Description:
            Updates the image of this slum when its population changes to reflect the new size
        Input:
            None
        Output:
            None
        '''
        if self.available_workers <= 2:
            self.set_image('small')
        elif self.available_workers <= 5:
            self.set_image('medium')
        else:
            self.set_image('large')

    def can_damage(self):
        '''
        Description:
            Returns whether this building is able to be damaged. Roads, railroads, and slums cannot be damaged
        Input:
            None
        Output:
            boolean: Returns whether this building is able to be damaged
        '''
        return(False)

    def remove(self):
        '''
        Description:
            Removes this object from relevant lists, prevents it from further appearing in or affecting the program, and removes it from the tiles it occupies
        Input:
            None
        Output:
            None
        '''
        super().remove()
        self.global_manager.set('slums_list', utility.remove_from_list(self.global_manager.get('slums_list'), self))

    def change_population(self, change):
        '''
        Description:
            Changes this slum's population by the inputted amount. Updates the tile info display as applicable and destroys the slum if its population reaches 0
        Input:
            int change: amount this slum's population is changed by
        Output:
            None
        '''
        self.available_workers += change
        if self.available_workers < 0:
            self.available_workers = 0
        self.update_slums_image()
        if self.images[0].current_cell.tile == self.global_manager.get('displayed_tile'): #if being displayed, change displayed population value
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.images[0].current_cell.tile)
        if self.available_workers == 0:
            self.remove()
            
    def recruit_worker(self):
        '''
        Description:
            Hires one of this slum's available workers by creating a worker, reducing the slum's population
        Input:
            None
        Output:
            None
        '''
        input_dict = {}
        input_dict['coordinates'] = (self.images[0].current_cell.x, self.images[0].current_cell.y)
        input_dict['grids'] = [self.images[0].current_cell.grid, self.images[0].current_cell.grid.mini_grid]
        input_dict['image'] = 'mobs/African workers/default.png'
        input_dict['modes'] = ['strategic']
        input_dict['name'] = 'African workers'
        input_dict['init_type'] = 'workers'
        input_dict['worker_type'] = 'African'
        self.global_manager.get('actor_creation_manager').create(False, input_dict, self.global_manager)
        self.change_population(-1)

    def to_save_dict(self):
        '''
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                Along with superclass outputs, also saves the following values:
                'available_workers': int value - Number of unemployed workers in this slum
        '''
        save_dict = super().to_save_dict()
        save_dict['available_workers'] = self.available_workers
        return(save_dict)
