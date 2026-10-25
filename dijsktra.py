# Calcul des plus courts chemins dans un réseau avec l'algorithme de Dijkstra

import math
import random

INFINITY = float("inf")


# Nom du routeur n°i : A, B, C... (R27, R28... au-delà de 26 routeurs)
def router_name(i):
    return chr(ord("A") + i) if i < 26 else f"R{i + 1}"


# 0a. Génération aléatoire du réseau (différent à chaque lancement)
def generer_reseau_aleatoire():
    nb_routers = random.randint(5, 8)
    routeurs = [router_name(i) for i in range(nb_routers)]
    links = []

    # chaque nouveau routeur se relie à un routeur déjà placé -> tout est relié
    for i in range(1, nb_routers):
        links.append((routeurs[i], random.choice(routeurs[:i]), random.randint(1, 10)))

    # quelques liens supplémentaires au hasard
    for _ in range(nb_routers):
        r1, r2 = random.sample(routeurs, 2)
        already_exists = any({r1, r2} == {a, b} for a, b, c in links)
        if not already_exists:
            links.append((r1, r2, random.randint(1, 10)))

    # une fois sur trois, on ajoute un routeur isolé (destination inaccessible)
    if random.random() < 1 / 3:
        routeurs.append(router_name(nb_routers))

    return routeurs, links


# 0b. Saisie du réseau sous forme de matrice d'adjacence
def saisir_matrice():
    while True:
        try:
            n = int(input("Number of routers: "))
            if n >= 2:
                break
        except ValueError:
            pass
        print("  Please enter an integer greater than or equal to 2.")

    routeurs = [router_name(i) for i in range(n)]
    print(f"Enter the matrix row by row ({n} numbers separated by spaces).")
    print("0 = no link. The diagonal must be 0 and the matrix must be symmetric.")
    print("Column order: " + " ".join(routeurs))

    matrix = []
    for i in range(n):
        while True:
            try:
                ligne = [float(x) for x in input(f"  Row {routeurs[i]}: ").split()]
            except ValueError:
                print("    Numbers only.")
                continue
            if len(ligne) != n:
                print(f"    Exactly {n} numbers are required.")
            elif any(not math.isfinite(x) or x < 0 for x in ligne):
                print("    Costs must be positive (0 = no link).")
            elif ligne[i] != 0:
                print("    The diagonal must be 0 (a router is not linked to itself).")
            elif any(ligne[j] != matrix[j][i] for j in range(i)):
                print("    The matrix must be symmetric: cost X-Y must equal cost Y-X.")
            else:
                break
        matrix.append([int(x) if x.is_integer() else x for x in ligne])

    # on transforme la matrice en liste de liens (on lit seulement au-dessus de la diagonale)
    links = []
    for i in range(n):
        for j in range(i + 1, n):
            if matrix[i][j] > 0:
                links.append((routeurs[i], routeurs[j], matrix[i][j]))
    return routeurs, links


# Menu de départ : choix du type de réseau
def choose_network():
    print("How do you want to create the network?")
    print("  1. Random network")
    print("  2. Enter an adjacency matrix")
    choix = input("Your choice (1 or 2): ").strip()
    while choix not in ("1", "2"):
        choix = input("Please type 1 or 2: ").strip()
    print()
    if choix == "1":
        return generer_reseau_aleatoire()
    return saisir_matrice()


# 1. Représentation du réseau : liste d'adjacence {routeur: {voisin: coût}}
def creer_reseau(routeurs, links):
    network = {r: {} for r in routeurs}
    for r1, r2, cout in links:
        if cout <= 0:
            raise ValueError(f"Link {r1}-{r2}: cost must be positive (got {cout})")
        network[r1][r2] = cout
        network[r2][r1] = cout   # lien dans les deux sens
    return network


# 2. LSDB : chaque routeur connaît, pour tous les routeurs, leurs voisins et les coûts
def build_lsdb(network):
    lsdb = {}
    for routeur in network:
        lsdb[routeur] = {r: dict(voisins) for r, voisins in network.items()}
    return lsdb


# 3. Algorithme de Dijkstra
def dijkstra(lsdb, source):
    distance = {r: INFINITY for r in lsdb}
    predecesseur = {r: None for r in lsdb}
    distance[source] = 0
    visited = []

    while True:
        # on choisit le routeur non visité le plus proche
        u = None
        for r in lsdb:
            if r not in visited and distance[r] < INFINITY:
                if u is None or distance[r] < distance[u]:
                    u = r
        if u is None:          # plus rien d'atteignable
            break
        visited.append(u)

        # on met à jour les distances de ses voisins
        for voisin, cost in lsdb[u].items():
            if distance[u] + cost < distance[voisin]:
                distance[voisin] = distance[u] + cost
                predecesseur[voisin] = u

    return distance, predecesseur


# Chemin complet de la source vers une destination (None si inaccessible)
def chemin(predecesseur, distance, source, destination):
    if distance[destination] == INFINITY:
        return None
    path = [destination]
    while path[-1] != source:
        path.append(predecesseur[path[-1]])
    return path[::-1]


# 4. Table de routage : destination -> prochain saut
def routing_table(predecesseur, distance, source):
    table = {}
    for dest in distance:
        if dest != source:
            path = chemin(predecesseur, distance, source, dest)
            table[dest] = path[1] if path else None
    return table


# 5. Affichage
def afficher_reseau(network):
    routeurs = sorted(network)
    print("\nNetwork (cost matrix, '.' = no link):")
    print("     " + "".join(f"{r:>4}" for r in routeurs))
    for r1 in routeurs:
        ligne = f"  {r1:<3}"
        for r2 in routeurs:
            if r1 == r2:
                value = "-"
            else:
                value = network[r1].get(r2, ".")
            ligne += f"{value:>4}"
        print(ligne)


def draw_tree(lsdb, predecesseur, distance, source):
    # on retrouve les enfants de chaque routeur à partir des prédécesseurs
    enfants = {r: [] for r in predecesseur}
    for r, p in predecesseur.items():
        if p is not None:
            enfants[p].append(r)

    def dessiner(node, indent):
        children = sorted(enfants[node])
        for i, child in enumerate(children):
            dernier = (i == len(children) - 1)
            branch = "└── " if dernier else "├── "
            print(f"  {indent}{branch}{child}  (link {lsdb[node][child]}, total {distance[child]})")
            dessiner(child, indent + ("    " if dernier else "│   "))

    print(f"  {source}")
    dessiner(source, "")


def show_results(routeur, lsdb, distance, predecesseur, table):
    print("\n" + "=" * 15, "Router", routeur, "=" * 15)

    print("LSDB:")
    for r, voisins in sorted(lsdb.items()):
        texte = ", ".join(f"{v}({c})" for v, c in sorted(voisins.items()))
        print(f"  {r}: {texte or 'no neighbor'}")

    print("Shortest path tree:")
    draw_tree(lsdb, predecesseur, distance, routeur)

    print("Distances and paths:")
    for dest in sorted(distance):
        path = chemin(predecesseur, distance, routeur, dest)
        if path:
            print(f"  {dest}: distance {distance[dest]}, predecessor {predecesseur[dest] or '-'}, "
                  f"path {' -> '.join(path)}")
        else:
            print(f"  {dest}: unreachable")

    print("Routing table:")
    print("  Destination | Next hop      | Cost")
    for dest, next_hop in sorted(table.items()):
        if next_hop:
            print(f"  {dest:<11} | {next_hop:<13} | {distance[dest]}")
        else:
            print(f"  {dest:<11} | {'-':<13} | unreachable")


# Programme principal
routeurs, links = choose_network()

try:
    network = creer_reseau(routeurs, links)
except ValueError as e:
    print("Error:", e)
    exit()

afficher_reseau(network)
lsdb = build_lsdb(network)

for routeur in sorted(network):          # Dijkstra depuis chaque routeur
    distance, predecesseur = dijkstra(lsdb[routeur], routeur)
    table = routing_table(predecesseur, distance, routeur)
    show_results(routeur, lsdb[routeur], distance, predecesseur, table)
