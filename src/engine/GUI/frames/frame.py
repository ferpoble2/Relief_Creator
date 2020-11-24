"""
Main Frame class for the others elements to use.
"""


class Frame:
    """
    Class to manager the frame behaviour. New frames must be children of this class.
    """

    def __init__(self):
        """
        Constructor of the class.
        """
        self._position = [100, 100]
        self._fixed_position = True

    def change_position(self, new_position: list) -> None:
        """
        Change the position of the frame in the screen. Only works properly when fixed_position is set to True.
        Args:
            new_position: New position where to put the frame. ([x_pos, y_pos])
        Returns: None
        """
        self._position = new_position

    def set_fixed_position(self, value: bool) -> None:
        """
        Change the state of the fixed position.
        Args:
            value:  Value True or False

        Returns: None

        """
        self._fixed_position = value

    def render(self) -> None:
        """
        Draw the frames on the screen.
        Returns: None
        """

        raise NotImplementedError("Render method not implemented.")
