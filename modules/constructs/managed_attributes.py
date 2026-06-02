# Implements managed_attributes, which are a centralized place to organize modifiers, multipliers, and their sources for a
#   complex attribute, such as warehouse capacity.

from typing import List, Dict, Tuple, Any


class managed_attribute:
    def __init__(self, base_value: int = 0) -> None:
        """
        Initializes a managed attribute.

        Usage: (example for warehouse capacity)
            A location might initialize a managed attribute for its warehouse capacity.
            When constructed or loaded in, a spaceport might set the modifier of the location's warehouse capacity attribute:
                (spaceport_reference, 9)
            If the spaceport is damaged, it can set its modifier back to 0
            If a spaceport is damaged and loads into a saved game, it will:
                1. Set the modifier to 9 when initialized
                2. Set the modifier to 0 when the damaged status is loaded in
            The location should also track the capacity of warehouses that have been manually built/upgraded as a class
                attribute. When this attribute is modified or loaded, it can be set to the new value.
            Maintaining the sources of the modifiers allows custom descriptions to break down the attribute modifiers.
            Any warehouse capacity or inventory display interface elements could be configured to update when the managed
                attribute publishes an update.
            Linking warehouse level (another managed attribute) as a dependency of warehouse capacity means that warehouse level
                can apply a modifier to warehouse capacity that is a function of level, such as 9 * level, and capacity is
                automatically updated with level.
        """
        self.modifiers: Dict[Any, int] = {}
        self.value: int = None
        self.base_value: int = base_value
        self.downstream: List[Tuple[managed_attribute, callable]] = []
        self.update_value()
        # self.multipliers: List[Tuple[Any, float]] = {}
        #   Expand schema as needed

    def update_value(self) -> None:
        self.value = self.base_value + sum(self.modifiers.values())
        for dependent_attribute, formula in self.downstream:
            dependent_attribute.set_modifier(self, formula(self.value))
        # for multiplier in self.multipliers.values():
        #     value *= multiplier[1]

    def set_modifier(self, source: Any, value: int) -> None:
        """
        Overwrites the modifier from a particular source to a new value, or creates a new modifier if that source is new
        """
        self.modifiers[source] = value
        self.update_value()

    def remove_modifier(self, source: Any) -> None:
        """
        Removes the modifier from a particular source, if it exists
        """
        if source in self.modifiers:
            del self.modifiers[source]
            self.update_value()

    def set_base_value(self, new_base_value: int) -> None:
        """
        Sets a new base value for this attribute
        """
        self.base_value = new_base_value
        self.update_value()

    def get_modifier_of_source(self, source: Any) -> int:
        """
        Returns the modifier from a particular source, or 0 if that source has no modifier
        """
        return self.modifiers.get(source, 0)

    def add_downstream_dependency(
        self, dependent_attribute: "managed_attribute", formula: callable
    ) -> None:
        self.downstream.append((dependent_attribute, formula))
        self.update_value()
