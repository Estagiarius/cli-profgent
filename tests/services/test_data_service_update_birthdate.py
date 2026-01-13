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
from datetime import date
from app.services.data_service import DataService
import pytest

def test_update_student_birth_date(data_service: DataService):
    # Create a student with no birth date
    student = data_service.add_student("Test", "Student")
    assert student['birth_date'] is None

    # Update birth date
    new_birth_date = date(2010, 5, 15)
    data_service.update_student(student['id'], "Test", "Student", birth_date=new_birth_date)

    # Verify update
    updated_student = data_service.get_student_by_name("Test Student")
    assert updated_student['birth_date'] == "2010-05-15"

    # Update again to None (if we supported clearing it, but currently the view passes empty string as None?
    # Logic in view converts empty string to None if user clears it.
    # DataService update_student accepts None.
    # Let's verify DataService behavior with None)

    # Wait, in DataService:
    # student.birth_date = birth_date
    # So if we pass None, it sets it to None.

    data_service.update_student(student['id'], "Test", "Student", birth_date=None)
    updated_student_none = data_service.get_student_by_name("Test Student")
    assert updated_student_none['birth_date'] is None
