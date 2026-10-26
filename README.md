# dijsktraproj
# Dijkstra and LSDB: 10 & 15

Author : Nolan & Constance

dijkstra_corrige.py computes, for each router in the network, the link state database (LSDB), the shortest path tree, the distances, the complete paths and the routing table.
This is the corrected version of the exercise *‘Calculating shortest paths in a network using Dijkstra’s  algorithm’*. It corrects the errors identified in the review (see the ‘Dijkstra code review’ page).
 
No external dependencies: only the standard Python library is used. Tested with Python 3.13.

## Running the programme
```bash
python3 dijkstra_corrige.py  
```
 
The programme first asks for the network generation mode:

1. **Random network**: a random network of 5 to 8 routers. One in every three times, an isolated router is added.
2. **Enter an adjacency matrix**: you enter the cost matrix, row by row.

### Entering a matrix 

- The number of routers must be at least 2. The names are A, B, C… then R27, R28… beyond 26.
- Each row contains as many numbers as there are routers, separated by spaces.
- `0` means ‘no link’ 
- A cost must be a positive, finite number. Negative values, `inf`, `nan` and letters are rejected with an error message.
- The diagonal must be zero.
- The matrix must be symmetric: the cost from A to B must be equal to the cost from B to A 

For example, the 5-router network from the journal :
```
2
5
0 2 5 0 0
2 0 1 4 0 
5 1 0 0 3 
0 4 0 0 1
0 0 3 1 0
```

To exit whilst entering data: Ctrl+D (Linux, macOS) or Ctrl+Z followed by Enter (Windows). The programme displays ‘Input closed, exiting.’ and exits with exit code 1. 

## What the programme displays
 
The programme begins with the cost matrix, then displays one block per router. Actual output for router A in the network shown above:
```
=============== Router A ===============
LSDB (LSAs received by this router):
  A (seq 1): B(2), C(5)
  B (seq 1): A(2), C(1), D(4)
  C (seq 1): A(5), B(1), E(3)
  D (seq 1): B(4), E(1)
  E (seq 1): C(3), D(1)
Shortest path tree:
  A
  └── B  (link 2, total 2)
      ├── C  (link 1, total 3)
      │   └── E  (link 3, total 6)
      └── D  (link 4, total 6)
Distances and paths:
  A: distance 0, predecessor -, path A
  B: distance 2, predecessor A, path A -> B
  C: distance 3, predecessor B, path A -> B -> C
  D: distance 6, predecessor B, path A -> B -> D
  E: distance 6, predecessor C, path A -> B -> C -> E
Routing table:
  Destination | Next hop      | Cost
  B           | B             | 2
  C           | B             | 3
  D           | B             | 6
  E           | B             | 6
```

For each block:

- **LSDB**: the LSAs that this router has received, one per router in its connected component.
- **Shortest path tree**: the shortest path tree, showing the cost of each link and the total cost from the source. 
- **Distances and paths**: the minimum distance, the predecessor and the complete path to each destination.
- **Routing table**: for each destination, the next hop and the cost.
 
An unreachable destination is marked as `unreachable`. A router located in another component does not appear in the LSDB: this is indicated by the line ‘No LSA received from: …’. 

## Changes from the original version
| Issue | Original version | Corrected version |
|---|---|---|
| Order of routers | `sorted()`  places R27 between R and S |  `sort_key`: length then name. The display order is the same as the input order |
| End of input | Ctrl+D causes an `EOFError` traceback | `ask()` exits cleanly with exit code 1 |
| LSDB | Copies the complete topology to each router |  `flood()` simulates LSA flooding. `topologie_vue_par()` only retains a link if it is advertised on both sides | 
| Tree | Recursive `draw_tree`, scales to around 1,000 routers | Traversal using a stack, with no depth limit |
| `inf` message | “Costs must be positive” | One message for non-finite values, one for negative values |
| Execution | The programme runs as soon as it is imported |  `main()` following `if __name__ == ‘__main__’:` |
| Output | `exit()` | `sys.exit()` |
 
Dijkstra’s algorithm is the same as in the original version. Only its inputs have changed: it now runs on the flooded LSDB of each router.

## File structure
| Function | Role |
|---|---|
| `router_name`, `sort_key` | Router names and display order |
| `ask` | Input protected against end-of-file |
| `generate_random_network`, `enter_matrix`, `choose_network` | Network creation |
| `create_network` | Adjacency list `{router: {neighbour: cost}}`, with validations |
| `originate_lsa`, `flood` | LSA for each router and flooding until stabilisation |
| `topology_as_seen_by` | Graph as seen by a router; link retained if advertised on both sides |
| `dijkstra` | Explicitly written algorithm: selection of the minimum, updating of neighbours |
| `path`, `routing_table` | Complete path and next hop |
| `display_network`, `draw_tree`, `show_results` | Display |
| `main` | Sequence: network, flooding, then Dijkstra from each router |

## Known limitations
- Asymmetric costs (A→B different from B→A) are not accepted when entered.
- There is no step-by-step Dijkstra table in the course format.
- The random mode generates only 5 to 8 routers (plus a possible isolated router). The matrix mode accepts more.
- `routing_table` recalculates the full path for each destination. This is correct but not very efficient.
- Calculation and display remain in the same file

## Tests carried out
The tests were run on this version. The test scripts are not included in this folder.

- Dijkstra on the flooded LSDB: 13,962 source calculations across 2,000 networks, compared with Bellman-Ford. No incorrect distances. Each router’s LSDB corresponds to its connected component.
- Split network (A–B and C–D): A’s LSDB contains only A and B. 
- `draw_tree`: identical to the original version on 1,666 trees. A chain of 1,200 routers produces 1,200 lines.
- Display order: identical to the input order, for 1 to 300 routers. 
- Example with 5 routers: same distances and tables as the original version.
- End of input: code 1, clean message, no traceback.
- 27 routers: the header and lines follow the input order. 
- Random mode: no errors.
- Time: 200 routers, flooding and Dijkstra from each, approximately 0.8 s.
- Lint:

  ```bash
  ruff check --select E,F,W,B,N,SIM,UP,I dijkstra_corrige.py
  ```

  Result: no issues reported.
