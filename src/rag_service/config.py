# src/rag_service/config.py
import os
class Cfg:
    AZ_OAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZ_OAI_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZ_OAI_CHAT = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT","gpt-4o-mini")

    SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
    SEARCH_KEY = os.getenv("AZURE_SEARCH_API_KEY")
    SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX","code-docs")
