# M04 — RAG & Information Retrieval

Recurring case study: an internal engineering assistant answering questions about service runbooks, incidents, and architecture decisions. Each lesson introduces one additional production capability, with an explicit failure case, runnable exercises, and spoken interview answers.

| ID | Lesson | Practical result |
|---|---|---|
| M04-L01 | RAG Architecture & Retrieval Pipelines | Trace offline indexing and online evidence-to-answer stages |
| M04-L02 | Embeddings, Similarity & Vector Search | Build and compare ranking strategies; reason about ANN recall |
| M04-L03 | Document Ingestion, Chunking & Metadata | Ingest revisions and preserve source provenance and ACLs |
| M04-L04 | Hybrid Retrieval, Reranking & Query Rewriting | Compare lexical + semantic recall and re-ranking |
| M04-L05 | Grounded Generation, Citations & Safety | Enforce grounded answers, citation checks and abstention |
| M04-L06 | RAG Evaluation, Debugging & Operations | Measure retrieval recall, context relevance, faithfulness, cost |
| M04-L07 | Advanced RAG System Design & Implementation | Deliver tested production-style architecture with SLOs and failure modes |

## Editorial contract

Explain each new term in plain English before the formal term. Contrast a happy path with a realistic failure, then walk through the engineering decision. Include interactive behavior that changes outcomes rather than labels only; tests should assert deterministic correctness. Interview answers must be first-person, complete, conversational, and accurate, including trade-offs. Continue existing chapter IDs and browser-local progress keys. Never alter M03 storage values.
