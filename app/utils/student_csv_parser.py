# -*- coding: utf-8 -*-
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

"""
Este módulo fornece um parser determinístico para arquivos CSV de alunos,
projetado especificamente para o formato exportado por sistemas de gestão
acadêmica brasileiros.
"""

# Importa o módulo 'csv' para ler e processar arquivos CSV.
import csv
# Importa 'StringIO' para tratar uma string como se fosse um arquivo em memória.
from io import StringIO
# Importa 'datetime' para validar o formato das datas.
from datetime import datetime
# Importa tipos para anotações (type hinting), melhorando a clareza do código.
from typing import List, Dict, Optional

# Importa a função utilitária para dividir nomes completos.
from app.utils.name_parser import split_full_name


def parse_student_csv(file_content: str) -> List[Dict[str, Optional[str]]]:
    """
    Parsa o conteúdo de um arquivo CSV contendo informações de alunos, convertendo-o em uma lista
    de dicionários com dados estruturados. O CSV deve conter colunas específicas, como "Nome do
    Aluno", "Data de Nascimento" e "Situação do Aluno".

    O cabeçalho do arquivo define os campos esperados, e os dados são processados para incluir
    informações opcionais, como o primeiro e o último nome derivados do nome completo do aluno.
    Além disso, normaliza o status do aluno e valida o formato da data de nascimento.

    :param file_content: Conteúdo do arquivo CSV no formato de string.
    :return: Lista de dicionários estruturados. Cada dicionário representa um aluno e contém as
        seguintes chaves: "full_name", "birth_date", "status", "status_detail", "first_name",
        "last_name".
    """
    # Inicializa a variável que armazenará a linha do cabeçalho.
    header_line_str = None
    # Divide o conteúdo do arquivo em uma lista de linhas.
    lines = file_content.splitlines()
    # Itera sobre cada linha para encontrar a que contém o cabeçalho.
    for line in lines:
        # Assume que a linha do cabeçalho contém estas strings específicas.
        if "Nome do Aluno" in line and "Data de Nascimento" in line:
            # Armazena a linha do cabeçalho encontrada.
            header_line_str = line
            # Interrompe o loop, pois o cabeçalho foi encontrado.
            break

    # Se, após o loop, nenhum cabeçalho for encontrado, lança um erro.
    if not header_line_str:
        raise ValueError("Cabeçalho do CSV não encontrado. Verifique o formato do arquivo.")

    # Tenta encontrar a posição do bloco de dados CSV real (tudo após a linha do cabeçalho).
    try:
        # Encontra a posição inicial da string do cabeçalho.
        header_pos = file_content.index(header_line_str)
        # Encontra a posição da quebra de linha logo após o cabeçalho.
        data_pos = file_content.index('\n', header_pos) + 1
        # Extrai o bloco de texto que contém apenas os dados.
        csv_data_block = file_content[data_pos:]
    # Se ocorrer um erro (ex: não há quebra de linha após o cabeçalho), assume que não há dados.
    except ValueError:
        csv_data_block = ""

    # Se o bloco de dados estiver vazio ou contiver apenas espaços, retorna uma lista vazia.
    if not csv_data_block.strip():
        return []

    # Cria um objeto 'arquivo em memória' a partir do bloco de dados para o módulo csv.
    csv_file = StringIO(csv_data_block)

    # Mapeia os nomes das colunas do CSV para as chaves usadas internamente na aplicação.
    column_map = {
        "Nome do Aluno": "full_name",
        "Data de Nascimento": "birth_date",
        "Situação do Aluno": "status"
    }

    # Divide a linha do cabeçalho pelo delimitador ';' para obter a lista real de colunas.
    actual_headers = [h.strip() for h in header_line_str.split(';')]
    # Cria um leitor de CSV que entende o delimitador ponto e vírgula.
    reader = csv.reader(csv_file, delimiter=';')

    # Usa um dicionário para armazenar os alunos, com o nome completo como chave.
    # Isso garante que, se um aluno for encontrado novamente, seus dados serão
    # substituídos, mantendo apenas a última ocorrência (a mais recente no arquivo).
    students_dict: Dict[str, Dict[str, Optional[str]]] = {}

    # Itera sobre cada linha (row) no leitor de CSV.
    for row in reader:
        # Ignora linhas vazias ou que contenham apenas células vazias.
        if not row or all(not cell.strip() for cell in row):
            continue

        # Dicionário para armazenar as informações do aluno da linha atual.
        student_info = {}
        # Itera sobre os cabeçalhos reais para extrair os dados da linha.
        for i, header in enumerate(actual_headers):
            # Se o cabeçalho é um dos que queremos mapear.
            if header in column_map:
                # Obtém o nome da chave interna (ex: "full_name").
                key = column_map[header]
                # Obtém o valor da célula correspondente, se existir, e remove espaços.
                value = row[i].strip() if i < len(row) else None
                # Armazena o par chave-valor.
                student_info[key] = value

        # Obtém o nome completo do aluno. Se não houver, pula para a próxima linha.
        full_name = student_info.get("full_name")
        if not full_name:
            continue

        # Usa a função utilitária para dividir o nome completo em nome e sobrenome.
        first_name, last_name = split_full_name(full_name)
        # Adiciona o nome e o sobrenome ao dicionário de informações do aluno.
        student_info["first_name"] = first_name
        student_info["last_name"] = last_name

        # Normaliza o status do aluno para "Active" ou "Inactive".
        raw_status = student_info.get("status", "").upper()
        student_info["status"] = "Active" if raw_status == "ATIVO" else "Inactive"
        # Armazena o status original para referência.
        student_info["status_detail"] = student_info.get("status", "")

        # Valida o formato da data de nascimento.
        raw_date = student_info.get("birth_date")
        if raw_date:
            try:
                # Tenta converter a string para um objeto datetime. Se falhar, o formato é inválido.
                datetime.strptime(raw_date, "%d/%m/%Y")
            except ValueError:
                # Se o formato for inválido, define a data de nascimento como None.
                student_info["birth_date"] = None

        # Adiciona ou atualiza o aluno no dicionário principal, usando o nome em minúsculas como chave para evitar duplicatas.
        students_dict[full_name.lower()] = student_info

    # Retorna uma lista contendo apenas os valores (os dicionários de alunos) do dicionário principal.
    return list(students_dict.values())
