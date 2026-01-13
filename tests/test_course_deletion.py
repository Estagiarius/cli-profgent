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

def test_delete_course_with_dependencies_raises_error(data_service: DataService):
    """
    Test that deleting a course associated with a class (via ClassSubject)
    raises a ValueError, as required by business logic.
    """
    # Create a course
    course = data_service.add_course("Math", "MATH101")
    assert course is not None
    course_id = course["id"]

    # Create a class
    class_ = data_service.create_class("Class A")
    assert class_ is not None
    class_id = class_["id"]

    # Link course to class (create dependency)
    data_service.add_subject_to_class(class_id, course_id)

    # Attempt to delete the course
    # This should raise ValueError per requirements
    with pytest.raises(ValueError, match="Cannot delete course"):
         data_service.delete_course(course_id)

    # Verify that the course was NOT deleted
    fetched_course = data_service.get_course_by_id(course_id)
    assert fetched_course is not None
