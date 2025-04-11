import io as io
import re as re

import Controllers.PartitionController.Helpers as PartitionControllerHelpers

from Controllers.PartitionController.Formats.FAT32.Helpers.ReadClusterChain import (
    ReadClusterChain,
)


def ExtractTxtContent(
    volume: io.BufferedReader,
    fatData: bytes,
    entry: dict,
    dataRegionOffset: int,
    clusterSize: int,
) -> str:
    """Extract the content of a .txt file from the FAT32 file system.

    ### Parameters
    - **volume** `BufferedReader`: The volume for the partition.
    - **fatData** `bytes`: The FAT table data.
    - **entry** `dict`: The directory entry for the .txt file.
    - **dataRegionOffset** `int`: The offset of the data region.
    - **clusterSize** `int`: The size of a cluster in bytes.

    ### Returns
    - `str`: The extracted and cleaned content of the .txt file.
    """
    content = ""

    # Get the cluster chain for the file
    clusters = ReadClusterChain(
        volume, fatData, entry["cluster"], dataRegionOffset, clusterSize
    )

    # Read and decode the content of each cluster
    for cluster in clusters:
        # Read the cluster data
        clusterOffset = dataRegionOffset + (cluster - 2) * clusterSize
        clusterData = PartitionControllerHelpers.ReadBytes(
            volume, clusterOffset, clusterSize
        )

        # Decode the data and clean it
        decodedData = clusterData.decode(errors="ignore")
        cleanedData = decodedData.replace("\x00", "")  # Remove null characters

        # Append the cleaned data to the content
        content += cleanedData

    return content
