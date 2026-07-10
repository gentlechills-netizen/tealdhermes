# Changelog

## V3 — 2026-07-09

### Added
- tealdeer engine (Rust) replaces custom generator
- `generate_listing.py` — 3-column category listing (64-char description width)
- `generate_pages.py` — 47 `.page.md` pages in OG tldr format
- `sources.py` — shared module for all data sources
- `tldrh` wrapper — installed in `~/.local/bin/` (PATH)
- `update.sh` — regeneration + examples diff report
- `install.sh` — distribution one-liner
- `STYLE.md` → `tldrh_pages_style_guide.md`
- `complex.md` — 9 commands with non-trivial arguments
- Examples diff report in `reports/examples-diff-<timestamp>.md`
- 25 manual exclusions (`exclusions.yaml`)
- 10 Dashboard notes (`notes.yaml`)

### Changed
- `examples.yaml` — cleaned from 62 to 46 entries, all synchronized
- `compact = false` in tealdeer config (blank lines between examples)
- Wrapper reads `_listing.md` via `cat` (never `bat` — avoids space normalization)
- Wrapper installed in PATH instead of bash alias

### Removed
- Old `tealdhermes` skill (V1)
- 15 orphaned entries from `examples.yaml`
- 16 commands excluded or filtered
- `bat` / `batcat` from listing pipeline

### Fixed
- Blank lines between examples (was `compact = true`)
- Alias cache issue (moved to PATH-based installation)
- `.page.md` cleanup on exclusion changes
- YAML dict flattening for notes with colons

## V2 — 2026-07-08

### Added
- `data_architecture.md` — specification for listing and page format
- `exclusions.yaml`, `notes.yaml`, `examples.yaml` — data sources
- 7 templates A-G for page generation (spec only)

### Changed
- Moved from monolithic generator to spec-driven approach

### Removed
- All V1 generated pages (destroyed by `--force`)

## V1 — 2026-07-07

### Added
- `generator.py` — 865 lines, 7 templates A-G
- BS4 scraping from docs page
- Command enrichment system
- First 63 `.page.md` pages

### Known Issues
- `--force` flag destroyed 33 pages
- Templates auto-detected but never validated
- Enrichment system not scalable
- Unilateral decisions without user validation
