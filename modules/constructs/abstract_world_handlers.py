from typing import Dict
from modules.constructs import world_handlers
from modules.constants import constants, status, flags


class abstract_world_handler(world_handlers.world_handler):
    def __init__(self, from_save: bool, input_dict: Dict[str, any]) -> None:
        self.abstract_world_type = input_dict["abstract_world_type"]
        super().__init__(from_save, input_dict)

    def is_abstract_world(self) -> bool:
        return True

    def is_earth(self) -> bool:
        return self.abstract_world_type == constants.EARTH
