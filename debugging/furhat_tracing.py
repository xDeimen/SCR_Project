import time
import furhat_remote_api
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


def get_speaking_user(users):
    """
    Find the user who is currently speaking or most recently spoke.
    """
    if not users:
        return None
    
    # Check for user with speech activity
    for user in users:
        # Check if user has speech-related attributes
        if hasattr(user, 'speech') and user.speech:
            print(f"Found speaking user: {user.id}")
            return user
        # Some APIs use 'isSpeaking' attribute
        if hasattr(user, 'isSpeaking') and user.isSpeaking:
            print(f"Found speaking user: {user.id}")
            return user
    
    # If no one is actively speaking, return the closest user (first in list)
    return users[0]


def conversation_loop():
    current_user_id = None
    
    # Get users in the scene and attend to the closest one initially
    try:
        users = furhat.get_users()
        print(f"Users detected: {len(users)}")
        
        if users:
            # Attend to the first/closest user initially
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
        
        # Get all users currently in frame
        try:
            users = furhat.get_users()
            print(f"Users in frame: {len(users)}")
            
            if users:
                # Find the user who is speaking or should be attended to
                target_user = get_speaking_user(users)
                
                if target_user:
                    user_id = target_user.id if hasattr(target_user, 'id') else target_user
                    
                    # Only switch attention if it's a different user
                    if user_id != current_user_id:
                        print(f"Switching attention from {current_user_id} to {user_id}")
                        furhat.attend(userid=user_id)
                        current_user_id = user_id
                    else:
                        print(f"Continuing to track user: {user_id}")
                        furhat.attend(userid=user_id)
        except Exception as e:
            print(f"Could not update attention: {e}")
        
        response = furhat.listen()

        # After listening, check for the speaking user and attend to them BEFORE responding
        try:
            users = furhat.get_users()
            if users and response and response.message:
                # The person who just spoke should be attended to
                target_user = get_speaking_user(users)
                if target_user:
                    user_id = target_user.id if hasattr(target_user, 'id') else target_user
                    if user_id != current_user_id:
                        print(f"Speaker detected! Switching to user: {user_id}")
                        furhat.attend(userid=user_id)
                        current_user_id = user_id
                        time.sleep(0.2)  # Brief pause to ensure attention is updated
                    else:
                        print(f"Already attending to speaker: {user_id}")
        except Exception as e:
            print(f"Could not attend to speaker: {e}")

        if response and response.message:
            user_input = response.message.lower()
            print(f"User said: {user_input}")

            if "goodbye" in user_input or "bye" in user_input:
                # Make sure we're looking at the person before saying goodbye
                try:
                    users = furhat.get_users()
                    if users:
                        target_user = get_speaking_user(users)
                        if target_user:
                            user_id = target_user.id if hasattr(target_user, 'id') else target_user
                            furhat.attend(userid=user_id)
                            time.sleep(0.2)
                except:
                    pass
                
                furhat.say(text="Goodbye! It was nice talking to you.", blocking=True)
                break

            # Attend to the speaker before responding
            try:
                users = furhat.get_users()
                if users:
                    target_user = get_speaking_user(users)
                    if target_user:
                        user_id = target_user.id if hasattr(target_user, 'id') else target_user
                        furhat.attend(userid=user_id)
                        time.sleep(0.2)  # Brief pause to ensure we're looking at them
            except:
                pass

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