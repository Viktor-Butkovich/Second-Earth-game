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
    None  # requires additional setup before initialization
)
terrain_manager: terrain_manager_template = (
    None  # requires additional setup before initialization
)
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
minister_limit: int = 15

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

current_game_mode: str = None
STRATEGIC_MODE: str = "strategic"
EARTH_MODE: str = "earth"
MINISTERS_MODE: str = "ministers"
TRIAL_MODE: str = "trial"
MAIN_MENU_MODE: str = "main_menu"
NEW_GAME_SETUP_MODE: str = "new_game_setup"
game_modes: List[str] = [
    STRATEGIC_MODE,
    EARTH_MODE,
    MINISTERS_MODE,
    TRIAL_MODE,
    MAIN_MENU_MODE,
    NEW_GAME_SETUP_MODE,
]

KNOWLEDGE: str = "knowledge"
WATER: str = "water"
TEMPERATURE: str = "temperature"
VEGETATION: str = "vegetation"
ROUGHNESS: str = "roughness"
SOIL: str = "soil"
ALTITUDE: str = "altitude"
terrain_parameters: List[str] = [
    KNOWLEDGE,
    WATER,
    TEMPERATURE,
    VEGETATION,
    ROUGHNESS,
    SOIL,
    ALTITUDE,
]

current_map_mode: str = "terrain"
map_modes: List[str] = [
    "terrain",
    ALTITUDE,
    TEMPERATURE,
    ROUGHNESS,
    VEGETATION,
    SOIL,
    WATER,
    "magnetic",
]

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

SETTLEMENT_PANEL: str = "settlement_panel"
TERRAIN_PANEL: str = "terrain_panel"
INVENTORY_PANEL: str = "inventory_panel"
REORGANIZATION_PANEL: str = "reorganization_panel"

SPACE_MINISTER: str = "space"
ECOLOGY_MINISTER: str = "ecology"
TERRAN_AFFAIRS_MINISTER: str = "terran_affairs"
SCIENCE_MINISTER: str = "science"
ENERGY_MINISTER: str = "energy"
INDUSTRY_MINISTER: str = "industry"
TRANSPORTATION_MINISTER: str = "transportation"
SECURITY_MINISTER: str = "security"

SPACE_SKILL: str = "space"
ECOLOGY_SKILL = "ecology"
TERRAN_AFFAIRS_SKILL = "terran_affairs"
SCIENCE_SKILL = "science"
ENERGY_SKILL = "energy"
INDUSTRY_SKILL = "industry"
TRANSPORTATION_SKILL = "transportation"
SECURITY_SKILL = "security"

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
    "lowborn": [None],
    "banker": [TERRAN_AFFAIRS_SKILL],
    "merchant": [TERRAN_AFFAIRS_SKILL],
    "lawyer": [SECURITY_SKILL],
    "army officer": [SPACE_SKILL],
    "naval officer": [TRANSPORTATION_SKILL],
    "priest": [TERRAN_AFFAIRS_SKILL],
    "preacher": [TERRAN_AFFAIRS_SKILL],
    "natural scientist": [SCIENCE_SKILL],
    "doctor": ["random"],
    "industrialist": [INDUSTRY_SKILL, TRANSPORTATION_SKILL],
    "aristocrat": [None, "random"],
    "politician": [None, "random"],
    "business magnate": [INDUSTRY_SKILL, TRANSPORTATION_SKILL],
    "royal heir": [None, "random"],
}
skill_types: List[str] = []
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

MOB: str = "mob"
EUROPEAN_WORKERS: str = "european_workers"
CHURCH_VOLUNTEERS: str = "church_volunteers"
TRAIN: str = "train"
SHIP: str = "ship"
BOAT: str = "boat"
OFFICER: str = "officer"
EXPLORER: str = "explorer"
ENGINEER: str = "engineer"
DRIVER: str = "driver"
FOREMAN: str = "foreman"
MERCHANT: str = "merchant"
EVANGELIST: str = "evangelist"
MAJOR: str = "major"
PORTERS: str = "porters"
WORK_CREW: str = "work_crew"
CONSTRUCTION_GANG: str = "construction_gang"
CARAVAN: str = "caravan"
MISSIONARIES: str = "missionaries"
EXPEDITION: str = "expedition"
BATTALION: str = "battalion"

RAILROAD: str = "railroad"
ROAD: str = "road"
ROAD_BRIDGE: str = "road_bridge"
RAILROAD_BRIDGE: str = "railroad_bridge"
FERRY: str = "ferry"
INFRASTRUCTURE: str = "infrastructure"
FORT: str = "fort"
TRAIN_STATION: str = "train_station"
PORT: str = "port"
WAREHOUSES: str = "warehouses"
WAREHOUSES_LEVEL: str = "warehouses_level"
RESOURCE: str = "resource"
RESOURCE_SCALE: str = "scale"
RESOURCE_EFFICIENCY: str = "efficiency"
SLUMS: str = "slums"
SETTLEMENT: str = "settlement"

CELL_ICON: str = "cell_icon"
NAME_ICON: str = "name_icon"
LOAN: str = "loan"
BUTTON: str = "button"
INTERFACE_ELEMENT: str = "interface_element"
INTERFACE_COLLECTION: str = "interface_collection"
AUTOFILL_COLLECTION: str = "autofill_collection"
ORDERED_COLLECTION: str = "ordered_collection"
INVENTORY_GRID: str = "inventory_grid"
TABBED_COLLECTION: str = "tabbed_collection"
END_TURN_BUTTON: str = "end_turn_button"
CYCLE_SAME_TILE_BUTTON: str = "cycle_same_tile_button"
FIRE_UNIT_BUTTON: str = "fire_unit_button"
SWITCH_GAME_MODE_BUTTON: str = "switch_game_mode_button"
CYCLE_AVAILABLE_MINISTERS_BUTTON: str = "cycle_available_ministers_button"
COMMODITY_BUTTON: str = "commodity_button"
SHOW_PREVIOUS_REPORTS_BUTTON: str = "show_previous_reports_button"
TAB_BUTTON: str = "tab_button"
REORGANIZE_UNIT_BUTTON: str = "reorganize_unit_button"
CYCLE_AUTOFILL_BUTTON: str = "cycle_autofill_button"
ANONYMOUS_BUTTON: str = "anonymous_button"
ACTION_BUTTON: str = "action_button"
SCROLL_BUTTON: str = "scroll_button"
MAP_MODE_BUTTON: str = "map_mode_button"
INSTRUCTIONS_BUTTON: str = "instructions_button"
CHOICE_BUTTON: str = "choice_button"
NEW_GAME_BUTTON: str = "new_game_button"
LOAD_GAME_BUTTON: str = "load_game_button"
SAVE_GAME_BUTTON: str = "save_game_button"
CYCLE_UNITS_BUTTON: str = "cycle_units_button"
WAKE_UP_ALL_BUTTON: str = "wake_up_all_button"
EXECUTE_MOVEMENT_ROUTES_BUTTON: str = "execute_movement_routes_button"
GENERATE_CRASH_BUTTON: str = "generate_crash_button"
USE_EACH_EQUIPMENT_BUTTON: str = "use_each_equipment_button"
PICK_UP_EACH_COMMODITY_BUTTON: str = "pick_up_each_commodity_button"
SELL_EACH_COMMODITY_BUTTON: str = "sell_each_commodity_button"
DROP_EACH_COMMODITY_BUTTON: str = "drop_each_commodity_button"
SELL_COMMODITY_BUTTON: str = "sell_commodity_button"
SELL_ALL_COMMODITY_BUTTON: str = "sell_all_commodity_button"
USE_EQUIPMENT_BUTTON: str = "use_equipment_button"
REMOVE_EQUIPMENT_BUTTON: str = "remove_equipment_button"
RENAME_SETTLEMENT_BUTTON: str = "rename_settlement_button"
MINIMIZE_INTERFACE_COLLECTION_BUTTON: str = "minimize_interface_collection_button"
MOVE_INTERFACE_COLLECTION_BUTTON: str = "move_interface_collection_button"
RESET_INTERFACE_COLLECTION_BUTTON: str = "reset_interface_collection_button"

RECRUITMENT_CHOICE_BUTTON: str = "recruitment_choice_button"
CHOICE_CONFIRM_MAIN_MENU_BUTTON: str = "choice_confirm_main_menu_button"
CHOICE_QUIT_BUTTON: str = "choice_quit_button"
CHOICE_END_TURN_BUTTON: str = "choice_end_turn_button"
CHOICE_CONFIRM_REMOVE_MINISTER: str = "choice_confirm_remove_minister_button"
CHOICE_FIRE_BUTTON: str = "choice_fire_button"

AUTOFILL_PROCEDURE: str = "autofill_procedure"
MERGE_PROCEDURE: str = "merge"
SPLIT_PROCEDURE: str = "split"
CREW_PROCEDURE: str = "crew"
UNCREW_PROCEDURE: str = "uncrew"
INVALID_PROCEDURE: str = "invalid"
AUTOFILL_PROCEDURES: List[str] = [
    MERGE_PROCEDURE,
    SPLIT_PROCEDURE,
    CREW_PROCEDURE,
    UNCREW_PROCEDURE,
    INVALID_PROCEDURE,
]

START_END_TURN_BUTTON: str = "start_end_turn_button"
RECRUITMENT_BUTTON: str = "recruitment_button"
BUY_ITEM_BUTTON: str = "buy_item_button"
EMBARK_ALL_PASSENGERS_BUTTON: str = "embark_all_passengers_button"
DISEMBARK_ALL_PASSENGERS_BUTTON: str = "disembark_all_passengers_button"
ENABLE_SENTRY_MODE_BUTTON: str = "enable_sentry_mode_button"
DISABLE_SENTRY_MODE_BUTTON: str = "disable_sentry_mode_button"
ENABLE_AUTOMATIC_REPLACEMENT_BUTTON: str = "enable_automatic_replacement_button"
DISABLE_AUTOMATIC_REPLACEMENT_BUTTON: str = "disable_automatic_replacement_button"
END_UNIT_TURN_BUTTON: str = "end_unit_turn_button"
REMOVE_WORK_CREW_BUTTON: str = "remove_work_crew_button"
DISEMBARK_VEHICLE_BUTTON: str = "disembark_vehicle_button"
EMBARK_VEHICLE_BUTTON: str = "embark_vehicle_button"
CYCLE_PASSENGERS_BUTTON: str = "cycle_passengers_button"
CYCLE_WORK_CREWS_BUTTON: str = "cycle_work_crews_button"
WORK_CREW_TO_BUILDING_BUTTON: str = "work_crew_to_building_button"
SWITCH_THEATRE_BUTTON: str = "switch_theatre_button"
APPOINT_MINISTER_BUTTON: str = "appoint_minister_button"
REMOVE_MINISTER_BUTTON: str = "remove_minister_button"
TO_TRIAL_BUTTON: str = "to_trial_button"
FABRICATE_EVIDENCE_BUTTON: str = "fabricate_evidence_button"
BRIBE_JUDGE_BUTTON: str = "bribe_judge_button"
TOGGLE_BUTTON: str = "toggle_button"
CHANGE_PARAMETER_BUTTON: str = "change_parameter_button"
MOVE_LEFT_BUTTON: str = "move_left_button"
MOVE_RIGHT_BUTTON: str = "move_right_button"
MOVE_UP_BUTTON: str = "move_up_button"
MOVE_DOWN_BUTTON: str = "move_down_button"
BUILD_TRAIN_BUTTON: str = "build_train_button"
EXECUTE_AUTOMATIC_ROUTE_BUTTON: str = "execute_automatic_route_button"
DRAW_AUTOMATIC_ROUTE_BUTTON: str = "draw_automatic_route_button"
CLEAR_AUTOMATIC_ROUTE_BUTTON: str = "clear_automatic_route_button"

SAME_TILE_ICON: str = "same_tile_icon"
MINISTER_PORTRAIT_IMAGE: str = "minister_portrait_image"
ITEM_ICON: str = "item_icon"
DIE_ELEMENT: str = "die_element"
PANEL_ELEMENT: str = "panel_element"
SAFE_CLICK_PANEL_ELEMENT: str = "safe_click_panel_element"
LABEL: str = "label"
VALUE_LABEL: str = "value_label"
MONEY_LABEL: str = "money_label"
COMMODITY_PRICES_LABEL: str = "commodity_prices_label"
MULTI_LINE_LABEL: str = "multi_line_label"
ACTOR_DISPLAY_LABEL: str = "actor_display_label"
ACTOR_TOOLTIP_LABEL: str = "actor_tooltip_label"
LIST_ITEM_LABEL: str = "list_item_label"
BUILDING_WORK_CREWS_LABEL: str = "building_work_crews_label"
CURRENT_BUILDING_WORK_CREW_LABEL: str = "current_building_work_crew_label"
BUILDING_EFFICIENCY_LABEL: str = "building_efficiency_label"
TERRAIN_FEATURE_LABEL: str = "terrain_feature_label"
BANNER_LABEL: str = "banner_label"
MINISTER_NAME_LABEL: str = "minister_name_label"
MINISTER_BACKGROUND_LABEL: str = "minister_background_label"
MINISTER_OFFICE_LABEL: str = "minister_office_label"
MINISTER_SOCIAL_STATUS_LABEL: str = "minister_social_status_label"
MINISTER_INTERESTS_LABEL: str = "minister_interests_label"
MINISTER_LOYALTY_LABEL: str = "minister_loyalty_label"
MINISTER_ABILITY_LABEL: str = "minister_ability_label"
SPACE_SKILL_LABEL: str = "space_skill_label"
ECOLOGY_SKILL_LABEL: str = "ecology_skill_label"
TERRAN_AFFAIRS_SKILL_LABEL: str = "terran_affairs_skill_label"
SCIENCE_SKILL_LABEL: str = "science_skill_label"
ENERGY_SKILL_LABEL: str = "energy_skill_label"
INDUSTRY_SKILL_LABEL: str = "industry_skill_label"
TRANSPORTATION_SKILL_LABEL: str = "transportation_skill_label"
SECURITY_SKILL_LABEL: str = "security_skill_label"

EVIDENCE_LABEL: str = "evidence_label"
NAME_LABEL: str = "name_label"
MINISTER_LABEL: str = "minister_label"
OFFICER_LABEL: str = "officer_label"
WORKERS_LABEL: str = "workers_label"
MOVEMENT_LABEL: str = "movement_label"
COMBAT_STRENGTH_LABEL: str = "combat_strength_label"
ATTITUDE_LABEL: str = "attitude_label"
CONTROLLABLE_LABEL: str = "controllable_label"
CREW_LABEL: str = "crew_label"
PASSENGERS_LABEL: str = "passengers_label"
CURRENT_PASSENGER_LABEL: str = "current_passenger_label"
INVENTORY_NAME_LABEL: str = "inventory_name_label"
INVENTORY_QUANTITY_LABEL: str = "inventory_quantity_label"
COORDINATES_LABEL: str = "coordinates_label"
KNOWLEDGE_LABEL: str = "knowledge_label"
TERRAIN_LABEL: str = "terrain_label"
WATER_LABEL: str = "water_label"
TEMPERATURE_LABEL: str = "temperature_label"
VEGETATION_LABEL: str = "vegetation_label"
ROUGHNESS_LABEL: str = "roughness_label"
SOIL_LABEL: str = "soil_label"
ALTITUDE_LABEL: str = "altitude_label"
RESOURCE_LABEL: str = "resource_label"
TILE_INVENTORY_CAPACITY_LABEL: str = "tile_inventory_capacity_label"
MOB_INVENTORY_CAPACITY_LABEL: str = "mob_inventory_capacity_label"

FREE_IMAGE: str = "free_image"
ACTOR_DISPLAY_FREE_IMAGE: str = "actor_display_free_image"
MOB_BACKGROUND_IMAGE: str = "mob_background_image"
MINISTER_BACKGROUND_IMAGE: str = "minister_background_image"
LABEL_IMAGE: str = "label_image"
BACKGROUND_IMAGE: str = "background_image"
TOOLTIP_FREE_IMAGE: str = "tooltip_free_image"
MINISTER_TYPE_IMAGE: str = "minister_type_image"
DICE_ROLL_MINISTER_IMAGE: str = "dice_roll_minister_image"
INDICATOR_IMAGE: str = "indicator_image"
WARNING_IMAGE: str = "warning_image"
LOADING_IMAGE_TEMPLATE_IMAGE: str = "loading_image_template_image"
MOUSE_FOLLOWER_IMAGE: str = "mouse_follower_image"
DIRECTIONAL_INDICATOR_IMAGE: str = "directional_indicator_image"

NOTIFICATION: str = "notification"
ZOOM_NOTIFICATION: str = "zoom_notification"
CHOICE_NOTIFICATION: str = "choice_notification"
ACTION_NOTIFICATION: str = "action_notification"
DICE_ROLLING_NOTIFICATION: str = "dice_rolling_notification"
OFF_TILE_EXPLORATION_NOTIFICATION: str = "off_tile_exploration_notification"

PMOB_PERMISSION: str = "pmob"
NPMOB_PERMISSION: str = "npmob"
VEHICLE_PERMISSION: str = "vehicle"
ACTIVE_PERMISSION: str = "active_permission"
ACTIVE_VEHICLE_PERMISSION: str = "active_vehicle"
INACTIVE_VEHICLE_PERMISSION: str = "inactive_vehicle"
OFFICER_PERMISSION: str = "officer"
WORKER_PERMISSION: str = "worker"
CHURCH_VOLUNTEERS_PERMISSION: str = "church_volunteers"
EUROPEAN_WORKERS_PERMISSION: str = "european_workers"
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

officer_types: List[str] = [
    EXPLORER,
    ENGINEER,
    DRIVER,
    FOREMAN,
    MERCHANT,
    EVANGELIST,
    MAJOR,
]
officer_group_type_dict: Dict[str, str] = {
    EXPLORER: EXPEDITION,
    ENGINEER: CONSTRUCTION_GANG,
    DRIVER: PORTERS,
    FOREMAN: WORK_CREW,
    MERCHANT: CARAVAN,
    EVANGELIST: MISSIONARIES,
    MAJOR: BATTALION,
}
officer_minister_dict: Dict[str, str] = {
    EXPLORER: SCIENCE_MINISTER,
    ENGINEER: INDUSTRY_MINISTER,
    DRIVER: TRANSPORTATION_MINISTER,
    FOREMAN: INDUSTRY_MINISTER,
    MERCHANT: TERRAN_AFFAIRS_MINISTER,
    EVANGELIST: TERRAN_AFFAIRS_MINISTER,
    MAJOR: SPACE_MINISTER,
}
group_minister_dict: Dict[str, str] = {
    EXPEDITION: SCIENCE_MINISTER,
    CONSTRUCTION_GANG: INDUSTRY_MINISTER,
    PORTERS: TRANSPORTATION_MINISTER,
    WORK_CREW: INDUSTRY_MINISTER,
    CARAVAN: TERRAN_AFFAIRS_MINISTER,
    MISSIONARIES: TERRAN_AFFAIRS_MINISTER,
    BATTALION: SPACE_MINISTER,
}

recruitment_types: List[str] = officer_types + [EUROPEAN_WORKERS, SHIP]
recruitment_costs: Dict[str, int] = {
    EUROPEAN_WORKERS: 0,
    SHIP: 10,
    OFFICER: 5,
}

building_types: List[str] = [
    RESOURCE,
    PORT,
    INFRASTRUCTURE,
    TRAIN_STATION,
    FORT,
    SLUMS,
    WAREHOUSES,
]
upgrade_types: List[str] = [RESOURCE_SCALE, RESOURCE_EFFICIENCY, WAREHOUSES_LEVEL]

building_prices: Dict[str, int] = {
    RESOURCE: 10,
    ROAD: 5,
    RAILROAD: 15,
    FERRY: 50,
    ROAD_BRIDGE: 100,
    RAILROAD_BRIDGE: 300,
    PORT: 15,
    TRAIN_STATION: 10,
    FORT: 5,
    WAREHOUSES: 5,
    TRAIN: 10,
}
