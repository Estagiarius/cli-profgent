from datetime import date, datetime
from sqlalchemy import func, or_, and_
from sqlalchemy.orm import Session
from app.models.student import Student
from app.models.incident import Incident
from app.models.grade import Grade
from app.models.class_enrollment import ClassEnrollment
from app.models.class_ import Class
from app.utils.student_csv_parser import parse_student_csv
from .base_service import BaseDataService

class StudentService(BaseDataService):
    def import_students_from_csv(self, class_id: int, file_content: str) -> dict:
        errors = []
        imported_count = 0
        try:
            parsed_data = parse_student_csv(file_content)
            if not parsed_data:
                errors.append("O arquivo CSV não contém dados de alunos válidos.")
                return {"imported_count": 0, "errors": errors}

            student_data_for_db = []
            for student_row in parsed_data:
                birth_date_obj = None
                if student_row.get("birth_date"):
                    try:
                        birth_date_obj = datetime.strptime(student_row["birth_date"], "%d/%m/%Y").date()
                    except ValueError:
                        errors.append(f"Formato de data inválido para {student_row['full_name']}: {student_row['birth_date']}. O aluno será importado sem data de nascimento.")

                student_data_for_db.append({
                    "full_name": student_row["full_name"], "first_name": student_row["first_name"],
                    "last_name": student_row["last_name"], "birth_date": birth_date_obj,
                    "status": student_row["status"], "status_detail": student_row.get("status_detail", "")
                })

            with self._get_db() as db:
                self._batch_upsert_students_and_enroll(db, class_id, student_data_for_db)

            imported_count = len({d['full_name'].lower() for d in student_data_for_db})
        except ValueError as ve:
            errors.append(str(ve))
        except Exception as e:
            errors.append(f"Ocorreu um erro inesperado durante a importação: {e}")

        return {"imported_count": imported_count, "errors": errors}

    def _batch_upsert_students_and_enroll(self, db: Session, class_id: int, student_data_list: list[dict]):
        unique_student_data = {data['full_name'].lower(): data for data in student_data_list}
        existing_students_map = {}
        conditions_list = list(unique_student_data.values())

        if conditions_list:
            batch_size = 50
            for i in range(0, len(conditions_list), batch_size):
                batch = conditions_list[i:i+batch_size]
                batch_conditions = [
                    and_(func.lower(Student.first_name) == data['first_name'].lower(),
                         func.lower(Student.last_name) == data['last_name'].lower())
                    for data in batch
                ]
                found_students = db.query(Student).filter(or_(*batch_conditions)).all()
                for s in found_students:
                    full_name = (s.first_name + " " + s.last_name).lower()
                    existing_students_map[full_name] = s

        # Re-implementing _get_next_call_number logic locally to avoid dependency
        max_call_number = db.query(func.max(ClassEnrollment.call_number)).filter(ClassEnrollment.class_id == class_id).scalar()
        next_call_number = (max_call_number or 0) + 1

        existing_student_ids = [s.id for s in existing_students_map.values()]
        existing_enrollments_map = {}
        if existing_student_ids:
             enrollments = db.query(ClassEnrollment).filter(
                 ClassEnrollment.class_id == class_id,
                 ClassEnrollment.student_id.in_(existing_student_ids)
             ).all()
             existing_enrollments_map = {e.student_id: e for e in enrollments}

        for full_name_lower, data in unique_student_data.items():
            student = existing_students_map.get(full_name_lower)
            if student:
                if data['birth_date'] and student.birth_date != data['birth_date']:
                    student.birth_date = data['birth_date']
            else:
                student = Student(
                    first_name=data['first_name'], last_name=data['last_name'],
                    birth_date=data['birth_date'], enrollment_date=date.today().isoformat()
                )
                db.add(student)
                db.flush()

            status = data['status']
            enrollment = existing_enrollments_map.get(student.id)

            if enrollment:
                if enrollment.status != status:
                    enrollment.status = status
            else:
                new_enrollment = ClassEnrollment(
                    class_id=class_id, student_id=student.id,
                    call_number=next_call_number, status=status
                )
                db.add(new_enrollment)
                next_call_number += 1

    def add_student(self, first_name: str, last_name: str, birth_date: date | None = None) -> dict | None:
        if not first_name or not last_name: return None
        if birth_date and birth_date > date.today():
            raise ValueError("Birth date cannot be in the future.")

        with self._get_db() as db:
            existing = db.query(Student).filter(
                and_(
                    func.lower(Student.first_name) == first_name.lower(),
                    func.lower(Student.last_name) == last_name.lower()
                )
            ).first()
            if existing:
                return {
                    "id": existing.id, "first_name": existing.first_name,
                    "last_name": existing.last_name, "birth_date": existing.birth_date.isoformat() if existing.birth_date else None
                }

            today = date.today()
            new_student = Student(first_name=first_name, last_name=last_name, enrollment_date=today.isoformat(), birth_date=birth_date)
            db.add(new_student)
            db.flush()
            db.refresh(new_student)
            return {
                "id": new_student.id, "first_name": new_student.first_name,
                "last_name": new_student.last_name, "birth_date": new_student.birth_date.isoformat() if new_student.birth_date else None
            }

    def get_all_students(self) -> list[dict]:
        with self._get_db() as db:
            students = db.query(Student).order_by(Student.first_name).all()
            return [{"id": s.id, "first_name": s.first_name, "last_name": s.last_name, "birth_date": s.birth_date.isoformat() if s.birth_date else None} for s in students]

    def get_student_count(self) -> int:
        with self._get_db() as db:
            return db.query(func.count(Student.id)).scalar()

    def get_student_by_name(self, name: str) -> dict | None:
        with self._get_db() as db:
            name = name.strip()
            parts = name.split(' ', 1)
            student = None
            if len(parts) == 2:
                first, last = parts
                student = db.query(Student).filter(
                    and_(
                        func.lower(Student.first_name) == first.lower(),
                        func.lower(Student.last_name) == last.lower()
                    )
                ).first()

            if not student:
                 student = db.query(Student).filter(func.lower(Student.first_name + " " + Student.last_name) == name.lower()).first()

            if student:
                return {
                    "id": student.id, "first_name": student.first_name,
                    "last_name": student.last_name, "birth_date": student.birth_date.isoformat() if student.birth_date else None
                }
            return None

    def get_student_by_id(self, student_id: int) -> dict | None:
        with self._get_db() as db:
            student = db.query(Student).filter(Student.id == student_id).first()
            if student:
                return {
                    "id": student.id, "first_name": student.first_name,
                    "last_name": student.last_name, "birth_date": student.birth_date.isoformat() if student.birth_date else None
                }
            return None

    def update_student(self, student_id: int, first_name: str, last_name: str, birth_date: date | None = None):
        if birth_date and birth_date > date.today():
            raise ValueError("Birth date cannot be in the future.")

        with self._get_db() as db:
            student = db.query(Student).filter(Student.id == student_id).first()
            if student:
                student.first_name = first_name
                student.last_name = last_name
                student.birth_date = birth_date

    def delete_student(self, student_id: int):
        with self._get_db() as db:
            db.query(Incident).filter(Incident.student_id == student_id).delete()
            db.query(Grade).filter(Grade.student_id == student_id).delete()
            db.query(ClassEnrollment).filter(ClassEnrollment.student_id == student_id).delete()

            student = db.query(Student).filter(Student.id == student_id).first()
            if student:
                db.delete(student)

    def get_students_with_active_enrollment(self) -> list[dict]:
        with self._get_db() as db:
            active_students = db.query(Student).join(ClassEnrollment).filter(ClassEnrollment.status == 'Active').all()
            return [{"id": s.id, "first_name": s.first_name, "last_name": s.last_name} for s in active_students]

    def get_paginated_students(self, page: int, page_size: int, search_term: str = None, active_only: bool = False) -> dict:
        with self._get_db() as db:
            query = db.query(Student)

            if active_only:
                query = query.filter(
                    db.query(ClassEnrollment.id).filter(
                        ClassEnrollment.student_id == Student.id,
                        ClassEnrollment.status == 'Active'
                    ).exists()
                )

            if search_term:
                search_pattern = f"%{search_term.lower()}%"
                query = query.filter(func.lower(Student.first_name + " " + Student.last_name).like(search_pattern))

            total_count = query.count()
            query = query.order_by(Student.first_name, Student.last_name)

            offset = (page - 1) * page_size
            students = query.offset(offset).limit(page_size).all()

            student_list = [
                {
                    "id": s.id,
                    "first_name": s.first_name,
                    "last_name": s.last_name,
                    "birth_date": s.birth_date.isoformat() if s.birth_date else None
                }
                for s in students
            ]

            return {
                "students": student_list,
                "total_count": total_count,
                "total_pages": (total_count + page_size - 1) // page_size if page_size > 0 else 1,
                "current_page": page
            }

    def get_unenrolled_students(self, class_id: int) -> list[dict]:
        with self._get_db() as db:
            students = (db.query(Student)
                        .outerjoin(ClassEnrollment, (ClassEnrollment.student_id == Student.id) & (ClassEnrollment.class_id == class_id))
                        .filter(ClassEnrollment.id == None)
                        .all())
            return [{"id": s.id, "first_name": s.first_name, "last_name": s.last_name} for s in students]

    def get_students_with_birthday_today(self) -> list[dict]:
        today = date.today()
        current_month = f"{today.month:02d}"
        current_day = f"{today.day:02d}"

        with self._get_db() as db:
            students = (
                db.query(Student, Class.name.label("class_name"))
                .join(ClassEnrollment, Student.id == ClassEnrollment.student_id)
                .join(Class, ClassEnrollment.class_id == Class.id)
                .filter(ClassEnrollment.status == 'Active')
                # noinspection PyTypeChecker
                .filter(func.strftime('%m', Student.birth_date) == current_month)
                # noinspection PyTypeChecker
                .filter(func.strftime('%d', Student.birth_date) == current_day)
                .all()
            )

            results = []
            for student, class_name in students:
                age = today.year - student.birth_date.year if student.birth_date else 0
                results.append({
                    "id": student.id,
                    "name": f"{student.first_name} {student.last_name}",
                    "age": age,
                    "class_name": class_name
                })
            return results
