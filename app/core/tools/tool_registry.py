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
from typing import List, Dict, Any, Callable

class ToolRegistry:
    """
    Gerenciador de ferramentas registradas.

    A classe ToolRegistry é responsável por armazenar e gerenciar funções
    ferramentas que são registradas dinamicamente. Ela também mantém os
    esquemas JSON (schemas) dessas ferramentas para facilitar a consulta.
    As funções ferramentas devem ser decoradas adequadamente para serem
    válidas e registradas no esquema.

    :ivar tools: Dicionário que associa o nome da ferramenta à função
        correspondente.
    :type tools: Dict[str, Callable]
    :ivar schemas: Lista dos esquemas JSON de todas as ferramentas
        registradas.
    :type schemas: List[Dict[str, Any]]
    """
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.schemas: List[Dict[str, Any]] = []

    def register(self, tool_func: Callable):
        """
        Registers a tool function.

        The function must be decorated with the @tool decorator to have a schema.
        """
        # Cast to Any to avoid linter errors about 'schema' attribute not existing on Callable
        func: Any = tool_func
        if not hasattr(func, 'schema'):
            raise ValueError(f"Function {func.__name__} is not a valid tool. Did you forget the @tool decorator?")

        tool_name = func.schema["function"]["name"]
        self.tools[tool_name] = func
        self.schemas.append(func.schema)
        print(f"Tool registered: {tool_name}")

    def get_tool(self, name: str) -> Callable | None:
        """Retrieves a tool function by its name."""
        return self.tools.get(name)

    def get_all_schemas(self) -> List[Dict[str, Any]]:
        """Returns the JSON schemas for all registered tools."""
        return self.schemas
