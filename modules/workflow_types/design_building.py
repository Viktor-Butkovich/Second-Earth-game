from __future__ import annotations
from modules.constants import constants, status, flags
from modules.interface_components import selectors
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
        return

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
                }
            )
        )

        constants.ActorCreationManager.create_interface_element(
            {
                "init_type": constants.ITEM_COUNT_INDICATOR,
                "item_count": 4.5,
                "item_type": status.item_types[constants.MATERIAL_BASE_METALS],
                "width": scaling.scale_width(100),
                "height": scaling.scale_height(50),
                "parent_collection": self.current_container.central_menu,
            }
        )
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
        super().__init__(input_dict)
        self.building_type_selector: selectors.dropdown_selector = None
