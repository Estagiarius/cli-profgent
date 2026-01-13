from datetime import date
from sqlalchemy import and_
from sqlalchemy.orm import joinedload
from app.models.student import Student
from app.models.course import Course
from app.models.grade import Grade
from app.models.class_ import Class
from app.models.class_subject import ClassSubject
from app.models.class_enrollment import ClassEnrollment
from app.models.assessment import Assessment
from .base_service import BaseDataService

class GradeService(BaseDataService):
    def add_assessment(self, class_subject_id: int, name: str, weight: float, grading_period: int = 1, bncc_codes: str = None) -> dict | None:
        if not all([class_subject_id, name, weight is not None]): return None
        if weight < 0:
            raise ValueError("Assessment weight must be non-negative.")
        if not (1 <= grading_period <= 5):
             raise ValueError("Grading period must be between 1 and 5.")

        assessment = Assessment(class_subject_id=class_subject_id, name=name, weight=weight, grading_period=grading_period, bncc_codes=bncc_codes)
        with self._get_db() as db:
            db.add(assessment)
            db.flush()
            db.refresh(assessment)
            return {
                "id": assessment.id,
                "name": assessment.name,
                "weight": assessment.weight,
                "class_subject_id": assessment.class_subject_id,
                "grading_period": assessment.grading_period,
                "bncc_codes": assessment.bncc_codes
            }

    def ensure_final_assessment(self, class_subject_id: int) -> dict:
        with self._get_db() as db:
            assessment = db.query(Assessment).filter(
                Assessment.class_subject_id == class_subject_id,
                Assessment.grading_period == 5
            ).first()

            if assessment:
                return {"id": assessment.id, "name": assessment.name}

            new_assessment = Assessment(
                class_subject_id=class_subject_id,
                name="Média Final (Manual)",
                weight=1.0,
                grading_period=5
            )
            db.add(new_assessment)
            db.flush()
            db.refresh(new_assessment)
            return {"id": new_assessment.id, "name": new_assessment.name}

    def update_assessment(self, assessment_id: int, name: str, weight: float, grading_period: int = None, bncc_codes: str = None):
        if weight < 0:
            raise ValueError("Assessment weight must be non-negative.")
        if grading_period is not None and not (1 <= grading_period <= 5):
             raise ValueError("Grading period must be between 1 and 5.")

        with self._get_db() as db:
            assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
            if assessment:
                assessment.name = name
                assessment.weight = weight
                if grading_period is not None:
                    assessment.grading_period = grading_period
                assessment.bncc_codes = bncc_codes

    def delete_assessment(self, assessment_id: int):
        with self._get_db() as db:
            db.query(Grade).filter(Grade.assessment_id == assessment_id).delete()
            assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
            if assessment:
                db.delete(assessment)

    def get_assessments_for_subject(self, class_subject_id: int) -> list[dict]:
        with self._get_db() as db:
            assessments = db.query(Assessment.id, Assessment.name, Assessment.weight, Assessment.grading_period).filter(Assessment.class_subject_id == class_subject_id).order_by(Assessment.grading_period, Assessment.name).all()
            return [{"id": a.id, "name": a.name, "weight": a.weight, "grading_period": a.grading_period} for a in assessments]

    def get_all_grades(self) -> list[dict]:
        with self._get_db() as db:
            grades = db.query(Grade).all()
            return [{"id": g.id, "student_id": g.student_id, "assessment_id": g.assessment_id, "score": g.score} for g in grades]

    def get_grades_for_subject(self, class_subject_id: int) -> list[dict]:
        with self._get_db() as db:
            grades = (db.query(Grade.id, Grade.student_id, Grade.assessment_id, Grade.score, Assessment.name.label('assessment_name'))
                      .join(Assessment, Grade.assessment_id == Assessment.id)
                      .join(ClassSubject, Assessment.class_subject_id == ClassSubject.id)
                      .join(ClassEnrollment, (Grade.student_id == ClassEnrollment.student_id) & (ClassSubject.class_id == ClassEnrollment.class_id))
                      .filter(Assessment.class_subject_id == class_subject_id)
                      .filter(ClassEnrollment.status == 'Active').all())
            return [
                {"id": g.id, "student_id": g.student_id, "assessment_id": g.assessment_id, "score": g.score, "assessment_name": g.assessment_name}
                for g in grades
            ]

    def get_student_period_averages(self, student_id: int, class_subject_id: int) -> dict:
        with self._get_db() as db:
            assessments = db.query(Assessment).filter(Assessment.class_subject_id == class_subject_id).all()
            if not assessments:
                return {}

            assessment_ids = [a.id for a in assessments]
            grades = db.query(Grade).filter(
                Grade.student_id == student_id,
                Grade.assessment_id.in_(assessment_ids)
            ).all()

            grades_map = {g.assessment_id: g.score for g in grades}
            results = {}
            final_sum = 0.0
            periods_count = 0

            for period in range(1, 5):
                period_assessments = [a for a in assessments if a.grading_period == period]
                if not period_assessments:
                    results[period] = None
                    final_sum += 0.0
                    periods_count += 1
                else:
                    assessments_data = [{"id": a.id, "weight": a.weight} for a in period_assessments]
                    period_total_weight = sum(a['weight'] for a in assessments_data)
                    avg = self.calculate_weighted_average(student_id, grades_map, assessments_data, total_weight=period_total_weight)
                    results[period] = avg
                    final_sum += avg
                    periods_count += 1

            calculated_final = final_sum / 4.0 if periods_count > 0 else 0.0
            results["final_calculated"] = calculated_final

            final_assessment = next((a for a in assessments if a.grading_period == 5), None)
            if final_assessment and final_assessment.id in grades_map:
                results["final_override"] = grades_map[final_assessment.id]
            else:
                results["final_override"] = None

            return results

    def get_class_period_averages(self, class_subject_id: int) -> dict:
        with self._get_db() as db:
            assessments = db.query(Assessment).filter(Assessment.class_subject_id == class_subject_id).all()
            if not assessments: return {}

            assessment_ids = [a.id for a in assessments]
            grades = db.query(Grade.student_id, Grade.assessment_id, Grade.score).filter(Grade.assessment_id.in_(assessment_ids)).all()

            student_grades = {}
            for g in grades:
                if g.student_id not in student_grades: student_grades[g.student_id] = {}
                student_grades[g.student_id][g.assessment_id] = g.score

            results = {}
            period_assessments = {1: [], 2: [], 3: [], 4: [], 5: []}
            for a in assessments:
                period_assessments[a.grading_period].append({"id": a.id, "weight": a.weight})

            final_assessment_id = next((a.id for a in assessments if a.grading_period == 5), None)
            period_weights = {p: sum(a['weight'] for a in period_assessments[p]) for p in range(1, 6)}

            for student_id, s_grades_map in student_grades.items():
                s_results = {}
                final_sum = 0.0
                periods_count = 0

                for period in range(1, 5):
                    assessments_data = period_assessments[period]
                    if not assessments_data:
                        s_results[period] = None
                        final_sum += 0.0
                        periods_count += 1
                        continue

                    total_weight = period_weights[period]
                    avg = self.calculate_weighted_average(student_id, s_grades_map, assessments_data, total_weight=total_weight)
                    s_results[period] = avg
                    final_sum += avg
                    periods_count += 1

                s_results["final_calculated"] = final_sum / 4.0 if periods_count > 0 else 0.0

                if final_assessment_id and final_assessment_id in s_grades_map:
                    s_results["final_override"] = s_grades_map[final_assessment_id]
                else:
                    s_results["final_override"] = None

                results[student_id] = s_results

            return results

    def get_all_grades_with_details(self) -> list[dict]:
        with self._get_db() as db:
            grades_query = (
                db.query(
                    Grade.id, Grade.score, Student.id.label("student_id"),
                    Student.first_name.label("student_first_name"), Student.last_name.label("student_last_name"),
                    Assessment.id.label("assessment_id"), Assessment.name.label("assessment_name"),
                    Class.id.label("class_id"), Class.name.label("class_name"),
                    Course.id.label("course_id"), Course.course_name.label("course_name")
                )
                .join(Student, Grade.student_id == Student.id)
                .join(Assessment, Grade.assessment_id == Assessment.id)
                .join(ClassSubject, Assessment.class_subject_id == ClassSubject.id)
                .join(Class, ClassSubject.class_id == Class.id)
                .join(Course, ClassSubject.course_id == Course.id)
                .all()
            )
            return [row._asdict() for row in grades_query]

    def add_grade(self, student_id: int, assessment_id: int, score: float) -> dict | None:
        if not all([student_id, assessment_id, score is not None]): return None
        if not (0 <= score <= 10):
            raise ValueError("Score must be between 0 and 10.")

        today = date.today()
        new_grade = Grade(student_id=student_id, assessment_id=assessment_id, score=score, date_recorded=today.isoformat())
        with self._get_db() as db:
            db.add(new_grade)
            db.flush()
            db.refresh(new_grade)
            return {"id": new_grade.id, "score": new_grade.score}

    def delete_grade(self, grade_id: int):
        with self._get_db() as db:
            grade = db.query(Grade).filter(Grade.id == grade_id).first()
            if grade:
                db.delete(grade)

    def upsert_grades_for_subject(self, class_subject_id: int, grades_data: list[dict]):
        with self._get_db() as db:
            existing_grades_query = db.query(Grade.id, Grade.student_id, Grade.assessment_id, Grade.score).join(Assessment).filter(Assessment.class_subject_id == class_subject_id)
            existing_grades_map = {(g.student_id, g.assessment_id): g for g in existing_grades_query}

            to_insert = []
            to_update = []
            today_str = date.today().isoformat()

            for grade_info in grades_data:
                try:
                    student_id = int(grade_info['student_id'])
                    assessment_id = int(grade_info['assessment_id'])
                except (ValueError, TypeError):
                    continue

                score = grade_info['score']
                if not (0 <= score <= 10):
                    raise ValueError(f"Score must be between 0 and 10.")

                existing_grade = existing_grades_map.get((student_id, assessment_id))

                if existing_grade:
                    if existing_grade.score != score:
                        to_update.append({"id": existing_grade.id, "score": score})
                else:
                    to_insert.append({
                        "student_id": student_id,
                        "assessment_id": assessment_id,
                        "score": score,
                        "date_recorded": today_str
                    })

            if to_insert:
                db.bulk_insert_mappings(Grade, to_insert)
            if to_update:
                db.bulk_update_mappings(Grade, to_update)

            db.flush()

    @staticmethod
    def calculate_weighted_average(student_id: int, grades: list[dict] | dict[int, float], assessments: list[dict], total_weight: float = None) -> float:
        if total_weight is None:
            total_weight = sum(a['weight'] for a in assessments)
        if total_weight == 0: return 0.0

        if isinstance(grades, dict):
            student_grades = grades
        else:
            student_grades = {g['assessment_id']: g['score'] for g in grades if g.get('student_id') == student_id}

        weighted_sum = sum(student_grades.get(a['id'], 0.0) * a['weight'] for a in assessments)
        return weighted_sum / total_weight
