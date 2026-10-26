# Compute the shortest path in network with Dijkstra algorithm

import math
import random
import sys
from collections import deque

INFINITY = float("inf")


# router name n°i : A, B, C... (R27, R28... after 26 routers)
def router_name(i):
    return chr(ord("A") + i) if i < 26 else f"R{i + 1}"

# Print order A to Z then R27, R28.. 
# Sort by length then alphabetic order
def sort_key(name):
    return (len(name), name)

#close properly (CTL+D) with input()
def ask(prompt):
    try: 
        return input(prompt)
    except EOFError:
        print("\nInput closed, exiting.")
        sys.exit(1)

# 0a. aleatory network generation (different at each run)
def generate_network():
    nb_routers = random.randint(5, 8)
    routers = [router_name(i) for i in range(nb_routers)]
    links = []

    # new router always link to a router already in the network -> all linked
    for i in range(1, nb_routers):
        links.append((routers[i], random.choice(routers[:i]), random.randint(1, 10)))

    # try supplement link random
    for _ in range(nb_routers):
        r1, r2 = random.sample(routers, 2)
        already_exists = any({r1, r2} == {a, b} for a, b, c in links)
        if not already_exists:
            links.append((r1, r2, random.randint(1, 10)))

    # add a isolate router at 1 over 3 (unreachable destination)
    if random.random() < 1 / 3:
        routers.append(router_name(nb_routers))

    return routers, links


# 0b. We enter the network as a adjacency matrix
def matrix():
    while True:
        try:
            n = int(ask("Number of routers: "))
            if n >= 2:
                break
        except ValueError:
            pass
        print("  Please enter an integer greater than or equal to 2.")

    routers = [router_name(i) for i in range(n)]
    print(f"Enter the matrix row by row ({n} numbers separated with spaces).")
    print("0 = no link. The diagonal must be 0 and the matrix symmetric.")
    print("Column order: " + " ".join(routers))

    costs = []
    for i in range(n):
        while True:
            try:
                line = [float(x) for x in ask(f"  Row {routers[i]}: ").split()]
            except ValueError:
                print("    Numbers only.")
                continue
            if len(line) != n:
                print(f"    Exactly {n} numbers are required.")
            elif any(x < 0 for x in line):
                print("    Costs must be positive (0 = no link).")
            elif any(not math.isfinite(x) for x in line):
                print("    Costs must be finite numbers (0 = no link).")
            elif line[i] != 0:
                print("    The diagonal must be 0 (a router is not linked to itself).")
            elif any(line[j] != costs[j][i] for j in range(i)):
                print("    The matrix must be symmetric: cost X-Y must equal cost Y-X.")
            else:
                break
        costs.append([int(x) if x.is_integer() else x for x in line])

    # transform matrix in list of edges 
    links = []
    for i in range(n):
        for j in range(i + 1, n):
            if costs[i][j] > 0:
                links.append((routers[i], routers[j], costs[i][j]))
    return routers, links


# Menu :type of the network
def choose_network():
    print("How do you want to create the network?")
    print("  1. Random network")
    print("  2. Enter an adjacency matrix")
    user = ask("Your choice (1 or 2): ").strip()
    while user not in ("1", "2"):
        user = ask("Please type 1 or 2: ").strip()
    print()
    if user == "1":
        return generate_network()
    return  matrix()


# 1. Create the network : adjacency matrix {router: {neighbor: weight}}
def create_reseau(routers, links):
    network = {r: {} for r in routers}
    for r1, r2, weight in links:
        if r1 == r2:
            raise ValueError(f"Link {r1}-{r2}: a router cannot be linked to itself")
        if weight <= 0 or not math.isfinite(weight):
            raise ValueError(f"Link {r1}-{r2}: cost must be positive (got {weight})")
        if r2 in network[r1]:
            raise ValueError(f"Link {r1}-{r2}: duplicate link")
        network[r1][r2] = weight
        network[r2][r1] = weight   # edge in both way
    return network


# 2. LSDB : each router know, all other routers, their neighbor and their weight
def lsa(network, router, sequence=1):
    return {"origin" : router, "seq": sequence,  "links": dict(network[router])}


def build_lsdb(network):
    """ Return the LSDB of each router """
    lsdb = {r: {} for r in network}
    tmp = deque()
    for router in network:
        lsa_value = lsa(network, router)
        lsdb[router][router] = lsa_value
        tmp.append((router, lsa_value))
    while tmp:
        x, lsa_value = tmp.popleft()
        for neighbor in network[x]:
            currently = lsdb[neighbor].get(lsa_value["origin"])
            if currently is None or lsa_value["seq"] > currently["seq"]:
                lsdb[neighbor][lsa_value["origin"]] = lsa_value
                tmp.append((neighbor, lsa_value))
    return lsdb


def topology(lsdb_router):
    """Graph seen by one router: a link is kept only if both routers announce it."""
    topo = {origin: {} for origin in lsdb_router}
    for origin, adv in lsdb_router.items():
            for neighbor, weight in adv["links"].items():
                pair = lsdb_router.get(neighbor)
                if pair is not None and origin in pair["links"]:
                    topo[origin][neighbor] = weight
    return topo


# 3. Dijkstra algorithm
def dijkstra(topo, source, all_router):
    distance = {r: INFINITY for r in all_router}
    edge_before = {r: None for r in all_router}
    distance[source] = 0
    visited = set()

    while True:
        # pick the nearest non visited router
        u = None
        for r in all_router:
            if r in visited or distance[r] == INFINITY:
                continue
            if u is None or distance[r] < distance[u]:
                u = r
        if u is None:          # nothing more reachable
            break
        visited.add(u)

        # update the edges and neighbor
        for neighbor, cost in topo[u].items():
            if distance[u] + cost < distance[neighbor]:
                distance[neighbor] = distance[u] + cost
                edge_before[neighbor] = u

    return distance, edge_before


# Complete path from source to a destination (None if not reachable)
def shortest_path(edge_before, distance, source, destination):
    if distance[destination] == INFINITY:
        return None
    path = [destination]
    while path[-1] != source:
        path.append(edge_before[path[-1]])
    return path[::-1]


# 4. Routing table : destination -> next hop
def routing_table(edge_before, distance, source):
    table = {}
    for dest in distance:
        if dest != source:
            route = shortest_path(edge_before, distance, source, dest)
            table[dest] = route[1] if route else None
    return table


# 5. Print 
def print_network(network):
    routers = sorted(network, key=sort_key)
    print("\nNetwork (cost matrix, '.' = no link):")
    print("     " + "".join(f"{r:>4}" for r in routers))
    for r1 in routers:
        line = f"  {r1:<3}"
        for r2 in routers:
            value = "-" if r1 == r2 else network[r1].get(r2, ".")
            line += f"{value:>4}"
        print(line)


def draw_tree(lsdb, edge_before, distance, source):
    # children of each router, found from its edge_before (its parent)
    child = {r: [] for r in edge_before}
    for r, p in edge_before.items():
        if p is not None:
            child[p].append(r)
    for r in child:
        child[r].sort(key=sort_key)
        
    print(f"  {source}")
    # a stack instead of recursion: no limit on the depth of the tree
    
    kids = child[source]
    stack = [(c, "", i == len(kids) - 1) for i, c in enumerate(kids)]
    stack.reverse()
    while stack:
        node, indent, last = stack.pop()
        branch = "└── " if last else "├── "
        parent = edge_before[node]
        
        print(f"  {indent}{branch}{node}  "
            f"(link {lsdb[parent][node]}, total {distance[node]})")
        
        kids = child[node]
        below = indent + ("    " if last else "│   ")
        pending = [(c, below, i == len(kids) - 1) for i, c in enumerate(kids)]
        pending.reverse()
        stack.extend(pending)


def show_results(router, lsdb, topo, distance, edge_before, table, all_router):
    print("\n" + "=" * 15, "Router", router, "=" * 15)

    print("LSDB:")
    for origin in sorted(lsdb, key=sort_key):
        entry = lsdb[origin]
        neighbors = sorted(entry["links"].items(), key=lambda kv: sort_key(kv[0]))
        text = ", ".join(f"{v}({c})" for v, c in neighbors)
        print(f"  {origin} (seq {entry['seq']}): {text or 'no neighbors'}")
    unknown = [r for r in all_router if r not in lsdb]
    if unknown:
        print(f"  No LSA received from: {', '.join(unknown)}")

    print("Shortest path tree:")
    draw_tree(topo, edge_before, distance, router)

    print("Distances and paths:")
    for dest in all_router:
        route = shortest_path(edge_before, distance, router, dest)
        if route:
            print(f"  {dest}: distance {distance[dest]}, predecessor {edge_before[dest] or '-'}, "
                f"path {' -> '.join(route)}")
        else:
            print(f"  {dest}: unreachable")

    print("Routing table:")
    print("  Destination | Next hop      | Cost")
    for dest, next_hop in sorted(table.items(), key=lambda kv: sort_key(kv[0])):
        if next_hop:
            print(f"  {dest:<11} | {next_hop:<13} | {distance[dest]}")
        else:
            print(f"  {dest:<11} | {'-':<13} | unreachable")


# Main
def main():
    routers, links = choose_network()
    try:
        network = create_reseau(routers, links)
    except ValueError as e:
        print("Error:", e)
        sys.exit(1)

    print_network(network)
    all_routers = sorted(network, key=sort_key)
    lsdbs = build_lsdb(network)

    for router in all_routers:          # Dijkstra from each router
        topo = topology(lsdbs[router])
        distance, edge_before= dijkstra(topo, router, all_routers)
        table = routing_table(edge_before, distance, router)
        show_results(router, lsdbs[router], topo, distance, edge_before, table, all_routers)
        
if __name__ == "__main__":
    main()
