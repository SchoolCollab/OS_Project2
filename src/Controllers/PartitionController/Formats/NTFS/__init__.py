from __future__ import annotations
import Data.Types as _TYPES

import datetime as datetime

import Controllers.PartitionController.Helpers as PartitionControllerHelpers
import Controllers.PartitionController.Formats.NTFS.Helpers as NftsHelpers


class NTFS:
    """Data for a NTFS disk."""

    def __init__(self) -> None:
        self.Files: dict[int, _TYPES.File] = {}
        self.Folders: dict[int, _TYPES.Folder] = {}


Data: dict[str, NTFS] = {}
"""Data for managing NTFS disks.

This dictionary stores information about NTFS-formatted disks, where each key represents a disk identifier (e.g., drive letter or volume name), and the value is an `NTFS` object containing the disk's file and folder data.

### Structure
- **Key** `str`: The identifier for the NTFS disk (e.g., `"\\\.\C:"`, `"\\\.\D:"`).
- **Value** `NTFS`: An object containing the following attributes:
    - **Files** `dict[int, _TYPES.File]`: A dictionary mapping file IDs to `File` objects, representing all files on the disk.
    - **Folders** `dict[int, _TYPES.Folder]`: A dictionary mapping folder IDs to `Folder` objects, representing all folders on the disk.

### Example
```python
# Accessing data for the "C:" drive
ntfsDisk = Data["\\\.\C:"]
allFiles = ntfsDisk.Files
allFolders = ntfsDisk.Folders
"""


def Init(partition: _TYPES.DiskPartition) -> _TYPES.Folder:
    """Initialize the NTFS partition and parse its Master File Table (MFT) to extract file and folder information.

    ### Parameters
    - **partition** `DiskPartition`: The partition to initialize.

    ### Returns
    - `Folder`: The root folder of the NTFS partition.
    """
    assert partition.format == "NTFS", "Partition format must be NTFS."

    # Get the partition path
    partitionPath = partition.rawPath

    # Initialize the Data dictionary for this partition
    if partitionPath not in Data:
        Data[partitionPath] = NTFS()

    with open(partitionPath, "rb") as volume:
        # Get MFT offset and entry size for provided partition
        MftOffset, MftEntrySize, clusterSize = NftsHelpers.ReadVbrData(volume)

        # Get MFT size
        MftEntry0Data = PartitionControllerHelpers.ReadBytes(
            volume, MftOffset, MftEntrySize
        )
        MftSize = NftsHelpers.GetMftSize(MftEntry0Data)

        if MftSize is None:
            raise ValueError("Error reading MFT size.")

        # Calculate the number of entries in the MFT
        MftMaxEntries = MftSize // MftEntrySize
        # print(MftOffset, MftEntrySize)

        for i in range(MftMaxEntries):
            # Read each MFT entry
            entryOffset = MftOffset + i * MftEntrySize
            MftEntryData = PartitionControllerHelpers.ReadBytes(
                volume, entryOffset, MftEntrySize
            )
            # Parse the entry
            result = NftsHelpers.ParseMftEntry(volume, MftEntryData, clusterSize)

            # Skip if the result is None (e.g., deleted or invalid entry)
            if result is None:
                continue

            # Get the file or folder information
            item, parentId = result

            # Set the ID for the item
            item.id = i

            # Ensure the parent folder exists in the Folders dictionary
            if parentId not in Data[partitionPath].Folders:
                # Create a placeholder folder for the parent if it doesn't exist
                Data[partitionPath].Folders[parentId] = _TYPES.Folder(
                    0, f"Placeholder_{parentId}", datetime.datetime.now()
                )

            # Set the parent folder for the item
            item.parent = Data[partitionPath].Folders[parentId]

            # Add the item to the appropriate dictionary based on its type
            if isinstance(item, _TYPES.File):
                Data[partitionPath].Files[i] = item

                # Add the file to its parent's descendants
                Data[partitionPath].Folders[parentId].descendants.files.append(item)

            else:
                # Check if the folder is already in the Folders dictionary
                if i in Data[partitionPath].Folders:
                    # Update existing folder
                    Data[partitionPath].Folders[i].id = item.id
                    Data[partitionPath].Folders[i].name = item.name
                    Data[partitionPath].Folders[
                        i
                    ].creationDateTime = item.creationDateTime

                else:
                    # Add the new folder to the Folders dictionary
                    Data[partitionPath].Folders[i] = item

                # Add the folder to its parent's descendants
                if i != parentId:
                    Data[partitionPath].Folders[parentId].descendants.folders.append(
                        item
                    )

    # Rename the root folder to match the partition's mount point
    Data[partitionPath].Folders[5].name = partition.mountPoint

    return Data[partitionPath].Folders[5]  # Return the root folder (ID 5)


def GetItem(partitionPath: str, itemId: int) -> _TYPES.File | _TYPES.Folder | None:
    """Get an item (file or folder) by its ID from a partition.

    ### Parameters
    - **partitionPath** `str`: The path to the partition (e.g., `\\.\C:`).
    - **itemId** `int`: The ID of the item.

    ### Returns
    - `File | Folder | None`: The item (file or folder) if found, or `None` if not found.
    """
    # Check if the partition exists in the Data dictionary
    if partitionPath in Data:
        # Get the partition's data
        partitionData = Data[partitionPath]

        # Check if the item ID is valid
        if itemId in partitionData.Folders:
            return partitionData.Folders[itemId]

        elif itemId in partitionData.Files:
            return partitionData.Files[itemId]

    return None


__all__ = ["Data", "Init", "GetItem"]
