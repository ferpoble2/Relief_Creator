"""
Main Frame class for the others elements to use.
"""


class Frame:
    """
    Class to manager the frame behaviour. New frames must be children of this class.
    """

    # noinspection PyUnresolvedReferences
    def __init__(self, gui_manager: 'GUIManager'):
        """
        Constructor of the class.
        """
        self._position = [100, 100]
        self._GUI_manager = gui_manager

    def add_new_polygon(self, polygon_id) -> None:
        """
        Function to call to add a new polygon into the frame.

        Must be defined in child classes.

        Args:
            polygon_id: ID of the polygon.

        Returns: None
        """
        pass

    def change_position(self, new_position: list) -> None:
        """
        Change the position of the frame in the screen. Only works properly when fixed_position is set to True.
        Args:
            new_position: New position where to put the frame. ([x_pos, y_pos])
        Returns: None
        """
        self._position = new_position

    def get_position(self) -> list:
        """
        Get the position of the frame.
        Returns: list with the position of the frame.
        """
        return self._position

    def render(self) -> None:
        """
        Draw the frames on the screen.
        Returns: None
        """

        raise NotImplementedError("Render method not implemented.")
