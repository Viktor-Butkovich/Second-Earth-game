# Contains functionality for interface selectors

from __future__ import annotations
from modules.constants import constants, status, flags
from modules.interface_components import interface_elements
from typing import List, Dict, Tuple, Any


class left_right_selector(interface_elements.interface_element):
    def __init__(self, input_dict: Dict[str, Any]) -> None:
        super().__init__(input_dict)


class dropdown_selector(interface_elements.interface_element):
    def __init__(self, input_dict: Dict[str, Any]) -> None:
        super().__init__(input_dict)
