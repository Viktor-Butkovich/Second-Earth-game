from __future__ import annotations
from modules.constants import constants, status, flags
from modules.interface_components import selectors, interface_elements, labels
from modules.workflow_types import workflows
from modules.util import scaling, actor_utility
from modules.constructs import building_types
from typing import Dict, Any


class design_building_workflow(workflows.workflow):
    """
    Workflow for designing a building to be constructed at a zone
    """

    def __init__(self):
        """
        Initializes this object
        """
        super().__init__()
        self.container_init_type: str = constants.DESIGN_BUILDING_CONTAINER
        self.description: str = "building design panel"
        self.current_container: design_building_container = None

    @property
    def workflow_type(self) -> str:
        return constants.DESIGN_BUILDING_WORKFLOW

    def get_configuration(self, init_type: str) -> Dict[str, Any]:
        """
        Description:
            Returns an input_dict configuration dictionary for an init_type associated with this workflow
        Input:
            str init_type: Type of interface element to be created for this workflow
        Output:
            Dict[str, Any]: Configuration dictionary for the requested init_type
        """
        if init_type == constants.OPEN_WORKFLOW_BUTTON:
            return {
                **super().get_configuration(init_type),
                "image_id": actor_utility.generate_frame(
                    "buttons/actions/design_building.png"
                ),
            }
        else:
            return super().get_configuration(init_type)

    def select_building_type(
        self, selected_building_type: building_types.building_type
    ) -> None:
        if self.current_container.total_cost_collection:
            self.current_container.total_cost_collection.clear()
            total_cost = selected_building_type.cost_per_attempt.multiply(
                selected_building_type.required_successes
            )
            for material_key, material_amount in total_cost.enumerate().items():
                constants.ActorCreationManager.create_interface_element(
                    {
                        "init_type": constants.ITEM_COUNT_INDICATOR,
                        "item_count": material_amount,
                        "item_type": status.item_types[material_key],
                        "width": self.current_container.total_cost_collection.height
                        * 2,
                        "height": self.current_container.total_cost_collection.height,
                        "parent_collection": self.current_container.total_cost_collection,
                    }
                )
        if self.current_container.successes_required_label:
            self.current_container.successes_required_label.set_label(
                f"Successes Required: {selected_building_type.required_successes}"
            )

    def populate_container(self) -> None:
        super().populate_container()
        building_type_options = [
            selectors.dropdown_option(
                option_text=current_building_type.name,
                option=current_building_type,
                tooltip_text=[
                    [f"Build a {current_building_type.name} in this zone"],
                    current_building_type.description,
                ],
            )
            for current_building_type in status.building_types.values()
        ]
        self.current_container.building_type_selector = (
            constants.ActorCreationManager.create_interface_element(
                {
                    "init_type": constants.DROPDOWN_SELECTOR,
                    "dropdown_options": building_type_options,
                    "prefix": "Building Type: ",
                    "width": scaling.scale_width(120),
                    "height": scaling.scale_height(30),
                    "on_select": self.select_building_type,
                    "parent_collection": self.current_container.central_menu,
                    "delay_finish_init": True,
                }
            )
        )
        total_cost_label: labels.label = (
            constants.ActorCreationManager.create_interface_element(
                {
                    "init_type": constants.LABEL,
                    "message": "Total Cost: ",
                    "parent_collection": self.current_container.central_menu,
                    "height": scaling.scale_height(30),
                    "minimum_width": scaling.scale_width(10),
                    "image_id": "misc/empty.png",
                    "enable_tooltip": False,
                }
            )
        )

        self.current_container.total_cost_collection = (
            constants.ActorCreationManager.create_interface_element(
                {
                    "init_type": constants.ORDERED_COLLECTION,
                    "parent_collection": self.current_container.central_menu,
                    "direction": "horizontal",
                    "height": scaling.scale_height(50),  # Height used by members
                    "separation": scaling.scale_width(15),
                    "member_config": {
                        "order_y_offset": scaling.scale_height(10),
                    },
                }
            )
        )
        self.current_container.successes_required_label = (
            constants.ActorCreationManager.create_interface_element(
                {
                    "init_type": constants.LABEL,
                    "message": "",  # Set when building type is selected
                    "parent_collection": self.current_container.central_menu,
                    "height": scaling.scale_height(30),
                    "minimum_width": scaling.scale_width(10),
                    "image_id": "misc/empty.png",
                    "enable_tooltip": False,
                }
            )
        )

        # Must run after total cost collection and successes required inits
        self.current_container.building_type_selector.finish_init()

        # Rethink how to handle the container population process. Should there be a workflow container subclass for each workflow type, where the subclass defines its own interface?
        # This allows easy attribute references and cleanup, but splits the interface creation logic between workflow
        # and container. Alternatively, the workflow could define a populate_container method that returns a list of
        # interface elements to be created, which the container then creates. This keeps the interface creation
        # logic in one place, but requires passing references to the container and workflow around.
        # If we use subclasses, we need to consider the init types to create the different container types...

        """
        Solution: A workflow subclass' get_configuration will use the correct init_type for the workflow container
            subclass for that workflow type. This is a lite subclass that just defines its different interface
            components as None. The actual workflow subclass should define and initialize all the components in the
            container as needed, handle workflow logic, etc.
        As such, the workflow container class likely doesn't even need to define top right menu and reposition/close
            buttons - these can be treated as generic components created in the workflow superclass.
        The container should only be responsible for holding the interface elements and being their parent
            collection, such that closing it deletes all of them, while the workflow should handle all "business"
            logic and interface layout.
        """


class design_building_container(workflows.workflow_container):
    def __init__(self, input_dict: Dict[str, Any]) -> None:
        self.building_type_selector: selectors.dropdown_selector = None
        self.total_cost_collection: interface_elements.ordered_collection = None
        self.successes_required_label: labels.label = None
        super().__init__(input_dict)
