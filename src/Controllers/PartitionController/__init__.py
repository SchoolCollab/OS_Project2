import Data.Types as _TYPES
import Controllers.PartitionController.Data.PartitionController_Types as _PARTITION_TYPES

from Controllers.PartitionController.Formats import FAT32, NTFS

import os as os
import psutil as psutil
import logging as logging


class PartitionController:
    partitions: list[_PARTITION_TYPES.DiskPartition] = []


Data: PartitionController = PartitionController()
"""Data for the PartitionController

### Attributes
- **partitions** `dict[str, DiskPartition]`: A dictionary of all the partitions in the disk.
"""


def GetPartitions() -> list[_PARTITION_TYPES.DiskPartition]:
    """Retrieve all partitions on the disk.

    ### Returns
    - `list[DiskPartition]`: A list of all partitions on the disk.
    """
    # Check if the partitions are already acquired
    if len(Data.partitions) != 0:
        return Data.partitions

    try:
        # Get the partitions
        for partition in psutil.disk_partitions():
            Data.partitions.append(_PARTITION_TYPES.DiskPartition(partition))

    except Exception as e:
        raise e

    return Data.partitions


def IsFile(filePath: str) -> bool:
    """Check if a given path points to a file.

    ### Parameters
    - **filePath** `str`: The path to check.

    ### Returns
    - `bool`: `True` if the path points to a file, `False` otherwise.
    """
    return os.path.isfile(filePath)


def IsDir(dirPath: str) -> bool:
    """Check if a given path points to a directory.

    ### Parameters
    - **dirPath** `str`: The path to check.

    ### Returns
    - `bool`: `True` if the path points to a directory, `False` otherwise.
    """
    return os.path.isdir(dirPath)


def ListDirContents(path: str) -> tuple[list[str], list[str]]:
    """List the contents of a directory, including files and sub-folders.

    ### Parameters
    - **path** `str`: The path of the directory to list.

    ### Returns
    - `tuple[list[str], list[str]]`: A tuple containing two lists:
        - The first list contains the paths of sub-folders.
        - The second list contains the paths of files.
    """
    assert IsDir(path), ValueError(f"The provided path is not a directory: {path}")

    dirPaths: list[str] = []
    filePaths: list[str] = []

    try:
        for entry in os.scandir(path):
            if entry.is_dir():
                dirPaths.append(entry.path)
            elif entry.is_file():
                filePaths.append(entry.path)

    except Exception as e:
        logging.error(f"Error listing directory contents for {path}: {e}")

    return dirPaths, filePaths
