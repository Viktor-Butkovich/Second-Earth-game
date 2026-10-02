from __future__ import annotations
from dataclasses import dataclass
from modules.constants import constants, status, flags
from typing import Callable, Dict, List, Tuple, Any


@dataclass
class material_cost:
    base_metals: float = 0.0  # Default value
    building_materials: float = 0.0
    advanced_metals: float = 0.0
    fuels: float = 0.0
    chemicals: float = 0.0
    biomaterials: float = 0.0
    nuclear_materials: float = 0.0
    decimal_places: int = 2

    def enumerate(self) -> Dict[str, float]:
        return self.omit_zero_keys(
            self.sort(
                {
                    constants.MATERIAL_BASE_METALS: self.base_metals,
                    constants.MATERIAL_BUILDING_MATERIALS: self.building_materials,
                    constants.MATERIAL_ADVANCED_METALS: self.advanced_metals,
                    constants.MATERIAL_FUELS: self.fuels,
                    constants.MATERIAL_CHEMICALS: self.chemicals,
                    constants.MATERIAL_BIOMATERIALS: self.biomaterials,
                    constants.MATERIAL_NUCLEAR_MATERIALS: self.nuclear_materials,
                }
            )
        )

    def multiply(self, multiplier: int) -> material_cost:
        return material_cost(
            base_metals=round(self.base_metals * multiplier, self.decimal_places),
            building_materials=round(
                self.building_materials * multiplier, self.decimal_places
            ),
            advanced_metals=round(
                self.advanced_metals * multiplier, self.decimal_places
            ),
            fuels=round(self.fuels * multiplier, self.decimal_places),
            chemicals=round(self.chemicals * multiplier, self.decimal_places),
            biomaterials=round(self.biomaterials * multiplier, self.decimal_places),
            nuclear_materials=round(
                self.nuclear_materials * multiplier, self.decimal_places
            ),
            decimal_places=self.decimal_places,
        )

    def sort(self, enum: Dict[str, float]) -> Dict[str, float]:
        """
        Sorts material costs in descending order of magnitude, with tiebreakers based on original order
        """
        return dict(
            sorted(
                enum.items(),
                key=lambda item: (
                    -item[1],
                    list(enum.keys()).index(item[0]),
                ),
            )
        )

    def omit_zero_keys(self, enum: Dict[str, float]) -> Dict[str, float]:
        """
        Returns a dictionary of material costs with zero-value keys omitted
        """
        return {k: v for k, v in enum.items() if v > 0}


@dataclass
class anonymous_button_definition:
    on_click: List[Tuple[Callable, List[Any]]] = None  # Actions taken upon button click
    can_show: List[Tuple[Callable, List[Any]]] = (
        None  # Series of boolean checks, all of which must be True to show
    )
    # A series of tuples that each contain a callback function and its arguments, to be invoked in order
    tooltip: List[str] = None
    message: str = ""

    def anonymous_on_click(self) -> None:
        """
        Executes the on_click actions
        """
        if self.on_click:
            for func, args in self.on_click:
                func(*args)

    def anonymous_can_show(self) -> bool:
        """
        Executes the can_show checks
        """
        return (
            all(func(*args) for func, args in self.can_show) if self.can_show else True
        )

    @property
    def anonymous_tooltip(self) -> List[str]:
        """
        Provides the tooltip for this object
        """
        return self.tooltip if self.tooltip else []
