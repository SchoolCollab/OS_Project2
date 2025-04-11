from __future__ import annotations

import pygame as pygame

type Font = pygame.font.Font
"""Type alias for pygame.font.Font"""

type Color = pygame.Color
"""Type alias for pygame.Color"""

type Rect = pygame.Rect
"""Type alias for pygame.Rect"""

type Surface = pygame.Surface
"""Type alias for pygame.Surface"""

type Display = pygame.display
"""Type alias for pygame.display"""

type Event = pygame.event.Event
"""Type alias for pygame.event.Event"""


class ItemDrawInfo:
    """A class to represent the draw info of an item.

    ### Attributes
    - **name** `Surface`: The rendered text of the name of the item.
    - **icon** `Surface`: The expansion/collapse icon if text is the name of a folder.
    - **index** `int`: The index(row) of the item.
    - **level** `int`: The level(depth) of the item.
    - **nameHitbox** `Rect`: The hitbox of the name.
    - **iconHitbox** `Rect`: The hitbox of the icon.
    - **id** `int`: The ID of the item.
    - **subItems** `list[ItemDrawInfo]`: The subitems of the current item.
    """

    def __init__(
        self,
        name: Surface,
        icon: Surface,
        index: int,
        level: int,
        partitionPath: str,
        id: int,
    ):
        """Constructs the DrawInfo for an item.

        ### Parameters
        - **name** `Surface`: The rendered text of the name of the item.
        - **icon** `Surface`: The expansion/collapse icon if item is a folder.
        - **index** `int`: The index(row) of the item.
        - **level** `int`: The level(depth) of the item.
        - **partitionPath** `str`: The path of the partition this item belongs to.
        - **id** `int`: The ID of the item.
        """
        # Set the index and level
        self.index: int = index
        self.level: int = level

        # Set the text and icon
        self.name: Surface = name
        self.icon: Surface = icon

        # Set the font size based on the icon or name
        fontSize = icon.get_height() if icon is not None else name.get_height() * 3 // 4

        # Get the hitboxes of the name and icon
        self.nameHitbox: Rect = pygame.Rect(
            level * fontSize * 2 + fontSize * 3 // 2,
            index * fontSize * 2 + fontSize,
            name.get_width(),
            name.get_height(),
        )
        self.iconHitbox: Rect = (
            pygame.Rect(
                level * fontSize * 2,
                index * fontSize * 2 + fontSize,
                icon.get_width(),
                icon.get_height(),
            )
            if icon is not None
            else None
        )

        self.partitionPath: str = partitionPath
        self.id: int = id

        self.subItems: list[ItemDrawInfo] = []

    def Move(self, index: int, level: int = None) -> None:
        """Move the item to a new position

        ### Parameters
        - **index** `int`: The new index(row) of the item.
        - **level** `int`: The new level(depth) of the item.
        """
        # Update the index and level
        self.index = index
        self.level = level if level is not None else self.level

        fontSize = (
            self.icon.get_height()
            if self.icon is not None
            else self.name.get_height() * 3 // 4
        )

        # Update the hitboxes
        self.nameHitbox.topleft = (
            self.level * fontSize * 2 + fontSize * 3 // 2,
            self.index * fontSize * 2 + fontSize,
        )
        if self.iconHitbox is not None:
            self.iconHitbox.topleft = (
                self.level * fontSize * 2,
                self.index * fontSize * 2 + fontSize,
            )


__all__ = ["Font", "Color", "Surface", "Rect", "Display", "Event", "ItemDrawInfo"]
