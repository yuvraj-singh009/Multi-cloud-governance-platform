
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


import os

# Provide test-only configuration before importing the application.
os.environ.setdefault(
    "SUPABASE_URL",
    "https://example.supabase.co"
)

os.environ.setdefault(
    "SUPABASE_SECRET_KEY",
    "ci-test-placeholder-key"
)

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

