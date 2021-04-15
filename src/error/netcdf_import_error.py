"""
File with the class definition of the NetCDFImportError, class to use when there is errors importing netcdf files.
"""


class NetCDFImportError(Exception):
    """
    Class to use when there are errors in the import of netcdf files.
    """

    def __init__(self, code, data = None):
        """
        Constructor of the class.
        """
        self.code = code
        self.data = data
        self.codes = {
            0: 'Default Error',
            1: 'A key from the file is not in the list of accepted keys on the program.'
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
