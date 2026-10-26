# dijsktraproj
# Dijkstra and LSDB: 10 & 15
Authors : Nolan & Constance

This program compute the shortest path in a routing network with Djikstra algorithm. For each router, the program print the Data base table, the shortest path treeand the distance and the routing table.
The program use the standard library Python (V3)

# Project
```bash
python3 dijkstra.py
```
Ask the user the mode of the network : 
1. **Random network** :  5 and 8 routers, randomly generated. A isolate router is generate 1 over 3 times
2. **Adjacency matrix** : you enter the matrice and the weight line per line
If not `2` the code is launch automiticaly in random

# Matrix
First you asnwer the number of routers with names (A/B/C...)
Then each line contains as many numbers as there are routers, separated by spaces. And 0 mean non link
The wight of a egde is a positive number
The matrice must be symmetrical the cost must be the same in both direction  

Example 5 routers :
```
2
5
0 2 5 0 0
2 0 1 4 0
5 1 0 0 3
0 4 0 0 1
0 0 3 1 0
```
In this example, the first line (`2`) specifies that a matrix is to be entered, the second line (`5`) specifies the number of routers, and the next five lines make up the matrix.

# Terminal
program print first cost matrice then a part by router
Example :

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

- LSDB: for each router, its neighbours and the cost of each link 
- Shortest path tree: the tree of shortest paths from the router in question. The number in brackets is the total cost from the source
- Distances and paths: the minimum distance, the predecessor and the complete path to each destination 
- Routing table: for each destination, the next hop and the cost
unreachable if the router is not accessible
If a router is on a other part of the network it doesn't appears in the LSDB

# Limits
If the number of routers is not an integer (e.g. `abc`), the programme terminates with an error.
The programme does not check that the values on the diagonal are 0. Any non-zero value there is ignored.
Decimal costs (e.g. `2.5`) are not accepted.
The LSDB is constructed from the complete network; for very large networks, the tree is displayed recursively.
If there are more than approximately 1,000 routers linked in a chain, the programme terminates with a `RecursionError`.

# Tests
Calculation of distances compared with the Bellman-Ford algorithm on 2,000 random networks (13,870 calculations from each source)
A network with 5 routers produced results matching those of the manual calculation.
The routers on the other side are reported as inaccessible because the network is split in two
Networks with 27 and 200 routers in a chain produced correct results, with the random mode functioning correctly in each case
