# Contains functionality for workflows, which are a series of related tasks performed within a container

from __future__ import annotations
from modules.constants import constants, status, flags
from modules.interface_components import buttons, containers
from modules.util import scaling, main_loop_utility, actor_utility
from typing import Dict, List, Any
from abc import ABC, abstractmethod


class workflow(ABC):
    """
    Central configuration for a series of related tasks performed within a container, such as a building design or
        contract bid workflow.
    """

    def __init__(self, input_dict: Dict[str, Any]) -> None:
        """
        Description:
            Initializes this object
        Input:
            Dict[str, Any] input_dict: Keys corresponding to the values needed to initialize this object
                string workflow_type: Workflow type key for this workflow
        Output:
            None
        """
        self.workflow_type: str = input_dict["workflow_type"]
        status.workflows[self.workflow_type] = self
        self.open_workflow_button: buttons.open_workflow_button = None
        self.current_container: containers.container = None

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
        elif init_type == constants.CLOSE_WORKFLOW_BUTTON:
            button_size = 20
            return {
                "coordinates": (
                    self.current_container.image.width
                    - scaling.scale_width(button_size + 5),
                    self.current_container.image.height
                    - scaling.scale_height(button_size + 5),
                ),
                "width": scaling.scale_width(button_size),
                "height": scaling.scale_height(button_size),
                "parent_collection": self.current_container,
                "init_type": constants.CLOSE_WORKFLOW_BUTTON,
                "image_id": "buttons/minimize_button.png",
            }
        elif init_type == constants.WORKFLOW_CONTAINER:
            x_size, y_size = 0.4, 0.4
            return {
                "init_type": constants.WORKFLOW_CONTAINER,
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


class design_building_workflow(workflow):
    """
    Workflow for designing a building to be constructed at a zone
    """
    def __init__(self):
        """
        Description:
            Initializes this object
        Input:
            Dict[str, Any] input_dict: Keys corresponding to the values needed to initialize this object
                string workflow_type: Workflow type key for this workflow
        Output:
            None
        """
        input_dict = {
            "workflow_type": constants.DESIGN_BUILDING_WORKFLOW,
        }
        super().__init__(input_dict)
        self.description: str = "building design panel"

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
    def on_click(self):
        """
        Controls this button's behavior when clicked. This button closes its attached workflow's container, and
            performs any required confirmation or cleanup steps
        """
        self.parent_collection.remove()

    @property
    def tooltip_text(self) -> List[str]:
        """
        Provides the tooltip for this object
        """
        return ["Close container"]
