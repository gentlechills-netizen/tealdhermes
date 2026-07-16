#!/usr/bin/env python3
"""
generate_listing.py — Volet 1 : Listing tldrh
Produit _listing.md à partir des sources canoniques.

Sources :
  - COMMAND_REGISTRY (catégories, descriptions, args_hint)
  - exclusions.yaml (commandes manuelles)
  - overrides.yaml (remplacements manuels)

Sortie : fichier texte 3 colonnes par catégorie.
  === Session ===
  /compress    Compress conversation context    [here [N] | focus ...]
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sources import (
    parse_command_defs,
    load_exclusions,
    load_overrides,
    short_description,
    CATEGORY_ORDER,
)

TLDRH_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(TLDRH_DIR, "pages", "_listing.md")


def build_listing(cmd_defs, excluded, overrides=None):
    """Assembler le listing 3 colonnes par catégorie depuis COMMAND_REGISTRY."""
    if overrides is None:
        overrides = {}
    by_cat = {}
    for name, d in cmd_defs.items():
        if name in excluded:
            continue
        if d.get("gateway_only"):
            continue
        cat = d.get("category", "Uncategorized")
        by_cat.setdefault(cat, []).append((name, d))

    lines = []
    for cat in CATEGORY_ORDER:
        if cat not in by_cat:
            continue
        lines.append(f"=== {cat} ===")
        for name, d in sorted(by_cat[cat]):
            short = short_description(d.get("description", "")) or "-"
            if name in overrides and "short" in overrides.get(name, {}):
                short = overrides[name]["short"]
            hint = d.get("args_hint", "") or "-"
            if name in overrides and "args_hint" in overrides.get(name, {}):
                hint = overrides[name]["args_hint"]
            lines.append(f"/{name:<20} {short:<64} {hint}")
        lines.append("")

    return "\n".join(lines)


def main():
    print("📖 Reading COMMAND_REGISTRY...")
    cmd_defs = parse_command_defs()
    print(f"   → {len(cmd_defs)} CommandDef trouvés\n")

    print("📋 Loading exclusions...")
    excluded = load_exclusions()
    print(f"   → {len(excluded)} exclusions manuelles\n")

    print("🔄 Loading overrides...")
    overrides = load_overrides()
    print(f"   → {len(overrides)} commandes avec overrides\n")

    listing = build_listing(cmd_defs, excluded, overrides)

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w") as f:
        f.write(listing)
    print(f"✅ Listing sauvegardé : {OUTPUT}")


if __name__ == "__main__":
    main()
