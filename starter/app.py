from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None,
    'difficulty': 'medium',
    'hints_used': 0,
}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/new')
def new_game():
    difficulty = request.args.get('difficulty', 'medium')
    clues = request.args.get('clues')

    if clues is not None:
        puzzle, solution = sudoku_logic.generate_puzzle(clues=int(clues))
    else:
        puzzle, solution = sudoku_logic.generate_puzzle(difficulty=difficulty)

    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    CURRENT['difficulty'] = difficulty
    CURRENT['hints_used'] = 0
    return jsonify({'puzzle': puzzle, 'solution': solution, 'difficulty': difficulty})


@app.route('/check', methods=['POST'])
def check_solution():
    data = request.get_json(silent=True) or {}
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    if not isinstance(board, list) or len(board) != sudoku_logic.SIZE:
        return jsonify({'error': 'Invalid board data'}), 400

    incorrect = []
    for i in range(sudoku_logic.SIZE):
        row = board[i]
        if not isinstance(row, list) or len(row) != sudoku_logic.SIZE:
            return jsonify({'error': 'Invalid board data'}), 400
        for j in range(sudoku_logic.SIZE):
            if row[j] != solution[i][j]:
                incorrect.append([i, j])
    return jsonify({'incorrect': incorrect})


@app.route('/hint', methods=['POST'])
def hint_cell():
    data = request.get_json(silent=True) or {}
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    if not isinstance(board, list) or len(board) != sudoku_logic.SIZE:
        return jsonify({'error': 'Invalid board data'}), 400

    for i in range(sudoku_logic.SIZE):
        row = board[i]
        if not isinstance(row, list) or len(row) != sudoku_logic.SIZE:
            return jsonify({'error': 'Invalid board data'}), 400

    if board == solution:
        return jsonify({'solved': True, 'message': 'Puzzle solved'})

    for i in range(sudoku_logic.SIZE):
        row = board[i]
        for j in range(sudoku_logic.SIZE):
            if row[j] == 0:
                CURRENT['hints_used'] = CURRENT.get('hints_used', 0) + 1
                return jsonify({'row': i, 'col': j, 'value': solution[i][j], 'solved': False})

    return jsonify({'error': 'No empty cells available'}), 400


if __name__ == '__main__':
    app.run(debug=True)