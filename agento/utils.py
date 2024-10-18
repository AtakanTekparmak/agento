import re
from typing import List, Callable, Any, Tuple
import inspect
import json

from agento.settings import SYSTEM_PROMPT_PATH

def extract_python_code(content: str) -> Tuple[str, bool]:
    """
    Extracts Python code from the given content.

    Args:
        content (str): The content to extract Python code from.

    Returns:
        Tuple[str, bool]: A tuple containing the extracted Python code and a boolean indicating if extraction was successful.
    """
    # Extract Python code from markdown code blocks
    pattern = r'```python\n(.*?)\n```'
    matches = re.findall(pattern, content, re.DOTALL)
    if matches:
        return '\n'.join(matches), True
    else:
        return '', False

def create_functions_schema(functions: List[Callable]) -> str:
    """
    Creates the functions schema for the prompt.
    """
    functions_schema = []
    for function in functions:
        name = function.__name__
        try:
            annotations = function.__annotations__
            parameters = {
                param: annotations.get(param, Any).__name__
                for param in inspect.signature(function).parameters
                if param != 'return'
            }
            returns = annotations.get('return', Any).__name__
            
            metadata = {
                "name": name,
                "description": function.__doc__.replace('\\n', '\n') if function.__doc__ else "",
                "parameters": {"properties": parameters, "required": list(parameters.keys())},
                "returns": returns
            }
            functions_schema.append(metadata)
        except Exception as e:
            print(f"Error creating metadata for function {name}: {str(e)}")

    return json.dumps(functions_schema, indent=2, ensure_ascii=False)

def load_system_prompt(
        functions_schema: str = "",
        instructions: str = "",
        is_orchestrator: bool = False,
        file_path: str = SYSTEM_PROMPT_PATH
    ) -> str:
    """
    Loads the system prompt from the specified file.
    """
    def replace_functions_schema(content: str) -> str:
        return content.replace("{{functions_schema}}", functions_schema)
    
    def replace_instructions(content: str) -> str:
        return content.replace("{{instructions}}", instructions)
    
    def replace_prompt_beginning(content: str) -> str:
        if is_orchestrator:
            return content.replace(
                "{{prompt_beginning}}", 
                "You are an expert orchestrator AI assistant that specializes in providing Python code to solve the task/problem at hand provided by the user and/or transfer the task to the appropriate team member."
            )
        else:
            return content.replace(
                "{{prompt_beginning}}", 
                "You are an expert AI assistant that specializes in providing Python code to solve the task/problem at hand provided by the user.."
            )
    
    try:
        with open(file_path, "r") as file:
            return replace_instructions(
                replace_functions_schema(
                    replace_prompt_beginning(file.read())
                )
            )
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return ""