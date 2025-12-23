prompt = """
Enter the number of the simulation you want to run:
1. Investing Strategies
"""
valid_choices = ["1"]
chosen_simulation = None
while chosen_simulation not in valid_choices:
    print("\nInvalid choice. Please enter a valid number.")
    chosen_simulation = input(prompt)

if chosen_simulation == "1":
    print("Running Investing Strategies Simulation...")
    from modules.simulations.investing_strategies import main

main()
