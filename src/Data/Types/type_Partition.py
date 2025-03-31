from __future__ import annotations

import Data.Types.type_Time as Time

from enum import Enum
from psutil._common import sdiskpart

import os as os
import datetime as datetime
import psutil as psutil


class DiskFormat(Enum):
    """An enumeration to represent the format of a disk.

    ### Values
    - **FAT32**: FAT32 format
    - **exFAT**: exFAT format
    - **NTFS**: NTFS format
    - **APFS**: APFS format
    - **HFSP**: HFSP format
    - **ext2**: ext2 format
    - **ext3**: ext3 format
    - **ext4**: ext4 format
    """

    # Cross-platform
    FAT32 = "fat32"
    exFAT = "exfat"
    # Windows
    NTFS = "ntfs"
    # MacOS
    APFS = "apfs"
    HFSP = "hfsp"
    # Linux
    ext2 = "ext2"
    ext3 = "ext3"
    ext4 = "ext4"


class File:
    """A class to represent a file.

    ### Attributes
    - **name** `str`: The name of the file.
    - **extension** `str`: The extension of the file.
    - **path** `str`: The path of the file.
    - **size** `int`: The size of the file in bytes.
    - **creationDateTime** `_TYPES.DateTime`: The date and time the file was created.
    - **parent** `Folder`: The parent folder of the file.
    """

    def __init__(self, filepath: str, parentFolder: Folder = None):
        """Constructs all the necessary attributes for the file object.

        ### Parameters
        - **filepath** `str`: The file path.
        - **parentFolder** `Folder`, optional): The parent folder of the file.
        """
        assert isinstance(filepath, str), TypeError("Filepath must be a string.")
        assert isinstance(parentFolder, Folder) or parentFolder is None, TypeError(
            "Parent folder must be a Folder object."
        )

        # Check if the file exists
        if not os.path.exists(filepath) or not os.path.isfile(filepath):
            raise FileNotFoundError(f"{filepath} is not a file")

        self.name: str = filepath.split("/")[-1].split("\\")[-1].split(".")[0]
        self.extension: str = filepath.split(".")[-1]
        self.path: str = filepath
        self.size: int = os.path.getsize(filepath)

        # Get the creation datetime of the file
        if os.name == "nt":  # Windows
            creationTime = os.path.getctime(filepath)
        else:  # macOS and Linux
            stat = os.stat(filepath)
            try:
                creationTime = stat.st_birthtime
            except AttributeError:
                # Fallback to last metadata change time if birth time is not available
                creationTime = stat.st_mtime

        self.creationDateTime = Time.DateTime(
            datetime.datetime.fromtimestamp(creationTime)
        )
        self.parent: Folder = parentFolder


class Descendants:
    """A class to represent the descendants of a folder.

    ### Attributes
    - **files** `list[File]`: The files in the folder.
    - **folders** `list[Folder]`: The sub-folders in the folder.
    """

    def __init__(self):
        """Constructs all the necessary attributes for the descendants object."""
        self.files: list[File] = []
        self.folders: list[Folder] = []

    def __len__(self) -> int:
        """Get the number of descendants.

        ### Returns
        - **int**: The number of descendants.
        """
        return len(self.files) + len(self.folders)

    def isEmpty(self) -> bool:
        """Check if the descendants are empty.

        ### Returns
        - **bool**: `True` if the descendants are empty, `False` otherwise.
        """
        return len(self.files) == 0 and len(self.folders) == 0

    def __iter__(self) -> iter[tuple[list[File], list[Folder]]]:
        """Get the iterator of the descendants.

        ### Returns
        - **iter**: The iterator of the descendants.
        """
        return iter((self.files, self.folders))


class Folder:
    """A class to represent a folder.

    ### Attributes
    - **name** `str`: The name of the folder.
    - **path** `str`: The path of the folder.
    - **size** `int`: The size of the folder in bytes.
    - **fullSize** `bool`: Whether the size of the folder is fully calculated.
    - **creationDateTime** `_TYPES.DateTime`: The date and time the folder was created.
    - **parent** `Folder`: The parent folder of the folder.
    - **descendants** `Descendants`: The files and sub-folders in the folder.
    """

    def __init__(self, dirpath: str, parentFolder: Folder = None):
        """Constructs all the necessary attributes for the folder object.

        ### Parameters
        - **dirpath** `str`: The folder path.
        - **parentFolder** `Folder`, optional): The parent folder of the folder.
        """
        assert isinstance(dirpath, str), TypeError("Dirpath must be a string.")
        assert isinstance(parentFolder, Folder) or parentFolder is None, TypeError(
            "Parent folder must be a Folder object."
        )

        # Check if the folder exists
        if not os.path.exists(dirpath) or not os.path.isdir(dirpath):
            raise FileNotFoundError(f"{dirpath} is not a folder")

        self.name: str = dirpath.split("/")[-1].split("\\")[-1]
        self.path: str = dirpath
        self.size: int = 0
        self.fullSize: bool = False

        # Get the creation datetime of the folder
        if os.name == "nt":  # Windows
            creationTime = os.path.getctime(dirpath)
        else:  # macOS and Linux
            stat = os.stat(dirpath)
            try:
                creationTime = stat.st_birthtime
            except AttributeError:
                # Fallback to last metadata change time if birth time is not available
                creationTime = stat.st_mtime

        self.creationDateTime = Time.DateTime(
            datetime.datetime.fromtimestamp(creationTime)
        )
        self.parent: Folder = parentFolder
        self.descendants: Descendants = Descendants()


class DiskPartition:
    """A class to represent a partition.

    ### Attributes
    - **device** `str`: The device name of the partition.
    - **formatStype** `DiskFormat`: The format of the partition.
    - **mountPoint** `str`: The mount point of the partition.
    - **mountOptions** `str`: The mount options of the partition.
    - **home** `Folder`: The home folder of the partition.
    """

    def __init__(self, partition: sdiskpart):
        """Constructs all the necessary attributes for the partition object.

        ### Parameters
        - **partition** `sdiskpart`: The partition object from psutil.
        """
        assert isinstance(partition, sdiskpart), TypeError(
            "Partition must be a psutil._common.sdiskpart object."
        )

        self.device: str = partition.device
        self.formatStype: DiskFormat = DiskFormat(partition.fstype.lower())
        self.mountPoint: str = partition.mountpoint
        self.mountOptions: str = partition.opts
        self.home: Folder = None


__all__ = ["DiskFormat", "DiskPartition", "File", "Folder", "Descendants"]
