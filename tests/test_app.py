import pytest

import app as notes_app

XSS_PAYLOAD = "<script>alert(1)</script>"


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


def test_search_is_not_sql_injectable(client):
    add_note(client, "Secret", "should stay hidden")

    page = client.get("/", query_string={"q": "x' OR 1=1 --"}).get_data(as_text=True)
    assert "should stay hidden" not in page


def test_search_term_is_html_escaped(client):
    page = client.get("/", query_string={"q": XSS_PAYLOAD}).get_data(as_text=True)
    assert XSS_PAYLOAD not in page
    assert "&lt;script&gt;" in page


def test_note_content_is_html_escaped(client):
    add_note(client, "Hello", XSS_PAYLOAD)
    page = client.get("/").get_data(as_text=True)
    assert XSS_PAYLOAD not in page
    assert "&lt;script&gt;" in page
