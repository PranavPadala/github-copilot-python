from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import app, CURRENT
import pytest


@pytest.fixture
def client():
    CURRENT.clear()
    CURRENT.update({'puzzle': None, 'solution': None})
    app.config['TESTING'] = True
    with app.test_client() as test_client:
        yield test_client
