"""
File with the class ReliefTools. Class in charge of render the Relief tools inside another frame.
"""

import imgui

from src.utils import get_logger

from src.error.scene_error import SceneError
from src.error.model_transformation_error import ModelTransformationError

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

        self.__polygon_data = {}

    def render(self) -> None:
        """
        Render the relief tools to modify the relief of the model.
        Returns: None
        """
        # get all the data necessary
        active_polygon_id = self.__gui_manager.get_active_polygon_id()
        active_model_id = self.__gui_manager.get_active_model_id()

        if active_polygon_id not in self.__polygon_data:
            self.__polygon_data[active_polygon_id] = {
                'max_height': None,
                'min_height': None
            }

        self.__gui_manager.set_tool_title_font()
        imgui.text('Relief Tools')
        self.__gui_manager.set_regular_font()

        imgui.text('Current polygon information:')
        imgui.columns(2, None, False)
        imgui.text(f'Max height:')
        imgui.next_column()
        imgui.text(str(self.__polygon_data[active_polygon_id]['min_height']))
        imgui.next_column()
        imgui.text(f'Min height:')
        imgui.next_column()
        imgui.text(str(self.__polygon_data[active_polygon_id]['max_height']))
        imgui.columns(1)

        if imgui.button('Recalculate Information', -1):
            log.debug('Recalculate polygon information')

            if active_model_id is None:
                self.__gui_manager.set_modal_text('Error', 'You must load a model to try to calculate the '
                                                           'height of the '
                                                           'points inside it.')
            else:
                maximum, minimum = self.__gui_manager.calculate_max_min_height(active_model_id,
                                                                               active_polygon_id)
                self.__polygon_data[active_polygon_id]['max_height'] = maximum
                self.__polygon_data[active_polygon_id]['min_height'] = minimum


        clicked, self.__current_combo_option = imgui.combo(
            "Transformation", self.__current_combo_option, self.__combo_options
        )

        _, self.__min_height_value = imgui.input_float('Min Height', self.__min_height_value)
        _, self.__max_height_value = imgui.input_float('Max Height', self.__max_height_value)

        if imgui.button('Change Height', -1):
            if self.__min_height_value >= self.__max_height_value:
                self.__gui_manager.set_modal_text('Error', 'The new minimum value is higher or equal to'
                                                           ' the maximum value.')
            elif active_model_id is None:
                self.__gui_manager.set_modal_text('Error', 'You must load a model to try to calculate the '
                                                           'height of the '
                                                           'points inside it.')
            else:
                if self.__current_combo_option == 0:
                    try:
                        self.__gui_manager.change_points_height(active_polygon_id,
                                                                active_model_id,
                                                                min_height=self.__min_height_value,
                                                                max_height=self.__max_height_value,
                                                                transformation_type='linear')
                    except ModelTransformationError as e:
                        if e.code == 4:
                            self.__gui_manager.set_modal_text('Error',
                                                              'The current model is not supported to use to update the '
                                                              'height of the vertices, try using another type of '
                                                              'model.')
                        elif e.code == 2:
                            self.__gui_manager.set_modal_text('Error',
                                                              'The polygon must have at least 3 points to be able to '
                                                              'modify the heights.')
                        elif e.code == 3:
                            self.__gui_manager.set_modal_text('Error',
                                                              'The polygon is not planar. Try using a planar polygon.')
