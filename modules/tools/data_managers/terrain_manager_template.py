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
    "Single source of truth" handler for the terrain/local characteristics of each version of a cell on different grids
    """

    def __init__(self, attached_cell, input_dict: Dict[str, any] = None) -> None:
        """
        Description:
            Initializes this object
        Input:
            cell attached_cell: Default strategic_map_grid cell to attach this handler to
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Dictionary of saved information necessary to recreate this terrain handler if loading grid, or None if creating new terrain handler
        """
        if not input_dict:
            input_dict = {}
        self.terrain_features: Dict[str, bool] = input_dict.get("terrain_features", {})
        self.terrain_parameters: Dict[str, int] = input_dict.get(
            "terrain_parameters",
            {
                "altitude": 1,
                "temperature": 1,
                "roughness": 1,
                "vegetation": 1,
                "soil": 1,
                "water": 1,
            },
        )
        self.terrain_variant: int = input_dict.get("terrain_variant", 0)
        self.terrain: str = input_dict.get("terrain", "none")
        self.resource: str = input_dict.get("resource", "none")
        self.visible: bool = input_dict.get("visible", True)
        self.default_cell = attached_cell
        self.attached_cells: list = []
        self.add_cell(attached_cell)

    def change_parameter(self, parameter_name: str, change: int) -> None:
        """
        Description:
            Changes the value of a parameter for this handler's cells
        Input:
            string parameter_name: Name of the parameter to change
            int change: Amount to change the parameter by
        Output:
            None
        """
        self.terrain_parameters[parameter_name] = max(
            1, min(self.terrain_parameters[parameter_name] + change, 6)
        )

    def set_parameter(self, parameter_name: str, new_value: int) -> None:
        """
        Description:
            Sets the value of a parameter for this handler's cells
        Input:
            string parameter_name: Name of the parameter to change
            int new_value: New value for the parameter
        Output:
            None
        """
        self.terrain_parameters[parameter_name] = max(1, min(new_value, 6))

    def to_save_dict(self) -> Dict[str, any]:
        """
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                'visible': boolean value - Whether this handler's cells are visible or not
                'terrain': string value - Terrain type of this handler's cells and their tiles, like 'swamp'
                'terrain_variant': int value - Variant number to use for image file path, like mountain_0
                'terrain_features': string/boolean dictionary value - Dictionary containing an entry for each terrain feature in this handler's cells
                'terrain_parameters': string/int dictionary value - Dictionary containing 1-6 parameters for this handler's cells, like 'temperature': 1
                'resource': string value - Resource type of this handler's cells and their tiles, like 'exotic wood'
        """
        save_dict = {}
        save_dict["terrain_variant"] = self.terrain_variant
        save_dict["terrain_features"] = self.terrain_features
        save_dict["terrain_parameters"] = self.terrain_parameters
        save_dict["terrain"] = self.terrain
        save_dict["resource"] = self.resource
        return save_dict

    def set_terrain(self, new_terrain) -> None:
        """
        Description:
            Sets this handler's terrain type, automatically generating a variant (not used for loading with pre-defined variant)
        Input:
            string new_terrain: New terrain type for this handler's cells and their tiles, like 'swamp'
        Output:
            None
        """
        self.terrain = new_terrain
        self.terrain_variant = random.randrange(
            0, constants.terrain_variant_dict.get(new_terrain, 1)
        )
        for cell in self.attached_cells:
            if cell.tile != "none":
                cell.tile.set_terrain(self.terrain, update_image_bundle=False)

    def set_resource(self, new_resource) -> None:
        """
        Description:
            Sets this handler's resource type
        Input:
            string new_terrain: New resource type for this handler's cells and their tiles, like 'rubber'
        Output:
            None
        """
        self.resource = new_resource
        for cell in self.attached_cells:
            if cell.tile != "none":
                cell.tile.set_resource(self.resource, update_image_bundle=False)

    def set_visibility(self, new_visibility, update_image_bundle=False) -> None:
        """
        Description:
            Sets the visibility of this cell and its attached tile to the inputted value. A visible cell's terrain and resource can be seen by the player.
        Input:
            boolean new_visibility: This cell's new visibility status
            boolean update_image_bundle: Whether to update the image bundle - if multiple sets are being used on a tile, optimal to only update after the last one
        Output:
            None
        """
        self.visible = new_visibility
        if update_image_bundle:
            for cell in self.attached_cells:
                if cell.tile != "none":
                    cell.tile.update_image_bundle()
        if new_visibility:
            constants.achievement_manager.check_achievements("Heart of Darkness")

    def add_cell(self, cell) -> None:
        """
        Description:
            Adds the inputted cell to this handler, removing it from any previous handler and updating its parameters to this handler's
        Input:
            cell: Cell to add to this handler
        Output:
            None
        """
        if cell.terrain_handler:
            cell.terrain_handler.remove_cell(cell)
        self.attached_cells.append(cell)
        cell.terrain_handler = self

        if cell.tile != "none":
            cell.tile.set_terrain(self.terrain, update_image_bundle=False)
            cell.tile.set_resource(self.resource, update_image_bundle=False)
            cell.tile.update_image_bundle()

    def remove_cell(self, cell) -> None:
        """
        Description:
            Removes the inputted cell from the terrain handler - precondition that cell is in the terrain handler
        Input:
            cell cell: Cell to remove from the terrain handler
        Output:
            None
        """
        self.attached_cells.remove(cell)
        cell.terrain_handler = None
