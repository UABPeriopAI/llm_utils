import csv
from pathlib import Path

import pandas as pd
<<<<<<< HEAD
=======
from aiweb_common.generate.QueryInterface import QueryInterface
>>>>>>> develop
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.document_loaders.pdf import PyMuPDFLoader
from langchain_community.vectorstores import FAISS

<<<<<<< HEAD
from aiweb_common.generate.QueryInterface import QueryInterface

#TODO Add documentation for methods and classes throughout
class RAGServicer(QueryInterface):
    def __init__(
        self, language_model_interface, embedding_interface, vectorstore: Path
    ):
=======

# TODO Add documentation for methods and classes throughout
class RAGServicer(QueryInterface):
    def __init__(self, language_model_interface, embedding_interface, vectorstore: Path):
        """
        The function initializes an object with language model, embedding interface, and vector store
        attributes.

        :param language_model_interface: The `language_model_interface` parameter in the `__init__`
        method is typically an interface or object that provides functionality related to language
        modeling. This could include methods for processing text, generating language models, or
        performing natural language processing tasks
        :param embedding_interface: The `embedding_interface` parameter in the `__init__` method is
        typically used to pass an interface or object that provides access to word embeddings. Word
        embeddings are dense vector representations of words in a continuous vector space, often used in
        natural language processing tasks
        :param vectorstore: The `vectorstore` parameter in the `__init__` method is of type `Path`. It is
        used to store the path to a directory or file where vectors are stored. This path could point to
        a file containing pre-trained word embeddings or a directory where multiple vector files are
        stored. The
        :type vectorstore: Path
        """
>>>>>>> develop
        self.vectorstore = vectorstore
        self.embedding_interface = embedding_interface
        super().__init__(language_model_interface)

    def retrieve_data(self, query):
<<<<<<< HEAD
=======
        """
        The `retrieve_data` function loads a vector database, performs a search using a query, and returns
        the retrieved data.

        :param query: The `query` parameter in the `retrieve_data` function is typically a search query or a
        piece of information that you want to use to retrieve relevant data from the vector database. This
        query is passed to the `invoke` method of the `docsearch` object to retrieve the relevant data based
        on
        :return: The `retrieved_data` variable is being returned from the `retrieve_data` method.
        """
>>>>>>> develop
        vectordb = FAISS.load_local(
            self.vectorstore,
            self.embedding_interface,
            allow_dangerous_deserialization=True,
        )
        docsearch = vectordb.as_retriever()
        retrieved_data = docsearch.invoke(query)
        return retrieved_data


class SearchServicer(QueryInterface):
<<<<<<< HEAD
    def __init__(self, language_model_interface, searchable):
        self.searchable = searchable
        super().__init__(language_model_interface)

    #TODO fix yellow underline warning here
    def retrieve_data(self, search_function):
=======
    """
    The `SearchServicer` class initializes an object with language model interface and searchable
    attributes, allowing retrieval of data based on a search function.
    """

    def __init__(self, language_model_interface, searchable):
        """
        The function initializes an object with a language model interface and a searchable attribute.

        :param language_model_interface: The `language_model_interface` parameter in the `__init__` method
        is typically an interface or object that provides language processing capabilities or
        functionalities. It could be a natural language processing (NLP) model, a machine learning model for
        language tasks, or any other component that deals with language understanding or
        :param searchable: The `searchable` parameter in the `__init__` method is typically used to indicate
        whether the object being initialized should be searchable or not. This parameter allows you to
        control whether the object can be included in search operations or not
        """
        self.searchable = searchable
        super().__init__(language_model_interface)

    def retrieve_data(self, search_function):
        """
        The `retrieve_data` function takes a search function as input, searches documents based on a
        searchable input using that function, and returns the retrieved data.

        :param search_function: The `search_function` parameter is a function that will be used to search
        for data based on the `searchable` input. It is a function that takes the `searchable` input as an
        argument and returns the retrieved data. You can pass different search functions to the
        `retrieve_data` method
        :return: The `retrieved_data` variable is being returned.
        """
>>>>>>> develop
        # docsearch = DocumentSearcher(self.searchable)  # Use a document searcher object
        retrieved_data = search_function(
            self.searchable
        )  # Search documents based on the searchable input
        return retrieved_data


class VectorStoreBuilder:
    # TODO make into factory for PDF/CSV and allowing for future file type integrations
    def __init__(self, embedding_model, output_faiss: Path):
        self.embedding_model = embedding_model
        self.out = output_faiss

    def _clean_csv(self, input_csv):
        # Make sure the data frame is clean - remove NaN and drop duplicates
        df = pd.read_csv(input_csv, na_values=[""])
        df.drop_duplicates(inplace=True)
        df = df.dropna(how="any")
        clean_csv_path = Path(input_csv).parent / "clean_csv_for_vectorstore.csv"
        df.to_csv(clean_csv_path, index=False, quoting=csv.QUOTE_ALL)
        return clean_csv_path

    def convert_csv_to_vectorstore(self, input_csv, clean_csv=False):
        if clean_csv:
            input_csv = self._clean_csv(input_csv)

        csv_loader = CSVLoader(file_path=input_csv)
        documents = csv_loader.load()

        vector_store = FAISS.from_documents(documents, self.embedding_model)
        vector_store.save_local(self.out)

    def load_pdf_and_process(self, file_path):
        loader = PyMuPDFLoader(file_path)
        document = loader.load()
        return document

    def convert_pdf_to_vectorstore(self, pdf_folder):
        folder_path = Path(pdf_folder)
        list_of_docs = folder_path.glob("**/*.pdf")

        vector_store = None
        for idx, file_path in enumerate(list_of_docs):
            document = self.load_pdf_and_process(file_path)
            if idx == 0:
                vector_store = FAISS.from_documents(document, self.embedding_model)
            else:
                vector_store_idx = FAISS.from_documents(document, self.embedding_model)
                vector_store.merge_from(vector_store_idx)

        vector_store.save_local(self.out)
