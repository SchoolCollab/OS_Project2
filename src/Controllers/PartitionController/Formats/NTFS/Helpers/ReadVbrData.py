import io as io
import struct as struct

from Controllers.PartitionController.Helpers import ReadBytes


def ReadVbrData(volume: io.BufferedReader) -> tuple[int, int]:
    """Read the Volume Boot Record (VBR) of an NTFS partition.

    The VBR contains metadata about the file system, such as cluster size and MFT offset.

    ### Parameters
    - **volume** `BufferedReader`: The Master File Table (MFT) buffer.

    ### Returns
    - `tuple[int, int]`: A tuple containing the MFT offset and the MFT entry size.
        - **mftOffset** `int`: The offset of the MFT in bytes.
        - **mftEntrySize** `int`: The size of an MFT entry in bytes.
    """
    # Read the first 512 bytes of the VBR
    vbrTable = ReadBytes(volume, 0, 512)

    # Unpack the VBR data

    # Get the bytes per sector and sectors per cluster
    bytesPerSector = struct.unpack_from("<H", vbrTable, 11)[0]
    sectorsPerCluster = struct.unpack_from("<B", vbrTable, 13)[0]

    # Get the MFT cluster to calculate the MFT offset
    mftCluster = struct.unpack_from("<q", vbrTable, 48)[0]
    clusterSize = bytesPerSector * sectorsPerCluster

    mftOffset = mftCluster * clusterSize

    # Get the MFT entry size
    rawMftEntrySize = struct.unpack_from("<b", vbrTable, 64)[0]
    mftEntrySize = 2 ** abs(rawMftEntrySize)

    return (mftOffset, mftEntrySize)


__all__ = ["ReadVbrData"]
