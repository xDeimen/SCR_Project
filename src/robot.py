import time
import random
from enum import Enum, auto
from furhat_remote_api import FurhatRemoteAPI
from furhat.gesture_parser import FurhatGestureParser
from furhat.config import FurhatConfig
from llm.interface import LLMInterface
from dataclasses import dataclass, field

class RobotState(Enum):
    LISTENING = auto()
    TALKING = auto()
    IDLE = auto()
    STOP = auto()

@dataclass
class RobotConfig:
    IDLE_GESTURES: list = field(default_factory=lambda: ["LookAround", "Oh", "Wink", "Smile"])
    GOODBY_TRIGGERS: list = field(default_factory=lambda: ["goodbye", "bye", "see you", "shut up", "exit"])
    INITIAL_GREETING: str = "Hello! [Smile] I am ready to chat. Please step closer."
    FINAL_MESSAGE: str = "Alright. Goodbye for now! [Smile]"
    IDLE_TIMEOUT: int = 20
    RANDOM_IDLE_ANIMATION_INTERVAL: int = 5
    AFTER_SPEAKING_BUFFER: int  = 0.5
    CPU_BREAK_BUFFER: int  = 0.05
    PASSIVE_LISTEN_SLEEP: int = 0.2
    SAFETY_PAUSE_SLEEP: int = 1.0
    INITIAL_PRINT_STATEMENT: str = "🤖 Robot System Started. Initial State:"
    TRACKING_WARNING: str = "⚠️ Tracking Warning:"
    SWITCH_TO_IDLE: str = "⏳ Idle timeout reached. Switching to IDLE state."
    LISTENING: str = "👂 Listening..."
    USER_SAID: str = "👤 User said: "
    MIC_ERROR: str = "⚠️ Mic Error: " 
    PROCESSING_RESPONSE: str = "🧠 Processing response..."
    IDLE_ANIMATION: str = "💤 Idle Animation: "
    WAKING_UP: str = "⏰ Waking up! User said: "
    STOP: str = "🛑 Stopping conversation."

@dataclass
class Config:
    furhat: FurhatConfig
    llm: LLMInterface
    robot: RobotConfig

class RobotController:
    def __init__(self, config: Config):
        # 1. Setup Robot
        self.furhat = FurhatRemoteAPI(config.furhat.ip_address)
        config.furhat.apply_to(self.furhat)
        
        # 2. Components
        self.parser = FurhatGestureParser(self.furhat)
        self.llm = config.llm
        self.robot = config.robot
        
        # 3. State Management
        self.current_state = RobotState.LISTENING
        self.last_interaction_time = time.time()
        self.is_running = True

        # 4. Idle Settings
        self.last_idle_anim_time = time.time()

    def run(self):
        """Main State Machine Loop"""
        print(f"{self.robot.INITIAL_PRINT_STATEMENT} {self.current_state.name}")
    
        self.parser.parse_sequence_and_perform(self.robot.INITIAL_GREETING)
        
        time.sleep(self.robot.AFTER_SPEAKING_BUFFER)

        STATE_MAP = {
            RobotState.LISTENING: self._handle_listening,
            RobotState.TALKING: self._handle_talking,
            RobotState.IDLE: self._handle_idle,
            RobotState.STOP: self._handle_stop
        }

        while self.is_running:
            handle_function = STATE_MAP[self.current_state]
            handle_function()
            time.sleep(self.robot.CPU_BREAK_BUFFER)

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
            print(f"{self.robot.TRACKING_WARNING} {e}")

    def _handle_listening(self):
        # 1. Check Timeout
        if time.time() - self.last_interaction_time > self.robot.IDLE_TIMEOUT:
            print(self.robot.SWITCH_TO_IDLE)
            self.current_state = RobotState.IDLE
            return

        # 2. PRE-LISTEN SETUP (From your working code)
        self._update_attention() # Look at the user first!
        time.sleep(self.robot.AFTER_SPEAKING_BUFFER)

        print(self.robot.LISTENING)
        try:
            # 3. Listen
            result = self.furhat.listen() 
            
            # 4. Process Result
            user_input = ""
            if result and hasattr(result, 'message') and result.message:
                user_input = result.message

            if user_input:
                print(f"{self.robot.USER_SAID} '{user_input}'")
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
            print(f"{self.robot.MIC_ERROR} {e}")
            time.sleep(self.robot.SAFETY_PAUSE_SLEEP) # Safety pause if things are crashing

    def _handle_talking(self):
        print(self.robot.PROCESSING_RESPONSE)
        
        # 1. Get LLM Response
        response_text = self.llm.get_response(self.user_input_buffer)
        
        # 2. Speak & Act (Parser handles blocking=True)
        self.parser.parse_sequence_and_perform(response_text)
        
        # 3. Return to listening
        self.current_state = RobotState.LISTENING

    def _handle_idle(self):
        # 1. Random Animation (Every 10s)
        if time.time() - self.last_idle_anim_time > self.robot.RANDOM_IDLE_ANIMATION_INTERVAL:
            gesture = random.choice(self.robot.IDLE_GESTURES)
            print(f"{self.robot.IDLE_ANIMATION} {gesture}")
            try:
                self.furhat.gesture(name=gesture)
            except:
                pass
            self.last_idle_anim_time = time.time()

        # 2. Check for users (Wake up if someone walks in)
        self._update_attention() 

        # 3. Passive Listen (Wake up word check)
        time.sleep(self.robot.PASSIVE_LISTEN_SLEEP) 
        
        try:
            result = self.furhat.listen()
            user_input = result.message if (result and hasattr(result, 'message')) else ""

            if user_input:
                print(f"{self.robot.WAKING_UP} {user_input}")
                self.last_interaction_time = time.time()
                
                if self._is_goodbye(user_input):
                    self.current_state = RobotState.STOP
                else:
                    self.user_input_buffer = user_input
                    self.current_state = RobotState.TALKING
        except Exception:
            pass

    def _handle_stop(self):
        print(f"{self.robot.STOP}")
        self.parser.parse_sequence_and_perform(self.robot.FINAL_MESSAGE)
        
        self.llm.clear_history()
        self.is_running = False

    def _is_goodbye(self, text: str) -> bool:
        return any(trigger in text.lower() for trigger in self.robot.GOODBY_TRIGGERS)


if __name__ == "__main__":
    furhat_config = FurhatConfig(
        ip_address="localhost", 
        voice_name="Matthew",
        character_name="James", 
        mask_type="Adult"
    )
    llm_interface = LLMInterface(mocked=True)
    robot_config = RobotConfig()
    config = Config(furhat_config, llm_interface, robot_config)

    bot = RobotController(config)
    bot.run()

