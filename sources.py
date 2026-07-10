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
DOCS_URL = "https://hermes-agent.nousresearch.com/docs/reference/slash-commands"

# Paths relatifs au projet tldr-hermes
EXCLUSIONS_YAML = os.path.join(TLDRH_DIR, "exclusions.yaml")
NOTES_YAML = os.path.join(TLDRH_DIR, "notes.yaml")
EXAMPLES_YAML = os.path.join(TLDRH_DIR, "examples.yaml")

# Catégories CLI (hors messaging) — ordre d'affichage du listing
CLI_CATEGORIES = {
    "Session", "Configuration", "Tools & Skills",
    "Info", "Exit", "Dynamic CLI slash commands",
}
CATEGORY_ORDER = [
    "Session", "Configuration", "Tools & Skills",
    "Info", "Exit", "Dynamic CLI slash commands",
]


# ═══════════════════════════════════════════════════════════════════════
# PAGE DOCS OFFICIELLE (catégories + descriptions longues)
# ═══════════════════════════════════════════════════════════════════════

def fetch_docs_page():
    """Scraper la page docs pour catégories et descriptions longues.

    Retourne : list of (name, full_description, category)
    """
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        print("❌ Installe requests + beautifulsoup4 : pip install requests beautifulsoup4 lxml")
        sys.exit(1)

    try:
        resp = requests.get(DOCS_URL, headers={"User-Agent": "tldr-hermes/2.0"}, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"❌ Échec du fetch docs page : {e}")
        sys.exit(1)

    soup = BeautifulSoup(resp.text, "lxml")
    content = soup.find("div", class_="theme-doc-markdown")
    if not content:
        print("❌ Structure .theme-doc-markdown introuvable")
        sys.exit(1)

    commands = []
    current_cat = None
    in_messaging = False

    for el in content.children:
        if el.name == "h2":
            text = el.get_text(strip=True)
            if "Messaging" in text:
                in_messaging = True
            continue

        if in_messaging:
            continue

        if el.name == "h3":
            text = el.get_text(strip=True).rstrip("\u200b").strip()
            current_cat = text if text in CLI_CATEGORIES else None
            continue

        if el.name == "table" and current_cat:
            for row in el.find_all("tr")[1:]:
                cells = row.find_all("td")
                if len(cells) < 2:
                    continue
                code = cells[0].find("code")
                if not code:
                    continue
                m = re.match(r"^/([a-z][a-z0-9_-]*)", code.get_text(strip=True))
                if m:
                    name = m.group(1)
                    desc = cells[1].get_text(separator=" ", strip=True)
                    desc = re.sub(r"\s+", " ", desc).strip()
                    commands.append((name, desc, current_cat))

    return commands


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
            hint_m = re.search(r'args_hint="([^"]*)"', block)
            aliases_m = re.search(r"aliases=\(([^)]*)\)", block)
            cli_only = "cli_only=True" in block
            gateway_only = "gateway_only=True" in block

            defs[name] = {
                "description": desc,
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
