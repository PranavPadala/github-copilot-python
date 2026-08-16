import copy
import random

SIZE = 9
EMPTY = 0
DIFFICULTY_CLUES = {
    'easy': 45,
    'medium': 36,
    'hard': 30,
}


def deep_copy(board):
    return copy.deepcopy(board)

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True

def remove_cells(board, clues):
    attempts = SIZE * SIZE - clues
    while attempts > 0:
        row = random.randrange(SIZE)
        col = random.randrange(SIZE)
        if board[row][col] != EMPTY:
            board[row][col] = EMPTY
            attempts -= 1

def count_solutions(board, limit=2):
    working_board = deep_copy(board)
    solutions = 0

    def backtrack():
        nonlocal solutions

        if solutions >= limit:
            return

        empty_cell = None
        for row in range(SIZE):
            for col in range(SIZE):
                if working_board[row][col] == EMPTY:
                    empty_cell = (row, col)
                    break
            if empty_cell is not None:
                break

        if empty_cell is None:
            solutions += 1
            return

        row, col = empty_cell
        for candidate in range(1, SIZE + 1):
            if is_safe(working_board, row, col, candidate):
                working_board[row][col] = candidate
                backtrack()
                working_board[row][col] = EMPTY
                if solutions >= limit:
                    return

    backtrack()
    return solutions


def get_clues_for_difficulty(difficulty=None, clues=None):
    if clues is not None:
        return int(clues)

    normalized = (difficulty or 'medium').lower()
    if normalized not in DIFFICULTY_CLUES:
        raise ValueError(f"Unsupported difficulty: {difficulty}")
    return DIFFICULTY_CLUES[normalized]


def generate_puzzle(clues=35, difficulty=None):
    if difficulty is not None:
        target_clues = get_clues_for_difficulty(difficulty=difficulty)
        minimum_clues = target_clues
    else:
        target_clues = int(clues)
        minimum_clues = 0

    for _ in range(150):
        board = create_empty_board()
        fill_board(board)
        solution = deep_copy(board)

        puzzle = deep_copy(board)
        positions = [(row, col) for row in range(SIZE) for col in range(SIZE)]
        random.shuffle(positions)

        for row, col in positions:
            filled_count = sum(cell != EMPTY for puzzle_row in puzzle for cell in puzzle_row)
            if filled_count <= max(target_clues, minimum_clues):
                break

            original_value = puzzle[row][col]
            puzzle[row][col] = EMPTY
            if count_solutions(puzzle, limit=2) != 1:
                puzzle[row][col] = original_value

        filled_count = sum(cell != EMPTY for puzzle_row in puzzle for cell in puzzle_row)
        if filled_count >= minimum_clues and filled_count <= max(target_clues, minimum_clues):
            return puzzle, solution

    raise ValueError(f"Unable to generate a unique-solution puzzle for difficulty={difficulty!r}, clues={clues!r}")
