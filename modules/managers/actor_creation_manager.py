# Contains actor/interface element creation factory singleton

import random
from modules.constructs.actor_types import locations, mobs
from modules.constructs.actor_types.mob_types import (
    vehicles,
    officers,
    dummy,
    workers,
    groups,
)
from modules.constructs.actor_types.mob_types.group_types import (
    battalions,
    expeditions,
    work_crews,
)
from modules.interface_components import (
    dice,
    buttons,
    labels,
    panels,
    notifications,
    choice_notifications,
    instructions,
    action_notifications,
    interface_elements,
    earth_transactions,
    inventory_interface,
    grids,
)
from modules.interface_components.info_display_elements import (
    info_display_buttons,
    info_display_labels,
    info_display_images,
)
from modules.constructs import (
    buildings,
    hosted_icons,
    ministers,
    images,
    settlements,
    unit_types,
    world_handler_types,
)
from modules.util import utility, actor_utility, market_utility
from modules.managers import mouse_follower
from modules.constants import constants, status, flags


class actor_creation_manager:
    """
    Object that creates new mobs and buildings based on inputted values
        Allows getting instance from anywhere and creating actors without importing respective actor module
    """

    def __init__(self):
        """
        Initializes this object
        """
        self.actor_constructors = {
            constants.MOB: mobs.mob,
            constants.COLONISTS: workers.worker,
            constants.TRAIN: vehicles.vehicle,
            constants.COLONY_SHIP: vehicles.vehicle,
            constants.EXPLORER: officers.officer,
            constants.ENGINEER: officers.officer,
            constants.DRIVER: officers.officer,
            constants.FOREMAN: officers.officer,
            constants.MERCHANT: officers.officer,
            constants.EVANGELIST: officers.officer,
            constants.MAJOR: officers.officer,
            constants.ASTRONAUT_COMMANDER: officers.officer,
            constants.PORTERS: groups.group,
            constants.WORK_CREW: work_crews.work_crew,
            constants.CONSTRUCTION_CREW: groups.group,
            constants.CARAVAN: groups.group,
            constants.MISSIONARIES: groups.group,
            constants.EXPEDITION: expeditions.expedition,
            constants.BATTALION: battalions.battalion,
            constants.ASTRONAUTS: groups.group,
            constants.INFRASTRUCTURE: buildings.infrastructure_building,
            constants.FORT: buildings.building,
            constants.TRAIN_STATION: buildings.building,
            constants.SPACEPORT: buildings.building,
            constants.WAREHOUSES: buildings.warehouses,
            constants.RESOURCE: buildings.resource_building,
            constants.SETTLEMENT: settlements.settlement,
            constants.LOAN: market_utility.loan,
            constants.LOCATION: locations.location,
            constants.FULL_WORLD: world_handler_types.full_world_handler,
            constants.ABSTRACT_WORLD: world_handler_types.abstract_world_handler,
            constants.ORBITAL_WORLD: world_handler_types.orbital_world_handler,
        }
        self.interface_constructors = {
            constants.BUTTON: buttons.button,
            constants.NEW_GAME_BUTTON: buttons.button,
            constants.LOAD_GAME_BUTTON: buttons.button,
            constants.CYCLE_UNITS_BUTTON: buttons.button,
            constants.WAKE_UP_ALL_BUTTON: buttons.button,
            constants.GENERATE_CRASH_BUTTON: buttons.button,
            constants.EXECUTE_MOVEMENT_ROUTES_BUTTON: buttons.button,
            constants.MOVE_LEFT_BUTTON: buttons.button,
            constants.MOVE_RIGHT_BUTTON: buttons.button,
            constants.MOVE_UP_BUTTON: buttons.button,
            constants.MOVE_DOWN_BUTTON: buttons.button,
            constants.SAVE_GAME_BUTTON: buttons.button,
            constants.USE_EACH_EQUIPMENT_BUTTON: buttons.button,
            constants.SELL_ITEM_BUTTON: buttons.button,
            constants.SELL_ALL_ITEM_BUTTON: buttons.button,
            constants.SELL_EACH_ITEM_BUTTON: buttons.button,
            constants.DROP_EACH_ITEM_BUTTON: buttons.button,
            constants.PICK_UP_EACH_ITEM_BUTTON: buttons.button,
            constants.USE_EQUIPMENT_BUTTON: buttons.button,
            constants.RENAME_SETTLEMENT_BUTTON: buttons.button,
            constants.RENAME_PLANET_BUTTON: buttons.button,
            constants.MINIMIZE_INTERFACE_COLLECTION_BUTTON: buttons.button,
            constants.MOVE_INTERFACE_COLLECTION_BUTTON: buttons.button,
            constants.RESET_INTERFACE_COLLECTION_BUTTON: buttons.button,
            constants.BUILD_TRAIN_BUTTON: buttons.button,
            constants.INTERFACE_ELEMENT: interface_elements.interface_element,
            constants.INTERFACE_COLLECTION: interface_elements.interface_collection,
            constants.AUTOFILL_COLLECTION: interface_elements.autofill_collection,
            constants.ORDERED_COLLECTION: interface_elements.ordered_collection,
            constants.INVENTORY_GRID: inventory_interface.inventory_grid,
            constants.TABBED_COLLECTION: interface_elements.tabbed_collection,
            constants.END_TURN_BUTTON: buttons.end_turn_button,
            constants.CYCLE_SAME_LOCATION_BUTTON: buttons.cycle_same_location_button,
            constants.FIRE_UNIT_BUTTON: buttons.fire_unit_button,
            constants.SWITCH_GAME_MODE_BUTTON: buttons.switch_game_mode_button,
            constants.CYCLE_AVAILABLE_MINISTERS_BUTTON: buttons.cycle_available_ministers_button,
            constants.SELLABLE_ITEM_BUTTON: buttons.sellable_item_button,
            constants.SHOW_PREVIOUS_REPORTS_BUTTON: buttons.show_previous_reports_button,
            constants.TAB_BUTTON: buttons.tab_button,
            constants.REORGANIZE_UNIT_BUTTON: buttons.reorganize_unit_button,
            constants.CYCLE_AUTOFILL_BUTTON: buttons.cycle_autofill_button,
            constants.ANONYMOUS_BUTTON: buttons.anonymous_button,
            constants.ACTION_BUTTON: buttons.action_button,
            constants.SCROLL_BUTTON: buttons.scroll_button,
            constants.REMOVE_EQUIPMENT_BUTTON: buttons.remove_equipment_button,
            constants.MAP_MODE_BUTTON: buttons.map_mode_button,
            constants.INSTRUCTIONS_BUTTON: instructions.instructions_button,
            constants.CHOICE_BUTTON: choice_notifications.choice_button,
            constants.RECRUITMENT_CHOICE_BUTTON: choice_notifications.recruitment_choice_button,
            constants.RECRUITMENT_BUTTON: earth_transactions.recruitment_button,
            constants.BUY_ITEM_BUTTON: earth_transactions.buy_item_button,
            constants.EMBARK_ALL_PASSENGERS_BUTTON: info_display_buttons.embark_all_passengers_button,
            constants.DISEMBARK_ALL_PASSENGERS_BUTTON: info_display_buttons.disembark_all_passengers_button,
            constants.ENABLE_SENTRY_MODE_BUTTON: info_display_buttons.enable_sentry_mode_button,
            constants.DISABLE_SENTRY_MODE_BUTTON: info_display_buttons.disable_sentry_mode_button,
            constants.ENABLE_AUTOMATIC_REPLACEMENT_BUTTON: info_display_buttons.enable_automatic_replacement_button,
            constants.DISABLE_AUTOMATIC_REPLACEMENT_BUTTON: info_display_buttons.disable_automatic_replacement_button,
            constants.END_UNIT_TURN_BUTTON: info_display_buttons.end_unit_turn_button,
            constants.REMOVE_WORK_CREW_BUTTON: info_display_buttons.remove_work_crew_button,
            constants.DISEMBARK_VEHICLE_BUTTON: info_display_buttons.disembark_vehicle_button,
            constants.EMBARK_VEHICLE_BUTTON: info_display_buttons.embark_vehicle_button,
            constants.CYCLE_PASSENGERS_BUTTON: info_display_buttons.cycle_passengers_button,
            constants.CYCLE_WORK_CREWS_BUTTON: info_display_buttons.cycle_work_crews_button,
            constants.WORK_CREW_TO_BUILDING_BUTTON: info_display_buttons.work_crew_to_building_button,
            constants.SWITCH_THEATRE_BUTTON: info_display_buttons.switch_theatre_button,
            constants.APPOINT_MINISTER_BUTTON: info_display_buttons.appoint_minister_button,
            constants.FIRE_MINISTER_BUTTON: info_display_buttons.fire_minister_button,
            constants.REAPPOINT_MINISTER_BUTTON: info_display_buttons.reappoint_minister_button,
            constants.TO_TRIAL_BUTTON: info_display_buttons.to_trial_button,
            constants.FABRICATE_EVIDENCE_BUTTON: info_display_buttons.fabricate_evidence_button,
            constants.BRIBE_JUDGE_BUTTON: info_display_buttons.bribe_judge_button,
            constants.EXECUTE_AUTOMATIC_ROUTE_BUTTON: info_display_buttons.automatic_route_button,
            constants.DRAW_AUTOMATIC_ROUTE_BUTTON: info_display_buttons.automatic_route_button,
            constants.CLEAR_AUTOMATIC_ROUTE_BUTTON: info_display_buttons.automatic_route_button,
            constants.TOGGLE_BUTTON: info_display_buttons.toggle_button,
            constants.CHANGE_PARAMETER_BUTTON: info_display_buttons.change_parameter_button,
            constants.HELP_BUTTON: info_display_buttons.help_button,
            constants.SAME_LOCATION_ICON: buttons.same_location_icon,
            constants.MINISTER_PORTRAIT_IMAGE: buttons.minister_portrait_image,
            constants.ITEM_ICON: inventory_interface.item_icon,
            constants.DIE_ELEMENT: dice.die,
            constants.PANEL_ELEMENT: panels.panel,
            constants.SAFE_CLICK_PANEL_ELEMENT: panels.safe_click_panel,
            constants.LABEL: labels.label,
            constants.VALUE_LABEL: labels.value_label,
            constants.MONEY_LABEL: labels.money_label,
            constants.ITEM_PRICES_LABEL: labels.item_prices_label_template,
            constants.MULTI_LINE_LABEL: labels.multi_line_label,
            constants.ACTOR_DISPLAY_LABEL: info_display_labels.actor_display_label,
            constants.MINISTER_NAME_LABEL: info_display_labels.actor_display_label,
            constants.MINISTER_BACKGROUND_LABEL: info_display_labels.actor_display_label,
            constants.MINISTER_OFFICE_LABEL: info_display_labels.actor_display_label,
            constants.MINISTER_SOCIAL_STATUS_LABEL: info_display_labels.actor_display_label,
            constants.MINISTER_ETHNICITY_LABEL: info_display_labels.actor_display_label,
            constants.MINISTER_INTERESTS_LABEL: info_display_labels.actor_display_label,
            constants.MINISTER_LOYALTY_LABEL: info_display_labels.actor_display_label,
            constants.MINISTER_ABILITY_LABEL: info_display_labels.actor_display_label,
            constants.SPACE_SKILL_LABEL: info_display_labels.actor_display_label,
            constants.ECOLOGY_SKILL_LABEL: info_display_labels.actor_display_label,
            constants.TERRAN_AFFAIRS_SKILL_LABEL: info_display_labels.actor_display_label,
            constants.SCIENCE_SKILL_LABEL: info_display_labels.actor_display_label,
            constants.ENERGY_SKILL_LABEL: info_display_labels.actor_display_label,
            constants.INDUSTRY_SKILL_LABEL: info_display_labels.actor_display_label,
            constants.TRANSPORTATION_SKILL_LABEL: info_display_labels.actor_display_label,
            constants.SECURITY_SKILL_LABEL: info_display_labels.actor_display_label,
            constants.EVIDENCE_LABEL: info_display_labels.actor_display_label,
            constants.UNIT_TYPE_LABEL: info_display_labels.actor_display_label,
            constants.OFFICER_NAME_LABEL: info_display_labels.actor_display_label,
            constants.GROUP_NAME_LABEL: info_display_labels.actor_display_label,
            constants.MINISTER_LABEL: info_display_labels.actor_display_label,
            constants.OFFICER_LABEL: info_display_labels.actor_display_label,
            constants.WORKERS_LABEL: info_display_labels.actor_display_label,
            constants.MOVEMENT_LABEL: info_display_labels.actor_display_label,
            constants.EQUIPMENT_LABEL: info_display_labels.actor_display_label,
            constants.COMBAT_STRENGTH_LABEL: info_display_labels.actor_display_label,
            constants.ATTITUDE_LABEL: info_display_labels.actor_display_label,
            constants.CONTROLLABLE_LABEL: info_display_labels.actor_display_label,
            constants.CREW_LABEL: info_display_labels.actor_display_label,
            constants.PASSENGERS_LABEL: info_display_labels.actor_display_label,
            constants.COORDINATES_LABEL: info_display_labels.actor_display_label,
            constants.KNOWLEDGE_LABEL: info_display_labels.actor_display_label,
            constants.TERRAIN_LABEL: info_display_labels.actor_display_label,
            constants.PLANET_NAME_LABEL: info_display_labels.actor_display_label,
            constants.WATER_LABEL: info_display_labels.actor_display_label,
            constants.TEMPERATURE_LABEL: info_display_labels.actor_display_label,
            constants.LOCAL_AVERAGE_TEMPERATURE_LABEL: info_display_labels.actor_display_label,
            constants.VEGETATION_LABEL: info_display_labels.actor_display_label,
            constants.ROUGHNESS_LABEL: info_display_labels.actor_display_label,
            constants.SOIL_LABEL: info_display_labels.actor_display_label,
            constants.HABITABILITY_LABEL: info_display_labels.actor_display_label,
            constants.ALTITUDE_LABEL: info_display_labels.actor_display_label,
            constants.RESOURCE_LABEL: info_display_labels.actor_display_label,
            constants.PRESSURE_LABEL: info_display_labels.actor_display_label,
            constants.OXYGEN_LABEL: info_display_labels.actor_display_label,
            constants.GHG_LABEL: info_display_labels.actor_display_label,
            constants.INERT_GASES_LABEL: info_display_labels.actor_display_label,
            constants.TOXIC_GASES_LABEL: info_display_labels.actor_display_label,
            constants.AVERAGE_WATER_LABEL: info_display_labels.actor_display_label,
            constants.AVERAGE_TEMPERATURE_LABEL: info_display_labels.actor_display_label,
            constants.GRAVITY_LABEL: info_display_labels.actor_display_label,
            constants.RADIATION_LABEL: info_display_labels.actor_display_label,
            constants.MAGNETIC_FIELD_LABEL: info_display_labels.actor_display_label,
            constants.STAR_DISTANCE_LABEL: info_display_labels.actor_display_label,
            constants.INSOLATION_LABEL: info_display_labels.actor_display_label,
            constants.GHG_EFFECT_LABEL: info_display_labels.actor_display_label,
            constants.WATER_VAPOR_EFFECT_LABEL: info_display_labels.actor_display_label,
            constants.ALBEDO_EFFECT_LABEL: info_display_labels.actor_display_label,
            constants.TOTAL_HEAT_LABEL: info_display_labels.actor_display_label,
            constants.MOB_INVENTORY_CAPACITY_LABEL: info_display_labels.actor_display_label,
            constants.LOCATION_INVENTORY_CAPACITY_LABEL: info_display_labels.actor_display_label,
            constants.INVENTORY_NAME_LABEL: info_display_labels.actor_display_label,
            constants.INVENTORY_QUANTITY_LABEL: info_display_labels.actor_display_label,
            constants.SETTLEMENT: info_display_labels.actor_display_label,
            constants.RESOURCE: info_display_labels.actor_display_label,
            constants.SPACEPORT: info_display_labels.actor_display_label,
            constants.INFRASTRUCTURE: info_display_labels.actor_display_label,
            constants.TRAIN_STATION: info_display_labels.actor_display_label,
            constants.FORT: info_display_labels.actor_display_label,
            constants.WAREHOUSES: info_display_labels.actor_display_label,
            constants.TERRAIN_FEATURE_LABEL: info_display_labels.terrain_feature_label,
            constants.CURRENT_PASSENGER_LABEL: info_display_labels.list_item_label,
            constants.ACTOR_TOOLTIP_LABEL: info_display_labels.actor_tooltip_label,
            constants.LIST_ITEM_LABEL: info_display_labels.list_item_label,
            constants.BUILDING_WORK_CREWS_LABEL: info_display_labels.building_work_crews_label,
            constants.BUILDING_EFFICIENCY_LABEL: info_display_labels.building_efficiency_label,
            constants.TERRAIN_FEATURE_LABEL: info_display_labels.terrain_feature_label,
            constants.BANNER_LABEL: info_display_labels.banner,
            constants.FREE_IMAGE: images.free_image,
            constants.ACTOR_DISPLAY_FREE_IMAGE: info_display_images.actor_display_free_image,
            constants.LABEL_IMAGE: info_display_images.label_image,
            constants.BACKGROUND_IMAGE: images.background_image,
            constants.TOOLTIP_FREE_IMAGE: images.tooltip_free_image,
            constants.MINISTER_TYPE_IMAGE: images.minister_type_image,
            constants.DICE_ROLL_MINISTER_IMAGE: images.dice_roll_minister_image,
            constants.INDICATOR_IMAGE: images.indicator_image,
            constants.WARNING_IMAGE: images.warning_image,
            constants.LOADING_IMAGE_TEMPLATE_IMAGE: images.loading_image_template,
            constants.MOUSE_FOLLOWER_IMAGE: mouse_follower.mouse_follower,
            constants.DIRECTIONAL_INDICATOR_IMAGE: images.directional_indicator_image,
            constants.NOTIFICATION: notifications.notification,
            constants.CHOICE_NOTIFICATION: choice_notifications.choice_notification,
            constants.ACTION_NOTIFICATION: action_notifications.action_notification,
            constants.DICE_ROLLING_NOTIFICATION: action_notifications.dice_rolling_notification,
            constants.ADJACENT_LOCATION_EXPLORATION_NOTIFICATION: action_notifications.adjacent_location_exploration_notification,
            constants.MINI_GRID: grids.mini_grid,
            constants.ABSTRACT_GRID: grids.abstract_grid,
            constants.HOSTED_ICON: hosted_icons.hosted_icon,
        }

    def create(self, from_save, input_dict):
        """
        Description:
            Initializes a mob, building, cell icon, or loan based on inputted values
        Input:
            boolean from_save: True if the object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize the object, with contents varying based on the type of object
                'init_type': string value - Always required, determines type of object created
        Output:
            actor: Returns the mob or building that was created
        """
        return self.actor_constructors[input_dict["init_type"]](from_save, input_dict)

    def create_dummy(self, input_dict=None):
        """
        Description:
            Creates a special fake version of a unit to display as a hypothetical, with the same images and tooltips as a real unit
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize the object, with contents varying based on the type of object
                'init_type': string value - Always required, determines type of object created
        Output:
            actor: Returns the unit that was created
        """
        if not input_dict:
            input_dict = {}
        new_actor = dummy.dummy(input_dict)
        return new_actor

    def create_interface_element(self, input_dict):
        """
        Description:
            Initializes an interface element based on inputted values
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize the object, with contents varying based on the type of object
                'init_type': string value - Always required, determines type of object created
        Output:
            actor: Returns the interface element created
        """
        return self.interface_constructors[input_dict["init_type"]](input_dict)

    def display_recruitment_choice_notification(
        self, recruitment_type: unit_types.unit_type
    ):
        """
        Description:
            Displays a choice notification to verify the recruitment of a unit
        Input:
            unit_type recruitment_type: Type of unit to recruit
        Output:
            None
        """
        if recruitment_type.number >= 2:
            message = f"Are you sure you want to {recruitment_type.recruitment_verb} a unit of {recruitment_type.name} for {recruitment_type.recruitment_cost} money? /n /n"
        else:
            message = f"Are you sure you want to {recruitment_type.recruitment_verb} {utility.generate_article(recruitment_type.name)} {recruitment_type.name} for {recruitment_type.recruitment_cost} money? /n /n"
        message += recruitment_type.get_string_description()

        constants.NotificationManager.display_notification(
            {
                "message": message,
                "choices": [constants.RECRUITMENT_CHOICE_BUTTON, None],
                "extra_parameters": {
                    "recruitment_type": recruitment_type,
                },
            }
        )

    def create_group(
        self, worker, officer
    ):  # Use when merging groups. At beginning of game, instead of using this, create a group which creates its worker and officer and merges them
        """
        Description:
            Creates a group out of the inputted worker and officer. Once the group is created, it's component officer and worker will not be able to be directly seen or interacted with until the group is disbanded
                independently until the group is disbanded
        Input:
            worker worker: worker to create a group out of
            officer officer: officer to create a group out of
        Output:
            None
        """
        return self.create(
            False,
            {
                "location": worker.location,
                "worker": worker,
                "officer": officer,
                "init_type": officer.unit_type.group_type.key,
                "name": actor_utility.generate_group_name(worker, officer),
            },
        )

    def create_initial_ministers(self):
        """
        Creates a varying number of unappointed ministers at the start of the game
        """
        if constants.EffectManager.effect_active("speed_loading"):
            for i in range(8):
                self.create_minister(False, {})
        else:
            for i in range(0, constants.minister_limit - 2 + random.randrange(-2, 3)):
                self.create_minister(False, {})

    def create_minister(self, from_save, input_dict):
        """
        Description:
            Creates either a new random minister with a randomized face, name, skills, and corruption threshold or loads a saved minister
        Input:
            boolean from_save: True if the object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize the object, with contents varying based on the type of object
        Output:
            None
        """
        ministers.minister(from_save, input_dict)
