import Data.Types as _TYPES
from Controllers.InterfaceController.Data import (
    InterfaceController_Types as _INTERFACE_TYPES,
)

import Controllers.FileSystemController as FileSystemController

from Controllers.InterfaceController.Helpers.SanitizeText import SanitizeText

from Controllers.InterfaceController.Data.InterfaceController_Data import (
    Data as InterfaceData,
)


def HandleFolderExpansion(
    event: _INTERFACE_TYPES.Event,
    item: _INTERFACE_TYPES.ItemDrawInfo,
    index: int,
) -> int:
    """Handle the folder expansion/collapse event

    ### Parameters
    - **event** `Event`: The event to handle.
    - **item** `ItemDrawInfo`: The item to handle the event for.
    - **index** `int`: The index of the item.
    """
    # Update the index of the items after expanded/collapsed item
    if InterfaceData.expansionToggled or InterfaceData.collapseToggled:
        item.Move(index)
        index += 1

        # Check if the item is a folder and collapsed
        if not item.icon or item.icon == InterfaceData.images["plus"]:
            return index

        # Increment the index for the sub-items
        for subItem in item.subItems:
            index = HandleFolderExpansion(event, subItem, index)

        return index

    # If item is a file, return
    if item.icon is None:
        return index

    # Check if the folder's icon is clicked
    if not item.iconHitbox.collidepoint(
        (
            event.pos[0] + InterfaceData.screenOffset[1],
            event.pos[1] + InterfaceData.screenOffset[0],
        )
    ):
        # Skip check for sub items if the folder is not expanded
        if item.icon == InterfaceData.images["plus"]:
            return index

        # Also check if icons of any sub folders are clicked
        for subItem in item.subItems:
            index = HandleFolderExpansion(event, subItem, index)

        return index

    # Get the index of the interacted item
    index = item.index + 1

    # Check if the folder is expanded or collapsed
    if item.icon == InterfaceData.images["plus"]:
        # Change the icon to minus
        item.icon = InterfaceData.images["minus"]
        InterfaceData.expansionToggled = True

    else:
        # Change the icon to plus
        item.icon = InterfaceData.images["plus"]
        InterfaceData.collapseToggled = True

        return index

    # Check if the folder has any sub items
    if len(item.subItems) > 0:
        # Update the index of the folder's sub items
        for subItem in item.subItems:
            index = HandleFolderExpansion(event, subItem, index)

        return index

    # Get the folder's descendants
    files, subfolders = FileSystemController.GetDescendants(
        _TYPES.Folder(item.itempath)
    )

    for subfolder in subfolders:
        # Render the subfolder name
        renderedSubfolderName = InterfaceData.fonts["explorer"].render(
            SanitizeText(subfolder.name), True, (0, 0, 0)
        )

        # Get the item info
        itemInfo = _INTERFACE_TYPES.ItemDrawInfo(
            renderedSubfolderName,
            InterfaceData.images["plus"],
            index,
            item.level + 1,
            subfolder.path,
        )

        # Append the folder to current folder's subItems
        item.subItems.append(itemInfo)

        # Increment the index
        index += 1

    for file in files:
        # Render the file name
        renderedFileName = InterfaceData.fonts["explorer"].render(
            SanitizeText(file.name + file.extension), True, (0, 0, 0)
        )

        # Get the item, info
        itemInfo = _INTERFACE_TYPES.ItemDrawInfo(
            renderedFileName,
            None,
            index,
            item.level + 1,
            file.path,
        )

        # Append the file to current folder's subItems
        item.subItems.append(itemInfo)

        # Increment the index
        index += 1

    return index


__all__ = ["HandleFolderExpansion"]
