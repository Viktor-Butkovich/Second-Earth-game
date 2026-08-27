from __future__ import annotations
from dataclasses import dataclass
from modules.constants import constants, status, flags
from typing import Dict


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
