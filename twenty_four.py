from search import *
import itertools
import copy
import re
from pathlib import Path

def remove(lst,index_pair):
    '''
    This function takes a list lst and a pair of indices i, j in range(len(lst)) and returns the list
    obtained from lst by removing the two elements found in the locations i and j. 
    '''
    return [lst[x] for x in range(len(lst)) if x not in index_pair]

'''
We represent an equation x <op> y  = z as the dictionary {'left': x, 'right': y, 'op': <op>, 'value': z},
where x, y and z are numbers and <op> is a string, e.g., the equation 2 + 3 = 5 becomes
{'left': 2, 'right': 3, 'op': '+', 'value': 5}.  
'''

def make_eqn(a,b,op):
    '''
    Produce the equation formed by applying op to the numbers a and b. 
    '''    
    value = a+b if op == '+' else a-b if op == '-' else a*b if op == '*' else a/b
    return {'left':a, 'right':b, 'op': op, 'value': float(value)}
    
def dedup_equations_by_value(eqns):
    '''
    This function takes a list of equations and dedups them by their 'value' field. 
    '''
    D = {}
    for eqn in eqns:
        if eqn['value'] not in D:
            D[eqn['value']] = eqn
    return list(D.values())

def make_all_eqn_pairs(a,b):
    '''
    Make all possible equations for two numbers a and b and return them as a list. 
    '''
    eqns = [make_eqn(a,b,'+'),make_eqn(a,b,'*'),make_eqn(a,b,'-'),make_eqn(b,a,'-')]
    eqns += ([make_eqn(a,b,'/')] if b != 0 else []) + ([make_eqn(b,a,'/')] if a != 0 else [])
    return dedup_equations_by_value(eqns)

def make_all_eqns(num_list):
    '''
    Given a list of numbers, num_list, this returns all pairs of the form ((i,j),eqns) where i, j are distinct indices
    in range(num_list) and eqns is a list of all the equations that can be built from the two numbers num_list[i] and num_list[j].
    '''    
    index_pairs = [(i,j) for i in range(len(num_list)) for j in range(len(num_list)) if i < j]
    return [((i,j),make_all_eqn_pairs(num_list[i],num_list[j])) for i, j in index_pairs]

def combine(num_list,n):
    '''
    Return the set of all values that can be obtained by applying an operation to n and an element of num_list (in any order).
    '''        
    return set(itertools.chain.from_iterable([[n+m,n-m,m-n,n*m] +
                                              ([n/m] if m != 0 else []) +
                                              ([m/n] if n != 0 else []) for m in num_list]))

def sample(num_list):
    '''
    Recursively generate the set of all values that can be obtained by applying a sequence of N-1 operations to elements of num_list,
    where N = len(num_list).
    '''            
    return set(num_list) if len(num_list) < 2 else combine(sample(num_list[1:]),num_list[0])

def eqn_to_str(e):
    '''
    Return the printed representation of an equation: 
    '''
    return '(' + str(e['left']) + ' ' + e['op'] + ' ' + str(e['right']) + ' = ' + str(e['value']) + ')'

class TwentyFourState(State):

    # Only sample 20 random operations by default: 
    MAX_SAMPLES = 20

    @staticmethod
    def set_max_samples(m):
        TwentyFourState.MAX_SAMPLES = m

    @staticmethod
    def get_max_samples():
        return TwentyFourState.MAX_SAMPLES      
    
    def __init__(self, starting_numbers, starting_equations=[]):
        super().__init__()
        self.available_nums = [float(x) for x in starting_numbers]
        self.eqns = starting_equations

    def nested_str(self):
        '''
        This method returns a nested-string representation of the equations, e.g., the three equations 10 + 4 = 14, 2 * 5 = 10, and 14 + 10 = 24
        will produce the string ((10 + 4) + (2 * 5) = 24). This might not be possible for some states. 
        '''
        def eqn_to_str_no_identity(e):
            return '(' + str(e['left']) + ' ' + e['op'] + ' ' + str(e['right']) + ')'        
        E = copy.deepcopy(self.eqns)
        if not(E):
            return 'none yet'
        e = eqn_to_str_no_identity(E.pop())
        while E:
            candidates = [(i,E[i]) for i in range(len(E)) if str(E[i]['value']) in re.findall(r'-?\b\d+(?:\.\d+)?\b',e)]
            if candidates: 
                e = e.replace(str(candidates[0][1]['value']),eqn_to_str_no_identity(candidates[0][1]),1)
                E.pop(candidates[0][0])
            else:
                return 'none yet'
        return e.replace('.0','')
        
    def __str__(self):
        return 'Available numbers: ' + str(self.available_nums) + '. Equations: [' + ', '.join([eqn_to_str(e) for e in self.eqns]) + ']. Nested form: ' + self.nested_str()

    @classmethod
    def from_line(cls,line_string):        
        number_strings = line_string.split()
        if len(number_strings) == 4:
            return cls(number_strings)
        else:
            raise ValueError("Invalidly formatted string given as input to TwentyFourState.from_line")

    @staticmethod
    #Return a list of initial games of 24 built from a text file whose every line is a string that can be parsed by from_line: 
    def parse_file(file_name,is_csv_file=True):
        lines = [l.strip() for l in Path(file_name).read_text().split("\n") if l]
        if is_csv_file:
            new_lines = []
            for l in lines: 
                toks = l.split(",")
                new_lines.append(toks[1])
            lines = new_lines
        return [TwentyFourState.from_line(l) for l in lines]

    def distance(self):
        '''
        To estimate how close a state is to the goal of producing 24, we sample the available numbers (perform random binary operations on them),
        up to MAX_SAMPLES, and take the minimum absolute difference from 24. 
        '''
        try:
            return min([abs(24-x) for x in list(sample(self.available_nums))[:TwentyFourState.MAX_SAMPLES]])
        except:
            return 10000
        
    def is_solution(self):
        return len(self.available_nums) == 1 and self.available_nums[0] == 24
    
    def expand(self):
        # If we don't have at least two available numbers, this is a leaf state. 
       if len(self.available_nums) < 2:
           return []
       all_indexed_eqns = make_all_eqns(self.available_nums)
       children_states = []                     
       for ((i,j),eqns) in all_indexed_eqns: 
           for e in eqns:
               remaining_nums = remove(self.available_nums,(i,j))
               current_eqns_copy = copy.deepcopy(self.eqns)
               new_eqns = current_eqns_copy + [e]
               children_states.append(TwentyFourState(starting_numbers=[e['value']]+remaining_nums,starting_equations=new_eqns))
       return children_states

s = TwentyFourState([2, 4, 5, 10])
solutions, iterations = s.beam_search({'beam_width':1})
path = solutions[0].solution_path()

file_name = 'puzzles_24_100.txt'
State.solve_batch(file_name,
                  lambda file_name: TwentyFourState.parse_file(file_name,is_csv_file=False),
                  params={'max_iterations':4, 'beam_width':1},algorithm='beam_search')

