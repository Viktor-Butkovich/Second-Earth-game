import pygame
from typing import Dict, List, Tuple, Any
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
from modules.tools.data_managers.help_manager_template import help_manager_template
from modules.tools.mouse_followers import mouse_follower_template
from modules.interface_types.labels import money_label_template
from modules.constructs.fonts import font

effect_manager: effect_manager_template = effect_manager_template()
pygame.init()
pygame.mixer.init()
pygame.display.set_icon(pygame.image.load("graphics/misc/SE.png"))
pygame.display.set_caption("SE")
pygame.key.set_repeat(300, 200)
pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)
music_endevent: int = pygame.mixer.music.get_endevent()

loading_loops: int = 0

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
    game_display: pygame.Surface = pygame.display.set_mode(
        (0, 0), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
    )
else:
    display_width: float = resolution_finder.current_w - round(
        default_display_width / 10
    )
    if effect_manager.effect_active("skinny_screen"):
        display_width /= 2
    display_height: float = resolution_finder.current_h - round(
        default_display_height / 10
    )
    if effect_manager.effect_active("short_screen"):
        display_height /= 2
    game_display: pygame.Surface = pygame.display.set_mode(
        (display_width, display_height), pygame.HWSURFACE | pygame.DOUBLEBUF
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
help_manager: help_manager_template = (
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
mouse_position: Tuple[int, int] = None
mouse_position_tracker: value_tracker_template = None
frames_this_second: int = 0
last_fps_update: float = 0.0

previous_turn_time: float = 0.0
current_time: float = 0.0
last_selection_outline_switch: float = 0.0
mouse_moved_time: float = 0.0
end_turn_wait_time: float = 0.05

old_mouse_x: int = pygame.mouse.get_pos()[0]
old_mouse_y: int = pygame.mouse.get_pos()[1]

small_font_name: str = "times new roman"
font_name: str = "microsoftsansserif"
default_font_size: int = 18
font_size: float = None
default_notification_font_size: int = 22
notification_font_size: float = None
myfont: font = None
fonts: Dict[str, font] = {}

default_music_volume: float = 0.3

current_instructions_page_index: int = 0
current_instructions_page_text: str = ""
message: str = ""

grids_collection_x: int = default_display_width - 740
grids_collection_y: int = default_display_height - 325

earth_grid_x_offset: int = -75
earth_grid_y_offset: int = 140
earth_grid_width: int = 108
earth_grid_height: int = 108

strategic_map_x_offset: int = earth_grid_x_offset + earth_grid_width + 15
strategic_map_y_offset: int = earth_grid_y_offset
strategic_map_pixel_width: int = 180
strategic_map_pixel_height: int = 180

globe_projection_grid_x_offset: int = (
    strategic_map_x_offset + strategic_map_pixel_width + 15
)
globe_projection_grid_y_offset: int = earth_grid_y_offset
globe_projection_grid_width: int = 108
globe_projection_grid_height: int = 108

minimap_grid_x_offset: int = -75
minimap_grid_y_offset: int = 150
minimap_grid_pixel_width: int = 750  # strategic_map_pixel_width * 2
minimap_grid_pixel_height: int = 750  # strategic_map_pixel_height * 2
minimap_grid_coordinate_size: int = 7

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
    "inventory_attrition": "logistical incidents",
    "sold_items": "item sales",
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

COLOR_BLACK: str = "black"
COLOR_WHITE: str = "white"
COLOR_LIGHT_GRAY: str = "light gray"
COLOR_GRAY: str = "gray"
COLOR_DARK_GRAY: str = "dark gray"
COLOR_BRIGHT_RED: str = "bright red"
COLOR_RED: str = "red"
COLOR_DARK_RED: str = "dark red"
COLOR_BRIGHT_GREEN: str = "bright green"
COLOR_GREEN: str = "green"
COLOR_DARK_GREEN: str = "dark green"
COLOR_BRIGHT_BLUE: str = "bright blue"
COLOR_BLUE: str = "blue"
COLOR_DARK_BLUE: str = "dark blue"
COLOR_YELLOW: str = "yellow"
COLOR_BROWN: str = "brown"
COLOR_BLONDE: str = "blonde"
COLOR_PURPLE: str = "purple"
COLOR_TRANSPARENT: str = "transparent"
COLOR_GREEN_ICON: str = "green_icon"
COLOR_YELLOW_ICON: str = "yellow_icon"
COLOR_RED_ICON: str = "red_icon"
COLOR_GRAY_2: str = "gray_2"
COLOR_BRIGHT_GREEN_2: str = "bright_green_2"
COLOR_BRIGHT_BLUE_2: str = "bright_blue_2"
COLOR_PURPLE_2: str = "purple_2"
COLOR_ORANGE: str = "orange"
COLOR_FIRE_ORANGE: str = "fire_orange"
COLOR_GREEN_SCREEN_1: str = "green_screen_1"
COLOR_GREEN_SCREEN_2: str = "green_screen_2"
COLOR_GREEN_SCREEN_3: str = "green_screen_3"
color_dict: Dict[str, tuple[int, int, int]] = {
    COLOR_BLACK: (0, 0, 0),
    COLOR_WHITE: (255, 255, 255),
    COLOR_LIGHT_GRAY: (230, 230, 230),
    COLOR_GRAY: (190, 190, 190),
    COLOR_DARK_GRAY: (150, 150, 150),
    COLOR_BRIGHT_RED: (255, 0, 0),
    COLOR_RED: (200, 0, 0),
    COLOR_DARK_RED: (150, 0, 0),
    COLOR_BRIGHT_GREEN: (0, 255, 0),
    COLOR_GREEN: (0, 200, 0),
    COLOR_DARK_GREEN: (0, 150, 0),
    COLOR_BRIGHT_BLUE: (0, 0, 255),
    COLOR_BLUE: (0, 0, 200),
    COLOR_DARK_BLUE: (0, 0, 150),
    COLOR_YELLOW: (255, 255, 0),
    COLOR_BROWN: (85, 53, 22),
    COLOR_BLONDE: (188, 175, 123),
    COLOR_PURPLE: (127, 0, 170),
    COLOR_TRANSPARENT: (1, 1, 1),
    COLOR_GREEN_ICON: (15, 154, 54),
    COLOR_YELLOW_ICON: (255, 242, 0),
    COLOR_RED_ICON: (231, 0, 46),
    COLOR_GRAY_2: (180, 180, 180),
    COLOR_BRIGHT_GREEN_2: (0, 230, 41),
    COLOR_BRIGHT_BLUE_2: (41, 168, 255),
    COLOR_PURPLE_2: (201, 98, 255),
    COLOR_ORANGE: (255, 157, 77),
    COLOR_FIRE_ORANGE: (245, 66, 0),
    COLOR_GREEN_SCREEN_1: (62, 82, 82),
    COLOR_GREEN_SCREEN_2: (70, 70, 92),
    COLOR_GREEN_SCREEN_3: (110, 107, 3),
}

quality_colors: Dict[str, tuple[int, int, int]] = {
    1: color_dict[COLOR_GRAY_2],
    2: color_dict[COLOR_WHITE],
    3: color_dict[COLOR_BRIGHT_GREEN_2],
    4: color_dict[COLOR_BRIGHT_BLUE_2],
    5: color_dict[COLOR_PURPLE_2],
    6: color_dict[COLOR_ORANGE],
}

green_screen_colors: List[tuple[int, int, int]] = [
    color_dict[COLOR_GREEN_SCREEN_1],
    color_dict[COLOR_GREEN_SCREEN_2],
    color_dict[COLOR_GREEN_SCREEN_3],
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
minister_limit: int = 17

worker_upkeep_increment: float = 0.25
base_upgrade_price: float = 20.0  # 20 for 1st upgrade, 40 for 2nd, 80 for 3rd, etc.
consumer_goods_starting_price: int = 1

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
    "show_clouds": {
        "default": "Toggles cloud visibility on explored tiles",
        "True": "Currently showing clouds, even on explored tiles",
        "False": "Currently showing clouds on unexplored tiles only",
    },
    "god_mode": {
        "default": "Toggles god mode, allowing manual control of planetary global/local parameters",
        "True": "God mode currently enabled",
        "False": "God mode currently disabled",
    },
    "earth_preset": {
        "default": "Creates an Earth-like planet",
        "True": "Earth-like planet creation enabled",
        "False": "Earth-like planet creation disabled",
    },
    "mars_preset": {
        "default": "Creates a Mars-like planet",
        "True": "Mars-like planet creation enabled",
        "False": "Mars-like planet creation disabled",
    },
    "venus_preset": {
        "default": "Creates a Venus-like planet",
        "True": "Venus-like planet creation enabled",
        "False": "Venus-like planet creation disabled",
    },
}

world_dimensions_options: List[int] = None
earth_dimensions: int = None

EARTH: str = "earth"

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
# Create interface that conveys total pressure w/ proportions as well as quantities of O2, GHG, inert gases, toxic gases, followed by total water, radiation, and magnetic field
#   - ~8 labels

PRESSURE: str = "pressure"
OXYGEN: str = "oxygen"
GHG: str = "GHG"
INERT_GASES: str = "inert_gases"
TOXIC_GASES: str = "toxic_gases"
ATMOSPHERE_COMPONENTS: str = [OXYGEN, GHG, INERT_GASES, TOXIC_GASES]
GRAVITY: str = "gravity"
RADIATION: str = "radiation"
MAGNETIC_FIELD: str = "magnetic_field"
global_parameters: List[str] = [
    PRESSURE,
    OXYGEN,
    GHG,
    INERT_GASES,
    TOXIC_GASES,
    GRAVITY,
    RADIATION,
    MAGNETIC_FIELD,
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

DEFAULT_MINISTER_OUTFIT_TYPE = "business"

HAT_LEVEL: int = 9
EYES_LEVEL: int = 3
GLASSES_LEVEL: int = 4
HAIR_LEVEL: int = 5
FACIAL_HAIR_LEVEL: int = 8
PORTRAIT_LEVEL: int = 10
LABEL_LEVEL: int = 11
FRONT_LEVEL: int = 20
BACKGROUND_LEVEL: int = -5
DEFAULT_LEVEL: int = 2
BACKPACK_LEVEL: int = 1

ALTITUDE_BRIGHTNESS_MULTIPLIER: float = 0.5
PIXELLATED_SIZE: int = 2
LIGHT_PIXELLATED_SIZE: int = 70
if effect_manager.effect_active("speed_loading"):
    DETAIL_LEVEL: float = 1.0
    BUNDLE_IMAGE_DETAIL_LEVEL: float = 0.1
    BUTTON_DETAIL_LEVEL: float = 1.0
    GLOBE_PROJECTION_DETAIL_LEVEL: float = 1.0
    TERRAIN_DETAIL_LEVEL: float = 0.1
    CLOUDS_DETAIL_LEVEL: float = 0.1
else:
    DETAIL_LEVEL: float = 1.0
    BUNDLE_IMAGE_DETAIL_LEVEL: float = 0.5
    BUTTON_DETAIL_LEVEL: float = 1.0
    GLOBE_PROJECTION_DETAIL_LEVEL: float = 1.0
    TERRAIN_DETAIL_LEVEL: float = 0.5
    CLOUDS_DETAIL_LEVEL: float = 0.15

TERRAIN_KNOWLEDGE: str = "terrain"
TERRAIN_KNOWLEDGE_REQUIREMENT: int = 0
TERRAIN_PARAMETER_KNOWLEDGE: str = "terrain_parameter"
TERRAIN_PARAMETER_KNOWLEDGE_REQUIREMENT: int = 0

WORLD_GREEN_SCREEN_DEFAULTS: str = "world_green_screen_defaults"
TIME_PASSING_ROTATION: int = 0
TIME_PASSING_INITIAL_ORIENTATION: int = 0
TIME_PASSING_EQUATORIAL_COORDINATES: List[Tuple[int, int]] = []
TIME_PASSING_TARGET_ROTATIONS: int = 3
TIME_PASSING_EARTH_ROTATIONS: int = 0
TIME_PASSING_ITERATIONS: int = 0
TIME_PASSING_EARTH_SCHEDULE: List[bool] = []
TIME_PASSING_PLANET_SCHEDULE: List[bool] = []


def update_terrain_knowledge_requirements():
    global TERRAIN_KNOWLEDGE_REQUIREMENT, TERRAIN_PARAMETER_KNOWLEDGE_REQUIREMENT
    TERRAIN_KNOWLEDGE_REQUIREMENT = (
        0 if effect_manager.effect_active("remove_fog_of_war") else 1
    )
    TERRAIN_PARAMETER_KNOWLEDGE_REQUIREMENT = (
        0 if effect_manager.effect_active("remove_fog_of_war") else 2
    )


update_terrain_knowledge_requirements()

UNIQUE_FEATURE_TRACKING: str = "unique"
LIST_FEATURE_TRACKING: str = "list"

MAP_MODE_ALPHA: int = 0

SETTLEMENT_PANEL: str = "settlement_panel"
LOCAL_CONDITIONS_PANEL: str = "local_conditions_panel"
GLOBAL_CONDITIONS_PANEL: str = "global_conditions_panel"
TEMPERATURE_BREAKDOWN_PANEL: str = "temperature_breakdown_panel"

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

social_status_description_dict: Dict[int, str] = {
    1: "low",
    2: "moderate",
    3: "high",
    4: "very high",
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
COLONISTS: str = "colonists"
TRAIN: str = "train"
COLONY_SHIP: str = "colony_ship"
SPACESHIP: str = "spaceship"
BOAT: str = "boat"
OFFICER: str = "officer"
EXPLORER: str = "explorer"
ENGINEER: str = "engineer"
DRIVER: str = "driver"
FOREMAN: str = "foreman"
MERCHANT: str = "merchant"
EVANGELIST: str = "evangelist"
MAJOR: str = "major"
ASTRONAUT_COMMANDER: str = "astronaut_commander"
PORTERS: str = "porters"
WORK_CREW: str = "work_crew"
CONSTRUCTION_CREW: str = "construction_crew"
CARAVAN: str = "caravan"
MISSIONARIES: str = "missionaries"
EXPEDITION: str = "expedition"
BATTALION: str = "battalion"
ASTRONAUTS: str = "astronauts"

RAILROAD: str = "railroad"
ROAD: str = "road"
ROAD_BRIDGE: str = "road_bridge"
RAILROAD_BRIDGE: str = "railroad_bridge"
FERRY: str = "ferry"
INFRASTRUCTURE: str = "infrastructure"
FORT: str = "fort"
TRAIN_STATION: str = "train_station"
SPACEPORT: str = "spaceport"
WAREHOUSES: str = "warehouses"
WAREHOUSE_LEVEL: str = "warehouse_level"
RESOURCE: str = "resource"
RESOURCE_SCALE: str = "scale"
RESOURCE_EFFICIENCY: str = "efficiency"
SLUMS: str = "slums"
SETTLEMENT: str = "settlement"

CELL_ICON: str = "cell_icon"
NAME_ICON: str = "name_icon"
LOAN: str = "loan"
LOCATION: str = "location"
FULL_WORLD: str = "full_world"
ABSTRACT_WORLD: str = "abstract_world"
ORBITAL_WORLD: str = "orbital_world"
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
SELLABLE_ITEM_BUTTON: str = "sellable_item_button"
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
PICK_UP_EACH_ITEM_BUTTON: str = "pick_up_each_item_button"
SELL_EACH_ITEM_BUTTON: str = "sell_each_item_button"
DROP_EACH_ITEM_BUTTON: str = "drop_each_item_button"
SELL_ITEM_BUTTON: str = "sell_item_button"
SELL_ALL_ITEM_BUTTON: str = "sell_all_item_button"
USE_EQUIPMENT_BUTTON: str = "use_equipment_button"
REMOVE_EQUIPMENT_BUTTON: str = "remove_equipment_button"
RENAME_SETTLEMENT_BUTTON: str = "rename_settlement_button"
RENAME_PLANET_BUTTON: str = "rename_planet_button"
MINIMIZE_INTERFACE_COLLECTION_BUTTON: str = "minimize_interface_collection_button"
MOVE_INTERFACE_COLLECTION_BUTTON: str = "move_interface_collection_button"
RESET_INTERFACE_COLLECTION_BUTTON: str = "reset_interface_collection_button"

RECRUITMENT_CHOICE_BUTTON: str = "recruitment_choice_button"
CHOICE_CONFIRM_MAIN_MENU_BUTTON: str = "choice_confirm_main_menu_button"
CHOICE_QUIT_BUTTON: str = "choice_quit_button"
CHOICE_END_TURN_BUTTON: str = "choice_end_turn_button"
CHOICE_CONFIRM_FIRE_MINISTER_BUTTON: str = "choice_confirm_fire_minister_button"
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
FIRE_MINISTER_BUTTON: str = "fire_minister_button"
REAPPOINT_MINISTER_BUTTON: str = "reappoint_minister_button"
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
HELP_BUTTON: str = "help_button"

SAME_TILE_ICON: str = "same_tile_icon"
MINISTER_PORTRAIT_IMAGE: str = "minister_portrait_image"
ITEM_ICON: str = "item_icon"
DIE_ELEMENT: str = "die_element"
PANEL_ELEMENT: str = "panel_element"
SAFE_CLICK_PANEL_ELEMENT: str = "safe_click_panel_element"
LABEL: str = "label"
VALUE_LABEL: str = "value_label"
MONEY_LABEL: str = "money_label"
ITEM_PRICES_LABEL: str = "item_prices_label"
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
MINISTER_ETHNICITY_LABEL: str = "minister_ethnicity_label"
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
UNIT_TYPE_LABEL: str = "unit_type_label"
OFFICER_NAME_LABEL: str = "officer_name_label"
GROUP_NAME_LABEL: str = "group_name_label"
MINISTER_LABEL: str = "minister_label"
OFFICER_LABEL: str = "officer_label"
WORKERS_LABEL: str = "workers_label"
MOVEMENT_LABEL: str = "movement_label"
EQUIPMENT_LABEL: str = "equipment_label"
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
PLANET_NAME_LABEL: str = "planet_name_label"
WATER_LABEL: str = "water_label"
TEMPERATURE_LABEL: str = "temperature_label"
LOCAL_AVERAGE_TEMPERATURE_LABEL: str = "local_average_temperature_label"
VEGETATION_LABEL: str = "vegetation_label"
ROUGHNESS_LABEL: str = "roughness_label"
SOIL_LABEL: str = "soil_label"
HABITABILITY_LABEL: str = "habitability_label"
ALTITUDE_LABEL: str = "altitude_label"
RESOURCE_LABEL: str = "resource_label"
PRESSURE_LABEL: str = "pressure_label"
OXYGEN_LABEL: str = "oxygen_label"
GHG_LABEL: str = "GHG_label"
INERT_GASES_LABEL: str = "inert_gases_label"
TOXIC_GASES_LABEL: str = "toxic_gases_label"
ATMOSPHERE_COMPONENT_LABELS: str = [
    OXYGEN_LABEL,
    GHG_LABEL,
    INERT_GASES_LABEL,
    TOXIC_GASES_LABEL,
]
AVERAGE_WATER_LABEL: str = "average_water_label"
AVERAGE_TEMPERATURE_LABEL: str = "average_temperature_label"
GRAVITY_LABEL: str = "gravity_label"
RADIATION_LABEL: str = "radiation_label"
MAGNETIC_FIELD_LABEL: str = "magnetic_field_label"
STAR_DISTANCE_LABEL: str = "star_distance_label"
INSOLATION_LABEL: str = "insolation_label"
GHG_EFFECT_LABEL: str = "GHG_effect_label"
WATER_VAPOR_EFFECT_LABEL: str = "water_vapor_effect_label"
ALBEDO_EFFECT_LABEL: str = "albedo_effect_label"
TOTAL_HEAT_LABEL: str = "total_heat_label"
TILE_INVENTORY_CAPACITY_LABEL: str = "tile_inventory_capacity_label"
MOB_INVENTORY_CAPACITY_LABEL: str = "mob_inventory_capacity_label"

FREE_IMAGE: str = "free_image"
ACTOR_DISPLAY_FREE_IMAGE: str = "actor_display_free_image"
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

MINI_GRID: str = "mini_grid"
ABSTRACT_GRID: str = "abstract_grid"

NOTIFICATION: str = "notification"
CHOICE_NOTIFICATION: str = "choice_notification"
ACTION_NOTIFICATION: str = "action_notification"
DICE_ROLLING_NOTIFICATION: str = "dice_rolling_notification"
OFF_TILE_EXPLORATION_NOTIFICATION: str = "off_tile_exploration_notification"

SPACESUITS_EQUIPMENT: str = "spacesuits"
CONSUMER_GOODS_ITEM: str = "consumer_goods"
FUEL_ITEM: str = "fuel"
ENERGY_ITEM: str = "energy"
FOOD_ITEM: str = "food"
WATER_ITEM: str = "water"
AIR_ITEM: str = "air"

UPKEEP_MISSING_PENALTY_DEATH: str = 4  # Highest penalty takes precedent
UPKEEP_MISSING_PENALTY_DEHYDRATION: str = 3
UPKEEP_MISSING_PENALTY_STARVATION: str = 2
UPKEEP_MISSING_PENALTY_MORALE: str = 1
UPKEEP_MISSING_PENALTY_NONE: str = 0
UPKEEP_MISSING_PENALTY_CODES: Dict[str, int] = {
    4: "death",
    3: "dehydration",
    2: "starvation",
    1: "morale",
    0: "none",
}

PMOB_PERMISSION: str = "pmob"
NPMOB_PERMISSION: str = "npmob"
VEHICLE_PERMISSION: str = "vehicle"
SPACESHIP_PERMISSION: str = "spaceship"
IN_VEHICLE_PERMISSION: str = "in_vehicle"
IN_GROUP_PERMISSION: str = "in_group"
IN_BUILDING_PERMISSION: str = "in_building"
TRAIN_PERMISSION: str = "train"
TRAVEL_PERMISSION: str = "travel"
TRAVELING_PERMISSION: str = "traveling"
MOVEMENT_DISABLED_PERMISSION: str = "movement_disabled"
INFINITE_MOVEMENT_PERMISSION: str = "infinite_movement"
CONSTANT_MOVEMENT_COST_PERMISSION: str = "constant_movement_cost"
ACTIVE_PERMISSION: str = "active_permission"
WALK_PERMISSION: str = "walk_permission"
SWIM_PERMISSION: str = "swim_permission"
ACTIVE_VEHICLE_PERMISSION: str = "active_vehicle"
INACTIVE_VEHICLE_PERMISSION: str = "inactive_vehicle"
OFFICER_PERMISSION: str = "officer"
WORKER_PERMISSION: str = "worker"
GROUP_PERMISSION: str = "group"
INIT_COMPLETE_PERMISSION: str = "init_complete"
DISORGANIZED_PERMISSION: str = "disorganized"
DEHYDRATION_PERMISSION: str = "dehydration"
STARVATION_PERMISSION: str = "starvation"
VETERAN_PERMISSION: str = "veteran"
DUMMY_PERMISSION: str = "dummy"
SPACESUITS_PERMISSION: str = "spacesuits"
SURVIVABLE_PERMISSION: str = "survivable"

EXPEDITION_PERMISSION: str = "expedition"
CONSTRUCTION_PERMISSION: str = "construction"
WORK_CREW_PERMISSION: str = "work_crew"
CARAVAN_PERMISSION: str = "caravan"
MISSIONARIES_PERMISSION: str = "missionaries"
BATTALION_PERMISSION: str = "battalion"
ASTRONAUTS_PERMISSION: str = "astronauts"
PORTERS_PERMISSION: str = "porters"

EXPLORER_PERMISSION: str = "explorer"
ENGINEER_PERMISSION: str = "engineer"
DRIVER_PERMISSION: str = "driver"
FOREMAN_PERMISSION: str = "foreman"
MERCHANT_PERMISSION: str = "merchant"
EVANGELIST_PERMISSION: str = "evangelist"
MAJOR_PERMISSION: str = "major"
ASTRONAUT_COMMANDER_PERMISSION: str = "astronaut_commander"

CREW_VEHICLE_PERMISSION: str = "crew_vehicle"
CREW_SPACESHIP_PERMISSION: str = "crew_spaceship"
CREW_TRAIN_PERMISSION: str = "crew_train"

DEFAULT_PERMISSIONS: Dict[str, Any] = {
    ACTIVE_PERMISSION: True,
    WALK_PERMISSION: True,
}

CREW_PERMISSIONS: Dict[str, Any] = {
    SPACESHIP: CREW_SPACESHIP_PERMISSION,
    COLONY_SHIP: CREW_SPACESHIP_PERMISSION,
    TRAIN: CREW_TRAIN_PERMISSION,
}

ALLOW_DISORGANIZED: bool = False

INITIAL_MONEY: int = 1000
INITIAL_PUBLIC_OPINION: int = 50

FULL_BODY_PORTRAIT_SECTION: str = "full_body"
OUTFIT_PORTRAIT_SECTION: str = "outfit"
SKIN_PORTRAIT_SECTION: str = "skin"
HAIR_PORTRAIT_SECTION: str = "hair"
FACIAL_HAIR_PORTAIT_SECTION: str = "facial_hair"
GLASSES_PORTRAIT_SECTION: str = "glasses"
BACKPACK_PORTRAIT_SECTION: str = "backpack"
HAT_PORTRAIT_SECTION: str = "hat"
NOSE_PORTRAIT_SECTION: str = "nose"
MOUTH_PORTRAIT_SECTION: str = "mouth"
EYES_PORTRAITS_SECTION: str = "eyes"
FRAME_PORTRAIT_SECTION: str = "frame"

MOB_ACTOR_TYPE: str = "mob"
MOB_INVENTORY_ACTOR_TYPE: str = "mob_inventory"
TILE_ACTOR_TYPE: str = "tile"
TILE_INVENTORY_ACTOR_TYPE: str = "tile_inventory"
BUILDING_ACTOR_TYPE: str = "building"
CELL_ICON_ACTOR_TYPE: str = "cell_icon"
MINISTER_ACTOR_TYPE: str = "minister"
PROSECUTION_ACTOR_TYPE: str = "prosecution"
DEFENSE_ACTOR_TYPE: str = "defense"

HABITABILITY_PERFECT: int = 5
HABITABILITY_TOLERABLE: int = 4
HABITABILITY_UNPLEASANT: int = 3
HABITABILITY_HOSTILE: int = 2
HABITABILITY_DANGEROUS: int = 1
HABITABILITY_DEADLY: int = 0
HABITABILITY_DESCRIPTIONS: Dict[int, str] = {
    HABITABILITY_PERFECT: "perfect",
    HABITABILITY_TOLERABLE: "tolerable",
    HABITABILITY_UNPLEASANT: "unpleasant",
    HABITABILITY_HOSTILE: "hostile",
    HABITABILITY_DANGEROUS: "dangerous",
    HABITABILITY_DEADLY: "deadly",
}

ABSOLUTE_ZERO: float = -459.67

HELP_GLOBAL_PARAMETERS: str = "help_subjects_global_parameters"
HELP_WORLD_HANDLER_CONTEXT: str = "help_subjects_world_handler_context"

DEADLY_PARAMETER_BOUNDS: Dict[str, Tuple[float, float]] = {
    PRESSURE: (0.12, 30),
    OXYGEN: (0.1, None),
    GHG: (None, 0.03),
    INERT_GASES: (None, None),
    TOXIC_GASES: (None, 0.004),
    GRAVITY: (None, None),
    RADIATION: (None, 4),
}

PERFECT_PARAMETER_BOUNDS: Dict[str, Tuple[float, float]] = {
    PRESSURE: (0.9, 1.1),
    OXYGEN: (0.2, 0.22),
    GHG: (None, 0.006),
    INERT_GASES: (0.76, 0.8),
    TOXIC_GASES: (None, 0.0005),
    GRAVITY: (0.8, 1.2),
    RADIATION: (0, 0),
}
