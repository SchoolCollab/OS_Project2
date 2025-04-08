import Data.Types as _TYPES
from Controllers.InterfaceController.Data import (
    InterfaceController_Types as _INTERFACE_TYPES,
)

import os as os
import pygame as pygame

import Controllers.PartitionController as PartitionController
import Controllers.FileSystemController as FileSystemController

import Controllers.InterfaceController.Utilities as Utilities
import Controllers.InterfaceController.Helpers as Helpers

from Controllers.InterfaceController.Data.InterfaceController_Data import (
    Data as InterfaceData,
)


def Init() -> None:
    """Initialize the interface"""

    # Set the display to be centered
    os.environ["SDL_VIDEO_CENTERED"] = "1"

    # Initialize pygame
    pygame.init()

    # Get the resolutions
    displayInfo = pygame.display.Info()
    InterfaceData.surfaceResolution = (displayInfo.current_w, displayInfo.current_h)
    InterfaceData.screenResolution = (
        InterfaceData.surfaceResolution[0] // 2,
        InterfaceData.surfaceResolution[1] // 2,
    )

    # Init the display
    InterfaceData.display = pygame.display
    InterfaceData.display.init()
    InterfaceData.display.set_caption("Explorer")

    # Get the absolute path to the fonts and images directory
    InterfaceData.dataPath = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "..",
        "Data",
        "Assets",
    )

    fontPath = os.path.join(InterfaceData.dataPath, "Fonts")
    imagePath = os.path.join(InterfaceData.dataPath, "Images")

    # Initialize the window
    InterfaceData.surface = InterfaceData.display.set_mode(
        InterfaceData.screenResolution, pygame.RESIZABLE
    )

    # Set the font size
    InterfaceData.fontSize = 17

    # Get the fonts
    InterfaceData.fonts["explorer"] = pygame.font.Font(
        os.path.join(fontPath, "font_explorer.ttf"), InterfaceData.fontSize
    )
    InterfaceData.fonts["property"] = pygame.font.Font(
        os.path.join(fontPath, "font_property.ttf"), InterfaceData.fontSize
    )

    # Get the images
    InterfaceData.images["background"] = pygame.image.load(
        os.path.join(imagePath, "background.png")
    ).convert_alpha()
    InterfaceData.images["plus"] = pygame.image.load(
        os.path.join(imagePath, "Icons", "plus.png")
    ).convert_alpha()
    InterfaceData.images["minus"] = pygame.image.load(
        os.path.join(imagePath, "Icons", "minus.png")
    ).convert_alpha()

    # Scale the icons down to the font size
    InterfaceData.images["plus"] = pygame.transform.scale(
        InterfaceData.images["plus"], (InterfaceData.fontSize, InterfaceData.fontSize)
    )
    InterfaceData.images["minus"] = pygame.transform.scale(
        InterfaceData.images["minus"], (InterfaceData.fontSize, InterfaceData.fontSize)
    )

    # Scale the background to the screen resolution and draw
    # InterfaceData.images["background"] = pygame.transform.scale(
    #     InterfaceData.images["background"], InterfaceData.screenResolution
    # )
    # DrawImage(InterfaceData.images["background"], (0, 0))
    InterfaceData.surface.fill((200, 200, 200))  # Dark gray background

    # Draw the partition name on the surface
    partitions = PartitionController.GetPartitions()

    # Get the partitions and draw them on the surface
    for i, partition in enumerate(partitions):
        # Render the partition mount point
        renderedPartitionName = InterfaceData.fonts["explorer"].render(
            Helpers.SanitizeText(partition.mountPoint), True, (0, 0, 0)
        )

        # Append the partition name to the lines list
        InterfaceData.items.append(
            _INTERFACE_TYPES.ItemDrawInfo(
                renderedPartitionName,
                InterfaceData.images["plus"],
                i,
                0,
                partition.mountPoint,
            )
        )

        DrawItem(InterfaceData.items[-1])

    # Update the display
    InterfaceData.display.flip()

    # Set the status to True
    InterfaceData.status = True

    # Handle pygame events
    while InterfaceData.status:
        for event in pygame.event.get():
            # Handle events
            EventHandler(event)

    # Clean pygame
    InterfaceData.display.quit()
    pygame.quit()

    # Wait for all processes to finish453eewwd4r
    for process in InterfaceData.processes:
        process.join()


def EventHandler(event: pygame.event.Event) -> None:
    """Handle events for the interface

    ### Returns
    - **None**: None
    """
    # Handle quit event
    if event.type == pygame.QUIT:
        InterfaceData.status = False

    # Handle window resize
    elif event.type == pygame.VIDEORESIZE:
        # Update the surface resolution
        InterfaceData.screenResolution = (event.w, event.h)

        # Scale the background to the new resolution
        # InterfaceData.images["background"] = pygame.transform.scale(
        #     InterfaceData.images["background"], InterfaceData.screenResolution
        # )
        # InterfaceData.surface.blit(InterfaceData.images["background"], (0, 0))
        InterfaceData.surface.fill((200, 200, 200))  # Dark gray background

        # Redraw all items
        for item in InterfaceData.items:
            DrawItem(item)

        # Update the display
        InterfaceData.display.update()

    # Handle mouse button down event
    elif event.type == pygame.MOUSEBUTTONDOWN:
        # Return if the button is not left mouse
        if event.button != 1:
            return

        # Initialize the index and toggled flags
        index = 0
        InterfaceData.expansionToggled = False
        InterfaceData.collapseToggled = False

        # Handle the expansion/collapse event for each item
        for item in InterfaceData.items:
            index = Helpers.FolderExpansionHandler(event, item, index)

        # Redraw the entire screent if folder expansion/collapse is toggled
        if InterfaceData.expansionToggled or InterfaceData.collapseToggled:
            # Fill the surface with the background
            # InterfaceData.surface.blit(Data.images["background"], (0, 0))
            InterfaceData.surface.fill((200, 200, 200))  # Dark gray background

            # Redraw all items
            for item in InterfaceData.items:
                DrawItem(item)

            # Update the display
            InterfaceData.display.flip()
            return

        # Handle the property window showing event
        for item in InterfaceData.items:
            if Helpers.ItemPropertyShowingHandler(event, item):
                return

    # Handle mouse wheel scrolling
    elif event.type == pygame.MOUSEWHEEL:
        # Limit the scroll range by getting the last item
        lastItem = InterfaceData.items[-1]

        while len(lastItem.subItems) > 0:
            # Get the last sub item
            lastItem = lastItem.subItems[-1]

        # Get the maximum scroll value
        maxScroll = lastItem.index * InterfaceData.fontSize * 2 + 100

        # Update the screen offset
        InterfaceData.screenOffset = (
            max(
                0,
                min(
                    InterfaceData.screenOffset[0]
                    - event.y * InterfaceData.fontSize * 2,
                    maxScroll
                    - InterfaceData.screenResolution[1]
                    + InterfaceData.fontSize * 2,
                ),
            ),
            0,
        )

        # Redraw the screen with the updated scroll offset
        InterfaceData.surface.fill((200, 200, 200))  # Dark gray background
        for item in InterfaceData.items:
            DrawItem(item)

        InterfaceData.display.update()

    elif event.type == pygame.KEYDOWN:
        # Check if the key pressed is Escape
        if event.key == pygame.K_ESCAPE:
            InterfaceData.status = False

    # Remove terminated processes from the processes list
    InterfaceData.processes = [
        process for process in InterfaceData.processes if process.is_alive()
    ]


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
    """
    Utilities.DrawText(text, position, font, color)


def DrawImage(image: _INTERFACE_TYPES.Surface, position: tuple[int, int]) -> None:
    """Draw image on the surface

    ### Parameters
    - **image** `Surface`: The image to draw.
    - **position** `tuple[int, int]`: The position to draw the image at.
    """
    Utilities.DrawImage(image, position)


def DrawItem(item: _INTERFACE_TYPES.ItemDrawInfo) -> None:
    """Draw the item on the surface

    ### Parameters
    - **item** `ItemDrawInfo`: The item to draw.
    """
    Utilities.DrawItem(item)


def EraseItem(item: _INTERFACE_TYPES.ItemDrawInfo) -> None:
    """Erase the item on the surface

    ### Parameters
    - **item** `ItemDrawInfo`: The item to erase.
    """
    Utilities.EraseItem(item)


__all__ = {"InterfaceData", "Init"}
