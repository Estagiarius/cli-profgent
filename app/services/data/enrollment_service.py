from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.student import Student
from app.models.class_enrollment import ClassEnrollment
from app.models.class_ import Class
from .base_service import BaseDataService

class EnrollmentService(BaseDataService):
    def get_student_enrollments(self, student_id: int) -> list[dict]:
        with self._get_db() as db:
            enrollments = (db.query(
                ClassEnrollment.id, ClassEnrollment.status, Class.name.label('class_name'), Class.id.label('class_id')
            )
            .join(Class, ClassEnrollment.class_id == Class.id)
            .filter(ClassEnrollment.student_id == student_id)
            .all())

            return [
                {
                    "id": e.id, "status": e.status,
                    "class_name": e.class_name, "class_id": e.class_id
                } for e in enrollments
            ]

    def add_student_to_class(self, student_id: int, class_id: int, call_number: int, status: str = "Active") -> dict | None:
        if not all([student_id, class_id, call_number is not None]): return None
        with self._get_db() as db:
            existing = db.query(ClassEnrollment).filter_by(student_id=student_id, class_id=class_id).first()
            if existing:
                existing.call_number = call_number
                existing.status = status
                db.flush()
                return {"id": existing.id, "student_id": existing.student_id, "class_id": existing.class_id, "status": existing.status}

            enrollment = ClassEnrollment(student_id=student_id, class_id=class_id, call_number=call_number, status=status)
            db.add(enrollment)
            db.flush()
            db.refresh(enrollment)
            return {"id": enrollment.id, "student_id": enrollment.student_id, "class_id": enrollment.class_id, "status": enrollment.status}

    def get_enrollments_for_class(self, class_id: int) -> list[dict]:
        with self._get_db() as db:
            enrollments = (db.query(
                ClassEnrollment.id, ClassEnrollment.call_number, ClassEnrollment.status, ClassEnrollment.student_id,
                Student.first_name, Student.last_name, Student.birth_date
            )
            .join(Student, ClassEnrollment.student_id == Student.id)
            .filter(ClassEnrollment.class_id == class_id)
            .order_by(ClassEnrollment.call_number)
            .all())

            return [
                {
                    "id": e.id, "call_number": e.call_number, "status": e.status,
                    "student_id": e.student_id,
                    "student_first_name": e.first_name, "student_last_name": e.last_name,
                    "student_birth_date": e.birth_date.isoformat() if e.birth_date else None
                } for e in enrollments
            ]

    def update_enrollment_status(self, enrollment_id: int, status: str):
        with self._get_db() as db:
            enrollment = db.query(ClassEnrollment).filter(ClassEnrollment.id == enrollment_id).first()
            if enrollment:
                enrollment.status = status

    def enroll_students(self, class_id: int, student_ids: list[int]):
        with self._get_db() as db:
            next_call_number = self._get_next_call_number(db, class_id)

            existing_enrollments = db.query(ClassEnrollment).filter(
                ClassEnrollment.class_id == class_id,
                ClassEnrollment.student_id.in_(student_ids)
            ).all()

            existing_map = {e.student_id: e for e in existing_enrollments}
            new_enrollments_data = []

            for student_id in student_ids:
                existing = existing_map.get(student_id)
                if existing:
                    existing.status = "Active"
                    existing.call_number = next_call_number
                else:
                    new_enrollments_data.append({
                        "class_id": class_id,
                        "student_id": student_id,
                        "call_number": next_call_number,
                        "status": "Active"
                    })

                next_call_number += 1

            if new_enrollments_data:
                db.bulk_insert_mappings(ClassEnrollment, new_enrollments_data)

            db.flush()

    @staticmethod
    def _get_next_call_number(db: Session, class_id: int) -> int:
        max_call_number = db.query(func.max(ClassEnrollment.call_number)).filter(ClassEnrollment.class_id == class_id).scalar()
        return (max_call_number or 0) + 1

    def get_next_call_number(self, class_id: int) -> int:
        with self._get_db() as db:
            return self._get_next_call_number(db, class_id)
