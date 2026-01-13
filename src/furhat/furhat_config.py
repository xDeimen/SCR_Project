from dataclasses import dataclass
from furhat_remote_api import FurhatRemoteAPI

@dataclass
class FurhatConfig:
    """
    Central configuration for the Furhat Robot.
    """
    ip_address: str = "localhost"
    voice_name: str = "Matthew"       # Options: Matthew, Joanna, Amy, Brian
    character_name: str = "James"     # Options: James, Patricia, etc.
    mask_type: str = "Adult"          # Options: Adult, Child
    
    def apply_to(self, furhat: FurhatRemoteAPI):
        """
        Applies this configuration to a connected Furhat instance.
        """
        print(f"⚙️ [CONFIG] Applying settings to Furhat at {self.ip_address}...")
        
        try:
            # 1. Set Voice
            print(f"   -> Setting Voice: {self.voice_name}")
            furhat.set_voice(name=self.voice_name)
            
            # 2. Set Face/Mask
            print(f"   -> Setting Face: {self.character_name} ({self.mask_type})")
            furhat.set_face(character=self.character_name, mask=self.mask_type)
            
            # 3. Reset State
            furhat.gesture(name="ExpressNeutral")
            print("✅ [CONFIG] Setup Complete.")
            
        except Exception as e:
            print(f"❌ [CONFIG] Error applying settings: {e}")
            print("   (Ensure the robot is online and the voice/face names are valid)")