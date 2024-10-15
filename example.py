from agento import Agent, ChatMessage
from typing import List

def get_apples(quantity: int):
    """Get a certain quantity of apples."""
    return ["Apple" for _ in range(quantity)]

def eat_apples(apples: List[str]):
    """Eat a certain quantity of apples."""
    return f"Eaten {len(apples)} apples."

def sell_apples(apples: List[str]):
    """Sell a certain quantity of apples."""
    return f"Sold {len(apples)} apples."

agent = Agent(
    name="Test Agent",
    instructions="You like to eat apples.",
    functions=[get_apples, eat_apples],
)

seller = Agent(
    name="Seller Agent",
    instructions="You sell apples.",
    functions=[sell_apples, get_apples],
)

results: List[ChatMessage] = agent("Can you get and eat 4 apples?")
results = agent(history=results, user_query="How about 2 more?")
results += seller(user_query="Can you get and sell 2 apples?")[1:]
for message in results[1:]:
    print(f"-----\n~Sender: {message.sender}\n~Message: {message.message.content}\n-----\n")