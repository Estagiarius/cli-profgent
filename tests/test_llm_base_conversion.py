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

import pytest
from unittest.mock import AsyncMock, MagicMock
from app.core.llm.base import LLMProvider, AssistantResponse

class TestProvider(LLMProvider):
    @property
    def name(self):
        return "Test"

    async def get_chat_response(self, messages, tools=None):
        pass

    async def list_models(self):
        pass

@pytest.mark.anyio
async def test_create_chat_completion_converts_tool_calls():
    # Setup
    provider = TestProvider()
    provider.client = MagicMock()

    # Mock response from OpenAI client
    mock_response = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "Thinking..."

    # Create mock tool call object that is NOT a dict but has model_dump
    mock_tool_call = MagicMock()
    mock_tool_call.model_dump.return_value = {"id": "call_1", "type": "function"}
    # Simulate that it is NOT subscriptable to prove the conversion happens
    mock_tool_call.__getitem__ = MagicMock(side_effect=TypeError("Not subscriptable"))

    mock_message.tool_calls = [mock_tool_call]
    mock_response.choices = [MagicMock(message=mock_message)]

    # Mock the create method to return the response
    provider.client.chat.completions.create = AsyncMock(return_value=mock_response)

    # Execute
    response = await provider._create_chat_completion(messages=[])

    # Verify
    assert isinstance(response, AssistantResponse)
    assert response.tool_calls is not None
    assert len(response.tool_calls) == 1
    assert isinstance(response.tool_calls[0], dict)
    assert response.tool_calls[0]["id"] == "call_1"

    # Verify model_dump was called
    mock_tool_call.model_dump.assert_called_once()

@pytest.mark.anyio
async def test_create_chat_completion_handles_no_tool_calls():
    # Setup
    provider = TestProvider()
    provider.client = MagicMock()

    # Mock response with no tool calls
    mock_response = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "Hello"
    mock_message.tool_calls = None
    mock_response.choices = [MagicMock(message=mock_message)]

    provider.client.chat.completions.create = AsyncMock(return_value=mock_response)

    # Execute
    response = await provider._create_chat_completion(messages=[])

    # Verify
    assert response.content == "Hello"
    assert response.tool_calls is None
