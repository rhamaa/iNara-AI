import os
import glob
from langchain_community.document_loaders import (
    DirectoryLoader,
    PyPDFLoader,
    UnstructuredMarkdownLoader,
    UnstructuredExcelLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
import shutil

# Konfigurasi
DATA_PATH = "data"
DB_PATH = "db"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
EMBEDDING_MODEL = "all-MiniLM-L6-v2" # Model embedding yang ringan dan efisien

# Mapping ekstensi file ke loader yang sesuai
LOADER_MAPPING = {
    ".md": UnstructuredMarkdownLoader,
    ".pdf": PyPDFLoader,
    ".xlsx": UnstructuredExcelLoader,
    # Tambahkan loader lain jika diperlukan (misal: .docx, .csv)
}

def load_documents(source_dir: str) -> list:
    """Memuat semua dokumen dari direktori sumber menggunakan loader yang sesuai."""
    all_files = []
    for ext in LOADER_MAPPING:
        # Cari file secara rekursif di dalam direktori data
        all_files.extend(
            glob.glob(os.path.join(source_dir, f"**/*{ext}"), recursive=True)
        )

    loaded_documents = []
    processed_files = set() # Untuk melacak file yang sudah diproses

    for file_path in all_files:
        # Normalisasi path untuk menghindari duplikasi karena perbedaan separator
        normalized_path = os.path.normpath(file_path)
        if normalized_path in processed_files:
            continue

        ext = os.path.splitext(normalized_path)[1].lower() # Pastikan ekstensi lowercase
        if ext in LOADER_MAPPING:
            loader_class = LOADER_MAPPING[ext]
            try:
                print(f"Memuat {normalized_path}...")
                # Beberapa loader mungkin memerlukan argumen berbeda
                if loader_class == PyPDFLoader:
                    loader = loader_class(normalized_path)
                else:
                    # Asumsi loader lain menerima path saja
                    loader = loader_class(normalized_path)

                docs = loader.load()
                # Tambahkan metadata sumber ke setiap dokumen
                for doc in docs:
                    doc.metadata["source"] = os.path.basename(normalized_path)
                loaded_documents.extend(docs)
                processed_files.add(normalized_path)
            except Exception as e:
                print(f"Gagal memuat {normalized_path}: {e}")
        else:
            print(f"Ekstensi tidak didukung: {normalized_path}")

    return loaded_documents

def main():
    print("Memulai proses training data...")

    # 1. Muat dokumen
    print(f"Memuat dokumen dari direktori: {DATA_PATH}")
    documents = load_documents(DATA_PATH)
    if not documents:
        print("Tidak ada dokumen yang ditemukan atau berhasil dimuat. Proses dihentikan.")
        return
    print(f"Berhasil memuat {len(documents)} dokumen.")

    # 2. Pisahkan dokumen menjadi chunk
    print("Memisahkan dokumen menjadi chunk...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    texts = text_splitter.split_documents(documents)
    print(f"Dokumen dipecah menjadi {len(texts)} chunk.")

    # 3. Buat embedding
    print(f"Membuat embedding menggunakan model: {EMBEDDING_MODEL}")
    # Gunakan SentenceTransformerEmbeddings yang lebih umum
    embeddings = SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL)

    # 4. Buat dan simpan vector store
    # Hapus direktori DB lama jika ada untuk memastikan data baru
    if os.path.exists(DB_PATH):
        print(f"Menghapus direktori database lama: {DB_PATH}")
        shutil.rmtree(DB_PATH)

    print(f"Membuat dan menyimpan vector store ke: {DB_PATH}")
    # Pastikan direktori ada sebelum menyimpan
    os.makedirs(DB_PATH, exist_ok=True)
    vectorstore = Chroma.from_documents(texts, embeddings, persist_directory=DB_PATH)
    # Chroma otomatis persist jika persist_directory diberikan saat inisialisasi
    # vectorstore.persist() # Tidak perlu dipanggil lagi
    print("Vector store berhasil dibuat dan disimpan.")

    print("Proses training data selesai.")

if __name__ == "__main__":
    main()