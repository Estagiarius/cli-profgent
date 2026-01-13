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
from app.utils.format_utils import parse_float_input, format_float_output

def test_parse_float_input_with_comma():
    assert parse_float_input("7,5") == 7.5

def test_parse_float_input_with_dot():
    assert parse_float_input("7.5") == 7.5

def test_parse_float_input_integer():
    assert parse_float_input("10") == 10.0

def test_parse_float_input_invalid():
    with pytest.raises(ValueError):
        parse_float_input("abc")

def test_parse_float_input_empty():
    with pytest.raises(ValueError):
        parse_float_input("")

def test_format_float_output_simple():
    assert format_float_output(7.5) == "7,5"

def test_format_float_output_integer_float():
    # Standard Python behavior: str(7.0) -> "7.0" -> "7,0"
    assert format_float_output(7.0) == "7,0"

def test_format_float_output_precision():
    assert format_float_output(7.567, precision=2) == "7,57"

def test_format_float_output_none():
    assert format_float_output(None) == ""

def test_format_float_output_zero():
    assert format_float_output(0.0) == "0,0"
