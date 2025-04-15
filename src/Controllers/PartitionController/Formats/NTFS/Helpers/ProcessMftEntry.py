from __future__ import annotations
import Data.Types as _TYPES

import io as io
import struct as struct
import logging as logging
from datetime import datetime

import Controllers.PartitionController.Helpers as PartitionControllerHelpers


def ParseMftEntry(
    volume: io.BufferedReader,
    mftEntryData: bytes,
    clusterSize: int,
) -> tuple[_TYPES.Folder | _TYPES.File, int] | None:
    """Parse an MFT entry to extract file or folder metadata.

    ### Parameters
    - **volume** `BufferedReader`: The volume to read from.
    - **mftEntryData** `bytes`: The raw bytes of the MFT entry.
    - **clusterSize** `int`: The size of a cluster in bytes.

    ### Returns
    - `tuple[Folder | File, int] | None`: A tuple containing a `Folder` or `File` object and its parent's ID, or `None` if parsing fails.
    """
    # Check for a valid MFT entry signature ("FILE")
    if mftEntryData[0:4] != b"FILE":
        return None

    # Initialize metadata dictionary
    metadata = {
        "isDirectory": False,
        "name": None,
        "size": 0,
        "creationDateTime": None,
        "data": None,
        "dataRuns": None,
        "parent": None,
    }

    # Get the offset to the first attribute in the MFT entry
    firstAttrOffset = struct.unpack_from("<H", mftEntryData, 0x14)[0]
    currentOffset = firstAttrOffset

    # Iterate through the attributes in the MFT entry
    while currentOffset < len(mftEntryData):
        # Read the attribute type (4 bytes)
        attributeType = struct.unpack_from("<I", mftEntryData, currentOffset)[0]

        # Check if we've reached the end of the attributes
        if attributeType == 0xFFFFFFFF:
            break

        # Read the length of the current attribute (4 bytes)
        attributeLength = struct.unpack_from("<I", mftEntryData, currentOffset + 4)[0]

        # Ensure the attribute length is valid
        if attributeLength == 0:
            logging.warning(
                f"Invalid attribute length at offset {currentOffset}: {attributeLength}"
            )
            continue

        # Read the content size and offset within the attribute
        contentSize = struct.unpack_from("<I", mftEntryData, currentOffset + 16)[0]
        contentOffset = (
            struct.unpack_from("<H", mftEntryData, currentOffset + 20)[0]
            + currentOffset
        )

        # Extract the content of the attribute
        content = mftEntryData[contentOffset : contentOffset + contentSize]

        # Process the attribute based on its type
        if attributeType == 0x10:  # STANDARD_INFORMATION
            metadata["creationDateTime"] = extractCreationTime(content)

        elif attributeType == 0x30:  # FILE_NAME
            fileNameMetadata = extractFileNameMetadata(content)
            if fileNameMetadata:
                metadata.update(fileNameMetadata)

        elif attributeType == 0x80:  # $DATA
            isNonResident = struct.unpack_from("<B", mftEntryData, currentOffset + 8)[0]

            # Resident data
            if isNonResident == 0:
                # Read the size and offset of the data
                dataSize = struct.unpack_from("<I", mftEntryData, currentOffset + 16)[0]
                dataOffset = (
                    struct.unpack_from("<H", mftEntryData, currentOffset + 20)[0]
                    + currentOffset
                )

                # Extract the data from the MFT entry
                data = mftEntryData[dataOffset : dataOffset + dataSize]

                # Check if the data is a Zone Transfer (Zone Transfer Protocol)
                if not b"[ZoneTransfer]" in data:
                    metadata["data"] = data

                    # Move to next offset
                    currentOffset += attributeLength
                    continue

            # Non-resident data, the header contains the data runs and

            # Get the data runs
            dataRunsOffset = (
                struct.unpack_from("<H", mftEntryData, currentOffset + 32)[0]
                + currentOffset
            )
            metadata["dataRuns"] = mftEntryData[
                dataRunsOffset : currentOffset + attributeLength
            ]

            if isNonResident == 1:
                # Use the real file size field located at offset 48 (0x30)
                metadata["size"] = struct.unpack_from(
                    "<Q", mftEntryData, currentOffset + 0x30
                )[0]

        # Move to the next attribute
        currentOffset += attributeLength

    # Return a Folder or File object based on the metadata
    if metadata["name"] != None:
        if metadata["isDirectory"]:
            return (
                _TYPES.Folder(
                    0,
                    metadata["name"],
                    (
                        metadata["creationDateTime"]
                        if metadata["creationDateTime"]
                        else datetime.now()
                    ),
                ),
                metadata["parent"],
            )
        else:
            # Get the file data if available
            content: bytes = None

            if metadata["name"].endswith(".txt"):
                if metadata.get("data"):
                    content = metadata["data"]
                elif metadata.get("dataRuns"):
                    content = parseDataRuns(
                        volume, metadata["dataRuns"], clusterSize, metadata["size"]
                    )

            # If the content is not None, decode it to a string
            # and remove null characters
            if content is not None:
                content = content.decode("utf-8", errors="ignore").replace("\x00", "")

            return (
                _TYPES.File(
                    0,
                    metadata["name"],
                    metadata["size"],
                    (
                        metadata["creationDateTime"]
                        if metadata["creationDateTime"]
                        else datetime.now()
                    ),
                    content,
                ),
                metadata["parent"],
            )

    return None


def extractCreationTime(attributeContent: bytes) -> datetime | None:
    """Extract the creation time from the STANDARD_INFORMATION attribute.

    ### Parameters
    - **attributeContent** `bytes`: The content of the STANDARD_INFORMATION attribute.

    ### Returns
    - `datetime | None`: The creation time as a **datetime** object, or `None` if parsing fails.
    """
    try:
        # Extract the 64-bit Windows filetime value (at offset 0x00)
        filetime = struct.unpack_from("<Q", attributeContent, 0x00)[0]

        # Windows filetime represents the number of 100-nanosecond intervals since January 1, 1601 (UTC)
        FILETIME_EPOCH = 116444736000000000  # January 1, 1970 as filetime
        HUNDREDS_OF_NANOSECONDS = (
            10000000  # Number of 100-nanosecond intervals in a second
        )

        # Convert filetime to a Unix timestamp
        unixTimestamp = (filetime - FILETIME_EPOCH) / HUNDREDS_OF_NANOSECONDS

        # Convert the Unix timestamp to a datetime object
        return datetime.fromtimestamp(unixTimestamp)

    except Exception as e:
        logging.error(f"Error parsing creation time: {e}")
        return None


def extractFileNameMetadata(attributeContent: bytes) -> dict[str, any] | None:
    """Extract metadata from the FILE_NAME attribute.

    ### Parameters
    - **attributeContent** `bytes`: The content of the FILE_NAME attribute.

    ### Returns
    - `dict[str, any] | None`: A dictionary containing file metadata:
        - **parent** `int`: The parent MFT entry ID.
        - **name** `str`: The file or folder name.
        - **isDirectory** `bool`: Whether the entry is a directory.
        - **size** `int`: The size of the file in bytes.
    """
    try:
        # Extract the parent MFT entry ID (6 bytes, masked from 8 bytes at offset 0x00)
        parentMftId = (
            struct.unpack_from("<Q", attributeContent, 0x00)[0] & 0xFFFFFFFFFFFF
        )

        # Extract the real size of the file (8 bytes at offset 0x30)
        fileSize = struct.unpack_from("<Q", attributeContent, 0x30)[0]

        # Extract the flags (4 bytes at offset 0x38) to determine if it's a directory
        flags = struct.unpack_from("<I", attributeContent, 0x38)[0]
        isDirectory = (flags & 0x10000000) != 0  # Check the directory flag

        # Extract the length of the file name (1 byte at offset 0x40)
        nameLength = struct.unpack_from("<B", attributeContent, 0x40)[0]

        # Extract the file name (UTF-16LE encoded, starting at offset 0x42)
        fileName = attributeContent[0x42 : 0x42 + nameLength * 2].decode("utf-16le")

        # Return the parsed metadata as a dictionary
        return {
            "parent": parentMftId,
            "name": fileName,
            "isDirectory": isDirectory,
            "size": fileSize,
        }

    except Exception as e:
        logging.error(f"Error parsing FILE_NAME attribute: {e}")
        return None


def parseDataRuns(
    volume: io.BufferedReader, dataRuns: bytes, clusterSize: int, fileSize: int
) -> bytes:
    """
    Parse the data runs from a non-resident $DATA attribute.

    ### Parameters
    - **volume** `BufferedReader`: The volume to read from.
    - **dataRuns** `bytes`: The raw bytes of the data runs.
    - **clusterSize** `int`: The size of a cluster in bytes.
    - **fileSize** `int`: The actual size of the file in bytes.

    ### Returns
    - `bytes`: The concatenated data read from the volume based on the data runs.
    """
    # Initialize an empty byte array to store the data
    data: bytes = b""

    # Initialize the current index for reading data runs
    currentIndex = 0
    # Tracks the previous cluster offset for relative addressing
    previousOffset = 0

    # Track how many bytes are left to read
    bytesRemaining = fileSize

    try:
        while currentIndex < len(dataRuns):
            header = dataRuns[currentIndex]
            if header == 0x00:  # End of data runs
                break

            # Extract the sizes of the length and offset fields
            lengthSize = header & 0x0F
            offsetSize = (header >> 4) & 0x0F
            currentIndex += 1

            # Ensure the sizes are valid
            if currentIndex + lengthSize + offsetSize > len(dataRuns):
                logging.error("Data run header exceeds available data length.")
                break

            # Extract the length (number of clusters in the run)
            runLength = int.from_bytes(
                dataRuns[currentIndex : currentIndex + lengthSize], byteorder="little"
            )
            currentIndex += lengthSize

            # Extract the offset (relative to the previous run)
            rawOffset = int.from_bytes(
                dataRuns[currentIndex : currentIndex + offsetSize],
                byteorder="little",
                signed=True,
            )
            currentIndex += offsetSize

            # Calculate the absolute cluster offset
            previousOffset += rawOffset

            # Read the data from the volume
            for i in range(runLength):
                # Calculate the absolute offset in bytes
                absoluteOffset = (previousOffset + i) * clusterSize

                # Determine how many bytes to read (don't exceed file size)
                bytesToRead = min(clusterSize, bytesRemaining)

                # Read the data from the volume
                clusterData = PartitionControllerHelpers.ReadBytes(
                    volume, absoluteOffset, bytesToRead
                )

                # Append the cluster data to the result
                data += clusterData

                # Decrease the remaining bytes to read
                bytesRemaining -= bytesToRead

                # Stop reading if we've read the entire file
                if bytesRemaining <= 0:
                    break

            # Stop processing further data runs if we've read the entire file
            if bytesRemaining <= 0:
                break

    except Exception as e:
        logging.error(f"Error parsing data runs: {e}")

    return data


__all__ = [
    "ParseMftEntry",
]
