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
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base

class SeatingChart(Base):
    """
    Representa o layout (mapa de sala) de uma turma.
    Define as dimensões da sala e a configuração das células (mesa, porta, etc.).
    """
    __tablename__ = 'seating_charts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    class_id = Column(Integer, ForeignKey('classes.id'), nullable=False, index=True)
    name = Column(String, nullable=False) # Ex: "Layout Padrão", "Dia de Prova"
    rows = Column(Integer, nullable=False)
    columns = Column(Integer, nullable=False)

    # Armazena a configuração "estática" da grade como uma string JSON.
    # Ex: {"0,0": "teacher_desk", "0,5": "door", "2,2": "void"}
    # As células não mencionadas são assumidas como "student_seat".
    layout_config = Column(String, default="{}")

    created_at = Column(DateTime, default=datetime.now)

    # Relacionamentos
    class_ = relationship("Class", backref="seating_charts")
    assignments = relationship("SeatAssignment", back_populates="chart", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<SeatingChart(id={self.id}, name='{self.name}', class_id={self.class_id})>"


class SeatAssignment(Base):
    """
    Representa a atribuição de um aluno a um assento específico em um mapa de sala.
    """
    __tablename__ = 'seat_assignments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    chart_id = Column(Integer, ForeignKey('seating_charts.id'), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False, index=True)

    row_index = Column(Integer, nullable=False)
    col_index = Column(Integer, nullable=False)

    # Relacionamentos
    chart = relationship("SeatingChart", back_populates="assignments")
    student = relationship("Student") # Acesso unidirecional ao aluno é suficiente

    def __repr__(self):
        return f"<SeatAssignment(chart={self.chart_id}, student={self.student_id}, pos=({self.row_index},{self.col_index}))>"
