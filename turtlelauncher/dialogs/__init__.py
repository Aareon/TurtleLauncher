from pathlib import Path
from turtlelauncher.dialogs.generic_confirmation import GenericConfirmationDialog
from turtlelauncher.dialogs.error import ErrorDialog


def show_success_dialog(title, message, parent=None):
    custom_styles = {
        "#content-widget": {
            "border": "2px solid #45a049"
        }
    }
    GenericConfirmationDialog(
        parent,
        title=title, message=message, confirm_text="OK", cancel_text="",
        icon_path=Path(__file__).parent.parent.parent / "assets" / "images" / "turtle_wow_icon.png",
        custom_styles=custom_styles
    ).exec()

def show_error_dialog(title, message):
    error_dialog = ErrorDialog(title, message)
    error_dialog.exec()
    
def show_warning_dialog(title, message, parent=None):
    custom_styles = {
        "#content-widget": {
            "border": "2px solid #FF8C00"
        }
    }
    GenericConfirmationDialog(
        parent,
        title=title, message=message, confirm_text="OK", cancel_text="",
        icon_path=Path(__file__).parent.parent.parent / "assets" / "images" / "turtle_wow_icon.png",
        custom_styles=custom_styles
    ).exec()