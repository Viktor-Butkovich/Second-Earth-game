import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt


def fuzzy_habitability(ghg_level: float) -> float:
    # Define the universe of discourse for GHG levels and habitability
    ghg = ctrl.Antecedent(np.arange(0, 1.01, 0.0001), "ghg")
    habitability = ctrl.Consequent(np.arange(0, 6, 0.1), "habitability")

    # Define fuzzy membership functions for GHG levels
    ghg["perfect"] = fuzz.trimf(ghg.universe, [0, 0, 0.0061])
    ghg["tolerable"] = fuzz.trimf(ghg.universe, [0.006, 0.008, 0.011])
    ghg["unsuitable"] = fuzz.trimf(ghg.universe, [0.01, 0.0125, 0.016])
    ghg["dangerous"] = fuzz.trimf(ghg.universe, [0.015, 0.0175, 0.021])
    ghg["hostile"] = fuzz.trimf(ghg.universe, [0.02, 0.025, 0.031])
    ghg["deadly"] = fuzz.trapmf(ghg.universe, [0.03, 0.03, 1.0, 1.0])

    # Define fuzzy membership functions for habitability
    habitability["deadly"] = fuzz.trimf(habitability.universe, [0, 0.5, 1.5])
    habitability["hostile"] = fuzz.trimf(habitability.universe, [0.5, 1.5, 2.5])
    habitability["dangerous"] = fuzz.trimf(habitability.universe, [1.5, 2.5, 3.5])
    habitability["unsuitable"] = fuzz.trimf(habitability.universe, [2.5, 3.5, 4.5])
    habitability["tolerable"] = fuzz.trimf(habitability.universe, [3.5, 4.5, 5.5])
    habitability["perfect"] = fuzz.trimf(habitability.universe, [4.5, 5.5, 6])

    # Define the rules
    rule1 = ctrl.Rule(ghg["perfect"], habitability["perfect"])
    rule2 = ctrl.Rule(ghg["tolerable"], habitability["tolerable"])
    rule3 = ctrl.Rule(ghg["unsuitable"], habitability["unsuitable"])
    rule4 = ctrl.Rule(ghg["dangerous"], habitability["dangerous"])
    rule5 = ctrl.Rule(ghg["hostile"], habitability["hostile"])
    rule6 = ctrl.Rule(ghg["deadly"], habitability["deadly"])

    # Create the control system and simulation
    habitability_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6])
    habitability_sim = ctrl.ControlSystemSimulation(habitability_ctrl)

    # Pass the input to the control system
    habitability_sim.input["ghg"] = ghg_level

    # Compute the result
    habitability_sim.compute()

    return round(habitability_sim.output["habitability"])


# Generate GHG levels from 0.0 to 1.0
ghg_levels = np.arange(0.0, 0.04, 0.001)
habitability_scores = [fuzzy_habitability(ghg) for ghg in ghg_levels]
print(habitability_scores)
# Plot the results
plt.figure(figsize=(10, 5))
plt.plot(ghg_levels, habitability_scores, label="Habitability Score")
plt.xlabel("GHG Level")
plt.ylabel("Habitability")
plt.title("Habitability Score vs GHG Level")
plt.legend()
plt.grid(True)
plt.show()

"""
Perfect habitability should be from 0.0 to 0.006
Tolerable habitability should be from 0.006 to 0.01
Unsuitable habitability should be from 0.01 to 0.015
Dangerous habitability should be from 0.015 to 0.02
Hostile habitability should be from 0.02 to 0.03
Deadly habitability should be from 0.03 to 1.0
"""
boundaries = {}
for ghg in ghg_levels:
    score = fuzzy_habitability(ghg)
    if score not in boundaries:
        boundaries[score] = ghg

desired_intervals = {
    "Perfect": (0.0, 0.006),
    "Tolerable": (0.006, 0.01),
    "Unsuitable": (0.01, 0.015),
    "Dangerous": (0.015, 0.02),
    "Hostile": (0.02, 0.03),
    "Deadly": (0.03, 1.0),
}

# Print the boundaries
for score in sorted(boundaries.keys(), reverse=True):
    print(
        f"Habitability score {score} is first reached at GHG level: {boundaries[score]}"
    )
    # Print the desired intervals from the comment block

for label, (start, end) in desired_intervals.items():
    print(f"{label} habitability should be from {start} to {end}")

"""
It is very difficult to get the right level of precision - we should keep using pre-defined logic for these
We could try to use fuzzy logic for temperature generation, but this is not feasible or efficient for simple 1-dimensional thresholds
"""
