import pytest

import app as notes_app


@pytest.fixture
def client(tmp_path):
    notes_app.app.config.update(TESTING=True, DATABASE=str(tmp_path / "test.db"))
    notes_app.init_db()
    return notes_app.app.test_client()


def add_note(client, title, content):
    return client.post("/notes", data={"title": title, "content": content})


def test_healthz(client):
    assert client.get("/healthz").get_json() == {"status": "ok"}


def test_create_and_search_notes(client):
    add_note(client, "Groceries", "Milk, bread")
    add_note(client, "Meeting", "Thursday 10AM")

    page = client.get("/", query_string={"q": "Groc"}).get_data(as_text=True)
    assert "Groceries" in page
    assert "Meeting" not in page


def test_empty_note_is_rejected(client):
    assert add_note(client, "", "").status_code == 400