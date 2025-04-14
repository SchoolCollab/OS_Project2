from __future__ import annotations
import Data.Types as _TYPES

from Controllers.PartitionController.Formats import FAT32, NTFS

import psutil as psutil
import logging as logging


class PartitionController:
    partitions: dict[str, _TYPES.DiskPartition] = {}


Data: PartitionController = PartitionController()
"""Data for the PartitionController

### Attributes
- **partitions** `dict[str, DiskPartition]`: A dictionary of all the partitions in the disk.
"""


def GetPartitions() -> list[_TYPES.DiskPartition]:
    """Retrieve all partitions on the disk.

    ### Returns
    - `list[DiskPartition]`: A list of all partitions on the disk.
    """
    # Check if the partitions are already acquired
    if len(Data.partitions) != 0:
        return Data.partitions

    # Initialize an empty list to store partition paths
    partitionPaths = []

    try:
        # Iterate through all partitions
        for partition in psutil.disk_partitions():
            # Convert the device path (e.g., `C:\`) to the raw device format `\\.\C:`
            rawDevicePath = (
                r"\\.\  ".rstrip() + partition.device[0].replace(r"\\", "") + ":"
            )
            partitionPaths.append(rawDevicePath)

    except Exception as e:
        logging.error(f"Error retrieving partition paths: {e}")

    # Iterate through the partition paths and create DiskPartition objects
    for partitionPath in partitionPaths:
        # Get the format of the partition
        partitionFormat = IdentifyFileSystem(partitionPath)

        # Create a DiskPartition object and initialize it
        partition = _TYPES.DiskPartition(partitionFormat, partitionPath)
        if partitionFormat == "NTFS":
            partition.home = NTFS.Init(partition)
        elif partitionFormat == "FAT32":
            partition.home = FAT32.Init(partition)
        else:
            logging.warning(f"Unsupported partition format: {partitionFormat}")
            continue

        # Add the partition to the Data dictionary
        Data.partitions[partitionPath] = partition

    # Return the list of partitions
    return list(Data.partitions.values())


def IdentifyFileSystem(partitionPath: str) -> str | None:
    """Identify the file system type of a partition (FAT32 or NTFS).

    ### Parameters
    - **partitionPath** `str`: The path to the partition (e.g., `\\.\C:`).

    ### Returns
    - `str | None`: The file system type (`"FAT32"`, `"NTFS"`, or `None` if unknown).
    """
    try:
        # Read the first 512 bytes (VBR)
        with open(partitionPath, "rb") as f:
            vbr = f.read(512)

        # Check for NTFS (OEM Name at offset 0x03)
        if vbr[3:11].decode("ascii", errors="ignore").strip() == "NTFS":
            return "NTFS"

        # Check for FAT32 (File System Type at offset 0x52)
        if vbr[82:90].decode("ascii", errors="ignore").strip() == "FAT32":
            return "FAT32"

        # Unknown file system
        return "Unsupported"

    except PermissionError:
        logging.error(
            f"Permission denied when accessing {partitionPath}. Try running as administrator."
        )
        return None

    except OSError as e:
        logging.error(f"Error accessing {partitionPath}: {e}")
        return None


def GetItem(partitionPath: str, itemId: int) -> _TYPES.File | _TYPES.Folder | None:
    """Get an item (file or folder) by its ID from a partition.

    ### Parameters
    - **partitionPath** `str`: The path to the partition (e.g., `\\.\C:`).
    - **itemId** `int`: The ID of the item.

    ### Returns
    - `File | Folder | None`: The item (file or folder) if found, or `None` if not found.
    """
    # Check if the partition exists in the Data dictionary
    if partitionPath in Data.partitions:
        # Get the partition and its format
        partition = Data.partitions[partitionPath]
        format = partition.format

        #
        if format == "NTFS":
            return NTFS.GetItem(partitionPath, itemId)
        elif format == "FAT32":
            return FAT32.GetItem(partitionPath, itemId)

    logging.warning(f"Item with ID {itemId} not found in {partitionPath}.")
    return None


__all__ = ["Data", "GetPartitions", "GetItem"]
