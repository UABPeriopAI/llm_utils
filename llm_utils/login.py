import streamlit as st
import os
import requests
            

class BYOK_Handler():
    def __init__(self, chat_config, pubmed_chat_config):
        self.api_key_type = None
        self.api_key = None
        self.CHAT = chat_config
        self.PUBMED_CHAT = pubmed_chat_config

    def _incorporate_api_key(self, api_key):
        st.success('API key is valid.')
        os.environ["OPENAI_API_KEY"] = api_key

    def _api_key_validation(self, api_key):
        pass

    def initialize_api_key(self, api_key):
        pass

    def get_chat_function(self):
        # print('parent - ', self.CHAT)
        return self.CHAT
    
    def get_pubmed_chat_function(self):
        return self.PUBMED_CHAT


class AzureKeyHandler(BYOK_Handler):

    def _api_key_validation(self, api_key):
        # TODO: timeout
        response = requests.get('https://nlp-ai-svc.openai.azure.com/openai/models?api-version=2024-02-01', headers={ 'api-key': api_key})

        if response.status_code == 200:
            return True
        else:
            return False

    def initialize_api_key(self, api_key):
        if self._api_key_validation(api_key):
            # TODO: generalize this - next 2 lines
            self._incorporate_api_key(api_key)
            return True

        else:
            st.error('API key is invalid.')
            return False


class OpenaiKeyHandler(BYOK_Handler):


    def _api_key_validation(self, api_key):
                # TODO: timeout

        response = requests.get('https://api.openai.com/v1/engines', headers={ 'Authorization': 'Bearer ' + api_key})

        if response.status_code == 200:
            return True
        else:
            return False
        
    def initialize_api_key(self, api_key):
        if self._api_key_validation(api_key):
            self._incorporate_api_key(api_key)
            return True
        else:
            st.error('API key is invalid.')
            return False



