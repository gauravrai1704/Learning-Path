import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


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