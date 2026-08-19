# Contains functionality for workflows, which are a series of related tasks performed within a container

from __future__ import annotations
from modules.constants import constants, status, flags
from modules.interface_components import (
    buttons,
    containers,
    selectors,
    interface_elements,
)
from modules.util import scaling, main_loop_utility, actor_utility
from modules.constructs import building_types
from typing import Dict, List, Any
from abc import ABC, abstractmethod


class workflow(ABC):
    """
    Central configuration for a series of related tasks performed within a container, such as a building design or
        contract bid workflow.
    """

    def __init__(self) -> None:
        """
        Description:
            Initializes this object
        Input:
            Dict[str, Any] input_dict: Keys corresponding to the values needed to initialize this object
                string workflow_type: Workflow type key for this workflow
        Output:
            None
        """
        status.workflows[self.workflow_type] = self
        self.open_workflow_button: open_workflow_button = None
        self.current_container: workflow_container = None
        self.container_init_type: str = None

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
                "init_type": constants.OPEN_WORKFLOW_BUTTON,
                "image_id": "buttons/default_button.png",
                "workflow": self,
            }
        elif init_type == constants.WORKFLOW_CONTAINER:
            x_size, y_size = 0.4, 0.4
            return {
                "init_type": self.container_init_type,
                "coordinates": scaling.scaled_coordinates_percentage(
                    (1 - x_size) / 2,
                    (1 - y_size) / 2,
                ),
                "width": scaling.scale_width_percentage(x_size),
                "height": scaling.scale_height_percentage(y_size),
                "image_id": "buttons/default_button_frameless.png",
                "outline_width": 5,
                "modes": [constants.current_game_mode],
                "workflow": self,
                "outline_config": {
                    "outline_color": constants.color_dict["black"],
                    "outline_width": 5,
                },
            }
        else:
            return {}

    def populate_container(self) -> None:
        top_right_menu_button_size = 40
        top_right_menu_separation = 10
        central_menu_separation = 10
        self.current_container.top_right_menu = (
            constants.ActorCreationManager.create_interface_element(
                {
                    "init_type": constants.ORDERED_COLLECTION,
                    "coordinates": (
                        self.current_container.image.width
                        - scaling.scale_width(
                            top_right_menu_button_size + top_right_menu_separation
                        ),
                        self.current_container.image.height
                        - scaling.scale_height(
                            top_right_menu_button_size + top_right_menu_separation
                        ),
                    ),
                    "parent_collection": self.current_container,
                    "direction": "horizontal",
                    "reversed": True,  # Right-left
                    "separation": scaling.scale_width(top_right_menu_separation),
                }
            )
        )
        self.current_container.central_menu = (
            constants.ActorCreationManager.create_interface_element(
                {
                    "init_type": constants.ORDERED_COLLECTION,
                    "coordinates": (
                        self.current_container.image.width * 0.2,
                        self.current_container.image.height * 0.8,
                    ),
                    "parent_collection": self.current_container,
                    "direction": "vertical",
                    "reversed": False,  # Top-down
                    "separation": scaling.scale_height(central_menu_separation),
                }
            )
        )

        self.current_container.reposition_button = (
            constants.ActorCreationManager.create_interface_element(
                {
                    "init_type": constants.REPOSITION_CONTAINER_BUTTON,
                    "width": scaling.scale_width(top_right_menu_button_size),
                    "height": scaling.scale_height(top_right_menu_button_size),
                    "image_id": "buttons/reposition_button.png",
                    "parent_collection": self.current_container.top_right_menu,
                    "container": self.current_container,
                }
            )
        )
        self.current_container.close_workflow_button = (
            constants.ActorCreationManager.create_interface_element(
                {
                    "init_type": constants.CLOSE_WORKFLOW_BUTTON,
                    "width": scaling.scale_width(top_right_menu_button_size),
                    "height": scaling.scale_height(top_right_menu_button_size),
                    "image_id": "buttons/minimize_button.png",
                    "parent_collection": self.current_container.top_right_menu,
                    "workflow": self,
                }
            )
        )

    @property
    @abstractmethod
    def workflow_type(self) -> str:
        pass


class design_building_workflow(workflow):
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
        print(f"Selected building type: {selected_building_type.name}")
        raise Exception("Placeholder")

    def populate_container(self) -> None:
        super().populate_container()
        building_type_options = [
            selectors.dropdown_option(
                text=current_building_type.name,
                value=current_building_type,
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
                    "width": scaling.scale_width(100),
                    "height": scaling.scale_height(30),
                    "on_select": self.select_building_type,
                    "parent_collection": self.current_container.central_menu,
                    "image_id": "buttons/default_button.png",
                }
            )
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


class open_workflow_button(buttons.button):
    """
    Button configured by a workflow to open it when clicked
    """

    def __init__(self, input_dict: Dict[str, Any]) -> None:
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object. Same as superclass, except,
                workflow workflow: Workflow that this button is configured by, which this button opens
        Output:
            None
        """
        super().__init__(input_dict)
        self.workflow: workflow = input_dict["workflow"]
        self.workflow.open_workflow_button = self

    @property
    def tooltip_text(self) -> List[str]:
        """
        Provides the tooltip for this object
        """
        return [f"Opens {self.workflow.description}"]

    def on_click(self) -> None:
        """
        Controls this button's behavior when clicked. This button opens its attached workflow's container
        """
        if main_loop_utility.action_possible() and not status.displayed_container:
            constants.ActorCreationManager.create_interface_element(
                self.workflow.get_configuration(constants.WORKFLOW_CONTAINER)
            )


class close_workflow_button(buttons.button):
    """
    Button configured by a workflow to close it when clicked
    """

    def __init__(self, input_dict: Dict[str, Any]) -> None:
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object. Same as superclass, except,
                workflow workflow: Workflow that this button is configured by, which this button closes
        Output:
            None
        """
        super().__init__(input_dict)
        self.workflow: workflow = input_dict["workflow"]

    def on_click(self):
        """
        Controls this button's behavior when clicked. This button closes its attached workflow's container, and
            performs any required confirmation or cleanup steps
        """
        self.workflow.current_container.remove()

    @property
    def tooltip_text(self) -> List[str]:
        """
        Provides the tooltip for this object
        """
        return ["Click to close this panel"]


class workflow_container(containers.container):
    """
    Container attached to opening a workflow
    """

    def __init__(self, input_dict: Dict[str, Any]) -> None:
        """
        Description:
            Initializes this object
        Input:
            Dict[str, Any] input_dict: Keys corresponding to the values needed to initialize this object. Same as superclass, except,
                workflow workflow: Workflow that this container is attached to
        Output:
            None
        """
        super().__init__(input_dict)
        self.workflow: workflow = input_dict["workflow"]
        self.workflow.current_container = self
        self.top_right_menu: interface_elements.interface_collection = None
        self.central_menu: interface_elements.interface_collection = None
        self.reposition_button: containers.reposition_container_button = None
        self.close_workflow_button: close_workflow_button = None
        self.workflow.populate_container()

    def remove(self):
        """
        Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        """
        super().remove()
        self.workflow.current_container = None


class design_building_container(workflow_container):
    def __init__(self, input_dict: Dict[str, Any]) -> None:
        super().__init__(input_dict)
        self.design_building_selector: selectors.dropdown_selector = None
