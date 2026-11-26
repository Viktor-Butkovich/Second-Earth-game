from __future__ import annotations
from modules.constants import constants, status, flags
from modules.util import scaling, game_transitions, actor_utility


def config_grids() -> None:
    """
    Description:
        Creates grids (current world minimaps, Earth abstract grid, etc.) upon loading or creating a new game
    Input:
        None
    Output:
        None
    """
    status.scrolling_strategic_map_grid = (
        constants.ActorCreationManager.create_interface_element(
            input_dict={
                "init_type": constants.MINI_GRID,
                "world_handler": status.current_world,
                "coordinates": scaling.scale_coordinates(
                    constants.strategic_map_x_offset,
                    constants.strategic_map_y_offset,
                ),
                "width": scaling.scale_width(constants.strategic_map_pixel_width),
                "height": scaling.scale_height(constants.strategic_map_pixel_height),
                "modes": [constants.STRATEGIC_MODE],
                "coordinate_size": status.current_world.world_dimensions,
                "grid_line_width": 2,
                "parent_collection": status.grids_collection,
            }
        )
    )

    status.minimap_grid = constants.ActorCreationManager.create_interface_element(
        input_dict={
            "init_type": constants.MINI_GRID,
            "world_handler": status.current_world,
            "coordinates": scaling.scale_coordinates(
                constants.minimap_grid_x_offset,
                -1 * (constants.minimap_grid_pixel_height + 25)
                + constants.minimap_grid_y_offset,
            ),
            "width": scaling.scale_width(constants.minimap_grid_pixel_width),
            "height": scaling.scale_height(constants.minimap_grid_pixel_height),
            "modes": [constants.STRATEGIC_MODE],
            "coordinate_size": constants.minimap_grid_coordinate_size,
            "external_line_color": constants.COLOR_BRIGHT_RED,
            "parent_collection": status.grids_collection,
        }
    )

    globe_projection_grid = constants.ActorCreationManager.create_interface_element(
        input_dict={
            "init_type": constants.ABSTRACT_GRID,
            "world_handler": status.current_world.orbital_world,
            "coordinates": scaling.scale_coordinates(
                constants.globe_projection_grid_x_offset,
                constants.globe_projection_grid_y_offset,
            ),
            "width": scaling.scale_width(constants.globe_projection_grid_width),
            "height": scaling.scale_height(constants.globe_projection_grid_height),
            "modes": [constants.STRATEGIC_MODE],
            "parent_collection": status.grids_collection,
        }
    )

    earth_grid = constants.ActorCreationManager.create_interface_element(
        input_dict={
            "init_type": constants.ABSTRACT_GRID,
            "world_handler": status.earth_world,
            "coordinates": scaling.scale_coordinates(
                constants.earth_grid_x_offset,
                constants.earth_grid_y_offset,
            ),
            "width": scaling.scale_width(constants.earth_grid_width),
            "height": scaling.scale_height(constants.earth_grid_height),
            "modes": [constants.STRATEGIC_MODE, constants.EARTH_MODE],
            "parent_collection": status.grids_collection,
        }
    )

    actor_utility.calibrate_minimap_grids(
        status.current_world,
        round(0.75 * status.current_world.world_dimensions),
        round(0.75 * status.current_world.world_dimensions),
    )

    status.focused_location_zone_grid = (
        constants.ActorCreationManager.create_interface_element(
            input_dict={
                "init_type": constants.ZONE_GRID,
                "coordinates": scaling.scale_coordinates(
                    constants.zone_grid_x, constants.zone_grid_y
                ),
                "width": scaling.scale_width(constants.zone_grid_pixel_width),
                "height": scaling.scale_height(constants.zone_grid_pixel_height),
                "modes": [constants.LOCATION_MODE],
                "coordinate_size": constants.zone_grid_coordinate_size,
                "external_line_color": constants.COLOR_BRIGHT_RED,
            }
        )
    )

    status.focused_location_grid = (
        constants.ActorCreationManager.create_interface_element(
            input_dict={
                "init_type": constants.ABSTRACT_GRID,
                "world_handler": status.current_world,
                "coordinates": scaling.scale_coordinates(
                    750,
                    10,
                ),
                "width": scaling.scale_width(constants.earth_grid_width),
                "height": scaling.scale_height(constants.earth_grid_height),
                "modes": [constants.LOCATION_MODE],
                "external_line_color": constants.COLOR_BRIGHT_RED,
            }
        )
    )
