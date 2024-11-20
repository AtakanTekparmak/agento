from typing import List, Callable, Dict, Any, Tuple

from agento.client import ChatMessage

def execute_python_code(
        code: str, 
        functions: List[Callable] = [],
        context_variables: Dict[str, Any] = {},
        safe: bool = False
    ) -> Dict[str, Any]:
    """
    Execute Python code with given functions and context variables,
    and return the results of function calls and variables defined in the code.
    
    Args:
        code (str): The Python code to execute.
        functions (List[Callable], optional): A list of functions to make available to the code.
        context_variables (Dict[str, Any], optional): Variables to make available to the code.
        safe (bool, optional): Whether to sandbox the execution environment by restricting dangerous builtins.
    
    Returns:
        Dict[str, Any]: A dictionary containing the function results, variables defined in the code, and any errors.
    """
    # Define dangerous builtins to restrict
    dangerous_builtins = [
        'exec', 'eval', 'execfile', 'compile', 
        'importlib', '__import__', 'input'
    ]
    
    # Create an execution environment
    env = {'__builtins__': __builtins__}
    
    # If sandboxing is enabled, restrict dangerous builtins
    if safe:
        env['__builtins__'] = {k: v for k, v in __builtins__.__dict__.items() if k not in dangerous_builtins}
    
    # Record the initial environment keys
    initial_keys = set(env.keys())
    
    # Add context variables to the execution environment
    if context_variables and isinstance(context_variables, dict):
        env.update(context_variables)
    
    # A dictionary to store function call results
    call_results = {}
    
    # Wrap the functions to capture their return values
    def make_wrapper(func_name, func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            call_results.setdefault(func_name, []).append(result)
            return result
        return wrapper
    
    # Add the wrapped functions to the execution environment
    for func in functions:
        env[func.__name__] = make_wrapper(func.__name__, func)
    
    # Execute the code and catch any exceptions
    errors = []
    try:
        exec(code, env)
    except Exception as e:
        errors.append(str(e))
    
    # Extract variables defined in the code
    variables = {
        k: v for k, v in env.items()
        if k not in initial_keys and not k.startswith('__') and not callable(v)
    }
    
    # Match the call results with the variable names
    for func_name, results in list(call_results.items()):
        for variable_name, variable_value in variables.items():
            for result in results:
                if variable_value == result:
                    call_results[func_name] = variable_name
                    break
    
    # Return function results, variables, and any errors
    return {
        'function_results': call_results, 
        'variables': variables, 
        'errors': errors
    }

def process_results(results: Dict[str, Any]) -> Tuple[Dict[str, Any], List[ChatMessage]]:
    """
    Process the results of a function call session to remove the history from the results
    and remove any list of ChatMessages from the variables.

    Args:
        results (Dict[str, Any]): The results of a function call session.
    
    Returns:
        Tuple[Dict[str, Any], List[ChatMessage]]: The processed results and the chat messages.
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

    # Save the history and chat messages in separate variables
    chat_messages = []
    history = results["variables"].get('history', None)
    chat_messages = [v for _, v in results["variables"].items() if is_list_of_chat_messages(v)]
    chat_messages = chat_messages + history if history else chat_messages
    # If chat_messages is a list of one list, extract the list
    if len(chat_messages) > 0 and isinstance(chat_messages, list) and isinstance(chat_messages[0], list):
        chat_messages = chat_messages[0]
    
    # Remove the history and chat messages from the results
    results["variables"] = {k: v for k, v in results["variables"].items() if k != 'history' and not is_list_of_chat_messages(v)}

    return results, chat_messages[2:] # Skip the first two messages (system prompt and task prompt)