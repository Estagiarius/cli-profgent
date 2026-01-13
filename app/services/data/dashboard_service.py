from sqlalchemy import func
from sqlalchemy.orm import joinedload
from app.models.student import Student
from app.models.course import Course
from app.models.class_ import Class
from app.models.grade import Grade
from app.models.class_subject import ClassSubject
from app.models.class_enrollment import ClassEnrollment
from app.models.assessment import Assessment
from app.models.incident import Incident
from .base_service import BaseDataService
from .grade_service import GradeService

class DashboardService(BaseDataService):
    def get_global_dashboard_stats(self) -> dict:
        with self._get_db() as db:
            active_students = db.query(func.count(func.distinct(ClassEnrollment.student_id))).filter(ClassEnrollment.status == 'Active').scalar()
            total_classes = db.query(func.count(Class.id)).scalar()
            total_courses = db.query(func.count(Course.id)).scalar()
            total_incidents = db.query(func.count(Incident.id)).scalar()

            return {
                "active_students": active_students or 0,
                "total_classes": total_classes or 0,
                "total_courses": total_courses or 0,
                "total_incidents": total_incidents or 0
            }

    def get_class_incident_ranking(self, limit: int = 5) -> list[dict]:
        with self._get_db() as db:
            ranking = (
                db.query(Class.name, func.count(Incident.id).label('count'))
                .join(Incident, Class.id == Incident.class_id)
                .group_by(Class.id)
                .order_by(func.count(Incident.id).desc())
                .limit(limit)
                .all()
            )
            return [{"class_name": r.name, "count": r.count} for r in ranking]

    def get_class_report_data(self, class_id: int) -> dict:
        with self._get_db() as db:
            subjects = (db.query(ClassSubject)
                        .options(joinedload(ClassSubject.assessments), joinedload(ClassSubject.course))
                        .filter(ClassSubject.class_id == class_id)
                        .all())

            subjects_data = []
            all_assessment_ids = []

            for s in subjects:
                assessments = [{"id": a.id, "name": a.name, "weight": a.weight} for a in s.assessments]
                all_assessment_ids.extend([a['id'] for a in assessments])
                subjects_data.append({
                    "id": s.id,
                    "course_name": s.course.course_name,
                    "assessments": assessments
                })

            enrollments = (db.query(ClassEnrollment)
                           .options(joinedload(ClassEnrollment.student))
                           .filter(ClassEnrollment.class_id == class_id)
                           .order_by(ClassEnrollment.call_number)
                           .all())

            students_data = []
            student_ids = []
            for e in enrollments:
                student_ids.append(e.student_id)
                students_data.append({
                    "student_id": e.student_id,
                    "name": f"{e.student.first_name} {e.student.last_name}",
                    "call_number": e.call_number,
                    "status": e.status
                })

            grades_map = {}
            if all_assessment_ids and student_ids:
                 grades = db.query(Grade.student_id, Grade.assessment_id, Grade.score).filter(
                     Grade.assessment_id.in_(all_assessment_ids),
                     Grade.student_id.in_(student_ids)
                 ).all()
                 for g in grades:
                     grades_map[(g.student_id, g.assessment_id)] = g.score

            return {
                "subjects": subjects_data,
                "students": students_data,
                "grades_map": grades_map
            }

    def get_course_averages(self, course_id: int) -> list[float]:
        averages = []
        with self._get_db() as db:
            subjects = (db.query(ClassSubject)
                        .options(joinedload(ClassSubject.assessments))
                        .filter(ClassSubject.course_id == course_id)
                        .all())

            if not subjects:
                return []

            class_ids = [s.class_id for s in subjects]

            enrollments = db.query(ClassEnrollment).filter(
                ClassEnrollment.class_id.in_(class_ids),
                ClassEnrollment.status == 'Active'
            ).all()

            class_students_map = {}
            for e in enrollments:
                if e.class_id not in class_students_map:
                    class_students_map[e.class_id] = []
                class_students_map[e.class_id].append(e.student_id)

            all_assessment_ids = []
            assessments_map = {}

            for subject in subjects:
                s_assessments = [{"id": a.id, "weight": a.weight} for a in subject.assessments]
                assessments_map[subject.id] = s_assessments
                all_assessment_ids.extend([a['id'] for a in s_assessments])

            if not all_assessment_ids:
                return []

            all_grades = db.query(Grade.student_id, Grade.assessment_id, Grade.score).filter(Grade.assessment_id.in_(all_assessment_ids)).all()

            grades_by_student = {}
            for g in all_grades:
                if g.student_id not in grades_by_student:
                    grades_by_student[g.student_id] = {}
                grades_by_student[g.student_id][g.assessment_id] = g.score

            for subject in subjects:
                assessments_data = assessments_map.get(subject.id, [])
                if not assessments_data:
                    continue

                total_weight = sum(a['weight'] for a in assessments_data)
                student_ids = class_students_map.get(subject.class_id, [])

                for student_id in student_ids:
                    student_grades = grades_by_student.get(student_id, {})
                    avg = GradeService.calculate_weighted_average(student_id, student_grades, assessments_data, total_weight=total_weight)
                    averages.append(avg)

        return averages

    def get_global_performance_stats(self) -> dict:
        total_enrollments_analyzed = 0
        approved_count = 0
        failed_details = []
        honor_roll_details = []

        with self._get_db() as db:
            subjects = db.query(ClassSubject).options(
                joinedload(ClassSubject.class_),
                joinedload(ClassSubject.course),
                joinedload(ClassSubject.assessments)
            ).all()

            if not subjects:
                return {
                    "total_analyzed": 0, "approved": 0, "failed": 0, "approval_rate": 0.0,
                    "failed_details": [], "honor_roll_details": []
                }

            all_active_enrollments = (db.query(ClassEnrollment)
                                      .options(joinedload(ClassEnrollment.student))
                                      .filter(ClassEnrollment.status == 'Active')
                                      .all())

            enrollments_by_class = {}
            for e in all_active_enrollments:
                if e.class_id not in enrollments_by_class:
                    enrollments_by_class[e.class_id] = []
                enrollments_by_class[e.class_id].append(e)

            all_assessment_ids = []
            for s in subjects:
                for a in s.assessments:
                    all_assessment_ids.append(a.id)

            all_grades = []
            if all_assessment_ids:
                 chunk_size = 500
                 for i in range(0, len(all_assessment_ids), chunk_size):
                     chunk = all_assessment_ids[i:i+chunk_size]
                     grades_chunk = db.query(Grade.student_id, Grade.assessment_id, Grade.score).filter(Grade.assessment_id.in_(chunk)).all()
                     all_grades.extend(grades_chunk)

            grades_by_student = {}
            for g in all_grades:
                if g.student_id not in grades_by_student:
                    grades_by_student[g.student_id] = {}
                grades_by_student[g.student_id][g.assessment_id] = g.score

            for subject in subjects:
                assessments_data = [{"id": a.id, "weight": a.weight} for a in subject.assessments]
                if not assessments_data: continue

                total_weight = sum(a['weight'] for a in assessments_data)
                class_enrollments = enrollments_by_class.get(subject.class_id, [])

                for enrollment in class_enrollments:
                    student_grades = grades_by_student.get(enrollment.student_id, {})
                    avg = GradeService.calculate_weighted_average(enrollment.student_id, student_grades, assessments_data, total_weight=total_weight)

                    total_enrollments_analyzed += 1

                    if avg >= 5.0:
                        approved_count += 1
                        if avg >= 9.0:
                             honor_roll_details.append({
                                "student_name": f"{enrollment.student.first_name} {enrollment.student.last_name}",
                                "class_name": subject.class_.name,
                                "course_name": subject.course.course_name,
                                "average": round(avg, 2)
                            })
                    else:
                        failed_details.append({
                            "student_name": f"{enrollment.student.first_name} {enrollment.student.last_name}",
                            "class_name": subject.class_.name,
                            "course_name": subject.course.course_name,
                            "average": round(avg, 2)
                        })

        return {
            "total_analyzed": total_enrollments_analyzed,
            "approved": approved_count,
            "failed": total_enrollments_analyzed - approved_count,
            "approval_rate": (approved_count / total_enrollments_analyzed * 100) if total_enrollments_analyzed > 0 else 0.0,
            "failed_details": failed_details,
            "honor_roll_details": honor_roll_details
        }

    def get_student_performance_summary(self, student_id: int, class_id: int) -> dict | None:
        with self._get_db() as db:
            assessments = (db.query(Assessment)
                           .join(ClassSubject)
                           .filter(ClassSubject.class_id == class_id)
                           .all())

            assessments_data = [{"id": a.id, "weight": a.weight} for a in assessments]
            assessment_ids = [a['id'] for a in assessments_data]

            if not assessments_data:
                 weighted_average = 0.0
            else:
                 grades = db.query(Grade).filter(
                     Grade.student_id == student_id,
                     Grade.assessment_id.in_(assessment_ids)
                 ).all()
                 grades_data = [{"assessment_id": g.assessment_id, "score": g.score, "student_id": g.student_id} for g in grades]

                 weighted_average = GradeService.calculate_weighted_average(student_id, grades_data, assessments_data)

            incidents_count = db.query(func.count(Incident.id)).filter(Incident.class_id == class_id, Incident.student_id == student_id).scalar()

            return {
                "weighted_average": weighted_average,
                "incident_count": incidents_count
            }

    def get_students_at_risk(self, class_id: int, grade_threshold: float = 5.0, incident_threshold: int = 2) -> list[dict]:
        with self._get_db() as db:
             enrollments = (db.query(ClassEnrollment)
                            .options(joinedload(ClassEnrollment.student))
                            .filter(ClassEnrollment.class_id == class_id, ClassEnrollment.status == 'Active')
                            .all())

             student_ids = [e.student_id for e in enrollments]
             if not student_ids:
                 return []

             incidents_query = (db.query(Incident.student_id, func.count(Incident.id).label('count'))
                                .filter(Incident.class_id == class_id, Incident.student_id.in_(student_ids))
                                .group_by(Incident.student_id).all())
             incidents_map = {row.student_id: row.count for row in incidents_query}

             assessments = (db.query(Assessment)
                            .join(ClassSubject)
                            .filter(ClassSubject.class_id == class_id)
                            .all())
             assessments_data = [{"id": a.id, "weight": a.weight} for a in assessments]
             assessment_ids = [a['id'] for a in assessments_data]

             grades = db.query(Grade.student_id, Grade.assessment_id, Grade.score).filter(
                 Grade.student_id.in_(student_ids),
                 Grade.assessment_id.in_(assessment_ids)
             ).all()

             grades_by_student = {}
             for g in grades:
                 if g.student_id not in grades_by_student:
                     grades_by_student[g.student_id] = {}
                 grades_by_student[g.student_id][g.assessment_id] = g.score

             total_weight = sum(a['weight'] for a in assessments_data)
             at_risk_students = []

             for enrollment in enrollments:
                 student_id = enrollment.student_id
                 incident_count = incidents_map.get(student_id, 0)
                 student_grades = grades_by_student.get(student_id, {})
                 weighted_average = GradeService.calculate_weighted_average(student_id, student_grades, assessments_data, total_weight=total_weight)

                 is_at_risk = (weighted_average < grade_threshold) or (incident_count >= incident_threshold)

                 if is_at_risk:
                     at_risk_students.append({
                        "student_id": student_id,
                        "student_name": f"{enrollment.student.first_name} {enrollment.student.last_name}",
                        "average_grade": weighted_average,
                        "incident_count": incident_count
                    })

        return at_risk_students
