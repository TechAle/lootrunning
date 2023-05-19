import cv2
import numpy as np
from numpy.random import choice as np_choice

# Source: https://github.com/Akavall/AntColonyOptimization/blob/master/ant_colony.py
class AntColony(object):

    def __init__(self, distances, n_ants, n_best, n_iterations, decay, alpha=1, beta=1, backStart = True, maxSelfPath = 999999):
        """
        Args:
            distances (2D numpy.array): Square matrix of distances. Diagonal is assumed to be np.inf.
            n_ants (int): Number of ants running per iteration
            n_best (int): Number of best ants who deposit pheromone
            n_iteration (int): Number of iterations
            decay (float): Rate it which pheromone decays. The pheromone value is multiplied by decay, so 0.95 will lead to decay, 0.5 to much faster decay.
            alpha (int or float): exponenet on pheromone, higher alpha gives pheromone more weight. Default=1
            beta (int or float): exponent on distance, higher beta give distance more weight. Default=1

        Example:
            ant_colony = AntColony(german_distances, 100, 20, 2000, 0.95, alpha=1, beta=2)
        """
        self.distances  = distances
        self.pheromone = np.ones(self.distances.shape) / len(distances)
        self.all_inds = range(len(distances))
        self.n_ants = n_ants
        self.n_best = n_best
        self.n_iterations = n_iterations
        self.decay = decay
        self.alpha = alpha
        self.beta = beta
        self.backStart = backStart
        self.maxSelfPath = maxSelfPath

    def run(self, draw, chests):
        samePath = 0
        shortest_path = None
        all_time_shortest_path = ("placeholder", np.inf)
        prevScore = -1
        display = None

        for i in range(self.n_iterations):
            all_paths = self.gen_all_paths()
            self.spread_pheronome(all_paths, self.n_best, shortest_path=shortest_path)
            shortest_path = min(all_paths, key=lambda x: x[1])
            if shortest_path[1] < all_time_shortest_path[1]:
                all_time_shortest_path = shortest_path
                samePath = 0
            else:
                if all_time_shortest_path[1] == prevScore:
                    samePath += 1
                    if self.maxSelfPath < samePath:
                        print("stuck")
                        break
                else:
                    samePath = 0
                    prevScore = all_time_shortest_path[1]
            self.pheromone = self.pheromone * self.decay
            if True:
                display = self.updateMapAnts(draw.copy(), all_time_shortest_path[0], shortest_path[0], all_time_shortest_path[1], shortest_path[1], chests)
        if self.maxSelfPath >= samePath:
            print("End iterations")
        return all_time_shortest_path, display

    def getCordsById(self, id, chests):
        for i in chests:
            if i.graphs.id == id:
                return (i.avgX, i.avgY)
        return None
    def updateMapAnts(self, display, pathOptimized, pathUnoptimized, costsOptimized, costsUnoptimized, chests):

        pathOptimizedConnections = []
        pathUnoptimizedConnections = []

        firstBreak = False
        for chest in chests:
            if chest.graphs.id == pathUnoptimized[0][0]:
                pathUnoptimizedConnections.append(chest)
                if firstBreak:
                    break
                else:
                    firstBreak = True
            if chest.graphs.id == pathOptimized[0][0]:
                pathOptimizedConnections.append(chest)
                if firstBreak:
                    break
                else:
                    firstBreak = True

        for opt, unopt in zip(pathOptimized, pathUnoptimized):
            firstBreak = False
            for chest in chests:
                if chest.graphs.id == opt[1]:
                    pathOptimizedConnections.append(chest)
                    if firstBreak:
                        break
                    else:
                        firstBreak = True
                if chest.graphs.id == unopt[1]:
                    pathUnoptimizedConnections.append(chest)
                    if firstBreak:
                        break
                    else:
                        firstBreak = True

        # Display best path
        for i in range(len(pathOptimizedConnections) - 1):
            display = cv2.line(display, (pathOptimizedConnections[i].avgX, pathOptimizedConnections[i].avgY),
                               (pathOptimizedConnections[i + 1].avgX, pathOptimizedConnections[i + 1].avgY), (255, 255, 0), 2)

        # Display current test
        for i in range(len(pathUnoptimizedConnections) - 1):
            display = cv2.line(display, (pathUnoptimizedConnections[i].avgX, pathUnoptimizedConnections[i].avgY),
                               (pathUnoptimizedConnections[i + 1].avgX, pathUnoptimizedConnections[i + 1].avgY), (0, 255, 255), 1)

        # Display text
        display = cv2.putText(display, "Best costs: " + str(costsOptimized), (120, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                              (255, 255, 0), 1, cv2.LINE_AA)
        display = cv2.putText(display, "Current costs: " + str(costsUnoptimized), (460, 250), cv2.FONT_HERSHEY_SIMPLEX,
                              0.5,
                              (0, 255, 255), 1, cv2.LINE_AA)

        display = cv2.circle(display, (pathOptimizedConnections[0].avgX, pathOptimizedConnections[0].avgY,), 10,
                             (255, 255, 255), 2)

        cv2.imshow("Lootrunning", display)
        cv2.waitKey(1)
        return display

    def spread_pheronome(self, all_paths, n_best, shortest_path):
        sorted_paths = sorted(all_paths, key=lambda x: x[1])
        for path, dist in sorted_paths[:n_best]:
            for move in path:
                self.pheromone[move] += 1.0 / self.distances[move]

    def gen_path_dist(self, path):
        total_dist = 0
        for ele in path:
            total_dist += self.distances[ele]
        return total_dist

    def gen_all_paths(self):
        all_paths = []
        for i in range(self.n_ants):
            path = self.gen_path(0)
            all_paths.append((path, self.gen_path_dist(path)))
        return all_paths

    def gen_path(self, start):
        path = []
        visited = set()
        visited.add(start)
        prev = start
        for i in range(len(self.distances) - 1):
            move = self.pick_move(self.pheromone[prev], self.distances[prev], visited)
            path.append((prev, move))
            prev = move
            visited.add(move)
        if self.backStart:
            path.append((prev, start)) # going back to where we started
        return path

    def pick_move(self, pheromone, dist, visited):
        pheromone = np.copy(pheromone)
        pheromone[list(visited)] = 0

        row = pheromone ** self.alpha * (( 1.0 / dist) ** self.beta)

        norm_row = row / row.sum()
        move = np_choice(self.all_inds, 1, p=norm_row)[0]
        return move

