# Contains functionality for interface selectors

from __future__ import annotations
from modules.constants import constants, status, flags
from modules.interface_components import interface_elements, buttons, labels
from modules.constructs import fonts
from modules.util import scaling, text_utility
from typing import List, Dict, Tuple, Any, Callable


class left_right_selector(interface_elements.interface_element):
    def __init__(self, input_dict: Dict[str, Any]) -> None:
        super().__init__(input_dict)


class dropdown_selector(buttons.button):
    def __init__(self, input_dict: Dict[str, Any]) -> None:
        if "image_id" in input_dict:
            raise Exception("dropdown_item sets image_id automatically.")
        input_dict["image_id"] = "misc/empty.png"
        super().__init__(input_dict)
        self.font: fonts.font = constants.fonts[constants.DEFAULT_NOTIFICATION_FONT]
        self.dropdown_options: List[dropdown_option] = input_dict["dropdown_options"]
        self.prefix: str = input_dict["prefix"]
        self.current_dropdown_items: List[dropdown_item] = []
        self.insert_collection_above(
            override_input_dict={
                "init_type": constants.ORDERED_COLLECTION,
                "direction": "horizontal",
                "separation": scaling.scale_width(5),
            }
        )
        self.on_select: Callable[[Any], None] = input_dict["on_select"]
        prefix_label: labels.label = (
            constants.ActorCreationManager.create_interface_element(
                {
                    "init_type": constants.LABEL,
                    "message": self.prefix,
                    "parent_collection": self.parent_collection,
                    "minimum_width": scaling.scale_width(10),
                    "height": self.height,
                    "image_id": "misc/empty.png",
                    "member_config": {"index": 0},  # Place before dropdown
                    "enable_tooltip": False,
                }
            )
        )
        self.insert_collection_above()
        self.dropdown_options_collection: interface_elements.interface_collection = (
            constants.ActorCreationManager.create_interface_element(
                {
                    "init_type": constants.ORDERED_COLLECTION,
                    "coordinates": (0, -scaling.scale_height(5)),
                    "parent_collection": self.parent_collection,
                    "member_config": {"order_exempt": True},
                }
            )
        )
        self.current_selection: dropdown_option = None
        self.delay_finish_init: bool = input_dict["delay_finish_init"]
        self.ran_finished_init: bool = False
        if not self.delay_finish_init:
            self.finish_init()

    def finish_init(self) -> None:
        assert not self.ran_finished_init, "Cannot finish initialization twice."
        self.ran_finished_init = True
        self.update_selection(self.dropdown_options[0])

    def update_selection(self, new_selection: dropdown_option) -> None:
        assert (
            self.ran_finished_init
        ), "Cannot update selection before finishing initialization."
        self.current_selection = new_selection
        dropdown_arrow_size = scaling.unscale_height(self.height) * 0.9
        dropdown_arrow_icon = (
            "buttons/cycle_ministers_down_button.png"
            if status.active_dropdown is None
            else "buttons/cycle_ministers_up_button.png"
        )
        message = (
            new_selection.option_text
        )  # f"{self.prefix}{new_selection.option_text}"
        font = constants.fonts[constants.DEFAULT_NOTIFICATION_FONT]
        self.set_size(
            width=font.calculate_size(message)
            + scaling.scale_width(dropdown_arrow_size + 10),
            height=self.height,
        )
        self.image.set_image(
            [
                text_utility.prepare_render(
                    message=message,
                    font=font,
                    override_input_dict={
                        "level": constants.FRONT_LEVEL,
                        "x_offset": 0.05,  # Left margin
                    },
                    target_width=self.width,
                    alignment="left",
                ),
                {
                    "image_id": dropdown_arrow_icon,
                    "level": constants.FRONT_LEVEL,
                    "override_width": scaling.scale_width(dropdown_arrow_size),
                    "override_height": scaling.scale_height(dropdown_arrow_size),
                    "abs_x_offset": (self.width / 2)
                    - scaling.scale_width(dropdown_arrow_size / 2),
                },
                {
                    "image_id": "buttons/default_wide_button.png",
                    "level": constants.BACKGROUND_LEVEL,
                },
            ]
        )
        self.on_select(new_selection.option)

    def on_click(self) -> None:
        super().on_click()
        if status.active_dropdown is None:
            status.active_dropdown = self
            self.update_selection(self.current_selection)
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
                            "parent_collection": self.dropdown_options_collection,
                            "width": longest_width + scaling.scale_width(10),
                            "height": scaling.scale_height(self.font.size + 5),
                            "dropdown_selector": self,
                        }
                    )
                )

    def close_dropdown(self) -> None:
        status.active_dropdown = None
        for current_item in self.current_dropdown_items:
            current_item.remove()
        self.current_dropdown_items = []
        self.update_selection(self.current_selection)


class dropdown_item(buttons.button):
    def __init__(self, input_dict: Dict[str, Any]) -> None:
        self.dropdown_option: dropdown_option = input_dict["dropdown_option"]
        self.dropdown_selector: dropdown_selector = input_dict["dropdown_selector"]
        if "image_id" in input_dict:
            raise Exception("dropdown_item sets image_id automatically.")
        input_dict["image_id"] = [
            text_utility.prepare_render(
                message=self.dropdown_option.option_text,
                font=constants.fonts[constants.DEFAULT_NOTIFICATION_FONT],
                override_input_dict={
                    "level": constants.FRONT_LEVEL,
                },
            ),
            {
                "image_id": "buttons/default_wide_button.png",
                "level": constants.BACKGROUND_LEVEL,
            },
        ]
        super().__init__(input_dict)
        self.draw_priority = self.parent_collection.draw_priority + 1

    def on_click(self) -> None:
        super().on_click()
        self.dropdown_selector.close_dropdown()
        self.dropdown_selector.update_selection(self.dropdown_option)

    @property
    def batch_tooltip_list(self):
        return reversed(self.dropdown_option.tooltip_text)


class dropdown_option:
    def __init__(
        self, option_text: str, option: Any, tooltip_text: List[List[str]]
    ) -> None:
        self.option_text: str = option_text
        self.option: Any = option
        self.tooltip_text: List[List[str]] = tooltip_text


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
