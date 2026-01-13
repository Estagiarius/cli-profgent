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
import pytest
from datetime import date
from app.services.data_service import DataService
from app.models.student import Student
from app.models.lesson import Lesson
from app.models.class_subject import ClassSubject
from app.models.attendance import Attendance

class TestAttendance:
    def test_register_attendance(self, db_session, data_service):
        # Setup data
        student1 = Student(first_name="John", last_name="Doe", enrollment_date="2023-01-01")
        student2 = Student(first_name="Jane", last_name="Doe", enrollment_date="2023-01-01")
        db_session.add(student1)
        db_session.add(student2)
        db_session.flush()

        class_subject = ClassSubject(class_id=1, course_id=1) # Mock IDs
        db_session.add(class_subject)
        db_session.flush()

        lesson = Lesson(title="Math 101", date=date(2023, 10, 1), class_subject_id=class_subject.id)
        db_session.add(lesson)
        db_session.flush()

        # Register attendance
        attendance_data = [
            {'student_id': student1.id, 'status': 'P'},
            {'student_id': student2.id, 'status': 'F'}
        ]

        data_service.register_attendance(lesson.id, attendance_data)

        # Verify
        records = db_session.query(Attendance).filter(Attendance.lesson_id == lesson.id).all()
        assert len(records) == 2

        r1 = next(r for r in records if r.student_id == student1.id)
        assert r1.status == 'P'

        r2 = next(r for r in records if r.student_id == student2.id)
        assert r2.status == 'F'

        # Update attendance
        attendance_data_update = [
            {'student_id': student2.id, 'status': 'J'}
        ]
        data_service.register_attendance(lesson.id, attendance_data_update)

        db_session.expire_all()
        r2_updated = db_session.query(Attendance).filter(Attendance.student_id == student2.id, Attendance.lesson_id == lesson.id).first()
        assert r2_updated.status == 'J'

    def test_get_attendance_stats(self, db_session, data_service):
        # Setup
        student = Student(first_name="Stats", last_name="Student", enrollment_date="2023-01-01")
        db_session.add(student)
        db_session.flush()

        class_subject = ClassSubject(class_id=1, course_id=1)
        db_session.add(class_subject)
        db_session.flush()

        # Create 4 lessons
        lessons = []
        for i in range(4):
            l = Lesson(title=f"L{i}", date=date(2023, 10, 1), class_subject_id=class_subject.id)
            db_session.add(l)
            lessons.append(l)
        db_session.flush()

        # Attendance: P, F, A, J -> 3 Present (P, A, J), 1 Absent (F) => 75%
        statuses = ['P', 'F', 'A', 'J']
        for i, l in enumerate(lessons):
            att = Attendance(lesson_id=l.id, student_id=student.id, status=statuses[i])
            db_session.add(att)
        db_session.flush()

        stats = data_service.get_student_attendance_stats(student.id, class_subject.id)

        assert stats['total_lessons'] == 4
        assert stats['present_count'] == 3
        assert stats['absent_count'] == 1
        assert stats['percentage'] == 75.0
