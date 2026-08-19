# Contains functionality for interface selectors

from __future__ import annotations
from modules.constants import constants, status, flags
from modules.interface_components import interface_elements, buttons
from modules.constructs import fonts
from modules.util import scaling
from typing import List, Dict, Tuple, Any, Callable


class left_right_selector(interface_elements.interface_element):
    def __init__(self, input_dict: Dict[str, Any]) -> None:
        super().__init__(input_dict)


class dropdown_selector(buttons.button):
    def __init__(self, input_dict: Dict[str, Any]) -> None:
        super().__init__(input_dict)
        self.font: fonts.font = constants.fonts[constants.DEFAULT_NOTIFICATION_FONT]
        self.dropdown_options: List[dropdown_option] = input_dict["dropdown_options"]
        self.current_dropdown_items: List[dropdown_item] = []
        self.insert_collection_above()
        self.on_select: Callable[[dropdown_option], None] = input_dict["on_select"]

    def on_click(self) -> None:
        super().on_click()
        if status.active_dropdown is None:
            status.active_dropdown = self
            longest_width: int = max(
                [
                    self.font.calculate_size(current_option.option_text)
                    for current_option in self.dropdown_options
                ]
            )
            for current_option in self.dropdown_options:
                self.current_dropdown_items.append(
                    constants.ActorCreationManager.create_interface_element(
                        {
                            "init_type": constants.DROPDOWN_ITEM,
                            "dropdown_option": current_option,
                            "parent_collection": self.parent_collection,
                            "width": longest_width + scaling.scale_width(10),
                            "height": scaling.scale_height(self.font.size + 5),
                            "dropdown_selector": self,
                            "image_id": "buttons/default_button.png",
                        }
                    )
                )


class dropdown_item(buttons.button):
    def __init__(self, input_dict: Dict[str, Any]) -> None:
        super().__init__(input_dict)
        self.dropdown_option: dropdown_option = input_dict["dropdown_option"]
        self.dropdown_selector: dropdown_selector = input_dict["dropdown_selector"]

    def on_click(self) -> None:
        super().on_click()
        status.active_dropdown = None
        for current_item in self.dropdown_selector.current_dropdown_items:
            current_item.remove()
        self.dropdown_selector.current_dropdown_items = []
        self.dropdown_selector.on_select(self.dropdown_option)


class dropdown_option:
    def __init__(self, text: str, value: Any, tooltip_text: str) -> None:
        self.text: str = text
        self.value: Any = value
        self.tooltip_text: str = tooltip_text


"""
Dropdown selector:
* Clicking opens the list of options, which is not yet scrollable but should be bound to the screen edges like a
    tooltip. It could be implemented as a pop-up ordered collection of selection buttons (with no button
    selection highlight or borders to blur the distinction between them), clicking any one of which would close
    the popup and set the dropdown's selected value. Clicking anywhere else would close the dropdown in its
    current state.
* Add an extra image layer onto the button with a dropdown arrow to show that it is a dropdown selector - this extra layer
    should be consistently used for dropdown selectors.
Left/right arrow selector:
* This has been implemented ad-hoc too many times throughout the codebase. Create a formal interface collection
    that can be set up to cycle through an inputted list of options and trigger configured callbacks
* For easier resizing, probably have the interface as {[left arrow], [right arrow], [current value label]}
"""
