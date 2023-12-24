from search import *
'''
To make it easier to search directed graphs whose edges have costs, we introduce Graph_State, a subclass of State,
that contains a graph_definition (None by default, as actual graphs will be introduced as subclass of Graph_State). 
A graph definition is a dictionary with two keys, 'nodes', whose value is a set of objects (e.g., name strings);
and 'edges', a dictionary whose keys are nodes and whose values are lists of pairs of the form {'node': ..., 'cost': ...}.
See the Romania_Travel example. 
'''
class Graph_State(State):

    # The graph_definition will be specified by subclasses of Graph_State as needed: 
    
    graph_definition = None
    
    #This will usually be the identity function, as it's conveninent to represent nodes by their string names,
    # but a given subclass can override it if need be (e.g., if it wants to represent nodes as integers). 
    @classmethod 
    def make_node(cls,node_string):
        return node_string

    # We construct graph states with this factory class method, called on some appropriate subclass of Graph_State: 
    @classmethod
    def create(cls,node_string): 
        return cls(cls.make_node(node_string))

    # A graph state has a node and a cost: 
    def __init__(self, node):
        super().__init__()
        self.node = node        
        self.cost = 0

    def get_cost(self):
        return self.cost

    def __str__(self):
        return str(self.node)

    def expand(self):
        children_states = []
        for c in type(self).graph_definition['edges'][self.node]: 
            child_node = type(self).create(c['node'])
            if 'cost' in c:
                child_node.cost = self.cost + c['cost']
            children_states.append(child_node)
        return children_states
        
class Romania_Travel(Graph_State):
    '''
    This graph comes from Figure 3.2 of the Russell+Norvig AI textbook, where S stands for Sibius,
    R for Rimnicu Vilcea, F for Fagaras, P for Pitesti, and B for Bucharest. The edge costs are
    as they appear there. There are two different paths from Sibius to Bucharest:
    (1) Sibius -> Fagaras -> Bucharest; and 
    (2) Sibius -> Rimnicu Vilcea -> Pitesti -> Bucharest. 
    The first is shorter but ultimately more expensive. A* (best-first search) will find the optimal
    path by default, but by setting max_solutions > 1 we can get multiple solutions, which will be
    sorted by increasing cost. 
    '''
    graph_definition = {'nodes': set(['S', 'R', 'F', 'P', 'B']),
                        'edges': {'S': [{'node': 'R', 'cost': 80},
                                        {'node': 'F', 'cost': 99}],
                                  'R': [{'node': 'P', 'cost': 97}],
                                  'F': [{'node': 'B', 'cost': 211}],
                                  'P': [{'node': 'B', 'cost': 101}]
                                  }}

    def __init__(self, v):
        super().__init__(v)
        
    def is_solution(self):
        return self.node == 'B'
    
s = Travel.create('S')
(sols,its) = s.best_first_search({'max_solutions':2})
sol1,sol2 = sols
path1 = sol1.solution_path()
path2 = sol2.solution_path()
