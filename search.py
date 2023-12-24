''' 
The class State implements general classical-AI search functionality over trees or general graphs: 
depth-first, breadth-first, iterative deepening, best-first, beam search, and A*. All six algorithms 
are implemented by passing appropriate argument values to one single method, State.search. 

Backtracking pruning is also implemented by incorporating into State.search a virtual method is_valid that
determines whether a given state is feasible. Only valid states are expanded. The default implementation
of is_valid returns True, so all states are normally expanded, but for Sudoku (for example) we define 
this method so that any state that violates the rules of the game is deemed invalid. 

Best-first, beam search, and A* require an estimate of the distance from a given state to a goal 
(solution) state. If such a notion is available, it is implemented by overriding the virtual method 
'distance' (this is the "heuristic function" often represented by the letter 'h' in presentations of 
search algorithms); the default implementation returns 0. The cost of reaching a state (starting 
from an initial state) is given by the virtual method  get_cost (this is often denoted by the letter
'g'). The default implementation of get_cost simply returns the depth of a state s (the number of 
edges from the start state to s) as its cost. Any over-riding implementation must return non-negative numbers. 

Parameters that can be used to control the search include the maximum number of iterations; the maximum
number of states to show during the execution of a search algorithm (5 by default; setting this to 0 forces
the algorithm to be silent); the maximum number of solutions to return (1 by default); the maximum depth 
to search (no such limit exists by default); the beam width (this is only applicable to beam search); and
tree_space, a parameter indicating whether the search space is a tree (true by default; setting this to
False means that the search space is a non-tree graph, i.e., that there are multiple paths between some
pairs of nodes). In that case the implementation uses hash tables to keep track of the search fringe 
as well as the set of visited nodes. By default, states are hashed on their string representations, but this
can be changed by overriding the __hash__ and __eq__ methods. 

By default a state contains only a pointer to its parent state (used to obtain solution paths), and its depth. 
Of course subclasses derived from State will typically have additional content, e.g., a Sudoku state will
contain the board. In most cases, one only has to override the following methods for a derived class: 

(1) the __str__ method; 
(2) the is_solution method (which determines whether a state is a goal state, the default implementation
returns False); and 
(3) the expand method, which returns a list of all and only the successor states of self; and, if applicable,
(4) the is_valid method. 

See sudoku.py and twenty_four.py for examples of tree-based search, and see graph.py for graph-based examples
and A*. 
'''

from queue import *
from heapq import merge 
from abc import ABC, abstractmethod
import numpy as np

def in_place_merge_descending(L1, L2, get_key=lambda x: x):
    '''
    This helper function takes two lists L1 and L2 of arbitrary objects, where every such object x 
    has some numeric key associated with it, obtained by get_key(x). (By default, get_key is the
    identity function.) L1 is already sorted in reverse. This function sorts L2 (also in reverse order)
    and then does an in-place merge of the result with L1. The idea here is that L1 will typically
    be large and already sorted, while L2 will be relatively small. So instead of adding L2's elements
    to L1 and then re-sorting the entire thing from scratch, we only sort L2 and then merge. 
    '''
    # First, sort L2: 
    L2.sort(key=get_key,reverse=True)
    # Then, expand L1 to accommodate the elements of L2: 
    L1.extend([None] * len(L2))
    # Set up three indices (for L1, L2, and the merged list): 
    i1 = len(L1) - len(L2) - 1  # Index of the last non-None element in the original L1
    i2 = len(L2) - 1            # Index of the last element in L2
    i = len(L1) - 1             # Index for the merged list
    # Finally, merge L2 into L1 in-place, starting from the end: 
    while i1 >= 0 and i2 >= 0:
        if get_key(L1[i1]) < get_key(L2[i2]):
            L1[i] = L1[i1]
            i1 -= 1
        else:
            L1[i] = L2[i2]
            i2 -= 1
        i -= 1
    # If any elements are left in L2, place them at whatever empty locations remain in L1: 
    while i2 >= 0:
        L1[i] = L2[i2]
        i2 -= 1
        i -= 1

class State(ABC):

    default_params = {'max_iterations': 500,
                      'max_states_to_show': 5,
                      'max_solutions': 1,
                      'max_depth': None,
                      'beam_width': 4,
                      'tree_space': True}
    
    def __init__(self) -> None:
        self.parent = None
        self.depth = 0
        pass

    @abstractmethod
    def __str__(self):
        pass
    
    def is_valid(self):
        return True

    def __hash__(self):
        return hash(str(self))
    
    def __eq__(self, other):
        if isinstance(other, State):
            return str(self) == str(other)
        return NotImplemented
    
    # Set s to be the parent of this state:
    def set_parent(self,s):
        self.parent = s
        self.depth = 1 + s.depth
        
    def is_solution(self):
        return False    

    @staticmethod
    def push_new(new_items,old_items):
        for item in reversed(new_items):
            old_items.append(item)

    @abstractmethod            
    def expand(self):
        pass

    def distance(self):
        '''        
        Return the estimated distance between self and a goal state. 
        '''
        return 0

    def get_cost(self):
        '''        
        Return the true cost/distance from the initial state to self.  
        '''        
        return self.depth
    
    def print_state_frontier(self,
                             states,
                             state_iterator,
                             max_states_to_show=8):
        i = 0
        state_count = len(states)
        for s in state_iterator(states):
            i += 1
            if i > max_states_to_show:
                remaining = len(states) - max_states_to_show
                print("... " + str(remaining) + " more " + ('states' if remaining > 1 else 'state')  + " ...")
                return 
            elif i == 1:
                print("\033[31m" + "State #" + str(i) + ": " + str(s) + "\033[0m" + " ---- distance: " + str(s.distance()) + ", cost: " + str(s.get_cost()))
            else:
                print("State #" + str(i) + ": " + str(s) + "  --- distance: " + str(s.distance()) + ", cost: " + str(s.get_cost()))

    def show_states(self,
                    states,
                    iteration,
                    state_iterator,
                    max_states_to_show):
        if max_states_to_show > 0:
            print("==== Iteration #" + str(iteration) + ', ' + str(len(states))  + " open states: ")
            self.print_state_frontier(states,state_iterator,max_states_to_show=max_states_to_show)

    @staticmethod
    def worth_keeping(s,visited_table,frontier_table,graph_state_space):
        '''        
        If we are searching a tree we keep every expanded state, since every such state is fresh (we didn't see it before).
        For a graph, a state can be generated multiple times, so a state might either have already been visited, in
        which case we only keep it if its cost is smaller than the one we saw before; or it might already be in the frontier,
        in which case we keep it there but replacing it with the new instance if the latter's cost is smaller.
        '''                
        if not(graph_state_space):
            # If we're searching a tree, 
            return True
        if s in visited_table:
            if visited_table[s].get_cost() > s.get_cost():
                visited_table.pop(s)
                return True
            else:
                return False
        if s in frontier_table:
            if frontier_table[s].get_cost() > s.get_cost():
                frontier_table[s] = s
                return False
            else:
                return False
        return True 

    @staticmethod
    def switch_if_cheaper_path_exists(state,frontier_table):
        if state in frontier_table and [state].get_cost() < state.get_cost():
            return frontier_table[state]
        else:
            return state
        
    def search(self,
               make_initial_frontier,
               add_states,
               choose_state_to_expand,
               state_iterator,
               params=default_params):
        # Note that frontier_table is a hash-table representation of the list open_states. 
        params = {**State.default_params, **params}
        graph_state_space = not(params['tree_space'])
        frontier_table, visited_table = {}, {}
        def add_to_table(item,table):
            if graph_state_space:
                table[item] = item
        add_to_table(self,frontier_table)
        max_iterations, max_states_to_show = params['max_iterations'], params['max_states_to_show']
        max_solutions, max_depth = params['max_solutions'], params['max_depth']
        open_states = make_initial_frontier(self)
        iteration, solutions = 0, []        
        while open_states:
            iteration += 1
            if iteration > max_iterations:
                print("Reached the maximum number of iterations (" + str(max_iterations) + "), stopping the search. Pending open states: " + str(len(open_states)) + ".")
                return (solutions,iteration)
            self.show_states(open_states,iteration,state_iterator,max_states_to_show)
            state = choose_state_to_expand(open_states)
            if graph_state_space:
                # It's possible that the table already contains this state but with a smaller cost; if so, swap it:
                State.switch_if_cheaper_path_exists(state,frontier_table)
                # Remove the state from the frontier table: 
                frontier_table.pop(state)
            add_to_table(state,visited_table)
            if state.is_valid() and not(max_depth is not None and state.depth > max_depth): 
                if state.is_solution():
                    print("\nSuccess! Solution found after " + str(iteration)  + " iterations: " + str(state))
                    solutions.append(state)
                    if len(solutions) >= max_solutions:
                        return (solutions,iteration)
                else:
                    children_states = [s for s in state.expand() if State.worth_keeping(s,visited_table,frontier_table,graph_state_space)]
                    for child_state in children_states:
                        child_state.set_parent(state)
                        add_to_table(child_state,frontier_table)
                    add_states(children_states,open_states)
        print("No more states to explore after " + str(iteration) + " iterations.")
        return (solutions,iteration)

    def dfs(self,params=default_params):
        return self.search(make_initial_frontier=lambda state: [state],
                           # Assuming that new_states were generated in their natural left-to-right order, they should be pushed
                           # on the stack in reverse order, from right to left, using push_new:
                           add_states=lambda new_states,old_states: State.push_new(new_states,old_states),
                           choose_state_to_expand=lambda states: states.pop(),
                           state_iterator=lambda states: reversed(states),
                           params=params)

    def iterative_deepening(self,depth_limit,params=default_params):
        params = {**State.default_params, **params}        
        depth = 0
        all_results, all_iterations = [], 0
        print("Here's depth: " + str(depth))
        print("And here's depth_limit: " + str(depth_limit))
        while depth <= depth_limit:
            print("-------------------------------------------- DFS up to depth " + str(depth))
            (results,iterations) = self.dfs(params={**params, 'max_depth':depth})
            all_results.extend(results)
            all_iterations += iterations
            if len(all_results) >= params['max_solutions']:
                return (all_results,all_iterations)
            depth += 1
        return (all_results,all_iterations)

    def bfs(self,params=default_params): 
        return self.search(make_initial_frontier=lambda state: Queue(state),
                           add_states=lambda new_states,old_states: old_states.enqueue_items(new_states),
                           choose_state_to_expand=lambda states: states.dequeue(),
                           state_iterator=lambda states: states.__iter__(),
                           params=params)                           
    
    @staticmethod        
    def sorter(new_states,old_states,beam_width=None):
        '''
        Instead of adding the new states to the old states and sorting the result, we can take advantage of the fact that
        the old states are already sorted, so we only need to sort the new states (typically a relatively short list) and then
        merge the resulting list with the old states, a linear-time operation.
        We sort in reverse order so that the smallest-distance element is at the right end of the list.
        This ensures that we can then get the best state to expand in O(1) time. 
        #old_states.sort(key=lambda s: -(s.get_cost() + s.distance()))
        If a beam width is specified, keep only the candidates in the beam, pruning everything else.
        Since we are sorting in reverse, this means we need to keep the *last* beam_width list elements.         
        '''
        in_place_merge_descending(old_states,new_states,get_key=lambda s: s.get_cost() + s.distance())
        if beam_width:
            # Remove all but the last beam_width elements: 
            del old_states[:-beam_width]
        
    def best_first_search(self,params=default_params): 
        return self.search(make_initial_frontier=lambda state: [state],
                           add_states=State.sorter,
                           choose_state_to_expand=lambda states: states.pop(), # get the smallest-distance state 
                           state_iterator=lambda states: reversed(states),
                           params=params)                                                      
    
    def beam_search(self,params=default_params):
        return self.search(make_initial_frontier=lambda state: [state],
                           add_states=lambda new_states, old_states: State.sorter(new_states, old_states, beam_width=params['beam_width']),
                           choose_state_to_expand=lambda states: states.pop(),
                           state_iterator=lambda states: reversed(states),
                           params=params)                                                                                 

    # Solve a bunch of problem instances parsed from file_name. Report stats at the end. 
    @staticmethod        
    def solve_batch(file_name,parse_file,params=default_params,algorithm='dfs'):
        initial_states = parse_file(file_name)
        results, iters = [], []
        for initial_state in initial_states:
            result = None
            if algorithm == 'dfs':
                result = initial_state.dfs({**State.default_params, **params, 'max_states_to_show':0})
            elif algorithm == 'bfs':
                result = initial_state.bfs({**State.default_params, **params, 'max_states_to_show':0})
            elif algorithm == 'beam_search':
                result = initial_state.beam_search({**State.default_params, **params, 'max_states_to_show':0})         
            else:
                result = initial_state.best_first_search({**State.default_params, **params, 'max_states_to_show':0})
            results.append(result[0])                
            iters.append(result[1])
        successes = len([result for result in results if result])
        print("\nSolved " + str(successes) + " problems out of " + str(len(initial_states)) + ".")
        print("Average number of iterations: " + str(np.mean(iters)) + ".\n")
        return results

    # Print a path from the initial state to a solution state: 
    def solution_path(self):
        p = self
        parents = [p]
        while p.parent:
            p = p.parent
            parents.append(p)
        res = list(reversed(parents))        
        print("Solution path: ")
        cost_so_far = 0        
        if len(res) > 1: 
            for i in range(len(res)-1):
                print('\t' + str(res[i]) + " --> " + str(res[i+1]) + " (cost: " +  str(res[i+1].get_cost() - cost_so_far) + ')')
                cost_so_far = res[i+1].get_cost()
        else:
            print('\t' + str(res[0]))
        print("Total path cost: " + str(cost_so_far))
        return res
