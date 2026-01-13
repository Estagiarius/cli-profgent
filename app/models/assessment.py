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
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
# Importa a classe 'Base' declarativa da qual todos os modelos devem herdar.
from app.models.base import Base

# Define a classe Assessment, que representa uma avaliação (prova, trabalho, etc.) no banco de dados.
class Assessment(Base):
    """
    Representa a classe de modelo Assessment.

    A classe Assessment é utilizada para modelar uma entidade de avaliação, responsável
    por armazenar informações como nome, peso e associação com uma determinada disciplina de uma turma.
    Esse modelo é utilizado no contexto de persistência de dados em um banco relacional
    e é definido no formato de uma tabela SQL.

    :ivar id: Identificador único para cada avaliação.
    :type id: int
    :ivar name: Nome da avaliação, obrigatório.
    :type name: str
    :ivar weight: Peso atribuído à avaliação, obrigatório, com valor padrão de 1.0.
    :type weight: float
    :ivar class_subject_id: Identificador da disciplina da turma, referenciando uma chave estrangeira. Indexado.
    :type class_subject_id: int
    """
    # Define o nome da tabela no banco de dados para este modelo.
    __tablename__ = 'assessments'

    # Define a coluna 'id' como um inteiro, chave primária e com autoincremento.
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Define a coluna 'name' como uma string que não pode ser nula (obrigatória).
    name = Column(String, nullable=False)
    # Define a coluna 'weight' como um número de ponto flutuante (decimal), obrigatório, com valor padrão de 1.0.
    weight = Column(Float, nullable=False, default=1.0)
    # Define o período de avaliação (1, 2, 3, 4 para bimestres, 5 para final).
    grading_period = Column(Integer, nullable=False, default=1)
    # Define a coluna 'bncc_codes' para armazenar os códigos da BNCC avaliados.
    bncc_codes = Column(Text, nullable=True)
    # Define a coluna 'class_subject_id' como um inteiro que é uma chave estrangeira.
    # index=True otimiza busca de avaliações por disciplina.
    class_subject_id = Column(Integer, ForeignKey('class_subjects.id'), nullable=False, index=True)

    # Relacionamento com ClassSubject
    class_subject = relationship("ClassSubject", back_populates="assessments")

    # Define uma representação em string para o objeto Assessment, útil para depuração.
    def __repr__(self):
        # Retorna uma string formatada com o id, nome e peso da avaliação.
        return f"<Assessment(id={self.id}, name='{self.name}', weight={self.weight})>"
