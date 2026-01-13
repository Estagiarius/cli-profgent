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
from app.tools import database_tools

class TestDatabaseTools:
    @pytest.fixture
    def mock_data_service(self, mocker):
        return mocker.patch('app.tools.database_tools.data_service')

    def test_create_new_class(self, mock_data_service):
        mock_data_service.get_class_by_name.return_value = None
        mock_data_service.create_class.return_value = {"id": 1, "name": "1A"}

        result = database_tools.create_new_class("1A")

        assert "criada com sucesso" in result
        mock_data_service.create_class.assert_called_with("1A")

    def test_add_subject_to_class(self, mock_data_service):
        mock_data_service.get_class_by_name.return_value = {"id": 1, "name": "1A"}
        mock_data_service.get_course_by_name.return_value = {"id": 2, "course_name": "Math"}
        mock_data_service.add_subject_to_class.return_value = True

        result = database_tools.add_subject_to_class("1A", "Math")

        assert "adicionada à turma" in result
        mock_data_service.add_subject_to_class.assert_called_with(1, 2)

    def test_add_new_lesson(self, mock_data_service):
        mock_data_service.get_class_by_name.return_value = {"id": 1}
        mock_data_service.get_subjects_for_class.return_value = [{"id": 10, "course_name": "Math"}]
        mock_data_service.create_lesson.return_value = {"id": 100}

        result = database_tools.add_new_lesson("1A", "Math", "Algebra", "Basics", "12/12/2024")

        assert "registrada com sucesso" in result
        # Check if it used the subject ID 10
        mock_data_service.create_lesson.assert_called()
        args, _ = mock_data_service.create_lesson.call_args
        assert args[0] == 10  # subject_id

    def test_create_new_assessment(self, mock_data_service):
        mock_data_service.get_class_by_name.return_value = {"id": 1}
        mock_data_service.get_subjects_for_class.return_value = [{"id": 10, "course_name": "History"}]
        mock_data_service.add_assessment.return_value = {"id": 50}

        result = database_tools.create_new_assessment("1A", "History", "Test 1", 1.0)

        assert "criada para History" in result
        mock_data_service.add_assessment.assert_called_with(10, "Test 1", 1.0)

    def test_add_new_grade(self, mock_data_service):
        mock_data_service.get_student_by_name.return_value = {"id": 100}
        mock_data_service.get_class_by_name.return_value = {"id": 1}
        mock_data_service.get_subjects_for_class.return_value = [{"id": 10, "course_name": "Math"}]
        mock_data_service.get_assessments_for_subject.return_value = [{"id": 5, "name": "Exam 1"}]
        mock_data_service.add_grade.return_value = {"id": 99}

        result = database_tools.add_new_grade("John", "1A", "Math", "Exam 1", 9.5)

        assert "Nota 9.5 adicionada" in result
        mock_data_service.add_grade.assert_called_with(100, 5, 9.5)

    def test_list_all_classes(self, mock_data_service):
        mock_data_service.get_all_classes.return_value = [
            {"id": 1, "name": "1A", "student_count": 20}
        ]
        mock_data_service.get_subjects_for_class.return_value = [
            {"course_name": "Math"}, {"course_name": "History"}
        ]

        result = database_tools.list_all_classes()

        assert "Turma: 1A" in result
        assert "Math, History" in result

    def test_get_student_grades_by_course(self, mock_data_service):
        mock_data_service.get_student_by_name.return_value = {"id": 1, "name": "John"}
        mock_data_service.get_course_by_name.return_value = {"id": 2, "course_name": "Math"}
        mock_data_service.get_all_grades_with_details.return_value = [
            {"student_id": 1, "course_id": 2, "class_name": "1A", "assessment_name": "Test", "score": 10.0},
            {"student_id": 1, "course_id": 3, "class_name": "1A", "assessment_name": "Geo Test", "score": 5.0} # Should filter out
        ]

        result = database_tools.get_student_grades_by_course("John", "Math")

        assert "Test" in result
        assert "10.0" in result
        assert "Geo Test" not in result
