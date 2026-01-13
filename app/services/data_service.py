# Author: Victor Hugo Garcia de Oliveira
# Date: 2025-12-21
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Este arquivo de código-fonte está sujeito aos termos da Mozilla Public
# License, v. 2.0. Se uma cópia da MPL não foi distribuída com este
# arquivo, você pode obter uma em https://mozilla.org/MPL/2.0/.
from sqlalchemy.orm import Session
from app.services.data.student_service import StudentService
from app.services.data.course_service import CourseService
from app.services.data.enrollment_service import EnrollmentService
from app.services.data.grade_service import GradeService
from app.services.data.lesson_service import LessonService
from app.services.data.incident_service import IncidentService
from app.services.data.schedule_service import ScheduleService
from app.services.data.dashboard_service import DashboardService
from app.services.data.seating_chart_service import SeatingChartService
from contextlib import contextmanager

class DataService:
    """
    Facade class that delegates operations to specialized services.
    This maintains the original API contract while using the new modular architecture.
    """
    def __init__(self, db_session: Session = None):
        self._db_session = db_session

        # Instantiate specialized services
        self.student_service = StudentService(db_session)
        self.course_service = CourseService(db_session)
        self.enrollment_service = EnrollmentService(db_session)
        self.grade_service = GradeService(db_session)
        self.lesson_service = LessonService(db_session)
        self.incident_service = IncidentService(db_session)
        self.schedule_service = ScheduleService(db_session)
        self.dashboard_service = DashboardService(db_session)
        self.seating_chart_service = SeatingChartService(db_session)

    @contextmanager
    def _get_db(self):
        # We delegate to the base service logic, but since we are a facade,
        # we can just use any service's context manager or replicate the base logic.
        # For simplicity and consistency, we delegate to one of the services.
        with self.student_service._get_db() as db:
            yield db

    # --- Student Service Delegations ---
    def import_students_from_csv(self, *args, **kwargs):
        return self.student_service.import_students_from_csv(*args, **kwargs)

    def add_student(self, *args, **kwargs):
        return self.student_service.add_student(*args, **kwargs)

    def get_all_students(self, *args, **kwargs):
        return self.student_service.get_all_students(*args, **kwargs)

    def get_student_count(self, *args, **kwargs):
        return self.student_service.get_student_count(*args, **kwargs)

    def get_student_by_name(self, *args, **kwargs):
        return self.student_service.get_student_by_name(*args, **kwargs)

    def get_student_by_id(self, *args, **kwargs):
        return self.student_service.get_student_by_id(*args, **kwargs)

    def update_student(self, *args, **kwargs):
        return self.student_service.update_student(*args, **kwargs)

    def delete_student(self, *args, **kwargs):
        return self.student_service.delete_student(*args, **kwargs)

    def get_students_with_active_enrollment(self, *args, **kwargs):
        return self.student_service.get_students_with_active_enrollment(*args, **kwargs)

    def get_paginated_students(self, *args, **kwargs):
        return self.student_service.get_paginated_students(*args, **kwargs)

    def get_unenrolled_students(self, *args, **kwargs):
        return self.student_service.get_unenrolled_students(*args, **kwargs)

    def get_students_with_birthday_today(self, *args, **kwargs):
        return self.student_service.get_students_with_birthday_today(*args, **kwargs)

    # --- Course Service Delegations ---
    def add_course(self, *args, **kwargs):
        return self.course_service.add_course(*args, **kwargs)

    def get_all_courses(self, *args, **kwargs):
        return self.course_service.get_all_courses(*args, **kwargs)

    def get_course_count(self, *args, **kwargs):
        return self.course_service.get_course_count(*args, **kwargs)

    def get_course_by_name(self, *args, **kwargs):
        return self.course_service.get_course_by_name(*args, **kwargs)

    def get_course_by_id(self, *args, **kwargs):
        return self.course_service.get_course_by_id(*args, **kwargs)

    def update_course(self, *args, **kwargs):
        return self.course_service.update_course(*args, **kwargs)

    def update_course_bncc(self, *args, **kwargs):
        return self.course_service.update_course_bncc(*args, **kwargs)

    def delete_course(self, *args, **kwargs):
        return self.course_service.delete_course(*args, **kwargs)

    def create_class(self, *args, **kwargs):
        return self.course_service.create_class(*args, **kwargs)

    def copy_class(self, *args, **kwargs):
        return self.course_service.copy_class(*args, **kwargs)

    def add_subject_to_class(self, *args, **kwargs):
        return self.course_service.add_subject_to_class(*args, **kwargs)

    def get_subjects_for_class(self, *args, **kwargs):
        return self.course_service.get_subjects_for_class(*args, **kwargs)

    def get_class_by_name(self, *args, **kwargs):
        return self.course_service.get_class_by_name(*args, **kwargs)

    def get_all_classes(self, *args, **kwargs):
        return self.course_service.get_all_classes(*args, **kwargs)

    def get_class_by_id(self, *args, **kwargs):
        return self.course_service.get_class_by_id(*args, **kwargs)

    def update_class(self, *args, **kwargs):
        return self.course_service.update_class(*args, **kwargs)

    def delete_class(self, *args, **kwargs):
        return self.course_service.delete_class(*args, **kwargs)

    # --- Enrollment Service Delegations ---
    def get_student_enrollments(self, *args, **kwargs):
        return self.enrollment_service.get_student_enrollments(*args, **kwargs)

    def add_student_to_class(self, *args, **kwargs):
        return self.enrollment_service.add_student_to_class(*args, **kwargs)

    def get_enrollments_for_class(self, *args, **kwargs):
        return self.enrollment_service.get_enrollments_for_class(*args, **kwargs)

    def update_enrollment_status(self, *args, **kwargs):
        return self.enrollment_service.update_enrollment_status(*args, **kwargs)

    def enroll_students(self, *args, **kwargs):
        return self.enrollment_service.enroll_students(*args, **kwargs)

    def get_next_call_number(self, *args, **kwargs):
        return self.enrollment_service.get_next_call_number(*args, **kwargs)

    def _get_next_call_number(self, db, class_id):
        # Expose the static helper for backward compatibility if accessed directly (though unlikely)
        # But for facade, it's better to delegate to the static method on the service class
        return EnrollmentService._get_next_call_number(db, class_id)

    # --- Grade Service Delegations ---
    def add_assessment(self, *args, **kwargs):
        return self.grade_service.add_assessment(*args, **kwargs)

    def ensure_final_assessment(self, *args, **kwargs):
        return self.grade_service.ensure_final_assessment(*args, **kwargs)

    def update_assessment(self, *args, **kwargs):
        return self.grade_service.update_assessment(*args, **kwargs)

    def delete_assessment(self, *args, **kwargs):
        return self.grade_service.delete_assessment(*args, **kwargs)

    def get_assessments_for_subject(self, *args, **kwargs):
        return self.grade_service.get_assessments_for_subject(*args, **kwargs)

    def get_all_grades(self, *args, **kwargs):
        return self.grade_service.get_all_grades(*args, **kwargs)

    def get_grades_for_subject(self, *args, **kwargs):
        return self.grade_service.get_grades_for_subject(*args, **kwargs)

    def get_student_period_averages(self, *args, **kwargs):
        return self.grade_service.get_student_period_averages(*args, **kwargs)

    def get_class_period_averages(self, *args, **kwargs):
        return self.grade_service.get_class_period_averages(*args, **kwargs)

    def get_all_grades_with_details(self, *args, **kwargs):
        return self.grade_service.get_all_grades_with_details(*args, **kwargs)

    def add_grade(self, *args, **kwargs):
        return self.grade_service.add_grade(*args, **kwargs)

    def delete_grade(self, *args, **kwargs):
        return self.grade_service.delete_grade(*args, **kwargs)

    def upsert_grades_for_subject(self, *args, **kwargs):
        return self.grade_service.upsert_grades_for_subject(*args, **kwargs)

    @staticmethod
    def calculate_weighted_average(*args, **kwargs):
        return GradeService.calculate_weighted_average(*args, **kwargs)

    # --- Lesson Service Delegations ---
    def create_lesson(self, *args, **kwargs):
        return self.lesson_service.create_lesson(*args, **kwargs)

    def update_lesson(self, *args, **kwargs):
        return self.lesson_service.update_lesson(*args, **kwargs)

    def delete_lesson(self, *args, **kwargs):
        return self.lesson_service.delete_lesson(*args, **kwargs)

    def get_lessons_for_subject(self, *args, **kwargs):
        return self.lesson_service.get_lessons_for_subject(*args, **kwargs)

    def copy_lessons(self, *args, **kwargs):
        return self.lesson_service.copy_lessons(*args, **kwargs)

    def register_attendance(self, *args, **kwargs):
        return self.lesson_service.register_attendance(*args, **kwargs)

    def get_lesson_attendance(self, *args, **kwargs):
        return self.lesson_service.get_lesson_attendance(*args, **kwargs)

    def get_student_attendance_stats(self, *args, **kwargs):
        return self.lesson_service.get_student_attendance_stats(*args, **kwargs)

    def get_class_attendance_stats(self, *args, **kwargs):
        return self.lesson_service.get_class_attendance_stats(*args, **kwargs)

    def get_bncc_coverage(self, *args, **kwargs):
        return self.lesson_service.get_bncc_coverage(*args, **kwargs)

    # --- Incident Service Delegations ---
    def create_incident(self, *args, **kwargs):
        return self.incident_service.create_incident(*args, **kwargs)

    def get_incidents_for_class(self, *args, **kwargs):
        return self.incident_service.get_incidents_for_class(*args, **kwargs)

    def get_student_incidents(self, *args, **kwargs):
        return self.incident_service.get_student_incidents(*args, **kwargs)

    # --- Schedule Service Delegations ---
    def create_time_slot(self, *args, **kwargs):
        return self.schedule_service.create_time_slot(*args, **kwargs)

    def get_time_slots(self, *args, **kwargs):
        return self.schedule_service.get_time_slots(*args, **kwargs)

    def delete_time_slot(self, *args, **kwargs):
        return self.schedule_service.delete_time_slot(*args, **kwargs)

    def create_schedule_assignment(self, *args, **kwargs):
        return self.schedule_service.create_schedule_assignment(*args, **kwargs)

    def get_full_schedule_grid(self, *args, **kwargs):
        return self.schedule_service.get_full_schedule_grid(*args, **kwargs)

    def get_lesson_for_schedule(self, *args, **kwargs):
        return self.schedule_service.get_lesson_for_schedule(*args, **kwargs)

    # --- Dashboard Service Delegations ---
    def get_global_dashboard_stats(self, *args, **kwargs):
        return self.dashboard_service.get_global_dashboard_stats(*args, **kwargs)

    def get_class_incident_ranking(self, *args, **kwargs):
        return self.dashboard_service.get_class_incident_ranking(*args, **kwargs)

    def get_class_report_data(self, *args, **kwargs):
        return self.dashboard_service.get_class_report_data(*args, **kwargs)

    def get_course_averages(self, *args, **kwargs):
        return self.dashboard_service.get_course_averages(*args, **kwargs)

    def get_global_performance_stats(self, *args, **kwargs):
        return self.dashboard_service.get_global_performance_stats(*args, **kwargs)

    def get_student_performance_summary(self, *args, **kwargs):
        return self.dashboard_service.get_student_performance_summary(*args, **kwargs)

    def get_students_at_risk(self, *args, **kwargs):
        return self.dashboard_service.get_students_at_risk(*args, **kwargs)

    # --- Seating Chart Service Delegations ---
    def create_seating_chart(self, *args, **kwargs):
        return self.seating_chart_service.create_seating_chart(*args, **kwargs)

    def get_seating_charts_for_class(self, *args, **kwargs):
        return self.seating_chart_service.get_seating_charts_for_class(*args, **kwargs)

    def get_seating_chart_details(self, *args, **kwargs):
        return self.seating_chart_service.get_seating_chart_details(*args, **kwargs)

    def update_seating_chart_layout(self, *args, **kwargs):
        return self.seating_chart_service.update_seating_chart_layout(*args, **kwargs)

    def save_seat_assignments(self, *args, **kwargs):
        return self.seating_chart_service.save_seat_assignments(*args, **kwargs)

    def delete_seating_chart(self, *args, **kwargs):
        return self.seating_chart_service.delete_seating_chart(*args, **kwargs)

    # Legacy private method used by CSV import in StudentService
    # Since StudentService now handles this internally, we might not need to expose it here
    # unless some other part of the system calls it directly.
    # It was private (_) so it shouldn't be called externally.
    def _batch_upsert_students_and_enroll(self, db, class_id, student_data_list):
         return self.student_service._batch_upsert_students_and_enroll(db, class_id, student_data_list)
