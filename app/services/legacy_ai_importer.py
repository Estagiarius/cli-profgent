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
Este módulo contém a lógica de importação de alunos via CSV que foi desativada.

A abordagem original utilizava um provedor de Large Language Model (LLM) para
analisar o conteúdo de arquivos CSV e extrair de forma inteligente os dados
dos alunos, incluindo a complexa tarefa de dividir nomes completos em nome e
sobrenome.

-------------------------------------------------------------------------------
Visão Geral da Lógica Antiga
-------------------------------------------------------------------------------
1.  **`parse_student_csv_with_ai`**:
    -   Esta função recebia o conteúdo de texto de um arquivo CSV.
    -   Ela enviava o texto completo para a IA com um prompt detalhado,
        solicitando a extração dos dados dos alunos.
    -   A expectativa era que a IA retornasse uma string JSON contendo uma
        lista de dicionários, cada um representando um aluno com os campos
        'full_name', 'first_name', 'last_name', 'birth_date', e 'status'.

2.  **`split_full_name` (Função Auxiliar)**:
    -   Originalmente, o plano era processar o CSV linha por linha, e esta
        função seria chamada para cada nome de aluno.
    -   Ela enviava um único nome completo para a IA e pedia a divisão em
        nome e sobrenome, retornando um JSON.
    -   Esta abordagem se mostrou muito lenta devido à alta latência de
        múltiplas chamadas de rede.

-------------------------------------------------------------------------------
Motivo da Desativação
-------------------------------------------------------------------------------
A importação baseada em IA foi desativada por duas razões principais:

1.  **Falta de Confiabilidade**: O provedor de IA nem sempre retornava um
    JSON válido. Muitas vezes, a resposta incluía texto conversacional
    adicional (e.g., "Aqui está o JSON que você pediu: ```json...```"), o
    que causava falhas na análise do JSON. Além disso, a IA por vezes
    "alucinava" dados incorretos, como datas de nascimento inválidas.

2.  **Performance e Custo**: A abordagem de fazer uma chamada de API para cada
    aluno (`split_full_name`) era inviável em termos de velocidade. A abordagem
    de enviar o arquivo inteiro (`parse_student_csv_with_ai`) era mais rápida,
    mas ainda significativamente mais lenta e mais cara (em termos de uso de API)
    do que uma solução determinística.

A funcionalidade foi substituída por um parser determinístico localizado em
`app/utils/student_csv_parser.py` que utiliza uma lógica baseada em uma lista
de nomes compostos comuns para alcançar um resultado mais rápido e confiável.
"""
# Importa o módulo 'json' para trabalhar com dados no formato JSON.
import json

# As dependências abaixo seriam necessárias se este código estivesse ativo.
# from app.core.llm.base import LLMProvider


# Define uma classe para encapsular a lógica antiga de parsing de CSV com IA.
class LegacyAiCsvParser:
    """
    Classe para parsing de nomes e análise de conteúdo CSV com suporte a IA.

    A classe oferece métodos para dividir nomes completos em nome e sobrenome,
    e para analisar conteúdo de arquivo CSV utilizando um provedor de
    Large Language Models (LLM). Há suporte para estratégias de fallback
    em casos de erro ao utilizar o serviço de IA.

    :ivar provider: Instância do provedor de IA utilizado para consultas.
    """
    # Método construtor da classe.
    def __init__(self, provider):
        """
        Inicializa o parser com um provedor de IA.

        Args:
            provider (LLMProvider): Uma instância de um provedor de LLM.
        """
        # Armazena a instância do provedor de LLM.
        self.provider = provider

    # Método assíncrono para dividir um nome completo em nome e sobrenome.
    async def split_full_name(self, full_name: str) -> tuple[str, str]:
        """
        (Desativado) Divide um nome completo em nome e sobrenome usando IA.
        """
        # Define uma função simples de fallback para dividir o nome.
        def simple_split(name):
            # Divide o nome em palavras.
            parts = name.split()
            # Retorna a primeira palavra como nome e o resto como sobrenome.
            return parts[0], " ".join(parts[1:])

        # Se não houver provedor ou nome, usa a divisão simples.
        if not self.provider or not full_name:
            return simple_split(full_name)

        # Bloco try/except para capturar possíveis erros durante a chamada da API.
        try:
            # Cria o prompt (instrução) para a IA.
            prompt = (
                "Você é um especialista linguístico especializado em nomes brasileiros. "
                "Sua tarefa é separar um nome completo em nome e sobrenome. "
                "O nome pode ser composto (ex: 'Ana Julia', 'Maria Clara'). "
                "Responda apenas com um objeto JSON com duas chaves: 'first_name' e 'last_name'.\\n\\n"
                f'Nome completo: \\"{full_name}\\"'
            )
            # Prepara a mensagem para ser enviada ao provedor de IA.
            messages = [{"role": "user", "content": prompt}]
            # Chama o provedor de IA para obter a resposta.
            response = await self.provider.get_chat_response(messages)

            # Se a resposta tiver conteúdo.
            if response.content:
                try:
                    # Tenta converter a resposta de string JSON para um dicionário Python.
                    name_parts = json.loads(response.content)
                    # Extrai o nome e o sobrenome do dicionário.
                    first_name = name_parts.get('first_name')
                    last_name = name_parts.get('last_name')
                    # Se ambos foram extraídos com sucesso, retorna os valores.
                    if first_name and last_name:
                        return first_name, last_name
                # Captura erros se a resposta não for um JSON válido ou não tiver as chaves esperadas.
                except (json.JSONDecodeError, KeyError):
                    print(f"A resposta da IA para a divisão do nome não era um JSON válido: {response.content}")

        # Captura qualquer outra exceção que possa ocorrer.
        except Exception as e:
            print(f"Ocorreu um erro durante a divisão de nome pela IA: {e}")

        # Se a IA falhar, retorna o resultado da divisão simples como fallback.
        return simple_split(full_name)

    # Método assíncrono para analisar o conteúdo completo de um CSV usando IA.
    async def parse_student_csv_with_ai(self, csv_content: str) -> list[dict]:
        """
        (Desativado) Usa uma única chamada de IA para analisar o conteúdo de um CSV.
        """
        # Lança um erro se o provedor de IA não estiver configurado.
        if not self.provider:
            raise RuntimeError("O provedor de IA não está configurado.")

        # Cria o prompt para a IA (o prompt completo foi omitido por brevidade no arquivo original).
        prompt = (
            "Você é um assistente especialista em extração de dados. Analise o seguinte texto... "
            f'"""{csv_content}"""'
        )
        # Prepara a mensagem para ser enviada.
        messages = [{"role": "user", "content": prompt}]

        try:
            # Obtém a resposta da IA.
            response = await self.provider.get_chat_response(messages)

            # Verifica se a resposta está vazia.
            if not response or not response.content:
                raise RuntimeError("O provedor de IA retornou uma resposta vazia.")

            # Verifica se a resposta é uma mensagem de erro do próprio provedor.
            if response.content.strip().startswith("Error:"):
                raise RuntimeError(f"O provedor de IA relatou um erro: {response.content.strip()}")

            # Limpa a string de resposta, removendo marcações de bloco de código que a IA às vezes adiciona.
            cleaned_json_str = response.content.strip().replace("```json", "").replace("```", "").strip()

            # Verifica se a string limpa ficou vazia.
            if not cleaned_json_str:
                raise RuntimeError("O provedor de IA retornou uma string JSON vazia.")

            # Converte a string JSON limpa em uma lista de dicionários Python e a retorna.
            return json.loads(cleaned_json_str)
        # Captura erro de decodificação de JSON.
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Falha ao analisar CSV com IA: Formato JSON inválido. Erro: {e}") from e
        # Captura qualquer outro erro inesperado.
        except Exception as e:
            raise RuntimeError(f"Ocorreu um erro inesperado ao analisar CSV com IA: {e}") from e
