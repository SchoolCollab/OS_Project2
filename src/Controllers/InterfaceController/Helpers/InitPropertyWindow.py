import Data.Types as _TYPES
from Controllers.InterfaceController.Data import (
    InterfaceController_Types as _INTERFACE_TYPES,
)

import os as os
import pygame as pygame

import Controllers.FileSystemController as FileSystemController

from Controllers.InterfaceController.Helpers.SanitizeText import SanitizeText


def InitPropertyWindow(
    resolution: tuple[int, int], fontPath: str, fontSize: int, itemPath: str
) -> None:
    """Initialize the property window to display an item's properties.

    ### Parameters
    - **resolution** `tuple[int, int]`: The resolution of the window.
    - **fontpath** `str`: The path to the font file.
    - **fontSize** `int`: The size of the font.
    - **itempath** `str`: The path of the item (must be a file or folder).
    """
    # Set the display to be centered
    os.environ["SDL_VIDEO_CENTERED"] = "1"

    # Initialize pygame
    pygame.init()

    # Get the display
    display: _INTERFACE_TYPES.Display = pygame.display
    display.set_caption("Properties")

    # Init the display window
    surface: _INTERFACE_TYPES.Surface = display.set_mode(resolution)

    # Fill the background with a color
    surface.fill((200, 200, 200))  # Dark gray background

    # Load the font
    font: _INTERFACE_TYPES.Font = pygame.font.Font(fontPath, fontSize)

    # Prepare the properties to display
    properties = []

    if os.path.isdir(itemPath):
        # Get the folder and calculate its size
        folder: _TYPES.Folder = FileSystemController.GetItem(itemPath)
        FileSystemController.CalculateFolderSize(folder)

        # Handle folder properties
        properties.append(f"Name: {folder.name}")
        properties.append(f"Type: Folder")
        properties.append(f"Size: {folder.size} bytes")
        properties.append(f"Creation Date: {folder.creationDateTime}")

    elif os.path.isfile(itemPath):
        # Get the file and its properties
        file: _TYPES.File = FileSystemController.GetItem(itemPath)

        # Handle file properties
        properties.append(f"Name: {file.name}")
        properties.append(f"Extension: {file.extension}")
        properties.append(f"Size: {file.size} bytes")
        properties.append(f"Creation Date: {file.creationDateTime}")

    else:
        properties.append("Invalid path")

    # Render and display the properties
    for i, prop in enumerate(properties):
        renderedText = font.render(SanitizeText(prop), True, (0, 0, 0))  # White text
        surface.blit(
            renderedText, (20, i * fontSize * 2 + fontSize)
        )  # Position the text

    # Update the display
    pygame.display.update()

    # Wait for the user to close the window
    running = True

    # Handle events for property window
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEOEXPOSE:
                # Redraw the surface if the window is resized
                surface.fill((200, 200, 200))
                for i, prop in enumerate(properties):
                    renderedText = font.render(SanitizeText(prop), True, (0, 0, 0))
                    surface.blit(renderedText, (20, i * 30 + 20))

                pygame.display.update()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

    # Quit pygame
    pygame.quit()


__all__ = ["InitPropertyWindow"]
