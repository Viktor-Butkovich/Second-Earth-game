#Contains functionality for ministers

import random

from . import utility
from . import actor_utility
from . import minister_utility
from . import notification_tools
from . import images
from . import scaling

class minister():
    '''
    Person that can be appointed to control a certain part of the company and will affect actions based on how skilled and corrupt they are
    '''
    def __init__(self, from_save, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'name': string value - Required if from save, this minister's name
                'current_position': string value - Office that this minister is currently occupying, or 'none' if no office occupied
                'background': string value - Career background of minister, determines social status and skills
                'personal savings': double value - How much non-stolen money this minister has based on their social status
                'general_skill': int value - Value from 1 to 3 that changes what is added to or subtracted from dice rolls
                'specific_skills': dictionary value - String keys corresponding to int values to record skill values for each minister office
                'interests': string list value - List of strings describing the skill categories this minister is interested in
                'corruption': int value - Measure of how corrupt a minister is, with 6 having a 1/2 chance to steal, 5 having 1/3 chance, etc.
                'image_id': string value - File path to the image used by this minister
                'stolen_money': double value - Amount of money this minister has stolen or taken in bribes
                'just_removed': boolean value - Whether this minister was just removed from office and will be fired at the end of the turn
                'corruption_evidence': int value - Number of pieces of evidence that can be used against this minister in a trial, includes fabricated evidence
                'fabricated_evidence': int value - Number of temporary fabricated pieces of evidence that can be used against this minister in a trial this turn
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.actor_type = 'minister' #used for actor display labels and images
        self.global_manager = global_manager
        self.global_manager.get('minister_list').append(self)
        self.tooltip_text = []
        if from_save:
            self.name = input_dict['name']
            self.current_position = input_dict['current_position']
            
            self.background = input_dict['background']
            self.status_number = global_manager.get('background_status_dict')[self.background]
            status_number_dict = {1: 'low', 2: 'moderate', 3: 'high', 4: 'very high'}
            self.status = status_number_dict[self.status_number]
            self.personal_savings = input_dict['personal_savings']
            
            self.general_skill = input_dict['general_skill']
            self.specific_skills = input_dict['specific_skills']
            self.interests = input_dict['interests']
            self.corruption = input_dict['corruption']
            self.corruption_threshold = 10 - self.corruption
            self.image_id = input_dict['image_id']
            self.stolen_money = input_dict['stolen_money']
            self.corruption_evidence = input_dict['corruption_evidence']
            self.fabricated_evidence = input_dict['fabricated_evidence']
            self.just_removed = input_dict['just_removed']
            
            if not self.current_position == 'none':
                self.appoint(self.current_position)
            else:
                self.global_manager.get('available_minister_list').append(self)
                minister_utility.update_available_minister_display(self.global_manager)
        else:
            
            self.background = random.choice(global_manager.get('weighted_backgrounds'))
            self.name = self.global_manager.get('flavor_text_manager').generate_minister_name(self.background)
            self.status_number = global_manager.get('background_status_dict')[self.background]
            status_number_dict = {1: 'low', 2: 'moderate', 3: 'high', 4: 'very high'}
            self.status = status_number_dict[self.status_number]
            self.personal_savings = 5 ** (self.status_number - 1) + random.randrange(0, 6) #1-6 for lowborn, 5-10 for middle, 25-30 for high, 125-130 for very high
            
            self.skill_setup()
            self.interests_setup()
            self.corruption_setup()
            self.current_position = 'none'
            self.global_manager.get('available_minister_list').append(self)
            self.image_id = random.choice(self.global_manager.get('minister_portraits'))
            self.stolen_money = 0
            self.corruption_evidence = 0
            self.fabricated_evidence = 0
            self.just_removed = False
                
            minister_utility.update_available_minister_display(self.global_manager)
        self.stolen_already = False
        self.update_tooltip()

    def update_tooltip(self):
        '''
        Description:
            Sets this minister's tooltip to what it should be whenever the player looks at the tooltip. By default, sets tooltip to this minister's name and current office
        Input:
            None
        Output:
            None
        '''
        self.tooltip_text = []
        if not self.current_position == 'none':
            keyword = self.global_manager.get('minister_type_dict')[self.current_position] #type, like military
            self.tooltip_text.append('This is ' + self.name + ', your ' + self.current_position + '.')
        else:
            self.tooltip_text.append('This is ' + self.name + ', a recruitable minister.')
        self.tooltip_text.append("Background: " + self.background)
        self.tooltip_text.append("Social status: " + self.status)
        self.tooltip_text.append("Interests: " + self.interests[0] + " and " + self.interests[1])
        self.tooltip_text.append("Evidence: " + str(self.corruption_evidence))
        if self.just_removed and self.current_position == 'none':
            self.tooltip_text.append("This minister was just removed from office and expects to be reappointed to an office by the end of the turn.")
            self.tooltip_text.append("If not reappointed by the end of the turn, he will be permanently fired, incurring a large public opinion penalty.")

    def display_message(self, text):
        '''
        Description:
            Displays a notification message from this minister with an attached portrait
        Input:
            string text: Message to display in notification
        Output:
            None
        '''
        minister_icon_coordinates = (scaling.scale_width(self.global_manager.get('notification_manager').notification_x - 140, self.global_manager), scaling.scale_height(440, self.global_manager))
        minister_position_icon = images.dice_roll_minister_image(minister_icon_coordinates, scaling.scale_width(100, self.global_manager), scaling.scale_height(100, self.global_manager), ['strategic', 'ministers', 'europe'],
            self, 'position', self.global_manager, True)
        minister_portrait_icon = images.dice_roll_minister_image(minister_icon_coordinates, scaling.scale_width(100, self.global_manager), scaling.scale_height(100, self.global_manager), ['strategic', 'ministers', 'europe'],
            self, 'portrait', self.global_manager, True)
        self.global_manager.get('notification_manager').minister_message_queue.append(self)
        notification_tools.display_notification(text, 'minister', self.global_manager, 0)

    def steal_money(self, value, theft_type = 'none'):
        '''
        Description:
            Steals money from a company action, giving this minister money but causing a chance to be caught by the prosecutor. If caught by the prosecutor, the prosecutor may create evidence and report to the player, or, if corrupt,
                take a bribe to do nothing
        Input:
            double value: Amount of money stolen
            string theft_type = 'none': Type of theft, used in prosecutor report description
        Output:
            None
        '''
        prosecutor = self.global_manager.get('current_ministers')['Prosecutor']
        if not prosecutor == 'none':
            if self.global_manager.get('DEBUG_show_minister_stealing'):
                print(self.current_position + " " + self.name + " stole " + str(value) + " money from " + self.global_manager.get('theft_type_descriptions')[theft_type] + ".")
            difficulty = self.no_corruption_roll(6)
            result = prosecutor.no_corruption_roll(6)
            if (not prosecutor == self) and result >= difficulty: #caught by prosecutor if prosecutor succeeds skill contest roll
                if prosecutor.check_corruption(): #if prosecutor takes bribe, split money
                    prosecutor.stolen_money += (value / 2)
                    self.stolen_money += (value / 2)
                    if self.global_manager.get('DEBUG_show_minister_stealing'):
                        print("The theft was caught by the prosecutor, who accepted a bribe to not create evidence.")
                        print(prosecutor.current_position + " " + prosecutor.name + " has now stolen a total of " + str(prosecutor.stolen_money) + " money.")
                else: #if prosecutor refuses bribe, still keep money but create evidence
                    self.stolen_money += value
                    self.corruption_evidence += 1
                    evidence_message = ""

                    evidence_message += "Prosecutor " + prosecutor.name + " suspects that " + self.current_position + " " + self.name + " just engaged in corrupt activity relating to "
                    evidence_message += self.global_manager.get('theft_type_descriptions')[theft_type] + " and has filed a piece of evidence against him. /n /n"
                    evidence_message += "There are now " + str(self.corruption_evidence) + " piece" + utility.generate_plural(self.corruption_evidence) + " of evidence against " + self.name + ". /n /n"
                    evidence_message += "Each piece of evidence can help in a trial to remove a corrupt minister from office. /n /n"
                    prosecutor.display_message(evidence_message)
                    if self.global_manager.get('DEBUG_show_minister_stealing'):
                        print("The theft was caught by the prosecutor, who chose to create evidence.") 
            else: #if not caught, keep money
                self.stolen_money += value
                if self.global_manager.get('DEBUG_show_minister_stealing') and not prosecutor == self:
                    print("The theft was not caught by the prosecutor.")
        if self.global_manager.get('DEBUG_show_minister_stealing'):
            print(self.current_position + " " + self.name + " has now stolen a total of " + str(self.stolen_money) + " money.")

        if value > 0:
            self.global_manager.get('evil_tracker').change(2)
                
    def to_save_dict(self):
        '''
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                'name': string value - This minister's name
                'current_position': string value - Office that this minister is currently occupying, or 'none' if no office occupied
                'background': string value - Career background of minister, determines social status and skills
                'personal savings': double value - How much non-stolen money this minister has based on their social status
                'general_skill': int value - Value from 1 to 3 that changes what is added to or subtracted from dice rolls
                'specific_skills': dictionary value - String keys corresponding to int values to record skill values for each minister office
                'interests': string list value - List of strings describing the skill categories this minister is interested in
                'corruption': int value - Measure of how corrupt a minister is, with 6 having a 1/2 chance to steal, 5 having 1/3 chance, etc.
                'image_id': string value - File path to the image used by this minister
                'stolen_money': double value - Amount of money this minister has stolen or taken in bribes
                'just_removed': boolean value - Whether this minister was just removed from office and will be fired at the end of the turn
                'corruption_evidence': int value - Number of pieces of evidence that can be used against this minister in a trial, includes fabricated evidence
                'fabricated_evidence': int value - Number of temporary fabricated pieces of evidence that can be used against this minister in a trial this turn
        '''    
        save_dict = {}
        save_dict['name'] = self.name
        save_dict['current_position'] = self.current_position
        save_dict['general_skill'] = self.general_skill
        save_dict['specific_skills'] = self.specific_skills
        save_dict['interests'] = self.interests
        save_dict['corruption'] = self.corruption
        save_dict['image_id'] = self.image_id
        save_dict['stolen_money'] = self.stolen_money
        save_dict['corruption_evidence'] = self.corruption_evidence
        save_dict['fabricated_evidence'] = self.fabricated_evidence
        save_dict['just_removed'] = self.just_removed
        save_dict['background'] = self.background
        save_dict['personal_savings'] = self.personal_savings
        return(save_dict)

    def roll(self, num_sides, min_success, max_crit_fail, value, roll_type, predetermined_corruption = False):
        '''
        Description:
            Rolls and returns the result of a die with the inputted number of sides, modifying the result based on skill and possibly lying about the result based on corruption
        Input:
            int num_sides: Number of sides on the die rolled
            int min_success: Minimum roll required for a success
            int max_crit_fail: Maximum roll required for a critical failure
            double value: Amount of money being spent by company to make this roll, can be stolen
            string roll_type: Type of roll being made, used in prosector report description if minister steals money and is caught
            boolean predetermined_corruption = False: Whether the corruption roll has already been made for this situation
        Output:
            int: Returns the roll's modified result
        '''
        min_result = 1
        max_result = num_sides
        result = random.randrange(1, num_sides + 1)
        result += self.get_roll_modifier()
        
        if (predetermined_corruption or self.check_corruption()):
            if not self.stolen_already: #true if stealing
                self.steal_money(value, roll_type)
            result = random.randrange(max_crit_fail + 1, min_success) #if crit fail on 1 and success on 4+, do random.randrange(2, 4), pick between 2 and 3

        if result < min_result:
            result = min_result
        elif result > max_result:
            result = max_result

        #if corrupt, chance to choose random non-critical failure result
        if result > num_sides:
            result = num_sides
        return(result)

    def no_corruption_roll(self, num_sides):
        '''
        Description:
            Rolls and returns the result of a die with the inputted number of sides, modifying the result based on skill with the assumption that corruption has already failed to occur or otherwise does not allow for corruption
        Input:
            int num_sides: Number of sides on the die rolled
        Output:
            int: Returns the roll's modified result
        '''
        min_result = 1
        max_result = num_sides
        result = random.randrange(1, num_sides + 1)
        result += self.get_roll_modifier()
        
        if result < min_result:
            result = min_result
        elif result > max_result:
            result = max_result

        return(result)

    def roll_to_list(self, num_sides, min_success, max_crit_fail, value, roll_type, num_dice): #use when multiple dice are being rolled, makes corruption independent of dice
        '''
        Description:
            Rolls and returns the result of the inputted number of dice each with the inputted number of sides, modifying the results based on skill and possibly lying about the result based on corruption
        Input:
            int num_sides: Number of sides on the die rolled
            int min_success: Minimum roll required for a success
            int max_crit_fail: Maximum roll required for a critical failure
            double value: Amount of money being spent by company to make this roll, can be stolen
            string roll_type: Type of roll being made, used in prosector report description if minister steals money and is caught
            int num_dice: How many dice to roll
        Output:
            int list: Returns a list of the rolls' modified results
        '''
        results = []
        if self.check_corruption():
            self.steal_money(value, roll_type)
            self.stolen_already = True
            corrupt_index = random.randrange(0, num_dice)
            for i in range(num_dice): #num_sides, min_success, max_crit_fail, value, roll_type, predetermined_corruption = False
                if i == corrupt_index: #if rolling multiple dice, choose one of the dice randomly and make it the corrupt result, making it a non-critical failure
                    results.append(self.roll(num_sides, min_success, max_crit_fail, value, roll_type, True))
                else: #for dice that are not chosen, can be critical or non-critical failure because higher will be chosen in case of critical failure, no successes allowed
                    results.append(self.roll(num_sides, min_success, 0, value, roll_type, True)) #0 for max_crit_fail allows critical failure numbers to be chosen
        else: #if not corrupt, just roll with minister modifier
            for i in range(num_dice):
                results.append(self.no_corruption_roll(num_sides))
        self.stolen_already = False
        return(results)
            
    def attack_roll_to_list(self, own_modifier, enemy_modifier, value, roll_type, num_dice):
        '''
        Description:
            Rolls and returns the result of the inputted number of 6-sided dice along with the enemy unit's roll in combat, modifying the results based on skill and possibly lying about the result based on corruption
        Input:
            int own_modifier: Modifier added to the friendly unit's roll, used to create realistic inconclusive results when corrupt
            int enemy_modifier: Modifier added to the enemy unit's roll, used to create realistic inconclusive results when corrupt
            double value: Amount of money being spent by company to make this roll, can be stolen
            string roll_type: Type of roll being made, used in prosector report description if minister steals money and is caught
            int num_dice: number of dice rolled by the friendly unit, not including the one die rolled by the enemy unit
        Output:
            int list: Returns a list of the rolls' modified results, with the first item being the enemy roll
        '''
        results = []
        if self.check_corruption():
            self.steal_money(value, roll_type)
            self.stolen_already = True
            for i in range(num_dice):
                results.append(0)
            difference = 10
            while difference >= 2: #keep rolling until a combination of attacker and defender rolls with an inconclusive result is found
                own_roll = random.randrange(1, 7)
                enemy_roll = random.randrange(1, 7)
                difference = abs((own_roll + own_modifier) - (enemy_roll + enemy_modifier))
            corrupt_index = random.randrange(0, num_dice)
            for i in range(num_dice):
                if i == corrupt_index: #if rolling multiple dice, choose one of the dice randomly to be the chosen result, with the others being lower
                    results[i] = own_roll
                else:
                    results[i] = random.randrange(1, own_roll + 1) # if own_roll is 1, range is 1-2 non-inclusive, always chooses 1
            results = [enemy_roll] + results #inserts enemy roll at beginning

        else: #if not corrupt, just roll with minister modifier
            for i in range(num_dice):
                results.append(self.no_corruption_roll(6))
            enemy_roll = random.randrange(1, 7)
            results = [enemy_roll] + results
        self.stolen_already = False
        return(results)

    def appoint(self, new_position):
        '''
        Description:
            Appoints this minister to a new office, putting it in control of relevant units. If the new position is 'none', removes the minister from their current office
        Input:
            string new_position: Office to appoint this minister to, like 'Minister of Trade'. If this equals 'none', fires this minister
        Output:
            None
        '''
        old_position = self.current_position
        if not self.current_position == 'none': #if removing, set old position to none
            self.global_manager.get('current_ministers')[self.current_position] = 'none'
        self.current_position = new_position
        self.global_manager.get('current_ministers')[new_position] = self
        for current_pmob in self.global_manager.get('pmob_list'):
            current_pmob.update_controlling_minister()
        if not new_position == 'none': #if appointing
            self.global_manager.set('available_minister_list', utility.remove_from_list(self.global_manager.get('available_minister_list'), self))
            if self.global_manager.get('available_minister_left_index') >= len(self.global_manager.get('available_minister_list')) - 3:
                self.global_manager.set('available_minister_left_index', len(self.global_manager.get('available_minister_list')) - 3) #move available minister display up because available minister was removed
        else:
            self.global_manager.get('available_minister_list').append(self)
            self.global_manager.set('available_minister_left_index', len(self.global_manager.get('available_minister_list')) - 3) #move available minister display to newly fired minister
        for current_minister_type_image in self.global_manager.get('minister_image_list'):
            if current_minister_type_image.minister_type == new_position:
                current_minister_type_image.calibrate(self)
            elif current_minister_type_image.minister_type == old_position:
                current_minister_type_image.calibrate('none')
        if self.global_manager.get('displayed_minister') == self:
            minister_utility.calibrate_minister_info_display(self.global_manager, self) #update minister label
        minister_utility.update_available_minister_display(self.global_manager)
        
        if not self.global_manager.get('minister_appointment_tutorial_completed'):
            completed = True
            for current_position in self.global_manager.get('minister_types'):
                if self.global_manager.get('current_ministers')[current_position] == 'none':
                    completed = False
            if completed:
                self.global_manager.set('minister_appointment_tutorial_completed', True)
                notification_tools.show_tutorial_notifications(self.global_manager)

    def skill_setup(self):
        '''
        Description:
            Sets up the general and specific skills for this minister when it is created
        Input:
            None
        Output:
            None
        '''
        self.general_skill = random.randrange(1, 4) #1-3, general skill as in all fields, not military
        self.specific_skills = {}
        background_skill = random.choice(self.global_manager.get('background_skills_dict')[self.background])
        if background_skill == 'random':
            background_skill = random.choice(self.global_manager.get('skill_types'))
        for current_minister_type in self.global_manager.get('minister_types'):
            self.specific_skills[current_minister_type] = random.randrange(0, 4) #0-3
            if self.global_manager.get('minister_type_dict')[current_minister_type] == background_skill:
                self.specific_skills[current_minister_type] += 1

    def interests_setup(self):
        '''
        Description:
            Chooses and sets 2 interest categories for this minister. One of a minister's interests is one of their best skills, while the other is randomly chosen
        Input:
            None
        Output:
            None
        '''
        skill_types = self.global_manager.get('skill_types')
        type_minister_dict = self.global_manager.get('type_minister_dict')
        highest_skills = []
        highest_skill_number = 0
        for current_skill in skill_types:
            if len(highest_skills) == 0 or self.specific_skills[type_minister_dict[current_skill]] > highest_skill_number:
                highest_skills = [current_skill]
                highest_skill_number = self.specific_skills[type_minister_dict[current_skill]]
            elif self.specific_skills[type_minister_dict[current_skill]] == highest_skill_number:
                highest_skills.append(current_skill)
        first_interest = random.choice(highest_skills)
        second_interest = first_interest
        while second_interest == first_interest:
            second_interest = random.choice(skill_types)

        if random.randrange(1, 7) >= 4:
            self.interests = [first_interest, second_interest]
        else:
            self.interests = [second_interest, first_interest]

    def corruption_setup(self):
        '''
        Description:
            Sets up the corruption level for this minister when it is created
        Input:
            None
        Output:
            None
        '''
        self.corruption = random.randrange(1, 7) #1-7
        self.corruption_threshold = 10 - self.corruption #minimum roll on D6 required for corruption to occur
            
    def check_corruption(self): #returns true if stealing for this roll
        '''
        Description:
            Checks and returns whether this minister will steal funds and lie about the dice roll results on a given roll
        Input:
            None
        Output:
            boolean: Returns True if this minister will be corrupt for the roll
        '''
        if self.global_manager.get('DEBUG_band_of_thieves'):
            return(True)
        elif self.global_manager.get('DEBUG_ministry_of_magic'):
            return(False)
            
        if random.randrange(1, 7) >= self.corruption_threshold:
            if random.randrange(1, 7) >= self.global_manager.get('fear'): #higher fear reduces chance of exceeding threshold and stealing
                return(True)
            else:
                if self.global_manager.get('DEBUG_show_fear'):
                    print(self.name + " was too afraid to steal money")
                return(False)
        else:
            return(False)

    def gain_experience(self):
        '''
        Description:
            Gives this minister a chance of gaining skill in their current cabinet position if they have one
        Input:
            None
        Output:
            None
        '''
        if not self.current_position == 'none':
            if self.specific_skills[self.current_position] < 3:
                self.specific_skills[self.current_position] += 1

    def estimate_expected(self, base, allow_decimals = True):
        '''
        Description:
            Calculates and returns an expected number within a certain range of the inputted base amount, with accuracy based on this minister's skill. A prosecutor will attempt to estimate what the output of production, commodity
                sales, etc. should be
        Input:
            double base: Target amount that estimate is approximating
        Output:
            double: Returns the estimaed number
        '''
        if self.no_corruption_roll(6) >= 4:
            return(base)
        else:
            multiplier = random.randrange(80, 121)
            multiplier /= 100
            if allow_decimals:
                return(round(base * multiplier, 2))
            else:
                return(round(base * multiplier))

    def get_skill_modifier(self):
        '''
        Description:
            Checks and returns the dice roll modifier for this minister's current office. A combined general and specific skill of <= 2 gives a -1 modifier, >5 5 gives a +1 modifier and other give a 0 modifier
        Input:
            None
        Output:
            int: Returns the dice roll modifier for this minister's current office
        '''
        if not self.current_position == 'none':
            skill = self.general_skill + self.specific_skills[self.current_position]
        else:
            skill = self.general_skill
        if skill <= 2: #1-2
            return(-1)
        elif skill <= 4: #3-4
            return(0)
        else: #5-6
            return(1)

    def get_roll_modifier(self):
        '''
        Description:
            Returns the modifier this minister will apply to a given roll. As skill has only a half chance of applying to a given roll, the returned value may vary
        Input:
            None
        Output:
            int: Returns the modifier this minister will apply to a given roll. As skill has only a half chance of applying to a given roll, the returned value may vary
        '''
        if self.global_manager.get('DEBUG_ministry_of_magic'):
            return(5)
        if random.randrange(1, 3) == 1: #half chance to apply skill modifier, otherwise return 0
            return(self.get_skill_modifier())
        else:
            return(0)

    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        Input:
            None
        Output:
            None
        '''
        if not self.current_position == 'none':
            self.global_manager.get('current_ministers')[self.current_position] = 'none'
            for current_minister_image in self.global_manager.get('minister_image_list'):
                if current_minister_image.minister_type == self.current_position:
                    current_minister_image.calibrate('none')
            self.current_position = 'none'
        #self.global_manager.set('available_minister_left_index', self.global_manager.get('available_minister_left_index') - 1)
        self.global_manager.set('minister_list', utility.remove_from_list(self.global_manager.get('minister_list'), self))
        self.global_manager.set('available_minister_list', utility.remove_from_list(self.global_manager.get('available_minister_list'), self))
        minister_utility.update_available_minister_display(self.global_manager)

    def respond(self, event):
        '''
        Description:
            Causes this minister to display a message notification and sometimes cause effects based on their background and social status when an event like being fired happens
        Input:
            string event: Type of event the minister is responding to, like 'fired'
        Output:
            None
        '''
        text = ""
        public_opinion_change = 0

        if self.status_number >= 3:
            if self.background == 'politician':
                third_party = ['the media', 'the prime minister', 'Parliament']
            elif self.background == 'industrialist':
                third_party = ['the business community', 'my investors', 'my friends']
            else: #royal heir or aristocrat
                third_party = ['my family', 'my cousins', 'the nobility']
        
        if event == 'first hired':
            if self.status_number >= 3:
                public_opinion_change = self.status_number + random.randrange(-1, 2)
                if self.status_number == 4:
                    public_opinion_change += 6
            text += "From: " + self.name + " /n /n"
            intro_options = ["You have my greatest thanks for appointing me to your cabinet. ",
                             "Honored governor, my gratitude knows no limits. ",
                             "Finally, a chance to bring glory to our empire! "]
            text += random.choice(intro_options)
            
            middle_options = ["I shall ensure my duties are completed with the utmost precision and haste. ",
                              "I will never betray you, I swear. ",
                              "Nothing will keep us from completing our divine mission. "]
            text += random.choice(middle_options)

            if self.status_number >= 3:
                conclusion_options = ["I'll make sure to put a good word in with " + random.choice(third_party) + " about you.",
                                      "I'm sure " + random.choice(third_party) + " would enjoy hearing about this wise decision.",
                                      "Perhaps I could pull some strings with " + random.choice(third_party) + " to help repay you?"]
                text += random.choice(conclusion_options)
                text += " /n /n /nYou have gained " + str(public_opinion_change) + " public opinion. /n /n"
                
            else:
                heres_to_options = ['victory', 'conquest', 'glory']
                conclusion_options = ["Please send the other ministers my regards - I look forward to working with them. ",
                                      "Here's to " + random.choice(heres_to_options) + "!",
                                      "We're going to make a lot of money together! "]
                text += random.choice(conclusion_options) + ' /n /n /n'
            
            if self.status_number == 1:
                public_opinion_change = -1
                text += "While lowborn can easily be removed should they prove incompetent or disloyal, it reflects poorly on the company to appoint them as ministers. /n /n"
                text += "You have lost " + str(-1 * public_opinion_change) + " public opinion. /n /n"
            
        elif event == 'fired':
            multiplier = random.randrange(8, 13) / 10.0 #0.8-1.2
            public_opinion_change = -10 * self.status_number * multiplier #4-6 for lowborn, 32-48 for very high
            self.global_manager.get('evil_tracker').change(2)
            text += "From: " + self.name + " /n /n"
            intro_options = ["How far our empire has fallen... ",
                             "You have made a very foolish decision in firing me. ",
                             "I was just about to retire, and you had to do this? ",
                             "I was your best minister - you're all doomed without me. "]
            text += random.choice(intro_options)
            
            if self.background == 'royal heir':
                family_members = ['father', 'mother', 'father', 'mother', 'uncle', 'aunt', 'brother', 'sister']
                threats = ['killed', 'executed', 'decapitated', 'thrown in jail', 'banished', 'exiled']
                text += "My " + random.choice(family_members) + " could have you " + random.choice(threats) + " for this. "
            elif self.status_number >= 3:
                warnings = ["You better be careful making enemies in high places, friend. ",
                            'Parliament will cut your funding before you can even say "bribe". ',
                            "You have no place in our empire, you greedy upstart. ",
                            "Learn how to respect your betters - we're not savages. "]
                text += random.choice(warnings)
            else:
                warnings = ["Think of what will happen to the " + random.choice(self.global_manager.get('commodity_types')) + " prices after the media hears about this! ",
                            "You think you can kick me down from your palace in the clouds? ",
                            "I'll make sure to tell all about those judges you bribed. ",
                            "So many dead... what will be left of this land by the time you're done? ",
                            "What next? Will you murder me like you did those innocents in the village? ",
                            "You'll burn in hell for this. ",
                            "Watch your back, friend. "]
                text += random.choice(warnings)
            text += " /n /n /nYou have lost " + str(-1 * public_opinion_change) + " public opinion. /n"
            text += self.name + " has been fired and removed from the game. /n /n"
            
        elif event == 'prison':
            text += "From: " + self.name + " /n /n"
            if self.status_number >= 3:
                intro_options = ["Do you know what we used to do to upstarts like you?",
                                 "This is nothing, " + random.choice(third_party) + " will get me out within days.",
                                 "You better be careful making enemies in high places, friend. "]
            else:
                intro_options = ["I would've gotten away with it, too, if it weren't for that meddling prosecutor.",
                                 "Get off your high horse - we could have done great things together.",
                                 "How much money would it take to change your mind?"]
            intro_options.append("Do you even know how many we killed? We all deserve this.")
            intro_options.append("I'm innocent, I swear!")
            intro_options.append("You'll join me here soon: sic semper tyrannis.")
            
            text += random.choice(intro_options)
            text += " /n /n /n"
            text += self.name + " is now in prison and has been removed from the game. /n /n"

        elif event == 'retirement':
            if self.current_position == 'none':
                text = self.name + " no longer desires to be appointed as a minister and has left the pool of available minister appointees. /n /n"
            else:
                if random.randrange(0, 100) < self.global_manager.get('evil'):
                    tone = 'guilty'
                else:
                    tone = 'content'
                    
                if self.stolen_money >= 10.0 and random.randrange(1, 7) >= 4:
                    tone = 'confession'
                    
                if tone == 'guilty':
                    intro_options = ["I can't believe some of the things I saw here. ",
                                     "What gave us the right to conquer this place? ",
                                     "I see them every time I close my eyes - I can't keep doing this."]
                    middle_options = ["I hear God weeping at the crimes we commit in His name.",
                                      "We sent so many young men to die just to fill our coffers. ",
                                      "We're no better than the wild beasts we fear. "]
                    conclusion_options = ["I pray we will be forgiven for the things we've done, and you ought to do the same. ",
                                          "Was it all worth it? ",
                                          "I promise to never again set foot on this stolen continent. "]
                elif tone == 'content':
                    intro_options = ["I'm sorry to say it, but I've gotten too old for this. ",
                                     "This has been a pleasant journey, but life has greater opportunities planned for me. ",
                                     "Unfortunately, I can no longer work in your cabinet - I am needed back home. "]
                    middle_options = ["Can you believe it, though? We singlehandedly civilized this place. ",
                                      "I wish I could stay. The thrill of adventure, the wonders I've seen here. It's like I was made for this. ",
                                      "Never has the world seen such glory as what we have brought here. "]
                    conclusion_options = ["I trust you'll continue to champion the cause of our God and our empire. ",
                                          "I hope to live many more years, but my best were spent here with you. ",
                                          "Promise me you'll protect what we built here. Never forget our mission, and never grow complacent. "]
                elif tone == 'confession':
                    intro_options = ["You fool! I took " + str(self.stolen_money) + " money from behind your back, and you just looked the other way. ",
                                     "I'll have an amazing retirement with the " + str(self.stolen_money) + " money you let me steal. ",
                                     "I could tell you just how much money I stole from you over the years, but I'll spare you the tears. "]
                    middle_options = ["We represent the empire's best, but so many of the ministers are just thieves behind your back. ",
                                      "Did you really believe all those setbacks and delays I invented? ",
                                      "Believe it or not, I was always one of the lesser offenders. "]
                    conclusion_options = ["We aren't so different, you and I - we're both just here to make money. Who ever cared about the empire? ",
                                          "You'll never see me again, of course, but I wish I could see the look on your face. ",
                                          "If I had the chance, I'd do it all again. "]
                text += random.choice(intro_options) + random.choice(middle_options) + random.choice(conclusion_options)
                text += ' /n /n /n' + self.current_position + " " + self.name + " has chosen to step down and retire. /n /n"
                text += "Their position will need to be filled by a replacement as soon as possible for your company to continue operations. /n /n"
        self.global_manager.get('public_opinion_tracker').change(public_opinion_change)
        if not text == "":
            self.display_message(text)
