import copy

from app import CURRENT


def test_index_route_returns_html(client):
    response = client.get('/')

    assert response.status_code == 200
    assert 'text/html' in response.content_type


def test_new_game_route_creates_puzzle_and_solution(client):
    response = client.get('/new?clues=35')

    assert response.status_code == 200
    assert 'puzzle' in response.get_json()
    puzzle = response.get_json()['puzzle']
    assert len(puzzle) == 9
    assert all(len(row) == 9 for row in puzzle)
    assert puzzle == CURRENT['puzzle']
    assert CURRENT['solution'] is not None
    assert all(cell in range(0, 10) for row in puzzle for cell in row)


def test_check_solution_returns_empty_incorrect_list_for_correct_board(client):
    client.get('/new?clues=35')
    board = copy.deepcopy(CURRENT['solution'])

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert response.get_json()['incorrect'] == []


def test_check_solution_returns_wrong_coordinates_for_incorrect_board(client):
    client.get('/new?clues=35')
    board = copy.deepcopy(CURRENT['solution'])
    wrong_value = (CURRENT['solution'][0][0] % 9) + 1
    board[0][0] = wrong_value

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert [0, 0] in response.get_json()['incorrect']


def test_check_solution_fails_when_no_game_is_active(client):
    response = client.post('/check', json={'board': [[0 for _ in range(9)] for _ in range(9)]})

    assert response.status_code == 400
    assert response.get_json()['error'] == 'No game in progress'
