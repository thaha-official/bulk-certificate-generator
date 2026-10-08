# Bulk Certificate Generator API

## Objective

A backend API that accepts a certificate generation request for multiple recipients and generates certificates using a predefined template.

## Technology Used

- Python
- FastAPI
- SQLite
- SQLAlchemy
- ReportLab
- Pytest

## Project Structure

```text
Bulk-Certificate-Generator/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── certificate.py
│   └── worker.py
│
├── certificates/
├── tests/
│   └── test_api.py
├── requirements.txt
└── README.md