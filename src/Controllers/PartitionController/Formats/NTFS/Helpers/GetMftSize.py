import struct


def GetMftSize(mftEntryData: bytes) -> int | None:
    """Retrieve the allocated size of the Master File Table (MFT).

    ### Parameters
    - **mftEntryData** `bytes`: The raw binary data of the first MFT entry.

    ### Returns
    - `int | None`: The allocated size of the MFT in bytes, or `None` if not found.
    """
    # Get the offset to the first attribute in the MFT entry
    firstAttributeOffset = struct.unpack_from("<H", mftEntryData, 0x14)[0]

    # Iterate through the attributes in the MFT entry
    currentOffset = firstAttributeOffset
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
            break

        # Check if the attribute is $DATA and non-resident
        isNonResident = struct.unpack_from("<B", mftEntryData, currentOffset + 8)[0]
        if attributeType == 0x80 and isNonResident == 1:  # $DATA non-resident
            # Read the allocated size (8 bytes)
            allocatedSize = struct.unpack_from(
                "<Q", mftEntryData, currentOffset + 0x30
            )[0]

            return allocatedSize

        # Move to the next attribute
        currentOffset += attributeLength

    # Return None if no allocated size is found
    return None


__all__ = {
    "GetMftSize",
}
