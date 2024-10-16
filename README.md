# agento

Very simple, minimal and stateless agent framework. Highly inspired by [openai/swarm](https://github.com/openai/swarm).

**DISCLAIMER**: This is highly work in progress, and the API is not stable. Any contributions are welcome.
Especially in terms of multi-agent interactions, I'm all ears for any ideas or suggestions.

## Installation

```bash
git clone https://github.com/AtakanTekparmak/agento 
cd agento
pip install -r requirements.txt
```

## Usage

1. Go to `agento/settings.py` and set the `DEFAULT_MODEL`, `BASE_URL` and `API_KEY` according to your needs.

### Example 1: Single Agent with Many Functions

```python
from agento import Agent
from typing import List

# Define the functions that the agents can use
def get_apples(quantity: int):
    """Get a certain quantity of apples."""
    return ["Apple" for _ in range(quantity)]

def eat_apples(apples: List[str]):
    """Eat a certain quantity of apples."""
    return apples, f"Eaten {len(apples)} apples."

def sell_apples(apples: List[str]):
    """Sell a certain quantity of apples."""
    return f"Sold {len(apples)} apples."

# Define the agent
agent = Agent(
    name="Apple Agent",
    instructions="You are an apple seller. You can get, eat or sell apples.",
    functions=[get_apples, eat_apples, sell_apples],
)

# Run the agent
results = agent("Can you get 4 apples, eat 1 of them and sell the rest?")

# Print the results
for message in results[1:]:
    print(f"-----------\n~Sender: {message.sender}\n~Message: {message.message.content}\n-----------\n")
```
