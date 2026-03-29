from abc import ABC, abstractmethod


class LanguageModel(ABC):
    @abstractmethod
    def extract_from_image(self, image_bytes: bytes, prompt: str) -> str:
        """Send an image to the LLM with a prompt and return raw text response."""

    @abstractmethod
    def extract_from_images(self, images: list[bytes], prompt: str) -> str:
        """Send multiple images to the LLM with a prompt and return raw text response."""

    @abstractmethod
    def extract_from_pdf(self, pdf_bytes: bytes, prompt: str) -> str:
        """Send a PDF to the LLM with a prompt and return raw text response."""

    @abstractmethod
    def extract_from_text(self, text: str, prompt: str) -> str:
        """Send plain text to the LLM with a prompt and return raw text response."""
