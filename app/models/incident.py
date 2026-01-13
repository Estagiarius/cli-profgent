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
# Importa os tipos de coluna necessários do SQLAlchemy.
from sqlalchemy import Column, Integer, Text, Date, ForeignKey
# Importa a função 'relationship' para definir relacionamentos entre modelos.
from sqlalchemy.orm import relationship
# Importa a classe 'Base' declarativa da qual todos os modelos devem herdar.
from app.models.base import Base

# Define a classe Incident, que representa uma ocorrência ou incidente envolvendo um aluno.
class Incident(Base):
    """
    Representa um incidente registrado no contexto de uma classe escolar.

    Este modelo mapeia a tabela 'incidents' no banco de dados e registra informações
    relacionadas a incidentes específicos, como data, descrição, aluno envolvido e
    turma associada. Ele possui relacionamentos com os modelos 'Class' e 'Student',
    permitindo manipulação bidirecional dos dados entre essas tabelas.

    :ivar id: ID único do incidente.
    :type id: Integer
    :ivar date: Data do incidente. Este campo é obrigatório.
    :type date: Date
    :ivar description: Descrição detalhada do incidente. Este campo é obrigatório.
    :type description: Text
    :ivar class_id: Identificador da turma associada ao incidente. Este campo é obrigatório. Indexado.
    :type class_id: Integer
    :ivar student_id: Identificador do aluno relacionado ao incidente. Este campo é obrigatório. Indexado.
    :type student_id: Integer
    :ivar class_: Relacionamento com o modelo 'Class', representando a turma associada.
    :type class_: relationship
    :ivar student: Relacionamento com o modelo 'Student', representando o aluno relacionado.
    :type student: relationship
    """
    # Define o nome da tabela no banco de dados para este modelo.
    __tablename__ = 'incidents'

    # Define a coluna 'id' como um inteiro e chave primária.
    id = Column(Integer, primary_key=True)
    # Define a coluna 'date' como do tipo Date (data), não podendo ser nula.
    date = Column(Date, nullable=False)
    # Define a coluna 'description' como do tipo Text (texto longo), não podendo ser nula.
    description = Column(Text, nullable=False)

    # Define a coluna 'class_id' como uma chave estrangeira para a tabela 'classes'. Não pode ser nula.
    # index=True otimiza queries de ranking de incidentes por turma.
    class_id = Column(Integer, ForeignKey('classes.id'), nullable=False, index=True)
    # Define a coluna 'student_id' como uma chave estrangeira para a tabela 'students'. Não pode ser nula.
    # index=True otimiza queries de incidentes por aluno (ex: análise de risco).
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False, index=True)

    # Define o relacionamento com o modelo Class. 'back_populates' cria a referência inversa no modelo Class.
    class_ = relationship("Class", back_populates="incidents")
    # Define o relacionamento com o modelo Student. 'back_populates' cria a referência inversa no modelo Student.
    student = relationship("Student", back_populates="incidents")

    # Define uma representação em string para o objeto Incident, útil para depuração.
    def __repr__(self):
        # Retorna uma string formatada com o id do incidente e os IDs do aluno e da turma.
        return f"<Incident(id={self.id}, student_id={self.student_id}, class_id={self.class_id})>"
