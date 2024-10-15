from typing import List, Callable, Dict, Any

def execute_python_code(code: str, functions: List[Callable] = []) -> Dict[str, Any]:
    """
    Execute Python code with given functions and return the results of function calls.

    Args:
        code (str): The Python to execute.
        functions (List[Callable], optional): A list of functions to make available to the code.

    Returns:
        Dict[str, Any]: A dictionary containing the function names and their return values.
    """
    # Create an execution environment with builtins
    env = {'__builtins__': __builtins__}

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

    return call_results

