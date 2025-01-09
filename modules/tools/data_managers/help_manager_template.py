from typing import List, Dict, Any
from modules.util import utility
from modules.constructs import world_handlers
from modules.constants import constants, status, flags


class help_manager_template:
    """
    Object that controls generating game advice
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
        self.subjects: Dict[str, List[str]] = {
            constants.HELP_GLOBAL_PARAMETERS: [
                constants.PRESSURE_LABEL,
                constants.AVERAGE_WATER_LABEL,
                constants.GRAVITY_LABEL,
                constants.RADIATION_LABEL,
                constants.MAGNETIC_FIELD_LABEL,
                constants.TOTAL_HEAT_LABEL,
                constants.INSOLATION_LABEL,
                constants.GHG_EFFECT_LABEL,
                constants.WATER_VAPOR_EFFECT_LABEL,
                constants.ALBEDO_EFFECT_LABEL,
                constants.AVERAGE_TEMPERATURE_LABEL,
            ]
            + constants.ATMOSPHERE_COMPONENT_LABELS,
        }
        self.label_types: List[str] = [
            item for sublist in self.subjects.values() for item in sublist
        ]

    def generate_message(self, subject: str, context: Dict[str, Any] = None) -> str:
        """
        Description:
            Generates and returns a notification message for the inputted subject
        Input:
            string subject: Subject to generate a message for, like constants.PRESSURE
            dictionary context: Optional context for message generation, like {"world_handler": ...}
        Output:
            string: Returns a notification message for the inputted subject
        """
        message = []
        if subject in self.subjects[constants.HELP_GLOBAL_PARAMETERS]:
            if subject == constants.MAGNETIC_FIELD_LABEL:
                subject = constants.RADIATION_LABEL  # Matching descriptions
            world_handler: world_handlers.world_handler = context[
                constants.HELP_WORLD_HANDLER_CONTEXT
            ]
            planet_name_possessive = utility.generate_possessive(world_handler.name)
            parameter = subject.removesuffix("_label")
            (
                deadly_lower_bound,
                deadly_upper_bound,
            ) = constants.DEADLY_PARAMETER_BOUNDS.get(parameter, (None, None))
            (
                perfect_lower_bound,
                perfect_upper_bound,
            ) = constants.PERFECT_PARAMETER_BOUNDS.get(parameter, (None, None))

            attrition_message = f"Humans in non-ideal conditions receive penalties and have a higher risk of attrition. "

            if subject == constants.PRESSURE_LABEL:
                value = round(world_handler.get_pressure_ratio(), 2)
                parameter_habitability = world_handler.calculate_parameter_habitability(
                    parameter
                )

                current_line = ""
                current_line += f"Atmospheric pressure is the total amount of gas in {planet_name_possessive} atmosphere, in atmospheres (atm). "
                current_line += (
                    f"1 atm represents 6 units (u) of gas per tile on a planet."
                )
                message.append(current_line)

                current_line = ""
                if parameter_habitability == constants.HABITABILITY_DEADLY:
                    if value <= deadly_lower_bound:
                        current_line += f"{planet_name_possessive} current pressure of {value} atm is too low for humans to survive. "
                    else:
                        current_line += f"{planet_name_possessive} current pressure of {value} atm is too high for humans to survive. "
                    current_line += f"Humans can survive pressure levels of {deadly_lower_bound}-{deadly_upper_bound} atm. "
                elif parameter_habitability != constants.HABITABILITY_PERFECT:
                    if value <= perfect_lower_bound:
                        current_line += f"{planet_name_possessive} current pressure of {value} atm is lower than ideal for humans. "
                    else:
                        current_line += f"{planet_name_possessive} current pressure of {value} atm is higher than ideal for humans. "
                    current_line += f"The ideal pressure for humans is {perfect_lower_bound}-{perfect_upper_bound} atm. "
                    current_line += attrition_message
                else:
                    current_line += f"{planet_name_possessive} current pressure of {value} atm is ideal for humans and does not need to be changed. "
                message.append(current_line)

                current_line = ""
                if parameter_habitability != constants.HABITABILITY_PERFECT:
                    if value <= perfect_lower_bound:
                        current_line += f"Pressure can be increased by adding more gas to the atmosphere. "
                        current_line += f"Inert gases have few side effects and are a simple way to increase pressure"
                        if (
                            world_handler.get_composition(constants.OXYGEN)
                            < constants.PERFECT_PARAMETER_BOUNDS[constants.OXYGEN][0]
                        ):
                            current_line += (
                                f", while oxygen can be added to improve air quality. "
                            )
                        else:
                            current_line += f". "
                        if (
                            world_handler.average_temperature
                            < status.earth_grid.world_handler.average_temperature
                        ):
                            current_line += f"Alternatively, GHG can be added to raise temperature at the cost of air quality. "
                        elif (
                            world_handler.average_temperature
                            > status.earth_grid.world_handler.average_temperature
                        ):
                            current_line += f"Alternatively, toxic gases can be added to increase albedo, lowering temperature at the cost of air quality. "
                        current_line += f"Regardless of composition, increasing pressure slightly strengthens the GHG effect and raises temperature."
                    else:
                        current_line += f"Pressure can be decreased by removing gas from the atmosphere. "
                        first_advice = True
                        if (
                            world_handler.get_composition(constants.TOXIC_GASES)
                            > constants.PERFECT_PARAMETER_BOUNDS[constants.TOXIC_GASES][
                                1
                            ]
                        ):
                            current_line += f"Toxic gases can be removed while improving air quality, although this can decrease albedo and raise temperature. "
                            first_advice = False
                        if (
                            world_handler.get_composition(constants.GHG)
                            > constants.PERFECT_PARAMETER_BOUNDS[constants.GHG][1]
                        ):
                            if first_advice:
                                current_line += f"Excess GHG can be removed to improve both pressure and air quality while weakening the GHG effect and lowering temperature. "
                            else:
                                current_line += f"Similarly, excess GHG can be removed while weakening the GHG effect and lowering temperature. "
                        current_line += f"Regardless of composition, decreasing pressure slightly weakens the GHG effect and lowers temperature. "
                    message.append(current_line)

            elif subject == constants.AVERAGE_WATER_LABEL:
                value = (
                    world_handler.average_water
                    / status.earth_grid.world_handler.average_water
                )
                value_percent = round(value * 100, 2)
                current_line = ""

                if (
                    world_handler.average_water
                    < status.earth_grid.world_handler.average_water
                ):
                    current_line += f"{planet_name_possessive} current water levels are {value_percent}% of Earth, which are less than ideal for an Earth-like environment. "
                    message.append(current_line)

                    current_line = ""
                    if world_handler.average_temperature <= world_handler.get_tuning(
                        "water_freezing_point"
                    ):
                        current_line += "At freezing temperatures, adding water increases ice, raising albedo and lowering temperature. "
                    else:
                        current_line += "At non-freezing temperatures, adding water both increases the water vapor GHG effect and albedo from clouds, having mixed effects on temperature. "
                        message.append(current_line)
                        current_line = "To confirm the effects of adding water, add small amounts and observe the resulting temperature changes. "
                    message.append(current_line)

                elif (
                    world_handler.average_water
                    > status.earth_grid.world_handler.average_water
                ):
                    current_line += f"{planet_name_possessive} current water levels are {value_percent}% of Earth, which are not Earth-like but still habitable. "
                    message.append(current_line)

                    current_line = ""
                    if world_handler.average_temperature <= world_handler.get_tuning(
                        "water_freezing_point"
                    ):
                        current_line += f"At freezing temperatures, removing water decreases ice, lowering albedo and raising temperature. "
                    else:
                        current_line += f"At non-freezing temperatures, removing water both decreases the water vapor GHG effect and albedo from clouds, having mixed effects on temperature. "
                        message.append(current_line)
                        current_line = f"To confirm the effects of removing water, remove small amounts and observe the resulting temperature changes. "
                    message.append(current_line)

                else:
                    current_line += f"{planet_name_possessive} current water levels of {value_percent}% Earth are ideal for an Earth-like environment and do not need to be changed. "
                    message.append(current_line)

                    if world_handler.average_temperature <= world_handler.get_tuning(
                        "water_freezing_point"
                    ):
                        current_line = ""
                        current_line += f"At freezing temperatures, water can be removed to decrease ice, lowering albedo and raising temperature. "
                        message.append(current_line)

            elif subject == constants.GRAVITY_LABEL:
                value = round(world_handler.get_parameter(constants.GRAVITY), 2)
                parameter_habitability = world_handler.calculate_parameter_habitability(
                    parameter
                )

                current_line = ""
                if world_handler == status.earth_grid.world_handler:
                    current_line += f"The gravity on {planet_name_possessive} surface is {value} g. "
                else:
                    current_line += f"The gravity on {planet_name_possessive} surface is {value} g, with 1.0 g being Earth's gravity. "
                current_line += f"The ideal gravity for humans is {perfect_lower_bound}-{perfect_upper_bound} g. "
                message.append(current_line)

                if parameter_habitability != constants.HABITABILITY_PERFECT:
                    if value <= perfect_lower_bound:
                        current_line = f"{planet_name_possessive} gravity is weaker than ideal for humans. "
                        current_line += f"While gravity is difficult to modify, weak gravity eases spacecraft launches, construction, and movement but introduces long-term health problems for colonists. "
                        current_line += f"However, low-gravity planets tend to be smaller and less likely to retain strong atmospheres and magnetic fields. "
                    else:
                        current_line = f"{planet_name_possessive} gravity is stronger than ideal for humans. "
                        current_line += f"While gravity is difficult to modify, strong gravity hinders spacecraft launches, construction, and movement, and introduces long-term health problems for colonists. "
                        current_line += f"However, high-gravity planetes tend to be larger and more likely to retain strong atmospheres and magnetic fields. "
                    message.append(current_line)
                else:
                    current_line = f"{planet_name_possessive} gravity is ideal for humans and has no notable effects. "
                    message.append(current_line)

            elif subject in [constants.RADIATION_LABEL, constants.MAGNETIC_FIELD_LABEL]:
                value = max(
                    0,
                    world_handler.get_parameter(constants.RADIATION)
                    - world_handler.get_parameter(constants.MAGNETIC_FIELD),
                )
                message.append(
                    "Any planet is constantly bombarded by radiation from its star and the rest of the universe, but this can be mitigated by a planetary magnetic field. "
                )
                current_line = f"{world_handler.get_parameter(constants.RADIATION)} radiation - {world_handler.get_parameter(constants.MAGNETIC_FIELD)} magnetic field = {value} effective radiation. "
                message.append(current_line)

                if value <= perfect_upper_bound:
                    current_line = f"{world_handler.name} receives an effective radiation of 0, which is ideal for humans and does not need to be modified. "
                elif value < deadly_lower_bound:
                    current_line = f"{world_handler.name} receives an effective radiation of {value}, which is more than ideal for humans. "
                    current_line += attrition_message
                else:
                    current_line = f"{world_handler.name} receives an effective radiation of {value}, which is deadly for humans. "
                    current_line += f"Humans can survive effective radiation levels of 0-{deadly_lower_bound - 1}. "
                message.append(current_line)

                if value > perfect_upper_bound:
                    current_line = ""
                    current_line += f"Any unmitigated radiation can cause a slow loss of atmosphere and non-frozen water to space, with faster rates for stronger radiation. "
                    message.append(current_line)

                if value > 0:
                    current_line = ""
                    current_line += f"Effective radiation can be decreased by strengthening the magnetic field. "
                    current_line += f"This requires either stimulating liquid movement within the planet or running an artificial current around the planet. "
                    message.append(current_line)

            elif subject in [
                constants.TOTAL_HEAT_LABEL,
                constants.AVERAGE_TEMPERATURE_LABEL,
            ]:
                if subject == constants.TOTAL_HEAT_LABEL:
                    value = world_handler.get_total_heat()
                    earth_value = status.earth_grid.world_handler.get_total_heat()
                    keyword = "total heat received"
                    message.append(
                        "Total heat is the energy received by the planet, based on insolation multiplied by the GHG, water vapor, and albedo effects. "
                    )
                elif subject == constants.AVERAGE_TEMPERATURE_LABEL:
                    value = utility.fahrenheit(world_handler.average_temperature)
                    earth_value = utility.fahrenheit(
                        status.earth_grid.world_handler.average_temperature
                    )
                    keyword = "average temperature"
                    message.append(
                        "Average temperature is absolute zero combined with the heat received by the planet. "
                    )

                current_line = ""
                if subject == constants.AVERAGE_TEMPERATURE_LABEL:
                    current_line += f"{constants.ABSOLUTE_ZERO} °F absolute zero + {world_handler.get_total_heat()} °F total heat "
                    if value >= earth_value:
                        current_line += f"= {round(value, 2)} °F average temperature (+{round(value - earth_value, 2)} °F Earth)"
                    else:
                        current_line += f"= {round(value, 2)} °F average temperature ({round(value - earth_value, 2)} °F Earth)"
                else:
                    current_line += (
                        f"{round(world_handler.get_sun_effect(), 2)} °F insolation "
                    )
                    if world_handler.ghg_multiplier < 1.0:
                        current_line += f"- {abs(round((world_handler.ghg_multiplier - 1.0) * 100, 2))}% GHG "
                    else:
                        current_line += f"+ {round((world_handler.ghg_multiplier - 1.0) * 100, 2)}% GHG "
                    current_line += f"+ {round((world_handler.water_vapor_multiplier - 1.0) * 100, 2)}% water vapor "
                    current_line += f"- {abs(round((world_handler.albedo_multiplier - 1.0) * 100, 2))}% albedo "

                    current_line += f"= {round(value, 2)} °F total heat ({round((value / earth_value) * 100)}% Earth)"
                message.append(current_line)

                current_line = ""
                if value > earth_value + 5:
                    current_line += f"{planet_name_possessive} {keyword} is hotter than ideal for an Earth-like environment. "
                    current_line += f"To cool the planet, weaken the GHG or water vapor effects, or strengthen the albedo effect - check each effect's respective advice for specific information. "
                    message.append(current_line)
                elif value < earth_value - 5:
                    current_line += f"{planet_name_possessive} {keyword} is colder than ideal for an Earth-like environment. "
                    current_line += f"To warm the planet, strengthen the GHG or water vapor effects, or weaken the albedo effect - check each effect's respective advice for specific information. "
                    message.append(current_line)
                else:
                    current_line += f"{planet_name_possessive} {keyword} is ideal for an Earth-like environment and does not need to be changed. "
                    message.append(current_line)

            elif subject == constants.INSOLATION_LABEL:
                value = world_handler.get_insolation()
                earth_value = status.earth_grid.world_handler.get_insolation()
                message.append(
                    f"Insolation is the baseline amount of sunlight received by {world_handler.name}, based on star distance. "
                )
                message.append(
                    f"1 / ({world_handler.star_distance} AU from star) ^ 2 = {round(value, 2)}x Earth's insolation"
                )
                message.append(
                    f"Heat caused by insolation: Stefan-Boltzmann law({round(value, 2)} insolation) = {round(world_handler.get_sun_effect(), 2)} °F ({round((world_handler.get_sun_effect() / status.earth_grid.world_handler.get_sun_effect()) * 100)}% Earth)"
                )
                if value > earth_value:
                    current_line = ""
                    current_line += f"{planet_name_possessive} insolation is stronger than Earth's, raising the base temperature. "
                    current_line += f"This can be offset with weaker GHG and water vapor effects and a stronger albedo effect - check each effect's respective advice for specific information. "
                    message.append(current_line)
                    message.append(
                        "Additionally, portions of sunlight can be directly blocked by constructing solar shaders."
                    )
                elif value < earth_value:
                    current_line = ""
                    current_line += f"{planet_name_possessive} insolation is weaker than Earth's, lowering the base temperature. "
                    current_line += f"This can be offset with stronger GHG and water vapor effects and a weaker albedo effect - check each effect's respective advice for specific information. "
                    message.append(current_line)
                    message.append(
                        "Additionally, portions of sunlight can be directly amplified by constructing solar mirrors. "
                    )
                else:
                    message.append(
                        f"{planet_name_possessive} insolation is equal to Earth's and does not need to be changed. "
                    )
            elif subject in [constants.GHG_EFFECT_LABEL, constants.GHG_LABEL]:
                value = round((world_handler.ghg_multiplier - 1) * 100, 2)
                value_description = str(value)
                if value >= 0:
                    value_description = f"+{value}"
                ghg_atm = world_handler.get_pressure_ratio(constants.GHG)
                if ghg_atm < 0.01:
                    ghg_atm = "<0.01"
                else:
                    ghg_atm = round(ghg_atm, 2)
                total_atm = world_handler.get_pressure_ratio()
                if total_atm < 0.01:
                    total_atm = "<0.01"
                else:
                    total_atm = round(total_atm, 2)
                message.append(
                    f"Greenhouse gases (GHG) such as carbon dioxide and methane trap heat in the atmosphere, raising the temperature through the GHG effect."
                )
                message.append(
                    f"{planet_name_possessive} GHG effect of {value_description}% is determined by the {ghg_atm} atm of GHG in the atmosphere and the {total_atm} atm total pressure. "
                )
                message.append(
                    f"This results in a {value_description}% modifier to the total heat received by the planet."
                )
                low_pressure_message = f"The GHG effect is currently negative because of the very low pressure. Once the pressure is increased, the GHG effect will increase, raising temperature."
                if (
                    world_handler.get_total_heat()
                    > status.earth_grid.world_handler.get_total_heat() + 5
                ):
                    if value < 0:
                        message.append(low_pressure_message)
                    elif (
                        world_handler.calculate_parameter_habitability(constants.GHG)
                        != constants.HABITABILITY_PERFECT
                    ):
                        message.append(
                            f"To lower the temperature, the GHG effect can be weakened by removing GHG from the atmosphere or decreasing overall pressure, which would also improve air quality. "
                        )
                    elif world_handler.get_parameter(constants.GHG) == 0:
                        message.append(
                            f"While the temperature is higher than ideal, there is no more GHG to remove to lower the GHG effect. "
                        )
                    else:
                        message.append(
                            f"To lower the temperature, the GHG effect can be weakened by removing GHG from the atmosphere or decreasing overall pressure. "
                        )
                elif (
                    world_handler.get_total_heat()
                    < status.earth_grid.world_handler.get_total_heat() - 5
                ):
                    if value < 0:
                        message.append(low_pressure_message)
                    elif (
                        world_handler.calculate_parameter_habitability(constants.GHG)
                        != constants.HABITABILITY_PERFECT
                    ):
                        message.append(
                            f"The temperature could be raised by strengthening the GHG effect with more GHG or higher pressure, but this would further worsen air quality. "
                        )
                    else:
                        message.append(
                            f"The temperature could be raised by strengthening the GHG effect with more GHG or higher pressure. "
                        )
                elif value < 0:
                    message.append(low_pressure_message)
                elif (
                    world_handler.calculate_parameter_habitability(constants.GHG)
                    != constants.HABITABILITY_PERFECT
                ):
                    message.append(
                        f"While {world_handler.name} has an ideal temperature, the air quality can only be improved by weakening the GHG effect, which would decrease temperature. "
                    )
                else:
                    message.append(
                        f"{world_handler.name} has an ideal temperature and air quality, and the GHG effect does not need to be changed. "
                    )

        # Still missing water vapor effect, albedo effect, toxic gases, oxygen, and inert gases help messages

        return " /n /n".join(message) + " /n /n"

    def generate_tooltip(self, subject: str, context: Dict[str, Any]) -> List[str]:
        """
        Description:
            Generates and returns a tooltip description for the inputted subject
        Input:
            string subject: Subject to generate a tooltip before, like constants.PRESSURE
            dictionary context: Optional context for tooltip generation, like {"world_handler": ...}
        Output:
            string list: Returns a tooltip description for the inputted subject
        """
        tooltip = []
        if subject in self.subjects[constants.HELP_GLOBAL_PARAMETERS]:
            world_handler: world_handlers.world_handler = context.get(
                constants.HELP_WORLD_HANDLER_CONTEXT, None
            )
            if not world_handler:
                return tooltip
            intro = f"Provides advice for managing {utility.generate_possessive(world_handler.name)}"
            if subject == constants.PRESSURE_LABEL:
                tooltip.append(f"{intro} atmospheric pressure")
            elif subject == constants.AVERAGE_WATER_LABEL:
                tooltip.append(f"{intro} water levels")
            elif subject == constants.GRAVITY_LABEL:
                tooltip.append(f"{intro} gravity")
            elif subject == constants.RADIATION_LABEL:
                tooltip.append(f"{intro} radiation")
            elif subject == constants.MAGNETIC_FIELD_LABEL:
                tooltip.append(f"{intro} magnetic field")
            elif subject == constants.TOTAL_HEAT_LABEL:
                tooltip.append(
                    f"{intro} total heat received, which determines the average temperature"
                )
            elif subject == constants.INSOLATION_LABEL:
                tooltip.append(
                    f"{intro} insolation, the baseline amount of sunlight received"
                )
            elif subject == constants.GHG_EFFECT_LABEL:
                tooltip.append(
                    f"{intro} greenhouse gas effect, which multiplies total heat based on GHG and pressure levels"
                )
            elif subject == constants.WATER_VAPOR_EFFECT_LABEL:
                tooltip.append(
                    f"{intro} water vapor effect, which multiplies total heat based on water and temperature levels"
                )
            elif subject == constants.ALBEDO_EFFECT_LABEL:
                tooltip.append(
                    f"{intro} albedo effect, which decreases total heat based on how much sunlight is reflected away"
                )
            elif subject == constants.AVERAGE_TEMPERATURE_LABEL:
                tooltip.append(
                    f"{intro} average temperature levels, which are based on absolute zero added with total heat"
                )
            elif subject in constants.ATMOSPHERE_COMPONENT_LABELS:
                tooltip.append(
                    f"{intro} {subject.removesuffix('_label').replace('_', ' ').replace('gases', 'gas')} levels"
                )
        return tooltip
