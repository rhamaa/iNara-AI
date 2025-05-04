import os
import re
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.rag import retrieve_context
from functions.time_utils import get_current_time

# Load environment variables
load_dotenv()

# Configure Google Gemini API Key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Error: GOOGLE_API_KEY tidak ditemukan di file .env")
    print("Silakan buat file .env di root project dan tambahkan GOOGLE_API_KEY=API_KEY_ANDA")
    exit()

# Initialize Gemini client
client = genai.Client(api_key=api_key)

def generate_response(query: str) -> str:
    """Generate response using Gemini with tools."""
    model = "gemini-2.0-flash"
    
    # Get context from RAG if needed
    relevant_docs = retrieve_context(query, k=3)
    context_str = "\n\n".join([doc.page_content for doc in relevant_docs]) if relevant_docs else ""
    
    # Define tools
    tools = [
        types.Tool(
            function_declarations=[
                types.FunctionDeclaration(
                    name="RAG",
                    description="Query campus information from knowledge base",
                    parameters={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The query to search in the knowledge base"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                types.FunctionDeclaration(
                    name="Time",
                    description="Get current time",
                    parameters={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                )
            ]
        )
    ]

    # Configure generation settings
    generate_content_config = types.GenerateContentConfig(
        tools=tools,
        response_mime_type="text/plain",
        system_instruction=[
            types.Part.from_text(text="""Anda adalah Nara, staf Tata Usaha (TU) virtual yang ramah dan siap membantu memberikan informasi seputar kampus.
Jawab pertanyaan berikut berdasarkan konteks yang diberikan. Jika konteks tidak cukup, jawab berdasarkan pengetahuan umum Anda sebagai Nara, dan jika perlu, sebutkan bahwa informasi spesifik tidak ada dalam data yang saya miliki saat ini.

Konteks:
{context_str}

Pertanyaan: {query}""")
        ]
    )

    # Create content for the model
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=query)
            ]
        )
    ]

    try:
        # Generate response
        response = ""
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config
        ):
            if chunk.function_calls:
                # Handle function calls
                for func_call in chunk.function_calls:
                    if func_call.name == "RAG":
                        # Process RAG query
                        rag_results = retrieve_context(func_call.args.get("query", ""), k=3)
                        response += "\n".join([doc.page_content for doc in rag_results])
                    elif func_call.name == "Time":
                        # Get current time
                        response += get_current_time()
            else:
                response += chunk.text
        return response
    except Exception as e:
        print(f"Error saat memanggil LLM: {e}")
        return "Maaf, terjadi kesalahan saat mencoba menghasilkan respons."

def main():
    print("\nSelamat datang! Saya Nara, staf TU virtual Anda.")
    print("Ada yang bisa saya bantu terkait informasi kampus? Anda juga bisa menanyakan waktu saat ini.")
    print("Ketik 'quit' atau 'exit' untuk keluar.")

    # Daftar sapaan umum
    sapaan = ["halo", "hai", "hi", "selamat pagi", "selamat siang", "selamat sore", "selamat malam"]
    # Pola regex untuk mendeteksi pertanyaan waktu
    pola_waktu = r"(jam berapa|waktu sekarang|tanggal berapa|hari apa)"

    while True:
        query = input("\nAnda: ").lower().strip()

        if query in ["quit", "exit"]:
            print("\nNara: Terima kasih telah bertanya. Sampai jumpa lagi!")
            break

        if not query:
            continue

        # 1. Cek Sapaan
        if any(s in query for s in sapaan) and len(query.split()) <= 3:
            print("\nNara: Halo! Ada yang bisa saya bantu terkait informasi kampus atau waktu saat ini?")
        # 2. Cek Pertanyaan Waktu
        elif re.search(pola_waktu, query):
            print("\nNara: Tentu, saya cek waktu sekarang...")
            waktu_sekarang = get_current_time()
            print(f"Nara: Sekarang pukul {waktu_sekarang}.")
        # 3. Anggap Pertanyaan Informasi Kampus
        else:
            print("\nNara: Baik, saya coba carikan informasinya untuk Anda...")
            response = generate_response(query)
            print(f"Nara: {response}")

if __name__ == "__main__":
    main()