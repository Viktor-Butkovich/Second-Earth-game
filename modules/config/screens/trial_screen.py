from __future__ import annotations
from modules.constants import constants, status, flags
from modules.util import scaling


def config_trial_screen() -> None:
    """
    Initializes static interface of trial screen
    """
    trial_display_default_y = 700
    button_separation = 100
    distance_to_center = 300
    distance_to_notification = 100

    defense_y = trial_display_default_y
    defense_x = (
        (constants.default_display_width / 2)
        + (distance_to_center - button_separation)
        + distance_to_notification
    )
    status.defense_info_display = (
        constants.ActorCreationManager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(defense_x, defense_y),
                "width": 10,
                "height": 10,
                "modes": [constants.TRIAL_MODE],
                "init_type": constants.ORDERED_COLLECTION,
                "is_info_display": True,
                "actor_type": constants.DEFENSE_ACTOR_TYPE,
                "allow_minimize": False,
                "allow_move": False,
                "description": "defense information panel",
            }
        )
    )

    defense_portrait_image = constants.ActorCreationManager.create_interface_element(
        {
            "width": scaling.scale_width(button_separation * 2 - 5),
            "height": scaling.scale_height(button_separation * 2 - 5),
            "init_type": constants.ACTOR_ICON,
            "actor_type": constants.MINISTER_ACTOR_TYPE,
            "parent_collection": status.defense_info_display,
        }
    )

    input_dict = {
        "minimum_width": scaling.scale_width(10),
        "height": scaling.scale_height(constants.default_notification_font_size + 5),
        "image_id": "misc/default_label.png",
        "message": "Defense",
        "init_type": constants.LABEL,
        "parent_collection": status.defense_info_display,
    }
    defense_label = constants.ActorCreationManager.create_interface_element(input_dict)

    input_dict["actor_type"] = "minister"
    del input_dict["message"]
    for current_actor_label_type in [
        constants.MINISTER_NAME_LABEL,
        constants.MINISTER_OFFICE_LABEL,
        constants.EVIDENCE_LABEL,
    ]:
        input_dict["init_type"] = current_actor_label_type
        constants.ActorCreationManager.create_interface_element(input_dict)

    prosecution_y = trial_display_default_y
    prosecution_x = (
        (constants.default_display_width / 2)
        - (distance_to_center + button_separation)
        - distance_to_notification
    )
    status.prosecution_info_display = (
        constants.ActorCreationManager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(prosecution_x, prosecution_y),
                "width": 10,
                "height": 10,
                "modes": [constants.TRIAL_MODE],
                "init_type": constants.ORDERED_COLLECTION,
                "is_info_display": True,
                "actor_type": constants.PROSECUTION_ACTOR_TYPE,
                "allow_minimize": False,
                "allow_move": False,
                "description": "prosecution information panel",
            }
        )
    )

    prosecution_portrait_image = (
        constants.ActorCreationManager.create_interface_element(
            {
                "width": scaling.scale_width(button_separation * 2 - 5),
                "height": scaling.scale_height(button_separation * 2 - 5),
                "init_type": constants.ACTOR_ICON,
                "actor_type": constants.MINISTER_ACTOR_TYPE,
                "parent_collection": status.prosecution_info_display,
            }
        )
    )

    input_dict = {
        "minimum_width": scaling.scale_width(10),
        "height": scaling.scale_height(constants.default_notification_font_size + 5),
        "image_id": "misc/default_label.png",
        "message": "Prosecution",
        "init_type": constants.LABEL,
        "parent_collection": status.prosecution_info_display,
    }
    prosecution_label = constants.ActorCreationManager.create_interface_element(
        input_dict
    )

    input_dict["actor_type"] = "minister"
    del input_dict["message"]
    input_dict["parent_collection"] = status.prosecution_info_display
    for current_actor_label_type in [
        constants.MINISTER_NAME_LABEL,
        constants.MINISTER_OFFICE_LABEL,
    ]:
        input_dict["init_type"] = current_actor_label_type
        constants.ActorCreationManager.create_interface_element(input_dict)

    bribed_judge_indicator = constants.ActorCreationManager.create_interface_element(
        {
            "image_id": "misc/bribed_judge.png",
            "coordinates": scaling.scale_coordinates(
                (constants.default_display_width / 2)
                - ((button_separation * 2 - 5) / 2),
                trial_display_default_y,
            ),
            "width": scaling.scale_width(button_separation * 2 - 5),
            "height": scaling.scale_height(button_separation * 2 - 5),
            "modes": [constants.TRIAL_MODE],
            "indicator_type": "prosecution_bribed_judge",
            "init_type": constants.INDICATOR_IMAGE,
        }
    )

    non_bribed_judge_indicator = (
        constants.ActorCreationManager.create_interface_element(
            {
                "image_id": "misc/non_bribed_judge.png",
                "coordinates": scaling.scale_coordinates(
                    (constants.default_display_width / 2)
                    - ((button_separation * 2 - 5) / 2),
                    trial_display_default_y,
                ),
                "width": scaling.scale_width(button_separation * 2 - 5),
                "height": scaling.scale_height(button_separation * 2 - 5),
                "modes": [constants.TRIAL_MODE],
                "indicator_type": "not prosecution_bribed_judge",
                "init_type": constants.INDICATOR_IMAGE,
            }
        )
    )
