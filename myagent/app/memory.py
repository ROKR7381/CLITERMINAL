try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    HAS_CHROMA = True
except ImportError:
    HAS_CHROMA = False

from pathlib import Path


class ProjectMemory:
    def __init__(self, collection_name: str = "project_memory"):
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self._init_chroma()

    def _init_chroma(self):
        if not HAS_CHROMA:
            return
        try:
            memory_dir = Path(__file__).parent.parent / ".myagent" / "memory"
            memory_dir.mkdir(parents=True, exist_ok=True)
            self.client = chromadb.Client(ChromaSettings(
                persist_directory=str(memory_dir),
                anonymized_telemetry=False,
            ))
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        except Exception:
            self.client = None
            self.collection = None

    def add_document(self, doc_id: str, text: str, metadata: dict = None):
        if not self.collection:
            return False
        try:
            self.collection.upsert(
                ids=[doc_id],
                documents=[text],
                metadatas=[metadata or {}],
            )
            return True
        except Exception:
            return False

    def search(self, query: str, n_results: int = 5) -> list:
        if not self.collection:
            return []
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
            )
            docs = results.get("documents", [[]])[0]
            metas = results.get("metadatas", [[]])[0]
            return [{"text": d, "metadata": m} for d, m in zip(docs, metas)]
        except Exception:
            return []

    def get_context(self, query: str, max_tokens: int = 2000) -> str:
        results = self.search(query, n_results=3)
        if not results:
            return ""
        context_parts = []
        total = 0
        for r in results:
            text = r["text"]
            if total + len(text.split()) > max_tokens:
                break
            context_parts.append(text)
            total += len(text.split())
        return "\n---\n".join(context_parts)

    def index_file(self, file_path: str):
        try:
            content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
            if len(content.strip()) < 10:
                return
            chunks = self._chunk_text(content, chunk_size=500)
            for i, chunk in enumerate(chunks):
                doc_id = f"{file_path}::chunk_{i}"
                self.add_document(
                    doc_id=doc_id,
                    text=chunk,
                    metadata={"file": file_path, "chunk": i},
                )
        except Exception:
            pass

    def _chunk_text(self, text: str, chunk_size: int = 500) -> list:
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
        return chunks

    def index_project(self, root: str = "."):
        from app.context import scan_repo, IGNORE_DIRS, CODE_EXTS
        summary = scan_repo(root)
        for f in summary["files"][:50]:
            self.index_file(f)
        return len(summary["files"])


memory = ProjectMemory()
