from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import GenerationJob, Certificate
from .schemas import GenerationRequest
from .worker import process_job


# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bulk Certificate Generator API")


@app.get("/")
def home():
    return {
        "message": "Bulk Certificate Generator API is running"
    }


@app.post("/jobs")
def create_job(
    request: GenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Validate recipients list
    if not request.recipients:
        raise HTTPException(
            status_code=400,
            detail="Recipients list cannot be empty"
        )

    # Validate recipient names
    for recipient in request.recipients:
        if not recipient.name.strip():
            raise HTTPException(
                status_code=400,
                detail="Recipient name cannot be empty"
            )

    # Create a new job
    job = GenerationJob(
        status="PENDING",
        total=len(request.recipients),
        completed=0,
        failed=0
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    # Convert recipients to dictionaries
    recipients = [
        {"name": recipient.name}
        for recipient in request.recipients
    ]

    # Start background certificate generation
    background_tasks.add_task(
        process_job,
        job.id,
        recipients,
        request.event_name,
        request.certificate_title,
        request.issue_date
    )

    return {
        "job_id": job.id,
        "status": job.status,
        "total": job.total
    }


@app.get("/jobs/{job_id}")
def get_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    job = db.query(GenerationJob).filter(
        GenerationJob.id == job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return {
        "job_id": job.id,
        "status": job.status,
        "total": job.total,
        "completed": job.completed,
        "failed": job.failed
    }


@app.get("/jobs/{job_id}/certificates")
def get_certificates(
    job_id: int,
    db: Session = Depends(get_db)
):
    job = db.query(GenerationJob).filter(
        GenerationJob.id == job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    certificates = db.query(Certificate).filter(
        Certificate.job_id == job_id
    ).all()

    return [
        {
            "certificate_id": certificate.id,
            "recipient_name": certificate.recipient_name,
            "status": certificate.status,
            "error": certificate.error_message
        }
        for certificate in certificates
    ]


@app.get("/certificates/{certificate_id}")
def download_certificate(
    certificate_id: int,
    db: Session = Depends(get_db)
):
    certificate = db.query(Certificate).filter(
        Certificate.id == certificate_id
    ).first()

    if not certificate:
        raise HTTPException(
            status_code=404,
            detail="Certificate not found"
        )

    if certificate.status != "COMPLETED":
        raise HTTPException(
            status_code=400,
            detail="Certificate is not available"
        )

    return FileResponse(
        certificate.file_path,
        media_type="application/pdf",
        filename=f"certificate_{certificate.id}.pdf"
    )