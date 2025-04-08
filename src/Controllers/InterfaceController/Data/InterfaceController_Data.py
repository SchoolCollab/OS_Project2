from __future__ import annotations
from Controllers.InterfaceController.Data import (
    InterfaceController_Types as _INTERFACE_TYPES,
)

import multiprocessing as multiprocessing
from threading import Thread, Event


class InterfaceController:
    """InterfaceController class to manage the interface data and state."""

    status: bool = False

    fontSize: int = 0

    dataPath: str = ""

    fonts: dict[str, _INTERFACE_TYPES.Font] = {}
    images: dict[str, _INTERFACE_TYPES.Surface] = {}

    display: _INTERFACE_TYPES.Display = None
    surface: _INTERFACE_TYPES = None

    screenResolution: tuple[int, int] = ()
    windowResolution: tuple[int, int] = ()

    items: list[_INTERFACE_TYPES.ItemDrawInfo] = []

    expansionToggled: bool = False
    collapseToggled: bool = False

    screenOffset: tuple[int, int] = (0, 0)

    scrollingEvents: dict[str, Event] = {}
    scrollingThreads: dict[str, Thread] = {}

    processes: list[multiprocessing.Process] = []


Data: InterfaceController = InterfaceController()
""" Data for the InterfaceController

### Attributes
- **status** `bool`: The status of the interface. `True` if the interface is running, `False` otherwise.
- **fontSize** `int`: The font size of the interface.
- **dataPath** `str`: The path to the data folder.
- **fonts** `dict[str, Font]`: A dictionary of all the fonts in the interface.
- **images** `dict[str, Surface]`: A dictionary of all the images in the interface.
- **display** `Display`: The display object
- **surface** `Surface`: The surface object
- **screenResolution** `tuple[int, int]`: The resolution of the screen.
- **windowResolution** `tuple[int, int]`: The resolution of the window.
- **items** `dict[str, Surface]`: A dictionary of all the items in the interface.
- **expansionToggled** `bool`: Whether the expansion icon is toggled or not.
- **collapseToggled** `bool`: Whether the collapse icon is toggled or not.
- **screenOffset** `tuple[int, int]`: The offset of the screen.
- **scrollingEvents** `Event`: The events for page scrolling.
- **scrollingThreads** `Event`: The threads for page scrolling.
- **processes** `list[multiprocessing.Process]`: A list of all the processes in the interface.
"""

__all__ = ["Data"]
