# Graph Analysis Toolkit

A command-line Python toolkit for generating, analyzing, and visualizing graphs.
Built with [NetworkX](https://networkx.org/) as part of a graph theory practical assignment.

## Features

- **Graph types:** Complete, Regular (k-regular), Eulerian, Random, and JSON-loaded graphs
- **Path-finding:** BFS (unweighted), Dijkstra (weighted), Floyd-Warshall (all-pairs)
- **Tours:** Eulerian tour (Hierholzer's algorithm), TSP nearest-neighbour, TSP brute-force

## Requirements

- Python 3.8+
- Install dependencies:

  pip install -r requirements.txt

## Usage

### Generate a complete graph with 5 vertices
  python main.py --type complete --num-vertices 5

### Load a graph from JSON and run Dijkstra
  python main.py --json any_given.json --path-algorithm dijkstra --source 0 --target 3

### Generate a graph from JSON and run Dijkstra
  python main.py --json any_given.json --path-algorithm dijkstra --source 0 --target 3

### Run a TSP brute-force tour on a complete graph
  python main.py --type complete --num-vertices 7 --min-weight 5 --max-weight 10 --path-algorithm tsp-brute

### Run an Eulerian tour
  python main.py --type eulerian --num-vertices 8 --path-algorithm eulerian

## Command Reference

| Argument | Description |
|---|---|
| `--type` | Graph type: `complete`, `regular`, `random`, `eulerian` |
| `--num-vertices` | Number of vertices |
| `--k` | Degree for regular/Eulerian graphs |
| `--min-weight` / `--max-weight` | Edge weight range |
| `--min-edges` / `--max-edges` | Edge count range (random graphs) |
| `--json` | Path to a JSON graph file |
| `--path-algorithm` | One of: `bfs`, `dijkstra`, `floyd`, `eulerian`, `tsp-nn`, `tsp-brute` |
| `--source` / `--target` | Source and target vertices (BFS, Dijkstra) |
