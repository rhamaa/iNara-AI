# filepath: /home/firdaus/Documents/Projects/iNara-AI/livekit/main.py
from livekit import agents
from livekit.agents import AgentSession, BackgroundAudioPlayer, AudioConfig, Agent, RunContext, RoomInputOptions
from livekit.plugins import google, cartesia, deepgram, noise_cancellation, silero
# from livekit.plugins.turn_detector.multilingual import MultilingualModel
import asyncio
from dotenv import load_dotenv
from tools import lookup_user, lookup_schedule
import os


# Load environment variables from a .env file
load_dotenv()

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="Kamu adalah Nara, AI Agent yang berperan sebagai staf TU di Universtas Kebangsaan Republik Indonesia. Gunakan tool yang tersedia untuk membantu menjawab pertanyaan user. Jawablah hanya berdasarkan informasi yang didapat dari tool. Jika tool tidak memberikan informasi yang relevan atau data tidak ditemukan, beri tahu user bahwa informasi tersebut tidak tersedia dalam data yang kamu miliki dan jangan mengarang jawaban.",
            tools=[lookup_user, lookup_schedule],
        )


async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()

    session = AgentSession(
        llm=google.beta.realtime.RealtimeModel(
            model="gemini-2.0-flash-live-001",
            voice="Leda",
            temperature=0.5,
            # instructions="You are a helpful assistant",
        ),
    )
    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            # LiveKit Cloud enhanced noise cancellation
            # - If self-hosting, omit this parameter
            # - For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await session.generate_reply(
        instructions="Kamu adalah Nara, AI Agent yang berperan sebagai staf TU di Universtas Kebangsaan Republik Indonesia."
    )

    # background_audio = BackgroundAudioPlayer(
    #     thinking_sound=[
    #         AudioConfig(BuiltinAudioClip.KEYBOARD_TYPING, volume=0.8),
    #         AudioConfig(BuiltinAudioClip.KEYBOARD_TYPING2, volume=0.7),
    #     ],
    # )
    # await background_audio.start(room=ctx.room, agent_session=session)

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))