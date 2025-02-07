import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

# Define fuzzy variables
food = ctrl.Antecedent(np.arange(0, 11, 1), "food")
service = ctrl.Antecedent(np.arange(0, 11, 1), "service")
tip = ctrl.Consequent(np.arange(0, 26, 1), "tip")

# Define membership functions
food["poor"] = fuzz.trimf(food.universe, [0, 0, 5])
food["average"] = fuzz.trimf(food.universe, [0, 5, 10])
food["excellent"] = fuzz.trimf(food.universe, [5, 10, 10])

service["poor"] = fuzz.trimf(service.universe, [0, 0, 5])
service["average"] = fuzz.trimf(service.universe, [0, 5, 10])
service["excellent"] = fuzz.trimf(service.universe, [5, 10, 10])

tip["low"] = fuzz.trimf(tip.universe, [0, 0, 13])
tip["medium"] = fuzz.trimf(tip.universe, [0, 13, 25])
tip["high"] = fuzz.trimf(tip.universe, [13, 25, 25])
# tip being the output of the rules means that it will be defuzzified to a crisp result

# Define rules
rule1 = ctrl.Rule(food["poor"] & service["poor"], tip["low"])
# If food is poor (0-5 / 10) and service is poor (0-5 / 10), then tend towards low tip (0-13%)

rule2 = ctrl.Rule(service["average"], tip["medium"])
# If service is average (0-5 / 10), then tend towards medium tip (~13%)

rule3 = ctrl.Rule(service["excellent"] | food["excellent"], tip["high"])
# If the service is average or the food is excellent, then the tip is high (~25%)

rule4 = ctrl.Rule(food["average"], tip["medium"])
# If the food is average, then tend towards medium tip (~13%)

# The result may be determined by a combination of rules depending on how strong the input values are

# Create control system
tipping_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4])
tipping = ctrl.ControlSystemSimulation(tipping_ctrl)
# The control system receives input and gives output based on its rules


def analyze(fuzzy_input):
    for key, value in fuzzy_input.items():
        tipping.input[key] = value
    tipping.compute()
    print(
        f"Suggested tip for {fuzzy_input['food']}/10 food, {fuzzy_input['service']}/10 service: {tipping.output['tip']:.2f}%"
    )
    return tipping.output["tip"]


analyze({"food": 6.5, "service": 9.8})

analyze({"food": 9.5, "service": 1.5})

analyze({"food": 5.5, "service": 5.5})

analyze({"food": 1, "service": 1})

# Generate the universe variables
food_values = np.arange(0, 11, 1)
service_values = np.arange(0, 11, 1)

# Create a meshgrid for food and service
food_grid, service_grid = np.meshgrid(food_values, service_values)
tip_grid = np.zeros_like(food_grid, dtype=float)

# Evaluate the control system for each pair of food and service values
for i in range(11):
    for j in range(11):
        tipping.input["food"] = food_grid[i, j]
        tipping.input["service"] = service_grid[i, j]
        tipping.compute()
        tip_grid[i, j] = tipping.output["tip"]
        # There seems to be a gap in the graph because the rules don't cover what to do for perfectly medium food
        # If you get an output error, the rules don't correctly encompass that scenario
        # Make sure behavior is reasonable - in this scenario, we are decreasing tip as food quality increases if service is already at 10


# Plot the topography
fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")
ax.plot_surface(food_grid, service_grid, tip_grid, cmap="viridis")

ax.set_xlabel("Food Quality")
ax.set_ylabel("Service Quality")
ax.set_zlabel("Tip Percentage")
ax.set_title("Topography of Tip Percentage based on Food and Service Quality")

plt.show()

# This would be a very fun way to implement AI behavior in a game, or even SE planetary parameters
#   Convey logic system as a domain expert (me) and easily make behavior that isn't controlled by if/else chains
