from pathlib import Path

import yaml
from langchain.prompts import ChatPromptTemplate
from langchain_community.callbacks import get_openai_callback  # Add this import


class PromptyHandler:
    def _load_prompty(self, prompty_path, llm_interface):
        # self.prompty_path initialized by child
        # This should likely be broken up more with to isolate functionality further
        prompty_path = Path(prompty_path)
        if not prompty_path.exists():
            raise FileNotFoundError(f"Prompty file not found at: {prompty_path}")
        with open(prompty_path, "r") as f:
            prompty_content = f.read()

        prompty_data = list(yaml.safe_load_all(prompty_content))

        if not prompty_data or len(prompty_data) < 2:
            raise ValueError("Invalid prompty file format.")

        prompt_section = prompty_data[1]
        prompt_template = prompt_section.get("prompt", {}).get("template", None)

        if prompt_template is None:
            raise ValueError("Prompt template not found in prompty file.")

        chain_prompt_template = ChatPromptTemplate.from_template(
            prompt_template, template_format="jinja2"
        )

        return self._create_chain(chain_prompt_template, llm_interface)

    def _create_chain(self, prompt_template, llm_interface):
        return prompt_template | llm_interface

    def generate_response(self, chain, input_data):
        with get_openai_callback() as result_meta:  # Capture response_meta
            result = chain.invoke(input_data)

        return result, result_meta
