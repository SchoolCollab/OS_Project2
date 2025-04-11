import io as io


def ReadClusterChain(
    fatData: bytes,
    cluster: int,
) -> list[int]:
    """Read the cluster chain for a given starting cluster.

    ### Parameters
    - **fatData** `bytes`: The FAT data.
    - **cluster** `int`: The starting cluster.

    ### Returns
    - `list[int]`: A list of clusters in the chain.
    """
    clusters = []

    # Keep reading until we reach the end of the chain
    while 0x00000002 <= cluster < 0x0FFFFFF8:
        clusters.append(cluster)

        # Get the next cluster in the chain
        entryOffset = cluster * 4
        entry = int.from_bytes(fatData[entryOffset : entryOffset + 4], "little")

        cluster = entry & 0x0FFFFFFF  # Only lower 28 bits are valid in FAT32

    return clusters


__all___ = [
    "ReadClusterChain",
]
