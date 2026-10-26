# Computer Networks 2 - Link state routing with Dijkstra

import random
import sys

INF = float("inf")


def router_name(i):
    # A, B, C ... then R27, R28 if there are more than 26 routers
    if i < 26:
        return chr(65 + i)
    return "R" + str(i + 1)


def random_network():
    n = random.randint(5, 8)
    routers = [router_name(i) for i in range(n)]
    links = []

    # each new router is linked to one already placed -> the network is connected
    for i in range(1, n):
        neighbor = random.choice(routers[:i])
        links.append((routers[i], neighbor, random.randint(1, 10)))

    # add some random links
    for k in range(n):
        a, b = random.sample(routers, 2)
        exists = False
        for (x, y, c) in links:
            if (x == a and y == b) or (x == b and y == a):
                exists = True
        if not exists:
            links.append((a, b, random.randint(1, 10)))

    # one time out of three we add an isolated router (to test unreachable destinations)
    if random.randint(1, 3) == 1:
        routers.append(router_name(n))

    return routers, links


def read_row(name, n):
    while True:
        try:
            values = [int(x) for x in input("  Row " + name + ": ").split()]
        except ValueError:
            print("  -> integers only please")
            continue
        if len(values) == n:
            return values
        print("  -> you need", n, "values")


def enter_matrix():
    n = int(input("Number of routers: "))
    routers = [router_name(i) for i in range(n)]
    print("Enter the adjacency matrix row by row (0 = no link)")
    print("Column order:", " ".join(routers))

    mat = []
    for i in range(n):
        mat.append(read_row(routers[i], n))

    links = []
    for i in range(n):
        for j in range(i + 1, n):
            if mat[i][j] != mat[j][i]:
                print("Error: the matrix must be symmetric (", routers[i], "-", routers[j], ")")
                sys.exit(1)
            if mat[i][j] != 0:
                links.append((routers[i], routers[j], mat[i][j]))
    return routers, links


# Adjacency list: graph[router] = {neighbor: cost}
def build_graph(routers, links):
    graph = {}
    for r in routers:
        graph[r] = {}
    for (a, b, cost) in links:
        if cost <= 0:
            print("Error: link", a, "-", b, "has an invalid cost (", cost, "), costs must be positive")
            sys.exit(1)
        graph[a][b] = cost
        graph[b][a] = cost
    return graph


# LSDB of a router: it receives (by flooding) the LSA of every router it can reach.
# An LSA = the list of neighbors of a router with the costs.
def build_lsdb(graph, router):
    lsdb = {}
    to_visit = [router]
    while len(to_visit) > 0:
        r = to_visit.pop(0)
        if r in lsdb:
            continue
        lsdb[r] = dict(graph[r])
        for v in graph[r]:
            if v not in lsdb:
                to_visit.append(v)
    return lsdb


def dijkstra(lsdb, source, routers):
    dist = {}
    pred = {}
    for r in routers:
        dist[r] = INF
        pred[r] = None
    dist[source] = 0
    visited = []

    while True:
        # pick the closest router not visited yet
        u = None
        for r in routers:
            if r not in visited and dist[r] != INF:
                if u is None or dist[r] < dist[u]:
                    u = r
        if u is None:
            break  # nothing else is reachable
        visited.append(u)

        # update the neighbors of u
        for v in lsdb[u]:
            if dist[u] + lsdb[u][v] < dist[v]:
                dist[v] = dist[u] + lsdb[u][v]
                pred[v] = u

    return dist, pred


def get_path(pred, source, dest):
    p = [dest]
    while p[0] != source:
        p.insert(0, pred[p[0]])
    return p


def routing_table(dist, pred, source, routers):
    table = {}
    for d in routers:
        if d == source:
            continue
        if dist[d] == INF:
            table[d] = None
        else:
            table[d] = get_path(pred, source, d)[1]  # next hop
    return table


def print_network(graph, routers):
    print("\nCost matrix (. = no link)")
    print("     " + "".join(r.rjust(4) for r in routers))
    for a in routers:
        line = "  " + a.ljust(3)
        for b in routers:
            if a == b:
                line += "-".rjust(4)
            elif b in graph[a]:
                line += str(graph[a][b]).rjust(4)
            else:
                line += ".".rjust(4)
        print(line)


def print_tree(pred, dist, routers, node, level=0):
    if level == 0:
        print("  " + node)
    else:
        print("  " + "    " * (level - 1) + "|-- " + node + " (" + str(dist[node]) + ")")
    for r in routers:
        if pred[r] == node:
            print_tree(pred, dist, routers, r, level + 1)


def main():
    print("=== Shortest paths with Dijkstra ===")
    print("1 - random network")
    print("2 - enter an adjacency matrix")
    choice = input("Choice: ")
    if choice == "2":
        routers, links = enter_matrix()
    else:
        routers, links = random_network()

    graph = build_graph(routers, links)
    print_network(graph, routers)

    for source in routers:
        print("\n========== Router", source, "==========")

        lsdb = build_lsdb(graph, source)
        print("LSDB:")
        for r in routers:
            if r in lsdb:
                neighbors = [v + "(" + str(c) + ")" for v, c in lsdb[r].items()]
                print("  ", r, ":", ", ".join(neighbors) if neighbors else "no neighbor")

        dist, pred = dijkstra(lsdb, source, routers)

        print("Shortest path tree:")
        print_tree(pred, dist, routers, source)

        print("Distances and paths:")
        for d in routers:
            if d == source:
                continue
            if dist[d] == INF:
                print("  ", d, ": unreachable")
            else:
                print("  ", d, ": distance", dist[d], "| predecessor", pred[d],
                      "| path", " -> ".join(get_path(pred, source, d)))

        print("Routing table:")
        print("   Destination | Next hop      | Cost")
        table = routing_table(dist, pred, source, routers)
        for d in table:
            if table[d] is None:
                print("   " + d.ljust(11) + " | " + "-".ljust(13) + " | unreachable")
            else:
                print("   " + d.ljust(11) + " | " + table[d].ljust(13) + " | " + str(dist[d]))


if __name__ == "__main__":
    main()
