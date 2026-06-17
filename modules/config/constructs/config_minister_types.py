from __future__ import annotations
from modules.constants import constants, status, flags
from modules.constructs import minister_types


def config_minister_types() -> None:
    """
    Defines minister positions, backgrounds, and associated units
    """
    minister_types.minister_type(
        {
            "key": constants.SPACE_MINISTER,
            "name": "Minister of Space",
            "skill_type": constants.SPACE_SKILL,
            "description": [
                "Space-oriented units include astronauts, navigators, and space vehicles.",
                "The Minister of Space also controls outer colonies and space logistics.",
            ],
        }
    )
    minister_types.minister_type(
        {
            "key": constants.ECOLOGY_MINISTER,
            "name": "Minister of Ecology",
            "skill_type": constants.ECOLOGY_SKILL,
            "description": ["Ecology-oriented units include terraformers and doctors."],
        }
    )
    minister_types.minister_type(
        {
            "key": constants.TERRAN_AFFAIRS_MINISTER,
            "name": "Minister of Terran Affairs",
            "skill_type": constants.TERRAN_AFFAIRS_SKILL,
            "description": [
                "Terran Affairs-oriented units include lobbyists, executives, and influencers.",
                "The Minister of Terran Affairs also controls the purchase and sale of goods on Earth",
            ],
        }
    )
    minister_types.minister_type(
        {
            "key": constants.SCIENCE_MINISTER,
            "name": "Minister of Science",
            "skill_type": constants.SCIENCE_SKILL,
            "description": [
                "Science-oriented units include researchers and surveyors."
            ],
        }
    )

    minister_types.minister_type(
        {
            "key": constants.INDUSTRY_MINISTER,
            "name": "Minister of Industry",
            "skill_type": constants.INDUSTRY_SKILL,
            "description": [
                "Industry-oriented units include construction crews and work crews."
            ],
        }
    )

    minister_types.minister_type(
        {
            "key": constants.ENERGY_MINISTER,
            "name": "Minister of Energy",
            "skill_type": constants.ENERGY_SKILL,
            "description": ["Energy-oriented units include technicians."],
        }
    )

    minister_types.minister_type(
        {
            "key": constants.TRANSPORTATION_MINISTER,
            "name": "Minister of Transportation",
            "skill_type": constants.TRANSPORTATION_SKILL,
            "description": [
                "Transportation-oriented units include planetary vehicles and their crews.",
                "The Minister of Transportation also manages planetary logistics and warehouses.",
            ],
        }
    )
    minister_types.minister_type(
        {
            "key": constants.SECURITY_MINISTER,
            "name": "Minister of Security",
            "skill_type": constants.SECURITY_SKILL,
            "controls_units": False,
            "description": [
                "Security-oriented units include marines and investigators."
                "The Minister of Security also controls the process of investigating and removing corrupt ministers."
            ],
        }
    )
