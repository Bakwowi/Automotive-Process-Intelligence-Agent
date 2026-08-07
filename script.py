import anthropic
from anthropic import beta_tool
from dotenv import load_dotenv
import json
import requests
from IPython.display import Image, display
from typing import Annotated, Any, Dict, List, TypedDict
from pydantic import BaseModel, Field

# LangChain / Anthropic integrations
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool

# LangGraph runtime primitives
from langgraph.graph import StateGraph, START, END

load_dotenv()


# client = anthropic.Anthropic()


@tool
def get_conversion_rate(base_currency: str, target_currency: str):
    """Retrieves the current exchange rate between two specified currencies.

    Uses standard 3-letter ISO 4217 currency codes to fetch real-time exchange rates.

    Args:
        base_currency (str): The 3-letter ISO 4217 currency code to convert from
            (e.g., 'USD', 'EUR', 'GBP', 'JPY').
        target_currency (str): The 3-letter ISO 4217 currency code to convert into
            (e.g., 'EUR', 'CAD', 'AUD', 'INR').

    Returns:
        dict: A dictionary containing the exchange rate data between the base
            and target currencies.

    Example:
        >>> get_conversion_rate(base_currency="USD", target_currency="EUR")
        {"base_currency": "USD", "target_currency": "EUR", "rate": 0.92}
    """
    
    url = url = f'https://v6.exchangerate-api.com/v6/d0397a29769416a679436009/pair/{base_currency}/{target_currency}'

    try:
        response = requests.get(url)
        data = response.json()
        return json.dumps(data)
    
    except requests.exceptions.HTTPError as http_err:
        return print(f"HTTP error occurred: {http_err} (Status code: {response.status_code})")
    except requests.exceptions.ConnectionError as conn_err:
        return print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        return print(f"Request timed out: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        # Catch-all for any other requests exceptions
        return print(f"An error occurred: {req_err}")
    


# define node state
class ConversionNodeState(TypedDict):
    user_input: str
    conversion_result: str


model = ChatAnthropic(
    model="claude-haiku-4-5",
    max_tokens=1024
)

tools = [get_conversion_rate]

model_with_tools = model.bind_tools(tools=tools, parallel_tool_use=True)



def conversion_node(state: ConversionNodeState) -> ConversionNodeState:
    user_input = state.get("user_input", "")
    if not user_input.strip():
        raise ValueError("User input is required for conversion.")

    messages = [
        {"role": "user", "content": str(user_input)}
    ]

    runner = model_with_tools.run(
        messages=messages,
        system="You are a precise, single-purpose Currency Conversion Agent. Your sole task is to take a financial value in one currency specified by the user. If the user inputs something you can't understand or is ambiguous, ask for more clarity, query an external exchange rate tool, and convert that value into the target currency.",
        stream=True
    )

    conversion_result = ""
    print(runner)
    for message in runner:
        if message["type"] == "tool_response":
            conversion_result += message["content"]
        elif message["type"] == "model_response":
            conversion_result += message["content"]

    state["conversion_result"] = conversion_result
    return state


graph = StateGraph(ConversionNodeState)

graph.add_node("conversion_node", conversion_node, inputs=["user_input"], outputs=["conversion_result"])

graph.add_edge(START, "conversion_node")
graph.add_edge("conversion_node", "conversion_node")  # Loop back to the same node for continuous conversion
graph.add_edge("conversion_node", END)

app = graph.compile()

display(Image(app.get_graph().draw_mermaid_png()))

# user_input = input("What do you want to convert?")

# if user_input.strip() == "":
#     user_input = input("What do you want to convert?")

# messages = [
#     {"role": "user", "content": str(user_input)}
# ]

# runner = client.beta.messages.tool_runner(
#     model="claude-haiku-4-5",
#     max_tokens=1024,
#     tools=[get_conversion_rate],
#     tool_choice={"type": "auto", "disable_parallel_tool_use": True},
#     system="You are a precise, single-purpose Currency Conversion Agent. Your sole task is to take a financial value in one currency specified by the user. If the user inputs something you can't understand or is ambigious, ask for more clarity query an external exchange rate tool, and convert that value into the target currency.",
#     messages=messages,
#     stream=True
# )


