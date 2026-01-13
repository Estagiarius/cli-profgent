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
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base

class ClassSubject(Base):
    """
    Representa a associação entre uma Turma (Class) e uma Disciplina (Course).
    Ex: Turma "1A" tem a disciplina "Matemática".

    :ivar id: Identificador único da associação.
    :ivar class_id: ID da turma.
    :ivar course_id: ID da disciplina. Indexado.
    """
    __tablename__ = 'class_subjects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    class_id = Column(Integer, ForeignKey('classes.id'), nullable=False)
    # index=True otimiza buscas reversas (Course -> ClassSubject), ex: estatísticas por disciplina.
    # O índice composto (class_id, course_id) não cobre buscas apenas por course_id.
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False, index=True)

    # Relacionamentos
    class_ = relationship("Class", back_populates="subjects")
    course = relationship("Course", back_populates="class_subjects")

    # Objetos dependentes dessa associação
    assessments = relationship("Assessment", back_populates="class_subject", cascade="all, delete-orphan")
    lessons = relationship("Lesson", back_populates="class_subject", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('class_id', 'course_id', name='_class_course_uc'),
    )

    def __repr__(self):
        return f"<ClassSubject(class_id={self.class_id}, course_id={self.course_id})>"
