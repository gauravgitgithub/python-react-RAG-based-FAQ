import os
import pickle
import numpy as np
from typing import List, Tuple, Optional
# Mock imports for when ML dependencies are not available
try:
    from sentence_transformers import SentenceTransformer
    import faiss
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("Warning: ML dependencies (sentence_transformers, faiss) not available. Using mock embeddings.")
from app.core.config import settings


class EmbeddingService:
    def __init__(self):
        if ML_AVAILABLE:
            self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        else:
            self.model = None
        self.index = None
        self.chunk_ids = []
        self.load_or_create_index()

    def load_or_create_index(self):
        """Load existing FAISS index or create a new one"""
        if not ML_AVAILABLE:
            # Mock index for when ML dependencies are not available
            self.index = None
            self.chunk_ids = []
            return
            
        if os.path.exists(f"{settings.FAISS_INDEX_PATH}.index"):
            # Load existing index
            self.index = faiss.read_index(f"{settings.FAISS_INDEX_PATH}.index")
            with open(f"{settings.FAISS_INDEX_PATH}_chunk_ids.pkl", "rb") as f:
                self.chunk_ids = pickle.load(f)
        else:
            # Create new index
            dimension = self.model.get_sentence_embedding_dimension()
            self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
            self.chunk_ids = []

    def save_index(self):
        """Save FAISS index and chunk IDs"""
        if not ML_AVAILABLE:
            return
            
        os.makedirs(os.path.dirname(settings.FAISS_INDEX_PATH), exist_ok=True)
        faiss.write_index(self.index, f"{settings.FAISS_INDEX_PATH}.index")
        with open(f"{settings.FAISS_INDEX_PATH}_chunk_ids.pkl", "wb") as f:
            pickle.dump(self.chunk_ids, f)

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts"""
        if not ML_AVAILABLE:
            # Return mock embeddings (random vectors)
            return np.random.rand(len(texts), 384)  # 384 is a common embedding dimension
            
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return embeddings

    def add_embeddings(self, texts: List[str], chunk_ids: List[str]) -> List[int]:
        """Add embeddings to the FAISS index"""
        if not texts:
            return []
        
        if not ML_AVAILABLE:
            # Mock implementation
            start_idx = len(self.chunk_ids)
            self.chunk_ids.extend(chunk_ids)
            return list(range(start_idx, start_idx + len(texts)))
        
        embeddings = self.generate_embeddings(texts)
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add to index
        start_idx = len(self.chunk_ids)
        self.index.add(embeddings)
        
        # Update chunk IDs
        self.chunk_ids.extend(chunk_ids)
        
        # Save index
        self.save_index()
        
        # Return the indices of added embeddings
        return list(range(start_idx, start_idx + len(texts)))

    def search_similar(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Search for similar chunks given a query"""
        if not self.chunk_ids:
            return []
        
        if not ML_AVAILABLE:
            # Mock implementation - return random results
            import random
            results = []
            for i in range(min(top_k, len(self.chunk_ids))):
                chunk_id = random.choice(self.chunk_ids)
                similarity = random.uniform(0.5, 1.0)
                results.append((chunk_id, similarity))
            return results
        
        # Generate query embedding
        query_embedding = self.model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Search in index
        similarities, indices = self.index.search(query_embedding, min(top_k, len(self.chunk_ids)))
        
        # Return chunk IDs and similarity scores
        results = []
        for idx, similarity in zip(indices[0], similarities[0]):
            if idx < len(self.chunk_ids):
                results.append((self.chunk_ids[idx], float(similarity)))
        
        return results

    def remove_embeddings(self, chunk_ids: List[str]):
        """Remove embeddings from the index (recreate index without specified chunks)"""
        if not chunk_ids:
            return
        
        if not ML_AVAILABLE:
            # Mock implementation
            chunk_id_set = set(chunk_ids)
            self.chunk_ids = [cid for cid in self.chunk_ids if cid not in chunk_id_set]
            return
        
        # Create new index
        dimension = self.model.get_sentence_embedding_dimension()
        new_index = faiss.IndexFlatIP(dimension)
        new_chunk_ids = []
        
        # Rebuild index excluding specified chunk IDs
        chunk_id_set = set(chunk_ids)
        for i, chunk_id in enumerate(self.chunk_ids):
            if chunk_id not in chunk_id_set:
                # Get embedding from old index
                embedding = self.index.reconstruct(i).reshape(1, -1)
                new_index.add(embedding)
                new_chunk_ids.append(chunk_id)
        
        # Replace old index with new one
        self.index = new_index
        self.chunk_ids = new_chunk_ids
        
        # Save updated index
        self.save_index()

    def get_index_stats(self) -> dict:
        """Get statistics about the current index"""
        if not ML_AVAILABLE:
            return {
                "total_chunks": len(self.chunk_ids),
                "index_type": "mock",
                "dimension": 384
            }
            
        return {
            "total_chunks": len(self.chunk_ids),
            "index_type": "faiss",
            "dimension": self.model.get_sentence_embedding_dimension() if self.model else 0,
            "is_trained": self.index.is_trained if self.index else False
        } 