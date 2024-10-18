from typing import List, Callable
import json

from agento.settings import DEFAULT_MODEL
from agento.engine import execute_python_code
from agento.client import ChatMessage, ChatCompletionMessage, chat
from agento.utils import extract_python_code, load_system_prompt, create_functions_schema

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
    Function to create an agent.

    Args:
        name (str): The name of the agent.
        instructions (str): The instructions for the agent.
        functions (List[Callable]): The functions that the agent can call.
        model (str): The model to use for the agent.

    Returns:
        Callable: A function representing the agent.
    """
    def format_agent_name(agent_name: str):
        """
        Format the agent name.

        Args:
            agent_name (str): The name of the agent.

        Returns:
            str: The formatted agent name.
        """
        return agent_name.strip().replace(" ", "_").lower()
    
    def create_transfer_functions(team: List[ProcessFunction]) -> List[Callable]:
        """
        Create the transfer functions.

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
                    message=ChatCompletionMessage(role="user", content=f"\n<|function_results|>\n{results}\n<|end_function_results|>")
            ))

            # Get the response from the chat client
            response = chat(history, model)
            history.append(ChatMessage(sender=name, message=ChatCompletionMessage(role="assistant", content=response)))


        # Return the history
        return history

    process.__name__ = format_agent_name(name)
    process.__doc__ = process.__doc__.replace("the history.", "the history, using agent: " + format_agent_name(name))
    return process