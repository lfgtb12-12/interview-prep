"""Deterministic document ingestion, chunking, revision and ACL exercise.

Word units are used for illustration, not tokenizer-specific model tokens.
"""
from dataclasses import dataclass
import re

@dataclass(frozen=True)
class Document:
    id: str
    revision: int
    text: str
    allowed_roles: frozenset[str]
    source: str

@dataclass(frozen=True)
class Chunk:
    id: str
    document_id: str
    revision: int
    start_word: int
    end_word: int
    text: str
    allowed_roles: frozenset[str]
    source: str

def words(text):
    return re.findall(r"\S+", text)

def chunk_document(doc: Document, size: int, overlap: int) -> list[Chunk]:
    if type(size) is not int or type(overlap) is not int or size < 1 or not 0 <= overlap < size:
        raise ValueError("Require positive chunk size and 0 <= overlap < size")
    tokens = words(doc.text)
    result = []
    step = size - overlap
    for start in range(0, len(tokens), step):
        end = min(start + size, len(tokens))
        result.append(Chunk(f"{doc.id}:r{doc.revision}:{start}-{end}", doc.id,
                            doc.revision, start, end, " ".join(tokens[start:end]),
                            doc.allowed_roles, doc.source))
        if end == len(tokens):
            break
    return result

class Index:
    """Small transactional-in-memory teaching demo; NOT durable production storage."""
    def __init__(self):
        self._docs = {}
        self._chunks = {}

    def upsert(self, doc: Document, size=12, overlap=3):
        old = self._docs.get(doc.id)
        if old is not None and doc.revision <= old.revision:
            raise ValueError("Revision must increase")
        new = chunk_document(doc, size, overlap)
        # Build and validate first, then replace this document's indexed chunks.
        next_chunks = {k: v for k, v in self._chunks.items() if v.document_id != doc.id}
        next_chunks.update({part.id: part for part in new})
        self._chunks = next_chunks
        self._docs[doc.id] = doc

    def delete(self, doc_id: str, revision: int):
        old = self._docs.get(doc_id)
        if old is None or revision <= old.revision:
            raise ValueError("Missing document or stale deletion")
        self._chunks = {k: v for k, v in self._chunks.items() if v.document_id != doc_id}
        del self._docs[doc_id]

    def visible(self, role: str) -> list[Chunk]:
        return [part for part in self._chunks.values() if role in part.allowed_roles]

    def all_chunks(self):
        return list(self._chunks.values())
