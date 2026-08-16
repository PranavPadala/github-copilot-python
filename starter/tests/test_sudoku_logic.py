import sudoku_logic


def test_create_empty_board_returns_9_by_9_zero_board():
    board = sudoku_logic.create_empty_board()

    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(cell == sudoku_logic.EMPTY for row in board for cell in row)


def test_is_safe_rejects_conflicts_in_row_column_and_box():
    board = sudoku_logic.create_empty_board()

    board[0][0] = 5
    board[0][1] = 3
    board[1][0] = 7
    board[2][2] = 9

    assert sudoku_logic.is_safe(board, 0, 2, 5) is False
    assert sudoku_logic.is_safe(board, 0, 2, 1) is True

    board = sudoku_logic.create_empty_board()
    board[0][0] = 1
    board[0][1] = 2
    board[0][2] = 3
    board[1][0] = 4
    board[1][1] = 5
    board[1][2] = 6
    board[2][0] = 7
    board[2][1] = 8
    board[2][2] = 9

    assert sudoku_logic.is_safe(board, 0, 0, 9) is False
    assert sudoku_logic.is_safe(board, 0, 0, 4) is False


def test_fill_board_solves_empty_grid():
    board = sudoku_logic.create_empty_board()

    solved = sudoku_logic.fill_board(board)

    assert solved is True
    assert all(cell != sudoku_logic.EMPTY for row in board for cell in row)

    for row in board:
        assert sorted(row) == list(range(1, sudoku_logic.SIZE + 1))

    for col in range(sudoku_logic.SIZE):
        column_values = [board[row][col] for row in range(sudoku_logic.SIZE)]
        assert sorted(column_values) == list(range(1, sudoku_logic.SIZE + 1))

    for start_row in range(0, sudoku_logic.SIZE, 3):
        for start_col in range(0, sudoku_logic.SIZE, 3):
            values = []
            for row in range(start_row, start_row + 3):
                for col in range(start_col, start_col + 3):
                    values.append(board[row][col])
            assert sorted(values) == list(range(1, sudoku_logic.SIZE + 1))


def test_generate_puzzle_returns_puzzle_and_solution():
    puzzle, solution = sudoku_logic.generate_puzzle(clues=35)

    assert len(puzzle) == sudoku_logic.SIZE
    assert len(solution) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)
    assert all(len(row) == sudoku_logic.SIZE for row in solution)
    assert all(cell in range(0, sudoku_logic.SIZE + 1) for row in puzzle for cell in row)
    assert all(cell in range(1, sudoku_logic.SIZE + 1) for row in solution for cell in row)

    filled_cells = sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row)
    assert 0 < filled_cells <= 81
