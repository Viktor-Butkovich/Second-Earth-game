import pygame
from typing import Dict, List, Any
from modules.tools.data_managers.sound_manager_template import sound_manager_template
from modules.tools.data_managers.save_load_manager_template import (
    save_load_manager_template,
)
from modules.tools.data_managers.flavor_text_manager_template import (
    flavor_text_manager_template,
)
from modules.tools.data_managers.input_manager_template import input_manager_template
from modules.tools.data_managers.actor_creation_manager_template import (
    actor_creation_manager_template,
)
from modules.tools.data_managers.event_manager_template import event_manager_template
from modules.tools.data_managers.achievement_manager_template import (
    achievement_manager_template,
)
from modules.tools.data_managers.terrain_manager_template import (
    terrain_manager_template,
)
from modules.tools.data_managers.character_manager_template import (
    character_manager_template,
)
from modules.tools.data_managers.effect_manager_template import effect_manager_template
from modules.tools.data_managers.notification_manager_template import (
    notification_manager_template,
)
from modules.tools.data_managers.value_tracker_template import (
    value_tracker_template,
    public_opinion_tracker_template,
    money_tracker_template,
)
from modules.tools.mouse_followers import mouse_follower_template
from modules.interface_types.labels import money_label_template
from modules.constructs.fonts import font

effect_manager: effect_manager_template = effect_manager_template()
pygame.init()
pygame.mixer.init()
pygame.display.set_icon(pygame.image.load("graphics/misc/SE.png"))
pygame.display.set_caption("SFA")
pygame.key.set_repeat(300, 200)
pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)
music_endevent: int = pygame.mixer.music.get_endevent()

key_codes: List[int] = [
    pygame.K_a,
    pygame.K_b,
    pygame.K_c,
    pygame.K_d,
    pygame.K_e,
    pygame.K_f,
    pygame.K_g,
    pygame.K_h,
    pygame.K_i,
    pygame.K_j,
    pygame.K_k,
    pygame.K_l,
    pygame.K_m,
    pygame.K_n,
    pygame.K_o,
    pygame.K_p,
    pygame.K_q,
    pygame.K_r,
    pygame.K_s,
    pygame.K_t,
    pygame.K_u,
    pygame.K_v,
    pygame.K_w,
    pygame.K_x,
    pygame.K_y,
    pygame.K_z,
    pygame.K_1,
    pygame.K_2,
    pygame.K_3,
    pygame.K_4,
    pygame.K_5,
    pygame.K_6,
    pygame.K_7,
    pygame.K_8,
    pygame.K_9,
    pygame.K_0,
    pygame.K_F1,
    pygame.K_F2,
    pygame.K_F3,
]
lowercase_key_values: List[str] = [
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "0",
]
uppercase_key_values: List[str] = [
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
    "!",
    "@",
    "#",
    "$",
    "%",
    "^",
    "&",
    "*",
    "(",
    ")",
]

default_display_width: int = (
    1728  # all parts of game made to be at default_display and scaled to display
)
default_display_height: int = 972
resolution_finder = pygame.display.Info()
if effect_manager.effect_active("fullscreen"):
    display_width: float = resolution_finder.current_w
    display_height: float = resolution_finder.current_h
    game_display: pygame.Surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
else:
    display_width: float = resolution_finder.current_w - round(
        default_display_width / 10
    )
    display_height: float = resolution_finder.current_h - round(
        default_display_height / 10
    )
    game_display: pygame.Surface = pygame.display.set_mode(
        (display_width, display_height)
    )

sound_manager: sound_manager_template = sound_manager_template()
save_load_manager: save_load_manager_template = save_load_manager_template()
flavor_text_manager: flavor_text_manager_template = flavor_text_manager_template()
input_manager: input_manager_template = input_manager_template()
actor_creation_manager: actor_creation_manager_template = (
    actor_creation_manager_template()
)
terrain_manager: terrain_manager_template = terrain_manager_template()
character_manager: character_manager_template = (
    None  # requires additional setup before initialization
)
achievement_manager: achievement_manager_template = (
    None  # requires additional setup before initialization
)
event_manager: event_manager_template = event_manager_template()
notification_manager: notification_manager_template = (
    None  # requires additional setup before initialization
)
mouse_follower: mouse_follower_template = None

turn: int = 0
turn_tracker: value_tracker_template = None
public_opinion: int = 0
public_opinion_tracker: public_opinion_tracker_template = None
money: float = 0
money_tracker: money_tracker_template = None
money_label: money_label_template = None
evil: int = 0
evil_tracker: value_tracker_template = None
fear: int = 0
fear_tracker: value_tracker_template = None
fps: int = 0
fps_tracker: value_tracker_template = None
frames_this_second: int = 0
last_fps_update: float = 0.0

current_game_mode: str = None
game_modes: List[str] = ["strategic", "earth", "ministers", "trial", "new_game_setup"]
current_map_mode: str = "terrain"
map_modes: List[str] = [
    "terrain",
    "altitude",
    "temperature",
    "roughness",
    "vegetation",
    "soil",
    "water",
    "magnetic",
]

loading_start_time: float = 0.0
previous_turn_time: float = 0.0
current_time: float = 0.0
last_selection_outline_switch: float = 0.0
mouse_moved_time: float = 0.0
end_turn_wait_time: float = 0.8

old_mouse_x: int = pygame.mouse.get_pos()[0]
old_mouse_y: int = pygame.mouse.get_pos()[1]

font_name: str = "times new roman"
default_font_size: int = 15
font_size: float = None
default_notification_font_size: int = 25
notification_font_size: float = None
myfont: font = None
fonts: Dict[str, font] = {}

default_music_volume: float = 0.3

current_instructions_page_index: int = 0
current_instructions_page_text: str = ""
message: str = ""

grid_types_list: List[str] = [
    "strategic_map_grid",
    "earth_grid",
    "scrolling_strategic_map_grid",
    "minimap_grid",
]
abstract_grid_type_list: List[str] = ["earth_grid"]

grids_collection_x: int = default_display_width - 740
grids_collection_y: int = default_display_height - 325

strategic_map_pixel_width: int = 320
strategic_map_pixel_height: int = 300
earth_grid_x_offset: int = 30
earth_grid_y_offset: int = 145

minimap_grid_pixel_width: int = strategic_map_pixel_width * 2
minimap_grid_pixel_height: int = strategic_map_pixel_height * 2
minimap_grid_coordinate_size: int = 5

default_text_box_height: int = 0
text_box_height: int = 0

mob_ordered_list_start_y: int = 0

available_minister_left_index: int = -2  # so that first index is in middle

building_types: List[str] = [
    "resource",
    "port",
    "infrastructure",
    "train_station",
    "fort",
    "slums",
    "warehouses",
]
upgrade_types: List[str] = ["scale", "efficiency", "warehouse_level"]

building_prices: Dict[str, int] = {
    "resource": 10,
    "road": 5,
    "railroad": 15,
    "ferry": 50,
    "road_bridge": 100,
    "railroad_bridge": 300,
    "port": 15,
    "train_station": 10,
    "fort": 5,
    "warehouses": 5,
    "train": 10,
}
base_action_prices: Dict[str, int] = {}
action_types: List[str] = []
action_prices: Dict[str, float] = {}

transaction_descriptions: Dict[str, str] = {
    "loan": "loans",
    "production": "production",
    "bribery": "bribery",
    "loan_interest": "loan interest",
    "inventory_attrition": "missing commodities",
    "sold_commodities": "commodity sales",
    "worker_upkeep": "worker upkeep",
    "subsidies": "subsidies",
    "trial_compensation": "trial compensation",
    "fabricated_evidence": "fabricated evidence",
    "items": "item purchases",
    "unit_recruitment": "unit recruitment",
    "attrition_replacements": "attrition replacements",
    "misc_revenue": "misc",
    "misc_expenses": "misc",
    "none": "miscellaneous company activities",
}
transaction_types: List[str] = [current_key for current_key in transaction_descriptions]

color_dict: Dict[str, tuple[int, int, int]] = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "light gray": (230, 230, 230),
    "gray": (190, 190, 190),
    "dark gray": (150, 150, 150),
    "bright red": (255, 0, 0),
    "red": (200, 0, 0),
    "dark red": (150, 0, 0),
    "bright green": (0, 255, 0),
    "green": (0, 200, 0),
    "dark green": (0, 150, 0),
    "bright blue": (0, 0, 255),
    "blue": (0, 0, 200),
    "dark blue": (0, 0, 150),
    "yellow": (255, 255, 0),
    "brown": (85, 53, 22),
    "blonde": (188, 175, 123),
    "purple": (127, 0, 170),
    "transparent": (1, 1, 1),
    "green_icon": (15, 154, 54),
    "yellow_icon": (255, 242, 0),
    "red_icon": (231, 0, 46),
}

quality_colors: Dict[str, tuple[int, int, int]] = {
    1: (180, 180, 180),
    2: (255, 255, 255),
    3: (0, 230, 41),
    4: (41, 168, 255),
    5: (201, 98, 255),
    6: (255, 157, 77),
}

green_screen_colors: List[tuple[int, int, int]] = [
    (62, 82, 82),
    (70, 70, 92),
    (110, 107, 3),
]

terrain_parameters: List[str] = [
    "knowledge",
    "water",
    "temperature",
    "vegetation",
    "roughness",
    "soil",
    "altitude",
]

terrain_colors: Dict[str, tuple[int, int, int]] = {
    "savannah": (150, 200, 104),
    "hills": (50, 205, 50),
    "jungle": (0, 100, 0),
    "water": (0, 0, 200),
    "mountains": (100, 100, 100),
    "swamp": (100, 100, 50),
    "desert": (255, 248, 104),
    "none": (0, 0, 0),
}
terrain_animal_dict: Dict[str, tuple[str, str, str]] = {
    "savannah": ["lion", "bull elephant", "Cape buffalo"],
    "hills": ["gorilla", "Cape buffalo", "hippopotamus"],
    "jungle": ["gorilla", "crocodile", "leopard"],
    "water": ["crocodile", "hippopotamus", "leopard"],
    "mountains": ["lion", "gorilla", "leopard"],
    "swamp": ["bull elephant", "crocodile", "hippopotamus"],
    "desert": ["lion", "bull elephant", "Cape buffalo"],
}
animal_terrain_dict: Dict[str, tuple[str, str, str]] = {
    "lion": ["savannah", "desert", "mountains"],
    "bull elephant": ["savannah", "swamp", "desert"],
    "Cape buffalo": ["savannah", "hills", "desert"],
    "crocodile": ["water", "swamp", "jungle"],
    "hippopotamus": ["water", "swamp", "hills"],
    "gorilla": ["mountains", "jungle", "hills"],
    "leopard": ["jungle", "mountains", "water"],
}
animal_adjectives: List[str] = [
    "man-eating",
    "bloodthirsty",
    "rampaging",
    "giant",
    "ravenous",
    "ferocious",
    "king",
    "lurking",
    "spectral",
    "infernal",
]
terrain_movement_cost_dict: Dict[str, int] = {
    "savannah": 1,
    "hills": 2,
    "jungle": 3,
    "water": 1,
    "mountains": 3,
    "swamp": 3,
    "desert": 2,
}
terrain_build_cost_multiplier_dict: Dict[str, int] = {
    "savannah": 1,
    "hills": 2,
    "jungle": 3,
    "water": 1,
    "mountains": 3,
    "swamp": 3,
    "desert": 2,
}

terrain_attrition_dict: Dict[str, int] = {
    "savannah": 1,
    "hills": 1,
    "jungle": 3,
    "water": 2,
    "mountains": 2,
    "swamp": 3,
    "desert": 2,
}

commodity_types: List[str] = [
    "consumer goods",
    "coffee",
    "copper",
    "diamond",
    "exotic wood",
    "fruit",
    "gold",
    "iron",
    "ivory",
    "rubber",
]
collectable_resources: List[str] = [
    "coffee",
    "copper",
    "diamond",
    "exotic wood",
    "fruit",
    "gold",
    "iron",
    "ivory",
    "rubber",
]
item_prices: Dict[str, int] = {}
sold_commodities: Dict[str, int] = {}
commodities_produced: Dict[str, int] = {}
attempted_commodities: List[str] = []
resource_building_dict: Dict[str, str] = {
    "coffee": "plantation",
    "copper": "mine",
    "diamond": "mine",
    "exotic wood": "plantation",
    "fruit": "plantation",
    "gold": "mine",
    "iron": "mine",
    "ivory": "camp",
    "rubber": "plantation",
}

weighted_backgrounds: List[str] = [
    "lowborn",
    "lowborn",
    "lowborn",
    "lowborn",
    "lowborn",
    "lowborn",
    "lowborn",
    "lowborn",
    "lowborn",
    "lowborn",
    "banker",
    "merchant",
    "lawyer",
    "industrialist",
    "industrialist",
    "industrialist",
    "industrialist",
    "industrialist",
    "industrialist",
    "natural scientist",
    "doctor",
    "politician",
    "politician",
    "army officer",
    "naval officer",
]
background_status_dict: Dict[str, int] = {
    "lowborn": 1,
    "banker": 2,
    "merchant": 2,
    "lawyer": 2,
    "army officer": 2,
    "naval officer": 2,
    "priest": 2,
    "preacher": 2,
    "natural scientist": 2,
    "doctor": 2,
    "industrialist": 3,
    "aristocrat": 3,
    "politician": 3,
    "business magnate": 4,
    "royal heir": 4,
}
background_skills_dict: Dict[str, List[str]] = {
    "lowborn": ["none"],
    "banker": ["trade"],
    "merchant": ["trade"],
    "lawyer": ["prosecution"],
    "army officer": ["military"],
    "naval officer": ["transportation"],
    "priest": ["religion"],
    "preacher": ["religion"],
    "natural scientist": ["exploration"],
    "doctor": ["random"],
    "industrialist": ["construction", "production", "transportation"],
    "aristocrat": ["none", "random"],
    "politician": ["none", "random"],
    "business magnate": ["construction", "production", "transportation"],
    "royal heir": ["none", "random"],
}
skill_types: List[str] = [
    "military",
    "religion",
    "trade",
    "exploration",
    "construction",
    "production",
    "transportation",
    "prosecution",
]
minister_types: List[str] = [
    "General",
    "Bishop",
    "Minister of Trade",
    "Minister of Geography",
    "Minister of Engineering",
    "Minister of Production",
    "Minister of Transportation",
    "Prosecutor",
]
type_minister_dict: Dict[str, str] = {
    "military": "General",
    "religion": "Bishop",
    "trade": "Minister of Trade",
    "exploration": "Minister of Geography",
    "construction": "Minister of Engineering",
    "production": "Minister of Production",
    "transportation": "Minister of Transportation",
    "prosecution": "Prosecutor",
}
minister_type_dict: Dict[str, str] = {
    "General": "military",
    "Bishop": "religion",
    "Minister of Trade": "trade",
    "Minister of Geography": "exploration",
    "Minister of Engineering": "construction",
    "Minister of Production": "production",
    "Minister of Transportation": "transportation",
    "Prosecutor": "prosecution",
}
minister_skill_to_description_dict: List[List[str]] = [
    ["unknown"],
    ["brainless", "moronic", "stupid", "idiotic"],
    ["incompetent", "dull", "slow", "bad"],
    ["incapable", "poor", "ineffective", "lacking"],
    ["able", "capable", "effective", "competent"],
    ["smart", "clever", "quick", "good"],
    ["expert", "genius", "brilliant", "superior"],
]  # not literally a dict, but index of skill number can be used like a dictionary
minister_corruption_to_description_dict: List[List[str]] = [
    ["unknown"],
    ["absolute", "fanatic", "pure", "saintly"],
    ["steadfast", "honest", "straight", "solid"],
    ["decent", "obedient", "dependable", "trustworthy"],
    ["opportunist", "questionable", "undependable", "untrustworthy"],
    ["shady", "dishonest", "slippery", "mercurial"],
    ["corrupt", "crooked", "rotten", "treacherous"],
]  # not literally a dict, but index of corruption number can be used like a dictionary
minister_limit: int = 15

officer_types: List[str] = [
    "explorer",
    "engineer",
    "driver",
    "foreman",
    "merchant",
    "evangelist",
    "major",
]
officer_group_type_dict: Dict[str, str] = {
    "explorer": "expedition",
    "engineer": "construction_gang",
    "driver": "porters",
    "foreman": "work_crew",
    "merchant": "caravan",
    "evangelist": "missionaries",
    "major": "battalion",
}
officer_minister_dict: Dict[str, str] = {
    "explorer": type_minister_dict["exploration"],
    "engineer": type_minister_dict["construction"],
    "driver": type_minister_dict["transportation"],
    "foreman": type_minister_dict["production"],
    "merchant": type_minister_dict["trade"],
    "evangelist": type_minister_dict["religion"],
    "major": type_minister_dict["military"],
}
group_minister_dict: Dict[str, str] = {
    "expedition": type_minister_dict["exploration"],
    "construction_gang": type_minister_dict["construction"],
    "porters": type_minister_dict["transportation"],
    "work_crew": type_minister_dict["production"],
    "caravan": type_minister_dict["trade"],
    "missionaries": type_minister_dict["religion"],
    "battalion": type_minister_dict["military"],
}
recruitment_types: List[str] = officer_types + ["European workers", "steamship"]
recruitment_costs: Dict[str, int] = {
    "European workers": 0,
    "steamship": 10,
    "officer": 5,
}

worker_upkeep_increment: float = 0.25
base_upgrade_price: float = 20.0  # 20 for 1st upgrade, 40 for 2nd, 80 for 3rd, etc.
consumer_goods_starting_price: int = 1

list_descriptions: Dict[str, List[str]] = {}
string_descriptions: Dict[str, str] = {}

toggle_button_tooltips: Dict[str, Dict[str, str]] = {
    "wait_until_full": {
        "default": "Toggles wait until full - waiting until there is a full load to transport or no remaining warehouse space before starting automatic route",
        "True": "Currently waiting until full",
        "False": "Currently waiting until there is anything to transport",
    },
    "show_planet_mask": {
        "default": "Toggles a frame around the planet to approximate viewing from space",
        "True": "Currently showing frame",
        "False": "Currently not showing frame",
    },
    "show_grid_lines": {
        "default": "Toggles grid lines on the map",
        "True": "Currently showing grid lines",
        "False": "Currently not showing grid lines",
    },
    "expand_text_box": {
        "default": "Expands the text box",
        "True": "Currently expanded",
        "False": "Currently default size",
    },
    "remove_fog_of_war": {
        "default": "Disables fog of war",
        "True": "Fog of war disabled - no knowledge required to view tiles",
        "False": "Fog of war active - knowledge required to view tiles",
    },
}

HAT_LEVEL: int = 6
EYES_LEVEL: int = 2
GLASSES_LEVEL: int = 3
HAIR_LEVEL: int = 4
FACIAL_HAIR_LEVEL: int = 8
PORTRAIT_LEVEL: int = 10
LABEL_LEVEL: int = 11
FRONT_LEVEL: int = 20
BACKGROUND_LEVEL: int = -5

PIXELLATED_SIZE: int = 2

TERRAIN_KNOWLEDGE: str = "terrain"
TERRAIN_KNOWLEDGE_REQUIREMENT: int = 0
TERRAIN_PARAMETER_KNOWLEDGE: str = "terrain_parameter"
TERRAIN_PARAMETER_KNOWLEDGE_REQUIREMENT: int = 0


def update_terrain_knowledge_requirements():
    global TERRAIN_KNOWLEDGE_REQUIREMENT, TERRAIN_PARAMETER_KNOWLEDGE_REQUIREMENT
    TERRAIN_KNOWLEDGE_REQUIREMENT = (
        1 if effect_manager.effect_active("remove_fog_of_war") else 2
    )
    TERRAIN_PARAMETER_KNOWLEDGE_REQUIREMENT = (
        1 if effect_manager.effect_active("remove_fog_of_war") else 3
    )


update_terrain_knowledge_requirements()

UNIQUE_FEATURE_TRACKING: str = "unique"
LIST_FEATURE_TRACKING: str = "list"

MAP_MODE_ALPHA: int = 170

PMOB_PERMISSION: str = "pmob"
NPMOB_PERMISSION: str = "npmob"
VEHICLE_PERMISSION: str = "vehicle"
ACTIVE_PERMISSION: str = "active_permission"
INACTIVE_VEHICLE_PERMISSION: str = "inactive_vehicle"
OFFICER_PERMISSION: str = "officer"
WORKER_PERMISSION: str = "worker"
GROUP_PERMISSION: str = "group"
INIT_COMPLETE_PERMISSION: str = "init_complete"
DISORGANIZED_PERMISSION: str = "disorganized"
VETERAN_PERMISSION: str = "veteran"
DUMMY_PERMISSION: str = "dummy"

EXPEDITION_PERMISSION: str = "expedition"
CONSTRUCTION_PERMISSION: str = "construction"
WORK_CREW_PERMISSION: str = "work_crew"
CARAVAN_PERMISSION: str = "caravan"
MISSIONARIES_PERMISSION: str = "missionaries"
BATTALION_PERMISSION: str = "battalion"

EXPLORER_PERMISSION: str = "explorer"
ENGINEER_PERMISSION: str = "engineer"
DRIVER_PERMISSION: str = "driver"
FOREMAN_PERMISSION: str = "foreman"
MERCHANT_PERMISSION: str = "merchant"
EVANGELIST_PERMISSION: str = "evangelist"
MAJOR_PERMISSION: str = "major"

DEFAULT_PERMISSIONS: Dict[str, Any] = {
    ACTIVE_PERMISSION: True,
}
