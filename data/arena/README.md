# Arena Data Layout

This directory holds raw and normalized inputs for historical replay seasons.

## Recommended structure

- `data/arena/raw/`
  Raw provider payloads, archived by source and date.
- `data/arena/manifests/`
  Curated season manifests imported into SQLite.

## Import flow

1. Prepare a season manifest JSON under `data/arena/manifests/`.
2. Import it with:

```bash
python3 scripts/import_arena_data.py data/arena/manifests/sample_season.json --replace
```

3. Start the app and open `/arena`.

## Storage policy

- Keep full raw payloads in `raw/` only when you need reproducibility.
- Store normalized daily bars and curated event summaries in SQLite.
- Do not store full article bodies in SQLite for V1.
