# Contains functionality for mobs

import pygame, random
from modules.constructs import images, unit_types, ministers, item_types, locations
from modules.util import (
    utility,
    actor_utility,
    main_loop_utility,
    text_utility,
    minister_utility,
)
from modules.interface_types import cells
from modules.actor_types.actors import actor
from modules.constants import constants, status, flags
from typing import List, Dict, Any


class mob(actor):
    """
    Actor that can be selected and move within and between grids, but cannot necessarily controlled
    """

    def __init__(self, from_save, input_dict, original_constructor: bool = True):
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'grids': grid list value - grids in which this mob's images can appear
                'image': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'name': string value - Required if from save, this mob's name
                'modes': string list value - Game modes during which this mob's images can appear
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'max_movement_points': int value - Required if from save, maximum number of movement points this mob can have
        Output:
            None
        """
        self.default_permissions: Dict[str, Any] = {}
        self.override_permissions: Dict[str, Any] = {}
        self.unit_type: unit_types.unit_type = input_dict.get(
            "unit_type", status.unit_types.get(input_dict.get("init_type"))
        )
        self.unit_type.num_instances += 1
        self.controlling_minister: ministers.minister = None
        self.update_controlling_minister()
        self.actor_type = constants.MOB_ACTOR_TYPE
        self.end_turn_destination = None
        self.habitability = constants.HABITABILITY_PERFECT
        self.ambient_sound_channel: pygame.mixer.Channel = None
        self.locked_ambient_sound: bool = False
        super().__init__(from_save, input_dict, original_constructor=False)
        if isinstance(input_dict["image"], str):
            self.image_dict = {"default": input_dict["image"]}
        else:
            self.image_dict = {"default": input_dict["image"]["image_id"]}
        self.image_variants_setup(from_save, input_dict)
        self.images: List[images.mob_image] = []
        self.status_icons = []
        for current_grid in self.grids:
            self.images.append(
                images.mob_image(
                    self,
                    current_grid.get_cell_width(),
                    current_grid.get_cell_height(),
                    current_grid,
                    "default",
                )
            )
        status.mob_list.append(self)
        self.set_name(input_dict["name"])
        self.max_movement_points = 1
        self.movement_points = self.max_movement_points
        self.movement_cost = 1
        self.permissions_setup()
        if from_save:
            self.set_max_movement_points(input_dict["max_movement_points"])
            self.set_movement_points(input_dict["movement_points"])
            self.creation_turn = input_dict["creation_turn"]
            self.set_permission(
                constants.DISORGANIZED_PERMISSION, input_dict.get("disorganized", False)
            )
            self.set_permission(
                constants.DEHYDRATION_PERMISSION, input_dict.get("dehydration", False)
            )
            self.set_permission(
                constants.STARVATION_PERMISSION, input_dict.get("starvation", False)
            )
        else:
            self.unit_type.on_recruit()
            self.reset_movement_points()
            if flags.creating_new_game:
                self.creation_turn = 0
            else:
                self.creation_turn = constants.turn
        self.finish_init(original_constructor, from_save, input_dict)

    def get_radio_effect(self) -> bool:
        """
        Description:
            Calculates and returns whether this unit's voicelines should have a radio filter applied, based on the unit's current circumstances
                Apply filter if spaceship or if wearing a spacesuit helmet
        Input:
            None
        Output:
            bool: Returns whether this unit's voiceliens should have a radio filter applied
        """
        return self.get_permission(constants.VEHICLE_PERMISSION) or (
            self.get_permission(constants.SPACESUITS_PERMISSION)
            and status.equipment_types[
                constants.SPACESUITS_EQUIPMENT
            ].can_show_portrait_section(self, constants.HAT_PORTRAIT_SECTION)
        )

    def check_action_survivability(self, notify: bool = True) -> bool:
        """
        Description:
            Checks whether this unit can survive doing an action in its current tile - no certain death actions are allowed
        Input:
            bool notify: Whether to notify the player if it is not survivable
        Output:
            bool: Returns True if this unit can survive doing an action in its current tile, False otherwise
        """
        survivable = self.get_permission(constants.SURVIVABLE_PERMISSION)
        if notify and not survivable:
            constants.notification_manager.display_notification(
                {
                    "message": "Due to the deadly local environmental conditions, this unit can perform no actions except equipping spacesuits or finding shelter locally. /n /n",
                },
            )
        return survivable

    def update_habitability(self):
        """
        Description:
            Updates this unit's habitability based on the tile it is in
        Input:
            None
        Output:
            None
        """
        if self.get_cell():
            self.habitability = self.get_location().get_unit_habitability(self)
            self.set_permission(
                constants.SURVIVABLE_PERMISSION,
                self.habitability != constants.HABITABILITY_DEADLY,
            )

    def can_travel(self):
        """
        Description:
            Returns whether this unit can move between grids, such as in space
        Input:
            None
        Output:
            boolean: Returs True if this unit has travel permissions (based on unit type), is active (crewed), and is not disabled this turn
        """
        return self.all_permissions(
            constants.TRAVEL_PERMISSION, constants.ACTIVE_PERMISSION
        ) and not self.get_permission(constants.MOVEMENT_DISABLED_PERMISSION)

    def update_controlling_minister(self):
        """
        Description:
            Sets the minister that controls this unit to the one occupying the office that has authority over this unit
        Input:
            None
        Output:
            None
        """
        self.controlling_minister = minister_utility.get_minister(
            self.unit_type.controlling_minister_type.key
        )
        for current_minister_type_image in status.minister_image_list:
            if (
                current_minister_type_image.minister_type
                == self.unit_type.controlling_minister_type
            ):
                current_minister_type_image.calibrate(self.controlling_minister)

    def get_cell(self) -> cells.cell:
        """
        Description:
            Returns the cell this mob is currently in
        Input:
            None
        Output:
            cell: Returns the cell this mob is currently in
        """
        if self.get_permission(constants.DUMMY_PERMISSION):
            if status.displayed_mob:
                return status.displayed_mob.get_cell()
            else:
                return None
        elif self.get_permission(constants.IN_VEHICLE_PERMISSION):
            return self.vehicle.get_cell()
        elif self.get_permission(constants.IN_GROUP_PERMISSION):
            return self.group.get_cell()
        return self.images[0].current_cell

    def get_location(self) -> locations.location:
        """
        Description:
            Returns the location this mob is currently in
        Input:
            None
        Output:
            location: Returns the location this mob is currently in
        """
        current_cell = self.get_cell()
        if current_cell:
            return current_cell.get_location()
        return None

    def on_move(self):
        """
        Description:
            Automatically called when unit arrives in a tile for any reason
        Input:
            None
        Output:
            None
        """
        current_cell = self.get_cell()
        if current_cell:
            self.update_habitability()
            if self.equipment:  # Update spacesuit image for local conditions
                self.update_image_bundle()

    def permissions_setup(self) -> None:
        """
        Description:
            Sets up this mob's permissions
        Input:
            None
        Output:
            None
        """
        for permission, value in self.unit_type.permissions.items():
            self.set_permission(permission, value)

    def set_permission(
        self, task: str, value: Any, override: bool = False, update_image: bool = True
    ) -> None:
        """
        Description:
            Sets the permission this mob has to perform the inputted task
        Input:
            string task: Task for which to set permission
            Any value: Permission value to set for the inputted task, deleting the permission if None
            boolean override: Whether to modify override permissions or default permissions
            boolean update_image: Whether to update the image bundle and tooltip after setting the permission
        Output:
            None
        """
        previous_effect = self.get_permission(task)
        if override:
            modified_permissions = self.override_permissions
        else:
            modified_permissions = self.default_permissions
        if value == None:
            if task in modified_permissions:
                del modified_permissions[task]
        else:
            modified_permissions[task] = value

        if (
            previous_effect != self.get_permission(task)
            and self.get_permission(constants.INIT_COMPLETE_PERMISSION)
            and not self.get_permission(constants.DUMMY_PERMISSION)
            and update_image
        ):
            self.update_image_bundle()
            self.update_tooltip()
        if task == constants.IN_VEHICLE_PERMISSION or (
            task in [constants.VEHICLE_PERMISSION, constants.SPACESUITS_PERMISSION]
            and (not self.get_permission(constants.DUMMY_PERMISSION))
            and self.get_cell()
        ):
            self.update_habitability()
        elif task == constants.TRAVELING_PERMISSION and self.get_permission(
            constants.SPACESHIP_PERMISSION
        ):
            self.start_ambient_sound()
        elif task == constants.STARVATION_PERMISSION and self.get_permission(
            constants.IN_GROUP_PERMISSION
        ):
            # Group is shown as starving if either component is starving
            self.group.set_permission(
                constants.STARVATION_PERMISSION,
                self.group.worker.get_permission(constants.STARVATION_PERMISSION)
                or self.group.officer.get_permission(constants.STARVATION_PERMISSION),
            )
        elif task == constants.DEHYDRATION_PERMISSION and self.get_permission(
            constants.IN_GROUP_PERMISSION
        ):
            # Group is shown as dehydrated if either component is dehydrated
            self.group.set_permission(
                constants.DEHYDRATION_PERMISSION,
                self.group.worker.get_permission(constants.DEHYDRATION_PERMISSION)
                or self.group.officer.get_permission(constants.DEHYDRATION_PERMISSION),
            )

    def all_permissions(self, *tasks: str) -> bool:
        """
        Description:
            Checks if this mob has permission to perform all of the inputted tasks
        Input:
            *tasks: Variable number of string arguments representing tasks to check permission for
        Output:
            bool: True if this mob has permission to perform all of the inputted tasks, False otherwise
        """
        for task in tasks:
            if not self.get_permission(task):
                return False
        return True

    def any_permissions(self, *tasks: str) -> bool:
        """
        Description:
            Checks if this mob has permission to perform any of the inputted tasks
        Input:
            *tasks: Variable number of string arguments representing tasks to check permission for
        Output:
            bool: True if this mob has permission to perform any of the inputted tasks, False otherwise
        """
        for task in tasks:
            if self.get_permission(task):
                return True
        return False

    def get_permission(self, task: str, one_time_permissions: Dict = None) -> Any:
        """
        Description:
            Returns the permission this mob has to perform the inputted task
        Input:
            string task: Task for which to check permission
        Output:
            Any: Returns the permission value for the inputted task
        """
        if one_time_permissions:
            return one_time_permissions.get(
                task,
                self.override_permissions.get(
                    task,
                    self.default_permissions.get(
                        task, constants.DEFAULT_PERMISSIONS.get(task, False)
                    ),
                ),
            )
        else:
            return self.override_permissions.get(
                task,
                self.default_permissions.get(
                    task, constants.DEFAULT_PERMISSIONS.get(task, False)
                ),
            )

    def finish_init(
        self,
        original_constructor: bool,
        from_save: bool,
        input_dict: Dict[str, any],
        create_portrait: bool = True,
    ):
        """
        Description:
            Finishes initialization of this actor, called after the original is finished
        Input:
            boolean original_constructor: Whether this is the original constructor call for this object
        Output:
            None
        """
        if original_constructor:
            if create_portrait:
                if not from_save:
                    metadata = {"body_image": self.image_dict["default"]}
                    if self.get_permission(constants.OFFICER_PERMISSION):
                        metadata.update(self.character_info)
                    self.image_dict["portrait"] = (
                        constants.character_manager.generate_unit_portrait(
                            self, metadata
                        )
                    )
                else:
                    self.image_dict["portrait"] = input_dict.get("portrait", [])
            if not from_save:
                self.reselect()
            self.set_permission(constants.INIT_COMPLETE_PERMISSION, True)
            self.update_habitability()

    def image_variants_setup(self, from_save, input_dict):
        """
        Description:
            Sets up this unit's image variants
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
        Output:
            None
        """
        self.image_variants = actor_utility.get_image_variants(
            self.image_dict["default"]
        )
        if self.image_dict["default"].endswith("default.png") and not from_save:
            if not from_save:
                self.image_variant = random.randrange(0, len(self.image_variants))
                self.image_dict["default"] = self.image_variants[self.image_variant]
        elif from_save and "image_variant" in input_dict:
            self.image_variant = input_dict["image_variant"]
            self.image_dict["default"] = self.image_variants[self.image_variant]
            if "second_image_variant" in input_dict:
                self.second_image_variant = input_dict["second_image_variant"]

    def to_save_dict(self):
        """
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                Along with superclass outputs, also saves the following values:
                'movement_points': int value - How many movement points this mob currently has
                'max_movement_points': int value - Maximum number of movement points this mob can have
                'image': string value - File path to the image used by this mob
                'creation_turn': int value - Turn number on which this mob was created
                'disorganized': boolean value - Whether this unit is currently disorganized
                'image_variant': int value - Optional variants of default image to use from same file, applied to get_image_id_list but not default image path
        """
        save_dict = super().to_save_dict()
        save_dict["init_type"] = self.unit_type.key
        save_dict["movement_points"] = self.movement_points
        save_dict["max_movement_points"] = self.max_movement_points
        save_dict["image"] = self.image_dict["default"]
        if "portrait" in self.image_dict:
            save_dict["portrait"] = self.image_dict["portrait"]
        if "left portrait" in self.image_dict:
            save_dict["left portrait"] = self.image_dict["left portrait"]
        if "right portrait" in self.image_dict:
            save_dict["right portrait"] = self.image_dict["right portrait"]
        save_dict["creation_turn"] = self.creation_turn
        save_dict["disorganized"] = self.get_permission(
            constants.DISORGANIZED_PERMISSION
        )
        save_dict["dehydration"] = self.get_permission(constants.DEHYDRATION_PERMISSION)
        save_dict["starvation"] = self.get_permission(constants.STARVATION_PERMISSION)
        if hasattr(self, "image_variant"):
            save_dict["image"] = self.image_variants[0]
            save_dict["image_variant"] = self.image_variant
            if hasattr(self, "second_image_variant"):
                save_dict["second_image_variant"] = self.second_image_variant
        return save_dict

    def insert_equipment(self, portrait: List[any]) -> List[any]:
        """
        Description:
            Returns a version of the inputted unit portrait with any equipment images inserted into the correct sections
        Input:
            list portrait: List of unit portrait sections
        Output:
            list: Returns a version of the inputted unit portrait with any equipment images inserted into the correct sections
        """
        if not portrait:  # If empty portrait, return intact
            return portrait
        copied = False
        for key, equipment_type in status.equipment_types.items():
            if self.get_permission(key):  # If equipped
                for (
                    section_key,
                    section_image_id,
                ) in equipment_type.equipment_image.items():
                    if equipment_type.can_show_portrait_section(self, section_key):
                        if (
                            not copied
                        ):  # If making any changes, copy portrait to avoid changing original
                            portrait = portrait.copy()
                            copied = True
                        portrait_index = (
                            constants.character_manager.find_portrait_section(
                                section_key, portrait
                            )
                        )
                        portrait[portrait_index] = portrait[portrait_index].copy()
                        portrait[portrait_index]["image_id"] = section_image_id
        return portrait

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
        if any(
            section in self.image_dict and len(self.image_dict[section]) > 0
            for section in ["portrait", "left portrait", "right portrait"]
        ):
            image_id_list.remove(self.image_dict["default"])
        image_id_list += self.insert_equipment(self.image_dict.get("portrait", []))
        if override_values.get(
            "disorganized", self.get_permission(constants.DISORGANIZED_PERMISSION)
        ):
            image_id_list.append("misc/disorganized_icon.png")
        if override_values.get(
            "dehydration", self.get_permission(constants.DEHYDRATION_PERMISSION)
        ):
            image_id_list.append("misc/dehydration_icon.png")
        if override_values.get(
            "starvation", self.get_permission(constants.STARVATION_PERMISSION)
        ):
            image_id_list.append("misc/starvation_icon.png")
        if not override_values.get(
            "survivable", self.get_permission(constants.SURVIVABLE_PERMISSION)
        ):
            image_id_list.append("misc/deadly_icon.png")
        return image_id_list

    def get_combat_modifier(self, opponent=None, include_tile=False):
        """
        Description:
            Calculates and returns the modifier added to this unit's combat rolls
        Input:
            None
        Output:
            int: Returns the modifier added to this unit's combat rolls
        """
        modifier = 0
        if self.get_permission(constants.PMOB_PERMISSION):
            if (
                self.get_permission(constants.GROUP_PERMISSION)
                and self.unit_type == status.unit_types[constants.BATTALION]
            ):
                modifier += 1
            else:
                modifier -= 1
                if self.get_permission(constants.OFFICER_PERMISSION):
                    modifier -= 1
            if include_tile and self.get_cell().has_intact_building(constants.FORT):
                modifier += 1
        if self.get_permission(constants.DISORGANIZED_PERMISSION):
            modifier -= 1
        return modifier

    def get_combat_strength(self):
        """
        Description:
            Calculates and returns this unit's combat strength. While combat strength has no role in combat calculations, it serves as an estimate for the player of the unit's combat capabilities
        Input:
            None
        Output:
            int: Returns this unit's combat strength
        """
        # A unit with 0 combat strength cannot fight
        # combat modifiers range from -3 (disorganized lone officer) to +2 (imperial battalion), and veteran status should increase strength by 1: range from 0 to 6
        # add 3 to modifier and add veteran bonus to get strength
        # 0: lone officer, vehicle
        # 1: disorganized workers/civilian group
        # 2: veteran lone officer, workers/civilian group
        # 3: veteran civilian group, disorganized colonial battalion
        # 4: colonial battalion, disorganized imperial battalion
        # 5: imperial battalion, veteran colonial battalion, disorganized veteran imperial battalion
        # 6: veteran imperial battalion
        base = self.get_combat_modifier()
        result = base + 3
        if self.get_permission(constants.VETERAN_PERMISSION):
            result += 1
        if self.get_permission(constants.PMOB_PERMISSION):
            for current_equipment in self.equipment:
                if "combat" in status.equipment_types[current_equipment].effects.get(
                    "positive_modifiers", []
                ):
                    result += 1
                elif "combat" in status.equipment_types[current_equipment].effects.get(
                    "negative_modifiers", []
                ):
                    result -= 1
        if self.any_permissions(
            constants.OFFICER_PERMISSION, constants.INACTIVE_VEHICLE_PERMISSION
        ):
            result = 0
        return result

    def combat_possible(self):
        """
        Description:
            Returns whether this unit can start any combats in its current cell. A pmob can start combats with npmobs in its cell, and a hostile npmob can start combats with pmobs in its cell
        Input:
            None
        Output:
            boolean: Returns whether this unit can start any combats in its current cell
        """
        if self.get_permission(constants.NPMOB_PERMISSION):
            if self.hostile:
                if not self.get_cell():
                    if (
                        self.grids[0]
                        .find_cell(self.x, self.y)
                        .has_unit([constants.PMOB_PERMISSION])
                    ):  # If hidden and in same tile as pmob
                        return True
                elif self.get_cell().has_unit(
                    [constants.PMOB_PERMISSION]
                ):  # If visible and in same tile as pmob
                    return True
        elif self.get_permission(constants.PMOB_PERMISSION):
            if self.get_cell().has_unit([constants.NPMOB_PERMISSION]):
                return True
        return False

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this unit can be shown. By default, it can be shown when it is in a discovered cell during the correct game mode and is not attached to any other units or buildings
        Input:
            None
        Output:
            boolean: Returns True if this image can appear during the current game mode, otherwise returns False
        """
        if not self.any_permissions(
            constants.IN_VEHICLE_PERMISSION,
            constants.IN_GROUP_PERMISSION,
            constants.IN_BUILDING_PERMISSION,
        ):
            if (
                self.get_cell()
                and self.get_cell().contained_mobs[0] == self
                and constants.current_game_mode in self.modes
            ):
                if self.get_location().visible:
                    return True
        return False

    def can_show_tooltip(self):
        """
        Description:
            Returns whether this unit's tooltip can be shown. Along with superclass conditions, requires that it is in a discovered cell
        Input:
            None
        Output:
            None
        """
        return (
            super().can_show_tooltip()
            and self.get_cell()
            and self.get_location().visible
        )

    def get_movement_cost(self, x_change, y_change):
        """
        Description:
            Returns the cost in movement points of moving by the inputted amounts. Only works when one inputted amount is 0 and the other is 1 or -1, with 0 and -1 representing moving 1 cell downward
        Input:
            int x_change: How many cells would be moved to the right in the hypothetical movement
            int y_change: How many cells would be moved upward in the hypothetical movement
        Output:
            double: How many movement points would be spent by moving by the inputted amount
        """
        cost = self.movement_cost
        if self.get_permission(constants.CONSTANT_MOVEMENT_COST_PERMISSION):
            return cost

        direction = None
        if x_change < 0:
            direction = "left"
        elif x_change > 0:
            direction = "right"
        elif y_change > 0:
            direction = "up"
        elif y_change < 0:
            direction = "down"

        if not direction:
            adjacent_location = self.get_location()
        else:
            adjacent_location = self.get_location().adjacent_locations[direction]

        if adjacent_location:
            cost *= constants.terrain_movement_cost_dict.get(
                adjacent_location.terrain, 1
            )
            if self.get_permission(constants.PMOB_PERMISSION):
                local_infrastructure = self.get_location().get_intact_building(
                    constants.INFRASTRUCTURE
                )
                adjacent_infrastructure = self.get_location().get_intact_building(
                    constants.INFRASTRUCTURE
                )
                if local_infrastructure and adjacent_infrastructure:
                    # If both have infrastructure and connected by land or bridge, use discount
                    cost = cost / 2
                # Otherwise, use default cost but not full cost (no canoe penantly)
                if (
                    adjacent_infrastructure
                    and adjacent_infrastructure.infrastructure_type == constants.FERRY
                ):
                    cost = 2
                if (not adjacent_location.visible) and self.get_permission(
                    constants.EXPEDITION_PERMISSION
                ):
                    cost = self.movement_cost
        return cost

    def adjacent_to_water(self):
        """
        Description:
            Returns whether any of the cells directly adjacent to this mob's cell has the water terrain. Otherwise, returns False
        Input:
            None
        Output:
            boolean: Returns True if any of the cells directly adjacent to this mob's cell has the water terrain. Otherwise, returns False
        """
        for current_location in self.get_location().adjacent_list:
            if current_location.terrain == "water" and current_location.visible:
                return True
        return False

    def change_movement_points(self, change):
        """
        Description:
            Changes this mob's movement points by the inputted amount. Ensures that the mob info display is updated correctly and that whole number movement point amounts are not shown as decimals
        Input:
            None
        Output:
            None
        """
        if not self.get_permission(constants.INFINITE_MOVEMENT_PERMISSION):
            self.movement_points += change
            if self.movement_points == round(
                self.movement_points
            ):  # if whole number, don't show decimal
                self.movement_points = round(self.movement_points)
            if (
                self.get_permission(constants.PMOB_PERMISSION)
                and self.movement_points <= 0
            ):
                self.remove_from_turn_queue()
            if (
                status.displayed_mob == self
            ):  # update mob info display to show new movement points
                actor_utility.calibrate_actor_info_display(
                    status.mob_info_display, self
                )

    def set_movement_points(self, new_value):
        """
        Description:
            Sets this mob's movement points to the inputted amount. Ensures that the mob info display is updated correctly and that whole number movement point amounts are not shown as decimals
        Input:
            None
        Output:
            None
        """
        if new_value < 0:
            new_value = 0
        self.movement_points = new_value
        if self.movement_points == round(
            self.movement_points
        ):  # if whole number, don't show decimal
            self.movement_points = round(self.movement_points)
        if self.get_permission(constants.PMOB_PERMISSION) and self.movement_points <= 0:
            self.remove_from_turn_queue()
        if status.displayed_mob == self:
            actor_utility.calibrate_actor_info_display(status.mob_info_display, self)

    def reset_movement_points(self):
        """
        Description:
            Sets this mob's movement points to its maximum number of movement points at the end of the turn. Ensures that the mob info display is updated correctly and that whole number movement point amounts are not shown as decimals
        Input:
            None
        Output:
            None
        """
        if self.get_permission(constants.MOVEMENT_DISABLED_PERMISSION):
            self.set_permission(
                constants.MOVEMENT_DISABLED_PERMISSION, False, override=True
            )
            self.movement_points = 0
        else:
            self.movement_points = self.max_movement_points
            if self.movement_points == round(
                self.movement_points
            ):  # if whole number, don't show decimal
                self.movement_points = round(self.movement_points)
            if self.get_permission(
                constants.PMOB_PERMISSION
            ) and not self.any_permissions(
                constants.INACTIVE_VEHICLE_PERMISSION,
                constants.IN_VEHICLE_PERMISSION,
                constants.IN_BUILDING_PERMISSION,
                constants.IN_GROUP_PERMISSION,
            ):
                self.add_to_turn_queue()
            if status.displayed_mob == self:
                actor_utility.calibrate_actor_info_display(
                    status.mob_info_display, self
                )

    def set_max_movement_points(
        self, new_value, initial_setup=True, allow_increase=True
    ):
        """
        Description:
            Sets this mob's maximum number of movement points and changes its current movement points by the amount increased or to the maximum, based on the input boolean
        Input:
            boolean initial_setup: Whether to set this current movement points to the max (on recruitment) or change by the amount increased (when increased after recruitment)
        Output:
            None
        """
        increase = 0
        if allow_increase and not initial_setup:
            increase = new_value - self.max_movement_points
        if (
            increase + self.movement_points > new_value
        ):  # If current movement points is above max, set current movement points to max
            increase = new_value - self.movement_points
        self.max_movement_points = new_value
        if initial_setup:
            self.set_movement_points(new_value)
        else:
            self.set_movement_points(self.movement_points + increase)

    def go_to_grid(self, new_grid, new_coordinates):
        """
        Description:
            Links this mob to a grid, causing it to appear on that grid and its minigrid at certain coordinates. Used when crossing the ocean and when a mob that was previously attached to another actor becomes independent and visible,
                like when a building's worker leaves. Also moves this unit's status icons as necessary
        Input:
            grid new_grid: grid that this mob is linked to
            int tuple new_coordinates: Two values representing x and y coordinates to start at on the inputted grid
        Output:
            None
        """
        if new_grid == status.earth_grid:
            self.modes.append(constants.EARTH_MODE)
        else:  # If mob was spawned on Earth, make it so that it does not appear in the Earth screen after leaving
            self.modes = utility.remove_from_list(self.modes, constants.EARTH_MODE)
        self.x, self.y = new_coordinates
        old_image_id = self.images[0].image_id
        for current_image in self.images:
            current_image.remove_from_cell()
        self.location = new_grid.world_handler.find_location(
            new_coordinates[0], new_coordinates[1]
        )
        self.update_attached_grids()

        self.images = []
        for current_grid in self.grids:
            self.images.append(
                images.mob_image(
                    self,
                    current_grid.get_cell_width(),
                    current_grid.get_cell_height(),
                    current_grid,
                    old_image_id,
                )
            )
            self.images[-1].add_to_cell()
        self.on_move()

    def reselect(self):
        """
        Description:
            Deselects and reselects this mob if it was already selected
        Input:
            None
        Output:
            None
        """
        if status.displayed_mob == self:
            self.locked_ambient_sound = True
            actor_utility.calibrate_actor_info_display(
                status.mob_info_display, None, override_exempt=True
            )
            self.select()
            self.locked_ambient_sound = False

    def select(self):
        """
        Description:
            Selects this mob, causing this mob to be shown in the mob display and causing a selection outline to appear around it
        Input:
            None
        Output:
            None
        """
        self.move_to_front()
        flags.show_selection_outlines = True
        constants.last_selection_outline_switch = constants.current_time
        actor_utility.calibrate_actor_info_display(
            status.location_info_display, self.get_cell().tile
        )
        actor_utility.calibrate_actor_info_display(status.mob_info_display, self)
        for grid in self.grids:
            grid.calibrate(self.x, self.y)

    def cycle_select(self):
        """
        Description:
            Selects this mob while also moving it to the front of the tile and playing its selection sound - should be used when unit is clicked on
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            if status.displayed_mob != self:
                self.select()
                if self.get_permission(constants.PMOB_PERMISSION):
                    self.selection_sound()
                for (
                    current_image
                ) in self.images:  # move mob to front of each stack it is in
                    if current_image.current_cell:
                        while not self == current_image.current_cell.contained_mobs[0]:
                            current_image.current_cell.contained_mobs.append(
                                current_image.current_cell.contained_mobs.pop(0)
                            )
        else:
            text_utility.print_to_screen(
                "You are busy and cannot select a different unit"
            )

    def move_to_front(self):
        """
        Description:
            Moves the image of this unit to the front of the cell, making it visible and selected first when the cell is clicked
        Input:
            None
        Output:
            None
        """
        for current_image in self.images:
            current_cell = self.get_cell()
            if self in current_cell.contained_mobs:
                while (
                    not current_cell.contained_mobs[0] == self
                ):  # Move to front of tile
                    current_cell.contained_mobs.append(
                        current_cell.contained_mobs.pop(0)
                    )

    def draw_outline(self):
        """
        Description:
            Draws a flashing outline around this mob if it is selected
        Input:
            None
        Output:
            None
        """
        if flags.show_selection_outlines:
            for current_image in self.images:
                if (
                    current_image.current_cell
                    and self == current_image.current_cell.contained_mobs[0]
                    and current_image.current_cell.grid.showing
                ):  # only draw outline if on top of stack
                    pygame.draw.rect(
                        constants.game_display,
                        constants.color_dict[self.selection_outline_color],
                        (current_image.outline),
                        current_image.outline_width,
                    )

    def update_image_bundle(self):
        """
        Description:
            Updates this actor's images with its current image id list
        Input:
            None
        Output:
            None
        """
        previous_image = self.previous_image
        super().update_image_bundle()
        if self.previous_image != previous_image:
            self.reselect()

    def update_tooltip(self):
        """
        Description:
            Sets this mob's tooltip to what it should be whenever the player mouses over one of its images
        Input:
            None
        Output:
            None
        """
        tooltip_list = []

        tooltip_list.append(
            "Unit type: " + self.name[:1].capitalize() + self.name[1:]
        )  # Capitalizes first letter while keeping rest the same
        if self.get_permission(constants.OFFICER_PERMISSION):
            tooltip_list.append("Name: " + self.character_info["name"])
        if self.get_permission(constants.PMOB_PERMISSION):
            if self.get_permission(constants.GROUP_PERMISSION):
                tooltip_list.append("    Officer: " + self.officer.name.capitalize())
                tooltip_list.append(
                    "        Name: " + self.officer.character_info["name"]
                )
                tooltip_list.append("    Workers: " + self.worker.name.capitalize())
            elif self.get_permission(constants.VEHICLE_PERMISSION):
                if self.get_permission(constants.ACTIVE_PERMISSION):
                    tooltip_list.append("    Crew: " + self.crew.name.capitalize())
                else:
                    tooltip_list.append("    Crew: None")
                    tooltip_list.append(
                        f"    A {self.name} cannot move or take passengers or cargo without crew"
                    )

                if len(self.contained_mobs) > 0:
                    tooltip_list.append("    Passengers: ")
                    for current_mob in self.contained_mobs:
                        tooltip_list.append("        " + current_mob.name.capitalize())
                else:
                    tooltip_list.append("    Passengers: None")

            if self.get_permission(
                constants.ACTIVE_PERMISSION
            ) and not self.get_permission(constants.INFINITE_MOVEMENT_PERMISSION):
                tooltip_list.append(
                    f"Movement points: {self.movement_points}/{self.max_movement_points}"
                )
            elif self.get_permission(
                constants.MOVEMENT_DISABLED_PERMISSION
            ) or not self.get_permission(constants.ACTIVE_PERMISSION):
                tooltip_list.append("No movement")
            else:
                tooltip_list.append("Movement points: Infinite")

        else:
            tooltip_list.append("Movement points: ???")

        if self.get_permission(constants.PMOB_PERMISSION):
            held_items: List[item_types.item_type] = self.get_held_items()
            if held_items or self.inventory_capacity > 0:
                tooltip_list.append(
                    f"Inventory: {self.get_inventory_used()}/{self.inventory_capacity}"
                )
                for item_type in held_items:
                    tooltip_list.append(
                        f"    {item_type.name.capitalize()}: {self.get_inventory(item_type)}"
                    )
            if len(self.base_automatic_route) > 1:
                start_coordinates = self.base_automatic_route[0]
                end_coordinates = self.base_automatic_route[-1]
                tooltip_list.append(
                    f"This unit has a designated movement route of length {len(self.base_automatic_route)}, picking up items at ({start_coordinates[0]}, {start_coordinates[1]}) and dropping them off at ({end_coordinates[0]}, {end_coordinates[1]})"
                )

            if self.equipment:
                tooltip_list.append(f"Equipment: {', '.join(self.equipment.keys())}")

            item_upkeep = self.get_item_upkeep(recurse=True, earth_exemption=False)
            show_air_exemption = False
            top_message = "Item upkeep per turn:"
            if not item_upkeep:
                top_message += " None"
            elif self.get_cell() and self.get_cell().grid == status.earth_grid:
                top_message += " (exempt while on Earth)"
            elif (
                self.get_cell()
                and self.get_location().get_unit_habitability()
                > constants.HABITABILITY_DEADLY
            ):
                show_air_exemption = True
            tooltip_list.append(top_message)

            for item_type_key, amount_required in item_upkeep.items():
                if amount_required == 0:
                    message = f"    Requires access to {status.item_types[item_type_key].name}"
                else:
                    message = f"    Requires {amount_required} {status.item_types[item_type_key].name}"
                if show_air_exemption and item_type_key == constants.AIR_ITEM:
                    message += f" (exempt while in non-deadly atmosphere)"
                tooltip_list.append(message)

        if not self.get_permission(constants.SURVIVABLE_PERMISSION):
            tooltip_list.append(
                "This unit is in deadly environmental conditions and will die if remaining there at the end of the turn"
            )
        if self.get_permission(constants.DISORGANIZED_PERMISSION):
            tooltip_list.append(
                "This unit is currently disorganized, giving a combat penalty until its next turn"
            )
        if self.get_permission(constants.DEHYDRATION_PERMISSION):
            tooltip_list.append(
                "This unit is dehydrated and will die if not provided sufficient water upkeep this turn"
            )
        if self.get_permission(constants.STARVATION_PERMISSION):
            tooltip_list.append(
                "This unit is starving and will die if not provided sufficient food upkeep this turn"
            )

        if self.end_turn_destination:
            if not self.end_turn_destination.get_world_handler().is_abstract_world:
                tooltip_list.append(
                    f"This unit has been issued an order to travel to ({self.end_turn_destination.x}, {self.end_turn_destination.y}) on {self.end_turn_destination.get_world_handler().name} at the end of the turn"
                )
            else:
                tooltip_list.append(
                    f"This unit has been issued an order to travel to {self.end_turn_destination.get_world_handler().name} at the end of the turn"
                )

        if self.get_permission(constants.NPMOB_PERMISSION):
            if self.hostile:
                tooltip_list.append("Attitude: Hostile")
            else:
                tooltip_list.append("Attitude: Neutral")
            tooltip_list.append("You do not control this unit")
        elif self.get_permission(constants.PMOB_PERMISSION) and self.sentry_mode:
            tooltip_list.append("This unit is in sentry mode")

        self.set_tooltip(tooltip_list)

    def drop_inventory(self):
        """
        Description:
            Drops each item held in this actor's inventory into its current tile
        Input:
            None
        Output:
            None
        """
        for current_item in self.get_held_items():
            self.get_cell().tile.change_inventory(
                current_item, self.get_inventory(current_item)
            )
            self.set_inventory(current_item, 0)
        if self.actor_type == constants.MOB_ACTOR_TYPE and self.get_permission(
            constants.PMOB_PERMISSION
        ):
            for current_equipment in self.equipment.copy():
                if self.equipment[current_equipment]:
                    self.get_cell().tile.change_inventory(
                        status.equipment_types[current_equipment], 1
                    )
                    status.equipment_types[current_equipment].unequip(self)
            self.equipment = {}

    def remove(self):
        """
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. Also deselects this mob
        Input:
            None
        Output:
            None
        """
        if status.displayed_mob == self:
            actor_utility.calibrate_actor_info_display(
                status.mob_info_display, None, override_exempt=True
            )
        for current_image in self.images:
            current_image.remove_from_cell()
        super().remove()
        status.mob_list = utility.remove_from_list(status.mob_list, self)
        for current_status_icon in self.status_icons:
            current_status_icon.remove_complete()
        self.status_icons = []
        self.unit_type.on_remove()

    def die(self, death_type="violent"):
        """
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. Used instead of remove to improve consistency with groups/vehicles, whose die and remove have different
                functionalities
        Input:
            string death_type == 'violent': Type of death for this unit, determining the type of sound played
        Output:
            None
        """
        if self.get_permission(constants.PMOB_PERMISSION):
            self.death_sound(death_type)
        self.drop_inventory()
        self.remove_complete()

    def death_sound(self, death_type: str = "violent"):
        """
        Description:
            Makes a sound when this unit dies, depending on the type of death
        Input:
        string death_type == 'violent': Type of death for this unit, determining the type of sound played
        Output:
            None
        """
        possible_sounds: List[str] = []
        if death_type == "fired":
            possible_sounds = []
        elif death_type == "quit":
            possible_sounds = ["quit 1", "quit 2", "quit 3"]
        elif death_type == "violent":
            possible_sounds = [
                "dead 1",
                "dead 2",
                "dead 3",
                "dead 4",
                "dead 5",
                "dead 6",
                "dead 7",
                "dead 8",
                "dead 9",
            ]
        if len(possible_sounds) > 0:
            constants.sound_manager.play_sound(
                "voices/" + random.choice(possible_sounds),
                0.5,
                radio_effect=self.get_radio_effect(),
            )

    def can_move(self, x_change: int, y_change: int, can_print: bool = False):
        """
        Description:
            Returns whether this mob can move to the tile x_change to the right of it and y_change above it. Movement can be prevented by not being able to move on water/land, the edge of the map, limited movement points, etc.
        Input:
            int x_change: How many cells would be moved to the right in the hypothetical movement
            int y_change: How many cells would be moved upward in the hypothetical movement
        Output:
            boolean: Returns True if this mob can move to the proposed destination, otherwise returns False
        """
        future_x = (self.x + x_change) % self.grid.coordinate_width
        future_y = (self.y + y_change) % self.grid.coordinate_height
        if minister_utility.get_minister(constants.TRANSPORTATION_MINISTER):
            if not self.get_location().get_world_handler().is_abstract_world:
                future_location = (
                    self.get_location()
                    .get_world_handler()
                    .find_location(future_x, future_y)
                )
                if (
                    future_location.get_unit_habitability(self)
                    == constants.HABITABILITY_DEADLY
                ):
                    if can_print:
                        constants.notification_manager.display_notification(
                            {
                                "message": "This unit cannot move into a tile with deadly environmental conditions without spacesuits. /n /n",
                            }
                        )
                    return False

                if self.unit_type.required_infrastructure:
                    if not (
                        self.get_cell().has_intact_building(
                            self.unit_type.required_infrastructure.key
                        )
                        and self.grids[0]
                        .find_cell(self.x + x_change, self.y + y_change)
                        .has_intact_building(self.unit_type.required_infrastructure.key)
                    ):
                        if can_print:
                            text_utility.print_to_screen(
                                f"{self.unit_type.name}s can only move along {self.unit_type.required_infrastructure.name}s."
                            )
                        return False

                if future_location.visible or self.any_permissions(
                    constants.EXPEDITION_PERMISSION, constants.NPMOB_PERMISSION
                ):
                    if (
                        self.movement_points
                        >= self.get_movement_cost(x_change, y_change)
                        or self.get_permission(constants.INFINITE_MOVEMENT_PERMISSION)
                        and self.movement_points > 0
                    ):
                        return True
                    elif can_print:
                        text_utility.print_to_screen(
                            "You do not have enough movement points to move."
                        )
                        text_utility.print_to_screen(
                            f"You have {self.movement_points} movement points, while {self.get_movement_cost(x_change, y_change)} are required."
                        )
                elif can_print:
                    text_utility.print_to_screen(
                        "You cannot move to an unexplored tile."
                    )
            elif can_print:
                text_utility.print_to_screen("You cannot move while in this area.")
        elif can_print:
            text_utility.print_to_screen(
                "You cannot move units before a Minister of Transportation has been appointed."
            )
        return False

    def selection_sound(self) -> pygame.mixer.Channel:
        """
        Description:
            Plays a sound when this unit is selected, with a varying sound based on this unit's type
        Input:
            None
        Output:
            pygame.mixer.Channel: Returns the channel that the sound was played on, if any
        """
        channel = None
        if self.all_permissions(
            constants.PMOB_PERMISSION, constants.VEHICLE_PERMISSION
        ):
            if self.get_permission(constants.ACTIVE_PERMISSION):
                if self.get_permission(constants.TRAIN_PERMISSION):
                    channel = constants.sound_manager.play_sound("effects/train_horn")
        officer = None
        if self.get_permission(constants.OFFICER_PERMISSION):
            officer = self
        elif self.get_permission(constants.GROUP_PERMISSION):
            officer = self.officer
        elif self.get_permission(constants.ACTIVE_VEHICLE_PERMISSION):
            officer = self.crew.officer
        if officer:
            channel = constants.sound_manager.play_sound(
                utility.get_voice_line(officer, "acknowledgement"),
                radio_effect=self.get_radio_effect(),
            )
        return channel

    def travel_sound(self):
        """
        Description:
            Plays a sound when this unit starts traveling between grids, with a varying sound based on this unit's type
        Input:
            None
        Output:
            None
        """
        if self.get_permission(constants.SPACESHIP_PERMISSION):
            channel = self.selection_sound()
            constants.sound_manager.queue_sound(
                "effects/spaceship_launch", channel, volume=1.0
            )  # Play spaceship launch after radio acknowledgement
        else:
            constants.sound_manager.play_sound("effects/ocean_splashing")
            constants.sound_manager.play_sound("effects/ship_propeller")

    def movement_sound(self):
        """
        Description:
            Plays a sound when this unit moves or embarks/disembarks a vehicle, with a varying sound based on this unit's type
        Input:
            None
        Output:
            None
        """
        possible_sounds = []
        if self.get_permission(constants.PMOB_PERMISSION) or self.visible():
            if self.get_permission(constants.VEHICLE_PERMISSION):
                if self.get_permission(constants.TRAIN_PERMISSION):
                    possible_sounds.append("effects/train_moving")
                elif self.get_permission(constants.SPACESHIP_PERMISSION):
                    possible_sounds.append("effects/spaceship_moving")
                else:
                    constants.sound_manager.play_sound("effects/ocean_splashing")
                    possible_sounds.append("effects/ship_propeller")
            else:
                if self.get_cell() and self.get_location().terrain == "water":
                    local_infrastructure = self.get_location().get_intact_building(
                        constants.INFRASTRUCTURE
                    )
                    if (
                        local_infrastructure
                        and local_infrastructure.is_bridge
                        and (
                            local_infrastructure.is_road
                            or local_infrastructure.is_railroad
                        )
                        and not self.get_permission(constants.SWIM_PERMISSION)
                    ):  # If walking on bridge
                        possible_sounds.append("effects/footsteps")
                    else:
                        possible_sounds.append("effects/river_splashing")
                else:
                    possible_sounds.append("effects/footsteps")
                self.selection_sound()
        if possible_sounds:
            constants.sound_manager.play_sound(random.choice(possible_sounds))

    def move(self, x_change, y_change):
        """
        Description:
            Moves this mob x_change to the right and y_change upward
        Input:
            int x_change: How many cells are moved to the right in the movement
            int y_change: How many cells are moved upward in the movement
        Output:
            None
        """
        if self.get_permission(constants.PMOB_PERMISSION) and self.sentry_mode:
            self.set_sentry_mode(False)
        self.end_turn_destination = None  # Cancels planned movements
        status.displayed_mob.set_permission(constants.TRAVELING_PERMISSION, False)
        self.change_movement_points(-1 * self.get_movement_cost(x_change, y_change))
        if self.get_permission(constants.PMOB_PERMISSION):
            previous_cell = self.get_cell()
        for current_image in self.images:
            current_image.remove_from_cell()
        self.x = (self.x + x_change) % self.grid.coordinate_width
        self.y = (self.y + y_change) % self.grid.coordinate_height
        status.minimap_grid.calibrate(self.x, self.y)
        for current_image in self.images:
            current_image.add_to_cell()

        self.movement_sound()

        actor_utility.calibrate_actor_info_display(status.mob_info_display, self)

        if self.get_permission(
            constants.PMOB_PERMISSION
        ):  # Do an inventory attrition check when moving, using the destination's terrain
            self.manage_inventory_attrition()

        self.last_move_direction = (x_change, y_change)
        self.on_move()

    def retreat(self):
        """
        Description:
            Causes a free movement to the last cell this unit moved from, following a failed attack
        Input:
            None
        Output:
            None
        """
        original_movement_points = self.movement_points
        self.move(-1 * self.last_move_direction[0], -1 * self.last_move_direction[1])

        self.set_movement_points(original_movement_points)  # retreating is free

    def touching_mouse(self):
        """
        Description:
            Returns whether any of this mob's images is colliding with the mouse. Also ensures that no hidden images outside of the minimap are considered as colliding
        Input:
            None
        Output:
            boolean: True if any of this mob's images is colliding with the mouse, otherwise return False
        """
        for current_image in self.images:
            if current_image.Rect.collidepoint(
                pygame.mouse.get_pos()
            ):  # if mouse is in image
                if not (
                    current_image.grid == status.minimap_grid
                    and not current_image.grid.is_on_mini_grid(self.x, self.y)
                ):  # do not consider as touching mouse if off-map
                    return True
        return False

    def set_name(self, new_name):
        """
        Description:
            Sets this mob's name. Also updates the mob info display to show the new name
        Input:
            string new_name: Name to set this mob's name to
        Output:
            None
        """
        super().set_name(new_name)
        if status.displayed_mob == self:
            actor_utility.calibrate_actor_info_display(status.mob_info_display, self)

    def hide_images(self):
        """
        Description:
            Hides this mob's images, allowing it to be hidden but still stored at certain coordinates when it is attached to another actor or otherwise not visible
        Input:
            None
        Output:
            None
        """
        if status.displayed_mob == self:
            actor_utility.calibrate_actor_info_display(status.mob_info_display, None)
        for current_image in self.images:
            current_image.remove_from_cell()

    def show_images(self):
        """
        Description:
            Shows this mob's images at its stored coordinates, allowing it to be visible after being attached to another actor or otherwise not visible
        Input:
            None
        Output:
            None
        """
        for current_image in self.images:
            current_image.add_to_cell()

    def start_ambient_sound(self):
        """
        Description:
            Starts the ambient sound for this unit, continuing looping sound until invalid or the unit is deselected
        Input:
            None
        Output:
            None
        """
        if self == status.displayed_mob and not self.locked_ambient_sound:
            if self.all_permissions(
                constants.SPACESHIP_PERMISSION, constants.ACTIVE_VEHICLE_PERMISSION
            ):
                if self.get_permission(constants.TRAVELING_PERMISSION):
                    sound = "effects/spaceship_engine"
                    volume = 0.8
                else:
                    sound = "effects/spaceship_idling"
                    volume = 0.3
                if self.ambient_sound_channel:
                    constants.sound_manager.stop_looping_sound(
                        self.ambient_sound_channel
                    )
                self.ambient_sound_channel = (
                    constants.sound_manager.start_looping_sound(sound, volume=volume)
                )
            else:
                self.stop_ambient_sound()

    def stop_ambient_sound(self):
        """
        Description:
            Stops any ambient sound for this unit when the sound is invalid or the unit is deselected
        Input:
            None
        Output:
            None
        """
        if self.ambient_sound_channel and not self.locked_ambient_sound:
            constants.sound_manager.stop_looping_sound(self.ambient_sound_channel)
            self.ambient_sound_channel = None
