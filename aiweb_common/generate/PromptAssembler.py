from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)


class PromptAssembler:
    @staticmethod
    def assemble_prompt(system_prompt, user_prompt, **kwargs):
        system_message = SystemMessagePromptTemplate.from_template(system_prompt)
        user_message = HumanMessagePromptTemplate.from_template(user_prompt)
        chat_prompt = ChatPromptTemplate.from_messages([system_message, user_message])
        formatted_prompt = chat_prompt.format_prompt(**kwargs)
        # print('prompt formatting complete = ',formatted_prompt, flush = True)
        return formatted_prompt

    @staticmethod
    def assemble_chat_template(prompt, role: str = "system", **kwargs):
        # If prompt contains curly braces, escape them for Jinja2 safety
        if isinstance(prompt, str):
            print("[DEBUG] PromptAssembler.assemble_chat_template - original prompt:", prompt, flush=True)
            prompt = prompt.replace("{", "{{").replace("}", "}}")
            print("[DEBUG] PromptAssembler.assemble_chat_template - escaped prompt:", prompt, flush=True)
        chat_template = ChatPromptTemplate.from_messages(
            [
                (
                    role,
                    prompt,
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        print("[DEBUG] PromptAssembler.assemble_chat_template - chat_template:", chat_template, flush=True)
        return chat_template
