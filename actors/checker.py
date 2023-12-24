import json
import copy
import common.consts as consts
import math

class StateCheckerBase(object):

    def __init__(self, state_manager) -> None:
        self.state_manager = state_manager

    def check_current_state(self):
        return None


class SudokuStateCheckResults:

    def __init__(self) -> None:
        self.rows = []
        self.cols = []
        self.is_valid = False
        self.solution_found = False
        self.message = ""


def validBlock(result,starting_row,starting_col,n):
    # Given a board of size n^2 X n^2, we check the n X n subblock whose upper left-hand cell is (starting_row, starting_col).
    # Therefore, its lower right-hand cell is (starting_row+n, starting_col+n).
    entries = set([])
    for row in range(starting_row,starting_row + n):
        for col in range(starting_col,starting_col + n):
            value = result.rows[row][col]
            if value != '*':
                if value in entries:
                    return False, 'Duplicate cell value (' + str(value)  + ') found in the ' + str(n) + ' X ' + str(n) + ' sub-grid starting at (' + str(row) + ', ' + str(col) + ').'
                else:
                    entries.add(value)
    return True,''
            
def validBlocks(result):
    n_square = len(result.rows)
    if n_square != len(result.cols):
        return False, "The board is not a square matrix!"        
    n = int(math.sqrt(n_square))
    if (n * n != n_square):
        return True, ''
    for row in range(n):
        for col in range(n):
            res, msg = validBlock(result,row*n,col*n,n)
            if not(res):
                return res,msg
    return True,''
    
class RuleBasedSudokuStateChecker(StateCheckerBase):

    def __init__(self, state_manager) -> None:
        super().__init__(state_manager)

    def check_current_state(self):
        init_board = self.state_manager.get_initial_state()
        if init_board is None:
            raise "The initial board is invalid"
        current_board = self.state_manager.get_current_state()
        if current_board is None:
            raise "The current board is invalid"
        
        return RuleBasedSudokuStateChecker.check_sudoku_board(init_board, current_board)
    
    def check_sudoku_board(init_board, current_board):
        #print("HERE IS THE INIT_BOARD:\n" + str(init_board))
        #print("AND ITS TYPE: " + str(type(init_board)))

        result = SudokuStateCheckResults()
        for row in current_board:
            result.rows.append(row.tolist()[0])

        for col_idx in range(current_board.shape[1]):
            col = current_board[:, col_idx]
            result.cols.append(col.squeeze().tolist()[0])

        # Check constraint 1: the current board must have the same size as the initial board
        board_size = init_board.shape[0]
        if (current_board.shape[0] != board_size) or (current_board.shape[1] != board_size):
            result.is_valid = False
            result.message = "The current Sudoku board has a size different than the original board."
            return result
        
        # Check constraint 2: the board must be filled with numbers from 1-n with no repeated numbers in each line, horizontally or vertically.
        for i in range(len(result.rows)):
            row = result.rows[i]
            has_duplicates, duplicated_elem = RuleBasedSudokuStateChecker._has_duplicates(row)
            if has_duplicates:
                result.is_valid = False
                msg_tmpl = """Row {} is invalid, it contains two {}s."""
                result.message = msg_tmpl.format(json.dumps(row), duplicated_elem)
                return result
        
        for j in range(len(result.cols)):
            col = result.cols[j]
            has_duplicates, duplicated_elem = RuleBasedSudokuStateChecker._has_duplicates(col)
            if has_duplicates:
                result.is_valid = False
                msg_tmpl = """Column {} is invalid, it contains two {}s."""
                result.message = msg_tmpl.format(json.dumps(col), duplicated_elem)
                return result
        
        # Check constraint 3: the current board should not overwrite the cells that are already filled before puzzle solving, or has invalid content
        valid_content = [str(i+1) for i in range(board_size)]
        valid_content.append(consts.SUDOKU_UNFILLED_CELLS_PLACEHOLDER)
        for i in range(board_size):
            for j in range(board_size):
                if not current_board[i, j] in valid_content:
                    result.is_valid = False
                    msg_tmpl = """Cell [{}][{}] contains an invalid character. It should be either the string representation of a number between 1 to {}, or *"""
                    result.message = msg_tmpl.format(i, j, board_size)
                    return result            
                if (init_board[i, j] != consts.SUDOKU_UNFILLED_CELLS_PLACEHOLDER and init_board[i, j] != current_board[i, j]):
                    result.is_valid = False
                    msg_tmpl = """Cell [{}][{}] is invalid. The corresponding cell has been filled with {} initially. We cannot set it to a different number."""
                    result.message = msg_tmpl.format(i, j, init_board[i, j])
                    return result
        
        # TODO: Check constraint 4: The numbers in each block are distinct
        
        ok_blocks, block_error_msg = validBlocks(result)
        if not(ok_blocks):
            result.is_valid = False
            result.message = block_error_msg
            return result
        
        msg_tmpl = """The current board is valid. The rows are [{}], and the columns are [{}]"""
        result.message = msg_tmpl.format(json.dumps(result.rows), json.dumps(result.cols))
        result.is_valid = True

        has_unfilled_cells = False
        for i in range(board_size):
            for j in range(board_size):
                if str(current_board[i, j]) == "*":
                    has_unfilled_cells = True
        result.solution_found = not has_unfilled_cells

        return result

    def _has_duplicates(vec):
        if len(vec) <= 1:
            return False
        v = copy.deepcopy(vec)
        v = sorted(v)
        for i in range(len(v) - 1):
            if (not (str(v[i]) == "*")) and v[i] == v[i+1]:
                return True, v[i]
        return False, None        

class LLMBasedSudokuStateChecker(StateCheckerBase):
    def __init__(self, state_manager) -> None:
        super().__init__(state_manager)

    def check_current_state(self):
        return None
