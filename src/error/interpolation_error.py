"""
File with the InterpolationError class, class to use when raising exceptions related to the interpolation process.
"""

from src.error.scene_error import SceneError


class InterpolationError(SceneError):
    """
    Class to use when there is an error in the transformation process of a model.
    """

    def __init__(self, code: int = 0):
        """
        Constructor of the class.
        """
        self.code = code

        self.__codes = {
            0: 'Error description not selected.',
            1: 'Not enough points in the polygon to do the interpolation.',
        }

    def __str__(self) -> str:
        """
        Returns: Message showed in the console.
        """
        return self.get_code_message()

    def get_code_message(self) -> str:
        """
        Get the message stored describing the error.

        Returns: string
        """
        return self.__codes[self.code]
