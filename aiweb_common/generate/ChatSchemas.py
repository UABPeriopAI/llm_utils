from datetime import date, datetime
from enum import Enum
from typing import List

import pytz
<<<<<<< HEAD
from pydantic import BaseModel, Field
=======
from pydantic import BaseModel, Field, field_serializer
>>>>>>> develop
from typing_extensions import Annotated

# Default System Message
current_date = date.today().strftime("%Y-%m-%d")
DEFAULT_SYSTEM_MESSAGE = f"You are ChatGPT, a large language model trained by OpenAI, based on the GPT architecture. \
Knowledge cutoff: 2023-12 Current date: {current_date}"


class Role(str, Enum):
    ai = "ai"
    human = "human"


class AIName(str, Enum):
    GPT4 = "gpt4"
    GPT35 = "gpt3.5"


class Message(BaseModel):
<<<<<<< HEAD
    role: Role = Field(example=Role.human)
    content: str
    time: datetime = Field(
        default_factory=lambda: datetime.now(pytz.timezone("US/Central")),
        description="The time the message was created",
        example=datetime.now(
            pytz.timezone("US/Central")
        ).isoformat(),  # Example in Central Time
=======
    role: "Role" = Field(
        default="Role.human",  # Replace with Role.human if Role is an enum/class.
        json_schema_extra={"example": "Role.human"},  # Adjust as needed.
    )
    content: str
    time: datetime = Field(
        default_factory=lambda: datetime.now(pytz.timezone("US/Central")),
        json_schema_extra={
            "description": "The time the message was created",
            "example": datetime.now(pytz.timezone("US/Central")).isoformat(),
        },
>>>>>>> develop
    )

    def __init__(self, **data):
        super().__init__(**data)
        # Convert time to Central Time if it's not already
        if self.time.tzinfo is None:
            self.time = pytz.timezone("US/Central").localize(self.time)
        else:
            self.time = self.time.astimezone(pytz.timezone("US/Central"))

<<<<<<< HEAD
    class Config:
        json_encoders = {
            datetime: lambda v: v.astimezone(pytz.timezone("US/Central")).isoformat()
        }
=======
    @field_serializer("time", mode="plain")
    def serialize_time(self, dt: datetime, _info):
        return dt.astimezone(pytz.timezone("US/Central")).isoformat()
>>>>>>> develop


class ChatRequest(BaseModel):
    history: List[Message]
    chat_ai_choice: AIName = AIName.GPT35  # Default model choice
<<<<<<< HEAD
    temperature: Annotated[
        float, Field(strict=True, ge=0, le=2)
    ] = 0.7  # Default temperature
    system_message: str = (
        DEFAULT_SYSTEM_MESSAGE  # Default instructions mimicking commercial gpt
    )
=======
    temperature: Annotated[float, Field(strict=True, ge=0, le=2)] = 0.0  # Default temperature
    system_message: str = DEFAULT_SYSTEM_MESSAGE  # Default instructions mimicking commercial gpt
>>>>>>> develop


class ChatResponse(BaseModel):
    response: Message  # Now using a Message model instead of a string
