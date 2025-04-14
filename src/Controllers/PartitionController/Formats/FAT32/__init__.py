from __future__ import annotations
import Data.Types as _TYPES

import io as io
import logging as logging
import datetime as datetime

import Controllers.PartitionController.Helpers as PartitionControllerHelpers
import Controllers.PartitionController.Formats.FAT32.Helpers as Fat32Helpers


class FAT32:
    """Data for a FAT32 disk."""

    def __init__(self) -> None:
        self.itemCount = 0
        self.files: dict[int, _TYPES.File] = {}
        self.folders: dict[int, _TYPES.Folder] = {}


Data: dict[str, FAT32] = {}
"""Data for managing FAT32 disks.

This dictionary stores information about FAT32-formatted disks, where each key represents a disk identifier (e.g., drive letter or volume name), and the value is a `FAT32` object containing the disk's file and folder data.

### Structure
- **Key** `str`: The identifier for the FAT32 disk (e.g., `"\\.\C:"`, `"\\.\D:"`).
- **Value** `FAT32`: An object containing the following attributes:
    - **itemCount** `int`: The total number of items (files and folders) on the disk.
    - **files** `dict[int, _TYPES.File]`: A dictionary mapping file IDs to `File` objects, representing all files on the disk.
    - **folders** `dict[int, _TYPES.Folder]`: A dictionary mapping folder IDs to `Folder` objects, representing all folders on the disk.

### Example
```python
# Accessing data for the "C:" drive
fat32Disk = Data["\\\.\C:"]
allFiles = fat32Disk.files
allFolders = fat32Disk.folders
"""


def Init(partition: _TYPES.DiskPartition) -> _TYPES.Folder | None:
    """Initialize the FAT32 partition and parse its file system to extract file and folder information."""
    assert partition.format == "FAT32", "Partition format must be FAT32."

    # Get the partition path
    partitionPath = partition.rawPath

    # Initialize the Data dictionary for this partition
    if partitionPath not in Data:
        Data[partitionPath] = FAT32()

    with open(partitionPath, "rb") as volume:
        # Parse the boot sector
        bootSector = Fat32Helpers.ParseBootSector(volume)

        # Extract data from the boot sector
        bytesPerSector = bootSector["bytesPerSector"]
        sectorsPerCluster = bootSector["sectorsPerCluster"]
        reservedSectors = bootSector["reservedSectors"]
        numFats = bootSector["numFats"]
        sectorsPerFat = bootSector["sectorsPerFat"]
        rootCluster = bootSector["rootCluster"]

        logging.debug(f"Root cluster: {rootCluster}")

        # Calculate offsets and sizes
        fatOffset = reservedSectors * bytesPerSector
        fatSize = sectorsPerFat * bytesPerSector
        dataRegionOffset = (reservedSectors + numFats * sectorsPerFat) * bytesPerSector
        clusterSize = sectorsPerCluster * bytesPerSector

        # Read the FAT
        fatData = PartitionControllerHelpers.ReadBytes(volume, fatOffset, fatSize)

        # Read the root directory entries
        rootClusters = Fat32Helpers.ReadClusterChain(fatData, rootCluster)
        rootEntries = Fat32Helpers.ReadDirectoryEntries(
            volume, rootClusters, dataRegionOffset, clusterSize
        )

        # Initialize the root folder
        Data[partitionPath].folders[0] = _TYPES.Folder(
            0,
            partition.mountPoint,
            None,
        )

        # Update the item count
        Data[partitionPath].itemCount += 1

        # Remove the first entry as it is the "." entry
        rootEntries = [
            entry for entry in rootEntries if entry["name"] not in (".", "..")
        ]

        # Process the root directory entries
        for entry in rootEntries:
            item = ProcessEntry(
                volume, fatData, entry, dataRegionOffset, clusterSize, partitionPath
            )

            if item is not None:
                # Append item to the root folder descendants
                if isinstance(item, _TYPES.File):
                    Data[partitionPath].folders[0].descendants.files.append(item)
                else:
                    Data[partitionPath].folders[0].descendants.folders.append(item)

        return Data[partitionPath].folders[0]  # Return the root folder

    return None


def ProcessEntry(
    volume: io.BufferedReader,
    fatData: bytes,
    entry: dict,
    dataRegionOffset: int,
    clusterSize: int,
    partitionPath: str,
) -> _TYPES.File | _TYPES.Folder | None:
    """Process a directory entry and add it to the FAT32 data structure.

    ### Parameters
    - **volume** `BufferedReader`: The volume for the partition.
    - **fatData** `bytes`: The FAT table data.
    - **entry** `dict`: The directory entry to process.
    - **dataRegionOffset** `int`: The offset of the data region.
    - **clusterSize** `int`: The size of a cluster in bytes.
    - **partitionPath** `str`: The path of the partition.

    ### Returns
    - `File | Folder | None`: The processed file or folder, or `None` if not applicable.
    """
    if entry["isDir"]:
        # Get the current id and update the item count
        itemId = Data[partitionPath].itemCount
        Data[partitionPath].itemCount += 1

        # Add the folder to the partition's folder dictionary
        Data[partitionPath].folders[itemId] = _TYPES.Folder(
            itemId,
            entry["name"],
            entry["creationDateTime"],
        )

        if entry["cluster"] >= 2:
            # Get the subdirectory entries
            clusters = Fat32Helpers.ReadClusterChain(fatData, entry["cluster"])
            subEntries = Fat32Helpers.ReadDirectoryEntries(
                volume, clusters, dataRegionOffset, clusterSize
            )

            # Recursively process subdirectories
            for subEntry in subEntries:
                if subEntry["name"] not in (".", ".."):
                    # Process the subdirectory entry
                    item = ProcessEntry(
                        volume,
                        fatData,
                        subEntry,
                        dataRegionOffset,
                        clusterSize,
                        partitionPath,
                    )

                    if item == None:
                        continue

                    # Append item to the current folder descendants
                    if isinstance(item, _TYPES.File):
                        Data[partitionPath].folders[itemId].descendants.files.append(
                            item
                        )
                    else:
                        Data[partitionPath].folders[itemId].descendants.folders.append(
                            item
                        )

        return Data[partitionPath].folders[itemId]

    elif entry["isFile"]:
        # Get the current id and update the item count
        itemId = Data[partitionPath].itemCount
        Data[partitionPath].itemCount += 1

        # Add the file to the partition's file dictionary
        Data[partitionPath].files[itemId] = _TYPES.File(
            itemId,
            entry["name"],
            entry["size"],
            entry["creationDateTime"],
            (
                Fat32Helpers.ExtractTxtContent(
                    volume, fatData, entry, dataRegionOffset, clusterSize
                )
                if entry["name"].lower().endswith(".txt")
                else None
            ),
        )

        return Data[partitionPath].files[itemId]

    logging.warning(
        f"Unknown entry type for {entry['name']} in partition {partitionPath}."
    )

    return None


def GetItem(partitionPath: str, itemId: int) -> _TYPES.File | _TYPES.Folder | None:
    """Get an item (file or folder) by its ID from a partition.

    ### Parameters
    - **partitionPath** `str`: The path to the partition (e.g., `
    \\\.\C:`).
    - **itemId** `int``: The ID of the item.

    ### Returns
    - `File | Folder | None`: The item (file or folder) if found, or `None` if not found.
    """
    # Check if the partition exists in the Data dictionary
    if partitionPath in Data:
        # Get the partition's data
        partitionData = Data[partitionPath]

        # Check if the item ID is valid
        if itemId in partitionData.folders:
            return partitionData.folders[itemId]

        elif itemId in partitionData.files:
            return partitionData.files[itemId]

    return None


__all__ = ["Data", "Init", "GetItem"]
