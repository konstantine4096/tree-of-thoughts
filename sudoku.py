from search import *
import itertools
import math
import copy
import ast
import numpy as np
from pathlib import Path

class SudokuBoard(State):
    
    def __init__(self, rows):
        # A Sudoku board is represented as a list of rows, where each row is a list of digit strings or '*' (or '_').
        super().__init__()
        self.rows = rows
        N = len(rows)
        self.N = N

    def __str__(self):
        return str(self.rows)

    def blank_cells(self):
        '''
        Return the total number of blank cells in the puzzle.
        '''
        total = 0
        for row in self.rows:
            total += row.count('*') + row.count('_')
        return total
        
    @classmethod
    # A factory method that builds a Sudoku board from a string (rather than a list) of the form "[[...], ..., [...]]",
    # where every entry in the inner lists is either a digit or an underscore or an asterisk (the latter two are interchangeable).
    def from_line(cls,line_string):
        try: 
            lst = ast.literal_eval(line_string)
            return cls([[str(x) for x in l] for l in lst])
        except:        
            lst = ast.literal_eval(line_string.replace('*',"'*'").replace('_',"'*'"))
            return cls([[str(x) for x in l] for l in lst])
        
    @staticmethod
    #Return a list of boards built from a text file whose every line is a string that can be parsed by from_line: 
    def parse_file(file_name):
        lines = [l.strip() for l in Path(file_name).read_text().split("\n") if l]
        return [SudokuBoard.from_line(l) for l in lines]
        
    def extends(self,board):
        # Return True or False depending on whether the given board extends self.
        if self.N != board.N:
            return False
        for r in range(len(board.rows)):
            row = board.rows[r]
            for c in range(len(row)):
                entry = row[c]
                if entry.isdigit() and self.rows[r][c] != entry: 
                    return False
        return True 
            
    def distance(self):
        '''
        A decent distance estimate for a Sudoku goal is the number of blank cells. This is basically what depth-first uses by default. 
        '''
        return np.sum([row.count('*') for row in self.rows])    
        
    def all_unique(self,lst):
        '''
        Return True iff all (non-blank) elements in the given list are unique.
        '''
        non_blanks = [x for x in lst if x != '*']
        return len(non_blanks) == len(set(non_blanks))

    def validBlock(self,starting_row,starting_col,n):
    # Given a square board of size n^2 x n^2, we check the n x n sub-block whose upper left-hand cell is at (starting_row, starting_col).
    # (Therefore, its lower right-hand cell is at (starting_row + n, starting_col + n).) All digits in such a sub-block must be distinct.
        entries = set([])
        for row in range(starting_row,starting_row + n):
            for col in range(starting_col,starting_col + n):
                value = self.rows[row][col]
                if value != '*':
                    if value in entries:
                        return False
                    else:
                        entries.add(value)
        return True

    def valid_blocks(self):
        n = int(math.sqrt(self.N))
        for row in range(n):
            for col in range(n):
                if not(self.validBlock(row*n,col*n,n)):
                    return False
        return True

    def is_valid(self):
        '''
        A square n^2 x n^2 grid is valid iff every row, every column, and every n x n sub-grid has unique entries.
        '''
        for row in self.rows:
            if not(self.all_unique(row)):
                return False
        cols = [[row[i] for row in self.rows] for i in range(self.N)]
        for col in cols: 
            if not(self.all_unique(col)):
                return False
        if not(self.valid_blocks()):
            return False
        return True

    def missing_values(self,row):
        return [str(v) for v in range(1,10) if not(str(v) in self.rows[row])]

    def can_be_placed(self,row,col,v):
        original_entry = self.rows[row][col]
        self.rows[row][col] = v
        res = self.is_valid()
        self.rows[row][col] = original_entry
        return res
    
    def deduce(self):
        '''
        Carry out all uniquely-determined-cell deductions possible in the current board. 
        Return the deductions as a list of dictionaries of the form {'row': ..., 'unique_cell': ..., 'value': ...}
        '''
        initial_rows = copy.deepcopy(self.rows)
        deductions = []
        for row in range(9):
            missing_vals = self.missing_values(row)
            for v in missing_vals:
                cands = []
                for col in [c for c in range(9) if not(self.rows[row][c].isdigit())]:
                    if self.can_be_placed(row,col,v):
                        cands.append(col)
                if len(cands) == 1:
                    deductions.append({'row': row, 'unique_cell': cands[0], 'value': v})
        self.rows = initial_rows
        return deductions

    def solve_deductively(self):
        '''
        Solve a Sudoku puzzle by pure Boolean constraint propagation. 
        '''
        done = False
        while not(done):
            if self.blank_cells() == 0:
                return True
            deductions = self.deduce()
            for d in deductions:
                self.rows[d['row']][d['unique_cell']] = d['value']
            if len(deductions) < 1: 
                done = True
        return self.blank_cells() == 0 
                
    def is_det(self,row,col):
        original_entry = self.rows[row][col]
        cands = 0
        for v in range(1,10):
            self.rows[row][col] = str(v)
            if self.is_valid():
                cands += 1
        self.rows[row][col] = original_entry
        return cands == 1
    
    def det_cells(self):
        uniquely_determined_cells = []
        for row in range(9):
            for col in range(9):
                if self.is_det(row,col):
                    uniquely_determined_cells.append((row,col))
        if uniquely_determined_cells:
            s = ''
            for (r,c) in uniquely_determined_cells:
                s += " -- (" + str(r) + ", " + str(c) + ")"
        return uniquely_determined_cells
                    
    def is_solution(self):
        return self.is_valid() and not([row for row in self.rows if '*' in row])        

    def cands(self,r,c):
        row = self.rows[r]
        col = [row[c] for row in self.rows]
        ruled_out = set([d for d in row + col if d != '*'])
        return list(reversed([digit for digit in [chr(i) for i in range(49,49+self.N)] if not(digit in ruled_out)]))
    
    def get_candidates(self,r,c):
        row = self.rows[r]
        return [row[:c] + [digit] + row[c+1:] for digit in self.cands(r,c)]

    def get_all_candidates(self,r,cols):
        return list(itertools.chain.from_iterable(self.get_candidates(r,c) for c in cols))
    
    def expand(self):
        new1, new2, new3 = [], [], []
        for r in range(self.N):
            row = self.rows[r]
            blanks = [i for i, entry in enumerate(row) if entry == '*']
            if not(blanks): 
                new1.append(copy.deepcopy(row))
            else:
                new2 = self.get_all_candidates(r,[blanks[0]])
                new3 = self.rows[r+1:]
                return [SudokuBoard(new1 + [cand] + new3) for cand in new2]
        return []

rows = "[[_,3,_,8,9,_,_,_,4],\
         [_,6,_,_,3,1,8,9,_],\
         [_,9,7,_,_,_,2,_,_],\
         [9,_,8,6,5,_,_,_,2],\
         [1,_,2,_,_,_,6,_,3],\
         [6,_,_,_,4,2,9,7,_],\
         [3,_,5,_,_,9,_,2,_],\
         [_,2,_,3,_,5,7,8,_],\
         [_,_,_,4,2,_,_,1,5]]"

b = SudokuBoard.from_line(rows)

(solutions,iterations) = b.dfs({'max_states_to_show':0})

file_name = "easy_sudoku_puzzles_9x9_100.txt"
State.solve_batch(file_name,SudokuBoard.parse_file,{'max_iterations':800})
