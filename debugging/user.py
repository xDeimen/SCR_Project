import time
import furhat_remote_api
from furhat_remote_api import FurhatRemoteAPI

# Furhat Robot IP
FURHAT_IP = "10.88.143.249"
furhat = FurhatRemoteAPI(FURHAT_IP)


def debug_users():
    """
    Debug function to see all user attributes and understand speech detection
    """
    users = furhat.get_users()
    print(f"\n{'='*50}")
    print(f"Total users detected: {len(users)}")
    print(f"{'='*50}")
    
    for i, user in enumerate(users):
        print(f"\n--- User {i+1} ---")
        print(f"User ID: {user.id if hasattr(user, 'id') else 'No ID'}")
        
        # Print all attributes
        print("\nAll attributes:")
        for attr in dir(user):
            if not attr.startswith('_'):  # Skip private attributes
                try:
                    value = getattr(user, attr)
                    if not callable(value):  # Skip methods
                        print(f"  {attr}: {value}")
                except:
                    pass
        
        # Check common speech-related attributes
        speech_attrs = ['speech', 'isSpeaking', 'speaking', 'audioLevel', 
                       'voiceActivity', 'isAudioSource', 'audioEnergy']
        
        print("\nSpeech-related attributes:")
        for attr in speech_attrs:
            if hasattr(user, attr):
                print(f"  {attr}: {getattr(user, attr)}")


def conversation_loop():
    current_user_id = None
    
    # Initial user detection
    try:
        users = furhat.get_users()
        print(f"Users detected: {len(users)}")
        
        # DEBUG: See what user attributes are available
        if users:
            debug_users()
        
        if users:
            user_id = users[0].id if hasattr(users[0], 'id') else users[0]
            furhat.attend(userid=user_id)
            current_user_id = user_id
            print(f"Furhat is now attending to user: {user_id}")
        else:
            print("No users detected. Furhat will look forward.")
    except Exception as e:
        print(f"Error detecting/attending to users: {e}")
    
    furhat.say(text="Hello! I'm ready to chat. Say 'goodbye' when you want to stop.", blocking=True)
    time.sleep(0.4)

    while True:
        print("\nListening for input...")
        
        response = furhat.listen()

        # DEBUG: After someone speaks, check user attributes again
        try:
            users = furhat.get_users()
            if users and response and response.message:
                print("\n--- AFTER SPEECH DETECTED ---")
                debug_users()
        except Exception as e:
            print(f"Debug error: {e}")

        # ... rest of your code