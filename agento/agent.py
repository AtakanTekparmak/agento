from typing import List, Callable
import json

from agento.settings import DEBUG
from agento.engine import execute_python_code, process_results
from agento.client import ChatMessage, ChatCompletionMessage, chat, add_messages_to_history
from agento.utils import extract_python_code, load_system_prompt, create_functions_schema, format_agent_name

# Type alias for the process function
AgentFunction = Callable[[str, List[ChatMessage]], List[ChatMessage]]

def Agent(
        name: str,
        instructions: str,
        model: str,
        provider: str,
        functions: List[Callable] = [],
        history: List[ChatMessage] = [],
        team: List[AgentFunction] = [],
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
        model (str): The model to use for the agent.
        provider (str): The provider to use for the agent.
        functions (List[Callable]): The functions that the agent can call.
        history (List[ChatMessage]): The history of the conversation.
        team (List[AgentFunction]): The team of agents.

    Returns:
        Callable: A function representing the agent.
    """
    
    def create_transfer_function(team: List[AgentFunction]) -> Callable:
        """
        Create the transfer functions. Used for an agent 
        with a team to transfer the task to the next agent.

        Args:
            team (List[AgentFunction]): The team of agents.

        Returns:
            List[Callable]: The transfer functions.
        """
        
        # Create a map of agent names to their response functions
        agents_map = {
            format_agent_name(agent.__name__): lambda task, context: agent(task=task, context_variables=context) for agent in team
        }

        # Create a string of available agent names
        available_agents = ", ".join(agents_map.keys())

        def transfer_to_agent(task: str, agent_name: str, context_variables = None) -> tuple[str, list[ChatMessage]]:
            """
            Transfer the task to the agent with the 
            given name and return the agent's response.

            Args:
                task (str): The task to transfer.
                agent_name (str): The name of the agent to transfer the task to. Available option(s) are: {available_agents}.
                context_variables: The context variables to pass to the other agent. You have to pass them as a dictionary,
                with the keys being the variable names and the values being the variable values.

            Returns:
                str: The agent's response to the task.
                list[ChatMessage]: The history of the transfer agent after processing the task.
            """
            result = agents_map[agent_name](task, context_variables)
            return result[-1].message.content, result
        
        # Set the name and docstring of the transfer function
        transfer_to_agent.__doc__ = transfer_to_agent.__doc__.replace("{available_agents}", available_agents)

        return transfer_to_agent

    def init_or_update_history(task: str, history: List[ChatMessage], context_variables = None):
        """
        If the history is empty, create a new history with the system prompt.
        If the history is not empty, update the history with the user query.

        Args:
            task (str): The user query.
            history (List[ChatMessage]): The history of the conversation.

        Returns:
            List[ChatMessage]: The updated history.
        """
        if not history or not isinstance(history, list) or not len(history) > 0:
            if len(team) > 0:
                # Add transfer functions to the functions
                functions_schema = create_functions_schema(functions + [create_transfer_function(team)])
            else:
                functions_schema = create_functions_schema(functions)

            # Load the system prompt
            if context_variables:
                system_prompt = load_system_prompt(
                    functions_schema=functions_schema,
                    instructions=instructions,
                    context_variables=context_variables,
                    is_orchestrator=True if len(team) > 0 else False
                )
            else:
                system_prompt = load_system_prompt(
                    functions_schema=functions_schema,
                    instructions=instructions,
                    is_orchestrator=True if len(team) > 0 else False
                )
            history = [
                ChatMessage(
                    sender="system", 
                    message=ChatCompletionMessage(role="system", content=system_prompt)
                )
            ]
        if task:
            history.append(ChatMessage(sender="user", message=ChatCompletionMessage(role="user", content=task)))
        return history

    def process(
            task: str = "",
            history: List[ChatMessage] = history,
            context_variables = None,
            debug: bool = DEBUG
        ) -> List[ChatMessage]:
        """
        Process the user query and update the history 
        using agent: {name}.

        The process is as follows:  
        1. The history is initialized with the system prompt and the user query or updated with the user query.
        2. The response is generated from the chat client using agent: {name}.
        3. The Python code is extracted from the response.
        4. The code is executed and the results are added to the history as a new user message containing the function results.
        5. The response is generated from the chat client using agent: {name}.

        Args:
            task (str): The user query.
            history (List[ChatMessage]): The history of the conversation.

        Returns:
            List[ChatMessage]: The updated history.
        """
        
        # Initialize or update the history
        history = init_or_update_history(task, history, context_variables)

        # Get the response from the chat client
        response = chat(history, model, provider)

        if debug:
            print("-"*50)
            print(f"Sender: {name}")
            print(f"Response:\n{response}") 
            print(f"Context variables:\n{context_variables}") 
            print("-"*50)

        # Extract the Python code from the response
        code, is_code = extract_python_code(response)

        # If the response contains code, execute the code
        if is_code:
            results = execute_python_code(
                code=code, 
                functions=functions if len(team) == 0 else functions + [create_transfer_function(team)], 
                context_variables=context_variables
            )

            # Process the results
            results, chat_messages = process_results(results)

            # Convert the results to a JSON string
            results = json.dumps(results, indent=2)

            # Add the agent response and the function results to the history
            history.append(ChatMessage(sender=name, message=ChatCompletionMessage(role="assistant", content=response)))

            # Add the chat messages to the history
            if len(chat_messages) > 0:
                # Set the include_in_chat flag to False for the chat messages
                chat_messages = [ChatMessage(sender=chat_message.sender, message=chat_message.message, include_in_chat=False) for chat_message in chat_messages]
                history = add_messages_to_history(history, chat_messages)

            history.append(ChatMessage(
                    sender="user", 
                    message=ChatCompletionMessage(role="user", content=f"<|function_results|>\n{results}\n<|end_function_results|>")
            ))

            # Get the response from the chat client
            response = chat(history, model, provider)
            history.append(ChatMessage(sender=name, message=ChatCompletionMessage(role="assistant", content=response)))

        # Return the history
        return history

    # Set the name and docstring of the process function
    process.__name__ = format_agent_name(name)
    process.__doc__ = process.__doc__.replace("\{name\}", format_agent_name(name))
    return process