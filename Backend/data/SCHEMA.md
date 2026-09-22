# Knowledge Layer Schema

These five files are the **only** source of truth the system is allowed to
draw on for BIS facts (Rule 1 -- Zero Hallucination). They currently ship
empty (or with `TEST-` prefixed fixtures in `tests/`) and must be populated
by the data-curation workstream. `app/data_layer/repository.py` is the only
module that reads these files directly.

Every record should carry a `source_id` that resolves in `sources.json`,
so any fact returned by the API can be traced back to where it came from
(Rule 3 -- Traceability). Do not duplicate a source's URL/title across
files -- store it once in `sources.json` and reference it by id.

## bis_metadata.json — list[object]

Used for embedding / semantic search (Phase 2). One object per standard.

```json
[
  {
    "is_number": "IS 269:2015",
    "title": "Ordinary Portland Cement — Specification",
    "keywords": ["cement", "OPC", "building material"],
    "product": "Cement",
    "sector": "Building Materials",
    "scope_summary": "Public scope/abstract text only -- never the full copyrighted standard text.",
    "source_id": "SRC-BIS-KYS-IS269"
  }
]
```

Required: `is_number` (unique key), `title`.
Do NOT embed: URLs, source ids, dates, confidence values, compliance
flags -- those stay structured metadata, not text fed to the embedding
model (see `<ml_architecture>` in the project spec).

## bis_compliance.json — object keyed by is_number

Deterministic compliance facts. One key per `is_number` from
`bis_metadata.json`.

```json
{
  "IS 269:2015": {
    "standard_status": "ACTIVE",
    "current_version": "IS 269:2015",
    "amendments": ["Amendment No. 1 (2016)"],
    "superseded_by": null,
    "supersedes": ["IS 269:1989"],
    "qco_applicable": true,
    "certification_required": true,
    "testing_scheme": "Scheme-I",
    "normative_references": ["IS 4031"],
    "missing_information": [],
    "source_id": "SRC-BIS-KYS-IS269"
  }
}
```

Any field that cannot be verified from a real source should be omitted or
left `null` -- never guessed. The API layer must render an omitted field
as `NOT VERIFIED`, not as "no" / "not applicable".

## qco_mapping.json — list[object]

Product → Quality Control Order → IS mapping.

```json
[
  {
    "product": "Cement",
    "qco_name": "Cement and Cement Products (Quality Control) Order",
    "is_number": "IS 269:2015",
    "enforcement_date": "2023-04-01",
    "source_id": "SRC-BIS-QCO-CEMENT"
  }
]
```

Required: `product`, `is_number`. `product` matching is case-insensitive
exact match in Phase 1; fuzzy/semantic product matching is a later-phase
concern in the matcher, not the repository.

## normative_graph.json — list[object]

Directed edges between standards.

```json
[
  {
    "from_is": "IS 269:2015",
    "to_is": "IS 4031",
    "relationship_type": "REFERENCES_TEST_METHOD",
    "source_id": "SRC-BIS-KYS-IS269"
  }
]
```

Required: `from_is`, `to_is`, `relationship_type`. Every edge must be
traceable to a `source_id` -- never inferred by the AI.

## sources.json — object keyed by source_id

```json
{
  "SRC-BIS-KYS-IS269": {
    "title": "BIS Know Your Standard -- IS 269:2015",
    "url": "https://www.bis.gov.in/know-your-standard/?lang=en",
    "retrieved_on": "2026-09-01"
  }
}
```
