from __future__ import annotations
from modules.constants import constants, status, flags
from modules.action_types import (
    public_relations_campaign,
    advertising_campaign,
    combat,
    exploration,
    construction,
    loan_search,
    active_investigation,
    trial,
)


def config_actions() -> None:
    """
    Configures any actions in the action_types folder, preparing them to be automatically implemented
    """
    for building_type in status.building_types.values():
        if building_type.can_construct:
            construction.construction(building_type=building_type)
        # if building_type.can_damage:
        #     repair.repair(building_type=building_type)
        # for upgrade_type in building_type.upgrade_fields.keys():
        #     upgrade.upgrade(building_type=building_type, upgrade_type=upgrade_type)
    public_relations_campaign.public_relations_campaign()
    advertising_campaign.advertising_campaign()
    combat.combat()
    exploration.exploration()
    loan_search.loan_search()
    active_investigation.active_investigation()
    trial.trial()

    for key, action_type in status.actions.items():
        if action_type.placement_type == "free":
            button_input_dict = action_type.button_setup({})
            if button_input_dict:
                action_type.button = (
                    constants.ActorCreationManager.create_interface_element(
                        button_input_dict
                    )
                )
    # action imports hardcoded here, alternative to needing to keep module files in .exe version
