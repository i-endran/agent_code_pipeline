from fastapi.testclient import TestClient
from app.main import app
import docx
import io
import pytest

client = TestClient(app)

def test_upload_txt():
    content = "This is a requirement."
    files = {"file": ("reqs.txt", content, "text/plain")}
    response = client.post("/api/scribe/upload", files=files)
    assert response.status_code == 200
    assert response.json()["text"] == content

def test_upload_docx():
    doc = docx.Document()
    doc.add_paragraph("This is a docx requirement.")

    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)

    files = {"file": ("reqs.docx", bio, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    response = client.post("/api/scribe/upload", files=files)
    assert response.status_code == 200
    assert "This is a docx requirement." in response.json()["text"]
