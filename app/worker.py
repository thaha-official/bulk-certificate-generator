from .database import SessionLocal
from .models import GenerationJob, Certificate
from .certificate import generate_certificate


def process_job(
    job_id,
    recipients,
    event_name,
    certificate_title,
    issue_date
):
    db = SessionLocal()

    try:
        job = db.query(GenerationJob).filter(
            GenerationJob.id == job_id
        ).first()

        if not job:
            return

        job.status = "PROCESSING"
        db.commit()

        for recipient in recipients:
            certificate = Certificate(
                job_id=job_id,
                recipient_name=recipient["name"],
                status="PROCESSING"
            )

            db.add(certificate)
            db.commit()
            db.refresh(certificate)

            try:
                file_path = generate_certificate(
                    recipient["name"],
                    event_name,
                    certificate_title,
                    issue_date,
                    certificate.id
                )

                certificate.status = "COMPLETED"
                certificate.file_path = file_path
                job.completed += 1

            except Exception as e:
                certificate.status = "FAILED"
                certificate.error_message = str(e)
                job.failed += 1

            db.commit()

        job.status = "COMPLETED"
        db.commit()

    finally:
        db.close()