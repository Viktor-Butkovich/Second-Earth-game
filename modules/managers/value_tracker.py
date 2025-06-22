# Contains variable getter/setter/display management singletons

from modules.constants import constants, status, flags


class value_tracker:
    """`
    Object that controls the value of a certain variable
    """

    def __init__(self, value_key, initial_value, min_value, max_value):
        """
        Description:
            Initializes this object
        Input:
            string value_key: Key used to access this tracker's variable in constants
            any type initial_value: Value that this tracker's variable is set to when initialized
        Output:
            None
        """
        setattr(constants, value_key, initial_value)
        self.value_label = None
        self.value_key = value_key
        self.min_value = min_value
        self.max_value = max_value

    def get(self):
        """
        Description:
            Returns the value of this tracker's variable
        Input:
            None
        Output:
            any type: Value of this tracker's variable
        """
        return getattr(constants, self.value_key)

    def change(self, value_change):
        """
        Description:
            Changes the value of this tracker's variable by the inputted amount. Only works if this tracker's variable is a type that can be added to, like int, float, or string
        Input:
            various types value_change: Amount that this tracker's variable is changed. Must be the same type as this tracker's variable
        Output:
            None
        """
        self.set(self.get() + value_change)
        if self.value_label:
            self.value_label.update_label(self.get())

    def set(self, new_value):
        """
        Description:
            Sets the value of this tracker's variable to the inputted amount
        Input:
            any type value_change: Value that this tracker's variable is set to
        Output:
            None
        """
        setattr(constants, self.value_key, new_value)
        if self.min_value != None:
            if self.get() < self.min_value:
                setattr(constants, self.value_key, self.min_value)
        if self.max_value != None:
            if self.get() > self.max_value:
                setattr(constants, self.value_key, self.max_value)
        if self.value_label:
            self.value_label.update_label(self.get())


class public_opinion_tracker(value_tracker):
    """
    Value tracker that tracks public opinion
    """

    def change(self, value_change):
        """
        Description:
            Changes the value of this tracker's variable by the inputted amount. Only works if this tracker's variable is a type that can be added to, like int, float, or string
        Input:
            various types value_change: Amount that this tracker's variable is changed. Must be the same type as this tracker's variable
        Output:
            None
        """
        super().change(value_change)
        constants.MoneyLabel.check_for_updates()
        if self.get() <= 0:
            constants.AchievementManager.achieve("Vilified")
        elif self.get() >= 100:
            constants.AchievementManager.achieve("Idolized")


class money_tracker(value_tracker):
    """
    Value tracker that tracks money and causes the game to be lost when money runs out
    """

    def __init__(self, initial_value):
        """
        Description:
            Initializes this object
        Input:
            any type initial_value: Value that the money variable is set to when initialized
        Output:
            None
        """
        self.transaction_history = {}
        self.reset_transaction_history()
        super().__init__(
            value_key="money",
            initial_value=initial_value,
            min_value=None,
            max_value=None,
        )

    def reset_transaction_history(self):
        """
        Resets the stored transactions from the last turn, allowing new transactions to be recorded for the current turn's financial report
        """
        self.transaction_history = {}
        for current_transaction_type in constants.transaction_types:
            self.transaction_history[current_transaction_type] = 0

    def change(self, value_change, change_type="misc."):
        """
        Description:
            Changes the money variable by the inputted amount
        Input:
            int value_change: Amount that the money variable is changed
        Output:
            None
        """
        if change_type == "misc.":
            if value_change > 0:
                change_type = "misc_revenue"
            else:
                change_type = "misc_expenses"
        self.transaction_history[change_type] += value_change
        if not value_change == 0:
            if abs(value_change) < 15:
                constants.SoundManager.play_sound("effects/coins_1")
            else:
                constants.SoundManager.play_sound("effects/coins_2")
        super().change(value_change)

    def set(self, new_value):
        """
        Description:
            Sets the money variable to the inputted amount
        Input:
            int value_change: Value that the money variable is set to
        Output:
            None
        """
        super().set(round(new_value, 2))

    def prepare_financial_report(self):
        """
        Description:
            Creates and formats the text for a financial report based on the last turn's transactions
        Input:
            None
        Output:
            string: Formatted financial report text with /n being a new line
        """
        notification_text = "Financial report: /n /n"
        notification_text += "Revenue: /n"
        total_revenue = 0
        for transaction_type in constants.transaction_types:
            if self.transaction_history[transaction_type] > 0:
                notification_text += f" {constants.transaction_descriptions[transaction_type].capitalize()}: {str(self.transaction_history[transaction_type])} /n"
                total_revenue += self.transaction_history[transaction_type]
        if total_revenue == 0:
            notification_text += "  None /n"
        if (
            total_revenue > 0
            and total_revenue
            > self.transaction_history["subsidies"] + self.transaction_history["loan"]
        ):
            constants.AchievementManager.check_achievements("Return on Investment")

        notification_text += "/nExpenses: /n"
        total_expenses = 0
        for transaction_type in constants.transaction_types:
            if self.transaction_history[transaction_type] < 0:
                notification_text += f" {constants.transaction_descriptions[transaction_type].capitalize()}: {str(self.transaction_history[transaction_type])} /n"
                total_expenses += self.transaction_history[transaction_type]
        if total_expenses == 0:
            notification_text += "  None /n"
        notification_text += " /n"
        notification_text += f"Total revenue: {round(total_revenue, 2)} /n"
        notification_text += f"Total expenses: {round(total_expenses, 2)} /n"
        notification_text += (
            f"Total profit: {round(total_revenue + total_expenses, 2)} /n"
        )
        return notification_text
