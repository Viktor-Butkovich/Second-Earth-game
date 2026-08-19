# Contains functionality for interface containers

from __future__ import annotations
import pygame
from modules.interface_components import interface_elements, buttons
from modules.constants import constants, status, flags
from typing import List, Dict, Tuple, Any


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
        self.reposition_origin: Tuple[int, int] = None
        self.repositioning_mouse_origin: Tuple[int, int] = None
        self.repositioning: bool = False

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

    def on_frame_update(self) -> None:
        super().on_frame_update()
        if self.repositioning:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_offset_x, mouse_offset_y = (
                mouse_x - self.reposition_mouse_origin[0],
                mouse_y - self.reposition_mouse_origin[1],
            )
            x, y = (
                self.reposition_origin[0] + mouse_offset_x,
                self.reposition_origin[1] - mouse_offset_y,
            )

            # Bound to edges
            x = min(
                x,
                constants.display_width
                - (self.width + self.outline_config["outline_width"]),
            )
            x = max(x, self.outline_config["outline_width"])
            y = min(
                y,
                constants.display_height
                - (self.height + self.outline_config["outline_width"]),
            )
            y = max(y, self.outline_config["outline_width"])
            self.set_origin(x, y)

    def start_reposition(self) -> None:
        self.repositioning = True
        self.reposition_origin = (self.x, self.y)
        self.reposition_mouse_origin = pygame.mouse.get_pos()

    def end_reposition(self) -> None:
        self.repositioning = False
        self.reposition_origin = None
        self.reposition_mouse_origin = None


class reposition_container_button(buttons.button):
    def __init__(self, input_dict: Dict[str, Any]) -> None:
        super().__init__(input_dict)
        self.container: container = input_dict["container"]

    def on_click(self) -> None:
        super().on_click()
        (
            self.container.start_reposition()
            if not self.container.repositioning
            else self.container.end_reposition()
        )

    @property
    def tooltip_text(self) -> List[str]:
        if not self.container.repositioning:
            return ["Click to reposition this panel"]
        else:
            return ["Click to stop repositioning this panel"]
