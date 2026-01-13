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
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any
import httpx


@dataclass
class AssistantResponse:
    """
    Representa uma resposta de um assistente, contendo o conteúdo textual
    da resposta gerada, além de possíveis chamadas de ferramentas realizadas
    pelo assistente.

    A classe organiza as informações retornadas pelo assistente em dois
    atributos principais. O atributo `content` contém a mensagem textual
    produzida, enquanto o atributo `tool_calls` representa uma lista de
    chamadas de ferramentas, caso tenham ocorrido durante o processo de
    resposta. É possível que `tool_calls` seja None, caso nenhuma chamada
    de ferramenta tenha sido feita.

    :ivar content: Conteúdo textual da resposta gerada pelo assistente.
                   Contém o texto principal retornado.
    :type content: str
    :ivar tool_calls: Lista de dicionários representando chamadas de
                      ferramentas realizadas ou None, caso não existam
                      chamadas de ferramenta.
    :type tool_calls: List[Dict[str, Any]] | None
    """
    content: str
    tool_calls: List[Dict[str, Any]] | None = None


class LLMProvider(ABC):
    """
    Representa uma abstração de um provedor de modelos de linguagem.

    Fornece métodos e atributos necessários para interação com modelos de linguagem
    e manipulação de respostas em aplicações baseadas em inteligência artificial.

    :ivar client: Cliente utilizado para realizar interações com o provedor.
    :type client: Any
    :ivar model: Modelo atualmente selecionado para geração de respostas.
    :type model: str
    """
    client: Any = None
    model: str = ""

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Returns the name of the provider (e.g., 'OpenAI').
        """
        pass

    async def _create_chat_completion(self, messages: list, tools: list | None = None) -> AssistantResponse:
        """
        A helper method to create a chat completion and handle common exceptions.
        """
        # Note: self.client and self.model are expected to be set by subclasses.
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto" if tools else None,
            )

            message = response.choices[0].message
            content = message.content or ""

            # Convert tool_calls objects (Pydantic models) to dictionaries
            tool_calls = None
            if message.tool_calls:
                tool_calls = []
                for tc in message.tool_calls:
                    if hasattr(tc, 'model_dump'):
                        tool_calls.append(tc.model_dump())
                    elif hasattr(tc, 'dict'):
                        tool_calls.append(tc.dict())
                    else:
                        tool_calls.append(tc)

            return AssistantResponse(content=content, tool_calls=tool_calls)

        except httpx.ConnectError:
            error_message = (
                f"Could not connect to {self.name} server at {getattr(self.client, 'base_url', 'unknown URL')}. "
                f"Is the service running?"
            )
            print(error_message)
            return AssistantResponse(content=error_message)
        except Exception as e:
            error_message = f"An error occurred with the {self.name} API: {e}"
            print(error_message)
            return AssistantResponse(content=error_message)

    @abstractmethod
    async def get_chat_response(self, messages: list, tools: list | None = None) -> AssistantResponse:
        """
        Asynchronously obtains a chat response from the model.
        """
        pass

    @abstractmethod
    async def list_models(self) -> List[str]:
        """
        Asynchronously retrieves a list of available model names from the provider.
        """
        pass

    async def close(self):
        """
        Asynchronously closes any open resources, like network clients.
        """
        pass
