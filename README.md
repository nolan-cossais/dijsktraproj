# dijsktraproj
# Dijkstra and LSDB: 10 & 15
Auteurs : Nolan & Constance

Ce programme calcule les plus courts chemins dans un réseau de routeurs avec Dijkstra. Pour chaque routeur, il affiche sa table de base de données (LSDB), son arbre des plus courts chemins, les distances et sa table de routage.

Le programme n'utilise que la bibliothèque standard de Python (version 3).

## Lancer 
```bash
python3 dijkstra.py
```

Le programme demande ensuite le mode de du réseau :

1. **Réseau aléatoire** : entre 5 et 8 routeurs, générés au hasard. Une fois sur trois, un routeur isolé est ajouté.
2. **Matrice d'adjacence** : tu entres toi-même la matrice des coûts, ligne par ligne.

Tout autre choix que `2` lance en automatique le mode aléatoire.

## Entrer une matrice
- Le nombre de routeurs est demandé en premier. Les noms sont A, B, C, etc.
- Chaque ligne contient autant de nombres qu'il y a de routeurs, séparés par des espaces.
- `0` signifie « pas de lien ».
- Les coûts doivent être des nombres uniquement entiers positifs  
- La matrice doit être symétrique : le coût de A vers B doit être égal au coût de B vers A.

Exemple réseau à 5 routeurs :
```
2
5
0 2 5 0 0
2 0 1 4 0
5 1 0 0 3
0 4 0 0 1
0 0 3 1 0
```
Dans cet exemple, la première ligne (`2`) choisit la saisie de la matrice, la deuxième (`5`) donne le nombre de routeurs, et les cinq suivantes forment la matrice.

## Ce que le programme affiche
Le programme affiche d'abord la matrice des coûts, puis un bloc par routeur. 
Exemple :

```
========== Router ==========
LSDB:
   A : B(2), C(5)
   B : A(2), C(1), D(4)
   C : A(5), B(1), E(3)
   D : B(4), E(1)
   E : C(3), D(1)
Shortest path tree:
  A
  |-- B (2)
      |-- C (3)
          |-- E (6)
      |-- D (6)
Distances and paths:
   B : distance 2 | predecessor A | path A -> B
   C : distance 3 | predecessor B | path A -> B -> C
   D : distance 6 | predecessor B | path A -> B -> D
   E : distance 6 | predecessor C | path A -> B -> C -> E
Routing table:
   Destination | Next hop      | Cost
   B           | B             | 2
   C           | B             | 3
   D           | B             | 6
   E           | B             | 6
```

- LSDB : pour chaque routeur, ses voisins et le coût de chaque lien.
- Shortest path tree : l'arbre des plus courts chemins depuis le routeur étudié. Le nombre entre parenthèses est le coût total depuis la source.
- Distances and paths : la distance minimale, le prédécesseur et le chemin complet vers chaque destination.
- Routing table : pour chaque destination, le prochain saut et le coût.

Une destination inaccessible est affichée `unreachable`. Un routeur situé dans une autre partie du réseau n'apparaît pas dans la LSDB.

## Limites connues
Nombre de routeurs non entier si `abc` : le programme s'arrête sur une erreur.
Diagonale : le programme ne vérifie pas que les valeurs de la diagonale sont à 0. Une valeur non nulle y est ignorée.
Coûts décimaux (par exemple `2.5`) : refusés.
LSDB : elle est construite à partir du réseau complet, sans simuler l'échange de LSA entre routeurs.
Très grands réseaux : l'affichage de l'arbre est récursif. Au-delà d'environ 1 000 routeurs alignés en chaîne, le programme s'arrête avec une erreur `RecursionError`.

## Tests effectués
Calcul des distances comparé à l'algorithme de Bellman-Ford sur 2 000 réseaux aléatoires (13 870 calculs depuis chaque source) : aucune erreur.
Réseau à 5 routeurs : résultats conformes au calcul à la main.
Réseau coupé en deux : les routeurs de l'autre partie sont signalés comme inaccessibles.
Mode aléatoire lancé 200 fois : aucun échec.
Réseau de 27 et de 200 routeurs en chaîne : résultats corrects.
