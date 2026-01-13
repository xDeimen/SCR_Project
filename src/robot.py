import time
import random
from enum import Enum, auto
from furhat_remote_api import FurhatRemoteAPI
from furhat.gesture_parser import FurhatGestureParser
from furhat.config import FurhatConfig
from llm.interface import LLMInterface

class RobotState(Enum):
    LISTENING = auto()
    TALKING = auto()
    IDLE = auto()
    STOP = auto()

class RobotController:
    def __init__(self, config: FurhatConfig, llm: LLMInterface):
        # 1. Setup Robot
        self.furhat = FurhatRemoteAPI(config.ip_address)
        config.apply_to(self.furhat)
        
        # 2. Components
        self.parser = FurhatGestureParser(self.furhat)
        self.llm = llm
        
        # 3. State Management
        self.current_state = RobotState.LISTENING
        self.last_interaction_time = time.time()
        self.idle_timeout = 60.0 
        self.is_running = True

        # 4. Idle Settings
        self.idle_gestures = ["LookAround", "Oh", "Wink", "Smile"]
        self.last_idle_anim_time = time.time()

    def run(self):
        """Main State Machine Loop"""
        print(f"🤖 Robot System Started. Initial State: {self.current_state.name}")
        
        # Initial greeting
        intro = "Hello! [Smile] I am ready to chat. Please step closer."
        self.parser.parse_sequence_and_perform(intro)
        
        # Buffer after speaking before logic starts
        time.sleep(0.5)

        STATE_MAP = {
            RobotState.LISTENING: self._handle_listening,
            RobotState.TALKING: self._handle_talking,
            RobotState.IDLE: self._handle_idle,
            RobotState.STOP: self._handle_stop
        }

        while self.is_running:
            handle_function = STATE_MAP[self.current_state]
            handle_function()
            time.sleep(0.05)

    def _update_attention(self):
        """
        Crucial: Tells Furhat to physically look at the user.
        This aligns the directional microphones for better audio capture.
        """
        try:
            users = self.furhat.get_users()
            if users:
                # Attend to the closest/first user
                # Handle both object and dict implementations of user
                user_id = users[0].id if hasattr(users[0], 'id') else users[0]
                self.furhat.attend(userid=user_id)
            else:
                # If no one is there, look forward (neutral)
                # self.furhat.attend(location="Unknown") # Optional: Reset gaze
                pass
        except Exception as e:
            # Don't crash the whole robot if tracking fails
            print(f"⚠️ Tracking Warning: {e}")

    def _handle_listening(self):
        # 1. Check Timeout
        if time.time() - self.last_interaction_time > self.idle_timeout:
            print("⏳ Idle timeout reached. Switching to IDLE state.")
            self.current_state = RobotState.IDLE
            return

        # 2. PRE-LISTEN SETUP (From your working code)
        self._update_attention() # Look at the user first!
        time.sleep(0.4)          # Let audio settle so we don't hear echoes

        print("👂 Listening...")
        try:
            # 3. Listen
            result = self.furhat.listen() 
            
            # 4. Process Result
            user_input = ""
            if result and hasattr(result, 'message') and result.message:
                user_input = result.message

            if user_input:
                print(f"👤 User said: '{user_input}'")
                self.last_interaction_time = time.time() 
                
                if self._is_goodbye(user_input):
                    self.current_state = RobotState.STOP
                else:
                    self.user_input_buffer = user_input
                    self.current_state = RobotState.TALKING
            else:
                # Silence detected - Loop back to try again
                pass

        except Exception as e:
            print(f"⚠️ Mic Error: {e}")
            time.sleep(1.0) # Safety pause if things are crashing

    def _handle_talking(self):
        print("🧠 Processing response...")
        
        # 1. Get LLM Response
        response_text = self.llm.get_response(self.user_input_buffer)
        
        # 2. Speak & Act (Parser handles blocking=True)
        self.parser.parse_sequence_and_perform(response_text)
        
        # 3. Return to listening
        self.current_state = RobotState.LISTENING

    def _handle_idle(self):
        # 1. Random Animation (Every 10s)
        if time.time() - self.last_idle_anim_time > 10.0:
            gesture = random.choice(self.idle_gestures)
            print(f"💤 Idle Animation: {gesture}")
            try:
                self.furhat.gesture(name=gesture)
            except:
                pass
            self.last_idle_anim_time = time.time()

        # 2. Check for users (Wake up if someone walks in)
        self._update_attention() 

        # 3. Passive Listen (Wake up word check)
        # We use a shorter sleep here because we aren't in a rapid convo flow
        time.sleep(0.2) 
        
        try:
            result = self.furhat.listen()
            user_input = result.message if (result and hasattr(result, 'message')) else ""

            if user_input:
                print(f"⏰ Waking up! User said: {user_input}")
                self.last_interaction_time = time.time()
                
                if self._is_goodbye(user_input):
                    self.current_state = RobotState.STOP
                else:
                    self.user_input_buffer = user_input
                    self.current_state = RobotState.TALKING
        except Exception:
            pass

    def _handle_stop(self):
        print("🛑 Stopping conversation.")
        final_message = "Alright. Goodbye for now! [Smile]"
        self.parser.parse_sequence_and_perform(final_message)
        
        self.llm.clear_history()
        self.is_running = False

    def _is_goodbye(self, text: str) -> bool:
        triggers = ["goodbye", "bye", "see you", "shut up", "exit"]
        return any(trigger in text.lower() for trigger in triggers)

# --- Main Execution ---
if __name__ == "__main__":
    # Initialize your config
    config = FurhatConfig(
        ip_address="localhost", 
        voice_name="Matthew",
        character_name="James", 
        mask_type="Adult"
    )
    
    # Initialize your LLM
    llm = LLMInterface(mocked=True) 

    # Start Controller
    bot = RobotController(config, llm)
    bot.run()