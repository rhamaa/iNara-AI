import os
from langchain_community.vectorstores import Chroma
# Ganti SentenceTransformerEmbeddings dengan HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings

# Tentukan path absolut ke direktori skrip saat ini
current_dir = os.path.dirname(os.path.abspath(__file__))
# Tentukan path absolut ke direktori db
DB_PATH = os.path.join(current_dir, "..", "db")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Inisialisasi embedding function menggunakan HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

# Muat vector store yang sudah ada
if os.path.exists(DB_PATH):
    vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
    print(f"Vector store dimuat dari: {DB_PATH}")
else:
    print(f"Error: Direktori vector store tidak ditemukan di '{DB_PATH}'. Pastikan path sudah benar dan Anda telah menjalankan train.py terlebih dahulu.")
    vectorstore = None # Atau tangani error sesuai kebutuhan

def retrieve_context(query: str, k: int = 5) -> list:
    """Mengambil k dokumen paling relevan dari vector store berdasarkan query."""
    if vectorstore is None:
        print("Vector store belum diinisialisasi.")
        return []

    try:
        # Lakukan pencarian similarity
        results = vectorstore.similarity_search(query, k=k)
        print(f"Ditemukan {len(results)} dokumen relevan untuk query: '{query}'")
        # Mengembalikan konten dokumen saja untuk konteks
        # return [doc.page_content for doc in results]
        # Mengembalikan seluruh objek Document untuk akses metadata jika perlu
        return results
    except Exception as e:
        print(f"Error saat melakukan retrieval: {e}")
        return []

# Contoh penggunaan (bisa dihapus atau dikomentari)
if __name__ == '__main__':
    test_query = "apa sejarah ukri?"
    print(f"\nTesting retrieval dengan query: '{test_query}'")
    relevant_docs = retrieve_context(test_query)
    if relevant_docs:
        print("\nDokumen relevan:")
        for i, doc in enumerate(relevant_docs):
            print(f"--- Dokumen {i+1} (Source: {doc.metadata.get('source', 'N/A')}) ---")
            print(doc.page_content)
            print("---------------------")
    else:
        print("Tidak ada dokumen relevan yang ditemukan.")