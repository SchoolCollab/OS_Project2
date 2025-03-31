from __future__ import annotations
import Data.Types as _TYPES

import os as os
import sys as sys
import copy as copy
import pygame as pygame
import logging as logging
import multiprocessing as multiprocessing

import Utilities as Utilities
import Controllers.PartitionController as PartitionController


type Surface = pygame.Surface
"""Type alias for pygame.Surface"""

type Rect = pygame.Rect
"""Type alias for pygame.Rect"""

type Font = pygame.font.Font
"""Type alias for pygame.font.Font"""

type Color = pygame.Color
"""Type alias for pygame.Color"""


class LineDrawInfo:
    """A class to represent the draw info of a line.

    ### Attributes
    - **text** `Surface`: The rendered text.
    - **icon** `Surface`: The expansion/collapse icon if text is the name of a folder.
    - **index** `int`: The index(row) of the line.
    - **level** `int`: The level(depth) of the line.
    - **iconRect** `pygame.Rect`: The rect of the icon.
    - **textRect** `pygame.Rect`: The rect of the text.
    - **itempath** `str`: The path of the item represented by this line.
    - **subLines** `list[LineDrawInfo]`: The sublines of the line.
    - **selected** `bool`: Whether the line is selected or not.
    """

    def __init__(
        self,
        text: Surface,
        icon: Surface,
        index: int,
        level: int,
        itempath: str,
    ):
        """Constructs the DrawInfo for a line.

        ### Parameters
        - **text** `Surface`: The rendered text.
        - **icon** `Surface`: The expansion/collapse icon if text is the name of a folder.
        - **index** `int`: The index(row) of the line.
        - **level** `int`: The level(depth) of the line.
        - **itempath** `str`: The path of the item represented by this line.
        """
        # Set the index and level
        self.index: int = index
        self.level: int = level

        # Set the text and icon
        self.text: Surface = text
        self.icon: Surface = icon

        # Get the rects of the text and icon
        self.textRect: Rect = pygame.Rect(
            level * 40 + 30, index * 30 + 14, Data.screenResolution[0], Data.fontSize
        )
        self.iconRect: pygame.Rect = (
            pygame.Rect(
                level * 40 + 10,
                index * 30 + 14,
                icon.get_width(),
                icon.get_height(),
            )
            if icon is not None
            else None
        )

        self.itempath: str = itempath
        self.subLines: list[LineDrawInfo] = []

        self.selected: bool = False

    def Move(self, index: int, level: int = None) -> None:
        """Move the line to a new position

        ### Parameters
        - **index** `int`: The new index(row) of the line.
        - **level** `int`: The new level(depth) of the line.
        """
        # Update the index and level
        self.index = index
        self.level = level if level is not None else self.level

        # Update the rects
        self.textRect.topleft = (self.level * 40 + 30, self.index * 30 + 14)
        if self.iconRect is not None:
            self.iconRect.topleft = (self.level * 40 + 10, self.index * 30 + 14)

    def Draw(self) -> None:
        """Draw the line on the surface"""
        # Return if the line is out of the screen
        if self.textRect.y > Data.screenResolution[1]:
            return

        # Draw the text and icon on the surface
        DrawText(self.text, (self.textRect.x, self.textRect.y - 4))
        if self.icon is not None:
            DrawImage(self.icon, (self.iconRect.x, self.iconRect.y))

        # Return if the line is not expanded
        if self.icon is None or self.icon == Data.images["plus"]:
            return

        # Also draw the sublines if expanded
        for subline in self.subLines:
            subline.Draw()

    def Erase(self) -> None:
        """Erase the line on the surface"""
        # Get the area to erase
        areaToErase = (
            0,
            self.textRect.y,
            Data.screenResolution[1],
            Data.fontSize,
        )

        # Get the background at the exact line
        background = Data.images["background"].subsurface(areaToErase)

        # Fill the surface with the background
        Data.surface.blit(background, areaToErase)


class InterfaceController:
    status: bool = False

    fontSize: int = 15

    fonts: dict[str, pygame.font.Font] = {}
    images: dict[str, Surface] = {}

    display: pygame.display = None
    surface: Surface = None

    screenResolution: tuple[int, int] = ()
    windowResolution: tuple[int, int] = ()

    lines: list[LineDrawInfo] = []

    expansionToggled: bool = False
    collapseToggled: bool = False

    processes: list[multiprocessing.Process] = []


Data: InterfaceController = InterfaceController()
""" Data for the InterfaceController

### Attributes
- **status** `bool`: The status of the interface. `True` if the interface is running, `False` otherwise.
- **fonts** `dict[str, pygame.font.Font]`: A dictionary of all the fonts in the interface.
- **images** `dict[str, Surface]`: A dictionary of all the images in the interface.
- **display** `pygame.display`: The display object
- **surface** `Surface`: The surface object
- **screenResolution** `tuple[int, int]`: The resolution of the screen.
- **windowResolution** `tuple[int, int]`: The resolution of the window.
- **lines** `dict[str, Surface]`: A dictionary of all the lines in the interface.
- **expansionToggled** `bool`: Whether the expansion icon is toggled or not.
- **collapseToggled** `bool`: Whether the collapse icon is toggled or not.
- **processes** `list[multiprocessing.Process]`: A list of all the processes in the interface.
"""


def Init() -> None:
    """Initialize the interface"""

    # Set the display to be centered
    os.environ["SDL_VIDEO_CENTERED"] = "1"

    # Initialize pygame
    pygame.init()

    # Get the resolutions
    displayInfo = pygame.display.Info()
    Data.surfaceResolution = (displayInfo.current_w, displayInfo.current_h)
    Data.screenResolution = (
        Data.surfaceResolution[0] // 2,
        Data.surfaceResolution[1] // 2,
    )

    # Init the display
    Data.display = pygame.display
    Data.display.init()
    Data.display.set_caption("Explorer")

    # Get the absolute path to the fonts and images directory
    basePath = os.path.dirname(os.path.abspath(__file__))  # Directory of this script
    fontPath = os.path.join(basePath, "..", "Data", "Assets", "Fonts")
    imagePath = os.path.join(basePath, "..", "Data", "Assets", "Images")

    # Initialize the window
    Data.surface = Data.display.set_mode(Data.screenResolution, pygame.RESIZABLE)

    # Get the fonts
    Data.fonts["explorer"] = pygame.font.Font(
        os.path.join(fontPath, "font_explorer.ttf"), Data.fontSize
    )
    Data.fonts["property"] = pygame.font.Font(
        os.path.join(fontPath, "font_property.ttf"), Data.fontSize
    )

    # Get the images
    Data.images["background"] = pygame.image.load(
        os.path.join(imagePath, "background.png")
    ).convert_alpha()
    Data.images["plus"] = pygame.image.load(
        os.path.join(imagePath, "Icons", "plus.png")
    ).convert_alpha()
    Data.images["minus"] = pygame.image.load(
        os.path.join(imagePath, "Icons", "minus.png")
    ).convert_alpha()

    # Scale the background to the screen resolution
    Data.images["background"] = pygame.transform.scale(
        Data.images["background"], Data.screenResolution
    )

    # Scale the icons down to the font size
    Data.images["plus"] = pygame.transform.scale(
        Data.images["plus"], (Data.fontSize, Data.fontSize)
    )
    Data.images["minus"] = pygame.transform.scale(
        Data.images["minus"], (Data.fontSize, Data.fontSize)
    )

    # Draw the background on the surface
    DrawImage(Data.images["background"], (0, 0))

    # Draw the partition name on the surface
    partitions = PartitionController.GetPartitions()

    # Get the partitions and draw them on the surface
    for i, partition in enumerate(partitions):
        # Render the partition mount point
        renderedPartitionName = Data.fonts["explorer"].render(
            Utilities.SanitizeText(partition.mountPoint), True, (255, 255, 255)
        )

        # Append the partition name to the lines list
        Data.lines.append(
            LineDrawInfo(
                renderedPartitionName, Data.images["plus"], i, 0, partition.mountPoint
            )
        )

        Data.lines[-1].Draw()

    # Update the display
    Data.display.flip()

    # Set the status to True
    Data.status = True

    # Handle pygame events
    while Data.status:
        for event in pygame.event.get():
            # Handle events
            EventHandler(event)

    # Clean pygame
    Data.display.quit()
    pygame.quit()

    # Wait for all processes to finish453eewwd4r
    for process in Data.processes:
        process.join()


def InitPropertyWindow(resolution: tuple[int, int], itempath: str) -> None:
    """Initialize the property window to display file or folder properties.

    ### Parameters
    - **resolution** `tuple[int, int]`: The resolution of the window.
    - **itempath** `str`: The path of the file or folder.
    """
    # Set the display to be centered
    os.environ["SDL_VIDEO_CENTERED"] = "1"

    # Initialize pygame
    pygame.init()

    # Get the display
    display = pygame.display
    display.set_caption("Properties")

    # Init the display window
    surface = display.set_mode(resolution)

    # Fill the background with a color
    surface.fill((30, 30, 30))  # Dark gray background

    # Load the font
    basePath = os.path.dirname(os.path.abspath(__file__))
    fontPath = os.path.join(
        basePath, "..", "Data", "Assets", "Fonts", "font_property.ttf"
    )
    font = pygame.font.Font(fontPath, 20)

    # Prepare the properties to display
    properties = []

    if os.path.isdir(itempath):
        # Get the folder and calculate its size
        folder: _TYPES.Folder = PartitionController.GetItem(itempath)
        PartitionController.CalculateFolderSize(folder)

        # Handle folder properties
        properties.append(f"Name: {folder.name}")
        properties.append(f"Type: Folder")
        properties.append(f"Size: {folder.size} bytes")
        properties.append(f"Creation Date: {folder.creationDateTime}")

    elif os.path.isfile(itempath):
        # Get the file and its properties
        file: _TYPES.File = PartitionController.GetItem(itempath)

        # Handle file properties
        properties.append(f"Name: {file.name}")
        properties.append(f"Extension: {file.extension}")
        properties.append(f"Size: {file.size} bytes")
        properties.append(f"Creation Date: {file.creationDateTime}")

    else:
        properties.append("Invalid path")

    # Render and display the properties
    for i, prop in enumerate(properties):
        renderedText = font.render(
            Utilities.SanitizeText(prop), True, (255, 255, 255)
        )  # White text
        surface.blit(renderedText, (20, i * 30 + 20))  # Position the text

    # Update the display
    pygame.display.update()

    # Wait for the user to close the window
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEOEXPOSE:
                # Redraw the surface if the window is resized
                surface.fill((30, 30, 30))
                for i, prop in enumerate(properties):
                    renderedText = font.render(
                        Utilities.SanitizeText(prop), True, (255, 255, 255)
                    )
                    surface.blit(renderedText, (20, i * 30 + 20))

                pygame.display.update()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

    # Quit pygame
    pygame.quit()


def ItemPropertyShowingHandler(event: pygame.event.Event, line: LineDrawInfo) -> bool:
    """Handle property window showing event

    ### Parameters
    - **event** `pygame.event.Event`: The event to handle.
    - **line** `LineDrawInfo`: The line to handle the event for.
    """
    # Check if the line is clicked
    if not line.textRect.collidepoint(event.pos):
        # Skip sublines check if the line is not expanded
        if not line.icon or line.icon == Data.images["plus"]:
            return False

        # Also check if any items are clicked
        for subline in line.subLines:
            if ItemPropertyShowingHandler(event, subline):
                return True

        return False

    print("Clicked on item:", line.itempath)

    # Start a new process to show the properties of the item
    Data.processes.append(
        multiprocessing.Process(
            target=InitPropertyWindow,
            args=(Data.screenResolution, line.itempath),
        )
    )
    Data.processes[-1].start()

    return True


def FolderExpansionHandler(
    event: pygame.event.Event,
    line: LineDrawInfo,
    index: int,
) -> int:
    """Handle the folder expansion/collapse event

    ### Parameters
    - **event** `pygame.event.Event`: The event to handle.
    - **line** `LineDrawInfo`: The line to handle the event for.
    - **index** `int`: The index of the line.
    """
    # Update the index of the lines after expanded/collapsed line
    if Data.expansionToggled or Data.collapseToggled:
        line.Move(index)
        index += 1

        # Check if the line is collapsed
        if not line.icon or line.icon == Data.images["plus"]:
            return index

        # Increment the index for the sublines
        for subline in line.subLines:
            index = FolderExpansionHandler(event, subline, index)

        return index

    # If line represents a file, return
    if line.icon is None:
        return index

    # Check if the folder is clicked
    if not line.iconRect.collidepoint(event.pos):
        # Skip sublines check if the folder is not expanded
        if line.icon == Data.images["plus"]:
            return index

        # Also check if icons of any folders are clicked
        for subline in line.subLines:
            index = FolderExpansionHandler(event, subline, index)

        return index

    # Get the index of the line
    index = line.index + 1

    # Check if the line is expanded or collapsed
    if line.icon == Data.images["plus"]:
        # Change the icon to minus
        line.icon = Data.images["minus"]
        Data.expansionToggled = True

    else:
        # Change the icon to plus
        line.icon = Data.images["plus"]
        Data.collapseToggled = True

    # Return if the line is collapsed
    if line.icon == Data.images["plus"]:
        return index

    # Check if the line has sublines
    if len(line.subLines) > 0:
        # Update the index of the line's sublines
        for subline in line.subLines:
            index = FolderExpansionHandler(event, subline, index)

        return index

    # Check if the item is a folder
    if not os.path.isdir(line.itempath):
        logging.error(f"{line.itempath} is not a folder")
        return index

    # Get the folder's descendants
    files, subfolders = PartitionController.GetDescendants(_TYPES.Folder(line.itempath))

    for subfolder in subfolders:
        # Render the subfolder name
        renderedSubfolderName = Data.fonts["explorer"].render(
            Utilities.SanitizeText(subfolder.name), True, (255, 255, 255)
        )

        # Get the line info
        lineInfo = LineDrawInfo(
            renderedSubfolderName,
            Data.images["plus"],
            index,
            line.level + 1,
            subfolder.path,
        )

        # Append the line to line.sublines
        line.subLines.append(lineInfo)

        # Increment the index
        index += 1

    for file in files:
        # Render the file name
        renderedFileName = Data.fonts["explorer"].render(
            Utilities.SanitizeText(file.name + file.extension), True, (255, 255, 255)
        )

        # Get the line info
        lineInfo = LineDrawInfo(
            renderedFileName,
            None,
            index,
            line.level + 1,
            file.path,
        )

        # Append the line to line.sublines
        line.subLines.append(lineInfo)

        # Increment the index
        index += 1

    return index


def EventHandler(event: pygame.event.Event) -> None:
    """Handle events for the interface

    ### Returns
    - **None**: None
    """
    # Handle quit event
    if event.type == pygame.QUIT:
        Data.status = False

    # Handle window resize
    elif event.type == pygame.VIDEORESIZE:
        # Update the surface resolution
        Data.screenResolution = (event.w, event.h)

        # Scale the background to the new resolution
        Data.images["background"] = pygame.transform.scale(
            Data.images["background"], Data.screenResolution
        )
        Data.surface.blit(Data.images["background"], (0, 0))

        # Redraw all lines
        for line in Data.lines:
            line.Draw()

        # Update the display
        Data.display.update()

    # Handle mouse button down event
    elif event.type == pygame.MOUSEBUTTONDOWN:
        # Return if the button is not left mouse
        if event.button != 1:
            return

        # Initialize the index and toggled flags
        index = 0
        Data.expansionToggled = False
        Data.collapseToggled = False

        # Handle the expansion/collapse event for each line
        for line in Data.lines:
            index = FolderExpansionHandler(event, line, index)

        # Redraw the entire screent if folder expansion/collapse is toggled
        if Data.expansionToggled or Data.collapseToggled:
            # Fill the surface with the background
            Data.surface.blit(Data.images["background"], (0, 0))

            # Redraw all lines
            for line in Data.lines:
                line.Draw()

            # Update the display
            Data.display.flip()
            return

        # Handle the property window showing event
        for line in Data.lines:
            if ItemPropertyShowingHandler(event, line):
                return


def DrawText(
    text: str | Surface,
    position: tuple[int, int],
    font: Font = None,
    color: Color = None,
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

        renderedText = font.render(Utilities.SanitizeText(text), True, color)
    else:
        renderedText = text

    # Blit the text on the surface
    Data.surface.blit(renderedText, position)


def DrawImage(image: Surface, position: tuple[int, int]) -> None:
    """Draw image on the surface

    ### Parameters
    - **image** `Surface`: The image to draw.
    - **position** `tuple[int, int]`: The position to draw the image at.
    """
    assert position is not None, "Position cannot be None"

    # Blit the image on the surface
    Data.surface.blit(image, position)


__all__ = {"Data", "Init"}
