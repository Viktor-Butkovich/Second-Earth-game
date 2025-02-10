import numpy as np
import skfuzzy as fuzz
import random
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

specifications = [
    (0.0, 5),
    (0.005, 5),
    (0.006, 4),
    (0.01, 4),
    (0.011, 3),
    (0.015, 3),
    (0.016, 2),
    (0.02, 2),
    (0.021, 1),
    (0.029, 1),
    (0.03, 0),
    (0.031, 0),
    (1.0, 0),
]

ghg = ctrl.Antecedent(np.arange(0, 1.01, 0.0001), "ghg")
habitability = ctrl.Consequent(np.arange(0, 6), "habitability")


def simulate(genome, input_value):
    # Define fuzzy membership functions for GHG levels
    ghg["perfect"] = fuzz.trapmf(ghg.universe, genome[0:4])
    ghg["tolerable"] = fuzz.trapmf(ghg.universe, genome[4:8])
    ghg["unsuitable"] = fuzz.trapmf(ghg.universe, genome[8:12])
    ghg["dangerous"] = fuzz.trapmf(ghg.universe, genome[12:16])
    ghg["hostile"] = fuzz.trapmf(ghg.universe, genome[16:20])
    ghg["deadly"] = fuzz.trapmf(ghg.universe, genome[20:24])

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
    habitability_sim.input["ghg"] = input_value

    # Compute the result
    habitability_sim.compute()
    if habitability_sim.output:
        return habitability_sim.output["habitability"]
    else:
        return -5


class individual:
    def __init__(self, genome):
        self.genome = genome
        self.sort_genome()

    def evaluate(self):
        self.fitness = 1 + sum(
            [abs(spec[1] - simulate(self.genome, spec[0])) for spec in specifications]
        )

    def mutate(self, cooling=1.0):
        index = np.random.randint(0, len(self.genome))
        self.genome[index] = min(
            1, max(0, self.genome[index] + (cooling * random.uniform(-1.0, 1.0)))
        )
        self.sort_genome()

    def sort_genome(self):
        # Ensure every set of 4 genome numbers is sorted in ascending order
        for i in range(0, len(self.genome), 4):
            self.genome[i : i + 4] = sorted(self.genome[i : i + 4])


random.seed(0)
population_size = 1  # 16
population = [
    individual([random.uniform(0, 1) for _ in range(24)])
    for _ in range(population_size * 2)
]
for generation in range(2000):
    for current_individual in population:
        current_individual.evaluate()

    population.sort(key=lambda x: x.fitness)
    print(
        f"Generation {generation}: {round(population[0].fitness, 2)}, {round(population[1].fitness, 2)}"
    )
    population = population[:population_size]
    # print(population[0].genome)
    # for spec in specifications:
    #    simulation_result = simulate(population[0].genome, spec[0])
    #    if simulation_result != spec[1]:
    #        print(f"{spec[0]}: {simulation_result} (expected {spec[1]})")
    # new_population = population.copy() #population[:population_size//2]
    if population_size == 1:
        for i in range(1):
            population.append(individual(population[0].genome.copy()))
            for i in range(5):
                population[-1].mutate(cooling=1 - (i / 2000))
    else:
        for i in range(population_size // 2):
            parent1, parent2 = random.choices(
                population,
                weights=[
                    1 / current_individual.fitness for current_individual in population
                ],
                k=2,
            )
            population.append(individual(parent1.genome.copy()))
            population[-1].mutate()
            population.append(individual(parent2.genome.copy()))
            population[-1].mutate()

    # population = new_population
print(population[0].genome)
for spec in specifications:
    simulation_result = simulate(population[0].genome, spec[0])
    print(
        f"{spec[0]}% GHG: habitability {round(simulation_result, 2)} (expected {round(spec[1], 2)})"
    )

# Not terrible results, but would be better to create a formula such as this manually
