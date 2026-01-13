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
from app.services.data_service import DataService
from app.models.course import Course
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base

# Setup in-memory DB for isolation
@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture
def data_service(db_session):
    return DataService(db_session=db_session)

def test_update_course_bncc(data_service, db_session):
    # 1. Create a course
    course = Course(course_name="History", course_code="HIS101", bncc_expected="EF01HI01")
    db_session.add(course)
    db_session.commit()
    course_id = course.id

    # 2. Update BNCC
    new_bncc = "EF01HI01,EF01HI02"
    data_service.update_course_bncc(course_id, new_bncc)

    # 3. Verify
    updated_course = db_session.query(Course).filter(Course.id == course_id).first()
    assert updated_course.bncc_expected == new_bncc

    # 4. Verify other fields remained touched
    assert updated_course.course_name == "History"
    assert updated_course.course_code == "HIS101"

def test_update_course_bncc_empty(data_service, db_session):
    course = Course(course_name="Math", course_code="MAT101", bncc_expected="EF01MA01")
    db_session.add(course)
    db_session.commit()

    # Update to empty string
    data_service.update_course_bncc(course.id, "")

    updated = db_session.query(Course).get(course.id)
    assert updated.bncc_expected == ""
