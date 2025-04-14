import Data.Types as _TYPES


class PartitionController:
    partitions: dict[str, _TYPES.DiskPartition] = {}


Data: PartitionController = PartitionController()
"""Data for the PartitionController

### Attributes
- **partitions** `dict[str, DiskPartition]`: A dictionary of all the partitions in the disk.
"""
