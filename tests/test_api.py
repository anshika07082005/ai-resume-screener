import uuid

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


# ============================================================
# SYSTEM ENDPOINTS
# ============================================================

def test_root_endpoint():

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["version"] == "2.0.0"

    assert (
        "AI Resume Screener"
        in data["message"]
    )


def test_health_endpoint():

    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"

    assert (
        data["service"]
        == "AI Resume Screener"
    )

    assert data["version"] == "2.0.0"


# ============================================================
# AUTHENTICATION
# ============================================================

def test_register_login_and_me():

    random_email = (
        f"test_{uuid.uuid4().hex}@example.com"
    )

    password = "TestPassword123"


    # --------------------------------------------------------
    # REGISTER
    # --------------------------------------------------------

    register_response = client.post(
        "/register",
        data={
            "email": random_email,
            "password": password,
        },
    )

    assert (
        register_response.status_code
        == 200
    )

    register_data = (
        register_response.json()
    )

    assert (
        register_data["email"]
        == random_email
    )


    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------

    login_response = client.post(
        "/login",
        data={
            "email": random_email,
            "password": password,
        },
    )

    assert (
        login_response.status_code
        == 200
    )

    login_data = (
        login_response.json()
    )

    assert "access_token" in login_data

    assert (
        login_data["token_type"]
        == "bearer"
    )


    access_token = (
        login_data["access_token"]
    )


    # --------------------------------------------------------
    # CURRENT USER
    # --------------------------------------------------------

    me_response = client.get(
        "/me",
        headers={
            "Authorization":
                f"Bearer {access_token}"
        },
    )

    assert (
        me_response.status_code
        == 200
    )

    me_data = (
        me_response.json()
    )

    assert (
        me_data["email"]
        == random_email
    )

    assert (
        me_data["authenticated"]
        is True
    )


def test_me_requires_authentication():

    response = client.get(
        "/me"
    )

    assert response.status_code == 401