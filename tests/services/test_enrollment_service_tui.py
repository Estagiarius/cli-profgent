from app.services.data.enrollment_service import EnrollmentService
from app.models.student import Student
from app.models.class_ import Class
from app.models.class_enrollment import ClassEnrollment
from datetime import date

def test_get_student_enrollments(db_session):
    # Setup
    service = EnrollmentService(db_session)

    # Create class
    cls = Class(name="Test Class")
    db_session.add(cls)
    db_session.flush()

    # Create student
    student = Student(first_name="John", last_name="Doe", enrollment_date=date.today().isoformat())
    db_session.add(student)
    db_session.flush()

    # Create enrollment
    enrollment = ClassEnrollment(class_id=cls.id, student_id=student.id, call_number=1, status="Active")
    db_session.add(enrollment)
    db_session.commit()

    # Test
    enrollments = service.get_student_enrollments(student.id)

    assert len(enrollments) == 1
    assert enrollments[0]['class_name'] == "Test Class"
    assert enrollments[0]['status'] == "Active"
    assert enrollments[0]['class_id'] == cls.id
