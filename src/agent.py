import os
import re
from google import genai
from dotenv import load_dotenv

load_dotenv()

class CommentaryAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if api_key else None

    def generate_commentary(self, event: dict, base_line: str, match_state: dict) -> tuple[str, str]:
        """
        Returns (script_line, source) where source is 'ai' or 'fallback'.
        """
        if not self.client:
            return base_line, "fallback"

        event_type = event.get("type", "").lower()
        minute = event.get("minute", 0)
        is_significant = event_type in ["goal", "card", "penalty", "save"] or minute >= 85

        prompt = f"""
You are a professional football match commentator. 
Your task is to rewrite the provided base line to match the specific event and match state naturally.

EVENT DETAILS:
- Type: {event.get('type')}
- Minute: {minute}'
- Team: {event.get('team')}
- Player: {event.get('player')}
- Target Player: {event.get('target_player', 'None')}
- Outcome: {event.get('outcome')}
- Zone: {event.get('zone')}

MATCH CONTEXT:
- Score: Home {match_state['score']['home']} - Away {match_state['score']['away']}
- Recent Events: {match_state['events_history'][-3:]}
- Recently Spoken Lines (DO NOT REUSE THESE PHRASES): {match_state['lines_history'][-3:]}

BASE LINE TO ADAPT:
"{base_line}"

RULES:
1. Use ONLY player names and numbers present in the input event. NEVER invent names, numbers, or stats.
2. Keep it to 1-2 sentences.
3. {"Add a short, punchy insight since this moment is significant." if is_significant else "Do not add extraneous insights; keep it concise."}
4. Return ONLY the final commentary text, with no extra conversational filler.
"""

        try:
            response = self.client.models.generate_content(
                model='gemini-3.8-flash',
                contents=prompt,
            )
            generated_line = response.text.strip().strip('"')
            
            if self._verify_names(generated_line, event):
                return generated_line, "ai"
            else:
                print("Validation check failed: Hallucinated name detected. Falling back.")
                return base_line, "fallback"

        except Exception as e:
            print(f"Gemini API Error/Rate limit: {e}. Falling back.")
            return base_line, "fallback"

    def _verify_names(self, output_text: str, event: dict) -> bool:
        """
        Checks if capitalized words/potential names in output text exist in the input event.
        """
        allowed_names = {str(event.get("player", "")), str(event.get("target_player", ""))}
        allowed_names = {n.lower() for n in allowed_names if n and n != "None"}
        
        words = re.findall(r'Player\s+[A-Za-z0-9]+', output_text)
        for w in words:
            if w.lower() not in [n.lower() for n in allowed_names]:
                return False
        return True

commentary_agent = CommentaryAgent()