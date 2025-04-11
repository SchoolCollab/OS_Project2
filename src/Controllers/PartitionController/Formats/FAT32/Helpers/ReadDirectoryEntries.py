from __future__ import annotations

import io as io
import re as re
import logging as logging
from datetime import datetime

import Controllers.PartitionController.Helpers as PartitionControllerHelpers


def ReadDirectoryEntries(
    volume: io.BufferedReader,
    clusters: list[int],
    dataRegionOffset: int,
    clusterSize: int,
) -> list[dict]:
    """Read directory entries from a list of clusters.

    ### Parameters
    - **volume** `BufferedReader`: The volume for the partition.
    - **clusters** `list[int]`: The list of clusters.
    - **dataRegionOffset** `int`: The offset of the data region.
    - **clusterSize** `int`: The size of a cluster in bytes.

    ### Returns
    - `list[dict]`: A list of directory entries, each dictionary includes:
        - **name** `str`: The name of the file or directory.
        - **isDir** `bool`: Whether the entry is a directory.
        - **isFile** `bool`: Whether the entry is a file.
        - **cluster** `int`: The starting cluster of the file or directory.
        - **size** `int`: The size of the file in bytes.
        - **creationDateTime** `datetime`: The creation date and time of the file or directory.
    """
    # Initialize an empty list to store directory entries
    entries = []

    for cluster in clusters:
        # Read the cluster data
        clusterOffset = dataRegionOffset + (cluster - 2) * clusterSize
        clusterData = PartitionControllerHelpers.ReadBytes(
            volume, clusterOffset, clusterSize
        )

        # Initialize an empty list to store long file name parts
        lfnParts = []

        # Parse directory entries from the cluster data
        for i in range(0, len(clusterData), 32):  # Each directory entry is 32 bytes
            entry = clusterData[i : i + 32]

            if entry[0] == 0x00:  # No more entries
                break
            if entry[0] == 0xE5:  # Deleted entry
                continue

            # Handle Long File Name (LFN) entries
            if entry[11] == 0x0F:
                namePart = entry[1:11] + entry[14:26] + entry[28:32]

                try:
                    part = namePart.decode("utf-16le", errors="ignore")
                    lfnParts.insert(
                        0, part
                    )  # Insert at the beginning to preserve order

                except UnicodeDecodeError:
                    logging.error(f"Failed to decode LFN part: {namePart.hex()}")

                # Read the next entry
                continue

            # Skip corrupted or invalid entries
            if len(entry) < 32:
                break

            # Use LFN if available, otherwise use the short name
            if lfnParts:
                name = CleanLFNName(lfnParts)
                lfnParts = []  # Reset LFN parts after use
            else:
                name = ParseFileName(entry)

            # Parse standard directory entry

            # Check if the entry is a directory or file
            isDir = (entry[11] & 0x10) != 0
            isFile = not isDir and (entry[11] & 0x08) == 0

            # Parse the starting cluster and item's size
            cluster = int.from_bytes(entry[26:28], "little") | (
                int.from_bytes(entry[20:22], "little") << 16
            )
            size = int.from_bytes(entry[28:32], "little")

            # Parse the creation date and time
            creationDateTime = DecodeTimeDate(entry)

            entries.append(
                {
                    "name": name,
                    "isDir": isDir,
                    "isFile": isFile,
                    "cluster": cluster,
                    "size": size,
                    "creationDateTime": creationDateTime,
                }
            )

    return entries


def CleanLFNName(rawParts: list[str]) -> str:
    """Clean and combine parts of a long file name.

    ### Parameters
    - **rawParts** `list[str]`: The raw parts of the long file name.

    ### Returns
    - `str`: The cleaned and combined long file name.
    """
    name = "".join(rawParts)
    name = name.replace("\xff", "").replace("\xffff", "").replace("\x00", "")
    name = re.sub(r"[^\x20-\x7E]", "", name)

    return name.strip()


def ParseFileName(entry: bytes):
    """Parse the file name from a directory entry.

    ### Parameters
    - **entry** `bytes`: The raw directory entry.

    ### Returns
    - `str`: The parsed file name.
    """
    name = entry[0:8].decode("ascii", errors="ignore").strip()
    extention = entry[8:11].decode("ascii", errors="ignore").strip()

    return (f"{name}.{extention}" if extention else name).strip()


def DecodeTimeDate(entry: bytes) -> datetime:
    """Decode the creation time and date from a directory entry.

    ### Parameters
    - **entry** `bytes`: The raw directory entry.

    ### Returns
    - `datetime`: The decoded creation time and date.
    """
    timeRaw = int.from_bytes(entry[14:16], "little")
    dateRaw = int.from_bytes(entry[16:18], "little")

    # Decode time
    hours = (timeRaw >> 11) & 0x1F  # timeRaw // 2048
    minutes = (timeRaw >> 5) & 0x3F  # (timeRaw % 2048) // 32
    seconds = (timeRaw & 0x1F) * 2  # (timeRaw % 32) * 2

    # Decode date
    year = ((dateRaw >> 9) & 0x7F) + 1980  # (dateRaw // 512) + 1980
    month = (dateRaw >> 5) & 0x0F  # (dateRaw % 512) // 32
    day = dateRaw & 0x1F  # dateRaw % 32

    return datetime(year, month, day, hours, minutes, seconds)


__all__ = [
    "ReadDirectoryEntries",
]
