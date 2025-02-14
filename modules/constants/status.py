import pygame
from typing import Dict, List, Any
from modules.actor_types.tiles import tile
from modules.actor_types.mobs import mob
from modules.constructs.ministers import minister
from modules.constructs.building_types import building_type
from modules.constructs.unit_types import unit_type, worker_type
from modules.constructs.equipment_types import equipment_type
from modules.constructs.item_types import item_type
from modules.constructs.minister_types import minister_type
from modules.constructs.terrain_feature_types import terrain_feature_type
from modules.constructs.images import image, free_image, directional_indicator_image
from modules.interface_types.interface_elements import (
    interface_collection,
    tabbed_collection,
    ordered_collection,
    autofill_collection,
)
from modules.interface_types.inventory_interface import inventory_grid
from modules.interface_types.grids import grid, mini_grid, abstract_grid
from modules.interface_types.world_grids import world_grid
from modules.interface_types.cells import cell
from modules.interface_types.panels import safe_click_panel
from modules.interface_types.notifications import notification
from modules.interface_types.buttons import (
    button,
    same_tile_icon,
    reorganize_unit_button,
    minister_portrait_image,
    switch_game_mode_button,
)
from modules.interface_types.inventory_interface import item_icon
from modules.interface_types.instructions import instructions_page
from modules.interface_types.dice import die
from modules.interface_types.labels import (
    item_prices_label_template,
    multi_line_label,
    label,
)
from modules.actor_types.actors import actor
from modules.actor_types.buildings import building, slums, resource_building
from modules.actor_types.mobs import mob
from modules.actor_types.mob_types.pmobs import pmob
from modules.actor_types.mob_types.npmobs import npmob
from modules.constructs.settlements import settlement
from modules.util.market_utility import loan
from modules.action_types.action import action
from modules.tools.effects import effect

strategic_map_grid: world_grid = None
scrolling_strategic_map_grid: mini_grid = None
minimap_grid: mini_grid = None
earth_grid: abstract_grid = None
globe_projection_grid: abstract_grid = None
planet_view_mask: free_image = None

actions: Dict[str, action] = {}

displayed_mob: mob = None
displayed_mob_inventory: item_icon = None
displayed_tile: tile = None
displayed_tile_inventory: item_icon = None
displayed_minister: minister = None
displayed_defense: minister = None
displayed_prosecution: minister = None
displayed_notification: notification = None

cached_images: Dict[str, pygame.Surface] = {}
globe_projection_image: free_image = None
globe_projection_surface: pygame.Surface = None
to_strategic_button: switch_game_mode_button = None
to_earth_button: switch_game_mode_button = None

button_list: List[button] = []
instructions_list: List[str] = []
minister_list: List[minister] = []
available_minister_list: List[minister] = []
building_types: Dict[str, building_type] = {}
unit_types: Dict[str, unit_type] = {}
worker_types: Dict[str, worker_type] = {}
recruitment_types: List[unit_type] = []
item_types: Dict[str, item_type] = {}
equipment_types: Dict[str, equipment_type] = {}
minister_types: Dict[str, minister_type] = {}
terrain_feature_types: Dict[str, terrain_feature_type] = {}
flag_icon_list: List[button] = []
grid_list: List[grid] = []
text_list: List[str] = []
free_image_list: List[free_image] = []
minister_image_list: List[Any] = []
available_minister_portrait_list: List[button] = []

actor_list: List[actor] = []
mob_list: List[mob] = []
pmob_list: List[pmob] = []
npmob_list: List[npmob] = []
settlement_list: List[settlement] = []
building_list: List[building] = []
slums_list: List[slums] = []
resource_building_list: List[resource_building] = []
loan_list: List[loan] = []
attacker_queue: List[npmob] = []
enemy_turn_queue: List[npmob] = []
player_turn_queue: List[pmob] = []
independent_interface_elements: List[Any] = []
dice_list: List[die] = []
draw_list: List[Any] = []
same_tile_icon_list: List[same_tile_icon] = []
directional_indicator_image_list: List[directional_indicator_image] = []

loading_image: image = None
loading_screen_quote_banner: multi_line_label = None
loading_screen_continue_banner: label = None
safe_click_area: safe_click_panel = None
info_displays_collection: interface_collection = None
grids_collection: interface_collection = None
mob_info_display: ordered_collection = None
mob_inventory_info_display: ordered_collection = None
mob_inventory_grid: inventory_grid = None
tile_info_display: ordered_collection = None
tile_inventory_info_display: ordered_collection = None
tile_inventory_grid: inventory_grid = None
minister_info_display: ordered_collection = None
prosecution_info_display: ordered_collection = None
defense_info_display: ordered_collection = None
mob_tabbed_collection: tabbed_collection = None
tile_tabbed_collection: tabbed_collection = None
mob_inventory_collection: ordered_collection = None
tile_inventory_collection: ordered_collection = None
mob_reorganization_collection: ordered_collection = None
group_reorganization_collection: autofill_collection = None
vehicle_reorganization_collection: autofill_collection = None
settlement_collection: ordered_collection = None
local_conditions_collection: ordered_collection = None
global_conditions_collection: ordered_collection = None
temperature_breakdown_collection: ordered_collection = None
item_prices_label: item_prices_label_template = None
reorganize_group_left_button: reorganize_unit_button = None
reorganize_group_right_button: reorganize_unit_button = None
reorganize_vehicle_left_button: reorganize_unit_button = None
reorganize_vehicle_right_button: reorganize_unit_button = None
minister_loading_image: minister_portrait_image = None
albedo_free_image: free_image = None
cursor_image: pygame.image = None
next_boarded_vehicle: pmob = None
text_box_destination: callable = None

current_instructions_page: instructions_page = None
current_ministers: Dict[str, minister] = {}
lore_types_effects_dict: Dict[str, effect] = {}
previous_production_report: str = None
previous_sales_report: str = None
previous_financial_report: str = None
transaction_history: Dict[str, float] = {}

initial_tutorial_completed: bool = False

# Status variables automatically updated when corresponding terrain features are created
north_pole: cell = None
south_pole: cell = None
equator_list: List[cell] = []
