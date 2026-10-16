import requests
import json
import time

API_URL = "http://127.0.0.1:8000/commentary"

DEMO_EVENTS = [
    {
        "match_id": "derby_match_01",
        "score": {"home": 0, "away": 0},
        "event": {
            "type": "tackle",
            "minute": 12,
            "team": "Team A",
            "player": "Player A",
            "target_player": "Player B",
            "outcome": "won",
            "zone": "midfield"
        }
    },
    {
        "match_id": "derby_match_01",
        "score": {"home": 0, "away": 0},
        "event": {
            "type": "foul",
            "minute": 24,
            "team": "Team B",
            "player": "Player C",
            "target_player": "Player A",
            "outcome": "committed",
            "zone": "defensive_third"
        }
    },
    {
        "match_id": "derby_match_01",
        "score": {"home": 0, "away": 0},
        "event": {
            "type": "save",
            "minute": 41,
            "team": "Team A",
            "player": "Player D",
            "target_player": "Player C",
            "outcome": "saved",
            "zone": "box"
        }
    },
    {
        "match_id": "derby_match_01",
        "score": {"home": 1, "away": 0},
        "event": {
            "type": "goal",
            "minute": 78,
            "team": "Team A",
            "player": "Player A",
            "target_player": "None",
            "outcome": "scored",
            "zone": "box"
        }
    }
]

def run_demo():
    print("\nSTARTING LIVE COMMENTARY DEMO SIMULATION...\n" + "="*50)
    
    for idx, payload in enumerate(DEMO_EVENTS, 1):
        event = payload["event"]
        print(f"\n[Minute {event['minute']}'] Event #{idx}: {event['type'].upper()} ({event['player']} vs {event.get('target_player', 'None')})")
        
        try:
            response = requests.post(API_URL, json=payload)
            if response.status_code == 200:
                data = response.json()
                script_line = data["script"][0]["line"]
                source = data["source"]
                latency = data["latency_ms"]
                
                print(f"🎙️  Commentator: \"{script_line}\"")
                print(f"   [Source: {source.upper()} | Latency: {latency}ms | Card ID: {data['card_id']}]")
            else:
                print(f" Error {response.status_code}: {response.text}")
        except requests.exceptions.ConnectionError:
            print(" Error: Could not connect to FastAPI server. Make sure uvicorn is running!")
            break
            
        # Small pause between events for dramatic effect during demo
        time.sleep(5)
        
    print("\n" + "="*50 + "\nDEMO SIMULATION COMPLETED SUCCESSFULLY!\n")

if __name__ == "__main__":
    run_demo()