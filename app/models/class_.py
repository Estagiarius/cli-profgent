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
# Importa os tipos de coluna necessários do SQLAlchemy para definir o modelo.
from sqlalchemy import Column, Integer, String, Enum
# Importa a função 'relationship' para definir relacionamentos entre modelos.
from sqlalchemy.orm import relationship
# Importa a classe 'Base' declarativa da qual todos os modelos devem herdar.
from app.models.base import Base

# Define a classe Class, que representa uma turma no banco de dados.
# O nome do arquivo e da classe usa um underscore '_' para evitar conflito com a palavra-chave 'class' do Python.
class Class(Base):
    """
    Representa uma turma associada a um curso em um sistema educacional.

    Esta classe modela uma turma que pertence a um curso, com métodos de cálculo avaliativo e relacionadas
    a componentes como avaliações, aulas, matrículas e incidentes. A associação com outros modelos, como
    Course, Assessment ou Lesson, é feita por meio de relacionamentos SQLAlchemy.

    :ivar __tablename__: Nome da tabela no banco de dados.
    :type __tablename__: str
    :ivar id: Identificador único da turma, número inteiro, autoincrementável.
    :type id: int
    :ivar name: Nome único da turma, obrigatório.
    :type name: str
    :ivar calculation_method: Método de cálculo aplicado na turma.
        Pode ser 'arithmetic' (média aritmética) ou 'weighted' (média ponderada).
    :type calculation_method: Enum('arithmetic', 'weighted')
    :ivar subjects: Relacionamento com ClassSubject.
        Representa as disciplinas associadas à turma.
    :type subjects: list[ClassSubject]
    :ivar enrollments: Relacionamento com o modelo ClassEnrollment.
        Representa as matrículas realizadas na turma.
    :type enrollments: list[ClassEnrollment]
    :ivar incidents: Relacionamento com o modelo Incident.
        Representa os incidentes registrados na turma.
    :type incidents: list[Incident]
    """
    # Define o nome da tabela no banco de dados para este modelo.
    __tablename__ = 'classes'

    # Define a coluna 'id' como um inteiro, chave primária e com autoincremento.
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Define a coluna 'name' como uma string que não pode ser nula e deve ser única.
    name = Column(String, nullable=False, unique=True)
    # Define a coluna 'calculation_method' usando o tipo Enum do SQLAlchemy.
    # Isso restringe os valores a 'arithmetic' (média aritmética) ou 'weighted' (média ponderada).
    # O campo é obrigatório e o valor padrão é 'arithmetic'.
    calculation_method = Column(Enum('arithmetic', 'weighted', name='calculation_methods'), nullable=False, default='arithmetic')

    # Relacionamento com ClassSubject (Disciplinas da Turma)
    subjects = relationship("ClassSubject", back_populates="class_", cascade="all, delete-orphan")

    # Define o relacionamento com ClassEnrollment (matrículas), criando a referência inversa.
    enrollments = relationship("ClassEnrollment", back_populates="class_", cascade="all, delete-orphan")

    # Define o relacionamento com Incident (incidentes).
    incidents = relationship("Incident", back_populates="class_", cascade="all, delete-orphan")

    # Define uma representação em string para o objeto Class, útil para depuração.
    def __repr__(self):
        # Retorna uma string formatada com o id e o nome da turma.
        return f"<Class(id={self.id}, name='{self.name}')>"
