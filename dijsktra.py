# Calcul des plus courts chemins dans un réseau avec l'algorithme de Dijkstra

import random

INFINI = float("inf")


# 0. Génération aléatoire du réseau (différent à chaque lancement)
def generer_reseau_aleatoire():
    nb = random.randint(5, 8)
    routeurs = [chr(ord("A") + i) for i in range(nb)]
    liens = []

    # chaque nouveau routeur se relie à un routeur déjà placé -> tout est relié
    for i in range(1, nb):
        liens.append((routeurs[i], random.choice(routeurs[:i]), random.randint(1, 10)))

    # quelques liens supplémentaires au hasard
    for _ in range(nb):
        r1, r2 = random.sample(routeurs, 2)
        deja_la = any({r1, r2} == {a, b} for a, b, c in liens)
        if not deja_la:
            liens.append((r1, r2, random.randint(1, 10)))

    # une fois sur trois, on ajoute un routeur isolé (destination inaccessible)
    if random.random() < 1 / 3:
        routeurs.append(chr(ord("A") + nb))

    return routeurs, liens


# 1. Représentation du réseau : liste d'adjacence {routeur: {voisin: coût}}
def creer_reseau(routeurs, liens):
    reseau = {r: {} for r in routeurs}
    for r1, r2, cout in liens:
        if cout <= 0:
            raise ValueError(f"Lien {r1}-{r2} : le coût doit être positif (reçu {cout})")
        reseau[r1][r2] = cout
        reseau[r2][r1] = cout   # lien dans les deux sens
    return reseau


# 2. LSDB : chaque routeur connaît, pour tous les routeurs, leurs voisins et les coûts
def construire_lsdb(reseau):
    lsdb = {}
    for routeur in reseau:
        lsdb[routeur] = {r: dict(voisins) for r, voisins in reseau.items()}
    return lsdb


# 3. Algorithme de Dijkstra
def dijkstra(lsdb, source):
    distance = {r: INFINI for r in lsdb}
    predecesseur = {r: None for r in lsdb}
    distance[source] = 0
    visites = []

    while True:
        # on choisit le routeur non visité le plus proche
        u = None
        for r in lsdb:
            if r not in visites and distance[r] < INFINI:
                if u is None or distance[r] < distance[u]:
                    u = r
        if u is None:          # plus rien d'atteignable
            break
        visites.append(u)

        # on met à jour les distances de ses voisins
        for voisin, cout in lsdb[u].items():
            if distance[u] + cout < distance[voisin]:
                distance[voisin] = distance[u] + cout
                predecesseur[voisin] = u

    return distance, predecesseur


# Chemin complet de la source vers une destination (None si inaccessible)
def chemin(predecesseur, distance, source, destination):
    if distance[destination] == INFINI:
        return None
    c = [destination]
    while c[-1] != source:
        c.append(predecesseur[c[-1]])
    return c[::-1]


# 4. Table de routage : destination -> prochain saut
def table_routage(predecesseur, distance, source):
    table = {}
    for dest in distance:
        if dest != source:
            c = chemin(predecesseur, distance, source, dest)
            table[dest] = c[1] if c else None
    return table


# 5. Affichage
def afficher_reseau(reseau):
    routeurs = sorted(reseau)
    print("Réseau généré (matrice des coûts, '.' = pas de lien) :")
    print("     " + "".join(f"{r:>4}" for r in routeurs))
    for r1 in routeurs:
        ligne = f"  {r1:<3}"
        for r2 in routeurs:
            if r1 == r2:
                valeur = "-"
            else:
                valeur = reseau[r1].get(r2, ".")
            ligne += f"{valeur:>4}"
        print(ligne)


def afficher_arbre(lsdb, predecesseur, distance, source):
    # on retrouve les enfants de chaque routeur à partir des prédécesseurs
    enfants = {r: [] for r in predecesseur}
    for r, p in predecesseur.items():
        if p is not None:
            enfants[p].append(r)

    def dessiner(noeud, decalage):
        fils = sorted(enfants[noeud])
        for i, f in enumerate(fils):
            dernier = (i == len(fils) - 1)
            branche = "└── " if dernier else "├── "
            print(f"  {decalage}{branche}{f}  (lien {lsdb[noeud][f]}, total {distance[f]})")
            dessiner(f, decalage + ("    " if dernier else "│   "))

    print(f"  {source}")
    dessiner(source, "")


def afficher(routeur, lsdb, distance, predecesseur, table):
    print("\n" + "=" * 15, "Routeur", routeur, "=" * 15)

    print("LSDB :")
    for r, voisins in sorted(lsdb.items()):
        texte = ", ".join(f"{v}({c})" for v, c in sorted(voisins.items()))
        print(f"  {r} : {texte or 'aucun voisin'}")

    print("Arbre des plus courts chemins :")
    afficher_arbre(lsdb, predecesseur, distance, routeur)

    print("Distances et chemins :")
    for dest in sorted(distance):
        c = chemin(predecesseur, distance, routeur, dest)
        if c:
            print(f"  {dest} : distance {distance[dest]}, prédécesseur {predecesseur[dest] or '-'}, "
                  f"chemin {' -> '.join(c)}")
        else:
            print(f"  {dest} : inaccessible")

    print("Table de routage :")
    print("  Destination | Prochain saut | Coût")
    for dest, saut in sorted(table.items()):
        if saut:
            print(f"  {dest:<11} | {saut:<13} | {distance[dest]}")
        else:
            print(f"  {dest:<11} | {'-':<13} | inaccessible")


# Programme principal
routeurs, liens = generer_reseau_aleatoire()

try:
    reseau = creer_reseau(routeurs, liens)
except ValueError as e:
    print("Erreur :", e)
    exit()

afficher_reseau(reseau)
lsdb = construire_lsdb(reseau)

for routeur in sorted(reseau):          # Dijkstra depuis chaque routeur
    distance, predecesseur = dijkstra(lsdb[routeur], routeur)
    table = table_routage(predecesseur, distance, routeur)
    afficher(routeur, lsdb[routeur], distance, predecesseur, table)
