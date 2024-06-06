from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)


class PromptAssembler:
    @staticmethod
    def assemble_prompt(system_prompt, user_prompt, **kwargs):
        system_message = SystemMessagePromptTemplate.from_template(system_prompt)
        user_message = HumanMessagePromptTemplate.from_template(user_prompt)
        chat_prompt = ChatPromptTemplate.from_messages([system_message, user_message])
        formatted_prompt = chat_prompt.format_prompt(**kwargs)
        print('prompt formatting complete = ',formatted_prompt, flush = True)
        return formatted_prompt
