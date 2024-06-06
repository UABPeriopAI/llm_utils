from llm_utils.api_utils.Response import ResponseHandler
from llm_utils.api_utils.AugmentedServicer import RAGServicer, SearchServicer


# This Python class `AugmentedResponseHandler` extends `ResponseHandler` and implements methods for
# processing input and generating responses using a language model service.
class AugmentedResponseHandler(ResponseHandler):
    def __init__(self, llm_interface):
        super().__init__(llm_interface)

    def process_input(self):
        self.prompt = self.aug_service.process_input()
        
    def generate_response(self, assembled_prompt):
        # Focus on the specifics of how to interact with the language model.
        # Implement the details of calling the LLM and handling the response.
        return self.aug_service.generate_langchain_response(assembled_prompt)

class RAGResponseHandler(AugmentedResponseHandler):
    def __init__(self, llm_interface, embedding_interface, vectorstore):
        self.aug_service = RAGServicer(llm_interface, embedding_interface, vectorstore)
        super().__init__(llm_interface)

class SearchResponseHandler(AugmentedResponseHandler):
    def __init__(self, llm_interface, searchable):
        self.aug_service = SearchServicer(llm_interface, searchable)
        super().__init__(llm_interface)
