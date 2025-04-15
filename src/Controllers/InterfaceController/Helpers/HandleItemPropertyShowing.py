import Data.Types as _TYPES
from Controllers.InterfaceController.Data import (
    InterfaceController_Types as _INTERFACE_TYPES,
)

import os as os
import pygame as pygame
from threading import Thread, Event
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
                os.path.join(InterfaceData.dataPath, "Fonts"),
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
    propertyFont: _INTERFACE_TYPES.Font = pygame.font.Font(
        os.path.join(fontPath, "font_property.ttf"), fontSize
    )
    textFont: _INTERFACE_TYPES.Font = pygame.font.Font(
        os.path.join(fontPath, "font_text.ttf"), fontSize
    )

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
            content = item.content or ""

    else:
        properties.append("Invalid path")

    # Initialize the rendered properties and content
    renderedProperties: list[_INTERFACE_TYPES.Surface] = []
    renderedContent: list[_INTERFACE_TYPES.Surface] = []

    # Render text for the properties
    for prop in properties:
        renderedText = propertyFont.render(SanitizeText(prop), True, (0, 0, 0))
        renderedProperties.append(renderedText)

    # Render text for the content if available
    if content is not None:
        for line in content.split("\n"):
            # Replace emtry lines with a space
            if not line or line == "":
                line = " "

            # Replace \t with spaces
            line = line.replace("\t", " " * 4)

            # Split the line if it exceeds the width of the window
            while textFont.size(line)[0] > resolution[0] - 30:
                # Find the index to split the line
                splitIndex = 0
                while textFont.size(line[:splitIndex])[0] < resolution[0] - 30:
                    splitIndex += 1

                renderedText = textFont.render(line[:splitIndex], True, (0, 0, 0))
                renderedContent.append(renderedText)

                line = line[splitIndex:]

            renderedText = textFont.render(line, True, (0, 0, 0))
            renderedContent.append(renderedText)

    def calculateMaxScroll() -> int:
        """Calculate the maximum scroll offset based on the content."""
        return max(0, len(renderedContent) * fontSize * 2 - resolution[1])

    # Initialize scrolling variables
    scrollOffset = 0
    maxScroll = calculateMaxScroll()
    scrollingEvents = {"up": Event(), "down": Event()}

    def display():
        """Render the properties or content."""
        surface.fill((200, 200, 200))  # Clear the surface

        if isShowingProperties:
            for i, prop in enumerate(renderedProperties):
                surface.blit(prop, (20, i * fontSize * 2 + fontSize))

            # Add a toggle message if content is available
            if content is not None:
                toggleMessage = propertyFont.render(
                    "Press TAB to view content", True, (0, 0, 0)
                )
                surface.blit(toggleMessage, (20, resolution[1] - fontSize * 2))

        else:
            for i, line in enumerate(renderedContent):
                yPosition = i * fontSize * 2 - scrollOffset

                if 0 <= yPosition < resolution[1]:  # Only render visible lines
                    surface.blit(line, (20, yPosition))

        pygame.display.flip()

    def handleScrolling(direction: str, scrollValue: int):
        """Handle smooth scrolling in a specific direction."""
        initialWait = 100

        while scrollingEvents[direction].is_set():
            # Calculate the scroll offset
            nonlocal scrollOffset
            scrollOffset = max(0, min(scrollOffset + scrollValue, maxScroll))

            # Update the display
            display()

            initialWait = max(
                5, initialWait - 10
            )  # Reduce wait time for smoother scrolling

            pygame.time.wait(initialWait)

    # Render the initial display
    display()

    # Wait for the user to close the window
    running = True
    scrollingThreads = {"up": None, "down": None}

    # Handle events for property window
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEOEXPOSE:
                # Redraw the surface if the window is resized
                display()

            elif event.type == pygame.MOUSEWHEEL:
                # Adjust the scroll offset based on the mouse wheel
                scrollOffset -= event.y * fontSize * 2
                scrollOffset = max(0, min(scrollOffset, maxScroll))

                display()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_TAB and content is not None:
                    # Toggle between properties and content
                    isShowingProperties = not isShowingProperties
                    scrollOffset = 0  # Reset scroll offset

                    # Recalculate max scroll and display
                    calculateMaxScroll()
                    display()

                elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    # Start scrolling thread for UP or DOWN
                    direction = "up" if event.key == pygame.K_UP else "down"
                    scrollValue = -fontSize * 2 if direction == "up" else fontSize * 2

                    if not scrollingEvents[direction].is_set():
                        # Set the event to start scrolling
                        scrollingEvents[direction].set()

                        # Start the scrolling thread
                        scrollingThreads[direction] = Thread(
                            target=handleScrolling, args=(direction, scrollValue)
                        )
                        scrollingThreads[direction].start()

            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_UP, pygame.K_DOWN):
                    # Stop scrolling thread for UP or DOWN
                    direction = "up" if event.key == pygame.K_UP else "down"
                    scrollingEvents[direction].clear()

                    if scrollingThreads[direction] is not None:
                        scrollingThreads[direction].join()

    # Quit pygame
    pygame.quit()


__all__ = ["HandleItemPropertyShowing"]
