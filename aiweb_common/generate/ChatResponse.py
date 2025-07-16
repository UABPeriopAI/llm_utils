from aiweb_common.generate.ChatServicer import ChatServicer
from aiweb_common.generate.Response import ResponseHandler


class ChatResponseHandler(ResponseHandler):
    """
    The `ChatResponseHandler` class initializes a chat servicer with an interface object and prompt,
    delegates response generation to the chat service, and updates conversation history.
    """

    def __init__(self, llm_interface, prompt):
        """
        The function initializes a chat servicer with a given llm_interface and prompt.

        :param llm_interface: The `llm_interface` parameter seems to be an interface object that is being
        passed to the constructor of the class. It is likely used to interact with some external system or
        service
        :param prompt: The `prompt` parameter in the `__init__` method is likely a string that represents
        the message or question that will be displayed to prompt the user for input in the chat service. It
        is used to initialize the `ChatServicer` class along with the `llm_interface`
        """
        super().__init__(llm_interface)
        print("initializing chat servicer")
        self.chat_service = ChatServicer(self.llm_interface, prompt)

    def generate_response(self, messages):
        """
        The `generate_response` function delegates the task of generating a language model response to the
        `chat_service` object.

        :param messages: The `generate_response` method takes a list of messages as input. These messages
        are likely the conversation history or context that will be used to generate a response using the
        language model. The method then calls the `generate_langchain_response` method from the
        `chat_service` object to generate a response based
        :return: The `generate_response` method is returning the result of calling the
        `generate_langchain_response` method from the `chat_service` object with the `messages` parameter
        passed to it.
        """
        # Focus on the specifics of how to interact with the language model.
        # Implement the details of calling the LLM and handling the response.
        return self.chat_service.generate_langchain_response(messages)

    def update_history(self, message, conversation_history):
        """
        The `update_history` function updates the conversation history with a new message using the
        `chat_service` object.

        :param message: The `message` parameter likely refers to the new message that needs to be added to
        the conversation history. It could be a text message, an image, a file, or any other type of data
        that is part of the conversation
        :param conversation_history: The `conversation_history` parameter is likely a data structure that
        stores the history of a conversation. It could be a list, dictionary, or any other data structure
        that keeps track of messages or interactions that have occurred during the conversation. When the
        `update_history` method is called, it is expected to
        :return: The `update_history` method is returning the result of calling the `update_history` method
        of the `chat_service` object with the `message` and `conversation_history` parameters.
        """
        return self.chat_service.update_history(message, conversation_history)
