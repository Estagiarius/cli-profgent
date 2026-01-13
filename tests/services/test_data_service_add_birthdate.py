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

def test_add_student_with_birth_date(data_service: DataService):
    # Data de nascimento válida
    birth_date = date(2015, 8, 20)

    # Chama add_student passando a data
    student = data_service.add_student("New", "Student", birth_date=birth_date)

    # Verifica se foi criado corretamente
    assert student is not None
    assert student['first_name'] == "New"
    assert student['last_name'] == "Student"
    assert student['birth_date'] == "2015-08-20"

    # Verifica no banco (via get_student_by_name)
    fetched_student = data_service.get_student_by_name("New Student")
    assert fetched_student['birth_date'] == "2015-08-20"

def test_add_student_without_birth_date(data_service: DataService):
    # Sem data de nascimento
    student = data_service.add_student("NoDate", "Student")

    assert student is not None
    assert student['birth_date'] is None
