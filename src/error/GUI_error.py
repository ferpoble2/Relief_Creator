"""
File containing the class GUIError
"""
from src.error.base_error import BaseError


class GUIError(BaseError):
    """
    Error to use for GUI related errors.
    """

    def __init__(self, code=0):
        """
        Constructor of the class.
        """
        super(GUIError, self).__init__(code=code)

        self.codes = {
            0: 'Default Error.',
            1: 'Filter ID not found on the table of filters.'
        }
