import os
import re # Import modul regex untuk pencocokan kata kunci
import google.generativeai as genai
from dotenv import load_dotenv
from functions.rag import retrieve_context
from functions.time_utils import get_current_time # Import fungsi waktu

# Muat environment variables dari .env file
load_dotenv()

# Konfigurasi Google Gemini API Key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Error: GOOGLE_API_KEY tidak ditemukan di file .env")
    print("Silakan buat file .env di root project dan tambahkan GOOGLE_API_KEY=API_KEY_ANDA")
    exit()

genai.configure(api_key=api_key)

# Inisialisasi model Gemini
# Pilih model yang sesuai, contoh: 'gemini-pro'
model = genai.GenerativeModel('gemini-2.0-flash') # Ganti model jika perlu, 1.5 flash lebih baru

def generate_response_rag(query: str) -> str:
    """Menghasilkan respons menggunakan RAG dan LLM untuk pertanyaan informasi kampus."""
    print(f"\nMencari konteks untuk query: '{query}'...")
    # 1. Ambil konteks relevan dari vector store
    relevant_docs = retrieve_context(query, k=3) # Ambil 3 dokumen teratas

    if not relevant_docs:
        print("Tidak ditemukan konteks relevan. Mencoba menjawab tanpa konteks tambahan.")
        context_str = ""
    else:
        # Gabungkan konten dokumen relevan menjadi satu string konteks
        context_str = "\n\n".join([doc.page_content for doc in relevant_docs])
        print("Konteks ditemukan:")
        # Tampilkan sumber konteks (opsional)
        sources = list(set([doc.metadata.get('source', 'N/A') for doc in relevant_docs]))
        print(f"  Sumber: {', '.join(sources)}")
        # print(f"--- Raw context --- ") # Uncomment untuk melihat konteks mentah (perlu variabel context_str)

    # 2. Buat prompt untuk LLM dengan persona Nara
    prompt = f"""
Anda adalah Nara, staf Tata Usaha (TU) virtual yang ramah dan siap membantu memberikan informasi seputar kampus.
Jawab pertanyaan berikut berdasarkan konteks yang diberikan. Jika konteks tidak cukup, jawab berdasarkan pengetahuan umum Anda sebagai Nara, dan jika perlu, sebutkan bahwa informasi spesifik tidak ada dalam data yang saya miliki saat ini.

Konteks:
{context_str}

Pertanyaan: {query}

Jawaban Nara:
"""

    print("\nMengirim prompt ke LLM...")
    try:
        # 3. Panggil LLM (Gemini)
        response = model.generate_content(prompt)
        # Pastikan response.text tidak None sebelum mengembalikannya
        return response.text if response.text else "Maaf, saya tidak dapat menghasilkan respons saat ini."
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
        if any(s in query for s in sapaan) and len(query.split()) <= 3: # Anggap sapaan jika pendek
            print("\nNara: Halo! Ada yang bisa saya bantu terkait informasi kampus atau waktu saat ini?")
        # 2. Cek Pertanyaan Waktu
        elif re.search(pola_waktu, query):
            print("\nNara: Tentu, saya cek waktu sekarang...")
            print("[Fungsi waktu dieksekusi]")
            waktu_sekarang = get_current_time()
            print(f"Nara: Sekarang pukul {waktu_sekarang}.")
        # 3. Anggap Pertanyaan Informasi Kampus (RAG)
        else:
            print("\nNara: Baik, saya coba carikan informasinya untuk Anda...")
            print("[Fungsi RAG dieksekusi]")
            response = generate_response_rag(query) # Panggil fungsi RAG
            print(f"Nara: {response}")

if __name__ == "__main__":
    main()