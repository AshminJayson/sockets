from tabulate import tabulate

class Router:
    def __init__(self, name):
        self.name = name
        self.distance_vector = {self.name: 0}
        self.neighbors = {}

    def add_neighbor(self, neighbor, cost):
        self.neighbors[neighbor] = cost
        self.distance_vector[neighbor] = cost

    def send_distance_vector(self):
        return {self.name: self.distance_vector}

    def receive_distance_vector(self, neighbor, received_vector):
        updated = False
       
        for _, sepdict in received_vector.items():
            for destination, cost in sepdict.items():
                

                total_cost = cost + self.neighbors.get(neighbor, 0)
                if self.update_distance_vector(destination, total_cost):
                    updated = True
                    print(f"{self.name}: Updated distance to {destination} via {neighbor} to {total_cost}")
        return updated

    def update_distance_vector(self, destination, new_distance):
        current_distance = self.distance_vector.get(destination, float('inf'))
        if new_distance < current_distance:
            self.distance_vector[destination] = new_distance
            return True
        return False

def get_test_cases():
    router_a = Router('A')
    router_b = Router('B')
    router_c = Router('C')


    router_a.add_neighbor('B', 1)
    router_b.add_neighbor('C', 2)
    router_c.add_neighbor('A', 5)
    
    return [router_a, router_b, router_c]


def simulate_network():
    input_routers = {}
    edges = set()
    while True:
        from_node = input('Enter Router Name or 0 : ')
        if from_node == '0': break
        temp = Router(from_node)
        input_routers[from_node] = temp

        print("Neighbour distances(neighbor -space- distance) or 0")
        while True:
            x = input()
            if x == '0': break
            to_node, dist = x.split(' ')
            dist = int(dist)
            edges.add((from_node, to_node, dist))

    for fro, to, dist in edges:
        source = input_routers[fro]
        source.add_neighbor(to, dist)

    routers = list(input_routers.values())

    for router in routers:
        print(router.neighbors)

    for _ in range(5):
        print("\n---- Simulation Step ----")
        updated_routers = []
        for router in routers:
            for neighbor, _ in router.neighbors.items():
                neighbor_router = next(r for r in routers if r.name == neighbor)
                updated = neighbor_router.receive_distance_vector(router.name, router.send_distance_vector())
                if updated:
                    updated_routers.append(neighbor_router)
                    print("\nRouting Tables:")
                    for router in routers:
                        print(f"{router.name}: {router.distance_vector}")

        if not updated_routers:
            print("Convergence reached.")
            break

simulate_network()
