# Contains functionality for tiles and other cell icons

import pygame
import random
import math
from typing import Tuple, Dict, List
from modules.constructs import images
from modules.util import utility, actor_utility, main_loop_utility
from modules.actor_types.actors import actor
from modules.interface_types import cells
from modules.constructs import item_types, locations
from modules.constants import constants, status, flags


class tile(actor):
    """
    An actor that appears under other actors and occupies a grid cell, being able to act as a passive icon, resource, terrain, or a hidden area
    """

    def __init__(self, from_save, input_dict, original_constructor=True):
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'grid': grid value - grid in which this location can appear
                'image': string value - File path to the image used by this object
                'name': string value - this location's name
                'modes': string list value - Game modes during which this actor's images can appear
                'show_terrain': boolean value - True if this location shows a cell's terrain. False if it does not show terrain, like a veteran icon or resource icon
        Output:
            None
        """
        status.tile_list.append(self)
        self.actor_type = constants.LOCATION_ACTOR_TYPE

        input_dict["grids"] = [
            input_dict["grid"]
        ]  # Give actor a 1-item list of grids as input
        self.name_icon = None
        self.resource: item_types.item_type = None
        self.cell = input_dict["cell"]
        self.grid = input_dict["grid"]
        super().__init__(from_save, input_dict, original_constructor=False)
        self.set_name(input_dict["name"])
        self.image_dict = {"default": input_dict["image"]}
        self.image = images.tile_image(
            self,
            self.grid.get_cell_width(),
            self.grid.get_cell_height(),
            input_dict["grid"],
            "default",
        )
        self.images = [
            self.image
        ]  # tiles only appear on 1 grid, but have a list of images defined to be more consistent with other actor subclasses
        self.show_terrain = input_dict["show_terrain"]
        if self.show_terrain:
            self.cell.tile = self
            self.image_dict["hidden"] = "terrains/paper_hidden.png"
            self.set_terrain(
                self.get_location().terrain
            )  # terrain is a property of the cell, being stored information rather than appearance, same for resource, set these in cell
            # if self.cell.grid.from_save:
            #    self.inventory = self.cell.save_dict["inventory"]

        elif self.grid.world_handler.is_abstract_world:
            self.cell.tile = self
            self.terrain = None
            # if self.cell.grid.from_save:
            #    self.inventory = self.cell.save_dict["inventory"]
            if (
                self.cell.get_location().get_world_handler().is_earth
            ):  # Earth should be able to hold items despite not being terrain
                self.infinite_inventory_capacity = True
                if constants.effect_manager.effect_active("infinite_commodities"):
                    for current_item_type in status.item_types.values():
                        if current_item_type.can_sell:
                            self.inventory[current_item_type.key] = 10
        else:
            self.terrain = None
        self.finish_init(original_constructor, from_save, input_dict)
        if (
            self.name == "default"
        ):  # Set tile name to that of any terrain features, if applicable
            for terrain_feature in self.get_location().terrain_features:
                if (
                    self.get_location()
                    .terrain_features[terrain_feature]
                    .get("name", False)
                ):
                    self.set_name(
                        self.get_location().terrain_features[terrain_feature]["name"]
                    )

    def get_cell(self) -> cells.cell:
        """
        Description:
            Returns the cell this location is currently in
        Input:
            None
        Output:
            cell: Returns the cell this location is currently in
        """
        return self.cell

    def get_location(self) -> locations.location:
        """
        Description:
            Returns the location this location is currently in
        Input:
            None
        Output:
            location: Returns the location this location is currently in
        """
        if not self.cell:
            return None
        return self.cell.get_location()

    def set_name(self, new_name):
        """
        Description:
            Sets this actor's name, also updating its name icon if applicable
        Input:
            string new_name: Name to set this actor's name to
        Output:
            None
        """
        super().set_name(new_name)
        if (
            not self.get_location().get_world_handler().is_abstract_world
        ) and new_name not in ["default", "placeholder"]:
            # Make sure user is not allowed to input default or *.png as a tile name
            if self.name_icon:
                self.name_icon.remove_complete()

            y_offset = -0.75
            has_building = False
            for building_type in status.building_types.keys():
                if (
                    self.get_location().has_building(building_type)
                    and building_type != constants.INFRASTRUCTURE
                ):  # if any building present, shift name up to not cover them
                    has_building = True
                    break
            if has_building:
                y_offset += 0.3

            self.name_icon = constants.actor_creation_manager.create(
                False,
                {
                    "coordinates": (self.x, self.y),
                    "grids": [self.grid] + self.grid.mini_grids,
                    "image": actor_utility.generate_label_image_id(
                        new_name, y_offset=y_offset
                    ),
                    "modes": self.grid.mini_grids[0].modes,
                    "init_type": constants.CELL_ICON,
                    "location": self,
                },
            )

    def remove(self):
        """
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        Input:
            None
        Output:
            None
        """
        super().remove()
        status.tile_list = utility.remove_from_list(status.tile_list, self)
        if self.name_icon:
            self.name_icon.remove()

    def draw_destination_outline(self, color="default"):  # called directly by mobs
        """
        Description:
            Draws an outline around this location when the displayed mob has a pending movement order to move to this location
        Input:
            string color = 'default': If an input is given, that color from the color_dict will be used instead of the default destination outline color
        Output:
            None
        """
        for current_image in self.images:
            if current_image.can_show():
                outline = self.cell.Rect
                if color == "default":
                    color = constants.color_dict[self.selection_outline_color]
                else:
                    color = constants.color_dict[
                        color
                    ]  # converts input string to RGB tuple
                pygame.draw.rect(
                    constants.game_display,
                    color,
                    (outline),
                    current_image.outline_width,
                )

    def get_all_local_inventory(self) -> Dict[str, float]:
        """
        Description:
            Returns a dictionary of all items held by this location and local mobs
        Input:
            None
        Output:
            None
        """
        return utility.add_dicts(
            self.inventory, *[mob.inventory for mob in self.cell.contained_mobs]
        )

    def create_item_request(self, required_items: Dict[str, float]) -> Dict[str, float]:
        """
        Description:
            Given a dictionary of required items with amounts, create a dictionary of the amount of items that need to be externally sourced to meet the requirements
        Input:
            Dict[str, float] required_items: Dictionary of required items with amounts
        Output:
            Dict[str, float]: Dictionary of items with amounts that need to be externally sourced to meet the requirements
        """
        return {
            key: value
            for key, value in utility.subtract_dicts(
                required_items, self.get_all_local_inventory()
            ).items()
            if value > 0
        }

    def fulfill_item_request(
        self, requested_items: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Description:
            Attempt to externally source the requested items
        Input:
            Dict[str, float] requested_items: Dictionary of items with amounts that need to be externally sourced to meet the requirements
        Output:
            Dict[str, float]: Dictionary of items with amounts that can not be provided
        """
        if constants.ENERGY_ITEM in requested_items:
            missing_energy = self.consume_items(
                {constants.FUEL_ITEM: requested_items[constants.ENERGY_ITEM]}
            ).get(constants.ENERGY_ITEM, 0)
            # Attempt to consume fuel equal to energy request - returns amount of request that cannot be met
            self.change_inventory(
                status.item_types[constants.ENERGY_ITEM],
                requested_items[constants.ENERGY_ITEM] - missing_energy,
            )  # Turn fuel into required energy
            requested_items[constants.ENERGY_ITEM] = missing_energy
        requested_items = {
            key: value for key, value in requested_items.items() if value > 0
        }  # Remove fulfilled requests
        return requested_items

    def get_item_upkeep(
        self, recurse: bool = False, earth_exemption: bool = True
    ) -> Dict[str, float]:
        """
        Description:
            Returns the item upkeep requirements for all units in this location
        Input:
            None
        Output:
            dictionary: Returns the item upkeep requirements for all units in this location
        """
        return utility.add_dicts(
            *[
                mob.get_item_upkeep(recurse=recurse, earth_exemption=earth_exemption)
                for mob in self.cell.contained_mobs
            ]
        )

    def remove_excess_inventory(self):
        """
        Description:
            Removes random excess items from this location until the number of items fits in this location's inventory capacity
        Input:
            None
        Output:
            None
        """
        lost_items: Dict[str, float] = {}
        if not self.infinite_inventory_capacity:
            amount_to_remove = self.get_inventory_used() - self.inventory_capacity
            if amount_to_remove > 0:
                for current_item_type in self.get_held_items():
                    decimal_amount = round(
                        self.get_inventory(current_item_type)
                        - math.floor(self.get_inventory(current_item_type)),
                        2,
                    )
                    if (
                        decimal_amount > 0
                    ):  # Best to remove partially consumed items first, since they each take an entire inventory slot
                        lost_items[current_item_type.key] = (
                            lost_items.get(current_item_type.key, 0) + decimal_amount
                        )
                        self.change_inventory(current_item_type, -decimal_amount)
                        amount_to_remove -= 1
                    if amount_to_remove <= 0:
                        break
            if amount_to_remove > 0:
                items_held = []
                for current_item_type in self.get_held_items():
                    items_held += [current_item_type] * self.get_inventory(
                        current_item_type
                    )
                item_types_removed = random.sample(
                    population=items_held, k=amount_to_remove
                )
                for (
                    current_item_type
                ) in item_types_removed:  # Randomly remove amount_to_remove items
                    lost_items[current_item_type.key] = (
                        lost_items.get(current_item_type.key, 0) + 1
                    )
                    self.change_inventory(current_item_type, -1)
        if sum(lost_items.values()) > 0:
            if sum(lost_items.values()) == 1:
                was_word = "was"
            else:
                was_word = "were"
            status.logistics_incident_list.append(
                {
                    "unit": self,
                    "cell": self.get_cell(),
                    "explanation": f"{actor_utility.summarize_amount_dict(lost_items)} {was_word} lost due to insufficient storage space.",
                }
            )

    def get_absolute_coordinates(self) -> Tuple[int, int]:
        """
        Description:
            Returns the coordinates cooresponding to this location on the strategic map grid. If this location is already on the strategic map grid, just returns this location's coordinates
        Input:
            None
        Output:
            int tuple: Two
        """
        if self.grid.world_handler.is_abstract_world:
            return (1, 1)
        else:
            return self.grid.get_absolute_coordinates(self.x, self.y)

    def set_terrain(
        self, new_terrain, update_image_bundle=True
    ):  # to do, add variations like grass to all terrains
        """
        Description:
            Sets the terrain type of this location to the inputted value, changing its appearance as needed
        Input:
            string new_terrain: The new terrain type of this location, like 'swamp'
            boolean update_image_bundle: Whether to update the image bundle - if multiple sets are being used on a tile, optimal to only update after the last one
        Output:
            None
        """
        if new_terrain in constants.terrain_manager.terrain_list:
            self.image_dict["default"] = (
                f"terrains/{new_terrain}_{self.get_location().terrain_variant}.png"
            )
        elif not new_terrain:
            self.image_dict["default"] = "terrains/hidden.png"
        if update_image_bundle:
            self.update_image_bundle()

    def can_show_tooltip(self):  # only terrain tiles have tooltips
        """
        Description:
            Returns whether this location's tooltip can be shown. Along with the superclass' requirements, only terrain tiles have tooltips and tiles outside of the strategic map boundaries on the minimap grid do not have tooltips
        Input:
            None
        Output:
            None
        """
        return (
            self.show_terrain
            and self.touching_mouse()
            and (constants.current_game_mode in self.modes)
            and self.get_location().terrain
        )

    def select(self, music_override: bool = False):
        """
        Description:
            Selects this location and switches music based on which type of tile is selected, if the type of tile selected would change the music
        Input:
            None
        Output:
            None
        """
        if music_override or (
            flags.player_turn and main_loop_utility.action_possible()
        ):
            if constants.sound_manager.previous_state != "earth":
                constants.event_manager.clear()
                constants.sound_manager.play_random_music("earth")


class abstract_tile(tile):
    """
    tile for 1-cell abstract grids like Earth, can have a tooltip but has no terrain, instead having a unique image
    """

    def __init__(self, from_save, input_dict):
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'grid': grid value - grid in which this location can appear
                'image': string value - File path to the image used by this object
                'name': string value - this location's name
                'modes': string list value - Game modes during which this actor's images can appear
        Output:
            None
        """
        input_dict["coordinates"] = (0, 0)
        input_dict["show_terrain"] = False
        if input_dict["grid"].world_handler.is_earth:
            self.grid_image_id = [
                "misc/space.png",
                {
                    "image_id": "locations/earth.png",
                    "size": 0.8,
                    "detail_level": 1.0,
                },
            ]
        else:  # Such as globe projection grid
            self.grid_image_id = [
                {
                    "image_id": "misc/empty.png",
                }
            ]
        input_dict["image"] = self.grid_image_id
        super().__init__(from_save, input_dict)

    def can_show_tooltip(self):
        """
        Description:
            Returns whether this location's tooltip can be shown. Has default tooltip requirements of being visible and touching the mosue
        Input:
            None
        Output:
            None
        """
        if self.touching_mouse() and constants.current_game_mode in self.modes:
            return True
        else:
            return False

    def get_image_id_list(self, **kwargs):
        return self.grid_image_id
