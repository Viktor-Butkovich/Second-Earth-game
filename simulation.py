import json
from scmrepo.git import Git

PACKAGE_ROOT = Git(root_dir=".").root_dir

config = json.load(open(f"{PACKAGE_ROOT}/modules/simulations/sim_config.json", "r"))
chosen_simulation = config["chosen_simulation"]

if chosen_simulation == 1:
    print("Running Investing Strategies Simulation...")
    from modules.simulations.investing_strategies import main
elif chosen_simulation == 2:
    print("Running Dice Game Simulation...")
    from modules.simulations.dice_game import main
elif chosen_simulation == 3:
    print("Running AutoGUI...")
    from modules.simulations.auto_gui import load_and_select_first_unit as main
elif chosen_simulation == 4:
    print("Running AutoGUI...")
    from modules.simulations.auto_gui import new_game as main

main()
