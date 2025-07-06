# Contains functionality for timed function call events

from modules.util import utility
from modules.constants import constants, status, flags


class scheduled_job:
    def __init__(self, function, inputs, activation_time):
        """
        Description:
            Initializes this object
        Input:
            function function: Function that will be called after the inputted time has elapsed
            list inputs: List of inputs the function will be called with, in order
            double activation_time: Amount of time that will pass before the function is called
        Output:
            None
        """
        self.function = function
        self.inputs = inputs
        self.activation_time = activation_time

    def activate(self):
        """
        Calls this event's function with its inputs
        """
        self.function(
            *self.inputs
        )  # Unpacking argument operator - turns tuple into separate arguments for the function

    def remove(self):
        """
        Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        """
        if self in constants.JobScheduler.scheduled_jobs:
            constants.JobScheduler.scheduled_jobs = utility.remove_from_list(
                constants.JobScheduler.scheduled_jobs, self
            )


class repeating_scheduled_job(scheduled_job):
    """
    Scheduled job that creates a new version of itself upon activation to repeat a particular number of times
    """

    def __init__(self, function, inputs, activation_time, num_repeats):
        """
        Description:
            Initializes this object
        Input:
            function function: Function that will be called each time the inputted time elapses
            list inputs: List of inputs the function will be called with, in order
            double activation_time: Amount of time that will pass between each function call
            int num_repeats: Number of times to repeat this event, or -1 if it repeats infinitely
        Output:
            None
        """
        super().__init__(function, inputs, activation_time)
        self.original_activation_time = activation_time
        self.num_repeats = num_repeats

    def activate(self):
        """
        Calls this job's function with its inputs and adds a new repeated version with 1 fewer repeats, or -1 if it repeats infinitely
        """
        super().activate()
        if not self.num_repeats == -1:
            self.num_repeats -= 1
        if (
            self.num_repeats > 0 or self.num_repeats == -1
        ):  # if any repeats left or repeats infinitely
            constants.JobScheduler.add_event(
                self.function,
                self.inputs,
                self.original_activation_time,
                self.num_repeats,
            )
