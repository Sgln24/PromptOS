import uuid
import httpx
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# 1. Configuration
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
OLLAMA_URL = "http://localhost:11434/api/embeddings"
EMBEDDING_MODEL = "nomic-embed-text"
COLLECTION_NAME = "company_guidelines"

client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

# 2. Canonical Enterprise Guidelines
real_guidelines = [
    "anthropic claude formatting: Structure the prompt entirely using XML tags (e.g., <instructions>, <context>, <output>). To improve logic, strictly instruct the model to think step-by-step inside <thinking> tags before providing the final answer.",
    "openai gpt formatting: Use Markdown headers (###) or triple quotes (\"\"\") to separate instructions from context. Start with zero-shot instructions. Use positive framing (tell the model exactly what to do, rather than what not to do). Provide strict JSON schemas for structured outputs.",
    "deepseek reasoner r1 formatting: Use direct, zero-shot problem statements. Do NOT use few-shot examples, as they can degrade the model's native reasoning performance. Do not force specific step-by-step formatting; allow the model to naturally output its chain of thought.",
    "coding agents cursor github copilot formatting: Enforce strict software engineering constraints. Always require absolute file paths, output clean unified code diffs, forbid conversational explanations or filler text, and specify exact framework versions (e.g., Next.js 14 App Router, Python 3.11).",
    "google gemini formatting: Define a strict persona upfront. Break the task down into a sequential, multi-modal friendly list. Ground the prompt in heavy context and provide structured few-shot examples to dictate the output quality.",
    "general enterprise structural rules: Never hallucinate statistics. If data is missing, instruct the AI to state 'Data Unavailable'. Ensure output conforms strictly to the requested schema without conversational filler."
]

def get_embedding(text: str) -> list[float]:
    """Fetches vector embeddings from local Ollama."""
    response = httpx.post(
        OLLAMA_URL, 
        json={"model": EMBEDDING_MODEL, "prompt": text},
        timeout=30.0
    )
    response.raise_for_status()
    return response.json()["embedding"]

def reset_and_seed_qdrant():
    # 3. Delete testing data
    try:
        client.delete_collection(collection_name=COLLECTION_NAME)
        print(f"🗑️  Deleted old testing collection: '{COLLECTION_NAME}'")
    except Exception as e:
        print(f"Collection might not exist yet, proceeding... ({e})")

    # 4. Recreate collection for nomic-embed-text (size 768)
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE),
    )
    print(f"✅ Created fresh collection: '{COLLECTION_NAME}'")

    # 5. Embed and Insert Guidelines
    points = []
    print("🧠 Generating embeddings via Ollama...")
    for text in real_guidelines:
        vector = get_embedding(text)
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={"text": text}
            )
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )
    print(f"🚀 Successfully seeded {len(points)} enterprise guidelines into Qdrant!")

if __name__ == "__main__":
    reset_and_seed_qdrant()