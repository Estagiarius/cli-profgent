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
from openai import AsyncOpenAI
from app.core.llm.base import LLMProvider, AssistantResponse
from typing import List


class OpenAIProvider(LLMProvider):
    """
    An implementation of the LLMProvider for OpenAI's API, using an async client.
    """

    def __init__(self, api_key: str, model: str = "gpt-4"):
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
            return sorted([model.id for model in models if "gpt" in model.id])  # type: ignore
        except Exception as e:
            print(f"Error listing OpenAI models: {e}")
            return []

    async def close(self):
        await self.client.close()
