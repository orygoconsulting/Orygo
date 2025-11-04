import os
from pathlib import Path
import openai
import pinecone
from pdf_extract import extract_text_from_pdf

openai.api_key = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
INDEX_NAME = os.getenv("PINECONE_INDEX", "ops-consultant")
EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")

if not PINECONE_API_KEY:
    raise RuntimeError("PINECONE_API_KEY no configurado")

pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)

if INDEX_NAME not in pinecone.list_indexes():
    pinecone.create_index(INDEX_NAME, dimension=1536)

index = pinecone.Index(INDEX_NAME)

def embed_text(text: str):
    text = text.strip()
    if not text:
        return None
    resp = openai.Embedding.create(model=EMBED_MODEL, input=text)
    return resp["data"][0]["embedding"]

def chunk_text(text: str, max_chars=2000):
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks = []
    cur = ""
    for p in paragraphs:
        if len(cur) + len(p) + 1 <= max_chars:
            cur += p + "\n"
        else:
            chunks.append(cur.strip())
            cur = p + "\n"
    if cur.strip():
        chunks.append(cur.strip())
    return chunks

def index_document_text(text: str, doc_id: str, metadata: dict, company_id: str = None):
    chunks = chunk_text(text)
    to_upsert = []
    for i,ch in enumerate(chunks):
        emb = embed_text(ch)
        if emb is None:
            continue
        meta = metadata.copy()
        meta.update({
            "source": doc_id,
            "chunk_index": i,
            "text_snippet": ch[:800]
        })
        to_upsert.append((f"{doc_id}-{i}", emb, meta))
    if to_upsert:
        if company_id:
            index.upsert(vectors=to_upsert, namespace=company_id)
            print(f"Upserted {len(to_upsert)} vectors into namespace '{company_id}' from {doc_id}")
        else:
            index.upsert(vectors=to_upsert)
            print(f"Upserted {len(to_upsert)} vectors into default namespace from {doc_id}")

def index_folder(folder_path="./docs", company_id: str = None):
    folder = Path(folder_path)
    for f in folder.glob("**/*"):
        if f.is_file():
            if f.suffix.lower() in [".md", ".txt"]:
                text = f.read_text(encoding="utf-8")
                index_document_text(text, doc_id=f.stem, metadata={"type":"methodology", "filename": f.name}, company_id=company_id)
            elif f.suffix.lower() == ".pdf":
                txt = extract_text_from_pdf(f)
                index_document_text(txt, doc_id=f.stem, metadata={"type":"methodology", "filename": f.name}, company_id=company_id)
    print("Indexación finalizada.")

if __name__ == "__main__":
    cid = os.getenv("COMPANY_ID")
    index_folder("./docs", company_id=cid)
