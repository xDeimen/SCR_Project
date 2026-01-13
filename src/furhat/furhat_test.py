from furhat_remote_api  import FurhatRemoteAPI
from furhat_config import FurhatConfig
from furhat_gesture_parser import FurhatGestureParser


if __name__ == "__main__":
    
    config = FurhatConfig(
        ip_address="localhost",
        voice_name="Joanna",
        character_name="Patricia"
    )

    furhat = FurhatRemoteAPI(config.ip_address)

    config.apply_to(furhat)

    parser = FurhatGestureParser(furhat)
    
    llm_output = "[Smile] Systems are online. [Nod] I am ready to help."
    parser.parse_sequence_and_perform(llm_output)