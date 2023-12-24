import sys
import time 
from common.config import Config
from tot.tot import TreeOfThought
import common.utils
from actors.llm import llm4 
import math
import random
from sudoku import *
import ast
import re
import argparse

#====================================================== GAME OF 24: 

def make_game_of_24_prompt(int_line):
    ints = [i.strip() for i in int_line.split(' ')]
    s = ints[0] + ', ' + ints[1] + ', ' + ints[2] + ' and ' + ints[3]
    prompt =  'You are an expert solver of game-of-24 puzzles, where you are given 4 positive integers and you use the four arithmetic '
    prompt += 'operators +, -, *, and /, along with left and right parentheses, to come up with an '
    prompt += 'expression whose value is 24. Each of the four given integers must appear exactly '
    prompt += 'once in the output expression. Here is an example of how such a puzzle is solved when '
    prompt += 'the four given integers are 6, 8, 12, and 5. The puzzle is solved by coming up with three intermediate equations:\n'
    prompt += 'First intermediate equation: 8 + 12. This gives a result of 20. Thus, the available numbers now are 6, 5, and 20.\n'
    prompt += 'Second intermediate equation: 20 / 5. This gives a result of 4. Thus, the available numbers now are 6 and 4.\n'
    prompt += 'Third  intermediate equation: 6 * 4. This gives the desired result of 24.\n'
    prompt += 'Thus, putting it all together, the output expression is: (8 + 12) * (20 / 5). '
    prompt += 'This expression is a solution because its value is 24 and it uses every given integer exactly once.\n'
    prompt += 'Now please try to solve the puzzle where the four given integers are these: ' + s + '.\n'
    prompt += 'Take a deep breath and think this out step-by-step, explaining your reasoning along the way.\n'
    prompt += 'Return your final solution in the following JSON format:  { "expression": "<your output expression>" }.\n'
    return prompt

def all_four_integers(exp,puzzle_string):
    ints = [i.strip() for i in puzzle_string.split(' ')] 
    exp_toks = common.utils.tokenize(exp,"+*()/-")
    return len(exp_toks) == 4 and set(exp_toks) == set(ints)
    
def solve_puzzle_of_24_with_single_prompt(puzzle_string,temp=1.0):
    prompt = make_game_of_24_prompt(puzzle_string)
    llm_reply = ''
    try:
        llm_reply = llm4([],msg=prompt,temp=temp)
    except:
        return (False, prompt,llm_reply,'LLM call failure')
    (successful_json_extraction,json_dict) = common.utils.extract_json_from_text_string(llm_reply,quote_digits=False)
    reason = ''
    if successful_json_extraction:
        exp = json_dict['expression']
        res = 0.0
        try:
            res = eval(exp)
        except:
            reason = 'Ill-formed expression.' 
        if res != 24:
            if not(reason):
                reason = 'Wrong result: ' + str(res)
            return (False,prompt,llm_reply, reason)
        else:
            all_present_once = False
            try:
                all_present_once = all_four_integers(exp,puzzle_string)
            except:
                pass
            if all_present_once:
                return (True,prompt,llm_reply, '')
            else:
                return (False,prompt,llm_reply, 'Not all four integers occur exactly once in the result')
    else:
        print("Could not extract a proper JSON object from this LLM reply: " + llm_reply,flush=True)
        return (False, prompt,llm_reply,'formatting error')        

def solve_puzzle_of_24_with_independent_iterations(puzzle_string,attempt_count=100,temp=1.0):
    for i in range(1,attempt_count+1):
        temp = random.random()                
        print("\n[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[\nAttempt #" + \
              str(i) + " with temp: "  + str(temp)  + " to solve this game-of-24 puzzle: " + \
              puzzle_string,flush=True)
        (success,prompt,llm_reply,reason) = solve_puzzle_of_24_with_single_prompt(puzzle_string,temp=temp)
        if success:
            print("----------- Fantastic - valid solution found on attempt #" + str(i) + "!",flush=True)
            print(">>>>>>>>Here is the prompt:\n" + prompt + \
                  "\n>>>>>>>>and here is the LLM's reply:\n" + llm_reply,flush=True)
            print(">>>>>>>> Final verdict: Success!", flush=True)
            print("\n]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]",flush=True)
            return True
        else:
            print("Attempt failed for this reason: " + reason + ".",flush=True)
            print(">>>>>>>>Here is the prompt:\n" + prompt + \
                  "\n>>>>>>>>and here is the LLM's reply:\n" + llm_reply,flush=True)
            print(">>>>>>>> Final verdict: Fail",flush=True)
            print("\n]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]",flush=True)
    return False 

def solve_puzzles_of_24_with_independent_iterations_batch(file_name,attempt_count=100,temp=1.0):
    lines = [l.strip() for l in common.utils.readFile(file_name).split("\n") if l]
    iteration = 0
    for l in lines:
        iteration += 1 
        print("============================================ Working on puzzle #" + \
              str(iteration) + ": " + l, flush=True)
        solve_puzzle_of_24_with_independent_iterations(l,attempt_count=attempt_count,temp=temp)

#====================================================== SUDOKU:        


def solve_sudoku_puzzle(puzzle_string):
    grid_dim = puzzle_string.count('[') - 1
    prompt = "Please solve this " +  str(grid_dim) + "x" + str(grid_dim) + " sudoku puzzle: " + \
        puzzle_string + ", where * represents a cell to be filled in."
    path_to_config_yaml = "./config.yaml"
    config = Config(path_to_config_yaml)
    tot = TreeOfThought(config)
    success, solution = tot.run(prompt)
    return success, puzzle_string, solution 

def showSols(S):
    for (p,sol) in S:
        print("Puzzle: " + p + " --- SOLUTION: " + str(sol))

def solve_sudoku_puzzle_with_single_prompt(puzzle_string,grid_dimension=9,temp=1.0):
    given_puzzle = SudokuBoard.from_line(puzzle_string)
    grid_dim_str = str(grid_dimension) + "x" + str(grid_dimension)
    sq_root = int(math.sqrt(grid_dimension))
    grid_dim_sq_root_str = str(sq_root) + "x" + str(sq_root)
    prompt = "Here is an example showing how to solve the 3x3 Sudoku puzzle [[1, *, *], [*, 1, *], [*, 2, *]], " + \
        "where * represents a blank cell to be filled in. First, notice that the second column already has 1 and 2, " + \
        "so the first cell in the second row needs to be 3. After this step, the first row has 1 and 3. Hence the " + \
        "last cell in the first row must be 2. Now, look at the cell at the intersection of the second row and " + \
        "the third column. It must be 3. As a result, the cell at the intersection of the third row and the third " + \
        "column must be 1. The remaining cells are now easy to fill in. In conclusion, the puzzle solution is " + \
        "[[1, 3, 2], [2, 1, 3], [3, 2, 1]].\n\nPlease try to solve this " + grid_dim_str + " Sudoku puzzle: "
    prompt += puzzle_string + "."
    prompt += '\nMake sure to fill in all the blank cells, and return your solution in the following JSON format: { "rows": [] }.'
    llm_reply = ''
    try:
        llm_reply = llm4([],msg=prompt,temp=temp)
    except:
        return (False, prompt,llm_reply,'LLM call failure')
    (successful_json_extraction,json_dict) = common.utils.extract_json_from_text_string(llm_reply)
    if successful_json_extraction:
        line_str = str(json_dict['rows'])
        print("Managed to extract the JSON answer, about to construct a Sudoku board from this flat string: " + line_str,flush=True)
        board = SudokuBoard.from_line(line_str)
        if not(board.has_dimension(grid_dimension)):
            return (False, prompt,llm_reply,'formatting error')
        res1 = board.extends(given_puzzle)
        res2 = board.is_valid()
        res3 = board.blank_cells() == 0
        res = res1 and res2 and res3
        error_reason = '' if res else ('extension error' if not(res1) else ('incomplete' if not(res3) else 'logical/validity error'))
        return (res,prompt,llm_reply,error_reason)
    else:
        print("Could not extract a proper JSON object from this LLM reply: " + llm_reply,flush=True)
        return (False, prompt,llm_reply,'formatting error')

def solve_sudoku_puzzle_with_independent_iterations(puzzle_string,grid_dimension=9,attempt_count=100,temp=1.0):
    for i in range(1,attempt_count+1):
        print("\n[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[\nAttempt #" + str(i) + \
              " with temp: " + str(temp) + " to solve this puzzle: " + puzzle_string,flush=True)
        (success,prompt,llm_reply,reason) = solve_sudoku_puzzle_with_single_prompt(puzzle_string,
                                                                                   grid_dimension=grid_dimension,
                                                                                   temp=temp)
        if success:
            print("----------- Fantastic - valid solution found on attempt #" + str(i) + "!",flush=True)
            print(">>>>>>>>Here is the prompt:\n" + prompt + \
                  "\n>>>>>>>>and here is the LLM's reply:\n" + llm_reply,flush=True)
            print(">>>>>>>> FINAL VERDICT: SUCCESS!", flush=True)
            print("\n]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]",flush=True)
            return True
        else:
            print("Attempt failed for this reason: " + reason + ".",flush=True)
            print(">>>>>>>>Here is the prompt:\n" + prompt + \
                  "\n>>>>>>>>and here is the LLM's reply:\n" + llm_reply,flush=True)
            print(">>>>>>>> FINAL VERDICT: FAIL",flush=True)
            print("\n]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]",flush=True)
    return False 

def solve_sudoku_puzzle_with_independent_iterations_batch(file_name,
                                                          grid_dimension=9,
                                                          attempt_count=100,
                                                          temp=1.0):
    lines = [l.strip() for l in common.utils.readFile(file_name).split("\n") if l]
    iteration = 0
    for l in lines:
        iteration += 1 
        print("============================================ Working on puzzle #" + \
              str(iteration) + ": " + l, flush=True)
        solve_sudoku_puzzle_with_independent_iterations(l,
                                                        grid_dimension=grid_dimension,
                                                        attempt_count=attempt_count,
                                                        temp=temp)
              
def solve_sudoku_puzzle_batch(puzzle_file):
    lines = [l.strip() for l in common.utils.readFile(puzzle_file).split("\n") if l]
    S, F = [], []
    iteration = 0
    execution_times = []
    for l in lines:
        iteration += 1
        print("Working on puzzle #" + str(iteration) + "...",flush=True)
        start_time = time.time()
        success, puzzle_string, solution = solve_sudoku_puzzle(l)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print("Execution time for puzzle #" + str(iteration) + ": " + \
              str(elapsed_time) + " seconds.", flush=True)
        execution_times.append(elapsed_time)
        if success:
            S.append((puzzle_string,solution,elapsed_time))
        else:
            F.append((puzzle_string,elapsed_time))
    print("===================== Search was able to solve " + str(len(S)) +
          " puzzles in " + str(np.sum(execution_times)) + " seconds (avg time: " + \
          str(np.mean(execution_times)) + ").")
    print("\nSuccesses: " + str(len(S)))
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('binomial-sudoku', type=str)
    parser.add_argument('binomial-24', type=str)    
    first_arg = sys.argv[1]
    if first_arg == 'binomial-sudoku':
        puzzle_file = sys.argv[2]
        grid_dimension = int(sys.argv[3])
        attempt_count = 100
        try:
            attempt_count = int(sys.argv[4])
        except:
            pass
        temp = random.random()
        try:
            temp = float(sys.argv[5])
        except:
            pass
        print("Will try to solve the puzzles in " + puzzle_file + \
              " with indepedent iterations. Grid dimension: " + \
              str(grid_dimension) + ", attempt_count: " + \
              str(attempt_count),flush=True)
        solve_sudoku_puzzle_with_independent_iterations_batch(puzzle_file,
                                                              grid_dimension=grid_dimension,
                                                              attempt_count=attempt_count,
                                                              temp=temp)
    elif first_arg == 'binomial-24':
        puzzle_file = sys.argv[2]
        attempt_count = 100
        try:
            attempt_count = int(sys.argv[3])
        except:
            pass
        temp = random.random()
        try:
            temp = float(sys.argv[4])
        except:
            pass
        print("Will try to solve the game-of-24 puzzles in " + puzzle_file + \
              " with indepedent iterations. Attempt_count: " + \
              str(attempt_count) + ", temp: " + str(temp),flush=True)
        solve_puzzles_of_24_with_independent_iterations_batch(puzzle_file,
                                                              attempt_count=attempt_count,
                                                              temp=temp)        
    else:
        puzzle_file = first_arg
        solve_sudoku_puzzle_batch(puzzle_file)
