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
from sqlalchemy import Column, Integer, String, Time, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base

class TimeSlot(Base):
    """
    Representa um intervalo de tempo configurável na grade horária do professor.
    Ex: Segunda-feira, 1ª Aula (07:30 - 08:20).
    """
    __tablename__ = 'time_slots'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # 0 = Segunda, 1 = Terça, ..., 4 = Sexta, 5 = Sábado, 6 = Domingo
    day_of_week = Column(Integer, nullable=False)

    # Índice visual da aula (ex: 1ª aula, 2ª aula). Ajuda a alinhar a grade visualmente.
    period_index = Column(Integer, nullable=False)

    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    # Relacionamento com a alocação (aula fixa)
    schedule_assignment = relationship("WeeklySchedule", uselist=False, back_populates="time_slot", cascade="all, delete-orphan")

    __table_args__ = (
        # Garante que não haja dois slots com mesmo índice no mesmo dia
        UniqueConstraint('day_of_week', 'period_index', name='_day_period_uc'),
    )

    def __repr__(self):
        return f"<TimeSlot(day={self.day_of_week}, period={self.period_index}, start={self.start_time})>"


class WeeklySchedule(Base):
    """
    Representa a alocação fixa de uma turma/disciplina em um slot de tempo.
    Ex: No slot "Segunda, 1ª Aula", o professor dá aula de "Matemática" para a "Turma 1A".
    """
    __tablename__ = 'weekly_schedule'

    id = Column(Integer, primary_key=True, autoincrement=True)

    time_slot_id = Column(Integer, ForeignKey('time_slots.id'), nullable=False, unique=True)
    class_subject_id = Column(Integer, ForeignKey('class_subjects.id'), nullable=False)

    time_slot = relationship("TimeSlot", back_populates="schedule_assignment")
    class_subject = relationship("ClassSubject")

    def __repr__(self):
        return f"<WeeklySchedule(slot={self.time_slot_id}, subject={self.class_subject_id})>"
