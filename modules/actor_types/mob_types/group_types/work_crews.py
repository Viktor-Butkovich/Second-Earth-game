# Contains functionality for work crews

import random
from ..groups import group
from ....util import actor_utility, utility, market_utility
import modules.constants.constants as constants
import modules.constants.status as status


class work_crew(group):
    """
    A group with a foreman officer that can work in buildings
    """

    def work_building(self, building):
        """
        Description:
            Orders this work crew to work in the inputted building, attaching this work crew to the building and allowing the building to function. A resource production building with an attached work crew produces a commodity every
                turn
        Input:
            building building: building to which this work crew is attached
        Output:
            None
        """
        self.in_building = True
        self.building = building
        self.hide_images()
        self.remove_from_turn_queue()
        building.contained_work_crews.append(self)
        building.cell.tile.update_image_bundle()
        actor_utility.calibrate_actor_info_display(
            status.tile_info_display, building.cell.tile
        )  # update tile ui with worked building
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
        self.in_building = False
        self.building = None
        self.show_images()
        self.add_to_turn_queue()
        building.contained_work_crews = utility.remove_from_list(
            building.contained_work_crews, self
        )
        actor_utility.calibrate_actor_info_display(
            status.mob_info_display, None, override_exempt=True
        )
        self.select()

    def attempt_production(self, building):
        """
        Description:
            Attempts to produce commodities at a production building at the end of a turn. A work crew makes a number of rolls equal to the building's efficiency level, and each successful roll produces a unit of the building's
                commodity. Each roll has a success chance based on the work crew's experience and its minister's skill/corruption levels. Promotes foreman to veteran on critical success
        Input:
            building building: building in which this work crew is working
        Output:
            None
        """
        value_stolen = 0
        if (
            self.movement_points >= 1
        ):  # Do not attempt production if unit already did something this turn or suffered from attrition # not self.temp_movement_disabled:
            if not building.resource_type in constants.attempted_commodities:
                constants.attempted_commodities.append(building.resource_type)
            for current_attempt in range(building.efficiency):
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
                        building.cell.tile.change_inventory(building.resource_type, 1)
                        constants.commodities_produced[building.resource_type] += 1

                        if (
                            not self.get_permission(constants.VETERAN_PERMISSION)
                        ) and roll_result >= 6:
                            self.promote()
                            constants.notification_manager.display_notification(
                                {
                                    "message": f"The work crew working in the {building.name} at ({building.cell.x}, {building.cell.y}) has become a veteran and will be more successful in future production attempts. /n /n",
                                    "zoom_destination": building.cell.tile,
                                }
                            )
                    else:
                        value_stolen += constants.item_prices[building.resource_type]
            if value_stolen > 0:
                self.controlling_minister.steal_money(
                    value_stolen, "production"
                )  # minister steals value of commodities
                if random.randrange(1, 7) <= 1:  # 1/6 chance
                    market_utility.change_price(building.resource_type, -1)
