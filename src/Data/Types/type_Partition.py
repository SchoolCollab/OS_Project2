from __future__ import annotations
import Data.Types.type_Time as Time

import os as os
import datetime as datetime

import Controllers.PartitionController as PartitionController


class File:
    """A class to represent a file.

    ### Attributes
    - **id** `int`: The ID of the file.
    - **name** `str`: The name of the file.
    - **extension** `str`: The extension of the file.
    - **size** `int`: The size of the file in bytes.
    - **creationDateTime** `DateTime`: The date and time the file was created.
    - **content** `str`: The content of the file.
    - **parent** `Folder`: The parent folder of the file.
    """

    def __init__(
        self,
        id: int,
        fileName: str,
        fileSize: int,
        creationDateTime: datetime.datetime,
        content: str = None,
        parentFolder: Folder = None,
    ):
        """Constructs all the necessary attributes for the file object.

        ### Parameters
        - **id** `int`: The ID of the file.
        - **fileName** `str`: The name of the file.
        - **fileSize** `int`: The size of the file in bytes.
        - **creationDateTime** `datetime.datetime`: The date and time the file was created.
        - **content** `str`: The content of the file.
        - **parentFolder** `Folder`: The parent folder of the file.
        """
        self.id = id

        self.name: str = fileName.split(".")[0]
        self.extension: str = fileName.split(".")[-1]

        self.size: int = fileSize
        self.creationDateTime = Time.DateTime(creationDateTime)

        self.content: str = content

        self.parent: Folder = parentFolder


class Folder:
    """A class to represent a folder.

    ### Attributes
    - **id** `int`: The ID of the folder.
    - **name** `str`: The name of the folder.
    - **creationDateTime** `DateTime`: The date and time the folder was created.
    - **parent** `Folder`: The parent folder of the folder.
    - **descendants** `Descendants`: The files and sub-folders in the folder.
    """

    def __init__(
        self,
        id: int,
        dirName: str,
        creationDateTime: datetime.datetime,
        parentFolder: Folder = None,
    ):
        """Constructs all the necessary attributes for the folder object.

        ### Parameters
        - **id** `int`: The ID of the folder.
        - **dirName** `str`: The name of the folder.
        - **creationDateTime** `datetime.datetime`: The date and time the folder was created.
        - **parentFolder** `Folder`, optional): The parent folder of the folder.
        """
        self.id = id

        self.name: str = dirName

        self.size: int = 0
        self.fullSize: bool = False

        self.creationDateTime = Time.DateTime(creationDateTime)

        self.parent: Folder = parentFolder
        self.descendants: Descendants = Descendants()


class DiskPartition:
    """A class to represent a partition.

    ### Attributes
    - **format** `str`: The format of the partition.
    - **rawPath** `str`: The raw path of the partition.
    - **mountPoint** `str`: The mount point of the partition.
    - **home** `Folder`: The home folder of the partition.
    """

    def __init__(self, format: str, rawPath: str):
        """Constructs all the necessary attributes for the partition object.

        ### Parameters
        - **format** `str`: The format of the partition.
        - **rawPath** `str`: The raw path of the partition.
        """
        self.format: str = format

        self.rawPath: str = rawPath
        self.mountPoint: str = rawPath.replace("\\\\.\\", "")

        self.home: Folder = None


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
        - `int`: The number of descendants.
        """
        return len(self.files) + len(self.folders)

    def __iter__(self) -> iter[tuple[list[File], list[Folder]]]:
        """Get the iterator of the descendants.

        ### Returns
        - `iter`: The iterator of the descendants.
        """
        return iter((self.files, self.folders))

    def isEmpty(self) -> bool:
        """Check if the descendants are empty.

        ### Returns
        - `bool`: **True** if the descendants are empty, **False** otherwise.
        """
        return len(self.files) == 0 and len(self.folders) == 0


__all__ = ["File", "Folder", "DiskPartition", "Descendants"]
