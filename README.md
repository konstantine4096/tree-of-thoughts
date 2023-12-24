# ReadMe 

This repo is built on top of a copy of [Jieyi Long's ToT repo](https://github.com/jieyilong/tree-of-thought-puzzle-solver). As described below in more detail, this repo contains:

 1. an implementation of classical AI search algorithms and a formulation of Sudoku and the game of 24 as search problems;
 2. two new Sudoku puzzle datasets (consisting of 100 4x4 puzzles and 100 easy 9x9 puzzles);
 3.  logs/results from running Long's ToT algorithm on these new datasets;
 4.  logs/results from running a naive "binomial" algorithm on both of the above datasets;
 5. a file containing the 100 game-of-24 puzzles used in the paper *[Tree of Thoughts: Deliberate Problem Solving wit Large Language Models](https://arxiv.org/pdf/2305.10601.pdf)*;
 6. logs/results from running the binomial algorithm with GPT-4 as the solver on these 100 game-of-24 puzzles.

More details are provided below.
## Classical AI Search
The main file is [search.py](https://github.com/konstantine4096/tot/blob/main/search.py), which implements classical AI search algorithms (depth-first, breadth-first, iterative deepening, best-first, beam search, and A*). The files [sudoku.py](https://github.com/konstantine4096/tot/blob/main/sudoku.py) and [twenty_four.py](https://github.com/konstantine4096/tot/blob/main/twenty_four.py) derive appropriate subclasses from the base class State (introduced in search.py). Use these to solve Sudoku and game-of-24 puzzles, respectively, using classical search.  

## ToT Results on Sudoku

There are two data files for Sudoku puzzles: [sudoku_4x4_puzzles_100.txt](https://github.com/konstantine4096/tree-of-thoughts/blob/main/new_data/sudoku_4x4_puzzles_100.txt) and [easy_sudoku_puzzles_9x9_100.txt](https://github.com/konstantine4096/tree-of-thoughts/blob/main/new_data/easy_sudoku_puzzles_9x9_100.txt). Each contains 100 freshly generated Sudoku puzzles (with grid dimensions 4x4 and 9x9, respectively). 

## Data
All data files can be found in the directory [new_data](https://github.com/konstantine4096/tree-of-thoughts/tree/main/new_data). These include the newly generated Sudoku puzzles, as well as logs for all the results reported in the Medium article.  

## How to do Inference
I used [OpenRouter](https://openrouter.ai/docs#models) for the convenience of being able to experiment with a host of language models at (relatively) reasonable prices. In the file actors/llm.py, you should insert your own OpenRouter key as the value of the `api_key` argument:

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="...")

If you prefer to use your OpenAI key instead and work only with OpenAI models, you will need to change the `call_loop` function in that file accordingly. 

## Replicating the Experiments

 - To run Long's ToT code on a given file of Sudoku puzzles: `python3 main.py <text-file>`
 - To run "P+" (aka the "binomial" LLM algorithm) on a text file of Sudoku puzzles, do:
 `python3 main.py binomial-sudoku <text-file> <grid-dim> {<max_attempts>} {<temp>}`
 The `<text-file>` argument is the name of the text file containing the puzzles. The rest of the arguments are numeric: `<grid-dim>` is the dimension of the grid (4 or 9); `<max-attempts>` is the maximum number of repetitions; and `<temp>` is the temperature. The last two arguments are optional. The default maximum number of attempts is 100. If no temperature is specified, a random value between 0 and 1 is used. 
 - To run P+ on a text file of games of 24, do: `python3 main.py binomial-24 <text-file> {max_attempts} {temp}`. The `<max-attempts>` and `<temp>` arguments are again optional, with the same defaults as specified above.

