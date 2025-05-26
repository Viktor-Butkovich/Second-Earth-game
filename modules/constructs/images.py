# Contains functionality for images

import pygame
import math
from modules.util import (
    utility,
    drawing_utility,
    text_utility,
    scaling,
    minister_utility,
)
from modules.constants import constants, status, flags


class image:
    """
    Abstract base image class
    """

    def __init__(self, width, height):
        """
        Description:
            Initializes this object
        Input:
            int width: Pixel width of this image
            int height: Pixel height of this image
        Output:
            None
        """
        self.contains_bundle = False
        self.text = False
        self.width = width
        self.height = height
        self.Rect = None

    def complete_draw(self):
        """
        Description:
            Draws this image after the necessary pre-call checks are done
        Input:
            None
        Output:
            None
        """
        if self.contains_bundle:
            self.image.complete_draw()
        elif self.image_id != "misc/empty.png":
            drawing_utility.display_image(self.image, self.x, self.y - self.height)

    def touching_mouse(self):
        """
        Description:
            Returns whether this image is colliding with the mouse
        Input:
            None
        Output:
            boolean: Returns True if this image is colliding with the mouse, otherwise returns False
        """
        return self.Rect and self.Rect.collidepoint(pygame.mouse.get_pos())
        # If mouse is in button

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
        return

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this image can be shown
        Input:
            None
        Output:
            boolean: Returns True
        """
        return True

    def draw(self):
        """
        Description:
            Draws this image if it should currently be visible
        Input:
            None
        Output:
            None
        """
        if self.can_show():
            self.complete_draw()

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
        if type(self.image_id) == str:
            image_id_list = [self.image_id]
        else:
            image_id_list = self.image_id
        return image_id_list


class image_bundle(image):
    """
    Group of 'anonymous' bundle images that act as a single image object and are always drawn together in a particular order
    An image can be set to an image bundle rather than a string image path
    """

    def __init__(self, parent_image, image_id_list, pixellate_bundle: bool = False):
        """
        Description:
            Initializes this object
        Input:
            image parent_image: Image that this bundle is attached to
            list image_id_list: List of string image file paths and/or offset image dictionaries
                offset image dictionary: String keys corresponding to extra information for offset images
                    'image'_id': string value - File path to image used for this offset image
                    'size': float value - Scale of offset image, with 1 being the same size as the bundle
                    'x_offset': float value - x-axis offset of image, with 1 being shifted a full width to the right
                    'y_offset': float value - y-axis offset of image, with 1 being shifted a full height upward
                    'level': int value - Layer for image to appear on, with 0 being the default layer, positive levels being above it, and negative levels being below it
            boolean to_front = False: If True, allows this image to appear in front of most other objects instead of being behind them
            pixellated = False: If True, renders this image with a small number of pixels
        Output:
            None
        """
        self.image_type = "bundle"
        self.combined_surface = None
        super().__init__(parent_image.width, parent_image.height)
        self.parent_image = parent_image
        self.members = []
        if isinstance(image_id_list, list):
            for current_image_id in image_id_list:
                self.add_member(current_image_id, generate_combined_surface=False)
            self.combined_surface = (
                self.generate_combined_surface()
            )  # Avoid calling generate_combined_surface on each component
        else:
            if image_id_list.contains_bundle:
                image_id_list = image_id_list.image
            self.members = image_id_list.members
            self.combined_surface = pygame.transform.scale(
                image_id_list.combined_surface, (self.width, self.height)
            )
        self.scale()

    def copy(self):
        """
        Description:
            Creates and returns a copy of this image bundle
        Input:
            None
        Output:
            image_bundle: Returns a copy of this image bundle
        """
        return image_bundle(self.parent_image, self)

    def scale(self):
        """
        Description:
            Sets this bundle to be the size of its attached images and scales each of its member images relative to the bundle size
        Input:
            None
        Output:
            None
        """
        self.width = self.parent_image.width
        self.height = self.parent_image.height
        for member in self.members:
            member.scale()

    def add_member(
        self, image_id, member_type="default", generate_combined_surface: bool = False
    ):
        """
        Description:
            Adds a new member image to this bundle
        Input:
            string/dictionary image_id: String image file path or offset image dictionary that defines the member added
            string member_type = 'default': Optional string to designate this member's type, allowing it to be specifically removed or found based on type later
        """
        if isinstance(image_id, str):
            new_member = bundle_image(self, image_id, member_type)
        else:  # If image id is dictionary with extra information
            new_member = bundle_image(self, image_id, member_type, is_offset=True)
        index = 0
        while (
            index < len(self.members) and self.members[index].level <= new_member.level
        ):  # inserts at back of same level
            index += 1
        self.members.insert(index, new_member)
        if generate_combined_surface:
            self.combined_surface = self.generate_combined_surface()

    def get_blit_sequence(self):
        """
        Description:
            Generates and returns a list of tuples of image surfaces and their respective blit offsets for each member image in this bundle, designed as input for Pygame.blits
        Input:
            None
        Output:
            list: Returns list of tuples of image surfaces and their respective blit offsets for each member image in this bundle
        """
        blit_sequence = []
        for member in self.members:
            if (
                type(member) == image_bundle
            ):  # Recursively get blit sequence for image bundle members
                blit_sequence += member.get_blit_sequence()
            elif member.image_id != "misc/empty.png":
                if member.is_offset:
                    blit_sequence.append(
                        (
                            member.image,
                            ((member.get_blit_x_offset(), member.get_blit_y_offset())),
                        )
                    )
                else:
                    blit_sequence.append((member.image, (0, 0)))
        return blit_sequence

    def generate_combined_surface(self):
        """
        Description:
            Creates and returns a surface that is a combination of each of this bundle's images - allows all images to be drawn with only one blit per frame
        Input:
            None
        Output:
            pygame.Surface: Returns a Pygame Surface that is a combination of each of this bundle's images
        """
        # this is running whenever image is set, even if being set to same image as another bundle
        combined_surface = pygame.Surface(
            (self.width, self.height), pygame.HWSURFACE | pygame.DOUBLEBUF
        )  # has strange interaction with smoke effects
        combined_surface.fill(constants.color_dict[constants.COLOR_TRANSPARENT])
        combined_surface.set_colorkey(
            constants.color_dict[constants.COLOR_TRANSPARENT], pygame.RLEACCEL
        )
        blit_sequence = self.get_blit_sequence()
        if blit_sequence:
            combined_surface.blits(blit_sequence)
        return combined_surface

    def complete_draw(self):
        """
        Description:
            Draws each of this bundle's member images in the correct order with each one's respective size and offsets
        Input:
            None
        Output:
            None
        """
        drawing_utility.display_image(
            self.combined_surface,
            self.parent_image.x,
            self.parent_image.y - self.height,
        )

    def remove_member(self, member_type):
        """
        Description:
            Removes all members of the inputted member type
        Input:
            string member_type: Type of member image to remove
        Output:
            None
        """
        new_member_list = []
        for current_member in self.members:
            if current_member.member_type != member_type:
                new_member_list.append(current_member)
        self.members = new_member_list
        self.combined_surface = self.generate_combined_surface()

    def has_member(self, member_type):
        """
        Description:
            Returns whether this bundle contains any member images of the inputted type
        Input:
            string member_type: Type of member image to search for
        Output:
            None
        """
        for current_member in self.members:
            if current_member.member_type == member_type:
                return True
        return False

    def clear(self):
        """
        Description:
            Removes all of this bundle's member images
        Input:
            None
        Output:
            None
        """
        self.members = []
        self.combined_surface = self.generate_combined_surface()

    def to_list(self):
        """
        Description:
            Generates and returns a list of string image file paths and/or offset image dictionaries that could be passed to a new image bundle to create an identical copy
        Input:
            None
        Output:
            list: Returns list of string image file paths and/or offset image dictionaries
        """
        return_list = []
        for current_member in self.members:
            if not current_member.is_offset:
                return_list.append(current_member.image_id)
            else:
                return_list.append(current_member.image_id_dict)
        return return_list


class bundle_image:
    """
    Not a true image, just a width, height, and id for an image in a bundle
    """

    def __init__(self, bundle, image_id, member_type, is_offset=False):
        """
        Description:
            Initializes this object
        Input:
            image_bundle bundle: Image bundle that this bundle image is a member of
            string/dictionary image_id: String image file path or offset image dictionary to define this image's appearance
                offset image dictionary: String keys corresponding to extra information for offset images
                    'image'_id': string value - File path to image used for this offset image
                    'size' = 1: float value - Scale of offset image, with 1 being the same size as the bundle
                    'x_size' = 1: float value - Scale of offset image on x axis, overrides size
                    'y_size' = 1: float value - Scale of offset image on y axis, overrides size
                    'x_offset' = 0: float value - x-axis offset of image, with 1 being shifted a full width to the right
                    'y_offset' = 0: float value - y-axis offset of image, with 1 being shifted a full height upward
                    'level' = 0: int value - Layer for image to appear on, with 0 being the default layer, positive levels being above it, and negative levels being below it
                    'green_screen': Tuple[int] | List[Tuple[int]] | Dict[str, Dict[str, any]] value - List of colors to use to replace particular preset colors in this image
                        If given [(255, 0, 0)] or (255, 0, 0), replace each instance of the 1st preset green screen color of (62, 82, 82) with red
                        If given [(255, 0, 0), (0, 0, 0)], replace 1st preset green screen color with red, and 2nd preset green screen color with black
                        If given "smart green screen" dict value in the following format:
                            {
                                'water': {
                                    'base_color': (20, 20, 200),
                                    'tolerance': 50,
                                    'replacement_color': (200, 20, 20)
                                },
                                'sand': {
                                    ...
                                }...
                            }
                            Take all colors that are within 50 (tolerance) of the base color and replace them with a new color, while retaining the same difference from
                                the new color as it did with the old color. If a spot of water is slightly darker than the base water color, replace it with something
                                slightly darker than the replacement color, while ignoring anything that is not within 50 of the base water color.
                            Each category can have a preset base color/tolerance determined during asset creation, as well as a procedural replacement color
                            Each category can have a preset smart green screen, with per-terrain or per-tile modifications controlled by world handler and locations
                                World handler handles per-terrain modifications, like dunes sand being slightly different from desert sand, while both are still "Mars red"
                                Locations handlers per-tile modifications, like a tile with earth-imported soil looking different from default planet soil
                            This system could also work for skin shading, polar dust, light levels, vegetation, resources, building appearances, etc.
                    'color_filter': dictionary value - Dictionary of RGB values to add to each pixel in this image
            string member_type: String to designate this member's type, allowing it to be specifically removed or found based on type later, 'default' by default
            boolean is_offset = False: Whether this is an offset image that takes a dictionary image id or a normal image that takes a string image id
        Output:
            None
        """
        self.bundle = bundle
        self.image = None
        self.member_type = member_type
        self.is_offset = is_offset
        if not is_offset:
            self.image_id = image_id
            self.level = 0
            self.detail_level = constants.BUNDLE_IMAGE_DETAIL_LEVEL
        else:
            self.image_id_dict = image_id
            self.image_id = image_id["image_id"]
            self.x_size = image_id.get(
                "x_size", image_id.get("size", 1)
            )  # uses inputted x_size if present, otherwise inputted size, otherwise 1
            self.y_size = image_id.get(
                "y_size", image_id.get("size", 1)
            )  # uses inputted y_size if present, otherwise inputted size, otherwise 1
            self.x_offset = image_id.get("x_offset", 0)
            self.y_offset = image_id.get("y_offset", 0)
            self.level = image_id.get("level", 0)
            self.alpha = image_id.get("alpha", 255)
            self.detail_level = image_id.get(
                "detail_level", constants.BUNDLE_IMAGE_DETAIL_LEVEL
            )
            self.override_green_screen_colors = image_id.get(
                "override_green_screen_colors", []
            )
            if image_id.get("override_width", None):
                self.override_width = image_id["override_width"]
            if image_id.get("override_height", None):
                self.override_height = image_id["override_height"]
            if "green_screen" in image_id:
                self.has_green_screen = True
                self.green_screen_colors = []
                if image_id["green_screen"] == constants.WORLD_GREEN_SCREEN_DEFAULTS:
                    image_id["green_screen"] = status.current_world.get_green_screen()
                if type(image_id["green_screen"]) == list:
                    for index in range(0, len(image_id["green_screen"])):
                        self.green_screen_colors.append(image_id["green_screen"][index])
                elif type(image_id["green_screen"]) == dict:
                    self.green_screen_colors = image_id["green_screen"]
                else:
                    self.green_screen_colors.append(image_id["green_screen"])
            else:
                self.has_green_screen = False
            if "color_filter" in image_id:
                self.has_color_filter = True
                self.color_filter = image_id["color_filter"]
            else:
                self.has_color_filter = False
            self.pixellated = image_id.get("pixellated", False)
            self.light_pixellated = image_id.get("light_pixellated", False)
            if "font" in image_id:
                self.font = image_id["font"]
            elif type(self.image_id) == str and not self.image_id.endswith(".png"):
                self.font = constants.myfont
            if "free" in image_id:
                self.free = image_id["free"]
        self.scale()
        if (
            type(self.image_id) == pygame.Surface
        ):  # if given pygame Surface, avoid having to render it again
            self.image = self.image_id
        else:
            self.load()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))

    def get_blit_x_offset(self):
        """
        Description:
            Calculates and returns the final x offset of this member image when blitted to bundle's combined surface
        Input:
            None
        Output:
            double: Returns final x offset of this member image when blitted to bundle's combined surface
        """
        if hasattr(self, "free") and self.free:
            return self.bundle.width * self.x_offset
        else:
            return (
                (self.bundle.width * self.x_offset)
                - (self.width / 2)
                + (self.bundle.width / 2)
            )

    def get_blit_y_offset(self):
        """
        Description:
            Calculates and returns the final y offset of this member image when blitted to bundle's combined surface
        Input:
            None
        Output:
            double: Returns final y offset of this member image when blitted to bundle's combined surface
        """
        if hasattr(self, "free") and self.free:  # hasattr(self, 'override_width'):
            return self.bundle.height * self.y_offset * -1
        else:
            return (
                (self.bundle.height * self.y_offset * -1)
                - (self.height / 2)
                + (self.bundle.height / 2)
            )

    def scale(self):
        """
        Description:
            Sets this image's size to one relative to its bundle's size based on its size multiplier
        Input:
            None
        Output:
            None
        """
        if self.is_offset:
            if hasattr(self, "override_width"):
                self.width = self.override_width
            else:
                self.width = self.bundle.width * self.x_size
            if hasattr(self, "override_height"):
                self.height = self.override_height
            else:
                self.height = self.bundle.height * self.y_size
        else:
            self.width = self.bundle.width
            self.height = self.bundle.height

    def get_color_difference(self, color1, color2):
        """
        Description:
            Calculates and returns the difference between two colors
        Input:
            int tuple color1: RGB values of first color
            int tuple color2: RGB values of second color
        Output:
            int tuple: Returns difference between two colors
        """
        return [a - b for a, b in zip(color1, color2)]

    def load(self):
        """
        Description:
            Loads in this image's image file on initialization
        Input:
            None
        Output:
            None
        """
        if type(self.image_id) == str and self.image_id.endswith(".png"):
            full_image_id = "graphics/" + self.image_id
        elif self.image_id == None:
            full_image_id = "graphics/misc/empty.png"
        else:
            full_image_id = self.image_id
        key = str(full_image_id) + str(self.detail_level)
        no_green_screen_key = key
        if self.is_offset:
            if self.has_green_screen:
                key += str(self.green_screen_colors)
            if self.has_color_filter:
                key += str(self.color_filter)
            if self.pixellated:
                non_pixellated_key = key
                key += "pixellated"
            if self.alpha != 255:
                key += str(self.alpha)
        if key in status.cached_images:  # if image already loaded, use it
            self.image = status.cached_images[key]
        else:  # If image not loaded, load it and add it to the loaded images
            if full_image_id.endswith(".png"):
                self.text = False
                try:  # use if there are any image path issues to help with file troubleshooting, shows the file location in which an image was expected
                    self.image = pygame.image.load(full_image_id)
                except:
                    self.image = pygame.image.load(full_image_id)
                self.image.convert()
                size = self.image.get_size()
                self.image = pygame.transform.scale(  # Decrease detail of each image before applying pixel mutations to speed processing
                    self.image,
                    (
                        math.floor(size[0] * self.detail_level),
                        math.floor(size[1] * self.detail_level),
                    ),
                )
                if self.is_offset and (self.has_green_screen or self.has_color_filter):
                    self.apply_per_pixel_mutations()
            else:
                self.text = True
                self.image = text_utility.text(self.image_id, self.font)
            if self.is_offset:
                if self.light_pixellated:
                    self.image = pygame.transform.scale(
                        self.image,
                        (
                            constants.LIGHT_PIXELLATED_SIZE,
                            constants.LIGHT_PIXELLATED_SIZE,
                        ),
                    )
                if self.pixellated:
                    status.cached_images[non_pixellated_key] = self.image
                    self.image = pygame.transform.scale(
                        self.image,
                        (constants.PIXELLATED_SIZE, constants.PIXELLATED_SIZE),
                    )
                    hashed_key = hash(
                        no_green_screen_key
                    )  # Randomly flip pixellated image in the same way every time
                    if hashed_key % 2 == 0:
                        self.image = pygame.transform.flip(self.image, True, False)
                    if hashed_key % 4 >= 2:
                        self.image = pygame.transform.flip(self.image, False, True)
            if self.is_offset and self.alpha != 255:
                self.image.set_alpha(self.alpha)
            status.cached_images[key] = self.image

    def apply_per_pixel_mutations(self):
        """
        Description:
            Applies green screen and color filter changes to this image
        Input:
            None
        Output:
            None
        """
        width, height = self.image.get_size()
        smart_green_screen = (
            self.has_green_screen and type(self.green_screen_colors) == dict
        )
        color_cache = (
            {}
        )  # Avoid re-computing color changes for that starting color for the rest of the image
        for x in range(width):
            for y in range(height):
                (
                    original_red,
                    original_green,
                    original_blue,
                    alpha,
                ) = self.image.get_at((x, y))
                red, green, blue = (
                    original_red,
                    original_green,
                    original_blue,
                )
                if (
                    color_cache.get((original_red, original_green, original_blue), None)
                    == None
                ):
                    if self.has_green_screen:
                        if smart_green_screen:
                            replaced = False
                            for terrain_type in self.green_screen_colors:
                                if not replaced:
                                    metadata = self.green_screen_colors[terrain_type]
                                    for base_color in metadata["base_colors"]:
                                        displacement = self.get_color_difference(
                                            (red, green, blue),
                                            base_color,
                                        )
                                        if (
                                            sum([abs(a) for a in displacement])
                                            <= metadata["tolerance"]
                                        ):
                                            replaced = True
                                            difference_proportion = (
                                                min(red / base_color[0], 1.5),
                                                min(
                                                    green / base_color[1],
                                                    1.5,
                                                ),
                                                min(
                                                    blue / base_color[2],
                                                    1.5,
                                                ),
                                            )
                                            red = min(
                                                max(
                                                    round(
                                                        metadata["replacement_color"][0]
                                                        * difference_proportion[0]
                                                    ),
                                                    0,
                                                ),
                                                255,
                                            )
                                            green = min(
                                                max(
                                                    round(
                                                        metadata["replacement_color"][1]
                                                        * difference_proportion[1]
                                                    ),
                                                    0,
                                                ),
                                                255,
                                            )
                                            blue = min(
                                                max(
                                                    round(
                                                        metadata["replacement_color"][2]
                                                        * difference_proportion[2]
                                                    ),
                                                    0,
                                                ),
                                                255,
                                            )
                                            break
                                else:
                                    break
                        else:
                            if self.override_green_screen_colors:
                                replaced_colors = self.override_green_screen_colors
                            else:
                                replaced_colors = constants.green_screen_colors
                            for index, current_replaced_color in enumerate(
                                replaced_colors
                            ):
                                # If pixel matches preset green screen color, replace it with the image's corresponding replacement color
                                if (
                                    red,
                                    green,
                                    blue,
                                ) == current_replaced_color:
                                    (
                                        red,
                                        green,
                                        blue,
                                    ) = self.green_screen_colors[index]
                                    break
                    if self.has_color_filter:
                        red = round(
                            max(
                                min(
                                    self.color_filter.get(constants.COLOR_RED, 1) * red,
                                    255,
                                ),
                                0,
                            )
                        )
                        green = round(
                            max(
                                min(
                                    self.color_filter.get(constants.COLOR_GREEN, 1)
                                    * green,
                                    255,
                                ),
                                0,
                            )
                        )
                        blue = round(
                            max(
                                min(
                                    self.color_filter.get(constants.COLOR_BLUE, 1)
                                    * blue,
                                    255,
                                ),
                                0,
                            )
                        )
                    color_cache[(original_red, original_green, original_blue)] = (
                        red,
                        green,
                        blue,
                    )
                else:
                    red, green, blue = color_cache[
                        (original_red, original_green, original_blue)
                    ]
                self.image.set_at((x, y), (red, green, blue, alpha))


class free_image(image):
    """
    Image unrelated to any actors or grids that appears at certain pixel coordinates
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'image_id': string/string list value - List of image bundle component descriptions or string file path to the image used by this object
                'coordinates' = (0, 0): int tuple value - Two values representing x and y coordinates for the pixel location of this image
                'width': int value - Pixel width of this image
                'height': int value - Pixel height of this image
                'modes': string list value - Game modes during which this button can appear
                'parent_collection' = None: interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'member_config' = {}: Dictionary of extra configuration values for how to add elements to collections
                'to_front' = False: boolean value - If True, allows this image to appear in front of most other objects instead of being behind them
        Output:
            None
        """
        self.image_type = "free"
        self.showing = False
        self.has_parent_collection = False
        super().__init__(input_dict["width"], input_dict["height"])
        self.parent_collection = input_dict.get("parent_collection", None)
        self.color_key = input_dict.get("color_key", None)
        self.has_parent_collection = self.parent_collection
        self.pixellate_image: bool = input_dict.get("pixellate_image", False)
        if not self.has_parent_collection:
            status.independent_interface_elements.append(self)

        if self.has_parent_collection:
            input_dict["member_config"] = input_dict.get("member_config", {})
            if not "x_offset" in input_dict["member_config"]:
                input_dict["member_config"]["x_offset"] = input_dict["coordinates"][0]
            if not "y_offset" in input_dict["member_config"]:
                input_dict["member_config"]["y_offset"] = input_dict["coordinates"][1]
            self.parent_collection.add_member(self, input_dict["member_config"])
        else:
            self.set_origin(input_dict["coordinates"][0], input_dict["coordinates"][1])

        if "modes" in input_dict:
            self.set_modes(input_dict["modes"])
        elif self.parent_collection:
            self.set_modes(self.parent_collection.modes)
        self.set_image(input_dict["image_id"])

        self.to_front = input_dict.get("to_front", False)
        status.free_image_list.append(self)

    def calibrate(self, new_actor):
        return

    def set_origin(self, new_x, new_y):
        """
        Description:
            Sets this interface element's location at the inputted coordinates. Along with set_modes, allows a free image to behave as an interface element and join interface collections
        Input:
            int new_x: New x coordinate for this element's origin
            int new_y: New y coordinate for this element's origin
        Output:
            None
        """
        self.x = new_x
        self.y = constants.display_height - new_y
        if hasattr(self, "Rect") and self.Rect:
            self.Rect.x = self.x
            self.Rect.y = constants.display_height - (new_y + self.height)
        if self.has_parent_collection:
            self.x_offset = new_x - self.parent_collection.x
            self.y_offset = new_y - self.parent_collection.y

    def set_modes(self, new_modes):
        """
        Description:
            Sets this interface element's active modes to the inputted list. Along with set_origin, allows a free image to behave as an interface element and join interface collections
        Input:
            string list new_modes: List of game modes in which this element is active
        Output:
            None
        """
        self.modes = new_modes

    def can_draw(self):
        """
        Description:
            Calculates and returns whether it would be valid to call this object's draw()
        Input:
            None
        Output:
            boolean: Returns whether it would be valid to call this object's draw()
        """
        return self.showing

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this image can be shown. By default, it can be shown during game modes in which this image can appear
        Input:
            None
        Output:
            boolean: Returns True if this image can appear during the current game mode, otherwise returns False
        """
        if (
            self.has_parent_collection and self.parent_collection.showing
        ) or not self.has_parent_collection:
            if constants.current_game_mode in self.modes:
                return True
        return False

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
        status.independent_interface_elements = utility.remove_from_list(
            status.independent_interface_elements, self
        )
        status.free_image_list = utility.remove_from_list(status.free_image_list, self)

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

    def set_image(self, new_image):
        """
        Description:
            Changes this image to reflect the inputted image file path
        Input:
            string/image new_image: Image file path to change this image to, or an image to copy
        Output:
            None
        """
        if isinstance(new_image, image_bundle):
            self.contains_bundle = True
            self.image = new_image.copy()
        elif isinstance(new_image, pygame.Surface):
            self.image = new_image
            self.contains_bundle = False
        else:
            if (not hasattr(self, "image_id")) or new_image != self.image_id:
                self.image_id = new_image
                if isinstance(new_image, str):  # if set to string image path
                    self.contains_bundle = False
                    if new_image.endswith(".png"):
                        self.text = False
                        full_image_id = "graphics/" + self.image_id
                    else:
                        self.text = True
                        full_image_id = self.image_id
                    if full_image_id in status.cached_images:
                        self.image = status.cached_images[full_image_id]
                    else:
                        if not self.text:
                            try:  # use if there are any image path issues to help with file troubleshooting, shows the file location in which an image was expected
                                self.image = pygame.image.load(full_image_id)
                            except:
                                print(full_image_id)
                                self.image = pygame.image.load(full_image_id)
                        else:
                            self.image = text_utility.text(
                                full_image_id, constants.myfont
                            )
                        size = self.image.get_size()
                        self.image = pygame.transform.scale(  # Decrease detail of each image before applying pixel mutations to speed processing
                            self.image,
                            (
                                math.floor(size[0] * constants.DETAIL_LEVEL),
                                math.floor(size[1] * constants.DETAIL_LEVEL),
                            ),
                        )
                        status.cached_images[full_image_id] = self.image
                    self.image = pygame.transform.scale(
                        self.image, (self.width, self.height)
                    )
                    if self.color_key:
                        self.image.set_colorkey(self.color_key)
                else:  # if set to image path list
                    self.contains_bundle = True
                    self.image = image_bundle(self, self.image_id)
        if (
            self.pixellate_image and type(self.image) != pygame.Surface
        ):  # If image is an image bundle, convert it to a sufficiently pixellated Surface
            self.image = self.image.generate_combined_surface()
            self.contains_bundle = False
            self.image = pygame.transform.scale(
                self.image,
                (constants.LIGHT_PIXELLATED_SIZE, constants.LIGHT_PIXELLATED_SIZE),
            )
            self.image = pygame.transform.scale(
                self.image,
                (self.width, self.height),
            )

    def can_show_tooltip(self):
        """
        Description:
            Returns whether this image's tooltip can currently be shown. By default, free images do not have tooltips and this always returns False
        Input:
            None
        Output:
            Returns whether this image's tooltip can currently be shown
        """
        return False

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


class background_image(free_image):
    """
    Background image covering entire screen - designed to blit efficiently
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'modes': string list value - Game modes during which this button can appear
        Output:
            None
        """
        input_dict["image_id"] = input_dict.get(
            "image_id",
            {"image_id": "misc/screen_backgrounds/background.png", "detail_level": 1.0},
        )
        if type(input_dict["image_id"]) != list:
            input_dict["image_id"] = [input_dict["image_id"]]
        self.default_image_id = input_dict["image_id"]
        input_dict["coordinates"] = (0, 0)
        input_dict["width"] = constants.display_width
        input_dict["height"] = constants.display_height
        super().__init__(input_dict)
        self.previous_safe_click_area_showing = False

    def can_show(self):
        """
        Description:
            Returns whether this image can be shown, while also re-setting its image based on current circumstances
        Input:
            None
        Output:
            boolean: Returns True if this image can currently appear, otherwise returns False
        """
        if super().can_show():
            if status.safe_click_area.showing != self.previous_safe_click_area_showing:
                self.previous_safe_click_area_showing = status.safe_click_area.showing
                if self.previous_safe_click_area_showing:
                    self.set_image(
                        utility.combine(
                            self.default_image_id,
                            {
                                "image_id": "misc/safe_click_area.png",
                                "override_width": status.safe_click_area.width,
                                "free": True,
                                "detail_level": 1.0,
                            },
                        )
                    )
                else:
                    self.set_image(self.default_image_id)
            return True
        return False


class tooltip_free_image(free_image):
    """
    Abstract class, free image that has a tooltip when moused over
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'image_id': string/string list value - List of image bundle component descriptions or string file path to the image used by this object
                'coordinates' = (0, 0): int tuple value - Two values representing x and y coordinates for the pixel location of this image
                'width': int value - Pixel width of this image
                'height': int value - Pixel height of this image
                'modes': string list value - Game modes during which this button can appear
                'to_front' = False: boolean value - If True, allows this image to appear in front of most other objects instead of being behind them
        Output:
            None
        """
        super().__init__(input_dict)
        self.Rect = pygame.Rect(
            self.x,
            constants.display_height - (self.y + self.height),
            self.width,
            self.height,
        )
        self.Rect.y = self.y - self.height
        self.tooltip_text = input_dict.get("tooltip_text", [])
        self.update_tooltip()

    def set_tooltip(self, tooltip_text):
        """
        Description:
            Sets this image's tooltip to the inputted list, with each inputted list representing a line of the tooltip
        Input:
            string list new_tooltip: Lines for this image's tooltip
        Output:
            None
        """
        self.tooltip_text = tooltip_text
        tooltip_width = 0
        font = constants.fonts["default"]
        for text_line in tooltip_text:
            tooltip_width = max(
                tooltip_width, font.calculate_size(text_line) + scaling.scale_width(10)
            )
        tooltip_height = (len(self.tooltip_text) * font.size) + scaling.scale_height(5)
        self.tooltip_box = pygame.Rect(self.x, self.y, tooltip_width, tooltip_height)
        self.tooltip_outline_width = 1
        self.tooltip_outline = pygame.Rect(
            self.x - self.tooltip_outline_width,
            self.y + self.tooltip_outline_width,
            tooltip_width + (2 * self.tooltip_outline_width),
            tooltip_height + (self.tooltip_outline_width * 2),
        )

    def update_tooltip(self):
        """
        Description:
            Sets this image's tooltip to what it should be, depending on its subclass. By default, tooltip free images do not have any tooltip text
        Input:
            None
        Output:
            None
        """
        self.set_tooltip(self.tooltip_text)

    def can_show_tooltip(self):
        """
        Description:
            Returns whether this image's tooltip can currently be shown. By default, its tooltip can be shown when it is visible and colliding with the mouse
        Input:
            None
        Output:
            Returns whether this image's tooltip can currently be shown
        """
        if self.touching_mouse() and self.can_show():
            return True
        else:
            return False

    def draw_tooltip(self, below_screen, beyond_screen, height, width, y_displacement):
        """
        Description:
            Draws this image's tooltip when moused over. The tooltip's location may vary when the tooltip is near the edge of the screen or if multiple tooltips are being shown
        Input:
            boolean below_screen: Whether any of the currently showing tooltips would be below the bottom edge of the screen. If True, moves all tooltips up to prevent any from being below the screen
            boolean beyond_screen: Whether any of the currently showing tooltips would be beyond the right edge of the screen. If True, moves all tooltips to the left to prevent any from being beyond the screen
            int height: Combined pixel height of all tooltips
            int width: Pixel width of the widest tooltip
            int y_displacement: How many pixels below the mouse this tooltip should be, depending on the order of the tooltips
        Output:
            None
        """
        if self.can_show():
            self.update_tooltip()
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if below_screen:
                mouse_y = constants.display_height + 10 - height
            if beyond_screen:
                mouse_x = constants.display_width - width
            mouse_y += y_displacement
            self.tooltip_box.x = mouse_x
            self.tooltip_box.y = mouse_y
            self.tooltip_outline.x = self.tooltip_box.x - self.tooltip_outline_width
            self.tooltip_outline.y = self.tooltip_box.y - self.tooltip_outline_width
            pygame.draw.rect(
                constants.game_display,
                constants.color_dict[constants.COLOR_BLACK],
                self.tooltip_outline,
            )
            pygame.draw.rect(
                constants.game_display,
                constants.color_dict[constants.COLOR_WHITE],
                self.tooltip_box,
            )
            for text_line_index in range(len(self.tooltip_text)):
                text_line = self.tooltip_text[text_line_index]
                constants.game_display.blit(
                    text_utility.text(text_line, constants.myfont),
                    (
                        self.tooltip_box.x + scaling.scale_width(10),
                        self.tooltip_box.y + (text_line_index * constants.font_size),
                    ),
                )


class directional_indicator_image(tooltip_free_image):
    """
    Image that moves around minimap to indicate direction or location of a particular cell from status, automatically calibrating with minimap
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'image_id': string/string list value - List of image bundle component descriptions or string file path to the image used by this object
                'coordinates' = (0, 0): int tuple value - Two values representing x and y coordinates for the pixel location of this image
                'width': int value - Pixel width of this image
                'height': int value - Pixel height of this image
                'modes': string list value - Game modes during which this button can appear
                'to_front' = False: boolean value - If True, allows this image to appear in front of most other objects instead of being behind them
                'anchor_key': string value - String status key identifying cell to point to when minimap is calibrated
        Output:
            None
        """
        self.hosting_tile = None
        self.anchor_key = input_dict["anchor_key"]
        status.directional_indicator_image_list.append(self)
        super().__init__(input_dict)

    def update_tooltip(self):
        """
        Description:
            Sets this image's tooltip to what it should be, depending on its subclass. By default, tooltip free images do not have any tooltip text
        Input:
            None
        Output:
            None
        """
        self.set_tooltip([f"Points towards the {self.anchor_key.replace('_', ' ')}"])

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this image can be shown
        Input:
            None
        Output:
            boolean: Returns True if this image can currently appear, otherwise returns False
        """
        return (
            super().can_show(skip_parent_collection=skip_parent_collection)
            and self.hosting_tile == None
        )

    def get_image_id_list(self):
        """
        Description:
            Generates and returns a list this actor's image file paths and dictionaries that can be passed to any image object to display those images together in a particular order and
                orientation
        Input:
            None
        Output:
            list: Returns list of string image file paths, possibly combined with string key dictionaries with extra information for offset images
        """
        image_id_list = super().get_image_id_list()
        for index, current_image in enumerate(image_id_list):
            if type(current_image) == str:
                image_id_list[index] = {
                    "image_id": current_image,
                    "override_width": self.width,
                    "override_height": self.height,
                }
            elif type(current_image) == dict:
                current_image["override_width"] = self.width
                current_image["override_height"] = self.height
        return image_id_list

    def calibrate(self):
        """
        Description:
            Places this image on the anchor cell, if visible on minimap, or otherwise points towards it along the side of the minimap grid
        Input:
            None
        Output:
            None
        """
        return
        anchor = getattr(status, self.anchor_key, None)
        if not anchor:  # Don't attempt to calibrate if anchor cell is not yet defined
            return

        status.scrolling_strategic_map_grid.find_cell(
            *status.scrolling_strategic_map_grid.get_mini_grid_coordinates(
                anchor.x, anchor.y
            )
        ).tile.add_hosted_image(self)
        if status.minimap_grid.is_on_mini_grid(anchor.x, anchor.y):
            status.minimap_grid.find_cell(
                *status.minimap_grid.get_mini_grid_coordinates(anchor.x, anchor.y)
            ).tile.add_hosted_image(self)
        else:
            if self.hosting_tile:
                self.hosting_tile.remove_hosted_image(self)
            anchor_scrolling_cell = status.scrolling_strategic_map_grid.find_cell(
                *status.scrolling_strategic_map_grid.get_mini_grid_coordinates(
                    anchor.x, anchor.y
                )
            )
            anchor_scrolling_coordinates = (
                anchor_scrolling_cell.x,
                anchor_scrolling_cell.y,
            )
            x_offset = (
                status.scrolling_strategic_map_grid.coordinate_width // 2
                - anchor_scrolling_coordinates[0]
            )
            y_offset = (
                status.scrolling_strategic_map_grid.coordinate_height // 2
                - anchor_scrolling_coordinates[1]
            )
            if abs(x_offset) > abs(y_offset):
                slope = y_offset / x_offset

                if x_offset < 0:
                    slope *= -1

                x_position = (
                    status.minimap_grid.x + status.minimap_grid.width - self.width // 2
                )
                x_origin = status.minimap_grid.x + (status.minimap_grid.width // 2)
                y_origin = status.minimap_grid.y + (status.minimap_grid.height // 2)
                y_position = (
                    y_origin - slope * (x_position - x_origin)
                ) - self.height // 2

                if x_offset > 0:
                    x_position -= status.minimap_grid.width
            elif abs(x_offset) < abs(y_offset):
                if x_offset != 0:
                    slope = y_offset / x_offset
                    if y_offset < 0:
                        slope *= -1
                    y_position = (
                        status.minimap_grid.y
                        + status.minimap_grid.height
                        - self.height // 2
                    )
                    y_origin = status.minimap_grid.y + (status.minimap_grid.height // 2)
                    x_origin = status.minimap_grid.x + (status.minimap_grid.width // 2)
                    x_position = (
                        ((y_origin - y_position) / slope) + x_origin - self.width // 2
                    )
                    if y_offset > 0:
                        y_position -= status.minimap_grid.height
                elif y_offset < 0:
                    x_position, y_position = (
                        status.minimap_grid.x
                        + status.minimap_grid.width // 2
                        - self.width // 2,
                        status.minimap_grid.y
                        + status.minimap_grid.height
                        - self.height // 2,
                    )
                else:
                    x_position, y_position = (
                        status.minimap_grid.x
                        + status.minimap_grid.width // 2
                        - self.width // 2,
                        status.minimap_grid.y - self.height // 2,
                    )
            else:  # If x_offset == y_offset
                if y_offset > 0:
                    y_position = status.minimap_grid.y - self.height // 2
                else:
                    y_position = (
                        status.minimap_grid.y
                        + status.minimap_grid.height
                        - self.height // 2
                    )
                if x_offset > 0:
                    x_position = status.minimap_grid.x - self.width // 2
                else:
                    x_position = (
                        status.minimap_grid.x
                        + status.minimap_grid.width
                        - self.width // 2
                    )

            self.set_origin(x_position, y_position)


class indicator_image(tooltip_free_image):
    """
    Image that appears under certain conditions based on its type
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'image_id': string/string list value - List of image bundle component descriptions or string file path to the image used by this object
                'coordinates' = (0, 0): int tuple value - Two values representing x and y coordinates for the pixel location of this image
                'width': int value - Pixel width of this image
                'height': int value - Pixel height of this image
                'modes': string list value - Game modes during which this button can appear
                'to_front' = False: boolean value - If True, allows this image to appear in front of most other objects instead of being behind them
                'indicator_type': string value - Type of variable that this indicator is attached to, like 'prosecution_bribed_judge'
        Output:
            None
        """
        self.indicator_type = input_dict["indicator_type"]
        super().__init__(input_dict)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this image can be shown. Indicator images are shown when their attached variables are at certain values
        Input:
            None
        Output:
            boolean: Returns True if this image can currently appear, otherwise returns False
        """
        if super().can_show(skip_parent_collection=skip_parent_collection):
            if self.indicator_type == "prosecution_bribed_judge":
                if flags.prosecution_bribed_judge:
                    return True
            elif self.indicator_type == "not prosecution_bribed_judge":
                if not flags.prosecution_bribed_judge:
                    return True
            else:
                return True
        return False

    def update_tooltip(self):
        """
        Description:
            Sets this image's tooltip to what it should be, depending on its attached variable
        Input:
            None
        Output:
            None
        """
        if self.indicator_type == "prosecution_bribed_judge":
            text = []
            text.append(
                "The judge has been bribed, giving you an advantage in the next trial this turn"
            )
            text.append("This bonus will fade at the end of the turn if not used")
            self.set_tooltip(text)
        elif self.indicator_type == "not prosecution_bribed_judge":
            text = []
            text.append("The judge has not yet been bribed")
            text.append(
                "Bribing the judge may give you an advantage in the next trial this turn or blunt the impact of any bribes made by the defense."
            )
            self.set_tooltip(text)
        else:
            self.set_tooltip([])


class dice_roll_minister_image(tooltip_free_image):
    """
    Part of a pair of images that shows the controlling minister's position and portrait next to notifications during dice rolls
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'image_id': string/string list value - List of image bundle component descriptions or string file path to the image used by this object
                'coordinates' = (0, 0): int tuple value - Two values representing x and y coordinates for the pixel location of this image
                'width': int value - Pixel width of this image
                'height': int value - Pixel height of this image
                'modes': string list value - Game modes during which this button can appear
                'attached_minister': minister value - Minister attached to this image
                'minister_image_type': string value - Type of minister information shown by this image, like 'portrait' or 'position'
                'minister_position_type': minister_type value - Minister office whose icon should be used by this image, overrides attached_minister's current value
                'minister_message_image' = False: boolean value - Whether this image is attached to a minister message or an action notification dice roll
        Output:
            None
        """
        self.attached_minister = input_dict["attached_minister"]
        self.minister_image_type = input_dict[
            "minister_image_type"
        ]  # position or portrait
        self.minister_position_type = input_dict.get(
            "minister_position_type", self.attached_minister.current_position
        )
        if self.minister_image_type == "portrait":
            input_dict["image_id"] = self.attached_minister.image_id
        elif self.minister_image_type == "position":
            if self.minister_position_type:
                input_dict["image_id"] = (
                    f"ministers/icons/{self.minister_position_type.skill_type}.png"
                )
            else:
                input_dict["image_id"] = "misc/actor_backgrounds/mob_background.png"
        self.minister_message_image = input_dict.get("minister_message_image", False)
        super().__init__(input_dict)
        self.to_front = True

    def update_tooltip(self):
        """
        Description:
            Sets this image's tooltip to what it should be, depending on its subclass. A dice roll minister image's tooltip copies the tooltip of the minister, which describes their name and position. Only the portrait image has a
                tooltip, preventing a double tooltip from the position image
        Input:
            None
        Output:
            None
        """
        if self.minister_image_type == "portrait":
            self.set_tooltip(self.attached_minister.tooltip_text)
        else:
            self.set_tooltip([])


class minister_type_image(tooltip_free_image):
    """
    Image that displays the icon corresponding to a certain minister office. Can be set to always show the icon for the same office or to show the icon of a certain unit's minister
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'image_id': string/string list value - List of image bundle component descriptions or string file path to the image used by this object
                'coordinates' = (0, 0): int tuple value - Two values representing x and y coordinates for the pixel location of this image
                'width': int value - Pixel width of this image
                'height': int value - Pixel height of this image
                'modes': string list value - Game modes during which this button can appear
                'minister_type': string value - Minister office whose icon is always represented by this image, or None if the icon can change
                'attached_label': actor_display_label/string value - Actor display label that this image appears next to, or None if not attached to a label
                'minister_image_type': string value = 'position': Type of minister image to show - either only position or full portrait
        Output:
            None
        """
        self.current_minister = None
        input_dict["image_id"] = "misc/empty.png"
        super().__init__(input_dict)
        self.attached_label = input_dict["attached_label"]
        self.minister_type = input_dict["minister_type"]  # position, like General
        if self.minister_type:
            self.calibrate(minister_utility.get_minister(self.minister_type))
        status.minister_image_list.append(self)
        self.to_front = True

    def calibrate(self, new_minister):
        """
        Description:
            Attaches this image to the inputted minister and updates this image's appearance to the minister's office icon
        Input:
            string/minister new_minister: The displayed minister whose information is matched by this label. If this equals None, the label is detached from any minister and is hidden
        Output:
            None
        """
        if new_minister and new_minister.actor_type != constants.MINISTER_ACTOR_TYPE:
            if hasattr(new_minister, "controlling_minister"):
                new_minister = new_minister.controlling_minister
            else:
                new_minister = None

        self.current_minister = new_minister
        if new_minister:
            self.minister_type = new_minister.current_position
        current_minister_type = self.minister_type
        if (
            self.attached_label
            and self.attached_label.actor
            and self.attached_label.actor.get_permission(constants.PMOB_PERMISSION)
        ):
            current_minister_type = (
                self.attached_label.actor.unit_type.controlling_minister_type
            )
        if current_minister_type:
            self.tooltip_text = current_minister_type.get_description()
            image_id_list = [f"ministers/icons/{current_minister_type.skill_type}.png"]
            self.set_image(image_id_list)
        self.update_image_bundle()

    def update_tooltip(self):
        """
        Description:
            Sets this image's tooltip to what it should be, depending on its subclass. A minister type image's tooltip describes what the office of its office icon does
        Input:
            None
        Output:
            None
        """
        self.set_tooltip(self.tooltip_text)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this image can be shown. If not attached to label, returns same as superclass. Otherwise, returns True if the attached label is showing or False if it is not showing
        Input:
            None
        Output:
            boolean: Returns True if this image can currently appear, otherwise returns False
        """
        if self.attached_label:
            return self.attached_label.showing
        else:
            return super().can_show(skip_parent_collection=skip_parent_collection)


class warning_image(free_image):
    """
    Image that appears over the image it is attached to under certain conditions to draw the player's attention
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'attached_image': image value - Image that this warning appears over under certain conditions
        Output:
            None
        """
        self.attached_image = input_dict["attached_image"]
        input_dict["image_id"] = "misc/warning_icon.png"
        input_dict["coordinates"] = (self.attached_image.x, self.attached_image.y)
        input_dict["width"] = self.attached_image.width
        input_dict["height"] = self.attached_image.height
        input_dict["modes"] = self.attached_image.modes
        super().__init__(input_dict)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this image can be shown. A warning image is shown when the image it is attached to says to show a warning
        Input:
            None
        Output:
            boolean: Returns True if this image can currently appear, otherwise returns False
        """
        return (
            super().can_show(skip_parent_collection=skip_parent_collection)
            and self.attached_image.can_show_warning()
        )


class loading_image_template(free_image):
    """
    Image that occupies the entire screen, covering all other objects while the game is loading
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'image_id': string/string list value - List of image bundle component descriptions or string file path to the image used by this object
        Output:
            None
        """
        input_dict["coordinates"] = (0, 0)
        input_dict["width"] = constants.display_width
        input_dict["height"] = constants.display_height
        input_dict["modes"] = []
        super().__init__(input_dict)
        status.independent_interface_elements = utility.remove_from_list(
            status.independent_interface_elements, self
        )

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this image can be shown. Unlike other images, a loading screen image is always "showing" but only draws when draw() is  directly
                called
        Input:
            None
        Output:
            boolean: Returns True if this image can appear during the current game mode, otherwise returns False
        """
        return True


class actor_image(image):
    """
    Image that is attached to an actor and a grid, representing the actor on a certain grid. An actor will have a different actor_image for each grid on which it appears
    """

    def __init__(self, actor, width, height, grid, image_description):
        """
        Description:
            Initializes this object
        Input:
            actor actor: actor to which this image is attached
            int width: Pixel width of this image
            int height: Pixel height of this image
            grid grid: actor's grid on which this image appears. Each of an actor's images appears on a different grid
            string image_description: Key in this image's actor's image_dict corresponding to the appearance that this image has. For example, a 'default' actor_image will show the actor's default appearance
        Output:
            None
        """
        self.image_type = "actor"
        super().__init__(width, height)
        self.actor = actor
        self.Rect = pygame.Rect(
            self.actor.x, self.actor.y - self.height, self.width, self.height
        )  # (left, top, width, height), bottom left on coordinates
        self.set_image(image_description)
        self.image_description == image_description
        self.grid = grid
        self.modes = self.grid.modes
        self.outline_width = self.grid.grid_line_width + 1
        self.outline = pygame.Rect(
            self.actor.x,
            constants.display_height - (self.actor.y + self.height),
            self.width,
            self.height,
        )
        self.x, self.y = self.grid.convert_coordinates((self.actor.x, self.actor.y))
        if (
            self.grid.is_mini_grid
        ):  # if on minimap and within its smaller range of coordinates, convert actor's coordinates to minimap coordinates and draw image there
            grid_x, grid_y = self.grid.get_mini_grid_coordinates(
                self.actor.x, self.actor.y
            )
        else:
            grid_x = self.actor.x
            grid_y = self.actor.y
        self.go_to_cell((grid_x, grid_y))
        self.set_tooltip("")
        self.change_with_other_images = (
            True  # determines whether set_image function of actor affects this image
        )

    def get_center_coordinates(self):
        """
        Description:
            Returns the pixel coordinates of the center of this image's cell
        Input:
            None
        Output:
            int tuple: Two values representing x and y pixel coordinates of the center of this image's cell
        """
        cell_width = self.grid.get_cell_width()
        cell_height = self.grid.get_cell_height()
        return (
            self.x + round(cell_width / 2),
            constants.display_height - (self.y + round(cell_height / 2)),
        )

    def set_image(self, new_image_description):
        """
        Description:
            Changes this image to reflect this image's actor's image_dict file path value for the inputted key
        Input:
            string new_image_description: Key in this image's actor's image_dict corresponding to this image's new appearance. For example, 'default' will change this actor_image to show the actor's default appearance
            or string list new_image_description: List of image file paths corresponding to this image's new appearance
        Output:
            None
        """
        if (
            isinstance(new_image_description, str)
            and new_image_description in self.actor.image_dict
        ):
            self.image_description = new_image_description
            self.image_id = self.actor.image_dict[new_image_description]
        elif isinstance(new_image_description, image_bundle):
            self.contains_bundle = True
            self.image = new_image_description.copy()
            self.image_id = self.image.image_id
        elif isinstance(new_image_description, pygame.Surface):
            self.image = new_image_description
            self.contains_bundle = False
        else:
            self.image_description = "default"
            self.image_id = new_image_description

        if not isinstance(new_image_description, image_bundle):
            if isinstance(self.image_id, str):  # if set to string image path
                self.contains_bundle = False
                if self.image_id.endswith(".png"):
                    self.text = False
                    full_image_id = "graphics/" + self.image_id
                else:
                    self.text = True
                    full_image_id = self.image_id
                if full_image_id in status.cached_images:
                    self.image = status.cached_images[full_image_id]
                else:
                    if not self.text:
                        try:  # use if there are any image path issues to help with file troubleshooting, shows the file location in which an image was expected
                            self.image = pygame.image.load(full_image_id)
                        except:
                            print(full_image_id)
                            self.image = pygame.image.load(full_image_id)
                    else:
                        self.image = text_utility.text(self.image_id, constants.myfont)
                    size = self.image.get_size()
                    self.image = pygame.transform.scale(  # Decrease detail of each image before applying pixel mutations to speed processing
                        self.image,
                        (
                            math.floor(size[0] * constants.DETAIL_LEVEL),
                            math.floor(size[1] * constants.DETAIL_LEVEL),
                        ),
                    )
                    status.cached_images[full_image_id] = self.image
                self.image = pygame.transform.scale(
                    self.image, (self.width, self.height)
                )
            else:  # if set to image path list
                self.contains_bundle = True
                self.image = image_bundle(self, self.image_id)

    def draw(self):
        """
        Description:
            Draws this image if it should currently be visible. Unlike free images, actor images appear at their actor's grid coordinates
        Input:
            None
        Output:
            None
        """
        if self.can_show():
            if (
                self.grid.is_mini_grid
            ):  # if on minimap and within its smaller range of coordinates, convert actor's coordinates to minimap coordinates and draw image there
                if self.grid.is_on_mini_grid(self.actor.x, self.actor.y):
                    grid_x, grid_y = self.grid.get_mini_grid_coordinates(
                        self.actor.x, self.actor.y
                    )
                    self.go_to_cell((grid_x, grid_y))
                    self.complete_draw()
            else:
                self.go_to_cell((self.actor.x, self.actor.y))
                self.complete_draw()

    def go_to_cell(self, coordinates):
        """
        Description:
            Moves this image to the pixel coordinates corresponding to the inputted grid coordinates
        Input:
            int tuple coordinates: Two values representing x and y coordinates on this image's grid
        Output:
            None
        """
        self.x, self.y = self.grid.convert_coordinates(coordinates)
        self.Rect.x = self.x
        self.Rect.y = self.y - self.height
        self.outline.x = self.x
        self.outline.y = self.y - self.height
        if self.contains_bundle:
            self.image.x = self.x
            self.image.y = self.y

    def set_tooltip(self, tooltip_text):
        """
        Description:
            Sets this image's tooltip to the inputted list, with each item representing a line of the tooltip
        Input:
            string list tooltip_text: Lines for this actor's tooltip
        Output:
            None
        """
        self.tooltip_text = tooltip_text
        tooltip_width = 10  # minimum tooltip width
        font = constants.fonts["default"]
        for text_line in tooltip_text:
            tooltip_width = max(
                tooltip_width, font.calculate_size(text_line) + scaling.scale_width(10)
            )
        tooltip_height = (font.size * len(tooltip_text)) + scaling.scale_height(5)
        self.tooltip_box = pygame.Rect(
            self.actor.x, self.actor.y, tooltip_width, tooltip_height
        )
        self.actor.tooltip_box = self.tooltip_box
        self.tooltip_outline_width = 1
        self.tooltip_outline = pygame.Rect(
            self.actor.x - self.tooltip_outline_width,
            self.actor.y + self.tooltip_outline_width,
            tooltip_width + (2 * self.tooltip_outline_width),
            tooltip_height + (self.tooltip_outline_width * 2),
        )

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this image can be shown. By default, it can be shown during game modes in which this image can appear
        Input:
            None
        Output:
            boolean: Returns True if this image can appear during the current game mode, otherwise returns False
        """
        if constants.current_game_mode in self.modes:
            return True
        else:
            return False


class mob_image(actor_image):
    """
    actor image attached to a mob rather than an actor, gaining the ability to manage the cells corresponding to this image's mob's coordinates
    """

    def __init__(self, actor, width, height, grid, image_description):
        """
        Description:
            Initializes this object
        Input:
            actor actor: actor to which this image is attached
            int width: Pixel width of this image
            int height: Pixel height of this image
            grid grid: actor's grid on which this image appears. Each of an actor's images appears on a different grid
            string image_description: Key in this image's actor's image_dict corresponding to the appearance that this image has. For example, a 'default' actor_image will show the actor's default appearance
        Output:
            None
        """
        super().__init__(actor, width, height, grid, image_description)
        self.current_cell = None
        self.image_type = "mob"
        self.add_to_cell()

    def remove_from_cell(self):
        """
        Description:
            Removes this image and its mob from this image's cell
        Input:
            None
        Output:
            None
        """
        if self.current_cell:
            self.current_cell.contained_mobs = utility.remove_from_list(
                self.current_cell.contained_mobs, self.actor
            )
        self.current_cell = None

    def add_to_cell(self):
        """
        Description:
            Moves this image to the cell corresponding to its grid coordinates, causing this image's actor to be considered to be in the cell. Removes this image from its previous cell. Unlike go_to_cell, which handles pixel location,
                this handles grid location
        Input:
            None
        Output:
            None
        """
        if (
            self.grid.is_mini_grid
        ):  # if on minimap and within its smaller range of coordinates, convert actor's coordinates to minimap coordinates and draw image there
            mini_x, mini_y = self.grid.get_mini_grid_coordinates(
                self.actor.x, self.actor.y
            )
            if self.grid.is_on_mini_grid(self.actor.x, self.actor.y):
                old_cell = self.current_cell
                self.current_cell = self.grid.find_cell(mini_x, mini_y)
                if (
                    old_cell != self.current_cell
                    and not self.actor in self.current_cell.contained_mobs
                    and not (
                        self.actor.any_permissions(
                            constants.IN_GROUP_PERMISSION,
                            constants.IN_VEHICLE_PERMISSION,
                            constants.IN_BUILDING_PERMISSION,
                        )
                    )
                ):
                    self.current_cell.contained_mobs.insert(0, self.actor)
            else:
                self.remove_from_cell()
            self.go_to_cell((mini_x, mini_y))
        else:
            self.remove_from_cell()
            self.current_cell = self.grid.find_cell(self.actor.x, self.actor.y)
            if not self.actor in self.current_cell.contained_mobs and not (
                self.actor.any_permissions(
                    constants.IN_GROUP_PERMISSION,
                    constants.IN_VEHICLE_PERMISSION,
                    constants.IN_BUILDING_PERMISSION,
                )
            ):
                self.current_cell.contained_mobs.insert(0, self.actor)
            self.go_to_cell((self.current_cell.x, self.current_cell.y))

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this image can be shown. By default, it can be shown when its mob should be visible
        Input:
            None
        Output:
            boolean: Returns True if this image can appear during the current game mode and if its mob is not attached to another actor or behind another mob, otherwise returns False
        """
        return self.actor.can_show() and super().can_show()


class button_image(actor_image):
    """
    actor image attached to a button rather than an actor, causing it to be located at a pixel coordinate location where its button should be rather than within a grid cell
    """

    def __init__(self, button, width, height, image_id):
        """
        Description:
            Initializes this object
        Input:
            button button: button to which this image is attached
            int width: Pixel width of this image
            int height: Pixel height of this image
            string image_id: File path to the image used by this object
        Output:
            None
        """
        self.image_type = "button"
        self.button = button
        self.width = width
        self.height = height
        self.x = self.button.x
        self.y = constants.display_height - (self.button.y + self.height) - self.height
        self.modes = button.modes
        self.image_id = image_id
        self.set_image(image_id)
        self.Rect = self.button.Rect
        self.outline_width = 2
        self.outline = pygame.Rect(
            self.x - self.outline_width,
            constants.display_height - (self.y + self.height + self.outline_width),
            self.width + (2 * self.outline_width),
            self.height + (self.outline_width * 2),
        )

    def update_state(self, new_x, new_y, new_width, new_height):
        """
        Description:
            Changes this image's size and location to match its button when its button's size or location changes
        Input:
            new_x: New pixel x coordinate for this image
            new_y: New pixel y coordinate for this image
            new_width: new pixel width for this image
            new_height: new pixel height for this image
        Output:
            None
        """
        self.Rect = self.button.Rect
        self.width = new_width
        self.height = new_height
        self.outline.x = new_x - self.outline_width
        self.outline.y = constants.display_height - (
            new_y + new_height + self.outline_width
        )
        self.outline.width = new_width + (2 * self.outline_width)
        self.outline.height = new_height + (self.outline_width * 2)
        self.set_image(self.image_id)

    def set_image(self, new_image_id):
        """
        Description:
            Changes the image file reflected by this object
        Input:
            string new_image_id: File path to the new image used by this object
        Output:
            None
        """
        self.image_id = new_image_id
        if isinstance(self.image_id, str):  # If set to string image path
            self.contains_bundle = False
            full_image_id = f"graphics/{self.image_id}"
            if full_image_id in status.cached_images:
                self.image = status.cached_images[full_image_id]
            else:
                try:  # Use if there are any image path issues to help with file troubleshooting, shows the file location in which an image was expected
                    self.image = pygame.image.load(full_image_id)
                except:
                    print(full_image_id)
                    self.image = pygame.image.load(full_image_id)
                size = self.image.get_size()
                self.image = pygame.transform.scale(  # Decrease detail of each image before applying pixel mutations to speed processing
                    self.image,
                    (
                        math.floor(size[0] * constants.BUTTON_DETAIL_LEVEL),
                        math.floor(size[1] * constants.BUTTON_DETAIL_LEVEL),
                    ),
                )
                status.cached_images[full_image_id] = self.image
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        elif isinstance(new_image_id, pygame.Surface):
            self.image = new_image_id
            self.contains_bundle = False
        else:  # If set to image path list
            self.contains_bundle = True
            self.image = image_bundle(self, self.image_id)

    def draw(self):
        """
        Description:
            Draws this image if it should currently be visible at the coordinates of its button
        Input:
            None
        Output:
            None
        """
        if self.button.showing:
            self.x = self.button.x
            self.y = (
                constants.display_height - (self.button.y + self.height) + self.height
            )
            self.complete_draw()

    def draw_tooltip(self):
        """
        Description:
            Usually draws a tooltip when moused over. However, since buttons, unlike actors, manage their own tooltips, button images do not need any tooltip functionality
        Input:
            None
        Output:
            None
        """
        return ()

    def set_tooltip(self, tooltip_text):
        """
        Description:
            Usually sets an image's tooltip to the inputted list, with each item representing a line of the tooltip. However, since buttons, unlike actors, manage their own tooltips, button images do not need any tooltip functionality
        Input:
            string list tooltip_text: Lines for this image's tooltip
        Output:
            None
        """
        return ()


class collection_image(button_image):
    def draw(self):
        if self.button.showing:
            self.x = self.button.x
            self.y = constants.display_height + self.height - self.button.y
            self.complete_draw()


class tile_image(actor_image):
    """
    actor_image attached to a tile rather than an actor, causing it to use file paths directly rather than an dictionary of image keys and file path values
    """

    def __init__(self, actor, width, height, grid, image_description):
        """
        Description:
            Initializes this object
        Input:
            actor actor: actor to which this image is attached
            int width: Pixel width of this image
            int height: Pixel height of this image
            grid grid: actor's grid on which this image appears. Each of an actor's images appears on a different grid
            string image_description: Key in this image's actor's image_dict corresponding to the appearance that this image has. For example, a 'default' actor_image will show the actor's default appearance
        Output:
            None
        """
        super().__init__(actor, width, height, grid, image_description)
        self.go_to_cell((self.actor.x, self.actor.y))

    def go_to_cell(self, coordinates):
        """
        Description:
            Moves this image to the pixel coordinates corresponding to the inputted grid coordinates
        Input:
            int tuple coordinates: Two values representing x and y coordinates on this image's grid
        Output:
            None
        """
        self.x, self.y = self.grid.convert_coordinates(coordinates)
        self.Rect.x = self.x
        self.Rect.y = self.y - self.height
        self.outline.x = self.x - self.outline_width
        self.outline.y = self.y - (self.height + self.outline_width)

    def draw(self):
        """
        Description:
            Draws this image if it should currently be visible
        Input:
            None
        Output:
            None
        """
        if self.actor.name == "resource icon" and not self.actor.get_location().visible:
            return ()  # do not show if resource icon in undiscovered tile
        self.go_to_cell((self.actor.x, self.actor.y))
        self.complete_draw()
