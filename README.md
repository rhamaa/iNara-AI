# iNara-AI: Virtual Campus Information Assistant

iNara-AI adalah asisten virtual kampus yang menggunakan teknologi AI untuk memberikan informasi seputar kampus. Asisten ini menggunakan kombinasi RAG (Retrieval-Augmented Generation) dan LLM (Large Language Model) untuk memberikan jawaban yang akurat dan kontekstual.

## Fitur Utama

- 🤖 Asisten virtual dengan persona Nara (staf TU virtual)
- 🔍 Pencarian informasi kampus menggunakan RAG
- ⏰ Informasi waktu real-time
- 💬 Interaksi natural dalam bahasa Indonesia
- 📚 Basis pengetahuan yang dapat diperbarui

## Teknologi yang Digunakan

- Google Gemini AI (LLM)
- LangChain (Framework RAG)
- ChromaDB (Vector Database)
- Sentence Transformers (Embeddings)
- Python 3.x

## Persyaratan Sistem

- Python 3.x
- Google API Key untuk Gemini AI
- Dependensi Python (lihat requirements.txt)

## Instalasi

1. Clone repository:
```bash
git clone https://github.com/yourusername/iNara-AI.git
cd iNara-AI
```

2. Buat virtual environment (opsional tapi direkomendasikan):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# atau
.\venv\Scripts\activate  # Windows
```

3. Install dependensi:
```bash
pip install -r requirements.txt
```

4. Buat file `.env` di root project dan tambahkan API key:
```
GOOGLE_API_KEY=your_api_key_here
```

5. Siapkan data dan train model:
```bash
python train.py
```

## Penggunaan

Jalankan aplikasi dengan perintah:
```bash
python main.py
```

Setelah aplikasi berjalan, Anda dapat:
- Bertanya tentang informasi kampus
- Menanyakan waktu saat ini
- Mengucapkan sapaan
- Ketik 'quit' atau 'exit' untuk keluar

## Struktur Project

```
iNara-AI/
├── data/               # Direktori untuk data training
├── db/                 # Vector database
├── functions/          # Modul fungsi-fungsi utama
│   ├── __init__.py
│   ├── rag.py         # Implementasi RAG
│   └── time_utils.py  # Utilitas waktu
├── main.py            # Entry point aplikasi
├── train.py           # Script untuk training model
├── requirements.txt   # Dependensi project
└── .env              # File konfigurasi (buat sendiri)
```

## Kontribusi

Kontribusi selalu diterima! Silakan buat pull request atau buka issue untuk diskusi.

## Lisensi

[Masukkan informasi lisensi di sini]

## Kontak

[Masukkan informasi kontak di sini] 