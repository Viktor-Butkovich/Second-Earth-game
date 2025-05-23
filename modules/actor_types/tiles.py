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


class tile(actor):  # to do: make terrain tiles a subclass
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
                'grid': grid value - grid in which this tile can appear
                'image': string value - File path to the image used by this object
                'name': string value - This tile's name
                'modes': string list value - Game modes during which this actor's images can appear
                'show_terrain': boolean value - True if this tile shows a cell's terrain. False if it does not show terrain, like a veteran icon or resource icon
        Output:
            None
        """
        status.tile_list.append(self)
        self.actor_type = constants.TILE_ACTOR_TYPE
        self.selection_outline_color = constants.COLOR_YELLOW
        self.actor_match_outline_color = constants.COLOR_WHITE
        input_dict["grids"] = [
            input_dict["grid"]
        ]  # Give actor a 1-item list of grids as input
        self.name_icon = None
        self.resource: item_types.item_type = None
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
        self.cell = self.grid.find_cell(self.x, self.y)
        self.hosted_images = []
        if self.show_terrain:
            self.cell.tile = self
            self.image_dict["hidden"] = "terrains/paper_hidden.png"
            self.set_terrain(
                self.get_location().terrain
            )  # terrain is a property of the cell, being stored information rather than appearance, same for resource, set these in cell
            if self.cell.grid.from_save:
                self.inventory = self.cell.save_dict["inventory"]
            if self.cell.grid == status.strategic_map_grid:
                status.main_tile_list.append(
                    self
                )  # List of all tiles that can be interacted with, and don't purely exist for visual purposes - 1:1 relationship with locations

        elif self.grid.grid_type in constants.abstract_grid_type_list:
            self.cell.tile = self
            self.terrain = None
            if self.cell.grid.from_save:
                self.inventory = self.cell.save_dict["inventory"]
            if (
                self.grid.grid_type == constants.EARTH_GRID_TYPE
            ):  # Earth should be able to hold items despite not being terrain
                self.infinite_inventory_capacity = True
                if constants.effect_manager.effect_active("infinite_commodities"):
                    for current_item_type in status.item_types.values():
                        if current_item_type.can_sell:
                            self.inventory[current_item_type.key] = 10
            status.main_tile_list.append(
                self
            )  # List of all tiles that can be interacted with, and don't purely exist for visual purposes - 1:1 relationship with locations
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
            Returns the cell this tile is currently in
        Input:
            None
        Output:
            cell: Returns the cell this tile is currently in
        """
        return self.cell

    def get_location(self) -> locations.location:
        """
        Description:
            Returns the location this tile is currently in
        Input:
            None
        Output:
            location: Returns the location this tile is currently in
        """
        if not self.cell:
            return None
        return self.cell.location

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
        if self.grid == status.strategic_map_grid and not new_name in [
            "default",
            "placeholder",
        ]:  # make sure user is not allowed to input default or *.png as a tile name
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
                    "init_type": constants.NAME_ICON,
                    "tile": self,
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
        status.main_tile_list = utility.remove_from_list(status.main_tile_list, self)
        if self.name_icon:
            self.name_icon.remove()

    def draw_destination_outline(self, color="default"):  # called directly by mobs
        """
        Description:
            Draws an outline around this tile when the displayed mob has a pending movement order to move to this tile
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

    def draw_actor_match_outline(self, recursive=False):
        """
        Description:
            Draws an outline around the displayed tile. If the tile is shown on a minimap, tells the equivalent tile to also draw an outline around the displayed tile
        Input:
            boolean recursive=False: True if this function is being called by the equivalent tile on either the minimap grid or the strategaic map grid, otherwise False. Prevents infinite loops of equivalent tiles repeatedly
                calling each other
        Output:
            None
        """
        if self.images[0].can_show():
            for current_image in self.images:
                outline = self.cell.Rect
                pygame.draw.rect(
                    constants.game_display,
                    constants.color_dict[self.actor_match_outline_color],
                    (outline),
                    current_image.outline_width,
                )
        if not recursive:
            for tile in self.get_equivalent_tiles():
                tile.draw_actor_match_outline(recursive=True)

    def get_all_local_inventory(self) -> Dict[str, float]:
        """
        Description:
            Returns a dictionary of all items held by this tile and local mobs
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
            Returns the item upkeep requirements for all units in this tile
        Input:
            None
        Output:
            dictionary: Returns the item upkeep requirements for all units in this tile
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
            Removes random excess items from this tile until the number of items fits in this tile's inventory capacity
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

    def set_inventory(self, item: item_types.item_type, new_value: int) -> None:
        """
        Description:
            Sets the number of items of a certain type held by this tile. Also ensures that the tile info display is updated correctly
        Input:
            item_type item: Type of item to set the inventory of
            int new_value: Amount of items of the inputted type to set inventory to
        Output:
            None
        """
        super().set_inventory(item, new_value)
        equivalent_tiles = self.get_equivalent_tiles()
        for tile in equivalent_tiles:
            tile.inventory[item.key] = self.get_inventory(item)
        if status.displayed_tile in [self] + equivalent_tiles:
            actor_utility.calibrate_actor_info_display(status.tile_info_display, self)

    def set_inventory_capacity(self, new_value):
        """
        Description:
            Sets this unit's inventory capacity, updating info displays as needed
        Input:
            int new_value: New inventory capacity value
        Output:
            None
        """
        for tile in self.get_equivalent_tiles():
            tile.inventory_capacity = new_value
        super().set_inventory_capacity(new_value)

    def get_main_grid_coordinates(self) -> Tuple[int, int]:
        """
        Description:
            Returns the coordinates cooresponding to this tile on the strategic map grid. If this tile is already on the strategic map grid, just returns this tile's coordinates
        Input:
            None
        Output:
            int tuple: Two
        """
        if self.grid.is_mini_grid:
            return self.grid.get_main_grid_coordinates(self.x, self.y)
        else:
            return (self.x, self.y)

    def get_equivalent_tiles(self):
        """
        Description:
            Returns the corresponding minimap tile if this tile is on the strategic map grid or vice versa
        Input:
            None
        Output:
            tile: tile on the corresponding tile on the grid attached to this tile's grid
        """
        return_list = []
        if self.grid == status.strategic_map_grid:
            for mini_grid in self.grid.mini_grids:
                if mini_grid.is_on_mini_grid(self.x, self.y):
                    mini_x, mini_y = mini_grid.get_mini_grid_coordinates(self.x, self.y)
                    equivalent_cell = mini_grid.find_cell(mini_x, mini_y)
                    if equivalent_cell and equivalent_cell.tile:
                        return_list.append(equivalent_cell.tile)
        elif self.grid.is_mini_grid:
            main_x, main_y = self.grid.get_main_grid_coordinates(self.x, self.y)
            equivalent_cell = self.grid.attached_grid.find_cell(main_x, main_y)
            return_list.append(equivalent_cell.tile)
        return return_list

    def remove_hosted_image(self, old_image):
        """
        Description:
            Removes the inputted image from this tile's hosted images and updates this tile's image bundle
        Input:
            image old_image: Image to remove from this tile's hosted images
        Output:
            None
        """
        if old_image in self.hosted_images:
            self.hosted_images.remove(old_image)
            self.update_image_bundle()
            if hasattr(old_image, "hosting_tile"):
                old_image.hosting_tile = None

    def add_hosted_image(self, new_image):
        """
        Description:
            Adds the inputted image to this tile's hosted images and updates this tile's image bundle
        Input:
            image new_image: Image to add to this tile's hosted images
        Output:
            None
        """
        if hasattr(new_image, "hosting_tile"):
            if new_image.hosting_tile:
                new_image.hosting_tile.remove_hosted_image(new_image)
            new_image.hosting_tile = self

        self.hosted_images.append(new_image)
        self.update_image_bundle()

    def get_image_id_list(
        self,
        terrain_only=False,
        force_visibility=False,
        force_clouds=False,
        force_pixellated=False,
        allow_mapmodes=True,
        allow_clouds=True,
    ):
        """
        Description:
            Generates and returns a list this actor's image file paths and dictionaries that can be passed to any image object to display those images together in a particular order and
                orientation
        Input:
            boolean terrain_only = False: Whether to just show tile's terrain or all contents as well
            boolean force_visibility = False: Shows a fully visible version of this tile, even if it hasn't been explored yet
        Output:
            list: Returns list of string image file paths, possibly combined with string key dictionaries with extra information for offset images
        """
        image_id_list = []
        if (
            (not allow_mapmodes)
            or constants.current_map_mode == "terrain"
            or constants.MAP_MODE_ALPHA
        ):
            if self.cell.grid.is_mini_grid:
                equivalent_tiles = self.get_equivalent_tiles()
                if equivalent_tiles and self.show_terrain:
                    image_id_list = equivalent_tiles[0].get_image_id_list()
                for current_image in self.hosted_images:
                    image_id_list += current_image.get_image_id_list()
            elif self.cell.grid == status.earth_grid:
                image_id_list = []
            else:
                if (
                    self.get_location().visible or force_visibility
                ):  # Force visibility shows full tile even if tile is not yet visible
                    image_id_list.append(
                        {
                            "image_id": self.image_dict["default"],
                            "level": -9,
                            "color_filter": self.get_location().get_color_filter(),
                            "green_screen": self.get_location().get_green_screen(),
                            "pixellated": force_pixellated
                            or not self.get_location().knowledge_available(
                                constants.TERRAIN_KNOWLEDGE
                            ),
                            "detail_level": constants.TERRAIN_DETAIL_LEVEL,
                        }
                    )
                    if allow_clouds:
                        for (
                            terrain_overlay_image
                        ) in self.get_location().get_overlay_images():
                            if type(terrain_overlay_image) == str:
                                terrain_overlay_image = {
                                    "image_id": terrain_overlay_image,
                                }
                            terrain_overlay_image.update(
                                {
                                    "level": -8,
                                    "color_filter": self.get_location().get_color_filter(),
                                    "pixellated": force_pixellated
                                    or not self.get_location().knowledge_available(
                                        constants.TERRAIN_KNOWLEDGE
                                    ),
                                    "detail_level": terrain_overlay_image.get(
                                        "detail_level", constants.TERRAIN_DETAIL_LEVEL
                                    ),
                                }
                            )
                            if not terrain_overlay_image.get("green_screen", None):
                                terrain_overlay_image["green_screen"] = (
                                    self.get_location().get_green_screen()
                                )
                            image_id_list.append(terrain_overlay_image)
                    if allow_clouds and (
                        constants.effect_manager.effect_active("show_clouds")
                        or force_clouds
                        or not self.get_location().knowledge_available(
                            constants.TERRAIN_KNOWLEDGE
                        )
                    ):
                        for cloud_image in self.get_location().current_clouds:
                            image_id_list.append(cloud_image.copy())
                            if not image_id_list[-1].get("detail_level", None):
                                image_id_list[-1][
                                    "detail_level"
                                ] = constants.TERRAIN_DETAIL_LEVEL
                            image_id_list[-1]["level"] = -7
                            if not image_id_list[-1].get("green_screen", None):
                                image_id_list[-1][
                                    "green_screen"
                                ] = self.get_location().get_green_screen()
                    if not terrain_only:
                        for terrain_feature in self.get_location().terrain_features:
                            new_image_id = (
                                self.get_location()
                                .terrain_features[terrain_feature]
                                .get(
                                    "image_id",
                                    status.terrain_feature_types[
                                        terrain_feature
                                    ].image_id,
                                )
                            )
                            if new_image_id != "misc/empty.png":
                                if type(
                                    new_image_id
                                ) == str and not new_image_id.endswith(".png"):
                                    new_image_id = (
                                        actor_utility.generate_label_image_id(
                                            new_image_id, y_offset=-0.75
                                        )
                                    )
                                image_id_list = utility.combine(
                                    image_id_list, new_image_id
                                )
                        if (
                            self.get_location().resource
                        ):  # If resource visible based on current knowledge
                            resource_icon = actor_utility.generate_resource_icon(self)
                            if type(resource_icon) == str:
                                image_id_list.append(resource_icon)
                            else:
                                image_id_list += resource_icon
                        for building_type in status.building_types.keys():
                            current_building = self.get_location().get_building(
                                building_type
                            )
                            if current_building:
                                image_id_list += current_building.get_image_id_list()
                elif self.show_terrain:
                    pass
                    # image_id_list.append(self.image_dict["hidden"])
                else:
                    pass
                    # image_id_list.append(self.image_dict["default"])
                for current_image in self.hosted_images:
                    if (
                        not current_image.anchor_key in ["south_pole", "north_pole"]
                        and not terrain_only
                    ):
                        image_id_list += current_image.get_image_id_list()

        if constants.current_map_mode != "terrain" and allow_mapmodes:
            map_mode_image = "misc/map_modes/none.png"
            if constants.current_map_mode in constants.terrain_parameters:
                if self.get_location().knowledge_available(
                    constants.TERRAIN_PARAMETER_KNOWLEDGE
                ):
                    if constants.current_map_mode in [
                        constants.WATER,
                        constants.TEMPERATURE,
                        constants.VEGETATION,
                    ]:
                        map_mode_image = f"misc/map_modes/{constants.current_map_mode}/{self.cell.get_parameter(constants.current_map_mode)}.png"
                    else:
                        map_mode_image = f"misc/map_modes/{self.cell.get_parameter(constants.current_map_mode)}.png"
            elif constants.current_map_mode == "magnetic":
                if self.get_location().terrain_features.get(
                    "southern tropic", False
                ) or self.get_location().terrain_features.get("northern tropic", False):
                    map_mode_image = "misc/map_modes/equator.png"
                elif self.get_location().terrain_features.get("north pole", False):
                    map_mode_image = "misc/map_modes/north_pole.png"
                elif self.get_location().terrain_features.get("south pole", False):
                    map_mode_image = "misc/map_modes/south_pole.png"
            if constants.MAP_MODE_ALPHA:
                image_id_list.append(
                    {
                        "image_id": map_mode_image,
                        "detail_level": 1.0,
                        "alpha": constants.MAP_MODE_ALPHA,
                    }
                )
            else:
                image_id_list = [
                    {
                        "image_id": map_mode_image,
                        "detail_level": 1.0,
                    }
                ]
        for current_image in self.hosted_images:
            if (
                current_image.anchor_key in ["south_pole", "north_pole"]
                and not terrain_only
            ):
                image_id_list += current_image.get_image_id_list()

        return image_id_list

    def update_image_bundle(self, override_image=None):
        """
        Description:
            Updates this actor's images with its current image id list, also updating the minimap grid version if applicable
        Input:
            image_bundle override_image=None: Image bundle to update image with, setting this tile's image to a copy of the image bundle instead of generating a new image
                bundle
        Output:
            None
        """
        previous_image = self.previous_image
        if override_image:
            self.set_image(override_image)
        else:
            self.set_image(self.get_image_id_list())
        if self.grid == status.strategic_map_grid:
            for equivalent_tile in self.get_equivalent_tiles():
                equivalent_tile.update_image_bundle(override_image=override_image)
        if previous_image != self.previous_image:
            self.reselect()

    def reselect(self):
        """
        Description:
            Deselects and reselects this mob if it was already selected
        Input:
            None
        Output:
            None
        """
        if status.displayed_tile == self:
            actor_utility.calibrate_actor_info_display(status.tile_info_display, None)
            actor_utility.calibrate_actor_info_display(status.tile_info_display, self)

    def set_resource(
        self, new_resource: item_types.item_type, update_image_bundle=True
    ):
        """
        Description:
            Sets the resource type of this tile to the inputted value, removing or creating resource icons as needed
        Input:
            item_type new_resource: The new resource type of this tile, like "Gold" or None
            boolean update_image_bundle: Whether to update the image bundle - if multiple sets are being used on a tile, optimal to only update after the last one
        Output:
            None
        """
        self.resource = new_resource
        if update_image_bundle:
            self.update_image_bundle()

    def set_terrain(
        self, new_terrain, update_image_bundle=True
    ):  # to do, add variations like grass to all terrains
        """
        Description:
            Sets the terrain type of this tile to the inputted value, changing its appearance as needed
        Input:
            string new_terrain: The new terrain type of this tile, like 'swamp'
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

    def update_tooltip(self):
        """
        Description:
            Sets this tile's tooltip to what it should be whenever the player looks at the tooltip. If this tile is explored, sets tooltip to this tile's terrain and its resource, if any. Otherwise, sets tooltip to a description of how
                this tile has not explored
        Input:
            None
        Output:
            None
        """
        if not (
            self.cell.grid == status.strategic_map_grid
            or self.cell.grid.is_abstract_grid
        ):
            main_tile = self.get_equivalent_tiles()[0]
            main_tile.update_tooltip()
            self.set_tooltip(main_tile.tooltip_text)
        else:
            tooltip_message = []
            if self.grid.is_abstract_grid:
                tooltip_message.append(self.name)
            elif self.show_terrain:
                coordinates = self.get_main_grid_coordinates()
                tooltip_message.append(
                    f"Coordinates: ({coordinates[0]}, {coordinates[1]})"
                )
                if self.get_location().terrain:
                    knowledge_value = self.get_location().get_parameter(
                        constants.KNOWLEDGE
                    )
                    knowledge_keyword = (
                        constants.terrain_manager.terrain_parameter_keywords[
                            constants.KNOWLEDGE
                        ][knowledge_value]
                    )
                    knowledge_maximum = maximum = self.get_location().maxima.get(
                        constants.KNOWLEDGE, 5
                    )
                    tooltip_message.append(
                        f"Knowledge: {knowledge_keyword} ({knowledge_value}/{knowledge_maximum})"
                    )

                    if self.get_location().knowledge_available(
                        constants.TERRAIN_KNOWLEDGE
                    ):
                        tooltip_message.append(
                            f"    Terrain: {self.get_location().terrain.replace('_', ' ')}"
                        )
                        if self.get_location().knowledge_available(
                            constants.TERRAIN_PARAMETER_KNOWLEDGE
                        ):
                            for terrain_parameter in constants.terrain_parameters:
                                if terrain_parameter != constants.KNOWLEDGE:
                                    maximum = self.get_location().maxima.get(
                                        terrain_parameter, 5
                                    )
                                    value = self.cell.get_parameter(terrain_parameter)
                                    keyword = constants.terrain_manager.terrain_parameter_keywords[
                                        terrain_parameter
                                    ][
                                        value
                                    ]
                                    tooltip_message.append(
                                        f"    {terrain_parameter.capitalize()}: {keyword} ({value}/{maximum})"
                                    )
                        else:
                            tooltip_message.append(f"    Details unknown")
                    else:
                        tooltip_message.append(f"    Terrain unknown")

            if self.get_location().get_world_handler():
                overall_habitability = self.get_location().get_known_habitability()
                if (not self.cell.grid.is_abstract_grid) and (
                    self.get_location().get_parameter(constants.KNOWLEDGE)
                    < constants.TERRAIN_PARAMETER_KNOWLEDGE_REQUIREMENT
                ):
                    tooltip_message.append(
                        f"Habitability: {constants.HABITABILITY_DESCRIPTIONS[overall_habitability].capitalize()} (estimated)"
                    )
                else:
                    tooltip_message.append(
                        f"Habitability: {constants.HABITABILITY_DESCRIPTIONS[overall_habitability].capitalize()}"
                    )

            if self.show_terrain:
                for current_building in self.get_location().get_buildings():
                    current_building.update_tooltip()
                    tooltip_message.append("")
                    tooltip_message += current_building.tooltip_text

                if self.get_location().resource:  # If resource present, show resource
                    tooltip_message.append("")
                    tooltip_message.append(
                        f"This tile has {utility.generate_article(self.get_location().resource.name)} {self.get_location().resource.name} resource"
                    )
                for terrain_feature in self.get_location().terrain_features:
                    if status.terrain_feature_types[terrain_feature].visible:
                        tooltip_message.append("")
                        tooltip_message += status.terrain_feature_types[
                            terrain_feature
                        ].description

            held_items: List[item_types.item_type] = self.get_held_items()
            if (
                held_items
                or self.inventory_capacity > 0
                or self.infinite_inventory_capacity
            ):
                if self.infinite_inventory_capacity:
                    tooltip_message.append(f"Inventory: {self.get_inventory_used()}")
                else:
                    tooltip_message.append(
                        f"Inventory: {self.get_inventory_used()}/{self.inventory_capacity}"
                    )
                if not held_items:
                    tooltip_message.append("    None")
                else:
                    for item_type in held_items:
                        tooltip_message.append(
                            f"    {item_type.name.capitalize()}: {self.get_inventory(item_type)}"
                        )

            self.set_tooltip(tooltip_message)

    def set_coordinates(self, x, y):
        """
        Description:
            Sets this tile's grid coordinates to the inputted values
        Input:
            int x: new grid x coordinate
            int y: new grid y coordinate
        Output:
            None
        """
        self.x = x
        self.y = y

    def can_show_tooltip(self):  # only terrain tiles have tooltips
        """
        Description:
            Returns whether this tile's tooltip can be shown. Along with the superclass' requirements, only terrain tiles have tooltips and tiles outside of the strategic map boundaries on the minimap grid do not have tooltips
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
            Selects this tile and switches music based on which type of tile is selected, if the type of tile selected would change the music
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
                'grid': grid value - grid in which this tile can appear
                'image': string value - File path to the image used by this object
                'name': string value - This tile's name
                'modes': string list value - Game modes during which this actor's images can appear
        Output:
            None
        """
        input_dict["coordinates"] = (0, 0)
        input_dict["show_terrain"] = False
        if input_dict["grid"] == status.earth_grid:
            self.grid_image_id = [
                "misc/space.png",
                {
                    "image_id": "locations/earth.png",
                    "size": 0.8,
                    "detail_level": 1.0,
                },
            ]
        elif input_dict["grid"] == status.globe_projection_grid:
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
            Returns whether this tile's tooltip can be shown. Has default tooltip requirements of being visible and touching the mosue
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
