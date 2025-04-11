import io as io


def ParseBootSector(metadata: io.BufferedReader) -> dict:
    """Parse the boot sector of a FAT32 partition.

    ### Parameters
    - **metadata** `io.BufferedReader`: The file-like object containing the FAT32 partition data.

    ### Returns
    - `dict`: A dictionary containing FAT32 metadata including:
        - **bytesPerSector** `int`: Number of bytes per sector.
        - **sectorsPerCluster** `int`: Number of sectors per cluster.
        - **reservedSectors** `int`: Number of reserved sectors.
        - **numFats** `int`: Number of FATs.
        - **sectorsPerFat** `int`: Number of sectors per FAT.
        - **rootCluster** `int`: The first cluster of the root directory.
    """
    metadata.seek(0)
    boot = metadata.read(512)

    return {
        "bytesPerSector": int.from_bytes(boot[11:13], "little"),
        "sectorsPerCluster": boot[13],
        "reservedSectors": int.from_bytes(boot[14:16], "little"),
        "numFats": boot[16],
        "sectorsPerFat": int.from_bytes(boot[36:40], "little"),
        "rootCluster": int.from_bytes(boot[44:48], "little"),
    }


__all__ = [
    "ParseBootSector",
]
