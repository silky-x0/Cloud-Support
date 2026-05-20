import os
import glob
import json
import shutil
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# pyrefly: ignore [missing-import]
from langchain_community.vectorstores import Chroma
# pyrefly: ignore [missing-import]
from langchain.text_splitter import RecursiveCharacterTextSplitter
# pyrefly: ignore [missing-import]
from langchain.schema import Document
from retrieval.embeddings import get_embeddings
from config.settings import settings

def ingest():
    persist_dir = settings.CHROMA_PERSIST_DIRECTORY
    
    # 1. Clean existing chroma directory if it exists
    if os.path.exists(persist_dir):
        print(f"Clearing existing vector database at {persist_dir}...")
        shutil.rmtree(persist_dir)

    # 2. Load articles
    docs = []
    kb_pattern = os.path.join("knowledge_base", "**", "*.json")
    for path in glob.glob(kb_pattern, recursive=True):
        try:
            with open(path, "r", encoding="utf-8") as f:
                article = json.load(f)
            
            docs.append(Document(
                page_content=article["content"],
                metadata={
                    "kb_id": article["id"],
                    "title": article["title"],
                    "category": article["category"]
                }
            ))
        except Exception as e:
            print(f"Failed to read {path}: {str(e)}")

    if not docs:
        print("No articles found in knowledge_base/")
        return

    # 3. Chunk documents
    # Splitter chunk size 512 characters, overlap 64 characters
    splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)
    chunks = splitter.split_documents(docs)

    # 4. Get embeddings and persist in Chroma
    embeddings = get_embeddings()
    Chroma.from_documents(
        chunks,
        embeddings,
        persist_directory=persist_dir
    )
    print(f"Successfully indexed {len(chunks)} chunks from {len(docs)} articles in Chroma DB.")

if __name__ == "__main__":
    ingest()
