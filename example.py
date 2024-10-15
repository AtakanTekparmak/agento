from agento import Agent, ChatMessage
from typing import List

# Define the functions that the agents can use
def get_apples(quantity: int):
    """Get a certain quantity of apples."""
    return ["Apple" for _ in range(quantity)]

def eat_apples(apples: List[str]):
    """Eat a certain quantity of apples."""
    return f"Eaten {len(apples)} apples."

def sell_apples(apples: List[str]):
    """Sell a certain quantity of apples."""
    return f"Sold {len(apples)} apples."

# Define the agents
# An agent is a function that can
# - take a user query and return a response
# - take a history and a user query and return a response
eater_agent = Agent(
    name="Test Agent",
    instructions="You like to eat apples.",
    functions=[get_apples, eat_apples],
)

seller_agent = Agent(
    name="Seller Agent",
    instructions="You sell apples.",
    functions=[sell_apples, get_apples],
)

# Run the eater agent
results: List[ChatMessage] = eater_agent("Can you get and eat 4 apples?")
results = eater_agent(history=results, user_query="How about 2 more?")

# Run the seller agent
results += seller_agent(user_query="Can you get and sell 2 apples?")[1:]

# Print the results
for message in results[1:]:
    print(f"-----\n~Sender: {message.sender}\n~Message: {message.message.content}\n-----\n")