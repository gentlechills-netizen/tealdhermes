#!/usr/bin/env python3
"""
sources.py — Sources de données canoniques pour les générateurs tldrh.

Fonctions partagées entre generate_listing.py et generate_pages.py.
Toute modification du scraping/parsing se fait ici, pas dans les générateurs.
"""

import os
import re
import sys
import yaml

# ── Paths ──────────────────────────────────────────────────────────────
HERMES_HOME = os.path.expanduser("~/.hermes")
TLDRH_DIR = os.path.join(HERMES_HOME, "tldr-hermes")
COMMANDS_PY = os.path.join(HERMES_HOME, "hermes-agent", "hermes_cli", "commands.py")
CONFIG_YAML = os.path.join(HERMES_HOME, "config.yaml")

# Paths relatifs au projet tldr-hermes
EXCLUSIONS_YAML = os.path.join(TLDRH_DIR, "exclusions.yaml")
NOTES_YAML = os.path.join(TLDRH_DIR, "notes.yaml")
EXAMPLES_YAML = os.path.join(TLDRH_DIR, "examples.yaml")
OVERRIDES_YAML = os.path.join(TLDRH_DIR, "overrides.yaml")

# Ordre d'affichage du listing
CATEGORY_ORDER = [
    "Session", "Configuration", "Tools & Skills",
    "Info", "Exit", "Dynamic CLI slash commands",
]


# ═══════════════════════════════════════════════════════════════════════
# COMMAND_REGISTRY (descriptions courtes, args_hint, aliases, flags)
# ═══════════════════════════════════════════════════════════════════════

def parse_command_defs():
    """Parser COMMAND_REGISTRY pour toutes les métadonnées.

    Retourne : dict of name -> {
        "description": str,     # description courte
        "args_hint": str,
        "aliases": list[str],
        "cli_only": bool,
        "gateway_only": bool,
    }
    """
    if not os.path.exists(COMMANDS_PY):
        print(f"⚠ {COMMANDS_PY} introuvable")
        return {}

    with open(COMMANDS_PY) as f:
        content = f.read()

    defs = {}
    pos = 0
    while True:
        start = content.find("CommandDef(", pos)
        if start == -1:
            break

        depth = 0
        end = start
        for i in range(start, len(content)):
            if content[i] == "(":
                depth += 1
            elif content[i] == ")":
                depth -= 1
                if depth == 0:
                    end = i
                    break

        block = content[start + 11 : end]
        pos = end + 1

        parts = re.findall(r'"((?:[^"\\]|\\.)*)"', block)
        if len(parts) >= 1:
            name = parts[0]
            desc = parts[1] if len(parts) >= 2 else ""
            category = parts[2] if len(parts) >= 3 else ""
            hint_m = re.search('args_hint="([^"]*)"', block)
            aliases_m = re.search(r"aliases=\(([^)]*)\)", block)
            cli_only = "cli_only=True" in block
            gateway_only = "gateway_only=True" in block

            defs[name] = {
                "description": desc,
                "category": category,
                "args_hint": hint_m.group(1) if hint_m else "",
                "aliases": re.findall(r'"([^"]+)"', aliases_m.group(1)) if aliases_m else [],
                "cli_only": cli_only,
                "gateway_only": gateway_only,
            }

    return defs


# ═══════════════════════════════════════════════════════════════════════
# CONFIG (clés top-level pour détection dashboard)
# ═══════════════════════════════════════════════════════════════════════

def get_config_top_keys():
    """Récupère les clés top-level de config.yaml.

    Retourne : set[str]
    """
    if not os.path.exists(CONFIG_YAML):
        return set()
    keys = set()
    with open(CONFIG_YAML) as f:
        for line in f:
            m = re.match(r"^([a-z][a-z0-9_-]*):", line)
            if m:
                keys.add(m.group(1))
    return keys


# ═══════════════════════════════════════════════════════════════════════
# EXCLUSIONS
# ═══════════════════════════════════════════════════════════════════════

def load_exclusions():
    """Charger les exclusions manuelles.

    Retourne : set[str] — noms des commandes exclues.
    """
    if not os.path.exists(EXCLUSIONS_YAML):
        return set()
    with open(EXCLUSIONS_YAML) as f:
        data = yaml.safe_load(f) or {}
    return {name for name, info in data.items() if info.get("ignore")}


# ═══════════════════════════════════════════════════════════════════════
# OVERRIDES (remplacements manuels pour champs COMMAND_REGISTRY)
# ═══════════════════════════════════════════════════════════════════════

def load_overrides():
    """Charger les overrides manuels.

    Retourne : dict of name -> dict of field -> value
    Utile pour remplacer args_hint trop long sans modifier commands.py.
    """
    if not os.path.exists(OVERRIDES_YAML):
        return {}
    with open(OVERRIDES_YAML) as f:
        data = yaml.safe_load(f) or {}
    return data


# ═══════════════════════════════════════════════════════════════════════
# NOTES (exceptions Dashboard + notes spéciales)
# ═══════════════════════════════════════════════════════════════════════

def load_notes():
    """Charger les notes manuelles.

    Retourne : dict of name -> list[str] — notes textuelles par commande.
    """
    if not os.path.exists(NOTES_YAML):
        return {}
    with open(NOTES_YAML) as f:
        data = yaml.safe_load(f) or {}
    return data


# ═══════════════════════════════════════════════════════════════════════
# EXEMPLES
# ═══════════════════════════════════════════════════════════════════════

def load_examples():
    """Charger les exemples de commandes.

    Retourne : dict of name -> list[{"cmd": str, "desc": str}]
    """
    if not os.path.exists(EXAMPLES_YAML):
        return {}
    with open(EXAMPLES_YAML) as f:
        data = yaml.safe_load(f) or {}
    return data


# ═══════════════════════════════════════════════════════════════════════
# DESCRIPTIONS LONGUES (source figée depuis la page docs)
# ═══════════════════════════════════════════════════════════════════════

def load_long_descriptions():
    """Charger les descriptions longues figées.

    Retourne : dict of name -> str — description longue par commande.
    Si le fichier n'existe pas, retourne dict vide (fallback inoffensif).
    """
    path = os.path.join(TLDRH_DIR, "descriptions_longues.yaml")
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        data = yaml.safe_load(f) or {}
    return data


# ═══════════════════════════════════════════════════════════════════════
# UTILITAIRES
# ═══════════════════════════════════════════════════════════════════════

def short_description(desc):
    """Nettoyer les parenthèses d'une description."""
    return re.sub(r"\s*\(.*?\)\s*", "", desc).strip()


def first_sentence(text):
    """Première phrase d'un texte."""
    # Split sur point+espace, point d'interrogation+espace, etc.
    m = re.split(r"(?<=[.!?])\s+", text.strip())
    return m[0] if m else text


def availability_label(cli_only, gateway_only):
    """Libellé de disponibilité."""
    if cli_only:
        return "Hermes TUI"
    if gateway_only:
        return "Gateway"
    return "Hermes TUI + Gateway"
