from pdb import set_trace as TT
from pdb import set_trace as T
from gym_pcgrl.envs.reps.representation import Representation
from PIL import Image
from gym import spaces
import numpy as np

"""
The cellular (autamaton-like) representation, where the agent may change all tiles on the map at each step.
"""


class CARepresentation(Representation):
    """
    Initialize all the parameters used by that representation
    """

    def __init__(self):
        super().__init__()

    """
    Gets the action space used by the cellular representation

    Parameters:
        width: the current map width
        height: the current map height
        num_tiles: the total number of the tile values

    Returns:
        Box: the action space is the same as the observation space, and consists of selected tile-types for
        each tile-coordinate in the level.
    """

    def get_action_space(self, width, height, num_tiles):
        return self.get_observation_space(width, height, num_tiles)

    """
    Get the observation space used by the cellular representation

    Parameters:
        width: the current map width
        height: the current map height
        num_tiles: the total number of the tile values

    Returns:
        Box: the observation space used by that representation. A 2D array of tile numbers
    """

    def get_observation_space(self, width, height, num_tiles):
        return spaces.Dict(
            {
                "map": spaces.Box(
                    low=0, high=num_tiles - 1, dtype=np.uint8, shape=(height, width)
                )
            }
        )

    """
    Get the current representation observation object at the current moment

    Returns:
        observation: the current observation at the current moment. A 2D array of tile numbers
    """

    def get_observation(self):
        return {"map": self._map.copy()}

    """
    Update the cellular representation with the input action

    Parameters:
        action: an action that is used to advance the environment (same as action space)

    Returns:
        boolean: True if the action change the map, False if nothing changed
    """

    def update(self, action, continuous=False):
        if not continuous:
            next_map = action.argmax(axis=0)
        else:
            next_map = action
        if self._map is None:
            # This is the case when using an actual latent seed (so we do only one pass through the generator and have
            # no need to set an initial map in the environment).
            change = True
        else:
            if next_map.shape != self._map.shape:
                print(next_map.shape, self._map.shape)
                raise Exception
            change = (next_map != self._map).any()
        self._map = next_map
        return change, [None, None]
