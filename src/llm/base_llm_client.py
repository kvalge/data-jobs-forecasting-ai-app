# base_llm_client.py
from abc import ABC, abstractmethod


class BaseLLMClient(ABC):
    """Abstract interface every LLM provider client must implement.

    The rest of the app (bll/extraction_service.py) depends only on this
    interface — not on any specific provider — so swapping providers later
    means writing a new client class, with no changes elsewhere.
    """

    @abstractmethod
    def extract(self, posting_text: str) -> dict:
        """Send posting_text to the LLM and return the parsed JSON response."""
        raise NotImplementedError