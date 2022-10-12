#Contains functions that manage market prices and sale of commodities

import random
from . import text_tools
from . import utility

def adjust_prices(global_manager):
    '''
    Description:
        Increases the prices of 2 normal commodities by 1 and decreases the price of 1 normal commodity by 1. Also has a 1/3 chance to decrease the cost of consumer goods by 1 and a 1/6 chance to increase the cost of consumer goods by 1
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    num_increased = 2
    num_decreased = 1
    for i in range(4):
        changed_commodity = random.choice(global_manager.get('commodity_types'))
        while changed_commodity == 'consumer goods':
            changed_commodity = random.choice(global_manager.get('commodity_types')) #consumer goods price is changed separately and should not be changed here
        change_price(changed_commodity, 1, global_manager)
    for i in range(2):
        changed_commodity = random.choice(global_manager.get('commodity_types'))
        while changed_commodity == 'consumer goods':
            changed_commodity = random.choice(global_manager.get('commodity_types')) #consumer goods price is changed separately and should not be changed here
        change_price(changed_commodity, -1, global_manager)
        
    consumer_goods_roll = random.randrange(1, 7)
    
    if consumer_goods_roll == 1:
        change_price('consumer goods', 1, global_manager)
    elif consumer_goods_roll >= 4:
        change_price('consumer goods', -1, global_manager)

def change_price(changed_commodity, num_change, global_manager):
    '''
    Description:
        Changes the price of the inputted commodity by the inputted amount
    Input:
        string changed_commodity: Type of commodity whose price changes, like 'exotic wood'
        int num_change: Amount the price of the inputted commodity increases
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    global_manager.get('commodity_prices')[changed_commodity] += num_change
    if global_manager.get('commodity_prices')[changed_commodity] < 1:
        global_manager.get('commodity_prices')[changed_commodity] = 1
    global_manager.get('commodity_prices_label').update_label()

def set_price(changed_commodity, new_value, global_manager):
    '''
    Description:
        Sets the price of the inputted commodity to the inputted amount
    Input:
        string changed_commodity: Type of commodity whose price changes, like 'exotic wood'
        int new_value: New price of the inputted commodity
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    global_manager.get('commodity_prices')[changed_commodity] = new_value
    if global_manager.get('commodity_prices')[changed_commodity] < 1:
        global_manager.get('commodity_prices')[changed_commodity] = 1
    global_manager.get('commodity_prices_label').update_label()

def sell(seller, sold_commodity, num_sold, global_manager):
    '''
    Description:
        Sells the inputted amount of the inputted commodity from the inputted actor's inventory, removing it from the inventory and giving an amount of money corresponding to the commodity's price. Each unit sold also has a 1/6 chance
            to decrease the price of the commodity by 1
    Input:
        actor seller: actor whose inventory the sold commodity is removed from
        string sold_commodity: Type of commodity that is sold, like 'exotic wood'
        int num_sold: Number of units of the commodity sold
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    global_manager.get('sold_commodities')[sold_commodity] += num_sold
    for i in range(num_sold):
        seller.change_inventory(sold_commodity, -1)

def attempt_worker_upkeep_change(change_type, worker_type, global_manager):
    '''
    Description:
        Controls the chance to increase worker upkeep when a worker leaves the labor pool or decrease worker upkeep when a worker joins the labor pool
    Input:
        string change_type: 'increase' or 'decrease' depending on whether a worker is being added to or removed from the labor pool, decides whether worker price increases or decreases
        string worker_type: 'European' or 'African', decides which type of worker has a price change
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    if random.randrange(1, 7) >= 4: #half chance of change
        current_price = global_manager.get(worker_type.lower() + '_worker_upkeep')
        if change_type == 'increase':
            changed_price = round(current_price + global_manager.get('worker_upkeep_fluctuation_amount'), 2)
            global_manager.set(worker_type.lower() + '_worker_upkeep', changed_price)
            text_tools.print_to_screen("Hiring " + utility.generate_article(worker_type) + " " + worker_type + " worker increased " + worker_type + " worker upkeep from " + str(current_price) + " to " + str(changed_price) + ".", global_manager)
        elif change_type == 'decrease':
            changed_price = round(current_price - global_manager.get('worker_upkeep_fluctuation_amount'), 2)
            if changed_price >= global_manager.get('min_' + worker_type.lower() + '_worker_upkeep'):
                global_manager.set(worker_type.lower() + '_worker_upkeep', changed_price)
                text_tools.print_to_screen("Adding " + utility.generate_article(worker_type) + " " + worker_type + " worker to the labor pool decreased " + worker_type + " worker upkeep from " + str(current_price) + " to " + str(changed_price) + ".", global_manager)

def attempt_slave_recruitment_cost_change(change_type, global_manager):
    '''
    Description:
        Controls the chance to increase slave recruitment cost when a slave worker is bought or decrease the recruitment cost over time
    Input:
        string change_type: 'increase' or 'decrease' depending on whether a worker is being added to or removed from the labor pool, decides whether worker price increases or decreases
        string worker_type: 'European' or 'African', decides which type of worker has a price change
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    if random.randrange(1, 7) >= 4:
        current_price = global_manager.get('recruitment_costs')['slave workers']
        if change_type == 'increase':
            changed_price = round(current_price + global_manager.get('slave_recruitment_cost_fluctuation_amount'), 2)
            global_manager.get('recruitment_costs')['slave workers'] = changed_price
            text_tools.print_to_screen("Buying slave workers increased the recruitment cost of slave workers from " + str(current_price) + " to " + str(changed_price) + ".", global_manager)
        elif change_type == 'decrease':
            changed_price = round(current_price - global_manager.get('slave_recruitment_cost_fluctuation_amount'), 2)
            if changed_price >= global_manager.get('min_slave_worker_recruitment_cost'):
                global_manager.get('recruitment_costs')['slave workers'] = changed_price
                text_tools.print_to_screen("Adding slaves to the slave recruitment pool decreased the recruitment cost of slave workers from " + str(current_price) + " to " + str(changed_price) + ".", global_manager)

def calculate_subsidies(global_manager, projected = False):
    '''
    Description:
        Calculates and returns the company's subsidies for the turn, taking into account the company's public opinion and savings
    Input:
        global_manager_template global_manager: Object that accesses shared variables
        boolean projected = False: Whether these subsidies are projected or actually taking place - projected subsidies have no random element
    Output:
        double: Returns the company's subsidies for the turn
    '''
    public_opinion = global_manager.get('public_opinion')
    if projected:
        if public_opinion < 50:
            public_opinion += 1
        elif public_opinion > 50:
            public_opinion -= 1
    else:
        public_opinion += random.randrange(-10, 11)
        
    subsidies = public_opinion / 5
    for i in range(599, round(global_manager.get('money')), 100): #remove 10% of subsidies for each 100 money over 500
        subsidies *= 0.9
    if subsidies < 1:
        subsidies = 0
    return(round(subsidies, 1)) #9.8 for 49 public opinion

def calculate_total_worker_upkeep(global_manager):
    '''
    Description:
        Calculates and returns the total upkeep of the company's workers
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        double: Returns the total upkeep of the company's workers
    '''
    num_african_workers = global_manager.get('num_african_workers')
    african_worker_upkeep = global_manager.get('african_worker_upkeep')
    total_african_worker_upkeep = round(num_african_workers * african_worker_upkeep, 2)

    num_european_workers = global_manager.get('num_european_workers')
    european_worker_upkeep = global_manager.get('european_worker_upkeep')
    total_european_worker_upkeep = round(num_european_workers * european_worker_upkeep, 2)

    num_slave_workers = global_manager.get('num_slave_workers')
    slave_worker_upkeep = global_manager.get('slave_worker_upkeep')
    total_slave_worker_upkeep = round(num_slave_workers * slave_worker_upkeep, 2)
        
    num_workers = num_african_workers + num_european_workers + num_slave_workers
    total_upkeep = round(total_african_worker_upkeep + total_european_worker_upkeep + total_slave_worker_upkeep, 2)
    return(total_upkeep)

def calculate_end_turn_money_change(global_manager):
    '''
    Description:
    Calculates and returns an estimate of how much money the company will gain or lose at the end of the turn
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    '''
    estimated_change = 0
    estimated_change += calculate_subsidies(global_manager, True)
    estimated_change -= calculate_total_worker_upkeep(global_manager)
    for current_loan in global_manager.get('loan_list'):
        estimated_change -= current_loan.interest
    return(round(estimated_change, 2))
    
class loan():
    '''
    Object corresponding to a loan with principal, interest, and duration
    '''
    def __init__(self, from_save, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'principal': int value - Amount of money borrowed by the loan
                'interest': int value - Cost of interest payments for this loan each turn
                'remaining_duration': int value - Number of remaining turns/interest payments
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''    
        self.global_manager = global_manager
        self.principal = input_dict['principal']
        self.interest = input_dict['interest']
        self.remaining_duration = input_dict['remaining_duration']
        self.total_to_pay = self.interest * self.remaining_duration
        self.global_manager.get('loan_list').append(self)
        if not from_save:
            self.global_manager.get('money_tracker').change(self.principal, 'loans')
            text_tools.print_to_screen("You have accepted a " + str(self.principal) + " money loan with interest payments of " + str(self.interest) + "/turn for " + str(self.remaining_duration) + " turns.", self.global_manager)

    def to_save_dict(self):
        '''
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                'init_type': string value - Represents the type of object this is, used to initialize the correct type of object on loading
                'principal': int tuple value - Amount of money borrowed by the loan
                'interest': int value - Cost of interest payments for this loan each turn
                'remaining_duration': int value - Number of remaining turns/interest payments
        '''
        save_dict = {}
        save_dict['init_type'] = 'loan'
        save_dict['principal'] = self.principal
        save_dict['interest'] = self.interest
        save_dict['remaining_duration'] = self.remaining_duration
        return(save_dict)

    def make_payment(self):
        '''
        Description:
            Makes a payment on this loan, paying its interest cost and reducing its remaining duration
        Input:
            None
        Output:
            None
        '''
        self.global_manager.get('money_tracker').change(-1 * self.interest, 'loan interest')
        self.remaining_duration -= 1
        self.total_to_pay -= self.interest
        if self.total_to_pay <= 0:
            self.remove()

    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        Input:
            None
        Output:
            None
        '''
        total_paid = self.interest * 10
        text_tools.print_to_screen("You have finished paying off the " + str(total_paid) + " money required for your " + str(self.principal) + " money loan", self.global_manager)
        self.global_manager.set('loan_list', utility.remove_from_list(self.global_manager.get('loan_list'), self))

    def get_description(self):
        '''
        Description:
             Returns a description of this loan, includings its principal, interest, remaining duration, and remaining payment 
        Input:
            None
        Output:
            string: Returns a description of this loan, includings its principal, interest, remaining duration, and remaining payment
        '''
        message = ""
        message += str(self.principal) + " money loan with interest payments of " + str(self.interest) + " each turn. " + str(self.remaining_duration) + " turns/" + str(self.total_to_pay) + "money remaining"
        return(message)
