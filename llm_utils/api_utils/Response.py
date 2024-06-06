from abc import abstractmethod, ABC


class Response(ABC):
    @abstractmethod
    def process_input(self):
        pass

    @abstractmethod
    def generate_response(self):
        pass


class ResponseHandler(Response):
    def __init__(self, llm_interface):
        self.llm_interface = llm_interface
