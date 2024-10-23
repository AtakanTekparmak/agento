# agento

Very simple, minimal and stateless agent framework. Highly inspired by [openai/swarm](https://github.com/openai/swarm).

**DISCLAIMER**: This is highly work in progress, and the API is not stable. Any contributions are welcome.

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

### Single-Agent Interaction Example

To run the single-agent interaction example script located in `single_agent_example.py`:
```bash
make run_single_agent
```

### Multi-Agent Interaction Example

To run the multi-agent interaction example script located in `multi_agent_example.py`:
```bash
make run_multi_agent
```

<details>
<summary>Example output, click to expand</summary>

```
             ╭───────────────────────────────────────────────────────────────╮                                                                                           
 user        │ Can you get 4 apples, eat 1 of them and sell the remaining 3? │                                                                                           
             ╰───────────────────────────────────────────────────────────────╯                                                                                           
             ╭─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮                                 
 Apple       │ Certainly! I'll get 4 apples, eat 1 of them, and then transfer the task of selling the remaining 3 to the seller agent. │                                 
 Agent       │                                                                                                                         │                                 
             │ ```python                                                                                                               │                                 
             │ apples = get_apples(4)                                                                                                  │                                 
             │ remaining_apples = eat_apples(apples, 1)                                                                                │                                 
             │ task = "sell these apples"                                                                                              │                                 
             │ agent_name = "seller_agent"                                                                                             │                                 
             │ context_variables = {'apples': remaining_apples}                                                                        │                                 
             │ result, history = transfer_to_agent(task, agent_name, context_variables)                                                │                                 
             │ ```                                                                                                                     │                                 
             ╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯                                 
             ╭────────────────────────────────────╮                                                                                                                      
 Seller      │ ```python                          │                                                                                                                      
 Agent       │ money_earned = sell_apples(apples) │                                                                                                                      
             │ ```                                │                                                                                                                      
             ╰────────────────────────────────────╯                                                                                                                      
             ╭───────────────────────────────────╮                                                                                                                       
 Function    │ <|function_results|>              │                                                                                                                       
 Results     │ {                                 │                                                                                                                       
             │   "function_results": {           │                                                                                                                       
             │     "sell_apples": "money_earned" │                                                                                                                       
             │   },                              │                                                                                                                       
             │   "variables": {                  │                                                                                                                       
             │     "apples": [                   │                                                                                                                       
             │       "Apple",                    │                                                                                                                       
             │       "Apple",                    │                                                                                                                       
             │       "Apple"                     │                                                                                                                       
             │     ],                            │                                                                                                                       
             │     "money_earned": "$3"          │                                                                                                                       
             │   }                               │                                                                                                                       
             │ }                                 │                                                                                                                       
             │ <|end_function_results|>          │                                                                                                                       
             ╰───────────────────────────────────╯                                                                                                                       
             ╭────────────────────────────────────────╮                                                                                                                  
 Seller      │ You earned $3 from selling the apples. │                                                                                                                  
 Agent       ╰────────────────────────────────────────╯                                                                                                                  
             ╭────────────────────────────────────────────────────────╮                                                                                                  
 Function    │ <|function_results|>                                   │                                                                                                  
 Results     │ {                                                      │                                                                                                  
             │   "function_results": {                                │                                                                                                  
             │     "get_apples": "apples",                            │                                                                                                  
             │     "eat_apples": "remaining_apples",                  │                                                                                                  
             │     "transfer_to_agent": "Transfer task result"        │                                                                                                  
             │   },                                                   │                                                                                                  
             │   "variables": {                                       │                                                                                                  
             │     "apples": [                                        │                                                                                                  
             │       "Apple",                                         │                                                                                                  
             │       "Apple",                                         │                                                                                                  
             │       "Apple",                                         │                                                                                                  
             │       "Apple"                                          │                                                                                                  
             │     ],                                                 │                                                                                                  
             │     "remaining_apples": [                              │                                                                                                  
             │       "Apple",                                         │                                                                                                  
             │       "Apple",                                         │                                                                                                  
             │       "Apple"                                          │                                                                                                  
             │     ],                                                 │                                                                                                  
             │     "task": "sell these apples",                       │                                                                                                  
             │     "agent_name": "seller_agent",                      │                                                                                                  
             │     "context_variables": {                             │                                                                                                  
             │       "apples": [                                      │                                                                                                  
             │         "Apple",                                       │                                                                                                  
             │         "Apple",                                       │                                                                                                  
             │         "Apple"                                        │                                                                                                  
             │       ]                                                │                                                                                                  
             │     },                                                 │                                                                                                  
             │     "result": "You earned $3 from selling the apples." │                                                                                                  
             │   }                                                    │                                                                                                  
             │ }                                                      │                                                                                                  
             │ <|end_function_results|>                               │                                                                                                  
             ╰────────────────────────────────────────────────────────╯                                                                                                  
             ╭────────────────────────────────────────╮                                                                                                                  
 Apple       │ You earned $3 from selling the apples. │                                                                                                                  
 Agent       ╰────────────────────────────────────────╯                                                                                                                   
```

</details>