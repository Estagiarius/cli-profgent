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
from typing import List, TYPE_CHECKING
from app.core.llm.base import LLMProvider, AssistantResponse
import httpx

if TYPE_CHECKING:
    from openai import AsyncOpenAI

class OllamaProvider(LLMProvider):
    """
    Representa um provedor de LLM (Large Language Model) utilizando a API Ollama.

    Esta classe serve como um wrapper para a interação com a API Ollama, permitindo realizar
    operações como obter respostas de chat, listar modelos disponíveis, e outros. A classe é
    altamente dependente da comunicação assíncrona com a API Ollama e utiliza um cliente
    assíncrono para realizar as requisições.

    :ivar client: Instância do cliente assíncrono para comunicação com a API Ollama.
    :type client: AsyncOpenAI
    :ivar model: Nome do modelo padrão utilizado pelo provedor.
    :type model: str
    """

    def __init__(self, base_url: str = "http://localhost:11434/v1", model: str = "llama3.1"):
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key="ollama",
        )
        self.model = model

    @property
    def name(self) -> str:
        return "Ollama"

    async def get_chat_response(self, messages: list, tools: list | None = None) -> AssistantResponse:
        return await self._create_chat_completion(messages=messages, tools=tools)

    async def list_models(self) -> List[str]:
        try:
            models_response = await self.client.models.list()
            # The ollama API returns model objects, and we need the 'id' attribute
            if models_response and hasattr(models_response, 'data'):
                return sorted([model.id for model in models_response.data])
            return []
        except httpx.ConnectError:
            print(f"Could not connect to Ollama server at {self.client.base_url} to list models.")
            return []
        except Exception as e:
            # This can happen if the API exists but doesn't return a valid model list (e.g., 404)
            print(f"Error listing Ollama models (this might be normal for older versions): {e}")
            return []

    async def close(self):
        await self.client.close()
