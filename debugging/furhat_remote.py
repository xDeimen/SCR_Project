import time
from furhat_remote_api import FurhatRemoteAPI

# Furhat Robot IP
FURHAT_IP = "localhost"
furhat = FurhatRemoteAPI(FURHAT_IP)

def speak_and_listen():
    """
    Make Furhat speak and then listen for user input without hearing itself.
    """
    try:
        print("Furhat is speaking...")

        # Important: blocking=True ensures Furhat finishes speaking
        furhat.say(text="Hello! I am Furhat. What would you like to talk about?", blocking=True)

        # Small delay to allow audio to settle before enabling the mic
        time.sleep(0.4)

        print("Furhat is now listening...")
        response = furhat.listen()  # No "avoid" on your version

        if response and response.message:
            user_input = response.message
            print(f"User said: {user_input}")

            furhat.say(text=f"You said: {user_input}. Thank you for talking with me!", blocking=True)
            time.sleep(0.4)

            return user_input
        else:
            print("No speech detected or listening timed out")
            furhat.say(text="I didn't hear anything. Please try again.", blocking=True)
            time.sleep(0.4)

            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def conversation_loop():
    # Get users in the scene and attend to the closest one
    try:
        users = furhat.get_users()
        print(f"Users detected: {users}")
        
        if users:
            # Try to attend to the first/closest user using their ID
            user_id = users[0].id if hasattr(users[0], 'id') else users[0]
            furhat.attend(userid=user_id)
            print(f"Furhat is now attending to user: {user_id}")
        else:
            print("No users detected. Furhat will look forward.")
    except Exception as e:
        print(f"Error detecting/attending to users: {e}")
    
    furhat.say(text="Hello! I'm ready to chat. Say 'goodbye' when you want to stop.", blocking=True)
    time.sleep(0.4)

    while True:
        print("\nListening for input...")
        
        # Update attention to track the user before each interaction
        try:
            users = furhat.get_users()
            if users:
                user_id = users[0].id if hasattr(users[0], 'id') else users[0]
                furhat.attend(userid=user_id)
                print(f"Tracking user: {user_id}")
        except Exception as e:
            print(f"Could not update attention: {e}")
        
        response = furhat.listen()

        if response and response.message:
            user_input = response.message.lower()
            print(f"User said: {user_input}")

            if "shut up" in user_input or "bye" in user_input:
                furhat.say(text="Sorry boss", blocking=True)
                break

            furhat.say(text=f"I heard you say: {user_input}", blocking=True)
            time.sleep(0.4)

        else:
            print("No speech detected")
            furhat.say(text="I didn't catch that. Could you repeat?", blocking=True)
            time.sleep(0.4)


if __name__ == "__main__":
    print("Starting Furhat interaction...")
    conversation_loop()
    print("Furhat interaction completed.")