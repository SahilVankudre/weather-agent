from email import message
import json
import os
from unittest import result
import requests
from openai import OpenAI
from pydantic import BaseModel, Field
from urllib3 import response

client = OpenAI(
    base_url="https://openrouter.ai/api/v1", 
    api_key="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")

def get_weather(latitude, longitude): 
    response = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    )
    data = response.json()
    return data["current"]

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current temperature for provided coordinates in celsius.",
            "parameters": {
                "type": "object",
                "properties": {
                    "latitude": {"type": "number"},
                    "longitude": {"type": "number"},
                },
                "required": ["latitude", "longitude"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    }
]

system_prompt = "You are a helpful weather assistant"

messages  = [
    {'role': "system", 'content': system_prompt},
    {'role': "user", 'content': "What is weather like in Mumbai today?"},
]

completion = client.chat.completions.create(
    model="mistralai/devstral-2512:free",
    messages=messages,
    tools=tools,
)

completion.model_dump()

def call_fun(name, args):
    if name == "get_weather":
        return get_weather(**args)

for tool_call in completion.choices[0].message.tool_calls:
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)
    messages.append(completion.choices[0].message)

    result = call_fun(name, args)
    messages.append(
        {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)}
    )


class WeatherResponse(BaseModel):
    temperature: float = Field(
        description= "The current temperature in celsius for the given location."
    )

    response: str = Field(
        description="A natural language response to the user's question."
    )

completion_2 = client.beta.chat.completions.parse(
    model = "mistralai/devstral-2512:free",
    messages=messages,
    tools=tools,
    response_format=WeatherResponse,
)

final_response = completion_2.choices[0].message.parsed
print(final_response.temperature)
print(final_response.response)