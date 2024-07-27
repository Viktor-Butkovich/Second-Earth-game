# Contains functionality for actor display images

from ..constructs.images import free_image
from ..util import action_utility
import modules.constants.constants as constants
import modules.constants.status as status


class actor_display_free_image(free_image):
    """
    Free image that changes its appearance to match selected mobs or tiles
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates' = (0, 0): int tuple value - Two values representing x and y coordinates for the pixel location of this image
                'width': int value - Pixel width of this image
                'height': int value - Pixel height of this image
                'modes': string list value - Game modes during which this button can appear
                'to_front' = False: boolean value - If True, allows this image to appear in front of most other objects instead of being behind them
                'actor_image_type': string value - subtype of actor image, like 'minister_default' or 'possible_artifact_location'
                'default_image_id' = 'none': string value - Image to use if not calibrated to any actor, such as for reorganization placeholder images
        Output:
            None
        """
        self.actor_image_type = input_dict["actor_image_type"]
        self.actor = "none"
        self.default_image_id = input_dict.get("default_image_id", "none")
        input_dict["image_id"] = "misc/empty.png"
        super().__init__(input_dict)

    def calibrate(self, new_actor):
        """
        Description:
            Sets this image to match the inputted object's appearance to show in the actor info display
        Input:
            string/actor new_actor: If this equals 'none', hides this image. Otherwise, causes this image will match this input's appearance
        Output:
            None
        """
        self.actor = new_actor
        if new_actor != "none":
            if self.actor_image_type in ["minister_default"]:
                self.set_image(new_actor.image_id)
            elif self.actor_image_type in ["inventory_default"]:
                self.set_image(new_actor.image.image_id)
            else:
                image_id_list = []
                default_image_key = "default"

                if (
                    new_actor.actor_type != "mob"
                    and not new_actor.cell.terrain_handler.visible
                ):
                    default_image_key = "hidden"
                if isinstance(
                    new_actor.images[0].image_id, str
                ):  # if id is string image path
                    image_id_list.append(new_actor.image_dict[default_image_key])
                else:  # if id is list of strings for image bundle
                    image_id_list += new_actor.get_image_id_list()
                if new_actor.actor_type == "mob":
                    image_id_list.append(
                        action_utility.generate_background_image_input_dict()
                    )
                    if new_actor.is_dummy:
                        image_id_list.append(
                            {
                                "image_id": "misc/dark_shader.png",
                                "level": constants.FRONT_LEVEL,
                            }
                        )
                    if new_actor.is_pmob:
                        image_id_list.append("misc/pmob_outline.png")
                    else:
                        image_id_list.append("misc/npmob_outline.png")
                else:
                    image_id_list.append("misc/tile_outline.png")
                self.set_image(image_id_list)
        else:
            image_id_list = ["misc/mob_background.png"]
            if self.default_image_id != "none":
                if type(self.default_image_id) == str:
                    image_id_list.append(self.default_image_id)
                else:
                    image_id_list += self.default_image_id
                image_id_list.append(
                    {"image_id": "misc/dark_shader.png", "level": constants.FRONT_LEVEL}
                )
            image_id_list.append("misc/pmob_outline.png")
            self.set_image(image_id_list)


class mob_background_image(free_image):
    """
    Image appearing behind the displayed actor in the actor info display
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
        self.actor = "none"

    def calibrate(self, new_actor):
        """
        Description:
            Updates which actor is in front of this image
        Input:
            string/actor new_actor: The displayed actor that goes in front of this image. If this equals 'none', there is no actor in front of it
        Output:
            None
        """
        self.actor = new_actor
        self.update_image_bundle()

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this image should be drawn
        Input:
            None
        Output:
            boolean: False if there is no actor in the info display, otherwise returns same value as superclass
        """
        if self.actor == "none":
            return False
        if self.image_id == "misc/pmob_background.png" and not self.actor.is_pmob:
            return False
        if self.image_id == "misc/npmob_background.png" and not self.actor.is_npmob:
            return False
        else:
            return super().can_show(skip_parent_collection=skip_parent_collection)

    def update_tooltip(self):
        """
        Description:
            Sets this image's tooltip to that of the actor in front of it
        Input:
            None
        Output:
            None
        """
        if not self.actor == "none":
            tooltip_text = self.actor.tooltip_text
            self.set_tooltip(tooltip_text)
        else:
            super().update_tooltip()


class minister_background_image(mob_background_image):
    """
    Image that appears behind a minister and changes to match their current office
    """

    def get_image_id_list(self, force_visibility=False):
        """
        Description:
            Generates and returns a list this actor's image file paths and dictionaries that can be passed to any image object to display those images together in a particular order and
                orientation
        Input:
            None
        Output:
            list: Returns list of string image file paths, possibly combined with string key dictionaries with extra information for offset images
        """
        image_id_list = []
        if not self.actor == "none":
            if self.actor.current_position == "none":
                image_id_list.append("misc/mob_background.png")
            else:
                image_id_list.append(
                    "ministers/icons/"
                    + constants.minister_type_dict[self.actor.current_position]
                    + ".png"
                )
            if self.actor.just_removed and self.actor.current_position == "none":
                image_id_list.append(
                    {"image_id": "misc/warning_icon.png", "x_offset": 0.75}
                )
        return image_id_list


class label_image(free_image):
    """
    Free image that is attached to a label and will only show when the label is showing
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates' = (0, 0): int tuple value - Two values representing x and y coordinates for the pixel location of this image
                'width': int value - Pixel width of this image
                'height': int value - Pixel height of this image
                'modes': string list value - Game modes during which this button can appear
                'to_front' = False: boolean value - If True, allows this image to appear in front of most other objects instead of being behind them
                'attached_label': label value - Label attached to this image
        Output:
            None
        """
        self.attached_label = input_dict["attached_label"]
        input_dict["image_id"] = "misc/empty.png"
        super().__init__(input_dict)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this image should be drawn
        Input:
            None
        Output:
            boolean: False if this image's label is not showing, otherwise returns same value as superclass
        """
        if self.attached_label.can_show(skip_parent_collection=skip_parent_collection):
            return super().can_show(skip_parent_collection=skip_parent_collection)
        else:
            return False
