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
# Importa os tipos de coluna necessários e a restrição de unicidade (UniqueConstraint) do SQLAlchemy.
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
# Importa a função 'relationship' para definir relacionamentos entre modelos.
from sqlalchemy.orm import relationship
# Importa a classe 'Base' declarativa da qual todos os modelos devem herdar.
from app.models.base import Base

# Define a classe ClassEnrollment, que representa a matrícula de um aluno em uma turma.
class ClassEnrollment(Base):
    """
    Representa a matrícula de um estudante em uma turma, detalhando as informações
    relacionadas ao aluno, à turma e o status da matrícula.

    Este modelo define a tabela `class_enrollments` no banco de dados e inclui
    restrições exclusivas para garantir a consistência dos dados. Além disso,
    estabelece relacionamentos diretos com os modelos `Student` e `Class` para
    acesso aos dados associados.

    :ivar id: Identificador único da matrícula, gerado automaticamente.
    :ivar class_id: Identificador da turma associada à matrícula. Chave estrangeira
        para a tabela 'classes'.
    :ivar student_id: Identificador do estudante associado à matrícula. Chave
        estrangeira para a tabela 'students'. Indexado.
    :ivar call_number: Número de chamada associado ao estudante nesta turma.
    :ivar status: Status da matrícula, como "Active" ou "Inactive". Valor padrão:
        "Active".
    :ivar status_detail: Detalhes adicionais sobre o status da matrícula. Exemplo:
        "Transferido". Este atributo é opcional (pode ser nulo).
    :ivar student: Relacionamento com o modelo `Student`. Permite acesso às
        informações do estudante associado.
    :ivar class_: Relacionamento com o modelo `Class`. Permite acesso às
        informações da turma associada. Este relacionamento é bidirecional, com
        suporte à referência inversa no modelo `Class`.
    """
    # Define o nome da tabela no banco de dados para este modelo.
    __tablename__ = 'class_enrollments'

    # Define a coluna 'id' como um inteiro, chave primária e com autoincremento.
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Define a coluna 'class_id' como uma chave estrangeira para a tabela 'classes'. Não pode ser nula.
    class_id = Column(Integer, ForeignKey('classes.id'), nullable=False)
    # Define a coluna 'student_id' como uma chave estrangeira para a tabela 'students'. Não pode ser nula.
    # index=True otimiza buscas reversas (Student -> ClassEnrollment), que não são cobertas pelo índice composto (class_id, student_id).
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False, index=True)
    # Define a coluna 'call_number' (número de chamada) como um inteiro. Não pode ser nula.
    call_number = Column(Integer, nullable=False)
    # Define a coluna 'status' como uma string, com valor padrão 'Active'. Ex: "Active", "Inactive".
    status = Column(String, nullable=False, default='Active')
    # Define a coluna 'status_detail' como uma string que pode ser nula. Ex: "Transferido".
    status_detail = Column(String, nullable=True)

    # Define o relacionamento com o modelo Student. Permite acessar os dados do aluno a partir da matrícula.
    student = relationship("Student")
    # Define o relacionamento com o modelo Class. 'back_populates' cria a referência inversa no modelo Class.
    class_ = relationship("Class", back_populates="enrollments")

    # Define restrições a nível de tabela.
    __table_args__ = (
        # Garante que a combinação de 'class_id' e 'student_id' seja única. Um aluno só pode se matricular uma vez na mesma turma.
        UniqueConstraint('class_id', 'student_id', name='_class_student_uc'),
        # Garante que a combinação de 'class_id' e 'call_number' seja única. Não pode haver dois números de chamada iguais na mesma turma.
        UniqueConstraint('class_id', 'call_number', name='_class_call_number_uc'),
    )

    # Define uma representação em string para o objeto ClassEnrollment, útil para depuração.
    def __repr__(self):
        # Retorna uma string formatada com os IDs da turma, do aluno e o número de chamada.
        return f"<ClassEnrollment(class_id={self.class_id}, student_id={self.student_id}, call_number={self.call_number})>"
