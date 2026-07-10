#!/usr/bin/env python3
"""
generate_listing.py — Volet 1 : Listing tldrh
Produit _listing.md à partir des sources canoniques.

Sources :
  - Page docs /reference/slash-commands (catégories)
  - COMMAND_REGISTRY (descriptions courtes + args_hint)
  - exclusions.yaml (9 commandes manuelles)

Sortie : fichier texte 3 colonnes par catégorie.
  === Session ===
  /compress    Compress conversation context    [here [N] | focus ...]
"""

import os
import sys

# Ajouter le répertoire du projet au path pour l'import de sources
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sources import (
    fetch_docs_page,
    parse_command_defs,
    load_exclusions,
    load_overrides,
    short_description,
    CATEGORY_ORDER,
)

TLDRH_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(TLDRH_DIR, "pages", "_listing.md")


def build_listing(commands, cmd_defs, excluded, overrides=None):
    """Assembler le listing 3 colonnes par catégorie."""
    if overrides is None:
        overrides = {}
    by_cat = {}
    for name, _, cat in commands:
        if name in excluded:
            continue
        d = cmd_defs.get(name, {"args_hint": "", "gateway_only": False})
        if d.get("gateway_only"):
            continue
        by_cat.setdefault(cat, []).append((name, d))

    lines = []
    for cat in CATEGORY_ORDER:
        if cat not in by_cat:
            continue
        lines.append(f"=== {cat} ===")
        for name, d in sorted(by_cat[cat]):
            short = short_description(d.get("description", "")) or "-"
            # Override manuel pour short (description affichée)
            if name in overrides and "short" in overrides.get(name, {}):
                short = overrides[name]["short"]
            hint = d.get("args_hint", "") or "-"
            # Override manuel pour args_hint
            if name in overrides and "args_hint" in overrides.get(name, {}):
                hint = overrides[name]["args_hint"]
            lines.append(f"/{name:<20} {short:<64} {hint}")
        lines.append("")

    return "\n".join(lines)


def main():
    print("📡 Fetch docs page...")
    docs_cmds = fetch_docs_page()
    print(f"   → {len(docs_cmds)} commandes trouvées\n")

    print("📖 Reading COMMAND_REGISTRY...")
    cmd_defs = parse_command_defs()
    print(f"   → {len(cmd_defs)} CommandDef trouvés\n")

    print("📋 Loading exclusions...")
    excluded = load_exclusions()
    print(f"   → {len(excluded)} exclusions manuelles\n")

    print("🔄 Loading overrides...")
    overrides = load_overrides()
    print(f"   → {len(overrides)} commandes avec overrides\n")

    listing = build_listing(docs_cmds, cmd_defs, excluded, overrides)

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w") as f:
        f.write(listing)
    print(f"✅ Listing sauvegardé : {OUTPUT}")


if __name__ == "__main__":
    main()
