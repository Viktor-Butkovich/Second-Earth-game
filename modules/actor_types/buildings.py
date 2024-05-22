# Contains functionality for buildings

import pygame
import random
from .actors import actor
from ..util import utility, scaling, actor_utility, text_utility
import modules.constants.constants as constants
import modules.constants.status as status


class building(actor):
    """
    Actor that exists in cells of multiple grids in front of tiles and behind mobs that cannot be clicked
    """

    def __init__(self, from_save, input_dict):
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'grids': grid list value - grids in which this mob's images can appear
                'image': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'name': string value - Required if from save, this building's name
                'building_type': string value - Type of building, like 'port'
                'modes': string list value - Game modes during which this building's images can appear
                'contained_work_crews': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each work crew working in this building
        Output:
            None
        """
        self.actor_type = "building"
        self.building_type = input_dict["building_type"]
        self.damaged = False
        super().__init__(from_save, input_dict)
        self.default_inventory_capacity = 0
        self.image_id = input_dict["image"]
        self.image_dict = {"default": input_dict["image"]}
        self.cell = self.grids[0].find_cell(self.x, self.y)
        status.building_list.append(self)
        self.set_name(input_dict["name"])
        self.contained_work_crews = []
        if from_save:
            for current_work_crew in input_dict["contained_work_crews"]:
                constants.actor_creation_manager.create(
                    True, current_work_crew
                ).work_building(self)
            if self.can_damage():
                self.set_damaged(input_dict["damaged"], True)

        if (not from_save) and self.can_damage():
            self.set_damaged(False, True)
        self.cell.contained_buildings[self.building_type] = self
        self.cell.tile.update_image_bundle()

        if (
            (not from_save)
            and input_dict["building_type"]
            in ["resource", "port", "train_station", "fort"]
            and not self.cell.settlement
        ):
            constants.actor_creation_manager.create(
                False,
                {"init_type": "settlement", "coordinates": (self.cell.x, self.cell.y)},
            )
        self.cell.tile.set_name(self.cell.tile.name)

        self.set_building_inventory_capacity(self.default_inventory_capacity)
        if constants.effect_manager.effect_active("damaged_buildings"):
            if self.can_damage():
                self.set_damaged(True, True)

    def to_save_dict(self):
        """
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
        """
        save_dict = super().to_save_dict()
        save_dict["building_type"] = self.building_type
        save_dict[
            "contained_work_crews"
        ] = (
            []
        )  # List of dictionaries for each work crew, on load a building creates all of its work crews and attaches them
        save_dict["image"] = self.image_dict["default"]
        save_dict["damaged"] = self.damaged
        for current_work_crew in self.contained_work_crews:
            save_dict["contained_work_crews"].append(current_work_crew.to_save_dict())
        return save_dict

    def can_damage(self):
        """
        Description:
            Returns whether this building is able to be damaged. Roads, railroads, and slums cannot be damaged
        Input:
            None
        Output:
            boolean: Returns whether this building is able to be damaged
        """
        return True

    def remove(self):
        """
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. Also removes this building from the tiles it occupies
        Input:
            None
        Output:
            None
        """
        self.cell.contained_buildings[self.building_type] = "none"
        super().remove()
        status.building_list = utility.remove_from_list(status.building_list, self)

    def update_tooltip(self):  # should be shown below mob tooltips
        """
        Description:
            Sets this image's tooltip to what it should be whenever the player looks at the tooltip. For buildings, sets tooltip to a description of the building
        Input:
            None
        Output:
            None
        """
        tooltip_text = [text_utility.remove_underscores(self.name.capitalize())]
        if self.building_type == "resource":
            tooltip_text.append(
                "Work crews: "
                + str(len(self.contained_work_crews))
                + "/"
                + str(self.scale)
            )
            for current_work_crew in self.contained_work_crews:
                tooltip_text.append("    " + current_work_crew.name)
            tooltip_text.append(
                "Lets "
                + str(self.scale)
                + " attached work crews each attempt to produce "
                + str(self.efficiency)
                + " units of "
                + self.resource_type
                + " each turn"
            )
        elif self.building_type == "port":
            tooltip_text.append("Allows ships to enter this tile")
            tooltip_text.append(
                "Steamboats and steamships can move between ports, but steamships can never move beyond coastal ports"
            )
        elif self.building_type == "infrastructure":
            if self.is_bridge:
                tooltip_text.append("Allows movement across the bridge")
                if self.is_railroad:
                    tooltip_text.append(
                        "Acts as a railroad between the tiles it connects"
                    )
                elif self.is_road:
                    tooltip_text.append("Acts as a road between the tiles it connects")
                    tooltip_text.append(
                        "Can be upgraded to a railroad bridge to allow trains to move through this tile"
                    )
                else:
                    tooltip_text.append(
                        "Allows walking for 2 movement points between the tiles it connects"
                    )
                    tooltip_text.append(
                        "Can be upgraded to a road bridge to act as a road through this tile"
                    )
            else:
                tooltip_text.append(
                    "Halves movement cost for units going to another tile with a road or railroad"
                )
                if self.is_railroad:
                    tooltip_text.append(
                        "Allows trains to move from this tile to other tiles that have railroads"
                    )
                else:
                    tooltip_text.append(
                        "Can be upgraded to a railroad to allow trains to move through this tile"
                    )
        elif self.building_type == "train_station":
            tooltip_text.append(
                "Allows construction gangs to build trains on this tile"
            )
            tooltip_text.append(
                "Allows trains to drop off or pick up cargo or passengers in this tile"
            )
        elif self.building_type == "slums":
            tooltip_text.append(
                "Contains "
                + str(self.available_workers)
                + " African workers in search of employment"
            )
        elif self.building_type == "trading_post":
            tooltip_text.append(
                "Increases the success chance of caravans trading with this tile's village"
            )
        elif self.building_type == "mission":
            tooltip_text.append(
                "Increases the success chance of missionaries converting this tile's village"
            )
        elif self.building_type == "fort":
            tooltip_text.append(
                "Grants a +1 combat modifier to your units fighting in this tile"
            )
        elif self.building_type == "warehouses":
            tooltip_text.append(
                "Level "
                + str(self.warehouse_level)
                + " warehouses allow an inventory capacity of "
                + str(9 * self.warehouse_level)
            )

        if self.damaged:
            tooltip_text.append(
                "This building is damaged and is currently not functional."
            )

        self.set_tooltip(tooltip_text)

    def set_tooltip(self, tooltip_text):
        """
        Description:
            Sets this building's tooltip to the inputted list, with each inputted list representing a line of the tooltip. Unlike most actors, buildings have no images and handle their own tooltips
        Input:
            string list new_tooltip: Lines for this image's tooltip
        Output:
            None
        """
        self.tooltip_text = tooltip_text
        tooltip_width = 10  # minimum tooltip width
        font = constants.fonts["default"]
        for text_line in tooltip_text:
            tooltip_width = max(
                tooltip_width, font.calculate_size(text_line) + scaling.scale_width(10)
            )
        tooltip_height = (font.size * len(tooltip_text)) + scaling.scale_height(5)
        self.tooltip_box = pygame.Rect(
            self.cell.tile.x, self.cell.y, tooltip_width, tooltip_height
        )
        self.tooltip_outline_width = 1
        self.tooltip_outline = pygame.Rect(
            self.cell.tile.x - self.tooltip_outline_width,
            self.cell.tile.y + self.tooltip_outline_width,
            tooltip_width + (2 * self.tooltip_outline_width),
            tooltip_height + (self.tooltip_outline_width * 2),
        )

    def set_damaged(self, new_value, mid_setup=False):
        """
        Description:
            Repairs or damages this building based on the inputted value. A damaged building still provides attrition resistance but otherwise loses its specialized capabilities
        Input:
            boolean new_value: New damaged/undamaged state of the building
        Output:
            None
        """
        self.damaged = new_value
        if self.building_type == "infrastructure":
            actor_utility.update_roads()
        if self.damaged:
            self.set_building_inventory_capacity(0)
        else:
            self.set_building_inventory_capacity(self.default_inventory_capacity)
        if (not mid_setup) and self.building_type in [
            "resource",
            "port",
            "train_station",
        ]:
            self.cell.get_building("warehouses").set_damaged(new_value)
        self.cell.tile.update_image_bundle()

    def set_default_inventory_capacity(self, new_value):
        """
        Description:
            Sets a new default inventory capacity for a building. A building's inventory capacity may differ from its default inventory capacity if it becomes damaged
        Input:
            int new_value: New default inventory capacity for the building
        Output:
            None
        """
        self.default_inventory_capacity = new_value
        self.set_building_inventory_capacity(new_value)

    def set_building_inventory_capacity(self, new_value):
        """
        Description:
            Sets a new current inventory capacity for a building. A building's inventory capacity may change when it is upgraded, damaged, or repaired
        Input:
            int/string new_value: New current inventory capacity for the building. 'default' sets the inventory capacity to its default amount
        Output:
            None
        """
        old_value = self.inventory_capacity
        if new_value == "default":
            self.inventory_capacity = self.default_inventory_capacity
        else:
            self.inventory_capacity = new_value
        self.contribute_local_inventory_capacity(old_value, new_value)

    def contribute_local_inventory_capacity(self, previous_value, new_value):
        """
        Description:
            Updates this building's tile's total inventory capacity based on changes to this buiding's current inventory capacity
        Input:
            int previous_value: Previous inventory capacity that had been used in the tile's total inventory capacity
            int new_value: New inventory capacity to be used in the tile's total inventory capacity
        Output:
            None
        """
        self.cell.tile.set_inventory_capacity(
            self.cell.tile.inventory_capacity + new_value - previous_value
        )

    def touching_mouse(self):
        """
        Description:
            Returns whether any tile containing this building is colliding with the mouse
        Input:
            None
        Output:
            boolean: Returns True if any of this building's images is colliding with the mouse, otherwise returns False
        """
        if self.cell.tile.touching_mouse() or (
            self.cell.tile.get_equivalent_tile() != "none"
            and self.cell.tile.get_equivalent_tile().touching_mouse()
        ):
            return True
        return False

    def get_build_cost(self):
        """
        Description:
            Returns the total cost of building this building and all of its upgrades, not accounting for failed attempts or terrain
        Input:
            None
        Output:
            double: Returns the total cost of building this building and all of its upgrades, not accounting for failed attempts or terrain
        """
        return constants.building_prices[self.building_type]

    def get_repair_cost(self):
        """
        Description:
            Returns the cost of repairing this building, not accounting for failed attempts. Repair cost if half of total build cost
        Input:
            None
        Output:
            double: Returns the cost of repairing this building, not accounting for failed attempts
        """
        return self.get_build_cost() / 2

    def get_image_id_list(self, override_values={}):
        """
        Description:
            Generates and returns a list this actor's image file paths and dictionaries that can be passed to any image object to display those images together in a particular order and
                orientation. Infrastructure buildings display connections between themselves and adjacent infrastructure buildings
        Input:
            None
        Output:
            list: Returns list of string image file paths, possibly combined with string key dictionaries with extra information for offset images
        """
        image_id = {"image_id": self.image_dict["default"]}
        relative_coordinates = {
            "fort": (-1, 1),
            "trading_post": (0, 1),
            "mission": (1, 1),
            "train_station": (0, -1),
            "port": (1, -1),
        }.get(self.building_type, (0, 0))
        if relative_coordinates == (0, 0):
            modifiers = {}
        else:  # If not centered, make smaller and move to one of 6 top/bottom slots
            modifiers = {
                "size": 0.75 * 0.45,
                "x_offset": relative_coordinates[0] * 0.33,
                "y_offset": relative_coordinates[1] * 0.33,
            }
        image_id.update(modifiers)
        return_list = [image_id]
        if self.building_type == "resource":
            return_list[0]["green_screen"] = constants.quality_colors[
                self.efficiency
            ]  # Set box to quality color based on efficiency
            return_list[0]["size"] = 0.6
            return_list[0]["level"] = image_id.get("level", 0) + 1
            for scale in range(1, self.scale + 1):
                scale_coordinates = {  # Place mine/camp/plantation icons in following order for each scale
                    1: (0, 1),  # top center
                    2: (-1, -1),  # bottom left
                    3: (1, -1),  # bottom right
                    4: (0, -1),  # bottom center
                    5: (-1, 1),  # top left
                    6: (1, 1),  # top right
                }
                if scale > len(self.contained_work_crews):
                    resource_image_id = (
                        "buildings/"
                        + constants.resource_building_dict[self.resource_type]
                        + "_no_work_crew.png"
                    )
                else:
                    resource_image_id = (
                        "buildings/"
                        + constants.resource_building_dict[self.resource_type]
                        + ".png"
                    )
                return_list.append(
                    {
                        "image_id": resource_image_id,
                        "size": return_list[0]["size"],
                        "level": return_list[0]["level"],
                        "x_offset": 0.12 * scale_coordinates[scale][0],
                        "y_offset": -0.07 + 0.07 * scale_coordinates[scale][1],
                    }
                )

        if self.building_type == "train_station":
            return_list.append(
                {"image_id": "buildings/infrastructure/down_railroad.png"}
            )
        if self.damaged and self.building_type != "warehouses":
            damaged_id = {"image_id": "buildings/damaged.png", "level": 3}
            damaged_id.update(modifiers)
            return_list.append(damaged_id)
        return return_list


class infrastructure_building(building):
    """
    Building that eases movement between tiles and is a road or railroad. Has images that show connections with other tiles that have roads or railroads
    """

    def __init__(self, from_save, input_dict):
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'grids': grid list value - grids in which this mob's images can appear
                'image': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'name': string value - Required if from save, this building's name
                'infrastructure_type': string value - Type of infrastructure, like 'road' or 'railroad'
                'modes': string list value - Game modes during which this building's images can appear
                'contained_work_crews': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each work crew working in this building
        Output:
            None
        """
        self.infrastructure_type = input_dict["infrastructure_type"]
        if self.infrastructure_type == "railroad":
            self.is_railroad = True
            self.is_road = False
            self.is_bridge = False
        elif self.infrastructure_type == "road":
            self.is_railroad = False
            self.is_road = True
            self.is_bridge = False
        elif self.infrastructure_type == "railroad_bridge":
            self.is_railroad = True
            self.is_road = False
            self.is_bridge = True
        elif self.infrastructure_type == "road_bridge":
            self.is_railroad = False
            self.is_road = True
            self.is_bridge = True
        elif self.infrastructure_type == "ferry":
            self.is_railroad = False
            self.is_road = False
            self.is_bridge = True

        input_dict["building_type"] = "infrastructure"
        self.connection_image_dict = {}
        for infrastructure_type in ["road", "bridge"]:
            if infrastructure_type == "road":
                building_types = ["road", "railroad"]
                directions = ["up", "down", "left", "right"]
            elif infrastructure_type == "bridge":
                building_types = ["road_bridge", "railroad_bridge", "ferry"]
                directions = ["vertical", "horizontal"]
            for direction in directions:
                for building_type in building_types:
                    self.connection_image_dict[direction + "_" + building_type] = (
                        "buildings/infrastructure/"
                        + direction
                        + "_"
                        + building_type
                        + ".png"
                    )

        super().__init__(from_save, input_dict)
        if self.is_bridge:
            up_cell = self.grids[0].find_cell(self.x, self.y + 1)
            down_cell = self.grids[0].find_cell(self.x, self.y - 1)
            left_cell = self.grids[0].find_cell(self.x - 1, self.y)
            right_cell = self.grids[0].find_cell(self.x + 1, self.y)
            if (not (up_cell == None or down_cell == None)) and (
                not (up_cell.terrain == "water" or down_cell.terrain == "water")
            ):
                self.connected_cells = [up_cell, down_cell]
                if self.is_road:
                    self.image_dict["default"] = self.connection_image_dict[
                        "vertical_road_bridge"
                    ]
                elif self.is_railroad:
                    self.image_dict["default"] = self.connection_image_dict[
                        "vertical_railroad_bridge"
                    ]
                else:
                    self.image_dict["default"] = self.connection_image_dict[
                        "vertical_ferry"
                    ]
            else:
                self.connected_cells = [left_cell, right_cell]
                if self.is_road:
                    self.image_dict["default"] = self.connection_image_dict[
                        "horizontal_road_bridge"
                    ]
                elif self.is_railroad:
                    self.image_dict["default"] = self.connection_image_dict[
                        "horizontal_railroad_bridge"
                    ]
                else:
                    self.image_dict["default"] = self.connection_image_dict[
                        "horizontal_ferry"
                    ]
        actor_utility.update_roads()

    def to_save_dict(self):
        """
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                Along with superclass outputs, also saves the following values:
                'infrastructure_type': string value - Type of infrastructure, like 'road' or 'railroad'
        """
        save_dict = super().to_save_dict()
        save_dict["infrastructure_type"] = self.infrastructure_type
        return save_dict

    def can_damage(self):
        """
        Description:
            Returns whether this building is able to be damaged. Roads, railroads, and slums cannot be damaged
        Input:
            None
        Output:
            boolean: Returns whether this building is able to be damaged
        """
        return False

    def get_image_id_list(self, override_values={}):
        """
        Description:
            Generates and returns a list this actor's image file paths and dictionaries that can be passed to any image object to display those images together in a particular order and
                orientation. Infrastructure buildings display connections between themselves and adjacent infrastructure buildings
        Input:
            None
        Output:
            list: Returns list of string image file paths, possibly combined with string key dictionaries with extra information for offset images
        """
        image_id_list = super().get_image_id_list(override_values)
        if self.cell.terrain != "water":
            connected_road, connected_railroad = (False, False)
            for direction in ["up", "down", "left", "right"]:
                adjacent_cell = self.cell.adjacent_cells[direction]
                if adjacent_cell:
                    own_tile_infrastructure = self.cell.get_intact_building(
                        "infrastructure"
                    )
                    adjacent_cell_infrastructure = adjacent_cell.get_intact_building(
                        "infrastructure"
                    )
                    if adjacent_cell_infrastructure != "none":
                        if (
                            adjacent_cell_infrastructure.is_railroad
                            and own_tile_infrastructure.is_railroad
                        ):
                            image_id_list.append(
                                self.connection_image_dict[direction + "_railroad"]
                            )
                        else:
                            image_id_list.append(
                                self.connection_image_dict[direction + "_road"]
                            )
                        if adjacent_cell_infrastructure.is_road:
                            connected_road = True
                        elif adjacent_cell_infrastructure.is_railroad:
                            connected_railroad = True
            if self.is_road and (connected_road or connected_railroad):
                image_id_list.pop(0)
            elif self.is_railroad and connected_railroad:
                image_id_list.pop(0)
        for index, current_image in enumerate(image_id_list):
            if type(current_image) == str:
                image_id_list[index] = {"image_id": current_image, "level": -1}
            else:
                current_image["level"] = -1
        return image_id_list


class trading_post(building):
    """
    Building in a village that increases success chance of trading
    """

    def __init__(self, from_save, input_dict):
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'grids': grid list value - grids in which this mob's images can appear
                'image': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'name': string value - Required if from save, this building's name
                'modes': string list value - Game modes during which this building's images can appear
                'contained_work_crews': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each work crew working in this building
        Output:
            None
        """
        input_dict["building_type"] = "trading_post"
        super().__init__(from_save, input_dict)


class mission(building):
    """
    Building in village that increases success chance of conversion
    """

    def __init__(self, from_save, input_dict):
        """
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
        Output:
            None
        """
        input_dict["building_type"] = "mission"
        super().__init__(from_save, input_dict)


class fort(building):
    """
    Building that grants a +1 combat modifier to your units fighting in its tile
    """

    def __init__(self, from_save, input_dict):
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'grids': grid list value - grids in which this mob's images can appear
                'image': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'name': string value - Required if from save, this building's name
                'modes': string list value - Game modes during which this building's images can appear
                'contained_work_crews': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each work crew working in this building
        Output:
            None
        """
        input_dict["building_type"] = "fort"
        super().__init__(from_save, input_dict)


class train_station(building):
    """
    Building along a railroad that allows the construction of train, allows trains to pick up and drop off cargo/passengers, and increases the tile's inventory capacity
    """

    def __init__(self, from_save, input_dict):
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'grids': grid list value - grids in which this mob's images can appear
                'image': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'name': string value - Required if from save, this building's name
                'modes': string list value - Game modes during which this building's images can appear
                'contained_work_crews': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each work crew working in this building
        Output:
            None
        """
        input_dict["building_type"] = "train_station"
        super().__init__(from_save, input_dict)


class port(building):
    """
    Building adjacent to water that allows steamships/steamboats to enter the tile, allows ships to travel to this tile if it is along the ocean, and increases the tile's inventory capacity
    """

    def __init__(self, from_save, input_dict):
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'grids': grid list value - grids in which this mob's images can appear
                'image': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'name': string value - Required if from save, this building's name
                'modes': string list value - Game modes during which this building's images can appear
                'contained_work_crews': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each work crew working in this building
        Output:
            None
        """
        input_dict["building_type"] = "port"
        super().__init__(from_save, input_dict)
        if (not from_save) and self.cell.village != "none":
            constants.sound_manager.play_random_music("europe")


class warehouses(building):
    """
    Buiding attached to a port, train station, and/or resource production facility that stores commodities
    """

    def __init__(self, from_save, input_dict):
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'grids': grid list value - grids in which this mob's images can appear
                'image': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'name': string value - Required if from save, this building's name
                'modes': string list value - Game modes during which this building's images can appear
                'contained_work_crews': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each work crew working in this building
                'warehouse_level': int value - Required if from save, size of warehouse (9 inventory capacity per level)
        Output:
            None
        """
        input_dict["building_type"] = "warehouses"
        self.warehouse_level = 1
        super().__init__(from_save, input_dict)
        self.set_default_inventory_capacity(9)
        if from_save:
            while self.warehouse_level < input_dict["warehouse_level"]:
                self.upgrade()

        if constants.effect_manager.effect_active("damaged_buildings"):
            if self.can_damage():
                self.set_damaged(True, True)

    def to_save_dict(self):
        """
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                Along with superclass outputs, also saves the following values:
                'warehouse_level': int value - Size of warehouse (9 inventory capacity per level)
        """
        save_dict = super().to_save_dict()
        save_dict["warehouse_level"] = self.warehouse_level
        return save_dict

    def can_upgrade(self, upgrade_type="warehouse_level"):
        """
        Description:
            Returns whether this building can be upgraded in the inputted field. Warehouses can be upgraded infinitely
        Input:
            string upgrade_type = 'warehouse_level': Represents type of upgrade, like 'scale' or 'efficiency'
        Output:
            boolean: Returns True if this building can be upgraded in the inputted field, otherwise returns False
        """
        return True

    def get_upgrade_cost(self):
        """
        Description:
            Returns the cost of the next upgrade for this building. The first successful upgrade costs 5 money and each subsequent upgrade costs twice as much as the previous. Building a train station, resource production facility, or
                port gives a free upgrade that does not affect the costs of future upgrades
        Input:
            None
        Output:
            None
        """
        return self.cell.get_warehouses_cost()

    def upgrade(self, upgrade_type="warehouse_level"):
        self.warehouse_level += 1
        self.set_default_inventory_capacity(self.default_inventory_capacity + 9)

    def get_image_id_list(self, override_values={}):
        """
        Description:
            Generates and returns a list this actor's image file paths and dictionaries that can be passed to any image object to display those images together in a particular order and
                orientation. Warehouses have no images
        Input:
            None
        Output:
            list: Returns list of string image file paths, possibly combined with string key dictionaries with extra information for offset images
        """
        return []


class resource_building(building):
    """
    Building in a resource tile that allows work crews to attach to this building to produce commodities over time
    """

    def __init__(self, from_save, input_dict):
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'grids': grid list value - grids in which this mob's images can appear
                'image': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'name': string value - Required if from save, this building's name
                'resource_type': string value - Type of resource produced by this building, like 'exotic wood'
                'modes': string list value - Game modes during which this building's images can appear
                'contained_work_crews': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each work crew working in this building
                'scale': int value - Required if from save, maximum number of work crews that can be attached to this building
                'efficiency': int value - Required if from save, number of rolls made by work crews each turn to produce commodities at this building
        Output:
            None
        """
        self.resource_type = input_dict["resource_type"]
        input_dict["building_type"] = "resource"
        self.scale = input_dict.get("scale", 1)
        self.efficiency = input_dict.get("efficiency", 1)
        self.num_upgrades = self.scale + self.efficiency - 2
        self.ejected_work_crews = []
        super().__init__(from_save, input_dict)
        status.resource_building_list.append(self)

    def to_save_dict(self):
        """
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
        """
        save_dict = super().to_save_dict()
        save_dict["resource_type"] = self.resource_type
        save_dict["scale"] = self.scale
        save_dict["efficiency"] = self.efficiency
        return save_dict

    def eject_work_crews(self):
        """
        Description:
            Removes this building's work crews
        Input:
            None
        Output:
            None
        """
        for current_work_crew in self.contained_work_crews:
            if not current_work_crew in self.ejected_work_crews:
                self.ejected_work_crews.append(current_work_crew)
                current_work_crew.leave_building(self)

    def set_damaged(self, new_value, mid_setup=False):
        """
        Description:
            Repairs or damages this building based on the inputted value. A damaged building still provides attrition resistance but otherwise loses its specialized capabilities. A damaged resource building ejects its work crews when
                damaged
        Input:
            boolean new_value: New damaged/undamaged state of the building
        Output:
            None
        """
        if new_value == True:
            self.eject_work_crews()
        super().set_damaged(new_value, mid_setup)

    def reattach_work_crews(self):
        """
        Description:
            After combat is finished, returns any surviving work crews to this building, if possible
        Input:
            None
        Output:
            None
        """
        for current_work_crew in self.ejected_work_crews:
            if current_work_crew in status.pmob_list:  # if not dead
                current_work_crew.work_building(self)
        self.ejected_work_crews = []

    def remove(self):
        """
        Description:
            Removes this object from relevant lists, prevents it from further appearing in or affecting the program, and removes it from the tiles it occupies
        Input:
            None
        Output:
            None
        """
        status.resource_building_list = utility.remove_from_list(
            status.resource_building_list, self
        )
        super().remove()

    def manage_health_attrition(self, current_cell="default"):
        """
        Description:
            Checks this building's work crews for health attrition each turn
        Input:
            string/cell current_cell = 'default': Records which cell the attrition is taking place in, used when a unit is in a building or another mob and does not technically exist in any cell
        Output:
            None
        """
        if current_cell == "default":
            current_cell = self.cell
        transportation_minister = status.current_ministers[
            constants.type_minister_dict["transportation"]
        ]
        worker_attrition_list = []
        officer_attrition_list = []
        for current_work_crew in self.contained_work_crews:
            if current_cell.local_attrition():
                if transportation_minister.no_corruption_roll(
                    6, "health_attrition"
                ) == 1 or constants.effect_manager.effect_active("boost_attrition"):
                    officer_attrition_list.append(current_work_crew)
            if current_cell.local_attrition():
                if transportation_minister.no_corruption_roll(
                    6, "health_attrition"
                ) == 1 or constants.effect_manager.effect_active("boost_attrition"):
                    worker_type = current_work_crew.worker.worker_type
                    if (not worker_type in ["African", "slave"]) or random.randrange(
                        1, 7
                    ) == 1:
                        worker_attrition_list.append(current_work_crew)
        for current_work_crew in worker_attrition_list:
            current_work_crew.attrition_death("worker")
        for current_work_crew in officer_attrition_list:
            current_work_crew.attrition_death("officer")

    def can_upgrade(self, upgrade_type):
        """
        Description:
            Returns whether this building can be upgraded in the inputted field. A building can be upgraded not be ugpraded above 6 in a field
        Input:
            string upgrade_type: Represents type of upgrade, like 'scale' or 'efficiency'
        Output:
            boolean: Returns True if this building can be upgraded in the inputted field, otherwise returns False
        """
        if upgrade_type == "scale":
            if self.scale < 6:
                return True
        elif upgrade_type == "efficiency":
            if self.efficiency < 6:
                return True
        return False

    def upgrade(self, upgrade_type):
        """
        Description:
            Upgrades this building in the inputted field, such as by increasing the building's efficiency by 1 when 'efficiency' is inputted
        Input:
            string upgrade_type: Represents type of upgrade, like 'scale' or 'effiency'
        Output:
            None
        """
        if upgrade_type == "scale":
            self.scale += 1
        elif upgrade_type == "efficiency":
            self.efficiency += 1
        if self.scale >= 6 and self.efficiency >= 6:
            constants.achievement_manager.achieve("Industrialist")
        self.num_upgrades += 1

    def get_upgrade_cost(self):
        """
        Description:
            Returns the cost of the next upgrade for this building. The first successful upgrade costs 20 money and each subsequent upgrade costs twice as much as the previous
        Input:
            None
        Output:
            None
        """
        if constants.effect_manager.effect_active("free_upgrades"):
            return 0
        else:
            return constants.base_upgrade_price * (
                2**self.num_upgrades
            )  # 20 for 1st upgrade, 40 for 2nd, 80 for 3rd, etc.

    def get_build_cost(self):
        """
        Description:
            Returns the total cost of building this building, including all of its upgrades but not failed attempts or terrain
        Input:
            None
        Output:
            double: Returns the total cost of building this building
        """
        cost = super().get_build_cost()
        for i in range(
            0, self.num_upgrades
        ):  # adds cost of each upgrade, each of which is more expensive than the last
            cost += constants.base_upgrade_price * (i + 1)
        return cost

    def produce(self):
        """
        Description:
            Orders each work crew attached to this building to attempt producing commodities at the end of a turn. Based on work crew experience and minister skill/corruption, each work crew can produce a number of commodities up to the
                building's efficiency
        Input:
            None
        Output:
            None
        """
        for current_work_crew in self.contained_work_crews:
            current_work_crew.attempt_production(self)


class slums(building):
    """
    Building automatically formed by unemployed workers and freed slaves around places of employment
    """

    def __init__(self, from_save, input_dict):
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'grids': grid list value - grids in which this mob's images can appear
                'image': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'name': string value - Required if from save, this building's name
                'building_type': string value - Type of building, like 'port'
                'modes': string list value - Game modes during which this building's images can appear
                'contained_work_crews': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each work crew working in this building

        Output:
            None
        """
        status.slums_list.append(self)
        input_dict["building_type"] = "slums"
        self.available_workers = 0
        if from_save:
            self.available_workers = input_dict["available_workers"]
        input_dict["image"] = "buildings/slums/default.png"
        self.size_image_dict = {
            "small": "buildings/slums/small.png",
            "medium": "buildings/slums/default.png",
            "large": "buildings/slums/large.png",
        }
        super().__init__(from_save, input_dict)
        if self.cell.tile == status.displayed_tile:
            actor_utility.calibrate_actor_info_display(
                status.tile_info_display, self.cell.tile
            )  # show self after creation

    def get_image_id_list(self, override_values={}):
        """
        Description:
            Generates and returns a list this actor's image file paths and dictionaries that can be passed to any image object to display those images together in a particular order and
                orientation
        Input:
            None
        Output:
            list: Returns list of string image file paths, possibly combined with string key dictionaries with extra information for offset images
        """
        image_id_list = super().get_image_id_list(override_values)
        if self.available_workers <= 2:
            image_id_list[0]["image_id"] = self.size_image_dict["small"]
        elif self.available_workers <= 5:
            image_id_list[0]["image_id"] = self.size_image_dict["medium"]
        else:
            image_id_list[0]["image_id"] = self.size_image_dict["large"]
        for current_image_id in image_id_list:
            current_image_id.update({"level": -2})
        return image_id_list

    def can_damage(self):
        """
        Description:
            Returns whether this building is able to be damaged. Roads, railroads, and slums cannot be damaged
        Input:
            None
        Output:
            boolean: Returns whether this building is able to be damaged
        """
        return False

    def remove(self):
        """
        Description:
            Removes this object from relevant lists, prevents it from further appearing in or affecting the program, and removes it from the tiles it occupies
        Input:
            None
        Output:
            None
        """
        super().remove()
        status.slums_list = utility.remove_from_list(status.slums_list, self)

    def change_population(self, change):
        """
        Description:
            Changes this slum's population by the inputted amount. Updates the tile info display as applicable and destroys the slum if its population reaches 0
        Input:
            int change: amount this slum's population is changed by
        Output:
            None
        """
        self.available_workers += change
        if self.available_workers < 0:
            self.available_workers = 0
        self.cell.tile.update_image_bundle()
        if (
            self.cell.tile == status.displayed_tile
        ):  # if being displayed, change displayed population value
            actor_utility.calibrate_actor_info_display(
                status.tile_info_display, self.cell.tile
            )
        if self.available_workers == 0:
            tile = self.cell.tile
            self.remove_complete()
            actor_utility.calibrate_actor_info_display(status.tile_info_display, tile)
            status.minimap_grid.calibrate(tile.x, tile.y)

    def recruit_worker(self):
        """
        Description:
            Hires one of this slum's available workers by creating a worker, reducing the slum's population
        Input:
            None
        Output:
            None
        """
        input_dict = {
            "select_on_creation": True,
            "coordinates": (self.cell.x, self.cell.y),
            "grids": [self.cell.grid, self.cell.grid.mini_grid],
            "modes": self.cell.grid.modes,
        }
        input_dict.update(status.worker_types["African"].generate_input_dict())
        constants.actor_creation_manager.create(False, input_dict)
        self.change_population(-1)

    def to_save_dict(self):
        """
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                Along with superclass outputs, also saves the following values:
                'available_workers': int value - Number of unemployed workers in this slum
        """
        save_dict = super().to_save_dict()
        save_dict["available_workers"] = self.available_workers
        return save_dict
