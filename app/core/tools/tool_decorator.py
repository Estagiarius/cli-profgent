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
import inspect
from functools import wraps

def tool(func):
    """
    Decora uma função para gerar um esquema JSON Schema com base na assinatura e no
    docstring da função. Este esquema pode ser utilizado para documentar ou validar
    os parâmetros e a descrição da função decorada.

    :param func: A função que será decorada.
    :type func: Callable
    :return: Uma função decorada, com o esquema JSON Schema gerado anexado como
    atributo `schema`.
    :rtype: Callable
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    # --- Schema Generation ---
    func_sig = inspect.signature(func)
    docstring = inspect.getdoc(func)

    # Basic function info
    schema = {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": "",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    }

    # Extract description from docstring (if available)
    if docstring:
        schema["function"]["description"] = docstring.strip().split('\n')[0]

    # Type mapping from Python to JSON Schema
    type_mapping = {
        "str": "string",
        "int": "integer",
        "float": "number",
        "bool": "boolean",
    }

    # Extract parameters
    for name, param in func_sig.parameters.items():
        param_type = "string" # Default to string
        if param.annotation is not inspect.Parameter.empty and param.annotation.__name__ in type_mapping:
            param_type = type_mapping[param.annotation.__name__]

        schema["function"]["parameters"]["properties"][name] = {
            "type": param_type,
            # In a more advanced implementation, you could parse the docstring
            # for parameter descriptions.
            "description": f"The {name} for the function."
        }

        # Check if the parameter has a default value
        if param.default is inspect.Parameter.empty:
            schema["function"]["parameters"]["required"].append(name)

    wrapper.schema = schema
    return wrapper
