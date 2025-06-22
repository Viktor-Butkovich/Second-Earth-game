# Contains topic subscription/publication-based event bus management singleton

from typing import List, Dict, Callable
from modules.constants import constants, status, flags


class event_bus:
    """
    Placeholder
    """

    def __init__(self):
        """
        Placeholder
        """
        self.subscriptions: Dict[str, List[Callable]] = {}

    def subscribe(self, topic: str, callback: Callable) -> None:
        """
        Description:
            Subscribes the inputted callback to be invoked whenever the inputted topic is published
        Input:
            str topic: Topic to subscribe to
            Callable callback: Callback function to invoke when the topic is published
        Output:
            None
        """
        if topic not in self.subscriptions:
            self.subscriptions[topic] = []
        if callback not in self.subscriptions[topic]:
            self.subscriptions[topic].append(callback)

    def publish(self, topic: str) -> None:
        """
        Description:
            Publishes the inputted topic, invoking all subscribed callbacks
                Modify this to accomodate *args, **kwargs if information needs to be passed
        Input:
            str topic: Topic to publish
        Output:
            None
        """
        for callback in self.subscriptions.get(topic, []):
            callback()
