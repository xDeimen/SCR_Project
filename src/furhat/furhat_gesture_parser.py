from enum import Enum
from furhat_remote_api import FurhatRemoteAPI
import re

# --- CONFIGURATION ---
ROBOT_IP = "localhost" 

class FacialExpressions(Enum):
    smile = "[Smile]"
    nod = "[Nod]"
    concern = "[Concern]"
    wink = "[Wink]"
    neutral = "[Neutral]"

GESTURE_MAP = {
    FacialExpressions.smile: "BigSmile",
    FacialExpressions.nod: "Nod",       
    FacialExpressions.concern: "ExpressSad", 
    FacialExpressions.wink: "Wink",
    FacialExpressions.neutral: "ExpressNeutral" 
}

class FurhatGestureParser:
    def __init__(self, furhat: FurhatRemoteAPI):
        self.furhat = furhat

    def parse_sequence_and_perform(self, raw_llm_response: str):
        """
        Splits text by tags and executes them in order.
        Input: "Hello! [Smile] I have bad news. [Concern]"
        """
        # 1. Regex to find all tags
        tag_pattern = "|".join([re.escape(e.value) for e in FacialExpressions])
        
        # 2. Split text, keeping tags as delimiters
        segments = re.split(f"({tag_pattern})", raw_llm_response, flags=re.IGNORECASE)

        current_text_buffer = ""
        
        for segment in segments:
            # Check if this segment is a known Tag
            found_tag = None
            for expr in FacialExpressions:
                if segment.lower() == expr.value.lower():
                    found_tag = expr
                    break
            
            if found_tag:
                # --- A Tag was found ---
                
                # 1. Speak whatever text we have accumulated so far (BLOCKING)
                # We must finish speaking before doing the gesture
                if current_text_buffer.strip():
                    print(f"🗣️ Speaking: {current_text_buffer}")
                    self.furhat.say(text=current_text_buffer, blocking=True)
                    current_text_buffer = "" # Clear buffer

                # 2. Perform the gesture (NON-BLOCKING usually, but instantaneous)
                self.execute_gestures([found_tag]) 
                
            else:
                # --- It is just text ---
                current_text_buffer += segment

        # 3. Speak any remaining text after the last tag
        if current_text_buffer.strip():
             print(f"🗣️ Speaking: {current_text_buffer}")
             self.furhat.say(text=current_text_buffer, blocking=True)

    def execute_gestures(self, gestures):
        """
        Sends actual commands to the Furhat robot via the API instance.
        """
        if not gestures:
            return

        for gesture in gestures:
            try:
                # Check if gesture exists in map before sending
                if gesture in GESTURE_MAP:
                    print(f"🤖 [API]: Sending '{GESTURE_MAP[gesture]}'")
                    self.furhat.gesture(name=GESTURE_MAP[gesture])
                else:
                    print(f"⚠️ Warning: Gesture {gesture} not found in map.")
                    
            except Exception as e:
                print(f"⚠️ API Error for gesture {gesture}: {e}")

# --- INTEGRATION EXAMPLE ---

if __name__ == "__main__":
    # 1. Connect
    try:
        furhat_connection = FurhatRemoteAPI(ROBOT_IP)
        print(f"✅ Connected to Furhat at {ROBOT_IP}")
    except Exception as e:
        print(f"❌ Could not connect: {e}")
        furhat_connection = None # Handle offline mode if needed

    if furhat_connection:
        # 2. Initialize Parser
        parser = FurhatGestureParser(furhat_connection)

        # 3. Simulate Complex LLM Response
        llm_output = "[Smile] Welcome! [Nod] It is great to see you. [Concern] Oh wait, looking at the schedule..."
        print(f"\n--- Processing: '{llm_output}' ---")
        
        # 4. EXECUTE SEQUENCE
        # This function now handles the loop of "Speak -> Gesture -> Speak"
        parser.parse_sequence_and_perform(llm_output)
        
        print("\n✅ Sequence Complete.")