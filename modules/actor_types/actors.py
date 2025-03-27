# Contains functionality for actors

import pygame
import random
import math
from modules.util import (
    text_utility,
    utility,
    actor_utility,
    scaling,
    market_utility,
    minister_utility,
)
from modules.constructs import item_types
from modules.interface_types.grids import grid
from modules.constants import constants, status, flags
from typing import Dict, List, Tuple


class actor:
    """
    Object that can exist within certain coordinates on one or more grids and can optionally be able to hold an inventory of items
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
                'modes': string list value - Game modes during which this actor's images can appear
                'inventory': dictionary value - This actor's initial items carried, with an integer value corresponding to amount of each item type
        Output:
            None
        """
        self.previous_image = None
        self.from_save = from_save
        status.actor_list.append(self)
        self.modes = input_dict["modes"]
        self.x, self.y = input_dict["coordinates"]
        if self.from_save:
            self.grid: grid = getattr(status, input_dict["grid_type"])
            self.grids: List[grid] = [self.grid] + self.grid.mini_grids
        else:
            self.grid: grid = input_dict["grids"][0]
            self.grids: List[grid] = input_dict["grids"]
        self.set_name(input_dict.get("name", "placeholder"))
        self.set_coordinates(self.x, self.y)

        self.tooltip_text = []

        self.infinite_inventory_capacity = False
        self.inventory_capacity = 0
        self.inventory: Dict[str, int] = input_dict.get("inventory", {})
        self.finish_init(original_constructor, from_save, input_dict)

    def finish_init(
        self, original_constructor: bool, from_save: bool, input_dict: Dict[str, any]
    ):
        """
        Description:
            Finishes initialization of this actor, called after the original is finished
                Helps with calling functions that are for setup but require that most initialization is complete before they are called
        Input:
            boolean original_constructor: Whether this is the original constructor call for this object
        Output:
            None
        """
        if original_constructor:
            self.update_image_bundle()
            self.update_tooltip()

    def to_save_dict(self):
        """
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                'init_type': string value - Represents the type of actor this is, used to initialize the correct type of object on loading
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'modes': string list value - Game modes during which this actor's images can appear
                'grid_type': string value - String matching the status key of this actor's primary grid, allowing loaded object to start in that grid
                'name': string value - This actor's name
                'inventory': dictionary value - This actor's items carried, with an integer value corresponding to amount of each item type
        """
        save_dict = {}
        init_type = ""
        if self.actor_type == constants.MOB_ACTOR_TYPE:
            init_type = self.unit_type.key
        elif self.actor_type == constants.TILE_ACTOR_TYPE:
            init_type = "tile"
        elif self.actor_type == constants.BUILDING_ACTOR_TYPE:
            init_type = self.building_type.key
        save_dict["init_type"] = init_type
        save_dict["coordinates"] = (self.x, self.y)
        save_dict["modes"] = self.modes
        for grid_type in constants.grid_types_list:
            if getattr(status, grid_type) == self.grid:
                save_dict["grid_type"] = grid_type
        save_dict["name"] = self.name
        save_dict["inventory"] = self.inventory
        return save_dict

    def set_image(self, new_image):
        """
        Description:
            Changes this actor's images to reflect the inputted image file path
        Input:
            string/image new_image: Image file path to change this actor's images to, or an image to copy
        Output:
            None
        """
        if new_image != self.previous_image:
            self.previous_image = new_image
        else:
            return
        for current_image in self.images:
            if current_image.change_with_other_images:
                current_image.set_image(new_image)
        if self.actor_type == constants.MOB_ACTOR_TYPE:
            if status.displayed_mob == self:
                actor_utility.calibrate_actor_info_display(
                    status.mob_info_display, self
                )
        elif self.actor_type == constants.TILE_ACTOR_TYPE:
            if status.displayed_tile == self:
                actor_utility.calibrate_actor_info_display(
                    status.tile_info_display, self
                )

    def consume_items(self, items: Dict[str, float]) -> Dict[str, float]:
        """
        Description:
            Attempts to consume the inputted items from the inventories of actors in this unit's tile
                First checks the tile's warehouses, followed by this unit's inventory, followed by other present units' inventories
        Input:
            dictionary items: Dictionary of item type keys and quantities to consume
        Output:
            dictionary: Returns a dictionary of item type keys and quantities that were not available to be consumed
        """
        missing_consumption = {}
        for item_key, consumption_remaining in items.items():
            item_type = status.item_types[item_key]
            for present_actor in [self.get_cell().tile, self] + [
                current_mob
                for current_mob in self.get_cell().contained_mobs
                if current_mob != self
            ]:
                if consumption_remaining <= 0:
                    break
                availability = present_actor.get_inventory(item_type)
                consumption = min(consumption_remaining, availability)
                present_actor.change_inventory(item_type, -consumption)
                consumption_remaining -= consumption
                consumption_remaining = round(consumption_remaining, 2)
            if consumption_remaining > 0:
                missing_consumption[item_key] = consumption_remaining
        return missing_consumption

    def item_present(self, item_type: item_types.item_type) -> bool:
        """
        Description:
            Returns whether the inputted item type is present anywhere in this unit's tile
        Input:
            item_type item_type: Item type to check for
        Output:
            bool: Returns whether the inputted item type is present anywhere in this unit's tile
        """
        if item_type == status.item_types[constants.ENERGY_ITEM]:
            return self.item_present(status.item_types[constants.FUEL_ITEM])

        for present_actor in [self.get_cell().tile, self] + [
            current_mob
            for current_mob in self.get_cell().contained_mobs
            if current_mob != self
        ]:
            if present_actor.get_inventory(item_type) > 0:
                return True
        return False

    def get_inventory_remaining(self, possible_amount_added=0) -> float:
        """
        Description:
            By default, returns amount of inventory space remaining. If input received, returns amount of space remaining in inventory if the inputted number of items were added to it.
        Input:
            int possible_amount_added = 0: Amount to add to the current inventory size, allowing inventory remaining after adding a certain number of items to be found
        Output:
            int: Amount of space remaining in inventory after possible_amount_added is added
        """
        if self.infinite_inventory_capacity:
            return 100
        else:
            return (
                self.inventory_capacity
                - self.get_inventory_used()
                - possible_amount_added
            )

    def get_inventory_used(self) -> float:
        """
        Description:
            Returns the number of items held by this actor
        Input:
            None
        Output:
            int: Number of items held by this actor
        """
        return sum(
            [
                math.ceil(self.get_inventory(item_type))
                for item_type in self.get_held_items()
            ]
        )

    def get_inventory(self, item: item_types.item_type) -> float:
        """
        Description:
            Returns the number of items of the inputted type held by this actor
        Input:
            item_type item: Type of item to check inventory for
        Output:
            float: Number of items of the inputted type held by this actor
        """
        return self.inventory.get(item.key, 0)

    def check_inventory(self, index: int) -> item_types.item_type:
        """
        Description:
            Returns the type of item at the inputted index of this actor's inventory, for display purposes
            Results in access time of O(# inventory types held), rather than O(1) that would be allowed by maintaining an inventory array. For ease of development, it
                has been determined that slightly slower inventory access is desirable over just having an inventory array (making it harder to count number of items in
                a category) or the possible bugs that could be introduced by trying to maintain both
        Input:
            int index: Index of inventory to check
        Output:
            item_type: Returns the item type held at the inputted index of the inventory, or None if no inventory held at that index
        """
        current_index: int = 0
        for item_type in self.get_held_items():
            current_index += math.ceil(self.get_inventory(item_type))
            if current_index > index:
                return item_type
        return None

    def change_inventory(self, item: item_types.item_type, change: int) -> None:
        """
        Description:
            Changes the number of items of a certain type held by this actor
        Input:
            item_type item: Type of item to change the inventory of
            int change: Amount of items of the inputted type to add. Removes items of the inputted type if negative
        Output:
            None
        """
        self.set_inventory(item, self.inventory.get(item.key, 0) + change)

    def set_inventory(self, item: item_types.item_type, new_value: float) -> None:
        """
        Description:
            Sets the number of items of a certain type held by this actor
        Input:
            item_type item: Type of item to set the inventory of
            int new_value: Numerical amount of items of the inputted type to set inventory to
        Output:
            None
        """
        self.inventory[item.key] = round(new_value, 2)
        if round(new_value) == self.inventory[item.key]:
            self.inventory[item.key] = round(
                new_value
            )  # If new value is an integer, set inventory to integer
        if round(new_value, 2) <= 0:
            del self.inventory[item.key]

    def get_held_items(self, ignore_consumer_goods=False) -> List[item_types.item_type]:
        """
        Description:
            Returns a list of the item types held by this actor
        Input:
            boolean ignore_consumer_goods = False: Whether to include consumer goods from tile
        Output:
            item_type list: Types of item types held by this actor
        """
        return list(
            [
                status.item_types[item_key]
                for item_key in self.inventory.keys()
                if not (
                    ignore_consumer_goods and item_key == constants.CONSUMER_GOODS_ITEM
                )
            ]
        )

    def manage_inventory_attrition(self):
        """
        Description:
            Checks this actor for inventory attrition each turn or when it moves while holding items
        Input:
            None
        Output:
            None
        """
        if (
            constants.effect_manager.effect_active("boost_attrition")
            and random.randrange(1, 7) >= 4
        ):
            self.trigger_inventory_attrition()
            return

        if self.get_inventory_used() > 0:
            if random.randrange(1, 7) <= 2 or (
                self.actor_type == constants.MOB_ACTOR_TYPE
                and (not self.get_permission(constants.VEHICLE_PERMISSION))
                and random.randrange(1, 7) <= 1
            ):  # Extra chance of failure when carried by non-vehicle
                transportation_minister = minister_utility.get_minister(
                    constants.TRANSPORTATION_MINISTER
                )
                if (
                    random.randrange(1, 7) <= 2
                    and transportation_minister.check_corruption()
                ):  # 1/18 chance of corruption check to take items - 1/36 chance for most corrupt to steal
                    self.trigger_inventory_attrition(stealing=True)
                    return
                elif (
                    self.get_cell().local_attrition("inventory")
                    and transportation_minister.no_corruption_roll(6) < 4
                ):  # 1/6 chance of doing tile conditions check, if passes minister needs to make a 4+ roll to avoid attrition
                    self.trigger_inventory_attrition()
                    return

            # This part of function only reached if no inventory attrition was triggered
            if (
                self.actor_type == constants.MOB_ACTOR_TYPE
                and self.all_permissions(
                    constants.PMOB_PERMISSION, constants.GROUP_PERMISSION
                )
                and self.unit_type == status.unit_types[constants.PORTERS]
                and (not self.get_permission(constants.VETERAN_PERMISSION))
                and random.randrange(1, 7) == 6
                and random.randrange(1, 7) == 6
            ):  # 1/36 chance of porters promoting on successful inventory attrition roll
                self.promote()
                constants.notification_manager.display_notification(
                    {
                        "message": "By avoiding losses and damage to the carried items, the porters' driver is now a veteran and will have more movement points each turn.",
                    }
                )

    def trigger_inventory_attrition(
        self, stealing=False
    ):  # later add input to see if corruption or real attrition to change how much minister has stolen
        """
        Description:
            Removes up to half of this unit's stored items when inventory attrition occurs. The inventory attrition may result from poor terrain/storage conditions or from the transportation minister stealing commodites. Also
                displays a zoom notification describing what was lost
        Input:
            boolean stealing = False: Whether the transportation minister is stealing the items
        Output:
            None
        """
        transportation_minister = minister_utility.get_minister(
            constants.TRANSPORTATION_MINISTER
        )
        lost_items_message = ""
        lost_items: Dict[str, float] = {}
        if stealing:
            value_stolen = 0
        for current_item in self.get_held_items():
            initial_amount = self.get_inventory(current_item)
            amount_lost = min(
                initial_amount, random.randrange(0, int(initial_amount / 2) + 2)
            )  # 0-50%
            if amount_lost > 0:
                lost_items[current_item.key] = (
                    lost_items.get(current_item.key, 0) + amount_lost
                )
                self.change_inventory(current_item, -1 * amount_lost)
                if stealing:
                    value_stolen += current_item.price * amount_lost
                    market_utility.change_price(
                        current_item,
                        sum(
                            [
                                random.randrange(1, 7) <= 1
                                for _ in range(math.ceil(amount_lost))
                            ]
                        ),
                    )

        if lost_items:  # If at least 1 item stolen
            if sum(lost_items.values()) == 1:
                was_word = "was"
            else:
                was_word = "were"

            if self.actor_type == constants.TILE_ACTOR_TYPE:
                text = f"{actor_utility.summarize_amount_dict(lost_items)} {was_word} lost, damaged, or misplaced."
            elif self.actor_type == constants.MOB_ACTOR_TYPE:
                text = f"{actor_utility.summarize_amount_dict(lost_items)} carried by the {self.name} {was_word} lost, damaged, or misplaced."

            if flags.player_turn:
                intro_text = f"{transportation_minister.current_position.name} {transportation_minister.name} reports a logistical incident "
                if self.get_cell().grid.is_abstract_grid:
                    intro_text += f"in orbit of {self.get_cell().grid.name}: /n /n"
                elif self.get_cell().tile.name != "default":
                    intro_text += f"at {self.get_cell().tile.name}: /n /n"
                else:
                    intro_text += (
                        f"at ({self.get_cell().x}, {self.get_cell().y}): /n /n"
                    )
                text = f"{intro_text}{text} /n /n"
                transportation_minister.display_message(
                    text, override_input_dict={"zoom_destination": self}
                )
            else:
                status.logistics_incident_list.append(
                    {
                        "unit": self,
                        "cell": self.get_cell(),
                        "explanation": text,
                    }
                )
        if stealing and value_stolen > 0:
            transportation_minister.steal_money(value_stolen, "inventory_attrition")

    def set_name(self, new_name):
        """
        Description:
            Sets this actor's name
        Input:
            string new_name: Name to set this actor's name to
        Output:
            None
        """
        self.name = new_name

    def set_coordinates(self, x, y):
        """
        Description:
            Moves this actor to the inputted coordinates
        Input:
            int x: grid x coordinate to move this actor to
            int y: grid y coordinate to move this actor to
        Output:
            None
        """
        self.x = x
        self.y = y

    def set_tooltip(self, new_tooltip):
        """
        Description:
            Sets this actor's tooltip to the inputted list, with each item representing a line of the tooltip
        Input:
            string list new_tooltip: Lines for this actor's tooltip
        Output:
            None
        """
        self.tooltip_text = new_tooltip
        for current_image in self.images:
            current_image.set_tooltip(new_tooltip)

    def update_tooltip(self):
        """
        Description:
            Sets this actor's tooltip to what it should be whenever the player looks at the tooltip. By default, sets tooltip to this actor's name
        Input:
            None
        Output:
            None
        """
        self.set_tooltip([self.name.capitalize()])

    def remove_complete(self):
        """
        Description:
            Removes this object and deallocates its memory - defined for any removable object w/o a superclass
        Input:
            None
        Output:
            None
        """
        self.remove()
        del self

    def remove(self):
        """
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        Input:
            None
        Output:
            None
        """
        status.actor_list = utility.remove_from_list(status.actor_list, self)

    def touching_mouse(self):
        """
        Description:
            Returns whether any of this actor's images is colliding with the mouse
        Input:
            None
        Output:
            boolean: Returns True if any of this actor's images is colliding with the mouse, otherwise returns False
        """
        for current_image in self.images:
            if current_image.Rect.collidepoint(
                pygame.mouse.get_pos()
            ):  # if mouse is in image
                return True
        return False  # return false if None touch mouse

    def can_show_tooltip(self):
        """
        Description:
            Returns whether this actor's tooltip can be shown. By default, its tooltip can be shown when it is visible and colliding with the mouse
        Input:
            None
        Output:
            None
        """
        if (
            self.touching_mouse() and constants.current_game_mode in self.modes
        ):  # and not targeting_ability
            return True
        else:
            return False

    def draw_tooltip(self, below_screen, beyond_screen, height, width, y_displacement):
        """
        Description:
            Draws this actor's tooltip when moused over. The tooltip's location may vary when the tooltip is near the edge of the screen or if multiple tooltips are being shown
        Input:
            boolean below_screen: Whether any of the currently showing tooltips would be below the bottom edge of the screen. If True, moves all tooltips up to prevent any from being below the screen
            boolean beyond_screen: Whether any of the currently showing tooltips would be beyond the right edge of the screen. If True, moves all tooltips to the left to prevent any from being beyond the screen
            int height: Combined pixel height of all tooltips
            int width: Pixel width of the widest tooltip
            int y_displacement: How many pixels below the mouse this tooltip should be, depending on the order of the tooltips
        Output:
            None
        """
        self.update_tooltip()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if below_screen:
            mouse_y = constants.display_height + 10 - height
        if beyond_screen:
            mouse_x = constants.display_width - width
        mouse_y += y_displacement

        if hasattr(self, "images"):
            tooltip_image = self.images[0]
            for (
                current_image
            ) in (
                self.images
            ):  # only draw tooltip from the image that the mouse is touching
                if current_image.Rect.collidepoint((mouse_x, mouse_y)):
                    tooltip_image = current_image
        else:
            tooltip_image = self

        if (mouse_x + tooltip_image.tooltip_box.width) > constants.display_width:
            mouse_x = constants.display_width - tooltip_image.tooltip_box.width
        tooltip_image.tooltip_box.x = mouse_x
        tooltip_image.tooltip_box.y = mouse_y
        tooltip_image.tooltip_outline.x = (
            tooltip_image.tooltip_box.x - tooltip_image.tooltip_outline_width
        )
        tooltip_image.tooltip_outline.y = (
            tooltip_image.tooltip_box.y - tooltip_image.tooltip_outline_width
        )
        pygame.draw.rect(
            constants.game_display,
            constants.color_dict[constants.COLOR_BLACK],
            tooltip_image.tooltip_outline,
        )
        pygame.draw.rect(
            constants.game_display,
            constants.color_dict[constants.COLOR_WHITE],
            tooltip_image.tooltip_box,
        )
        for text_line_index in range(len(tooltip_image.tooltip_text)):
            text_line = tooltip_image.tooltip_text[text_line_index]
            constants.game_display.blit(
                text_utility.text(text_line, constants.myfont),
                (
                    tooltip_image.tooltip_box.x + scaling.scale_width(10),
                    tooltip_image.tooltip_box.y
                    + (text_line_index * constants.fonts["default"].size),
                ),
            )

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
        return utility.combine([], self.image_dict["default"])

    def update_image_bundle(self):
        """
        Description:
            Updates this actor's images with its current image id list
        Input:
            None
        Output:
            None
        """
        self.set_image(self.get_image_id_list())

    def set_inventory_capacity(self, new_value):
        """
        Description:
            Sets this unit's inventory capacity, updating info displays as needed
        Input:
            int new_value: New inventory capacity value
        Output:
            None
        """
        self.inventory_capacity = new_value
        if new_value != 0:
            if (
                hasattr(status, f"displayed_{self.actor_type}")
                and getattr(status, f"displayed_{self.actor_type}") == self
            ):  # Updates info display for changed capacity
                actor_utility.calibrate_actor_info_display(
                    getattr(status, f"{self.actor_type}_info_display"), self
                )
