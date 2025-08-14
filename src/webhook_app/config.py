# src/webhook_app/config.py
import os

class Cfg:
    GH_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")
    GH_TOKEN  = os.getenv("GITHUB_TOKEN", "")
    ALLOWED_REPOS = set([r.strip() for r in os.getenv("ALLOWED_REPOS","").split(",") if r.strip()])

    AZ_OAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZ_OAI_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZ_OAI_CHAT = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT","gpt-4o-mini")
    AZ_OAI_EMBED = os.getenv("AZURE_OPENAI_EMBED_DEPLOYMENT","text-embedding-3-large")

    SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
    SEARCH_KEY = os.getenv("AZURE_SEARCH_API_KEY")
    SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX","code-docs")
