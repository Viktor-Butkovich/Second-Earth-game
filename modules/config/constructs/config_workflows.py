from __future__ import annotations
from modules.constants import constants, status, flags
from modules.workflow_types import workflows


def config_workflows() -> None:
    workflows.design_building_workflow()
