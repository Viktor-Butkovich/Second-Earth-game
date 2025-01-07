from typing import List, Dict, Any
from modules.constants import constants, status, flags


class help_manager_template:
    """
    Object that controls generating game advice
    """

    def __init__(self):
        """
        Description:
            Initializes this object
        Input:
            None
        Output:
            None
        """
        self.subjects: Dict[str, List[str]] = {
            constants.HELP_GLOBAL_PARAMETERS: [
                constants.PRESSURE_LABEL,
                constants.AVERAGE_WATER_LABEL,
                constants.GRAVITY_LABEL,
                constants.RADIATION_LABEL,
                constants.MAGNETIC_FIELD_LABEL,
                constants.TOTAL_HEAT_LABEL,
                constants.INSOLATION_LABEL,
                constants.GHG_EFFECT_LABEL,
                constants.WATER_VAPOR_EFFECT_LABEL,
                constants.ALBEDO_EFFECT_LABEL,
                constants.AVERAGE_TEMPERATURE_LABEL,
            ]
            + constants.ATMOSPHERE_COMPONENT_LABELS,
        }
        self.label_types: List[str] = [
            item for sublist in self.subjects.values() for item in sublist
        ]

    def generate_message(self, subject: str, context: Dict[str, Any] = None) -> str:
        """
        Description:
            Generates and returns a notification message for the inputted subject
        Input:
            string subject: Subject to generate a message for, like constants.PRESSURE
            dictionary context: Optional context for message generation, like {"world_handler": ...}
        Output:
            string: Returns a notification message for the inputted subject
        """
        message = ["line1", "line2"]

        return " /n /n".join(message) + " /n /n"

    def generate_tooltip(self, subject: str, context: Dict[str, Any]) -> List[str]:
        """
        Description:
            Generates and returns a tooltip description for the inputted subject
        Input:
            string subject: Subject to generate a tooltip before, like constants.PRESSURE
            dictionary context: Optional context for tooltip generation, like {"world_handler": ...}
        Output:
            string list: Returns a tooltip description for the inputted subject
        """
        tooltip = [subject]

        return tooltip
