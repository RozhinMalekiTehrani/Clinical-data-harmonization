# DH-2026-02 Clinical Data Harmonization

## Overview

This repository contains a small Python prototype for harmonizing heterogeneous
clinical data into a canonical clinical record.

The prototype accepts:

1. Structured laboratory CSV data.
2. Narrative clinical notes.

It produces:

- Canonical JSON.
- A JSON Schema validated canonical record.
- A human review queue for unresolved or conflicting information.

All assessment data are synthetic.


## Architecture

```text
Structured CSV ───────┐
                       │
                       ▼
                Input adapters
                       │
Narrative note ────────┘
                       │
                       ▼
             Deterministic parsing
                       │
                       ├── Local mappings
                       ├── Date normalization
                       ├── Unit normalization
                       ├── Negation handling
                       └── Narrative extraction
                       │
                       ▼
                Canonical facts
                       │
                       ▼
              Conflict detection
                       │
                       ▼
               Review queue
                       │
                       ▼
              JSON Schema validation
                       │
                       ▼
             Canonical JSON output




SciSpaCy is used as a biomedical NLP component for narrative processing. Next plan is to combine LLM-based and pretrained approaches using a majority-voting strategy.
