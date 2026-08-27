from functools import lru_cache
from typing import List

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """
    Load the embedding model once and reuse it.
    """
    return SentenceTransformer(MODEL_NAME)


def generate_embedding(text: str) -> List[float]:
    """
    Generate a dense vector representation for text.
    """

    if not text or not text.strip():
        return []

    model = get_embedding_model()

    embedding = model.encode(
        text,
        normalize_embeddings=True,
    )

    return embedding.tolist()


def semantic_similarity(
    text_a: str,
    text_b: str,
) -> float:
    """
    Calculate semantic similarity between two text blocks.

    Returns a percentage between 0 and 100.
    """

    if not text_a or not text_b:
        return 0.0

    model = get_embedding_model()

    embeddings = model.encode(
        [text_a, text_b],
        normalize_embeddings=True,
    )

    similarity = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]],
    )[0][0]

    # Prevent unexpected values outside valid range
    similarity = max(
        0.0,
        min(float(similarity), 1.0),
    )

    return round(
        similarity * 100,
        2,
    )