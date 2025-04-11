import Data.Types as _TYPES
from Controllers.InterfaceController.Data import (
    InterfaceController_Types as _INTERFACE_TYPES,
)

import os as os
import pygame as pygame
import multiprocessing as multiprocessing

import Controllers.PartitionController as PartitionController

from Controllers.InterfaceController.Helpers.SanitizeText import SanitizeText

from Controllers.InterfaceController.Data.InterfaceController_Data import (
    Data as InterfaceData,
)


def HandleItemPropertyShowing(
    event: _INTERFACE_TYPES.Event, item: _INTERFACE_TYPES.ItemDrawInfo
) -> bool:
    """Handle property window showing event

    ### Parameters
    - **event** `Event`: The event to handle.
    - **item** `ItemDrawInfo`: The item to handle the event for.
    """
    # Check if the item's name is clicked
    if not item.nameHitbox.collidepoint(
        (
            event.pos[0] + InterfaceData.screenOffset[1],
            event.pos[1] + InterfaceData.screenOffset[0],
        )
    ):
        # Skip check if the line is not expanded
        if not item.icon or item.icon == InterfaceData.images["plus"]:
            return False

        # Also check if any items' names are clicked
        for subItem in item.subItems:
            if HandleItemPropertyShowing(event, subItem):
                return True

        return False

    # Start a new process to show the properties of the item
    InterfaceData.processes.append(
        multiprocessing.Process(
            target=InitPropertyWindow,
            args=(
                InterfaceData.screenResolution,
                os.path.join(InterfaceData.dataPath, "Fonts", "font_property.ttf"),
                InterfaceData.fontSize,
                PartitionController.GetItem(item.partitionPath, item.id),
            ),
        )
    )
    InterfaceData.processes[-1].start()

    return True


def InitPropertyWindow(
    resolution: tuple[int, int],
    fontPath: str,
    fontSize: int,
    item: _TYPES.File | _TYPES.Folder,
) -> None:
    """Initialize the property window to display an item's properties or content.

    ### Parameters
    - **resolution** `tuple[int, int]`: The resolution of the window.
    - **fontPath** `str`: The path to the font file.
    - **fontSize** `int`: The size of the font.
    - **item** `File | Folder`: The item to display properties or content for.
    """
    # Set the display to be centered
    os.environ["SDL_VIDEO_CENTERED"] = "1"

    # Initialize pygame
    pygame.init()

    # Get the display
    display: _INTERFACE_TYPES.Display = pygame.display
    display.set_caption("Properties")

    # Init the display window and fill the background
    surface: _INTERFACE_TYPES.Surface = display.set_mode(resolution)
    surface.fill((200, 200, 200))  # Light gray background

    # Load the font
    font: _INTERFACE_TYPES.Font = pygame.font.Font(fontPath, fontSize)

    # Prepare the properties to display
    properties = []
    content = None
    isShowingProperties = True  # Toggle between properties and content

    if isinstance(item, _TYPES.Folder):
        # Handle folder properties
        properties.append(f"Name: {item.name}")
        properties.append(f"Type: Folder")
        properties.append(f"Creation Date: {item.creationDateTime}")

    elif isinstance(item, _TYPES.File):
        # Handle file properties
        properties.append(f"Name: {item.name}")
        properties.append(f"Extension: {item.extension}")
        properties.append(f"Size: {item.size} bytes")
        properties.append(f"Creation Date: {item.creationDateTime}")

        # If the file is a .txt file, extract its content
        if item.extension == "txt":
            print(f"Extracting content from {item.name}...")
            print(f"Item content: {item.content}")
            content = item.content

    else:
        properties.append("Invalid path")

    # Initialize the rendered properties and content
    renderedProperties: list[_INTERFACE_TYPES.Surface] = []
    renderedContent: list[_INTERFACE_TYPES.Surface] = []

    # Render text for the properties or content
    for prop in properties:
        renderedText = font.render(SanitizeText(prop), True, (0, 0, 0))
        renderedProperties.append(renderedText)

    if content:
        for line in content.split("\n"):
            renderedContent.append(font.render(SanitizeText(line), True, (0, 0, 0)))

    # Display the properties or content
    def display():
        surface.fill((200, 200, 200))  # Clear the surface

        if isShowingProperties:
            for i, prop in enumerate(renderedProperties):
                surface.blit(prop, (20, i * fontSize * 2 + fontSize))

        elif content:
            lines = content.split("\n")

            for i, line in enumerate(lines):
                surface.blit(line, (20, i * fontSize * 2 + fontSize))

        # Update the display
        pygame.display.flip()

    # Render the initial display
    display()

    # Wait for the user to close the window
    running = True

    # Handle events for property window
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEOEXPOSE:
                # Redraw the surface if the window is resized
                display()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_TAB and content:
                    # Toggle between properties and content
                    isShowingProperties = not isShowingProperties
                    display()

    # Quit pygame
    pygame.quit()


__all__ = ["HandleItemPropertyShowing"]
