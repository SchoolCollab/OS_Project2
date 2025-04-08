import os as os
import pygame as pygame

import Controllers.InterfaceController.Utilities as Utilities

from Controllers.InterfaceController.Data.InterfaceController_Data import (
    Data as InterfaceData,
)


def RedrawScreen() -> None:
    """Redraw the screen"""
    # Fill the screen with grey
    InterfaceData.surface.fill((200, 200, 200))

    # Draw the items on the screen
    for item in InterfaceData.items:
        Utilities.DrawItem(item)

    # Update the display
    pygame.display.update()


__all__ = ["RedrawScreen"]
