import Data.Types as _TYPES
from Controllers.InterfaceController.Data import (
    InterfaceController_Types as _INTERFACE_TYPES,
)

import os as os
import pygame as pygame

import Controllers.FileSystemController as FileSystemController
import Controllers.InterfaceController.Helpers as Helpers

from Controllers.InterfaceController.Data.InterfaceController_Data import (
    Data as InterfaceData,
)


def DrawText(
    text: str | _INTERFACE_TYPES.Surface,
    position: tuple[int, int],
    font: _INTERFACE_TYPES.Font = None,
    color: _INTERFACE_TYPES.Color = None,
) -> None:
    """Draw text on the surface

    ### Parameters
    - **text** `str`| `Surface`: The text to draw.
    - **position** `tuple[int, int]`: The position to draw the text at.
    - **font** `Font`: The font to use for the text.
    - **color** `Color`: The color of the text.
    - **textRendered** `Surface`: The rendered text surface. If not provided, the text will be rendered again.
    """
    assert position is not None, "Position cannot be None"

    # Render the text if rendered text is not provided
    if isinstance(text, str):
        assert font is not None, "Font must be provided if text is not rendered"
        assert color is not None, "Color must be provided if text is not rendered"

        renderedText = font.render(Helpers.SanitizeText(text), True, color)
    else:
        renderedText = text

    # Blit the text on the surface
    InterfaceData.surface.blit(renderedText, position)


def DrawImage(image: _INTERFACE_TYPES.Surface, position: tuple[int, int]) -> None:
    """Draw image on the surface

    ### Parameters
    - **image** `Surface`: The image to draw.
    - **position** `tuple[int, int]`: The position to draw the image at.
    """
    assert position is not None, "Position cannot be None"

    # Blit the image on the surface
    InterfaceData.surface.blit(image, position)


def DrawItem(item: _INTERFACE_TYPES.ItemDrawInfo) -> None:
    """Draw the item on the surface

    ### Parameters
    - **item** `ItemDrawInfo`: The item to draw.
    """
    # Adjust the position based on the screen offset
    adjustedY = item.nameHitbox.y - InterfaceData.screenOffset[0]

    # Draw the text and icon on the surface
    if (
        adjustedY + InterfaceData.fontSize >= 0
        and adjustedY <= InterfaceData.screenResolution[1]
    ):
        DrawText(item.name, (item.nameHitbox.x, adjustedY - 4))
        if item.icon is not None:
            DrawImage(item.icon, (item.iconHitbox.x, adjustedY))

    # Return if the line is not expanded
    if item.icon is None or item.icon == InterfaceData.images["plus"]:
        return

    # Draw the sub items if expanded
    for subItem in item.subItems:
        DrawItem(subItem)


def EraseItem(item: _INTERFACE_TYPES.ItemDrawInfo) -> None:
    """Erase the item on the surface

    ### Parameters
    - **item** `ItemDrawInfo`: The item to erase.
    """
    # Get the area to erase
    areaToErase: _INTERFACE_TYPES.Rect = (
        0,
        item.nameHitbox.y,
        InterfaceData.screenResolution[1],
        InterfaceData.fontSize,
    )

    # Get the background at the exact line
    background = InterfaceData.images["background"].subsurface(areaToErase)

    # Fill the surface with the background
    InterfaceData.surface.blit(background, areaToErase)

    # Return if the line is not expanded
    if item.icon is None or item.icon == InterfaceData.images["plus"]:
        return

    # Erase the sub items if expanded
    for subItem in item.subItems:
        EraseItem(subItem)


__all__ = [
    "DrawText",
    "DrawImage",
    "DrawItem",
    "EraseItem",
]
