from interface import LLMInterface

if __name__ == "__main__":
    # Set mocked=False to test actual history
    print("Sending request to Gemini...")
    llm_interface = LLMInterface(mocked=True) 
    
    # Turn 1
    print("\n--- User: Hi, I am John. ---")
    reply1 = llm_interface.get_response("Hi, I am John. Where is the restroom?")
    print(f"Furhat: {reply1}")

    # Turn 2 (Testing History)
    print("\n--- User: What was my name? ---")
    reply2 = llm_interface.get_response("What was my name?")
    print(f"Furhat: {reply2}")