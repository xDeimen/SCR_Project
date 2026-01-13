from dataclasses import dataclass
from furhat_remote_api import FurhatRemoteAPI

@dataclass
class FurhatConfig:
    """
    Central configuration for the Furhat Robot.
    """
    ip_address: str = "localhost"
    voice_name: str = "Matthew"
    character_name: str = "James"
    mask_type: str = "Adult"
    input_language: str = "en-US" 

    def apply_to(self, furhat: FurhatRemoteAPI):
        """
        Applies static settings (Voice/Face) to the robot.
        """
        print(f"⚙️ [CONFIG] Applying settings to Furhat at {self.ip_address}...")
        
        try:
            # 1. Set Voice (TTS)
            print(f"   -> Setting Voice: {self.voice_name}")
            furhat.set_voice(name=self.voice_name)
            
            # 2. Set Face (Mask)
            # This AUTOMATICALLY resets the face to a neutral expression.
            print(f"   -> Setting Face: {self.character_name}")
            furhat.set_face(character=self.character_name, mask=self.mask_type)
            
            # REMOVED: furhat.gesture(name="ExpressNeutral") 
            # This was causing the 400 error because the gesture doesn't exist.
            
            print("✅ [CONFIG] Setup Complete.")
            
        except Exception as e:
            print(f"❌ [CONFIG] Error applying settings: {e}")