# Contains functionality for buildings

from typing import Dict, List
from modules.constructs.actor_types import locations
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
        self.subscribed_location: locations.location = input_dict["location"]
        self.damaged = False
        self.upgrade_fields: Dict[str, int] = {}
        for upgrade_field in self.building_type.upgrade_fields:
            self.upgrade_fields[upgrade_field] = input_dict.get(upgrade_field, 1)
        status.building_list.append(self)
        self.subscribed_work_crews = []
        if from_save:
            for current_work_crew in input_dict["subscribed_work_crews"]:
                constants.ActorCreationManager.create(
                    True, current_work_crew
                ).work_building(self)
            if self.building_type.can_damage:
                self.set_damaged(input_dict["damaged"], mid_setup=True)

        if (not from_save) and self.building_type.can_damage:
            self.set_damaged(False, True)
        self.location.add_building(self)

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
    def location(self) -> locations.location:
        """
        Description:
            Returns the location this location is currently in
        Input:
            None
        Output:
            location: Returns the location this location is currently in
        """
        return self.subscribed_location

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
                'subscribed_work_crews': dictionary list value - list of dictionaries of saved information necessary to recreate each work crew working in this building
                'damaged': boolean value - whether this building is currently damaged
        """
        return {
            **self.upgrade_fields,
            "init_type": self.building_type.key,
            "subscribed_work_crews": [
                current_work_crew.to_save_dict()
                for current_work_crew in self.subscribed_work_crews
            ],
            "damaged": self.damaged,
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
        elif self.building_type == constants.WAREHOUSES:
            tooltip_text.append(
                f"Level {self.upgrade_fields[constants.WAREHOUSE_LEVEL]} warehouses allow an inventory capacity of {9 * self.upgrade_fields[constants.WAREHOUSE_LEVEL]}"
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
        if self.building_type.warehouse_level > 0 and self.location.has_building(
            constants.WAREHOUSES
        ):
            self.location.get_building(constants.WAREHOUSES).set_damaged(new_value)
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
                    resource_image_id = f"buildings/{constants.resource_building_dict[self.resource_type.key]}_no_work_crew.png"
                else:
                    resource_image_id = f"buildings/{constants.resource_building_dict[self.resource_type.key]}.png"
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
                    "image_id": "buildings/damaged.png",
                    "level": constants.BULIDING_INDICATOR_LEVEL,
                    **modifiers,
                }
            )
        return return_list


class infrastructure_building(building):
    """
    Building that eases movement between locations and is a road or railroad. Has images that show connections with other locations that have roads or railroads
    """

    def __init__(self, from_save, input_dict):
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'location': location value - Where this building is located
                'image': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'name': string value - Required if from save, this building's name
                'infrastructure_type': string value - Type of infrastructure, like 'road' or 'railroad'
                'subscribed_work_crews': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each work crew working in this building
        Output:
            None
        """
        return
        self.infrastructure_type = input_dict["infrastructure_type"]
        if self.infrastructure_type == constants.RAILROAD:
            self.is_railroad = True
            self.is_road = False
            self.is_bridge = False
        elif self.infrastructure_type == constants.ROAD:
            self.is_railroad = False
            self.is_road = True
            self.is_bridge = False
        elif self.infrastructure_type == constants.RAILROAD_BRIDGE:
            self.is_railroad = True
            self.is_road = False
            self.is_bridge = True
        elif self.infrastructure_type == constants.ROAD_BRIDGE:
            self.is_railroad = False
            self.is_road = True
            self.is_bridge = True
        elif self.infrastructure_type == constants.FERRY:
            self.is_railroad = False
            self.is_road = False
            self.is_bridge = True

        self.connection_image_dict = {}
        for infrastructure_type in [constants.ROAD, constants.RAILROAD]:
            if infrastructure_type == constants.ROAD:
                building_types = [constants.ROAD, constants.RAILROAD]
                directions = ["up", "down", "left", "right"]
            elif infrastructure_type in [
                constants.ROAD_BRIDGE,
                constants.RAILROAD_BRIDGE,
                constants.FERRY,
            ]:
                building_types = [
                    constants.ROAD_BRIDGE,
                    constants.RAILROAD_BRIDGE,
                    constants.FERRY,
                ]
                directions = ["vertical", "horizontal"]
            for direction in directions:
                for building_type in building_types:
                    self.connection_image_dict[f"{direction}_{building_type}"] = (
                        f"buildings/infrastructure/{direction}_{building_type}.png"
                    )

        super().__init__(from_save, input_dict)
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
        return
        save_dict = super().to_save_dict()
        save_dict["infrastructure_type"] = self.infrastructure_type
        return save_dict

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
        return
        image_id_list = super().get_image_id_list()
        if self.location.terrain != "water":
            connected_road, connected_railroad = (False, False)
            for direction in ["up", "down", "left", "right"]:
                adjacent_location = self.location.adjacent_locations[direction]
                own_infrastructure = self.location.get_intact_building(
                    constants.INFRASTRUCTURE
                )
                adjacent_infrastructure = adjacent_location.get_intact_building(
                    constants.INFRASTRUCTURE
                )
                if adjacent_infrastructure:
                    if (
                        adjacent_infrastructure.is_railroad
                        and own_infrastructure.is_railroad
                    ):
                        image_id_list.append(
                            self.connection_image_dict[direction + "_railroad"]
                        )
                    else:
                        image_id_list.append(
                            self.connection_image_dict[direction + "_road"]
                        )
                    if adjacent_infrastructure.is_road:
                        connected_road = True
                    elif adjacent_infrastructure.is_railroad:
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


class warehouses(building):
    """
    Buiding attached to a port, train station, and/or resource production facility that stores items
    """

    def __init__(self, from_save, input_dict):
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'location': location value - Where this building is located
                'image': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'name': string value - Required if from save, this building's name
                'subscribed_work_crews': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each work crew working in this building
                'warehouse_level': int value - Required if from save, size of warehouse (9 inventory capacity per level)
        Output:
            None
        """
        super().__init__(from_save, input_dict)
        self.location.set_inventory_capacity(
            self.upgrade_fields[constants.WAREHOUSE_LEVEL] * 9
        )
        if constants.EffectManager.effect_active("damaged_buildings"):
            if self.building_type.can_damage:
                self.set_damaged(True, True)

    def get_upgrade_cost(self):
        """
        Returns the cost of the next upgrade for this building. The first successful upgrade costs 5 money and each subsequent upgrade costs twice as much as the previous. Building a train station, resource production facility, or
            port gives a free upgrade that does not affect the costs of future upgrades
        """
        return self.location.get_warehouses_cost()

    def upgrade(self, upgrade_type="warehouses_level"):
        super().upgrade(upgrade_type)
        self.location.set_inventory_capacity(
            self.upgrade_fields[constants.WAREHOUSE_LEVEL] * 9
        )


class resource_building(building):
    """
    Building on a resource that allows work crews to attach to this building to produce resources over time
    """

    def __init__(self, from_save, input_dict):
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'location': location value - Where this building is located
                'image': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'name': string value - Required if from save, this building's name
                'resource_type': item_type value - Type of resource produced by this building, like "Gold"
                'subscribed_work_crews': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each work crew working in this building
                'scale': int value - Required if from save, maximum number of work crews that can be attached to this building
                'efficiency': int value - Required if from save, number of rolls made by work crews each turn to produce resources at this building
        Output:
            None
        """
        if from_save:
            self.resource_type: item_types.item_type = status.item_types[
                input_dict["resource_type"]
            ]  # If from save, uses saved key
        else:
            self.resource_type: item_types.item_type = input_dict[
                "resource_type"
            ]  # If during game, uses existing item type
        # Continue this conversion
        self.num_upgrades = (
            self.upgrade_fields[constants.RESOURCE_SCALE]
            + self.upgrade_fields[constants.RESOURCE_EFFICIENCY]
            - 2
        )
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
                'subscribed_work_crews': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each work crew working in this building
                'resource_type': string value - Type of resource produced by this building, like 'exotic wood'
                'scale': int value - Maximum number of work crews that can be attached to this building
                'efficiency': int value - Number of rolls made by work crews each turn to produce resources at this building
        """
        save_dict = super().to_save_dict()
        save_dict["resource_type"] = self.resource_type.key
        return save_dict

    def eject_work_crews(self):
        """
        Removes this building's work crews
        """
        for current_work_crew in self.subscribed_work_crews:
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
        After combat is finished, returns any surviving work crews to this building, if possible
        """
        for current_work_crew in self.ejected_work_crews:
            if current_work_crew in status.pmob_list:  # if not dead
                current_work_crew.work_building(self)
        self.ejected_work_crews = []

    def remove(self):
        """
        Removes this object from relevant lists, prevents it from further appearing in or affecting the program, and removes it from the location it occupies
        """
        status.resource_building_list = utility.remove_from_list(
            status.resource_building_list, self
        )
        super().remove()

    def upgrade(self, upgrade_type):
        """
        Description:
            Upgrades this building in the inputted field, such as by increasing the building's efficiency by 1 when 'efficiency' is inputted
        Input:
            string upgrade_type: Represents type of upgrade, like 'scale' or 'effiency'
        Output:
            None
        """
        self.upgrade_fields[upgrade_type] += 1
        if (
            self.upgrade_fields.get(constants.RESOURCE_SCALE) >= 6
            and self.upgrade_fields.get(constants.RESOURCE_EFFICIENCY) >= 6
        ):
            constants.AchievementManager.achieve("Industrialist")
        self.num_upgrades += 1

    def get_upgrade_cost(self):
        """
        Returns the cost of the next upgrade for this building. The first successful upgrade costs 20 money and each subsequent upgrade costs twice as much as the previous
        """
        if constants.EffectManager.effect_active("free_upgrades"):
            return 0
        else:
            return self.building_type.upgrade_fields[constants.RESOURCE_SCALE][
                "cost"
            ] * (
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
            cost += self.building_type.upgrade_fields[constants.RESOURCE_SCALE][
                "cost"
            ] * (i + 1)
        return cost

    def produce(self):
        """
        Orders each work crew attached to this building to attempt producing resources at the end of a turn. Based on work crew experience and minister skill/corruption, each work crew can produce a number of resources up to the
            building's efficiency
        """
        for current_work_crew in self.subscribed_work_crews:
            current_work_crew.attempt_production(self)
