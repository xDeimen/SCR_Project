from furhat_remote_api import FurhatRemoteAPI

def run_interaction():
    # Connect to Furhat
    furhat = FurhatRemoteAPI("10.88.143.249")
    print("✓ Connected")
    
    # Get system information including microphone
    try:
        system_info = furhat.furhat_get()
        print(f"\n=== System Information ===")
        print(f"Full system info: {system_info}")
        print(f"System info type: {type(system_info)}")
        print(f"System info dir: {dir(system_info)}")
        
        # Try to extract microphone info
        if hasattr(system_info, 'microphone'):
            print(f"Microphone: {system_info.microphone}")
        if hasattr(system_info, 'audio_input'):
            print(f"Audio Input: {system_info.audio_input}")
        if hasattr(system_info, 'to_dict'):
            print(f"System info dict: {system_info.to_dict()}")
    except Exception as e:
        print(f"Error getting system info: {e}")

    # Check current users to see if someone is detected
    try:
        users = furhat.get_users()
        print(f"\n=== Users ===")
        print(f"Users detected: {users}")
    except Exception as e:
        print(f"Error getting users: {e}")

    # Attend & speak
    furhat.attend(user="CLOSEST")
    furhat.say(text="Hi! Please say something.", blocking=True)

    print("\n🎤 Listening... (this will block until speech is detected)\n")

    # Call listen without parameters - it's a blocking call
    try:
        result = furhat.listen()
        
        print(f"\n=== Listen Result ===")
        print(f"Listen result type: {type(result)}")
        print(f"Listen result: {result}")
        
        if result:
            print(f"Listen result dir: {dir(result)}")
            
            # Try different ways to extract text
            if hasattr(result, 'message'):
                speech_text = result.message
                print(f"\n✓ You said (from message): {speech_text}")
                furhat.say(text=f"You said: {speech_text}")
            elif hasattr(result, 'text'):
                speech_text = result.text
                print(f"\n✓ You said (from text): {speech_text}")
                furhat.say(text=f"You said: {speech_text}")
            elif isinstance(result, str):
                print(f"\n✓ You said (string): {result}")
                furhat.say(text=f"You said: {result}")
            elif hasattr(result, 'to_dict'):
                result_dict = result.to_dict()
                print(f"\n✓ Result dict: {result_dict}")
                if 'message' in result_dict:
                    furhat.say(text=f"You said: {result_dict['message']}")
                else:
                    print(f"Available keys in result: {result_dict.keys()}")
            else:
                print(f"\n⚠ Unknown result format: {result}")
                # Try to convert to string and see what we get
                print(f"Result as string: {str(result)}")
                furhat.say(text="I detected something but couldn't understand it.")
        else:
            print("⚠ No speech detected (None returned)")
            furhat.say(text="I did not hear anything.")
            
    except Exception as e:
        print(f"Error during listening: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        furhat.say(text="Sorry, there was an error.")


if __name__ == "__main__":
    run_interaction()