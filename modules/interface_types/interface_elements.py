# Contains functionality for interface elements and collections

import pygame
from ..constructs import images
from ..util import scaling, utility, dummy_utility
import modules.constants.constants as constants
import modules.constants.status as status


class interface_element:
    """
    Abstract base interface element class
    Object that can be contained in an interface collection and has a location, rect, and image bundle with particular conditions for displaying, along with an optional
        tooltip when displayed
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates' = (0, 0): int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear, optional for elements with parent collections
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'member_config' = {}: Dictionary of extra configuration values for how to add elements to collections
        Output:
            None
        """
        self.can_show_override = "none"
        self.width = input_dict["width"]
        self.height = input_dict["height"]
        self.Rect = pygame.Rect(
            0, constants.display_height - (self.height), self.width, self.height
        )
        self.showing = False
        self.parent_collection = input_dict.get("parent_collection", "none")
        self.has_parent_collection = self.parent_collection != "none"
        if not self.has_parent_collection:
            status.independent_interface_elements.append(self)

        input_dict["coordinates"] = input_dict.get("coordinates", (0, 0))
        self.x, self.y = input_dict["coordinates"]
        if self.has_parent_collection:
            input_dict["member_config"] = input_dict.get("member_config", {})
            input_dict["member_config"]["x_offset"] = input_dict["member_config"].get(
                "x_offset", input_dict["coordinates"][0]
            )
            input_dict["member_config"]["y_offset"] = input_dict["member_config"].get(
                "y_offset", input_dict["coordinates"][1]
            )
            self.parent_collection.add_member(self, input_dict["member_config"])
        else:
            self.set_origin(input_dict["coordinates"][0], input_dict["coordinates"][1])

        if "modes" in input_dict:
            self.set_modes(input_dict["modes"])
        elif "parent_collection" != "none":
            self.set_modes(self.parent_collection.modes)

        if "image_id" in input_dict:
            self.create_image(input_dict["image_id"])

    def remove_recursive(self, complete=False):
        """
        Description:
            Recursively removes a collection and its members
        Input:
            boolean complete=False: Whether to use remove_complete or remove for each item
        Output:
            None
        """
        if complete:
            self.remove_complete()
        else:
            self.remove()

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
        if self.has_parent_collection:
            self.parent_collection.remove_member(self)
        status.independent_interface_elements = utility.remove_from_list(
            status.independent_interface_elements, self
        )

    def draw(self):
        """
        Description:
            Draws this element's image - should only call if can_draw()
        Input:
            None
        Output:
            None
        """
        self.image.draw()

    def create_image(self, image_id):
        """
        Description:
            Creates an image associated with this interface element - can be overridden by subclasses to allow different kinds of images to be created at the same initialization
                step
        """
        self.image = images.button_image(self, self.width, self.height, image_id)

    def can_draw(self):
        """
        Description:
            Calculates and returns whether it would be valid to call this object's draw()
        Input:
            None
        Output:
            boolean: Returns whether it would be valid to call this object's draw()
        """
        return self.showing and hasattr(self, "image")

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button can be shown. By default, elements can be shown during game modes in which they can appear, iff their parent collection (if any) is also showing
        Input:
            boolean skip_parent_collection=False: Whether can_show should rely on parent collection also showing
        Output:
            boolean: Returns True if this button can appear during the current game mode, otherwise returns False
        """
        if self.can_show_override == "none":
            if (not self.has_parent_collection) or skip_parent_collection:
                if (
                    skip_parent_collection
                    and self.has_parent_collection
                    and self.parent_collection.has_parent_collection
                ):
                    # skip_parent_collection ignores the immediate parent collection to avoid recursion, but can still check grandparent collection in most cases
                    return (
                        self.parent_collection.parent_collection.allow_show(self)
                        and constants.current_game_mode in self.modes
                    )
                return constants.current_game_mode in self.modes
            elif self.parent_collection.allow_show(self):
                return constants.current_game_mode in self.modes
            return False
        else:
            return self.can_show_override.can_show(skip_parent_collection=True)

    def set_origin(self, new_x, new_y):
        """
        Description:
            Sets this interface element's location at the inputted coordinates
        Input:
            int new_x: New x coordinate for this element's origin
            int new_y: New y coordinate for this element's origin
        Output:
            None
        """
        self.x = new_x
        self.Rect.x = self.x
        self.y = new_y
        self.Rect.y = constants.display_height - (self.y + self.height)
        if self.has_parent_collection:
            self.x_offset = self.x - self.parent_collection.x
            self.y_offset = self.y - self.parent_collection.y

    def set_modes(self, new_modes):
        """
        Description:
            Sets this interface element's active modes to the inputted list
        Input:
            string list new_modes: List of game modes in which this element is active
        Output:
            None
        """
        self.modes = new_modes

    def calibrate(self, new_actor, override_exempt=False):
        """
        Description:
            Allows subclasses to attach to the inputted actor and updates information based on the inputted actor
        Input:
            string/actor new_actor: The displayed actor whose information is matched by this label. If this equals 'none', the label does not match any actors.
        Output:
            None
        """
        return

    def insert_collection_above(self, override_input_dict=None):
        """
        Description:
            Replaces this element's place in its parent collection with a new interface collection, allowing elements to dynamically form collections after initialization
                without interfering with above hierarchies
        'Input':
            dictionary override_input_dict=None: Optional dictionary to override attributes of created collection's input_dict
        'Output':
            None
        """
        input_dict = {
            "coordinates": (self.x, self.y),
            "width": self.width,
            "height": self.height,
            "modes": self.modes,
            "parent_collection": self.parent_collection,
            "init_type": "interface collection",
            "member_config": {},
        }
        if override_input_dict:
            for attribute in override_input_dict:
                input_dict[attribute] = override_input_dict[attribute]

        if self.parent_collection != "none":
            input_dict["member_config"]["index"] = self.parent_collection.members.index(
                self
            )
            if (
                hasattr(self.parent_collection, "order_overlap_list")
                and self in self.parent_collection.order_overlap_list
            ):
                input_dict["member_config"]["order_overlap"] = True

            if (
                hasattr(self.parent_collection, "order_exempt_list")
                and self in self.parent_collection.order_exempt_list
            ):
                input_dict["member_config"]["order_exempt"] = True

            if hasattr(self, "x_offset"):
                input_dict["member_config"]["x_offset"] = self.x_offset

            if hasattr(self, "y_offset"):
                input_dict["member_config"]["y_offset"] = self.y_offset

            if hasattr(self, "order_x_offset"):
                input_dict["member_config"]["order_x_offset"] = self.order_x_offset

            if hasattr(self, "order_y_offset"):
                input_dict["member_config"]["order_y_offset"] = self.order_y_offset

            self.parent_collection.remove_member(self)

        new_parent_collection = (
            constants.actor_creation_manager.create_interface_element(input_dict)
        )

        new_parent_collection.add_member(self, {})

        return new_parent_collection

    def get_actor_type(self) -> str:
        """
        Description:
            Recursively finds the type of actor this interface is attached to
        Input:
            None
        Output:
            str: Returns type of actor this interface is attached to
        """
        if hasattr(self, "actor_type"):
            return self.actor_type
        elif self.has_parent_collection:
            return self.parent_collection.get_actor_type()
        else:
            return None


class interface_collection(interface_element):
    """
    Object managing an image bundle and collection of interactive interface elements, including buttons, free images, and other interface collections
    An entire collection can be displayed or hidden as a unit, along with individual components having their own conditions for being visible when the window is displayed
    A collection could have different modes that display different sub-windows under different conditions while keeping other elements constant
    A particular type of collection could have special ordered functionality, like a series of buttons that can be scrolled through, or a images displayed in horizontal rows w/ maximum widths
    Older, informal collections such as the available minister scrollbar, the movement buttons, and the mob, tile, minister, prosecution, and defense displays should be able to be
        implemented as interface collections. Additionally, the "mode" system could possibly be changed to use overarching interface collections for each mode
    Like an image bundle, members of an interface collection should have independent types and characteristics but be controlled as a unit and created in a list with a dictionary or simple
        string. Unlike an image bundle, a collection does not necessarily have to be saved, and
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'initial_members' = None: members initially created with this collection
        Output:
            None
        """
        self.members = []
        self.minimized = False
        self.is_info_display = input_dict.get("is_info_display", False)
        if self.is_info_display:
            self.actor_type = input_dict["actor_type"]

        input_dict["resize_with_contents"] = input_dict.get(
            "resize_with_contents", False
        )
        self.resize_with_contents = input_dict["resize_with_contents"]
        if self.resize_with_contents:
            self.member_rects = []

        self.calibrate_exempt_list = []

        super().__init__(input_dict)
        self.original_coordinates = (self.x, self.y)
        if self.has_parent_collection:
            self.original_offsets = (self.x_offset, self.y_offset)
        self.description = input_dict.get("description", "window")
        self.move_with_mouse_config = {"moving": False}
        customize_button_x_offset = 0
        customize_button_size = 20
        if input_dict.get("allow_minimize", False) or input_dict.get(
            "allow_move", False
        ):
            self.insert_collection_above()
            customize_button_width = scaling.scale_width(customize_button_size)
            customize_button_height = scaling.scale_width(customize_button_size)

            if input_dict.get("allow_minimize", False):
                constants.actor_creation_manager.create_interface_element(
                    {
                        "coordinates": scaling.scale_coordinates(
                            customize_button_x_offset, 5
                        ),
                        "width": customize_button_width,
                        "height": customize_button_height,
                        "parent_collection": self.parent_collection,
                        "attached_collection": self,
                        "init_type": "minimize interface collection button",
                        "image_id": "buttons/minimize_button.png",
                        "member_config": {"order_exempt": True},
                    }
                )
                customize_button_x_offset += customize_button_size + 5

            if input_dict.get("allow_move", False):
                constants.actor_creation_manager.create_interface_element(
                    {
                        "coordinates": scaling.scale_coordinates(
                            customize_button_x_offset, 5
                        ),
                        "width": customize_button_width,
                        "height": customize_button_height,
                        "parent_collection": self.parent_collection,
                        "init_type": "move interface collection button",
                        "image_id": "buttons/reposition_button.png",
                        "member_config": {"order_exempt": True},
                    }
                )
                customize_button_x_offset += customize_button_size + 5

                constants.actor_creation_manager.create_interface_element(
                    {
                        "coordinates": scaling.scale_coordinates(
                            customize_button_x_offset, 5
                        ),
                        "width": customize_button_width,
                        "height": customize_button_height,
                        "parent_collection": self.parent_collection,
                        "init_type": "reset interface collection button",
                        "image_id": "buttons/reset_button.png",
                        "member_config": {"order_exempt": True},
                    }
                )
                customize_button_x_offset += customize_button_size + 5

        for initial_member_dict in input_dict.get("initial_members", []):
            initial_member_dict["parent_collection"] = self
            constants.actor_creation_manager.create_interface_element(
                initial_member_dict
            )

    def create_image(self, image_id):
        """
        Description:
            Creates an image associated with this interface element - overrides parent version to create a collection image instead of the default button images at the same
                initialization step
        Input:
            string/list/dict image_id: Single or list of string image file paths and/or offset image dictionaries
        Output:
            None
        """
        self.image = images.collection_image(self, self.width, self.height, image_id)

    def calibrate(self, new_actor, override_exempt=False):
        """
        Description:
            Atttaches this collection and its members to inputted actor and updates their information based on the inputted actor
        Input:
            string/actor new_actor: The displayed actor whose information is matched by this label. If this equals 'none', the label does not match any actors.
        Output:
            None
        """
        super().calibrate(new_actor, override_exempt)
        for member in self.members:
            if override_exempt or (not member in self.calibrate_exempt_list):
                if hasattr(member, "members"):
                    member.calibrate(new_actor, override_exempt)
                else:
                    member.calibrate(new_actor)
        if self.is_info_display:
            if new_actor == "none":
                new_actor = None
            setattr(status, "displayed_" + self.actor_type, new_actor)

    def add_member(self, new_member, member_config=None):
        """
        Description:
            Adds an existing interface element as a member of this collection and sets its origin coordinates relative to this collection's origin coordinates
        Input:
            interface_element new_member: New element to add as a member
            int x_offset: Number of pixels to the right the new member's origin should be from the collection's origin
            int x_offset: Number of pixels upward the new member's origin should be from the collection's origin
        Output:
            None
        """
        if not member_config:
            member_config = {}

        member_config["x_offset"] = member_config.get("x_offset", 0)
        member_config["y_offset"] = member_config.get("y_offset", 0)
        member_config["calibrate_exempt"] = member_config.get("calibrate_exempt", False)

        if not new_member.has_parent_collection:
            new_member.has_parent_collection = True
            status.independent_interface_elements = utility.remove_from_list(
                status.independent_interface_elements, new_member
            )
        new_member.parent_collection = self
        if not "index" in member_config:
            self.members.append(new_member)
        else:
            self.members.insert(member_config["index"], new_member)
        if self.resize_with_contents and new_member.Rect != "none":
            self.member_rects.append(new_member.Rect)
        new_member.set_origin(
            self.x + member_config["x_offset"], self.y + member_config["y_offset"]
        )

        if member_config["calibrate_exempt"] and hasattr(self, "calibrate_exempt_list"):
            self.calibrate_exempt_list.append(new_member)

    def remove_member(self, removed_member):
        """
        Description:
            Removes a member from this collection
        Input:
            interface_element removed_member: Member to remove from this collection
        Output:
            None
        """
        if hasattr(removed_member, "x_offset"):
            removed_member.x_offset = None
        if hasattr(removed_member, "y_offset"):
            removed_member.y_offset = None
        removed_member.parent_collection = "none"
        removed_member.has_parent_collection = False
        status.independent_interface_elements.append(removed_member)
        self.members.remove(removed_member)

    def remove_recursive(self, complete=False):
        """
        Description:
            Recursively removes a collection and its members
        Input:
            boolean complete=False: Whether to use remove_complete or remove for each item
        Output:
            None
        """
        for current_member in self.members.copy():
            self.remove_member(current_member)
            current_member.remove_recursive(complete=complete)

        if complete:
            super().remove_complete()
        else:
            super().remove()

    def remove(self):
        """
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        Input:
            None
        Output:
            None
        """
        self.remove_recursive()

    def set_origin(self, new_x, new_y):
        """
        Description:
            Sets this interface element's location and those of its members to the inputted coordinates
        Input:
            int new_x: New x coordinate for this element's origin
            int new_y: New y coordinate for this element's origin
        Output:
            None
        """
        super().set_origin(new_x, new_y)
        for (
            member
        ) in (
            self.members
        ):  # members will retain their relative positions with the collection while shifting to be centered around the new collection origin
            member.set_origin(new_x + member.x_offset, new_y + member.y_offset)

    def set_modes(self, new_modes):
        """
        Description:
            Sets this interface element's active modes and those of its members to the inputted list
        Input:
            string list new_modes: List of game modes in which this element is active
        Output:
            None
        """
        super().set_modes(new_modes)
        for member in self.members:
            member.set_modes(new_modes)

    def allow_show(self, member):
        """
        Description:
            Returns whether this collection would allow the inputted member to be shown - allows collection to have control over whether
                members are shown without modifying either can_show logic
                for example, for a tabbed collection, the collection wants control over whether a member is shown based on which tab is selected but doesn't want this logic
                to interfere with its own can_show logic, since the overall tabbed collection should show regardless of which tab is selected
        Input:
            None
        Output:
            boolean: Returns True if this button can appear during the current game mode, otherwise returns False
        """
        return self.showing

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this collection can be shown
        Input:
            None
        Output:
            boolean: Returns True if this button can appear under current conditions, otherwise returns False
        """
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if (
            self.is_info_display
            and getattr(status, "displayed_" + self.actor_type) == None
        ):
            return False
        else:
            return result and not self.minimized

    def update_collection(self):
        if self.resize_with_contents:
            for member in self.members:
                if hasattr(member, "members"):
                    member.update_collection()
            if len(self.member_rects) > 0:
                self.Rect.update(
                    self.member_rects[0].unionall(self.member_rects)
                )  # self.Rect = self.member_rects[0].unionall(self.member_rects) #Rect.unionall(self.member_rects)
                if hasattr(self, "image"):
                    self.x = self.Rect.x
                    self.image.update_state(
                        self.image.x, self.image.y, self.Rect.width, self.Rect.height
                    )


class autofill_collection(interface_collection):
    """
    Collection that will calibrate particular 'target' members with specific actors instead of the one the entire collection is calibrating to - such as calibrating the
        group, officer, and worker cells to the corresponding actors in the autofill operation when an officer is selected
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'autofill target': dict value - Dictionary with lists of the elements to calibrate to each autofill target type, like {'officer': [...], 'group': [...]}
        Output:
            None
        """
        self.autofill_targets = input_dict["autofill_targets"]
        self.autofill_actors = {}
        for autofill_target_type in self.autofill_targets:
            self.autofill_actors[autofill_target_type] = "none"
        self.autofill_actors["procedure"] = "none"
        self.search_start_index = 0
        super().__init__(input_dict)

    def calibrate(self, new_actor, override_exempt=False):
        """
        Description:
            Atttaches this collection and its members to inputted actor and updates their information based on the inputted actor
        Input:
            string/actor new_actor: The displayed actor whose information is matched by this label. If this equals 'none', the label does not match any actors.
        Output:
            None
        """
        # search start index may be changed by cycle autofill buttons between calibrates
        self.autofill_actors = dummy_utility.generate_autofill_actors(
            search_start_index=self.search_start_index
        )
        for autofill_target_type in self.autofill_targets:
            for autofill_target in self.autofill_targets[autofill_target_type]:
                # eg. generate autofill actors gives back a dummy officer, which all autofill targets that accept officers then calibrate to, repeat for worker/group targets
                autofill_target.calibrate(self.autofill_actors[autofill_target_type])
        super().calibrate(new_actor, override_exempt)
        self.search_start_index = 0


class tabbed_collection(interface_collection):
    """
    High-level collection that controls a collection of tab buttons that each select an associated member collection "tab" to be shown, with only the tab buttons and the
        currently selected tab showing at a time
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
        Output:
            None
        """
        self.tabbed_members = []
        self.current_tabbed_member = None
        super().__init__(input_dict)
        self.tabs_collection = (
            constants.actor_creation_manager.create_interface_element(
                {
                    "coordinates": scaling.scale_coordinates(0, 5),
                    "width": scaling.scale_width(10),
                    "height": scaling.scale_height(30),
                    "init_type": "ordered collection",
                    "parent_collection": self,
                    "direction": "horizontal",
                }
            )
        )

    def allow_show(self, member):
        """
        Description:
            Returns whether this collection would allow the inputted member to be shown - allows collection to have control over whether
                members are shown without modifying either can_show logic -
                for example, for a tabbed collection, the collection wants control over whether a member is shown based on which tab is selected but doesn't want this logic
                to interfere with its own can_show logic, since the overall tabbed collection should show regardless of which tab is selected
        Input:
            None
        Output:
            boolean: Returns True if this button can appear during the current game mode, otherwise returns False
        """
        if member in self.tabbed_members and member != self.current_tabbed_member:
            return False
        return super().allow_show(member)

    def add_member(self, new_member, member_config={}):
        """
        Description:
            Adds an existing interface element as a member of this collection and sets its origin coordinates relative to this collection's origin coordinates. If adding a
                collection that is designated as a tab, it is automatically linked with a new tab button
        Input:

        Output:
            None
        """
        member_config["tabbed"] = member_config.get("tabbed", False)
        if member_config["tabbed"] and not "button_image_id" in member_config:
            member_config["button_image_id"] = "buttons/default_button.png"
        super().add_member(new_member, member_config)

        if member_config["tabbed"]:
            constants.actor_creation_manager.create_interface_element(
                {
                    "width": scaling.scale_width(36),
                    "height": scaling.scale_height(36),
                    "init_type": "tab button",
                    "parent_collection": self.tabs_collection,
                    "image_id": member_config["button_image_id"],
                    "identifier": member_config.get("identifier", None),
                    "linked_element": new_member,
                }
            )
            self.tabbed_members.append(new_member)
            if len(self.tabbed_members) == 1:
                self.current_tabbed_member = new_member
            if "identifier" in member_config:
                new_member.identifier = member_config["identifier"]


class ordered_collection(interface_collection):
    """
    Collection that moves its members to display each visible element in order
    """

    def __init__(
        self, input_dict
    ):  # change inventory display to a collection so that it orders correctly
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'separation' = scaling.scale_height(5): int value - Distance to set between ordered members
                'direction' = 'vertical': string value - Direction to order members in
                'reversed' = False: boolean value - Whether to reverse the order of members in the specified direction (top to bottom or bottom to top)
                'second_dimension_increment' = 0: int value - Increment between each row/column of this collection - 2 elements with a difference of 1 second dimension
                    coordinate will be the increment away along the second dimension
                'anchor_coordinate' = None: int value - Optional relative coordinate around which each row/column of collection will be centered
        Output:
            None
        """
        self.separation = input_dict.get("separation", scaling.scale_height(5))
        self.direction = input_dict.get("direction", "vertical")
        self.second_dimension_increment = input_dict.get(
            "second_dimension_increment", 0
        )
        self.second_dimension_coordinates = {}
        self.reverse_multiplier = 1
        if input_dict.get("reversed", False):
            self.reverse_multiplier *= -1
        self.order_overlap_list = []
        self.order_exempt_list = []
        if "anchor_coordinate" in input_dict:
            self.anchor_coordinate = input_dict["anchor_coordinate"]
        super().__init__(input_dict)

    def add_member(self, new_member, member_config={}):
        """
        Description:
            Adds an existing interface element as a member of this collection and sets its origin coordinates relative to this collection's origin coordinates
        Input:
            interface_element new_member: New element to add as a member
            int x_offset: Number of pixels to the right the new member's origin should be from the collection's origin
            int x_offset: Number of pixels upward the new member's origin should be from the collection's origin
        Output:
            None
        """
        member_config["order_overlap"] = member_config.get("order_overlap", False)
        member_config["order_exempt"] = member_config.get("order_exempt", False)
        member_config["order_x_offset"] = member_config.get("order_x_offset", 0)
        member_config["order_y_offset"] = member_config.get("order_y_offset", 0)
        if member_config.get("centered", False):
            member_config["order_x_offset"] -= new_member.width / 2
        member_config["second_dimension_coordinate"] = member_config.get(
            "second_dimension_coordinate", 0
        )
        new_member.order_x_offset = member_config["order_x_offset"]
        new_member.order_y_offset = member_config["order_y_offset"]
        super().add_member(new_member, member_config)

        if member_config["order_overlap"] and hasattr(
            self, "order_overlap_list"
        ):  # maybe have a list of lists to iterate through these operations
            self.order_overlap_list.append(new_member)

        if member_config["order_exempt"] and hasattr(self, "order_exempt_list"):
            self.order_exempt_list.append(new_member)

        if (
            "second_dimension_alignment" in member_config
        ):  # if left alignment, go left through each column until one is free, and vice versa
            if member_config["second_dimension_alignment"] in ["left", "leftmost"]:
                increment = -1
            else:
                increment = 1
            coordinate = 0
            valid = False
            while not valid:
                if not str(coordinate) in self.second_dimension_coordinates:
                    valid = True
                if not valid:
                    coordinate += increment
            if member_config["second_dimension_alignment"] in ["leftmost", "rightmost"]:
                # leftmost and rightmost go to farthest column in that direction, rather than making a new column
                coordinate -= increment
            member_config["second_dimension_coordinate"] = coordinate
        key = str(member_config["second_dimension_coordinate"])
        if key in self.second_dimension_coordinates:
            self.second_dimension_coordinates[key].append(new_member)
        else:
            self.second_dimension_coordinates[key] = [new_member]

    def remove_member(self, removed_member):
        """
        Description:
            Removes a member from this collection
        Input:
            interface_element removed_member: Member to remove from this collection
        Output:
            None
        """
        if hasattr(
            removed_member, "order_x_offset"
        ):  # see if there is a way to modify these attributes with a variable instead of manually
            removed_member.order_x_offset = None
        if hasattr(removed_member, "order_y_offset"):
            removed_member.order_y_offset = None
        if removed_member in self.order_overlap_list:
            self.order_overlap_list.remove(removed_member)
        if removed_member in self.order_exempt_list:
            self.order_exempt_list.remove(removed_member)
        for key in self.second_dimension_coordinates:
            if removed_member in self.second_dimension_coordinates[key]:
                self.second_dimension_coordinates[key].remove(removed_member)
        super().remove_member(removed_member)

    def get_size(self, second_dimension_coordinate=0):
        """
        Description:
            Calculates and returns the width or height of a particular row/column of this collection
        Input:
            int second_dimension_coordinate=0: Second dimension coordinate of row/column to check
        Output:
            int: Returns width or height of specified row/column
        """
        size = 0
        for member in self.second_dimension_coordinates.get(
            str(second_dimension_coordinate), []
        ):
            if not (
                member in self.order_exempt_list or member in self.order_overlap_list
            ):
                size += member.height
                size += self.separation
        return size

    def update_collection(self):
        """
        Description:
            Changes locations of collection members to put all visible members in order while skipping hidden ones. Each overlapped element follows ordering logic but
                causes no change in the current ordering location (causing next element to appear at its location), while each exempt element ignores ordering logic
        Input:
            None
        Output:
            None
        """
        super().update_collection()
        for key in self.second_dimension_coordinates:
            second_dimension_coordinate = int(key)
            if self.direction == "vertical":
                current_y = self.y
                current_x = self.x + (
                    second_dimension_coordinate * self.second_dimension_increment
                )
                if hasattr(self, "anchor_coordinate"):
                    current_y += self.anchor_coordinate - (
                        self.get_size(second_dimension_coordinate) / 2
                    )
            elif self.direction == "horizontal":
                current_y = self.y + (
                    second_dimension_coordinate * self.second_dimension_increment
                )
                current_x = self.x
                if hasattr(self, "anchor_coordinate"):
                    current_x += self.anchor_coordinate - (
                        self.get_size(second_dimension_coordinate) / 2
                    )
            for member in self.second_dimension_coordinates[key]:
                if member.showing and not member in self.order_exempt_list:
                    if self.direction == "vertical":
                        preincrement = False
                        if self.reverse_multiplier > 0:
                            preincrement = True
                            current_y -= member.height * self.reverse_multiplier
                        new_x = current_x + member.order_x_offset
                        new_y = current_y + member.order_y_offset
                        if not preincrement:
                            current_y -= member.height * self.reverse_multiplier

                        if (member.x, member.y) != (new_x, new_y):
                            if (
                                hasattr(member, "order_overlap_list")
                                and member.is_info_display
                            ):  # account for ordered collections having coordinates from top left instead of bottom left
                                new_y += member.height * self.reverse_multiplier
                            member.set_origin(new_x, new_y)

                        if not member in self.order_overlap_list:
                            current_y -= self.separation * self.reverse_multiplier
                        else:
                            current_y += member.height * self.reverse_multiplier

                    elif self.direction == "horizontal":
                        new_x = current_x + member.order_x_offset
                        new_y = current_y + member.order_y_offset
                        if (member.x, member.y) != (new_x, new_y):
                            member.set_origin(new_x, new_y)

                        if not member in self.order_overlap_list:
                            current_x += (
                                self.separation + member.width * self.reverse_multiplier
                            )
