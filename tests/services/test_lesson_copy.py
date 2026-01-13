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
from app.models.class_ import Class
from app.models.course import Course
from app.models.class_subject import ClassSubject
from app.models.lesson import Lesson

def test_copy_lessons(db_session):
    service = DataService(db_session)

    # Setup: Create Class A, Course Math, Subject A-Math
    class_a = Class(name="Class A")
    course = Course(course_name="Math", course_code="MATH")
    db_session.add(class_a)
    db_session.add(course)
    db_session.flush()

    subject_a = ClassSubject(class_id=class_a.id, course_id=course.id)
    db_session.add(subject_a)
    db_session.flush()

    # Create Lessons in A
    l1 = Lesson(class_subject_id=subject_a.id, title="L1", content="C1", date=date(2023, 1, 1))
    l2 = Lesson(class_subject_id=subject_a.id, title="L2", content="C2", date=date(2023, 1, 2))
    db_session.add_all([l1, l2])
    db_session.flush()

    # Setup: Create Class B, Subject B-Math
    class_b = Class(name="Class B")
    db_session.add(class_b)
    db_session.flush()
    subject_b = ClassSubject(class_id=class_b.id, course_id=course.id)
    db_session.add(subject_b)
    db_session.flush()

    # Action: Copy L1 and L2 to Subject B
    count = service.copy_lessons([l1.id, l2.id], subject_b.id)

    # Verify
    assert count == 2
    lessons_b = db_session.query(Lesson).filter(Lesson.class_subject_id == subject_b.id).all()
    assert len(lessons_b) == 2

    titles = sorted([l.title for l in lessons_b])
    assert titles == ["L1", "L2"]

    # Check content match
    l1_copy = next(l for l in lessons_b if l.title == "L1")
    assert l1_copy.content == "C1"
    assert l1_copy.date == date(2023, 1, 1)
