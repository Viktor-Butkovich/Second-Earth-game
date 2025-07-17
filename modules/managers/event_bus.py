# Contains topic subscription/publication-based event bus management singleton

from typing import List, Dict, Callable
from modules.constants import constants, status, flags


class event_bus:
    """
    Object that forwards events to subscribed callbacks based on topic subscriptions
    """

    def __init__(self):
        """
        Initializes this object
        """
        self.subscriptions: Dict[str, List[Callable]] = {}

    def subscribe(self, callback: Callable, endpoint: str, *routes: List[str]) -> None:
        """
        Description:
            Subscribes the inputted callback to be invoked whenever the inputted topic is published
        Input:
            Callable callback: Callback function to invoke when the topic is published
            str endpoint: Base topic to subscribe to, like a location's uuid
            string list routes: List of hierarchical sub-topics, like set_parameter, temperature
                Subscribing to 'uuid', 'set_parameter', and 'temperature' assembles the topic 'uuid/set_parameter/temperature'
        Output:
            None
        """
        topic = self.build_topic(endpoint, routes)
        if topic not in self.subscriptions:
            self.subscriptions[topic] = []
        if callback not in self.subscriptions[topic]:
            self.subscriptions[topic].append(callback)

    def unsubscribe(
        self, callback: Callable, endpoint: str, *routes: List[str]
    ) -> None:
        """
        Description:
            Unsubscribes the inputted callback from the specified topic
                Precondition that the callback is already subscribed to the topic
        Input:
            Callable callback: Callback function to remove from the topic
            str endpoint: Base topic to unsubscribe from, like a location's uuid
            string list routes: List of hierarchical sub-topics, like set_parameter, temperature
        Output:
            None
        """
        self.subscriptions[self.build_topic(endpoint, routes)].remove(callback)

    def build_topic(self, endpoint: str, routes: List[str]) -> str:
        """
        Description:
            Builds a topic string from the base endpoint and hierarchical sub-topics
        Input:
            str endpoint: Base topic to build, like a location's uuid
            string list routes: List of hierarchical sub-topics, like set_parameter, temperature
        Output:
            str: The constructed topic string, like 'uuid/set_parameter/temperature'
        """
        return endpoint + "".join(f"/{route}" for route in routes)

    def publish(self, endpoint: str, *routes: List[str]) -> None:
        """
        Description:
            Publishes the inputted topic, invoking all subscribed callbacks
                Modify this to accomodate *args, **kwargs if information needs to be passed
                Calling with (uuid, set_parameter, temperature) invokes all callbacks to 'uuid', 'uuid/set_parameter', and 'uuid/set_parameter/temperature'
        Input:
            str endpoint: Base topic to publish, like a location's uuid
            string list routes: List of hierarchical sub-topics, like set_parameter, temperature
        Output:
            None
        """
        topics = [endpoint]
        if routes:
            for route in routes:
                topics.append(f"{topics[-1]}/{route}")
        for topic in topics:
            for callback in self.subscriptions.get(topic, []):
                callback()

    def clear_endpoint(self, endpoint: str) -> None:
        """
        Description:
            Clears all subscriptions for the inputted endpoint
        Input:
            str endpoint: Base topic to clear, like a location's uuid
        Output:
            None
        """
        for topic in list(self.subscriptions.keys()).copy():
            if topic.startswith(f"{endpoint}/") or topic == endpoint:
                del self.subscriptions[topic]
