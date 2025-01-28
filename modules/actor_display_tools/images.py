# Contains functionality for actor display images

from modules.constructs.images import free_image
from modules.util import action_utility
from modules.constants import constants, status, flags


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
                'actor_image_type': string value - subtype of actor image, like 'default' or 'possible_artifact_location'
                'default_image_id' = None: string value - Image to use if not calibrated to any actor, such as for reorganization placeholder images
        Output:
            None
        """
        self.actor_image_type = input_dict["actor_image_type"]
        self.actor = None
        self.default_image_id = input_dict.get("default_image_id", None)
        input_dict["image_id"] = "misc/empty.png"
        super().__init__(input_dict)

    def calibrate(self, new_actor):
        """
        Description:
            Sets this image to match the inputted object's appearance to show in the actor info display
        Input:
            string/actor new_actor: If this equals None, hides this image. Otherwise, causes this image will match this input's appearance
        Output:
            None
        """
        self.actor = new_actor
        if new_actor:
            if self.actor_image_type in ["inventory_default"]:
                self.set_image(new_actor.image.image_id)
            else:
                image_id_list = action_utility.generate_background_image_id_list(
                    new_actor
                )
                default_image_key = "default"

                if (
                    new_actor.actor_type == constants.TILE_ACTOR_TYPE
                    and not new_actor.cell.terrain_handler.visible
                ):
                    default_image_key = "hidden"
                if new_actor.actor_type in [
                    constants.MOB_ACTOR_TYPE,
                    constants.TILE_ACTOR_TYPE,
                ] and isinstance(
                    new_actor.images[0].image_id, str
                ):  # if id is string image path
                    image_id_list.append(new_actor.image_dict[default_image_key])
                else:  # if id is list of strings for image bundle
                    image_id_list += new_actor.get_image_id_list()
                if new_actor.actor_type == constants.MOB_ACTOR_TYPE:
                    if new_actor.get_permission(constants.DUMMY_PERMISSION):
                        image_id_list.append(
                            {
                                "image_id": "misc/dark_shader.png",
                                "level": constants.FRONT_LEVEL,
                            }
                        )
                    if new_actor.get_permission(constants.PMOB_PERMISSION):
                        image_id_list.append(
                            {
                                "image_id": "misc/actor_backgrounds/pmob_outline.png",
                                "detail_level": 1.0,
                            }
                        )
                    else:
                        image_id_list.append(
                            {
                                "image_id": "misc/actor_backgrounds/npmob_outline.png",
                                "detail_level": 1.0,
                            }
                        )
                else:
                    image_id_list.append(
                        {
                            "image_id": "misc/tile_outline.png",
                            "detail_level": 1.0,
                        }
                    )
                self.set_image(image_id_list)
        else:
            image_id_list = action_utility.generate_background_image_id_list()
            if self.default_image_id:
                if type(self.default_image_id) == str:
                    image_id_list.append(self.default_image_id)
                else:
                    image_id_list += self.default_image_id
                image_id_list.append(
                    {"image_id": "misc/dark_shader.png", "level": constants.FRONT_LEVEL}
                )
            image_id_list.append(
                {
                    "image_id": "misc/actor_backgrounds/pmob_outline.png",
                    "detail_level": 1.0,
                }
            )
            self.set_image(image_id_list)


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
