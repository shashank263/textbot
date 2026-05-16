import json
import os
import pickle
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss


class CatalogProcessor:
    """Processes raw SHL catalog and generates embeddings."""
    
    def __init__(self, raw_catalog_path: str = "data/shl_catalog.json",
                 processed_catalog_path: str = "data/processed_catalog.json",
                 model_name: str = "all-MiniLM-L6-v2"):
        self.raw_catalog_path = raw_catalog_path
        self.processed_catalog_path = processed_catalog_path
        self.model = SentenceTransformer(model_name)
        self.processed_catalog = []
        self.embeddings = None
        self.metadata = None
    
    def load_raw_catalog(self) -> List[Dict]:
        """Load raw catalog from JSON."""
        if not os.path.exists(self.raw_catalog_path):
            raise FileNotFoundError(f"Catalog not found at {self.raw_catalog_path}")
        
        with open(self.raw_catalog_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def process_catalog(self) -> List[Dict]:
        """
        Process raw catalog: clean and merge searchable text.
        
        Combines name, description, skills, and test type into
        a searchable text field for embedding.
        """
        # Reset to prevent duplicates on repeated runs
        self.processed_catalog = []
        
        raw_catalog = self.load_raw_catalog()
        print(f"Loaded raw catalog: {len(raw_catalog)} assessments")
        
        for assessment in raw_catalog:
            # Merge all searchable fields
            searchable_text = self._create_searchable_text(assessment)
            
            processed_item = {
                "id": len(self.processed_catalog),
                "name": assessment.get("name", ""),
                "description": assessment.get("description", ""),
                "url": assessment.get("url", ""),
                "test_type": assessment.get("test_type", "O"),
                "skills": assessment.get("skills", []),
                "duration": assessment.get("duration"),
                "level": assessment.get("level"),
                "remote_support": assessment.get("remote_support", True),
                "searchable_text": searchable_text
            }
            
            self.processed_catalog.append(processed_item)
        
        print(f"Processed catalog: {len(self.processed_catalog)} assessments")
        return self.processed_catalog
    
    def _create_searchable_text(self, assessment: Dict) -> str:
        """Create searchable text from assessment."""
        parts = [
            assessment.get("name", ""),
            assessment.get("description", ""),
            " ".join(assessment.get("skills", [])),
            self._test_type_to_text(assessment.get("test_type", "")),
        ]
        return " ".join(parts).lower().strip()
    
    def _test_type_to_text(self, test_type: str) -> str:
        """Convert test type code to readable text. Handles comma-separated values."""
        mapping = {
            "P": "personality",
            "K": "knowledge",
            "A": "ability reasoning",
            "S": "situational judgment",
            "O": "other"
        }
        
        # Handle comma-separated test types (e.g., "P,A,K")
        if not test_type:
            return ""
        
        if ',' in test_type:
            types = [t.strip() for t in test_type.split(',')]
            readable = [mapping.get(t, "") for t in types]
            return " ".join([r for r in readable if r])  # Filter empty strings
        
        return mapping.get(test_type, "")
    
    def save_processed_catalog(self) -> None:
        """Save processed catalog to JSON."""
        os.makedirs(os.path.dirname(self.processed_catalog_path), exist_ok=True)
        with open(self.processed_catalog_path, 'w', encoding='utf-8') as f:
            json.dump(self.processed_catalog, f, indent=2, ensure_ascii=False)
        print(f"Processed catalog saved to {self.processed_catalog_path}")
    
    def generate_embeddings(self) -> np.ndarray:
        """
        Generate embeddings for all assessments using sentence-transformers.
        Returns array of embeddings.
        """
        # Crash protection: validate processed catalog
        if not self.processed_catalog:
            raise ValueError("Processed catalog is empty. Call process_catalog() first.")
        
        texts = [item["searchable_text"] for item in self.processed_catalog]
        
        # Crash protection: validate searchable texts
        if not texts:
            raise ValueError("No searchable texts found in processed catalog.")
        
        print(f"Generating embeddings for {len(texts)} assessments...")
        print(f"Debug - First assessment: {self.processed_catalog[0]}")
        
        self.embeddings = self.model.encode(texts, show_progress_bar=True)
        
        print(f"Embeddings shape: {self.embeddings.shape}")
        return self.embeddings
    
    def save_embeddings_and_metadata(self, 
                                     vectorstore_path: str = "vectorstore") -> None:
        """Save FAISS index and metadata."""
        os.makedirs(vectorstore_path, exist_ok=True)
        
        if self.embeddings is None:
            raise ValueError("Embeddings not generated. Call generate_embeddings() first.")
        
        # Validate embeddings shape before FAISS creation
        if len(self.embeddings.shape) != 2:
            raise ValueError(f"Embeddings shape invalid: expected 2D array, got shape {self.embeddings.shape}")
        
        # Create FAISS index
        dimension = self.embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(self.embeddings.astype(np.float32))
        
        # Save FAISS index
        index_path = os.path.join(vectorstore_path, "faiss.index")
        faiss.write_index(index, index_path)
        print(f"FAISS index saved to {index_path}")
        
        # Save metadata
        metadata = {
            "assessments": self.processed_catalog,
            "num_embeddings": len(self.processed_catalog),
            "embedding_dimension": dimension,
            "model": "all-MiniLM-L6-v2"
        }
        
        metadata_path = os.path.join(vectorstore_path, "metadata.pkl")
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)
        print(f"Metadata saved to {metadata_path}")
    
    def run_full_pipeline(self, vectorstore_path: str = "vectorstore") -> None:
        """Execute full processing pipeline."""
        print("Starting catalog processing pipeline...")
        
        print("\n1. Processing raw catalog...")
        self.process_catalog()
        self.save_processed_catalog()
        
        print("\n2. Generating embeddings...")
        self.generate_embeddings()
        
        print("\n3. Creating FAISS index...")
        self.save_embeddings_and_metadata(vectorstore_path)
        
        print("\nPipeline complete!")


if __name__ == "__main__":
    processor = CatalogProcessor()
    processor.run_full_pipeline()
