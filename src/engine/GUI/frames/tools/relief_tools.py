"""
File with the class ReliefTools. Class in charge of render the Relief tools inside another frame.
"""

import imgui

from src.utils import get_logger
from src.error.polygon_point_number_error import PolygonPointNumberError
from src.error.polygon_not_planar_error import PolygonNotPlanarError

log = get_logger(module="RELIEF_TOOLS")


class ReliefTools:
    """
    Class that render the ReliefTools inside another frame.
    """

    # noinspection PyUnresolvedReferences
    def __init__(self, gui_manager: 'GUIManager'):
        """
        Constructor of the class.
        """
        self.__gui_manager = gui_manager

        self.__combo_options = ["Linear"]
        self.__current_combo_option = 0

        self.__max_height_value = 0
        self.__min_height_value = 0

        self.__max_height_polygon = None
        self.__min_height_polygon = None

    def render(self) -> None:
        """
        Render the relief tools to modify the relief of the model.
        Returns: None
        """

        imgui.text('Relief Tools')

        imgui.text('Current polygon information:')

        imgui.columns(2, None, False)

        imgui.text(f'Max height:')
        imgui.next_column()
        imgui.text(str(self.__max_height_polygon))
        imgui.next_column()
        imgui.text(f'Min height:')
        imgui.next_column()
        imgui.text(str(self.__min_height_polygon))
        imgui.columns(1)

        if imgui.button('Recalculate Information', -1):
            log.debug('Recalculate polygon information')

            try:
                self.__max_height_polygon, self.__min_height_polygon = self.__gui_manager.calculate_max_min_height(
                    self.__gui_manager.get_active_model_id(),
                    self.__gui_manager.get_active_polygon_id())

            except TypeError:
                self.__gui_manager.set_modal_text('Error',
                                                  'The current model is not supported to use to update the '
                                                  'height of the vertices, try using another type of model.')

            except PolygonPointNumberError:
                self.__gui_manager.set_modal_text('Error',
                                                  'The polygon must have at least 3 points to be able to'
                                                  'modify the heights.')

            except PolygonNotPlanarError:
                self.__gui_manager.set_modal_text('Error',
                                                  'The polygon is not planar. Try using a planar polygon.')

        clicked, self.__current_combo_option = imgui.combo(
            "Transformation", self.__current_combo_option, self.__combo_options
        )

        _, self.__min_height_value = imgui.input_float('Min Height', self.__min_height_value)
        _, self.__max_height_value = imgui.input_float('Max Height', self.__max_height_value)

        if imgui.button('Change Height', -1):
            if self.__min_height_value > self.__max_height_value:
                self.__gui_manager.set_modal_text('Error', 'The new minimum value is higher than the maximum value.')
            else:
                if self.__current_combo_option == 0:
                    try:
                        self.__gui_manager.change_points_height(self.__gui_manager.get_active_polygon_id(),
                                                                self.__gui_manager.get_active_model_id(),
                                                                min_height=self.__min_height_value,
                                                                max_height=self.__max_height_value,
                                                                interpolation_type='linear')
                    except TypeError:
                        self.__gui_manager.set_modal_text('Error',
                                                          'The current model is not supported to use to update the '
                                                          'height of the vertices, try using another type of model.')

                    except PolygonPointNumberError:
                        self.__gui_manager.set_modal_text('Error',
                                                          'The polygon must have at least 3 points to be able to'
                                                          'modify the heights.')

                    except PolygonNotPlanarError:
                        self.__gui_manager.set_modal_text('Error',
                                                          'The polygon is not planar. Try using a planar polygon.')
