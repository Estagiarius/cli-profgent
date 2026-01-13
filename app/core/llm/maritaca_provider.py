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

class MaritacaProvider(LLMProvider):
    """
    An implementation of the LLMProvider for Maritaca's API,
    leveraging the async OpenAI compatibility layer.
    """

    def __init__(self, api_key: str, model: str = "sabia-3"):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://chat.maritaca.ai/api",
        )
        self.model = model

    @property
    def name(self) -> str:
        return "Maritaca"

    async def get_chat_response(self, messages: list, tools: list | None = None) -> AssistantResponse:
        return await self._create_chat_completion(messages, tools)

    async def list_models(self) -> List[str]:
        fallback_models = ["sabia-3.1", "sabia-3", "sabiazim-3"]
        try:
            models = await self.client.models.list()
            # Cast model to Any to avoid linter errors about dynamic attributes
            all_models = sorted([model.id for model in models])

            # Filter out deprecated models (e.g., sabia-2 family)
            # We keep only models that do NOT start with 'sabia-2'
            active_models = [m for m in all_models if not m.startswith("sabia-2")]

            if not active_models:
                 return fallback_models
            return active_models
        except Exception as e:
            print(f"Error listing Maritaca models: {e}")
            return fallback_models

    async def close(self):
        await self.client.close()
