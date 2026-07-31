import argparse
from scmrepo.git import Git

PACKAGE_ROOT = Git(root_dir=".").root_dir

parser = argparse.ArgumentParser(description="Simulation Runner")
parser.add_argument("simulation", type=str, help="Choose a simulation to run")
args = parser.parse_args()
chosen_simulation = args.simulation

if chosen_simulation == "investing_strategies":
    print("Running Investing Strategies Simulation...")
    from modules.simulations.investing_strategies import main
elif chosen_simulation == "dice_game":
    print("Running Dice Game Simulation...")
    from modules.simulations.dice_game import main
elif chosen_simulation == "load_and_select_first_unit":
    print("Running AutoGUI...")
    from modules.simulations.auto_gui import load_and_select_first_unit as main
elif chosen_simulation == "new_game":
    print("Running AutoGUI...")
    from modules.simulations.auto_gui import new_game as main
elif chosen_simulation == "network_analysis":
    from modules.simulations.network_analysis import main

main()
