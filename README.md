# agento

Very simple, minimal and stateless agent framework. Highly inspired by [openai/swarm](https://github.com/openai/swarm).

**DISCLAIMER**: This is highly work in progress, and the API is not stable. Any contributions are welcome.
Especially in terms of multi-agent interactions, I'm all ears for any ideas or suggestions.

## Installation

```bash
git clone https://github.com/AtakanTekparmak/agento 
cd agento
make install
```

## Testing

To run the tests, simply run:
```bash
make test
```

## Usage

1. Copy the `.env.example` file to `.env` and set the `DEFAULT_MODEL`, `BASE_URL` and `OPENAI_API_KEY` according to your needs.
```bash
make copy_env
```
I use [Qwen2.5-Coder-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct) in f16 precision through [Ollama](https://ollama.com/). To use the default settings, simply:
```bash
ollama pull qwen2.5-coder:7b-instruct-fp16
```

### Multi-Agent Interaction Example

**DISCLAIMER:** Work in progress. The sub-agent is being called twice and I am not sure why. Trying to figure that out, any help is highly appreciated.

To run the multi-agent interaction example script located in `example2.py`:
```bash
make run_multi_agent
```

### Example 1: Single Agent with Many Functions

```python
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
    functions=[get_apples, eat_apples, sell_apples],
)

# Run the agent
history = agent("Can you get 4 apples, eat 1 of them and sell the rest?")

# Print the history
print_history(history)
```

Example output, click to expand (text-based so Desktop is recommended):

<details>
<summary>Example Output</summary>

```
             ╭────────────────────────────────────────────────────────╮                                                                                                        
 user        │ Can you get 4 apples, eat 1 of them and sell the rest? │                                                                                                        
             ╰────────────────────────────────────────────────────────╯                                                                                                        
             ╭──────────────────────────────────────────────╮                                                                                                                  
 Apple       │ ```python                                    │                                                                                                                  
 Agent       │ apples = get_apples(4)                       │                                                                                                                  
             │ remaining_apples = eat_apples(apples, 1)     │                                                                                                                  
             │ money_earned = sell_apples(remaining_apples) │                                                                                                                  
             │ ```                                          │                                                                                                                  
             ╰──────────────────────────────────────────────╯                                                                                                                  
             ╭───────────────────────────────────────╮                                                                                                                         
 user        │ <|function_results|>                  │                                                                                                                         
             │ {                                     │                                                                                                                         
             │   "function_results": {               │                                                                                                                         
             │     "get_apples": "apples",           │                                                                                                                         
             │     "eat_apples": "remaining_apples", │                                                                                                                         
             │     "sell_apples": "money_earned"     │                                                                                                                         
             │   },                                  │                                                                                                                         
             │   "variables": {                      │                                                                                                                         
             │     "apples": [                       │                                                                                                                         
             │       "Apple",                        │                                                                                                                         
             │       "Apple",                        │                                                                                                                         
             │       "Apple",                        │                                                                                                                         
             │       "Apple"                         │                                                                                                                         
             │     ],                                │                                                                                                                         
             │     "remaining_apples": [             │                                                                                                                         
             │       "Apple",                        │                                                                                                                         
             │       "Apple",                        │                                                                                                                         
             │       "Apple"                         │                                                                                                                         
             │     ],                                │                                                                                                                         
             │     "money_earned": "$3"              │                                                                                                                         
             │   }                                   │                                                                                                                         
             │ }                                     │                                                                                                                         
             │ <|end_function_results|>              │                                                                                                                         
             ╰───────────────────────────────────────╯                                                                                                                         
             ╭─────────────────────────────────────────────────────────────────────────────────────────╮                                                                       
 Apple       │ Now you have $3 and 3 apples remaining. If you'd like to do anything else, let me know! │   
```

</details>