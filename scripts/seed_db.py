import json
import os
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer

def seed_database():
    db_path = "./chroma_db"
    client = PersistentClient(path=db_path)

    model = SentenceTransformer("all-MiniLM-L6-v2")

    collection_name = "scenario_bank"
    try:
        client.delete_collection(collection_name)
    except Exception:
        pass
    
    collection = client.get_or_create_collection(name=collection_name)

    json_path = os.path.join("data","scenario_bank.json")
    if not os.path.exists(json_path):
        print("Error path not found")
        return
    
    with open(json_path, "r") as f:
        cards = json.load(f)
    
    ids = []
    documents = []
    metadatas = []

    for card in cards:
        card_id = card["card_id"]
        header = card["header"]
        base_line = card["base_line"]

        doc_text = f"Type: {header['event_type']} | Outcome: {header['outcome']} | Zone: {header['zone']} | Line: {base_line}"
        ids.append(card_id)
        documents.append(doc_text)
        metadatas.append({
            "event_type": header["event_type"],
            "outcome": header["outcome"],
            "zone": header["zone"],
            "intensity": header["intensity"],
            "tone": header["tone"],
            "baseline": base_line
        })

        embeddings = model.encode(documents).tolist()

        collection.add(
            ids = ids,
            embeddings = embeddings,
            documents = documents,
            metadatas = metadatas
        )

        print("Successfully seeded cards into chromaDB")

if __name__ == "__main__":
    seed_database()


