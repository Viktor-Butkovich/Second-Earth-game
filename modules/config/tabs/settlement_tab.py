from __future__ import annotations
from modules.constants import constants, status, flags
from modules.util import scaling, actor_utility


def config_settlement_tab():
    """
    Initializes the settlement interface as part of the location tabbed collection
    """
    status.settlement_collection = (
        constants.ActorCreationManager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(0, 0),
                "width": scaling.scale_width(0),
                "height": scaling.scale_height(0),
                "init_type": constants.ORDERED_COLLECTION,
                "parent_collection": status.location_tabbed_collection,
                "member_config": {
                    "tabbed": True,
                    "button_image_id": actor_utility.generate_frame(
                        "buttons/grid_line_button.png"
                    ),
                    "identifier": constants.SETTLEMENT_PANEL,
                    "tab_name": "settlement",
                },
            }
        )
    )
    for current_actor_label_type in [
        constants.SETTLEMENT,
        # constants.INFRASTRUCTURE,
    ]:
        # if current_actor_label_type in [
        #    constants.SETTLEMENT,
        #    constants.INFRASTRUCTURE,
        # ]:  # Left align any top-level buildings
        #    x_displacement = 0
        # elif current_actor_label_type == constants.CURRENT_BUILDING_WORK_CREW_LABEL:
        #    x_displacement = 75
        # elif current_actor_label_type in [
        #    constants.BUILDING_EFFICIENCY_LABEL,
        #    constants.BUILDING_WORK_CREWS_LABEL,
        # ]:
        #    x_displacement = 50
        # else:
        #    x_displacement = 25
        x_displacement = 0
        input_dict = {
            "minimum_width": scaling.scale_width(10),
            "height": scaling.scale_height(
                constants.default_notification_font_size + 5
            ),
            "image_id": "misc/default_label.png",
            "actor_type": constants.LOCATION_ACTOR_TYPE,
            "parent_collection": status.settlement_collection,
            "member_config": {"order_x_offset": scaling.scale_width(x_displacement)},
        }

        """
        if current_actor_label_type == constants.BUILDING_EFFICIENCY_LABEL:
            input_dict["init_type"] = constants.BUILDING_EFFICIENCY_LABEL
            input_dict["building_type"] = constants.RESOURCE
            constants.ActorCreationManager.create_interface_element(input_dict)
        elif current_actor_label_type == constants.BUILDING_WORK_CREWS_LABEL:
            input_dict["init_type"] = constants.BUILDING_WORK_CREWS_LABEL
            input_dict["building_type"] = constants.RESOURCE
            constants.ActorCreationManager.create_interface_element(input_dict)
        elif current_actor_label_type == constants.CURRENT_BUILDING_WORK_CREW_LABEL:
            input_dict["init_type"] = constants.LIST_ITEM_LABEL
            input_dict["list_type"] = constants.RESOURCE
            for i in range(0, 3):
                input_dict["list_index"] = i
                constants.ActorCreationManager.create_interface_element(input_dict)
        else:
        """
        input_dict["init_type"] = current_actor_label_type
        constants.ActorCreationManager.create_interface_element(input_dict)
