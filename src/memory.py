class MatchMemoryStore:
    def __init__(self):
        self.store = {}

    def get_match(self, match_id: str) -> dict:
        if match_id not in self.store:
            self.store[match_id] = {
                "events_history": [],
                "lines_history": [],
                "cards_history": [],
                "score": {"home": 0, "away": 0}
            }
        return self.store[match_id]

    def update_match(self, match_id: str, event: dict, spoken_line: str, card_id: str, score: dict = None):
        match_state = self.get_match(match_id)
        
        if score:
            match_state["score"] = score
            
        match_state["events_history"].append(event)
        if len(match_state["events_history"]) > 5:
            match_state["events_history"].pop(0)
            
        match_state["lines_history"].append(spoken_line)
        if len(match_state["lines_history"]) > 5:
            match_state["lines_history"].pop(0)

        match_state["cards_history"].append(card_id)
        if len(match_state["cards_history"]) > 5:
            match_state["cards_history"].pop(0)

match_memory = MatchMemoryStore()