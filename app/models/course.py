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
from sqlalchemy import Column, Integer, String, Text
# Importa a função 'relationship' para definir relacionamentos entre modelos.
from sqlalchemy.orm import relationship
# Importa a classe 'Base' declarativa da qual todos os modelos devem herdar.
from app.models.base import Base

# Define a classe Course, que representa uma disciplina ou curso (ex: Matemática, História) no banco de dados.
class Course(Base):
    """
    Representa o modelo de um curso no sistema.

    A classe `Course` define as propriedades e relacionamentos associadas a um curso.
    Um curso é identificado por um código único, possui um nome exclusivo, e pode
    estar associado a várias turmas. Esse modelo reflete a estrutura da tabela
    'courses' no banco de dados.

    :ivar id: Identificador único do curso. Gerado automaticamente como chave primária.
    :type id: int
    :ivar course_name: Nome exclusivo do curso. Este campo é obrigatório.
    :type course_name: str
    :ivar course_code: Código único associado ao curso.
    :type course_code: str
    :ivar class_subjects: Relacionamento com ClassSubject.
        Representa as associações com turmas.
    :type class_subjects: List[ClassSubject]
    """
    # Define o nome da tabela no banco de dados para este modelo.
    __tablename__ = 'courses'

    # Define a coluna 'id' como um inteiro, chave primária e com autoincremento.
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Define a coluna 'course_name' como uma string que não pode ser nula e deve ser única.
    course_name = Column(String, nullable=False, unique=True)
    # Define a coluna 'course_code' como uma string que deve ser única.
    course_code = Column(String, unique=True)
    # Define a coluna 'bncc_expected' para armazenar os códigos da BNCC esperados (csv).
    bncc_expected = Column(Text, nullable=True)

    # Relacionamento com ClassSubject (Associações com Turmas)
    class_subjects = relationship("ClassSubject", back_populates="course", cascade="all, delete-orphan")

    # Define uma representação em string para o objeto Course, útil para depuração.
    def __repr__(self):
        # Retorna uma string formatada com o id e o nome do curso.
        return f"<Course(id={self.id}, course_name='{self.course_name}')>"
