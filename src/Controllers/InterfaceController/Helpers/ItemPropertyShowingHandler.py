from Controllers.InterfaceController.Data import (
    InterfaceController_Types as _INTERFACE_TYPES,
)

import os as os
import multiprocessing as multiprocessing

from Controllers.InterfaceController.Helpers.InitPropertyWindow import (
    InitPropertyWindow,
)

from Controllers.InterfaceController.Data.InterfaceController_Data import (
    Data as InterfaceData,
)


def ItemPropertyShowingHandler(
    event: _INTERFACE_TYPES.Event, item: _INTERFACE_TYPES.ItemDrawInfo
) -> bool:
    """Handle property window showing event

    ### Parameters
    - **event** `Event`: The event to handle.
    - **item** `ItemDrawInfo`: The item to handle the event for.
    """
    # Check if the item's name is clicked
    if not item.nameHitbox.collidepoint(
        (
            event.pos[0] + InterfaceData.screenOffset[1],
            event.pos[1] + InterfaceData.screenOffset[0],
        )
    ):
        # Skip check if the line is not expanded
        if not item.icon or item.icon == InterfaceData.images["plus"]:
            return False

        # Also check if any items' names are clicked
        for subItem in item.subItems:
            if ItemPropertyShowingHandler(event, subItem):
                return True

        return False

    # Start a new process to show the properties of the item
    InterfaceData.processes.append(
        multiprocessing.Process(
            target=InitPropertyWindow,
            args=(
                InterfaceData.screenResolution,
                os.path.join(InterfaceData.dataPath, "Fonts", "font_property.ttf"),
                InterfaceData.fontSize,
                item.itempath,
            ),
        )
    )
    InterfaceData.processes[-1].start()

    return True


__all__ = ["ItemPropertyShowingHandler"]
