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
Este módulo fornece funcionalidades para análise e divisão de nomes completos em
primeiro nome e sobrenome, com suporte especial para nomes compostos comuns no Brasil.
"""

# Lista dos 100 nomes compostos mais comuns no Brasil.
# Fontes:
# - https://www.pampers.com.br/gravidez/nomes-para-o-bebe/artigo/nomes-compostos-para-meninos-e-meninas
# - https://bebe.abril.com.br/nomes-de-bebe/100-nomes-compostos-para-meninas/
# - https://bebe.abril.com.br/nomes-de-bebe/50-nomes-compostos-para-meninos/
# A lista foi compilada e normalizada para maiúsculas para consistência.
COMMON_COMPOUND_NAMES = [
    "ANA BEATRIZ", "ANA CAROLINA", "ANA CLARA", "ANA JULIA", "ANA LAURA", "ANA LUIZA",
    "ANNE GABRIELLY", "ANTONIO CARLOS", "BRUNO HENRIQUE", "CAIO ALEXANDRE",
    "CARLOS ALBERTO", "CARLOS EDUARDO", "CARLOS HENRIQUE", "DAVI LUCAS", "DAVI LUIZ",
    "ENZO GABRIEL", "ENZO MIGUEL", "ERICK GABRIEL", "FERNANDA CATARINA", "FRANCISCO JOSE",
    "GABRIEL HENRIQUE", "GUSTAVO HENRIQUE", "HEITOR GABRIEL", "HELENA BEATRIZ",
    "HENRIQUE GABRIEL", "IGOR GABRIEL", "JOAO AUGUSTO", "JOAO BATISTA", "JOAO CARLOS",
    "JOAO FELIPE", "JOAO GABRIEL", "JOAO GUILHERME", "JOAO HENRIQUE", "JOAO LUCAS",
    "JOAO LUIZ", "JOAO MARCOS", "JOAO MIGUEL", "JOAO PAULO", "JOAO PEDRO", "JOAO VITOR",
    "JOSE CARLOS", "JOSE HENRIQUE", "JOSE LUIZ", "JOSE MIGUEL", "JUAN GUILHERME",
    "JULIA BEATRIZ", "JULIA GABRIELA", "JULIA VITORIA", "KAUA GABRIEL", "LAURA BEATRIZ",
    "LAURA SOFIA", "LORENZO GABRIEL", "LUCAS GABRIEL", "LUCAS HENRIQUE", "LUIZ ANTONIO",
    "LUIZ CARLOS", "LUIZ EDUARDO", "LUIZ FELIPE", "LUIZ FERNANDO", "LUIZ GUSTAVO",
    "LUIZ HENRIQUE", "LUIZ MIGUEL", "LUIZA HELENA", "MARCELA VITORIA", "MARCO ANTONIO",
    "MARCOS PAULO", "MARIA ALICE", "MARIA ANTONIA", "MARIA BEATRIZ", "MARIA CECILIA",
    "MARIA CLARA", "MARIA EDUARDA", "MARIA FERNANDA", "MARIA FLOR", "MARIA HELENA",
    "MARIA ISABEL", "MARIA JULIA", "MARIA LAURA", "MARIA LUIZA", "MARIA VALENTINA",
    "MARIA VITORIA", "MIGUEL HENRIQUE", "NICOLAS GABRIEL", "PAULO ANDRE", "PAULO CESAR",
    "PAULO HENRIQUE", "PAULO RICARDO", "PAULO ROBERTO", "PAULO SERGIO", "PAULO VICTOR",
    "PEDRO AFONSO", "PEDRO ARTHUR", "PEDRO AUGUSTO", "PEDRO DANIEL", "PEDRO ENRIQUE",
    "PEDRO GABRIEL", "PEDRO HENRIQUE", "PEDRO LUCAS", "PEDRO MIGUEL", "PIETRO GABRIEL",
    "RYAN GABRIEL", "VICTOR HUGO", "VITOR GABRIEL", "YASMIN VITORIA", "YURI GABRIEL"
]


def split_full_name(full_name, compound_names_list=None):
    """
    Divide um nome completo em primeiro nome e sobrenome. Este método leva em consideração
    uma lista pré-definida de nomes compostos para identificar corretamente os nomes que
    devem ser tratados como um único primeiro nome. Caso nenhum nome composto seja identificado,
    o nome é dividido com base no primeiro espaço encontrado.

    :param full_name: O nome completo a ser dividido.
    :type full_name: str
    :param compound_names_list: Uma lista opcional de nomes compostos para auxiliar
        na divisão dos nomes. Se não fornecida, será usada uma lista padrão.
    :type compound_names_list: list[str], optional
    :return: Uma tupla contendo o primeiro nome e o sobrenome correspondentes.
    :rtype: tuple[str, str]
    """
    # Define a lista padrão de nomes compostos se nenhuma for fornecida.
    # Isso evita o problema de usar um argumento padrão mutável.
    if compound_names_list is None:
        compound_names_list = COMMON_COMPOUND_NAMES
    # Se o nome completo for nulo ou vazio, retorna duas strings vazias.
    if not full_name:
        return "", ""

    # Converte o nome completo para maiúsculas para uma comparação sem distinção de caso.
    full_name_upper = full_name.upper()

    # Itera sobre cada nome composto na lista de nomes comuns.
    for compound_name in compound_names_list:
        # Verifica se o nome completo (em maiúsculas) começa com o nome composto seguido de um espaço.
        # O espaço é importante para evitar correspondências parciais (ex: "ANA" em "ANABELA").
        if full_name_upper.startswith(compound_name + " "):
            # Se encontrou um nome composto correspondente, calcula onde ele termina.
            first_name_end_index = len(compound_name)
            # Extrai o primeiro nome do nome completo original, preservando a capitalização original.
            first_name = full_name[:first_name_end_index]
            # Extrai o restante da string como o sobrenome e remove espaços em branco extras.
            last_name = full_name[first_name_end_index:].strip()
            # Retorna o nome e o sobrenome encontrados.
            return first_name, last_name

    # Se o loop terminar sem encontrar um nome composto, usa a lógica padrão.
    # Divide o nome completo em palavras com base nos espaços.
    parts = full_name.split(" ")
    # A primeira palavra é considerada o primeiro nome.
    first_name = parts[0]
    # Todas as palavras restantes são juntadas para formar o sobrenome.
    last_name = " ".join(parts[1:]).strip()

    # Retorna o resultado da divisão padrão.
    return first_name, last_name
