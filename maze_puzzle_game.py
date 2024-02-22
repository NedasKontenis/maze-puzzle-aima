from search import *

maze = [
    ['.', '.', '.', '#', '.'],
    ['.', '.', '.', '.', '.'],
    ['#', '.', '#', '.', '#'],
    ['.', '.', '.', '#', '.'],
    ['.', '#', '.', '.', '.']
]

# Sukuriamas MazePuzzle klases egzempliorius su pradine bei galine busena
puzzle = MazePuzzle((0, 0), (4, 4), maze)

# Kvieciamas paieskos i ploti algoritmas
solution = breadth_first_graph_search(puzzle).solution()
print("BFS Solution:", solution)

# Kvieciamas pirmo geriausio grafo algoritmas naudojant euristika
solution = best_first_graph_search(puzzle, lambda n: puzzle.h(n)).solution()
print("A* Solution:", solution)