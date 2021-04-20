"""
File with the definition of the UnitConverter class, class in charge of realizing the conversion between units.
"""


class UnitConverter:
    """
    Class in charge of the conversion between the different units accepted in the program.
    """

    def meter_to_kilometer(self) -> float:
        """
        Get the factor to use to convert meters to kilometers.

        Returns: Conversion factor.
        """
        return 0.001

    def meter_to_degrees(self) -> float:
        """
        Get the approximated factor to convert meter to degrees.

        The conversion factor is the one used in the equator.

        Returns: None
        """
        return 0.0001 / 111

    def kilometer_to_meter(self) -> float:
        """
        Get the factor to use to convert kilometers to meters.

        Returns: Conversion factor.
        """
        return 1000
