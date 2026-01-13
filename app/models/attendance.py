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
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base

class Attendance(Base):
    """
    Representa o registro de frequência de um aluno em uma aula.

    :ivar id: Identificador único do registro de frequência.
    :ivar lesson_id: ID da aula (Lesson).
    :ivar student_id: ID do aluno (Student). Indexado.
    :ivar status: Status da presença. 'P' (Presente), 'F' (Falta), 'J' (Justificada), 'A' (Atraso).
    """
    __tablename__ = 'attendance'

    id = Column(Integer, primary_key=True, autoincrement=True)
    lesson_id = Column(Integer, ForeignKey('lessons.id'), nullable=False)
    # index=True otimiza estatísticas de frequência por aluno (Student -> Attendance).
    # O índice composto (lesson_id, student_id) não cobre buscas apenas por student_id.
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False, index=True)
    status = Column(String, nullable=False, default='P')

    lesson = relationship("Lesson", back_populates="attendance_records")
    student = relationship("Student")

    __table_args__ = (
        UniqueConstraint('lesson_id', 'student_id', name='_lesson_student_attendance_uc'),
    )

    def __repr__(self):
        return f"<Attendance(lesson_id={self.lesson_id}, student_id={self.student_id}, status='{self.status}')>"
