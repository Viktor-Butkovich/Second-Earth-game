# Contains functions that control the display of new notifications

from modules.constants import constants, status, flags


def show_tutorial_notifications():
    """
    Description:
        Displays tutorial messages at various points in the program. The exact message depends on how far the player has advanced through the tutorial
    Input:
        None
    Output:
        None
    """
    if not status.initial_tutorial_completed:
        constants.notification_manager.display_notification(
            {"message": "Initial tutorial message /n /n"}
        )
        status.initial_tutorial_completed = True
