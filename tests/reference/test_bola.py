import os
import uuid

import httpx
import pytest


ENVIRONMENTS = [
    ("secure", "http://127.0.0.1:5001"),
    ("vulnerable", "http://127.0.0.1:5002"),
]


secure_url = os.environ.get("VAMPI_SECURE_URL")
if secure_url:
    ENVIRONMENTS = [("secure", secure_url)]


def register(client, username, password):
    response = client.post(
        "/users/v1/register",
        json={
            "username": username,
            "password": password,
            "email": f"{username}@example.com",
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "success"


def login(client, username, password):
    response = client.post(
        "/users/v1/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["auth_token"]


@pytest.mark.parametrize("mode,base_url", ENVIRONMENTS)
def test_bola_reference(mode, base_url):
    unique = uuid.uuid4().hex[:10]

    alice = f"alice_{unique}"
    bob = f"bob_{unique}"
    book = f"private_book_{unique}"
    secret = f"private_secret_{unique}"
    password = "DemoPassword123!"

    with httpx.Client(base_url=base_url, timeout=10) as client:
        register(client, alice, password)
        register(client, bob, password)

        alice_token = login(client, alice, password)
        bob_token = login(client, bob, password)

        # Alice creates her private book.
        created = client.post(
            "/books/v1",
            json={"book_title": book, "secret": secret},
            headers={"Authorization": f"Bearer {alice_token}"},
        )
        assert created.status_code == 200, created.text

        # Positive control: Alice can read her own book.
        owner_response = client.get(
            f"/books/v1/{book}",
            headers={"Authorization": f"Bearer {alice_token}"},
        )
        assert owner_response.status_code == 200
        assert owner_response.json()["secret"] == secret

        # Bob attempts to read Alice's private book.
        bob_response = client.get(
            f"/books/v1/{book}",
            headers={"Authorization": f"Bearer {bob_token}"},
        )

        if mode == "secure":
            assert bob_response.status_code == 404
            assert secret not in bob_response.text

        else:
            assert bob_response.status_code == 200
            assert bob_response.json()["owner"] == alice
            assert bob_response.json()["secret"] == secret
