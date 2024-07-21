# Contains functionality for creating new instances of mobs, buildings, dice, and ministers

import random
from ...actor_types import mobs, buildings
from ...actor_types.mob_types import vehicles, officers, dummy, workers
from ...actor_types.mob_types.group_types import (
    battalions,
    caravans,
    construction_gangs,
    expeditions,
    missionaries,
    porters,
    work_crews,
)
from ...interface_types import (
    dice,
    buttons,
    labels,
    panels,
    notifications,
    choice_notifications,
    instructions,
    action_notifications,
    interface_elements,
    cell_icons,
    earth_transactions,
    inventory_interface,
)
from ...actor_display_tools import buttons as actor_display_buttons
from ...actor_display_tools import labels as actor_display_labels
from ...actor_display_tools import images as actor_display_images
from ...constructs import ministers, images, settlements
from ...util import utility, actor_utility, market_utility
from .. import mouse_followers
import modules.constants.constants as constants


class actor_creation_manager_template:  # can get instance from anywhere and create actors with it without importing respective actor module
    """
    Object that creates new mobs and buildings based on inputted values
    """

    def __init__(self):
        """
        Description:
            Initializes this object
        Input:
            None
        Output:
            None
        """
        return

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
        init_type = input_dict["init_type"]
        # mobs
        if init_type == "mob":
            new_actor = mobs.mob(from_save, input_dict)
        elif init_type == "workers":
            new_actor = workers.worker(from_save, input_dict)
        elif init_type == "church_volunteers":
            new_actor = workers.church_volunteers(from_save, input_dict)
        elif init_type == "train":
            new_actor = vehicles.train(from_save, input_dict)
        elif init_type == "ship":
            new_actor = vehicles.ship(from_save, input_dict)
        elif init_type == "boat":
            new_actor = vehicles.boat(from_save, input_dict)
        elif init_type in constants.officer_types:
            new_actor = officers.officer(from_save, input_dict)

        # groups
        elif init_type == "porters":
            new_actor = porters.porters(from_save, input_dict)
        elif init_type == "work_crew":
            new_actor = work_crews.work_crew(from_save, input_dict)
        elif init_type == "construction_gang":
            new_actor = construction_gangs.construction_gang(from_save, input_dict)
        elif init_type == "caravan":
            new_actor = caravans.caravan(from_save, input_dict)
        elif init_type == "missionaries":
            new_actor = missionaries.missionaries(from_save, input_dict)
        elif init_type == "expedition":
            new_actor = expeditions.expedition(from_save, input_dict)
        elif init_type == "battalion":
            new_actor = battalions.battalion(from_save, input_dict)

        # buildings
        elif init_type == "infrastructure":
            new_actor = buildings.infrastructure_building(from_save, input_dict)
        elif init_type == "fort":
            new_actor = buildings.fort(from_save, input_dict)
        elif init_type == "train_station":
            new_actor = buildings.train_station(from_save, input_dict)
        elif init_type == "port":
            new_actor = buildings.port(from_save, input_dict)
        elif init_type == "warehouses":
            new_actor = buildings.warehouses(from_save, input_dict)
        elif init_type == "resource":
            new_actor = buildings.resource_building(from_save, input_dict)
        elif init_type == "slums":
            new_actor = buildings.slums(from_save, input_dict)
        elif init_type == "settlement":
            new_actor = settlements.settlement(from_save, input_dict)

        # cell icons
        elif init_type == "cell icon":
            new_actor = cell_icons.cell_icon(from_save, input_dict)
        elif init_type == "name icon":
            new_actor = cell_icons.name_icon(from_save, input_dict)

        # loans
        elif init_type == "loan":
            new_actor = market_utility.loan(from_save, input_dict)

        return new_actor

    def create_dummy(self, input_dict):
        """
        Description:
            Creates a special fake version of a unit to display as a hypothetical, with the same images and tooltips as a real unit
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize the object, with contents varying based on the type of object
                'init_type': string value - Always required, determines type of object created
        Output:
            actor: Returns the unit that was created
        """
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
        init_type = input_dict["init_type"]
        # interface elements
        if init_type == "button":
            new_element = buttons.button(input_dict)
        if init_type == "interface element":
            new_element = interface_elements.interface_element(input_dict)
        elif init_type == "interface collection":
            new_element = interface_elements.interface_collection(input_dict)
        elif init_type == "autofill collection":
            new_element = interface_elements.autofill_collection(input_dict)
        elif init_type == "ordered collection":
            new_element = interface_elements.ordered_collection(input_dict)
        elif init_type == "inventory grid":
            new_element = inventory_interface.inventory_grid(input_dict)
        elif init_type == "tabbed collection":
            new_element = interface_elements.tabbed_collection(input_dict)
        if init_type.endswith("button"):
            base = init_type.removesuffix("button")
            # buttons buttons
            if base == "":
                new_element = buttons.button(input_dict)
            else:
                base = base.removesuffix(" ")
                if base == "end turn":
                    new_element = buttons.end_turn_button(input_dict)
                elif base == "cycle same tile":
                    new_element = buttons.cycle_same_tile_button(input_dict)
                elif base == "fire unit":
                    new_element = buttons.fire_unit_button(input_dict)
                elif base == "switch game mode":
                    new_element = buttons.switch_game_mode_button(input_dict)
                elif base == "cycle available ministers":
                    new_element = buttons.cycle_available_ministers_button(input_dict)
                elif base == "commodity":
                    new_element = buttons.commodity_button(input_dict)
                elif base == "show previous reports":
                    new_element = buttons.show_previous_reports_button(input_dict)
                elif base == "tab":
                    new_element = buttons.tab_button(input_dict)
                elif base == "reorganize unit":
                    new_element = buttons.reorganize_unit_button(input_dict)
                elif base == "cycle autofill":
                    new_element = buttons.cycle_autofill_button(input_dict)
                elif base == "anonymous":
                    new_element = buttons.anonymous_button(input_dict)
                elif base == "action":
                    new_element = buttons.action_button(input_dict)
                elif base == "scroll":
                    new_element = buttons.scroll_button(input_dict)
                elif base == "remove equipment":
                    new_element = buttons.remove_equipment_button(input_dict)
                elif base == "map mode":
                    new_element = buttons.map_mode_button(input_dict)

                # instructions buttons
                elif base == "instructions":
                    new_element = instructions.instructions_button(input_dict)

                # choice_notifications buttons
                elif base == "choice":
                    new_element = choice_notifications.choice_button(input_dict)
                elif base == "recruitment choice":
                    new_element = choice_notifications.recruitment_choice_button(
                        input_dict
                    )
                elif base.endswith(
                    " choice"
                ):  # if given init type end turn choice button, base is end turn choice and button type is end turn as a choice button
                    base = base.removesuffix(" choice")
                    input_dict["button_type"] = base.removesuffix(" choice")
                    new_element = choice_notifications.choice_button(input_dict)

                # earth_transactions buttons
                elif base == "recruitment":
                    new_element = earth_transactions.recruitment_button(input_dict)
                elif base == "buy item":
                    new_element = earth_transactions.buy_item_button(input_dict)

                # actor_display_buttons buttons
                elif base == "embark all passengers":
                    new_element = actor_display_buttons.embark_all_passengers_button(
                        input_dict
                    )
                elif base == "disembark all passengers":
                    new_element = actor_display_buttons.disembark_all_passengers_button(
                        input_dict
                    )
                elif base == "enable sentry mode":
                    new_element = actor_display_buttons.enable_sentry_mode_button(
                        input_dict
                    )
                elif base == "disable sentry mode":
                    new_element = actor_display_buttons.disable_sentry_mode_button(
                        input_dict
                    )
                elif base == "enable automatic replacement":
                    new_element = (
                        actor_display_buttons.enable_automatic_replacement_button(
                            input_dict
                        )
                    )
                elif base == "disable automatic replacement":
                    new_element = (
                        actor_display_buttons.disable_automatic_replacement_button(
                            input_dict
                        )
                    )
                elif base == "end unit turn":
                    new_element = actor_display_buttons.end_unit_turn_button(input_dict)
                elif base == "remove work crew":
                    new_element = actor_display_buttons.remove_work_crew_button(
                        input_dict
                    )
                elif base == "disembark vehicle":
                    new_element = actor_display_buttons.disembark_vehicle_button(
                        input_dict
                    )
                elif base == "embark vehicle":
                    new_element = actor_display_buttons.embark_vehicle_button(
                        input_dict
                    )
                elif base == "cycle passengers":
                    new_element = actor_display_buttons.cycle_passengers_button(
                        input_dict
                    )
                elif base == "cycle work crews":
                    new_element = actor_display_buttons.cycle_work_crews_button(
                        input_dict
                    )
                elif base == "work crew to building":
                    new_element = actor_display_buttons.work_crew_to_building_button(
                        input_dict
                    )
                elif base == "switch theatre":
                    new_element = actor_display_buttons.switch_theatre_button(
                        input_dict
                    )
                elif base == "appoint minister":
                    new_element = actor_display_buttons.appoint_minister_button(
                        input_dict
                    )
                elif base == "remove minister":
                    new_element = actor_display_buttons.remove_minister_button(
                        input_dict
                    )
                elif base == "to trial":
                    new_element = actor_display_buttons.to_trial_button(input_dict)
                elif base == "fabricate evidence":
                    new_element = actor_display_buttons.fabricate_evidence_button(
                        input_dict
                    )
                elif base == "bribe judge":
                    new_element = actor_display_buttons.bribe_judge_button(input_dict)
                elif base == "recruit workers":
                    new_element = actor_display_buttons.recruit_workers_button(
                        input_dict
                    )
                elif base == "automatic route":
                    new_element = actor_display_buttons.automatic_route_button(
                        input_dict
                    )
                elif base == "toggle":
                    new_element = actor_display_buttons.toggle_button(input_dict)
                elif base == "change parameter":
                    new_element = actor_display_buttons.change_parameter_button(
                        input_dict
                    )
                else:  # if given init type cycle passengers button, will initialize as base button class with button type cycle passengers
                    input_dict["button_type"] = base
                    new_element = buttons.button(input_dict)
        elif init_type == "same tile icon":
            new_element = buttons.same_tile_icon(input_dict)
        elif (
            init_type == "minister portrait image"
        ):  # actually a button, fix misleading name eventually
            new_element = buttons.minister_portrait_image(input_dict)
        elif init_type == "item icon":
            new_element = inventory_interface.item_icon(input_dict)
        elif init_type == "die":
            new_element = dice.die(input_dict)
        elif init_type == "panel":
            new_element = panels.panel(input_dict)
        elif init_type == "safe click panel":
            new_element = panels.safe_click_panel(input_dict)

        elif init_type.endswith("label"):
            base = init_type.removesuffix("label")
            # labels labels
            if base == "":
                new_element = labels.label(input_dict)
            else:
                base = base.removesuffix(" ")
                if base == "value":
                    new_element = labels.value_label(input_dict)
                elif base == "money":
                    new_element = labels.money_label_template(input_dict)
                elif base == "commodity prices":
                    new_element = labels.commodity_prices_label_template(input_dict)
                elif base == "multi line":
                    new_element = labels.multi_line_label(input_dict)

                # actor display labels
                elif base == "actor display":
                    new_element = actor_display_labels.actor_display_label(input_dict)
                elif base == "actor tooltip":
                    new_element = actor_display_labels.actor_tooltip_label(input_dict)
                elif base == "list item":
                    new_element = actor_display_labels.list_item_label(input_dict)
                elif base == "building work crews":
                    new_element = actor_display_labels.building_work_crews_label(
                        input_dict
                    )
                elif base == "building efficiency":
                    new_element = actor_display_labels.building_efficiency_label(
                        input_dict
                    )
                elif base == "terrain feature":
                    new_element = actor_display_labels.terrain_feature_label(input_dict)
                elif base == "banner":
                    new_element = actor_display_labels.banner(input_dict)
                else:
                    new_element = actor_display_labels.actor_display_label(input_dict)
        elif init_type == "instructions page":
            new_element = instructions.instructions_page(input_dict)

        elif init_type.endswith("image"):
            base = init_type.removesuffix(" image")
            if base == "free":
                new_element = images.free_image(input_dict)
            elif base == "actor display free":
                new_element = actor_display_images.actor_display_free_image(input_dict)
            elif base == "mob background":
                new_element = actor_display_images.mob_background_image(input_dict)
            elif base == "minister background":
                new_element = actor_display_images.minister_background_image(input_dict)
            elif base == "label":
                new_element = actor_display_images.label_image(input_dict)
            elif base == "background":
                new_element = images.background_image(input_dict)
            elif base == "tooltip free":
                new_element = images.tooltip_free_image(input_dict)
            elif base == "minister type":
                new_element = images.minister_type_image(input_dict)
            elif base == "dice roll minister":
                new_element = images.dice_roll_minister_image(input_dict)
            elif base == "indicator":
                new_element = images.indicator_image(input_dict)
            elif base == "warning":
                new_element = images.warning_image(input_dict)
            elif base == "loading image template":
                new_element = images.loading_image_template(input_dict)
            elif base == "mouse follower":
                new_element = mouse_followers.mouse_follower_template(input_dict)
            elif base == "directional indicator":
                new_element = images.directional_indicator_image(input_dict)

        elif init_type.endswith("notification"):
            base = init_type.removesuffix("notification")
            # notifications notifications
            if base == "":
                new_element = notifications.notification(input_dict)
            else:
                base = base.removesuffix(" ")
                if base == "zoom":
                    new_element = notifications.zoom_notification(input_dict)

                # choice_notifications notifications
                elif base == "choice":
                    new_element = choice_notifications.choice_notification(input_dict)

                # action_notifications notifications
                elif base == "action":
                    new_element = action_notifications.action_notification(input_dict)
                elif base == "dice rolling":
                    new_element = action_notifications.dice_rolling_notification(
                        input_dict
                    )
                elif base == "off tile exploration":
                    new_element = (
                        action_notifications.off_tile_exploration_notification(
                            input_dict
                        )
                    )
                else:
                    new_element = notifications.notification(input_dict)
        new_element.showing = new_element.can_show()
        return new_element

    def display_recruitment_choice_notification(
        self, choice_info_dict, recruitment_name
    ):
        """
        Description:
            Displays a choice notification to verify the recruitment of a unit
        Input:
            dictionary choice_info_dict: dictionary containing various information needed for the choice notification
                'recruitment_type': string value - Type of unit to recruit, like 'European worker'
                'cost': double value - Recruitment cost of the unit
                'mob_image_id': string value - File path to the image used by the recruited unit
                'type': string value - Type of choice notification to display, always 'recruitment' for recruitment notificatoins
            string recruitment_name: Name used in the notification to signify the unit, like 'explorer'
        Output:
            None
        """
        recruitment_type = recruitment_name
        if recruitment_name in ["steamship"]:
            verb = "purchase"
        elif recruitment_name.endswith(" workers"):
            verb = "hire"
        else:
            verb = "recruit"

        if recruitment_name.endswith(" workers"):
            message = f"Are you sure you want to {verb} a unit of {recruitment_name} for {choice_info_dict['cost']} money? /n /n"
        else:
            message = f"Are you sure you want to {verb} {utility.generate_article(recruitment_name)} {recruitment_name} for {str(choice_info_dict['cost'])} money? /n /n"

        actor_utility.update_descriptions(recruitment_type)
        message += constants.string_descriptions[recruitment_type]

        constants.notification_manager.display_notification(
            {
                "message": message,
                "choices": ["recruitment", "none"],
                "extra_parameters": choice_info_dict,
            }
        )

    def create_group(
        self, worker, officer
    ):  # use when merging groups. At beginning of game, instead of using this, create a group which creates its worker and officer and merges them
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
                "coordinates": (officer.x, officer.y),
                "grids": officer.grids,
                "worker": worker,
                "officer": officer,
                "modes": officer.grids[
                    0
                ].modes,  # if created in Africa grid, should be ['strategic']. If created on Earth, should be ['strategic', 'earth']
                "init_type": constants.officer_group_type_dict[officer.officer_type],
                "image": "misc/empty.png",
                "name": actor_utility.generate_group_name(worker, officer),
            },
        )

    def create_initial_ministers(self):
        """
        Description:
            Creates a varying number of unappointed ministers at the start of the game
        Input:
            None
        Output:
            None
        """
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
