from typing import List, Callable, Dict, Any

from agento.client import ChatMessage

def execute_python_code(
        code: str, 
        functions: List[Callable] = [],
        context_variables: Dict[str, Any] = {},
    ) -> Dict[str, Any]:
    """
    Execute Python code with given functions and context variables,
    and return the results of function calls and variables defined in the code.
    
    Args:
        code (str): The Python code to execute.
        functions (List[Callable], optional): A list of functions to make available to the code.
        context_variables (Dict[str, Any], optional): Variables to make available to the code.
    
    Returns:
        Dict[str, Any]: A dictionary containing the function results and variables defined in the code.
    """
    # Create an execution environment with built-ins
    env = {'__builtins__': __builtins__}
    
    # Record the initial environment keys before adding context variables and functions
    initial_keys = set(env.keys())
    
    # Add the context variables to the execution environment, add them as variables
    if context_variables:
        for key, value in context_variables.items():
            env[key] = value
    
    # A dictionary to store function call results
    call_results = {}
    
    # Wrap the functions to capture their return values
    def make_wrapper(func_name, func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            # Append the result to the list for this function
            call_results.setdefault(func_name, []).append(result)
            return result
        return wrapper
    
    # Add the wrapped functions to the execution environment
    for func in functions:
        env[func.__name__] = make_wrapper(func.__name__, func)
    
    # Execute the code
    exec(code, env)
    
    # Extract variables defined in the code, excluding built-ins, context variables, and wrapped functions
    variables = {
        k: v for k, v in env.items()
        if k not in initial_keys and not k.startswith('__') and not callable(v)
    }
    
    # Match the call results with the variable names
    for func_name, results in call_results.items():
        for variable_name, variable_value in variables.items():
            for result in results:
                if variable_value == result:
                    call_results[func_name] = variable_name
    
    # Return both call_results and variables
    return {'function_results': call_results, 'variables': variables}

def process_results(results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process the results of a function call session to remove the history from the results
    and remove any list of ChatMessages from the variables.

    Args:
        results (Dict[str, Any]): The results of a function call session.
    
    Returns:
        Dict[str, Any]: The processed results.
    """
    def is_list_of_chat_messages(obj: Any) -> bool:
        """
        Check if the object is a list of ChatMessages or is a tuple of (str, list[ChatMessage]).

        Args:
            obj (Any): The object to check.
        
        Returns:
            bool: True if the object is a list of ChatMessages or a tuple of (str, list[ChatMessage]), False otherwise.
        """
        return (
            isinstance(obj, list) and
            all(isinstance(item, ChatMessage) for item in obj)
        ) or (
            isinstance(obj, tuple) and
            len(obj) == 2 and
            isinstance(obj[0], str) and
            isinstance(obj[1], list) and
            all(isinstance(item, ChatMessage) for item in obj[1])
        )
    
    if not "function_results" in results or not "variables" in results:
        raise ValueError("Results must contain 'function_results' and 'variables' keys.")
    
    # Check if function_results has the key 'transfer_to_agent'
    if 'transfer_to_agent' in results["function_results"]:
        if "results" in results["variables"]:
            results["function_results"]["transfer_to_agent"] = results["variables"]["results"]
        else:
            results["function_results"]["transfer_to_agent"] = "Transfer task result"

    # Remove the history from the results
    results["variables"] = {k: v for k, v in results["variables"].items() if k != 'history'}
    results["variables"] = {k: v for k, v in results["variables"].items() if not is_list_of_chat_messages(v)}   

    return results