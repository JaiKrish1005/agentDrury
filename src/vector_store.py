import os
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer

class VectorStoreManager:
    def __init__(self):
        self.client = PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection(name="scenario_bank")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def retrieve_scenario(self, event: dict, excluded_card_ids: list = None) -> dict:
        if excluded_card_ids is None:
            excluded_card_ids = []

        query_text = f"Type: {event.get('type')} | Outcome: {event.get('outcome')} | Zone: {event.get('zone')}"
        query_embedding = self.model.encode([query_text]).tolist()

        where_filter = {
            "event_type": event.get("type")
        }

        try:
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=3,
                where=where_filter
            )
        except Exception:
            results = None

        if not results or not results.get("ids") or not results["ids"][0]:
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=3
            )

        if not results or not results.get("ids") or not results["ids"][0]:
            return {
                "card_id": "default_01",
                "base_line": "{player} takes action in the {zone}.",
                "tone": "calm"
            }

        ids = results["ids"][0]
        metadatas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(ids)

        for card_id, metadata in zip(ids, metadatas):
            if card_id not in excluded_card_ids:
                metadata = metadata or {}
                base_line = metadata.get("base_line", "{player} makes a move.")
                return {
                    "card_id": card_id,
                    "base_line": base_line,
                    "tone": metadata.get("tone", "calm")
                }

        first_metadata = metadatas[0] if metadatas else {}
        return {
            "card_id": ids[0],
            "base_line": first_metadata.get("base_line", "{player} makes a move."),
            "tone": first_metadata.get("tone", "calm")
        }

vector_manager = VectorStoreManager()