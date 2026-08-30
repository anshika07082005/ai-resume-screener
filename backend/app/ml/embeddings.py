import os
from functools import lru_cache
from typing import List

from sklearn.feature_extraction.text import HashingVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


MODEL_NAME = "all-MiniLM-L6-v2"

# transformer = full SentenceTransformer model
# lightweight = low-memory deployment mode
EMBEDDING_MODE = os.getenv(
    "EMBEDDING_MODE",
    "transformer",
).strip().lower()


# ============================================================
# TRANSFORMER MODEL
# ============================================================

@lru_cache(maxsize=1)
def get_embedding_model():
    """
    Load SentenceTransformer only when transformer mode is enabled.

    Importing sentence_transformers lazily is important because
    importing PyTorch itself consumes significant memory.
    """

    if EMBEDDING_MODE != "transformer":
        return None

    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(
        MODEL_NAME,
        device="cpu",
    )


# ============================================================
# LIGHTWEIGHT EMBEDDING
# ============================================================

def generate_lightweight_embedding(
    text: str,
) -> List[float]:
    """
    Generate a deterministic low-memory text representation.

    HashingVectorizer does not require model loading or fitting
    and is suitable for memory-constrained deployments.
    """

    if not text or not text.strip():
        return []

    vectorizer = HashingVectorizer(
        n_features=384,
        alternate_sign=False,
        norm="l2",
        stop_words="english",
    )

    vector = vectorizer.transform(
        [text]
    )

    return vector.toarray()[0].tolist()


# ============================================================
# GENERATE EMBEDDING
# ============================================================

def generate_embedding(
    text: str,
) -> List[float]:
    """
    Generate a vector representation for text.

    Uses Sentence Transformers in transformer mode and a
    lightweight hashing representation in lightweight mode.
    """

    if not text or not text.strip():
        return []

    if EMBEDDING_MODE == "lightweight":
        return generate_lightweight_embedding(
            text
        )

    model = get_embedding_model()

    embedding = model.encode(
        text,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )

    return embedding.tolist()


# ============================================================
# LIGHTWEIGHT SIMILARITY
# ============================================================

def lightweight_similarity(
    text_a: str,
    text_b: str,
) -> float:
    """
    Calculate low-memory text similarity using TF-IDF.

    Returns percentage between 0 and 100.
    """

    if not text_a or not text_b:
        return 0.0

    try:

        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=5000,
        )

        vectors = vectorizer.fit_transform(
            [
                text_a,
                text_b,
            ]
        )

        similarity = cosine_similarity(
            vectors[0],
            vectors[1],
        )[0][0]

    except ValueError:

        return 0.0

    similarity = max(
        0.0,
        min(
            float(similarity),
            1.0,
        ),
    )

    return round(
        similarity * 100,
        2,
    )


# ============================================================
# SEMANTIC SIMILARITY
# ============================================================

def semantic_similarity(
    text_a: str,
    text_b: str,
) -> float:
    """
    Calculate similarity between two text blocks.

    transformer mode:
        SentenceTransformer MiniLM embeddings.

    lightweight mode:
        TF-IDF similarity for memory-constrained deployment.

    Returns percentage between 0 and 100.
    """

    if not text_a or not text_b:
        return 0.0

    if EMBEDDING_MODE == "lightweight":

        return lightweight_similarity(
            text_a,
            text_b,
        )

    model = get_embedding_model()

    embeddings = model.encode(
        [
            text_a,
            text_b,
        ],
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )

    similarity = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]],
    )[0][0]

    similarity = max(
        0.0,
        min(
            float(similarity),
            1.0,
        ),
    )

    return round(
        similarity * 100,
        2,
    )