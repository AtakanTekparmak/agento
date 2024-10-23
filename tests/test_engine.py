import pytest
from agento.engine import execute_python_code

def test_execute_python_code_basic():
    code = "x = 5\ny = 10\nresult = x + y"
    output = execute_python_code(code)
    assert output['variables'] == {'x': 5, 'y': 10, 'result': 15}
    assert output['function_results'] == {}
