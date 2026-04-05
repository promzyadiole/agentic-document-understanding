from __future__ import annotations

from typing import Any

from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec

from app.core.config import get_settings
from app.models.schemas import QueryResponseData, QuerySource, RAGChunk
from app.services.embeddings import embed_text, embed_texts

settings = get_settings()
openai_client = OpenAI(api_key=settings.openai_api_key)
pc = Pinecone(api_key=settings.pinecone_api_key)


def get_or_create_index():
    existing = pc.list_indexes()
    existing_names = set()

    for idx in existing:
        if isinstance(idx, dict):
            existing_names.add(idx.get("name"))
        else:
            try:
                existing_names.add(idx.name)
            except AttributeError:
                pass

    if settings.index_name not in existing_names:
        pc.create_index(
            name=settings.index_name,
            dimension=3072,  # text-embedding-3-large
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )

    return pc.Index(settings.index_name)


def _batch(iterable, batch_size: int):
    for i in range(0, len(iterable), batch_size):
        yield iterable[i:i + batch_size]


def upsert_chunks(
    chunks: list[RAGChunk],
    *,
    namespace: str = "default",
) -> int:
    """
    Embed and upsert chunks into Pinecone in safe batches.
    """
    if not chunks:
        return 0

    index = get_or_create_index()
    texts = [chunk.text for chunk in chunks]
    embeddings = embed_texts(texts)

    vectors = []
    for chunk, embedding in zip(chunks, embeddings):
        base_metadata = {
            "document_id": chunk.document_id,
            "preview": chunk.text[:300],
            **(chunk.metadata or {}),
        }

        if chunk.page is not None:
            base_metadata["page"] = chunk.page

        metadata = {k: v for k, v in base_metadata.items() if v is not None}

        vectors.append(
            {
                "id": chunk.chunk_id,
                "values": embedding,
                "metadata": metadata,
            }
        )
    batch_size = 50
    total = 0

    for batch in _batch(vectors, batch_size):
        index.upsert(vectors=batch, namespace=namespace)
        total += len(batch)

    return total


def retrieve_chunks(
    query: str,
    *,
    namespace: str = "default",
    top_k: int | None = None,
    filter_dict: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """
    Retrieve top-k relevant chunks from Pinecone.
    """
    index = get_or_create_index()
    query_embedding = embed_text(query)
    top_k = top_k or settings.top_k_retrieval

    response = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        namespace=namespace,
        filter=filter_dict,
    )

    matches = []
    for match in response.get("matches", []):
        matches.append(
            {
                "id": match["id"],
                "score": match.get("score"),
                "metadata": match.get("metadata", {}),
            }
        )

    return matches


def answer_with_rag(
    question: str,
    *,
    namespace: str = "default",
    top_k: int | None = None,
    filter_dict: dict[str, Any] | None = None,
) -> QueryResponseData:
    """
    Retrieve context and generate a grounded answer.
    """
    matches = retrieve_chunks(
        query=question,
        namespace=namespace,
        top_k=top_k,
        filter_dict=filter_dict,
    )

    if not matches:
        return QueryResponseData(
            answer="I could not find relevant context in the indexed documents.",
            sources=[],
            grounded=False,
        )

    context_blocks = []
    sources: list[QuerySource] = []

    for match in matches:
        md = match.get("metadata", {})
        text = md.get("preview", "")
        document_id = md.get("document_id", "unknown")
        filename = md.get("filename")
        page = md.get("page")

        context_blocks.append(
            f"[Document ID: {document_id} | Page: {page}]\n{text}"
        )

        sources.append(
            QuerySource(
                document_id=document_id,
                filename=filename,
                page=page,
                excerpt=text[:300],
            )
        )

    context = "\n\n---\n\n".join(context_blocks)

    prompt = f"""
You are a grounded document intelligence assistant.

Answer the user's question using ONLY the context below.
If the answer is not in the context, say so clearly.
Do not fabricate details.
Be concise but useful.

Question:
{question}

Context:
{context}
""".strip()

    response = openai_client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": "You answer only from retrieved document context."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )

    answer = response.choices[0].message.content or ""

    return QueryResponseData(
        answer=answer.strip(),
        sources=sources,
        grounded=True,
    )