import Data.Types as _TYPES

import os as os
import psutil as psutil
import logging as logging

import Controllers.PartitionController as PartitionController


class FileSystemController:
    files: dict[str, _TYPES.File] = {}
    folders: dict[str, _TYPES.Folder] = {}


Data: FileSystemController = FileSystemController()
"""Data for the FileSystemController

### Attributes
- **files** `dict[str, _TYPES.File]`: A dictionary of all the files in the disk.
- **folders** `dict[str, _TYPES.Folder]`: A dictionary of all the folders in the disk.
"""


def GetItem(itempath: str) -> _TYPES.File | _TYPES.Folder | None:
    """Get a file or folder from the path.

    ### Parameters
    - **itempath** `str`: The path of the file or folder.

    ### Returns
    - `_TYPES.File | _TYPES.Folder | None`: The file or folder object if it exists, `None` otherwise.
    """
    # Check if the item exists in the files dictionary
    if PartitionController.IsFile(itempath):
        if itempath not in Data.files:
            Data.files[itempath] = _TYPES.File(itempath)

        return Data.files[itempath]

    # Check if the item exists in the folders dictionary
    if os.path.isdir(itempath):
        if itempath not in Data.folders:
            Data.folders[itempath] = _TYPES.Folder(itempath)

        return Data.folders[itempath]

    return None


def GetDescendants(
    folder: _TYPES.Folder = None, path: str = None
) -> _TYPES.Descendants:
    """Get the descendants of a folder.

    ### Parameters
    - **folder** `_TYPES.Folder`: The folder object.
    - **path** `str`: The path of the folder.

    ### Returns
    - `_TYPES.Descendants`: The descendants of the folder (files and sub-folders).
    """
    assert (
        folder is not None or path is not None
    ), "Either folder or path must be provided"

    # Add the folder if the folder is not in the folders dictionary
    if folder is not None and folder.path not in Data.folders:
        Data.folders[folder.path] = folder

    elif path is not None:
        if path not in Data.folders:
            Data.folders[path] = _TYPES.Folder(path)

        # Get the folder object from the folders dictionary
        folder = Data.folders[path]

    # If the folder's size is already fully calculated, return the folder's descendants
    if folder.fullSize:
        return folder.descendants

    try:
        # Store the old size of the folder
        oldSize = folder.size

        # Get all the files and sub-folders' path in the folder
        filePaths: set[str] = {file.path for file in folder.descendants.files}
        folderPaths: set[str] = {folder.path for folder in folder.descendants.folders}

        # Get the descendants of the folder
        for dirpath, dirnames, filenames in os.walk(folder.path, topdown=True):
            # Skip symbolic links
            if os.path.islink(dirpath):
                logging.warning(f"Skipping symbolic link: {dirpath}")
                continue

            # Add the files to the current folder's descendants
            for filename in filenames:
                # Get the file path
                filepath = os.path.join(dirpath, filename)

                # Check if the file exists
                if not os.path.isfile(filepath):
                    logging.error(f"{filepath} is not a file")

                # Continue if the file is already in the current folder's descendants
                if filepath in filePaths:
                    continue

                # Add the current file path to the filePaths set
                filePaths.add(filepath)

                # Add the file to the files dictionary if the file does not exist
                if filepath not in Data.files:
                    Data.files[filepath] = _TYPES.File(filepath, folder)

                # Add the file to the descendant files list and update the size
                folder.descendants.files.append(Data.files[filepath])
                folder.size += folder.descendants.files[-1].size

            # Add the current folder to the sub-folders list
            for dirname in dirnames:
                # Get the folder path
                folderpath = os.path.join(dirpath, dirname)

                # Add the folder to the folders list if the folder exists
                if not os.path.isdir(folderpath):
                    logging.error(f"{folderpath} is not a folder")

                # Continue if the folder is already in the current folder's descendants
                if folderpath in folderPaths:
                    continue

                # Add the current folder path to the folderPaths set
                folderPaths.add(folderpath)

                # Add the folder to the folders dictionary if the folder does not exist
                if folderpath not in Data.folders:
                    Data.folders[folderpath] = _TYPES.Folder(folderpath, folder)

                # Add the folder to the descendant folders list and update the size
                folder.descendants.folders.append(Data.folders[folderpath])
                folder.size += folder.descendants.folders[-1].size

            # Clear the dirnames list to stop the walk from going deeper
            dirnames.clear()

        # Check if the folder's size is fully calculated
        folder.fullSize = (
            all(currentFolder.fullSize for currentFolder in folder.descendants.folders)
            or len(folder.descendants.folders) == 0
        )

        # Check if the folder's size is updated
        if folder.size != oldSize:
            # Get the parent folder
            parentFolder = folder.parent
            currentFolder = folder

            # Store the size difference
            sizeDifference = folder.size - oldSize

            # Update the size of the parent folders
            while parentFolder is not None:
                parentFolder.size += sizeDifference

                # Also check if the parent folder's size is fully calculated
                # if the current folder's size is
                if currentFolder.fullSize:
                    parentFolder.fullSize = all(
                        currentFolder.fullSize
                        for currentFolder in parentFolder.descendants.folders
                    )

                # Move up one level in the folder hierarchy
                parentFolder = parentFolder.parent

    except Exception as e:
        logging.error(e)

    return folder.descendants


def CalculateFolderSize(folder: _TYPES.Folder = None, path: str = None) -> int:
    """Calculate the size of a folder (including all its contents).

    ### Parameters
    - **folder** `_TYPES.Folder`: The folder object.
    - **path** `str`: The path of the folder.

    ### Returns
    - `int`: The total size of the folder object.
    """
    assert (
        folder is not None or path is not None
    ), "Either folder or path must be provided"

    # Add the folder if the folder is not in the folders dictionary
    if folder is not None and folder.path not in Data.folders:
        Data.folders[folder.path] = folder

    elif path is not None:
        if path not in Data.folders:
            Data.folders[path] = _TYPES.Folder(path)

        # Get the folder object from the folders dictionary
        folder = Data.folders[path]

    # If the folder's descendants are empty and its size is not fully calculated, get descendants
    if folder.descendants.isEmpty() and not folder.fullSize:
        GetDescendants(folder)

    # Return the folder's size if it's already fully calculated
    if folder.fullSize:
        return folder.size

    # Initialize the folder size to 0
    folder.size = 0

    # Add the size of all files in the folder
    for file in folder.descendants.files:
        folder.size += file.size

    # Recursively calculate the size of all subfolders
    for subfolder in folder.descendants.folders:
        if not subfolder.fullSize:
            folder.size += CalculateFolderSize(subfolder)
        else:
            folder.size += subfolder.size

    # Mark the folder's size as fully calculated
    folder.fullSize = True

    return folder.size


__all__ = [
    "Data",
    "GetDescendants",
    "CalculateFolderSize",
]
