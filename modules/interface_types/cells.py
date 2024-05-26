# Contains functionality for grid cells

import pygame
import random
from typing import Dict
from ..util import actor_utility
from ..tools.data_managers.terrain_manager_template import terrain_handler
import modules.constants.constants as constants
import modules.constants.status as status


class cell:
    """
    Object representing one cell of a grid corresponding to one of its coordinates, able to contain terrain, resources, mobs, and tiles
    """

    def __init__(self, x, y, width, height, grid, color, save_dict):
        """
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
        Output:
            None
        """
        self.x: int = x
        self.y: int = y
        self.width: int = width
        self.height: int = height
        self.grid = grid
        self.color: tuple[int, int, int] = color
        self.pixel_x, self.pixel_y = self.grid.convert_coordinates((self.x, self.y))
        self.Rect: pygame.Rect = pygame.Rect(
            self.pixel_x, self.pixel_y - self.height, self.width, self.height
        )  # (left, top, width, height)
        self.grid.cell_list[x][y] = self
        self.tile = "none"
        self.village = "none"
        self.settlement = None
        self.terrain_handler: terrain_handler = None
        self.contained_mobs: list = []
        self.reset_buildings()
        self.adjacent_cells: Dict[str, cell] = {
            "up": None,
            "down": None,
            "right": None,
            "left": None,
        }
        if save_dict != "none":  # if from save
            self.save_dict: dict = save_dict
            if constants.effect_manager.effect_active("remove_fog_of_war"):
                save_dict["visible"] = True
            self.terrain_handler = terrain_handler(self, save_dict)
        else:  # if creating new map
            self.terrain_handler = terrain_handler(self)

    def to_save_dict(self):
        """
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'visible': boolean value - Whether this cell is visible or not
                'terrain': string value - Terrain type of this cell and its tile, like 'swamp'
                'terrain_variant': int value - Variant number to use for image file path, like mountain_0
                'terrain feature': string/boolean dictionary value - Dictionary containing a True entry for each terrain feature type in this cell
                'resource': string value - Resource type of this cell and its tile, like 'exotic wood'
                'inventory': string/string dictionary value - Version of the inventory dictionary of this cell's tile only containing commodity types with 1+ units held
        """
        save_dict = {}
        save_dict["coordinates"] = (self.x, self.y)
        save_dict.update(self.terrain_handler.to_save_dict())
        save_dict["inventory"] = self.tile.inventory
        return save_dict

    def has_walking_connection(self, adjacent_cell):
        """
        Description:
            Finds and returns whether a walking-only unit could move between this cell and the inputted cell, based on the terrains of the cells and whether a bridge is built
        Input:
            cell adjacent_cell: Cell to check for walking connections
        Output:
            boolean: Returns whether a walking-only unit could move between this cell and the inputted cell, based on the terrains of the cells and whether a bridge is built
        """
        if not (
            self.terrain_handler.terrain == "water"
            or adjacent_cell.terrain_handler.terrain == "water"
        ):  # if both are land tiles, walking connection exists
            return True
        if (
            self.terrain_handler.terrain == "water"
            and adjacent_cell.terrain_handler.terrain == "water"
        ):  # if both are water, no walking connection exists
            return False

        if self.terrain_handler.terrain == "water":
            water_cell = self
            land_cell = adjacent_cell
        else:
            water_cell = adjacent_cell
            land_cell = self

        water_infrastructure = water_cell.get_intact_building("infrastructure")
        if (
            water_infrastructure == "none"
        ):  # if no bridge in water tile, no walking connection exists
            return False
        if water_infrastructure.is_bridge:
            if (
                land_cell in water_infrastructure.connected_cells
            ):  # if bridge in water tile connects to the land tile, walking connection exists
                return True
        return False

    def local_attrition(self, attrition_type="health"):
        """
        Description:
            Returns the result of a roll that determines if a given unit or set of stored commodities should suffer attrition based on this cell's terrain and buildings. Bad terrain increases attrition frequency while infrastructure
                decreases it
        Input:
            string attrition_type = 'health': 'health' or 'inventory', refers to type of attrition being tested for. Used because inventory attrition can occur on Earth but not health attrition
        Output:
            boolean: Returns whether attrition should happen here based on this cell's terrain and buildings
        """
        if self.grid in [
            status.earth_grid,
            status.slave_traders_grid,
        ]:  # no attrition on Earth or with slave traders
            if attrition_type == "health":
                return False
            elif (
                attrition_type == "inventory"
            ):  # losing inventory in warehouses and such is uncommon but not impossible on Earth, but no health attrition on Earth
                if (
                    random.randrange(1, 7) >= 2 or random.randrange(1, 7) >= 3
                ):  # same effect as clear area with port
                    return False
        else:
            if (
                random.randrange(1, 7)
                >= constants.terrain_attrition_dict.get(self.terrain_handler.terrain, 1)
                + 1
            ):  # Attrition on 1-, 2-, or 3-, based on terrain
                return False

            if (
                self.has_building("village")
                or self.has_building("train_station")
                or self.has_building("port")
                or self.has_building("resource")
                or self.has_building("fort")
            ):
                if random.randrange(1, 7) >= 3:  # removes 2/3 of attrition
                    return False
            elif self.has_building("road") or self.has_building("railroad"):
                if random.randrange(1, 7) >= 5:  # removes 1/3 of attrition
                    return False

        return True

    def has_building(
        self, building_type
    ):  # accepts village, train_station, port, trading_post, mission, fort, road, railroad, resource, slums. No forts in game yet
        """
        Description:
            Returns whether this cell has a building of the inputted type, even if the building is damaged
        Input:
            string building_type: type of building to search for
        Output:
            boolean: Returns whether this cell has a building of the inputted type
        """
        if building_type == "village":
            if self.village == "none":
                return False
            else:
                return True
        elif building_type in ["road", "railroad"]:
            if self.contained_buildings["infrastructure"] == "none":
                return False
            elif (
                building_type == "road"
                and self.contained_buildings["infrastructure"].is_road
            ):
                return True
            elif (
                building_type == "railroad"
                and self.contained_buildings["infrastructure"].is_railroad
            ):
                return True
            else:
                return False
        elif (
            not building_type in self.contained_buildings
        ):  # if checking for something that is not actually a building, like 'train'
            return False
        else:
            if self.contained_buildings[building_type] == "none":
                return False
            else:
                return True

    def has_intact_building(self, building_type):
        """
        Description:
            Returns whether this cell has an undamaged building of the inputted type
        Input:
            string building_type: Type of building to search for
        Output:
            boolean: Returns whether this cell has an undamaged building of the inputted type
        """
        if building_type == "village":
            if self.village == "none":
                return False
            else:
                return True

        elif building_type in ["road", "railroad"]:
            if self.contained_buildings["infrastructure"] == "none":
                return False
            elif (
                building_type == "road"
                and self.contained_buildings["infrastructure"].is_road
            ):
                returned_building = self.contained_buildings["infrastructure"]
            elif (
                building_type == "railroad"
                and self.contained_buildings["infrastructure"].is_railroad
            ):
                returned_building = self.contained_buildings["infrastructure"]
            else:
                return False

        elif (
            not building_type in self.contained_buildings
        ):  # if checking for something that is not actually a building, like 'train'
            return False

        else:
            if self.contained_buildings[building_type] == "none":
                return False
            else:
                returned_building = self.contained_buildings[building_type]

        if not returned_building.damaged:
            return True
        else:
            return False

    def get_building(self, building_type):
        """
        Description:
            Returns this cell's building of the inputted type, or 'none' if that building is not present
        Input:
            string building_type: Type of building to search for
        Output:
            building/string: Returns whether this cell's building of the inputted type, or 'none' if that building is not present
        """
        if self.has_building(building_type):
            if building_type == "village":
                return self.village
            elif building_type in ["road", "railroad"]:
                return self.contained_buildings["infrastructure"]
            else:
                return self.contained_buildings[building_type]
        else:
            return "none"

    def get_intact_building(self, building_type):
        """
        Description:
            Returns this cell's undamaged building of the inputted type, or 'none' if that building is damaged or not present
        Input:
            string building_type: Type of building to search for
        Output:
            building/string: Returns this cell's undamaged building of the inputted type, or 'none' if that building is damaged or not present
        """
        if self.has_intact_building(building_type):
            if building_type == "village":
                return self.village

            elif building_type in ["road", "railroad"]:
                return self.contained_buildings["infrastructure"]

            else:
                return self.contained_buildings[building_type]

        else:
            return "none"

    def reset_buildings(self):
        """
        Description:
            Resets the values of this cell's dictionary of contained buildings to 'none', initializing the dictionary or removing existing buildings
        Input:
            None
        Output:
            None
        """
        self.contained_buildings = {}
        for current_building_type in constants.building_types:
            self.contained_buildings[current_building_type] = "none"

    def get_buildings(self):
        """
        Description:
            Returns a list of the buildings contained in this cell
        Input:
            None
        Output:
            building list contained_buildings_list: buildings contained in this cell
        """
        contained_buildings_list = []
        for current_building_type in constants.building_types:
            if self.has_building(current_building_type):
                contained_buildings_list.append(
                    self.contained_buildings[current_building_type]
                )
        return contained_buildings_list

    def get_intact_buildings(self):
        """
        Description:
            Returns a list of the nondamaged buildings contained in this cell
        Input:
            None
        Output:
            building list contained_buildings_list: nondamaged buildings contained in this cell
        """
        contained_buildings_list = []
        for current_building_type in constants.building_types:
            if self.has_intact_building(current_building_type):
                contained_buildings_list.append(
                    self.contained_buildings[current_building_type]
                )
        return contained_buildings_list

    def adjacent_to_buildings(self):
        """
        Description:
            Finds and returns if this cell is adjacent to any buildings, used for beast spawning
        Input:
            None
        Output:
            boolean: Returns if this cell is adjacent to any buildings
        """
        for current_adjacent_cell in self.adjacent_list + [self]:
            if len(current_adjacent_cell.get_buildings()) > 0:
                return True
        return False

    def has_destructible_buildings(self):
        """
        Description:
            Finds and returns if this cell is adjacent has any buildings that can be damaged by native warriors (not roads or railroads), used for native warriors cell targeting
        Input:
            None
        Output:
            boolean: Returns if this cell has any buildings that can be damaged by native warriors
        """
        for current_building in self.get_intact_buildings():
            if current_building.can_damage():
                return True
        return False

    def get_warehouses_cost(self):
        """
        Description:
            Calculates and returns the cost of the next warehouses upgrade in this tile, based on the number of past warehouses upgrades
        Input:
            None
        Output:
            int: Returns the cost of the next warehouses upgrade in this tile, based on the number of past warehouse upgrades
        """
        warehouses = self.get_building("warehouses")
        if warehouses == "none":
            warehouses_built = 0
        else:
            warehouses_built = warehouses.warehouse_level
        if self.has_building("port"):
            warehouses_built -= 1
        if self.has_building("train_station"):
            warehouses_built -= 1
        if self.has_building("resource"):
            warehouses_built -= 1

        return constants.building_prices["warehouses"] * (
            2**warehouses_built
        )  # 5 * 2^0 = 5 if none built, 5 * 2^1 = 10 if 1 built, 20, 40...

    def create_slums(self):
        """
        Description:
            Creates an empty slums building when a worker migrates to this cell, if there is not already one present
        Input:
            None
        Outptu:
            None
        """
        constants.actor_creation_manager.create(
            False,
            {
                "coordinates": (self.x, self.y),
                "grids": [self.cell.grid] + self.cell.grid.mini_grids,
                "name": "slums",
                "modes": self.grid.modes,
                "init_type": "slums",
            },
        )
        if self.tile == status.displayed_tile:
            actor_utility.calibrate_actor_info_display(
                status.tile_info_display, self.tile
            )  # update tile display to show new building

    def has_vehicle(self, vehicle_type, is_worker=False):
        """
        Description:
            Returns whether this cell contains a crewed vehicle of the inputted type
        Input:
            string vehicle_type: 'train' or 'ship', determines what kind of vehicle is searched for
        Output:
            boolean: Returns True if this cell contains a crewed vehicle of the inputted type, otherwise returns False
        """
        for current_mob in self.contained_mobs:
            if (
                current_mob.is_vehicle
                and (current_mob.has_crew or is_worker)
                and current_mob.vehicle_type == vehicle_type
            ):
                return True
        return False

    def get_vehicle(self, vehicle_type, is_worker=False):
        """
        Description:
            Returns the first crewed vehicle of the inputted type in this cell, or 'none' if none are present
        Input:
            string vehicle_type: 'train' or 'ship', determines what kind of vehicle is searched for
        Output:
            string/vehicle: Returns the first crewed vehicle of the inputted type in this cell, or 'none' if none are present
        """
        for current_mob in self.contained_mobs:
            if (
                current_mob.is_vehicle
                and (current_mob.has_crew or is_worker)
                and current_mob.vehicle_type == vehicle_type
            ):
                return current_mob
        return "none"

    def get_vehicles(self, vehicle_type, is_worker=False):
        """
        Description:
            Returns each crewed vehicle of the inputted type in this cell, or 'none' if none are present
        Input:
            string vehicle_type: 'train' or 'ship', determines what kind of vehicle is searched for
        Output:
            string/vehicle: Returns the first crewed vehicle of the inputted type in this cell, or 'none' if none are present
        """
        return_list = []
        for current_mob in self.contained_mobs:
            if (
                current_mob.is_vehicle
                and (current_mob.has_crew or is_worker)
                and current_mob.vehicle_type == vehicle_type
            ):
                return_list.append(current_mob)
        return return_list

    def has_uncrewed_vehicle(self, vehicle_type):
        """
        Description:
            Returns whether this cell contains an uncrewed vehicle of the inputted type
        Input:
            string vehicle_type: 'train' or 'ship', determines what kind of vehicle is searched for
        Output:
            boolean: Returns True if this cell contains an uncrewed vehicle of the inputted type, otherwise returns False
        """
        for current_mob in self.contained_mobs:
            if (
                current_mob.is_vehicle
                and (not current_mob.has_crew)
                and current_mob.vehicle_type == vehicle_type
            ):
                return True
        return False

    def get_uncrewed_vehicle(self, vehicle_type, worker_type="default"):
        """
        Description:
            Returns the first uncrewed vehicle of the inputted type in this cell, or 'none' if none are present
        Input:
            string vehicle_type: 'train' or 'ship', determines what kind of vehicle is searched for
            string worker_type = 'default': If a worker type is inputted, only vehicles that the inputted worker type oculd crew are returned
        Output:
            string/vehicle: Returns the first uncrewed vehicle of the inputted type in this cell, or 'none' if none are present
        """
        if worker_type == "slave":
            return "none"
        for current_mob in self.contained_mobs:
            if (
                current_mob.is_vehicle
                and (not current_mob.has_crew)
                and current_mob.vehicle_type == vehicle_type
            ):
                if not (
                    worker_type == "African"
                    and current_mob.can_swim
                    and current_mob.can_swim_ocean
                ):
                    return current_mob
        return "none"

    def has_worker(self, possible_types=None, required_number=1):
        """
        Description:
            Returns whether this cell contains a worker of one of the inputted types
        Input:
            string list possible_types: Type of worker that can be detected, includes all workers by default
            int required_number=1: Number of workers that must be found to return True
        Output:
            Returns True if this cell contains the required number of workers of one of the inputted types, otherwise returns False
        """
        num_found = 0
        for current_mob in self.contained_mobs:
            if (
                current_mob.is_pmob
                and current_mob.is_worker
                and ((not possible_types) or current_mob.worker_type in possible_types)
            ):
                num_found += 1
                if num_found >= required_number:
                    return True
        return False

    def has_officer(self, allow_vehicle=True, required_number=1):
        """
        Description:
            Returns whether this cell contains an officer of an allowed type
        Input:
            boolean allow_vehicles=True: Whether uncrewed vehicles can be returned or just officers
            int required_number=1: Number of officers that must be found to return True
        Output:
            Returns True if this cell contains the required number of officers of one of the inputted types, otherwise returns False
        """
        num_found = 0
        for current_mob in self.contained_mobs:
            if current_mob.is_pmob and (
                current_mob.is_officer
                or (current_mob.is_vehicle and not current_mob.has_crew)
            ):
                num_found += 1
                if num_found >= required_number:
                    return True
        return False

    def get_worker(self, possible_types=None, start_index=0):
        """
        Description:
            Finds and returns the first worker in this cell of the inputted types, or 'none' if none are present
        Input:
            string list possible_types: Type of worker that can be returned, includes all workers by default
            int start_index=0: Index of contained_mobs to start search from - if starting in middle, wraps around iteration to ensure all items are still checked
        Output:
            string/worker: Returns the first worker in this cell of the inputted types, or 'none' if none are present
        """
        if start_index >= len(self.contained_mobs):
            start_index = 0
        if (
            start_index == 0
        ):  # don't bother slicing/concatenating list if just iterating from index 0
            iterated_list = self.contained_mobs
        else:
            iterated_list = (
                self.contained_mobs[start_index : len(self.contained_mobs)]
                + self.contained_mobs[0:start_index]
            )
        for current_mob in iterated_list:
            if (
                current_mob.is_pmob
                and current_mob.is_worker
                and ((not possible_types) or current_mob.worker_type in possible_types)
            ):
                return current_mob
        return "none"

    def get_officer(self, allow_vehicles=True, start_index=0):
        """
        Description:
            Finds and returns the first officer or, optionally, uncrewed vehicle, in this cell, or 'none' if none are present
        Input:
            boolean allow_vehicles=True: Whether uncrewed vehicles can be returned or just officers
            int start_index=0: Index of contained_mobs to start search from - if starting in middle, wraps around iteration to ensure all items are still checked
        Output:
            string/actor: Returns the first officer, or, optionally, uncrewed vehicle in this cell, or 'none' if none are present
        """
        if start_index >= len(self.contained_mobs):
            start_index = 0
        if (
            start_index == 0
        ):  # don't bother slicing/concatenating list if just iterating from index 0
            iterated_list = self.contained_mobs
        else:
            iterated_list = (
                self.contained_mobs[start_index : len(self.contained_mobs)]
                + self.contained_mobs[0:start_index]
            )
        for current_mob in iterated_list:
            if current_mob.is_pmob and (
                current_mob.is_officer
                or (current_mob.is_vehicle and not current_mob.has_crew)
            ):
                return current_mob
        return "none"

    def has_pmob(self):
        """
        Description:
            Returns whether this cell contains a pmob
        Input:
            None
        Output:
            boolean: Returns whether this cell contains a pmob
        """
        for current_mob in self.contained_mobs:
            if current_mob.is_pmob:
                return True
        if self.has_intact_building("resource"):
            if len(self.get_intact_building("resource").contained_work_crews) > 0:
                return True
        return False

    def get_pmob(self):
        """
        Description:
            Returns the first pmob in this cell, or 'none' if none are present
        Input:
            None
        Output:
            string/pmob: Returns the first pmob in this cell, or 'none' if none are present
        """
        for current_mob in self.contained_mobs:
            if current_mob.is_pmob:
                return current_mob
        return "none"

    def has_npmob(self):
        """
        Description:
            Returns whether this cell contains an npmob
        Input:
            None
        Output:
            boolean: Returns whether this cell contains an npmob
        """
        for current_mob in self.contained_mobs:
            if current_mob.is_npmob:
                return True
        return False

    def get_best_combatant(self, mob_type, target_type="human"):
        """
        Description:
            Finds and returns the best combatant of the inputted type in this cell. Combat ability is based on the unit's combat modifier and veteran status. Assumes that units in vehicles and buildings have already detached upon being
                attacked
        Input:
            string mob_type: Can be npmob or pmob, determines what kind of mob is searched for. An attacking pmob will search for the most powerful npmob and vice versa
            string target_type = 'human': Regardless of the mob type being searched for, target_type gives information about the npmob: when a pmob searches for an npmob, it will search for a 'human' or 'beast' npmob. When an npmob
                searches for a pmob, it will say whether it is a 'human' or 'beast' to correctly choose pmobs specialized at fighting that npmob type, like safaris against beasts
        Output;
            mob: Returns the best combatant of the inputted type in this cell
        """
        best_combatants = ["none"]
        best_combat_modifier = 0
        if mob_type == "npmob":
            for current_mob in self.contained_mobs:
                if current_mob.is_npmob:
                    if (
                        target_type == "human" and not current_mob.npmob_type == "beast"
                    ) or (target_type == "beast" and current_mob.npmob_type == "beast"):
                        current_combat_modifier = current_mob.get_combat_modifier()
                        if (
                            best_combatants[0] == "none"
                            or current_combat_modifier > best_combat_modifier
                        ):  # if first mob or better than previous mobs, set as only best
                            best_combatants = [current_mob]
                            best_combat_modifier = current_combat_modifier
                        elif (
                            current_combat_modifier == best_combat_modifier
                        ):  # if equal to previous mobs, add to best
                            best_combatants.append(current_mob)
        elif mob_type == "pmob":
            for current_mob in self.contained_mobs:
                if current_mob.is_pmob:
                    if (
                        current_mob.get_combat_strength() > 0
                    ):  # unit with 0 combat strength cannot fight
                        current_combat_modifier = current_mob.get_combat_modifier()
                        if (
                            current_mob.is_safari and target_type == "beast"
                        ):  # more likely to pick safaris for defense against beasts
                            current_combat_modifier += 3
                        elif target_type == "beast":
                            current_combat_modifier -= 1
                        if (
                            best_combatants[0] == "none"
                            or current_combat_modifier > best_combat_modifier
                        ):
                            best_combatants = [current_mob]
                            best_combat_modifier = current_combat_modifier
                        elif current_combat_modifier == best_combat_modifier:
                            if (
                                current_mob.veteran and not best_combatants[0].veteran
                            ):  # use veteran as tiebreaker
                                best_combatants = [current_mob]
                            else:
                                best_combatants.append(current_mob)
        return random.choice(best_combatants)

    def get_noncombatants(self, mob_type):
        """
        Description:
            Finds and returns all units of the inputted type in this cell that have 0 combat strength. Assumes that units in vehicles and buildings have already detached upon being attacked
        Input:
            string mob_type: Can be npmob or pmob, determines what kind of mob is searched for. An attacking pmob will search for noncombatant pmobs and vice versa
        Output:
            mob list: Returns the noncombatants of the inputted type in this cell
        """
        noncombatants = []
        if mob_type == "npmob":
            for current_mob in self.contained_mobs:
                if current_mob.is_npmob and current_mob.get_combat_strength() == 0:
                    noncombatants.append(current_mob)
        elif mob_type == "pmob":
            for current_mob in self.contained_mobs:
                if current_mob.is_pmob and current_mob.get_combat_strength() == 0:
                    noncombatants.append(current_mob)
        return noncombatants

    def copy(self, other_cell):
        """
        Description:
            Changes this cell into a copy of the inputted cell
        Input:
            cell other_cell: Cell to copy
        Output:
            None
        """
        self.contained_mobs = other_cell.contained_mobs
        self.contained_buildings = other_cell.contained_buildings
        self.village = other_cell.village
        other_cell.terrain_handler.add_cell(self)
        # self.tile.update_image_bundle(override_image=other_cell.tile.image) #correctly copies other cell's image bundle but ends up very pixellated due to size difference

    def draw(self):
        """
        Description:
            Draws this cell as a rectangle with a certain color on its grid, depending on this cell's color value, along with actors this cell contains
        Input:
            none
        Output:
            None
        """
        current_color = self.color
        red = current_color[0]
        green = current_color[1]
        blue = current_color[2]
        if not self.terrain_handler.visible:
            red, green, blue = constants.color_dict["blonde"]
        pygame.draw.rect(constants.game_display, (red, green, blue), self.Rect)
        if self.tile != "none":
            for current_image in self.tile.images:
                current_image.draw()
            if self.terrain_handler.visible and self.contained_mobs:
                for current_image in self.contained_mobs[0].images:
                    current_image.draw()
                self.show_num_mobs()

    def show_num_mobs(self):
        """
        Description:
            Draws a number showing how many mobs are in this cell if it contains multiple mobs, otherwise does nothing
        Input:
            None
        Output:
            None
        """
        length = len(self.contained_mobs)
        if length >= 2:
            message = str(length)
            font = constants.fonts["max_detail_white"]
            font_width = self.width * 0.13 * 1.3
            font_height = self.width * 0.3 * 1.3
            textsurface = font.pygame_font.render(message, False, font.color)
            textsurface = pygame.transform.scale(
                textsurface, (font_width * len(message), font_height)
            )
            text_x = self.pixel_x + self.width - (font_width * (len(message) + 0.3))
            text_y = self.pixel_y + (-0.8 * self.height) - (0.5 * font_height)
            constants.game_display.blit(textsurface, (text_x, text_y))

    def touching_mouse(self):
        """
        Description:
            Returns True if this cell is colliding with the mouse, otherwise returns False
        Input:
            None
        Output:
            boolean: Returns True if this cell is colliding with the mouse, otherwise returns False
        """
        if self.Rect.collidepoint(pygame.mouse.get_pos()):
            return True
        else:
            return False

    def find_adjacent_cells(self):
        """
        Description:
            Records a list of the cells directly adjacent to this cell. Also records these cells as values in a dictionary with string keys corresponding to their direction relative to this cell
        Input:
            None
        Output:
            None
        """
        adjacent_list = []

        adjacent_cell = self.grid.find_cell(
            (self.x - 1) % self.grid.coordinate_width, self.y
        )
        adjacent_list.append(adjacent_cell)
        self.adjacent_cells["left"] = adjacent_cell
        adjacent_cell = self.grid.find_cell(
            (self.x + 1) % self.grid.coordinate_width, self.y
        )
        adjacent_list.append(adjacent_cell)
        self.adjacent_cells["right"] = adjacent_cell
        adjacent_cell = self.grid.find_cell(
            self.x, (self.y - 1) % self.grid.coordinate_height
        )
        adjacent_list.append(adjacent_cell)
        self.adjacent_cells["down"] = adjacent_cell
        adjacent_cell = self.grid.find_cell(
            self.x, (self.y + 1) % self.grid.coordinate_height
        )
        adjacent_list.append(adjacent_cell)
        self.adjacent_cells["up"] = adjacent_cell

        self.adjacent_list = adjacent_list
