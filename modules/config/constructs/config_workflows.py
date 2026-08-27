from __future__ import annotations
from modules.constants import constants, status, flags
from modules.workflow_types import design_building


def config_workflows() -> None:
    design_building.design_building_workflow()
