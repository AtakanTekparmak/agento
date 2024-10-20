from typing import List, Callable
import json

from agento.settings import DEFAULT_MODEL
from agento.engine import execute_python_code
from agento.client import ChatMessage, ChatCompletionMessage, chat
from agento.utils import extract_python_code, load_system_prompt, create_functions_schema, format_agent_name

# Type alias for the process function
ProcessFunction = Callable[[str, List[ChatMessage]], List[ChatMessage]]

def Agent(
        name: str,
        instructions: str,
        functions: List[Callable] = [],
        model: str = DEFAULT_MODEL,
        history: List[ChatMessage] = [],
        team: List[ProcessFunction] = [],
    ):
    """
    Function to create an agent. The process() function 
    is the main function that is called to process the 
    user query and/or history. The process() function,
    after being defined, gets the name and docstring of 
    the agent.

    Args:
        name (str): The name of the agent.
        instructions (str): The instructions for the agent.
        functions (List[Callable]): The functions that the agent can call.
        model (str): The model to use for the agent.

    Returns:
        Callable: A function representing the agent.
    """
    
    def create_transfer_functions(team: List[ProcessFunction]) -> List[Callable]:
        """
        Create the transfer functions. Used for an agent 
        with a team to transfer the task to the next agent.

        Args:
            team (List[ProcessFunction]): The team of agents.

        Returns:
            List[Callable]: The transfer functions.
        """
        
        team_functions = []

        for agent in team:
            def team_function(task: str, agent=agent) -> str:
                return agent(task)[-1].message.content
            team_function.__name__ = f"transfer_to_{format_agent_name(agent.__name__)}"
            team_function.__doc__ = f"Transfer task to team member: {agent.__name__} "
            team_functions.append(team_function)

        return team_functions

    def init_or_update_history(user_query: str, history: List[ChatMessage]):
        """
        If the history is empty, create a new history with the system prompt.
        If the history is not empty, update the history with the user query.

        Args:
            user_query (str): The user query.
            history (List[ChatMessage]): The history of the conversation.

        Returns:
            List[ChatMessage]: The updated history.
        """
        if not history or len(history) == 0:
            system_prompt = load_system_prompt(
                functions_schema= create_functions_schema(functions),
                instructions=instructions
            )
            history = [
                ChatMessage(
                    sender="system", 
                    message=ChatCompletionMessage(role="system", content=system_prompt)
                )
            ]
        if user_query:
            history.append(ChatMessage(sender="user", message=ChatCompletionMessage(role="user", content=user_query)))
        return history

    def process(
            user_query: str = "",
            history: List[ChatMessage] = history
        ) -> List[ChatMessage]:
        """
        Process the user query and update the history.
        The process is as follows:  
        1. The history is initialized with the system prompt and the user query or updated with the user query.
        2. The response is generated from the chat client.
        3. The Python code is extracted from the response.
        4. The code is executed and the results are added to the history as a new user message containing the function results.
        5. The response is generated from the chat client.

        Args:
            user_query (str): The user query.
            history (List[ChatMessage]): The history of the conversation.

        Returns:
            List[ChatMessage]: The updated history.
        """
        # Initialize or update the history
        history = init_or_update_history(user_query, history)

        # Get the response from the chat client
        response = chat(history, model)

        # Extract the Python code from the response
        code, is_code = extract_python_code(response)

        # If the response contains code, execute the code
        if is_code:
            results = execute_python_code(code=code, functions=functions)
            # Convert the results to a JSON string
            results = json.dumps(results, indent=2)

            # Add the agent response and the function results to the history
            history.append(ChatMessage(sender=name, message=ChatCompletionMessage(role="assistant", content=response)))
            history.append(ChatMessage(
                    sender="user", 
                    message=ChatCompletionMessage(role="user", content=f"<|function_results|>\n{results}\n<|end_function_results|>")
            ))

            # Get the response from the chat client
            response = chat(history, model)
            history.append(ChatMessage(sender=name, message=ChatCompletionMessage(role="assistant", content=response)))

        # Return the history
        return history

    # Set the name and docstring of the process function
    process.__name__ = format_agent_name(name)
    process.__doc__ = process.__doc__.replace("the history.", "the history, using agent: " + format_agent_name(name))
    return process