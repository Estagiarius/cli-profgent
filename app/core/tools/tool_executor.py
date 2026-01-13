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
import json
from typing import Dict, Any
from app.core.tools.tool_registry import ToolRegistry


class ToolExecutor:
    """
    Handles the secure execution of tools requested by the LLM.
    """
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def execute_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a single tool call from the LLM's response.

        Args:
            tool_call: The tool call object from the LLM (e.g., from response.tool_calls).

        Returns:
            A dictionary representing the result to be sent back to the LLM.
        """
        tool_name = tool_call['function']['name']
        tool_function = self.registry.get_tool(tool_name)

        if not tool_function:
            return self._create_error_result(tool_call['id'], f"Tool '{tool_name}' not found.")

        try:
            # Securely parse the JSON arguments string
            arguments = json.loads(tool_call['function']['arguments'])

            # Execute the tool function with the parsed arguments
            result = tool_function(**arguments)

            return self._create_success_result(tool_call['id'], tool_name, result)

        except json.JSONDecodeError:
            return self._create_error_result(tool_call['id'], "Invalid arguments format. Expected a valid JSON string.")
        except TypeError as e:
            return self._create_error_result(tool_call['id'], f"Invalid arguments for tool '{tool_name}': {e}")
        except Exception as e:
            # Catch any other unexpected errors during tool execution
            return self._create_error_result(tool_call['id'], f"An unexpected error occurred: {e}")

    @staticmethod
    def _create_success_result(tool_call_id: str, tool_name: str, result: Any) -> Dict[str, Any]:
        return {
            "tool_call_id": tool_call_id,
            "role": "tool",
            "name": tool_name,
            "content": str(result),  # Ensure the result is a string
        }

    @staticmethod
    def _create_error_result(tool_call_id: str, error_message: str) -> Dict[str, Any]:
        # Even in case of an error, we need to return a valid tool message
        # to the model so it knows the call failed.
        return {
            "tool_call_id": tool_call_id,
            "role": "tool",
            "name": "error_handler", # Generic name for errors
            "content": f"Error: {error_message}",
        }
