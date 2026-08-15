import os
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from fastembed import TextEmbedding

class QdrantService:
    def __init__(self):
        qdrant_url = os.getenv("QDRANT_URL", "http://qdrant:6333")
        print(f"Connecting to Qdrant at {qdrant_url}...")
        
        self.client = QdrantClient(url=qdrant_url)
        self.collection_name = "company_guidelines"
        self._ensure_collection_exists()

        # Initialize the embedding model (downloads a lightweight model on first run)
        print("Initializing FastEmbed model...")
        self.embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

    def _ensure_collection_exists(self):
        collections = self.client.get_collections().collections
        if not any(c.name == self.collection_name for c in collections):
            print(f"Creating new Qdrant collection: {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )

    def upload_guideline(self, title: str, text: str) -> int:
        # 1. Chunking: Split by paragraphs for now. 
        # (If you move to long PDFs later, you can swap this for a recursive character chunker or hierarchical summarizer).
        chunks = [chunk.strip() for chunk in text.split("\n\n") if len(chunk.strip()) > 10]
        
        if not chunks:
            return 0

        # 2. Embed all chunks simultaneously
        embeddings = list(self.embedding_model.embed(chunks))

        # 3. Create Qdrant points with metadata payload
        points = []
        for i, (chunk, vector) in enumerate(zip(chunks, embeddings)):
            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector.tolist(),
                    payload={
                        "title": title,
                        "text": chunk,
                        "chunk_index": i
                    }
                )
            )

        # 4. Upload to the vector database
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

        return len(points)


    def search_guidelines(self, query: str, limit: int = 3) -> list[str]:
        print(f"Searching Qdrant for guidelines related to: '{query}'")
        
        # 1. Convert the user's prompt into a vector using the exact same model
        # fastembed returns a generator, so we use next() to get the first result
        query_vector = next(self.embedding_model.embed([query])).tolist()
        
        # 2. Perform a similarity search in Qdrant
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit, # Only bring back the top 3 most relevant rules
            score_threshold=0.5 # Optional: only return rules that are somewhat relevant
        )
        
        # 3. Extract just the text from the matching chunks
        guidelines = [hit.payload["text"] for hit in search_result if hit.payload]
        
        
        print(f"Found {len(guidelines)} relevant guidelines!")
        return guidelines

qdrant_db = QdrantService()