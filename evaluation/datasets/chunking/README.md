# Chunking Retrieval Evaluation

This directory contains manually verified questions
used to evaluate chunking and retrieval strategies.

Each evaluation case should be answerable from one
or more known document pages.

## Required fields

- id
- knowledge_base_slug
- question
- expected_document
- expected_pages
- expected_terms

## Example workflow

1. Read an ingested document.
2. Write a question whose answer is clearly supported.
3. Record the correct source document and page(s).
4. Add terms or facts that should appear in the
   relevant retrieved chunk.
5. Use the same evaluation set across all chunking
   and retrieval experiments.

Do not generate evaluation answers from the RAG
system itself. Ground-truth cases should be manually
verified.