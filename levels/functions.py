import glm
from typing import Callable
from levels.interactable import Interactable


def pickup_function(interact: Interactable, func: Callable) -> Callable:
    """
    Generates a "pick up" function for the given interactable.
    func will be activated when the player closes the pick up menu in the accept termination.
    The Interactable must have the following attributes:  `
    """
    