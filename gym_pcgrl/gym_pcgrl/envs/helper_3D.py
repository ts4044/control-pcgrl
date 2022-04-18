"""
A helper module that can be used by all problems in cubic 3D game
"""
import matplotlib.pyplot as plt
import numpy as np
from pdb import set_trace as TT

"""
Public function to get a dictionary of all location of all tiles

Parameters:
    map (any[][][]): the current map

    [[[0, 0, 0], [0, 0, 0], [0, 0, 0]],
     [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
     [[0, 0, 0], [0, 0, 0], [0, 0, 0]]]

    tile_values (any[]): an array of all the tile values that are possible

Returns:
    Dict(string,(int,int)[]): positions for every certain tile_value
"""


def get_tile_locations(map, tile_values):
    tiles = {}
    for t in tile_values:
        tiles[t] = []
    for z in range(len(map)):
        for y in range(len(map[z])):
            for x in range(len(map[z][y])):
                tiles[map[z][y][x]].append((x, y, z))
    return tiles


"""
Get the vertical distance to certain type of tiles

Parameters:
    map (any[][][]): the actual map
    x (int): the x position of the start location
    y (int): the y position of the start location
    z (int): the z position of the start location
    types (any[]): an array of types of tiles

Returns:
    int: the distance to certain types underneath a certain location
"""


def _calc_dist_floor(map, x, y, z, types):
    for dz in range(len(map)):
        if z + dz >= len(map):
            break
        if map[z + dz][y][x] in types:
            return dz - 1
    return len(map) - 1


"""
Public function to calculate the distance of a certain tiles to the floor tiles

Parameters:
    map (any[][][]): the current map
    from (any[]): an array of all the tile values that the method is calculating the distance to the floor
    floor (any[]): an array of all the tile values that are considered floor

Returns:
    int: a value of how far each tile from the floor where 0 means on top of floor and positive otherwise
"""


def get_floor_dist(map, fromTypes, floorTypes):
    result = 0
    for z in range(len(map)):
        for y in range(len(map[z])):
            for x in range(len(map[z][y])):
                if map[z][y][x] in fromTypes:
                    result += _calc_dist_floor(map, x, y, z, floorTypes)
    return result


"""
Get number of tiles that have certain value arround certain position

Parameters:
    map (any[][][]): the current map
    x (int): the x position of the start location
    y (int): the y position of the start location
    z (int): the z position of the start location
    types (any[]): an array of types of tiles
    relLocs ((int,int,int)[]): a tuple array of all the relative positions

Returns:
    int: the number of similar tiles around a certain location
"""


def _calc_group_value(map, x, y, z, types, relLocs):
    result = 0
    for l in relLocs:
        nx, ny, nz = x + l[0], y + l[1], z + l[2]
        if (
            nx < 0
            or ny < 0
            or nz < 0
            or nx >= len(map[0])
            or ny >= len(map)
            or nz >= len(map)
        ):
            continue
        if map[nz][ny][nx] in types:
            result += 1
    return result


"""
Get the number of tiles that is a group of certain size

Parameters:
    map (any[][][]): the current map
    types (any[]): an array of types of tiles
    relLocs ((int,int,int)[]): a tuple array of all the relative positions
    min (int): min number of tiles around
    max (int): max number of tiles around

Returns:
    int: the number of tiles that have surrounding between min and max
"""


def get_type_grouping(map, types, relLocs, min, max):
    result = 0
    for z in range(len(map)):
        for y in range(len(map[z])):
            for x in range(len(map[z][y])):
                if map[z][y][x] in types:
                    value = _calc_group_value(map, x, y, z, types, relLocs)
                    if value >= min and value <= max:
                        result += 1
    return result


"""
Get the number of changes of tiles in either vertical or horizontal direction

Parameters:
    map (any[][][]): the current map
    vertical (boolean): calculate the vertical changes instead of horizontal

Returns:
    int: number of different tiles either in vertical or horizontal x-direction or horizontal y-direction
"""


def get_changes(map, vertical=False, y_dir=False):
    start_z = 0
    start_y = 0
    start_x = 0
    if vertical:
        start_z = 1
    elif y_dir:
        start_y = 1
    else:
        start_x = 1
    value = 0
    for z in range(start_z, len(map)):
        for y in range(start_y, len(map[z])):
            for x in range(start_x, len(map[z][y])):
                same = False
                if vertical:
                    same = map[z][y][x] == map[z - 1][y][x]
                elif y_dir:
                    same = map[z][y][x] == map[z][y - 1][x]
                else:
                    same = map[z][y][x] == map[z][y][x - 1]
                if not same:
                    value += 1
    return value


"""
Private function to get a list of all tile locations on the map that have any of
the tile_values

Parameters:
    map_locations (Dict(string,(int,int,int)[])): the histogram of locations of the current map
    tile_values (any[]): an array of all the tile values that the method is searching for

Returns:
    (int,int,int)[]: a list of (x,y,z) position on the map that have a certain value
"""


def _get_certain_tiles(map_locations, tile_values):
    tiles = []
    for v in tile_values:
        tiles.extend(map_locations[v])
    return tiles


"""
Private function that see whether the current position is standable: The position is passable only when height >= 2
(character is 2 blocks tall)

Parameters:
    x (int): The current x position
    y (int): The current y position
    z (int): The current z position   
    map (any[][][]): the current tile map to check
    passable_values (any[]): an array of all the passable tile values

Return:
    boolen: True if the aisle is passable
"""


def _standable(map, x, y, z, passable_values):
    nx, ny, nz = x, y, z + 1
    if nz < 0 or nz >= len(map):
        return False
    elif map[nz][ny][nx] in passable_values and map[z][y][x] in passable_values:
        return True
    else:
        return False


"""
Private function that see whether the aisle is passable: The aisle is passable only when the agent can move to a 
adjacent position.
    (The adjacent position won't block the character's head)

Parameters:
    x (int): The current x position
    y (int): The current y position
    z (int): The current z position
    map (any[][][]): the current tile map to check
    passable_values (any[]): an array of all the passable tile values

Return:
    boolen: True if the aisle is passable
"""


def _passable(map, x, y, z, passable_values):

    passable_tiles = []

    # Check 4 adjacent directions: forward, back, left, right. For each, it is passable if we can move to it while
    # moving up/down-stairs or staying level.
    for dir in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
        nx, ny, nz = x + dir[0], y + dir[1], z

        # Check if out of bounds, if so, skip it
        if nx < 0 or ny < 0 or nx >= len(map[z][y]) or ny >= len(map[z]):
            continue

        # Check whether we can go down a step.
        if (
            # nz+1 < len(map) and  # Head-room is guaranteed if our current position is valid.
            (
                nz - 1 == 0  # Either we are moving either onto the bottom of the map...
                or nz - 1 > 0
                and map[nz - 2][ny][nx] not in passable_values
            )  # ... or onto am impassable (solid) tile.
            and map[nz - 1][ny][nx] in passable_values  # Foot-room at the lower stair.
            and map[nz][ny][nx] in passable_values  # Head-room at the lower stair.
            and map[nz + 1][ny][nx]
            in passable_values  # Extra head-room at the lower (next) stair.
        ):
            passable_tiles.append((nx, ny, nz - 1))

        # Check whether can stay at the same level.
        elif (
            # nz+1 < len(map) and  # Head-room at our next position is guaranteed if our current position is valid.
            (
                nz == 0
                or nz > 0  # Either we are on the bottom of the map...
                and map[nz - 1][ny][nx] not in passable_values
            )  # ...or moving onto an impassable (solid) tile.
            and map[nz][ny][nx] in passable_values  # Foot-room at our next position.
            and map[nz + 1][ny][nx]
            in passable_values  # Head-room at our next position.
        ):
            passable_tiles.append((nx, ny, nz))

        # Check whether can go up a step.
        elif (
            nz + 2 < len(map)  # Our head must remain inside the map.
            and map[nz][ny][nx]
            not in passable_values  # There must be a (higher) stair to climb onto.
            and map[nz + 1][ny][nx] in passable_values  # Foot-room at the higher stair.
            and map[nz + 2][ny][nx] in passable_values  # Head-room at the higher stair.
            and map[nz + 2][y][x]
            in passable_values  # Extra head-room at the lower (current) stair.
        ):
            passable_tiles.append((nx, ny, nz + 1))

        # TODO: check for ladder:  (ladder tiles are passable)
        # if current tile is ladder, then check if extra head-room above. If so, can move up.
        # if tile below is ladder, can move down.

        else:
            continue

    return passable_tiles


"""
Private function that runs flood fill algorithm on the current color map

Parameters:
    x (int): the starting x position of the flood fill algorithm
    y (int): the starting y position of the flood fill algorithm
    z (int): the starting z position of the flood fill algorithm
    color_map (int[][][]): the color map that is being colored
    map (any[][][]): the current tile map to check
    color_index (int): the color used to color in the color map
    passable_values (any[]): the current values that can be colored over

Returns:
    int: the number of tiles that has been colored
"""


def _flood_fill(x, y, z, color_map, map, color_index, passable_values):
    num_tiles = 0
    queue = [(x, y, z)]

    while len(queue) > 0:
        (cx, cy, cz) = queue.pop(0)

        # If tile has been visited, skip it.
        if (
            color_map[cz][cy][cx] != -1
        ):  # or (not _passablae(map, cx, cy, cz, passable_values) and not _standable(map, cx, cy, cz, passable_values)):
            continue

        num_tiles += 1
        color_map[cz][cy][cx] = color_index

        # Look at all adjacent tiles.
        for (dx, dy, dz) in [
            (-1, 0, 0),
            (1, 0, 0),
            (0, -1, 0),
            (0, 1, 0),
            (0, 0, -1),
            (0, 0, 1),
        ]:
            nx, ny, nz = cx + dx, cy + dy, cz + dz

            # If adjacent tile is out of bounds, skip it.
            if (
                nx < 0
                or ny < 0
                or nz < 0
                or nx >= len(map[0][0])
                or ny >= len(map[0])
                or nz >= len(map)
            ):
                continue

            # If adjacent tile is not passable, skip it.
            if map[nz][ny][nx] not in passable_values:
                continue

            # Otherwise, add adjacent tile to the queue.
            queue.append((nx, ny, nz))

    return num_tiles


"""
Calculates the number of regions in the current map with passable_values

Parameters:
    map (any[][][]): the current map being tested
    map_locations(Dict(string,(int,int,int)[])): the histogram of locations of the current map
    passable_values (any[]): an array of all the passable tile values

Returns:
    int: number of regions in the map
"""


def calc_num_regions(map, map_locations, passable_values):
    empty_tiles = _get_certain_tiles(map_locations, passable_values)
    region_index = 0
    color_map = np.full((len(map), len(map[0]), len(map[0][0])), -1)
    for (x, y, z) in empty_tiles:
        num_tiles = _flood_fill(
            x, y, z, color_map, map, region_index + 1, passable_values
        )
        if num_tiles > 0:
            region_index += 1
        else:
            continue
    return region_index


"""
Public function that runs dijkstra algorithm and return the map

Parameters:
    x (int): the starting x position for dijkstra algorithm
    y (int): the starting y position for dijkstra algorithm
    z (int): the starting z position for dijkstra algorithm
    map (any[][][]): the current map being tested
    passable_values (any[]): an array of all the passable tile values

Returns:
    int[][][]: returns the dijkstra map after running the dijkstra algorithm
"""


def run_dijkstra(x, y, z, map, passable_values):
    dijkstra_map = np.full((len(map), len(map[0]), len(map[0][0])), -1)
    visited_map = np.zeros((len(map), len(map[0]), len(map[0][0])))
    queue = [(x, y, z, 0)]

    while len(queue) > 0:
        # Looking at a new tile
        (cx, cy, cz, cd) = queue.pop(0)

        # Skip tile if we've already visited it
        if dijkstra_map[cz][cy][cx] >= 0 and dijkstra_map[cz][cy][cx] <= cd:
            continue

        # We never start path-finding from a position at which the player cannot stand. Foot-room is guaranteed, so we
        # check for headroom.
        # Zelda (and other games maybe) calls this function directly without calling calc_longest_path, so we need to
        # add this check here.
        if cz + 1 == len(map) or map[cz + 1][y][x] not in passable_values:
            visited_map[cz][cy][cx] = 1
            continue

        # Count the tile as visited and record its distance
        visited_map[cz][cy][cx] = 1
        dijkstra_map[cz][cy][cx] = cd

        # Call passable, which will return, (x, y, z) coordinates of tiles to which the player can travel from here
        # not for (dx,dy,dz) in [(-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 1, 0), (0, 0, -1), (0, 0, 1)]:
        # but for (nx,ny,nz) in stairring logic:
        for (nx, ny, nz) in _passable(map, cx, cy, cz, passable_values):

            #           # Check that the new tiles are in the bounds of the level
            #           nx,ny,nz=cx+dx,cy+dy,cz+dz
            #           if nx < 0 or ny < 0 or nz <0 or nx >= len(map[0][0]) or ny >= len(map[0]) or nz >=len(map):

            #               # If out of bounds, do not add the new tile to the frontier
            #               continue

            # Add the new tile to the frontier
            queue.append((nx, ny, nz, cd + 1))
    #           if cz == 3:
    #               print(f"**********current place: {cx},{cy},{cz}**********")
    #               print("queue in run_dijkstra: ", queue)
    #               print("dijkstra_map in run_dijkstra: ", dijkstra_map)

    return dijkstra_map, visited_map


"""
Calculate the longest path on the map

Parameters:
    map (any[][][]): the current map being tested
    map_locations (Dict(string,(int,int,int)[])): the histogram of locations of the current map
    passable_values (any[]): an array of all passable tiles in the map

Returns:
    int: the longest path value in tiles in the current map
"""


def calc_longest_path(map, map_locations, passable_values, get_path=False):
    empty_tiles = _get_certain_tiles(map_locations, passable_values)
    final_visited_map = np.zeros((len(map), len(map[0]), len(map[0][0])))
    final_value = 0

    # We'll iterate over all empty tiles. But checking against the visited_map means we only perform path-finding
    # algorithms once per connected component.
    for (x, y, z) in empty_tiles:

        if final_visited_map[z][y][x] > 0:
            continue

        # We never start path-finding from a position at which the player cannot stand. Foot-room is guaranteed, so we
        # check for headroom.
        if z + 1 == len(map) or map[z + 1][y][x] not in passable_values:
            final_visited_map[z][y][x] = 1
            continue

        # Calculate the distance from the current tile to all other (reachable) tiles.
        dijkstra_map, visited_map = run_dijkstra(x, y, z, map, passable_values)
        final_visited_map += visited_map

        # Get furthest tile from current tile.
        (mz, my, mx) = np.unravel_index(
            np.argmax(dijkstra_map, axis=None), dijkstra_map.shape
        )

        # Search again from this furthest tile. This tile must belong to a longest shortest path within this connected
        # component. Search again to find this path.
        dijkstra_map, _ = run_dijkstra(mx, my, mz, map, passable_values)
        max_value = np.max(dijkstra_map)

        # Store this path/length if it is the longest of all connected components visited thus far.
        if max_value > final_value:
            final_value = max_value

            if get_path:
                path_map = dijkstra_map

    path = []

    if get_path and final_value > 0:
        path = get_path_coords(path_map)

    return final_value, path


"""
Recover a shortest path (as list of coords) from a dijkstra map, 
using either some initial coords, or else from the furthest point

If you have trouble understanding this func, you can refer to the 2D version of this in helper.py

Parameters:
    path_map: 3D dijkstra map
    x, y, z (optional): ending point of the path

Returns:
    list: the longest path's coordinates (in x, y, z form)
"""

ADJ_FILTER = np.array(
    [
        [[0, 1, 0], [1, 0, 1], [0, 1, 0]],
        [[0, 1, 0], [1, 0, 1], [0, 1, 0]],
        [[0, 1, 0], [1, 0, 1], [0, 1, 0]],
    ]
)


def get_path_coords(path_map, x=None, y=None, z=None, can_fly=False):
    length, width, height = len(path_map[0][0]), len(path_map[0]), len(path_map)
    pad_path_map = np.zeros(shape=(height + 2, width + 2, length + 2), dtype=np.int32)
    pad_path_map.fill(0)
    pad_path_map[1 : height + 1, 1 : width + 1, 1 : length + 1] = path_map + 1
    if not x:
        # Work from the greatest cell value (end of the path) backward
        max_cell = pad_path_map.max()
        curr = np.array(np.where(pad_path_map == max_cell))
    else:
        curr = np.array([(z, y, x)], dtype=np.int32).T + 1
        max_cell = pad_path_map[curr[0][0], curr[1][0], curr[2][0]]
    zi, yi, xi = curr[:, 0]
    # print("curr: ", curr)
    # print("zi, yi, xi is curr[:, 0]: ", zi, yi, xi)
    # print("max_cell: ", max_cell)
    # print("iterating:")
    path = np.zeros(shape=(max_cell, 3), dtype=np.int32)
    i = 0
    while max_cell > 1:
        path[i, :] = [xi - 1, yi - 1, zi - 1]
        pad_path_map[zi, yi, xi] = -1
        max_cell -= 1
        x0, x1, y0, y1, z0, z1 = xi - 1, xi + 2, yi - 1, yi + 2, zi - 1, zi + 2
        adj_mask = np.zeros(shape=(height + 2, width + 2, length + 2), dtype=np.int32)
        adj_mask[z0:z1, y0:y1, x0:x1] = ADJ_FILTER
        # print("curr: ", curr)
        # print("zi, yi, xi is curr[:, 0]: ", zi, yi, xi)
        # print("max_cell: ", max_cell)
        curr = np.array(np.where(adj_mask * pad_path_map == max_cell))

        # print("curr is changed to: ", curr)
        # print("pad_path_map is : ", pad_path_map)
        zi, yi, xi = curr[:, 0]
        i += 1
    if i > 0:
        path[i, :] = [xi - 1, yi - 1, zi - 1]

    # if the agent can't fly, delete the blocks with identical vertical coordinates in the path, only reserve the bottom one
    if not can_fly:
        for i in range(0, len(path)):
            if i == 0:
                continue
            else:
                if path[i][0] == path[i - 1][0] and path[i][1] == path[i - 1][1]:
                    if path[i - 1][2] > path[i][2]:
                        path[i - 1, :] = [-1, -1, -1]
                    else:
                        path[i, :] = [-1, -1, -1]
    path = np.delete(path, np.where(path < 0)[0], axis=0)
    return path


def debug_path(path, map, passable_values):
    """
    Path debugging function
    """
    if len(path) == 0:
        return True
    for pos in path:
        x, y, z = pos[0], pos[1], pos[2]
        # checking if there is some issue with my head
        if z + 2 > len(map):
            print(
                f"My head is sticking out of range!!!!!!!!!!!!!!!! My foot is at the position {x}, {y}, {z}"
            )
            return False
        if map[z + 1][y][x] not in passable_values:
            print(
                f"Something in position {x}, {y}, {z+1} blocks my head!!!!!!!!!!!!!!!!!!!!!!!!!!"
            )
            return False
        # checking if I am floating
        if z - 1 > 0 and map[z - 1][y][x] in passable_values:
            print(f"I am floating illegally!!!!!!!!! My position is {x}, {y}, {z}")
            return False
    return True


"""
Calculate the number of tiles that have certain values in the map

Returns:
    int: get number of tiles in the map that have certain tile values
"""


def calc_certain_tile(map_locations, tile_values):
    return len(_get_certain_tiles(map_locations, tile_values))


"""
Calculate the number of reachable tiles of a certain values from a certain starting value
The starting value has to be one on the map

Parameters:
    map (any[][][]): the current map
    start_value (any): the start tile value it has to be only one on the map
    passable_values (any[]): the tile values that can be passed in the map
    reachable_values (any[]): the tile values that the algorithm trying to reach

Returns:
    int: number of tiles that has been reached of the reachable_values
"""


def calc_num_reachable_tile(
    map, map_locations, start_value, passable_values, reachable_values
):
    (sx, sy, sz) = _get_certain_tiles(map_locations, [start_value])[0]
    dijkstra_map, _ = run_dijkstra(sx, sy, sz, map, passable_values)
    tiles = _get_certain_tiles(map_locations, reachable_values)
    total = 0
    for (tx, ty, tz) in tiles:
        if dijkstra_map[tz][ty][tx] >= 0:
            total += 1
    return total


"""
Generate random map based on the input Parameters

Parameters:
    random (numpy.random): random object to help generate the map
    width (int): the generated map width
    height (int): the generated map height
    prob (dict(int,float)): the probability distribution of each tile value

Returns:
    int[][][]: the random generated map
"""


def gen_random_map(random, length, width, height, prob):
    map = random.choice(
        list(prob.keys()), size=(height, width, length), p=list(prob.values())
    ).astype(np.uint8)
    return map


"""
A method to convert the map to use the tile names instead of tile numbers

Parameters:
    map (numpy.int[][][]): a numpy 3D array of the current map
    tiles (string[]): a list of all the tiles in order

Returns:
    string[][][]: a 3D map of tile strings instead of numbers
"""


def get_string_map(map, tiles):
    int_to_string = dict((i, s) for i, s in enumerate(tiles))
    result = []
    for z in range(map.shape[0]):
        result.append([])
        for y in range(map.shape[1]):
            result[z].append([])
            for x in range(map.shape[2]):
                result[z][y].append(int_to_string[int(map[z][y][x])])
    return result


"""
A method to convert the probability dictionary to use tile numbers instead of tile names

Parameters:
    prob (dict(string,float)): a dictionary of the probabilities for each tile name
    tiles (string[]): a list of all the tiles in order

Returns:
    Dict(int,float): a dictionary of tile numbers to probability values (sum to 1)
"""


def get_int_prob(prob, tiles):
    string_to_int = dict((s, i) for i, s in enumerate(tiles))
    result = {}
    total = 0.0
    for t in tiles:
        result[string_to_int[t]] = prob[t]
        total += prob[t]
    for i in result:
        result[i] /= total
    return result


"""
A method to help calculate the reward value based on the change around optimal region

Parameters:
    new_value (float): the new value to be checked
    old_value (float): the old value to be checked
    low (float): low bound for the optimal region
    high (float): high bound for the optimal region

Returns:
    float: the reward value for the change between new_value and old_value
"""


def get_range_reward(new_value, old_value, low, high):
    if (
        new_value >= low
        and new_value <= high
        and old_value >= low
        and old_value <= high
    ):
        return 0
    if old_value <= high and new_value <= high:
        return min(new_value, low) - min(old_value, low)
    if old_value >= low and new_value >= low:
        return max(old_value, high) - max(new_value, high)
    if new_value > high and old_value < low:
        return high - new_value + old_value - low
    if new_value < low and old_value > high:
        return high - old_value + new_value - low


"""
A function to plot the 3D structure of the map
"""


def plot_3D_path(size_x, size_y, size_z, path_coords):

    # create the boolen map of the maze
    path_boolean_map = np.full((size_z, size_y, size_x), False, dtype=bool)

    for (x, y, z) in path_coords:
        path_boolean_map[z][y][x] = True

    # change the map axis for plotting
    path_boolean_map = np.moveaxis(path_boolean_map, (0, 2), (2, 1))

    # create the color map of the maze
    path_color_map = np.empty(path_boolean_map.shape, dtype=object)
    path_color_map[path_boolean_map] = "red"

    # make a 3D plot
    ax = plt.figure().add_subplot(projection="3d")

    # scale the plot so that the blocks are cube but not cuboid
    ax.set_box_aspect(
        [
            path_boolean_map.shape[0] / path_boolean_map.shape[1],
            1,
            path_boolean_map.shape[2] / path_boolean_map.shape[1],
        ]
    )

    # plot it out!
    ax.voxels(path_boolean_map, facecolors=path_color_map, edgecolor="k")
    plt.show()
