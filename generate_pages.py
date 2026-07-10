#!/usr/bin/env python3
"""
generate_pages.py — Volet 2 : Pages individuelles /<command>
Produit les 63 fichiers .page.md au format OG tldr.

Sources :
  - Page docs /reference/slash-commands (descriptions longues)
  - COMMAND_REGISTRY (args_hint, aliases, disponibilité)
  - config.yaml (clés top-level → Dashboard)
  - notes.yaml (exceptions Dashboard + notes spéciales)
  - examples.yaml (0-4 exemples par commande)
  - exclusions.yaml (9 commandes à exclure)

Sortie : ~/.hermes/tldr-hermes/pages/<commande>.page.md
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sources import (
    fetch_docs_page,
    parse_command_defs,
    load_exclusions,
    load_notes,
    load_examples,
    get_config_top_keys,
    first_sentence,
    availability_label,
    CATEGORY_ORDER,
)

TLDRH_DIR = os.path.dirname(os.path.abspath(__file__))
PAGES_DIR = os.path.join(TLDRH_DIR, "pages")

# Message Dashboard par défaut (CONFIG)
DASHBOARD_DEFAULT = (
    "> Command status and configuration in Hermes Web Dashboard.\n"
    "  Type `hermes dashboard` in the CLI terminal and select CONFIG menu."
)


def generate_page(name, full_desc, defn, notes, examples, config_keys):
    """Générer le contenu d'une page .page.md.

    Sections dans l'ordre du Volet 2 :
      1. Description (toujours)
      2. Syntax   (optionnel — args_hint non vide)
      3. Aliases  (optionnel — liste non vide)
      4. Available (toujours)
      5. Dashboard (optionnel — clé top-level config.yaml)
      6. Notes    (optionnel — notes.yaml)
      7. Exemples (variable 0-4)

    Chaque ligne n'apparaît que si la donnée source existe.
    """
    lines = []
    lines.append(f"# {name}")
    lines.append("")

    # ── 1. Description ────────────────────────────────────────────────
    desc = first_sentence(full_desc)
    lines.append(f"> {desc}")

    # ── 2. Syntax ─────────────────────────────────────────────────────
    hint = defn.get("args_hint", "")
    if hint:
        lines.append(f"> Syntax: /{name} {hint}")

    # ── 3. Aliases ────────────────────────────────────────────────────
    aliases = defn.get("aliases", [])
    if aliases:
        alias_str = ", ".join(f"/{a}" for a in aliases)
        lines.append(f"> Aliases: {alias_str}")

    # ── 4. Available ──────────────────────────────────────────────────
    avail = availability_label(defn.get("cli_only"), defn.get("gateway_only"))
    lines.append(f"> Available: {avail}")

    # ── 5. Dashboard ──────────────────────────────────────────────────
    # Si commande a une note dans notes.yaml → PAS de Dashboard générique
    # (la note couvre déjà le redirect dans la section Notes)
    if name not in notes and name in config_keys:
        lines.append("")
        lines.append(DASHBOARD_DEFAULT)

    # ── 6. Notes ──────────────────────────────────────────────────────
    if name in notes:
        lines.append("")
        for note in notes[name]:
            if isinstance(note, dict):
                # YAML a parsé "Also configurable in: X" comme un mapping
                # → reconstruire la chaîne originale
                note = ", ".join(f"{k}: {v}" for k, v in note.items())
            lines.append(f"> {note}")

    # ── 7. Exemples ──────────────────────────────────────────────────
    if name in examples:
        lines.append("")
        for ex in examples[name]:
            cmd = ex.get("cmd", f"/{name}")
            desc_text = ex.get("desc", "").strip()
            if desc_text:
                lines.append(f"- {desc_text}")
                lines.append("")
                lines.append(f"`{cmd}`")
            else:
                lines.append(f"- `{cmd}`")
            lines.append("")
    lines.append("")
    return "\n".join(lines)


def main():
    print("📡 Fetch docs page...")
    docs_cmds = fetch_docs_page()
    print(f"   → {len(docs_cmds)} commandes trouvées\n")

    print("📖 Reading COMMAND_REGISTRY...")
    cmd_defs = parse_command_defs()
    print(f"   → {len(cmd_defs)} CommandDef trouvés\n")

    print("⚙️  Reading config.yaml...")
    config_keys = get_config_top_keys()
    print(f"   → {len(config_keys)} clés top-level\n")

    print("📋 Loading exclusions...")
    excluded = load_exclusions()
    print(f"   → {len(excluded)} exclusions manuelles\n")

    print("📝 Loading notes...")
    notes = load_notes()
    print(f"   → {len(notes)} commandes avec notes\n")

    print("📝 Loading examples...")
    examples = load_examples()
    print(f"   → {len(examples)} commandes avec exemples\n")

    # ── Cross-référence ───────────────────────────────────────────────
    all_commands = []
    missing_defs = []
    for name, full_desc, cat in docs_cmds:
        if name in excluded:
            continue
        d = cmd_defs.get(name)
        if not d:
            missing_defs.append(name)
            continue
        if d.get("gateway_only"):
            continue
        all_commands.append((name, full_desc, cat, d))

    if missing_defs:
        print(f"\n⚠ Commandes sans CommandDef : {missing_defs}")

    # ── Génération ────────────────────────────────────────────────────
    os.makedirs(PAGES_DIR, exist_ok=True)
    count = 0
    by_cat = {}
    for name, full_desc, cat, d in sorted(all_commands, key=lambda x: x[0]):
        by_cat.setdefault(cat, []).append(name)
        page = generate_page(name, full_desc, d, notes, examples, config_keys)
        filepath = os.path.join(PAGES_DIR, f"{name}.page.md")
        with open(filepath, "w") as f:
            f.write(page)
        count += 1

    # ── Nettoyage : supprimer pages des commandes exclues ──────────
    kept_names = {name for name, _, _, _ in all_commands}
    removed = 0
    for f in os.listdir(PAGES_DIR):
        if f.endswith(".page.md"):
            name = f[: -len(".page.md")]
            if name not in kept_names:
                os.remove(os.path.join(PAGES_DIR, f))
                removed += 1
    if removed:
        print(f"   → {removed} anciennes pages supprimées (exclusions ou retraits)")

    # ── Résumé ────────────────────────────────────────────────────────
    print(f"\n✅ {count} pages générées dans {PAGES_DIR}/")
    for cat in CATEGORY_ORDER:
        if cat in by_cat:
            print(f"   {cat}: {len(by_cat[cat])} commandes")


if __name__ == "__main__":
    main()
