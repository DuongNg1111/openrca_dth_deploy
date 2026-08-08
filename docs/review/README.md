# Capstone review evidence — 2026-08-09

- `market_cloudbed1_dataset_card_2026-08-09.md`: verified dataset provenance,
  integrity, coverage, and label distribution.
- `market_cloudbed1_file_manifest_2026-08-09.tsv`: deterministic SHA-256 and byte
  inventory for all 20 extracted files; no telemetry values.
- `real_market_smoke_2026-08-09.md`: one read-only **metric-only** loader and
  detector failure case.
- `full_pipeline_local_integration_2026-08-09.md`: one controlled real
  metric/log/trace dry-run plus explicit Gemini/disposable-database integration.

These artifacts establish reproducibility and limitations. They are not a
multi-case accuracy benchmark. Raw telemetry, database files, and credentials
remain outside Git.
