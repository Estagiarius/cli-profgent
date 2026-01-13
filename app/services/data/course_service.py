from sqlalchemy import func
from sqlalchemy.orm import joinedload
from app.models.course import Course
from app.models.class_ import Class
from app.models.class_subject import ClassSubject
from app.models.assessment import Assessment
from app.models.grade import Grade
from app.models.lesson import Lesson
from app.models.incident import Incident
from app.models.class_enrollment import ClassEnrollment
from .base_service import BaseDataService

class CourseService(BaseDataService):
    def add_course(self, course_name: str, course_code: str, bncc_expected: str = None) -> dict | None:
        if not course_name or not course_code: return None
        new_course = Course(course_name=course_name, course_code=course_code, bncc_expected=bncc_expected)
        with self._get_db() as db:
            db.add(new_course)
            db.flush()
            db.refresh(new_course)
            return {"id": new_course.id, "course_name": new_course.course_name, "course_code": new_course.course_code, "bncc_expected": new_course.bncc_expected}

    def get_all_courses(self) -> list[dict]:
        with self._get_db() as db:
            courses = db.query(Course).order_by(Course.course_name).all()
            return [{"id": c.id, "course_name": c.course_name, "course_code": c.course_code, "bncc_expected": c.bncc_expected} for c in courses]

    def get_course_count(self) -> int:
        with self._get_db() as db:
            return db.query(func.count(Course.id)).scalar()

    def get_course_by_name(self, name: str) -> dict | None:
        with self._get_db() as db:
            course = db.query(Course).filter(func.lower(Course.course_name) == name.lower()).first()
            if course:
                return {"id": course.id, "course_name": course.course_name, "course_code": course.course_code, "bncc_expected": course.bncc_expected}
            return None

    def get_course_by_id(self, course_id: int) -> dict | None:
        with self._get_db() as db:
            course = db.query(Course).options(
                joinedload(Course.class_subjects).joinedload(ClassSubject.class_)
            ).filter(Course.id == course_id).first()

            if course:
                classes_list = []
                for cs in course.class_subjects:
                    if cs.class_:
                        classes_list.append({
                            "id": cs.class_.id,
                            "name": cs.class_.name,
                            "class_subject_id": cs.id
                        })

                return {
                    "id": course.id,
                    "course_name": course.course_name,
                    "course_code": course.course_code,
                    "bncc_expected": course.bncc_expected,
                    "classes": classes_list
                }
            return None

    def update_course(self, course_id: int, course_name: str, course_code: str, bncc_expected: str = None):
        with self._get_db() as db:
            course = db.query(Course).filter(Course.id == course_id).first()
            if course:
                course.course_name = course_name
                course.course_code = course_code
                course.bncc_expected = bncc_expected

    def update_course_bncc(self, course_id: int, bncc_expected: str):
        with self._get_db() as db:
            course = db.query(Course).filter(Course.id == course_id).first()
            if course:
                course.bncc_expected = bncc_expected

    def delete_course(self, course_id: int):
        with self._get_db() as db:
            subjects = db.query(ClassSubject).filter(ClassSubject.course_id == course_id).first()
            if subjects:
                raise ValueError("Cannot delete course because it is associated with one or more classes.")

            course = db.query(Course).filter(Course.id == course_id).first()
            if course:
                db.delete(course)

    def create_class(self, name: str, calculation_method: str = 'arithmetic') -> dict | None:
        if not name: return None

        with self._get_db() as db:
            if db.query(Class).filter(func.lower(Class.name) == func.lower(name)).first():
                raise ValueError(f"Uma turma com o nome '{name}' já existe.")

            new_class = Class(name=name, calculation_method=calculation_method)
            db.add(new_class)
            db.flush()
            db.refresh(new_class)
            return {"id": new_class.id, "name": new_class.name}

    def copy_class(self, source_class_id: int, new_name: str, copy_subjects: bool = False, copy_assessments: bool = False, copy_students: bool = False) -> dict | None:
        if not new_name:
            raise ValueError("O nome da nova turma não pode ser vazio.")

        with self._get_db() as db:
            source_class = db.query(Class).filter(Class.id == source_class_id).first()
            if not source_class:
                raise ValueError("Turma de origem não encontrada.")

            if db.query(Class).filter(func.lower(Class.name) == func.lower(new_name)).first():
                raise ValueError(f"Uma turma com o nome '{new_name}' já existe.")

            new_class = Class(name=new_name, calculation_method=source_class.calculation_method)
            db.add(new_class)
            db.flush()

            if copy_subjects:
                source_subjects = db.query(ClassSubject).options(joinedload(ClassSubject.assessments)).filter(ClassSubject.class_id == source_class_id).all()

                for source_subj in source_subjects:
                    new_subj = ClassSubject(class_id=new_class.id, course_id=source_subj.course_id)
                    db.add(new_subj)
                    db.flush()

                    if copy_assessments:
                        for source_assess in source_subj.assessments:
                            new_assess = Assessment(
                                class_subject_id=new_subj.id,
                                name=source_assess.name,
                                weight=source_assess.weight,
                                grading_period=source_assess.grading_period
                            )
                            db.add(new_assess)

            if copy_students:
                source_enrollments = db.query(ClassEnrollment).filter(
                    ClassEnrollment.class_id == source_class_id,
                    ClassEnrollment.status == 'Active'
                ).order_by(ClassEnrollment.call_number).all()

                next_call = 1
                for enroll in source_enrollments:
                    new_enroll = ClassEnrollment(
                        class_id=new_class.id,
                        student_id=enroll.student_id,
                        call_number=next_call,
                        status='Active'
                    )
                    db.add(new_enroll)
                    next_call += 1

            db.flush()
            db.refresh(new_class)
            return {"id": new_class.id, "name": new_class.name}

    def add_subject_to_class(self, class_id: int, course_id: int) -> dict | None:
        if not all([class_id, course_id]): return None

        with self._get_db() as db:
            existing = db.query(ClassSubject).filter_by(class_id=class_id, course_id=course_id).first()
            if existing:
                return {"id": existing.id, "class_id": existing.class_id, "course_id": existing.course_id}

            new_subject = ClassSubject(class_id=class_id, course_id=course_id)
            db.add(new_subject)
            db.flush()
            db.refresh(new_subject)
            return {"id": new_subject.id, "class_id": new_subject.class_id, "course_id": new_subject.course_id}

    def get_subjects_for_class(self, class_id: int) -> list[dict]:
        with self._get_db() as db:
            subjects = (db.query(ClassSubject.id, Course.id.label('course_id'), Course.course_name, Course.course_code)
                        .join(Course, ClassSubject.course_id == Course.id)
                        .filter(ClassSubject.class_id == class_id)
                        .all())
            return [{"id": s.id, "course_id": s.course_id, "course_name": s.course_name, "course_code": s.course_code} for s in subjects]

    def get_class_by_name(self, name: str) -> dict | None:
        with self._get_db() as db:
            class_ = db.query(Class).filter(func.lower(Class.name) == name.lower()).first()
            if class_:
                return {"id": class_.id, "name": class_.name}
            return None

    def get_all_classes(self) -> list[dict]:
        with self._get_db() as db:
            results = (db.query(Class.id, Class.name, func.count(ClassEnrollment.id).label('count'))
                       .outerjoin(ClassEnrollment, Class.id == ClassEnrollment.class_id)
                       .group_by(Class.id)
                       .order_by(Class.name)
                       .all())

            return [{"id": c.id, "name": c.name, "student_count": c.count} for c in results]

    def get_class_by_id(self, class_id: int) -> dict | None:
        with self._get_db() as db:
            class_ = db.query(Class).filter(Class.id == class_id).first()
            if class_:
                return {"id": class_.id, "name": class_.name}
            return None

    def update_class(self, class_id: int, name: str):
        with self._get_db() as db:
            class_ = db.query(Class).filter(Class.id == class_id).first()
            if class_:
                class_.name = name

    def delete_class(self, class_id: int):
        with self._get_db() as db:
            subjects = db.query(ClassSubject).filter(ClassSubject.class_id == class_id).all()
            subject_ids = [s.id for s in subjects]

            if subject_ids:
                 assessments = db.query(Assessment).filter(Assessment.class_subject_id.in_(subject_ids)).all()
                 assessment_ids = [a.id for a in assessments]

                 if assessment_ids:
                     db.query(Grade).filter(Grade.assessment_id.in_(assessment_ids)).delete(synchronize_session=False)

                 db.query(Assessment).filter(Assessment.class_subject_id.in_(subject_ids)).delete(synchronize_session=False)
                 db.query(Lesson).filter(Lesson.class_subject_id.in_(subject_ids)).delete(synchronize_session=False)
                 db.query(ClassSubject).filter(ClassSubject.class_id == class_id).delete(synchronize_session=False)

            db.query(Incident).filter(Incident.class_id == class_id).delete(synchronize_session=False)
            db.query(ClassEnrollment).filter(ClassEnrollment.class_id == class_id).delete(synchronize_session=False)

            class_ = db.query(Class).filter(Class.id == class_id).first()
            if class_:
                db.delete(class_)
