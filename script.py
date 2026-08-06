import anthropic
from anthropic import beta_tool
from dotenv import load_dotenv
import json
import requests


load_dotenv()


client = anthropic.Anthropic()

# tools = [
#     {
#         "name": "get_conversion_rate",
#         "description": "Retrieves the current exchange rate between two specified currencies using ISO 4217 standard 3-letter currency codes.",
#         "input_schema": {
#             "type": "object",
#             "properties": {
#                 "base_currency": {
#                     "type": "string",
#                     "description": "The 3-letter ISO 4217 currency code to convert from (e.g., USD, EUR, GBP, JPY)."
#                 },
#                 "target_currency": {
#                     "type": "string",
#                     "description": "The 3-letter ISO 4217 currency code to convert into (e.g., EUR, CAD, AUD, INR)."
#                 }
#             },
#             "required": ["base_currency", "target_currency"],
#             "additionalProperties": False
#         },
#         "input_examples": [
#                 {"base_currency": "USD", "target_currency": "EUR"}
#             ]
#     }
# ]


@beta_tool
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
    

# get_conversion_rate()

user_input = input("What do you want to convert?")

if user_input.strip() == "":
    user_input = input("What do you want to convert?")

messages = [
    {"role": "user", "content": str(user_input)}
]

runner = client.beta.messages.tool_runner(
    model="claude-haiku-4-5",
    max_tokens=1024,
    tools=[get_conversion_rate],
    tool_choice={"type": "auto", "disable_parallel_tool_use": True},
    system="You are a precise, single-purpose Currency Conversion Agent. Your sole task is to take a financial value in one currency specified by the user. If the user inputs something you can't understand or is ambigious, ask for more clarity query an external exchange rate tool, and convert that value into the target currency.",
    messages=messages,
    stream=True
)


final_message = runner.until_done()
for block in final_message.content:
    if block.type == "text":
        print(block.text)


# for message_stream in runner:
#     for event in message_stream:
#         print("event:", event)
#     print("message:", message_stream.get_final_message())

# print(runner.until_done())



# print(response)

# while response.stop_reason == "tool_use":
#     tool_use = next(block for block in response.content if block.type == "tool_use")
#     print(f"Tool: {tool_use.name}")
#     print(f"Input: {tool_use.input}")

#     results = get_conversion_rate(tool_use.input["base_currency"], tool_use.input["target_currency"])
#     # print(f"Results from the API: {results}")
#     if results:
#         messages += [{"role": "assistant", "content": response.content},
#                 {
#                     "role": "user",
#                     "content": [
#                         {
#                             "type": "tool_result",
#                             "tool_use_id": tool_use.id,
#                             "content": json.dumps(results),
#                         }
#                     ],
#                 }]

#         # print(messages)

#         response = client.messages.create(
#             model="claude-haiku-4-5",
#             max_tokens=1024,
#             tools=get_conversion_rate,
#             tool_choice={"type": "auto", "disable_parallel_tool_use": True},
#             system="You are a precise, single-purpose Currency Conversion Agent. Your sole task is to take a financial value in one currency specified by the user. If the user inputs something you can't understand or is ambigious, ask for more clarity query an external exchange rate tool, and convert that value into the target currency.",
#             messages=messages
#         )
#     else:
#         print('An error occured while fetching for the exchange rates')

# print(f"stop_reason: {response.stop_reason}")
# final_text = next(block for block in response.content if block.type == "text")
# print(final_text.text)