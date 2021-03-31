"""
File that contains all the exceptions related to the scene.
"""


class SceneError(Exception):
    """
    Class used to represent the scene related exceptions.
    """

    def __init__(self, code: int = 0):
        """
        Constructor of the class

        Args:
            code: Code of the error.
        """
        self.code = code
        self.codes = {
            0: 'Default Error'
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
        return self.codes[self.code]
