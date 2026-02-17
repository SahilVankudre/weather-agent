from pydantic import BaseModel
from openai import OpenAI
from pydantic.json_schema import model_json_schema

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="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")

class CalenderEvent(BaseModel):
    name: str 
    date: int
    participants : list[str]

response = client.beta.chat.completions.parse(
    model='mistralai/devstral-2512:free', 
    messages=[
        {
            'role': 'system', 'content': 'You are a weather expert.',
            'role': 'user','content': 'Tell me something about weather in India.',
        }
    ],
    response_format= CalenderEvent,
)

event = response.choices[0].message.parsed
print(event.name) 
print(event.date)
print(event.participants)

"""
def get_wether(long, lat):
    response = requests.get(
        f"api={long},{lat}"
    )
    data = response.json
    return data["current"]

tools = [
    {
        "type": "function",
        "name": "get_wether",
        "description": "Get today's weather.",
        "parameters": {
            "type": "object",
            "properties": {
                "latitude": {"type": "number"},
                "longitude": {"type": "nnumber"},
            },
            "required": ["latitude", "longitude"],
            "additionalProperties": False,
        },
        "strict":True,
    },
]
"""