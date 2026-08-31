import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load .env from current directory, code directory, and parent directory
env_path = Path(__file__).resolve().parent / ".env"
parent_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
load_dotenv(dotenv_path=parent_env_path)
load_dotenv()


def get_llm() -> ChatOpenAI:
    """
    Create and return the OpenAI chat model used by the LangGraph agents.
    """

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is not set. "
            "Please add it to the .env file."
        )

    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=api_key,
    )