#!/usr/bin/env python3
"""
Build RAG Vector Index from Repo Control Libraries (Repo Mode)

Loads ECC, CCC, and PDPL control JSON libraries from the data/ directory,
chunks them using ControlChunker, and builds a Chroma vector store index
for bilingual compliance queries.

Usage:
    python scripts/build_rag_index.py [--frameworks ECC CCC PDPL] [--output ./vectordb]

This script converts the system from Demo Mode to Repo Mode by indexing
the actual project control library data instead of placeholder documents.
"""

import argparse
import json
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ai.rag.control_loader import load_all_frameworks_as_documents, get_library_stats


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build RAG vector index from control libraries")
    parser.add_argument(
        "--frameworks",
        nargs="+",
        default=["ECC", "CCC", "PDPL"],
        choices=["ECC", "CCC", "PDPL"],
        help="Frameworks to index (default: all)",
    )
    parser.add_argument(
        "--output",
        default=str(ROOT / "vectordb"),
        help="Path to write the Chroma vector store (default: ./vectordb)",
    )
    parser.add_argument(
        "--model",
        default="intfloat/multilingual-e5-large",
        help="Sentence transformer model for embeddings",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Load and chunk documents but do not write vector store",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print("=" * 60)
    print("SICO GRC Platform - RAG Index Builder (Repo Mode)")
    print("=" * 60)

    # Print library stats
    print("\nControl Library Status:")
    stats = get_library_stats()
    for fw, info in stats.items():
        if info.get("available") is False:
            print(f"  {fw}: ⚠️  Library file not found")
        else:
            print(
                f"  {fw}: ✓  {info['total_controls']} controls "
                f"(version: {info['version']}, updated: {info['last_updated']})"
            )

    # Load documents from all specified frameworks
    print(f"\nLoading controls for frameworks: {', '.join(args.frameworks)}")
    documents = load_all_frameworks_as_documents(frameworks=args.frameworks, language="both")

    if not documents:
        print("\n❌ No documents loaded. Ensure JSON control library files exist in data/controls/")
        sys.exit(1)

    print(f"✓  Loaded {len(documents)} document chunks")

    # Breakdown by framework
    from collections import Counter
    fw_counts = Counter(doc.metadata.get("framework", "unknown") for doc in documents)
    for fw, count in sorted(fw_counts.items()):
        print(f"   {fw}: {count} chunks")

    if args.dry_run:
        print("\n[dry-run] Skipping vector store write.")
        print("✓  Dry run complete – documents are ready for indexing.")
        return

    # Build vector store
    try:
        from langchain.embeddings import HuggingFaceEmbeddings  # type: ignore[import-not-found]
        from langchain.vectorstores import Chroma  # type: ignore[import-not-found]
    except ImportError:
        print(
            "\n❌ langchain / sentence-transformers not installed.\n"
            "   Install AI dependencies: pip install langchain langchain-community "
            "sentence-transformers chromadb\n"
            "   Or use --dry-run to validate documents without building the index."
        )
        sys.exit(1)

    print(f"\nLoading embedding model: {args.model}")
    embeddings = HuggingFaceEmbeddings(
        model_name=args.model,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    print(f"Building Chroma vector store at: {args.output}")
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=args.output,
    )
    vectorstore.persist()

    doc_count = vectorstore._collection.count()
    print(f"\n✓  Vector store built with {doc_count} indexed documents")
    print(f"   Location: {args.output}")
    print("\n✅ RAG index built successfully from repo control libraries (Repo Mode)")
    print("   The BilingualRetriever will now use real project data instead of demo data.")


if __name__ == "__main__":
    main()
