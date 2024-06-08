import json

with open("country_groups.json") as active_file:
    country_dict = json.load(
        active_file
    )

total_population = 0
total_weighted_representation = 0
group_totals = {}
group_weighted_totals = {}
for group in country_dict:
    if group != "note":
        group_totals[group] = 0
        group_weighted_totals[group] = 0
        for country in country_dict[group]["populations"]:
            population = country_dict[group]["populations"][country]
            space_representation = country_dict[group]["metadata"]["space_representation"]
            weighted_representation = space_representation * population

            total_population += population
            total_weighted_representation += weighted_representation
            group_totals[group] += population
            group_weighted_totals[group] += weighted_representation
        group_weighted_totals[group] = round(group_weighted_totals[group], 2)

population_percentages = {}
weighted_percentages = {}
for group in group_totals:
    population_percentages[group] = round(group_totals[group] / total_population, 2)
    weighted_percentages[group] = round(group_weighted_totals[group] / total_weighted_representation, 2)

print('Total population (units of 10 million):', total_population)
print('Group totals:', group_totals)
print('Group percentages:', population_percentages)
print()
print('Space technology/involvement weighted total:', total_weighted_representation)
print('Weighted totals:', group_weighted_totals)
print("Weighted percentages:", weighted_percentages)
