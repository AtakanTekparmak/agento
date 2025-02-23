from agento import Agent, print_history
from typing import List

# Define the functions that the agents can use
def get_apples(quantity: int) -> List[str]:
    """
    Get a certain quantity of apples.

    Args:
        quantity (int): The quantity of apples to get.

    Returns:
        List[str]: A list of apples.
    """
    return ["Apple" for _ in range(quantity)]

def eat_apples(apples: List[str], quantity: int) -> List[str]:
    """
    Eat a certain quantity of apples.

    Args:
        apples (List[str]): A list of apples.
        quantity (int): The quantity of apples to eat.

    Returns:
        List[str]: The remaining apples.
    """
    return apples[quantity:] if quantity < len(apples) else []

def sell_apples(apples: List[str]) -> str:
    """
    Sell all the apples provided.

    Args:
        apples (List[str]): A list of apples.

    Returns:
        str: The money earned from selling the apples.
    """
    return f"${len(apples) * 1}"

# Define the agent
agent = Agent(
    name="Apple Agent",
    instructions="You are an apple seller. You can get, eat or sell apples.",
    model="Qwen/Qwen2.5-Coder-7B-Instruct",
    provider="vllm",
    functions=[get_apples, eat_apples, sell_apples],
)

# Run the agent
history = agent("Can you get 4 apples, eat 1 of them and sell the rest?")

# Print the history
print_history(history)