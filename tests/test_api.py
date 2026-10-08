from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_job():
    response = client.post(
        "/jobs",
        json={
            "event_name": "Python Workshop",
            "certificate_title": "Certificate of Participation",
            "issue_date": "2026-10-08",
            "recipients": [
                {"name": "Test User 1"},
                {"name": "Test User 2"}
            ]
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "job_id" in data
    assert data["total"] == 2


def test_empty_recipients():
    response = client.post(
        "/jobs",
        json={
            "event_name": "Python Workshop",
            "certificate_title": "Certificate of Participation",
            "issue_date": "2026-10-08",
            "recipients": []
        }
    )

    assert response.status_code == 400


def test_invalid_recipient_name():
    response = client.post(
        "/jobs",
        json={
            "event_name": "Python Workshop",
            "certificate_title": "Certificate of Participation",
            "issue_date": "2026-10-08",
            "recipients": [
                {"name": "   "}
            ]
        }
    )

    assert response.status_code == 400


def test_certificate_generation():
    response = client.post(
        "/jobs",
        json={
            "event_name": "Python Workshop",
            "certificate_title": "Certificate of Participation",
            "issue_date": "2026-10-08",
            "recipients": [
                {"name": "Certificate Test"}
            ]
        }
    )

    assert response.status_code == 200

    job_id = response.json()["job_id"]

    certificates_response = client.get(
        f"/jobs/{job_id}/certificates"
    )

    assert certificates_response.status_code == 200

    certificates = certificates_response.json()

    assert len(certificates) == 1
    assert certificates[0]["status"] == "COMPLETED"
    assert certificates[0]["recipient_name"] == "Certificate Test"


def test_job_status():
    response = client.post(
        "/jobs",
        json={
            "event_name": "Status Test",
            "certificate_title": "Certificate",
            "issue_date": "2026-10-08",
            "recipients": [
                {"name": "Status User"}
            ]
        }
    )

    assert response.status_code == 200

    job_id = response.json()["job_id"]

    status_response = client.get(f"/jobs/{job_id}")

    assert status_response.status_code == 200

    data = status_response.json()

    assert data["job_id"] == job_id
    assert data["total"] == 1
    assert data["completed"] == 1
    assert data["failed"] == 0
    assert data["status"] == "COMPLETED"


def test_individual_certificate_failure(monkeypatch):
    from app import worker

    original_generate = worker.generate_certificate

    def fake_generate(
        recipient_name,
        event_name,
        certificate_title,
        issue_date,
        certificate_id
    ):
        if recipient_name == "Fail User":
            raise Exception("Simulated certificate failure")

        return original_generate(
            recipient_name,
            event_name,
            certificate_title,
            issue_date,
            certificate_id
        )

    monkeypatch.setattr(
        worker,
        "generate_certificate",
        fake_generate
    )

    response = client.post(
        "/jobs",
        json={
            "event_name": "Failure Test",
            "certificate_title": "Certificate",
            "issue_date": "2026-10-08",
            "recipients": [
                {"name": "Good User"},
                {"name": "Fail User"},
                {"name": "Another Good User"}
            ]
        }
    )

    assert response.status_code == 200

    job_id = response.json()["job_id"]

    status_response = client.get(f"/jobs/{job_id}")
    data = status_response.json()

    assert data["total"] == 3
    assert data["completed"] == 2
    assert data["failed"] == 1
    assert data["status"] == "COMPLETED"


def test_retrieve_generated_certificate():
    response = client.post(
        "/jobs",
        json={
            "event_name": "Download Test",
            "certificate_title": "Certificate",
            "issue_date": "2026-10-08",
            "recipients": [
                {"name": "Download User"}
            ]
        }
    )

    assert response.status_code == 200

    job_id = response.json()["job_id"]

    certificates_response = client.get(
        f"/jobs/{job_id}/certificates"
    )

    certificates = certificates_response.json()

    certificate_id = certificates[0]["certificate_id"]

    download_response = client.get(
        f"/certificates/{certificate_id}"
    )

    assert download_response.status_code == 200
    assert download_response.headers["content-type"] == "application/pdf"
    assert download_response.content.startswith(b"%PDF")