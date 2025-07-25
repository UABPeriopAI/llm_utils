<<<<<<< HEAD
from langchain_core.prompts import (ChatPromptTemplate,
                                    HumanMessagePromptTemplate,
                                    MessagesPlaceholder,
                                    SystemMessagePromptTemplate)
=======
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
>>>>>>> develop


class PromptAssembler:
    @staticmethod
    def assemble_prompt(system_prompt, user_prompt, **kwargs):
<<<<<<< HEAD
=======
        """
        The function `assemble_prompt` formats a chat prompt using system and user message templates.

        :param system_prompt: The `system_prompt` parameter is typically a message or prompt template
        that is generated by the system or program. It could be a message informing the user of a system
        status, providing instructions, or asking for input
        :param user_prompt: It seems like the user_prompt parameter is missing. Could you please provide
        the user prompt so that I can assist you further with the assemble_prompt function?
        :return: The function `assemble_prompt` returns a formatted chat prompt that includes a system
        message and a user message, with the placeholders replaced by the provided keyword arguments
        (**kwargs).
        """
>>>>>>> develop
        system_message = SystemMessagePromptTemplate.from_template(system_prompt)
        user_message = HumanMessagePromptTemplate.from_template(user_prompt)
        chat_prompt = ChatPromptTemplate.from_messages([system_message, user_message])
        formatted_prompt = chat_prompt.format_prompt(**kwargs)
        # print('prompt formatting complete = ',formatted_prompt, flush = True)
        return formatted_prompt

    @staticmethod
    def assemble_chat_template(prompt, role: str = "system", **kwargs):
        chat_template = ChatPromptTemplate.from_messages(
            [
                (
                    role,
                    prompt,
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        return chat_template
