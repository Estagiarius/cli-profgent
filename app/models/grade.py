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
# Importa os tipos de coluna necessários e a restrição de verificação (CheckConstraint) do SQLAlchemy.
from sqlalchemy import Column, Integer, String, Float, ForeignKey, CheckConstraint
# Importa a função 'relationship' para definir relacionamentos entre modelos.
from sqlalchemy.orm import relationship
# Importa a classe 'Base' declarativa da qual todos os modelos devem herdar.
from app.models.base import Base

# Define a classe Grade, que representa a nota de um aluno em uma avaliação.
class Grade(Base):
    """
    Representa a tabela de notas (grades) no modelo de dados.

    A classe Grade modela uma nota associada a um aluno (student) e a uma avaliação
    (assessment) específica. Cada entrada inclui informações sobre a nota obtida,
    o aluno ao qual a nota pertence e a avaliação correspondente. Além disso,
    inclui uma data de registro da nota.

    :ivar id: Identificador único da nota. Chave primária com autoincremento.
    :type id: int
    :ivar student_id: Identificador do aluno associado à nota. Chave estrangeira
        para a tabela de alunos ('students'). Indexado para performance.
    :type student_id: int
    :ivar assessment_id: Identificador da avaliação associada à nota. Chave estrangeira
        para a tabela de avaliações ('assessments'). Indexado para performance.
    :type assessment_id: int
    :ivar score: Nota obtida pelo aluno na avaliação em questão. Deve ser um número
        maior ou igual a 0.
    :type score: float
    :ivar date_recorded: Data em que a nota foi registrada. Representada como uma
        string. Em aplicações reais, idealmente deveria ser do tipo DateTime.
    :type date_recorded: str
    """
    # Define o nome da tabela no banco de dados para este modelo.
    __tablename__ = 'grades'

    # Define a coluna 'id' como um inteiro, chave primária e com autoincremento.
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Define a coluna 'student_id' como uma chave estrangeira para a tabela 'students'. Não pode ser nula.
    # index=True adicionado para otimizar queries que filtram ou fazem join por aluno (ex: boletins).
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False, index=True)
    # Define a coluna 'assessment_id' como uma chave estrangeira para a tabela 'assessments'. Não pode ser nula.
    # index=True adicionado para otimizar queries que filtram ou fazem join por avaliação (ex: estatísticas globais).
    assessment_id = Column(Integer, ForeignKey('assessments.id'), nullable=False, index=True)
    # Define a coluna 'score' (nota) como um número de ponto flutuante. Não pode ser nula.
    score = Column(Float, nullable=False)
    # Define a coluna 'date_recorded' (data de registro) como uma string. Não pode ser nula.
    # Observação no código original: Em uma aplicação real, isso deveria ser do tipo DateTime.
    date_recorded = Column(String, nullable=False)

    # Define o relacionamento com o modelo Student. 'back_populates' cria a referência inversa no modelo Student.
    student = relationship("Student", back_populates="grades")
    # Define o relacionamento com o modelo Assessment. Permite acessar os dados da avaliação a partir da nota.
    assessment = relationship("Assessment")

    # Define restrições a nível de tabela.
    __table_args__ = (
        # Garante que o valor da coluna 'score' seja sempre maior ou igual a 0.
        CheckConstraint('score >= 0', name='check_score_positive'),
    )

    # Define uma representação em string para o objeto Grade, útil para depuração.
    def __repr__(self):
        # Retorna uma string formatada com o id, ids do aluno e da avaliação, e a nota.
        return f"<Grade(id={self.id}, student_id={self.student_id}, assessment_id={self.assessment_id}, score={self.score})>"
