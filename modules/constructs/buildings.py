# Contains functionality for buildings

from __future__ import annotations
from typing import Dict, List
from modules.constructs.actor_types import locations
from modules.constructs import zones
from modules.util import utility, actor_utility, text_utility
from modules.constructs import building_types, item_types
from modules.constants import constants, status, flags


class building:
    """
    Modifiable point of interest within a location that is displayed but not directly selected
    """

    def __init__(self, from_save, input_dict):
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'building_type': building_type value - Type of building
                'location': location value - Where this building is located
                'building_type': string value - Type of building, like 'port'
                'subscribed_work_crews': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each work crew working in this building
                'damaged': boolean value - Required if from save, whether this building is currently damaged
        Output:
            None
        """
        self.uuid: str = constants.UuidManager.assign_uuid()
        self.building_type: building_types.building_type = input_dict.get(
            "building_type", status.building_types[input_dict["init_type"]]
        )
        self.subscribed_zone: zones.zone = input_dict["zone"]
        self.damaged = False
        self.upgrade_fields: Dict[str, int] = {}
        for upgrade_field in self.building_type.upgrade_fields:
            self.upgrade_fields[upgrade_field] = input_dict.get(upgrade_field, 1)
        status.building_list.append(self)
        if self.building_type.warehouse_level > 0:
            self.location.warehouse_level.set_modifier(
                self, self.building_type.warehouse_level
            )
        if from_save:
            if self.building_type.can_damage:
                self.set_damaged(input_dict["damaged"], mid_setup=True)

        if (not from_save) and self.building_type.can_damage:
            self.set_damaged(False, True)
        self.zone.add_building(self)

        if (
            constants.EffectManager.effect_active("damaged_buildings")
            and self.building_type.can_damage
        ):
            self.set_damaged(True, mid_setup=True)

        if (
            (not from_save)
            and self.building_type.attached_settlement
            and not self.location.settlement
        ):
            constants.ActorCreationManager.create(
                False,
                {
                    "init_type": constants.SETTLEMENT,
                    "location": self.location,
                },
            )

    @property
    def zone(self) -> zones.zone:
        """
        Description:
            Returns the zone this building is located in
        Input:
            None
        Output:
            zone: Returns the zone this building is located in
        """
        return self.subscribed_zone

    @property
    def location(self) -> locations.location:
        """
        Description:
            Returns the location this location is currently in
        Input:
            None
        Output:
            location: Returns the location this location is currently in
        """
        return self.zone.parent_location

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
                'damaged': boolean value - whether this building is currently damaged
        """
        return {
            **self.upgrade_fields,
            "init_type": self.building_type.key,
            "damaged": self.damaged,
            "zone_coordinates": (self.zone.x, self.zone.y),
        }

    def remove(self):
        """
        Removes this object from relevant lists and prevents it from further appearing in or affecting the program. Also removes this building from its location
        """
        self.location.remove_building(self)
        status.building_list = utility.remove_from_list(status.building_list, self)

    @property
    def tooltip_text(self) -> List[List[str]]:
        """
        Provides the tooltip for this object
        """
        tooltip_text = [
            text_utility.remove_underscores(self.building_type.name.capitalize())
        ]
        if self.building_type == constants.RESOURCE:
            tooltip_text.append(
                f"Work crews: {len(self.subscribed_work_crews)}/{self.upgrade_fields[constants.RESOURCE_SCALE]}"
            )
            for current_work_crew in self.subscribed_work_crews:
                tooltip_text.append(f"    {current_work_crew.name}")
            tooltip_text.append(
                f"Lets {self.upgrade_fields[constants.RESOURCE_SCALE]} attached work crews each attempt to produce {self.upgrade_fields[constants.RESOURCE_EFFICIENCY]} units of {self.resource_type.name} each turn"
            )
        else:
            tooltip_text += self.building_type.description
        if self.damaged:
            tooltip_text.append(
                "This building is damaged and is currently not functional."
            )
        return tooltip_text

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
        if self.building_type == constants.INFRASTRUCTURE:
            actor_utility.update_roads()
        if self.building_type.warehouse_level > 0:
            if new_value == True:
                self.location.warehouse_level.set_modifier(self, 0)
            else:
                self.location.warehouse_level.set_modifier(
                    self, self.building_type.warehouse_level
                )
            # The network of managed modifiers means this temporarily sets the warehouse level contribution from this building to
            #   0, which then decreases inventory capacity by the correct amount. Upon repair, set the modifier back to the
            #   building type's warehouse level to restore the original state.
        constants.EventBus.publish(self.uuid, constants.BUILDING_SET_DAMAGED_ROUTE)

    def get_build_cost(self):
        """
        Description:
            Returns the total cost of building this building and all of its upgrades, not accounting for failed attempts or terrain
        Input:
            None
        Output:
            double: Returns the total cost of building this building and all of its upgrades, not accounting for failed attempts or terrain
        """
        return self.building_type.cost

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

    def get_image_id_list(self):
        """
        Description:
            Generates and returns a list this actor's image file paths and dictionaries that can be passed to any image object to display those images together in a particular order and
                orientation. Infrastructure buildings display connections between themselves and adjacent infrastructure buildings
        Input:
            None
        Output:
            list: Returns list of string image file paths, possibly combined with string key dictionaries with extra information for offset images
        """
        if self.building_type.display_coordinates == (0, 0):
            modifiers = {
                "level": constants.BUILDING_LEVEL,
            }
        else:  # If not centered, make smaller and move to one of 6 top/bottom slots
            modifiers = {
                "size": 0.75 * 0.45,
                "x_offset": self.building_type.display_coordinates[0] * 0.33,
                "y_offset": self.building_type.display_coordinates[1] * 0.33,
                "level": constants.BUILDING_LEVEL,
            }
        return_list = [
            {
                **image_id,
                **modifiers,
            }
            for image_id in self.building_type.image_id_list
        ]
        if self.building_type == constants.RESOURCE:
            return_list[0]["green_screen"] = constants.quality_colors[
                self.upgrade_fields[constants.RESOURCE_EFFICIENCY]
            ]  # Set box to quality color based on efficiency
            return_list[0]["size"] = 0.6
            return_list[0]["level"] = constants.BUILDING_INDICATOR_LEVEL
            for scale in range(1, self.upgrade_fields[constants.RESOURCE_SCALE] + 1):
                scale_coordinates = {  # Place mine/camp/plantation icons in following order for each scale
                    1: (0, 1),  # top center
                    2: (-1, -1),  # bottom left
                    3: (1, -1),  # bottom right
                    4: (0, -1),  # bottom center
                    5: (-1, 1),  # top left
                    6: (1, 1),  # top right
                }
                if scale > len(self.subscribed_work_crews):
                    resource_image_id = f"items/equipment/buildings/{constants.resource_building_dict[self.resource_type.key]}_no_work_crew.png"
                else:
                    resource_image_id = f"items/equipment/buildings/{constants.resource_building_dict[self.resource_type.key]}.png"
                return_list.append(
                    {
                        "image_id": resource_image_id,
                        "size": return_list[0]["size"],
                        "level": return_list[0]["level"],
                        "x_offset": 0.12 * scale_coordinates[scale][0],
                        "y_offset": -0.07 + 0.07 * scale_coordinates[scale][1],
                    }
                )
        if self.damaged and self.building_type.can_construct:
            return_list.append(
                {
                    "image_id": "items/equipment/buildings/damaged.png",
                    "level": constants.BUILDING_INDICATOR_LEVEL,
                    **modifiers,
                }
            )
        return return_list