# Contains functionality for work crews

import random
from modules.actor_types.mob_types.groups import group
from modules.actor_types.buildings import resource_building
from modules.util import actor_utility, utility, market_utility
from modules.constants import constants, status, flags


class work_crew(group):
    """
    A group with a foreman officer that can work in buildings
    """

    def work_building(self, building):
        """
        Description:
            Orders this work crew to work in the inputted building, attaching this work crew to the building and allowing the building to function. A resource production building with an attached work crew produces an item every
                turn
        Input:
            building building: building to which this work crew is attached
        Output:
            None
        """
        self.set_permission(constants.IN_BUILDING_PERMISSION, True)
        self.building = building
        self.location.unsubscribe_mob(self)
        self.remove_from_turn_queue()
        building.subscribed_work_crews.append(self)
        actor_utility.calibrate_actor_info_display(
            status.mob_info_display, None, override_exempt=True
        )

    def leave_building(self, building):
        """
        Description:
            Orders this work crew to stop working in the inputted building, making this work crew independent from the building and preventing the building from functioning
        Input:
            building building: building to which this work crew is no longer attached
        Output:
            None
        """
        self.set_permission(constants.IN_BUILDING_PERMISSION, False)
        self.building = None
        building.subscribed_work_crews = utility.remove_from_list(
            building.subscribed_work_crews, self
        )
        self.location.subscribe_mob(self)
        self.add_to_turn_queue()
        actor_utility.calibrate_actor_info_display(
            status.mob_info_display, None, override_exempt=True
        )
        self.select()

    def attempt_production(self, current_building: resource_building):
        """
        Description:
            Attempts to produce resources at a production building at the end of a turn. A work crew makes a number of rolls equal to the building's efficiency level, and each successful roll produces a unit of the building's
                item. Each roll has a success chance based on the work crew's experience and its minister's skill/corruption levels. Promotes foreman to veteran on critical success
        Input:
            building building: building in which this work crew is working
        Output:
            None
        """
        value_stolen = 0
        if (
            self.movement_points >= 1
        ):  # Do not attempt production if unit already did something this turn or suffered from attrition
            current_building.resource_type.production_attempted_this_turn = True
            for current_attempt in range(
                current_building.upgrade_fields[constants.RESOURCE_EFFICIENCY]
            ):
                if self.get_permission(constants.VETERAN_PERMISSION):
                    results = [
                        self.controlling_minister.no_corruption_roll(6),
                        self.controlling_minister.no_corruption_roll(6),
                    ]
                    roll_result = max(results[0], results[1])
                else:
                    roll_result = self.controlling_minister.no_corruption_roll(6)

                if roll_result >= 4:  # 4+ required on D6 for production
                    if not self.controlling_minister.check_corruption():
                        self.location.change_inventory(
                            current_building.resource_type, 1
                        )
                        current_building.resource_type.amount_produced_this_turn += 1
                        current_location = self.location
                        if (
                            not self.get_permission(constants.VETERAN_PERMISSION)
                        ) and roll_result >= 6:
                            self.promote()
                            constants.notification_manager.display_notification(
                                {
                                    "message": f"The work crew working in the {current_building.name} at ({current_location.x}, {current_location.y}) has become a veteran and will be more successful in future production attempts. /n /n",
                                    "zoom_destination": self.location,
                                }
                            )
                    else:
                        value_stolen += current_building.resource_type.price
            if value_stolen > 0:
                self.controlling_minister.steal_money(
                    value_stolen, "production"
                )  # Minister steals value of resources produced
                if random.randrange(1, 7) <= 1:  # 1/6 chance
                    market_utility.change_price(current_building.resource_type, -1)
