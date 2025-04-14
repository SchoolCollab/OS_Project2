import Data.Types as _TYPES
from Controllers.InterfaceController.Data import (
    InterfaceController_Types as _INTERFACE_TYPES,
)

from Controllers.InterfaceController.Data.InterfaceController_Data import (
    Data as InterfaceData,
)


def GetLongestItem(
    item: _INTERFACE_TYPES.ItemDrawInfo,
) -> _INTERFACE_TYPES.ItemDrawInfo:
    """Get the longest item in the interface

    ### Returns
    - **ItemDrawInfo**: The longest item in the interface.
    """
    longestItem = item

    for subItem in item.subItems:
        # Recursively get the longest item in the sub items
        subItem = GetLongestItem(subItem)

        if (
            subItem.name.get_width() + subItem.nameHitbox.left
            > longestItem.name.get_width() + longestItem.nameHitbox.left
        ):
            longestItem = subItem

    return longestItem


def HandleScrolling(x: int, y: int) -> None:
    """Handle the scrolling of the interface

    ### Parameters
    - **x** `int`: The x axis scroll value.
    - **y** `int`: The y axis scroll value.
    """
    # Handle scrolling in Y axis

    # Limit the scroll range by getting the last item
    lastItem = InterfaceData.items[-1]

    while len(lastItem.subItems) > 0:
        # Get the last sub item
        lastItem = lastItem.subItems[-1]

    # Get the maximum scroll value
    maxYScroll = lastItem.index * InterfaceData.fontSize * 2

    # Update the screen offset
    InterfaceData.screenOffset = (
        max(
            0,
            min(
                InterfaceData.screenOffset[0] - y * InterfaceData.fontSize * 2,
                maxYScroll
                - InterfaceData.screenResolution[1]
                + InterfaceData.fontSize * 4,
            ),
        ),
        InterfaceData.screenOffset[1],
    )

    # Handle scrolling in X axis

    # Limit the scroll range by getting the longest item
    longestItem = InterfaceData.items[0]

    for item in InterfaceData.items:
        # Get the longest item in the interface
        item = GetLongestItem(item)

        if (
            item.name.get_width() + item.nameHitbox.left
            > longestItem.name.get_width() + longestItem.nameHitbox.left
        ):
            longestItem = item

    # Get the maximum scroll value
    maxXScroll = longestItem.name.get_width() + longestItem.nameHitbox.left

    # Update the screen offset
    InterfaceData.screenOffset = (
        InterfaceData.screenOffset[0],
        max(
            0,
            min(
                InterfaceData.screenOffset[1] - x * InterfaceData.fontSize * 2,
                maxXScroll
                - InterfaceData.screenResolution[0]
                + InterfaceData.fontSize * 4,
            ),
        ),
    )


__all__ = ["HandleScrolling"]
