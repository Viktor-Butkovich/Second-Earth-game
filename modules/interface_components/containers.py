# Contains functionality for interface containers

from __future__ import annotations
import pygame
from modules.interface_components import interface_elements, buttons
from modules.workflow_types import workflows
from modules.util import scaling
from modules.constants import constants, status, flags
from typing import List, Dict, Any


class container(interface_elements.interface_collection):
    """
    Interface collection which is dynamically created and removed, contains a variety of interface, includes an intrinsic
        image with tooltip and boundaries, and can be moved around the screen
    """

    def __init__(self, input_dict: Dict[str, Any]) -> None:
        """
        Description:
            Initializes this object
        Input:
            Dict[str, Any] input_dict: Keys corresponding to the values needed to initialize this object. Same as superclass, except,
                'image_id': image ID value - Image to display for this container directly
                'outline_config' = None: Dict[str, Any] value -
                    string outline_color: Color key for the outline of this container
                    int outline_width: Width of the outline of this container
        Output:
            None
        """
        super().__init__(input_dict)
        self.create_image(input_dict["image_id"])
        status.displayed_container = self
        self.outline_config: Dict[str, Any] = input_dict.get("outline_config", None)
        self.has_outline: bool = bool(self.outline_config)
        if self.has_outline:
            assert "outline_color" in self.outline_config
            assert "outline_width" in self.outline_config
        self.draw_priority: int = constants.DRAW_PRIORITY_CONTAINER

    def remove(self):
        """
        Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        """
        super().remove()
        self.image.remove()
        status.displayed_container = None

    def touching_mouse(self) -> bool:
        """
        Description:
            Returns whether this container is colliding with the mouse, using its image as spatial reference
        Input:
            None
        Output:
            boolean: Returns True if this container is colliding with the mouse, otherwise returns False
        """
        return self.image.touching_mouse()

    def can_show_tooltip(self) -> bool:
        """
        Returns whether this container's tooltip can currently be shown
        """
        if self.touching_mouse() and self.showing:
            return True
        else:
            return False

    @property
    def batch_tooltip_list(self) -> List[List[str]]:
        """
        Gets a 2D list of strings to use as this object's tooltip
            Each string is displayed on a separate line, while each sublist is displayed in a separate box
        """
        return [self.tooltip_text]

    @property
    def tooltip_text(self) -> List[str]:
        """
        Provides the tooltip for this object
        """
        return ["Placeholder container tooltip"]

    def draw(self):
        """
        Draws this container's image and outline
        """
        super().draw()
        if self.has_outline:
            pygame.draw.rect(
                constants.game_display,
                self.outline_config["outline_color"],
                pygame.Rect(
                    self.x - self.outline_config["outline_width"],
                    constants.display_height
                    - (self.y + self.height + self.outline_config["outline_width"]),
                    self.width + (2 * self.outline_config["outline_width"]),
                    self.height + (self.outline_config["outline_width"] * 2),
                ),
                self.outline_config["outline_width"],
            )

    def add_member(
        self,
        new_member: interface_elements.interface_element,
        member_config: Dict[str, Any] = None,
    ) -> None:
        super().add_member(new_member, member_config)
        new_member.draw_priority = constants.DRAW_PRIORITY_CONTAINER_MEMBER


class workflow_container(container):
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
        self.workflow: workflows.workflow = input_dict["workflow"]
        self.workflow.current_container = self
        top_right_menu_button_size = 40
        top_right_menu_separation = 10
        self.top_right_menu: interface_elements.ordered_collection = (
            constants.ActorCreationManager.create_interface_element(
                {
                    "init_type": constants.ORDERED_COLLECTION,
                    "coordinates": (
                        self.image.width
                        - scaling.scale_width(
                            top_right_menu_button_size + top_right_menu_separation
                        ),
                        self.image.height
                        - scaling.scale_height(
                            top_right_menu_button_size + top_right_menu_separation
                        ),
                    ),
                    "parent_collection": self,
                    "direction": "horizontal",
                    "reversed": True,
                    "separation": scaling.scale_width(top_right_menu_separation),
                }
            )
        )
        self.reposition_button: reposition_container_button = (
            constants.ActorCreationManager.create_interface_element(
                {
                    "init_type": constants.REPOSITION_CONTAINER_BUTTON,
                    "width": scaling.scale_width(top_right_menu_button_size),
                    "height": scaling.scale_height(top_right_menu_button_size),
                    "image_id": "buttons/reposition_button.png",
                    "parent_collection": self.top_right_menu,
                }
            )
        )
        self.close_workflow_button: workflows.close_workflow_button = (
            constants.ActorCreationManager.create_interface_element(
                {
                    "init_type": constants.CLOSE_WORKFLOW_BUTTON,
                    "width": scaling.scale_width(top_right_menu_button_size),
                    "height": scaling.scale_height(top_right_menu_button_size),
                    "image_id": "buttons/minimize_button.png",
                    "parent_collection": self.top_right_menu,
                    "workflow": self.workflow,
                }
            )
        )

    def remove(self):
        """
        Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        """
        super().remove()
        self.workflow.current_container = None


class reposition_container_button(buttons.button):
    def __init__(self, input_dict):
        super().__init__(input_dict)
