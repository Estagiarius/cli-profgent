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

if TYPE_CHECKING:
    from openai import AsyncOpenAI

class OpenAIProvider(LLMProvider):
    """
    An implementation of the LLMProvider for OpenAI's API, using an async client.
    """

    def __init__(self, api_key: str, model: str = "gpt-4"):
        # Lazy import of openai
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    @property
    def name(self) -> str:
        return "OpenAI"

    async def get_chat_response(self, messages: list, tools: list | None = None) -> AssistantResponse:
        return await self._create_chat_completion(messages=messages, tools=tools)

    async def list_models(self) -> List[str]:
        try:
            models = await self.client.models.list()
            # Note: models object structure depends on openai version, keeping it simple
            return sorted([model.id for model in models.data if "gpt" in model.id])
        except Exception as e:
            print(f"Error listing OpenAI models: {e}")
            return []

    async def close(self):
        await self.client.close()
