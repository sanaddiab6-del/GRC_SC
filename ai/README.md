# AI/NLP Engine

## Bilingual AI-Powered Compliance Assistant

This directory contains the AI and Natural Language Processing components that power the SICO GRC Platform's intelligent features.

## Overview

The AI engine provides:
- **Bilingual RAG**: Arabic/English Retrieval-Augmented Generation
- **Smart Search**: Semantic search across regulatory documents
- **Citation Tracking**: Traceable answers with source references
- **Client Dictionary**: Custom terminology mapping
- **Adaptive Learning**: Per-client model fine-tuning

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   User Query (AR/EN)                    │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│              Client Dictionary Engine                    │
│  Translate custom terms to standard terminology         │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│                 RAG Pipeline                            │
│  1. Query embedding (BERT)                              │
│  2. Vector search (Chroma/Weaviate)                     │
│  3. Context retrieval                                   │
│  4. Answer generation (LLM)                             │
│  5. Citation extraction                                 │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│          Response with Citations                        │
│  Answer + Source documents + Confidence score           │
└─────────────────────────────────────────────────────────┘
```

## Components

### 1. Knowledge Base (`/knowledge-base`)
Regulatory document corpus and embeddings.

**Contents**:
- ECC/CCC/PDPL framework documents
- Implementation guides
- Best practices
- Case studies
- Pre-computed embeddings

**Structure**:
```
knowledge-base/
├── documents/
│   ├── ecc/              # ECC framework docs
│   ├── ccc/              # CCC framework docs
│   ├── pdpl/             # PDPL regulations
│   └── guides/           # Implementation guides
├── embeddings/           # Pre-computed vectors
└── metadata/             # Document metadata
```

### 2. RAG Pipeline (`/rag`)
Retrieval-Augmented Generation implementation.

**Components**:
- `embeddings.py` - Document and query embedding
- `retrieval.py` - Semantic search and ranking
- `generation.py` - Answer generation with LLM
- `citations.py` - Citation extraction and tracking
- `pipeline.py` - End-to-end RAG orchestration

**Features**:
- Hybrid search (semantic + keyword)
- Context window optimization
- Multi-document synthesis
- Confidence scoring
- Source attribution

### 3. Dictionary Engine (`/dictionary`)
Client-specific terminology mapping.

**Purpose**: 
Organizations use different terms for the same concepts. The dictionary engine:
- Maps client terms to standard terms
- Maintains per-client dictionaries
- Learns from user interactions
- Improves query understanding

**Example**:
```yaml
client_id: "client_123"
mappings:
  - client_term: "data owner"
    standard_term: "data controller"
  - client_term: "cyber policy"
    standard_term: "cybersecurity policy"
```

### 4. BERT Adapters (`/models`)
Fine-tuned models for improved accuracy.

**Base Models**:
- `aubmindlab/bert-base-arabertv2` - Arabic BERT
- `bert-base-multilingual-cased` - Multilingual BERT

**Adapters**:
- Client-specific fine-tuning
- Domain-specific terminology
- Improved entity recognition
- Custom classification

## Use Cases

### 1. Compliance Q&A
**Query**: "What are the requirements for password policy under ECC?"  
**Response**: 
```
Based on ECC Control 2-2-2 (Authentication), password policies must:
- Minimum 8 characters
- Complexity requirements (uppercase, lowercase, numbers, special chars)
- Maximum 90-day lifetime
- Prevention of password reuse (last 5 passwords)

[Source: ECC Framework, Section 2.2.2, Page 45]
[Confidence: 95%]
```

### 2. Evidence Recommendation
**Query**: "What evidence do I need for access control compliance?"  
**Response**:
```
For ECC Access Control (2-2-x), you need:
1. Access Control Policy (ECC-2-2-1)
2. User access review logs (ECC-2-2-3)
3. Privileged access management records (ECC-2-2-4)
4. Access provisioning/deprovisioning logs (ECC-2-2-5)

[Auto-generated evidence templates available]
```

### 3. Control Implementation Guidance
**Query**: "كيف أطبق متطلبات الحماية من البرمجيات الخبيثة؟" (How to implement malware protection?)  
**Response** (in Arabic):
```
لتطبيق متطلبات الحماية من البرمجيات الخبيثة (ECC 2-3-1):
1. تثبيت برنامج مكافحة البرمجيات الخبيثة
2. تحديث التوقيعات تلقائياً
3. فحص دوري للأنظمة
4. عزل الملفات المشبوهة
...
```

## Technical Details

### Embedding Models
- **Arabic**: AraBERT (768-dimensional vectors)
- **English**: Sentence-BERT (768-dimensional vectors)
- **Multilingual**: Multilingual E5 (768-dimensional vectors)

### Vector Database
- **Primary**: Chroma (open-source, easy deployment)
- **Alternative**: Weaviate (production scale)
- **Storage**: Persistent storage for embeddings

### LLM Integration
- **Primary**: OpenAI GPT-4 (via API)
- **Alternative**: Open-source models (LLaMA, Mistral)
- **Prompt Engineering**: Custom prompts for compliance domain

### Performance
- **Query latency**: < 2 seconds
- **Accuracy**: > 90% on compliance questions
- **Languages**: Arabic, English

## Configuration

### Environment Variables
```bash
# LLM Configuration
OPENAI_API_KEY=your_key
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.2

# Vector Database
VECTOR_DB=chroma
VECTOR_DB_PATH=/data/vector_db

# Embedding Models
EMBEDDING_MODEL_AR=aubmindlab/bert-base-arabertv2
EMBEDDING_MODEL_EN=sentence-transformers/all-mpnet-base-v2
```

## Development

### Setup
```bash
cd ai/
pip install -r requirements.txt
python setup.py
```

### Testing
```bash
pytest tests/
```

### Training Custom Adapters
```bash
python models/train_adapter.py --client_id CLIENT_ID --data_path PATH
```

---

**Last Updated**: February 2026
