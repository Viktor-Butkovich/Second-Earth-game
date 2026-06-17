from __future__ import annotations
from modules.constants import constants, status, flags
from modules.util import scaling


def config_minister_info_display() -> None:
    """
    Initializes minister selection interface
    """
    # minister info images setup
    minister_display_current_y = 0

    status.minister_info_display = (
        constants.ActorCreationManager.create_interface_element(
            {
                "coordinates": (5, -5),
                "width": 10,
                "height": 10,
                "modes": [constants.MINISTERS_MODE],
                "init_type": constants.ORDERED_COLLECTION,
                "is_info_display": True,
                "actor_type": constants.MINISTER_ACTOR_TYPE,
                "allow_minimize": False,
                "allow_move": False,
                "description": "minister information panel",
                "parent_collection": status.info_displays_collection,
            }
        )
    )

    minister_icon = constants.ActorCreationManager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(0, 0),
            "actor_type": constants.MINISTER_ACTOR_TYPE,
            "width": scaling.scale_width(constants.actor_icon_dimensions),
            "height": scaling.scale_height(constants.actor_icon_dimensions),
            "init_type": constants.ACTOR_ICON,
            "parent_collection": status.minister_info_display,
        }
    )

    minister_display_current_y -= 35
    # minister info images setup

    input_dict = {
        "coordinates": scaling.scale_coordinates(0, 0),
        "minimum_width": scaling.scale_width(10),
        "height": scaling.scale_height(constants.default_notification_font_size + 5),
        "image_id": "misc/default_label.png",
        "actor_type": constants.MINISTER_ACTOR_TYPE,
        "init_type": constants.ACTOR_DISPLAY_LABEL,
        "parent_collection": status.minister_info_display,
    }

    # minister info labels setup
    for current_actor_label_type in [
        constants.MINISTER_OFFICE_LABEL,
        constants.MINISTER_NAME_LABEL,
        constants.MINISTER_ETHNICITY_LABEL,
        constants.MINISTER_BACKGROUND_LABEL,
        constants.MINISTER_SOCIAL_STATUS_LABEL,
        constants.MINISTER_INTERESTS_LABEL,
        constants.MINISTER_LOYALTY_LABEL,
        constants.MINISTER_ABILITY_LABEL,
        constants.CURRENT_SKILL_LABEL,
        constants.EVIDENCE_LABEL,
    ]:
        if current_actor_label_type in [
            constants.CURRENT_SKILL_LABEL,
            constants.MINISTER_SOCIAL_STATUS_LABEL,
        ]:
            x_displacement = 50
        elif current_actor_label_type != constants.MINISTER_OFFICE_LABEL:
            x_displacement = 25
        else:
            x_displacement = 0
        input_dict["member_config"] = {"order_x_offset": x_displacement}
        input_dict["init_type"] = current_actor_label_type

        if current_actor_label_type == constants.CURRENT_SKILL_LABEL:
            input_dict["list_type"] = "skill types"
            for i in range(len(status.minister_types)):
                input_dict["list_index"] = i
                constants.ActorCreationManager.create_interface_element(input_dict)
        else:
            constants.ActorCreationManager.create_interface_element(input_dict)
    # minister info labels setup
