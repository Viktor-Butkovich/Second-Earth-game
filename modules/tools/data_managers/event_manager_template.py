from ...constructs import events
import modules.constants.constants as constants


class event_manager_template:
    """
    Object that tracks a list of events and calls the relevant functions once an inputted amount of time has passed
    """

    def __init__(self):
        """
        Description:
            Initializes this object
        Input:
            None
        Output:
            None
        """
        self.event_list = []
        self.event_time_list = []
        self.previous_time = 0.0

    def add_event(self, function, inputs, activation_time):
        """
        Description:
            Creates a new event with the inputted function and time that will call the inputted function with inputs after the inputted time has elapsed
        Input:
            function function: Function that will be called after the inputted time has elapsed
            list inputs: List of inputs the function will be called with, in order
            double activation_time: Amount of time that will pass before the function is called
        Output:
            None
        """
        self.event_list.append(events.event(function, inputs, activation_time, self))

    def add_repeating_event(self, function, inputs, activation_time, num_repeats=-1):
        """
        Description:
            Creates a new event with the inputted function and time that will call the inputted function with inputs after the inputted time has elapsed
        Input:
            function function: Function that will be called each time the inputted time elapses
            list inputs: List of inputs the function will be called with, in order
            double activation_time: Amount of time that will pass between each function call
        Output:
            None
        """
        self.event_list.append(
            events.repeating_event(function, inputs, activation_time, self, num_repeats)
        )

    def update(self, new_time):
        """
        Description:
            Updates events with the current time, activating any that run out of time
        Input:
            double new_time: New time to update this object with
        Output:
            None
        """
        time_difference = new_time - self.previous_time
        activated_events = []
        for current_event in self.event_list:
            current_event.activation_time -= (
                time_difference  # updates event times with new time
            )
            if (
                current_event.activation_time <= 0
            ):  # if any event runs out of time, activate it
                activated_events.append(current_event)
        if (
            len(activated_events) > 0
        ):  # when an event activates, call its stored function
            for current_event in activated_events:
                current_event.activate()
                current_event.remove()
        self.previous_time = new_time

    def clear(self):
        """
        Description:
            Removes this object's events, removing them from storage and stopping them before activation
        Input:
            None
        Output:
            None
        """
        existing_events = []
        for current_event in self.event_list:
            existing_events.append(current_event)
        for current_event in existing_events:
            current_event.remove()

    def go(self):
        """
        Description:
            Calls the money tracker's change function with an input of -20 every second, repeating indefinitely because no num_repeats is provided - solely for event testing
        Input:
            None
        Output:
            None
        """
        self.add_repeating_event(
            constants.money_tracker.change, [-20], activation_time=1
        )
