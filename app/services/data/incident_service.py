from datetime import date
from sqlalchemy import func
from app.models.incident import Incident
from app.models.student import Student
from .base_service import BaseDataService

class IncidentService(BaseDataService):
    def create_incident(self, class_id: int, student_id: int, description: str, incident_date: date) -> dict | None:
        if not all([class_id, student_id, description, incident_date]): return None
        new_incident = Incident(class_id=class_id, student_id=student_id, description=description, date=incident_date)
        with self._get_db() as db:
            db.add(new_incident)
            db.flush()
            db.refresh(new_incident)
            return {"id": new_incident.id}

    def get_incidents_for_class(self, class_id: int) -> list[dict]:
        with self._get_db() as db:
            incidents = (db.query(
                Incident.id, Incident.description, Incident.date,
                Student.id.label('student_id'), Student.first_name, Student.last_name
            )
            .join(Student, Incident.student_id == Student.id)
            .filter(Incident.class_id == class_id)
            .order_by(Incident.date.desc())
            .all())

            return [
                {
                    "id": i.id, "description": i.description, "date": i.date.isoformat(),
                    "student_id": i.student_id, "student_first_name": i.first_name, "student_last_name": i.last_name
                } for i in incidents
            ]

    def get_student_incidents(self, student_id: int, class_id: int) -> list[dict]:
        with self._get_db() as db:
            incidents = db.query(Incident).filter(
                Incident.student_id == student_id,
                Incident.class_id == class_id
            ).order_by(Incident.date.desc()).all()

            return [
                {"id": i.id, "description": i.description, "date": i.date.isoformat()}
                for i in incidents
            ]
