"""
Search (Chapters 3-4)

The way to use this code is to subclass Problem to create a class of problems,
then create problem instances and solve them with calls to the various search
functions.
"""

import sys
from collections import deque

from utils import *

import math
import decimal

import random

class Problem:
    """The abstract class for a formal problem. You should subclass
    this and implement the methods actions and result, and possibly
    __init__, goal_test, and path_cost. Then you will create instances
    of your subclass and solve them with the various search functions."""

    def __init__(self, initial, goal=None):
        """The constructor specifies the initial state, and possibly a goal
        state, if there is a unique goal. Your subclass's constructor can add
        other arguments."""
        self.initial = initial
        self.goal = goal

    def actions(self, state):
        """Return the actions that can be executed in the given
        state. The result would typically be a list, but if there are
        many actions, consider yielding them one at a time in an
        iterator, rather than building them all at once."""
        raise NotImplementedError

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        raise NotImplementedError

    def goal_test(self, state):
        """Return True if the state is a goal. The default method compares the
        state to self.goal or checks for state in self.goal if it is a
        list, as specified in the constructor. Override this method if
        checking against a single self.goal is not enough."""
        if isinstance(self.goal, list):
            return is_in(state, self.goal)
        else:
            return state == self.goal

    def path_cost(self, c, state1, action, state2):
        """Return the cost of a solution path that arrives at state2 from
        state1 via action, assuming cost c to get up to state1. If the problem
        is such that the path doesn't matter, this function will only look at
        state2. If the path does matter, it will consider c and maybe state1
        and action. The default method costs 1 for every step in the path."""
        return c + 1

    def value(self, state):
        """For optimization problems, each state has a value. Hill Climbing
        and related algorithms try to maximize this value."""
        raise NotImplementedError


# ______________________________________________________________________________
class Node:
    """A node in a search tree. Contains a pointer to the parent (the node
    that this is a successor of) and to the actual state for this node. Note
    that if a state is arrived at by two paths, then there are two nodes with
    the same state. Also includes the action that got us to this state, and
    the total path_cost (also known as g) to reach the node. Other functions
    may add an f and h value; see best_first_graph_search and astar_search for
    an explanation of how the f and h values are handled. You will not need to
    subclass this class."""

    def __init__(self, state, parent=None, action=None, path_cost=0):
        """Create a search tree Node, derived from a parent by an action."""
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.depth = 0
        if parent:
            self.depth = parent.depth + 1

    def __repr__(self):
        return "<Node {}>".format(self.state)

    def __lt__(self, node):
        return self.state < node.state

    def expand(self, problem):
        """List the nodes reachable in one step from this node."""
        return [self.child_node(problem, action)
                for action in problem.actions(self.state)]

    def child_node(self, problem, action):
        """[Figure 3.10]"""
        next_state = problem.result(self.state, action)
        next_node = Node(next_state, self, action, problem.path_cost(self.path_cost, self.state, action, next_state))
        return next_node

    def solution(self):
        """Return the sequence of actions to go from the root to this node."""
        return [node.action for node in self.path()[1:]]

    def path(self):
        """Return a list of nodes forming the path from the root to this node."""
        node, path_back = self, []
        while node:
            path_back.append(node)
            node = node.parent
        return list(reversed(path_back))

    # We want for a queue of nodes in breadth_first_graph_search or
    # astar_search to have no duplicated states, so we treat nodes
    # with the same state as equal. [Problem: this may not be what you
    # want in other contexts.]

    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

    def __hash__(self):
        # We use the hash value of the state
        # stored in the node instead of the node
        # object itself to quickly search a node
        # with the same state in a Hash Table
        return hash(self.state)
# ______________________________________________________________________________
# Uninformed Search algorithms


def breadth_first_graph_search(problem, step_limits = -1):
    """[Figure 3.11]
    Note that this function can be implemented in a
    single line as below:
    return graph_search(problem, FIFOQueue())
    """
    node = Node(problem.initial)
    if problem.goal_test(node.state):
        return node
    frontier = deque([node])
    explored = set()
    step_num = 0
    while frontier:
        step_num = step_num + 1
        #print(step_num)
        node = frontier.popleft()
        if step_limits > 0 and step_num >= step_limits:  # its for debug
            return node

        explored.add(node.state)
        for child in node.expand(problem):
            if child.state not in explored and child not in frontier:
                if problem.goal_test(child.state):
                    return child
                frontier.append(child)
    return None


def best_first_graph_search(problem, f, display=False):
    """Search the nodes with the lowest f scores first.
    You specify the function f(node) that you want to minimize; for example,
    if f is a heuristic estimate to the goal, then we have greedy best
    first search; if f is node.depth then we have breadth-first search.
    There is a subtlety: the line "f = memoize(f, 'f')" means that the f
    values will be cached on the nodes as they are computed. So after doing
    a best first search you can examine the f values of the path returned."""
    f = memoize(f, 'f')
    node = Node(problem.initial)
    frontier = PriorityQueue('min', f)
    frontier.append(node)
    explored = set()
    step_num = 0
    while frontier:
        step_num = step_num + 1
        #print(step_num)
        node = frontier.pop()
        if problem.goal_test(node.state):
            if display:
                print(len(explored), "paths have been expanded and", len(frontier), "paths remain in the frontier")
            return node
        explored.add(node.state)
        for child in node.expand(problem):
            if child.state not in explored and child not in frontier:
                frontier.append(child)
            elif child in frontier:
                if f(child) < frontier[child]:
                    del frontier[child]
                    frontier.append(child)
    return None

# ______________________________________________________________________________

class MazePuzzle(Problem):
    def __init__(self, initial, goal, maze):
        """Sukuriamas problemos mazePuzzle objektas.
        pradine busena: Tuple duomenu struktura reprezentuojanti pradine busena (x, y).
        goal: Tuple duomenu struktura reprezentuojanti galine busena (x, y).
        maze: axb reiksmiu tinklelis turintis b eiliu, kur '.' galima praeiti ir '#' yra kliutis."""
        super().__init__(initial, goal)
        self.maze = maze

    def actions(self, state):
        """Grazinamas veiksmu sarasas, kuris gali buti ivykdytas pagal tikrinama busena"""
        actions = []
        x, y = state
        if x > 0 and self.maze[x - 1][y] == '.':  # Up
            actions.append('UP')
        if x < len(self.maze) - 1 and self.maze[x + 1][y] == '.':  # Down
            actions.append('DOWN')
        if y > 0 and self.maze[x][y - 1] == '.':  # Left
            actions.append('LEFT')
        if y < len(self.maze[0]) - 1 and self.maze[x][y + 1] == '.':  # Right
            actions.append('RIGHT')
        return actions

    def result(self, state, action):
        """ Pagal duota busena ir veiksma grazina naujos busenos rezultata
                Action yra validus tikrinamos busenos veiksmas """
        x, y = state
        if action == 'UP':
            return (x - 1, y)
        elif action == 'DOWN':
            return (x + 1, y)
        elif action == 'LEFT':
            return (x, y - 1)
        elif action == 'RIGHT':
            return (x, y + 1)

    def goal_test(self, state):
        """Grazina true jei tikrinama busena sutampa su galine."""
        return state == self.goal

    def h(self, node):
        """Manhattan Distance euristine taisykle, skirta apskaičiuoti bendrą žingsnių skaičių,
         reikalingą tikslui pasiekti iš dabartinės padėties, neatsižvelgiant į kliūtis, kurios gali būti kelyje."""
        return abs(node.state[0] - self.goal[0]) + abs(node.state[1] - self.goal[1])