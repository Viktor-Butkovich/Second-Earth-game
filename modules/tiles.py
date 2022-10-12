#Contains functionality for tiles and other cell icons

import pygame
import random

from . import images
from . import utility
from . import actor_utility
from . import villages
from .actors import actor

class tile(actor): #to do: make terrain tiles a subclass
    '''
    An actor that appears under other actors and occupies a grid cell, being able to act as a passive icon, resource, terrain, or a hidden area
    '''
    def __init__(self, from_save, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'grid': grid value - grid in which this tile can appear
                'image': string value - File path to the image used by this object
                'name': string value - This tile's name
                'modes': string list value - Game modes during which this actor's images can appear
                'show_terrain': boolean value - True if this tile shows a cell's terrain. False if it does not show terrain, like a veteran icon or resource icon
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.actor_type = 'tile'
        self.selection_outline_color = 'yellow'#'bright blue'
        self.actor_match_outline_color = 'white'
        input_dict['grids'] = [input_dict['grid']] #give actor a 1-item list of grids as input
        super().__init__(from_save, input_dict, global_manager)
        self.set_name(input_dict['name'])
        self.global_manager.get('tile_list').append(self)
        self.image_dict = {'default': input_dict['image']}
        self.image = images.tile_image(self, self.grid.get_cell_width(), self.grid.get_cell_height(), input_dict['grid'], 'default', global_manager)
        self.images = [self.image] #tiles only appear on 1 grid, but have a list of images defined to be more consistent with other actor subclasses
        self.show_terrain = input_dict['show_terrain']
        self.cell = self.grid.find_cell(self.x, self.y)
        if self.show_terrain:
            self.cell.tile = self
            self.resource_icon = 'none' #the resource icon is appearance, making it a property of the tile rather than the cell
            self.set_terrain(self.cell.terrain) #terrain is a property of the cell, being stored information rather than appearance, same for resource, set these in cell
            self.image_dict['hidden'] = 'scenery/paper_hidden.png'
            self.set_visibility(self.cell.visible)
            self.can_hold_commodities = True
            self.inventory_setup()
            if self.cell.grid.from_save: #load in saved inventory from cell
                self.load_inventory(self.cell.save_dict['inventory'])
        elif self.name in ['Europe', 'Slave traders']: #abstract grid's tile has the same name as the grid, and Europe should be able to hold commodities despite not being terrain
            self.cell.tile = self
            self.resource_icon = 'none' #the resource icon is appearance, making it a property of the tile rather than the cell
            self.image_dict['hidden'] = 'scenery/paper_hidden.png'
            self.set_visibility(self.cell.visible)
            self.can_hold_commodities = True
            self.can_hold_infinite_commodities = True
            self.inventory_setup()
            self.terrain = 'none'
            if self.cell.grid.from_save: #load in saved inventory from cell
                self.load_inventory(self.cell.save_dict['inventory'])
        elif self.name == 'resource icon':
            self.image_dict['hidden'] = 'misc/empty.png'
        else:
            self.terrain = 'none'
        self.update_tooltip()

    def update_resource_icon(self): #changes size of resource icon if building present
        '''
        Description:
            Reduces the size of this tile's resouce icon when a building is present, allowing more icons to be shown on the tile at once
        Input:
            None
        Output:
            None
        '''
        if not self.resource_icon == 'none':
            self.resource_icon.update_resource_icon()
            equivalent_tile = self.get_equivalent_tile()
            if (not equivalent_tile == 'none') and (not equivalent_tile.resource_icon == 'none'):
                equivalent_tile.resource_icon.update_resource_icon()

    def draw_destination_outline(self, color = 'default'): #called directly by mobs
        '''
        Description:
            Draws an outline around this tile when the displayed mob has a pending movement order to move to this tile
        Input:
            string color = 'default': If an input is given, that color from the color_dict will be used instead of the default destination outline color
        Output:
            None
        '''
        for current_image in self.images:
            outline = self.cell.Rect
            if color == 'default':
                color = self.global_manager.get('color_dict')[self.selection_outline_color]
            else:
                color = self.global_manager.get('color_dict')[color] #converts input string to RGB tuple
            pygame.draw.rect(self.global_manager.get('game_display'), color, (outline), current_image.outline_width)

    def draw_actor_match_outline(self, called_by_equivalent):
        '''
        Description:
            Draws an outline around the displayed tile. If the tile is shown on a minimap, tells the equivalent tile to also draw an outline around the displayed tile
        Input:
            boolean called_by_equivalent: True if this function is being called by the equivalent tile on either the minimap grid or the strategaic map grid, otherwise False. Prevents infinite loops of equivalent tiles repeatedly
                calling each other
        Output:
            None
        '''
        if self.images[0].can_show():
            for current_image in self.images:
                outline = self.cell.Rect
                pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')[self.actor_match_outline_color], (outline), current_image.outline_width)
                equivalent_tile = self.get_equivalent_tile()
                if (not equivalent_tile == 'none') and (not called_by_equivalent):
                    equivalent_tile.draw_actor_match_outline(True)

    def remove_excess_inventory(self):
        '''
        Description:
            Removes random excess commodities from this tile until the number of commodities fits in this tile's inventory capacity
        Input:
            None
        Output:
            None
        '''
        if self.can_hold_commodities and not self.can_hold_infinite_commodities:
            inventory_used = self.get_inventory_used()
            amount_to_remove = inventory_used - self.inventory_capacity
            if amount_to_remove > 0:
                commodity_types = self.get_held_commodities()
                amount_removed = 0
                while amount_removed < amount_to_remove:
                    commodity_removed = random.choice(commodity_types)
                    if self.get_inventory(commodity_removed) > 0:
                        self.change_inventory(commodity_removed, -1)
                        amount_removed += 1
        
    def change_inventory(self, commodity, change):
        '''
        Description:
            Changes the number of commodities of a certain type held by this tile. Also ensures that the tile info display is updated correctly
        Input:
            string commodity: Type of commodity to change the inventory of
            int change: Amount of commodities of the inputted type to add. Removes commodities of the inputted type if negative
        Output:
            None
        '''
        if self.can_hold_commodities:
            self.inventory[commodity] += change
            if not self.grid.attached_grid == 'none': #only get equivalent if there is an attached grid
                self.get_equivalent_tile().inventory[commodity] += change #doesn't call other tile's function to avoid recursion
            if self.global_manager.get('displayed_tile') == self or self.global_manager.get('displayed_tile') == self.get_equivalent_tile():
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self)

    def set_inventory(self, commodity, new_value):
        '''
        Description:
            Sets the number of commodities of a certain type held by this tile. Also ensures that the tile info display is updated correctly
        Input:
            string commodity: Type of commodity to set the inventory of
            int new_value: Amount of commodities of the inputted type to set inventory to
        Output:
            None
        '''
        if self.can_hold_commodities:
            self.inventory[commodity] = new_value
            if not self.grid.attached_grid == 'none': #only get equivalent if there is an attached grid
                self.get_equivalent_tile.inventory[commodity] = new_value
            if self.global_manager.get('displayed_tile') == self or self.global_manager.get('displayed_tile') == self.get_equivalent_tile():
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self)

    def get_main_grid_coordinates(self):
        '''
        Description:
            Returns the coordinates cooresponding to this tile on the strategic map grid. If this tile is already on the strategic map grid, just returns this tile's coordinates
        Input:
            None
        Output:
            int tuple: Two 
        '''
        if self.grid.is_mini_grid:
            return(self.grid.get_main_grid_coordinates(self.x, self.y))
        else:
            return((self.x, self.y))

    def get_equivalent_tile(self):
        '''
        Description:
            Returns the corresponding minimap tile if this tile is on the strategic map grid or vice versa
        Input:
            None
        Output:
            tile: tile on the corresponding tile on the grid attached to this tile's grid
        '''
        if self.grid == self.global_manager.get('minimap_grid'):
            main_x, main_y = self.grid.get_main_grid_coordinates(self.x, self.y)
            attached_cell = self.grid.attached_grid.find_cell(main_x, main_y)
            if not attached_cell == 'none':
                return(attached_cell.tile)
            return('none')
        elif self.grid == self.global_manager.get('strategic_map_grid'):
            mini_x, mini_y = self.grid.mini_grid.get_mini_grid_coordinates(self.x, self.y)
            equivalent_cell = self.grid.mini_grid.find_cell(mini_x, mini_y)
            if not equivalent_cell == 'none':
                return(equivalent_cell.tile)
            else:
                return('none')
        return('none')
            
    def set_visibility(self, new_visibility):
        '''
        Description:
            Sets the visibility of this tile to the inputted value. A visible tile's terrain and resource can be seen by the player.
        Input:
            boolean new_visibility: This tile's new visibility status
        Output:
            None
        '''
        if new_visibility == True:
            image_name = 'default'
        else:
            image_name = 'hidden'
        self.image.set_image(image_name)
        self.image.previous_idle_image = image_name
        if not self.resource_icon == 'none':
            self.resource_icon.image.set_image(image_name)
            self.resource_icon.image.previous_idle_image = image_name
            
    def set_resource(self, new_resource):
        '''
        Description:
            Sets the resource type of this tile to the inputted value, removing or creating resource icons as needed
        Input:
            string new_resource: The new resource type of this tile, like 'exotic wood'
        Output:
            None
        '''
        if not self.resource_icon == 'none':
            self.resource_icon.remove()
            self.resource_icon = 'none'
        self.resource = new_resource
        if not new_resource == 'none':
            if self.resource == 'natives':
                equivalent_tile = self.get_equivalent_tile()
                village_exists = False
                if not equivalent_tile == 'none':
                    if not equivalent_tile.cell.village == 'none': #if equivalent tile present and equivalent tile has village, copy village to equivalent instead of creating new one
                        village_exists = True
                        self.cell.village = equivalent_tile.cell.village
                        self.cell.village.tiles.append(self)
                        if self.cell.grid.is_mini_grid: #set main cell of village to one on strategic map grid, as opposed to the mini map
                            self.cell.village.cell = equivalent_tile.cell
                        else:
                            self.cell.village.cell = self.cell
                if not village_exists: #make new village if village not present
                    input_dict = {'cell': self.cell}
                    if self.cell.grid.from_save:
                        input_dict['name'] = self.cell.save_dict['village_name']
                        input_dict['population'] = self.cell.save_dict['village_population']
                        input_dict['aggressiveness'] = self.cell.save_dict['village_aggressiveness']
                        input_dict['available_workers'] = self.cell.save_dict['village_available_workers']
                        input_dict['attached_warriors'] = self.cell.save_dict['village_attached_warriors']
                        self.cell.village = villages.village(True, input_dict, self.global_manager)
                        self.cell.village.tiles.append(self)
                    else:
                        self.cell.village = villages.village(False, input_dict, self.global_manager)
                        self.cell.village.tiles.append(self)
                    
            input_dict = {}
            input_dict['coordinates'] = (self.x, self.y)
            input_dict['grid'] = self.grid
            input_dict['resource'] = self.cell.resource
            input_dict['name'] = 'resource icon'
            input_dict['modes'] = ['strategic']
            input_dict['show_terrain'] = False
            input_dict['attached_tile'] = self
            self.resource_icon = resource_icon(False, input_dict, self.global_manager)
        self.set_visibility(self.cell.visible)
            
    def set_terrain(self, new_terrain): #to do, add variations like grass to all terrains
        '''
        Description:
            Sets the terrain type of this tile to the inputted value, changing its appearance as needed
        Input:
            string new_terrain: The new terrain type of this tile, like 'swamp'
        Output:
            None
        '''
        if new_terrain == 'clear':
            self.image_dict['default'] = 'scenery/terrain/clear.png'
            
        elif new_terrain == 'hills':
            self.image_dict['default'] = 'scenery/terrain/hills.png'
            
        elif new_terrain == 'jungle':
            self.image_dict['default'] = 'scenery/terrain/jungle.png'
            
        elif new_terrain == 'water':
            current_y = self.y
            if self.cell.grid.is_mini_grid:
                current_y = self.cell.grid.get_main_grid_coordinates(self.x, self.y)[1]
                
            if current_y == 0:
                self.image_dict['default'] = 'scenery/terrain/ocean_water.png'
            else:
                self.image_dict['default'] = 'scenery/terrain/river_water.png'
            
        elif new_terrain == 'mountain':
            self.image_dict['default'] = 'scenery/terrain/mountain.png'
            
        elif new_terrain == 'swamp':
            self.image_dict['default'] = 'scenery/terrain/swamp.png'
            
        elif new_terrain == 'desert':
            self.image_dict['default'] = 'scenery/terrain/desert.png'

        elif new_terrain == 'none':
            self.image_dict['default'] = 'scenery/hidden.png'

        self.image.set_image('default')

    def update_tooltip(self):
        '''
        Description:
            Sets this tile's tooltip to what it should be whenever the player looks at the tooltip. If this tile is explored, sets tooltip to this tile's terrain and its resource, if any. Otherwise, sets tooltip to a description of how
                this tile has not explored
        Input:
            None
        Output:
            None
        '''
        if self.show_terrain: #if is terrain, show tooltip
            tooltip_message = []
            if self.cell.visible:
                if self.cell.terrain == 'water':
                    current_y = self.y
                    if self.cell.grid.is_mini_grid:
                        current_y = self.cell.grid.get_main_grid_coordinates(self.x, self.y)[1]
                    if current_y == 0:
                        tooltip_message.append('This is an ocean water tile')
                    else:
                        tooltip_message.append('This is a river water tile')
                else:
                    tooltip_message.append('This is ' + utility.generate_article(self.cell.terrain) + ' ' + self.cell.terrain + ' tile')
                if not self.cell.village == 'none': #if village present, show village
                    tooltip_message += self.cell.village.get_tooltip()
                elif not self.cell.resource == 'none': #if not village but other resource present, show resource
                    tooltip_message.append('This tile has ' + utility.generate_article(self.cell.resource) + ' ' + self.cell.resource + ' resource')
            else:
                tooltip_message .append('This tile has not been explored')
            self.set_tooltip(tooltip_message)
        else:
            self.set_tooltip([])

    def set_coordinates(self, x, y):
        '''
        Description:
            Sets this tile's grid coordinates to the inputted values
        Input:
            int x: new grid x coordinate
            int y: new grid y coordinate
        Output:
            None
        '''
        self.x = x
        self.y = y
                
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
        self.global_manager.set('tile_list', utility.remove_from_list(self.global_manager.get('tile_list'), self))
        self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), self.image)) #to do: see if this can be removed, should already be in actor

    def can_show_tooltip(self): #only terrain tiles have tooltips
        '''
        Description:
            Returns whether this tile's tooltip can be shown. Along with the superclass' requirements, only terrain tiles have tooltips and tiles outside of the strategic map boundaries on the minimap grid do not have tooltips
        Input:
            None
        Output:
            None
        '''
        if self.show_terrain == True:
            if self.touching_mouse() and self.global_manager.get('current_game_mode') in self.modes: #and not targeting_ability
                if self.cell.terrain == 'none':
                    return(False)
                else:
                    return(True)
            else:
                return(False)
        else:
            return(False)

class abstract_tile(tile):
    '''
    tile for 1-cell abstract grids like Europe, can have a tooltip but has no terrain, instead having a unique image
    '''
    def __init__(self, from_save, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'grid': grid value - grid in which this tile can appear
                'image': string value - File path to the image used by this object
                'name': string value - This tile's name
                'modes': string list value - Game modes during which this actor's images can appear
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['coordinates'] = (0, 0)
        input_dict['show_terrain'] = False
        super().__init__(from_save, input_dict, global_manager)

    def update_tooltip(self):
        '''
        Description:
            Sets this tile's tooltip to what it should be whenever the player looks at the tooltip. An abstract tile's tooltip is its name
        Input:
            None
        Output:
            None
        '''
        self.set_tooltip([self.name])

    def can_show_tooltip(self):
        '''
        Description:
            Returns whether this tile's tooltip can be shown. Has default tooltip requirements of being visible and touching the mosue
        Input:
            None
        Output:
            None
        '''
        if self.touching_mouse() and self.global_manager.get('current_game_mode') in self.modes:
            return(True)
        else:
            return(False)

class resource_icon(tile):
    '''
    tile that appears above a terrain tile that has a resource and reflects the terrain tile's resource. Changes in size when buildings are built in its attached tile to allow more icons to be visible
    '''
    def __init__(self, from_save, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'grid': grid value - grid in which this tile can appear
                'image': string value - File path to the image used by this object
                'name': string value - This tile's name
                'modes': string list value - Game modes during which this actor's images can appear
                'show_terrain': boolean value - True if this tile shows a cell's terrain. False if it does not show terrain, like a veteran icon or resource icon
                'attached_tile': tile value - Terrain tile whose resource is represented by this tile
                'resource': string value - Type of resource represented by this tile, like 'exotic wood'
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.attached_tile = input_dict['attached_tile']
        self.resource = input_dict['resource']
        default_image_id = 'scenery/resources/' + self.resource + '.png'
        small_image_id = 'scenery/resources/small/' + self.resource + '.png'
        input_dict['image'] = default_image_id
        super().__init__(from_save, input_dict, global_manager)
        self.image_dict['small'] = small_image_id
        self.image_dict['large'] = default_image_id
        self.update_resource_icon()

    def update_resource_icon(self):
        '''
        Description:
            Changes this resource icon's size when buildings are built in its attached tile to allow more icons to be visible. Also reflects the size of the native village if this icon represents a village
        Input:
            None
        '''
        if self.resource == 'natives':
            attached_village = self.attached_tile.cell.get_building('village')
            if attached_village.population == 0: #0
                key = '0'
            elif attached_village.population <= 3: #1-3
                key = '1'
            elif attached_village.population <= 6: #4-6
                key = '2'
            else: #7-10
                key = '3'

            if attached_village.aggressiveness <= 3: #1-3
                key += '1'
            elif attached_village.aggressiveness <= 6: #4-6
                key += '2'
            else: #7-10
                key += '3'

            self.image_dict['small'] = 'scenery/resources/natives/small/' + key + '.png'
            self.image_dict['large'] = 'scenery/resources/natives/' + key + '.png'
        building_present = False
        for building_type in self.global_manager.get('building_types'):
            if self.attached_tile.cell.has_building(building_type): #if any building present
                self.image.set_image('small')
                self.image_dict['default'] = self.image_dict['small']
                building_present = True
                break
        if not building_present:
            self.image.set_image('large')
            self.image_dict['default'] = self.image_dict['large']

class status_icon(tile):
    '''
    A tile that follows one of the images of a unit, showing special statuses like veteran or disorganized
    '''
    def __init__(self, from_save, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'grid': grid value - grid in which this tile can appear
                'image': string value - File path to the image used by this object
                'name': string value - This tile's name
                'modes': string list value - Game modes during which this actor's images can appear
                'show_terrain': boolean value - True if this tile shows a cell's terrain. False if it does not show terrain, like a veteran icon or resource icon
                'actor': actor value - mob to which this icon is attached. Can be a group or an officer
                'status_icon_type': string value - type of status shown by icon, like veteran or disorganized
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(from_save, input_dict, global_manager)
        self.actor = input_dict['actor']
        self.status_icon_type = input_dict['status_icon_type']
        self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), self.image))
        self.image = images.veteran_icon_image(self, self.grid.get_cell_width(), self.grid.get_cell_height(), self.grid, 'default', global_manager)
        self.images = [self.image]
