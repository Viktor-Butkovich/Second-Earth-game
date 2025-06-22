import random
import os
from typing import Dict, List, Any
from math import ceil
from modules.constants import constants, status, flags


def generate_abstract_world_image(
    size: float = 0.8, planet: str = None, rotation: int = None
) -> List[Dict[str, Any]]:
    """
    Description:
        Generates an image ID list for the specified world
    Input:
        float size: Size multiplier to use for the planet portion of the image
        str planet: Type of planet to generate - constants.GLOBE_PROJECTION_WORLD for current globe projection, or an EARTH/VENUS/MARS preset
        int rotation: Rotation index of pre-computed frame to use for Earth, if any
    Output:
        image ID list: List of image ID dictionaries to use for the specified world
    """
    if planet == constants.GLOBE_PROJECTION_WORLD:
        image_id = status.globe_projection_surface
    elif planet != constants.EARTH_WORLD:
        image_id = f"locations/{planet}.png"
    elif rotation is None:
        image_id = "locations/earth.png"
    else:
        num_earth_images = len(os.listdir("graphics/locations/earth_rotations"))
        image_id = f"locations/earth_rotations/{(constants.TIME_PASSING_EARTH_ROTATIONS % num_earth_images)}.png"

    return [
        {
            "image_id": "misc/space.png",
        },
        {
            "image_id": image_id,
            "size": size,
            "detail_level": 1.0,
        },
    ]


def get_preset() -> str:
    """
    Description:
        Get the current world preset based on active effects
    Input:
        None
    Output:
        str: The name of the current world preset, or None if no preset is active.
    """
    for preset in [constants.EARTH_WORLD, constants.VENUS_WORLD, constants.MARS_WORLD]:
        if constants.EffectManager.effect_active(f"{preset}_preset"):
            return preset
    return None


def save_worlds() -> Dict[str, Dict[str, Any]]:
    return {
        "current_world": status.current_world.to_save_dict(),
        "earth_world": status.earth_world.to_save_dict(),
    }


def load_worlds(save_dicts: Dict[str, Dict[str, Any]]) -> None:
    status.current_world = constants.ActorCreationManager.create(
        True, save_dicts["current_world"]
    )
    status.earth_world = constants.ActorCreationManager.create(
        True, save_dicts["earth_world"]
    )
    for current_mob in status.mob_list:
        current_mob.load_end_turn_destination()
        # Loading end turn destinations depends on worlds being fully loaded


def new_worlds() -> None:
    status.current_world = constants.ActorCreationManager.create(
        from_save=False,
        input_dict=generate_current_world_input_dict(),
    )
    status.earth_world = constants.ActorCreationManager.create(
        from_save=False,
        input_dict=generate_earth_world_input_dict(),
    )


def generate_current_world_input_dict() -> Dict[str, Any]:
    return_dict: Dict[str, Any] = {}
    return_dict["init_type"] = constants.FULL_WORLD
    return_dict["green_screen"] = generate_world_green_screen()

    preset = get_preset()
    if preset:
        return_dict.update(generate_preset_world(preset))
    else:
        return_dict.update(generate_random_world())
    return return_dict


def generate_preset_world(preset: str) -> Dict[str, Any]:
    return_dict: Dict[str, Any] = {}
    return_dict["name"] = preset.capitalize()
    return_dict["world_dimensions"] = constants.world_dimensions_options[
        constants.TerrainManager.get_tuning(f"{preset}_dimensions_index")
    ]
    ideal_atmosphere_size = (return_dict["world_dimensions"] ** 2) * 6
    return_dict["rotation_direction"] = constants.TerrainManager.get_tuning(
        f"{preset}_rotation_direction"
    )
    return_dict["rotation_speed"] = constants.TerrainManager.get_tuning(
        f"{preset}_rotation_speed"
    )
    return_dict["global_parameters"] = {
        constants.GRAVITY: constants.TerrainManager.get_tuning(f"{preset}_gravity"),
        constants.RADIATION: constants.TerrainManager.get_tuning(f"{preset}_radiation"),
        constants.MAGNETIC_FIELD: constants.TerrainManager.get_tuning(
            f"{preset}_magnetic_field"
        ),
        constants.INERT_GASES: round(
            constants.TerrainManager.get_tuning(f"{preset}_inert_gases")
            * constants.TerrainManager.get_tuning(f"{preset}_pressure")
            * ideal_atmosphere_size,
            1,
        ),
        constants.OXYGEN: round(
            constants.TerrainManager.get_tuning(f"{preset}_oxygen")
            * constants.TerrainManager.get_tuning(f"{preset}_pressure")
            * ideal_atmosphere_size,
            1,
        ),
        constants.GHG: round(
            constants.TerrainManager.get_tuning(f"{preset}_GHG")
            * constants.TerrainManager.get_tuning(f"{preset}_pressure")
            * ideal_atmosphere_size,
            1,
        ),
        constants.TOXIC_GASES: round(
            constants.TerrainManager.get_tuning(f"{preset}_toxic_gases")
            * constants.TerrainManager.get_tuning(f"{preset}_pressure")
            * ideal_atmosphere_size,
            1,
        ),
    }
    return_dict["average_water_target"] = constants.TerrainManager.get_tuning(
        f"{preset}_average_water_target"
    )
    return_dict["sky_color"] = constants.TerrainManager.get_tuning(
        f"{preset}_sky_color"
    )
    return_dict["star_distance"] = constants.TerrainManager.get_tuning(
        f"{preset}_star_distance"
    )
    return return_dict


def generate_random_world() -> Dict[str, Any]:
    return_dict: Dict[str, Any] = {}
    return_dict["name"] = constants.FlavorTextManager.generate_flavor_text(
        "planet_names"
    )
    return_dict["world_dimensions"] = random.choice(constants.world_dimensions_options)
    ideal_atmosphere_size = (
        return_dict["world_dimensions"] ** 2
    ) * 6  # Atmosphere units required for 1 atm pressure (like Earth) - 6 units per location
    return_dict["star_distance"] = round(random.uniform(0.5, 2.0), 3)

    return_dict["rotation_direction"] = random.choice([1, -1])
    return_dict["rotation_speed"] = random.choice([1, 2, 2, 3, 4, 5])
    return_dict["average_water_target"] = random.choice(
        [
            random.uniform(0.0, 5.0),
            random.uniform(0.0, 1.0),
            random.uniform(0.0, 4.0),
        ]
    )
    return_dict["sky_color"] = [
        random.randrange(0, 256) for _ in range(3)
    ]  # Random sky color

    global_parameters: Dict[str, float] = {}
    global_parameters[constants.GRAVITY] = round(
        ((return_dict["world_dimensions"] ** 2) / (constants.earth_dimensions**2))
        * random.uniform(0.7, 1.3),
        2,
    )
    global_parameters[constants.RADIATION] = max(
        random.randrange(0, 5), random.randrange(0, 5)
    )
    global_parameters[constants.MAGNETIC_FIELD] = random.choices(
        [0, 1, 2, 3, 4, 5], [5, 2, 2, 2, 2, 2], k=1
    )[0]
    atmosphere_type = random.choice(
        ["thick", "thick", "medium", "medium", "medium", "thin"]
    )
    if (
        global_parameters[constants.MAGNETIC_FIELD]
        >= global_parameters[constants.RADIATION]
    ):
        if atmosphere_type in ["thin", "none"]:
            atmosphere_type = "medium"
    elif (
        global_parameters[constants.MAGNETIC_FIELD]
        >= global_parameters[constants.RADIATION] - 2
    ):
        if atmosphere_type == "none":
            atmosphere_type = "thin"

    if atmosphere_type == "thick":
        global_parameters.update(generate_thick_atmosphere(ideal_atmosphere_size))
    elif atmosphere_type == "medium":
        global_parameters.update(generate_medium_atmosphere(ideal_atmosphere_size))
    elif atmosphere_type == "thin":
        global_parameters.update(generate_thin_atmosphere(ideal_atmosphere_size))
    elif atmosphere_type == "none":
        global_parameters.update(generate_no_atmosphere())

    apply_initial_radiation_effect(global_parameters)

    for component in constants.ATMOSPHERE_COMPONENTS:
        if random.randrange(1, 7) >= 5:
            global_parameters[component] = 0
        global_parameters[component] += random.uniform(-10.0, 10.0)
        global_parameters[component] = max(0, round(global_parameters[component], 1))

    return_dict["global_parameters"] = global_parameters
    return return_dict


def generate_earth_world_input_dict() -> Dict[str, Any]:
    return_dict = {}
    return_dict["init_type"] = constants.ABSTRACT_WORLD
    return_dict["abstract_world_type"] = constants.EARTH_WORLD
    return_dict["name"] = "Earth"
    return_dict["world_dimensions"] = 1
    return_dict["rotation_direction"] = constants.TerrainManager.get_tuning(
        "earth_rotation_direction"
    )
    return_dict["rotation_speed"] = constants.TerrainManager.get_tuning(
        "earth_rotation_speed"
    )
    return_dict["global_parameters"] = {
        constants.GRAVITY: constants.TerrainManager.get_tuning("earth_gravity"),
        constants.RADIATION: constants.TerrainManager.get_tuning("earth_radiation"),
        constants.MAGNETIC_FIELD: constants.TerrainManager.get_tuning(
            "earth_magnetic_field"
        ),
        constants.INERT_GASES: round(
            constants.TerrainManager.get_tuning("earth_inert_gases")
            * constants.earth_dimensions**2
            * 6,
            1,
        ),
        constants.OXYGEN: round(
            constants.TerrainManager.get_tuning("earth_oxygen")
            * constants.earth_dimensions**2
            * 6,
            1,
        ),
        constants.GHG: round(
            constants.TerrainManager.get_tuning("earth_GHG")
            * constants.earth_dimensions**2
            * 6,
            1,
        ),
        constants.TOXIC_GASES: round(
            constants.TerrainManager.get_tuning("earth_toxic_gases")
            * constants.earth_dimensions**2
            * 6,
            1,
        ),
    }
    return_dict["average_water"] = constants.TerrainManager.get_tuning(
        "earth_average_water_target"
    )
    return_dict["size"] = constants.earth_dimensions**2
    return_dict["sky_color"] = constants.TerrainManager.get_tuning("earth_sky_color")
    return_dict["star_distance"] = constants.TerrainManager.get_tuning(
        "earth_star_distance"
    )
    return_dict["albedo_multiplier"] = constants.TerrainManager.get_tuning(
        "earth_albedo_multiplier"
    )
    return_dict["cloud_frequency"] = constants.TerrainManager.get_tuning(
        "earth_cloud_frequency"
    )
    return_dict["image_id_list"] = generate_abstract_world_image(
        planet=constants.EARTH_WORLD
    )
    return return_dict


def generate_thick_atmosphere(ideal_atmosphere_size: int) -> Dict[str, float]:
    return {
        constants.GHG: random.choices(
            [
                random.randrange(0, ideal_atmosphere_size * 90),
                random.randrange(0, ideal_atmosphere_size * 10),
                random.randrange(0, ideal_atmosphere_size * 5),
                random.randrange(0, ideal_atmosphere_size),
                random.randrange(0, ceil(ideal_atmosphere_size * 0.1)),
                0,
            ],
            [2, 4, 4, 4, 6, 6],
            k=1,
        )[0],
        constants.OXYGEN: random.choices(
            [
                random.randrange(0, ideal_atmosphere_size * 10),
                random.randrange(0, ideal_atmosphere_size * 5),
                random.randrange(0, ideal_atmosphere_size * 2),
                random.randrange(0, ceil(ideal_atmosphere_size * 0.5)),
                random.randrange(0, ceil(ideal_atmosphere_size * 0.01)),
                0,
            ],
            [2, 4, 4, 4, 6, 6],
            k=1,
        )[0],
        constants.INERT_GASES: random.choices(
            [
                random.randrange(0, ideal_atmosphere_size * 90),
                random.randrange(0, ideal_atmosphere_size * 10),
                random.randrange(0, ideal_atmosphere_size * 5),
                random.randrange(0, ideal_atmosphere_size),
                random.randrange(0, ceil(ideal_atmosphere_size * 0.1)),
                0,
            ],
            [2, 4, 4, 4, 6, 6],
            k=1,
        )[
            0
        ],  # Same distribution as GHG
        constants.TOXIC_GASES: random.choices(
            [
                random.randrange(0, ideal_atmosphere_size * 10),
                random.randrange(0, ideal_atmosphere_size * 5),
                random.randrange(0, ideal_atmosphere_size * 2),
                random.randrange(0, ceil(ideal_atmosphere_size * 0.5)),
                random.randrange(0, ceil(ideal_atmosphere_size * 0.01)),
                0,
            ],
            [2, 4, 4, 4, 6, 6],
            k=1,
        )[
            0
        ],  # Same distribution as oxygen
    }


def generate_medium_atmosphere(ideal_atmosphere_size: int) -> Dict[str, float]:
    return {
        constants.GHG: random.choices(
            [
                random.randrange(0, ideal_atmosphere_size),
                random.randrange(0, ceil(ideal_atmosphere_size * 0.5)),
                random.randrange(0, ceil(ideal_atmosphere_size * 0.3)),
                random.randrange(0, ceil(ideal_atmosphere_size * 0.1)),
                random.randrange(0, ceil(ideal_atmosphere_size * 0.01)),
                0,
            ],
            [3, 3, 3, 3, 3, 3],
            k=1,
        )[0],
        constants.OXYGEN: random.choices(
            [
                random.randrange(0, ceil(ideal_atmosphere_size * 0.6)),
                random.randrange(0, ceil(ideal_atmosphere_size * 0.3)),
                random.randrange(0, ceil(ideal_atmosphere_size * 0.15)),
                random.randrange(0, ceil(ideal_atmosphere_size * 0.05)),
                random.randrange(0, ceil(ideal_atmosphere_size * 0.01)),
                0,
            ],
            [3, 3, 3, 3, 3, 3],
            k=1,
        )[0],
        constants.INERT_GASES: random.choices(
            [
                random.randrange(0, ideal_atmosphere_size),
                random.randrange(0, ceil(ideal_atmosphere_size * 0.5)),
                random.randrange(0, ceil(ideal_atmosphere_size * 0.3)),
                random.randrange(0, ceil(ideal_atmosphere_size * 0.1)),
                random.randrange(0, ceil(ideal_atmosphere_size * 0.01)),
                0,
            ],
            [3, 3, 3, 3, 3, 3],
            k=1,
        )[
            0
        ],  # Same distribution as GHG
        constants.TOXIC_GASES: random.choices(
            [
                random.randrange(0, ceil(ideal_atmosphere_size * 0.6)),
                random.randrange(0, ceil(ideal_atmosphere_size * 0.3)),
                random.randrange(0, ceil(ideal_atmosphere_size * 0.15)),
                random.randrange(0, ceil(ideal_atmosphere_size * 0.05)),
                random.randrange(0, ceil(ideal_atmosphere_size * 0.01)),
                0,
            ],
            [3, 3, 3, 3, 3, 3],
            k=1,
        )[
            0
        ],  # Same distribution as oxygen
    }


def generate_thin_atmosphere(ideal_atmosphere_size: int) -> Dict[str, float]:
    return {
        constants.GHG: random.choices(
            [
                random.randrange(0, ceil(ideal_atmosphere_size * 0.05)),
                random.randrange(0, ceil(ideal_atmosphere_size * 0.01)),
                random.randrange(0, ceil(ideal_atmosphere_size * 0.005)),
                random.randrange(0, ceil(ideal_atmosphere_size * 0.001)),
                0,
                0,
            ],
            [3, 3, 3, 3, 3, 3],
            k=1,
        )[0],
        constants.OXYGEN: random.choices(
            [
                random.randrange(0, ceil(ideal_atmosphere_size * 0.01)),
                random.randrange(0, ceil(ideal_atmosphere_size * 0.005)),
                random.randrange(0, ceil(ideal_atmosphere_size * 0.001)),
                0,
                0,
            ],
            [3, 3, 3, 3, 3],
            k=1,
        )[0],
        constants.INERT_GASES: random.choices(
            [
                random.randrange(0, ceil(ideal_atmosphere_size * 0.05)),
                random.randrange(0, ceil(ideal_atmosphere_size * 0.01)),
                random.randrange(0, ceil(ideal_atmosphere_size * 0.005)),
                random.randrange(0, ceil(ideal_atmosphere_size * 0.001)),
                0,
                0,
            ],
            [3, 3, 3, 3, 3, 3],
            k=1,
        )[
            0
        ],  # Same distribution as GHG
        constants.TOXIC_GASES: random.choices(
            [
                random.randrange(0, ceil(ideal_atmosphere_size * 0.01)),
                random.randrange(0, ceil(ideal_atmosphere_size * 0.005)),
                random.randrange(0, ceil(ideal_atmosphere_size * 0.001)),
                0,
                0,
            ],
            [3, 3, 3, 3, 3],
            k=1,
        )[
            0
        ],  # Same distribution as oxygen
    }


def generate_no_atmosphere() -> Dict[str, float]:
    return {
        constants.GHG: 0,
        constants.OXYGEN: 0,
        constants.INERT_GASES: 0,
        constants.TOXIC_GASES: 0,
    }


def apply_initial_radiation_effect(global_parameters: Dict[str, float]) -> None:
    radiation_effect = (
        global_parameters[constants.RADIATION]
        - global_parameters[constants.MAGNETIC_FIELD]
    )
    if radiation_effect >= 3:
        global_parameters[constants.INERT_GASES] = 0
        global_parameters[constants.OXYGEN] = 0
        global_parameters[constants.TOXIC_GASES] /= 2
        global_parameters[constants.GHG] /= 2
    elif radiation_effect >= 1:
        global_parameters[constants.INERT_GASES] /= 2
        global_parameters[constants.OXYGEN] /= 2


def generate_world_green_screen() -> Dict[str, Dict[str, Any]]:
    """
    Description:
        Generate a smart green screen dictionary for this world handler, containing color configuration for each terrain surface type
    Input:
        None
    Output:
        None
    """
    preset = get_preset()
    if preset:
        water_color = constants.TerrainManager.get_tuning(f"{preset}_water_color")
        ice_color = constants.TerrainManager.get_tuning(f"{preset}_ice_color")
        sand_color = constants.TerrainManager.get_tuning(f"{preset}_sand_color")
        rock_color = constants.TerrainManager.get_tuning(f"{preset}_rock_color")
    else:
        sand_type = random.randrange(1, 7)
        if sand_type >= 5:
            sand_color = (
                random.randrange(150, 240),
                random.randrange(70, 196),
                random.randrange(20, 161),
            )
        elif sand_type >= 3:
            base_sand_color = random.randrange(50, 200)
            sand_color = (
                base_sand_color * random.uniform(0.8, 1.2),
                base_sand_color * random.uniform(0.8, 1.2),
                base_sand_color * random.uniform(0.8, 1.2),
            )
        else:
            sand_color = (
                random.randrange(3, 236),
                random.randrange(3, 236),
                random.randrange(3, 236),
            )

        rock_multiplier = random.uniform(0.8, 1.4)
        rock_color = (
            sand_color[0] * 0.45 * rock_multiplier,
            sand_color[1] * 0.5 * rock_multiplier,
            max(50, sand_color[2] * 0.6) * rock_multiplier,
        )

        water_color = (
            random.randrange(7, 25),
            random.randrange(15, 96),
            random.randrange(150, 221),
        )
        ice_color = (
            random.randrange(140, 181),
            random.randrange(190, 231),
            random.randrange(220, 261),
        )
    # Tuning should include water, ice, rock, sand RGB values, replacing any randomly generated values
    return {
        "ice": {
            "base_colors": [(150, 203, 230)],
            "tolerance": 180,
            "replacement_color": (
                round(ice_color[0]),
                round(ice_color[1]),
                round(ice_color[2]),
            ),
        },
        "dirt": {
            "base_colors": [(124, 99, 29)],
            "tolerance": 60,
            "replacement_color": (
                round((sand_color[0] + rock_color[0]) / 2),
                round((sand_color[1] + rock_color[1]) / 2),
                round((sand_color[2] + rock_color[2]) / 2),
            ),
        },
        "sand": {
            "base_colors": [(220, 180, 80)],
            "tolerance": 50,
            "replacement_color": (
                round(sand_color[0]),
                round(sand_color[1]),
                round(sand_color[2]),
            ),
        },
        "shadowed sand": {
            "base_colors": [(184, 153, 64)],
            "tolerance": 35,
            "replacement_color": (
                round(sand_color[0] * 0.8),
                round(sand_color[1] * 0.8),
                round(sand_color[2] * 0.8),
            ),
        },
        "deep water": {
            "base_colors": [(24, 62, 152)],
            "tolerance": 75,
            "replacement_color": (
                round(water_color[0] * 0.9),
                round(water_color[1] * 0.9),
                round(water_color[2] * 1),
            ),
        },
        "shallow water": {
            "base_colors": [(65, 26, 93)],
            "tolerance": 75,
            "replacement_color": (
                round(water_color[0]),
                round(water_color[1] * 1.1),
                round(water_color[2] * 1),
            ),
        },
        "rock": {
            "base_colors": [(90, 90, 90)],
            "tolerance": 90,
            "replacement_color": (
                round(rock_color[0]),
                round(rock_color[1]),
                round(rock_color[2]),
            ),
        },
        "mountaintop": {
            "base_colors": [(233, 20, 233)],
            "tolerance": 75,
            "replacement_color": (
                round(rock_color[0] * 1.4),
                round(rock_color[1] * 1.4),
                round(rock_color[2] * 1.4),
            ),
        },
        "faults": {
            "base_colors": [(54, 53, 40)],
            "tolerance": 0,
            "replacement_color": (
                round(rock_color[0] * 0.5),
                round(rock_color[1] * 0.5),
                round(rock_color[2] * 0.5),
            ),
        },
        "clouds": {
            "base_colors": [(174, 37, 19)],
            "tolerance": 60,
            "replacement_color": (0, 0, 0),
            # Replacement color updated when sky color changes
        },
    }
