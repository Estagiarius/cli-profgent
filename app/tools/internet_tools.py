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
# Importa a biblioteca 'requests' para fazer requisições HTTP (acessar sites).
import requests
# Importa a biblioteca 'BeautifulSoup' para fazer parsing (análise) de HTML e extrair informações.
from bs4 import BeautifulSoup
# Importa o decorador 'tool' para registrar a função como uma ferramenta de IA.
from app.core.tools.tool_decorator import tool

# Registra a função como uma ferramenta disponível para a IA.
@tool
def search_internet(query: str) -> str:
    """
    Busca por resultados na internet utilizando a engine de busca DuckDuckGo, retorna
    resumos curtos ou links correspondentes à consulta do usuário.

    Esta função realiza uma requisição HTTP para a interface HTML da página de busca
    do DuckDuckGo. Em seguida, processa o conteúdo da resposta com o BeautifulSoup
    para identificar e extrair os títulos, resumos e links relevantes dos resultados de
    pesquisa. Caso a estrutura da resposta HTML não seja conforme esperado, são adotados
    métodos de fallback para garantir que ao menos links sejam retornados.

    Lida com erros relacionados a rede, como ausência de conexão ou alterações na
    estrutura HTML da página.

    :param query: Texto da consulta de busca.
    :type query: str
    :return: Uma string contendo os resultados da consulta, que pode incluir títulos,
        resumos, e links associados. Caso nenhum resultado seja encontrado ou haja um
        erro, uma mensagem informativa será retornada.
    :rtype: str
    """
    # Bloco try/except para lidar com erros de rede ou de parsing.
    try:
        # Define um cabeçalho 'User-Agent' para simular um navegador e evitar ser bloqueado.
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        # Monta a URL de busca do DuckDuckGo com a consulta do usuário.
        # Normaliza a query para evitar problemas com caracteres especiais
        url = f"https://html.duckduckgo.com/html/?q={query}"

        # Faz a requisição GET para a URL, com os cabeçalhos e um timeout de 10 segundos (aumentado para robustez).
        response = requests.get(url, headers=headers, timeout=10)
        # Lança uma exceção se a resposta tiver um código de status de erro (ex: 404, 500).
        response.raise_for_status()

        # Cria um objeto BeautifulSoup para analisar o conteúdo HTML da resposta.
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extrai os "snippets" (resumos dos resultados) da página de resultados do DuckDuckGo.
        # A estrutura do DDQ HTML pode mudar, então tentamos ser mais abrangentes.
        # A classe 'result__snippet' costuma conter o texto do resumo.
        results = []

        # Tenta encontrar os containers de resultado
        result_elements = soup.find_all('div', class_='result')

        if not result_elements:
             # Fallback para links diretos se a estrutura de div não for encontrada
             result_elements = soup.find_all('a', class_='result__a')

        for i, element in enumerate(result_elements[:4]): # Aumentado para 4 resultados
            title = ""
            snippet_text = ""
            link = ""

            # Tenta extrair título e snippet de dentro do container
            title_elem = element.find('a', class_='result__a')
            snippet_elem = element.find('a', class_='result__snippet')

            # Se encontrou o elemento 'a' diretamente (fallback)
            if element.name == 'a':
                title = element.get_text(strip=True)
                link = element.get('href', '')
                # Tenta achar o snippet adjacente ou dentro
                snippet_elem = element.find_next('a', class_='result__snippet')
            elif title_elem:
                 title = title_elem.get_text(strip=True)
                 link = title_elem.get('href', '')

            if snippet_elem:
                snippet_text = snippet_elem.get_text(strip=True)

            # Se tivermos pelo menos um título ou snippet
            if title or snippet_text:
                results.append(f"**{title}**\n{snippet_text}\nLink: {link}\n")

        # Se nenhum resultado for encontrado.
        if not results:
            # Tenta uma extração bruta de texto de links se a estrutura falhar
            raw_links = soup.find_all('a', class_='result__a')
            if raw_links:
                for link in raw_links[:3]:
                    results.append(f"- {link.get_text(strip=True)} ({link.get('href')})")
            else:
                return "Nenhum resultado de busca encontrado ou estrutura da página mudou."

        return "\n".join(results)

    # Captura erros relacionados a requisições de rede (ex: sem conexão, timeout).
    except requests.RequestException as e:
        return f"Erro de conexão durante a busca na web: {e}"
    # Captura qualquer outro erro inesperado.
    except Exception as e:
        return f"Ocorreu um erro inesperado durante a busca: {e}"
