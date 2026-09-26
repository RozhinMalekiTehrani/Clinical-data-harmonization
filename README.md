# DH-2026-02-clinical-data-harmonization_Rozhin
# DH-2026-02 Clinical Data Harmonization

Candidate reference: DH-2026-02

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

## Scope

This prototype intentionally focuses on a narrow, auditable subset:

- laboratory observations
- medication mentions
- symptoms
- date normalization
- unit normalization
- local laboratory code mapping
- negation
- basic temporality
- source provenance
- medication conflict detection
- review queue generation
- schema validation
- deterministic replay

The prototype does not attempt to implement a complete clinical terminology
service, full FHIR ingestion layer, production database, clinical decision
support system, or production-scale model serving platform.

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




SciSpaCy is used as a biomedical NLP component for narrative processing. Due to deadline , I aimed to use majority voting, using LLM and pre-trained appriach, while tight dealine did not give me the cha.