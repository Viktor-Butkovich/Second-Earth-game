# Earth Terrain Definitional Grid: interactive way to define and compare Earth terrains

import modules.data_managers as data_managers
import modules.utility as utility
import modules.save_load_tools as save_load_tools
import modules.input_commands as input_commands

global_manager = data_managers.global_manager_template()
global_manager.set(
    "actor_creation_manager", data_managers.actor_creation_manager_template()
)
global_manager.set(
    "parameter_types", ["temperature", "roughness", "vegetation", "soil", "water"]
)
global_manager.set("terrain_list", [])
global_manager.set("point_list", [])
global_manager.set("displayed_terrain", "none")
global_manager.set("displayed_point", "none")
global_manager.set("current_display_mode", "browse")
global_manager.set(
    "valid_commands",
    {
        "browse": [
            "quit",
            "save",
            "new",
            "print",
            "delete",
            "list",
            "point",
            "select",
            "next",
            "findOverlap",
            "volume",
            "findExpansion",
        ],
        "terrain_view": [
            "quit",
            "new",
            "print",
            "save",
            "delete",
            "list",
            "browse",
            "point",
            "rename",
            "select",
            "next",
            "findOverlap",
            "volume",
            "copy",
            "findExpansion",
        ],
        "point_view": [
            "quit",
            "new",
            "print",
            "save",
            "delete",
            "list",
            "browse",
            "point",
            "select",
            "next",
            "findOverlap",
            "checkOverlap",
            "volume",
            "findExpansion",
        ],
    },
)
global_manager.set(
    "parameter_keywords",
    {
        "temperature": {
            1: "frozen",
            2: "cold",
            3: "cool",
            4: "warm",
            5: "hot",
            6: "scorching",
        },
        "roughness": {
            1: "flat",
            2: "rolling",
            3: "hilly",
            4: "rugged",
            5: "mountainous",
            6: "extreme",
        },
        "vegetation": {
            1: "barren",
            2: "sparse",
            3: "light",
            4: "medium",
            5: "heavy",
            6: "lush",
        },
        "soil": {1: "rock", 2: "sand", 3: "clay", 4: "silt", 5: "peat", 6: "loam"},
        "water": {
            1: "parched",
            2: "dry",
            3: "wet",
            4: "soaked",
            5: "shallow",
            6: "deep",
        },
    },
)

parameter_first_letters = []
for current_parameter in global_manager.get("parameter_types"):
    parameter_first_letters.append(current_parameter[0])
global_manager.get("valid_commands")["terrain_view"] += parameter_first_letters
global_manager.get("valid_commands")["point_view"] += parameter_first_letters

file_name = "modules/TDG.json"
save_load_tools.load_terrains(file_name, global_manager)

current_input = ["start"]
while current_input[0] != "quit":
    print(
        "\nDisplay mode: "
        + global_manager.get("current_display_mode").upper()
        + "("
        + utility.comma_list(
            global_manager.get("valid_commands")[
                global_manager.get("current_display_mode")
            ]
        )
        + ")"
    )
    if global_manager.get("current_display_mode") == "terrain_view":
        print("Selected terrain: " + global_manager.get("displayed_terrain").name)
        print(global_manager.get("displayed_terrain"))
    elif global_manager.get("current_display_mode") == "point_view":
        print(global_manager.get("displayed_point"))

    current_input = utility.extract_arguments(input("Enter a command: "))
    print("-----------------------------------------------------------")
    if len(current_input) > 0:
        if (
            current_input[0]
            in global_manager.get("valid_commands")[
                global_manager.get("current_display_mode")
            ]
        ):
            if current_input[0] == "save":
                input_commands.save(current_input, global_manager)
            elif current_input[0] == "print":
                input_commands.print_terrains(current_input, global_manager)
            elif current_input[0] == "new":
                input_commands.new(current_input, global_manager)
            elif current_input[0] == "delete":
                input_commands.delete(current_input, global_manager)
            elif current_input[0] == "list":
                input_commands.list(current_input, global_manager)
            elif current_input[0] == "browse":
                input_commands.browse(current_input, global_manager)
            elif current_input[0] == "select":
                input_commands.select(current_input, global_manager)
            elif current_input[0] == "rename":
                input_commands.rename(current_input, global_manager)
            elif current_input[0] in parameter_first_letters:
                if global_manager.get("current_display_mode") == "terrain_view":
                    input_commands.edit(current_input, global_manager)
                else:
                    input_commands.edit_point(current_input, global_manager)
            elif current_input[0] == "point":
                input_commands.select_point(current_input, global_manager)
            elif current_input[0] == "next":
                input_commands.select_next_point(current_input, global_manager)
            elif current_input[0] == "findOverlap":
                input_commands.select_first_overlap(current_input, global_manager)
            elif current_input[0] == "checkOverlap":
                input_commands.check_point_overlap(current_input, global_manager)
            elif current_input[0] == "volume":
                input_commands.volume_summary(current_input, global_manager)
            elif current_input[0] == "copy":
                input_commands.copy_terrain(current_input, global_manager)
            elif current_input[0] == "findExpansion":
                input_commands.find_possible_expansion(current_input, global_manager)
        else:
            print(
                current_input[0]
                + " is not a valid command in the "
                + global_manager.get("current_display_mode")
                + " display mode\n"
            )
    else:
        print(
            "That is not a valid command in the "
            + global_manager.get("current_display_mode")
            + " display mode\n"
        )

current_input = utility.extract_arguments(
    input(
        'Enter "discard" to discard new changes, or enter anything else to save changes: '
    )
)
if len(current_input) == 0 or current_input[0] != "discard":
    save_load_tools.save_terrains(global_manager)
