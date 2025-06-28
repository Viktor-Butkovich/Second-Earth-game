# Contains functionality for dummies, which replicate other objects or act as models of hypothetical objects with fake attribute values and tooltips

from typing import Dict, Any
from modules.constructs.actor_types.mob_types import pmobs
from modules.constants import constants, status, flags


class dummy(pmobs.pmob):
    """
    Mock mob that can take any attribute values needed to get certain image or tooltip outputs without affecting rest of program
    """

    def __init__(self, input_dict):
        """
        input dict always includes dummy_type, which is generally equal to the init type of the unit being replicated?
        """
        self.default_permissions: Dict[str, Any] = {}
        self.override_permissions: Dict[str, Any] = {}
        for key in input_dict:
            setattr(self, key, input_dict[key])
        self.generate_button_portrait = input_dict.get(
            "generate_button_portrait", False
        )
        self.set_permission(constants.DUMMY_PERMISSION, True)
        if self.generate_button_portrait:
            self.image_dict = {
                constants.IMAGE_ID_LIST_FULL_MOB: self.unit_type.generate_center_recruitment_image(
                    self
                ),
            }
        else:
            if not self.image_dict:
                self.image_dict = self.unit_type.image_dict.copy()
            self.image_dict[constants.IMAGE_ID_LIST_FULL_MOB] = self.get_image_id_list()

    def set_permission(self, task: str, value: bool, *args, **kwargs):
        """
        Handles simple permission changes for dummy mobs, who don't use event subscriptions
        """
        previous_permission = self.get_permission(task)
        super().set_permission(task, value, *args, **kwargs)
        if previous_permission != value and not self.generate_button_portrait:
            self.update_image_bundle()  # Simplistic replacement for event bus
            self.update_habitability()

    def configure_event_subscriptions(self):
        """
        Dummy mobs don't need to receive DOM events, since they are not real and cannot be directly selected or modified after creation
        """
        return

    def publish_events(self, *args, **kwargs):
        """
        Dummy mobs don't need to publish DOM events, since they are not real and cannot be directly selected or modified after creation
        """
        return

    def update_image_bundle(self):
        """
        Dummy mobs may change their images after initial creation (e.g. dummy mob created, then effect of removing spacesuits
            simulated), but no data binding is required - just maintaining the image dict
        """
        self.image_dict[constants.IMAGE_ID_LIST_FULL_MOB] = self.get_image_id_list()
