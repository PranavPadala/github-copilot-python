import copy

import sudoku_logic
from app import CURRENT


def test_generate_puzzle_easy_medium_hard_are_distinct_and_unique(client):
    for difficulty, expected_minimum in {'easy': 45, 'medium': 36, 'hard': 30}.items():
        response = client.get(f'/new?difficulty={difficulty}')
        assert response.status_code == 200
        puzzle = response.get_json()['puzzle']
        filled = sum(cell != 0 for row in puzzle for cell in row)
        assert filled >= expected_minimum
        assert sudoku_logic.count_solutions(puzzle, limit=2) == 1


def test_hint_returns_one_valid_cell_and_tracks_usage(client):
    client.get('/new?difficulty=easy')
    board = copy.deepcopy(CURRENT['puzzle'])
    board[0][0] = 0
    response = client.post('/hint', json={'board': board})

    assert response.status_code == 200
    payload = response.get_json()
    assert set(payload.keys()) >= {'row', 'col', 'value'}
    assert payload['value'] == CURRENT['solution'][payload['row']][payload['col']]
    assert CURRENT['hints_used'] >= 1


def test_invalid_board_data_is_handled_cleanly(client):
    client.get('/new?difficulty=medium')
    response = client.post('/check', json={'board': [[1, 2, 3]]})
    assert response.status_code == 400
    assert 'error' in response.get_json()

    response = client.post('/hint', json={'board': None})
    assert response.status_code == 400
    assert 'error' in response.get_json()


def test_hint_on_solved_board_reports_completion_instead_of_no_empty_error(client):
    client.get('/new?difficulty=easy')
    response = client.post('/hint', json={'board': copy.deepcopy(CURRENT['solution'])})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload.get('solved') is True
