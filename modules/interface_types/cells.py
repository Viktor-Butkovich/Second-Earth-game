# Contains functionality for grid cells

import pygame
import random
from typing import Dict, List, Any
from modules.util import actor_utility
from modules.constructs import locations
from modules.constants import constants, status, flags


class cell:
    """
    Object representing one cell of a grid corresponding to one of its coordinates, able to contain terrain, resources, mobs, and tiles
    """

    def __init__(self, x, y, width, height, grid, color):
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
        self.tile: status.tile = None
        self.settlement = None
        self.location: locations.location = None
        self.contained_mobs: list = []
        self.grid.world_handler.find_location(self.x, self.y).add_cell(self)

    def has_unit(self, permissions, required_number=1):
        """
        Description:
            Returns whether this cell contains the requested amount of units with all the inputted permissions
        Input:
            string list permissions: List of permissions to search for
            int required_number=1: Number of units that must be found to return True
        Output:
            boolean: Returns whether this cell contains the requested amount of units with all the inputted permissions
        """
        num_found = 0
        for current_mob in self.contained_mobs:
            if current_mob.all_permissions(*permissions):
                num_found += 1
                if num_found >= required_number:
                    return True
        return False

    def get_unit(self, permissions, start_index: int = 0, get_all: bool = False):
        """
        Description:
            Returns the first unit in this cell with all the inputted permissions, or None if none are present
        Input:
            string list permissions: List of permissions to search for
            int start_index=0: Index of contained_mobs to start search from - if starting in middle, wraps around iteration to ensure all items are still checked
                Allows finding different units with repeated calls by changing start_index
            boolean get_all=False: If True, returns all units with the inputted permissions, otherwise returns the first
        Output:
            mob: Returns the first unit in this cell with all the inputted permissions, or None if none are present
                If get_all, otherwise returns List[mob]: Returns all units in this cell with all the inputted permissions
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
        if get_all:
            results = []
        for current_mob in iterated_list:
            if current_mob.all_permissions(*permissions):
                if get_all:
                    results.append(current_mob)
                else:
                    return current_mob
        if get_all:
            return results
        else:
            return None

    def get_best_combatant(self, mob_type):
        """
        Description:
            Finds and returns the best combatant of the inputted type in this cell. Combat ability is based on the unit's combat modifier and veteran status. Assumes that units in vehicles and buildings have already detached upon being
                attacked
        Input:
            string mob_type: Can be npmob or pmob, determines what kind of mob is searched for. An attacking pmob will search for the most powerful npmob and vice versa
            string target_type = 'human': Regardless of the mob type being searched for, target_type gives information about the npmob: when a pmob searches for an npmob, it will search for a 'human' or 'beast' npmob. When an npmob
                searches for a pmob, it will say whether it is a 'human' or 'beast' to correctly choose pmobs specialized at fighting that npmob type
        Output;
            mob: Returns the best combatant of the inputted type in this cell
        """
        best_combatants = [None]
        best_combat_modifier = 0
        if mob_type == "npmob":
            for current_mob in self.contained_mobs:
                if current_mob.get_permission(constants.NPMOB_PERMISSION):
                    current_combat_modifier = current_mob.get_combat_modifier()
                    if (
                        best_combatants[0] == None
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
                if current_mob.get_permission(constants.PMOB_PERMISSION):
                    if (
                        current_mob.get_combat_strength() > 0
                    ):  # unit with 0 combat strength cannot fight
                        current_combat_modifier = current_mob.get_combat_modifier()
                        if (
                            best_combatants[0] == None
                            or current_combat_modifier > best_combat_modifier
                        ):
                            best_combatants = [current_mob]
                            best_combat_modifier = current_combat_modifier
                        elif current_combat_modifier == best_combat_modifier:
                            if current_mob.get_permission(
                                constants.VETERAN_PERMISSION
                            ) and not best_combatants[0].get_permission(
                                constants.VETERAN_PERMISSION
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
                if (
                    current_mob.get_permission(constants.NPMOB_PERMISSION)
                    and current_mob.get_combat_strength() == 0
                ):
                    noncombatants.append(current_mob)
        elif mob_type == "pmob":
            for current_mob in self.contained_mobs:
                if (
                    current_mob.get_permission(constants.PMOB_PERMISSION)
                    and current_mob.get_combat_strength() == 0
                ):
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
        other_cell.location.add_cell(self)

    def draw(self):
        """
        Description:
            Draws this cell as a rectangle with a certain color on its grid, depending on this cell's color value, along with actors this cell contains
        Input:
            None
        Output:
            None
        """
        current_color = self.color
        red = current_color[0]
        green = current_color[1]
        blue = current_color[2]
        if not self.location.visible:
            red, green, blue = constants.color_dict[constants.COLOR_BLONDE]
        pygame.draw.rect(constants.game_display, (red, green, blue), self.Rect)
        if self.tile:
            for current_image in self.tile.images:
                current_image.draw()
            if self.location.visible and self.contained_mobs:
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
