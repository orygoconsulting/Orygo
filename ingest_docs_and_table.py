# ingest_docs_and_table.py (versión optimizada)
import os
from pathlib import Path
from openai import OpenAI
import pinecone
from pdf_extract import extract_text_from_pdf

# === Configuración ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
INDEX_NAME = os.getenv("PINECONE_INDEX", "ops-consultant")
EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY no configurado")
if not PINECONE_API_KEY or not PINECONE_ENV:
    raise RuntimeError("Pinecone API key o entorno no configurado")

# === Inicializar clientes ===
client = OpenAI(api_key=OPENAI_API_KEY)
pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)

# Crear índice si no existe
if INDEX_NAME not in pinecone.list_indexes():
    pinecone.create_index(name=INDEX_NAME, dimension=1536)
index = pinecone.Index(INDEX_NAME)

# === Utilidades ===
def chunk_text(text: str, max_chars: int = 2000):
    """Divide texto largo en bloques de tamaño manejable (~2000 chars)."""
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks, cur = [], ""
    for p in paragraphs:
        if len(cur) + len(p) + 1 <= max_chars:
            cur += p + "\n"
        else:
            chunks.append(cur.strip())
            cur = p + "\n"
    if cur.strip():
        chunks.append(cur.strip())
    return chunks


def embed_batch(texts: list[str]):
    """Genera embeddings en batch para reducir coste y latencia."""
    if not texts:
        return []
    response = client.embeddings.create(model=EMBED_MODEL, input=texts)
    return [d.embedding for d in response.data]


def index_document_text(text: str, doc_id: str, metadata: dict, company_id: str = None):
    """Indexa un documento completo (PDF, MD, TXT) en Pinecone, por chunks."""
    chunks = chunk_text(text)
    if not chunks:
        print(f"[WARN] Documento vacío: {doc_id}")
        return

    # Obtener embeddings en batch
    embeddings = embed_batch(chunks)

    to_upsert = []
    for i, (ch, emb) in enumerate(zip(chunks, embeddings)):
        meta = metadata.copy()
        meta.update({
            "source": doc_id,
            "chunk_index": i,
            "text_snippet": ch[:800]
        })
        to_upsert.append((f"{doc_id}-{i}", emb, meta))

    if not to_upsert:
        print(f"[WARN] No se generaron embeddings para {doc_id}")
        return

    namespace = company_id or ""
    index.upsert(vectors=to_upsert, namespace=namespace)
    print(f"[OK] {len(to_upsert)} chunks indexados en namespace '{namespace}' ({doc_id})")


def index_folder(folder_path: str = "./docs", company_id: str = None):
    """Indexa todos los archivos de una carpeta."""
    folder = Path(folder_path)
    if not folder.exists():
        raise FileNotFoundError(f"La carpeta '{folder_path}' no existe")

    for f in folder.glob("**/*"):
        if not f.is_file():
            continue
        try:
            if f.suffix.lower() in [".md", ".txt"]:
                text = f.read_text(encoding="utf-8")
            elif f.suffix.lower() == ".pdf":
                text = extract_text_from_pdf(f)
            else:
                continue
            index_document_text(
                text,
                doc_id=f.stem,
                metadata={"type": "methodology", "filename": f.name},
                company_id=company_id,
            )
        except Exception as e:
            print(f"[ERROR] No se pudo procesar {f.name}: {e}")

    print("✅ Indexación completada.")


if __name__ == "__main__":
    cid = os.getenv("COMPANY_ID")
    index_folder("./docs", company_id=cid)

