import Data.Types as _TYPES

from enum import Enum
from psutil._common import sdiskpart


class DiskFormat(Enum):
    """An enumeration to represent the format of a disk.

    ### Values
    - **FAT16**: FAT16 format
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
    FAT16 = "fat16"
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
        self.home: _TYPES.Folder = None


__all__ = [
    "DiskFormat",
    "DiskPartition",
]
