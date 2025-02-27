import glm
import basilisk as bsk
from typing import Callable
from levels.interactable import Interactable
from player.held_item import HeldItem

def interact_to_hold(interact: Interactable, held: HeldItem) -> Callable:
    """
    Removes the Interactable from the scene and gives the player the held item
    """