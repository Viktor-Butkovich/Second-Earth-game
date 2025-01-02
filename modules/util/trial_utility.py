# Contains trial-related helper functions

from modules.constants import constants, status, flags


def manage_defense(corruption_evidence, prosecutor_corrupt):
    """
    Description:
        Determines the defending minister's actions in the trial, ranging from buying defense lawyers to bribing the prosecutor. The amount of money spent depends on the trial's success chance and the minister's savings
            Sets the following values in the trial action's current trial dictionary:
                'num_lawyers': int value - Number of defense lawyers working to cancel out evidence
                'defense_bribed_judge': boolean value - Whether the defense chose to bribe the judge
                'corruption_evidence': int value - Base amount of evidence in the case before lawyers intervene
                'effective_evidence': int value - Amount of evidence that is not cancelled out by defense lawyers
    Input:
        int corruption_evidence: How much evidence, real or fabricated, is being used in this trial
        boolean prosecutor_corrupt: Whether the prosecutor is corrupt and would be willing to take a bribe to intentionally lose the trial
    Output:

    """
    defense = status.displayed_defense
    prosecutor = status.displayed_prosecution
    max_defense_fund = 0.75 * (
        defense.stolen_money + defense.personal_savings
    )  # pay up to 75% of savings
    building_defense = True
    num_lawyers = 0
    defense_bribed_judge = False
    defense_cost = 0
    while building_defense:
        if prosecutor_corrupt:  # bribe costs defense less than actual trial
            defense_cost = max_defense_fund / 2
            prosecutor.steal_money(defense_cost, "bribery")
            building_defense = False
            if constants.effect_manager.effect_active("show_minister_stealing"):
                print(
                    f"{defense.current_position} {defense.name} now has {defense.stolen_money - defense_cost} money remaining."
                )
        else:
            lawyer_cost = get_lawyer_cost(num_lawyers)
            bribe_judge_cost = get_lawyer_cost(0)
            if (
                (not defense_bribed_judge)
                and num_lawyers > 0
                and (defense_cost + bribe_judge_cost <= max_defense_fund)
            ):  # bribe judge after getting 1 lawyer
                defense_cost += bribe_judge_cost
                defense_bribed_judge = True
            elif (defense_cost + lawyer_cost <= max_defense_fund) and (
                num_lawyers + 1 < corruption_evidence
            ):  # pay no more than 60% of savings and allow some chance of success for prosecution
                defense_cost += lawyer_cost
                num_lawyers += 1
            else:
                building_defense = False
    defense.personal_savings -= defense_cost
    if (
        defense.personal_savings < 0
    ):  # spend from personal savings, transfer stolen to personal savings if not enough
        defense.stolen_money += defense.personal_savings
        defense.personal_savings = 0
    status.actions["trial"].current_trial["num_lawyers"] = num_lawyers
    status.actions["trial"].current_trial["defense_bribed_judge"] = defense_bribed_judge
    status.actions["trial"].current_trial["corruption_evidence"] = corruption_evidence
    status.actions["trial"].current_trial["effective_evidence"] = (
        corruption_evidence - num_lawyers
    )


def get_lawyer_cost(num_lawyers):
    """
    Description:
        Returns the cost of hiring another defense lawyer. The cost increases for each existing defense lawyer in this case
    Input:
        int num_lawyers: How many defense lawyers have already been hired for this trial
    Output:
        Returns the cost of hiring another defense lawyer
    """
    base_cost = 5
    multiplier = 2**num_lawyers  # 1, 2, 4, 8
    return base_cost * multiplier


def get_fabricated_evidence_cost(current_fabricated_evidence, calculate_total=False):
    """
    Description:
        Returns the cost of fabricating another piece of evidence or how much the existing fabricated evidence cost. The cost increases for each existing fabricated evidence against the selected minister
    Input:
        int current_fabricated_evidence: How much evidence has already been fabricated against this minister for this trial
        boolean calculate_total = False: Determines whether to calculate the cost of fabricating a new piece of evidence or the total cost of the existing fabricated evidence
    Output:
        Returns the cost of fabricating another piece of evidence or how much the existing fabricated evidence cost
    """
    base_cost = 5
    if not calculate_total:  # Gets cost of next evidence
        multiplier = (
            2**current_fabricated_evidence
        )  # 1 if 0 evidence previously created, 2 if 1 previous, 4 if 2 previous, 8 if 3 previous
        return (
            base_cost * multiplier
        )  # 5 if 0 evidence previously created, 10 if 1 previous, 20 if 2 previous, 40 if 3 previous
    else:  # Gets cost of previously created evidence
        total = 0
        for i in range(0, current_fabricated_evidence):
            multiplier = 2**i
            total += base_cost * multiplier
        return total
