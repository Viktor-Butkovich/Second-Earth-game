from __future__ import annotations
from modules.constants import constants, status, flags
from modules.util import scaling
from modules.managers import value_tracker


def config_value_trackers() -> None:
    """
    Defines important global values and initializes associated tracker labels
    """
    value_trackers_ordered_collection = (
        constants.ActorCreationManager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(
                    250, constants.default_display_height - 5
                ),
                "width": scaling.scale_width(0),
                "height": scaling.scale_height(0),
                "modes": [
                    constants.STRATEGIC_MODE,
                    constants.EARTH_MODE,
                    constants.MINISTERS_MODE,
                    constants.TRIAL_MODE,
                    constants.MAIN_MENU_MODE,
                    constants.NEW_GAME_SETUP_MODE,
                    constants.LOCATION_MODE,
                ],
                "init_type": constants.ORDERED_COLLECTION,
            }
        )
    )

    constants.TurnTracker = value_tracker.value_tracker(
        value_key="turn", initial_value=0, min_value=None, max_value=None
    )
    constants.ActorCreationManager.create_interface_element(
        {
            "minimum_width": scaling.scale_width(10),
            "height": scaling.scale_height(
                constants.default_notification_font_size + 5
            ),
            "modes": [
                constants.STRATEGIC_MODE,
                constants.EARTH_MODE,
                constants.MINISTERS_MODE,
                constants.TRIAL_MODE,
                constants.LOCATION_MODE,
            ],
            "image_id": "misc/default_label.png",
            "value_name": "turn",
            "init_type": constants.VALUE_LABEL,
            "parent_collection": value_trackers_ordered_collection,
            "member_config": {
                "order_x_offset": scaling.scale_width(315),
                "order_overlap": True,
            },
        }
    )

    constants.MoneyTracker = value_tracker.money_tracker(100)
    constants.MoneyLabel = constants.ActorCreationManager.create_interface_element(
        {
            "minimum_width": scaling.scale_width(10),
            "height": scaling.scale_height(
                constants.default_notification_font_size + 5
            ),
            "modes": [
                constants.STRATEGIC_MODE,
                constants.EARTH_MODE,
                constants.MINISTERS_MODE,
                constants.TRIAL_MODE,
                constants.LOCATION_MODE,
            ],
            "image_id": "misc/default_label.png",
            "init_type": constants.MONEY_LABEL,
            "parent_collection": value_trackers_ordered_collection,
            "member_config": {
                "index": 1
            },  # should appear before public opinion in collection but relies on public opinion existing
        }
    )

    constants.PublicOpinionTracker = value_tracker.public_opinion_tracker(
        value_key="public_opinion", initial_value=0, min_value=0, max_value=100
    )
    constants.ActorCreationManager.create_interface_element(
        {
            "minimum_width": scaling.scale_width(10),
            "height": scaling.scale_height(
                constants.default_notification_font_size + 5
            ),
            "modes": [
                constants.STRATEGIC_MODE,
                constants.EARTH_MODE,
                constants.MINISTERS_MODE,
                constants.TRIAL_MODE,
                constants.LOCATION_MODE,
            ],
            "image_id": "misc/default_label.png",
            "value_name": "public_opinion",
            "init_type": constants.VALUE_LABEL,
            "parent_collection": value_trackers_ordered_collection,
        }
    )

    if constants.EffectManager.effect_active("track_fps"):
        constants.FpsTracker = value_tracker.value_tracker(
            value_key="fps", initial_value=0, min_value=0, max_value=None
        )
        constants.ActorCreationManager.create_interface_element(
            {
                "minimum_width": scaling.scale_width(10),
                "height": scaling.scale_height(
                    constants.default_notification_font_size + 5
                ),
                "modes": [
                    constants.STRATEGIC_MODE,
                    constants.EARTH_MODE,
                    constants.MINISTERS_MODE,
                    constants.TRIAL_MODE,
                    constants.MAIN_MENU_MODE,
                    constants.NEW_GAME_SETUP_MODE,
                    constants.LOCATION_MODE,
                ],
                "image_id": "misc/default_label.png",
                "value_name": "fps",
                "init_type": constants.VALUE_LABEL,
                "parent_collection": value_trackers_ordered_collection,
            }
        )

    if constants.EffectManager.effect_active("track_cached_image_memory"):
        constants.ImageCacheTracker = value_tracker.value_tracker(
            value_key="image_cache", initial_value=0, min_value=0, max_value=None
        )
        constants.ActorCreationManager.create_interface_element(
            {
                "minimum_width": scaling.scale_width(10),
                "height": scaling.scale_height(
                    constants.default_notification_font_size + 5
                ),
                "modes": [
                    constants.STRATEGIC_MODE,
                    constants.EARTH_MODE,
                    constants.MINISTERS_MODE,
                    constants.TRIAL_MODE,
                    constants.MAIN_MENU_MODE,
                    constants.NEW_GAME_SETUP_MODE,
                    constants.LOCATION_MODE,
                ],
                "image_id": "misc/default_label.png",
                "value_name": "image_cache",
                "unit": "MB",
                "init_type": constants.VALUE_LABEL,
                "parent_collection": value_trackers_ordered_collection,
            }
        )

    if constants.EffectManager.effect_active("track_mouse_position"):
        constants.mouse_position_tracker = value_tracker.value_tracker(
            value_key="mouse_position",
            initial_value=(0, 0),
            min_value=None,
            max_value=None,
        )
        constants.ActorCreationManager.create_interface_element(
            {
                "minimum_width": scaling.scale_width(10),
                "height": scaling.scale_height(
                    constants.default_notification_font_size + 5
                ),
                "modes": [
                    constants.STRATEGIC_MODE,
                    constants.EARTH_MODE,
                    constants.MINISTERS_MODE,
                    constants.TRIAL_MODE,
                    constants.MAIN_MENU_MODE,
                    constants.NEW_GAME_SETUP_MODE,
                    constants.LOCATION_MODE,
                ],
                "image_id": "misc/default_label.png",
                "value_name": "mouse_position",
                "init_type": constants.VALUE_LABEL,
                "parent_collection": value_trackers_ordered_collection,
            }
        )

    constants.ActorCreationManager.create_interface_element(
        {
            "coordinates": scaling.scale_coordinates(
                225, constants.default_display_height - 35
            ),
            "width": scaling.scale_width(30),
            "height": scaling.scale_height(30),
            "modes": [
                constants.STRATEGIC_MODE,
                constants.EARTH_MODE,
                constants.MINISTERS_MODE,
                constants.TRIAL_MODE,
                constants.LOCATION_MODE,
            ],
            "image_id": "buttons/instructions.png",
            "init_type": constants.SHOW_PREVIOUS_REPORTS_BUTTON,
        }
    )

    constants.EvilTracker = value_tracker.value_tracker("evil", 0, 0, 100)

    constants.FearTracker = value_tracker.value_tracker("fear", 1, 1, 6)
