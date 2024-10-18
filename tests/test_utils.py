import pytest
from agento.utils import extract_python_code, create_functions_schema, load_system_prompt

def test_extract_python_code():
    content = "Some text\n```python\nx = 10\ny = 20\nprint(x + y)\n```\n"
    expected_code = "x = 10\ny = 20\nprint(x + y)"
    code, success = extract_python_code(content)
    assert success == True
    assert code.strip() == expected_code.strip()

    # Test with no Python code
    content_no_code = "This is just plain text"
    code, success = extract_python_code(content_no_code)
    assert success == False
    assert code == ""

def test_create_functions_schema():
    def test_function(param1: int, param2: str) -> bool:
        """This is a test function."""
        pass

    schema = create_functions_schema([test_function])
    assert isinstance(schema, str)
    assert "test_function" in schema
    assert "This is a test function" in schema
    assert "param1" in schema
    assert "param2" in schema
    assert "int" in schema
    assert "str" in schema
    assert "bool" in schema

@pytest.fixture
def mock_system_prompt_file(tmp_path):
    content = """{{prompt_beginning}}
{{instructions}}
{{functions_schema}}"""
    file = tmp_path / "system_prompt.txt"
    file.write_text(content)
    return file

def test_load_system_prompt(mock_system_prompt_file):
    functions_schema = '{"function": "test"}'
    instructions = "Test instructions"
    
    # Test regular assistant
    prompt = load_system_prompt(
        functions_schema=functions_schema,
        instructions=instructions,
        is_orchestrator=False,
        file_path=str(mock_system_prompt_file)
    )
    assert "You are an expert AI assistant" in prompt
    assert instructions in prompt
    assert functions_schema in prompt

    # Test orchestrator
    prompt = load_system_prompt(
        functions_schema=functions_schema,
        instructions=instructions,
        is_orchestrator=True,
        file_path=str(mock_system_prompt_file)
    )
    assert "You are an expert orchestrator AI assistant" in prompt
    assert instructions in prompt
    assert functions_schema in prompt