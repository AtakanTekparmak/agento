from typing import List
from pydantic import BaseModel

import openai

from agento.settings import PROVIDER_URLS, DEFAULT_PROVIDER

class ChatCompletionMessage(BaseModel):
    """Wrapper class for a chat message."""
    role: str
    content: str

class ChatMessage(BaseModel):
    """Wrapper class for a ChatCompletionMessage."""
    sender: str
    message: ChatCompletionMessage
    include_in_chat: bool = True

def chat(messages: List[ChatMessage], model: str, provider: str = DEFAULT_PROVIDER) -> str:
    """
    Get a chat completion from the specified provider.

    Args:
        messages (List[ChatMessage]): The messages to send to the client.
        model (str): The model to use for the completion.
        provider (str): The provider to use for the completion. Available options: lm_studio, ollama, vllm, openrouter.

    Returns:
        str: The content of the response from the provider.
    """
    if provider not in PROVIDER_URLS:
        raise ValueError(f"Provider {provider} not supported. Available providers: {', '.join(PROVIDER_URLS.keys())}")
    
    base_url, api_key = PROVIDER_URLS[provider]
    
    client = openai.Client(
        api_key=api_key,
        base_url=base_url,
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