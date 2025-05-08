## pip install google-genai==0.3.0

import asyncio
import json
import os
import pyaudio
from google import genai
import base64
from dotenv import load_dotenv

# Audio configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 1024

# Load API key from environment
load_dotenv()
MODEL = "gemini-2.0-flash-live-001"

client = genai.Client(
    http_options={
        'api_version': 'v1alpha',
    }
)

# Mock function for set_light_values
def set_light_values(brightness, color_temp):
    return {
        "brightness": brightness,
        "colorTemperature": color_temp,
    }

# Define the tool (function)
tool_set_light_values = {
    "function_declarations": [
        {
            "name": "set_light_values",
            "description": "Set the brightness and color temperature of a room light.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "brightness": {
                        "type": "NUMBER",
                        "description": "Light level from 0 to 100. Zero is off and 100 is full brightness"
                    },
                    "color_temp": {
                        "type": "STRING",
                        "description": "Color temperature of the light fixture, which can be `daylight`, `cool` or `warm`."
                    }
                },
                "required": ["brightness", "color_temp"]
            }
        }
    ]
}

class AudioLoop:
    def __init__(self):
        self.audio_in_queue = None
        self.out_queue = None
        self.session = None
        self.send_text_task = None
        self.receive_audio_task = None
        self.play_audio_task = None
        self.pya = pyaudio.PyAudio()

    async def send_text(self):
        while True:
            text = await asyncio.to_thread(
                input,
                "message > ",
            )
            if text.lower() == "q":
                break
            await self.session.send(input=text or ".", end_of_turn=True)

    async def listen_audio(self):
        mic_info = self.pya.get_default_input_device_info()
        self.audio_stream = await asyncio.to_thread(
            self.pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=SEND_SAMPLE_RATE,
            input=True,
            input_device_index=mic_info["index"],
            frames_per_buffer=CHUNK_SIZE,
        )
        if __debug__:
            kwargs = {"exception_on_overflow": False}
        else:
            kwargs = {}
        while True:
            data = await asyncio.to_thread(self.audio_stream.read, CHUNK_SIZE, **kwargs)
            await self.session.send({"mime_type": "audio/pcm", "data": data})

    async def receive_from_gemini(self):
                    while True:
                        try:
                async for response in self.session.receive():
                                if response.server_content is None:
                                    if response.tool_call is not None:
                                           print(f"Tool call received: {response.tool_call}")
                                           function_calls = response.tool_call.function_calls
                                           function_responses = []

                                           for function_call in function_calls:
                                                 name = function_call.name
                                                 args = function_call.args
                                                 call_id = function_call.id

                                                 if name == "set_light_values":
                                                      try:
                                                          result = set_light_values(int(args["brightness"]), args["color_temp"])
                                        function_responses.append({
                                                                 "name": name,
                                                                 "response": {"result": result},
                                                                 "id": call_id  
                                        })
                                        print(f"Function executed: {result}")
                                                      except Exception as e:
                                                          print(f"Error executing function: {e}")
                                                          continue

                            await self.session.send(function_responses)
                                           continue

                                model_turn = response.server_content.model_turn
                                if model_turn:
                                    for part in model_turn.parts:
                                        if hasattr(part, 'text') and part.text is not None:
                                print(part.text)
                                        elif hasattr(part, 'inline_data') and part.inline_data is not None:
                                if part.inline_data.mime_type == "audio/pcm":
                                    await self.audio_in_queue.put(part.inline_data.data)
                                print("Audio received")

                                if response.server_content.turn_complete:
                                    print('\n<Turn complete>')

                except Exception as e:
                      print(f"Error receiving from Gemini: {e}")
                break

    async def play_audio(self):
        stream = await asyncio.to_thread(
            self.pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=RECEIVE_SAMPLE_RATE,
            output=True,
        )
        while True:
            bytestream = await self.audio_in_queue.get()
            await asyncio.to_thread(stream.write, bytestream)

    async def run(self):
        try:
            config = {
                "tools": [tool_set_light_values],
                "response_modalities": ["audio", "text"],
                "speech_config": {
                    "voice_config": {
                        "prebuilt_voice_config": {
                            "voice_name": "Leda"
                        }
                    }
                }
            }

            async with (
                client.aio.live.connect(model=MODEL, config=config) as session,
                asyncio.TaskGroup() as tg,
            ):
                self.session = session
                self.audio_in_queue = asyncio.Queue()
                self.out_queue = asyncio.Queue(maxsize=5)

                send_text_task = tg.create_task(self.send_text())
                tg.create_task(self.listen_audio())
                tg.create_task(self.receive_from_gemini())
                tg.create_task(self.play_audio())

                await send_text_task
                raise asyncio.CancelledError("User requested exit")

        except asyncio.CancelledError:
            pass
    except Exception as e:
            print(f"Error in main loop: {e}")
            if hasattr(self, 'audio_stream'):
                self.audio_stream.close()
    finally:
            self.pya.terminate()

if __name__ == "__main__":
    main = AudioLoop()
    asyncio.run(main.run())