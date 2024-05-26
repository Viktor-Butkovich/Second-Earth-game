# Contains functionality for terrain management classes

import random
from typing import List, Dict
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags


class terrain_manager_template:
    """
    Object that controls terrain templates
    """

    def __init__(self):
        """
        Description:
            Initializes this object
        Input:
            None
        Output:
            None
        """
        return


class terrain_handler:
    """
    "Single source of truth" handler for the terrain of each version of a cell on different grids
    """

    def __init__(self, attached_cell, from_save, save_dict=None):
        """
        Description:
            Initializes this object
        Input:
            cell attached_cell: Default strategic_map_grid cell to attach this handler to
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary save_dict: Dictionary of saved information necessary to recreate this terrain handler if loading grid
        """
        if from_save:
            self.terrain_features: Dict[str, bool] = save_dict["terrain_features"]
            self.terrain_parameters: Dict[str, int] = save_dict["terrain_parameters"]
            self.terrain_variant: int = save_dict["terrain_variant"]
            self.terrain: str = save_dict["terrain"]
            self.resource: str = save_dict["resource"]
        else:
            self.terrain_features: Dict[str, bool] = {}
            self.terrain_parameters: Dict[str, int] = {
                "temperature": 1,
                "roughness": 1,
                "vegetation": 1,
                "soil": 1,
                "water": 1,
            }
            self.terrain_variant: int = 0
            self.terrain: str = "none"
            self.resource: str = "none"
        self.default_cell = attached_cell
        self.attached_cells = []
        self.add_cell(attached_cell)

    def to_save_dict(self):
        save_dict = {}
        save_dict["terrain_variant"] = self.terrain_variant
        save_dict["terrain_features"] = self.terrain_features
        save_dict["terrain_parameters"] = self.terrain_parameters
        save_dict["terrain"] = self.terrain
        save_dict["resource"] = self.resource
        return save_dict

    def set_terrain(self, new_terrain):
        self.terrain = new_terrain
        self.terrain_variant = random.randrange(
            0, constants.terrain_variant_dict.get(new_terrain, 1)
        )
        for cell in self.attached_cells:
            if cell.tile != "none":
                cell.tile.set_terrain(self.terrain, update_image_bundle=False)

    def set_resource(self, new_resource):
        self.resource = new_resource
        for cell in self.attached_cells:
            if cell.tile != "none":
                cell.tile.set_resource(self.resource, update_image_bundle=False)

    def add_cell(self, cell):
        if cell.terrain_handler:
            cell.terrain_handler.remove_cell(cell)
        self.attached_cells.append(cell)
        cell.terrain_handler = self

        if cell.tile != "none":
            cell.tile.set_terrain(self.terrain, update_image_bundle=False)
            cell.tile.set_resource(self.resource, update_image_bundle=False)

    def remove_cell(self, cell):
        self.attached_cells.remove(cell)
        cell.terrain_handler = None
