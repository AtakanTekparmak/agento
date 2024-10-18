import pytest
from agento.engine import execute_python_code

def test_execute_python_code_basic():
    code = "x = 5\ny = 10\nresult = x + y"
    output = execute_python_code(code)
    assert output['variables'] == {'x': 5, 'y': 10, 'result': 15}
    assert output['function_results'] == {}

def test_execute_python_code_with_function():
    def multiply(a, b):
        return a * b

    code = "result1 = multiply(3, 4)\nresult2 = multiply(5, 6)"
    output = execute_python_code(code, functions=[multiply])
    assert output['variables'] == {'result1': 12, 'result2': 30}
    assert output['function_results'] == {'multiply': [12, 30]}
