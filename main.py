import networkx as nx
import matplotlib.pyplot as plt
import argparse
import json
import math
import random
from collections import deque

import heapq  # heap queue is like a priority queue

##################################################################################
# build stage

# complete graphs: each vertex connects to every other vertex
# k-regular graphs: all vertices have the same degree
# any given graph: specified by user
# random graph:
# valid_types = {"complete", "regular", "given", "random"}


# complete graphs: each vertex connects to every other vertex
# (there is exactly ONE edge between EVERY pair of vertices)
#
# inputs:
# num_vertices: number of vertices in the graph (n)
# min_weight: minimum edge weight (none for unweighted)
# max_weight: maximum edge weight (none for unweighted)
#
# outputs:
# a networkx graph where every vertex has degree n-1 and
# the total number of edges is n(n-1)/2
def build_complete_graph(num_vertices, min_weight, max_weight):

    assert num_vertices > 0
    # if user specfies min and max, randomly choose a weight
    use_random_weight = (min_weight is not None) and (max_weight is not None)

    g = nx.Graph()
    g.add_nodes_from(range(num_vertices))

    # for each node u, connect to every node v that comes after it
    # starting v at u+1 avoids duplicate edges (u,v) and (v,u) and self-loops

    # every pair of vertices has exactly ONE edge between them

    # for each node u
    for u in range(num_vertices):
        # for every node that comes after u
        for v in range(u + 1, num_vertices):
            # add edge with random weight
            if use_random_weight:
                w = random.randint(min_weight, max_weight)
                g.add_edge(u, v, weight=w)
            else:
                # add edge with no weight
                g.add_edge(u, v)

    return g




# # k-regular graphs: all vertices have the same degree
# #
# # inputs:
# # num_vertices: number of vertices in the graph (n)
# # k: degree of each vertex (number of edges per vertex)
# # min_weight: minimum edge weight (none for unweighted)
# # max_weight: maximum edge weight (none for unweighted)
# #
# # outputs:
# # a networkx graph where every vertex has exactly k edges
# def build_regular_graph(num_vertices, k, min_weight, max_weight):
#
#     assert num_vertices > 0
#     assert k >= 0
#
#     g = nx.Graph()
#     g.add_nodes_from(range(num_vertices))
#
#     use_random_weight = (min_weight is not None) and (max_weight is not None)
#
#     # for each vertex u
#     for u in range(num_vertices):
#         # u may connect to n nodes, but we only want k connections
#         u_neighbors = list(g.neighbors(u))
#         all_vertices = set(range(num_vertices))
#
#         candidates = all_vertices - set(u_neighbors)  # remove neighbors
#         candidates.discard(u)  # remove self
#
#         # remove nodes that alreday have degree = k
#         # list(candidates) copies 'candidates', so that we can iterate over it
#         # while modifying candidates
#         for v in list(candidates):
#             if len(list(g.neighbors(v))) == k:
#                 candidates.discard(v)
#
#         # now, candidates is ready to be selected from
#         num_new_neighbors_needed = k - len(u_neighbors)
#         new_neighbors = random.sample(list(candidates), num_new_neighbors_needed)
#         for new_neighbor in new_neighbors:
#             g.add_edge(u, new_neighbor)
#             if use_random_weight:
#                 w = random.randint(min_weight, max_weight)
#                 g.add_edge(u, new_neighbor, weight=w)
#             else:
#                 g.add_edge(u, new_neighbor)
#
#     return g


# inputs:
# num_vertices: number of vertices in the graph (n)
# k: degree of each vertex (number of edges per vertex)
# min_weight: minimum edge weight (none for unweighted)
# max_weight: maximum edge weight (none for unweighted)
#
# outputs:
# a networkx graph where every vertex has exactly k edges
def build_regular_graph_circulant(num_vertices, k, min_weight, max_weight):
    #  k-regular graph: every vertex has k edges
    #
    # build k-regular graph using circulant graph construction (algorithm)
    #
    # this algorithm is deterministic and always succeeds (unlike greedy random approaches)
    #
    # algorithm:
    #     1. arrange vertices conceptually in a circle using a list [0, 1, 2, ..., n-1] (indices)
    #     2. each vertex connects to its next k//2 neighbors going clockwise
    #     3. the counterclockwise connections are automatically created when
    #        those neighbors process their clockwise edges
    #     4. for odd k: add "diameter" edges connecting opposite vertices
    #
    # example (n=6, k=4, so k//2=2):
    #     vertices in circle: 0 - 1 - 2 - 3 - 4 - 5 - (back to 0)
    #
    #     each vertex connects forward with offsets 1 and 2:
    #         u=0: offset 1→1, offset 2→2   → creates: 0-1, 0-2
    #         u=1: offset 1→2, offset 2→3   → creates: 1-2, 1-3
    #         u=2: offset 1→3, offset 2→4   → creates: 2-3, 2-4
    #         u=3: offset 1→4, offset 2→5   → creates: 3-4, 3-5
    #         u=4: offset 1→5, offset 2→0   → creates: 4-5, 4-0  (wraps via mod!)
    #         u=5: offset 1→0, offset 2→1   → creates: 5-0, 5-1  (wraps via mod!)
    #
    #     result: each vertex has degree 4
    #         vertex 0: 0-1, 0-2 (from u=0) + 4-0, 5-0 (from u=4,5) = 4 edges
    #         vertex 1: 0-1 (u=0), 1-2, 1-3 (u=1), 5-1 (u=5) = 4 edges
    #         etc.
    #
    # requirements for k-regular graphs:
    #     - sum of degrees = 2 * edges
    #     - sum of degrees = n * k
    #     - n * k is even
    #     - k < n (can't have more neighbors than other vertices exist)


    # validate inputs
    assert num_vertices > 0, "need at least 1 vertex"
    assert k >= 0, "k must be non-negative"
    assert k < num_vertices, f"k={k} must be < num_vertices={num_vertices}" # duplicate edges otherwise
    assert (num_vertices * k) % 2 == 0, f"n*k must be even, got {num_vertices}*{k}={num_vertices*k}"

    use_random_weight = (min_weight is not None) and (max_weight is not None)

    # add vertices
    g = nx.Graph()
    g.add_nodes_from(range(num_vertices))

    # add edges and their weights
    #
    # step 1: connect each vertex to its k//2 nearest neighbors (clockwise)
    # only go "forward" (increasing vertex numbers, with wraparound)
    # "backward" connections are automatically created when those vertices
    # process their forward edges
    for u in range(num_vertices):
        # offset in range k//2
        for offset in range(1, k // 2 + 1):
            v = (u + offset) % num_vertices  # wrap around the circle
            if use_random_weight:
                w = random.randint(min_weight, max_weight)
                g.add_edge(u, v, weight=w)
            else:
                g.add_edge(u, v)

    # step 2: for odd k, add diameter edges
    # when k is odd, add one more edge per vertex
    # add edges between vertices that are exactly n/2 apart (directly across the circle)
    # this requires n to be even (already enforced by n*k being even when k is odd)
    if k % 2 == 1:
        for u in range(num_vertices // 2):
            v = u + num_vertices // 2  # vertex directly across the circle
            if use_random_weight:
                w = random.randint(min_weight, max_weight)
                g.add_edge(u, v, weight=w)
            else:
                g.add_edge(u, v)

    return g

# inputs:
# num_vertices: number of vertices in the graph (n)
# min_weight: minimum edge weight (none for unweighted)
# max_weight: maximum edge weight (none for unweighted)
#
# outputs:
# a networkx graph with an eulerian circuit
def build_eulerian_graph(num_vertices, min_weight, max_weight):
    #
    # build an eulerian graph using circulant construction
    #
    # an eulerian graph has an eulerian circuit: a path that visits every edge
    # exactly once and returns to the starting vertex, this requires:
    #     1. every vertex has even degree
    #     2. the graph is connected
    #
    # this function delegates to build_regular_graph_circulant() with constraints:
    #     - k must be even (ensures even degree for all vertices)
    #     - k must be >= 2 (ensures connectivity via the Hamiltonian cycle from offset 1)
    #
    # args:
    #     num_vertices: number of vertices in the graph
    #     k: degree of each vertex (must be even and >= 2)
    #     min_weight: minimum edge weight (None for unweighted)
    #     max_weight: maximum edge weight (None for unweighted)
    #
    # returns:
    #     a networkx graph with an eulerian circuit
    #

    # choose an even degree between 2 and num_vertices
    k = random.randrange(2, num_vertices, 2)

    assert k % 2 == 0, f"k must be even for eulerian graph, got k={k}"
    assert k >= 2, f"k must be >= 2 for connectivity, got k={k}"
    return build_regular_graph_circulant(num_vertices, k, min_weight, max_weight)




def build_random_graph(num_vertices, min_edges, max_edges, min_weight, max_weight):
    assert num_vertices > 0
    assert min_edges >= 0
    assert max_edges >= 0

    use_random_weight = (min_weight is not None) and (max_weight is not None)

    # create vertices
    g = nx.Graph()
    g.add_nodes_from(range(num_vertices))

    # create edges

    # check the current situation
    for u in range(num_vertices):
        # u could connect to n-1 other vertices, but we only want rand_num_edges connections
        u_neighbors = list(g.neighbors(u))
        all_vertices = set(range(num_vertices))

        # build the candidate set
        # set of vertices that u is allowed to connect to at this point
        candidates = all_vertices - set(u_neighbors)  # remove neighbors (no multi-edges)
        candidates.discard(u)  # remove self (no self-loops)

        # remove nodes that alreday have degree = max_edges
        # list(candidates) copies 'candidates', so that we can iterate over it
        # while modifying candidates
        for v in list(candidates):
            if len(list(g.neighbors(v))) == max_edges:
                candidates.discard(v)

        # roll a random number of edges
        rand_num_edges = random.randint(min_edges, max_edges)
        # if it's already connected to more vertices than 'rand_num_edges'
        if rand_num_edges <= len(u_neighbors):
            # skip the candidate filtering, sampling, and edge-adding steps entirely for this u
            continue

        # if u is not already connected to more vertices than 'rand_num_edges'
        # then candidates is ready to be selecetd from
        num_new_neighbors_needed = rand_num_edges - len(u_neighbors)

        new_neighbors = random.sample(list(candidates), num_new_neighbors_needed)
        for new_neighbor in new_neighbors:
            if use_random_weight:
                w = random.randint(min_weight, max_weight)
                g.add_edge(u, new_neighbor, weight=w)
            else:
                g.add_edge(u, new_neighbor)

    return g



def graph_from_json(json_str: str) -> nx.Graph:
    #
    # build an undirected networkx graph from a JSON string (e.g. from reading a file)
    #
    # expected format:
    #     {
    #         "vertices": [0, 1, ...],
    #         "edges": [
    #             [0, 1],  # unweighted edge
    #             [1, 3, 5], # weighted edge (must be positive)
    #             ...
    #         ]
    #     }
    #
    data = json.loads(json_str)

    g = nx.Graph()

    # 1. add all vertices first (captures isolated nodes with no edges)
    if "vertices" in data:
        g.add_nodes_from(data["vertices"])

    # 2. add edges, attaching 'weight' attribute when present
    if "edges" in data:
        for edge in data["edges"]:
            if len(edge) == 2:
                u, v = edge
                g.add_edge(u, v)
            elif len(edge) == 3:
                u, v, weight = edge
                assert weight > 0, "weight must be positive"
                g.add_edge(u, v, weight=weight)
            else:
                assert f"must have 2 or 3 elems"

    return g

###################################################################################
# path finding algorithms


# BFS (unweighted shortest path)
#
# inputs:
# graph object
# source vertex
# target vertex
#
# outputs:
# shortest path
# shortest distance (hop count)
def bfs_shortest_path(g, source, target):

    # BFS shortest path
    # treats all edges as weight = 1 (ignores actual weights)
    # returns (path_list, hop_count) or (none, inf)

    # if source vertex and target vertex do not exist in the graph
    if source not in g or target not in g:
        # return none for no path, and math.inf for no distance (infinitely far)
        return None, math.inf

    # create a dictionary to track which vertices have been visited
    # keys: vertices
    # values: predecessors
    # this allows us to reconstruct paths!!!!!!!!!!
    visited = {source: None}
    # starting predecessor is none because nothing comes before source at the beginning

    # create a double-ended queue (deque) from the provided list of vertices
    queue = deque([source])
    # a deque is like a list but optimized for adding/removing from both ends
    # deque is used because BFS works by processing vertices in the order they were discovered: first in, first out
    # the queue starts with the source vertex because we want to explore outward from the source
    #
    # list.pop(0) --> O(n) — shifts every element left to fill the gap
    # deque.popleft() --> O(1) — just moves a pointer

    # while there are items in the queue
    while queue:
        # take the vertex from the front of the queue (the oldest unprocessed vertex)
        # and assign it to node
        node = queue.popleft()

        # if this vertex equals the target vertex
        if node == target:
            # reconstruct the path
            path = []
            # our current vertex is the target vertex
            current = target
            while current is not None:
                # add the current vertex to path
                path.append(current)
                # re-assign current to the next predecessor
                current = visited[current]
            # re-order the path from source to target and return the hop count
            return list(reversed(path)), len(path) - 1

        # if this vertex does not equal the target vertex
        # look at its neighbors and continue to build the dictionary
        for neighbour in g.neighbors(node):
            # if neighbor vertex is not yet in the dictionary
            if neighbour not in visited:
                # add the vertex
                visited[neighbour] = node
                queue.append(neighbour)

    # if queue is exhausted and no path was found, return no path found and no distance (infinitely far)
    # empty queue = proof by exhaustion that target node is unreachable --> path is disconnected
    return None, math.inf



# dijkstra (weighted shortest path)
#
# inputs:
# graph object
# source vertex
# target vertex
#
# outputs:
# shortest path
# shortest distance
def dijkstra(g, source, target):

    # dictionary to track how far each vertex is from the source
    # keys: vertices
    # values: distances
    distance = {}
    for v in g.nodes():
        # every node starts at math.inf (no distance or infinitely far)
        # because we haven't explored anything yet
        distance[v] = math.inf

    # dictionary to reconstruct the shortest path
    # keys: vertex
    # values: the predecessor vertex that leads to it via the shortest path
    previous = {}
    for v in g.nodes():
        # every node's predecessor starts as none because no paths have been found yet
        previous[v] = None

    # set source distance to 0
    distance[source] = 0

    # heap (priority queue) items are tuples: (distance, vertex)
    # initialize the heap with the source vertex
    heap = [(0, source)]

    # while priority queue contains items
    while heap:
        # pop the smallest (closest) item from the priority queue and
        # unpack it into two variables: d: distance, u: vertex
        d, u = heapq.heappop(heap)

        # this entry is outdated, a shorter path to u was already found
        if d > distance[u]:
            # stop this iteration of the while loop
            continue
            # we never remove items from the heap so a node can appear multiple times with different distances

        # check if target vertex was reached
        if u == target:
            # exit the while loop
            break


        # UPDATE STEP
        # when we first added A to the heap with distance 10, we hadn't yet explored B
        # we had no way of knowing whether some other undiscovered path might offer a cheaper route to A or target
        #
        # if the entry is not outdated and u is not our target vertex:
        # iterate over every neighbor (v) of u
        #
        # g[u].items() returns (neighbour, edge_data) for every neighbor of u
        #
        # for neighbor vertex (v), neighbor vertex attribute (attrs) in g[u].items()
        for v, attrs in g[u].items():
            # get the edge weight between u and v
            # or default to 1 if it doesn't exist
            w = attrs.get("weight", 1)
            # calculate distance to neighbor v when travelling from u
            nd = distance[u] + w
            # if the new distance is shorter
            if nd < distance[v]:
                # update shortest distance to v with new value
                # "how far is v?"
                distance[v] = nd
                # update path to v with new vertex u
                # "how did we get to v?"
                previous[v] = u
                # add v to priority queue with new shorter distance
                heapq.heappush(heap, (nd, v))

    # if target was never reached
    if distance[target] == math.inf:
        # return no path found and no distance (infinitely far)
        return None, math.inf

    # target was found --> reconstruct the path
    path = []
    # work backwards, starting with the target vertex
    cur = target
    while cur is not None:
        path.append(cur)
        # re-assign current to the next predecessor
        cur = previous[cur]
    # re-order the path from source to target and return the total weight
    return list(reversed(path)), distance[target]




# floyd-warshall (weighted shortest paths)
#
# multi-source, multi-destination
#
# inputs:
# graph object
#
# outputs:
# nested dictionary mapping every vertex pair to the shortest distance between them
def floyd_warshall(graph):
    nodes = list(graph.nodes())


    # INITIALIZATION (0 to self, 1 or specified to neighbors, infinitely far away all others)
    # build a dictionary of distances between every pair of nodes
    #
    # outer dictionary maps nodes (keys) to dictionaries (values)
    dist = {}
    for u in nodes:
        # inner dictionary maps nodes (keys) to distances (values)
        dist[u] = {}
        for v in nodes:
            # a node will always have distance 0 to itself
            if u == v:
                dist[u][v] = 0
            else:
                # start by assuming no nodes can reach each other (infinitely far away)
                # this is for adjacent and non-adjacent vertices
                dist[u][v] = math.inf

    # refine adjacent vertex edge weights
    # iterate over edges in graph.edges
    # for node u, node v, and weight of edge u,v
    for u, v, data in graph.edges(data=True):
        # default weight to 1
        w = 1
        if "weight" in data:
            w = data["weight"]
        # distance from vertex u to v = distance from vertex v to u
        dist[u][v] = w
        dist[v][u] = w


    # the core of floyd-warshall: for every possible "middle stop" k,
    # check if going i → k → j is shorter than our current best i → j
    # after all iterations, dist[i][j] holds the true shortest path (smallest weight)
    for k in nodes:
        for i in nodes:
            for j in nodes:
                # if weight from i to k + weight from k to j < weight from i to j
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    # weight from i to k to j is better
                    dist[i][j] = dist[i][k] + dist[k][j]

    return dist


def eulerian_tour(g):
    #
    # find an eulerian circuit using hierholzer's algorithm
    #
    # an eulerian circuit visits every edge exactly once and returns to the start
    # precondition: the graph must be eulerian (connected, all vertices have even degree)
    #
    # algorithm (hierholzer's):
    #     1. start at any vertex, follow edges until returning to start (forming a cycle)
    #     2. if unvisited edges remain, find a vertex in the current path with unvisited edges
    #     3. start a new cycle from that vertex, splice it into the main path
    #     4. repeat until all edges are visited
    #
    # args:
    #     g: a networkx graph (must be eulerian)
    #
    # returns:
    #     list of vertices representing the eulerian circuit (first vertex == last vertex)


    # validate that all vertices have even degree and greater than zero degree
    for v in g.nodes():
        assert g.degree(v) % 2 == 0, f"vertex {v} has odd degree {g.degree(v)}"
        assert g.degree(v) > 0, f"vertex {v} has even degree {g.degree(v)}"

    # handling an edge case: no edges
    assert g.number_of_edges() > 0, f"graph has no edges"

    # create a dictionary describing the graph BEFORE any paths are taken
    # and use it later to track which edges have been used
    # keys are vertices
    # values are sets of neighbor vertices <-- sets enabale edge removal via discard()
    remaining = {}
    for v in g.nodes():
        remaining[v] = set(g.neighbors(v))

    # helper function to remove or "use" an edge from the dictionary
    def use_edge(u, v):
        # since graphs will be undirected we need to discard two instances of the edge
        # u is connected to v in one set in the dictionary
        # v is connected to u in another set in the dictionary
        remaining[u].discard(v)
        remaining[v].discard(u)

    # start the tour!

    # start from any vertex with edges (arbitrary choice since graph is eulerian)
    start = None
    for v in g.nodes():
        # check if vertex has unused edges
        # cannot be 0 because vertex must have > 0 edges
        if len(remaining[v]) > 0:
            start = v
            break

    path = [start]

    # PHASE 1: INITIAL CYCLE/PATH EXPLORATION
    # keep following edges until we return to the starting vertex

    # while current vertex has unexplored edges
    curr = start
    while len(remaining[curr]) > 0:

        # pick any available neighbor vertex (by turning set into list and grabbing first element)
        # then traverse the edge that connects to neighbor vertex
        next_v = list(remaining[curr])[0]
        # helper function to remove edge from dictionary
        use_edge(curr, next_v)
        # add vertex to path
        path.append(next_v)
        curr = next_v

    # PHASE 2: ITERATIVELY FIND VERTICES WITH UNUSED EDGES AND SPLICE IN NEW CYCLES
    # we linearly scan through the path to find vertices with remaining edges
    while True:
        # linear scan: find first vertex in path with unused edges
        splice_idx = None
        for i in range(len(path)):
            # check if set of vertices is not empty
            if remaining[path[i]]:
                splice_idx = i
                break

        # if no vertex has unused edges, we're done
        if splice_idx is None:
            break

        # build a new cycle from the vertex at splice_idx
        # explore greedily until returning to this vertex
        vertex_with_edges = path[splice_idx]
        new_cycle = [vertex_with_edges]
        curr = vertex_with_edges

        # keep following edges until we return to vertex_with_edges
        while len(remaining[curr]) > 0:

            # pick any available neighbor and traverse the edge
            next_v = list(remaining[curr])[0]
            # helper function to remove used edge
            use_edge(curr, next_v)
            new_cycle.append(next_v)
            curr = next_v

        # splice the new cycle into the path
        # remove the duplicate starting vertex (it's already in path at splice_idx)
        # insert the rest of the cycle after splice_idx
        #
        # use list slicing to splice in the new cycle
        path = path[:splice_idx + 1] + new_cycle[1:] + path[splice_idx + 1:]

    return path



# inputs:
# list of items to permute
#
# outputs:
# list of all permutations (each permutation is a list)
def generate_permutations(items: list) -> list[list]:
    # generate all permuations of a list using recursion
    # 1. base case: single element returns [[element]]
    # 2. recursive case: for each element, place it first and append
    #                   all permutations of the remaining elements

    # base case: single element (or empty) has only one permutation
    if len(items) <= 1:
        return [items]

    result: list[list] = []
    # try each item as the first element of a permutation
    for i, item in enumerate(items):
        # get all elements except the current item
        remaining = items[:i] + items[i + 1:]
        # recursively get all permutations of the remaining elements
        for perm in generate_permutations(remaining):
            # prepend current item to each permutation of remaining elements
            result.append([item] + perm)

    return result



# inputs:
# complete weighted graph
#
# outputs:
# tour as list of vertices
# total weight
#
# an exact solution to TSP by trying all permutations (all possible paths/arrangements of vertices!!!)
def tsp_brute_force(g):
    # find the minimum weight hamiltonian cycle (a tour visiting all vertices
    # exactly once and returning to the start) by exhaustive search
    # 1. fix the first vertex (reduces permutations by a factor of n)
    # 2. generate all permuations of remaining vertices
    # 3. for each permutation, calculate total tour weight
    # 4. track and return the minimum weight tour

    nodes = list(g.nodes())
    assert len(nodes) >= 2, "need at least 2 vertices for TSP"

    # fix first vertex to reduce permutations by factor of n (don't want duplicates)
    # all tours are cycles so starting point is arbitrary
    first = nodes[0]
    rest = nodes[1:]

    # track best tour found so far
    best_tour = []
    best_weight = math.inf

    # try every possible ordering of the remaining vertices
    for perm in generate_permutations(rest):
        # build complete tour: first -> perm[0] -> perm[1] -> ... -> first
        tour = [first] + perm + [first]

        # calculate total weight of this tour by summing edge weights
        total_weight = 0
        for i in range(len(tour) - 1):
            u, v = tour[i], tour[i + 1]
            # look up distance between u and v
            total_weight += g[u][v].get("weight", 1)

        # update best tour if this one is better
        if total_weight < best_weight:
            best_weight = total_weight
            best_tour = tour

    return best_tour, best_weight



# inputs:
# a complete weighted graph
# starting vertex, defaults to 0
#
#
# outputs:
# tuple[list[int], float]
# list of vertices ending at start
# total weight
#
# an approximate solution to TSP using nearest neighbor heuristic
def tsp_nearest_neighbor(g, start = None):
    # this algorithm is greedy and always moves to the nearest unvisited vertex
    # it's fast but may not find the optimal solution
    # 1. start at given vertex or at vertex 0
    # 2. repeat until all vertices visited:
    #   - find nearest unvisited neighbor
    #   - move to that neighbor, add edge weight to total
    # 3. return to starting vertex

    nodes = list(g.nodes())
    assert len(nodes) >= 2, "need at least 2 vertices for TSP"

    # use provided start vertex or default to first vertex
    if start is None:
        start = nodes[0]
    assert start in g, f"start vertex {start} not in graph"

    # keep track of visited vertices using a set
    visited = {start}

    # keep track of the path
    tour = [start]

    # total distance/weight so far
    total_weight = 0

    # current position
    current = start

    # greedy loop: repeatedly move to nearest unvisited neighbor
    while len(visited) < len(nodes):
        # find the nearest unvisited neighbor from current vertex
        nearest = None
        nearest_weight = math.inf

        for neighbor in g.neighbors(current):
            if neighbor not in visited:
                weight = g[current][neighbor].get("weight", 1)
                if weight < nearest_weight:
                    nearest = neighbor
                    nearest_weight = weight

        # if no unvisited neighbor exists, graph is not complete
        assert nearest is not None, "graph is not complete - no unvisited neighbor found"

        # move to the nearest neighbor
        visited.add(nearest)
        tour.append(nearest)
        total_weight += nearest_weight
        current = nearest

    # complete the cycle by returning to the start vertex
    total_weight += g[current][start].get("weight", 1)
    tour.append(start)

    return tour, total_weight




def main():

    # read command line arguments
    parser = argparse.ArgumentParser(description="graph analysis toolkit")

    # note that we force vertex names to be integers for simplicity
    parser.add_argument("--source", type=int, help="source vertex for path finding algorithm, only needed if path algorithm is bfs or dijkstra")
    parser.add_argument("--target", type=int, help="target vertex for path finding algorithm, only needed if path algorithm is bfs or dijkstra")

    parser.add_argument("--path-algorithm", type=str, help="one of (bfs, dijkstra, floyd, eulerian, tsp-brute, tsp-nn)")

    parser.add_argument("--json", type=str, help="json file with edges and vertices specified, this overrides the --type argument and uses the provided graph instead of generating one")

    parser.add_argument("--num-vertices", type=int, help="# of vertices, applicable for all graph types")
    parser.add_argument("--type", type=str, help="type of graph to build, one of (random, complete, regular, eulerian)")
    parser.add_argument("--k", type=int, help="K value to use for graph type = regular")

    parser.add_argument("--min-edges", type=int, help="only applicable for random type")
    parser.add_argument("--max-edges", type=int, help="only applicable for random type")

    parser.add_argument("--min-weight", type=int, help="applicable for random, complete, regular, eulerian")
    parser.add_argument("--max-weight", type=int, help="applicable for random, complete, regular, eulerian")

    # call to argument parse and save results to args
    args = parser.parse_args()

    # --json (given graph) gets priority
    if args.json is not None:
        with open(args.json, "r") as f:
            g = graph_from_json(f.read())

    # if json file is not specified, a specific graph type must be
    elif args.type == "complete":
        g = build_complete_graph(args.num_vertices, args.min_weight, args.max_weight)

    elif args.type == "regular":
        g = build_regular_graph_circulant(args.num_vertices, args.k, args.min_weight, args.max_weight)

    elif args.type == "random":
        # additional checks for random graphs
        assert args.min_edges < args.num_vertices, "min edges cannot be greater than num vertices"
        assert args.max_edges < args.num_vertices, "max edges cannot be greater than num vertices"
        assert args.min_edges < args.max_edges, "min edges cannot be greater than max edges"
        g = build_random_graph(args.num_vertices, args.min_edges, args.max_edges, args.min_weight, args.max_weight)

    elif args.type == "eulerian":
        # build a graph guaranteed to have an eulerian circuit (all vertices even degree, graph is connected)
        g = build_eulerian_graph(args.num_vertices, args.min_weight, args.max_weight)

    else:
        # if a json or specific graph type is not specified, it's invalid
        assert False, "invalid graph type"

    # path is a list of vertices
    path = []
    # path_distance is the distance from source target, found using the path algorithm of choice
    path_distance = 0



    # run the path finding algorithm of choice
    if args.path_algorithm == "bfs":
        assert args.source is not None
        assert args.target is not None
        result = bfs_shortest_path(g, args.source, args.target)
        path = result[0]
        path_distance = result[1]



    elif args.path_algorithm == "dijkstra":
        assert args.source is not None
        assert args.target is not None
        result = dijkstra(g, args.source, args.target)
        path = result[0]
        path_distance = result[1]



    elif args.path_algorithm == "floyd":
        floyd_result = floyd_warshall(g)

        # FLOYD APPLICATION 1: WAREHOUSE IN CITY
        # find vertex in graph from which the sum of the shortest
        # distances to all other vertices is minimum
        best_hub_vertex = 0
        best_hub_total_dist = math.inf
        # floyd result: nested dictionary (vertex -> vertex -> weight)
        for source_vertex in floyd_result:
            # first, find the sum of shortest path distances from source_vertex to all other vertices
            total_dist_from_source = 0
            for dest_vertex in floyd_result[source_vertex]:
                # sum each shortest path distance
                total_dist_from_source += floyd_result[source_vertex][dest_vertex]

            # if total_dist_from_source is smaller than the best_hub_total_dist found thus far,
            # source_vertex becomes the "best" vertex so far
            if total_dist_from_source < best_hub_total_dist:
                best_hub_vertex = source_vertex
                best_hub_total_dist = total_dist_from_source

        # FLOYD APPLICATION 2: FIRE STATION IN CITY
        # find vertex in graph such that the vertex
        # furthest from it is as close as possible
        best_station_vertex = 0
        best_station_max_dist = math.inf

        # first, find the longest shortest path from source_vertex to any destination vertex
        # "finding the max"
        for source_vertex in floyd_result:
            max_dist_from_source = 0
            # for vertex pair (source_vertex, dest_vertex) mapped to distance between them
            for dest_vertex in floyd_result[source_vertex]:
                # if new distance is greater
                if max_dist_from_source < floyd_result[source_vertex][dest_vertex]:
                    # assign new longest shortest path
                    max_dist_from_source = floyd_result[source_vertex][dest_vertex]

            # "finding the min of the maxes"
            # if max_dist_from_source is smaller than the best_station_max_dist found thus far,
            # source_vertex becomes the "best" vertex so far
            if max_dist_from_source < best_station_max_dist:
                best_station_vertex = source_vertex
                best_station_max_dist = max_dist_from_source

        print("Floyd:")
        print(f"  vertex with minimum sum of the shortest distances to all other vertices: {best_hub_vertex}")
        print(f"    best hub total distance: {best_hub_total_dist}")
        print(f"  vertex such that the furthest vertex is as close as possible: {best_station_vertex}")
        print(f"    furthest distance: {best_station_max_dist}")



    elif args.path_algorithm == "eulerian":
        # find eulerian tour (visits every edge exactly once)
        path = eulerian_tour(g)
        # for eulerian tour, "distance" is total edge count
        path_distance = len(path) - 1
    elif args.path_algorithm == "tsp-brute":
        # solve TSP exactly using brute-force enumeration
        path, path_distance = tsp_brute_force(g)
    elif args.path_algorithm == "tsp-nn":
        # solve TSP approximately using nearest neighbor heuristic
        start = args.source if args.source is not None else 0
        path, path_distance = tsp_nearest_neighbor(g, start)

    print(g)

    if path is None:
        print(f"No path found!")
    else:
        # now, turn 'path' into a list of edges so that we can highlight them a
        # different color in the graph visualization
        edges_in_path = []
        # use i to access all but the last element
        for i in range(len(path) - 1):
            u = path[i]
            v = path[i+1]
            edges_in_path.append((u, v))

        # separate edges into those in the path and those not in the path for visualization
        edges_not_in_path = []
        # create set with both (u,v) and (v,u) since graph is undirected
        edges_in_path_set = set(edges_in_path) | {(v, u) for u, v in edges_in_path}
        for u, v in g.edges():
            if (u, v) not in edges_in_path_set and (v, u) not in edges_in_path_set:
                edges_not_in_path.append((u, v))

        if args.path_algorithm == "bfs" or args.path_algorithm == "dijkstra":
            print(f"shortest path from {args.source} to {args.target}:")
            print(f"  algorithm: {args.path_algorithm}")
            print(f"  path:      {path}")
            print(f"  distance:  {path_distance}")
        elif args.path_algorithm == "eulerian":
            print(f"Eulerian tour:")
            print(f"  path:      {path}")
            print(f"  edges:     {path_distance}")
        elif args.path_algorithm == "tsp-brute":
            print(f"TSP brute-force tour:")
            print(f"  path:      {path}")
            print(f"  edges:     {path_distance}")
        elif args.path_algorithm == "tsp-nn":
            print(f"TSP nearest-neighbor tour:")
            print(f"  path:      {path}")
            print(f"  edges:     {path_distance}")



    plt.figure(figsize=(12, 10))
    plt.title("graph")

    pos = nx.circular_layout(g)
    # draw nodes, edges, and labels as separate layers
    # this gives independent control over styling each element
    nx.draw_networkx_nodes(g, pos, node_size=700, node_color="red")

    if len(edges_not_in_path) > 0:
        nx.draw_networkx_edges(g, pos, edgelist=edges_not_in_path, width=1, alpha=1, edge_color="black")
    nx.draw_networkx_edges(g, pos, edgelist=edges_in_path,     width=8, alpha=1, edge_color="green")

    nx.draw_networkx_labels(g, pos, font_size=12, font_color="yellow")

    edge_labels = nx.get_edge_attributes(g, "weight")   # → {(0,1): 0.5, ...}
    nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels)

    plt.axis("off")
    plt.tight_layout()
    plt.savefig("graph.png") # for now, just save to graph.png
    plt.show()

main()

