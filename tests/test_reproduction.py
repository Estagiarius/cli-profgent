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
from unittest.mock import MagicMock
from app.core.tools.tool_executor import ToolExecutor

# Mock the ChatCompletionMessageToolCall object structure
class MockToolCall:
    def __init__(self, call_id, name, arguments):
        self.call_id = call_id
        self.function = MagicMock()
        self.function.name = name
        self.function.arguments = arguments

    # Simulate it NOT being subscriptable
    def __getitem__(self, key):
        raise TypeError("'MockToolCall' object is not subscriptable")

def test_execute_tool_call_with_object_fails():
    registry = MagicMock()
    executor = ToolExecutor(registry)

    # Create a tool call that mimics the OpenAI object
    tool_call_object = MockToolCall(call_id="call_123", name="test_tool", arguments='{}')

    # Expect failure because ToolExecutor expects a dict
    with pytest.raises(TypeError, match="'MockToolCall' object is not subscriptable"):
        # We need to cast to Any or ignore type hint because we are intentionally passing the wrong type
        executor.execute_tool_call(tool_call_object)

def test_execute_tool_call_with_dict_succeeds():
    registry = MagicMock()
    tool_func = MagicMock(return_value="Success")
    registry.get_tool.return_value = tool_func

    executor = ToolExecutor(registry)

    tool_call_dict = {
        "id": "call_123",
        "function": {
            "name": "test_tool",
            "arguments": '{}'
        },
        "type": "function"
    }

    result = executor.execute_tool_call(tool_call_dict)
    assert result["content"] == "Success"
