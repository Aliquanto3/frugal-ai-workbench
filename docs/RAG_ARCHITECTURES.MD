# 🧠 Documentation Technique : Module RAG Frugal AI Workbench

Ce document détaille l'architecture du module RAG refondu (v2.0), conçu pour fonctionner **100% Localement**.

## 1. Architecture Globale

Le système repose sur une architecture modulaire utilisant le Pattern Strategy.
- **Ingestion** : Support multi-formats (PDF, DOCX, TXT, MD) via `IngestionPipeline`.
- **Stockage** : ChromaDB avec isolation des collections par modèle d'embedding.
- **Retrieval** : Stratégies interchangeables à chaud.

## 2. Stratégies de Retrieval Implémentées

### A. Naive RAG (Baseline)
- **Fonctionnement** : Recherche de similarité vectorielle (Cosine Similarity).
- **Option** : Reranking (Cross-Encoder) pour réordonner les résultats.
- **Usage** : Questions factuelles simples, base documentaire petite.
- **Latence** : ⚡ Faible.

### B. HyDE (Hypothetical Document Embeddings)
- **Fonctionnement** :
    1. Le LLM génère une réponse fictive ("Hallucination contrôlée") à la question.
    2. Cette réponse est vectorisée pour chercher des documents similaires.
    3. Les documents réels sont renvoyés.
- **Avantage** : Comble le fossé sémantique (question courte vs document technique).
- **Usage** : Questions mal formulées ou très courtes.
- **Latence** : 🐢 Moyenne (+1 appel LLM).

### C. Self-RAG (Corrective RAG)
- **Fonctionnement** (via LangGraph) :
    1. **Retrieve** : Récupère les documents.
    2. **Grade** : Un LLM Juge évalue la pertinence des docs (Yes/No).
    3. **Decide** :
        - Si pertinent : Génère la réponse.
        - Si non pertinent : Réécrit la question et recommence (Max 2 boucles).
- **Avantage** : Réduit drastiquement les hallucinations.
- **Usage** : Questions complexes nécessitant une haute précision.
- **Latence** : 🐢🐢 Élevée (Multiples appels LLM).

## 3. Modèles Supportés (Local)

Les modèles sont gérés dans `data/models/` et chargés via `RAGModelsFactory`.

| Rôle | Modèle Recommandé | Alternative Light |
| :--- | :--- | :--- |
| **Embedding** | `bge-m3` (SOTA, Hybrid) | `all-MiniLM-L6-v2` |
| **Reranker** | `bge-reranker-base` | `mxbai-rerank-base-v1` |
| **LLM Juge** | `Mistral-Nemo` ou `Llama-3` | `Qwen2.5-1.5B` |

## 4. Évaluation (EvalOps)

Le moteur utilise **Ragas** adapté au local.
- **Metrics** : Faithfulness (Fidélité), Answer Relevancy.
- **Constraint** : L'embedding utilisé pour l'évaluation est synchronisé avec celui du moteur RAG pour garantir la cohérence des scores.
