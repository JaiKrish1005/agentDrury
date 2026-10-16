import time
import traceback
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from src.vector_store import vector_manager
from src.agent import commentary_agent
from src.memory import match_memory

app = FastAPI(
    title="Real-Time Football Commentary & Insight Engine",
    version="1.0.0",
    description="Turn football events into EA FC-style commentary scripts with AI insights."
)

class EventPayload(BaseModel):
    type: str
    minute: int
    team: str
    player: str
    target_player: Optional[str] = None
    outcome: str
    zone: str

class CommentaryRequest(BaseModel):
    match_id: str
    event: EventPayload
    score: Optional[Dict[str, int]] = None

@app.post("/commentary")
def generate_commentary_endpoint(payload: CommentaryRequest):
    start_time = time.time()
    try:
        match_id = payload.match_id
        event_dict = payload.event.model_dump()
        
        match_state = match_memory.get_match(match_id)
        if payload.score:
            match_state["score"] = payload.score

        excluded_ids = match_state.get("cards_history", [])
        scenario = vector_manager.retrieve_scenario(event_dict, excluded_card_ids=excluded_ids)
        
        base_line = scenario["base_line"]
        card_id = scenario["card_id"]

        formatted_base_line = base_line.format(
            player=event_dict.get("player", "Player"),
            target=event_dict.get("target_player", "opponent")
        )

        final_line, source = commentary_agent.generate_commentary(
            event=event_dict,
            base_line=formatted_base_line,
            match_state=match_state
        )

        match_memory.update_match(
            match_id=match_id,
            event=event_dict,
            spoken_line=final_line,
            card_id=card_id,
            score=payload.score
        )

        latency_ms = int((time.time() - start_time) * 1000)

        return {
            "match_id": match_id,
            "script": [
                {"speaker": "commentator", "line": final_line}
            ],
            "card_id": card_id,
            "source": source,
            "latency_ms": latency_ms
        }

    except Exception as e:
        print("--- ERROR IN /commentary ENDPOINT ---")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "football-commentary-engine"}