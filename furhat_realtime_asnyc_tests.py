import asyncio
from furhat_realtime_api import AsyncFurhatClient

async def run_interaction():

    furhat = AsyncFurhatClient("localhost")
    await furhat.connect()
    print("✓ Connected")

    speech_data = {"text": None, "received": False}

    # ---- Correct event names based on API documentation ----
    async def on_hear_end(event):
        """Called when user stops speaking and speech is recognized"""
        print("[EVENT] Speech recognized:", event)
        speech_data["text"] = event.get("text")
        speech_data["received"] = True

    async def on_hear_start(event):
        """Called when user starts speaking"""
        print("[EVENT] User started speaking")

    async def on_listen_start(event):
        """Called when robot starts listening"""
        print("[EVENT] Robot started listening")

    async def on_listen_end(event):
        """Called when robot stops listening"""
        print("[EVENT] Robot stopped listening, cause:", event.get("cause"))

    async def on_hear_partial(event):
        """Called for partial speech results (if enabled)"""
        print("[EVENT] Partial speech:", event.get("text"))

    # Register handlers with correct event names from API
    furhat.add_handler("response.hear.end", on_hear_end)
    furhat.add_handler("response.hear.start", on_hear_start)
    furhat.add_handler("response.listen.start", on_listen_start)
    furhat.add_handler("response.listen.end", on_listen_end)
    furhat.add_handler("response.hear.partial", on_hear_partial)

    # Attend & speak
    await furhat.request_attend_user("closest")
    await furhat.request_speak_text("Hi! Please say something.")

    await asyncio.sleep(2)

    print("\n🎤 Listening...\n")

    # ---- Correct listen request based on API documentation ----
    await furhat.send_event({
        "type": "request.listen.start",
        "partial": True,  # Get partial results while speaking
        "concat": True,  # Concatenate results
        "stop_no_speech": True,  # Stop if silent too long
        "stop_user_end": True,  # Stop when end-of-speech detected
        "no_speech_timeout": 8.0,  # Seconds
        "end_speech_timeout": 1.5  # Seconds of silence to detect end
    })

    # Wait for speech
    try:
        await asyncio.wait_for(
            wait_for_speech(speech_data),
            timeout=12
        )
    except asyncio.TimeoutError:
        print("⚠ No speech detected")
        await furhat.request_speak_text("I did not hear anything.")
        await furhat.disconnect()
        return

    print(f"\n✓ You said: {speech_data['text']}")
    await furhat.request_speak_text(f"You said: {speech_data['text']}")

    await furhat.disconnect()


async def wait_for_speech(speech_data):
    while not speech_data["received"]:
        await asyncio.sleep(0.05)


if __name__ == "__main__":
    asyncio.run(run_interaction())