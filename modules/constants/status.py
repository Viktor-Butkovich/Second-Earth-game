from __future__ import annotations
import pygame
from typing import Dict, List, Any
from modules.constructs.actor_types.mobs import mob
from modules.constructs.ministers import minister
from modules.constructs.building_types import building_type
from modules.constructs.unit_types import unit_type, worker_type
from modules.constructs.equipment_types import equipment_type
from modules.constructs.item_types import item_type
from modules.constructs.minister_types import minister_type
from modules.constructs.terrain_feature_types import terrain_feature_type
from modules.constructs.images import image, free_image, directional_indicator_image
from modules.constructs.actor_types.locations import location
from modules.constructs.world_handler_types import (
    abstract_world_handler,
    full_world_handler,
)
from modules.interface_components.interface_elements import (
    interface_collection,
    tabbed_collection,
    ordered_collection,
    autofill_collection,
)
from modules.interface_components.inventory_interface import inventory_grid
from modules.interface_components.grids import grid, location_grid, mini_grid
from modules.interface_components.panels import safe_click_panel
from modules.interface_components.notifications import notification
from modules.interface_components.buttons import (
    button,
    same_location_icon,
    reorganize_unit_button,
    switch_game_mode_button,
)
from modules.interface_components.inventory_interface import item_icon
from modules.interface_components.instructions import instructions_page
from modules.interface_components.dice import die
from modules.interface_components.labels import (
    item_prices_label_template,
    multi_line_label,
    label,
)
from modules.interface_components.info_display_elements.info_display_buttons import (
    actor_icon,
)
from modules.constructs.buildings import building, resource_building
from modules.constructs.actor_types.mobs import mob
from modules.constructs.actor_types.mob_types.pmobs import pmob
from modules.constructs.actor_types.mob_types.npmobs import npmob
from modules.constructs.world_handlers import world_handler
from modules.util.market_utility import loan
from modules.action_types.action import action
from modules.constructs.effects import effect

scrolling_strategic_map_grid: mini_grid = None
minimap_grid: mini_grid = None
planet_view_mask: free_image = None

actions: Dict[str, action] = {}

displayed_mob: mob = None
displayed_mob_inventory: item_icon = None
displayed_location: location = None
displayed_location_inventory: item_icon = None
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
location_grid_list: List[location_grid] = []
world_list: List[world_handler] = []
text_list: List[str] = []
free_image_list: List[free_image] = []
minister_image_list: List[Any] = []
available_minister_icon_list: List[actor_icon] = []

mob_list: List[mob] = []
pmob_list: List[pmob] = []
npmob_list: List[npmob] = []
building_list: List[building] = []
resource_building_list: List[resource_building] = []
loan_list: List[loan] = []
attacker_queue: List[npmob] = []
enemy_turn_queue: List[npmob] = []
player_turn_queue: List[pmob] = []
independent_interface_elements: List[Any] = []
dice_list: List[die] = []
draw_list: List[Any] = []
same_location_icon_list: List[same_location_icon] = []
directional_indicator_image_list: List[directional_indicator_image] = []
logistics_incident_list: List[Dict[str, Any]] = []

loading_image: image = None
loading_screen_quote_banner: multi_line_label = None
loading_screen_continue_banner: label = None
safe_click_area: safe_click_panel = None
info_displays_collection: interface_collection = None
grids_collection: interface_collection = None
mob_info_display: ordered_collection = None
mob_inventory_info_display: ordered_collection = None
mob_inventory_grid: inventory_grid = None
location_info_display: ordered_collection = None
location_inventory_info_display: ordered_collection = None
location_inventory_grid: inventory_grid = None
minister_info_display: ordered_collection = None
prosecution_info_display: ordered_collection = None
defense_info_display: ordered_collection = None
mob_tabbed_collection: tabbed_collection = None
location_tabbed_collection: tabbed_collection = None
mob_inventory_collection: ordered_collection = None
location_inventory_collection: ordered_collection = None
mob_reorganization_collection: ordered_collection = None
group_reorganization_collection: autofill_collection = None
vehicle_reorganization_collection: autofill_collection = None
settlement_collection: ordered_collection = None
local_conditions_collection: ordered_collection = None
global_conditions_collection: ordered_collection = None
temperature_breakdown_collection: ordered_collection = None
supply_chain_collection: ordered_collection = None
item_prices_label: item_prices_label_template = None
reorganize_group_left_button: reorganize_unit_button = None
reorganize_group_right_button: reorganize_unit_button = None
reorganize_vehicle_left_button: reorganize_unit_button = None
reorganize_vehicle_right_button: reorganize_unit_button = None
minister_loading_image: actor_icon = None
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
north_pole: location = None
south_pole: location = None
equator_list: List[location] = []

current_world: full_world_handler = None
earth_world: abstract_world_handler = None
