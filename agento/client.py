from typing import List
from pydantic import BaseModel

import openai

from agento.settings import BASE_URL, API_KEY, DEFAULT_MODEL

class ChatCompletionMessage(BaseModel):
    role: str
    content: str

class ChatMessage(BaseModel):
    sender: str
    message: ChatCompletionMessage
    include_in_chat: bool = True

def chat(messages: List[ChatMessage], model: str = DEFAULT_MODEL) -> str:
    """
    Get a chat completion from the OpenAI client.

    Args:
        messages (List[ChatMessage]): The messages to send to the client.
        model (str): The model to use for the completion.

    Returns:
        str: The content of the response from the OpenAI client.
    """
    client = openai.Client(
        api_key=API_KEY,
        base_url=BASE_URL,
    )
    
    response = client.chat.completions.create(
        model=model,
        messages=[message.message.model_dump() for message in messages if message.include_in_chat]
    )
    
    return response.choices[0].message.content

def add_messages_to_history(history: List[ChatMessage], messages: List[ChatMessage]) -> List[ChatMessage]:
    """
    Add messages to the history. This method is used to 
    add the messages from a sub-agent to the history of 
    the main agent.

    Args:
        history (List[ChatMessage]): The history to add the messages to.
        messages (List[ChatMessage]): The messages to add to the history.

    Returns:
        List[ChatMessage]: The updated history with the new messages.
    """
    return history + messages