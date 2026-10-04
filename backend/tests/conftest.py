import pytest
from backend.app import create_app

@pytest.fixture
def app():
    """Create test application fixture."""
    app = create_app("testing")
    yield app

@pytest.fixture
def client(app):
    """Create test client fixture."""
    return app.test_client()
