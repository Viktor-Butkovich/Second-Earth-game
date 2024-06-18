"""
Colony ship has limited amount of space, 27 slots
can have workers, air, water, food, building materials, consumer goods, fuel
each unit of workers needs air, water, food, consumer goods, only consumed on arrival
for purpose of simulation, each properly supplied worker rolls a die against hostility of planet to see if colony succeeds
planet characteristics - (average) temperature, roughness, vegetation, soil, water, atmosphere, size, toxicity, radioactivity, magnetic field
difficulty of final roll based on difference between this and ideal Earth conditions

temperature: 3.5, severity 3
roughness: 3, severity 1
vegetation: 4, severity 2
soil: 6, severity 2
water: 4, severity 3
atmosphere: 6, severity 3
size: 3.5, severity 1
toxicity: 1, severity 2
radioactivity: 1, severity 2
magnetic field: 6, severity 2
"""
import random
import math


def print_inventory_dict(inventory_dict):
    print()
    for inventory_type in inventory_dict:
        print(f"{inventory_type.capitalize()}: {inventory_dict[inventory_type]}")


def print_planet(planet_dict, parameter_dict, parameter_keywords_dict):
    for current_parameter in planet_dict:
        difference = get_parameter_difference(
            current_parameter, planet_dict, parameter_dict
        )
        difficulty = get_parameter_difficulty(
            current_parameter, planet_dict, parameter_dict
        )
        if current_parameter in ["radioactivity", "magnetic field"]:
            tabs = "\t"
        else:
            tabs = "\t\t"
        print(
            f"{current_parameter.capitalize()}: {planet_dict[current_parameter]} - {parameter_keywords_dict[current_parameter][planet_dict[current_parameter]]} {tabs}(difference {difference}, difficulty {difficulty})"
        )
    print(f"Total difficulty: {get_planet_difficulty(planet_dict, parameter_dict)}")


def get_parameter_difference(parameter, planet_dict, parameter_dict):
    difference = abs(
        planet_dict[parameter] - math.floor(parameter_dict[parameter]["ideal"])
    )
    return difference


def get_parameter_difficulty(parameter, planet_dict, parameter_dict):
    difference = get_parameter_difference(parameter, planet_dict, parameter_dict)
    difficulty = 1 + (difference * 2)
    if difficulty > 6:
        difficulty = 6
    return difficulty


def get_planet_difficulty(planet_dict, parameter_dict):
    total_severity = 0
    weighted_difficulty = 0
    for current_parameter in parameter_dict:
        total_severity += parameter_dict[current_parameter]["severity"]
        weighted_difficulty += (
            get_parameter_difficulty(current_parameter, planet_dict, parameter_dict)
            * parameter_dict[current_parameter]["severity"]
        )
    total_difficulty = round(weighted_difficulty / total_severity) + 1
    return total_difficulty


def generate_planet(parameter_dict):
    planet_dict = {}
    for current_parameter in parameter_dict:
        planet_dict[current_parameter] = random.randrange(1, 7)
        if current_parameter == "atmosphere":
            new_atmosphere = random.randrange(1, 7)
            if planet_dict["atmosphere"] < new_atmosphere:
                planet_dict["atmosphere"] = new_atmosphere
            planet_dict["atmosphere"] -= 6 - planet_dict["magnetic field"]
            if planet_dict["atmosphere"] < 1:
                planet_dict["atmosphere"] = 1
        elif current_parameter == "water":
            if planet_dict["atmosphere"] > 1:
                planet_dict["water"] = random.randrange(1, 7)
            else:
                planet_dict["water"] = 1
        elif current_parameter == "vegetation":
            if (
                planet_dict["temperature"] > 1
                and planet_dict["soil"] > 1
                and planet_dict["water"] > 2
                and planet_dict["atmosphere"] > 2
            ):
                planet_dict["vegetation"] = random.randrange(2, 7)
            else:
                planet_dict["vegetation"] = 1
    return planet_dict


purchase_phase_complete = False
used_inventory = 0
parameter_dict = {
    "temperature": {"ideal": 3.5, "severity": 3},
    "roughness": {"ideal": 3, "severity": 1},
    "soil": {"ideal": 6, "severity": 2},
    "size": {"ideal": 3.5, "severity": 1},
    "toxicity": {"ideal": 1, "severity": 2},
    "radioactivity": {"ideal": 1, "severity": 2},
    "magnetic field": {"ideal": 6, "severity": 2},
    "atmosphere": {"ideal": 6, "severity": 2},
    "water": {"ideal": 4, "severity": 3},
    "vegetation": {"ideal": 4, "severity": 2},
}
parameter_keywords_dict = {
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
    "soil": {1: "rock", 2: "sand", 3: "clay", 4: "silt", 5: "peat", 6: "loam"},
    "size": {
        1: "very small",
        2: "small",
        3: "medium",
        4: "large",
        5: "very large",
        6: "extremely large",
    },
    "toxicity": {
        1: "none",
        2: "very low",
        3: "low",
        4: "moderate",
        5: "high",
        6: "very high",
    },
    "radioactivity": {
        1: "none",
        2: "very low",
        3: "low",
        4: "moderate",
        5: "high",
        6: "very high",
    },
    "magnetic field": {
        1: "none",
        2: "very weak",
        3: "weak",
        4: "moderate",
        5: "strong",
        6: "very strong",
    },
    "atmosphere": {
        1: "very hostile",
        2: "hostile",
        3: "unpleasant",
        4: "tolerable",
        5: "pleasant",
        6: "ideal",
    },
    "water": {1: "parched", 2: "dry", 3: "wet", 4: "soaked", 5: "shallow", 6: "deep"},
    "vegetation": {
        1: "barren",
        2: "sparse",
        3: "light",
        4: "medium",
        5: "heavy",
        6: "lush",
    },
}
while not purchase_phase_complete:
    inventory_dict = {
        "workers": 0,
        "air": 0,
        "water": 0,
        "food": 0,
        "consumer goods": 0,
        "building materials": 0,
        "fuel": 0,
    }
    used_inventory = 0
    for inventory_type in inventory_dict:
        print_inventory_dict(inventory_dict)
        print(f"Used inventory: {used_inventory}/27")
        print(f"How much {inventory_type} do you want to purchase? ")
        valid_input = False
        while not valid_input:
            purchased = input()
            if (
                purchased.isdigit()
                and int(purchased) >= 0
                and int(purchased) <= 27 - used_inventory
            ):
                valid_input = True
                inventory_dict[inventory_type] = int(purchased)
                used_inventory += int(purchased)
            else:
                print("That is not a valid input")
    print_inventory_dict(inventory_dict)
    print(f"Used inventory: {used_inventory}/27")
    completion_confirmation = input(
        "Enter restart to restart, or enter anything else to continue: "
    )
    if completion_confirmation != "restart":
        purchase_phase_complete = True

print("Final inventory:")
print_inventory_dict(inventory_dict)
landed = False
won = False
while inventory_dict["fuel"] > 0 and not landed:
    inventory_dict["fuel"] -= 1
    used_inventory -= 1
    print_inventory_dict(inventory_dict)
    print(f"Used inventory: {used_inventory}/27")
    print()
    planet_present = False
    if random.randrange(1, 7) >= 4:
        planet_present = True
    if planet_present:
        print("Current planet: ")
        current_planet = generate_planet(parameter_dict)
        print_planet(current_planet, parameter_dict, parameter_keywords_dict)
    print()
    if inventory_dict["fuel"] == 0:
        print("You have no more fuel and will not be able to travel to the next system")
    if planet_present:
        travel_input = input(
            "Enter land to land here, or enter anything else to continue: "
        )
        if travel_input == "land":
            landed = True
            planet_difficulty = get_planet_difficulty(current_planet, parameter_dict)
            won = False
            done = False
            counter = 1
            print(f"\nRoll difficulty: {planet_difficulty}")
            while inventory_dict["workers"] > 0 and not done:
                print_inventory_dict(inventory_dict)
                print(f"Used inventory: {used_inventory}/27")
                worker_requirements = ["air", "water", "food", "consumer goods"]
                requirements_filled = True
                for requirement in worker_requirements:
                    if inventory_dict[requirement] > 0:
                        inventory_dict[requirement] -= 1
                        print(f"Worker {counter} consumed 1 {requirement}")
                        used_inventory -= 1
                    else:
                        print(f"Worker {counter} ran out of {requirement}")
                        done = True
                if not done:
                    roll = random.randrange(1, 7)
                    print(f"Worker {counter} rolled a {roll}")
                    if roll >= planet_difficulty:
                        done = True
                        won = True
                counter += 1
                inventory_dict["workers"] -= 1
                used_inventory -= 1
                input("Press enter to continue: ")
    else:
        print("There is no planet in this system")
        travel_input = input("Press enter to continue: ")
if not landed:
    print("Your ship ran out of fuel")
if won:
    print("You win")
else:
    print("You lose")
