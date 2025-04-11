import io as io


def ReadBytes(volume: io.BufferedReader, offset: int, size: int) -> bytes:
    """Read a specific number of bytes from a buffer at a given offset.

    ### Parameters
    - **volume** `BufferedReader`: The volume to read from.
    - **offset** `int`: The offset to start reading from.
    - **size** `int`: The number of bytes to read.

    ### Returns
    - `bytes`: The bytes read from the file.
    """
    volume.seek(offset)
    return volume.read(size)


__all__ = ["ReadBytes"]
