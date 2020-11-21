"""
File with all the windows that the program must use to render the gui.
"""
import imgui


def test_window() -> None:
    """
    Define the test window to use in the GUI.
    Returns: None
    """
    imgui.show_test_window()


def sample_text() -> None:
    imgui.begin('test_text')
    imgui.text("This is a sample text to show iin the guy to test screens.")
    imgui.bullet_text("This is a bullet text, hope it helps.")

    if imgui.button("Open Modal popup"):
        imgui.open_popup("select-popup")

    imgui.same_line()

    if imgui.begin_popup_modal("select-popup")[0]:
        imgui.text("Select an option:")
        imgui.separator()
        imgui.selectable("One")
        imgui.selectable("Two")
        imgui.selectable("Three")
        imgui.end_popup()

    imgui.end()
