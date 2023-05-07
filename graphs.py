class graphs:
    ID = 0

    def __init__(self):
        self.preferedConnections = []
        self.id = graphs.ID
        graphs.ID += 1
        self.everyConnections = []
        self.visited = False
        self.toIgnore = []
        self.blackList = []

    def containsIgnore(self, id):
        for ignore in self.toIgnore:
            if ignore.reference.graphs.id == id:
                return True
        return False

    def addPreferedConnection(self, costs, reference):
        self.preferedConnections.append(connection(costs, reference))

    def addEveryConnections(self, N_DEEP, connections):
        keys = list(connections.keys())
        for i in range(len(connections)):
            costs = keys[i]
            value = connections[costs]
            toAdd = connection(costs, value)
            if i < N_DEEP:
                self.preferedConnections.append(toAdd)
            self.everyConnections.append(toAdd)


class connection:
    def __init__(self, costs, reference):
        self.costs = costs
        self.reference = reference
