# Contains functions that manage market prices and sale of commodities

import random
from . import text_utility, utility
import modules.constants.constants as constants
import modules.constants.status as status


def adjust_prices():
    """
    Description:
        Increases the prices of 2 normal commodities by 1 and decreases the price of 1 normal commodity by 1. Also has a 1/3 chance to decrease the cost of consumer goods by 1 and a 1/6 chance to increase the cost of consumer goods by 1
    Input:
        None
    Output:
        None
    """
    num_increased = 4
    num_decreased = 2
    for i in range(num_increased):
        changed_commodity = random.choice(constants.commodity_types)
        while changed_commodity == "consumer goods":
            changed_commodity = random.choice(
                constants.commodity_types
            )  # consumer goods price is changed separately and should not be changed here
        change_price(changed_commodity, 1)
    for i in range(num_decreased):
        changed_commodity = random.choice(constants.commodity_types)
        while changed_commodity == "consumer goods":
            changed_commodity = random.choice(
                constants.commodity_types
            )  # consumer goods price is changed separately and should not be changed here
        change_price(changed_commodity, -1)

    consumer_goods_roll = random.randrange(1, 7)

    if consumer_goods_roll == 1:
        change_price("consumer goods", 1)
    elif consumer_goods_roll >= 4:
        change_price("consumer goods", -1)


def change_price(changed_commodity, num_change):
    """
    Description:
        Changes the price of the inputted commodity by the inputted amount
    Input:
        string changed_commodity: Type of commodity whose price changes, like 'exotic wood'
        int num_change: Amount the price of the inputted commodity increases
    Output:
        None
    """
    constants.item_prices[changed_commodity] += num_change
    if constants.item_prices[changed_commodity] < 1:
        constants.item_prices[changed_commodity] = 1
    status.commodity_prices_label.update_label()
    constants.money_label.check_for_updates()


def set_price(changed_commodity, new_value):
    """
    Description:
        Sets the price of the inputted commodity to the inputted amount
    Input:
        string changed_commodity: Type of commodity whose price changes, like 'exotic wood'
        int new_value: New price of the inputted commodity
    Output:
        None
    """
    constants.item_prices[changed_commodity] = new_value
    if constants.item_prices[changed_commodity] < 1:
        constants.item_prices[changed_commodity] = 1
    status.commodity_prices_label.update_label()


def sell(seller, sold_commodity, num_sold):
    """
    Description:
        Sells the inputted amount of the inputted commodity from the inputted actor's inventory, removing it from the inventory and giving an amount of money corresponding to the commodity's price. Each unit sold also has a 1/6 chance
            to decrease the price of the commodity by 1
    Input:
        actor seller: actor whose inventory the sold commodity is removed from
        string sold_commodity: Type of commodity that is sold, like 'exotic wood'
        int num_sold: Number of units of the commodity sold
    Output:
        None
    """
    constants.sold_commodities[sold_commodity] += num_sold
    seller.change_inventory(sold_commodity, -1 * num_sold)
    constants.money_label.check_for_updates()


def calculate_total_sale_revenue():
    """
    Description:
        Calculates and returns the total estimated revenue from sold commodities this turn
    Input:
        None
    Output:
        int: Returns the total estimated revenue from sold commodities this turn
    """
    total_sale_price = 0
    for commodity in constants.commodity_types:
        total_sale_price += (
            constants.sold_commodities[commodity] * constants.item_prices[commodity]
        )
    return total_sale_price


def attempt_worker_upkeep_change(change_type, worker_type):
    """
    Description:
        Controls the chance to increase worker upkeep when a worker leaves the labor pool or decrease worker upkeep when a worker joins the labor pool
    Input:
        string change_type: 'increase' or 'decrease' depending on whether a worker is being added to or removed from the labor pool, decides whether worker price increases or decreases
        worker_type worker_type: Like 'Colonists', decides which type of worker has a price change
    Output:
        None
    """
    if random.randrange(1, 7) >= 4:  # half chance of change
        current_price = worker_type.upkeep
        if change_type == "increase":
            changed_price = round(current_price + constants.worker_upkeep_increment, 2)
            worker_type.upkeep = changed_price
            text_utility.print_to_screen(
                f"Hiring {utility.generate_article(worker_type.name)} increased {worker_type.name} upkeep from {current_price} to {changed_price}."
            )
        elif change_type == "decrease":
            changed_price = round(current_price - constants.worker_upkeep_increment, 2)
            if changed_price >= worker_type.min_upkeep:
                worker_type.upkeep = changed_price
                text_utility.print_to_screen(
                    f"Adding {utility.generate_article(worker_type.name)} {worker_type.name} to the labor pool decreased {worker_type.name} upkeep from {current_price} to {changed_price}."
                )
        constants.money_label.check_for_updates()


def calculate_subsidies(projected=False):
    """
    Description:
        Calculates and returns the company's subsidies for the turn, taking into account the company's public opinion and savings
    Input:
        boolean projected = False: Whether these subsidies are projected or actually taking place - projected subsidies have no random element
    Output:
        double: Returns the company's subsidies for the turn
    """
    public_opinion = constants.public_opinion
    if projected:
        if public_opinion < 50:
            public_opinion += 1
        elif public_opinion > 50:
            public_opinion -= 1
    else:
        public_opinion += random.randrange(-10, 11)

    subsidies = public_opinion / 5
    for i in range(
        599, round(constants.money), 100
    ):  # remove 10% of subsidies for each 100 money over 500
        subsidies *= 0.9
    if subsidies < 1:
        subsidies = 0
    return round(subsidies, 1)  # 9.8 for 49 public opinion


def calculate_total_worker_upkeep():
    """
    Description:
        Calculates and returns the total upkeep of the company's workers
    Input:
        None
    Output:
        double: Returns the total upkeep of the company's workers
    """
    total_upkeep = 0.0
    for key, current_worker_type in status.worker_types.items():
        total_upkeep += current_worker_type.get_total_upkeep()
    return round(total_upkeep, 2)


def calculate_end_turn_money_change():
    """
    Description:
        Calculates and returns an estimate of how much money the company will gain or lose at the end of the turn
    Input:
        None
    Output:
        double: Returns an estimate of how much money the company will gain or lose at the end of the turn
    """
    estimated_change = 0
    estimated_change += calculate_subsidies(True)
    estimated_change -= calculate_total_worker_upkeep()
    for current_loan in status.loan_list:
        estimated_change -= current_loan.interest
    estimated_change += calculate_total_sale_revenue()
    return round(estimated_change, 2)


class loan:
    """
    Object corresponding to a loan with principal, interest, and duration
    """

    def __init__(self, from_save, input_dict):
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'principal': int value - Amount of money borrowed by the loan
                'interest': int value - Cost of interest payments for this loan each turn
                'remaining_duration': int value - Number of remaining turns/interest payments
        Output:
            None
        """
        self.principal = input_dict["principal"]
        self.interest = input_dict["interest"]
        self.remaining_duration = input_dict["remaining_duration"]
        self.total_to_pay = self.interest * self.remaining_duration
        status.loan_list.append(self)
        if not from_save:
            constants.money_tracker.change(self.principal, "loan")
            text_utility.print_to_screen(
                "You have accepted a "
                + str(self.principal)
                + " money loan with interest payments of "
                + str(self.interest)
                + "/turn for "
                + str(self.remaining_duration)
                + " turns."
            )
            constants.money_label.check_for_updates()

    def to_save_dict(self):
        """
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
        """
        save_dict = {}
        save_dict["init_type"] = constants.LOAN
        save_dict["principal"] = self.principal
        save_dict["interest"] = self.interest
        save_dict["remaining_duration"] = self.remaining_duration
        return save_dict

    def make_payment(self):
        """
        Description:
            Makes a payment on this loan, paying its interest cost and reducing its remaining duration
        Input:
            None
        Output:
            None
        """
        constants.money_tracker.change(-1 * self.interest, "loan_interest")
        self.remaining_duration -= 1
        self.total_to_pay -= self.interest
        if self.total_to_pay <= 0:
            self.remove_complete()

    def remove_complete(self):
        """
        Description:
            Removes this object and deallocates its memory - defined for any removable object w/o a superclass
        Input:
            None
        Output:
            None
        """
        self.remove()
        del self

    def remove(self):
        """
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        Input:
            None
        Output:
            None
        """
        total_paid = self.interest * 10
        text_utility.print_to_screen(
            f"You have finished paying off the {total_paid} money required for your {self.principal} money loan"
        )
        status.loan_list = utility.remove_from_list(status.loan_list, self)

    def get_description(self):
        """
        Description:
             Returns a description of this loan, includings its principal, interest, remaining duration, and remaining payment
        Input:
            None
        Output:
            string: Returns a description of this loan, includings its principal, interest, remaining duration, and remaining payment
        """
        return f"{self.principal} money loan with interest payments of {self.interest} each turn. {self.remaining_duration} turns/{self.total_to_pay} money remaining"
