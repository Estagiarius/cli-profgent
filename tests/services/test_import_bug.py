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
# Importa as classes de serviço e de sessão do banco para serem usadas nas fixtures.
from app.services.data_service import DataService
from sqlalchemy.orm import Session

# Define a função de teste que simula o bug de importação.
def test_import_bug_with_user_csv(data_service: DataService, db_session: Session):
    """
    Caso de teste que usa o CSV fornecido pelo usuário para confirmar a correção final.
    Ele simula o fluxo de trabalho do orquestrador, lendo o conteúdo do arquivo
    e passando-o para o DataService.
    """
    # --- PREPARAÇÃO ---
    # Cria uma turma para o teste, isolando-o de outros dados.
    # course = data_service.add_course("Bug Repro Course", "BRC101") # Não precisa mais de curso para criar turma
    class_ = data_service.create_class("Bug Repro Class")
    db_session.flush()

    # --- DADOS DE TESTE ---
    # O conteúdo exato do arquivo CSV que causava o bug.
    # Este CSV tem várias características importantes para o teste:
    # - Linhas de metadados no início que devem ser ignoradas.
    # - Um cabeçalho que define as colunas.
    # - Alunos com status variados ("ATIVO", "BAIXA - TRANSFERÊNCIA", "Transferido").
    # - Alunos duplicados (ex: "JÚLIA NOGUEIRA RAMOS", "NICOLY ALVARES DE OLIVEIRA ROCHA"),
    #   onde apenas a última ocorrência (a mais recente no arquivo) deve ser considerada.
    csv_content = """Alunos;11/11/2025 13:31

Filtros

Ano Letivo;2025

Nº de chamada;Nome do Aluno;Data de Nascimento;Situação do Aluno
1;ALEANDRO VENICIO DO NASCIMENTO MORAIS;26/06/2009;BAIXA - TRANSFERÊNCIA
2;ANA CAROLINA DE SOUZA AMURIM;19/08/2009;BAIXA - TRANSFERÊNCIA
3;ANA JULIA GONÇALVES;09/06/2008;Transferido
4;ANDRÉ HENRIQUE COSTA E SILVA;01/10/2009;Ativo
5;ANNI MARCELLY DE ASSIS CANDIDO;26/03/2008;Transferido
6;ANNY DOMICIANO GOMES;13/09/2009;Ativo
7;ARTHUR DARIO MOREIRA CABRAL;20/11/2009;Ativo
8;ARTUR SOARES DE SOUZA COSTA;25/01/2010;Transferido
9;BÁRBARA ESTEVÃO RESENDE CAROZZI;21/12/2009;Ativo
10;CAIO HENRIQUE FERREIRA DOS SANTOS;10/12/2008;Transferido
11;DANIEL NAPOLEÃO DA SILVA;22/12/2009;Ativo
12;ENZO CASTRO DA SILVA;23/11/2009;Ativo
13;ESTER VIEIRA MAFRA;03/05/2010;Transferido
14;FERNANDA DE ABREU LUCHEZ;13/03/2010;Ativo
15;GABRIEL CARDOSO DA SILVA;27/05/2010;Ativo
16;GIOVANNA BARBOSA DEODATO;24/11/2009;Ativo
17;ISABELLE ARAUJO GOMES;10/07/2009;Ativo
18;JÚLIA NOGUEIRA RAMOS;28/09/2009;Transferido
19;KAIQUE ALMEIDA CLEMENTE;29/01/2010;Ativo
20;KETHELYN DIAS DE OLIVEIRA;20/08/2008;Transferido
21;KEVYN ALLYSSON CONCEIÇÃO FERNANDES;29/01/2009;BAIXA - TRANSFERÊNCIA
22;LARA SIMPLICIO DA SILVA;09/03/2010;Ativo
23;LEONARDO DE SOUZA JARDIM;23/02/2010;Ativo
24;MANUELA BENTO MONTEIRO;08/11/2009;Ativo
25;MARCUS VINÍCIUS ROCHA DOS SANTOS;03/11/2009;BAIXA - TRANSFERÊNCIA
26;MARIA CLARA DE ALCÂNTARA ALMEIDA;14/03/2010;Ativo
27;MARIA EDUARDA MORAES DA SILVA;03/07/2009;Transferido
28;MARIA EDUARDA VIEIRA MENDES;23/11/2009;Ativo
29;MATHEUS NEGREIROS RIBEIRO BELINELI;20/03/2010;Ativo
30;MATHEUS VIANA DOS SANTOS;23/11/2009;Ativo
31;MAYSA RIBEIRO MACIEL DOS SANTOS;09/12/2009;Ativo
32;MELISSA NASCIMENTO SILVA;01/02/2010;Ativo
33;MURILLO SILVA MAIA;17/08/2009;BAIXA - TRANSFERÊNCIA
34;NÍCOLAS JOAQUIM BADARÓ ALVES DOS SANTOS;30/09/2009;BAIXA - TRANSFERÊNCIA
35;NICOLE ALVES UCHOA;16/09/2009;Ativo
36;PEDRO HENRIQUE SILVA DA ROCHA;09/09/2009;Ativo
37;PEDRO HENRIQUE VILAS BOAS JOAQUIM;15/03/2010;BAIXA - TRANSFERÊNCIA
38;RAFAELLY FERREIRA BATISTA;04/09/2009;Ativo
39;RAPHAELA MENEZES TEMPORIM;18/03/2010;Ativo
40;SAMUEL COELHO DA COSTA;27/01/2010;Ativo
41;SOPHIA CUNHA VALENTIM;19/04/2010;Ativo
42;SOPHIA LAURA TEIXEIRA DA COSTA;02/03/2010;Ativo
43;THAINA RODRIGUES DE MORAIS SILVA;29/06/2010;Ativo
44;THIAGO LAUDELINO ALEIXO;14/08/2009;Ativo
45;VITOR WILLIAMS CORREIA;17/11/2009;BAIXA - TRANSFERÊNCIA
46;YASMIM DE ALMEIDA DUARTE;17/02/2010;Transferido
47;YASMIM MORGANA SOUSA GUERREIRO;28/02/2010;Ativo
48;YASMIN DA COSTA OLIVEIRA;21/08/2009;Transferido
49;ELOISA SILVA FERREIRA;22/12/2009;Ativo
50;LAURA RIBEIRO LARA CARDOZO;06/12/2009;Ativo
51;NICOLY ALVARES DE OLIVEIRA ROCHA;23/04/2010;BAIXA - TRANSFERÊNCIA
52;NATHALLY SILVA CARDOSO;02/07/2009;Transferido
53;RAYSSA DE OLIVEIRA MOURA;04/11/2009;Ativo
54;CAMILLA ARAUJO DA SILVA;04/02/2010;Transferido
55;DEYVID DA SILVA MELQUIADES;27/09/2009;BAIXA - TRANSFERÊNCIA
56;PIETRA FERREIRA GROBA;02/02/2010;Transferido
57;GEOVANNA COSTA SOUSA;16/12/2009;Transferido
58;EMANUELA GRAZIELLE DE SOUZA SILVA;31/10/2009;Transferido
59;RENAN CARLOS NOGUEIRA DOS SANTOS;24/03/2010;Ativo
60;PEDRO HENRIQUE DE SOUSA;31/05/2009;Transferido
61;NICOLY ALVARES DE OLIVEIRA ROCHA;23/04/2010;Ativo
62;JULIA ALVES NUNES;14/06/2010;Ativo
63;JÚLIA NOGUEIRA RAMOS;28/09/2009;Ativo
64;JHONATA NOGUEIRA FELIX;29/03/2010;Ativo
65;ARTHUR BERNARDINO SILVA DE OLIVEIRA;02/09/2009;Ativo
66;LUCAS SANTOS BATISTA;02/04/2010;Transferido
67;ISABELLA DE OLIVEIRA SANTOS SILVA;15/11/2009;Ativo
"""

    # --- AÇÃO ---
    # Chama o método de importação, passando o ID da turma e o conteúdo do CSV.
    result = data_service.import_students_from_csv(class_['id'], csv_content)
    # Salva as alterações no banco de dados de teste.
    db_session.commit()

    # --- VERIFICAÇÃO ---
    # Garante que a importação não retornou nenhum erro.
    assert not result["errors"], f"A importação falhou com erros: {result['errors']}"

    # O CSV contém 67 linhas de dados, mas alguns alunos estão duplicados.
    # O número esperado de alunos únicos é 65.
    expected_unique_students = 65

    # Verifica se o número de matrículas criadas na turma é o esperado.
    enrollments = data_service.get_enrollments_for_class(class_['id'])
    assert len(enrollments) == expected_unique_students, f"Esperado {expected_unique_students} matrículas, mas foram encontradas {len(enrollments)}"

    # Verifica se o número total de alunos no banco de dados corresponde ao número esperado.
    student_count = data_service.get_student_count()
    assert student_count == expected_unique_students, f"Esperado {expected_unique_students} alunos no BD, mas foram encontrados {student_count}"
