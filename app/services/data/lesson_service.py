from datetime import date
from sqlalchemy.orm import joinedload
from app.models.lesson import Lesson
from app.models.attendance import Attendance
from app.models.class_subject import ClassSubject
from app.models.assessment import Assessment
from .base_service import BaseDataService

class LessonService(BaseDataService):
    def create_lesson(self, class_subject_id: int, title: str, content: str, lesson_date: date, bncc_codes: str = None) -> dict | None:
        if not all([class_subject_id, title, lesson_date]): return None
        new_lesson = Lesson(class_subject_id=class_subject_id, title=title, content=content, date=lesson_date, bncc_codes=bncc_codes)
        with self._get_db() as db:
            db.add(new_lesson)
            db.flush()
            db.refresh(new_lesson)
            return {"id": new_lesson.id, "title": new_lesson.title, "content": new_lesson.content, "date": new_lesson.date.isoformat(), "bncc_codes": new_lesson.bncc_codes}

    def update_lesson(self, lesson_id: int, title: str, content: str, lesson_date: date, bncc_codes: str = None):
        with self._get_db() as db:
            lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
            if lesson:
                lesson.title = title
                lesson.content = content
                lesson.date = lesson_date
                lesson.bncc_codes = bncc_codes

    def delete_lesson(self, lesson_id: int):
        with self._get_db() as db:
            lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
            if lesson:
                db.delete(lesson)

    def get_lessons_for_subject(self, class_subject_id: int) -> list[dict]:
        with self._get_db() as db:
            lessons = db.query(Lesson.id, Lesson.title, Lesson.content, Lesson.date).filter(Lesson.class_subject_id == class_subject_id).order_by(Lesson.date.desc()).all()
            return [{"id": l.id, "title": l.title, "content": l.content, "date": l.date.isoformat()} for l in lessons]

    def copy_lessons(self, source_lesson_ids: list[int], target_class_subject_id: int) -> int:
        if not source_lesson_ids or not target_class_subject_id:
            return 0

        with self._get_db() as db:
            source_lessons = db.query(Lesson).filter(Lesson.id.in_(source_lesson_ids)).all()

            count = 0
            for src in source_lessons:
                new_lesson = Lesson(
                    class_subject_id=target_class_subject_id,
                    title=src.title,
                    content=src.content,
                    date=src.date
                )
                db.add(new_lesson)
                count += 1

            db.flush()
            return count

    def register_attendance(self, lesson_id: int, attendance_data: list[dict]):
        valid_statuses = {'P', 'F', 'J', 'A'}

        with self._get_db() as db:
            lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
            if not lesson:
                raise ValueError(f"Lesson with id {lesson_id} not found.")

            existing_records = db.query(Attendance).filter(Attendance.lesson_id == lesson_id).all()
            existing_map = {att.student_id: att for att in existing_records}

            to_insert = []

            for entry in attendance_data:
                student_id = entry.get('student_id')
                status = entry.get('status', 'P')

                if status not in valid_statuses:
                    continue

                existing = existing_map.get(student_id)
                if existing:
                    if existing.status != status:
                        existing.status = status
                else:
                    to_insert.append({
                        "lesson_id": lesson_id,
                        "student_id": student_id,
                        "status": status
                    })

            if to_insert:
                db.bulk_insert_mappings(Attendance, to_insert)

            db.flush()

    def get_lesson_attendance(self, lesson_id: int) -> list[dict]:
        with self._get_db() as db:
            records = db.query(Attendance).filter(Attendance.lesson_id == lesson_id).all()
            return [{"student_id": r.student_id, "status": r.status} for r in records]

    def get_student_attendance_stats(self, student_id: int, class_subject_id: int) -> dict:
        with self._get_db() as db:
            lesson_ids = db.query(Lesson.id).filter(Lesson.class_subject_id == class_subject_id)
            records = db.query(Attendance).filter(
                Attendance.student_id == student_id,
                Attendance.lesson_id.in_(lesson_ids)
            ).all()

            total_recorded = len(records)
            if total_recorded == 0:
                return {"total_lessons": 0, "present_count": 0, "absent_count": 0, "percentage": 100.0}

            present_count = sum(1 for r in records if r.status in ('P', 'A', 'J'))
            absent_count = sum(1 for r in records if r.status == 'F')

            percentage = (present_count / total_recorded) * 100

            return {
                "total_lessons": total_recorded,
                "present_count": present_count,
                "absent_count": absent_count,
                "percentage": percentage
            }

    def get_class_attendance_stats(self, class_subject_id: int) -> dict:
        with self._get_db() as db:
            lessons = db.query(Lesson.id).filter(Lesson.class_subject_id == class_subject_id).all()
            lesson_ids = [l.id for l in lessons]

            if not lesson_ids:
                return {}

            records = db.query(Attendance.student_id, Attendance.status).filter(Attendance.lesson_id.in_(lesson_ids)).all()
            stats = {}

            for r in records:
                if r.student_id not in stats:
                    stats[r.student_id] = {'present': 0, 'absent': 0, 'total': 0}

                stats[r.student_id]['total'] += 1
                if r.status in ('P', 'A', 'J'):
                    stats[r.student_id]['present'] += 1
                elif r.status == 'F':
                    stats[r.student_id]['absent'] += 1

            result = {}
            for sid, data in stats.items():
                total = data['total']
                pct = (data['present'] / total * 100) if total > 0 else 100.0
                result[sid] = {
                    "total_lessons": total,
                    "present_count": data['present'],
                    "absent_count": data['absent'],
                    "percentage": pct
                }
            return result

    def get_bncc_coverage(self, class_subject_id: int) -> dict:
        with self._get_db() as db:
            subject = db.query(ClassSubject).options(joinedload(ClassSubject.course)).filter(ClassSubject.id == class_subject_id).first()
            if not subject:
                return {}

            expected_raw = subject.course.bncc_expected or ""
            expected_set = {code.strip().upper() for code in expected_raw.split(',') if code.strip()}

            lessons = db.query(Lesson).filter(Lesson.class_subject_id == class_subject_id).all()
            covered_lessons_set = set()
            for l in lessons:
                if l.bncc_codes:
                    codes = {code.strip().upper() for code in l.bncc_codes.split(',') if code.strip()}
                    covered_lessons_set.update(codes)

            assessments = db.query(Assessment).filter(Assessment.class_subject_id == class_subject_id).all()
            covered_assessments_set = set()
            for a in assessments:
                if a.bncc_codes:
                    codes = {code.strip().upper() for code in a.bncc_codes.split(',') if code.strip()}
                    covered_assessments_set.update(codes)

            total_covered = covered_lessons_set.union(covered_assessments_set)
            missing = expected_set - total_covered
            relevant_covered = total_covered.intersection(expected_set)

            return {
                "expected": sorted(list(expected_set)),
                "covered_lessons": sorted(list(covered_lessons_set)),
                "covered_assessments": sorted(list(covered_assessments_set)),
                "total_covered": sorted(list(total_covered)),
                "missing": sorted(list(missing)),
                "coverage_percentage": (len(relevant_covered) / len(expected_set) * 100) if expected_set else 0.0
            }
