# Real-data dumps (A4 verification lane)

Some work — count-maintenance correctness (roadmap P5) and any
schema-altering change (Phase D) — can only be trusted against **real
data**, not the small `sample_data` graph. This directory is the seam for
that, in two tiers.

## Where dumps come from

A full MySQL dump of the GCD database, downloaded (login required) from
<https://www.comics.org/download/>. It is a `mysqldump` of the public
data tables only (≈78 tables: `gcd_*`, `stddata_*`, `taggit_*`) — no
`django_migrations`, no `oi_*`/auth/admin runtime tables, no user
credentials.

## Two tiers

**Tier 1 — the raw dump (private, not committed).**
Large (GBs) third-party data, so raw `*.sql` files are gitignored. Only
this `README.md` and the `CHECKSUMS` manifest are committed; the manifest
pins *which* dump a result came from. Loaded once into a throwaway
`test_dump` database and queried to build Tier 2. It stays local; it is
never needed by CI.

**Tier 2 — a committed, reproducible subset (public, tiny).**
`manage.py sample_from_dump` reads a bounded, connected slice from the
loaded Tier‑1 database (a few publishers with their full
series→issue→story→credit→cover→creator graphs, plus the rows that drive
counts/reprints) and writes a small fixture. Personal fields are
anonymised on the way out. That fixture is committed and is what the
`test-dump` lane actually runs on — so everyone and CI get real-shaped
data with no login and no multi‑GB file.

## Workflow

```
# 1. Download a dump into this directory, then record its checksum:
sha256sum dumps/2026-07-01.sql >> dumps/CHECKSUMS

# 2. Verify a dump matches the manifest before trusting a run:
just dump-verify dumps/2026-07-01.sql

# 3. Load it into the throwaway test_dump database (Tier 1):
just dump-load dumps/2026-07-01.sql

# 4. Regenerate the committed subset fixture from it (Tier 2):
just dump-extract

# 5. Run the real-data verification tests against the subset:
just test-dump
```

Schema caveat: the dump reflects comics.org production at its dump date.
The table columns are expected to match this branch's migrated schema
(verified for the core tables); `just dump-load` is followed by a
`migrate --check` preflight that fails loudly if they have diverged.
