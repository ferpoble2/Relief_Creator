"""
File with utils functions for the engine.
"""

def interpolate(value: float, value_min: float, value_max: float, target_min: float = -1,
                target_max: float = 1):
    """

    Args:
        value: Value to interpolate.
        value_min: Minimum value of the values.
        value_max: Maximum value of the values.
        target_min: Minimum value of the interpolation interval.
        target_max: Maximum value of the interpolation interval.

    Returns: Interpolated value.

    """
    return (float(value) - value_min) * (float(target_max) - target_min) / (float(value_max) - value_min) + target_min
