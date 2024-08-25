# Contains functionality for minister type templates, such as Prosecutor or Minister of Construction

from typing import Dict, List
import modules.constants.status as status
import modules.constants.constants as constants
import modules.util.minister_utility as minister_utility


class minister_type:
    """
    Minister template that tracks information about a minister position
    """

    def __init__(self, input_dict: Dict) -> None:
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'key': string value - Constant uniquely identifying this type of minister across the program
                'name': string value - Name of this minister type's office
                'skill_type': string value - Name of skill and image files associated with this minister type's office
                'controls_units': boolean value - Whether this minister type is responsible for commanding units
                'description': list[str] value - Description of this minister type
        Output:
            None
        """
        self.key: str = input_dict["key"]
        self.name: str = input_dict.get("name")
        self.skill_type: str = input_dict.get("skill_type")
        constants.skill_types.append(self.skill_type)
        self.controls_units: bool = input_dict.get("controls_units", True)
        self.description: List[str] = input_dict.get("description", "")
        status.minister_types[self.key] = self
        self.on_appoint(None)

    def get_description(self) -> List[str]:
        """
        Description:
            Generates and returns a description of this minister type
        Input:
            None
        Output:
            List[str]: Description of this minister type
        """
        tooltip_text = []
        if self.controls_units:
            tooltip_text.append(
                f"Whenever you command a {self.skill_type}-oriented unit to do an action, the {self.name} is responsible for executing the action."
            )
        tooltip_text += self.description
        if not minister_utility.get_minister(self.key):
            tooltip_text.append(
                f"There is currently no {self.name} appointed, so {self.skill_type}-oriented actions are not possible."
            )
        return tooltip_text

    def on_appoint(self, new_minister) -> None:
        """
        Description:
            Makes any updates required when worker first recruited (not on load)
        Input:
            None
        Output:
            None
        """
        minister_utility.set_minister(self.key, new_minister)

    def on_remove(self, old_minister):
        """
        Description:
            Makes any updates required when worker fired
        Input:
            boolean wander=False: Whether this worker will wander after being fired
        Output:
            None
        """
        minister_utility.set_minister(self.key, None)
        # for current_minister_image in status.minister_image_list:
        #    if current_minister_image.minister_type == self:
        #        current_minister_image.calibrate(None)
