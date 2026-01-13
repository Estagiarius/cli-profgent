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
import os
from app.services.report_service import ReportService

class TestReportService:
    @pytest.fixture
    def report_service(self, mocker):
        # Mock DataService within ReportService
        MockDataService = mocker.patch('app.services.report_service.DataService')
        service = ReportService()
        service.data_service = MockDataService.return_value
        return service

    def test_generate_student_report_card(self, report_service):
        # Mock data
        report_service.data_service.get_class_by_id.return_value = {"id": 1, "name": "Class A"}
        report_service.data_service.get_all_students.return_value = [{"id": 1, "first_name": "John", "last_name": "Doe"}]

        # New optimized mock structure
        report_service.data_service.get_class_report_data.return_value = {
            "students": [{"student_id": 1, "name": "John Doe", "call_number": 1, "status": "Active"}],
            "subjects": [
                {
                    "id": 10,
                    "course_name": "Math",
                    "assessments": [{"id": 100, "name": "Test 1", "weight": 1.0}]
                }
            ],
            "grades_map": {(1, 100): 9.0}
        }
        report_service.data_service.get_student_incidents.return_value = []
        report_service.data_service.calculate_weighted_average.return_value = 9.0
        # Mock attendance stats
        report_service.data_service.get_student_attendance_stats.return_value = {
            "total_lessons": 10,
            "present_count": 9,
            "absent_count": 1,
            "percentage": 90.0
        }

        # Call method
        filepath = report_service.generate_student_report_card(1, 1)

        # Verify
        assert os.path.exists(filepath)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "BOLETIM ESCOLAR" in content
            assert "John Doe" in content
            assert "DISCIPLINA: MATH" in content
            assert "MÉDIA FINAL: 9.00" in content

        # Cleanup
        os.remove(filepath)

    def test_generate_class_grade_distribution(self, report_service):
        # Mock data
        report_service.data_service.get_class_by_id.return_value = {"id": 1, "name": "Class A"}

        # New optimized mock structure
        report_service.data_service.get_class_report_data.return_value = {
            "students": [{"student_id": 1, "name": "John Doe", "call_number": 1, "status": "Active"}],
            "subjects": [
                {
                    "id": 10,
                    "course_name": "Math",
                    "assessments": [{"id": 100, "name": "Test 1", "weight": 1.0}]
                }
            ],
            "grades_map": {(1, 100): 8.0}
        }
        report_service.data_service.calculate_weighted_average.return_value = 8.0

        filepath = report_service.generate_class_grade_distribution(1)
        assert os.path.exists(filepath)
        os.remove(filepath)

    def test_export_class_grades_csv(self, report_service):
        # Mock data
        report_service.data_service.get_class_by_id.return_value = {"id": 1, "name": "Class A"}

        # New optimized mock structure
        report_service.data_service.get_class_report_data.return_value = {
            "students": [{"student_id": 1, "name": "John Doe", "call_number": 1, "status": "Active"}],
            "subjects": [
                {
                    "id": 10,
                    "course_name": "Math",
                    "assessments": [{"id": 100, "name": "Test 1", "weight": 1.0}]
                }
            ],
            "grades_map": {(1, 100): 10.0}
        }
        report_service.data_service.calculate_weighted_average.return_value = 10.0

        filepath = report_service.export_class_grades_csv(1)
        assert os.path.exists(filepath)

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "John Doe" in content
            assert "Math" in content # Header check
            assert "10.00" in content

        os.remove(filepath)
