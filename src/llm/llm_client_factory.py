# llm_client_factory.py
from src.llm.base_llm_client import BaseLLMClient
from src.llm.openrouter_client import OpenRouterClient


def get_llm_client() -> BaseLLMClient:
    """Return the active LLM client. Swap the returned class here
    if you switch providers — nothing outside this file needs to change."""
    return OpenRouterClient()