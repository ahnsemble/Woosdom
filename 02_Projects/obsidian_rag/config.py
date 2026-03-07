"""
config.py — Obsidian RAG 파이프라인 설정
"""
import os

VAULT_ROOT = "/Users/woosung/Desktop/Dev/Woosdom_Brain"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_DB_PATH = os.path.join(BASE_DIR, "chroma_db")
COLLECTION_NAME = "obsidian_vault"

EMBEDDING_MODEL = "gemini-embedding-001"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
EMBEDDING_DIMENSIONS = 768   # MRL: 768이면 개인 볼트 충분. 768/1536/3072 선택 가능

CHUNK_SIZE = 500        # tokens
CHUNK_OVERLAP = 50      # tokens
EMBED_BATCH_SIZE = 100  # Gemini API 배치 크기

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8100

WATCH_DEBOUNCE = 2.0    # seconds

EXCLUDE_DIRS = {".obsidian", ".trash", "chroma_db", "node_modules", ".git"}
