"""
Retrieval-Augmented Generation pipeline for the hospital medical assistant.

* Lazy + cached  - built on first use, so the app and tests boot without the ML
  deps or API keys; misconfiguration surfaces as ChatbotUnavailable -> HTTP 503.
* Chat model     - ChatOpenAI (gpt-4o-mini) instead of the legacy completion API.
* History-aware  - follow-ups are reformulated into standalone queries first.
* MMR retrieval  - relevant *and* diverse context chunks.
* Citations      - source document + page returned with each answer.
* Safety         - red-flag emergency symptoms short-circuit the LLM and direct
  the user to urgent care; every answer carries a medical disclaimer.
"""

import re
from functools import lru_cache

from django.conf import settings


class ChatbotUnavailable(Exception):
    """Raised when the RAG chain cannot be built (missing keys or deps)."""


_EMERGENCY_RE = re.compile(
    r"\bchest pain\b|\b(can'?t|cannot|trouble) breath(e|ing)\b|\bstroke\b|"
    r"\b(severe|heavy) bleeding\b|\bunconscious\b|\bseizure\b|\boverdose\b",
    re.IGNORECASE,
)
EMERGENCY_MESSAGE = (
    "This may be a medical emergency. Please call your local emergency number or "
    "go to the nearest emergency department now. You can also use this hospital's "
    "emergency-care booking. I'm an information tool and can't help in an emergency."
)
DISCLAIMER = (
    "This is general information, not medical advice. Please book an appointment "
    "for a proper consultation."
)


def detect_emergency(message: str) -> bool:
    return bool(_EMERGENCY_RE.search(message or ""))


@lru_cache(maxsize=1)
def _build_chain():
    if not settings.OPENAI_API_KEY or not settings.PINECONE_API_KEY:
        raise ChatbotUnavailable(
            "Chatbot is not configured. Set OPENAI_API_KEY and PINECONE_API_KEY, "
            "and build the Pinecone index."
        )
    try:
        import os

        from langchain.chains import (
            create_history_aware_retriever,
            create_retrieval_chain,
        )
        from langchain.chains.combine_documents import create_stuff_documents_chain
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        from langchain_openai import ChatOpenAI
        from langchain_pinecone import PineconeVectorStore

        from src.helper import download_hugging_face_embeddings
        from src.prompt import contextualize_q_system_prompt, system_prompt
    except ImportError as exc:  # pragma: no cover
        raise ChatbotUnavailable(f"Chatbot dependencies are not installed: {exc}") from exc

    os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
    os.environ["PINECONE_API_KEY"] = settings.PINECONE_API_KEY

    embeddings = download_hugging_face_embeddings()
    docsearch = PineconeVectorStore.from_existing_index(
        index_name=settings.PINECONE_INDEX_NAME, embedding=embeddings
    )
    retriever = docsearch.as_retriever(
        search_type="mmr",
        search_kwargs={"k": settings.RAG_RETRIEVER_K, "fetch_k": settings.RAG_FETCH_K},
    )
    llm = ChatOpenAI(model=settings.OPENAI_CHAT_MODEL, temperature=0.3, max_tokens=500)

    contextualize_prompt = ChatPromptTemplate.from_messages([
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    history_aware = create_history_aware_retriever(llm, retriever, contextualize_prompt)
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    qa_chain = create_stuff_documents_chain(llm, qa_prompt)
    return create_retrieval_chain(history_aware, qa_chain)


def _to_messages(history):
    from langchain_core.messages import AIMessage, HumanMessage

    messages = []
    for turn in history or []:
        role, content = turn.get("role"), turn.get("content", "")
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role in ("assistant", "ai", "bot"):
            messages.append(AIMessage(content=content))
    return messages


def _format_sources(documents):
    seen, sources = set(), []
    for doc in documents:
        meta = doc.metadata or {}
        source = str(meta.get("source", "knowledge base")).split("/")[-1]
        page = meta.get("page")
        if (source, page) in seen:
            continue
        seen.add((source, page))
        sources.append({"source": source, "page": page})
    return sources


def answer_question(message: str, history=None) -> dict:
    """Return {"answer", "sources", "emergency", "disclaimer"}."""
    if detect_emergency(message):
        return {"answer": EMERGENCY_MESSAGE, "sources": [], "emergency": True, "disclaimer": DISCLAIMER}

    chain = _build_chain()
    result = chain.invoke({"input": message, "chat_history": _to_messages(history)})
    return {
        "answer": result["answer"],
        "sources": _format_sources(result.get("context", [])),
        "emergency": False,
        "disclaimer": DISCLAIMER,
    }


def reset_cache():
    """Clear the cached chain (used in tests)."""
    _build_chain.cache_clear()
