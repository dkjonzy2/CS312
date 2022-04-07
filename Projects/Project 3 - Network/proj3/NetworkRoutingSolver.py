#!/usr/bin/python3


from CS312Graph import *
import time

# Unsorted Array implementation of a priority queue
class PriorityQueueArray:
    def __init__(self):
        self.set = set()

    # Insert a node into the array
    def insertNode(self, index):
        self.set.add(index)

    # return node with the smallest distance, remove from list
    def deleteMin(self, dist):
        minIndex = next(iter(self.set)) # gets first element from set
        for num in self.set:
            if dist[num] == float('inf'):
                continue
            elif dist[minIndex] is float('inf') or dist[num] < dist[minIndex]:
                minIndex = num
        self.set.remove(minIndex)
        return minIndex

    # decrease the dist value at that index
    def decreaseKey(self, index, newDist):
        pass

    # Check if tree has more items
    def isEmpty(self):
        if len(self.set) == 0:
            return True
        else:
            return False


class PriorityQueueHeap:
    def __init__(self):
        self.tree = []
        self.pointers = []

    # Insert a new node
    def insertNode(self, node_id):
        # Put new node into next stop
        loc = len(self.tree)
        self.pointers.append(loc)
        self.tree.append((node_id, float('inf')))
        # Bubble up not necessary here as all inserts will have inf distance

    # return and remove the minimum node
    def deleteMin(self, dist):
        # Catch error case where only 1 item in tree
        if len(self.tree) == 1:
            topNode_id, topNode_dist = self.tree.pop()
            return topNode_id
        # Get top node and remove from tree
        topNode_id, topNode_dist = self.tree[0]
        self.pointers[topNode_id] = None
        # move last node to top
        self.tree[0] = self.tree[-1]
        self.tree.pop()
        # Bubble top node down
        bottomNode_id, bottomNode_dist = self.tree[0]
        self.pointers[bottomNode_id] = 0
        self.bubbleDown(bottomNode_id)
        return topNode_id

    # lower the value of a node
    def decreaseKey(self, node_id, newDist):
        # get location from pointers
        loc = self.pointers[node_id]
        # Change value at that location
        self.tree[loc] = (node_id, newDist)
        # Bubble up
        self.bubbleUp(node_id)

    # Bubble a value up in the tree
    def bubbleUp(self, node_id):
        cur_id = node_id
        while True:
            cur_loc = self.pointers[cur_id]
            if cur_loc == 0:  # Check for top
                break
            parent_loc = (cur_loc - 1) // 2
            cur_id, cur_value = self.tree[cur_loc]
            parent_id, parent_value = self.tree[parent_loc]
            if cur_value < parent_value:  # swap child with parent if less
                self.tree[parent_loc] = self.tree[cur_loc]
                self.pointers[cur_id] = parent_loc
                self.tree[cur_loc] = (parent_id, parent_value)
                self.pointers[parent_id] = cur_loc
            else:
                break

    # Bubble a value down in the tree
    def bubbleDown(self, node_id):
        cur_id = node_id
        while True:
            cur_loc = self.pointers[cur_id]
            first_child_loc = round((cur_loc + 0.5) * 2)
            second_child_loc = (cur_loc + 1) * 2
            cur_id, cur_value = self.tree[cur_loc]
            # Check if children are valid
            maxLoc = len(self.tree) - 1
            if first_child_loc > maxLoc and second_child_loc > maxLoc:
                break
            else:
                if first_child_loc > maxLoc:
                    first_child_value = float('inf')
                    second_child_id, second_child_value = self.tree[second_child_loc]
                elif second_child_loc > maxLoc:
                    first_child_id, first_child_value = self.tree[first_child_loc]
                    second_child_value = float('inf')
                else:
                    first_child_id, first_child_value = self.tree[first_child_loc]
                    second_child_id, second_child_value = self.tree[second_child_loc]

            if first_child_value <= second_child_value:
                child_id = first_child_id
                child_value = first_child_value
                child_loc = first_child_loc
            else:
                child_id = second_child_id
                child_value = second_child_value
                child_loc = second_child_loc
            if cur_value > child_value:  # swap child with parent if less
                self.tree[child_loc] = self.tree[cur_loc]
                self.pointers[cur_id] = child_loc
                self.tree[cur_loc] = (child_id, child_value)
                self.pointers[child_id] = cur_loc
            else:
                break

    # Check if tree has more items
    def isEmpty(self):
        if len(self.tree) == 0:
            return True
        else:
            return False


class NetworkRoutingSolver:
    def __init__(self):
        self.dist = None
        self.prev = None
        self.source = None
        self.dest = None
        self.network = None

    def initializeNetwork(self, network):
        assert (type(network) == CS312Graph)
        self.network = network

    def getShortestPath(self, destIndex):
        self.dest = destIndex
        path_edges = []
        total_length = self.dist[self.dest]
        index = self.dest

        # Check for unreachable
        if self.prev[destIndex] is None:
            return {'cost': float('inf'),
                    'path': path_edges}

        # search backwards using prev pointers to find all edges used
        while self.prev[index] is not None:
            previous = self.prev[index]
            prevNode = self.network.nodes[previous]
            for edge in prevNode.neighbors:
                if edge.dest.node_id == index:
                    path_edges.append((edge.src.loc, edge.dest.loc, '{:.0f}'.format(edge.length)))
            index = previous

        return {'cost': total_length, 'path': path_edges}

    def computeShortestPaths(self, srcIndex, use_heap=False):
        self.source = srcIndex
        t1 = time.time()

        # Choose which heap implementation to use
        if use_heap:
            print("Using heap implementation")
            Q = PriorityQueueHeap()
        else:
            print("Using array implementation")
            Q = PriorityQueueArray()

        dist = []
        prev = []
        # load the queue with all the points
        for i in range(len(self.network.nodes)):
            dist.insert(i, float('inf'))
            prev.insert(i, None)
            Q.insertNode(i)
        dist[srcIndex] = 0
        Q.decreaseKey(srcIndex, 0)

        # loop until queue is empty
        while not Q.isEmpty():
            # get minimum node from queue
            uInd = Q.deleteMin(dist)

            # check if queue is still returning reachable nodes
            if dist[uInd] == float('inf'):
                print("All reachable nodes searched")
                break

            # update values for each neighboring node
            for edge in self.network.nodes[uInd].neighbors:
                vInd = edge.dest.node_id
                newDist = dist[uInd] + edge.length
                if dist[vInd] == float('inf') or newDist < dist[vInd]:
                    dist[vInd] = newDist
                    prev[vInd] = uInd
                    Q.decreaseKey(vInd, newDist)

        # set values for use in getPath function
        self.dist = dist
        self.prev = prev
        t2 = time.time()
        return t2 - t1
