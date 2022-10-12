import random
from . import utility
from . import notification_tools
from . import scaling
from . import game_transitions
from . import minister_utility
from . import dice_utility
from . import actor_utility

def start_trial(global_manager): #called by launch trial button in middle of trial screen
    '''
    Description:
        Used when the player presses the trial button in the trial screen, displays a choice notification that allows the player to start the trial or not
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    defense = global_manager.get('displayed_defense')
    prosecution = global_manager.get('displayed_prosecution')
    message = "Are you sure you want to start a trial against " + defense.name + "? You have " + str(defense.corruption_evidence) + " pieces of evidence to use. /n /n"
    message += "Your prosecutor may roll 1 die for each piece of evidence, and the trial is successful if a 6 is rolled on any of the evidence dice. /n /n"
    message += "However, the defense may spend from their personal savings (perhaps stolen from your company) to hire lawyers and negate some of the evidence. /n /n"
    message += "Along with any money paid for bribery or fabricated evidence, a trial fee of " + str(global_manager.get('action_prices')['trial']) + " money is also required. /n /n"

    choice_info_dict = {}
    global_manager.set('ongoing_trial', True)
    notification_tools.display_choice_notification(message, ['start trial', 'stop trial'], choice_info_dict, global_manager) #creates choice notification to verify starting trial

def manage_defense(corruption_evidence, prosecutor_corrupt, global_manager):
    '''
    Description:
        Determines the defending minister's actions in the trial, ranging from buying defense lawyers to bribing the prosecutor. The amount of money spent depends on the trial's success chance and the minister's savings
    Input:
        int corruption_evidence: How much evidence, real or fabricated, is being used in this trial
        boolean prosecutor_corrupt: Whether the prosecutor is corrupt and would be willing to take a bribe to intentionally lose the trial
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        dictionary: Keys corresponding to values containing information about the defense's strategy
            'num_lawyers': int value - Number of defense lawyers working to cancel out evidence
            'defense_bribed_judge': boolean value - Whether the defense chose to bribe the judge
            'corruption_evidence': int value - Base amount of evidence in the case before lawyers intervene
            'effective_evidence': int value - Amount of evidence that is not cancelled out by defense lawyers
    '''
    defense = global_manager.get('displayed_defense')
    prosecutor = global_manager.get('displayed_prosecution')
    max_defense_fund = 0.75 * (defense.stolen_money + defense.personal_savings) #pay up to 75% of savings
    building_defense = True
    num_lawyers = 0
    defense_bribed_judge = False
    defense_cost = 0
    while building_defense:
        if prosecutor_corrupt: #bribe costs defense less than actual trial
            defense_cost = max_defense_fund / 2
            prosecutor.steal_money(defense_cost, 'bribery')
            building_defense = False
            if global_manager.get('DEBUG_show_minister_stealing'):
                print(defense.current_position + " " + defense.name + " now has " + str(defense.stolen_money - defense_cost) + " money remaining.")
        else:
            lawyer_cost = get_lawyer_cost(num_lawyers)
            bribe_judge_cost = get_lawyer_cost(0)
            if (not defense_bribed_judge) and num_lawyers > 0 and (defense_cost + bribe_judge_cost <= max_defense_fund): #bribe judge after getting 1 lawyer
                defense_cost += bribe_judge_cost
                defense_bribed_judge = True
            elif (defense_cost + lawyer_cost <= max_defense_fund) and (num_lawyers + 1 < corruption_evidence): #pay no more than 60% of savings and allow some chance of success for prosecution
                defense_cost += lawyer_cost
                num_lawyers += 1
            else:
                building_defense = False
    defense.personal_savings -= defense_cost
    if defense.personal_savings < 0: #spend from personal savings, transfer stolen to personal savings if not enough
        defense.stolen_money += defense.personal_savings
        defense.personal_savings = 0
    defense_info_dict = {}
    defense_info_dict['num_lawyers'] = num_lawyers
    defense_info_dict['defense_bribed_judge'] = defense_bribed_judge
    defense_info_dict['corruption_evidence'] = corruption_evidence
    defense_info_dict['effective_evidence'] = corruption_evidence - num_lawyers
    return(defense_info_dict)
        
def get_lawyer_cost(num_lawyers):
    '''
    Description:
        Returns the cost of hiring another defense lawyer. The cost increases for each existing defense lawyer in this case
    Input:
        int num_lawyers: How many defense lawyers have already been hired for this trial
    Output:
        Returns the cost of hiring another defense lawyer
    '''
    base_cost = 5
    multiplier = 2 ** num_lawyers #1, 2, 4, 8
    return(base_cost * multiplier)

def get_fabricated_evidence_cost(current_fabricated_evidence, calculate_total = False):
    '''
    Description:
        Returns the cost of fabricating another piece of evidence or how much the existing fabricated evidence cost. The cost increases for each existing fabricated evidence against the selected minister
    Input:
        int current_fabricated_evidence: How much evidence has already been fabricated against this minister for this trial
        boolean calculate_total = False: Determines whether to calculate the cost of fabricating a new piece of evidence or the total cost of the existing fabricated evidence
    Output:
        Returns the cost of fabricating another piece of evidence or how much the existing fabricated evidence cost
    '''
    base_cost = 5
    if not calculate_total: #gets cost of next evidence
        multiplier = 2 ** current_fabricated_evidence #1 if 0 evidence previously created, 2 if 1 previous, 4 if 2 previous, 8 if 3 previous
        return(base_cost * multiplier) #5 if 0 evidence previously created, 10 if 1 previous, 20 if 2 previous, 40 if 3 previous
    else: #gets cost of previously created evidence
        total = 0
        for i in range(0, current_fabricated_evidence):
            multiplier = 2 ** i
            total += base_cost * multiplier
        return(total)

def trial(global_manager): #called by choice notification button
    '''
    Description:
        Controls the trial process, determining and displaying its result through a series of notifications
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    price = global_manager.get('action_prices')['trial']
    global_manager.get('money_tracker').change(-1 * global_manager.get('action_prices')['trial'], 'trial fees')
    actor_utility.double_action_price(global_manager, 'trial')
    defense = global_manager.get('displayed_defense')
    prosecution = global_manager.get('displayed_prosecution')
    prosecutor_corrupt = prosecution.check_corruption()
    if prosecutor_corrupt:
        prosecution.steal_money(price, 'trial fees')
        prosecution.steal_money(get_fabricated_evidence_cost(defense.fabricated_evidence, True), 'trial fees')
        if global_manager.get('prosecution_bribed_judge'):
            prosecution.steal_money(get_fabricated_evidence_cost(0), 'trial fees')

    defense_info_dict = manage_defense(defense.corruption_evidence, prosecutor_corrupt, global_manager)
    effective_evidence = defense_info_dict['effective_evidence']

    defense_bribed_judge = defense_info_dict['defense_bribed_judge']
    prosecution_bribed_judge = global_manager.get('prosecution_bribed_judge')
    text = ""
    judge_modifier = 0
    judge_bias = prosecution.no_corruption_roll(6) - defense.get_roll_modifier() #D6 with both skill modifiers competing
    if judge_bias < 1:
        judge_bias = 1
    elif judge_bias > 6:
        judge_bias = 6
    new_clothing_types = ['jewelry', 'robes', 'wig']
    if not (defense_bribed_judge or prosecution_bribed_judge):
        if judge_bias == 1:
            text = "Even before evidence is presented, the judge has a suspicious bias in favor of the defense, removing 1 of your evidence rolls."
            judge_modifier = -1
        elif judge_bias == 6:
            text = "Despite not being bribed, the judge has a healthy bias in favor of the prosecution, giving 1 additional evidence roll."
            judge_modifier = 1
        else:
            text = "The judge does not seem to favor any particular side."

    elif defense_bribed_judge and not prosecution_bribed_judge:
        if judge_bias <= 5:
            text = "Even before evidence is presented, the judge has a suspicious bias in favor of the defense, removing 1 of your evidence rolls."
            judge_modifier = -1
        else:
            text = "The judge does not seem to favor any particular side and does not modify your evidence rolls."
    elif prosecution_bribed_judge and not defense_bribed_judge:
        if judge_bias == 1 or prosecutor_corrupt: #judge never received the money
            text = "You could have sworn you sent your prosecutor to bribe the judge, but the judge gives the prosecution neither knowing glances nor special treatment." 
        else:
            text = "Smiling and flaunting his fancy new " + random.choice(new_clothing_types) + ", the judge has a healthy bias in favor of the prosecution, giving 1 additional evidence roll."
            judge_modifier = 1
    else: #if both sides bribed judge
        if judge_bias <= 2:
            text = "Despite his fancy new " + random.choice(new_clothing_types) +", the judge has a suspicious bias in favor of the defense, removing 1 of your evidence rolls."
            judge_modifier = -1
        elif judge_bias <= 4:
            text = "You could have sworn you sent your prosecutor to bribe the judge, but the judge gives the prosecution neither knowing glances nor special treatment."
        else:
            text = "Smiling and flaunting his fancy new " + random.choice(new_clothing_types) + ", the judge has a healthy bias in favor of the prosecution, giving 1 additional evidence roll."
            judge_modifier = 1
    text += ' /n /n'
    effective_evidence += judge_modifier
  
    if defense_info_dict['num_lawyers'] == 0:
        text += "As the defense decided not to hire any additional lawyers, each piece of evidence remains usable, allowing " + str(defense_info_dict['effective_evidence']) + " evidence rolls to attempt to win the trial. /n /n"
    else:
        text += "The defense hired " + str(defense_info_dict['num_lawyers']) + " additional lawyer" + utility.generate_plural(defense_info_dict['num_lawyers']) + ", cancelling out " + str(defense_info_dict['num_lawyers']) + " piece"
        text += utility.generate_plural(defense_info_dict['num_lawyers']) + " of evidence. This leaves " + str(effective_evidence) + " evidence roll"
        text += utility.generate_plural(effective_evidence) + " to attempt to win the trial. /n /n"    
    
    text += str(defense_info_dict['corruption_evidence']) + ' initial evidence - '
    text += str(defense_info_dict['num_lawyers']) + ' defense lawyers '
    if judge_modifier < 0:
        text += '- ' + str(judge_modifier) + ' judge bias '
    elif judge_bias > 0:
        text += '+ ' + str(judge_modifier) + ' judge bias '
    else:
        text += '+ 0 judge bias '
    text += '= ' + str(effective_evidence) + ' evidence rolls /n /n'
    notification_tools.display_notification(text, 'default', global_manager)
    
    global_manager.set('trial_rolls', [])

    if prosecutor_corrupt:
        max_roll = 5
    else:
        max_roll = 6
    for i in range(0, effective_evidence):
        current_roll = prosecution.no_corruption_roll(max_roll)
        global_manager.get('trial_rolls').append(current_roll)

    if len(global_manager.get('trial_rolls')) == 0:
        notification_tools.display_notification("As you have no evidence rolls remaining, you automatically lose the trial. /n /n", 'default', global_manager)
        complete_trial(1, global_manager)
    else:
        display_evidence_roll(global_manager)

def display_evidence_roll(global_manager):
    '''
    Description:
        Creates the die object and series of notifications necessary to display a single evidence roll in a trial
    Input:
        global_manager_template global_manager: Object that accesses shared variablesNone
    Output:
        None
    '''
    text = ''
    text += ''
    text = 'Evidence rolls remaining: ' + str(len(global_manager.get('trial_rolls'))) + ' /n /n'
    result = global_manager.get('trial_rolls')[0]
    result_outcome_dict = {'min_success': 6, 'min_crit_success': 6, 'max_crit_fail': 0}
    outcome_color_dict = {'success': 'dark green', 'fail': 'dark red', 'crit_success': 'bright green', 'crit_fail': 'bright red', 'default': 'black'}
    global_manager.get('actor_creation_manager').display_die(scaling.scale_coordinates(global_manager.get('notification_manager').notification_x - 140, 440, global_manager), scaling.scale_width(100, global_manager),
        scaling.scale_height(100, global_manager), ['trial'], 6, result_outcome_dict, outcome_color_dict, result, global_manager)
    notification_tools.display_notification(text + "Click to roll. 6+ required on at least 1 die to succeed.", 'default', global_manager, 1)
    notification_tools.display_notification(text + "Rolling... ", 'roll', global_manager, 1)
    results = dice_utility.roll_to_list(6, 'Evidence roll', 6, 6, 0, global_manager, result)
    notification_tools.display_notification(text + results[1], 'trial', global_manager)

def complete_trial(final_roll, global_manager):
    '''
    Description:
        Used when the player finishes trial evidence rolls, shows the trial's results and makes any changes caused by the result. If successful, removes the minister from the game and confiscates a portion of their savings. On a
            failure, removes about half of real evidence and all fabricated evidence
    Input:
        None
    Output:
        None
    '''
    prosecution = global_manager.get('displayed_prosecution')
    defense = global_manager.get('displayed_defense')
    game_transitions.set_game_mode('ministers', global_manager)
    
    if final_roll == 6:
        confiscated_money = defense.stolen_money / 2.0
        text = "You have won the trial, removing " + defense.name + " as " + defense.current_position + " and putting him in prison. /n /n"
        if confiscated_money > 0:
            text += "While most of " + defense.name + "'s money was spent on the trial or unaccounted for, authorities managed to confiscate " + str(confiscated_money) + " money, which has been given to your company as compensation. "
            text += " /n /n"
            global_manager.get('money_tracker').change(confiscated_money, 'trial compensation')
        else:
            text += "Authorities searched " + defense.name + "'s properties but were not able to find any stolen money with which to compensate your company. Perhaps it remains hidden, had already been spent, or had never been stolen. "
            text += " /n /n"
        notification_tools.display_notification(text, 'default', global_manager)
        
        defense.appoint('none')
        defense.respond('prison')
        defense.remove()
        global_manager.get('fear_tracker').change(1)
        notification_tools.display_notification("Whether or not the defendant was truly guilty, this vigilant show of force may make your ministers reconsider any attempts to steal money for the time being. /n /n", 'default', global_manager)

    else:
        text = "You have lost the trial and " + defense.name + " goes unpunished, remaining your " + defense.current_position + ". /n /n"
        fabricated_evidence = defense.fabricated_evidence
        real_evidence = defense.corruption_evidence - defense.fabricated_evidence

        remaining_evidence = 0
        lost_evidence = 0
        for i in range(0, real_evidence):
            if prosecution.no_corruption_roll(6) >= 4:
                remaining_evidence += 1
            else:
                lost_evidence += 1
                
        if fabricated_evidence > 0:
            text += "Fabricated evidence is temporary, so the " + str(fabricated_evidence) + " piece" + utility.generate_plural(fabricated_evidence) + " of fabricated evidence used in this trial "
            text += utility.conjugate('be', fabricated_evidence) + " now irrelevant to future trials. /n /n"

        if real_evidence > 0:
            if lost_evidence == 0: #if no evidence lost
                text += "All of the real evidence used in this trial remains potent enough to be used in future trials against "
                text += defense.name + ". /n /n"
            elif lost_evidence < real_evidence: #if some evidence lost
                text += "Of the " + str(real_evidence) + " piece" + utility.generate_plural(real_evidence) + " of real evidence used in this trial, " + str(remaining_evidence)
                text += " " + utility.conjugate('remain', remaining_evidence) + " potent enough to be relevant to future trials against " + defense.name + ", while " + str(lost_evidence) + " " + utility.conjugate('be', lost_evidence)
                text += " now irrelevant. /n /n"
            else: #if all evidence lost
                text += "Of the " + str(real_evidence) + " piece" + utility.generate_plural(real_evidence) + " of real evidence used in this trial, none remain potent enough to be relevant to future trials against " + defense.name + ". /n /n"

        defense.fabricated_evidence = 0
        defense.corruption_evidence = remaining_evidence
        notification_tools.display_notification(text, 'default', global_manager)
        minister_utility.calibrate_minister_info_display(global_manager, defense)
    global_manager.set('prosecution_bribed_judge', False)
    global_manager.set('ongoing_trial', False)
