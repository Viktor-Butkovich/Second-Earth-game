# Contains misc. interface components

from __future__ import annotations
from modules.interface_components import interface_elements
from modules.constants import constants, status, flags
from modules.util import text_utility, actor_utility, scaling
from modules.constructs import item_types
from typing import Dict, List, Any


class item_count_indicator(interface_elements.interface_element):
    def __init__(self, input_dict: Dict[str, Any]) -> None:
        if "image_id" in input_dict:
            raise Exception("item_count_indicator sets image_id automatically.")
        input_dict["image_id"] = "misc/empty.png"
        super().__init__(input_dict)
        unscaled_width, unscaled_height = scaling.unscale_width(
            self.width
        ), scaling.unscale_height(self.height)
        assert round(unscaled_height) == round(
            unscaled_width / 2
        ), f"item_count_indicator must have a 2:1 width to height ratio. Currently, width={unscaled_width:.2f}, height={unscaled_height:.2f}"
        self.item_count: float = input_dict["item_count"]
        self.item_type: item_types.item_type = input_dict["item_type"]
        item_meta = {
            "x_size": 0.5,
            "y_size": 1.0,
            "x_offset": 0.25,
            "level": constants.DEFAULT_LEVEL,
        }
        sample_render = text_utility.prepare_render(
            message=f"x{self.format_item_count(1.5)}",
            font=constants.fonts[constants.DEFAULT_NOTIFICATION_FONT],
            override_input_dict={
                "level": constants.FRONT_LEVEL,
                "x_offset": -0.03,
            },
            alignment="left",
        )
        text_render = text_utility.prepare_render(
            message=f"x{self.format_item_count(self.item_count)}",
            font=constants.fonts[constants.DEFAULT_NOTIFICATION_FONT],
            override_input_dict={
                "level": constants.FRONT_LEVEL,
                "x_offset": -0.03,
            },
            alignment="left",
        )
        assert isinstance(self.parent_collection, interface_elements.ordered_collection)
        if sample_render["override_width"] > text_render["override_width"]:
            # If standard text width exceeds text width exceeds standard text width, shift this element and all after it by the width deficit, such that the visible separation between elements remains constant
            self.parent_collection.shift(
                self,
                order_x_offset_increase=text_render["override_width"]
                - sample_render["override_width"],
                include_after=True,
            )

        self.image.set_image(
            [
                text_render,
                {
                    **item_meta,
                    "image_id": "misc/circle.png",
                    "green_screen": self.item_type.background_color,
                },
                {
                    **item_meta,
                    "image_id": self.item_type.item_image,
                },
            ]
        )

    def format_item_count(self, item_count: float) -> str:
        """
        Description:
            Formats the inputted item count as follows:
                1.0 -> 1
                1.515 -> 1.52
                0.5 -> .5
                0.0 -> 0
        Input:
            float item_count: Item count to format
        Output:
            str: Formatted item count
        """
        if item_count == 0:
            return "0"
        partial = f"{item_count:.2f}".rstrip("0").rstrip(".")
        return partial if not partial.startswith("0") else partial[1:]

    @property
    def batch_tooltip_list(self) -> List[List[str]]:
        return [[f"{self.item_count} {self.item_type.name}"]]

    def can_show_tooltip(self):
        """
        Returns whether this element's tooltip can be shown.
        """
        if self.touching_mouse() and self.showing:
            return True
        else:
            return False
