import pytest
from agento.engine import execute_python_code, process_results
from agento.client import ChatCompletionMessage, ChatMessage

def test_execute_python_code_basic():
    """Test the basic execution of Python code."""
    code = "x = 5\ny = 10\nresult = x + y"
    output = execute_python_code(code)
    assert output['variables'] == {'x': 5, 'y': 10, 'result': 15}
    assert output['function_results'] == {}

def test_execute_python_code_with_functions():
    """Test the execution of Python code with functions."""
    def add(a, b):
        return a + b
    
    def multiply(a, b):
        return a * b
    
    code = "result_add = add(3, 4)\nresult_multiply = multiply(2, 5)"
    output = execute_python_code(code, functions=[add, multiply])
    assert output['variables'] == {'result_add': 7, 'result_multiply': 10}
    assert output['function_results'] == {'add': 'result_add', 'multiply': 'result_multiply'}

def test_execute_python_code_with_context_variables():
    """Test the execution of Python code with context variables."""
    context = {'name': 'Alice', 'age': 30}
    code = "greeting = f'Hello, {name}!'\nage_next_year = age + 1"
    output = execute_python_code(code, context_variables=context)
    assert output['variables'] == {'greeting': 'Hello, Alice!', 'age_next_year': 31, 'name': 'Alice', 'age': 30}
    assert output['function_results'] == {}

def test_execute_python_code_with_functions_and_context():
    """Test the execution of Python code with functions and context variables."""
    def greet(name):
        return f"Hello, {name}!"
    
    context = {'city': 'New York'}
    code = "message = greet(name)\nlocation = f'Living in {city}'"
    output = execute_python_code(code, functions=[greet], context_variables={'name': 'Bob', **context})
    assert output['variables'] == {'message': 'Hello, Bob!', 'location': 'Living in New York', 'name': 'Bob', 'city': 'New York'}
    assert output['function_results'] == {'greet': 'message'}

def test_process_results_basic():
    """Test the processing of results without chat messages or history."""
    results = {
        'function_results': {'some_func': 'result'},
        'variables': {'x': 5, 'y': 10}
    }
    processed_results, chat_messages = process_results(results)
    assert processed_results == results
    assert chat_messages == []

def test_process_results_with_transfer_to_agent():
    """Test the processing of results with a transfer to agent."""
    results = {
        'function_results': {'transfer_to_agent': None},
        'variables': {'results': 'Task completed', 'x': 5}
    }
    processed_results, chat_messages = process_results(results)
    assert processed_results['function_results']['transfer_to_agent'] == 'Task completed'
    assert processed_results['variables'] == {'x': 5, 'results': 'Task completed'}
    assert chat_messages == []

def test_process_results_with_chat_messages():
    """Test the processing of results with chat messages."""
    chat_messages = [
        ChatMessage(sender="system", message=ChatCompletionMessage(role="system", content="System message")),
        ChatMessage(sender="user", message=ChatCompletionMessage(role="user", content="User message")),
        ChatMessage(sender="assistant", message=ChatCompletionMessage(role="assistant", content="Assistant message")),
        ChatMessage(sender="user", message=ChatCompletionMessage(role="user", content="Another user message")),
    ]
    results = {
        'function_results': {},
        'variables': {'messages': chat_messages, 'x': 5}
    }
    processed_results, extracted_messages = process_results(results)
    assert processed_results['variables'] == {'x': 5}
    assert extracted_messages == chat_messages[2:]

def test_process_results_with_history():
    """Test the processing of results with history."""
    history = [
        ChatMessage(sender="user", message=ChatCompletionMessage(role="user", content="User message")),
        ChatMessage(sender="assistant", message=ChatCompletionMessage(role="assistant", content="Assistant message")),
    ]
    results = {
        'function_results': {},
        'variables': {'history': history, 'x': 5}
    }
    processed_results, extracted_messages = process_results(results)
    assert processed_results['variables'] == {'x': 5}
    assert extracted_messages == []  # Expecting an empty list of extracted messages
    assert 'history' not in processed_results['variables']  # Ensure history is removed from variables

def test_process_results_with_invalid_input():
    """Test the processing of results with invalid input."""
    with pytest.raises(ValueError):
        process_results({'invalid': 'input'})