# Contains functionality for expeditions

import random
from modules.actor_types.mob_types.groups import group
from modules.constants import constants, status, flags


class expedition(group):
    """
    A group with an explorer officer that is able to explore and move on water
    """

    def move(self, x_change, y_change):
        """
        Description:
            Moves this mob x_change to the right and y_change upward. Allows exploration when moving into unexplored areas. Attempting an exploration starts the
                exploration process, which requires various dice rolls to succeed and can also result in the death of the expedition or the promotion of its explorer. A successful exploration uncovers the area and units to move into it
                normally in the future. As expeditions move, they automatically discover adjacent water tiles, and they also automatically discover all adjacent tiles when looking from a water tile
        Input:
            int x_change: How many cells are moved to the right in the movement
            int y_change: How many cells are moved upward in the movement
        Output:
            None
        """
        flags.show_selection_outlines = True
        flags.show_minimap_outlines = True
        constants.last_selection_outline_switch = constants.current_time

        future_x = (self.x + x_change) % self.grid.coordinate_width
        future_y = (self.y + y_change) % self.grid.coordinate_height
        if x_change > 0:
            direction = "east"
        elif x_change < 0:
            direction = "west"
        elif y_change > 0:
            direction = "north"
        elif y_change < 0:
            direction = "south"
        else:
            direction = None
        future_cell = self.grid.find_cell(future_x, future_y)
        if (
            not self.get_location()
            .get_world_handler()
            .find_location(future_x, future_y)
            .visible
        ):  # if moving to unexplored area, try to explore it
            status.actions["exploration"].on_click(
                self,
                on_click_info_dict={
                    "x_change": x_change,
                    "y_change": y_change,
                    "direction": direction,
                },
            )
        else:  # if moving to explored area, move normally
            super().move(x_change, y_change)

    def on_move(self):
        """
        Description:
            Automatically called when unit arrives in a tile for any reason
        Input:
            None
        Output:
            None
        """
        super().on_move()
        self.resolve_off_tile_exploration()

    def resolve_off_tile_exploration(self):
        """
        Description:
            Whenever an expedition arrives in a tile for any reason, they automatically discover any adjacent water tiles. Additionally, when standing on water, they automatically discover all adjacent tiles
        Input:
            None
        Output:
            None
        """
        return
        self.current_action_type = "exploration"  # used in action notification to tell whether off tile notification should explore tile or not
        cardinal_directions = {
            "up": "north",
            "down": "south",
            "right": "east",
            "left": "west",
        }
        promoted = self.get_permission(constants.VETERAN_PERMISSION)
        for current_direction in ["up", "down", "left", "right"]:
            target_location = self.get_location().adjacent_locations[current_direction]
            if target_location and not target_location.visible:
                if (
                    self.get_location().terrain == "water"
                    or target_location.terrain == "water"
                ):  # if on water, discover all adjacent undiscovered tiles. Also, discover all adjacent water tiles, regardless of if currently on water
                    if self.get_location().terrain == "water":
                        text = "From the water, the expedition has discovered a "
                    elif target_location.terrain == "water":
                        text = "The expedition has discovered a "
                    public_opinion_increase = random.randrange(0, 3)
                    money_increase = 0
                    if target_location.resource:
                        text += f"{target_location.terrain.upper()} tile with a {target_location.resource.upper()} resource (currently worth {constants.item_prices[target_cell.terrain_handler.resource]} money each) to the {cardinal_directions[current_direction]}. /n /n"
                        public_opinion_increase += 3
                    else:
                        text += f"{target_location.terrain.upper()} tile to the {cardinal_directions[current_direction]}. /n /n"

                    if public_opinion_increase > 0:  # Royal/National/Imperial
                        text += f"The Geographical Society is pleased with these findings, increasing your public opinion by {public_opinion_increase}. /n /n"
                    on_reveal, audio = (None, None)
                    if (
                        (not promoted)
                        and random.randrange(1, 7) == 6
                        and self.controlling_minister.no_corruption_roll() == 6
                    ):
                        text += "The explorer is now a veteran and will be more successful in future ventures. /n /n"
                        on_reveal = self.promote
                        audio = "effects/trumpet"
                        promoted = True
                    constants.notification_manager.display_notification(
                        {
                            "message": f"{text}Click to remove this notification. /n /n",
                            "notification_type": constants.OFF_TILE_EXPLORATION_NOTIFICATION,
                            "on_reveal": on_reveal,
                            "audio": audio,
                            "extra_parameters": {
                                "target_location": target_location,
                                "reveal": True,
                                "public_opinion_increase": public_opinion_increase,
                                "money_increase": money_increase,
                            },
                        }
                    )
