from datetime import date, datetime
from enum import Enum
from typing import List

import pytz
from pydantic import BaseModel, Field
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
    role: Role = Field(example=Role.human)
    content: str  # May be plain text or a JSON string encoding image update triggers
    time: datetime = Field(
        default_factory=lambda: datetime.now(pytz.timezone("US/Central")),
        description="The time the message was created",
        example=datetime.now(pytz.timezone("US/Central")).isoformat(),  # Example in Central Time
    )

    def __init__(self, **data):
        super().__init__(**data)
        # Convert time to Central Time if it's not already
        if self.time.tzinfo is None:
            self.time = pytz.timezone("US/Central").localize(self.time)
        else:
            self.time = self.time.astimezone(pytz.timezone("US/Central"))

    def get_image_update(self):
        """
        If content encodes an image update trigger (as JSON), return the image update dict.
        Otherwise, return None.

        Returns
        -------
        dict or None
            The image update trigger dict if present, else None.

        Example
        -------
        >>> msg = Message(content='{"text": "Here is your image", "image_update": {"url": "img.png"}}')
        >>> msg.get_image_update()
        {'url': 'img.png'}
        """
        import json
        try:
            obj = json.loads(self.content)
            if isinstance(obj, dict) and "image_update" in obj:
                return obj["image_update"]
        except Exception:
            pass
        return None

    class Config:
        json_encoders = {datetime: lambda v: v.astimezone(pytz.timezone("US/Central")).isoformat()}


class ChatRequest(BaseModel):
    history: List[Message]
    chat_ai_choice: AIName = AIName.GPT35  # Default model choice
    temperature: Annotated[float, Field(strict=True, ge=0, le=2)] = 0.7  # Default temperature
    system_message: str = DEFAULT_SYSTEM_MESSAGE  # Default instructions mimicking commercial gpt


class ChatResponse(BaseModel):
    response: Message  # Now using a Message model instead of a string
