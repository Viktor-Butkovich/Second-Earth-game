prompt = """
Enter the number of the simulation you want to run:
1. Investing Strategies
2. Dice Game
"""
valid_choices = ["1", "2"]
chosen_simulation = None
while chosen_simulation not in valid_choices:
    print("\nInvalid choice. Please enter a valid number.")
    chosen_simulation = input(prompt)

if chosen_simulation == "1":
    print("Running Investing Strategies Simulation...")
    from modules.simulations.investing_strategies import main
elif chosen_simulation == "2":
    print("Running Dice Game Simulation...")
    from modules.simulations.dice_game import main

main()
