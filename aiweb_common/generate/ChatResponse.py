from aiweb_common.generate.ChatServicer import ChatServicer
from aiweb_common.generate.Response import ResponseHandler


class ChatResponseHandler(ResponseHandler):
    def __init__(self, llm_interface, prompt):
        super().__init__(llm_interface)
        print("initializing chat servicer")
        self.chat_service = ChatServicer(self.llm_interface, prompt)

    def generate_response(self, messages):
        """
        Generate a chat response using the language model and return a ChatResponse object.

        Args:
            messages (List[Message]): The chat history/messages.

        Returns:
            ChatResponse: The response object containing the AI's reply as a Message.
        """
        from aiweb_common.generate.ChatSchemas import ChatResponse, Message

        # Get the raw response and metadata from the chat service
        response_content, response_meta = self.chat_service.generate_langchain_response(messages)

        # If the response includes an image update, encode it in Message.content as JSON
        # Convention: If response_content is a dict with 'text' and 'image_update', encode as JSON string
        import json
        if isinstance(response_content, dict) and "text" in response_content:
            # Example: {"text": "...", "image_update": {...}}
            content = json.dumps(response_content)
        else:
            content = response_content

        # Compose the Message object (role: ai)
        message = Message(role="ai", content=content)
        return ChatResponse(response=message)

    def update_history(self, message, conversation_history):
        return self.chat_service.update_history(message, conversation_history)
