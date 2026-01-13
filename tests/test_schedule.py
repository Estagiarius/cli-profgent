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
from datetime import datetime, date
from app.services.data_service import DataService
from app.models.schedule import TimeSlot, WeeklySchedule

def test_create_time_slot(data_service: DataService):
    # Setup
    slot = data_service.create_time_slot(0, 1, "08:00", "09:00")

    assert slot is not None
    assert slot['day_of_week'] == 0
    assert slot['period_index'] == 1
    assert slot['start_time'] == "08:00"
    assert slot['end_time'] == "09:00"

def test_duplicate_time_slot_raises_error(data_service: DataService):
    data_service.create_time_slot(0, 1, "08:00", "09:00")

    with pytest.raises(ValueError, match="Já existe um período configurado"):
        data_service.create_time_slot(0, 1, "09:00", "10:00") # Same day/index

def test_get_time_slots(data_service: DataService):
    data_service.create_time_slot(0, 1, "08:00", "09:00")
    data_service.create_time_slot(1, 1, "08:00", "09:00") # Tue

    slots = data_service.get_time_slots()
    assert len(slots) == 2

    monday_slots = data_service.get_time_slots(day_of_week=0)
    assert len(monday_slots) == 1
    assert monday_slots[0]['day_of_week'] == 0

def test_create_schedule_assignment(data_service: DataService):
    # Setup Class & Course
    cls = data_service.create_class("Test Class")
    course = data_service.add_course("Math", "MAT")
    subj = data_service.add_subject_to_class(cls['id'], course['id'])

    # Setup Slot
    slot = data_service.create_time_slot(0, 1, "08:00", "09:00")

    # Assign
    assign = data_service.create_schedule_assignment(slot['id'], subj['id'])
    assert assign is not None
    assert assign['id'] is not None

def test_get_full_schedule_grid(data_service: DataService):
    # Setup
    cls = data_service.create_class("Class A")
    course = data_service.add_course("Math", "MAT")
    subj = data_service.add_subject_to_class(cls['id'], course['id'])

    slot = data_service.create_time_slot(0, 1, "08:00", "09:00")
    data_service.create_schedule_assignment(slot['id'], subj['id'])

    grid = data_service.get_full_schedule_grid()

    assert 0 in grid
    assert len(grid[0]) == 1
    item = grid[0][0]
    assert item['start_time'] == "08:00"
    assert item['assignment'] is not None
    assert item['assignment']['class_name'] == "Class A"
    assert item['assignment']['course_name'] == "Math"

def test_delete_time_slot_removes_assignment(data_service: DataService):
    cls = data_service.create_class("Class A")
    course = data_service.add_course("Math", "MAT")
    subj = data_service.add_subject_to_class(cls['id'], course['id'])
    slot = data_service.create_time_slot(0, 1, "08:00", "09:00")
    data_service.create_schedule_assignment(slot['id'], subj['id'])

    # Delete
    data_service.delete_time_slot(slot['id'])

    # Verify
    slots = data_service.get_time_slots()
    assert len(slots) == 0

    # Verify assignment gone (via grid)
    grid = data_service.get_full_schedule_grid()
    assert 0 not in grid
