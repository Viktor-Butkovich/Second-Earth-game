from __future__ import annotations
from modules.constants import constants, status, flags
from modules.constructs import item_types, equipment_types

def config_item_types() -> None:
    """
    Configures all item types during setup
    """
    define_materials()
    define_resources()
    define_equipment()

def define_materials() -> None:
    """
    Configures material types during setup
    """
    item_types.material_type(
        {
            "key": constants.MATERIAL_STRUCTURAL_METALS,
            "can_purchase": True,
            "can_sell": True,
            "price": 5,
            "description": ["Placeholder structural metals description"],
            "item_image": "items/material/structural_metals.png",
            "background_color": constants.color_dict[constants.COLOR_DARKER_GRAY],
            "allow_price_variation": True,
            "abbreviated_name": "struct. metals",
        }
    )
    item_types.material_type(
        {
            "key": constants.MATERIAL_CONSTRUCTION_MATERIALS,
            "can_purchase": True,
            "can_sell": True,
            "price": 5,
            "description": ["Placeholder construction materials description"],
            "item_image": "items/material/construction_materials.png",
            "background_color": constants.color_dict[constants.COLOR_DARK_GRAY],
            "allow_price_variation": True,
            "abbreviated_name": "const. matls",
        }
    )
    item_types.material_type(
        {
            "key": constants.MATERIAL_ADVANCED_MATERIALS,
            "can_purchase": True,
            "can_sell": True,
            "price": 5,
            "description": ["Placeholder advanced materials description"],
            "item_image": "items/material/advanced_materials.png",
            "background_color": constants.color_dict[constants.COLOR_RED],
            "allow_price_variation": True,
            "abbreviated_name": "adv. matls",
        }
    )
    item_types.material_type(
        {
            "key": constants.MATERIAL_FUELS,
            "can_purchase": True,
            "can_sell": True,
            "price": 5,
            "description": ["Placeholder fuels description"],
            "item_image": "items/material/fuels.png",
            "background_color": constants.color_dict[constants.COLOR_FIRE_ORANGE],
            "allow_price_variation": True,
        }
    )
    item_types.material_type(
        {
            "key": constants.MATERIAL_CHEMICALS,
            "can_purchase": True,
            "can_sell": True,
            "price": 5,
            "description": ["Placeholder chemicals description"],
            "item_image": "items/material/chemicals.png",
            "background_color": constants.color_dict[constants.COLOR_YELLOW_GREEN],
            "allow_price_variation": True,
        }
    )
    item_types.material_type(
        {
            "key": constants.MATERIAL_BIOMATERIALS,
            "can_purchase": True,
            "can_sell": True,
            "price": 5,
            "description": ["Placeholder biomaterials description"],
            "item_image": "items/material/biomaterials.png",
            "background_color": constants.color_dict[constants.COLOR_DARK_GREEN],
            "allow_price_variation": True,
            "abbreviated_name": "bio. matls",
        }
    )
    item_types.material_type(
        {
            "key": constants.MATERIAL_NUCLEAR_MATERIALS,
            "can_purchase": True,
            "can_sell": True,
            "price": 5,
            "description": ["Placeholder nuclear materials description"],
            "item_image": "items/material/nuclear_materials.png",
            "background_color": constants.color_dict[constants.COLOR_BRIGHT_GREEN],
            "allow_price_variation": True,
            "abbreviated_name": "nuc. matls",
        }
    )

def define_resources() -> None:
    """
    Configures resource types during setup
    """
    item_types.resource_type(
        {
            "key": constants.RESOURCE_FOOD,
            "can_purchase": True,
            "can_sell": True,
            "price": 5,
            "description": ["Placeholder food description"],
            "item_image": "items/resource/food.png",
            "background_color": constants.color_dict[constants.COLOR_YELLOW],
            "allow_price_variation": True,
        }
    )

    item_types.resource_type(
        {
            "key": constants.RESOURCE_WATER,
            "can_purchase": True,
            "can_sell": True,
            "price": 5,
            "description": ["Placeholder water description"],
            "item_image": "items/resource/water.png",
            "background_color": constants.color_dict[constants.COLOR_BLUE],
            "allow_price_variation": True,
        }
    )

    item_types.resource_type(
        {
            "key": constants.RESOURCE_AIR,
            "can_purchase": True,
            "can_sell": True,
            "price": 5,
            "description": ["Placeholder air description"],
            "item_image": "items/resource/air.png",
            "background_color": constants.color_dict[constants.COLOR_WHITE],
            "allow_price_variation": True,
        }
    )

    item_types.resource_type(
        {
            "key": constants.RESOURCE_CONSUMER_GOODS,
            "can_purchase": True,
            "can_sell": True,
            "price": constants.consumer_goods_starting_price,
            "description": ["Placeholder consumer goods description"],
            "item_image": "items/resource/consumer_goods.png",
            "background_color": constants.color_dict[constants.COLOR_GREEN_ICON],
            "allow_price_variation": True,
            "abbreviated_name": "cons. goods",
        }
    )

    item_types.resource_type(
        {
            "key": constants.RESOURCE_ENERGY,
            "can_purchase": False,
            "can_sell": False,
            "description": ["Placeholder energy description"],
            "item_image": "items/resource/energy.png",
            "background_color": constants.color_dict[constants.COLOR_PURPLE],
        }
    )

def define_equipment() -> None:
    """
    Configures equipment types during setup
    """
    equipment_types.equipment_type(
        {
            "key": constants.EQUIPMENT_SPACESUITS,
            "can_purchase": True,
            "price": 5,
            "requirements": (
                "any",
                [
                    constants.GROUP_PERMISSION,
                    constants.WORKER_PERMISSION,
                    constants.OFFICER_PERMISSION,
                ],
            ),
            "effects": {
                "permissions": [constants.SPACESUITS_PERMISSION],
            },
            "description": [
                "Spacesuits are required for humans to survive in deadly conditions",
                "Human units without spacesuits in deadly conditions cannot perform actions and will die at the end of the turn",
                # "By default, solitary officers are assumed to be wearing personal spacesuits",
            ],
            "item_image": "items/equipment/spacesuits.png",  # Used for icons
            "equipment_image": {  # Used as mob image components
                constants.FULL_BODY_PORTRAIT_SECTION: "mobs/spacesuits/spacesuit_body.png",
                constants.HAT_PORTRAIT_SECTION: "ministers/portraits/hat/spacesuit/spacesuit_helmet.png",
                constants.HAIR_PORTRAIT_SECTION: "misc/empty.png",
                constants.FACIAL_HAIR_PORTAIT_SECTION: "misc/empty.png",
                constants.BACKPACK_PORTRAIT_SECTION: "mobs/spacesuits/spacesuit_backpack.png",
            },
        }
    )