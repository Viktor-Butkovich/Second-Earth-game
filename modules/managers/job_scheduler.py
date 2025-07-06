# Contains timed callback job scheduling singleton

from typing import List
from modules.constructs import scheduled_jobs
from modules.constants import constants, status, flags


class job_scheduler:
    """
    Object that tracks a list of events and calls the relevant functions once an inputted amount of time has passed
    """

    def __init__(self):
        """
        Initializes this object
        """
        self.scheduled_jobs: List[scheduled_jobs.scheduled_job] = []
        self.previous_time = 0.0

    def schedule_job(self, function, inputs, activation_time):
        """
        Description:
            Creates a new scheduled job with the inputted function and time that will call the inputted function with inputs after the inputted time has elapsed
        Input:
            function function: Function that will be called after the inputted time has elapsed
            list inputs: List of inputs the function will be called with, in order
            double activation_time: Amount of time that will pass before the function is called
        Output:
            None
        """
        self.scheduled_jobs.append(
            scheduled_jobs.scheduled_job(function, inputs, activation_time)
        )

    def schedule_repeating_job(self, function, inputs, activation_time, num_repeats=-1):
        """
        Description:
            Creates a new scheduled job with the inputted function and time that will call the inputted function with inputs after the inputted time has elapsed
        Input:
            function function: Function that will be called each time the inputted time elapses
            list inputs: List of inputs the function will be called with, in order
            double activation_time: Amount of time that will pass between each function call
        Output:
            None
        """
        self.scheduled_jobs.append(
            scheduled_jobs.repeating_scheduled_job(
                function, inputs, activation_time, self, num_repeats
            )
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
        activated_jobs = []
        for current_job in self.scheduled_jobs:
            current_job.activation_time -= (
                time_difference  # updates job times with new time
            )
            if (
                current_job.activation_time <= 0
            ):  # if any job runs out of time, activate it
                activated_jobs.append(current_job)
        if (
            len(activated_jobs) > 0
        ):  # when a job activates, invoke its callback function and unschedule it
            for current_job in activated_jobs:
                current_job.activate()
                current_job.remove()
        self.previous_time = new_time

    def clear(self):
        """
        Removes this object's events, removing them from storage and stopping them before activation
        """
        existing_jobs = []
        for current_job in self.scheduled_jobs:
            existing_jobs.append(current_job)
        for current_job in existing_jobs:
            current_job.remove()

    def go(self):
        """
        Calls the money tracker's change function with an input of -20 every second, repeating indefinitely because no num_repeats is provided
            Solely for job scheduling testing
        """
        self.schedule_repeating_job(
            constants.MoneyTracker.change, [-20], activation_time=1
        )
