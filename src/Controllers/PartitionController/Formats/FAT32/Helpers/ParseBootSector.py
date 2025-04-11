import io as io


def ParseBootSector(volume: io.BufferedReader) -> dict[str, int]:
    """Parse the boot sector of a FAT32 partition.

    ### Parameters
    - **volume** `BufferedReader`: The volume containing the FAT32 partition data.

    ### Returns
    - `dict`: A dictionary containing FAT32 metadata including:
        - **bytesPerSector** `int`: Number of bytes per sector.
        - **sectorsPerCluster** `bytes`: Number of sectors per cluster.
        - **reservedSectors** `int`: Number of reserved sectors.
        - **numFats** `int`: Number of FATs.
        - **sectorsPerFat** `int`: Number of sectors per FAT.
        - **rootCluster** `int`: The first cluster of the root directory.
    """
    volume.seek(0)
    boot = volume.read(512)

    return {
        "bytesPerSector": int.from_bytes(boot[11:13], "little"),
        "sectorsPerCluster": int.from_bytes(boot[13], "little"),
        "reservedSectors": int.from_bytes(boot[14:16], "little"),
        "numFats": int.from_bytes(boot[16], "little"),
        "sectorsPerFat": int.from_bytes(boot[36:40], "little"),
        "rootCluster": int.from_bytes(boot[44:48], "little"),
    }


__all__ = [
    "ParseBootSector",
]
